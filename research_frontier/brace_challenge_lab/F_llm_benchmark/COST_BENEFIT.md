# Cost-benefit of LLM personas vs statistical baselines (EXPLORATORY; training participants only)

Prices: `overnight/pricing_snapshot.json` (OpenRouter public list, 2026-11-14; GPT-4.1 $2 / $8 per M tokens,
GPT-4.1-mini $0.40 / $1.60). Token counts for the published specifications are **estimates**
(`cost_estimates.py`, `results/cost_rerun_estimates.csv`): the exact prompts are not public, so persona size is
proxied from local Twin-2K-500 question text + answer labels, and the survey part has a lower proxy (one scenario +
question, 1,200 characters) and an upper proxy (all question text in the study's QSF). 4 characters per token, 50
output tokens per call.

## 1. What each prediction costs

| Prediction source | Our cost here | Re-run cost per 1,000 people (GPT-4.1, estimate) | What else it needs |
|---|---|---|---|
| A population average / condition-only | $0 | $0 | an existing human sample in that condition |
| B census statistical model | $0 (CPU seconds) | $0 | human outcomes for this intervention to fit on |
| C published demographics-only twin | $0 (published) | about $2 (single-item lower proxy) to $41 (whole-survey upper proxy) | nothing beyond demographics |
| E published full-persona twin | $0 (published) | about $49 to $87 (median persona ~95k characters, ~24k tokens) | **a ~500-item survey of each person** |
| Prepared C/D/D-narr experiment | not run | pilot <= $0.35, full <= $3.68 upper bound (2,328 calls, cell-level) | owner authorisation, working key |

Cell-level prompting (one call per demographic cell x condition x sample, mapped to people) is what makes the
prepared experiment cheap: about 2,300 calls cover 594 people across two studies, instead of one long call per person.

## 2. What it buys (useful prediction = beats the condition-only baseline A1 with a CI excluding 0)

| | default_eric Brier gain vs A1 [95% CI] | targeting_fairness squared-error gain vs A1 | Useful? |
|---|---|---|---|
| B4_tuned / B10_tuned | +0.002 [-0.005, +0.008] / -0.000 [-0.008, +0.007] | -0.03 / -0.10 (CIs include 0) | No |
| C hard (T 0) | -0.171 [-0.217, -0.125] | -0.54 [-0.92, -0.15] | No (harmful) |
| C recalibrated | -0.004 [-0.017, +0.009] | -0.27 [-0.53, -0.00] | No |
| E hard | -0.073 [-0.120, -0.029] | -0.30 [-0.66, +0.09] | No |
| E recalibrated | **+0.022 [+0.004, +0.042]** (~9% of A1 Brier) | -0.21 [-0.49, +0.10] | default_eric only |

**Cost per useful prediction.**
- C (demographic persona): no useful predictions at any price in these data; the cost per useful prediction is
  undefined (infinite). Published files cost us $0, and they still did not help.
- E (full persona): useful on one of two outcomes, and only after recalibration with human outcomes. Inference is
  roughly $0.05-0.09 per person, but the real cost is the ~500-item survey per person. The same gain is available
  from a 6-item green-values scale plus the condition (accuracy 0.680 vs E 0.689; Modal run: attitudes vs LLM
  answer +0.002 [-0.012, +0.016] Brier), with no LLM.
- B (census model): $0, but no gain either; its value is as the honest baseline an LLM must beat.

## 3. Where an LLM could still pay off (untested here)
1. **A new intervention with no human data.** Statistical models cannot predict an effect they have never seen.
   The only evidence available (two studies, one model family) says LLM effect sizes are wrong by a factor of 0.4
   (persona prompts) to 4 (no persona), while the sign was right in 8 of 8 comparisons. Value: direction screening,
   not magnitude.
2. **Pre-testing wording or ranking many variants** before a human study, if the ranking is validated on a few
   studies with known human results first.
Both require the calibration evidence listed in `CLIENT_RECOMMENDATIONS.md` before client use.

## 4. Bottom line
For predicting attitudes or choices of demographic groups, the cheapest adequate method in these data is the
condition (or population) average; LLM demographic personas cost little but add no accuracy and worsen group-level
and small-group errors. Measured attitudes carry the signal, whether fed to a regression or to an LLM.
