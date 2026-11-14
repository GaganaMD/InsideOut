# Pre-registration: open-weight LLM persona benchmark on Modal GPU (default_eric)

This document was written **before any inference**. The prompt set (`prompts.jsonl`, 1,524 prompts) and the cross-fitted profiles (`profiles.csv`) were frozen first. It is committed before the full run.

## Question
For a group-level forecast of a hypothetical green-energy choice, does an open-weight LLM persona beat:
- the population average; and
- a cheap demographic statistical model?

Central comparison: does adding a **statistically estimated inner-layer profile** help the LLM (profile vs demo)? Does a **narrative** rendering of the *same* numbers change accuracy, calibration or confidence (narrative vs profile)?

**These are different models from GPT-4.1.** Results are labelled with the open-weight model ID and are never pooled with, or substituted for, the published GPT-4.1 twin results.

## Models
All are Apache-2.0, with revisions pinned at run time and recorded in the outputs.

| Role | Model | Parameters | Hardware |
|---|---|---|---|
| Primary | `Qwen/Qwen2.5-7B-Instruct` | 7.6B | bf16 on one L4, 24 GB |
| Replication | `Qwen/Qwen3-4B-Instruct-2507` | 4.0B | non-thinking instruct model |

Qwen2.5-3B was rejected because its licence is not Apache.

## Data and privacy
- **Training participants only.** The test split is never read.
- **What is sent to Modal:**
  - synthetic cell descriptions: age band × sex × income band × 3-level education, only cells with k ≥ 5 in the 2,058-person panel;
  - aggregate estimated profiles, which are ridge predictions from cell fields and are cross-fitted;
  - the public scenario text.
- **What is never sent:** IDs, outcomes, individual scores, free text.
- Scoring against human choices happens locally.

## Design
- **Units:** 76 cells covering 427 of the 428 training participants in default_eric.
  - Each cell is scored under both randomised default conditions and both answer orders.
  - The two answer orders are averaged as `p_green = mean over orders of P(green letter) / (P(A) + P(B))`.
- **Formats:**

| Format | Information given to the model |
|---|---|
| empty | No persona |
| demo | Cell fields only |
| profile | Cell fields + 6 estimated z-scores as a list |
| narrative | The same 6 numbers inside verbal persona sentences, with magnitude words: \|d\| < 0.1 "about average", < 0.3 "slightly", < 0.6 "moderately", otherwise "considerably" |

  Profile and narrative carry identical numeric information. The only difference is framing.
- **Cross-fitting:** 2 folds of the training participants, seed 20261114. Participants in fold f are predicted with profiles fit on fold 1 − f.
- **Baselines**, fit on fold 1 − f and evaluated on fold f:
  - **A (population average):** the condition-specific green rate.
  - **B (demographic model):** logistic regression on the 4 cell fields plus condition (L2, C = 1).
- **Probabilities:** from the model's next-token distribution. No sampling, no temperature.

## Metrics (fixed now)

**Primary.**
1. **Brier score of the group-level probability on each participant.** Each person gets the prediction for their own cell and condition (fold-matched for profile, narrative and B). Differences are reported against A, against B, and for the central contrasts (profile vs demo, narrative vs profile).
2. **Default-effect recovery.** Participant-weighted, cell-standardised contrast P(green | green default) − P(green | grey default), against the human contrast on the same participants. Reported as absolute error.
3. **Calibration.** Intercept and slope from a logistic regression of y on logit(p).

**Secondary.**
- Cell-level participant-weighted MAE against the observed cell rate, alongside a binomial noise floor.
- SD of cell predictions (heterogeneity), and mean |p − 0.5| (confidence).
- Correlation of predictions with the profile's green z-score (stereotyping).
- Performance in cells with ≤ 3 people.

**Uncertainty.** Paired cluster bootstrap over cells (participants resampled within cells), 2,000 resamples, seed 20261114.

## Decision rules (fixed now)
- **The LLM "adds value"** only if its Brier score is below **B's**, with the 95% CI of the difference excluding 0. Beating A alone is not enough.
- **The profile helps** if profile Brier < demo Brier, with the CI excluding 0.
- **Framing matters** if the narrative − profile CI excludes 0 on Brier or on confidence.
- **Individual-level fidelity is not claimed.** All predictions are cell-level, and the median cell has 5 people.

## Smoke test and stopping rules
The smoke test is 16 prompts on Qwen2.5-7B. It passes only if **all** of these hold:
- the GPU starts and the model loads at a resolved, pinned revision;
- "A" and "B" are single tokens;
- the mean A + B probability mass is ≥ 0.90;
- a repeat of 8 prompts agrees within 1e-3;
- the smoke cost is < $0.50.

During the full run:
- If more than 5% of prompts have a mass below 0.5, that model's results are reported as **invalid**, not analysed.
- Each model gets one GPU function call, with a 30-minute timeout and 0 retries.
- A second model runs only if the first passes.

## Cost

| Item | Rate | Amount |
|---|---|---|
| L4 | $0.80/h | — |
| 2 CPU | $0.095/h | — |
| 16 GiB memory | $0.128/h | — |
| **Container total** | **$1.02/h** | — |
| Smoke run, worst case | 20 min | $0.34 |
| Each full model, worst case | 30 min | $0.51 |
| HF weight cache, about 25 GB | $0.09/GiB-month, deleted after the run | under $0.10 |

- **Worst case in total:** about **$1.5**, against a **$5** ceiling.
- **Expected:** under $0.30.
