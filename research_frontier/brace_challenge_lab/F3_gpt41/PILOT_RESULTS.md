# GPT-4.1 pilot: feasibility results (2026-11-15; no accuracy claims)

## Run record

| | |
|---|---|
| Command | `python -m harness.cli live --experiment green_profiles --pilot --budget 1 --confirm "…"`, run from `research_frontier/overnight/` |
| Time | 03:03:52 to 03:08:16 UTC |
| Code | committed before the run (`8f80948`); pre-flight 11/11 passed on the exact payloads |
| Calls | 264 attempted, **264 valid (100%)**: 0 invalid, 0 errors, 0 retries, no budget stop |
| Tokens | 89,347 prompt, 3,960 completion |
| **Actual cost** | **$0.2104**. Computed and OpenRouter-billed cost agree. Estimate was ≤ $0.31; cap $1. |
| Served model / provider | `openai/gpt-4.1` / OpenAI. OpenRouter returns the alias only. The catalogue maps it to `gpt-4.1-2025-04-14`, but the underlying snapshot cannot be verified from the responses and may differ from Peng et al.'s runs. |
| Key status before the run | Valid; $10 limit, $0 used. Checked without inference. |

## Pre-registered go criteria

| Criterion | Result | Pass |
|---|---|---|
| Valid JSON ≥ 98% | 100% | ✅ |
| Cost ≤ 2× the estimate and ≤ $1 | $0.21 | ✅ |
| Re-ask mean \|Δp\| ≤ 0.10 | 0.032 (n = 20) | ✅ |
| Re-ask same choice ≥ 90% | 90% (18/20) | ✅ (at the threshold) |
| Choice consistent with p | 100% | ✅ |
| p not degenerate | SD 0.23; modal value 11% | ✅ |
| Served model is GPT-4.1 | yes (alias) | ✅ |

**Verdict: GO, meaning it is feasible to propose the full run.** The full run needs **separate authorization**:
- 1,556 calls, of which the 264 pilot calls are cached and not paid again;
- estimated cost ≤ $1.82;
- cumulative cap $5.

## Descriptive only (pilot cells; not evidence about accuracy)
- **Order sensitivity:** mean |P(green with green as A) − P(green with green as B)| is 0.036, signed +0.019. This is small. For comparison, Qwen2.5-7B was 0.51, though that is a different elicitation method and a different model.
- **Mean P(green), green default vs grey default:**

  | Format | Green default | Grey default |
  |---|---|---|
  | empty | 0.75 | 0.75 |
  | demographics | 0.37 | 0.30 |
  | profile | 0.38 | 0.32 |
  | narrative | 0.40 | 0.32 |

  These are 12 cells only. No comparison with humans or baselines is made from the pilot. That is the pre-registered full analysis.

## Notes for the full run
- **Re-ask agreement:** it sat exactly at the 90% threshold. The full run's 32 re-asks will be reported as well.
- **Elicitation:** the elicited p is a stated probability, not a token likelihood. Calibration will be judged empirically against the baselines.
