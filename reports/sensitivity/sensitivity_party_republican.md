# Persona: sensitivity_party_republican

> **SENSITIVITY PERSONA — uses self-reported party (Tier B), not census-observable**

**Outer-layer definition:** party = Republican  
**n** = 540 (26.2% of the panel); built from 387 train members, 153 held out.

*Scores: shipped scores (frozen original); add --corrected-scores for audited SD/CRT.*

## Inner layer (train members; typical = shrunken mean)

| Construct | Typical | 95% CI (raw mean) | Spread p10–p90 (SD) | vs population (d, 95% CI) | % on other side of pop. median | Confidence |
|---|---|---|---|---|---|---|
| Green values (1-5) | 3.32 | 3.13–3.36 | 1.6–4.7 (1.12) | -0.28 (-0.39, -0.17) | 39% | distinct |
| Social desirability (0-13) | 6.13 | 5.82–6.57 | 0.0–11.0 (3.80) | +0.12 (+0.02, +0.23) | 42% | weak difference |
| Tightwad(4)-spendthrift(26) | 14.26 | 13.93–14.75 | 9.0–20.0 (4.12) | +0.07 (-0.03, +0.16) | 42% | not distinguishable from population |
| Cognitive reflection (0-4) | 1.99 | 1.80–2.05 | 0.0–4.0 (1.23) | -0.10 (-0.20, +0.00) | 36% | not distinguishable from population |
| Dictator giving, % of $5 (hypothetical) | 39.42 | 34.49–38.38 | 0.0–60.0 (19.49) | -0.16 (-0.27, -0.06) | 15% | weak difference |
| Neuroticism (1-5) | 2.52 | 2.42–2.60 | 1.4–3.9 (0.91) | -0.21 (-0.30, -0.11) | 41% | distinct |

Source: Twin-2K-500 wave 1–3 scores (spendthrift re-scored from items; see audit). **Typical** is an empirical-Bayes estimate pulled toward the population mean by an amount set by n and by how much Tier A groups differ on that construct (none, for dictator giving, so it equals the population mean). The **95% CI** is for the raw member mean, a different estimand. **d** is relative to the train population SD. **Confidence**: *distinct* = |d| ≥ 0.20 and CI excludes 0; *weak* = CI excludes 0 but |d| < 0.20.

## Behaviour: hypothetical $39 renewable vs $32 supplier (Mega-Study `default_eric`)

| Default condition | n | Chose renewable | 95% CI | Population |
|---|---|---|---|---|
| grey_default | 58 | 26% | 0.16–0.38 | 36% (n=206) |
| green_default | 65 | 49% | 0.37–0.61 | 58% (n=222) |

**Say vs do** — members in the population's top third on green values who still declined the renewable option:

- grey_default: 56% (0.33–0.77), n=16 (population 47%)
- green_default: 36% (0.20–0.57), n=22 (population 21%)

*These are hypothetical survey choices, not purchases.*
