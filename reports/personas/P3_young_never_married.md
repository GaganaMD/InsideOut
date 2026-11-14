# Persona: P3_young_never_married

**Who (outer layer only):** age_band = 18-29; marital = Never been married · **n = 285** (197 train / 88 held out) · scores: Twin-2K-500 waves 1–3 · full tables: `P3_young_never_married_evidence.md`

## Bottom line

P3 was chosen by a pre-registered search rule. Its robust trait, **higher neuroticism**, is the same age gradient P2 shows. Its eye-catching trait, **lower green values**, replicated as a group shift but is **fragile and concentrated in young never-married men**, and helps almost no individual prediction. Treat that trait as a hypothesis. Behaviour cannot be assessed.

## Inner layer

| Part | Typical [p10–p90] | d vs population (95% CI) | Held-out d | Confidence |
|---|---|---|---|---|
| Green values (1-5) | 3.35 [1.9–4.5] | -0.27 (-0.42, -0.13) | -0.40 | distinct |
| Social desirability (0-13) | 5.83 [1–10]† | -0.16 (-0.29, -0.03)† | -0.30† | weak difference |
| Tightwad(4)-spendthrift(26) | 14.27 [9.0–21.0] | +0.09 (-0.06, +0.23) | +0.10 | not distinguishable from population |
| Cognitive reflection (0-4) | 2.40 [1–4]† | -0.07 (-0.21, +0.08)† | +0.04† | not distinguishable from population |
| Dictator giving, % of $5 (hypothetical) | 39.42 [0.0–60.0] | +0.08 (-0.08, +0.24) | -0.17 | not distinguishable from population |
| Neuroticism (1-5) | 3.10 [2.0–4.2] | +0.43 (+0.31, +0.56) | +0.55 | distinct |

† Social desirability and CRT use the audited item-level re-scores (the shipped scores are mis-scored for 180 and 450 people; see `reports/final_audit/statistical_audit.md`). Frozen original values are in the evidence file. *Distinct* = |d| ≥ 0.20 and CI excludes 0.

## Claim ledger

| Claim | Held-out MAE gain vs population mean | Stable in 6 redefinitions | Status |
|---|---|---|---|
| Higher neuroticism | +14.4% (CI > 0) | 6/6 | **Robust** (shared with P2) |
| Lower green values | +0.7% (CI includes 0) | 3/6 | **Fragile**: see caveat |
| Lower social desirability (corrected) | +1.8% (CI includes 0) | 5/6 | Weak |

## Sex-composition caveat

P3 is 56% male vs 36% among other 18–29s. Never-married **men**: d −0.40 (−0.59, −0.20), n = 111. Never-married **women**: d −0.12 (−0.32, +0.09), n = 86, not distinguishable. The gap also vanishes without the marital criterion (all 18–29: d −0.11) or at ages 30–49 (d −0.09). It came from a search over about 1,000 candidate groups, so it should be confirmed on new data before use.

## Why it fits

**Observed.** Among 18–29s, the never-married score 3.25 on green values vs 3.84 for others. The gap persists after adjusting for sex, income and education as main effects (−0.45 SD). **Interpretation.** Marital status mostly marks *who* is in the group: more men, and 21% students. **Speculation (not claimed).** That partnering raises environmental concern; composition and selection explain the data equally well.

## Say vs do

**Insufficient evidence.** Only 33 members took part in the green experiment (17 and 16 per condition, below the 20-per-condition threshold).

## Where it breaks

P3 predicts individual green values no better than the population mean. Its neuroticism profile duplicates P2's, so census facts mostly reveal one age axis, not three archetypes.
