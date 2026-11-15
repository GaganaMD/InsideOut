# Persona: P3_young_never_married

**Who (outer layer only):** age_band = 18-29; marital = Never been married · **n = 285** (197 train / 88 held out) · source: Twin-2K-500 waves 1–3 · evidence: `P3_young_never_married_evidence.md`

**Bottom line.** P3 was chosen by a pre-registered search rule. Its robust trait, **higher neuroticism** (stable in all 6 redefinitions), is the same age gradient P2 shows. Its eye-catching trait, **lower green values**, replicated as a group shift but is **fragile** (no reliable sex difference), and it barely improves individual prediction. Treat it as a hypothesis. Behaviour cannot be assessed.

| Part | Typical [p10–p90] | d vs pop. (95% CI) | Held-out d | Held-out error cut | Confidence |
|---|---|---|---|---|---|
| Green values | 3.35 [1.9–4.5] | -0.27 (-0.42, -0.13) | -0.40 | +1% | distinct before shrinkage; **weak after shrinkage** |
| Social desirability | 5.83 [1–10]† | -0.16 (-0.29, -0.03)† | -0.30† | +2% | weak |
| Tightwad(4)-spendthrift(26) | 14.27 [9.0–21.0] | +0.09 (-0.06, +0.23) | +0.10 | 0% | same as population |
| Cognitive reflection | 2.40 [1–4]† | -0.07 (-0.21, +0.08)† | +0.04† | 0% | same as population |
| Dictator giving | 39.42 [0.0–60.0] | +0.08 (-0.08, +0.24) | -0.17 | 0% | same as population |
| Neuroticism | 3.10 [2.0–4.2] | +0.43 (+0.31, +0.56) | +0.55 | +14% | distinct |

Held-out error cut = reduction in absolute error vs the population mean on held-out members. *Distinct* = |d| ≥ 0.20 with CI excluding 0. † Corrected item-level scores; the dataset's shipped social-desirability and CRT scores are mis-scored for 180/450 people (`reports/final_audit/statistical_audit.md`, values in `reports/final_audit/corrected_scores/personas_sd_crt.csv`). Frozen legacy values: evidence file.

**Why it fits.** *Observed:* never-married 18–29s score 3.25 on green values vs 3.84 for other 18–29s (−0.45 SD after adjusting for sex, income and education). *Interpretation:* marital status partly marks *who* is in the group (56% men vs 36% among other 18–29s; 21% students), but adjusting for sex does not remove the gap. *Speculation (not claimed):* that partnering raises environmental concern.

**Sex-composition caveat.** Against the whole population, men d −0.40 (−0.59, −0.20), n = 111; women d −0.12 (−0.32, +0.09), n = 86. But within 18–29 (never-married vs partnered) the gap is −0.41 in men and −0.59 in women; the sex interaction is null (+0.18, CI −0.31 to 0.66). The gap vanishes without the marital criterion (all 18–29s: −0.11) or at ages 30–49 (−0.09), and it appears significant in only 3 of 6 redefinitions. It was found in a search over about 1,000 groups.

**Say vs do.** **Insufficient evidence**: 33 members took the green experiment (17 and 16 per condition, below the 20 minimum).

**Where it breaks.** P3 predicts individual green values no better than the population mean. Census facts here mostly reveal one age axis, not three archetypes.
