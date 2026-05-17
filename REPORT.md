# RAG Conversational Assistant — Project Report

**Course assignment: Prototype conversational assistant over a synthetic document corpus**
**Company context: Nexus Consulting d.o.o. (synthetic IT consulting firm)**

---

## 1. System Overview

The assistant answers natural-language questions about Nexus Consulting's internal documents using a Retrieval-Augmented Generation (RAG) pipeline. It retrieves relevant document excerpts, then generates grounded answers using a large language model. All answers are cited to specific source documents and sections.

**Entry points:**
- `python src/cli.py` — interactive chat with rich terminal UI
- `python eval/evaluate.py` — automated LLM-as-judge evaluation over 15 test questions

---

## 2. Document Corpus

### 2.1 Composition

| Format | Count | Directory |
|--------|-------|-----------|
| `.md`  | 31    | `data/documents/` (3 subdirectories) |
| `.txt` |  2    | `data/documents/technical_reports/` |
| **Total** | **33** | |

Documents are organized into three thematic folders:

| Folder | Count | Content |
|--------|-------|---------|
| `meeting_minutes/` | 12 | Kickoff meetings, sprint reviews, steering committees, retrospectives |
| `proposals/` | 10 | Client proposals, final project reports, financial offers |
| `technical_reports/` | 11 | Architecture specs, skills matrices, vendor comparisons, postmortems |

### 2.2 Engineered Noise

The corpus contains deliberate inconsistencies to test the system's contradiction-handling:

- **Contradictory go-live dates** (Q14): The Atlas cloud migration project has four conflicting dates across documents (Dec 15 2024 in the go-live memo, Jan 8 2025 in the steering committee minutes, Feb 28 2025 in the postmortem, Mar 31 2025 in a proposal). This tests whether the assistant surfaces conflicts rather than picking one date arbitrarily.
- **Skills matrix drift** (Q15): `team_skills_matrix_2023.md` and `team_skills_matrix_2024.md` show different skill levels for the same employee (Janez Novak), reflecting realistic annual updates. This tests whether the assistant notes the discrepancy and identifies which version is more recent.
- **Outdated documents**: Several 2022–2023 reports describe project statuses that contradict more recent documents.

### 2.3 Chunk Statistics

After ingestion, the corpus produces **225 chunks** across all 33 documents, with a target size of 400 tokens and 80-token overlap between consecutive chunks. All chunks are stored in ChromaDB (vector index) and a BM25 pickle file (keyword index).

---

## 3. RAG Pipeline Architecture

### 3.1 Ingestion (`src/ingest.py`)

1. Reads all `.md` and `.txt` files recursively from `data/documents/`
2. Splits each document into overlapping chunks (400 tokens, 80-token stride)
3. Each chunk gets a stable ID: `{relative_path}::chunk_{index}`
4. Stores chunks in two indexes:
   - **ChromaDB** (vector index) using the E5 multilingual embedding model with `"passage: "` prefix
   - **BM25 pickle** (`data/bm25_index.pkl`) using `rank-bm25`

### 3.2 Retrieval (`src/retrieval.py`)

The `HybridRetriever` class executes a four-stage pipeline:

```
BM25(query) ──────────────────────────────────┐
                                               ├──► RRF fusion ──► Cross-encoder rerank ──► Neighbor expand
Vector(hypothetical_answer or query) ─────────┘
```

**Stage 1 — BM25 keyword search**
Tokenizes the query and scores all chunks by BM25 relevance. Returns top-20 candidates with their BM25 scores.

**Stage 2 — Vector semantic search**
Encodes the text with `"query: "` prefix (required by E5 models) and queries ChromaDB for the 20 nearest neighbors by cosine distance. Crucially, the *vector search uses the HyDE hypothetical answer* rather than the raw query (see §3.4).

**Stage 3 — Reciprocal Rank Fusion (RRF)**
Merges both ranked lists without requiring score normalization:

```
RRF_score(chunk) = 1/(rank_bm25 + 1 + 60) + 1/(rank_vector + 1 + 60)
```

The constant 60 dampens the advantage of very high rankings, making the fusion robust when one retriever dominates.

**Stage 4 — Cross-encoder reranking**
The top-20 fused candidates are re-evaluated by a cross-encoder (`cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`), which reads each `(query, chunk)` pair jointly. This is more accurate than bi-encoder similarity but too slow to run on the full corpus. Returns top-5 candidates ranked by reranker logit score.

**Stage 5 — Sentence-window expansion**
Each reranked chunk is expanded with its immediate neighbors (`chunk_{idx-1}` and `chunk_{idx+1}`) from the same document. The narrow chunk was used for precise retrieval; the expanded version gives GPT richer context. This avoids the boundary-cut problem where an answer starts in one chunk and ends in the next.

