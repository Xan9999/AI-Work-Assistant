"""
LLM-as-judge evaluation over the 15-question eval set.

Usage:
    python eval/evaluate.py
    python eval/evaluate.py --questions eval/questions_sl.json --results eval/results_sl.json --report eval/report_sl.md

Outputs:
    eval/results.json   — per-question scores
    eval/report.md      — human-readable summary
"""

import argparse
import gc
import os
import sys
import json
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Allow importing from src/
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from rag import RAGAssistant

load_dotenv(Path(__file__).parent.parent / ".env")

QUESTIONS_PATH = Path(__file__).parent / "questions.json"
RESULTS_PATH = Path(__file__).parent / "results.json"
REPORT_PATH = Path(__file__).parent / "report.md"

MODEL = os.getenv("CHATGPT_MODEL", "gpt-4o-mini")

JUDGE_PROMPT = """You are evaluating an AI assistant's answer to a question about internal company documents.

Question: {question}
Question type: {q_type}
Expected answer (reference): {expected}
AI assistant's actual answer: {actual}

Score the actual answer on these criteria (0–3 each):

1. **Factual correctness** (0–3): Is the answer factually accurate compared to the expected answer?
   - 3: Fully correct, no factual errors
   - 2: Mostly correct, minor inaccuracies
   - 1: Partially correct, significant gaps or errors
   - 0: Incorrect or hallucinated

2. **Source citation** (0–3): Does the answer cite sources appropriately?
   - 3: Clear, specific source citations (document name + section)
   - 2: Sources mentioned but not specific
   - 1: Vague reference to documents
   - 0: No sources cited

3. **Uncertainty handling** (0–3): For unanswerable questions, does it correctly refuse? For answerable ones, does it not over-hedge?
   - 3: Perfect handling (refuses when appropriate, answers confidently when appropriate)
   - 2: Mostly appropriate
   - 1: Somewhat appropriate
   - 0: Wrong (hallucinates when should refuse, or refuses when should answer)

4. **Contradiction handling** (0–3): For trick questions with contradictions, does it flag them?
   - 3: Explicitly flags contradiction and explains both versions
   - 2: Mentions contradiction briefly
   - 1: Picks one version without noting conflict
   - 0: Not applicable (score 3 automatically for non-trick questions) OR ignores clear contradiction

Reply with JSON only:
{{
  "factual_correctness": <0-3>,
  "source_citation": <0-3>,
  "uncertainty_handling": <0-3>,
  "contradiction_handling": <0-3>,
  "reasoning": "<one sentence explanation>"
}}"""


def judge_answer(client: OpenAI, question: dict, actual_answer: str) -> dict:
    """Use GPT-4o-mini as judge to score one answer."""
    prompt = JUDGE_PROMPT.format(
        question=question["question"],
        q_type=question["type"],
        expected=question["expected_answer"],
        actual=actual_answer,
    )

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    scores = json.loads(response.choices[0].message.content)

    # For non-trick questions, contradiction_handling is auto 3
    if question["type"] != "trick_contradictory":
        scores["contradiction_handling"] = 3

    # For unanswerable questions, source_citation is auto 3 when the answer correctly refuses.
    # Correct refusal = no sources were retrieved (system had nothing to cite).
    # Penalizing citation when there is nothing to cite conflates "no sources" with "bad citation".
    if question["type"] == "unanswerable" and scores["uncertainty_handling"] >= 2:
        scores["source_citation"] = 3

    scores["total"] = (
        scores["factual_correctness"]
        + scores["source_citation"]
        + scores["uncertainty_handling"]
        + scores["contradiction_handling"]
    )
    scores["max_total"] = 12

    return scores


