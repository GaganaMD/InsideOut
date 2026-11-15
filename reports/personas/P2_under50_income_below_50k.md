# Persona: P2_under50_income_below_50k

**Who (outer layer only):** age_band in {18-29, 30-49}; income in {Less than $30,000, $30,000-$50,000} · **n = 425** (291 train / 134 held out) · source: Twin-2K-500 waves 1–3 · evidence: `P2_under50_income_below_50k_evidence.md`

**Bottom line.** **Higher neuroticism** is the one dependable trait. It is the project's largest robust group difference and holds in all 6 redefinitions. The 'more spendthrift' prediction failed. The lower social desirability is fragile (it vanishes if the group is widened to 18–64), and the earlier CRT difference was a scoring artefact.

| Part | Typical [p10–p90] | d vs pop. (95% CI) | Held-out d | Held-out error cut | Confidence |
|---|---|---|---|---|---|
| Green values | 3.41 [2.0–4.5] | -0.15 (-0.26, -0.04) | -0.15 | 0% | weak |
| Social desirability | 5.66 [1–10]† | -0.21 (-0.32, -0.10)† | -0.25† | +2% | distinct before shrinkage; **weak after shrinkage** |
| Tightwad(4)-spendthrift(26) | 13.84 [8.0–21.0] | -0.08 (-0.21, +0.05) | +0.06 | -1% | same as population |
| Cognitive reflection | 2.42 [1–4]† | +0.00 (-0.11, +0.12)† | -0.14† | 0% | same as population |
| Dictator giving | 39.42 [20.0–60.0] | +0.11 (-0.01, +0.23) | +0.01 | 0% | same as population |
| Neuroticism | 3.15 [1.9–4.4] | +0.47 (+0.36, +0.58) | +0.55 | +11% | distinct |

Held-out error cut = reduction in absolute error vs the population mean on held-out members. *Distinct* = |d| ≥ 0.20 with CI excluding 0. *Typical* is a shrunken estimate (fully shrunk for dictator giving); d and its CI describe the raw mean. † Corrected item-level scores; the dataset's shipped social-desirability and CRT scores are mis-scored for 180/450 people (`reports/final_audit/statistical_audit.md`). Frozen legacy values: evidence file.

**Why this persona.** It asks whether money matters within a life stage.

**Extended profile (exploratory).** Training members only (n = 291), no held-out check; six further scales re-derived from items. Lower conscientiousness (d −0.48), extraversion (−0.47), self-concept clarity (−0.41), agreeableness (−0.26) and need for cognition (−0.22); openness unchanged (0.00). Within ages 18–49, adjusted for age band, the income gap is extraversion −0.47, conscientiousness −0.39 and self-concept clarity −0.25 (CIs exclude 0): income, not age. CIs: `research_frontier/persona_extension/`.

**Why it fits.** *Observed:* within each age band, lower-income members are more neurotic (18–29: 3.36 vs 2.99; 30–49: 3.07 vs 2.69; age-adjusted +0.30 SD, CI 0.20 to 0.40). *Interpretation:* consistent with the documented link between financial strain and negative affect. *Speculation:* the direction is unknown (strain → distress, distress → lower earnings, or health driving both). Household income may misclassify students on parental income.

**Say vs do.** When choosing renewable meant switching, 27% chose it on training data (n = 33; population 36%) but 47% on held-out members (n = 19). The tempting 'budget-constrained idealist' story **failed** the holdout, so no behavioural prediction is offered.

**Where it breaks.** About a quarter of members are calmer than the median panel member. The neuroticism shift helps individual prediction by about a tenth. P2 contains 81 of P3's 197 training members. **Inside it:** the 98 members in full-time work are close to the population (neuroticism +0.20, CI −0.00 to 0.40), against +0.61 for the other 193. Found by inspection.
