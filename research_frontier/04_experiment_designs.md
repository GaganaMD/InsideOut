# 04 · Exploratory experiment designs (written and committed before running)

**Status: EXPLORATORY.** All earlier results, including the held-out evaluation, have already been inspected, so nothing here is confirmatory.
- **Data:** training participants only. The code asserts `split == "train"`, and no test participant is read.
- **Outputs:** written to `experiments/results/`. Frozen outputs are untouched.
- **Code:** `experiments/run_experiments.py`.

## Selection: why only these three
The candidate list was screened for whether a result could change an interpretation we currently publish, and for duplication.

| Candidate | Decision | Reason |
|---|---|---|
| Reliability-adjusted predictability | Not run | Already in `reports/final_audit/headline_challenge/scale_properties.csv` (R² as a share of reliable variance) |
| Age alone vs full demographics | Not run | Already in `headline_challenge/nested.csv` |
| Nonlinear vs regularised demographic models | Not run | Already in `headline_challenge/model_families.csv` (gradient boosting with interactions was worse) |
| Default × green-values interaction | Not run | Pre-registered as H4 and already reported as inconclusive. Re-testing it would be a forking path |
| **Attitude–choice link under alternative scoring** | **Run as X2** | Unresolved construct-validity threat: the green-values scale contains purchase and cost items |
| **Persona differences after composition adjustment** | **Run as X3** | Only done ad hoc for P2 (income within age) and P3 (sex) |
| **Decomposition of green-choice prediction (new)** | **Run as X1** | Figure 2 shows "demographics + default" no better than the base rate, despite a large causal default effect. The reason is unresolved |

## X1 · What actually predicts the hypothetical green choice?
- **Question.** Is the predictive value in Figure 2 carried by green values and the default alone, with demographics adding noise? Or do demographics contribute once combined?
- **Competing explanations.**
  - (a) Demographics add only overfitting noise, so green values + default *without* demographics is at least as good as M3.
  - (b) Demographics carry real signal that is masked in small samples.
  - (c) The default's predictive value is hidden in M1D by demographic overfitting.
- **Data.** `default_eric` training participants (n = 428), the same stratified 5 folds (seed 20261114) and the same logistic regression (C = 1) as the existing exploratory models. Predictors are standardised inside folds.
- **Models.** Prevalence; default only; green values only; green values + default. The existing out-of-fold predictions for M1D and M3 are re-used, with an assert that participant order and folds are identical.
- **Estimand and metric.** Out-of-fold Brier score (also log loss, AUC, calibration slope and 5-bin ECE). Paired differences use a participant bootstrap with 2,000 resamples. These intervals are conditional on the fitted fold models.
- **Meaningful threshold.** |ΔBrier| ≥ 0.010 with a 95% CI excluding 0, the same threshold as before.
- **What would change our interpretation.**
  - If default-only beats the base rate by ≥ 0.010 while M1D does not, the Figure 2 caption ("the default adds little prediction") is incomplete. The default's predictive value is real but cancelled by demographic overfitting.
  - If green values + default is better than M3, the "demographics add nothing" claim strengthens to "demographics hurt in small samples".

## X2 · Is the attitude–choice link just construct overlap?
- **Threat.** The green-values items include product choice (item 1), purchase habits (item 3) and willingness to bear inconvenience (item 6). Those are close to a stated purchase intention, so "attitude predicts choice" could partly be "stated behaviour predicts stated behaviour".
- **Split (fixed in advance from item wording, verified in `question_catalog.json`).**
  - *Attitude-only:* item 2 (consider environmental impact), item 4 (concern about wasting resources), item 5 (environmentally responsible identity).
  - *Behaviour/cost:* items 1, 3 and 6.
- **Models.** Each 3-item subscale + default, compared with default-only and with each other. Same folds, metric and bootstrap as X1.
- **Supplementary.** Training-sample logistic OR per SD for the full scale and each subscale, adjusted for the default; Cronbach's α for each subscale.
- **Interpretation rule.**
  - If the attitude-only subscale improves on default-only by ≥ 0.010 (CI excluding 0), the link is not merely item overlap.
  - If only the behaviour/cost items predict, the README's "measured attitude" language must be narrowed to "stated green purchasing disposition".
  - If the two subscales differ by < 0.010, the overlap threat is not supported at this n.

## X3 · Are persona differences just demographic composition?
- **Question.** Do the robust persona traits survive adjustment for the census variables *not* used to define the persona? Examples: P1's sex, education and income mix; P2's sex and education mix.
- **Data.** Training participants (n = 1,442), corrected scores.
- **Outcomes.** P1 neuroticism and social desirability; P2 neuroticism and social desirability; P3 neuroticism and green values.
- **Model.** OLS of the standardised outcome on a membership indicator, with and without one-hot controls for all other Tier A variables. HC3 95% CIs.
- **Estimand.** Raw vs adjusted standardised difference, and the share retained (adjusted ÷ raw).
- **Interpretation rule.**
  - If ≥ 50% is retained with a CI excluding 0, "survives composition adjustment".
  - Otherwise the persona trait is largely a proxy for other demographics, and "why it fits" should say so.
