# Persona: P1_adults_65plus

**Outer-layer definition:** age_band = 65+  
**n** = 277 (13.5% of the panel); built from 194 train members, 83 held out.

## Inner layer (train members; typical = shrunken mean)

| Construct | Typical | 95% CI (raw mean) | Spread p10–p90 (SD) | vs population (d, 95% CI) | % on other side of pop. median | Confidence |
|---|---|---|---|---|---|---|
| Green values (1-5) | 3.62 | 3.53–3.81 | 2.2–4.8 (0.98) | +0.15 (+0.01, +0.28) | 38% | weak difference |
| Social desirability (0-13) | 6.96 | 6.80–7.80 | 2.0–11.0 (3.55) | +0.42 (+0.29, +0.55) | 30% | distinct |
| Tightwad(4)-spendthrift(26) | 13.69 | 12.93–14.03 | 9.0–19.0 (3.92) | -0.13 (-0.26, -0.00) | 38% | weak difference |
| Cognitive reflection (0-4) | 1.98 | 1.65–1.99 | 0.0–3.0 (1.24) | -0.18 (-0.32, -0.04) | 36% | weak difference |
| Dictator giving, % of $5 (hypothetical) | 39.42 | 38.54–43.11 | 20.0–60.0 (16.27) | +0.08 (-0.05, +0.20) | 12% | not distinguishable from population |
| Neuroticism (1-5) | 2.32 | 2.16–2.41 | 1.1–3.5 (0.91) | -0.43 (-0.56, -0.30) | 31% | distinct |

Source: Twin-2K-500 wave 1–3 scores (spendthrift re-scored from items; see audit).

## Behaviour: hypothetical $39 renewable vs $32 supplier (Mega-Study `default_eric`)

| Default condition | n | Chose renewable | 95% CI | Population |
|---|---|---|---|---|
| grey_default | 49 | 43% | 0.30–0.57 | 36% (n=206) |
| green_default | 40 | 55% | 0.40–0.69 | 58% (n=222) |

**Say vs do** — members in the population's top third on green values who still declined the renewable option:

- grey_default: 43% (0.26–0.63), n=23 (population 47%)
- green_default: 29% (0.13–0.53), n=17 (population 21%)

*These are hypothetical survey choices, not purchases.*

## Why it fits

The outer layer sees **life stage**, and the two constructs it separates best for adults 65+ are the two with the steepest monotonic age gradients in the whole panel. **Social desirability** is +0.42 SD; the train means by age band are 5.1, 5.0, 6.2 and 7.3. **Neuroticism** is −0.43 SD; the means are 3.14, 2.82, 2.51 and 2.28. Both match published cross-sectional patterns: emotional stability rises with age (the maturity principle; Roberts et al. 2006, Soto et al. 2011), and so does socially desirable self-presentation. Age is the strongest single Tier A predictor of neuroticism in the drop-one analysis. In contrast, what older adults *do* in the green-energy scenario is not distinguishable from the population.

## Alternative explanations

(1) **Cohort, not ageing.** The data are cross-sectional, so a 1950s-born cohort effect cannot be separated from age. (2) **Self-presentation.** Social desirability and neuroticism correlate at r = −0.39. Adjusting for social desirability shrinks the 65+ neuroticism gap from −0.50 to −0.32 SD (95% CI −0.46 to −0.18). About a third of the 'calmer' profile may therefore be how older people *describe* themselves, though the gap does not disappear. (3) **Panel selection.** Older online-panel members are probably unusual for their age group, so this describes 65+ panelists, not 65+ Americans.

## Where it breaks

About 30% of members sit on the 'wrong' side of the population median on each of the two defining traits, so the persona describes the group, not a given individual. Dictator giving, CRT, spendthrift and green values are at most weakly different from the population. The behavioural cells are small (40–49 per condition), and 65+ adults are over-represented in the Mega-Study (22% of participants vs 10% of non-participants), so experiment results lean old.

## Held-out check (frozen test split, evaluated once)

| Construct | n test | MAE persona | MAE population mean | Gain (95% CI) | 80% interval coverage: persona / population |
|---|---|---|---|---|---|
| green | 83 | 0.83 | 0.86 | +3.2% (+0.006, +0.046) | 81% / 78% |
| social_desirability | 83 | 3.05 | 3.45 | +11.6% (+0.137, +0.640) | 82% / 88% |
| spendthrift | 83 | 3.23 | 3.29 | +1.9% (-0.017, +0.138) | 86% / 88% |
| crt | 83 | 1.20 | 1.22 | +1.0% (-0.000, +0.023) | 88% / 100% |
| dictator_give | 83 | 11.66 | 11.66 | +0.0% (+0.000, +0.000) | 84% / 84% |
| neuroticism | 83 | 0.75 | 0.86 | +13.2% (+0.041, +0.190) | 83% / 78% |

Green choice on held-out members (Brier score; lower is better; persona rate used only if n ≥ 20 on train):

| Condition | n test | Test rate | Persona train rate | Brier persona / population |
|---|---|---|---|---|
| green_default | 18 | 67% | 55% | 0.236 / 0.230 |
| grey_default | 25 | 40% | 43% | 0.241 / 0.242 |
