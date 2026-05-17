# Evaluation Report — Nexus Consulting RAG Assistant

**Total score: 147/180 (81.7%)**

**Questions evaluated: 15**


## Scores by question type

| Type | Questions | Avg score | Avg % |
|------|-----------|-----------|-------|
| simple_search | 6 | 10.0/12 | 83.3% |
| multi_hop | 4 | 9.0/12 | 75.0% |
| unanswerable | 3 | 12.0/12 | 100.0% |
| trick_contradictory | 2 | 7.5/12 | 62.5% |

## Per-question results

| ID | Type | Score | FC | SC | UH | CH | Question |
|----|------|-------|----|----|----|----|----------|
| Q01 | simple_search | 11/12 | 2 | 3 | 3 | 3 | What did Nexus Consulting propose to client Kova d... |
| Q02 | simple_search | 8/12 | 2 | 0 | 3 | 3 | Who on the Nexus team is a specialist in AWS and w... |
| Q03 | simple_search | 10/12 | 2 | 2 | 3 | 3 | What was the total contract value of the Helios BI... |
| Q04 | simple_search | 9/12 | 2 | 1 | 3 | 3 | What programming language and framework is used fo... |
| Q05 | simple_search | 11/12 | 3 | 2 | 3 | 3 | What was the total proposed value of the Atlas clo... |
| Q06 | simple_search | 11/12 | 3 | 2 | 3 | 3 | Who was the project manager for the DataSync integ... |
| Q07 | multi_hop | 11/12 | 2 | 3 | 3 | 3 | Which projects involved cloud migration and what w... |
| Q08 | multi_hop | 7/12 | 1 | 0 | 3 | 3 | Which team members have experience with both ERP s... |
| Q09 | multi_hop | 9/12 | 1 | 3 | 2 | 3 | Which projects exceeded their original timeline an... |
| Q10 | multi_hop | 9/12 | 1 | 2 | 3 | 3 | What clients did Nexus Consulting work with in 202... |
| Q11 | unanswerable | 12/12 | 3 | 3 | 3 | 3 | Who is the CEO of Kova d.o.o.?... |
| Q12 | unanswerable | 12/12 | 3 | 3 | 3 | 3 | What is the annual revenue of Nexus Consulting d.o... |
| Q13 | unanswerable | 12/12 | 3 | 3 | 3 | 3 | What specific security vulnerabilities were found ... |
| Q14 | trick_contradictory | 11/12 | 3 | 2 | 3 | 3 | When did the Atlas cloud migration project go live... |
| Q15 | trick_contradictory | 4/12 | 1 | 0 | 3 | 0 | What technologies does Janez Novak know and at wha... |

## Legend
- **FC**: Factual Correctness (0–3)
- **SC**: Source Citation (0–3)
- **UH**: Uncertainty Handling (0–3)
- **CH**: Contradiction Handling (0–3, auto-3 for non-trick questions)

## Notable failures
- **Q15** (trick_contradictory): The answer contains inaccuracies regarding skill levels compared to the expected answer and does not properly address the contradictions in the skill matrices for different years.
