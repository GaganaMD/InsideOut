# Pre-specified hypotheses and analysis plan

Committed **before** any inner-layer ↔ outer-layer or attitude ↔ choice relationship was examined.
What had been seen at commit time: marginal distributions of scores and demographics, and the green-choice
rate by default condition (train 0.58 green-default vs 0.36 grey-default). Nothing else.

Rules of the game
- All estimation and model selection on the **train split only** (`data/split.csv`, 1,442 people).
- The **test split (616)** is used exactly once, by `src/holdout.py`, after every modelling choice below is frozen.
- Outer layer for personas and the predictability map = **Tier A only**: region, sex, age band, education, race,
  citizenship, marital status, income band, household size, employment. Party is a labelled sensitivity analysis only.
- Constructs (6): GREEN (`w1_score_GREEN`, mean of 6 pro-environment items, 1–5, verified exact);
  social desirability (`w2_score_socialdesirability`, 0–13); tightwad–spendthrift (**re-scored** from
  QID31+QID32+(6−QID33)+(6−QID34), 4–26, high = spendthrift — the shipped score mis-codes QID31 options 6 and 11
  as 0 for 409 people); CRT (`w1_crt2_score`, 0–4); dictator giving (`w3_score_dictator_sender`, 0–100, % of
  hypothetical $5 sent); neuroticism (`w1_score_neuroticism`, 1–5).
- Unless stated, "meaningful" = 95% CI excludes the null **and** effect clears the stated size threshold.

## H1 — The outer layer sees cognition, not temperament or values (predictability map)
Prediction: Tier A ridge regression, 5×5 repeated CV on train, gives CV R² ≥ 0.10 for **CRT** (education, age, sex),
but CV R² < 0.05 for GREEN, social desirability, tightwad–spendthrift, neuroticism and dictator giving.
- Supports: CRT CI lower bound > 0.05 and all others' point estimates < 0.05.
- Falsified: CRT R² < 0.05, **or** any non-cognitive construct with R² ≥ 0.10.
- Alternatives: low R² may reflect scale unreliability (bounded by α) rather than absence of signal; coarse coding
  (age in 4 bands, income in 5) caps achievable R².
- Type: predictive, not causal.
Directional sub-predictions (age band, from the maturity/socio-emotional literature): social desirability rises with
age; neuroticism falls with age. Falsified if the 65+ vs 18–29 difference has the opposite sign with CI excluding 0.

## H2 — Stated green values predict the hypothetical green choice
Model (train, n≈428): logit(chose_green) ~ GREEN_z + green_default + income_lt50k + GREEN_z×green_default.
Prediction: OR per SD of GREEN > 1, CI excluding 1.
- Falsified: CI includes 1 (attitudes do not translate even into a hypothetical costed choice).

## H3 — The default outweighs the attitude
Prediction: average marginal effect (AME) of green_default (probability points) exceeds the AME of +1 SD GREEN.
- Falsified: AME(GREEN, 1 SD) ≥ AME(default).
- Type: the default effect is **causal** (randomised); the GREEN effect is correlational.

## H4 — Attitudes matter more when acting on them requires effort
Prediction: GREEN slope is larger under the **grey default** (choosing green requires switching away) than under the
green default (interaction GREEN_z × green_default < 0).
- Competing prediction: attitudes matter more under the green default, because only low-GREEN people bother to
  switch away (interaction > 0).
- Falsified/uninformative: interaction CI includes 0. Expected power is low (≈210 per condition); a null is
  reported as "not detectable at this n", not as "no interaction".

## H5 — Cost bites harder for the financially constrained (exploratory, may be dropped)
Prediction: GREEN slope is smaller for household income < $50k. Fitted only if each income × condition cell has
≥ 40 people in train and the model converges without separation; otherwise reported as infeasible.

## H6 — Personas: group means transfer, individuals do not
Personas (Tier A only):
- P1: age 65+.
- P2: age 18–49 **and** household income < $50k.
- P3: chosen on **train data only** by this rule: among all Tier A groups defined by one level, or a conjunction of
  two levels from different variables, with n_train ≥ 150 and ≤ 50% member overlap with P1 and with P2, pick the
  group with the largest mean |Cohen's d| vs the train population across the 6 constructs.
Predictions on the holdout:
- (a) For constructs where the persona's train |d| ≥ 0.20, the persona's (shrunken) mean has lower MAE on held-out
  members than the population mean. Falsified if it does not, for the majority of such constructs.
- (b) For constructs with |d| < 0.20, persona and baseline MAE are indistinguishable (the outer layer adds nothing).
- (c) Persona 80% intervals (train 10th–90th percentile) cover 70–90% of held-out members.
- (d) The individual-level MAE gain is small (< 10% of baseline MAE) even where (a) holds — the ecological-fallacy
  prediction.
- Directional: P1 higher social desirability and lower neuroticism than the population; P2 higher neuroticism and
  more spendthrift than the population.

## Frozen implementation choices
- Ridge: one-hot Tier A (drop none; ridge handles collinearity), standardised outcome not required; α chosen by
  inner 5-fold CV over logspace(-2, 3, 30) within each outer fold. Outer CV: 5 folds × 5 repeats, seed 20261114.
- Uncertainty for CV R² and MAE: mean ± 1.96·SD/√(folds) across the 25 outer folds (repeated-CV SE is optimistic;
  flagged), plus a train-bootstrap of the full-sample R² gap for robustness.
- Persona means: empirical-Bayes shrinkage toward the train population mean, τ² estimated by method of moments from
  the between-group variance of all single-level Tier A groups with n_train ≥ 30.
- Insufficient evidence: n_train < 30 for a persona; < 20 per default condition for a behavioural estimate.
- Outcome estimates for personas: raw green-choice rate per default condition with Wilson 95% CI, plus the
  population model's predicted rate for persona members.
