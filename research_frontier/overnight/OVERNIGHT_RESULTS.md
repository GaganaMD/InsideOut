# Offline batch results: run `full-20261114` (EXPLORATORY; training participants only)

## Run record

| | |
|---|---|
| Status | **COMPLETED**: 18/18 tasks done, 0 failed, 0 resumed |
| Run ID | `full-20261114` |
| Modal app / function call | `ap-iZaSfXwamiHHroUCyfUR2I` / `fc-01M7DKWTZXJDPMMQK36DS0R35Q` (workspace `gagana-md-work`, env `main`) |
| Code | commit `3762a12`, `--mode full`; bundle sha256 matched the manifest (`69b250dd…`, `471b3188…`) |
| Time (UTC) | launched 18:07:39; orchestrator 18:07:46 → 18:09:19 (93 s); first checkpoint was already present when polled at 18:08:03 |
| Cost | **$0.0047** for this run (Modal billing report). Worst-case gate was $1.04 against a $5 ceiling. CPU only. |
| Results | Modal Volume `brace-overnight-results/full-20261114/`; copied to `overnight/results/modal_full-20261114/` (aggregate statistics only) |
| Settings | 10,000 bootstrap resamples (A, B); 100 × 5-fold CV repeats (C) |

**Data governance.**
- **Twin-2K-500:** CC BY 4.0, released "after anonymization and removal of sensitive columns".
- **Twin-2K-500 Mega-Study:** Apache-2.0, both the dataset and the GitHub results.
- Both licences permit copying and processing anywhere, subject to attribution. Neither card restricts cloud processing.
- The upload was a pseudonymous, training-only subset processed in a private workspace.
- Licences are copyright terms, not participant consent terms. Those were set by the data publishers when they released the data publicly.

**Attribution.**
- Twin-2K-500, Toubia et al. (2025), CC BY 4.0.
- Twin-2K-500 Mega-Study and published GPT-4.1 twin predictions, Peng et al. (2025, arXiv:2509.19088), Apache-2.0.

**Coding.** In targeting_fairness, treatment = **saw the women-targeted plan**, coded from `Segment` (display logic), because the embedded `target` label is inverted.

## A. Treatment-effect recovery: human vs published GPT-4.1 twins (same participants, same assigned condition)

| Study (outcome) | Human ATE [95% CI] | GPT-4.1 specification | LLM ATE [95% CI] | LLM − human [95% CI] |
|---|---|---|---|---|
| default_eric (P(choose green), green − grey default) | **+0.217** [0.124, 0.307] | demographics, T 0 | +0.142 [0.049, 0.237] | −0.075 [−0.193, 0.045] |
| | | demographics, T 0.7 | +0.111 [0.017, 0.205] | −0.107 [−0.229, 0.016] |
| | | full persona, T 0.7 | +0.084 [−0.010, 0.177] | **−0.133 [−0.236, −0.027]** |
| | | empty persona, T 0.7 | +0.874 [0.826, 0.920] | **+0.656 [0.555, 0.758]** |
| targeting_fairness (1–9 fairness, women-targeted − broad) | **−1.284** [−1.756, −0.806] | demographics, T 0 | −0.863 [−0.997, −0.728] | +0.420 [−0.080, 0.913] |
| | | demographics, T 0.7 | −0.854 [−0.992, −0.716] | +0.430 [−0.073, 0.917] |
| | | full persona, T 0.7 | −0.851 [−1.030, −0.679] | +0.433 [−0.064, 0.922] |
| | | empty persona, T 0.7 | −1.145 [−1.263, −1.022] | +0.139 [−0.361, 0.630] |

The sign is recovered in all 8 comparisons (bootstrap same-sign share 0.96–1.00).

Persona-conditioned twins **attenuate** the effect:
- **default_eric:** to 39–65% of the human effect;
- **targeting_fairness:** to 66–67% of the human effect.

The persona-free model **exaggerates** the default effect fourfold (+0.87 against +0.22). It nearly matches the fairness effect.

Two caveats on precision. The LLM confidence intervals are narrow because simulated answers vary little; that reflects consistency, not accuracy. And with 260–428 people, only the two bold differences are distinguishable from zero.

## B. Matched calibration

| Study | Specification | Bias | SD ratio, LLM/human | Individual r | Fit vs a constant baseline | Distribution distance (TV) |
|---|---|---|---|---|---|---|
| default_eric | full persona | −0.03 | 0.99 | **0.38** [0.29, 0.46] | Brier 0.311 vs 0.249 (worse) | 0.03 |
| default_eric | demographics / empty | +0.04 to +0.07 | 1.00 | 0.16–0.19 | Brier 0.41–0.42 vs 0.249 (worse) | 0.04–0.07 |
| targeting_fairness | full persona | −0.02 | **0.41** [0.35, 0.47] | 0.23 [0.11, 0.34] | MAE 1.62 vs 1.69 | **0.51** |
| targeting_fairness | demographics / empty | +0.10 to +0.44 | **0.34–0.36** | 0.17–0.21 | MAE 1.60–1.61 vs 1.69 | **0.57–0.58** |

