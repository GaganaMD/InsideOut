# Methods and held-out evaluation protocol

## Data
- **Twin-2K-500:** 2,058 participants. Waves 1–3 provide the six inner-layer scores:

  | Construct | Score used |
  |---|---|
  | Green values | 1–5 |
  | Social desirability | Reynolds Form C, 0–13 |
  | Tightwad–spendthrift | 4–26, re-scored from items |
  | CRT-2 | 0–4 |
  | Dictator giving | % of $5, hypothetical |
  | Neuroticism | 1–5 |

- **Outer layer, "Tier A":** region, sex, age band (4 levels), education, race, citizenship, marital status, income band (5 levels), household size and employment. Party is excluded except in one labelled sensitivity persona.
- **Behaviour:** Mega-Study `default_eric`. A hypothetical choice between a $39 renewable tariff and a $32 standard tariff, with a randomised green or grey default. 600 participants: 428 train, 172 test. There are no incentives.

## Split and pre-registration (provenance)

| Step | Commit | Date |
|---|---|---|
| Frozen 70/30 participant split, `data/split.csv` (1,442 train / 616 test; sha256 `8ef47da04a8d814d…`, checked by a test) | `cbf45f7` | 2026-11-14 |
| Hypotheses, falsifiers and analysis choices pre-specified (`hypotheses.md`) | `2540e2c` | 2026-11-14 |
| Holdout evaluation script committed before its first run (`src/holdout.py`) | `8104628` | 2026-11-14 |
| First and only holdout run (`results/`, byte-stable since) | `6b21fc3` | 2026-11-14 |

## Models (training data only)
- **Predictability map** (`src/predictability.py`):
  - ridge regression on one-hot Tier A, with an inner-CV penalty, under 5×5 repeated CV;
  - compared against a population-mean baseline;
  - intervals are mean ± 1.96·SD/√5 over fold estimates.
- **Say–do model** (`src/saydo.py`):
  - logistic regression of the choice on green values (standardised), default condition and income, plus green values × default;
  - average marginal effects with bootstrap CIs.
- **Personas** (`src/personas.py`):
  - membership is defined by Tier A criteria only;
  - **"Typical"** is the group mean shrunk toward the population (empirical Bayes; the prior variance comes from all single-level Tier A groups);
  - **"distinct"** (pre-registered) means |d| ≥ 0.20 with a raw-mean CI excluding 0;
  - since 2026-11-15, a shrinkage-adjusted label is shown alongside it;
  - behaviour is reported only where a default-condition cell has at least 20 people;
  - P3 was chosen by a pre-registered rule on training data.

## Held-out evaluation (`src/holdout.py`; run once)
- **Predictability:** the training-fit model is scored on the 616 test participants (test R², MAE vs the population-mean baseline).
- **Personas:**
  - test d is computed against the training population mean and SD;
  - individual MAE of the persona "Typical" vs the population mean, on held-out members, with a participant-bootstrap CI of the MAE reduction (raw units);
  - coverage of the training p10–p90 interval;
  - behaviour Brier scores, using the persona rate only where the training n is at least 20.
- **Say–do:** decline shares and model log loss on test participants.

## Scoring modes
Three shipped scale scores were found to be mis-scored by the dataset's string matching. These are reproduced in `reports/final_audit/statistical_audit.md`:
- ST-TW (corrected in the default pipeline);
- social desirability and CRT (corrected scores are used for the current findings).

`results/` keeps the legacy social-desirability and CRT scores for exact historical reproduction. The corrected reruns are in `02_evidence/corrected_scores/`.

## Post-review corrections
`02_evidence/post_review_corrections.md` lists every change made after the holdout run. These are code fixes, reporting and units, and wording. It states that no estimate, split or held-out result changed.
