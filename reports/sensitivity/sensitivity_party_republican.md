# Persona: sensitivity_party_republican

> **SENSITIVITY PERSONA — uses self-reported party (Tier B), not census-observable**

**Outer-layer definition:** party = Republican  
**n** = 540 (26.2% of the panel); built from 387 train members, 153 held out.

> **Scores:** LEGACY (historical reproduction): shipped social-desirability and CRT scores, which contain known scoring defects (180 and 450 people mis-scored). Do not use these values as current findings.

## Inner layer (train members; typical = shrunken mean)

| Construct | Typical | 95% CI (raw mean) | Spread p10–p90 (SD) | vs population (d, 95% CI) | % strictly on other side of pop. median (% exactly at it) | Confidence |
|---|---|---|---|---|---|---|
| Green values (1-5) | 3.32 | 3.13–3.36 | 1.6–4.7 (1.12) | -0.28 (-0.39, -0.17) | 39% (6%) | distinct |
| Social desirability (0-13) | 6.13 | 5.82–6.57 | 0.0–11.0 (3.80) | +0.12 (+0.02, +0.23) | 42% (8%) | weak difference |
| Tightwad(4)-spendthrift(26) | 14.26 | 13.93–14.75 | 9.0–20.0 (4.12) | +0.07 (-0.03, +0.16) | 42% (10%) | not distinguishable from population |
| Cognitive reflection (0-4) | 1.99 | 1.80–2.05 | 0.0–4.0 (1.23) | -0.10 (-0.20, +0.00) | 36% (20%) | not distinguishable from population |
| Dictator giving, % of $5 (hypothetical) | 39.42 | 34.49–38.38 | 0.0–60.0 (19.49) | -0.16 (-0.27, -0.06) | 15% (62%) | weak difference before shrinkage; **not distinguishable from population after shrinkage** |
| Neuroticism (1-5) | 2.52 | 2.42–2.60 | 1.4–3.9 (0.91) | -0.21 (-0.30, -0.11) | 41% (4%) | distinct before shrinkage; **weak difference after shrinkage** |

Source: Twin-2K-500 wave 1–3 scores (spendthrift re-scored from items; see audit). **Typical** is an empirical-Bayes estimate pulled toward the population mean by an amount set by n and by how much Tier A groups differ on that construct (none, for dictator giving, so it equals the population mean). The **95% CI** is for the raw member mean, a different estimand. **d** is relative to the train population SD. **Confidence**: *distinct* = |d| ≥ 0.20 and CI excludes 0; *weak* = CI excludes 0 but |d| < 0.20 (pre-registered, on the raw mean). The same rule is then re-applied to the shrunken estimate (d of Typical; posterior CI = Typical ± 1.96·√w·SE, w = shrink weight); if it gives a weaker label, both are shown and only the shrinkage-adjusted label should be narrated. **Other side of median** counts members strictly beyond the population median on the opposite side; members exactly at the median (common on discrete scales) are shown separately.

## Behaviour: hypothetical $39 renewable vs $32 supplier (Mega-Study `default_eric`)

| Default condition | n | Chose renewable | 95% CI | Population |
|---|---|---|---|---|
| grey_default | 58 | 26% | 0.16–0.38 | 36% (n=206) |
| green_default | 65 | 49% | 0.37–0.61 | 58% (n=222) |

**Say vs do** — members at or above the population's 67th-percentile green-values score (with ties, more than a third of people) who still declined the renewable option:

- grey_default: INSUFFICIENT EVIDENCE (n=16 < 20), n=16 (population 47%)
- green_default: 36% (0.20–0.57), n=22 (population 21%)

*These are hypothetical survey choices, not purchases.*
