# Pilot readiness: 80-call OpenRouter feasibility batch (default_eric)

Status: **prepared, not run.** No paid call has been made. This batch runs only after explicit written authorization from
the project owner. Harness base: commit `4ca4268`, plus the pilot changes in this commit.

## 1. Exact command (run from `research_frontier/overnight/`)

```bash
python -m harness.cli check-key
```
```bash
python -m harness.cli plan --model openai/gpt-4.1 --pilot
```
```bash
python -m harness.cli live --model openai/gpt-4.1 --pilot --budget 1 --confirm "I have authorization to send k-anonymous demographic cells to OpenRouter"
```

- **Model ID:** `openai/gpt-4.1` (OpenRouter). This may not be the same snapshot as the GPT-4.1 used by Peng et al. (2025).
  The comparison with their published predictions is therefore model-family-level, not a replication of their run.
- **Calls:** 80 unique calls. This is 20 empty-persona calls (10 samples × 2 default conditions) plus 60 Tier A cell
  calls (10 cells × 2 conditions × 3 samples). Retries for 429 or 5xx responses re-send the same request and are
  counted against the budget.
- **Estimated cost:** ≤ $0.072 as an upper bound. This assumes about 23,200 input tokens and the 40-token output cap
  for every call. Prices come from `pricing_snapshot.json` ($2/M in, $8/M out, snapshot 2026-11-14).
  - **Hard cap:** $1. With `--pilot`, a `--budget` above 1 is refused with exit code 2.
  - **Enforcement:** the runner reserves the worst-case cost of each call before sending it and stops when the reservation would exceed the budget.
- **Output:** `runs/live/pilot__openai__gpt-4.1/`, containing `cache.jsonl`, `events.jsonl` and `summary.json`. The
  folder is git-ignored. Re-running the command resumes from the cache and never pays twice for the same task key.

## 2. Credential handling (verified)

- **Key source.** The key is read from `OPEN_ROUTER_KEY` in the repository `.env` via `python-dotenv`, with
  `override=False`. `OPENROUTER_API_KEY` is accepted as an alias (`harness/credentials.py`).
- **When the key is loaded.** `.env` is loaded in only two places:
  - in `check-key`;
  - in `live`, *after* the exact `--confirm` text has been verified.

  Plan and dry-run modes never read it. A key being present never selects the HTTP transport; only the `live`
  subcommand does.
- **Three opt-ins.** All of these are required:
  1. the `live` subcommand;
  2. the exact confirmation sentence;
  3. a key being present.

  If any is missing, the command exits with code 3 and nothing is sent.
- **The key is never exposed.** It is never printed, logged, cached or passed on the command line. `redact()` scrubs
  the key value from any error text. `check-key` reports booleans only.
- **Git safety.** `.env` is now listed in `.gitignore` (before this commit it was untracked but not ignored). It is
  untracked and does not appear anywhere in git history.
- **Tests.** Every test uses a mock key (`mock-key-not-real-0000`) and stubs out the `.env` loader. Transports are
  either the dry-run transport or a mock.

## 3. Prompt examples (template hash `ce5d34f1da6ea2ad`)

Every call uses the same system message:
> You simulate how a person with the described characteristics would answer a survey question. Answer as that person
> would, not as an expert. Respond with JSON only.

**Empty persona, green-default condition.** The user message is an abridged paraphrase of the survey's scenario text, followed by:
```
Question: Which electricity supplier do you choose?
Options:
A: GreenGrid: renewable electricity, $39 per month
B: Twon: standard electricity, $32 per month
Reply with exactly this JSON and nothing else: {"choice": "<one of A | B>", "p": <your probability, 0-1, that this person picks option A>}
```

**Tier A cell, green-default condition.** The same message, preceded by:
```
Person:
- age: 30-49
- sex: Female
- household income: $100,000 or more
- education: college degree
```
The grey-default condition swaps the scenario text: Twon is the incumbent supplier and GreenGrid's flyer arrives later.

**Pilot cells.** These are the 10 largest training cells that are present in both conditions, all with k ≥ 5 in the
2,058-person panel:
30-49 F $100k+ college · 30-49 F <$30k no-college · 30-49 M $100k+ college · 30-49 M $30–50k no-college ·
30-49 M <$30k no-college · 50-64 F $100k+ college · 50-64 F $30–50k no-college · 50-64 F $50–75k college ·
50-64 F <$30k no-college · 50-64 M $100k+ college.

## 4. Privacy limitations and design audit

- **What is sent.** Only:
  - a four-field coarsened demographic cell (age band, sex, income band, 3-level education);
  - the public scenario text.

  No participant ID, actual answer, free text, psychological score or values profile is ever sent. A test asserts
  this for all 80 tasks.
