# Final statistical audit

Regenerate with `python src/final_audit.py`. Outputs are in this folder: `scale_verification.csv`, `misscoring_by_age.csv`,
`reliability.csv`, `integrity_checks.json` and `corrected_scores/`. Original frozen results (`results/`) were **not** modified.
Every corrected number sits beside its original.

Severity: **Critical** = invalidates a major conclusion or deliverable · **Major** = changes interpretation or confidence ·
**Minor** = documentation or presentation · **Verified** = independently checked and passed.

## Critical

### C1. Two more shipped scale scores are mis-scored, and the error depends on age (fixed)
All six constructs were re-derived from item-level data (`scale_verification.csv`):

| Construct | Item rule | Exact match with shipped score | Shipped score reproduced by |
|---|---|---|---|
| Green values | mean of QID235_1–6 | 100% | — |
| Neuroticism | BFI-44 items 4, 9R, 14, 19, 24R, 29, 34R, 39 | 100% | — |
| Dictator giving | (6 − QID231) × 20 | 100% | — |
| Spendthrift (already known) | Q31 + Q32 + (6 − Q33) + (6 − Q34) | 80.1% (409 wrong) | QID31 options 6 and 11 scored 0 (100% reproduced) |
| **Social desirability** | Reynolds Form C: TRUE-keyed 5, 7, 9, 10, 13; FALSE-keyed rest | **91.3% (180 wrong)** | Case-sensitive match on "TRUE"/"FALSE". 178 raw exports read "True"/"False"; 7 late IDs (2047–2057) were scored 0. Reproduces 99.7% |
| **CRT-2** | "emily", 0, 2, 8 | **78.1% (450 wrong)** | Case-sensitive "Emily" and exact strings "0", "2", "8". "emily" and "8.0" were marked wrong. Reproduces 100% |

**Why it is critical: the errors are not random with respect to age** (`misscoring_by_age.csv`):
- Social desirability is mis-scored for 11.6% of 18–29s but only 4.3% of 65+. The shipped score therefore *inflates* the age gradient.
- CRT is mis-scored for about 29% of people aged 50+ vs 14–19% of younger people. The shipped score therefore *manufactures* an age decline.

**Fix applied.**
- `load_people(corrected=True)` re-scores both constructs from the cleaned item CSV. The default path still reproduces every frozen original result, and a test checks this.
- The same pre-registered models and persona definitions were rerun with corrected scores (`corrected_scores/`). There was no new model selection, and the holdout was only re-scored.

**Impact** (original → corrected):

| Claim | Original | Corrected | Verdict |
|---|---|---|---|
| Social desirability: train CV R² / holdout R² | 0.051 / 0.067 | 0.062 / 0.077 | Holds, slightly stronger |
| Social desirability means by age band (18–29 → 65+) | 5.14 → 7.30 | 5.75 → 7.61 | Gradient holds, ~30% smaller range |
| P1 social desirability, d train → test | +0.42 → +0.49 | +0.39 → +0.47 | Holds, still distinct |
| P1 social desirability holdout MAE gain | +11.6% | +9.3% (CI 0.07–0.50) | Holds |
| P2 social desirability, d | −0.22 | −0.21 | Holds |
| CRT: train CV R² / holdout R² | 0.016 / 0.016 | 0.006 (CI −0.001 to 0.013) / 0.021 | CRT is even *less* predictable |
| CRT means by age band | 2.06, 2.21, 1.93, 1.82 | 2.38, 2.45, 2.43, 2.35 | **The age decline was an artefact** |
| P1 CRT, d | −0.18 ("weak difference") | −0.06 (not distinguishable) | **Original claim withdrawn** |
| P2 CRT, d | +0.13 ("weak difference") | +0.00 | **Original claim withdrawn** |
| P1 neuroticism gap adjusted for social desirability | −0.32 (−0.46, −0.18) | −0.31 (−0.45, −0.17) | Holds |
| P3 selection rule (re-run on train) | 18–29 never married | 18–29 never married | Unchanged |
| Say–do green-values OR adjusted for social desirability | 2.92 | 2.89 | Holds |

**Dependence.** Social desirability is one of P1's two distinct traits and appears in H1's directional checks. CRT drives H1's
"cognition" arm and two "weak difference" persona rows. No headline conclusion reverses. One H1 directional claim (CRT falls
with age) and two persona rows are withdrawn. The memo and persona reports now cite the corrected values and keep the originals in a note.

## Major

- **M1. CRT is unreliable** (KR-20 = 0.58 on 4 items; `reliability.csv`). Its low predictability is partly a measurement ceiling, so CRT
  comparisons should not carry weight. The other constructs are adequately reliable: green values α 0.93, neuroticism 0.90,
  social desirability 0.81, spendthrift 0.81. Dictator giving is a single item, so its reliability can't be estimated; it is also lumpy, with 6 possible values.
