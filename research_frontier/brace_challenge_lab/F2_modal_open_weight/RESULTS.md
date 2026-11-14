# Open-weight LLM persona benchmark: results (pre-registered; training participants only)

These are **open-weight Qwen models, not GPT-4.1.** They are never pooled with, or substituted for, the published GPT-4.1 twin results.

The design, metrics and decision rules were fixed in `PREREGISTRATION.md` and committed before inference (commit `16d76d1`).

## Run record

| | Qwen2.5-7B-Instruct | Qwen3-4B-Instruct-2507 |
|---|---|---|
| Revision (pinned) | `a09a35458c70…` | `cdbee75f17c0…` |
| Licence | Apache-2.0 | Apache-2.0 |
| GPU | NVIDIA A10 | NVIDIA A10 |
| Prompts | 1,524, all valid (A+B probability mass ≥ 0.99997) | 1,524, all valid (≥ 0.99997) |
| Determinism (32 prompts re-scored in reverse order) | identical (max difference 0.0) | identical (0.0) |
| **Position bias**: mean \|P(green) with green as A − with green as B\| | **0.51** | 0.12 |
| Scoring time | 182 s | about 3 min |

**Total Modal cost for this experiment:** $0.43. That covers both models, the smoke tests, the weight downloads, and one aborted run that sat waiting on a stalled download. The ceiling was $5. The cost comes from the Modal billing report.

**Deviation from the pre-registration (disclosed).** The first smoke test **failed** the determinism check, with a maximum difference of 0.217. The cause was left-padded batching without explicit position IDs, which made a prompt's score depend on its batch-mates. Following the stopping rule, the full run was not launched. Scoring was changed to unpadded (batch = 1), the smoke test was rerun and passed, and only then was the full run launched. The fix is in commit `3653518`.

## Results

427 training participants in 76 cells, cross-fitted. All CIs are 95% paired cluster bootstrap over cells, with 2,000 resamples.

| Method | Brier (lower is better) | Δ vs B, demographic model [95% CI] | Calibration slope | Predicted default effect (human +0.215) | SD of cell predictions |
|---|---|---|---|---|---|
| A. Population average (condition rate) | 0.241 | — | 0.79 | — | 0.110 |
| B. Demographic logistic model | 0.241 | — | 0.63 | — | 0.142 |
| Qwen2.5-7B, no persona | 0.241 | −0.000 [−0.016, +0.017] | 0.65 | +0.32 | 0.161 |
| Qwen2.5-7B, demographics | 0.359 | **+0.118 [+0.063, +0.174]** | 0.05 | +0.35 | 0.357 |
| Qwen2.5-7B, + numeric profile | 0.290 | **+0.049 [+0.017, +0.088]** | 0.04 | **+0.04** (error CI −0.33 to −0.03) | 0.215 |
| Qwen2.5-7B, + narrative profile | 0.326 | **+0.085 [+0.043, +0.132]** | 0.02 | **+0.01** (error CI −0.35 to −0.06) | 0.269 |
| Qwen3-4B, no persona | 0.468 | **+0.227 [+0.160, +0.294]** | 0.23 | +0.01 | 0.002 |
| Qwen3-4B, demographics | 0.399 | **+0.158 [+0.098, +0.224]** | 0.07 | +0.25 | 0.277 |
| Qwen3-4B, + numeric profile | 0.393 | **+0.152 [+0.093, +0.213]** | 0.03 | +0.05 (error CI −0.32 to −0.01) | 0.204 |
| Qwen3-4B, + narrative profile | 0.416 | **+0.175 [+0.121, +0.234]** | 0.03 | +0.12 | 0.426 |

### Central contrasts

| Contrast | Qwen2.5-7B [95% CI] | Qwen3-4B [95% CI] |
|---|---|---|
| Profile − demographics (Brier) | **−0.069 [−0.122, −0.012]**: profile helps | −0.006 [−0.038, +0.026]: no difference |
| Narrative − profile (Brier) | +0.035 [−0.006, +0.081]: not significant | +0.024 [−0.031, +0.079]: not significant |
| Narrative − profile (confidence, mean \|p − 0.5\|) | **+0.059 [+0.022, +0.093]**: more confident | **+0.090 [+0.040, +0.144]**: more confident |
| Correlation of predictions with the profile's green z-score | profile 0.62, narrative 0.76 | profile 0.47, narrative 0.76 |

## Pre-registered decisions
- **The LLM adds value beyond the demographic model: NO, for both models and all formats.**
  - Only Qwen2.5 with no persona ties the baselines (0.241). That is because, averaged over answer orders, it reproduces roughly the population rate.
  - Every persona format is significantly *worse* than both the population average and the demographic model.
- **The profile helps:**
  - **Yes for Qwen2.5**, relative to its own demographics-only prompt. But it is still worse than a free statistical baseline.
  - **No for Qwen3.**
- **Framing matters:** **yes, for confidence.** The narrative version makes predictions significantly more extreme in both models, with no accuracy gain. It is also more stereotyped: predictions track the green-values z-score more closely (r 0.76 vs 0.47–0.62).
- **Default-effect recovery:**
  - Adding an inner-layer profile, whether numeric or narrative, **erases** the randomised default effect. The model predicts +0.01 to +0.12 against a human +0.215; for Qwen2.5 both error CIs exclude 0. The model lets the persona dominate the situation.
  - Demographic-only prompts land near or above the human effect, but with calibration slopes of about 0.05, so they carry almost no information at the individual or cell level.
- **Individual-level fidelity:** not claimed. All predictions are at the cell level.

## Interpretation for Brace (cautious)
1. **Persona prompts made these open-weight models worse than doing nothing.** Group-level forecasts from a population average, or a 4-variable logistic model, were at least as good, and calibrated.
2. **Narrative personas add confidence and stereotyping, not accuracy.** This is the most product-relevant result: persuasive persona prose increases false certainty.
3. **Situation vs disposition.** Given psychological attributes, the models under-weight the randomised default, while humans respond to it by about 22 points. This mirrors the human-data finding that the situation (default) and one measured value both matter.
4. **Position bias is large.** It averages 0.51 for Qwen2.5. Any single-order LLM survey of this model would be dominated by option order. Counterbalancing is mandatory.

## Limits
- One scenario (default_eric) and two small open-weight models.
- 76 cells with a median of 5 people, so per-cell human rates are noisy. Both baselines share this noise, so relative comparisons are fair.
- Profiles are ridge estimates from 4 cell fields, not the submission's empirical-Bayes personas.
- Next-token probabilities are only one elicitation method; verbal or sampled answers could behave differently.
- These results say nothing about GPT-4.1 or other frontier models.

The full numbers are in `results.json`; the per-prompt outputs are in `outputs/full__*.json`.
