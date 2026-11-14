# COST_AND_RUN_PLAN

## Prices
- **Source:** OpenRouter's public models API (`https://openrouter.ai/api/v1/models`), fetched **2026-11-14 17:09 UTC**.
- **Snapshot file:** `overnight/pricing_snapshot.json`.
- **Re-check immediately before any paid run:** the CLI refuses models not in the snapshot.

| Model | Input $/M tokens | Output $/M tokens |
|---|---|---|
| openai/gpt-4.1 | 2.00 | 8.00 |
| openai/gpt-4.1-mini | 0.40 | 1.60 |
| openai/gpt-4.1-nano | 0.10 | 0.40 |
| openai/gpt-4o-mini | 0.15 | 0.60 |
| google/gemini-2.5-flash | 0.30 | 2.50 |
| deepseek/deepseek-chat-v3.1 | 0.25 | 0.95 |
| meta-llama/llama-3.3-70b-instruct | 0.71 | 0.71 |

## Cost matrix
**Assumptions:** about 272 prompt tokens per call, measured from the real rendered prompts by `harness.cli plan`. Output is capped at 40 tokens and costed at the cap, so these are **upper bounds**; real JSON replies are about 15 tokens.

| Run | Scope | Calls | Estimated cost |
|---|---|---|---|
| **Pilot** | `default_eric`, arms E/D/B, 77 cells × 2 conditions, 10 samples, de-duplicated by cache key | **2,100 per model (exact, from `plan`)** | GPT-4.1-mini **$0.36**; GPT-4.1 **$1.82**; Gemini 2.5 Flash $0.38; DeepSeek v3.1 $0.22 |
| Medium | + targeting_fairness + context_effects; 3 models (GPT-4.1-mini, GPT-4.1, Gemini 2.5 Flash), 10 samples | ≈ 20,000 per model, upper bound | ≈ **$24** total (GPT-4.1 ≈ $17) |
| Full | 3 studies, 4 models, 20 samples, including the disposition arm (if authorised) | ≈ 74,000 per model, upper bound | ≈ **$98** total (GPT-4.1 ≈ $64) |

Medium and full counts come from a formula, not the tested task builder: the two extra studies' builders don't exist yet. They over-count the condition-blind arm, which de-duplicates in practice.

## Run commands (from `research_frontier/overnight/`)
```bash
python -m pytest -q tests
python -m harness.cli plan    --model openai/gpt-4.1-mini --samples 10
python -m harness.cli dry-run --model openai/gpt-4.1-mini --samples 10
python -m harness.cli live    --model openai/gpt-4.1-mini --samples 10 --budget 1 --workers 4 --rpm 60 --confirm "I have authorization to send k-anonymous demographic cells to OpenRouter"
```
- `pytest` runs the harness tests (mock API, no network).
- `plan` prints the exact call count and cost estimate.
- `dry-run` exercises the full pipeline offline, with resume.
- `live` needs `OPENROUTER_API_KEY` in the environment.

**Runtime:** at 60 requests per minute the pilot is about 35 minutes per model. Raise `--rpm` only within the provider's limits.

**Resume:** re-running the same command skips every cached valid result. `runs/<mode>/<model>/summary.json` holds calls, tokens, spend and the stop reason.

**Not yet implemented:**
- the analysis script that turns `cache.jsonl` into the plan's metrics (`analyze_pilot.py`), required before results are interpreted, not before the pilot runs;
- task builders for targeting_fairness and context_effects.