### 3.3 Answer Generation (`src/rag.py`)

The `RAGAssistant` uses OpenAI's `gpt-4o-mini` (configurable via `CHATGPT_MODEL` in `.env`).

**System prompt** instructs the model to:
- Base answers strictly on the provided excerpts
- Cite sources by name and section
- Explicitly say "I cannot answer" when context is insufficient
- Flag contradictions explicitly when documents disagree

**Uncertainty threshold**: If the best reranker score across all retrieved chunks is below −6.0, the context is considered too weak and the model replies with a canned "cannot answer" message without an LLM call.

**Conversation history**: The last 3 question–answer turns are included in each request so the model can resolve follow-up questions. Short follow-up queries (< 6 words) are expanded with the previous question before retrieval to improve recall.

### 3.4 HyDE (Hypothetical Document Embeddings)

Before vector search, the assistant generates a plausible answer to the question using GPT. This hypothetical answer is then used as the vector search query instead of the raw question.

**Why this helps**: Document chunks describe facts ("Atlas went live on Dec 15"); questions ask about facts ("When did Atlas go live?"). These are semantically different surface forms. A hypothetical answer phrasing — "Atlas went live in December 2024" — is much closer to actual document language, improving vector recall.

BM25 always uses the original query (keyword matching needs exact terms from the question). The cross-encoder reranker always uses the original query (evaluating actual relevance to the question).

### 3.5 Multi-Hop Query Handling

Questions classified as `multi_hop` by an LLM classifier are decomposed into 2–4 sub-questions. Each sub-question triggers a separate retrieval round with its own HyDE hypothetical. Results from all rounds are merged (deduplicating by chunk ID) and then reranked jointly against the original question. This allows the system to find "team member skills" in one document and "project involvement" in another, then combine them into a single answer.

### 3.6 Multilingual Support

All models handle Slovenian text natively:
- **Embedding model**: `intfloat/multilingual-e5-base` — trained on 100 languages
- **Reranker**: `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` — XLM-RoBERTa base trained on mMARCO (multilingual MS MARCO), handles Slovenian queries against Slovenian documents
- **LLM**: GPT-4o-mini handles Slovenian natively

Models are stored project-locally in `data/models/` (downloaded once via `python src/download_models.py`) to avoid HuggingFace cache dependencies.

---

## 4. Evaluation

### 4.1 Question Set (`eval/questions.json`)

15 questions across four categories:

| Category | Count | Description |
|----------|-------|-------------|
| `simple_search` | 6 | Single-document lookup (financial values, names, technologies) |
| `multi_hop` | 4 | Requires combining information across ≥2 documents |
| `unanswerable` | 3 | Information genuinely not in the corpus |
| `trick_contradictory` | 2 | Documents contain conflicting information |

### 4.2 LLM-as-Judge Methodology

Each answer is scored by GPT-4o-mini on four criteria (0–3 each, max 12):

| Criterion | Abbr. | What it measures |
|-----------|-------|-----------------|
| Factual Correctness | FC | Are stated facts accurate against the reference answer? |
| Source Citation | SC | Does the answer cite specific documents and sections? |
| Uncertainty Handling | UH | Does it say "I don't know" when appropriate, without over-hedging? |
| Contradiction Handling | CH | Does it flag conflicting information when present? (auto-3 for non-trick questions) |

The judge prompt uses `response_format: {"type": "json_object"}` for reliable structured output. Scores are written to `eval/results.json`.

### 4.3 Results

**Overall score: 136 / 180 (75.6%)**

| Category | Score | Percentage | Avg/12 |
|----------|-------|------------|--------|
| simple_search | 66/72 | 91.7% | 11.0 |
| multi_hop | 32/48 | 66.7% | 8.0 |
| unanswerable | 27/36 | 75.0% | 9.0 |
| trick_contradictory | 11/24 | 45.8% | 5.5 |

**Average latency:** 22.2 s (simple: ~10 s, multi-hop: ~35 s)

### 4.4 Analysis by Category

**Simple search (91.7%)** — The hybrid retrieval pipeline reliably finds the relevant passage. The two partial failures (Q01: 11/12, Q02: 9/12) are due to imprecise secondary facts rather than retrieval failures.

**Multi-hop (66.7%)** — The weakest category apart from contradictions. Q08 (4/12) asks which team members have *both* ERP and cloud experience; the decomposed sub-questions retrieved skills-matrix chunks and project chunks, but GPT hallucinated names not found in those specific chunks. The primary issue is that the relevant information is spread across dense table-like sections in two different skills matrices, and the expanded chunks still don't contain all the necessary rows.

