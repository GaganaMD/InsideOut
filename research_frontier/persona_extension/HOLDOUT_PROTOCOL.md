# Held-out check of the extended persona profile: protocol

**Status: NOT RUN.** This protocol must be committed before any code reads the test split for these traits. Running it needs the author's explicit approval.

## What this is, and what it is not
- A **secondary, post-selection** check. The six traits were chosen after the frozen holdout had already been inspected for the six pre-registered constructs, and after the training-split results in this folder were seen.
- It is a **second use** of the test split. The pre-registered evaluation in `results/` remains the only confirmatory one and is not rerun or changed.
- Results must be labelled "secondary, post-selection held-out check" wherever they appear. They must not be merged into the memo's §4 table or the cards' pre-registered columns.

## Frozen before the run
1. **Traits (six):** conscientiousness, agreeableness, extraversion, openness, need for cognition, self-concept clarity, re-derived from items exactly as in `persona_extension.py`.
2. **Personas:** the three in `config/personas.json`, criteria unchanged.
3. **Estimates fixed on training data:** population mean and SD, each persona's training mean, the empirical-Bayes shrunken mean computed with `src/personas.py`'s `tau2_by_construct` method applied to each new trait, and each persona's training p10–p90.
4. **"Distinct on training" list** (the pre-registered rule: |d| ≥ 0.20 and 95% CI excluding 0). Fourteen cells:
   - P1: self-concept clarity, agreeableness, conscientiousness, extraversion.
   - P2: conscientiousness, extraversion, self-concept clarity, agreeableness, need for cognition.
   - P3: conscientiousness, self-concept clarity, agreeableness, extraversion, need for cognition.
5. **Metrics**, identical to `src/holdout.py`: test d against the training population; MAE of the shrunken persona mean versus the training population mean on held-out members, with a participant bootstrap CI (2,000 resamples, seed 20261114); 80% interval coverage.
6. **Isolation contrasts re-estimated on test:** income within ages 18–49 adjusted for age band (P2); never married within 18–29 adjusted for sex, income and education (P3).
7. **Counterexamples re-estimated on test:** 65+ under $30,000 (neuroticism); P2 full-time employed (neuroticism, conscientiousness); P3 full-time employed (conscientiousness). Test cells are small (about 17, 45 and 25 people), so these are reported with intervals and no pass/fail rule.

## Reporting rules
- Report all 18 persona × trait cells, not only the 14 distinct ones.
- Report how many of the 14 keep their direction, and how many show an MAE gain whose CI excludes 0. State both counts whatever they are.
- No trait may be added, dropped or re-keyed after the run. No threshold may be changed.
- One run only. Record the commit of this protocol and of the script, and the run time, in `holdout_run.json`.
- If any result contradicts the training-split wording on the cards, the cards are corrected to match the held-out result.

## Not covered
The two-cluster description and the say–do analysis are not part of this check. The green-experiment test cells (75 high scorers) are too small to add information beyond what `results/holdout_saydo.json` already reports.
