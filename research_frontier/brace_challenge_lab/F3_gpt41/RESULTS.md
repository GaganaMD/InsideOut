# GPT-4.1 matched persona-format experiment: full results (pre-registered; training participants only)

The design, metrics and decision rules are in `PREREGISTRATION.md` (commit `8f80948`), fixed before any paid call. The analysis is the unchanged F2 code (`F2_modal_open_weight/analyze.py`), with one disclosed robustness fix (see "Deviations").

## Run record

| | |
|---|---|
| Model | `openai/gpt-4.1` via OpenRouter, provider OpenAI. The catalogue maps it to `gpt-4.1-2025-04-14`, but responses return only the alias. **The snapshot is unverified and may differ from Peng et al.'s runs.** |
| Calls | 1,556 pre-registered (1,524 primary + 32 re-asks). 246 reused from the verified pilot cache; 1,310 new. |
| Validity | **1,574 / 1,574 valid (100%)** including the pilot-only re-asks. 0 invalid, 0 errors, 0 retries, no budget or authentication stop. |
| Time | 03:14:04 to 03:35:55 UTC |
| **Cost** | Computed from tokens: pilot $0.2104 + full run $1.0501 = $1.2605. **OpenRouter account usage: $1.2508 billed.** Cap: $5. |
| Re-ask stability (temperature 0) | 50 re-asks: mean \|Δp\| 0.015; same choice 96% |
| Choice vs p | 100% consistent |

## Main results

427 participants in 76 cells. All CIs are paired cluster bootstrap over cells, 95%, with 2,000 resamples.

| Method | Brier | Δ vs A: population [CI] | Δ vs B: demographic model [CI] | Calibration intercept / slope | Mean prediction | Cell-weighted MAE |
|---|---|---|---|---|---|---|
| A. Population (condition rate) | 0.2414 | — | — | −0.01 / 0.79 | 0.467 | 0.237 |
| B. Demographic logistic model | 0.2410 | −0.0004 [−0.014, +0.013] | — | −0.04 / 0.63 | 0.472 | 0.227 |
| GPT-4.1, no persona | 0.3271 | **+0.086 [+0.047, +0.126]** | **+0.086 [+0.047, +0.127]** | undefined (constant 0.75) | 0.750 | 0.350 |
| GPT-4.1, demographics | 0.2682 | +0.027 [−0.003, +0.060] | +0.027 [−0.004, +0.062] | +0.19 / 0.42 | 0.339 | 0.269 |
| GPT-4.1, + numeric profile | 0.2592 | +0.018 [−0.008, +0.047] | +0.018 [−0.007, +0.047] | +0.23 / 0.54 | 0.353 | 0.249 |
| GPT-4.1, + narrative profile | 0.2603 | +0.019 [−0.007, +0.047] | +0.019 [−0.006, +0.046] | +0.19 / 0.48 | 0.359 | 0.251 |

Positive Δ means the method is worse.

**Central contrasts (GPT-4.1):**

| Contrast | Estimate [95% CI] |
|---|---|
| Profile − demographics (Brier) | −0.009 [−0.024, +0.006] |
| Narrative − profile (Brier) | +0.001 [−0.006, +0.007] |
| Narrative − profile (confidence, mean \|p − 0.5\|) | +0.001 [−0.008, +0.011] |
| Correlation of predictions with the profile's green z-score | numeric 0.78; narrative 0.76 |

**Default-effect recovery** (human ATE on the same 427 people: +0.215 [0.083, 0.347]):

| GPT-4.1 format | Predicted effect | Signed error [95% CI] |
|---|---|---|
| no persona | 0.000 | [−0.347, −0.083] |
| demographics | +0.085 | [−0.269, +0.008] |
| numeric profile | +0.077 | [−0.268, −0.006] |
| narrative | +0.082 | [−0.265, +0.001] |

## Pre-registered decisions
- **"Adds value" beyond the demographic model: NOT PASSED.** No GPT-4.1 format has a lower Brier score than B. The persona formats are worse by 0.018–0.027, with CIs including 0; the no-persona format is significantly worse.
- **The profile helps (profile < demographics, CI excluding 0): not passed**, at −0.009 [−0.024, +0.006].
- **Framing matters: not passed** for GPT-4.1, on either Brier or confidence.
- **Individual-level fidelity:** not claimed.

