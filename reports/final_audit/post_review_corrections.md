# Post-review corrections to the submission (2026-11-15)

**Authorized by:** the project owner, after an independent internal audit (`research_frontier/brace_challenge_lab/`).

**What stayed exactly the same:**
- the analysis, the methodology and every estimate;
- the frozen split (`data/split.csv`, sha256 `8ef47da0…`);
- the frozen confirmatory outputs in `results/`, which are byte-stable;
- the pre-registration;
- all held-out results.

Every change below is either a code defect fix or a correction to reporting and wording. No number was re-estimated.

| # | Defect (source) | Evidence | Change | Files |
|---|---|---|---|---|
| 1 | **Repeated criteria silently overwritten** (Workstream B). The persona generator kept only the last clause when a variable was repeated. | `sex=Male; sex=Female` exited 0 and profiled all 1,044 women, headed "sex = Female". | `parse_criteria` now treats repeated clauses as AND and intersects their levels. A contradiction (empty intersection) raises `CriteriaError`, and the CLI exits 2. Consistent repeats (e.g. `sex=Female; sex=Female`) and duplicate levels are accepted. | `src/personas.py` |
| 2 | **Unsafe `--name`** (Workstream B). | A name containing `/` crashed with FileNotFoundError. A name containing `../` wrote files outside `--out`. | `--name` must match `[A-Za-z0-9][A-Za-z0-9_.-]*` and must not contain `..`; otherwise the CLI exits 2. | `src/personas.py` |
| 3 | **Regression tests** for #1 and #2. | — | 4 new tests: contradictory repeats are rejected; consistent repeats are intersected; an impossible group abstains cleanly with INSUFFICIENT EVIDENCE; the CLI rejects contradictory criteria and unsafe names without writing files. | `tests/test_pipeline.py` |
| 4 | **Mixed units in the held-out tables** (Workstream A). "Gain (95% CI)" printed a percentage next to a CI for the mean reduction in absolute error, which is in raw scale units. | `results/holdout_personas.csv`: `gain_lo`/`gain_hi` are bootstrap quantiles of `e_pop − e_persona` (`src/holdout.py`). Re-checked: each raw reduction lies inside its own CI (e.g. P1 social desirability +0.398, CI +0.137 to +0.640). | **Rendering only.** Separate columns now show "Gain, % of population MAE" and "MAE reduction in scale units (95% CI)", with a footnote. The corrected-score bullets also give the raw-unit CI. The underlying values are unchanged. | `src/personas.py` → regenerated `reports/personas/*_evidence.md`; `reports/final_audit/statistical_audit.md` (one row) |
| 5 | **"P3 green gap concentrated in men"** (Workstream A). This compared a significant and a non-significant estimate, with no interaction test. | Within 18–29 (never-married vs partnered): men −0.41, women −0.59. The sex interaction is +0.18 (CI −0.31 to 0.66); `A_mechanisms/PERSONA_MECHANISMS.md`. | Softened: the shift looks larger in men against the whole population, but a sex difference is not supported. | `reports/memo.md` §2; `config/personas.json` → P3 card |
| 6 | **"Part of the 65+ calm is self-presentation"** (Workstream A). This is not identified. | One self-report social-desirability scale cannot separate response style from genuine adjustment. | Changed to "may be self-presentation", with that limitation stated. | `reports/memo.md` §2; `config/personas.json` → P1 card |
| 7 | **"Low income goes with neuroticism within every age band"** (Workstream A). This fails at 65+. | By age band: 18–29 +0.37, 30–49 +0.39, 50–64 +0.23, 65+ +0.15 (CI −0.11 to 0.42). | Changed to "within each age band under 65", adding the 65+ estimate. | `reports/memo.md` §2 |
| 8 | **"Top third" mislabel, and "stable feature of the population"** (Workstream C). | The cut is `green ≥ quantile(2/3)` = 4.0. Because of ties this includes 41% of training participants (`src/saydo.py`). Decline shares are 47% (41/87, Wilson CI 37–58%) and 50% (23/46, CI 36–64%). The green-values items never mention paying more, and the choice is hypothetical. | The heading and bullet now state the actual cut, the CIs, and the fact that this is not a measured attitude–behaviour contradiction. The generated evidence label is aligned. | `reports/memo.md` §1; `src/personas.py` label |
| 9 | **Two wording slips** (Workstream C). | "One cheap inner-layer item, a 6-item scale". And "the default itself added a borderline ~0.01", which reads as "the default barely matters". | Now "one cheap inner-layer measure, the 6-item scale", and "added ~0.01 to *prediction*; its causal effect is still +25 points". | `reports/memo.md` §5, §6 |
| 10 | **Small-cell overconfidence in the P3 card** (Workstream A). | Adjusting for sex does not remove the gap. | "Marital status mostly marks who is in the group" became "partly marks …, but adjusting for sex does not remove the gap". | `config/personas.json` → P3 card |

| 11 | **"Nearly all" of social desirability's R² comes from age** (Workstream D). | `reports/final_audit/headline_challenge/nested.csv`: age-only R² 0.038 vs full Tier A 0.062 (corrected scores). | Now "about 60% of social desirability's (0.038 of 0.062)". | `reports/memo.md` §1 |

Checked and **not** changed: the memo's "22% are 65+ vs 10%" is correct for the 600 `default_eric` participants (22.0% vs 9.95%). `audit/AUDIT.md` reports 21% on a different base.

## Verification
- **Page limits:** `tools/page_count.py` gives the memo 4 A4 pages and each persona card 1 page.
- **Tests:** the full suite passes after this commit. The `test_originals_untouched` guards compare protected files with the committed versions, so they pass once these authorized edits are committed.
- **Frozen outputs:** `results/` and `data/split.csv` are unchanged. The persona JSON estimates were regenerated byte-identical in content.

## Known issues left open (not fixed here)
These are listed in `research_frontier/brace_challenge_lab/B_unseen/FAILURE_TAXONOMY.md`:
- **Labels vs headline value:** "Distinct" labels use the raw d, while the headline "Typical" value is shrunk, and the two can disagree in small groups.
- **Ties ignored:** the "% on other side of the median" column ignores ties.
- **CIs on insufficient cells:** behaviour cells marked insufficient still print a CI.

Each of these would change the generator's output logic. They are documented as live-review caveats rather than patched before the deadline.
