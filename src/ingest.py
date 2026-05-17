"""
Ingest documents into ChromaDB (vector) and BM25 (sparse) indices.

Run: python src/ingest.py
"""

import gc
import os
import re
import pickle
from pathlib import Path

# Limit CPU parallelism before importing torch — prevents AVX/MKL crashes
# on machines where PyTorch's default thread count exceeds available resources.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import chromadb
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

DATA_DIR = Path(__file__).parent.parent / "data" / "documents"
DB_DIR = Path(__file__).parent.parent / "data" / "chroma_db"
BM25_PATH = Path(__file__).parent.parent / "data" / "bm25_index.pkl"
MODEL_DIR = Path(__file__).parent.parent / "data" / "models"

EMBEDDING_MODEL = "intfloat/multilingual-e5-base"
COLLECTION_NAME = "nexus_docs"
MAX_CHUNK_CHARS = 1800


def chunk_markdown(text: str, doc_path: str, doc_type: str) -> list[dict]:
    """Split markdown into section-level chunks, further splitting long sections."""
    title_match = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    doc_title = title_match.group(1).strip() if title_match else Path(doc_path).stem

    chunks = []
    sections = re.split(r'\n(?=## )', text)

    for section in sections:
        section = section.strip()
        if len(section) < 40:
            continue

        heading_match = re.match(r'^#{1,3}\s+(.+)', section)
        section_heading = heading_match.group(1).strip() if heading_match else "Introduction"

        if len(section) <= MAX_CHUNK_CHARS:
            chunks.append(_make_chunk(section, doc_title, section_heading, doc_path, doc_type, len(chunks)))
        else:
            paragraphs = re.split(r'\n{2,}', section)
            current = ""
            for para in paragraphs:
                if len(current) + len(para) + 2 > MAX_CHUNK_CHARS and current:
                    chunks.append(_make_chunk(current.strip(), doc_title, section_heading, doc_path, doc_type, len(chunks)))
                    current = para
                else:
                    current = (current + "\n\n" + para).strip() if current else para
            if current.strip():
                chunks.append(_make_chunk(current.strip(), doc_title, section_heading, doc_path, doc_type, len(chunks)))

    return chunks


def chunk_text(text: str, doc_path: str, doc_type: str) -> list[dict]:
    """Split plain text into paragraph-level chunks."""
    doc_title = Path(doc_path).stem.replace("_", " ").title()
    paragraphs = re.split(r'\n{2,}', text.strip())
    chunks = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) + 2 > MAX_CHUNK_CHARS and current:
            chunks.append(_make_chunk(current, doc_title, "Content", doc_path, doc_type, len(chunks)))
            current = para
        else:
            current = (current + "\n\n" + para).strip() if current else para

    if current:
        chunks.append(_make_chunk(current, doc_title, "Content", doc_path, doc_type, len(chunks)))

    return chunks


def _make_chunk(text: str, doc_title: str, section: str, doc_path: str, doc_type: str, idx: int) -> dict:
    rel_path = str(Path(doc_path).relative_to(DATA_DIR))
    return {
        "id": f"{rel_path}::chunk_{idx}",
        "text": text,
        "metadata": {
            "doc_title": doc_title,
            "section": section,
            "doc_path": rel_path,
            "doc_type": doc_type,
            "chunk_idx": idx,
        },
    }


def load_documents() -> list[dict]:
    """Walk data/documents/ and parse all .md and .txt files into chunks."""
    all_chunks = []
    for file_path in sorted(DATA_DIR.rglob("*")):
        if file_path.suffix not in {".md", ".txt"}:
            continue

        doc_type = file_path.parent.name
        text = file_path.read_text(encoding="utf-8")

        if file_path.suffix == ".md":
            chunks = chunk_markdown(text, str(file_path), doc_type)
        else:
            chunks = chunk_text(text, str(file_path), doc_type)

        all_chunks.extend(chunks)
        print(f"  {file_path.name}: {len(chunks)} chunks")

    return all_chunks


def build_vector_index(chunks: list[dict]) -> None:
    """Pre-compute E5 embeddings, free the model, then store in ChromaDB."""
    local_path = MODEL_DIR / EMBEDDING_MODEL.replace("/", "--")
    model_path = str(local_path) if local_path.exists() else EMBEDDING_MODEL
    model = SentenceTransformer(model_path)

    texts = [f"passage: {c['text']}" for c in chunks]
    print(f"  Encoding {len(texts)} chunks...")
    embeddings = model.encode(texts, normalize_embeddings=True, batch_size=16, show_progress_bar=True)

    # Free model before ChromaDB operations to reduce peak memory
    del model
    gc.collect()

    client = chromadb.PersistentClient(path=str(DB_DIR))
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    batch_size = 50
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        collection.add(
            ids=[c["id"] for c in batch],
            documents=[c["text"] for c in batch],
            metadatas=[c["metadata"] for c in batch],
            embeddings=embeddings[i : i + batch_size].tolist(),
        )
        print(f"  Stored {min(i + batch_size, len(chunks))}/{len(chunks)} chunks...", end="\r")

    print(f"  Vector index: {len(chunks)} chunks stored in ChromaDB            ")


def build_bm25_index(chunks: list[dict]) -> None:
    """Build and persist BM25 index over all chunks."""
    tokenized = [c["text"].lower().split() for c in chunks]
    bm25 = BM25Okapi(tokenized)

    index_data = {"bm25": bm25, "chunks": chunks}
    with open(BM25_PATH, "wb") as f:
        pickle.dump(index_data, f)
    print(f"  BM25 index: {len(chunks)} chunks stored at {BM25_PATH}")


def main():
    print(f"Embedding model: {EMBEDDING_MODEL}")
    print("Loading and chunking documents...")
    chunks = load_documents()
    print(f"\nTotal chunks: {len(chunks)}")

    print("\nBuilding vector index (ChromaDB + E5)...")
    DB_DIR.mkdir(parents=True, exist_ok=True)
    build_vector_index(chunks)

    print("\nBuilding BM25 index...")
    build_bm25_index(chunks)

    print("\nIngestion complete.")


if __name__ == "__main__":
    main()
