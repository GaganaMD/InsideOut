# EXPLORATORY: Does a measured redistribution attitude beat demographics?

> **Exploratory follow-up, not part of the confirmatory analysis.** It was pre-specified in `PRESPEC.md` (committed before any model was fitted) and uses the **training split only**. The outcome is a **stated attitude**: there is no choice, cost or randomised condition, so models with an experimental condition (M3, M1 + condition) are **not applicable**. Predictor and outcome come from different surveys about 5 months apart, but they measure **adjacent constructs**.

Construct: redistributive policy support is the mean of support for Medicare for All, a public option and a 2% wealth tax (Twin `QID287_4/5/10`, 1–5). Cronbach's α on train is 0.71.

## Primary: government responsibility to help the poor (1–5, higher = more government)

n = 833 train participants ("don't know" and the attention-check failure excluded). Distribution: {1: 70, 2: 104, 3: 222, 4: 172, 5: 265}.

| Model | Features | OOF MAE | OOF R² |
|---|---|---|---|
| M0 | Training-fold mean | 1.109 | +0.000 |
| M1 | Tier A demographics | 1.078 | +0.006 |
| M2 | Tier A + redistributive policy support | 0.844 | +0.348 |
| M2_ideology | Tier A + ideology (sensitivity) | 0.791 | +0.389 |
| M2_equality | Tier A + EQUALITY value (sensitivity) | 0.925 | +0.210 |

| Contrast (A vs B) | ΔR² (95% CI) | ΔMAE (95% CI) | Verdict | ΔR² range over 5 other fold seeds |
|---|---|---|---|---|
| M1 vs M0 | +0.006 (-0.036, +0.048) | -0.031 (-0.058, -0.005) | no detectable difference | -0.011 to +0.020 |
| M2 vs M1 | +0.342 (+0.282, +0.402) | -0.233 (-0.277, -0.193) | practically meaningful improvement | +0.329 to +0.352 |
| M2_ideology vs M1 | +0.383 (+0.315, +0.448) | -0.286 (-0.335, -0.240) | practically meaningful improvement | +0.372 to +0.403 |
| M2_equality vs M1 | +0.204 (+0.150, +0.257) | -0.153 (-0.187, -0.118) | practically meaningful improvement | +0.189 to +0.198 |
| M2 vs M2_ideology | -0.041 (-0.106, +0.026) | +0.053 (+0.012, +0.094) | no detectable difference | -0.056 to -0.036 |

Effect sizes (Spearman ρ with the outcome, train): redist +0.55 (n = 833); ideology +0.64 (n = 833); equality +0.45 (n = 830)

## Secondary: willingness to pay higher taxes for health care (1–5, higher = more willing)

n = 830 train participants ("don't know" and the attention-check failure excluded). Distribution: {1: 139, 2: 116, 3: 116, 4: 314, 5: 145}.

| Model | Features | OOF MAE | OOF R² |
|---|---|---|---|
| M0 | Training-fold mean | 1.176 | +0.000 |
| M1 | Tier A demographics | 1.125 | +0.012 |
| M2 | Tier A + redistributive policy support | 0.889 | +0.312 |
| M2_ideology | Tier A + ideology (sensitivity) | 0.925 | +0.307 |
| M2_equality | Tier A + EQUALITY value (sensitivity) | 0.994 | +0.174 |

| Contrast (A vs B) | ΔR² (95% CI) | ΔMAE (95% CI) | Verdict | ΔR² range over 5 other fold seeds |
|---|---|---|---|---|
| M1 vs M0 | +0.012 (-0.036, +0.057) | -0.051 (-0.081, -0.019) | no detectable difference | -0.011 to +0.030 |
| M2 vs M1 | +0.300 (+0.242, +0.358) | -0.236 (-0.276, -0.194) | practically meaningful improvement | +0.273 to +0.305 |
| M2_ideology vs M1 | +0.295 (+0.239, +0.353) | -0.200 (-0.245, -0.158) | practically meaningful improvement | +0.270 to +0.292 |
| M2_equality vs M1 | +0.163 (+0.110, +0.214) | -0.131 (-0.163, -0.096) | practically meaningful improvement | +0.142 to +0.165 |
| M2 vs M2_ideology | +0.005 (-0.056, +0.063) | -0.035 (-0.076, +0.007) | no detectable difference | -0.000 to +0.015 |

Effect sizes (Spearman ρ with the outcome, train): redist +0.50 (n = 830); ideology +0.55 (n = 830); equality +0.38 (n = 827)

## Comparability check: binary outcome (government should help = points 1–2)

Prevalence 0.52. Logistic regression, C = 1.0, same folds.

| Model | Brier | Log loss | AUC |
|---|---|---|---|
| M0 | 0.2494 | 0.6919 | – |
| M1 | 0.2536 | 0.7030 | 0.563 |
| M2 | 0.1955 | 0.5723 | 0.764 |
| M2_ideology | 0.1754 | 0.5371 | 0.815 |
| M2_equality | 0.2129 | 0.6146 | 0.724 |

| Contrast | ΔBrier (95% CI) | ΔAUC (95% CI) |
|---|---|---|
| M1 vs M0 | +0.0042 (-0.0044, +0.0131) | – |
| M2 vs M1 | -0.0581 (-0.0716, -0.0450) | +0.201 (+0.163, +0.239) |

## Side by side with the green-energy follow-up

| | Green energy (hypothetical costed choice, randomised default) | Redistribution (stated attitude, no condition) |
|---|---|---|
| n (train) | 428 | 833 |
| Demographics vs baseline, ΔBrier | +0.0111 (-0.0043, +0.0259) | +0.0042 (-0.0044, +0.0131) |
| Measured attitude added, ΔBrier | -0.0334 (-0.0480, -0.0182) | -0.0581 (-0.0716, -0.0450) |
| Measured attitude added, ΔAUC | +0.136 | +0.201 |
| Experimental context | default adds ~0.01 Brier (borderline) | not applicable: no condition |