- **Small-cell disclosure.** Every cell sent has k ≥ 5 in the full public panel. Cells with k < 5 are never sent. The
  pilot cells are the *largest* cells, so disclosure risk is lowest here. Residual risk:
  - The panel is public (CC BY 4.0), so a cell reveals no more than the public data already does.
  - The prompt does not reveal *who* in the cell answered what, because outcomes stay local.
  - OpenRouter and the upstream provider see the cell text, and their retention policies apply.
- **Cell weighting.**
  - **Primary estimate:** participant-weighted. A cell's weight is the number of training participants in it, which
    represents the training sample.
  - **Secondary estimate:** cell-weighted, where every demographic profile counts equally.
  - Model and human contrasts always use the **same** cells and the **same** weights.
  - The pilot covers 10 cells (138 training participants), not the whole training sample.
- **Repeated stochastic predictions.** These are averaged within each (cell, condition) as the mean elicited `p`.
  - **Primary measure:** mean `p`.
  - **Secondary measure:** the share of `choice` = A.
  - The bootstrap resamples the samples within each cell, so the sampling noise from temperature is carried into the
    confidence interval and never treated as extra participants.
- **Resampling unit.** A two-stage cluster bootstrap:
  1. resample cells;
  2. within each cell, resample LLM samples and human participants.

  The reason: the model answers per cell, so cells are the independent units, and humans are nested within cells.
- **Why the simulated contrast is not a causal effect in humans.** The model contrast is the difference in the
  model's output when one sentence of the prompt changes. It is a property of the model under prompt manipulation.
  It is not an estimate of what defaults do to people, for three reasons:
  - the model was not randomised to conditions in the way people were;
  - its answers in the two conditions come from the same model, so they are not independent units;
  - agreement with the human contrast is an empirical fact about this model, prompt and cell set, and it may not
    transfer to other scenarios.

  The human contrast (randomised) is the causal benchmark. The model contrast is a prediction that is scored against it.

## 5. Why 80 calls rather than the planned 2,100

The 2,100-call plan in `COST_AND_RUN_PLAN.md` was sized to estimate cell-level contrasts for the full training
population across three arms with several samples each. That is an *inference* run. A pilot only has to establish
**feasibility**:
- the JSON validity rate;
- latency and rate-limit behaviour;
- actual tokens and cost compared with the estimate;
- that `p` is not degenerate (for example, always 0.5);
- that the analysis pipeline runs end to end on real output.

80 calls with 3–10 samples per condition are enough for all of these.

80 calls are **not** enough to measure agreement with the human contrast precisely. On the pilot cells the human
contrast is +0.240 with a 95% CI of −0.013 to 0.498, because of human sampling noise in 138 people. The pilot must
not be reported as a validity result.

The condition-blind arm is deferred to the full run.

## 6. Analysis commands (no API calls)

```bash
python research_frontier/overnight/analyze_pilot.py research_frontier/overnight/runs/live/pilot__openai__gpt-4.1
```

The analysis writes `analysis.json` in the run folder. It reports:
- validity and failure counts;
- green-choice rates by default condition;
- the model-implied default contrast, weighted by participant and by cell, on both the `p` and choice scales;
- the human contrast on the same cells, with absolute and signed error and CIs;
- individual-level Brier score and accuracy for matched participants only;
- the published GPT-4.1 results, both on the same cells and for all training participants.

These are the published reference values on all training participants, with a human contrast of +0.217:

| Published specification | Default contrast |
|---|---|
| Empty persona | +0.874 |
| Demographics-only, T 0.7 | +0.111 |
| Demographics-only, T 0 | +0.142 |
| Full persona | +0.084 |

**Already verified offline.** The dry-run batch scored 80/80 valid. The published contrasts reproduce
`results/benchmark_audit_default_effect.csv` to within 1e-4.

## 7. Stop/go criteria for scaling beyond the pilot

**Stop and diagnose** (do not scale) if any of these occurs:
- the valid-JSON rate is below 98%. The harness also stops on its own if more than 2% of calls are invalid after 50 calls;
- actual spend is more than 2× the estimate, or any budget stop fires;
- more than 10% of calls end in persistent errors after retries;
- `p` is degenerate: for example, more than 90% of values are identical, or `p` and `choice` disagree on more than
  20% of calls;
- the empty-arm green-default rate or grey-default rate is outside [0, 1] after parsing, or any prompt in
  `cache.jsonl` contains anything other than the cell and scenario.

**Go to the full pre-registered run** (a separate authorization) only if all of the stop criteria pass. Then:
- re-run `plan` without `--pilot` and present the exact call count and cost;
- obtain a new budget approval.

**Agreement with the human contrast is not a go criterion.** It is the question the full run answers.

## 8. Tests

```bash
python -m pytest -q research_frontier/overnight/tests
```
```bash
python -m pytest -q tests
```
