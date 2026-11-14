# Overnight offline batch on Modal: feasibility audit and launch plan (2026-11-14)

Status: **smoke-tested end to end on Modal; full batch NOT launched** (awaiting authorization). No API calls of any
kind; no GPU; Brace submission untouched.

## 1. Modal feasibility audit (verified tonight, not assumed)

| Check | Result |
|---|---|
| CLI | `modal` 1.6.2 (standalone tool install at `~/.local/bin`; its Python is separate from the analysis Python) |
| Authentication | Token valid; `modal token info` → workspace **gagana-md-work**, environment `main` |
| Active profile | `gagana-md-work` (active); second profile `gaganaaa-dev` not used |
| Credits / billing | `modal billing summary` (month): metered $7.22 (volumes, from earlier projects), fully offset by free storage → **billed $0.00**. The remaining credit balance and any workspace spending limit are **not exposed by the CLI**; check them in the dashboard (Settings → Usage & Billing). |
| CPU | Works. Smoke function on 1 CPU returned in about 11 s end to end. |
| GPU | **Not tested and not needed.** All experiments are pandas/scikit-learn statistics. |
| Unattended | **Verified.** `modal run --detach` with a local entrypoint that only *spawns* the orchestrator: the local client exited at once, and the job then ran remotely and wrote its `DONE` marker. Your laptop can be closed after launch. |
| Issue found | On Windows the CLI crashes printing "✓" (cp1252). **Fix:** run every `modal` command with `PYTHONUTF8=1 PYTHONIOENCODING=utf-8`. |
| Spend so far tonight | About **$0.017** for all smoke, resume and failure tests (`modal billing report --for today`). |

## 2. Experiments in the batch

The batch is pre-specified, offline, and uses training participants only. Code: `offline/experiments.py`.

**Scope.** Two studies whose builders were verified line by line:
- **default_eric:** green vs grey default; outcome is choosing the $39 renewable tariff.
- **targeting_fairness:** an ad plan targeted to women vs one advertised broadly; outcome is a fairness rating from 1 (not at all fair) to 9 (very fair).

The other 17 studies are excluded tonight:
- some have no between-subjects condition;
- some need outcome-item mapping that has not been verified (hiring_algorithms, context_effects);
- some have duplicate IDs.

The batch never expands beyond the fixed list of 18 tasks.

| ID | Experiment | Tasks | Priority |
|---|---|---|---|
| A | **Treatment-effect recovery** from published GPT-4.1 predictions. Human ATE vs LLM ATE on the same participants under the same assigned condition. Raw and standardised effects, paired stratified bootstrap with 10,000 resamples. | 2 studies × 4 specifications = 8 | A |
| B | **Matched calibration and uncertainty.** Bias, SD ratio (heterogeneity compression), individual r, Brier or MAE against a constant baseline, total-variation distance between response distributions, and cell-level mean correlation (k ≥ 5 cells with ≥ 8 people). | 8 | B |
| C | **Information value.** Repeated stratified 5-fold cross-validation *within training*, 100 repeats. Six models, all including the randomised condition: condition only; + Tier A; + 6 attitude scores; + both; Tier A + the published full-persona LLM answer; LLM answer only. Paired bootstrap of model differences. | 2 | C |

The four specifications are the published GPT-4.1 runs: demographics-only at T 0.7 and at T 0, empty persona at T 0.7, and full persona at T 0.7.

### Verification done before packaging

Each item is an `assert` in `offline/prepare_bundle.py`; any failure aborts the build.
- **Split.** Every bundled row is `train` in `data/split.csv`. No test participant is analysed.
- **Human outcomes.** Human outcomes and conditions equal the published `consolidated_original_answers` for every training participant in both studies.
- **LLM rows.** Published LLM rows have unique TWIN_IDs, cover all training participants, and carry the **same assigned condition** as the human. Outcome ranges are checked: 0/1 for default_eric, 1–9 for targeting_fairness.
- **Known values reproduced.** default_eric gives human ATE +0.217 and LLM ATE +0.111 (demographics-only, T 0.7), matching the earlier benchmark audit.
- **Coding finding (targeting_fairness).** The survey's embedded `target` label is **inverted** relative to the text shown:
  - display logic shows the women-targeted plan to `Segment` 2, which carries `target="broad"`;
  - the broad plan goes to `Segment` 1, which carries `target="female"`.

  Treatment is therefore coded from `Segment`, the field that controls what is displayed. The inversion is asserted, so a future data change will fail loudly.

  Result: the women-targeted plan is rated **less** fair (6.35 vs 7.63). Anyone using the `target` label directly would get the sign of this effect backwards.

