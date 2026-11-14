# EXPLORATORY: Redistribution follow-up, construct audit and pre-specification

This was written and committed **before** any predictor–outcome relationship was computed. At that point only marginal
distributions had been seen. It is an exploratory analysis added after the original holdout was inspected.
It uses the training split only and does not change any original file.

## Construct-validity audit (verified from `survey.qsf`, the raw CSV and `question_catalog.json`)

| Question | Finding |
|---|---|
| Outcome item | `GOVT_RESPONSIBILITY` (GSS/ANES-style): "Some people think that the government in Washington should do everything possible to improve the standard of living of all poor Americans (Point 1). Other people think it is not the government's responsibility, and that each person should take care of himself (Point 5)." Responses are 1–5, plus 6 = "Don't know". |
| Is it a decision? | **No.** It is a stated attitude, with no choice, no cost and no stakes. The only item with a personal cost is `HLTHTAX` ("How willing would you be to pay higher taxes to improve the level of health care…", 1 = very willing … 5 = very unwilling, 6 = don't know). It is a stated willingness, not a decision. |
| Random assignment | **None.** The survey flow is a fixed sequence of 9 blocks, with no randomizer and no block, question or choice randomization. **There is no experimental condition, so M3 and M1 + condition cannot be fitted.** |
| Outcome type | Ordinal, 5 points. Primary analysis treats it as continuous (MAE, R²). A binary version (points 1–2 = "government should help") is used only for comparability with the green-energy Brier score and AUC. |
| Linked participants | 1,198 unique; 841 train / 357 test. Exclusions: 1 attention-check failure, plus "don't know" on the outcome. |
| Independent attitude measure | Twin `QID287` ("Would you support or oppose…", 1 = strongly oppose … 5 = strongly support), collected in Twin waves 1–3 (January–February 2025). The outcome survey ran 27–30 June 2025, so the two are separated by about 5 months and come from different surveys. |
| Overlap / leakage | No outcome-survey item is used as a predictor. Party (Twin) and 2020 vote (outcome survey) are **excluded** from every model. Predictor and outcome are *different items* but *adjacent constructs* (specific policy support vs a general principle), so a large gain is expected and is **not** a say–do result. |

## Pre-specified constructs
- **Primary, "redistributive policy support"** (`REDIST`): the mean of `QID287_4` (Medicare for All), `QID287_5` (public health
  option) and `QID287_10` (2% wealth tax above $50M). These are the three items about government provision or redistribution. Carbon and immigration items are excluded as off-domain; paid leave (a mandate) and seniors' vouchers (privatisation) are excluded as ambiguous.
- **Sensitivity 1, ideology** (`QID22`, 1 = very conservative … 5 = very liberal). This is a general political self-placement, survey-only and dropped from the outer layer.
- **Sensitivity 2, EQUALITY value** (`QID29_21`, importance as a guiding principle, 1–9). This is a value rather than a policy position. 10 values are missing and are mean-imputed inside each fold.

## Models
These are fixed in advance, use the same stratified 5-fold split (seed 20261114) for every model, and fit all preprocessing inside each fold. The model is ridge regression with alpha = 1.0.
- M0: training-fold mean.
- M1: Tier A demographics.
- M2: Tier A + REDIST (primary).
- M2-ideology and M2-equality: sensitivities, each with a single construct swapped in.
- M3 and M1 + condition: **not applicable** (no randomised condition).

**Outcomes:** the primary outcome is `govt_help` = 6 − GOVT_RESPONSIBILITY, so higher means more government responsibility. The secondary outcome is `tax_willing` = 6 − HLTHTAX.

**Metrics:** out-of-fold MAE and R² (relative to the training-fold mean). Paired participant-bootstrap intervals (2,000 resamples) are reported for ΔMAE and ΔR².

**"Practically meaningful" increment:** ΔR² ≥ 0.05 with a 95% CI excluding 0. Smaller CI-excluding gains count as "detectable but small".

**Binary comparability check:** logistic regression with C = 1.0 on `govt_help ≥ 4`, reporting Brier, log loss and AUC.
