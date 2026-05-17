"""
RAG assistant: query classification, multi-hop decomposition, HyDE, answer generation.
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from retrieval import HybridRetriever, format_sources

load_dotenv()

MODEL = os.getenv("CHATGPT_MODEL", "gpt-4o-mini")
RERANK_SCORE_THRESHOLD = -6.0
MAX_HISTORY_TURNS = 3
CONTRADICTION_CHECK_K = 10


SYSTEM_PROMPT = """You are an internal AI assistant for Nexus Consulting d.o.o., an IT consulting firm.
You answer questions based ONLY on the provided document excerpts.

Rules:
1. Base your answer strictly on the provided context. Do not add information from outside the documents.
2. Always cite your sources: mention the document name and section (e.g., "According to [Source 1: Kova ERP Proposal — Financial Offer]...").
3. If the provided context does not contain enough information to answer, say explicitly: "Based on the available documents, I cannot answer this question." Then briefly explain what is missing.
4. If documents contain contradictory information, explicitly flag the contradiction: "Note: documents contain conflicting information — [explain both versions]."
5. For outdated documents, note when information may be stale.
6. Be concise but complete. Use bullet points for lists."""


CLASSIFY_PROMPT = """Classify this question as either "simple" or "multi_hop".

- simple: can be answered by finding a single relevant passage or document
- multi_hop: requires combining information from multiple documents or multiple retrieval steps

Question: {question}

Reply with JSON only: {{"type": "simple"}} or {{"type": "multi_hop"}}"""


DECOMPOSE_PROMPT = """Break down this complex question into 2-4 simpler sub-questions that together would provide all necessary information to answer the original question.

Original question: {question}

Reply with JSON only: {{"sub_questions": ["...", "...", ...]}}"""


HYDE_PROMPT = """Write a short, specific answer to the following question as if you were an IT consultant at a consulting firm. Include specific names, dates, and technical details where relevant. Do not say you don't know — make a plausible, concrete answer.

Question: {question}

Answer:"""


CONTRADICTION_PROMPT = """An AI assistant answered a question with the response below. You are given {n} document excerpts retrieved for the same question.

Question: {question}

Answer given: {answer}

Document excerpts:
{context}

---

Do any of these excerpts state a DIFFERENT value for the same fact mentioned in the answer? Look specifically for:
- Different dates, numbers, or amounts for the same event
- Different names or roles for the same person
- Different statuses or outcomes for the same project

