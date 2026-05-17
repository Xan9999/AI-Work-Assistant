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
CONTRADICTION_CHECK_K = 15


SYSTEM_PROMPT = """You are an internal AI assistant for Nexus Consulting d.o.o., an IT consulting firm.
You answer questions based ONLY on the provided document excerpts.

Rules:
1. Base your answer strictly on the provided context. Do not add information from outside the documents.
2. Always cite your sources: mention the document name and section (e.g., "According to [Source 1: Kova ERP Proposal — Financial Offer]...").
3. If the provided context does not contain enough information to answer, say explicitly: "Based on the available documents, I cannot answer this question." Then briefly explain what is missing.
4. When documents contain conflicting dates or values for the same event, report the value from the most recently dated document as authoritative, and list all versions chronologically (e.g. "Originally planned June 2024, revised September 2024, final confirmed December 15, 2024 per November memo"). Do not silently pick one version.
5. If documents contain contradictory information that cannot be resolved by document date, explicitly flag the contradiction: "Note: documents contain conflicting information — [explain both versions]."
6. For outdated documents, note when information may be stale.
7. For questions asking "which projects", "which team members", or "list all X", your answer must be exhaustive — scan ALL provided sources and include every matching entity, not just the most prominent one.
8. Be concise but complete. Use bullet points for lists."""


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


ALTERNATIVE_PROMPT = """One possible answer to the question below is provided. Write a SHORT, different, conflicting answer that a different document might state — use a different date, number, name, or status. Do not explain, do not hedge. Write only the alternative answer.

Question: {question}
Known answer: {known_answer}

Alternative answer:"""


CONTRADICTION_PROMPT = """You are checking whether the provided document excerpts contain conflicting factual claims about the same topic.

Document excerpts:
{context}

Do any excerpts state an explicitly DIFFERENT value (not just additional detail) for the exact same fact?
Examples of real contradictions: "go-live was June 2024" vs "go-live was December 2024", "skill score is 3" vs "skill score is 1".
Do NOT flag: missing info, different roles (e.g. CEO vs IT director), partial vs full dates that are consistent, same info stated differently.

Reply with JSON only:
- {{"contradiction": false}} if no real contradiction found
- {{"contradiction": true, "note": "fact X: document A says Y, document B says Z"}} if real contradiction found"""


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

    def _is_context_useful(self, chunks: list[dict]) -> bool:
        if not chunks:
            return False
        best_score = max(c.get("rerank_score", 0.0) for c in chunks)
        return best_score > RERANK_SCORE_THRESHOLD

    def _generate_alternative(self, question: str, known_answer: str) -> str | None:
        """Generate a plausible conflicting answer to attract contradicting documents via vector search."""
        try:
            return self._llm(
                ALTERNATIVE_PROMPT.format(question=question, known_answer=known_answer),
                max_tokens=80,
            )
        except Exception:
            return None

    def _check_contradiction(
        self,
        question: str,
        primary_context: str,
        sub_questions: list[str] | None = None,
    ) -> str | None:
        """Broad retrieval per sub-question + alternative-HyDE pass to surface contradicting documents.

        Two retrieval passes:
        1. Per-sub-question (no HyDE): broad coverage of the topic
        2. Alternative-HyDE: generate a conflicting answer, use it as hypothetical to attract
           documents that state a different value — the opposite of standard HyDE
        """
        try:
            queries = sub_questions if sub_questions else [question]
            seen_ids: set[str] = set()
            broad_chunks: list[dict] = []
            per_query_k = max(3, CONTRADICTION_CHECK_K // len(queries))

            # Pass 1: per-sub-question broad retrieval (no HyDE)
            for q in queries:
                for chunk in self.retriever.search(q, hypothetical=None, k=per_query_k):
                    if chunk["id"] not in seen_ids:
                        broad_chunks.append(chunk)
                        seen_ids.add(chunk["id"])

            # Pass 2: alternative-HyDE — extract a hint from primary context and search
            # for documents that disagree with it
            first_chunk_text = broad_chunks[0]["text"] if broad_chunks else ""
            alternative = self._generate_alternative(question, first_chunk_text[:300])
            if alternative:
                for chunk in self.retriever.search(question, hypothetical=alternative, k=5):
                    if chunk["id"] not in seen_ids:
                        broad_chunks.append(chunk)
                        seen_ids.add(chunk["id"])

            combined = primary_context + "\n\n---\n\n" + format_sources(broad_chunks)
            raw = self._llm(
                CONTRADICTION_PROMPT.format(context=combined),
                max_tokens=200,
            )
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            data = json.loads(raw)
            if data.get("contradiction"):
                return data.get("note", "Conflicting information found in documents.")
        except Exception:
            pass
        return None

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

            for sub_q in sub_questions:
                hypothetical = self._generate_hypothetical(sub_q)
                for chunk in self.retriever.search(sub_q, hypothetical=hypothetical):
                    if chunk["id"] not in seen_ids:
                        chunks.append(chunk)
                        seen_ids.add(chunk["id"])
        else:
            sub_questions = []
            hypothetical = self._generate_hypothetical(retrieval_query)
            chunks = self.retriever.search(retrieval_query, hypothetical=hypothetical)

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
        contradiction_note = self._check_contradiction(
            question, context, sub_questions=sub_questions if sub_questions else None
        )

        user_message = f"Context documents:\n\n{context}\n\n---\n\nQuestion: {question}"
        if contradiction_note:
            user_message += (
                f"\n\n⚠️ Opozorilo: Dokumenti vsebujejo nasprotujoče si informacije — "
                f"{contradiction_note}. Razreši protislovje eksplicitno v odgovoru."
            )

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
