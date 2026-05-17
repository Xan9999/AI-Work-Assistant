"""
Hybrid retrieval: BM25 + vector search fused with RRF, then cross-encoder reranked.

Improvements:
- multilingual reranker (mmarco-mMiniLMv2) handles Slovenian documents
- sentence-window overlap: each returned chunk is expanded with its neighbors
- HyDE: vector_search() accepts a pre-generated hypothetical answer
"""

import pickle
from pathlib import Path

import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings
from sentence_transformers import SentenceTransformer, CrossEncoder

BM25_PATH = Path(__file__).parent.parent / "data" / "bm25_index.pkl"
DB_DIR = Path(__file__).parent.parent / "data" / "chroma_db"
MODEL_DIR = Path(__file__).parent.parent / "data" / "models"

EMBEDDING_MODEL = "intfloat/multilingual-e5-base"
RERANKER_MODEL = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
COLLECTION_NAME = "nexus_docs"

RRF_K = 60
RETRIEVAL_TOP_K = 20
RERANK_TOP_K = 5


class E5EmbeddingFunction(EmbeddingFunction):
    """
    ChromaDB embedding function with 'passage: ' prefix for E5 models.
    Actual query embedding uses 'query: ' prefix and is done manually in vector_search().
    """

    def __init__(self, model_name: str):
        local_path = MODEL_DIR / model_name.replace("/", "--")
        self.model = SentenceTransformer(str(local_path) if local_path.exists() else model_name)

    def __call__(self, input: Documents) -> Embeddings:
        texts = [f"passage: {doc}" for doc in input]
        return self.model.encode(texts, normalize_embeddings=True).tolist()


class HybridRetriever:
    def __init__(self):
        print("Loading BM25 index...")
        with open(BM25_PATH, "rb") as f:
            data = pickle.load(f)
        self.bm25 = data["bm25"]
        self.chunks = data["chunks"]
        self._id_to_idx = {c["id"]: i for i, c in enumerate(self.chunks)}

        print(f"Loading embedding model ({EMBEDDING_MODEL})...")
        self.ef = E5EmbeddingFunction(EMBEDDING_MODEL)

        print("Connecting to ChromaDB...")
        client = chromadb.PersistentClient(path=str(DB_DIR))
        self.collection = client.get_collection(COLLECTION_NAME, embedding_function=self.ef)

        print(f"Loading reranker ({RERANKER_MODEL})...")
        local_reranker = MODEL_DIR / RERANKER_MODEL.replace("/", "--")
        reranker_path = str(local_reranker) if local_reranker.exists() else RERANKER_MODEL
        self.reranker = CrossEncoder(reranker_path)

    # ------------------------------------------------------------------ #
    # Core retrieval                                                       #
    # ------------------------------------------------------------------ #

    def bm25_search(self, query: str, k: int = RETRIEVAL_TOP_K) -> list[tuple[int, float]]:
        tokens = query.lower().split()
        scores = self.bm25.get_scores(tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [(idx, float(scores[idx])) for idx in top_indices]

    def vector_search(self, text: str, k: int = RETRIEVAL_TOP_K) -> list[tuple[str, float]]:
        """
        text can be either a raw query or a HyDE hypothetical answer —
        caller decides which to pass. Always uses 'query: ' prefix for E5.
        """
        embedding = self.ef.model.encode(
            f"query: {text}", normalize_embeddings=True
        ).tolist()
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=k,
            include=["distances"],
        )
        return list(zip(results["ids"][0], results["distances"][0]))

    def rrf_fusion(
        self,
        bm25_results: list[tuple[int, float]],
        vector_results: list[tuple[str, float]],
    ) -> list[dict]:
        rrf_scores: dict[str, float] = {}

        for rank, (chunk_idx, _) in enumerate(bm25_results):
            chunk_id = self.chunks[chunk_idx]["id"]
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + 1.0 / (rank + 1 + RRF_K)

        for rank, (chunk_id, _) in enumerate(vector_results):
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + 1.0 / (rank + 1 + RRF_K)

        sorted_ids = sorted(rrf_scores, key=lambda cid: rrf_scores[cid], reverse=True)

        fused = []
        for chunk_id in sorted_ids[:RETRIEVAL_TOP_K]:
            idx = self._id_to_idx.get(chunk_id)
            if idx is not None:
                chunk = dict(self.chunks[idx])
                chunk["rrf_score"] = rrf_scores[chunk_id]
                fused.append(chunk)

        return fused

    def rerank(self, query: str, candidates: list[dict], k: int = RERANK_TOP_K) -> list[dict]:
        if not candidates:
            return []

        pairs = [(query, c["text"]) for c in candidates]
        scores = self.reranker.predict(pairs)

        ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)

        results = []
        for chunk, score in ranked[:k]:
            chunk = dict(chunk)
            chunk["rerank_score"] = float(score)
            results.append(chunk)

        return results

    # ------------------------------------------------------------------ #
    # Sentence-window overlap                                              #
    # ------------------------------------------------------------------ #

    def _expand_chunk(self, chunk: dict) -> dict:
        """
        Expand a chunk with its immediate neighbors from the same document.
        ChromaDB stores only the core chunk (for accurate embedding), but GPT
        receives the expanded version (for richer context).
        """
        doc_path = chunk["metadata"]["doc_path"]
        idx = chunk["metadata"]["chunk_idx"]

        parts = []

        prev_id = f"{doc_path}::chunk_{idx - 1}"
        prev_idx = self._id_to_idx.get(prev_id)
        if prev_idx is not None:
            parts.append(self.chunks[prev_idx]["text"])

        parts.append(chunk["text"])

        next_id = f"{doc_path}::chunk_{idx + 1}"
        next_idx = self._id_to_idx.get(next_id)
        if next_idx is not None:
            parts.append(self.chunks[next_idx]["text"])

        expanded = dict(chunk)
        expanded["text"] = "\n\n".join(parts)
        return expanded

    # ------------------------------------------------------------------ #
    # Public interface                                                     #
    # ------------------------------------------------------------------ #

    def search(
        self,
        query: str,
        hypothetical: str | None = None,
        k: int = RERANK_TOP_K,
    ) -> list[dict]:
        """
        Full pipeline:
          BM25(query) + vector(hypothetical or query) → RRF → rerank(query) → expand
        """
        bm25_results = self.bm25_search(query)
        vector_results = self.vector_search(hypothetical if hypothetical else query)
        fused = self.rrf_fusion(bm25_results, vector_results)
        ranked = self.rerank(query, fused, k=k)
        return [self._expand_chunk(c) for c in ranked]


def format_sources(chunks: list[dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, 1):
        meta = chunk["metadata"]
        source_label = f"[Source {i}: {meta['doc_title']} — {meta['section']} ({meta['doc_path']})]"
        parts.append(f"{source_label}\n{chunk['text']}")
    return "\n\n---\n\n".join(parts)
