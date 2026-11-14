# Competing explanations for each persona pattern

**How to read this file.**
- **Our data** means training-split checks from `mechanisms.py` (`results.csv`), in z units, with 95% CIs.
- **External evidence** is published work. A work is cited only if we located it and checked its existence and DOI or URL during this session.
- Where we read only an abstract or summary, it is marked "(abstract-level)". Claims we could not verify are marked **"unverified — not cited"**.
- **Verdict** says whether our data discriminates between the explanations or not.

---

## P1 (65+)

### P1-1. Lower neuroticism (held-out d −0.58)
| Explanation | Our data | External evidence | What would weaken or falsify it |
|---|---|---|---|
| **A. Maturation:** people become emotionally more stable as they age | Consistent. The decline is linear across all 4 bands (−0.30 per band; departure from linearity p = 0.70). It survives Tier A adjustment (−0.41, CI −0.57 to −0.26). | The meta-analysis of 92 longitudinal samples finds emotional stability rising across adulthood, mostly ages 20–40 (Roberts, Walton & Viechtbauer 2006, *Psych Bull* 132:1–25, https://pubmed.ncbi.nlm.nih.gov/16435954/; abstract-level). The BLSA longitudinal HLM finds neuroticism declining up to about age 80 (Terracciano et al. 2005, *Psychology and Aging* 20:493–506, doi:10.1037/0882-7974.20.3.493; abstract-level). | Within-person panel data showing flat neuroticism over 10–20 years in this population. A gap that appears only between cohorts and not within people. |
| **B. Cohort:** older generations were always less neurotic, or answer such items differently | Indistinguishable from A in one cross-section. Age and cohort are perfectly collinear here. | Roberts et al. (2006) report that studies of younger cohorts show *more* change, which is a cohort moderation (abstract-level). | Longitudinal change inside cohorts as large as the cross-sectional gap would weaken a pure-cohort account. |
| **C. Survivorship and panel selection:** emotionally stable, healthy and educated older people are the ones who survive, go online and join panels | Cannot be tested directly. The panel's 65+ are 85% White vs 65% of under-65s, and 55% have a BA vs 50%. The gap is *no smaller* among the less educated: no BA −0.56 vs BA+ −0.43. That is weak evidence against selection operating through education. | Web-survey samples differ systematically from target populations, and propensity weighting is a proposed fix (Schonlau et al. 2009; https://www.stat.cmu.edu/~brian/303-2012-full/303-2011/303-2010/exam2/schonlau-et-al-2009-smr-propensity-scores-for-online-surveys.pdf; abstract-level). Specific claims that online older adults are healthier: unverified — not cited. | The gap persisting at similar size in a probability sample (e.g. HRS-type data with comparable BFI items) or after ACS/health reweighting. |
| **D. Response style, acquiescence:** young people agree with everything, so forward-keyed N is inflated | The gap is −0.55 on forward-keyed items and −0.32 on reverse-keyed items. All 8 items are negative. Acquiescence would move the two halves in opposite directions, so it explains at most about 0.1 SD. **Data discriminates: a minor contributor at most.** | Age–acquiescence findings are mixed across studies: unverified — not cited. | Reverse-keyed items showing *no* age gap would make acquiescence the dominant account. |
| **E. Response style, socially desirable responding:** older people under-report negative affect | Adjusting for SD shrinks the gap from −0.41 to −0.25 (CI −0.39 to −0.11). With employment and SD adjusted together it is −0.18 (−0.33 to −0.02). | SD scales correlate with real, spouse-rated personality, so partialling SD out may remove substance (McCrae & Costa 1983, *J Consult Clin Psychol* 51:882–888, doi:10.1037/0022-006X.51.6.882; abstract-level). Higher socially desirable responding with age is "widely acknowledged" in a geriatric study (https://pmc.ncbi.nlm.nih.gov/articles/PMC8442330/; abstract-level). | Informant-rated or behavioural neuroticism showing the same age gap would falsify a "pure self-presentation" account. **Our data cannot tell style from substance.** |
| **F. Life circumstances (retirement, mediator):** fewer work stressors | Employment adjustment moves −0.41 to −0.32. But within 65+, retired vs not is only −0.12 (−0.38, +0.15), and within 50–64 it is −0.09. | — | No retired/working difference within band (as observed) weakens F as a main driver. Collinearity with age means m2 is unreliable. |

**Verdict.**
- Our data rules out acquiescence and Tier A composition as the main source of the gap.
- It cannot separate maturation, cohort and survivorship/selection.
- It cannot separate style from substance for the SD overlap.

### P1-2. Higher social desirability (held-out d +0.47, corrected)
| Explanation | Our data | External evidence | Falsifier |
|---|---|---|---|
| **A. Age-related impression management or norm adherence** | The rise begins at 50+ (bands −0.15, −0.19, +0.13, +0.39; nonlinear p = 0.003). It survives Tier A adjustment (+0.39). | Dawes et al. list older age among common predictors of socially desirable responding, alongside alternative "traditional norms" readings (https://faculty.lsu.edu/pskatielab/files/contributions-social-desirability.pdf; abstract-level). | A within-person increase absent in panel data. |
| **B. Substance:** older people really behave more conscientiously or agreeably, and the scale captures it | Not separable from A with self-report. SD correlates −0.44 with neuroticism. | McCrae & Costa (1983), as above. | Behavioural or informant measures showing no age difference in the items' content. |
| **C. Nay-saying response style:** older people say "False" more | They do say "True" less (−0.41). But the SD gain appears on **both** TRUE-keyed (+0.24) and FALSE-keyed (+0.50) items. Nay-saying would lower the TRUE-keyed score. **Data discriminates: not the main driver**, though style may inflate the FALSE-keyed half. | — | TRUE-keyed SD flat or lower in 65+. |
| **D. Scoring artefact** | Already partly true: the shipped score inflated the gradient (`statistical_audit.md` C1). On corrected scores the gap survives. | — | — |
| **E. Cohort norms** | Indistinguishable from A. | — | Cohort-sequential data. |

### P1-3. Weak green and tightwad tilt
| Explanation | Our data | Verdict |
|---|---|---|
| **A. Age effect on values or money style** | Green +0.17 → +0.11 (CI includes 0) after Tier A; spendthrift −0.15 → −0.08 (CI includes 0). | Not supported once composition is held fixed. |
| **B. Composition (race, income, sex) of panel 65+** | Attenuates as expected. Green tilt is present in women (+0.27) and <$50k (+0.33), and about 0 in men and ≥$50k. | **Supported.** |
| External | The classic US review finds environmental concern *declining* with age (Van Liere & Dunlap 1980, *Public Opinion Quarterly* 44:181–197, doi:10.1086/268583; abstract-level). That runs opposite to a raw "older = greener" reading, which supports treating P1's tilt as composition or cohort, not age. | Falsifier: a persistent adjusted age gradient in a larger sample. |

---

## P2 (18–49, income < $50k)

### P2-1. Higher neuroticism (held-out d +0.55)
| Explanation | Our data | External evidence | Falsifier |
|---|---|---|---|
| **A. Age (same mechanisms as P1-1)** | About half: +0.23 (CI 0.16–0.30) of +0.47. | As P1-1. | — |
| **B. Social causation:** financial strain raises negative affect | Income within age: +0.24 (0.09–0.39) after Tier A. The gradient fades with age (18–29 +0.37, 30–49 +0.39, 50–64 +0.23, 65+ +0.15 with CI including 0). | Across MIDUS, HRS and SATSA, higher SES goes with lower neuroticism; evidence that SES changes neuroticism is weaker and concentrated at older ages (Luo et al., *J Personality* 92:243–260, doi:10.1111/jopy.12801; abstract-level). | Income shocks (e.g. lottery, layoff) producing no within-person change in neuroticism. |
| **C. Social selection (reverse):** neuroticism lowers earnings, employment and partnering | Indistinguishable from B in a cross-section. P2 is 23% unemployed vs 12% overall. Adjusting for employment trims the effect (+0.42 → +0.34). | The same Luo et al. paper; whether personality predicts SES change is not clearly established there (abstract-level). Twin-study "social causation over selection" claims: unverified — not cited. | Earlier neuroticism not predicting later income in panel data. |
| **D. Health confounding:** chronic illness raises both | Health is unmeasured, so this cannot be tested. | — | Gap unchanged after health adjustment. |
| **E. Measurement:** household income misclassifies students or co-resident young adults | Excluding students leaves +0.46. Other forms of misclassification are untestable. | — | — |
| **F. Response style** | Gap on forward-keyed +0.60 and reverse-keyed +0.47 items. SD adjustment gives +0.35. | — | Reverse-keyed items flat. |

**Verdict.**
- Our data separates age from income: about 50/50.
- It cannot separate B, C and D.

### P2-2. Lower social desirability (held-out d −0.25)
- **A. Age (younger people present themselves less favourably).** Within ages 18–49, low income has **zero** association with SD (−0.01, CI −0.16 to +0.14). The age mix alone predicts −0.17 of the −0.21. **Data discriminates: the trait is age, not income.**
- **B. SES norm differences.** Not supported (see A). Dawes et al. list low income among predictors of *higher* socially desirable responding (abstract-level, URL above). Our data shows no income effect in either direction.
- **C. Acquiescence.** P2 says "True" more often (+0.22). But SD is lower on both TRUE-keyed (−0.16) and FALSE-keyed (−0.28) items, so acquiescence is not the source.
- **Falsifier for A:** an income effect on SD appearing within an age band in a larger sample.

### P2-3. Weak green deficit (held-out d −0.15)
- **Composition.** The deficit is −0.19 raw and −0.08 (CI includes 0) after Tier A. Low income within age adds −0.05 (CI includes 0).
- **Cost or "financial constraint" account.** Not supported for *values*. The frozen behavioural "budget-constrained idealist" story also failed the holdout (memo §4).
- **Verdict:** composition. Falsifier: an adjusted income effect on green values in a larger sample.

---

## P3 (18–29, never married)

### P3-1. Higher neuroticism (held-out d +0.55)
- **A. Age band.** The within-18–29 never-married vs partnered difference is −0.01 (−0.26, +0.25), and +0.04 adjusted. **Data discriminates: P3's neuroticism is fully explained by age;** "never married" contributes nothing.
- **B. Partnering lowers distress, or stable people partner earlier (selection into marriage).** Not supported at this n. The point estimate is 0, with a CI of ±0.25.
- **Falsifier for A:** a within-age marital gap in larger data.

### P3-2. Lower green values (held-out d −0.40)
| Explanation | Our data | External evidence | Falsifier |
|---|---|---|---|
| **A. Sex composition** (the memo frames the gap as "concentrated in men") | Within 18–29 the never-married gap is −0.41 in men and −0.59 in women (interaction +0.18, CI −0.31 to +0.66). Re-weighting to equal sex mix leaves −0.53. **Data discriminates: sex composition is not the explanation.** The men/women asymmetry in the memo comes from comparing against the whole population, where young men are less green overall (−0.31 vs +0.09). | Women report more environmental concern than men in US data; a Gallup-based study finds weak support for a safety-concern explanation (https://aura.american.edu/articles/preprint/Explaining_gender_differences_in_concern_about_environmental_problems_in_the_United_States/23846604; abstract-level). | — |
| **B. Education and student status** | P3 has a BA in 33% of cases vs 60% of partnered 18–29s, and 21% are students. Adjusting moves −0.58 → −0.39 → −0.31 (CI just includes 0). **Partly supported.** | Van Liere & Dunlap (1980) tie concern to social class and education (abstract-level). | Gap unchanged after finer education and enrolment controls. |
| **C. Partnering raises concern (life-course/"legacy" mechanism)** | Not testable cross-sectionally. The comparison group is small (n = 75) and unusually green (married +0.36, cohabiting +0.26). | GSOEP 1984–2020 fixed-effects: childbirth has "marginal and mostly negative" effects on environmental concern (Zoch & Kapelle 2025, *Population and Environment* 47:23, doi:10.1007/s11111-025-00490-x). A UK panel finds only a small increase among already-concerned parents (https://link.springer.com/article/10.1007/s11111-017-0291-1; abstract-level). Marriage itself is little studied. **External evidence leans against C.** | Within-person change at partnering in panel data. |
| **D. Reverse/selection:** green, educated, "settled" young people partner earlier | Indistinguishable from C. | An MPIDR GSOEP working paper reports that parent vs childless differences in concern largely reflect unobserved heterogeneity (https://www.demogr.mpg.de/papers/working/wp-2023-023.pdf; abstract-level). That is consistent with selection, not causation. | Pre-partnering concern not predicting partnering. |
| **E. Ideology or identity** | Adding party (Tier B sensitivity): −0.46 (−0.75, −0.17). Party does not explain it. Other identity dimensions are unmeasured. | — | — |
| **F. Chance (selected from about 1,000 groups)** | The group was chosen by maximum mean \|d\|. It replicated out of sample (held-out −0.40), which argues against pure chance at the vs-population level. The *within-age* contrast rests on n = 75. | — | Failure to replicate in a fresh sample. |

### P3-3. Lower social desirability (held-out d −0.30)
- Within 18–29, never-married vs partnered: −0.03 (−0.30, +0.23). This is the age effect, so the data discriminates (as P2-2).
- A within-age never-married × male interaction exists (+0.63, p = 0.017). It is one of more than 40 interaction tests in this file, so it is not interpreted.

---

## External sources actually located (all abstract or record level unless noted)
1. Roberts, B. W., Walton, K. E., & Viechtbauer, W. (2006). Patterns of mean-level change in personality traits across the life course. *Psychological Bulletin*, 132(1), 1–25. https://pubmed.ncbi.nlm.nih.gov/16435954/
2. Terracciano, A., McCrae, R. R., Brant, L. J., & Costa, P. T. (2005). Hierarchical linear modeling analyses of the NEO-PI-R scales in the Baltimore Longitudinal Study of Aging. *Psychology and Aging*, 20(3), 493–506. doi:10.1037/0882-7974.20.3.493 (https://pubmed.ncbi.nlm.nih.gov/16248708/)
3. Soto, C. J., John, O. P., Gosling, S. D., & Potter, J. (2011). Age differences in personality traits from 10 to 65. *JPSP*. doi:10.1037/a0021717. Located and DOI verified via Crossref. Its neuroticism-specific findings were **not** read, so it is not used as evidence above.
4. McCrae, R. R., & Costa, P. T. (1983). Social desirability scales: More substance than style. *J Consult Clin Psychol*, 51(6), 882–888. doi:10.1037/0022-006X.51.6.882
5. Luo, J., Zhang, B., Antonoplis, S., & Mroczek, D. The effects of socioeconomic status on personality development in adulthood and aging. *Journal of Personality*, 92, 243–260. doi:10.1111/jopy.12801
6. Van Liere, K. D., & Dunlap, R. E. (1980). The social bases of environmental concern. *Public Opinion Quarterly*, 44(2), 181–197. doi:10.1086/268583
7. Zoch, G., & Kapelle, N. (2025). From parenthood to planet care? *Population and Environment*, 47(2), 23. doi:10.1007/s11111-025-00490-x
8. Socially desirable responding in geriatric outpatients with and without MCI. https://pmc.ncbi.nlm.nih.gov/articles/PMC8442330/
9. Dawes et al. Contributions of social desirability to self-reported ageism. https://faculty.lsu.edu/pskatielab/files/contributions-social-desirability.pdf
10. Explaining gender differences in concern about environmental problems in the United States. https://aura.american.edu/articles/preprint/Explaining_gender_differences_in_concern_about_environmental_problems_in_the_United_States/23846604
11. Legacy-hypothesis UK panel study, *Population and Environment* (2018). https://link.springer.com/article/10.1007/s11111-017-0291-1
12. MPIDR working paper WP-2023-023 (GSOEP, environmental concern and fertility). https://www.demogr.mpg.de/papers/working/wp-2023-023.pdf
13. Schonlau, M., et al. (2009). Selection bias in web surveys and the use of propensity scores. *Sociological Methods & Research*. https://www.stat.cmu.edu/~brian/303-2012-full/303-2011/303-2010/exam2/schonlau-et-al-2009-smr-propensity-scores-for-online-surveys.pdf

**Unverified — not cited:** age–acquiescence studies (e.g. World Values Survey analyses), a MIDUS twin study favouring social causation for income → internalising, and specific claims that online older adults are healthier or more educated.
