# Challenging the headline claim (exploratory sensitivity checks)

**Headline under test:** census-observable demographics weakly predict temperament, but give little practical predictive value for
values and hypothetical choices.

These are **exploratory** checks on the **training split only** (n = 1,442), using corrected social desirability and CRT scores.
Regenerate with `python src/headline_challenge.py`; tables are in `headline_challenge/`. None of this is confirmatory, and nothing here
touches the frozen hypotheses or the holdout.

## 1. What is robust
- **Neuroticism is genuinely, if modestly, predictable from census facts.**
  - CV R²: ridge 0.151, OLS 0.142, gradient boosting with interactions 0.131. All CIs exclude 0.
  - Holdout R² (frozen analysis) is 0.17. The result does not depend on model choice.
- **Values, money style, cognition and generosity are not predictable.**
  - Across all three model families, green values, spendthrift, CRT and dictator giving stay at R² ≤ 0.04. The flexible model is *worse*.
  - The null is not a reliability artefact. Green values (α 0.93) and spendthrift (α 0.81) are measured reliably and still reach only 2.5% and 4.5% of their reliable variance.
- **The green-choice conclusions survive Mega-Study selection.**
  - Participants are older than other panel members (65+: 21% vs 10%) but do not differ on green values (d +0.01).
  - Reweighting to the panel's age mix leaves the green-values OR almost unchanged (2.54 → 2.56) and moves the default OR from 3.31 to 3.65.

## 2. What depends on model choice or sample composition
- **Neuroticism's predictability is about half age.**
  - Age band alone gives R² 0.074. Sex adds +0.015, and income adds a further +0.028 (sex + income together: +0.043, CI 0.027 to 0.058).
  - Employment status adds +0.058, largely through *unemployed* and *retired* categories that are partly life circumstances rather than census-style background.
  - Education and region add nothing.
  - "Temperament is visible" therefore mostly means "age, income and work status are visible".
- **Social desirability is almost entirely age.**
  - Age gives R² 0.038; sex, income, education and region add nothing (−0.008 to 0.000). The full model reaches 0.062 only by adding race and marital status.
  - Its age gradient was also partly inflated by the shipped scoring bug: the corrected 18–29 vs 65+ range is 5.75 → 7.61, vs 5.14 → 7.30 originally.
- **The claims about choices rest on one experiment** (n = 428 train; hypothetical; not incentivised). The redistribution outcome is an attitude, not a choice.

## 3. Interpretations to weaken
- Replace "demographics predict temperament" with **"age (and, more weakly, income and work status) predicts average neuroticism and self-presentation"**.
- **Group means ≠ individuals.**
  - 65+ vs 18–29 differ by d = −0.87 in neuroticism, a large group gap. Yet a randomly chosen 65+ person is *more* neurotic than a randomly chosen 18–29-year-old 25% of the time, and age band explains 7.8% of individual variance.
  - For social desirability, the probability that the older person scores higher is 0.66.
  - Personas are descriptions of distributions, not of members.
- **CRT should not be compared across groups at all.** It is unreliable (KR-20 0.58) and has only 5 values, and the corrected scores show no age gradient. The earlier "older adults are less reflective" pattern was a scoring artefact.
- **R² comparisons across constructs are only partly comparable.** Dictator giving has 6 discrete values with 10% at the floor, so R² is a poor yardstick. A null for dictator giving means "no detectable signal on a coarse single item", not "generosity is unrelated to demographics".

## 4. What would justify stronger claims
- A representative sample (or ACS reweighting) with finer age and income measurement, so that age effects can be separated from cohort effects.
- Longitudinal or repeated measurement of temperament, to tell ageing apart from cohort and from self-presentation (social desirability correlates −0.44 with neuroticism).
- Incentivised or real choices, and more than one costed decision domain, before generalising the "values > demographics" result beyond one hypothetical scenario.
- Multi-item or repeated measures for CRT and generosity, to raise reliability enough to detect small group differences.
