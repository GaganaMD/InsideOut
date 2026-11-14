# Persona: P1_adults_65plus

**Who (outer layer only):** age_band = 65+ · **n = 277** (194 train / 83 held out) · scores: Twin-2K-500 waves 1–3 · full tables: `P1_adults_65plus_evidence.md`

## Bottom line

A 65+ group is **calmer** (lower neuroticism) and **presents itself more favourably** (higher social desirability) than the panel. Both differences replicate on held-out people and survive redefining the group. On values, money style, reflection, generosity and the hypothetical green choice, treat this group as the population average.

## Inner layer

| Part | Typical [p10–p90] | d vs population (95% CI) | Held-out d | Confidence |
|---|---|---|---|---|
| Green values (1-5) | 3.62 [2.2–4.8] | +0.15 (+0.01, +0.28) | +0.14 | weak difference |
| Social desirability (0-13) | 7.34 [3–11]† | +0.39 (+0.26, +0.52)† | +0.47† | distinct |
| Tightwad(4)-spendthrift(26) | 13.69 [9.0–19.0] | -0.13 (-0.26, -0.00) | -0.24 | weak difference |
| Cognitive reflection (0-4) | 2.40 [1–4]† | -0.06 (-0.21, +0.08)† | -0.07† | not distinguishable from population |
| Dictator giving, % of $5 (hypothetical) | 39.42 [20.0–60.0] | +0.08 (-0.05, +0.20) | -0.06 | not distinguishable from population |
| Neuroticism (1-5) | 2.32 [1.1–3.5] | -0.43 (-0.56, -0.30) | -0.58 | distinct |

† Social desirability and CRT use the audited item-level re-scores (the shipped scores are mis-scored for 180 and 450 people; see `reports/final_audit/statistical_audit.md`). Frozen original values are in the evidence file. *Distinct* = |d| ≥ 0.20 and CI excludes 0.

## Claim ledger

| Claim | Held-out MAE gain vs population mean | Stable in 5 redefinitions | Status |
|---|---|---|---|
| Lower neuroticism | +13.2% (CI > 0) | 5/5 | **Robust** |
| Higher social desirability (corrected) | +9.3% (CI > 0) | 5/5 | **Robust** |
| Slightly higher green values | +3.2% | 3/5 | Weak |
| Lower cognitive reflection | — | — | **Withdrawn** (CRT scoring artefact; corrected d −0.06) |

## Why it fits

**Observed.** Both traits move steadily across age bands: neuroticism 3.14 → 2.82 → 2.51 → 2.28; corrected social desirability 5.75 → 5.65 → 6.74 → 7.61. **Interpretation.** This matches published cross-sectional age differences in emotional stability and in socially desirable responding. **Speculation.** Ageing, cohort and self-presentation can't be separated here. Social desirability correlates −0.44 with neuroticism, and adjusting for it shrinks the neuroticism gap from −0.50 to −0.31 SD (CI −0.45 to −0.17): part of the calm is self-description, most is not.

## Say vs do

In the hypothetical $39 renewable offer, 43% chose renewable when it required switching (n = 49; population 36%) and 55% when it was the default (n = 40; 58%). These are not distinguishable from the population, and on held-out members they predict no better than the population rate.

## Where it breaks

This describes the group, not its members: a random 65+ member is more neurotic than a random 18–29-year-old 25% of the time. The panel's 65+ adults are online-survey completers, and they are over-represented in the experiments (21% vs 10%).
