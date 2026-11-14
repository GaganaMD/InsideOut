# Persona: P2_under50_income_below_50k

**Outer-layer definition:** age_band in {18-29, 30-49}; income in {Less than $30,000, $30,000-$50,000}  
**n** = 425 (20.7% of the panel); built from 291 train members, 134 held out.

## Bottom line

Under-50s with household income below $50k show **higher neuroticism**, the largest robust group difference in the project. It reflects **two** visible facts: youth, and lower income *within* every age band. Do not use this persona for money style (the pre-registered 'more spendthrift' prediction failed) or for responses to a costed green offer (the apparent cost effect did not replicate).

## Inner layer (train members; typical = shrunken mean)

| Construct | Typical | 95% CI (raw mean) | Spread p10–p90 (SD) | vs population (d, 95% CI) | % on other side of pop. median | Confidence |
|---|---|---|---|---|---|---|
| Green values (1-5) | 3.41 | 3.26–3.49 | 2.0–4.5 (0.96) | -0.15 (-0.26, -0.04) | 39% | weak difference |
| Social desirability (0-13) | 5.05 | 4.50–5.33 | 0.0–10.0 (3.63) | -0.22 (-0.33, -0.10) | 34% | distinct |
| Tightwad(4)-spendthrift(26) | 13.84 | 13.14–14.27 | 8.0–21.0 (4.88) | -0.08 (-0.21, +0.05) | 42% | not distinguishable from population |
| Cognitive reflection (0-4) | 2.10 | 2.07–2.34 | 1.0–4.0 (1.16) | +0.13 (+0.02, +0.24) | 31% | weak difference |
| Dictator giving, % of $5 (hypothetical) | 39.42 | 39.16–43.59 | 20.0–60.0 (19.25) | +0.11 (-0.01, +0.23) | 14% | not distinguishable from population |
| Neuroticism (1-5) | 3.15 | 3.07–3.28 | 1.9–4.4 (0.92) | +0.47 (+0.36, +0.58) | 25% | distinct |

Source: Twin-2K-500 wave 1–3 scores (spendthrift re-scored from items; see audit). **Typical** is an empirical-Bayes estimate pulled toward the population mean by an amount set by n and by how much Tier A groups differ on that construct (none, for dictator giving, so it equals the population mean). The **95% CI** is for the raw member mean, a different estimand. **d** is relative to the train population SD. **Confidence**: *distinct* = |d| ≥ 0.20 and CI excludes 0; *weak* = CI excludes 0 but |d| < 0.20.

**Measurement correction (final audit).** The shipped social-desirability and CRT scores are mis-scored for 180 and 450 people (case- and format-sensitive string matching; see `reports/final_audit/statistical_audit.md`). The table above keeps the frozen original values. With corrected scores (same definition, train-built):

- social_desirability: d -0.22 → **-0.21** (-0.32, -0.10), distinct; holdout d -0.25, MAE gain +2.0%
- crt: d +0.13 → **+0.00** (-0.11, +0.12), not distinguishable from population; holdout d -0.14, MAE gain +0.0%

## Behaviour: hypothetical $39 renewable vs $32 supplier (Mega-Study `default_eric`)

| Default condition | n | Chose renewable | 95% CI | Population |
|---|---|---|---|---|
| grey_default | 33 | 27% | 0.15–0.44 | 36% (n=206) |
| green_default | 36 | 58% | 0.42–0.73 | 58% (n=222) |

**Say vs do** — members in the population's top third on green values who still declined the renewable option:

- grey_default: 64% (0.35–0.85), n=11 (population 47%)
- green_default: INSUFFICIENT EVIDENCE (n<10), n=7 (population 21%)

*These are hypothetical survey choices, not purchases.*

## Held-out check (frozen test split, evaluated once)

| Construct | n test | MAE persona | MAE population mean | Gain (95% CI) | 80% interval coverage: persona / population |
|---|---|---|---|---|---|
| green | 134 | 0.81 | 0.81 | -0.1% (-0.019, +0.018) | 81% / 84% |
| social_desirability | 134 | 2.98 | 3.04 | +2.0% (-0.051, +0.162) | 93% / 96% |
| spendthrift | 134 | 4.07 | 4.04 | -0.8% (-0.068, -0.001) | 84% / 77% |
| crt | 134 | 1.04 | 1.03 | -0.7% (-0.017, +0.003) | 83% / 100% |
| dictator_give | 134 | 13.62 | 13.62 | +0.0% (+0.000, +0.000) | 83% / 83% |
| neuroticism | 134 | 0.88 | 1.00 | +11.2% (+0.044, +0.184) | 76% / 69% |

Green choice on held-out members (Brier score; lower is better; persona rate used only if n ≥ 20 on train):

| Condition | n test | Test rate | Persona train rate | Brier persona / population |
|---|---|---|---|---|
| green_default | 10 | 80% | 58% | 0.207 / 0.210 |
| grey_default | 19 | 47% | 27% | 0.290 / 0.262 |
