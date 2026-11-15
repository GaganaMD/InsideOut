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

| 12 | **Behaviour-cell floor inconsistent.** The say/do block used n ≥ 10, but the pre-registration (`hypotheses.md` line 76) and the memo require ≥ 20 per default condition for a behavioural estimate. | `src/personas.py`: `status="ok" if len(s) >= 10`. | The say/do block now uses `MIN_N_BEHAVIOUR` (20), the same floor as the choice rates. The only existing JSON values that change are `say_do_gap[*].status` for P1–P3; all shares, CIs and n are unchanged. | `src/personas.py` → `reports/personas/*` |
| 13 | **"Distinct" label inconsistent with the shrunk "Typical" value.** The label came from the raw mean, while Typical is shrunk, and the two can disagree in small groups. For 65+ & < $30k, CRT was raw-distinct at shrink weight 0.04. | Stress test (`B_unseen`). | **The pre-registered `confidence` field is unchanged** and still feeds every frozen result (`results/holdout_personas.csv`). New fields `shrunk_d`, `shrunk_ci_lo/hi` and `confidence_shrinkage_adjusted` re-apply the same rule to the shrunk estimate: \|d_shrunk\| ≥ 0.20 and a posterior CI excluding the population mean, with posterior SD = √w·SE. Because the posterior z = √w × the raw z, the adjusted label can never be stronger. When the adjusted label is weaker, cards and evidence files show both ("distinct before shrinkage; **weak after shrinkage**"). | `src/personas.py` → `reports/personas/*` |
| 14 | **"% on other side of median" hid ties.** For example, 72% of 65+ & < $30k sit exactly at the dictator-giving median. | Stress test. | The statistic is unchanged (strict: ties are not counted as "other side"). A new field, `share_at_pop_median`, is displayed in brackets, and the convention is stated under the table. | `src/personas.py` → evidence files and CLI output |

**Effect of #13 on the submitted personas (display only):**

| Persona | Construct | Before shrinkage → after shrinkage |
|---|---|---|
| P1 | green | weak → same as population |
| P1 | spendthrift | weak → same as population |
| P2 | social desirability† | distinct → weak |
| P3 | green values | distinct → weak |

The pre-registered labels, the held-out evaluation (H6) and the memo's §4 table are unchanged. The cards now show both labels.

**Regression tests added** (`tests/test_pipeline.py`):
- the shrinkage label is never stronger than the pre-registered one, which itself stays intact (9 groups, including small ones);
- the 65+ & < $30k CRT label is flagged;
- the three median shares sum to 1, and ties are visible;
- the behaviour floor is 20 for both the choice rates and the say/do block;
- plus the earlier tests for contradictory criteria and impossible groups.

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

## Independent-review corrections (2026-11-15, second pass; wording only)
An independent adversarial review (a Claude session that had not built the project) proposed these; the author approved the mandatory ones. **No estimate, split, persona definition or held-out result changed.**

| Area | Change | Why |
|---|---|---|
| Memo §1, headline and H1 | Scoped to the six pre-registered constructs; "reasoning" → "CRT-2 reflection"; H1 "falsified as registered, for CRT-2 and not for cognitive ability in general" | The frozen map covers six constructs, and cognition was measured only by the four-item CRT-2 (KR-20 0.58) |
| Memo §1, new scope bullet | Reports an exploratory sweep of all 50 usable shipped scores: median R² 0.05, maximum 0.16, eleven at 0.10 or more | The six are not representative. The sweep is training-only, sits outside `run_all.py` (`research_frontier/breadth_sweep/`), and uses scores that were not independently re-scored |
| Memo §1.4 | Group-level and individual-level conclusions separated; the behaviour null qualified by cell size | A 0.4–0.6 SD group shift and a one-tenth individual gain are both true; about 40 people per cell cannot exclude 10–15 point differences |
| Memo §3 | Census definition: party is excluded because no census form asks it, not because it is self-reported; most items are ACS; clients see areas | Every Tier A variable is self-reported (`audit/variable_map_outer.csv`) |
| Memo §1.3, §5 and the three cards | Persona overlap and age dependence stated: three of four holdout gains are neuroticism; 41% of P3's training members are in P2; P1 is age alone; none covers 50–64 | `results/p3_selection.csv`, `results/holdout_personas.csv` |
| Memo §5 and card footnote (`src/personas.py`, text only) | Shrinkage: "Typical" is a shrunken estimate, the CI is for the raw mean, the prior is zero for dictator giving | Statistical audit M2; the old text blamed a "Tier A-specific" prior |
| Memo §5, AI note, readiness file | Stale LLM statements corrected: post-submission runs exist; a 264-call GPT-4.1 pilot and then the full pre-registered run were completed (commit `58ed021`); no submitted estimate uses them | `research_frontier/brace_challenge_lab/F3_gpt41/RESULTS.md` |
| `research_frontier/` write-ups | Qwen prompt described as an abridged paraphrase without the survey's stay/switch options; the no-persona tie and the confidence result qualified; "never beat a free baseline" corrected | Survey QSF against the prompt code; raw Qwen outputs; `F_llm_benchmark/CALIBRATION_AND_FAILURES.md` |
| Memo, space only | Shortened passages to stay at 4 pages; no finding removed | Page limit |

Verification: memo 4 pages, cards 1 page each, `tests/` pass, `results/` and `data/split.csv` unchanged, persona JSON regenerated identical in content.

## Persona-extension additions (2026-11-15, third pass; exploratory, training split only)
Made after re-reading the brief, which weights the "why" most. **No frozen estimate, split, hypothesis or persona definition changed.** Source for every new number: `research_frontier/persona_extension/` (outside `run_all.py`).

| Area | Addition | Status |
|---|---|---|
| Cards | "Why this persona" (the question each one asks); an extended profile of six further scales; one within-persona counterexample; named sources in "Why it fits" | Scales re-derived from items (exact match). Training members only; not pre-registered; no held-out check. Counterexamples were found by inspection |
| Memo §1 | Who declines among high green-values scorers: not identifiable from the tested demographics and traits; detectable gap about 20 points | Exploratory; absence of evidence, stated as such |
| Memo §2 | Two loose trait clusters and their relation to Tier A and to the choice | Descriptive correlations; no confirmatory factor model |
| Memo §3, §5 | The question each persona asks; party judged against the brief's "census or public records" test; "two dimensions, not three archetypes" | Wording |
| Memo §6 | Compressed to make room; every number kept | Space only |

A held-out check of the extended profile is specified in `research_frontier/persona_extension/HOLDOUT_PROTOCOL.md` and has **not** been run.

**Integration adjustments to that pass** (wording only; made when applying it):
- **CRT caveat restored.** The withdrawn "less reflective" CRT caveat is back on the P1 and P2 cards.
- **No equivalence claim.** P1's behaviour line now says the small samples did not establish a difference and that this is not evidence of equivalence. It gives the held-out cell sizes (25 and 18, per `results/holdout_persona_behaviour.csv`).
- **Correlational wording in memo §2.** "the choice follows values" became "goes with values", and the bullet now states that it is a correlational description, not a mechanism.
