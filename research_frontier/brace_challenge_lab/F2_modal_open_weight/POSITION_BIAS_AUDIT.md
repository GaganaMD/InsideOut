# Audit of the Qwen position-bias figure (offline; saved outputs only; no new inference)

## Checks
1. **Option-token mapping.**
   - `modal_llm.py` reads the probabilities of the token IDs from `tok.encode("A")` and `tok.encode("B")`, and asserts each is a single token.
   - The top next token was only ever "A" or "B", across all 3,048 scored prompts (both models).
2. **Option-to-letter mapping.** It was re-derived from the prompt text itself: green is A exactly when "A: GreenGrid" appears in the prompt. This agrees with the `order` field for all 1,524 prompts. `test_f2.py` checks the same thing.
3. **Normalization.** `p_green = P(letter carrying green) / (P(A) + P(B))`. The A + B mass is at least 0.99997 for every prompt, so renormalising changes values by less than 3e-5.
4. **Averaging.** The two orders are averaged with equal weight on the probability scale. Every (format, condition, cell, fold) key has exactly one AB and one BA prompt (762 pairs per model).

## What "0.51" measures
`order_gap_mean_abs` = mean over pairs of |p_green(green shown as A) − p_green(green shown as B)|. This is **absolute order sensitivity**. It ignores direction.

The direction, recomputed independently:

| Model | Mean \|gap\| | Signed gap (+ = favours letter A) | Mean P(letter A) | Pairs where the same letter wins in both orders |
|---|---|---|---|---|
| Qwen2.5-7B | 0.507 | **−0.472** | 0.264 | 57% |
| Qwen3-4B | 0.124 | −0.121 | 0.440 | 13% |

The signed gap is almost as large as the absolute gap, so the sensitivity is **almost entirely directional**. Qwen2.5 systematically prefers the **second option, letter B**. In 57% of answer pairs it picks the same letter whichever option that letter carries; the content does not decide.

**By format, Qwen2.5 mean |gap|:**

| Format | Mean \|gap\| |
|---|---|
| empty | 0.62 |
| profile | 0.61 |
| narrative | 0.56 |
| demographics | 0.20 |

## Implications
- The reported figure is correct, but should be described as "mean absolute order sensitivity 0.51, mostly a directional preference for option B", not as a generic "bias" of unspecified sign.
- **Counterbalancing removes a constant letter preference only on average.** With a preference this strong, the averaged probabilities are pulled toward the middle. This is one reason the averaged LLM predictions are poorly calibrated (slopes 0.02–0.07 for persona formats). It does not make the LLM conditions look artificially *worse* than the baselines in a way that changes the decision: the no-persona Qwen2.5 average still ties the baselines. That tie should not be read as support: it averages four order-dependent prompts (0.27 / 0.94 and 0.56 / 0.00).
- The pre-registered conclusions are unchanged. A single-order LLM survey with this model would be dominated by option position.