**Reading the binary outcome (default_eric).**
- The SD ratio is uninformative here, because a binary SD is fixed by the mean.
- The aggregate choice share is close (TV ≤ 0.07).
- Individual hard 0/1 answers score worse on Brier than predicting everyone at the base rate, because the twins give confident answers that are often wrong.

**Reading the rating outcome (targeting_fairness).**
- Simulated ratings keep only about 35–41% of the human spread.
- The response distribution has the wrong shape (TV ≈ 0.55).
- The mean error is barely better than a constant.

**Cell-level results are not interpretable.** There are 18 cells for default_eric and only 7 for targeting_fairness, and cell means are dominated by sampling noise. They are reported in `report.md` but not interpreted.

## C. Information value (repeated 5-fold CV within training only; Brier or squared error; positive = lower loss)

| Contrast | default_eric, loss reduction [95% CI] (share of baseline) | targeting_fairness |
|---|---|---|
| + Tier A demographics, over condition only | −0.015 [−0.027, −0.002] (−6%): **hurts** | −0.61 [−0.98, −0.26] (−14%): **hurts** |
| + 6 attitude scores, over condition only | **+0.033 [0.016, 0.049] (+13%)** | +0.05 [−0.17, 0.27] (+1%), ns |
| attitudes added to Tier A | +0.028 [0.011, 0.044] (+11%) | +0.00 [−0.25, 0.26], ns |
| published full-persona LLM answer added to Tier A | **+0.029 [0.014, 0.045] (+12%)** | −0.03 [−0.13, 0.06], ns |
| attitudes alone vs LLM answer alone | +0.002 [−0.012, 0.016], ns (equivalent) | +0.06 [−0.18, 0.30], ns |

**default_eric:**
- Six measured attitude scores add real out-of-sample information.
- So does a single published full-persona twin answer, by about the same amount. This is expected, because the full-persona prompt contains the participant's survey answers, including those attitudes.
- Ten census variables add none: they overfit at n = 428.

**targeting_fairness:** apart from the randomised condition, nothing is predictable from these inputs.

## Failed tasks and limitations
- **Failed tasks:** none.
- **Scope:**
  - **Two studies only.** The other 17 lack a between-subjects condition, need outcome-mapping work that hasn't been verified, or have duplicate IDs.
  - **One model family.** All twins are GPT-4.1, from Peng et al.'s published runs; no new model was queried.
- **Data:**
  - **Training participants only.** No holdout analysis, so results are exploratory. They are not confirmatory and are not pre-registered at the level of these hypotheses.
  - **Single draws.** Each published twin answer is one draw per participant, so individual-level metrics combine model error with sampling noise.
- **Method:**
  - **Fixed regularisation.** Models in C use fixed regularisation (L2 with C = 1, ridge α = 1), not tuned. Negative skill for Tier A partly reflects 30+ one-hot levels at small n.
  - **No uncertainty in condition-only rows.** M0 has no variance across repeats.
- **Fairness outcome:** this is a one-item hypothetical judgement. Its human effect has a wide confidence interval (−1.76 to −0.81).

## Three most important findings
1. **Twins recover the direction of randomised effects, not their size, and the error depends on the prompt.** Persona-conditioned GPT-4.1 shrinks both effects to about 40–67% of the human value. Without a persona it inflates the default effect fourfold. Effect sizes from LLM twins are therefore not usable as forecasts of nudge magnitude without human calibration.
2. **Simulated respondents compress human heterogeneity.** On the fairness scale, twins keep about 35–41% of the human spread and produce the wrong response distribution. Individual-level agreement is weak (r 0.16–0.38). Twin samples will understate variance and the size of the tails.
3. **Measured dispositions carry the predictive signal; census demographics do not.** In default_eric, attitudes (or a twin built from them) improve out-of-sample prediction by about 12–13% of baseline, while Tier A demographics worsen it. In targeting_fairness neither helps.

**Data-quality note.** The Mega-Study `targeting_fairness` file labels its conditions backwards relative to the displayed text. Analyses that use the `target` label will reverse the sign of the effect.

## Recommendation for the Brace discussion

Do not change the frozen submission. If there is a discussion or Q&A, two points are worth raising, both labelled exploratory and training-only:
- **Finding 3** independently supports the submission's central claim that outer-layer (census) personas carry little behavioural signal, while inner-layer measures do. It largely re-confirms the existing values analysis rather than adding new evidence.
- **Finding 1** is the most decision-relevant caution for a behavioural science consultancy considering LLM "synthetic respondents": they may get the direction of an intervention right while misstating its size by a factor of 0.4 to 4, depending on the prompt.

Finding 2 and the label inversion are better kept as supporting detail. Do not present any of this as a validated benchmark: two studies and one model family are too narrow.
