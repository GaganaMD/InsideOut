# Calibration and failure modes (EXPLORATORY; training participants only)

Sources: `MODEL_COMPARISON.csv` (from `benchmark_offline.py`, 20 x 5-fold CV, 2,000 condition-stratified participant
bootstraps) and, for published-twin treatment effects, SD ratios and distributions, `overnight/results/modal_full-20261114`
(10,000 bootstraps; point estimates asserted identical). default_eric n = 428 (human green rate 0.472);
targeting_fairness n = 260. "C" = published GPT-4.1 `demographics_only` (not information-matched; see plan section 3),
"E" = published `full_persona`. No held-out participant was used; nothing here is confirmatory.

## 1. Hard answers are not probabilities, and scored as probabilities they fail

| default_eric | Brier [95% CI] | Log loss (clipped 0.01/0.99) | Accuracy |
|---|---|---|---|
| A0 population average | 0.249 [0.247, 0.252] | 0.692 | 0.528 |
| A1 condition only | 0.237 [0.228, 0.248] | 0.668 | 0.608 |
| C (T 0), hard | 0.409 [0.360, 0.456] | 1.889 | 0.591 |
| E, hard | 0.311 [0.269, 0.355] | 1.438 | 0.689 |

Every published twin answer is a confident 0 or 1, so each wrong answer costs a full Brier point. All published
hard-answer rows are worse than knowing nothing (A0). This is a scoring artefact of hard answers, not proof that
the model has no signal, which is why the recalibrated rows exist.

## 2. Fair comparison: cross-validated recalibration of the hard answer (labelled hybrid)

The published answer is mapped to P(green | answer) inside training folds (Laplace-smoothed), so it is scored as a
probability. This uses human outcomes, so it is a hybrid LLM + statistical prediction, not a pure LLM forecast.

| default_eric | Brier [95% CI] | Gain vs A1 (Brier) [95% CI] | ECE (5-bin) | Calibration slope [95% CI] |
|---|---|---|---|---|
| B10_tuned (Tier A + condition) | 0.238 [0.228, 0.248] | -0.000 [-0.008, +0.007] | 0.007 | 0.96 [0.53, 1.41] |
| B4_tuned (4 cell fields + condition) | 0.236 [0.226, 0.247] | +0.002 [-0.005, +0.008] | 0.011 | 1.00 [0.58, 1.45] |
| C (T 0) recalibrated | 0.241 [0.232, 0.250] | -0.004 [-0.017, +0.009] | 0.001 | 0.95 [0.44, 1.50] |
| C (T 0.7) recalibrated | 0.244 [0.236, 0.252] | -0.006 [-0.018, +0.006] | 0.001 | 0.91 [0.35, 1.53] |
| E recalibrated | **0.215 [0.199, 0.232]** | **+0.022 [+0.004, +0.042]** | 0.002 | 0.99 [0.73, 1.27] |
| empty recalibrated | 0.241 [0.233, 0.250] | -0.004 [-0.009, +0.002] | 0.001 | 0.99 [0.47, 1.50] |

Paired squared-error gains (positive = first model better):
- E_recal - C_t0_recal: **+0.026 [+0.013, +0.040]**; E - C (hard): +0.098 [+0.051, +0.143].
- C_t0_recal - B10_tuned: -0.004 [-0.016, +0.008]; E_recal - B10_tuned: **+0.023 [+0.004, +0.041]**.
- C_t0_recal - empty_recal: -0.000 [-0.012, +0.012] (demographic persona adds nothing detectable over no persona).

targeting_fairness (squared error; A1 = 3.95 [3.27, 4.74], MAE 1.61): nothing beats the condition-only baseline.
C (T 0) hard MSE 4.49 (gain vs A1 -0.54 [-0.92, -0.15]); C recalibrated 4.22 (-0.27 [-0.53, -0.00]); E hard 4.25
(-0.30 [-0.66, +0.09]); E recalibrated 4.16 (-0.21 [-0.49, +0.10]); B10_tuned 4.05 (-0.10 [-0.24, +0.04]); B4_tuned
3.98 (-0.03 [-0.15, +0.09]). The linear recalibration ignores the condition, so on this outcome it loses part of the
randomised contrast that A1 uses; this is a property of the pre-specified recalibration, noted rather than fixed.

**Reading.** Once hard answers are recalibrated, the demographic twin is indistinguishable from the condition-only
baseline and from census statistical models (all within about +/-0.01 Brier). Only the full-profile twin adds
predictive information (about 9% of the A1 Brier), and that profile contains the person's own measured attitudes.

## 3. Treatment-effect recovery (randomised effects)