Reply with JSON only:
{{"contradiction_found": true, "explanation": "<one sentence describing what conflicts>"}}
or
{{"contradiction_found": false, "explanation": ""}}"""


class RAGAssistant:
    def __init__(self):
        self.retriever = HybridRetriever()
        self.client = OpenAI(api_key=os.environ["CHATGPT_API_KEY"].strip())
        self.history: list[dict] = []

    def clear_history(self) -> None:
        self.history = []

    def _llm(self, prompt: str, max_tokens: int = 256) -> str:
        response = self.client.chat.completions.create(
            model=MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()

    def classify_query(self, question: str) -> str:
        try:
            raw = self._llm(CLASSIFY_PROMPT.format(question=question), max_tokens=64)
            return json.loads(raw).get("type", "simple")
        except Exception:
            return "simple"

    def decompose_query(self, question: str) -> list[str]:
        try:
            raw = self._llm(DECOMPOSE_PROMPT.format(question=question), max_tokens=256)
            return json.loads(raw).get("sub_questions", [question])
        except Exception:
            return [question]

    def _generate_hypothetical(self, question: str) -> str:
        """
        HyDE: generate a plausible answer before retrieval.
        The hypothetical answer is semantically closer to actual document passages
        than the raw question, improving vector search recall.
        """
        try:
            return self._llm(HYDE_PROMPT.format(question=question), max_tokens=200)
        except Exception:
            return question  # fallback: use original question

    def _retrieval_query(self, question: str) -> str:
        """Expand short follow-up questions with previous question for retrieval context."""
        if len(question.split()) < 6 and self.history:
            last_user = next(
                (m["content"] for m in reversed(self.history) if m["role"] == "user"),
                "",
            )
            return f"{last_user} {question}"
        return question

    def _check_contradiction(self, question: str, answer: str, broad_chunks: list[dict]) -> str | None:
        """
        Run a broader retrieval (k=10, no HyDE) and ask the LLM whether any chunk
        contradicts the already-generated answer. Returns an explanation string if
        a contradiction is found, otherwise None.
        No HyDE here — we want broad topic coverage, not confirmation of the answer.
        """
        if not broad_chunks:
            return None
        context = format_sources(broad_chunks)
        prompt = CONTRADICTION_PROMPT.format(
            n=len(broad_chunks),
            question=question,
            answer=answer,
            context=context,
        )
        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            data = json.loads(response.choices[0].message.content)
            if data.get("contradiction_found"):
                return data.get("explanation", "Dokumenti vsebujejo nasprotujoče si informacije.")
        except Exception:
            pass
        return None

    def _is_context_useful(self, chunks: list[dict]) -> bool:
        if not chunks:
            return False
        best_score = max(c.get("rerank_score", 0.0) for c in chunks)
        return best_score > RERANK_SCORE_THRESHOLD

    def answer(self, question: str) -> dict:
        """
        Full RAG pipeline with HyDE, sentence-window overlap, and conversation history:
        1. Expand short follow-up questions
        2. Classify (simple / multi_hop)
        3. Generate hypothetical answer (HyDE) for vector search
        4. Retrieve with hybrid search — BM25(query) + vector(hypothetical)
        5. Rerank with original query, expand chunks with neighbors
        6. Generate answer with history context
        """
        retrieval_query = self._retrieval_query(question)
        query_type = self.classify_query(retrieval_query)

        if query_type == "multi_hop":
            sub_questions = self.decompose_query(retrieval_query)
            chunks: list[dict] = []
            seen_ids: set[str] = set()
            best_sub_score = -999.0

            # Keep top-5 per sub-question instead of joint-reranking all results.
            # Joint reranking against the main question kills chunks that answer only
            # one part of a multi-part question (e.g. ERP skills table scores low
            # when the main question asks about BOTH ERP AND cloud experience).
            for sub_q in sub_questions:
                hypothetical = self._generate_hypothetical(sub_q)
                for chunk in self.retriever.search(sub_q, hypothetical=hypothetical, k=5):
                    best_sub_score = max(best_sub_score, chunk.get("rerank_score", -999.0))
                    if chunk["id"] not in seen_ids:
                        chunks.append(chunk)
                        seen_ids.add(chunk["id"])
        else:
            sub_questions = []
            hypothetical = self._generate_hypothetical(retrieval_query)
            chunks = self.retriever.search(retrieval_query, hypothetical=hypothetical)

        useful = self._is_context_useful(chunks) or (
            query_type == "multi_hop" and best_sub_score > RERANK_SCORE_THRESHOLD
        )
        if not useful:
            answer_text = "Based on the available documents, I cannot answer this question. No sufficiently relevant information was found in the document corpus."
            self.history.append({"role": "user", "content": question})
            self.history.append({"role": "assistant", "content": answer_text})
            return {
                "answer": answer_text,
                "sources": [],
                "query_type": query_type,
                "sub_questions": sub_questions,
            }

        context = format_sources(chunks)
        user_message = f"Context documents:\n\n{context}\n\n---\n\nQuestion: {question}"

        recent_history = self.history[-(MAX_HISTORY_TURNS * 2):]
        messages = (
            [{"role": "system", "content": SYSTEM_PROMPT}]
            + recent_history
            + [{"role": "user", "content": user_message}]
        )

        response = self.client.chat.completions.create(
            model=MODEL,
            max_tokens=1024,
            messages=messages,
        )

        answer_text = response.choices[0].message.content.strip()

        # Contradiction check: broader retrieval (no HyDE) to catch conflicting documents
        broad_chunks = self.retriever.search(retrieval_query, k=CONTRADICTION_CHECK_K)
        contradiction = self._check_contradiction(question, answer_text, broad_chunks)
        if contradiction:
            answer_text += f"\n\n⚠️ **Opozorilo — nasprotujoče si informacije:** {contradiction}"

        self.history.append({"role": "user", "content": question})
        self.history.append({"role": "assistant", "content": answer_text})

        sources = [
            {
                "doc_title": c["metadata"]["doc_title"],
                "section": c["metadata"]["section"],
                "doc_path": c["metadata"]["doc_path"],
                "rerank_score": round(c.get("rerank_score", 0.0), 3),
            }
            for c in chunks
        ]

        return {
            "answer": answer_text,
            "sources": sources,
            "query_type": query_type,
            "sub_questions": sub_questions,
        }
