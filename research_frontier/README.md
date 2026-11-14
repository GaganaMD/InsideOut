# Research frontier: independent red team, theory audit and next steps

A skeptical review of the submission at commit `6140750`.
- Everything here is **separate from the submission**: no frozen split, hypothesis, held-out result, persona criterion, memo, persona card, README, manifest or figure was changed.
- New analyses are **exploratory and training-only**.

**Start with** [`07_decision_memo.md`](07_decision_memo.md) (verdict: **SUBMIT WITH MINOR FIXES**).

| # | Report | Contents |
|---|---|---|
| 01 | [Project red team](01_project_red_team.md) | Validity audit; Figure 1 and 3 interval estimands; alternative explanations for the negative result; error search with severities; the five main weaknesses |
| 02 | [Literature and existing solutions](02_literature_and_existing_solutions.md) | 36 verified sources (LLM twins, profiling, attitude–behaviour, defaults), evidence types, comparison matrix, novelty assessment |
| 03 | [Theory audit](03_theory_audit.md) | Where the ten-framework list came from; category mismatch; per-framework classification |
| 04 | [Experiment designs and results](04_experiment_designs.md) | X1–X3 pre-specified (commit `61c451b`), then results |
| 05 | [Theory prioritisation](05_theory_prioritization.md) | Narrowed to two mechanisms, each with a new-data test |
| 06 | [LLM experiment roadmap](06_llm_experiment_roadmap.md) | No-API step 0; minimal controlled design; safeguards; unpriced cost model |
| 07 | [Decision memo](07_decision_memo.md) | Two-page verdict |
| 08 | [Visual and communication audit](08_visual_and_communication_audit.md) | The four figures, ranked fixes |

## Experiments (training participants only; deterministic)
```bash
python research_frontier/experiments/run_experiments.py        # X1 decomposition, X2 construct overlap, X3 composition
python research_frontier/experiments/audit_interval_check.py   # refit vs fixed-model interval widths (Figure 1 audit)
```
Outputs are in `experiments/results/`. Both scripts assert that only training participants are read.

No LaTeX/TikZ diagrams were created; none was needed to support a finding.