## Artifacts and diagnostics
- **Order sensitivity is small.** Mean |P(green with green as A) − with green as B| is 0.039 (signed +0.021).
- **Probability reporting is coarse and bounded.** GPT-4.1 used only 34 distinct p values, all within 0.15–0.85, clustered on mirror pairs such as 0.62/0.38, 0.68/0.32 and 0.72/0.28. It never used 0.5. Stated probabilities are not likelihoods.
- **Systematic under-prediction.** The mean predicted P(green) for persona formats is 0.34–0.36, against an observed 0.47. That is a positive calibration intercept, +0.19 to +0.23.
- **Slopes of 0.42–0.54 mean the predictions are too spread out** relative to the outcome, i.e. overconfident in their between-cell differences.
- **The no-persona format ignores the default.** It answers 0.75 in both conditions.
- **Stereotyping.** With a profile, predictions track the profile's green-values z-score closely (r ≈ 0.77). The model leans on the disposition cue and under-weights the default.

## Comparison with the open-weight runs (not a controlled model comparison)

**Brier by format:**

| Model | Probability method | No persona | Demographics | Numeric profile | Narrative | Δ vs B, best format |
|---|---|---|---|---|---|---|
| Qwen2.5-7B | next-token P("A")/P("B") | 0.241 | 0.359 | 0.290 | 0.326 | ≈ 0 (no persona only) |
| Qwen3-4B | next-token | 0.468 | 0.399 | 0.393 | 0.416 | +0.152 (profile) |
| GPT-4.1 | stated JSON p | 0.327 | 0.268 | 0.259 | 0.260 | +0.018 (profile, ns) |

The baselines score A 0.241 and B 0.241.

**Predicted default effect** (human +0.215):

| Model | No persona | Demographics | Numeric profile | Narrative |
|---|---|---|---|---|
| Qwen2.5-7B | +0.32 | +0.35 | +0.04 | +0.01 |
| Qwen3-4B | +0.01 | +0.25 | +0.05 | +0.12 |
| GPT-4.1 | 0.00 | +0.09 | +0.08 | +0.08 |

**Narrative vs numeric confidence:**

| Model | Narrative − numeric confidence |
|---|---|
| Qwen2.5-7B | +0.06 (significant) |
| Qwen3-4B | +0.09 (significant) |
| GPT-4.1 | +0.00 (ns) |

**Order sensitivity:**

| Model | Mean \|order gap\| |
|---|---|
| Qwen2.5-7B | 0.51 |
| Qwen3-4B | 0.12 |
| GPT-4.1 | 0.04 |

**What is identical across the three models:**
- the cells and cross-fitted profiles;
- the scenario text. This is an abridged paraphrase of the survey item, not its exact wording: the survey shows a longer welcome letter and "Stay with X / Switch to Y" options. The caveat applies to all three models and to the comparison with human choices;
- the person, profile and narrative text blocks;
- both answer orders;
- the participants, baselines and analysis code.

**What differs:**
1. **Probability extraction.** Qwen uses next-token token probabilities; GPT-4.1 states a probability in JSON.
2. **The final instruction.** "Answer with a single letter: A or B." for Qwen, versus the harness's JSON instruction for GPT-4.1.
3. **The system prompt.** The harness adds "Respond with JSON only."
4. **Sampling.** Deterministic logits for Qwen; temperature 0 sampling for GPT-4.1.

Differences between models therefore mix model capability with elicitation method.

## Deviations (disclosed)
- **`analyze.py` crashed on the no-persona GPT-4.1 arm.** That arm's predictions are constant (0.75), and `statsmodels` silently drops the intercept column for a constant regressor.
  - The fix: calibration now returns "undefined" for constant predictions.
  - Re-running with all three models reproduced every committed Qwen and baseline number exactly (checked to 1e-12).
  - No metric, rule, prompt or baseline was changed.
- **The verdict line in `full_report.json`** reuses the pilot's wording ("propose full run"). The criteria values are what matter.

## Files
| File | Contents |
|---|---|
| `results_all_models.json` | All three models, full analysis |
| `analysis_stdout.txt` | Analysis console output |
| `full_report.json` | Validity, cost and artifacts |
| `outputs/full__gpt41.json` | Converted primary predictions |
| `outputs/gpt41_responses_cache.jsonl` | Every raw response, with usage, cost and served model (no secrets) |
