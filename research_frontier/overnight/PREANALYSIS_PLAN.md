# PREANALYSIS_PLAN: LLM twins vs humans on randomised choices (pilot: `default_eric`)

**Status.** Written before any paid call; commit it before the pilot.
- **Exploratory relative to the submission**, but the hypotheses below are fixed in advance for this experiment.
- **Data:** training participants only (n = 428). **The held-out split is never used.**

## Arms (information-matched)
| Arm | The LLM sees | Statistical counterpart (same participants, 5-fold out-of-fold) | Privacy tier |
|---|---|---|---|
| E: empty | Scenario including the assigned default | Default-only logistic | 1 |
| D: cell demographics | Coarsened Tier A cell + scenario with default | Logistic on the same cell variables + default | 1 |
| B: condition-blind | Coarsened Tier A cell + **neutral** scenario (no default) | Logistic on the cell variables only | 1 |
| G: disposition | D + green-values tercile (only if cells stay k ≥ 5) | Logistic on cell + tercile + default | 1 or 2: excluded from the pilot |
| F: full profile | **Published** GPT-4.1 full-persona predictions (no new calls) | Green values + default (X1) | 0 |

- **Model:** GPT-4.1-mini in the pilot; GPT-4.1 to align with the published runs.
- **Sampling:** temperature 0.7, 10 samples per prompt.
- **Recorded per call:** the sampled choice and the elicited probability `p`.
- **Mapping:** each participant receives their cell's predictions for their own randomised condition, combined locally.

## Primary hypotheses (Holm-corrected across these two)
- **P1, treatment-effect recovery.** For arm D, the LLM-implied default effect (mean `p` under green default − mean `p` under grey default, averaged over participants) differs from the human effect (+0.217, CI 0.123–0.307).
  - Prediction from the published empty-persona result: **exaggerated**, D − human > +0.10.
  - Falsified (the LLM recovers the effect) if the 95% CI of D − human lies within ±0.10.
- **P2, individual prediction.** Arm D's Brier score (on `p`) is no better than arm E's.
  - Equivalence margin ±0.010 Brier: a TOST-style check with a 90% CI inside ±0.010.
  - Rejected if D improves on E by ≥ 0.010 with the 95% CI excluding 0.

## Secondary (exploratory, no correction, labelled as such)
- **S1:** LLM arm D vs its statistical counterpart (Brier, balanced accuracy, calibration slope).
- **S2:** arm B vs arm D (does the LLM use the condition information?), and B's implied default effect, which should be ≈ 0 by construction (manipulation check).
- **S3:** variance compression: SD of `p` across cells vs the SD of human cell means.
- **S4:** run-to-run stability: agreement of sampled choices across the 10 samples.

## Metrics and uncertainty
- **Metrics:** Brier and log loss on `p`; accuracy and balanced accuracy on the majority sampled choice; calibration slope and 5-bin ECE.
- **Uncertainty:** 95% CIs from a paired participant bootstrap (4,000 resamples). Sensitivity: a cluster bootstrap over cells, because predictions are cell-level.
- **Baselines:** prevalence; default-only; matched logistic models; published GPT-4.1 empty / demographics-only / full-persona predictions.

## Stopping and validity rules
1. **Budget:** hard cap per run (pilot $3); the runner stops scheduling once spending plus reserve would exceed it.
2. **Invalid outputs:** if more than 2% of outputs are malformed after 50 calls, stop. Fix the template (which changes its hash) and re-run from scratch. Results from different template hashes are never pooled.
3. **No peeking:** the pilot's results do not change P1, P2 or the arms. A medium run on new studies needs its own plan addendum committed before it starts.
4. **Exclusions:** cells with k < 5 are never sent; their members get arm E's prediction. Report how many there are (pilot: 1 of 428).
5. **Reporting:** report every arm and metric, including nulls and failures, with the template hash, model ID, run date and actual spend.

## Planned extensions (addendum required before running)
- **targeting_fairness:** the outcome is a 1–9 rating. Treatment effect = mean rating difference; MAE replaces Brier.
- **context_effects:** the effect is the decoy-induced shift in target-option share within each product.