- **M2. The persona "Typical" column and its CI describe different estimands.** "Typical" is an empirical-Bayes shrunken mean; the CI is
  for the raw member mean. For dictator giving, τ² = 0, so "Typical" equals the population mean for every persona, and in the party
  sensitivity persona it falls outside the raw CI. **Fix:** persona reports now explain both columns explicitly. The estimates are unchanged.
- **M3. Interval coverage is weak evidence on bounded, discrete scales.** The population p10–p90 for CRT spans the whole 0–4 range, giving 100% coverage
  by construction. Social desirability and dictator giving pile up at the bounds. The "15/18 cells within 70–90%" result (H6c) is informative
  only for green values, neuroticism and spendthrift. **Fix:** stated in the memo and persona reports.

## Minor
- The CV R² interval (fold SD/√5 across 5×5 repeated folds) is a heuristic, not an exact standard error. The holdout R² values agree within 0.02.
- The persona d CI treats the population mean and SD as fixed and ignores that persona members are part of the population. For n ≈ 200 the CI is about 5% too wide or narrow.
- The persona and baseline predictions are means, but they are judged on MAE (for which a median is optimal). The comparison is fair because both sides are means, just not the best possible.
- τ² is a method-of-moments estimate from overlapping single-level groups, which is approximate.
- Logged deviation: inner ridge CV switched from 5-fold to leave-one-out for runtime.
- Chance imbalance between default arms (p = 0.04): the adjusted estimates are unchanged.
- **Platform-dependent solver (found by the fresh-environment run; fixed).** The redistribution follow-up's Ridge model received sparse one-hot input, so scikit-learn used an iterative solver. Its results differed by about 1e-5 (relative) between pip and Anaconda builds. It now uses dense input, which gives an exact Cholesky solve. Two reported cells moved in the 3rd decimal at rounding boundaries: ideology-model MAE 0.791 → 0.792 and EQUALITY-model R² 0.174 → 0.175. No contrast, CI or conclusion changed. The frozen confirmatory models use RidgeCV's exact leave-one-out path and reproduce to better than 1e-9.

## Verified
1. **Joins.** 2,058 unique `pid`s. Score files use `TWIN_ID` (same set). The Mega-Study raw `TWIN_ID` equals the parquet `PID` ("pid_n") for all three studies.
2. **Train/test isolation.**
   - The split is disjoint and complete: 1,442 / 616, sha256 checked by a test.
   - No commit after the holdout-script commit `8104628` touched `src/predictability.py`, `src/saydo.py`, `src/holdout.py`, `data/split.csv` or `hypotheses.md`.
   - Persona names and criteria are identical to those at `8104628`. The only later config commit is `85215f3` (final-audit phase 3), which rewrote the interpretation text (`integrity_checks.json`).
   - A fresh-clone rerun flagged an earlier wording of this check, which said `config/personas.json` was untouched. That was true when first run, before phase 3; the check now tests the criteria.
   - All follow-ups use the training split only, enforced by tests.
3. **Group definitions.** P1 uses {age_band}, P2 {age_band, income}, P3 {age_band, marital}, all Tier A. The CLI rejects party (unless flagged), ideology and unknown levels.
4. **Score construction.** Covered in C1; missing values are 0 for all six constructs.
5. **Cross-validation.** Preprocessing (one-hot, scaling, imputation) is inside sklearn pipelines fitted per fold. Hyperparameters are either fixed in advance or selected by inner CV within training folds. Leakage tests flip held-out outcomes and confirm their own predictions are unchanged.
6. **Bootstrap.** Participant-level resampling is appropriate because each participant contributes exactly one row per analysis.
7. **Baselines.** Training-fold mean or prevalence for CV; the train population mean for the holdout.
8. **Coverage computation.** Recomputed independently in `corrected_scores/personas_sd_crt.csv` with the same rule (inclusive train p10–p90).
9. **Green default.**
   - A Qualtrics flow randomiser assigned exactly one green item per person (300/300).
   - Choice coding was checked against the QSF labels: OPTOUT 1 = stay with GreenGrid; OPTIN 2 = switch to GreenGrid.
   - The causal reading applies to the default effect only. The green-values slope is correlational.
10. **No revision after the holdout.**
    - After the holdout, only the memo wording, presentation code and the exploratory or robustness additions changed. The holdout CSVs are byte-identical to `6b21fc3`, enforced by tests.
    - The P3 caveat was added to the memo after the holdout. It weakens rather than strengthens a claim.
11. **Effect sizes.** The say–do OR recomputed from the model (2.947) equals the reported value. ORs, AMEs and intervals are mutually consistent.