**Unanswerable (75.0%)** — The system correctly declines to answer all three questions, scoring 3/3 on Factual Correctness and Uncertainty Handling. The 75% rather than 100% is entirely due to Source Citation being scored 0/3 — when no sources are retrieved, none can be cited, which is technically correct behavior but the judge penalizes it.

**Trick/contradictory (45.8%)** — The system's main weakness. For Q14 (Atlas go-live date), the model found the most prominent source (the go-live memo) and answered with that date rather than surfacing the four conflicting dates. For Q15 (Janez Novak skills), it gave a partially accurate answer but didn't note the 2023 vs. 2024 discrepancy. The contradiction-detection logic needs to be explicit in the prompt or handled with dedicated retrieval of multiple documents.

---

## 5. Identified Weaknesses and Potential Improvements

### 5.1 Contradiction Detection (most impactful)

**Problem**: The system doesn't explicitly search for contradicting documents when answering. It returns the top-ranked chunks, which typically agree with each other.

**Improvement**: After initial retrieval, run a second targeted retrieval with a contradiction-seeking prompt: *"Find other documents that mention [topic] and may have different information."* Or: after getting the initial answer, do a verification pass that retrieves documents with conflicting claims and asks the model to reconcile them explicitly.

### 5.2 Table/Structured Data Retrieval

**Problem**: The skills matrices store information in Markdown tables. A chunk containing a table row about one employee may be split from the header row that defines the columns. The model then misidentifies or hallucinates column values.

**Improvement**: Treat tables as atomic units — do not chunk across table boundaries. During ingest, detect Markdown tables and store the full table (with header) as a single chunk, even if it exceeds the target chunk size.

### 5.3 Multi-Hop Aggregation Accuracy

**Problem**: Multi-hop answers are assembled from up to 7 chunks, but GPT sometimes fails to correctly cross-reference entities (e.g., a team member name in a skills document vs. a project participation in a meeting document).

**Improvement**: After decomposing a multi-hop question, extract named entities from each sub-answer and use them as filters for subsequent retrieval steps. This "chain-of-thought retrieval" approach anchors each step on verified facts.

### 5.4 Query Classifier Reliability

**Problem**: The classifier sometimes misclassifies questions. Q02 and Q03 (simple lookups) were classified as `multi_hop`, triggering extra LLM calls and slower responses with no benefit.

**Improvement**: Fine-tune the classification prompt with more examples. Alternatively, always run the simple pipeline and only fall back to multi-hop if the initial retrieval score is below threshold.

### 5.5 Latency

**Problem**: Multi-hop queries take 30–47 seconds due to 4–8 sequential LLM calls (classify → decompose → N×HyDE → final answer + judge).

**Improvement**: Parallelize the HyDE calls for sub-questions. The sub-question hypothetical answers are independent and can be generated in parallel using `asyncio` with the OpenAI async client.

---

## 6. File Structure

```
AI-Work-Assistant/
├── data/
│   ├── documents/          # 33 synthetic documents (31 .md, 2 .txt)
│   │   ├── meeting_minutes/
│   │   ├── proposals/
│   │   └── technical_reports/
│   ├── chroma_db/          # ChromaDB vector index (225 chunks)
│   ├── bm25_index.pkl      # BM25 keyword index
│   ├── models/             # Local model storage
│   │   ├── intfloat--multilingual-e5-base/
│   │   └── cross-encoder--mmarco-mMiniLMv2-L12-H384-v1/
│   └── CORPUS_MANIFEST.md  # Document index with contradiction markers
├── src/
│   ├── ingest.py           # Chunking, embedding, index building
│   ├── retrieval.py        # HybridRetriever (BM25 + vector + rerank + expand)
│   ├── rag.py              # RAGAssistant (HyDE, multi-hop, history, generation)
│   ├── cli.py              # Interactive CLI with rich UI
│   └── download_models.py  # One-time model download to data/models/
├── eval/
│   ├── questions.json      # 15 evaluation questions with reference answers
│   ├── evaluate.py         # LLM-as-judge evaluation runner
│   ├── results.json        # Per-question scores (generated)
│   └── report.md           # Scores summary table (generated)
├── .env                    # CHATGPT_API_KEY, CHATGPT_MODEL
├── requirements.txt
└── REPORT.md               # This document
```

## 7. Setup and Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Download models to data/models/ (one-time, ~500 MB)
python src/download_models.py

# Build indexes (one-time, or after adding documents)
python src/ingest.py

# Run interactive assistant
python src/cli.py

# Run evaluation
python eval/evaluate.py
```

`.env` file:
```
CHATGPT_API_KEY=sk-...
CHATGPT_MODEL=gpt-4o-mini
```
