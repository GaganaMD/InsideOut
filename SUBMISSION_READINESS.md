# Submission readiness (2026-11-15)

## Verdict: **GO**

Every deliverable requirement is met and verified. No critical defect is open.

### Final verified state (final submission commit, 2026-11-15)
This commit applies the independent reviewer's persona-extension patch, prepared against `efcd76b`, plus integration adjustments. Every change is logged in `reports/final_audit/post_review_corrections.md`.

- **Exploratory content.** The extended profiles, within-age contrasts, counterexamples, two-cluster description and say–do check are exploratory: training split only, not pre-registered, no held-out check. They live in `research_frontier/persona_extension/`, outside `run_all.py`, and reproduce byte-identically from their script.
- **Unchanged frozen material:**
  - the split (sha256 `8ef47da0…`);
  - `results/` and `hypotheses.md`;
  - the persona criteria and persona JSON estimates;
  - the confirmatory six-construct evaluation.
- **Fresh clone of the candidate** (`efcd76b` plus these changes, before the final documentation-only edits):
  - `python run_all.py` exited 0 in 11m12s, and `pytest` passed **43**;
  - the only regenerated difference is `integrity_checks.json`, which records the git log.
- **After the final documentation-only edits** (P1 wording, `SUBMISSION.md`, review-packet copies, this file), checked on the working tree before committing:
  - the cards were regenerated;
  - the research harness passed 39 tests;
  - the submission suite passed 40. The 3 `test_originals_untouched` guards flagged only the intentionally edited config, cards and P2/P3 evidence files; they compare against the last commit, so they pass once this commit exists.
- **Page limits:** the memo is 4 pages (page 4 has no slack) and each persona card is 1 page.

### Earlier integration check at `f9ee2bc` (historical; superseded by the section above)
This commit combines the GPT-4.1 results (`58ed021`), the exploratory breadth sweep (`8906c18`) and the independent-review wording corrections (`f9ee2bc`).

- **Fresh clone:** `python run_all.py` exited 0 in 11m22s, and `pytest` passed **43**.
- **Generated outputs:** ignoring line endings, the only difference from the committed files is `reports/final_audit/integrity_checks.json`, which records the git log. `results/`, `data/split.csv`, `reports/personas/*` and the memo regenerate identically.
- **Page limits:** the memo is 4 pages and each persona card 1 page (`tools/page_count.py`).
- **Research harness tests:** 39 passed.
- **Unchanged since the holdout:** the frozen split (sha256 `8ef47da0…`), `results/` and `hypotheses.md`.
- **Outside the submission pipeline:** the breadth sweep (`research_frontier/breadth_sweep/`) is not referenced by `run_all.py`, `src/`, `tests/` or `tools/`.
- **LLM work:** the GPT-4.1 run (1,556 responses, about $1.25 billed) and the Qwen runs are exploratory, under `research_frontier/`, and contribute to no submitted estimate.
- **Separate review folder:** `independent_review/` is kept local and excluded via `.git/info/exclude`. It is not part of the submission.

## Requirement checks

| Requirement | Status | Evidence |
|---|---|---|
| Memo ≤ 4 pages | ✅ 4 A4 pages at 11pt | `python tools/page_count.py reports/memo.md` |
| Three personas, about 1 page each | ✅ 1 page each | `tools/page_count.py` on `reports/personas/P{1,2,3}_*.md` |
| Exploration log | ✅ | `reports/exploration_log.md` |
| AI-use note | ✅ | `reports/ai_note.md` (see the note at the end of this file) |
| One-command reproducibility | ✅ | See "Clean-clone reproduction" below |
| New-group persona generation | ✅ | `python src/personas.py build …`. Contradictory or unsafe input is rejected with exit 2, and groups with n_train < 30 abstain. 25 unseen groups were stress-tested (`research_frontier/brace_challenge_lab/B_unseen/`). |
| Honest held-out evaluation | ✅ | The split is frozen (`data/split.csv`, sha256 `8ef47da0…`, tested). `results/` is byte-identical in content after every correction. The held-out set was evaluated once; no method was tuned on it. |