def run_evaluation(questions_path: Path = QUESTIONS_PATH, results_path: Path = RESULTS_PATH, report_path: Path = REPORT_PATH):
    questions = json.loads(questions_path.read_text(encoding="utf-8"))
    api_key = os.getenv("CHATGPT_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("CHATGPT_API_KEY not set — add it to your .env file in the project root")
    client = OpenAI(api_key=api_key)

    print("Initializing RAG assistant...")
    assistant = RAGAssistant()
    print(f"Running evaluation on {len(questions)} questions...\n")

    results = []

    for i, q in enumerate(questions, 1):
        print(f"[{i:02d}/{len(questions)}] {q['id']} ({q['type']}) — {q['question'][:60]}...")

        # Get RAG answer
        t0 = time.time()
        rag_result = assistant.answer(q["question"])
        elapsed = time.time() - t0

        # Judge the answer
        try:
            scores = judge_answer(client, q, rag_result["answer"])
        except Exception as e:
            print(f"  Judge failed: {e}")
            scores = {
                "factual_correctness": 0,
                "source_citation": 0,
                "uncertainty_handling": 0,
                "contradiction_handling": 0,
                "total": 0,
                "max_total": 12,
                "reasoning": f"Judge error: {e}",
            }

        result = {
            "id": q["id"],
            "type": q["type"],
            "question": q["question"],
            "query_type_detected": rag_result["query_type"],
            "actual_answer": rag_result["answer"],
            "sources_retrieved": len(rag_result["sources"]),
            "elapsed_seconds": round(elapsed, 2),
            "scores": scores,
        }
        results.append(result)

        pct = round(scores["total"] / scores["max_total"] * 100)
        print(f"  Score: {scores['total']}/12 ({pct}%) — {scores['reasoning']}\n")

        # Small delay to respect free-tier rate limits
        time.sleep(1)
        gc.collect()

    results_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResults saved to {results_path}")

    write_report(results, report_path)
    print(f"Report saved to {report_path}")


def write_report(results: list[dict], report_path: Path = REPORT_PATH) -> None:
    total_score = sum(r["scores"]["total"] for r in results)
    max_score = sum(r["scores"]["max_total"] for r in results)
    overall_pct = round(total_score / max_score * 100, 1)

    by_type: dict[str, list] = {}
    for r in results:
        by_type.setdefault(r["type"], []).append(r)

    lines = [
        "# Evaluation Report — Nexus Consulting RAG Assistant\n",
        f"**Total score: {total_score}/{max_score} ({overall_pct}%)**\n",
        f"**Questions evaluated: {len(results)}**\n",
        "",
        "## Scores by question type\n",
        "| Type | Questions | Avg score | Avg % |",
        "|------|-----------|-----------|-------|",
    ]

    for q_type, group in by_type.items():
        avg = sum(r["scores"]["total"] for r in group) / len(group)
        avg_pct = round(avg / 12 * 100, 1)
        lines.append(f"| {q_type} | {len(group)} | {avg:.1f}/12 | {avg_pct}% |")

    lines += [
        "",
        "## Per-question results\n",
        "| ID | Type | Score | FC | SC | UH | CH | Question |",
        "|----|------|-------|----|----|----|----|----------|",
    ]

    for r in results:
        s = r["scores"]
        lines.append(
            f"| {r['id']} | {r['type']} | {s['total']}/12 "
            f"| {s['factual_correctness']} | {s['source_citation']} "
            f"| {s['uncertainty_handling']} | {s['contradiction_handling']} "
            f"| {r['question'][:50]}... |"
        )

    lines += [
        "",
        "## Legend",
        "- **FC**: Factual Correctness (0–3)",
        "- **SC**: Source Citation (0–3)",
        "- **UH**: Uncertainty Handling (0–3)",
        "- **CH**: Contradiction Handling (0–3, auto-3 for non-trick questions)",
        "",
        "## Notable failures",
    ]

    failures = [r for r in results if r["scores"]["total"] < 6]
    if failures:
        for r in failures:
            lines.append(f"- **{r['id']}** ({r['type']}): {r['scores']['reasoning']}")
    else:
        lines.append("- No major failures (score < 6/12).")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM-as-judge evaluation for the RAG assistant.")
    parser.add_argument(
        "--questions",
        default=str(QUESTIONS_PATH),
        help="Path to questions JSON file (default: eval/questions.json)",
    )
    parser.add_argument(
        "--results",
        default=str(RESULTS_PATH),
        help="Output path for results JSON (default: eval/results.json)",
    )
    parser.add_argument(
        "--report",
        default=str(REPORT_PATH),
        help="Output path for report Markdown (default: eval/report.md)",
    )
    args = parser.parse_args()
    run_evaluation(
        questions_path=Path(args.questions),
        results_path=Path(args.results),
        report_path=Path(args.report),
    )