## 3. Exact data transferred to Modal

Only two parquet files, built into the container image. They total about 42 KB; the manifest has the sha256 for each.

| File | Rows | Columns |
|---|---|---|
| `default_eric.parquet` | 428 (training) | See below |
| `targeting_fairness.parquet` | 260 (training) | See below |

Columns in both files:
- `row`: a random permutation index, **not** the TWIN_ID;
- `treat` and `y_human`;
- 4 published LLM answers (`y_<spec>`);
- the 10 Tier A census variables;
- a coarsened demographic `cell` (k ≥ 5 in the full panel, otherwise `OTHER`);
- 6 derived scale scores (`att_green`, `att_social_desirability`, `att_spendthrift`, `att_crt`, `att_dictator_give`, `att_neuroticism`; corrected SD and CRT).

What is **not** sent:
- TWIN_IDs or the pid-to-row mapping, which is never written anywhere;
- item-level responses or free text;
- full psychological profiles;
- test-split participants;
- `.env`, API keys or Modal secrets. A test checks that the app attaches no secret, requests no GPU, and uploads exactly these two files.

**Residual risk:** Tier A plus six scores per row is quasi-identifying in principle. The source panel is public (CC BY 4.0), so this re-exposes public data inside a private Modal workspace. Nothing new is disclosed.

## 4. Runtime and cost

| | Value |
|---|---|
| Measured locally (full size) | A: 1 s per task; B: up to 5 s; C: 32 s per study |
| Expected Modal wall time | **About 2–5 min** for all 18 tasks (4 workers, plus image start). An overnight window is not actually needed; detached mode only removes the need to keep the laptop on. |
| Expected cost | **About $0.02–0.05.** CPU $0.0473 per core-hour and memory $0.008 per GiB-hour, from `modal billing rates`. |
| Hard worst case | **$1.04**, if every task hits its 30-minute timeout twice and the orchestrator runs its full 3 hours. The entrypoint asserts that this stays under **$5**. |
| Storage | Under 1 MB of results on the Volume, covered by Modal's free storage. |

## 5. Bounds, checkpoints and retrieval

**Bounds:**
- the 18-task list is fixed in `offline/tasklist.py`;
- worker: 1 CPU, 1 GiB, **30-minute timeout, 1 retry**, at most 4 containers;
- orchestrator: 3-hour timeout, **0 retries**;
- no loops that depend on results, and no expansion.

**Checkpoints.** Volume `brace-overnight-results/<run_id>/` holds:
- `manifest.json`: tasks, parameters, bundle hashes and worst-case cost;
- `progress/<task>.json`: started or done, with runtime;
- `results/<task>.json`: committed as soon as each task finishes;
- `failures/<task>.json`: error and traceback;
- `summary.json` and `DONE`.

Re-launching with the same `--run-id` skips finished tasks. **Verified:** a re-run gave `skipped_existing: 3`.

**Failure behaviour (verified with a deliberately broken task):**
- the error and traceback are written to `failures/`;
- Modal retries the task once, then marks it failed;
- the orchestrator still completes and writes `summary.json` (with `failed: 1`) and `DONE`;
- other tasks are unaffected.

If the orchestrator itself dies, finished results remain on the Volume and a re-launch resumes. If the whole job fails, the only loss is time; the cost is bounded as in section 4.

**Retrieving results tomorrow** (verified with the smoke run):
```bash
PYTHONUTF8=1 PYTHONIOENCODING=utf-8 modal volume get brace-overnight-results <run-id> research_frontier/overnight/runs/modal/
```
```bash
python research_frontier/overnight/offline/summarize.py research_frontier/overnight/runs/modal/<run-id>
```

## 6. Launch command (requires authorization)

```bash
cd research_frontier/overnight/offline && PYTHONUTF8=1 PYTHONIOENCODING=utf-8 modal run --detach modal_app.py --mode full --run-id full-20261114
```

## 7. Verdict

**GO for the bounded full batch, pending your authorization.** Every check passed:
- authentication;
- remote CPU execution;
- detached execution that survives the local client exiting;
- persisted and retrievable results;
- resume;
- bounded failure handling;
- a worst-case cost under the ceiling;
- minimal, pseudonymous, training-only data.

**Caveats:**
- The credit balance and spending limit could not be verified from the CLI.
- Only 2 of the 19 studies are in scope.
- The results are exploratory. They add no holdout analysis, and they do not test any new LLM.
