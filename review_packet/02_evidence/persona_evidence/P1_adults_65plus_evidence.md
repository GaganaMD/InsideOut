# Persona: P1_adults_65plus

**Outer-layer definition:** age_band = 65+  
**n** = 277 (13.5% of the panel); built from 194 train members, 83 held out.

> **Scores:** FROZEN HISTORICAL ESTIMATES. Tables below use the LEGACY (historical reproduction): shipped social-desirability and CRT scores, which contain known scoring defects (180 and 450 people mis-scored). Do not use these values as current findings. Corrected values for those two constructs follow the inner-layer table and are the ones cited in the persona card and memo.

## Bottom line

This group is **calmer** (lower neuroticism) and **describes itself more favourably** (higher social desirability) than the panel. Both differences replicate on held-out people and survive all 5 one-criterion redefinitions. On values, money style, reflection, generosity and the hypothetical green choice, treat it as the population average. The earlier 'less reflective' (CRT) result was a scoring artefact and is withdrawn.

## Inner layer (train members; typical = shrunken mean)

| Construct | Typical | 95% CI (raw mean) | Spread p10–p90 (SD) | vs population (d, 95% CI) | % strictly on other side of pop. median (% exactly at it) | Confidence |
|---|---|---|---|---|---|---|
| Green values (1-5) | 3.62 | 3.53–3.81 | 2.2–4.8 (0.98) | +0.15 (+0.01, +0.28) | 38% (4%) | weak difference before shrinkage; **not distinguishable from population after shrinkage** |
| Social desirability (0-13) | 6.96 | 6.80–7.80 | 2.0–11.0 (3.55) | +0.42 (+0.29, +0.55) | 30% (10%) | distinct |
| Tightwad(4)-spendthrift(26) | 13.69 | 12.93–14.03 | 9.0–19.0 (3.92) | -0.13 (-0.26, -0.00) | 38% (9%) | weak difference before shrinkage; **not distinguishable from population after shrinkage** |
| Cognitive reflection (0-4) | 1.98 | 1.65–1.99 | 0.0–3.0 (1.24) | -0.18 (-0.32, -0.04) | 36% (16%) | weak difference before shrinkage; **not distinguishable from population after shrinkage** |
| Dictator giving, % of $5 (hypothetical) | 39.42 | 38.54–43.11 | 20.0–60.0 (16.27) | +0.08 (-0.05, +0.20) | 12% (70%) | not distinguishable from population |
| Neuroticism (1-5) | 2.32 | 2.16–2.41 | 1.1–3.5 (0.91) | -0.43 (-0.56, -0.30) | 31% (3%) | distinct |

Source: Twin-2K-500 wave 1–3 scores (spendthrift re-scored from items; see audit). **Typical** is an empirical-Bayes estimate pulled toward the population mean by an amount set by n and by how much Tier A groups differ on that construct (none, for dictator giving, so it equals the population mean). The **95% CI** is for the raw member mean, a different estimand. **d** is relative to the train population SD. **Confidence**: *distinct* = |d| ≥ 0.20 and CI excludes 0; *weak* = CI excludes 0 but |d| < 0.20 (pre-registered, on the raw mean). The same rule is then re-applied to the shrunken estimate (d of Typical; posterior CI = Typical ± 1.96·√w·SE, w = shrink weight); if it gives a weaker label, both are shown and only the shrinkage-adjusted label should be narrated. **Other side of median** counts members strictly beyond the population median on the opposite side; members exactly at the median (common on discrete scales) are shown separately.

**Measurement correction (final audit).** The shipped social-desirability and CRT scores are mis-scored for 180 and 450 people (case- and format-sensitive string matching; see `reports/final_audit/statistical_audit.md`). The table above keeps the frozen original values. With corrected scores (same definition, train-built):

- social_desirability: d +0.42 → **+0.39** (+0.26, +0.52), distinct; holdout d +0.47, MAE gain +9.3% (reduction CI +0.068 to +0.501 scale units)
- crt: d -0.18 → **-0.06** (-0.21, +0.08), not distinguishable from population; holdout d -0.07, MAE gain -0.1% (reduction CI -0.004 to +0.002 scale units)

## Behaviour: hypothetical $39 renewable vs $32 supplier (Mega-Study `default_eric`)

| Default condition | n | Chose renewable | 95% CI | Population |
|---|---|---|---|---|
| grey_default | 49 | 43% | 0.30–0.57 | 36% (n=206) |
| green_default | 40 | 55% | 0.40–0.69 | 58% (n=222) |

**Say vs do** — members at or above the population's 67th-percentile green-values score (with ties, more than a third of people) who still declined the renewable option:

- grey_default: 43% (0.26–0.63), n=23 (population 47%)
- green_default: INSUFFICIENT EVIDENCE (n=17 < 20), n=17 (population 21%)

*These are hypothetical survey choices, not purchases.*

## Held-out check (frozen test split, evaluated once)

| Construct | n test | MAE persona | MAE population mean | Gain, % of population MAE | MAE reduction in scale units (95% CI) | 80% interval coverage: persona / population |
|---|---|---|---|---|---|---|
| green | 83 | 0.83 | 0.86 | +3.2% | +0.027 (+0.006, +0.046) | 81% / 78% |
| social_desirability | 83 | 3.05 | 3.45 | +11.6% | +0.398 (+0.137, +0.640) | 82% / 88% |
| spendthrift | 83 | 3.23 | 3.29 | +1.9% | +0.062 (-0.017, +0.138) | 86% / 88% |
| crt | 83 | 1.20 | 1.22 | +1.0% | +0.012 (-0.000, +0.023) | 88% / 100% |
| dictator_give | 83 | 11.66 | 11.66 | +0.0% | +0.000 (+0.000, +0.000) | 84% / 84% |
| neuroticism | 83 | 0.75 | 0.86 | +13.2% | +0.114 (+0.041, +0.190) | 83% / 78% |

*The CI is a participant bootstrap of the mean reduction in absolute error, in the construct's own units (not in percent).*

Green choice on held-out members (Brier score; lower is better; persona rate used only if n ≥ 20 on train):

| Condition | n test | Test rate | Persona train rate | Brier persona / population |
|---|---|---|---|---|
| green_default | 18 | 67% | 55% | 0.236 / 0.230 |
| grey_default | 25 | 40% | 43% | 0.241 / 0.242 |
