# Persona: P3_young_never_married

**Outer-layer definition:** age_band = 18-29; marital = Never been married  
**n** = 285 (13.8% of the panel); built from 197 train members, 88 held out.

> **Scores:** FROZEN HISTORICAL ESTIMATES. Tables below use the LEGACY (historical reproduction): shipped social-desirability and CRT scores, which contain known scoring defects (180 and 450 people mis-scored). Do not use these values as current findings. Corrected values for those two constructs follow the inner-layer table and are the ones cited in the persona card and memo.

## Bottom line

Its robust trait, **higher neuroticism**, is the same age gradient P2 shows. Its eye-catching trait, **lower green values**, replicated as a group shift but is **fragile** (no reliable sex difference), and it barely improves individual prediction.

## Inner layer (train members; typical = shrunken mean)

| Construct | Typical | 95% CI (raw mean) | Spread p10–p90 (SD) | vs population (d, 95% CI) | % strictly on other side of pop. median (% exactly at it) | Confidence |
|---|---|---|---|---|---|---|
| Green values (1-5) | 3.35 | 3.11–3.40 | 1.9–4.5 (1.03) | -0.27 (-0.42, -0.13) | 34% (10%) | distinct before shrinkage; **weak difference after shrinkage** |
| Social desirability (0-13) | 5.18 | 4.53–5.53 | 0.0–10.0 (3.55) | -0.19 (-0.32, -0.05) | 35% (10%) | weak difference |
| Tightwad(4)-spendthrift(26) | 14.27 | 13.80–15.06 | 9.0–21.0 (4.49) | +0.09 (-0.06, +0.23) | 46% (6%) | not distinguishable from population |
| Cognitive reflection (0-4) | 2.04 | 1.86–2.20 | 0.0–3.0 (1.25) | -0.01 (-0.15, +0.14) | 45% (18%) | not distinguishable from population |
| Dictator giving, % of $5 (hypothetical) | 39.42 | 37.98–43.85 | 0.0–60.0 (21.02) | +0.08 (-0.08, +0.24) | 19% (52%) | not distinguishable from population |
| Neuroticism (1-5) | 3.10 | 3.01–3.26 | 2.0–4.2 (0.89) | +0.43 (+0.31, +0.56) | 27% (2%) | distinct |

Source: Twin-2K-500 wave 1–3 scores (spendthrift re-scored from items; see audit). **Typical** is an empirical-Bayes estimate pulled toward the population mean by an amount set by n and by how much Tier A groups differ on that construct (none, for dictator giving, so it equals the population mean). The **95% CI** is for the raw member mean, a different estimand. **d** is relative to the train population SD. **Confidence**: *distinct* = |d| ≥ 0.20 and CI excludes 0; *weak* = CI excludes 0 but |d| < 0.20 (pre-registered, on the raw mean). The same rule is then re-applied to the shrunken estimate (d of Typical; posterior CI = Typical ± 1.96·√w·SE, w = shrink weight); if it gives a weaker label, both are shown and only the shrinkage-adjusted label should be narrated. **Other side of median** counts members strictly beyond the population median on the opposite side; members exactly at the median (common on discrete scales) are shown separately.

**Measurement correction (final audit).** The shipped social-desirability and CRT scores are mis-scored for 180 and 450 people (case- and format-sensitive string matching; see `reports/final_audit/statistical_audit.md`). The table above keeps the frozen original values. With corrected scores (same definition, train-built):

- social_desirability: d -0.19 → **-0.16** (-0.29, -0.03), weak difference; holdout d -0.30, MAE gain +1.8% (reduction CI -0.044 to +0.123 scale units)
- crt: d -0.01 → **-0.07** (-0.21, +0.08), not distinguishable from population; holdout d +0.04, MAE gain -0.4% (reduction CI -0.007 to -0.000 scale units)

## Behaviour: hypothetical $39 renewable vs $32 supplier (Mega-Study `default_eric`)

| Default condition | n | Chose renewable | 95% CI | Population |
|---|---|---|---|---|
| grey_default | 17 | INSUFFICIENT EVIDENCE (n=17 < 20) | 0.10–0.47 | 36% (n=206) |
| green_default | 16 | INSUFFICIENT EVIDENCE (n=16 < 20) | 0.44–0.86 | 58% (n=222) |

**Say vs do** — members at or above the population's 67th-percentile green-values score (with ties, more than a third of people) who still declined the renewable option:

- grey_default: INSUFFICIENT EVIDENCE (n=4 < 20), n=4 (population 47%)
- green_default: INSUFFICIENT EVIDENCE (n=6 < 20), n=6 (population 21%)

*These are hypothetical survey choices, not purchases.*

## Held-out check (frozen test split, evaluated once)

| Construct | n test | MAE persona | MAE population mean | Gain, % of population MAE | MAE reduction in scale units (95% CI) | 80% interval coverage: persona / population |
|---|---|---|---|---|---|---|
| green | 88 | 0.90 | 0.90 | +0.7% | +0.006 (-0.030, +0.044) | 73% / 77% |
| social_desirability | 88 | 2.77 | 2.81 | +1.3% | +0.037 (-0.075, +0.149) | 99% / 100% |
| spendthrift | 88 | 3.72 | 3.73 | +0.1% | +0.005 (-0.039, +0.049) | 86% / 81% |
| crt | 88 | 1.11 | 1.11 | -0.0% | -0.000 (-0.001, +0.000) | 86% / 100% |
| dictator_give | 88 | 12.14 | 12.14 | +0.0% | +0.000 (+0.000, +0.000) | 99% / 83% |
| neuroticism | 88 | 0.79 | 0.92 | +14.4% | +0.133 (+0.061, +0.203) | 72% / 74% |

*The CI is a participant bootstrap of the mean reduction in absolute error, in the construct's own units (not in percent).*

Green choice on held-out members (Brier score; lower is better; persona rate used only if n ≥ 20 on train):

| Condition | n test | Test rate | Persona train rate | Brier persona / population |
|---|---|---|---|---|
| green_default | 7 | 43% | 69% (not used) | 0.267 / 0.267 |
| grey_default | 6 | 50% | 24% (not used) | 0.270 / 0.270 |