### Clean-clone reproduction
1. **Committed state at `d8de4ce`.** A fresh `git clone` plus `data/` ran `python run_all.py`, which exited 0 in 10m14s, followed by `pytest`: 39 passed. Ignoring CR/LF line endings, only two regenerated files differed from the committed versions:
   - `integrity_checks.json`: expected, because it records the git log;
   - the party sensitivity persona: stale after a label change, now regenerated in `212481a`.
2. **Latest commit, `212481a`.** In the same clone, re-running `src/holdout.py`, `personas.py build-config` and the sensitivity build gave **zero** content differences. `pytest`: **43 passed**.
3. **Log noise.** One `[WinError 2]` line in the log is a joblib warning about counting CPU cores. It does not affect results.

### Test counts (local, final)

| Suite | Passed |
|---|---|
| Submission, `tests/` | 43 |
| Research harness, `research_frontier/overnight/tests` | 39 |
| Open-weight design checks, `F2_modal_open_weight/test_f2.py` | 5 |

## Exact commands
```bash
pip install -r requirements.txt
```
```bash
python run_all.py
```
```bash
python -m pytest -q tests
```
```bash
python src/personas.py list-levels
```
```bash
python src/personas.py build --name my_group --criteria "age_band=65+; income=Less than $30,000"
```

When narrating a live persona:
1. Read the definition and n back.
2. Narrate only traits that are still "distinct" **after shrinkage**.
3. Behaviour needs at least 20 people per default condition.

## Relevant commits (2026-11-15)

| Commit | Change |
|---|---|
| `0852b63` | Criteria bug, table units, softened claims |
| `5eddaf6` | Social desirability R² share |
| `f9cbe6b` | Behaviour floor 20, shrinkage-consistent labels, median ties, plus the Qwen order-bias audit |
| `212481a` | Sensitivity persona regenerated |
| Independent-review corrections (the commit after `58ed021`) | Wording only: scope of the six constructs and CRT-2, group versus individual prediction, census definition, persona overlap, shrinkage, LLM descriptions |

Every change is listed in `reports/final_audit/post_review_corrections.md`. **No estimate, split or held-out result changed.**

## Unresolved limitations (state them openly)
- **Cross-sectional design:** age effects mix maturation, cohort and online-panel selection. Age has only 4 bands and income 5.
- **Hypothetical choices:** all choices are hypothetical, with no incentives. The "say–do" decline is not a measured attitude–behaviour contradiction.
- **Social desirability:** one self-report scale cannot separate response style from genuine adjustment.
- **Persona behaviour rates:** they do not forecast at the persona level, because cells are small.
- **Labels after shrinkage:** some pre-registered "distinct" labels weaken after shrinkage: P2 social desirability, P3 green values. Cards now show both labels.
- **LLM comparisons are exploratory and outside the submission:**
  - GPT-4.1 with an estimated profile: a 264-call feasibility pilot and then the full pre-registered run (1,556 calls; $1.25 billed in total) were completed on 2026-11-15 (`research_frontier/brace_challenge_lab/F3_gpt41/RESULTS.md`). No submitted estimate uses them.
  - The open-weight Qwen results cover one scenario and two small models.

## Files to send to Kush
1. `reports/memo.md`
2. `reports/personas/P1_adults_65plus.md`, `reports/personas/P2_under50_income_below_50k.md`, `reports/personas/P3_young_never_married.md`
3. `reports/exploration_log.md`
4. `reports/ai_note.md`
5. The repository link, with `README.md` and `SUBMISSION.md` as entry points. If he asks: `reports/final_audit/post_review_corrections.md`.

Render the markdown files to PDF if the brief asks for documents. `tools/page_count.py` produces A4 PDFs.

`reports/ai_note.md` discloses the 2026-11-15 AI-assisted audit, the corrections and the later independent review.

`research_frontier/` holds the post-submission research (mechanisms, stress tests, the LLM benchmarks). It is supporting material, not a deliverable.