| Outcome | Human ATE [95% CI] | C T 0 | C T 0.7 | E | empty | B4_tuned |
|---|---|---|---|---|---|---|
| default_eric (P green, green - grey default) | +0.217 [0.124, 0.307] | +0.142 | +0.111 | +0.084 (diff -0.133 [-0.236, -0.027]) | **+0.874** (diff +0.656 [0.555, 0.758]) | +0.184 |
| targeting_fairness (1-9, women-targeted - broad) | -1.284 [-1.756, -0.806] | -0.863 | -0.854 | -0.851 | -1.145 | -0.985 |

- Persona-conditioned twins get the direction right and shrink the size (39-67% of the human effect); the
  persona-free twin inflates the default effect fourfold.
- **The statistical models' good effect recovery is not a forecast.** A1/B recover the effect because they are
  fitted to this experiment's randomised outcomes. For a *new* intervention with no human data they have nothing
  to say, which is the one use case where an LLM could add value, and the only evidence here says its effect sizes
  are off by a factor of 0.4 to 4 depending on prompt. Recalibrated rows are not used for effect recovery: the
  map ignores the condition and mechanically shrinks the contrast (e.g. C_t0_recal +0.026).

## 4. Variance compression and distributional fidelity

- **Rating outcome (fairness).** Human answers use the whole scale (24% answer 5 or lower; 34% answer 9). The
  demographic twin (T 0) puts 0% on 1-5 and 1% on 9, with 99% on 6-8; the full-persona twin puts 64% on 7. SD ratio
  LLM/human 0.34 [demographics] to 0.41 [full persona] (Modal CIs 0.35-0.47 for E); TV distance 0.51-0.57.
- **Binary outcome (default_eric).** Aggregate share is close (TV 0.03-0.07); the SD ratio is uninformative for a
  0/1 variable.
- **Caveat for comparisons with B.** Regression predictions are conditional means, so their SD ratio is low by
  design (B4_tuned 0.26 on fairness) and rounding them gives a poor distribution (TV 0.58). That is acceptable for
  a point forecast but means neither B nor a one-answer twin can serve as a synthetic sample; only a model that
  outputs a distribution (the prepared probability elicitation) can be judged on distributional fidelity.

## 5. Group-level and small-group performance

Mean |predicted group mean - human group mean| (no CIs: biased bootstrap, see plan):

| | default_eric cells (18, >= 8 members) | default_eric small groups (8 single-level Tier A groups, n 10-39) | fairness cells (7) | fairness small groups (14) |
|---|---|---|---|---|
| A0 population average | 0.145 | 0.090 | 0.568 | 0.364 |
| A1 condition only | 0.139 | 0.086 | 0.617 | 0.389 |
| B4_tuned | 0.124 | 0.082 | 0.483 | 0.330 |
| C (T 0) hard | 0.168 | 0.127 | 0.903 | 0.648 |
| E hard | 0.159 | 0.072 | 0.583 | 0.373 |

- Demographic twins have the **largest** group-level errors, worst on the small groups a client would most want
  synthetic respondents for (fairness small groups: 0.65 vs 0.36 for simply using the population mean).
- Human cell and small-group means are themselves noisy (n 8-39), so these errors are dominated by sampling noise;
  read the ranking, not the level.
- B10_fixed shows very low small-group error (0.020 / 0.027) because its weakly penalised group dummies reuse
  other members' outcomes of the same group in the training folds; this is optimistic and not comparable.

## 6. Failure catalogue (when not to trust an LLM persona)

1. **Confident individual answers**: a single sampled answer per person scores worse than the base rate (section 1).
2. **Prompt-dependent effect sizes**: no-persona prompt x4 inflation; persona prompts 0.4-0.7x attenuation (section 3).
3. **Compressed, wrong-shaped distributions** on rating scales: tails (strong objection, "very fair") vanish (section 4).
4. **Small demographic groups**: errors grow, not shrink, relative to the population average (section 5).
5. **Demographics add nothing detectable** over the empty persona (C_recal - empty_recal = -0.000 [-0.012, +0.012]),
   replicating the census-only negative result with an independent method that probably had *more* information
   (party, ideology, religion).
6. **The only working persona is the measured one**: E's gain disappears as a claim about LLMs once one notes that a
   6-item green-values scale plus the condition matches it (accuracy 0.680 vs 0.689; 09 report and Modal run C).

## 7. Limits of this analysis
- One model family (GPT-4.1), two outcomes, both hypothetical choices; training participants only.
- Published twins are single draws; T 0.7 rows mix model error with sampling noise.
- The C proxy is not information-matched and its fields are unverified (plan section 3).
- Bootstrap CIs do not include model-refitting uncertainty for the CV models.
