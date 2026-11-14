# Persona: P2_under50_income_below_50k

**Who (outer layer only):** age_band in {18-29, 30-49}; income in {Less than $30,000, $30,000-$50,000} · **n = 425** (291 train / 134 held out) · scores: Twin-2K-500 waves 1–3 · full tables: `P2_under50_income_below_50k_evidence.md`

## Bottom line

Under-50s with household income below $50k show **higher neuroticism**, the largest robust group difference in the project. It reflects **two** visible facts: youth, and lower income *within* every age band. Do not use this persona for money style (the pre-registered 'more spendthrift' prediction failed) or for responses to a costed green offer (the apparent cost effect did not replicate).

## Inner layer

| Part | Typical [p10–p90] | d vs population (95% CI) | Held-out d | Confidence |
|---|---|---|---|---|
| Green values (1-5) | 3.41 [2.0–4.5] | -0.15 (-0.26, -0.04) | -0.15 | weak difference |
| Social desirability (0-13) | 5.66 [1–10]† | -0.21 (-0.32, -0.10)† | -0.25† | distinct |
| Tightwad(4)-spendthrift(26) | 13.84 [8.0–21.0] | -0.08 (-0.21, +0.05) | +0.06 | not distinguishable from population |
| Cognitive reflection (0-4) | 2.42 [1–4]† | +0.00 (-0.11, +0.12)† | -0.14† | not distinguishable from population |
| Dictator giving, % of $5 (hypothetical) | 39.42 [20.0–60.0] | +0.11 (-0.01, +0.23) | +0.01 | not distinguishable from population |
| Neuroticism (1-5) | 3.15 [1.9–4.4] | +0.47 (+0.36, +0.58) | +0.55 | distinct |

† Social desirability and CRT use the audited item-level re-scores (the shipped scores are mis-scored for 180 and 450 people; see `reports/final_audit/statistical_audit.md`). Frozen original values are in the evidence file. *Distinct* = |d| ≥ 0.20 and CI excludes 0.

## Claim ledger

| Claim | Held-out MAE gain vs population mean | Stable in 6 redefinitions | Status |
|---|---|---|---|
| Higher neuroticism | +11.2% (CI > 0) | 6/6 | **Robust** |
| Lower social desirability (corrected) | +2.0% (CI includes 0) | 5/6 | Fragile: gone if widened to 18–64 |
| More spendthrift (pre-registered) | ≈0 | — | **Falsified** |
| Higher cognitive reflection | — | — | **Withdrawn** (CRT scoring artefact; corrected d +0.00) |

## Why it fits

**Observed.** Within each age band, lower-income members are more neurotic (18–29: 3.36 vs 2.99; 30–49: 3.07 vs 2.69; age-adjusted +0.30 SD, CI 0.20 to 0.40). Adding sex and income to age raises neuroticism predictability from R² 0.074 to 0.117. **Interpretation.** This is consistent with the documented link between financial strain and negative affect. **Speculation.** The direction is unknown: strain could raise distress, distress could lower earnings, or health could drive both. Household income may also misclassify students living on parental income.

## Say vs do

When choosing renewable meant switching, 27% chose it on train (n = 33; population 36%), but 47% did on held-out members (n = 19). A tempting 'budget-constrained idealist' story **failed** the holdout, so no behavioural prediction is offered.

## Where it breaks

About a quarter of members are calmer than the median panel member. The neuroticism gain is a group-level shift that helps individual prediction by about a tenth.
