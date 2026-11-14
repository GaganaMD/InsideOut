# EXPLORATORY robustness: persona stability under one-criterion changes

> Exploratory, **training split only** (built with the same generator as the personas). The original personas, their estimates and the holdout are untouched. Nothing here is used to re-tune them.

## Variants and sample sizes

| Persona | Variant | Criteria | n train | Green-choice n (grey / green default) | Status |
|---|---|---|---|---|---|
| P1 | ORIGINAL | `age_band=65+` | 194 | 49 / 40 | ok |
| P1 | shift age: 50-64 | `age_band=50-64` | 461 | 60 / 88 | ok |
| P1 | widen age: 50+ | `age_band=50-64|65+` | 655 | 109 / 128 | ok |
| P1 | add: retired only | `age_band=65+; employment=Retired` | 98 | 27 / 24 | ok |
| P1 | add: income < $50k | `age_band=65+; income=Less than $30,000|$30,000-$50,000` | 94 | 25 / 21 | ok |
| P1 | add: college degree | `age_band=65+; education=College graduate/some postgrad|Postgraduate` | 107 | 28 / 19 ⚠ behaviour < 20/cell | ok |
| P2 | ORIGINAL | `age_band=18-29|30-49; income=Less than $30,000|$30,000-$50,000` | 291 | 33 / 36 | ok |
| P2 | narrow age: 18-29 | `age_band=18-29; income=Less than $30,000|$30,000-$50,000` | 108 | 6 / 4 ⚠ behaviour < 20/cell | ok |
| P2 | narrow age: 30-49 | `age_band=30-49; income=Less than $30,000|$30,000-$50,000` | 183 | 27 / 32 | ok |
| P2 | widen age: 18-64 | `age_band=18-29|30-49|50-64; income=Less than $30,000|$30,000-$50,000` | 444 | 57 / 70 | ok |
| P2 | narrow income: < $30k | `age_band=18-29|30-49; income=Less than $30,000` | 123 | 13 / 18 ⚠ behaviour < 20/cell | ok |
| P2 | widen income: < $75k | `age_band=18-29|30-49; income=Less than $30,000|$30,000-$50,000|$50,000-$75,000` | 448 | 56 / 52 | ok |
| P2 | drop income criterion | `age_band=18-29|30-49` | 787 | 97 / 94 | ok |
| P3 | ORIGINAL | `age_band=18-29; marital=Never been married` | 197 | 17 / 16 ⚠ behaviour < 20/cell | ok |
| P3 | drop marital criterion | `age_band=18-29` | 272 | 29 / 19 ⚠ behaviour < 20/cell | ok |
| P3 | shift age: 30-49 | `age_band=30-49; marital=Never been married` | 190 | 23 / 37 | ok |
| P3 | drop age criterion | `marital=Never been married` | 503 | 57 / 75 | ok |
| P3 | widen marital: + living with partner | `age_band=18-29; marital=Never been married|Living with a partner` | 244 | 24 / 17 ⚠ behaviour < 20/cell | ok |
| P3 | add: male | `age_band=18-29; marital=Never been married; sex=Male` | 111 | 11 / 11 ⚠ behaviour < 20/cell | ok |
| P3 | add: female | `age_band=18-29; marital=Never been married; sex=Female` | 86 | 6 / 5 ⚠ behaviour < 20/cell | ok |

## Stability of each construct conclusion

| Persona | Construct | Original (d, class) | d range across variants | Sign kept | CI excludes 0 | Stable? |
|---|---|---|---|---|---|---|
| P1 | crt | -0.18, weak difference | -0.15 to -0.09 | 5/5 | 1/5 | **yes** |
| P1 | dictator_give | +0.08, not distinguishable from population | -0.04 to +0.18 | 2/5 | 0/5 | **yes** |
| P1 | green | +0.15, weak difference | +0.01 to +0.23 | 5/5 | 3/5 | no |
| P1 | neuroticism | -0.43, distinct | -0.50 to -0.20 | 5/5 | 5/5 | **yes** |
| P1 | social_desirability | +0.42, distinct | +0.12 to +0.51 | 5/5 | 5/5 | **yes** |
| P1 | spendthrift | -0.13, weak difference | -0.17 to -0.05 | 5/5 | 1/5 | **yes** |
| P2 | crt | +0.13, weak difference | +0.01 to +0.21 | 6/6 | 2/6 | no |
| P2 | dictator_give | +0.11, not distinguishable from population | +0.01 to +0.25 | 6/6 | 1/6 | no |
| P2 | green | -0.15, weak difference | -0.28 to -0.07 | 6/6 | 4/6 | no |
| P2 | neuroticism | +0.47, distinct | +0.22 to +0.66 | 6/6 | 6/6 | **yes** |
| P2 | social_desirability | -0.22, distinct | -0.29 to -0.08 | 6/6 | 5/6 | no |
| P2 | spendthrift | -0.08, not distinguishable from population | -0.18 to +0.06 | 4/6 | 1/6 | **yes** |
| P3 | crt | -0.01, not distinguishable from population | -0.19 to +0.23 | 1/6 | 2/6 | no |
| P3 | dictator_give | +0.08, not distinguishable from population | -0.07 to +0.09 | 5/6 | 0/6 | **yes** |
| P3 | green | -0.27, distinct | -0.40 to -0.09 | 6/6 | 3/6 | no |
| P3 | neuroticism | +0.43, distinct | +0.21 to +0.67 | 6/6 | 6/6 | **yes** |
| P3 | social_desirability | -0.19, weak difference | -0.29 to -0.11 | 6/6 | 5/6 | no |
| P3 | spendthrift | +0.09, not distinguishable from population | -0.07 to +0.22 | 3/6 | 1/6 | no |

*Stable* means: for an originally *distinct* construct, the sign is kept and the CI excludes 0 in every variant. For other constructs, no variant turns them into a distinct difference.

## CLI with newly specified criteria

| Case | Criteria | Exit (expected) | Result | Pass |
|---|---|---|---|---|
| new_group_west_women_college | `region=West (WA, OR, ID, MT, WY, CA, NV, UT, CO, AZ, NM); sex=Female; education=College graduate/some postgrad|Postgraduate`  | 0 (0) | ok | ✓ |
| new_group_single_hh_retired | `hh_size=1; employment=Retired`  | 0 (0) | ok | ✓ |
| new_group_tiny | `age_band=18-29; employment=Retired`  | 0 (0) | INSUFFICIENT EVIDENCE: n_train=0 < 30 | ✓ |
| rejected_party | `party=Democrat`  | 2 (2) | ERROR: 'party' is not an allowed outer-layer variable (party needs --allow-party; it is se | ✓ |
| rejected_ideology | `ideology=Liberal`  | 2 (2) | ERROR: 'ideology' is not an allowed outer-layer variable. Allowed: ['region', 'sex', 'age_ | ✓ |
| rejected_bad_level | `age_band=40-60`  | 2 (2) | ERROR: age_band: unknown level(s) ['40-60']. Valid: ['18-29', '30-49', '50-64', '65+'] | ✓ |
| sensitivity_party | `party=Democrat` --allow-party | 0 (0) | ok | ✓ |
