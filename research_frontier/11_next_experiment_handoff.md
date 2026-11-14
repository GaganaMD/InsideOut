# 11 · Next-experiment handoff

## Ranking of the four options (1 = worst, 5 = best)
| Option | Scientific value | Identification | Feasibility | Cost | Privacy risk (5 = none) | Brace relevance | Notes |
|---|---|---|---|---|---|---|---|
| **A. Published LLM predictions vs our demographic baseline** | 5 | 4 | 5 | 5 ($0) | 5 | 5 | **Done for the green choice** (`09`). Extending to all 19 studies is the next step |
| B. OpenRouter LLM vs demographic statistics | 3 | 3 | 3 | 2 | 2 (participant data sent out) | 4 | Mostly duplicates A, which already has published GPT-4.1 / GPT-5 / Gemini / DeepSeek outputs |
| C. Ablation of concern vs identity vs willingness-to-pay items | 2 | 3 | 5 | 5 | 5 | 3 | **Already done** as X2 (concern/identity vs purchase/cost subscales); do not repeat |
| D. Calibrated uncertainty for persona generation | 3 | 3 | 4 | 5 | 5 | 4 | Useful engineering (refit-aware intervals, Bonferroni flags), not new evidence |

## Best next experiment: A-extended, a census-demographics baseline across the Mega-Study
- **Question.** Across all Mega-Study outcomes, does a transparent Tier A statistical model, fitted on training participants, match published demographics-only LLM twins (GPT-4.1) at predicting individuals?
- **Hypotheses.**
  - H-A1: mean per-outcome correlation (Peng et al.'s metric) of Tier A out-of-fold predictions is at least the demographics-only LLM's, within 0.03.
  - Rival: the LLM extracts demographic signal that linear models miss.
- **Verified data** (GitHub `TianyiPeng/Twin-2K-500-Mega-Study`, Apache-2.0, checked through the GitHub API on 2026-11-14):
  - `results/<study>/demographics_only_<date>/consolidated_llm_values.csv.gz`, plus `empty_persona_*` and `full_persona_*`;
  - `consolidated_original_answers_values.csv.gz`, which holds the human answers keyed by `TWIN_ID`;
  - `evaluation/column_mapping.csv`, which maps outcome columns;
  - 19 study folders under `results/`, and `configs/<study>/<study>_demographics_only.yaml` per study.
- **Steps.**
  1. Write `research_frontier/experiments/mega_benchmark.py`, re-using `llm_benchmark.py`'s fetch and match logic. For each study, download the 3 specifications × 2 files.
  2. Keep **training participants only** (`data/split.csv`). Assert that the human answers equal the published originals.
  3. Pick outcome columns with `evaluation/column_mapping.csv`, dropping timing and meta columns. Treat numeric and ordinal outcomes as continuous, and binary outcomes as logistic.
  4. For each outcome: 5-fold out-of-fold Tier A ridge or logistic predictions (folds stratified, seed 20261114) → Pearson r and accuracy. Compute the same for each LLM specification on the same participants.
  5. Aggregate the mean r across outcomes. Get CIs from a participant-cluster bootstrap (resample participants within each study), and report each study separately.
- **Commands.**
  ```bash
  python research_frontier/experiments/llm_benchmark.py      # existing: green-choice benchmark (done)
  python research_frontier/experiments/mega_benchmark.py     # to be written per the steps above
  ```
- **Runtime and cost.** About 10 MB of downloads and a few minutes of computation. **API cost: $0.**
- **Evaluation.**
  - Paired difference in mean r (Tier A minus demographics-only LLM).
  - Variance ratio (SD of predictions / SD of the outcome) to quantify LLM flattening.
  - Per-study table.
- **Falsification.**
  - The claim that census demographics carry little individual signal regardless of method is **weakened** if the LLM beats Tier A by ≥ 0.05 in mean r with a CI excluding 0.
  - It is **strengthened** if the difference CI lies within ±0.03.
- **Caveats.**
  - The LLM's demographic fields probably include party, ideology and religion (unverified; `09` point 4). Record this, or add those fields to a sensitivity model.
  - Hard LLM answers vs probabilistic statistical predictions.
- **Privacy.** Downloads only; no participant data leave the machine. Matching uses the anonymous `TWIN_ID`. The held-out split is never evaluated.
- **Timing.** **After submission**, or optionally before, since it is cheap. It does not change any submitted conclusion. The green-choice result in `09` is already enough to mention in the interview.
