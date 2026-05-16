"""
RAG assistant: query classification, multi-hop decomposition, answer generation.
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from retrieval import HybridRetriever, format_sources

load_dotenv()

MODEL = os.getenv("CHATGPT_MODEL", "gpt-4o-mini")
RERANK_SCORE_THRESHOLD = -6.0
MAX_HISTORY_TURNS = 3  # how many past Q&A pairs to include in context


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


class RAGAssistant:
    def __init__(self):
        self.retriever = HybridRetriever()
        self.client = OpenAI(api_key=os.environ["CHATGPT_API_KEY"].strip())
        self.history: list[dict] = []  # {"role": "user"|"assistant", "content": "..."}

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

    def _retrieval_query(self, question: str) -> str:
        """
        For very short follow-up questions, prepend the last user question
        so the retriever has enough signal to find relevant chunks.
        e.g. "and the costs?" → "What did Nexus propose to Kova? and the costs?"
        """
        if len(question.split()) < 6 and self.history:
            last_user = next(
                (m["content"] for m in reversed(self.history) if m["role"] == "user"),
                "",
            )
            return f"{last_user} {question}"
        return question

    def _is_context_useful(self, chunks: list[dict]) -> bool:
        if not chunks:
            return False
        best_score = max(c.get("rerank_score", 0.0) for c in chunks)
        return best_score > RERANK_SCORE_THRESHOLD

    def answer(self, question: str) -> dict:
        """
        Full RAG pipeline with conversation history:
        1. Expand short follow-up questions for retrieval
        2. Classify and retrieve context
        3. Build messages = system + recent history + new context + question
        4. Generate answer, update history
        """
        retrieval_query = self._retrieval_query(question)
        query_type = self.classify_query(retrieval_query)

        if query_type == "multi_hop":
            sub_questions = self.decompose_query(retrieval_query)
            all_chunks: list[dict] = []
            seen_ids: set[str] = set()

            for sub_q in sub_questions:
                for chunk in self.retriever.search(sub_q):
                    if chunk["id"] not in seen_ids:
                        all_chunks.append(chunk)
                        seen_ids.add(chunk["id"])

            chunks = self.retriever.rerank(retrieval_query, all_chunks, k=7)
        else:
            sub_questions = []
            chunks = self.retriever.search(retrieval_query)

        if not self._is_context_useful(chunks):
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

        # Build message list: system + last N turns + new user message
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

        # Store only the bare question and answer in history (not the full context block)
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
