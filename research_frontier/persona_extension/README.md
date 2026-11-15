# Persona extension (exploratory; not part of the submission pipeline)

`run_all.py` does not call this, and no frozen estimate depends on it. It was added on 2026-11-15, after the holdout had been inspected, because the brief weights the "why" behind each persona most. **Training split only. Not pre-registered. No held-out check has been run** (see `HOLDOUT_PROTOCOL.md`).

Regenerate from the repository root:

```bash
python research_frontier/persona_extension/persona_extension.py
```

Outputs: `extended_profile.csv` (persona × construct: n, mean, p10–p90, d, 95% CI, split-half d) and `results.json` (everything else below).

## 1. Six further scales, re-derived from items

| Scale | Items | Exact match with shipped score | Cronbach's α |
|---|---|---|---|
| Conscientiousness (BFI-44) | 9 | 100% | 0.87 |
| Agreeableness (BFI-44) | 9 | 100% | 0.82 |
| Extraversion (BFI-44) | 8 | 100% | 0.88 |
| Openness (BFI-44) | 10 | 100% | 0.84 |
| Need for cognition | 18 | 100% | 0.94 |
| Self-concept clarity | 12 | 100% | 0.92 |

Only these six are used. Other shipped scores (depression, anxiety, vocabulary and the rest) were not re-derived and are not cited in the submission.

## 2. What each persona isolates

| Persona | Question | Result (SD units, 95% CI) |
|---|---|---|
| P1, age 65+ | What does age alone reveal? | Self-concept clarity +0.43, agreeableness +0.34, conscientiousness +0.30, extraversion +0.23 against the population. Against ages 50–64 only agreeableness (+0.22; 0.06 to 0.38) and self-concept clarity (+0.19; 0.04 to 0.34) are higher. Openness and need for cognition do not differ. |
| P2, under 50 and under $50k | Does money matter within a life stage? | Within ages 18–49, adjusted for age band (n = 291 vs 496): extraversion −0.47 (−0.61 to −0.33), conscientiousness −0.39 (−0.54 to −0.25), neuroticism +0.38 (0.24 to 0.52), self-concept clarity −0.25 (−0.39 to −0.10). |
| P3, 18–29 never married | Does the most distinctive group found by search differ from other young adults? | Within 18–29, adjusted for sex, income and education (n = 197 vs 75): green values −0.48 (−0.75 to −0.20) and conscientiousness −0.33 (−0.61 to −0.05). Neuroticism −0.01 and self-concept clarity +0.12 do not differ. |

**Reading.** P1 and P3 are the two ends of one age gradient. P2 adds a second dimension, income within a life stage. P3 adds one fragile lead on green values. These are two dimensions, not three archetypes.

## 3. Within-persona counterexamples

Found by inspecting several subgroup splits, so they are leads and their p-values are uncorrected.

| Persona | Subgroup | Result |
|---|---|---|
| P1 | Income under $30,000 (n = 40) | Neuroticism d −0.09 (−0.40 to 0.22) against −0.52 for other 65+; difference +0.43 (0.11 to 0.75). Self-concept clarity is as high as in other 65+ (+0.41). |
| P2 | Full-time employed (n = 98) | Neuroticism +0.20 (−0.00 to 0.40) and conscientiousness −0.22, against +0.61 and −0.61 for the other 193. |
| P3 | Full-time employed (n = 58) | Conscientiousness −0.07 (−0.29 to 0.14), against −1.31 for the 50 unemployed. |

**Measurement caveat.** Several BFI conscientiousness items ask about work ("does a thorough job", "is a reliable worker"). Part of the employment gap in conscientiousness may be the scale rather than the trait.

## 4. Two loose clusters

Nine scales; correlations before and after removing all ten Tier A variables.

| | Raw | Tier A removed |
|---|---|---|
| Mean \|r\| within neuroticism, conscientiousness, self-concept clarity, social desirability | 0.47 | 0.43 |
| Mean \|r\| within green values, openness, need for cognition | 0.42 | 0.41 |
| Mean \|r\| between the two sets | 0.14 | 0.12 |
| r between the two composites | 0.25 | 0.21 |

- Tier A CV R² (same model as the frozen map): adjustment composite 0.17; openness and need-for-cognition composite 0.04.
- Green choice (train, n = 428), with the default in the model: adjustment composite OR 1.01 per SD (0.79 to 1.30). The openness and need-for-cognition composite has OR 1.32 (1.07 to 1.64), which falls to 1.02 (0.80 to 1.30) once green values are added.
- A descriptive two-factor solution gives the same picture (first two eigenvalues 3.33 and 1.65), but green values load only moderately on the second factor (0.39).

**Limits.** This is a description of correlations. No confirmatory factor model was fitted, the clusters are not independent (r about 0.2), all measures are self-report from one panel, and nothing here is causal. The interval for the adjustment composite excludes odds ratios below about 0.8 or above about 1.3, not smaller effects.

## 5. Who declines among high green-values scorers

High scorers are those at or above 4.0 on green values (176 training participants in the green experiment).

- Decline rate: 41 of 87 (47%; 37–58%) when renewable required switching; 19 of 89 (21%; 14–31%) when it was the default. Difference 26 points (12 to 39).
- Low income, age 50+, sex and college education each change the decline rate by 3 to 9 points, with intervals of about ±15 points that include zero.
- Tightwad, middle and spendthrift thirds decline at 32%, 39% and 31%.
- Eleven demographic and trait terms together add nothing detectable (likelihood-ratio χ² = 6.3, df 11, p = 0.85).

**Limits.** With two equal groups of 88, only a difference of about 21 points in decline rate would be detected with 80% power. Smaller real differences cannot be excluded. The choice is hypothetical.

## Sources

Bibliographic details were checked by web search; abstracts or secondary summaries were read, not full texts.

- Roberts, B. W., Walton, K. E., & Viechtbauer, W. (2006). Patterns of mean-level change in personality traits across the life course: A meta-analysis of longitudinal studies. *Psychological Bulletin*, 132(1), 1–25. Supports: conscientiousness, emotional stability and agreeableness rise across adulthood.
- Lodi-Smith, J., & Roberts, B. W. (2010). Getting to know me: Social role experiences and age differences in self-concept clarity during adulthood. *Journal of Personality*, 78(5), 1383–1410. Supports: self-concept clarity is higher in mid-life than in young adulthood. Does not support: it reports a decline in later life, which this panel does not show.
- Soutter, A. R. B., Bates, T. C., & Mõttus, R. (2020). Big Five and HEXACO personality traits, proenvironmental attitudes, and behaviors: A meta-analysis. *Perspectives on Psychological Science*, 15(4). Supports: openness is among the strongest personality correlates of pro-environmental attitudes (r = .22 across 38 sources, N = 44,993). Page numbers were not checked.
- Pichert, D., & Katsikopoulos, K. V. (2008). Green defaults: Information presentation and pro-environmental behaviour. *Journal of Environmental Psychology*, 28(1), 63–73. Context only: green-electricity default experiments of the kind used here. Whether the Mega-Study scenario was adapted from this paper was not verified, so the submission does not cite it.
