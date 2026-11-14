# Run full-20261114

Tasks 18: done 18, resumed 0, failed 0; wall 93 s.


## A. Treatment-effect recovery (training participants; published GPT-4.1 answers)

| Study | Spec | Human ATE [95% CI] | LLM ATE [95% CI] | LLM - human [95% CI] | Same sign (boot share) |
|---|---|---|---|---|---|
| default_eric | demographics_t0 | +0.217 [0.124, 0.307] | +0.142 [0.049, 0.237] | -0.075 [-0.193, 0.045] | True (1.00) |
| default_eric | demographics_t07 | +0.217 [0.124, 0.307] | +0.111 [0.017, 0.205] | -0.107 [-0.229, 0.016] | True (0.99) |
| default_eric | empty_t07 | +0.217 [0.124, 0.307] | +0.874 [0.826, 0.920] | +0.656 [0.555, 0.758] | True (1.00) |
| default_eric | full_persona_t07 | +0.217 [0.124, 0.307] | +0.084 [-0.010, 0.177] | -0.133 [-0.236, -0.027] | True (0.96) |
| targeting_fairness | demographics_t0 | -1.284 [-1.756, -0.806] | -0.863 [-0.997, -0.728] | +0.420 [-0.080, 0.913] | True (1.00) |
| targeting_fairness | demographics_t07 | -1.284 [-1.756, -0.806] | -0.854 [-0.992, -0.716] | +0.430 [-0.073, 0.917] | True (1.00) |
| targeting_fairness | empty_t07 | -1.284 [-1.756, -0.806] | -1.145 [-1.263, -1.022] | +0.139 [-0.361, 0.630] | True (1.00) |
| targeting_fairness | full_persona_t07 | -1.284 [-1.756, -0.806] | -0.851 [-1.030, -0.679] | +0.433 [-0.064, 0.922] | True (1.00) |

## B. Matched calibration

| Study | Spec | Bias | SD ratio LLM/human [CI] | Individual r [CI] | Fit vs constant baseline | TV distance | Cell-mean r (cells) |
|---|---|---|---|---|---|---|---|
| default_eric | demographics_t0 | +0.068 | 1.00 [0.99, 1.01] | +0.188 [0.09, 0.28] | Brier 0.409 vs 0.249 | 0.07 | +0.392 (18) |
| default_eric | demographics_t07 | +0.051 | 1.00 [0.99, 1.01] | +0.162 [0.07, 0.26] | Brier 0.421 vs 0.249 | 0.05 | +0.254 (18) |
| default_eric | empty_t07 | +0.044 | 1.00 [1.00, 1.01] | +0.184 [0.09, 0.28] | Brier 0.409 vs 0.249 | 0.04 | +0.225 (18) |
| default_eric | full_persona_t07 | -0.030 | 0.99 [0.98, 1.00] | +0.375 [0.29, 0.46] | Brier 0.311 vs 0.249 | 0.03 | +0.385 (18) |
| targeting_fairness | demographics_t0 | +0.442 | 0.34 [0.30, 0.39] | +0.187 [0.07, 0.30] | MAE 1.60 vs 1.69 | 0.57 | -0.673 (7) |
| targeting_fairness | demographics_t07 | +0.415 | 0.35 [0.31, 0.39] | +0.169 [0.05, 0.29] | MAE 1.61 vs 1.69 | 0.57 | -0.491 (7) |
| targeting_fairness | empty_t07 | +0.096 | 0.36 [0.33, 0.40] | +0.209 [0.09, 0.33] | MAE 1.61 vs 1.69 | 0.58 | +0.196 (7) |
| targeting_fairness | full_persona_t07 | -0.023 | 0.41 [0.35, 0.47] | +0.228 [0.11, 0.34] | MAE 1.62 vs 1.69 | 0.51 | -0.045 (7) |

## C. Information value (repeated 5-fold CV within training; loss reduction, positive = first model better)

**default_eric** (brier, constant baseline 0.2492, 100 repeats)

| Model | Mean loss | Skill vs constant |
|---|---|---|
| M0_condition | 0.2375 | +0.047 |
| M1_tierA | 0.2519 | -0.011 |
| M2_attitudes | 0.2044 | +0.180 |
| M3_tierA_attitudes | 0.2242 | +0.100 |
| M4_tierA_llm | 0.2227 | +0.106 |
| M5_llm_only | 0.2069 | +0.170 |

| Contrast | Loss reduction [95% CI] | Share of baseline |
|---|---|---|
| M1_tierA_vs_M0_condition | -0.0145 [-0.0274, -0.0017] | -0.058 |
| M2_attitudes_vs_M0_condition | +0.0330 [0.0163, 0.0490] | +0.132 |
| M3_tierA_attitudes_vs_M1_tierA | +0.0277 [0.0111, 0.0439] | +0.111 |
| M3_tierA_attitudes_vs_M2_attitudes | -0.0198 [-0.0303, -0.0096] | -0.079 |
| M4_tierA_llm_vs_M1_tierA | +0.0292 [0.0137, 0.0446] | +0.117 |
| M2_attitudes_vs_M5_llm_only | +0.0024 [-0.0119, 0.0159] | +0.010 |

**targeting_fairness** (squared_error, constant baseline 4.3411, 100 repeats)

| Model | Mean loss | Skill vs constant |
|---|---|---|
| M0_condition | 3.9515 | +0.090 |
| M1_tierA | 4.5632 | -0.051 |
| M2_attitudes | 3.9034 | +0.101 |
| M3_tierA_attitudes | 4.5609 | -0.051 |
| M4_tierA_llm | 4.5916 | -0.058 |
| M5_llm_only | 3.9615 | +0.087 |

| Contrast | Loss reduction [95% CI] | Share of baseline |
|---|---|---|
| M1_tierA_vs_M0_condition | -0.6117 [-0.9781, -0.2622] | -0.141 |
| M2_attitudes_vs_M0_condition | +0.0481 [-0.1698, 0.2654] | +0.011 |
| M3_tierA_attitudes_vs_M1_tierA | +0.0023 [-0.2495, 0.2575] | +0.001 |
| M3_tierA_attitudes_vs_M2_attitudes | -0.6575 [-1.0144, -0.3259] | -0.151 |
| M4_tierA_llm_vs_M1_tierA | -0.0285 [-0.1282, 0.0602] | -0.007 |
| M2_attitudes_vs_M5_llm_only | +0.0581 [-0.1846, 0.2982] | +0.013 |
