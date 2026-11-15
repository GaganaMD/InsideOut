# Known limitations and open issues (as recorded by the author)

## Design
- **One wave of data.** Everyone is observed once. Age differences combine maturation, cohort and selection into the online panel.
- **Coarse categories.** Age has 4 bands and income 5, which caps achievable R².
- **Hypothetical choice only.** Behaviour is a single hypothetical, non-incentivised choice in one scenario (`default_eric`). The green-values items do not mention paying more.
- **Experiment sample skews old.** In `default_eric`, 22% of participants are 65+ vs 10% of the other panel members. Persona behaviour cells are small: 16–17 per condition for P3.
- **Panel weighting.** The panel is a US online panel, not reweighted to census margins.

## Measurement
- **Shipped scoring.** Three shipped scale scores contained scoring defects (see `03_METHODS_AND_HOLDOUT.md`). Results exist in both legacy and corrected modes.
- **Social desirability.** It is measured by one self-report scale, which cannot separate response style from genuine adjustment.
- **CRT reliability.** CRT-2 has KR-20 0.58.

## Inference
- **Associations.** The green-values association with choice is not causal. Only the default effect is randomised.
- **Multiple comparisons.** The P3 search covered about 1,000 candidate groups. P3's green-values difference is weak after shrinkage, and has no supported sex difference.
- **Behaviour forecasts.** Behaviour rates at persona level did not beat the population rate on held-out data.
- **Labels change after shrinkage.** Some pre-registered "distinct" labels become "weak" or "same as population" after shrinkage: P1 green and spendthrift; P2 social desirability; P3 green values. Both labels are displayed.
- **Repeated-CV uncertainty.** Predictability CIs use mean ± 1.96·SD/√5 over repeated-CV folds, an approximation the memo calls "somewhat optimistic".

## Reporting
- **Units in `results/predictability_map.csv`.** The file has `mae_gain_pct` (percent) next to `mae_gain_lo/hi` (raw units, ±1.96 SE). It is a frozen file; the memo does not print these intervals.
- **Commit log entry.** `reports/final_audit/integrity_checks.json` records the git log, so it changes with every new commit.
