# GO_NO_GO

## Verdict: **READY FOR PILOT**
The scope is the `default_eric` cell-level pilot only, with tier 1 privacy, after your explicit authorisation. **Medium and full runs: NEEDS DATA VERIFICATION.**

## Gate checklist
| Gate | Status | Evidence |
|---|---|---|
| Published-benchmark audit done; overstatements corrected | ✅ | `BENCHMARK_VALIDITY.md`; corrections appended to `09_existing_llm_benchmark.md` |
| Studies inspected; ≤ 3 selected; randomisation verified from survey flows | ✅ | `STUDY_SELECTION.md`, `results/study_audit.csv` |
| Information-matched arms specified | ✅ for E/D/B; G deferred (privacy); F uses published predictions | `PREANALYSIS_PLAN.md` |
| Privacy and licence gate | ✅ CC BY 4.0 and Apache-2.0 verified. Consent does not cover third-party API processing, so the design is **restricted to tier 1** (k ≥ 5 synthetic cells, no IDs or outcomes); tier 2 has no code path | `PRIVACY_AND_PERMISSIONS.md` |
| Harness: dry-run, fixed templates (hash `ce5d34f1da6ea2ad`), JSON validation, concurrency and rate limit, cache and resume, retries, token and cost accounting, hard budget, secret redaction | ✅ | `harness/`; **20 unit tests pass** (mock API, no network); a dry run of 420 calls then resumed with 0 new calls |
| Prices verified, not assumed | ✅ (snapshot 2026-11-14 17:09 UTC) | `pricing_snapshot.json`, `COST_AND_RUN_PLAN.md` |
| Pre-analysis plan with hypotheses, metrics, uncertainty, multiplicity and stopping rules | ✅ | `PREANALYSIS_PLAN.md` |
| No paid calls made | ✅ | Only `DryRunTransport` and mocks were used |
| Submission, figures and frozen results untouched | ✅ | All work is in `research_frontier/` |

## Before pressing go (pilot)
1. Read `PRIVACY_AND_PERMISSIONS.md` and decide whether you authorise tier 1. Your typed confirmation string is the authorisation record.
2. Re-verify the model's price (rebuild `pricing_snapshot.json`) and set `--budget 1`.
3. Optionally add OpenRouter's no-data-retention provider setting, after checking its exact parameter name in the docs.
4. Commit `PREANALYSIS_PLAN.md`, which is part of this commit, so the plan predates the run.

## Open items blocking the medium and full runs (data verification)
- The demographics-only persona fields used by Peng et al. are unverified, which affects how well our arm D aligns with their published arm.
- Task builders and outcome coding are not written for targeting_fairness and context_effects (scenario wording, the group → version mapping).
- `analyze_pilot.py` (cache → plan metrics) is not written. It is needed before interpreting results.
- Duplicate IDs in obedient_twins and digital_certification, if those studies are ever added.
