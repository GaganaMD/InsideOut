# Persona: P3_young_never_married

**Who (outer layer only):** age_band = 18-29; marital = Never been married · **n = 285** (197 train / 88 held out) · source: Twin-2K-500 waves 1–3 · evidence: `P3_young_never_married_evidence.md`

**Bottom line.** Its robust trait, **higher neuroticism**, is the same age gradient P2 shows. Its eye-catching trait, **lower green values**, replicated as a group shift but is **fragile** (no reliable sex difference), and it barely improves individual prediction.

| Part | Typical [p10–p90] | d vs pop. (95% CI) | Held-out d | Held-out error cut | Confidence |
|---|---|---|---|---|---|
| Green values | 3.35 [1.9–4.5] | -0.27 (-0.42, -0.13) | -0.40 | +1% | distinct before shrinkage; **weak after shrinkage** |
| Social desirability | 5.83 [1–10]† | -0.16 (-0.29, -0.03)† | -0.30† | +2% | weak |
| Tightwad(4)-spendthrift(26) | 14.27 [9.0–21.0] | +0.09 (-0.06, +0.23) | +0.10 | 0% | same as population |
| Cognitive reflection | 2.40 [1–4]† | -0.07 (-0.21, +0.08)† | +0.04† | 0% | same as population |
| Dictator giving | 39.42 [0.0–60.0] | +0.08 (-0.08, +0.24) | -0.17 | 0% | same as population |
| Neuroticism | 3.10 [2.0–4.2] | +0.43 (+0.31, +0.56) | +0.55 | +14% | distinct |

Held-out error cut = reduction in absolute error vs the population mean on held-out members. *Distinct* = |d| ≥ 0.20 with CI excluding 0. *Typical* is a shrunken estimate (fully shrunk for dictator giving); d and its CI describe the raw mean. † Corrected item-level scores; the dataset's shipped social-desirability and CRT scores are mis-scored for 180/450 people (`reports/final_audit/statistical_audit.md`). Frozen legacy values: evidence file.

**Why this persona.** It asks whether the pre-registered search for the most distinctive group (about 1,000 candidates) finds more than youth. Against other 18–29-year-olds it differs only on green values and conscientiousness (−0.33, CI −0.61 to −0.05); the rest is the young end of P1's gradient.

**Extended profile (exploratory).** Training members only (n = 197), no held-out check; six further scales re-derived from items. Lower conscientiousness (d −0.61), self-concept clarity (−0.56), agreeableness (−0.37), extraversion (−0.36) and need for cognition (−0.29), all CIs excluding 0; openness −0.13. CIs: `research_frontier/persona_extension/`.

**Why it fits.** *Observed:* never-married 18–29s score 3.25 on green values vs 3.84 for other 18–29s (−0.45 SD after adjusting for sex, income and education). *Interpretation:* marital status partly marks *who* is in the group (56% men vs 36% among other 18–29s; 21% students), but adjusting for sex does not remove the gap.

**Sex-composition caveat.** Against the whole population the green gap is d −0.40 in men (n = 111) and −0.12 in women (n = 86), but within 18–29 the sex interaction is null (+0.18, CI −0.31 to 0.66). The gap vanishes without the marital criterion (all 18–29s: −0.11), and it is significant in only 3 of 6 redefinitions.

**Say vs do.** **Insufficient evidence**: 33 members took the green experiment (17 and 16 per condition, below the 20 minimum).

**Where it breaks.** P3 predicts individual green values no better than the population mean. 41% of its training members are also in P2. **Inside it:** the 58 members in full-time work match the population on conscientiousness (−0.07, CI −0.29 to 0.14), against −1.31 for the 50 unemployed. Found by inspection.
