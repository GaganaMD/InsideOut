# EXPLORATORY robustness: demographic model complexity

> Exploratory, training split only. Same participants and folds as the follow-ups; all preprocessing fitted inside each fold. The verdict rule was fixed in advance: the negative finding is overturned only if a demographic model improves Brier over the baseline by at least 0.010 with a CI excluding 0.

## Green energy: hypothetical $39 renewable choice (n = 428)

| Model | Brier | Log loss | AUC | Calibration-in-the-large | Calibration slope | ECE |
|---|---|---|---|---|---|---|
| D0: Population baseline | 0.2492 | 0.6916 | – | +0.000 | – | 0.000 |
| D1: Compact: age + income + education (C=1) | 0.2611 | 0.7159 | 0.435 | -0.005 | -0.94 | 0.096 |
| D2: Full Tier A (C=1) | 0.2603 | 0.7186 | 0.551 | -0.000 | 0.25 | 0.092 |
| D3: Full Tier A, strong L2 (C=0.05) | 0.2470 | 0.6873 | 0.567 | -0.001 | 0.67 | 0.047 |
| D4: Full Tier A, C tuned by inner CV | 0.2467 | 0.6866 | 0.576 | -0.001 | 1.68 | 0.046 |

| Contrast | ΔBrier vs baseline (95% CI) | Verdict |
|---|---|---|
| D1 vs D0 | +0.0119 (+0.0057, +0.0183) | worse |
| D2 vs D0 | +0.0111 (-0.0038, +0.0262) | no detectable difference |
| D3 vs D0 | -0.0022 (-0.0096, +0.0049) | no detectable difference |
| D4 vs D0 | -0.0025 (-0.0056, +0.0007) | no detectable difference |

## Redistribution attitude, binary (n = 833)

| Model | Brier | Log loss | AUC | Calibration-in-the-large | Calibration slope | ECE |
|---|---|---|---|---|---|---|
| D0: Population baseline | 0.2494 | 0.6919 | – | -0.000 | – | 0.000 |
| D1: Compact: age + income + education (C=1) | 0.2494 | 0.6923 | 0.554 | -0.000 | 0.49 | 0.037 |
| D2: Full Tier A (C=1) | 0.2536 | 0.7030 | 0.563 | -0.001 | 0.36 | 0.076 |
| D3: Full Tier A, strong L2 (C=0.05) | 0.2461 | 0.6855 | 0.574 | -0.001 | 0.68 | 0.028 |
| D4: Full Tier A, C tuned by inner CV | 0.2452 | 0.6835 | 0.578 | -0.000 | 1.05 | 0.026 |

| Contrast | ΔBrier vs baseline (95% CI) | Verdict |
|---|---|---|
| D1 vs D0 | +0.0000 (-0.0064, +0.0062) | no detectable difference |
| D2 vs D0 | +0.0042 (-0.0050, +0.0139) | no detectable difference |
| D3 vs D0 | -0.0033 (-0.0096, +0.0027) | no detectable difference |
| D4 vs D0 | -0.0042 (-0.0084, -0.0002) | detectable but small improvement over baseline |

**Negative demographic finding overturned by any variant: NO.**