- **Caveat.** Adjustment can remove real persona effects that act *through* composition (mediation). This is descriptive decomposition, not causal identification.

## Not run, needing new data or authorization
- LLM demographic baseline: see `06_llm_experiment_roadmap.md`.
- Any incentivised or real-behaviour outcome.
- Test–retest reliability of the scales: wave 4 repeated only the heuristics-and-biases items.

---

## Results (added after running; design sections above unchanged since commit `61c451b`)
Command: `python research_frontier/experiments/run_experiments.py`. Two runs gave byte-identical output. Training participants only.

### X1 · Decomposition (n = 428; out-of-fold; paired bootstrap 95% CI, conditional on the fold models)

| Model | Brier | AUC | Calibration slope |
|---|---|---|---|
| Prevalence | 0.249 | – | – |
| Default only | 0.238 | 0.59 | 0.97 |
| Green values only | 0.217 | 0.71 | 0.99 |
| **Green values + default (no demographics)** | **0.203** | **0.75** | 0.99 |
| M1D: demographics + default (existing) | 0.250 | 0.60 | 0.45 |
| M3: demographics + green values + default (existing) | 0.214 | 0.73 | 0.70 |

| Contrast | ΔBrier (95% CI) | Verdict |
|---|---|---|
| Default only vs prevalence | −0.011 (−0.021, −0.000) | Meaningful, but barely clears the threshold |
| Default only vs M1D | −0.011 (−0.025, +0.002) | Not detectable |
| Green values + default vs default only | −0.036 (−0.052, −0.020) | Meaningful |
| **Green values + default vs M3 (adding demographics)** | **−0.012 (−0.024, −0.001)** | **Meaningful: demographics make it worse** |
| *Post-hoc:* green values + default vs green values only | −0.014 (−0.025, −0.003) | Meaningful (not pre-specified) |

**Interpretation.**
- (c) is supported: on its own the default carries predictive value, which demographic overfitting cancels in M1D.
- (a) is supported and strengthened: at this n, demographics *harm* prediction and calibration.
- The post-hoc contrast shows the README's "adds little prediction once green values are known" undersells the default (see `01_project_red_team.md` #1).

### X2 · Construct overlap
- The attitude-only subscale (items 2, 4, 5; α 0.82) + default beats default-only by **−0.026 (−0.040, −0.013)**: meaningful.
- The behaviour/cost subscale (items 1, 3, 6; α 0.89) + default beats default-only by −0.041. It is better than the attitude-only subscale by 0.015 (0.007, 0.022).
- The subscales correlate at r = 0.89.
- OR per SD, adjusted for the default: full scale 2.54, attitude-only 2.18 (1.73–2.75), behaviour/cost 2.78 (2.16–3.57).

**Interpretation.** The attitude–choice link is **not** merely item overlap, because concern and identity items alone predict meaningfully. But the items describing purchasing and cost-willingness predict more strongly, partly because they are more reliable. The accurate phrase is "a measured environmental disposition", not "a pure attitude".

### X3 · Composition adjustment (n = 1,442; HC3 95% CIs; corrected scores)

| Persona and trait | Raw difference (SD units) | Adjusted for other census variables | Retained |
|---|---|---|---|
| P1 neuroticism | −0.50 (−0.64, −0.36) | −0.32 (−0.48, −0.15) | 63% |
| P1 social desirability | +0.45 (+0.31, +0.59) | +0.34 (+0.17, +0.52) | 77% |
| P2 neuroticism | +0.59 (+0.47, +0.71) | +0.34 (+0.21, +0.48) | 58% |
| P2 social desirability | −0.27 (−0.39, −0.14) | −0.15 (−0.29, −0.01) | 56% |
| P3 neuroticism | +0.50 (+0.36, +0.64) | +0.39 (+0.22, +0.55) | 77% |
| P3 green values | −0.32 (−0.47, −0.16) | −0.21 (−0.39, −0.03) | 66% |

The raw differences here are vs non-members, so they are larger than the d vs the whole population shown in the cards.

**Interpretation.** No robust persona trait is merely a proxy for other demographics. All keep more than half their size, with CIs excluding 0. Adjustment controls only main effects, though: P3's concentration in men is an *interaction* and remains a caveat. The adjustment may also remove real effects that operate through composition, so this is not causal.

### Not run
The Dual-Process CRT × default and Prospect Theory loss-aversion × default tests were not run (see `03_theory_audit.md`). The reasons are low power, an unreliable or mostly unscorable moderator, and forking-path risk.
