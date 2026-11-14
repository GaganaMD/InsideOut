# Submission manifest

## A. Submit: the deliverables Brace asked for
| Deliverable (assignment item) | File(s) |
|---|---|
| Research memo, ≤ 4 pages, conclusions first | `reports/memo.md` (renders to 4 A4 pages at 11pt) |
| Three personas, about one page each | `reports/personas/P1_adults_65plus.md`, `reports/personas/P2_under50_income_below_50k.md`, `reports/personas/P3_young_never_married.md` (each renders to 1 A4 page at 11pt) |
| Exploration log | `reports/exploration_log.md` |
| Note on AI use | `reports/ai_note.md` |
| Code repository; one command regenerates everything; builds personas for new criteria | The whole repository. Entry points: `README.md`, `run_all.py`, `src/personas.py build …`. Also needed: `requirements.txt`, `config/personas.json`, `hypotheses.md`, `data/split.csv`, `src/`, `tests/`, `tools/` |

## B. Supporting evidence (in the repository, referenced by the deliverables)
| What | File(s) |
|---|---|
| Full persona tables (frozen legacy-scored estimates, plus a correction note) | `reports/personas/*_evidence.md`, `reports/personas/*.json` |
| Final statistical audit (scale re-derivation, scoring defects, corrected reruns) | `reports/final_audit/statistical_audit.md`, `scale_verification.csv`, `misscoring_by_age.csv`, `reliability.csv`, `integrity_checks.json`, `corrected_scores/` |
| Headline challenge (exploratory sensitivity checks) | `reports/final_audit/headline_challenge.md`, `headline_challenge/` |
| Fresh-environment reproduction and CLI simulation | `reports/final_audit/live_review_simulation.md`, `live_review/` |
| Data audit and frozen split provenance | `audit/AUDIT.md` and the `audit/` tables |
| Frozen confirmatory outputs (byte-stable since the holdout run) | `results/` |
| Pre-registration | `hypotheses.md` (commit `2540e2c`) |

## C. Historical or exploratory artefacts (kept for provenance; not current findings)
| What | File(s) | Caveat |
|---|---|---|
| Exploratory follow-ups (green values vs demographics; redistribution attitude) | `reports/exploratory/` | Training data only; added after the holdout was inspected |
| Robustness analyses and first adversarial review | `reports/robustness/` | Persona stability used the **legacy** social-desirability score. The adversarial review predates the final audit, which supersedes it |
| Party sensitivity persona | `reports/sensitivity/` | Self-reported party (Tier B), legacy scoring |
| Reviewer preparation (for the presenter) | `reports/final_audit/reviewer_defense.md` | Optional to share |

## D. Not submitted
- `data/raw/` and `data/processed/`: downloaded or regenerated; git-ignored.
- `reports/generated/` and `reports/robustness/cli_examples/`: ad-hoc CLI output; git-ignored.

## Scoring modes (why some files show different social-desirability and CRT values)
The dataset's shipped social-desirability and CRT scores contain scoring defects that are reproduced exactly in `reports/final_audit/statistical_audit.md`.
- **Current findings** (memo, persona cards, `build` by default) use corrected item-level scores, marked † or "corrected".
- **Historical reproduction** (`results/`, `*_evidence.md` tables, `--legacy-scores`) keeps the shipped scores, so pre-audit results reproduce exactly. These are labelled LEGACY, and their values must not be cited as current findings.
