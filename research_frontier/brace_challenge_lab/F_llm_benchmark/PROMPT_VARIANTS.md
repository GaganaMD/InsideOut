# Prompt variants for C vs D vs narrative (prepared, NOT run)

Module: `prompt_variants.py` (new; harness code unchanged). Variant template hash **`4c1d7afbed1000bf`** (any wording change
changes the hash and therefore every cache key). Dry-run output: `results/prompt_variants_dryrun.json` and
`results/prompt_variants_dryrun_stdout.txt`. No network call is made by the module; its pipeline check uses an
offline `FakeTransport` that returns schema-valid placeholders (not model output).

**Blocker.** OpenRouter path blocked (expired key); open-weight path on Modal handled in `F2_modal_open_weight/` — a
DIFFERENT model family, never to be substituted for GPT-4.1 results. The variants are model-agnostic (`--model`), so
F2 can render identical prompts; its results must be reported as a separate model family.

## 1. The three formats (one fixed template, only the profile block changes)

| Format | Condition | Profile block |
|---|---|---|
| `demo` | C (our version) | 4 coarsened census fields of a k-anonymous cell: age band, sex, household income band, education (college / no college) |
| `demo_stat` | D | `demo` + estimated inner-layer profile as numbers: for each of 6 constructs, typical value, population percentile, 80% band |
| `demo_narr` | D-narrative | `demo` + the **same numbers** written as prose. `checks()` asserts that the multiset of numbers in `demo_stat` and `demo_narr` is identical for every prompt (776 prompt groups in the full design) |

Fixed elements: system message (identical to the overnight harness), scenario wording from the survey files
(default_eric: harness `SCENARIOS`; targeting_fairness: QID1459/QID1460 text, condition coded from `Segment`),
temperature 0.7, default model `openai/gpt-4.1`, max output tokens 40 (binary) / 120 (rating).

**Probability elicitation.**
- default_eric: `{"choice": "A|B", "p": P(option A = renewable)}` (same schema as the harness).
- targeting_fairness: `{"rating": 1-9, "probs": [9 probabilities]}`; the parser rejects sums outside 1 +/- 0.02 and
  renormalises; the expected rating is the primary prediction, the probability vector gives a full predicted
  distribution (so distributional fidelity can be scored without rounding).

**How the estimated profile is built (statistical, no individual data).**
- Source: TRAINING participants who are **not** in the scored study sample (default_eric: n = 1014;
  targeting_fairness: n = 1182), so no scored person's own attitudes enter any prompt.
- Model: ridge regression (penalty by internal CV) of each construct on the one-hot 4 cell fields; the cell value is
  the model prediction (a model-based group mean, comparable in spirit to the persona generator's shrunk means).
- 80% band = estimate +/- 1.2816 x residual SD (model-based, not empirical percentiles of cell members, so small
  cells reveal nothing about individuals). Percentile = share of the profile-source people strictly below the
  estimate (ties make discrete scales look low, e.g. generosity, where many people give exactly 40-50%).
- Scores use the corrected scoring (`load_people(corrected=True)`).
- Important design point: the D profile is a deterministic function of the same 4 fields as C. **D therefore adds no
  new information about the person; it tests whether making the statistical consequences of demographics explicit
  changes the LLM's predictions.** A gain of D over C would show the LLM under-uses demographic information; no gain
  would mean the prior negative result for demographic personas is not a prompting artefact.

## 2. Rendered examples (from the dry run; pilot cell 1)

### default_eric, `demo`
```
===== default_eric | demo | green_default | 30-49 | Male | $100,000 or more | college degree =====
[system]
You simulate how a person with the described characteristics would answer a survey question. Answer as that person would, not as an expert. Respond with JSON only.
[user]
Person:
- age: 30-49
- sex: Male
- household income: $100,000 or more
- education: college degree

Scenario:
Imagine you have to relocate to another town. After you move into your new flat, you receive a letter from the electric power supplier, GreenGrid. You are told that by moving into your new flat you became a GreenGrid customer. GreenGrid sells clean electricity, generated from renewable energy sources. Your monthly premium is $39. Some weeks later you find a flyer from the electric power supplier Twon: you can easily switch, and Twon's low-priced tariff costs $32 per month.

Question: Which electricity supplier do you choose?
Options:
A: GreenGrid: renewable electricity, $39 per month
B: Twon: standard electricity, $32 per month

Reply with exactly this JSON and nothing else: {"choice": "<one of A | B>", "p": <your probability, 0-1, that this person picks option A>}
```

### default_eric, `demo_stat`
```
===== default_eric | demo_stat | green_default | 30-49 | Male | $100,000 or more | college degree =====
[system]
You simulate how a person with the described characteristics would answer a survey question. Answer as that person would, not as an expert. Respond with JSON only.
[user]
Person:
- age: 30-49
- sex: Male
- household income: $100,000 or more
- education: college degree

Estimated profile of people with these characteristics (a statistical estimate from a survey of US adults, not this person's own answers). Typical value; percentile among US adults; range covering 80% of similar people:
- green (pro-environmental) values (1-5 scale, higher = stronger pro-environmental values): 3.5; 45th percentile; 2.3 to 4.8
- neuroticism (1-5 scale, higher = more anxious and emotionally reactive): 2.6; 44th percentile; 1.4 to 3.7
- social desirability (0-13 scale, higher = stronger tendency to present oneself favourably): 6; 42nd percentile; 1 to 10
- spending style (4-26 scale, 4 = strong tightwad, 26 = strong spendthrift): 14; 51st percentile; 9 to 20
- cognitive reflection (0-4 correct answers on a reasoning test): 2.4; 46th percentile; 1.0 to 3.9
- generosity (share of a hypothetical $5 given to a stranger, 0-100%): 39; 16th percentile; 15 to 62

Scenario:
Imagine you have to relocate to another town. After you move into your new flat, you receive a letter from the electric power supplier, GreenGrid. You are told that by moving into your new flat you became a GreenGrid customer. GreenGrid sells clean electricity, generated from renewable energy sources. Your monthly premium is $39. Some weeks later you find a flyer from the electric power supplier Twon: you can easily switch, and Twon's low-priced tariff costs $32 per month.

Question: Which electricity supplier do you choose?
Options:
A: GreenGrid: renewable electricity, $39 per month
B: Twon: standard electricity, $32 per month

Reply with exactly this JSON and nothing else: {"choice": "<one of A | B>", "p": <your probability, 0-1, that this person picks option A>}
```

### default_eric, `demo_narr`
```
===== default_eric | demo_narr | green_default | 30-49 | Male | $100,000 or more | college degree =====
[system]
You simulate how a person with the described characteristics would answer a survey question. Answer as that person would, not as an expert. Respond with JSON only.
[user]
Person:
- age: 30-49
- sex: Male
- household income: $100,000 or more
- education: college degree

About people like this person (a statistical estimate from a survey of US adults, not this person's own answers):
On green (pro-environmental) values (1-5 scale, higher = stronger pro-environmental values) they typically score 3.5, around the 45th percentile of US adults, and 80% of similar people fall between 2.3 and 4.8. On neuroticism (1-5 scale, higher = more anxious and emotionally reactive) they typically score 2.6, around the 44th percentile of US adults, and 80% of similar people fall between 1.4 and 3.7. On social desirability (0-13 scale, higher = stronger tendency to present oneself favourably) they typically score 6, around the 42nd percentile of US adults, and 80% of similar people fall between 1 and 10. On spending style (4-26 scale, 4 = strong tightwad, 26 = strong spendthrift) they typically score 14, around the 51st percentile of US adults, and 80% of similar people fall between 9 and 20. On cognitive reflection (0-4 correct answers on a reasoning test) they typically score 2.4, around the 46th percentile of US adults, and 80% of similar people fall between 1.0 and 3.9. On generosity (share of a hypothetical $5 given to a stranger, 0-100%) they typically score 39, around the 16th percentile of US adults, and 80% of similar people fall between 15 and 62.

Scenario:
Imagine you have to relocate to another town. After you move into your new flat, you receive a letter from the electric power supplier, GreenGrid. You are told that by moving into your new flat you became a GreenGrid customer. GreenGrid sells clean electricity, generated from renewable energy sources. Your monthly premium is $39. Some weeks later you find a flyer from the electric power supplier Twon: you can easily switch, and Twon's low-priced tariff costs $32 per month.

Question: Which electricity supplier do you choose?
Options:
A: GreenGrid: renewable electricity, $39 per month
B: Twon: standard electricity, $32 per month

Reply with exactly this JSON and nothing else: {"choice": "<one of A | B>", "p": <your probability, 0-1, that this person picks option A>}
```

### targeting_fairness, `demo_stat` (rating format)
```
===== targeting_fairness | demo_stat | targeted_women | 50-64 | Male | $100,000 or more | college degree =====
[system]
You simulate how a person with the described characteristics would answer a survey question. Answer as that person would, not as an expert. Respond with JSON only.
[user]
Person:
- age: 50-64
- sex: Male
- household income: $100,000 or more
- education: college degree

Estimated profile of people with these characteristics (a statistical estimate from a survey of US adults, not this person's own answers). Typical value; percentile among US adults; range covering 80% of similar people:
- green (pro-environmental) values (1-5 scale, higher = stronger pro-environmental values): 3.6; 46th percentile; 2.4 to 4.9
- neuroticism (1-5 scale, higher = more anxious and emotionally reactive): 2.1; 31st percentile; 1.0 to 3.3
- social desirability (0-13 scale, higher = stronger tendency to present oneself favourably): 7; 54th percentile; 2 to 11
- spending style (4-26 scale, 4 = strong tightwad, 26 = strong spendthrift): 14; 45th percentile; 8 to 19
- cognitive reflection (0-4 correct answers on a reasoning test): 2.5; 46th percentile; 1.0 to 3.9
- generosity (share of a hypothetical $5 given to a stranger, 0-100%): 37; 16th percentile; 14 to 60

Scenario:
A snack foods company has developed a new line of snacks. Initial testing showed that, due to the taste and texture profile of the snacks, the snacks are better suited to the preferences of their female customers. The company is developing a marketing plan to promote the snacks. Because they believe the snacks are best suited to their female customers, they will advertise the snacks to women directly.

Question: How fair is this advertising plan?
Answer on a scale from 1 (not at all fair) to 9 (very fair).

Reply with exactly this JSON and nothing else: {"rating": <integer 1-9, this person's most likely answer>, "probs": [<9 probabilities for answers 1..9, summing to 1>]}
```

## 3. Privacy (tier 1 in `overnight/PRIVACY_AND_PERMISSIONS.md`)
- Only k >= 5 cells (counted in the full 2,058 panel) are rendered; cells present in only one condition are skipped.
- Never rendered: participant IDs, outcomes, free text, individual scale scores. Asserted for every task.
- The estimated profile is an aggregate model output. The privacy document lists a disposition arm as tier 1 only
  "as a coarse bin inside cells that stay k >= 5"; these model-based cell means satisfy that in my reading, but the
  project owner must confirm this explicitly before a live run (the D arm was excluded from the earlier pilot).

## 4. Counts and cost (GPT-4.1, `pricing_snapshot.json` 2026-11-14, upper bound = output cap on every call)

| Design | Cells/study | Samples | Calls | Est. input tokens | Upper-bound cost |
|---|---|---|---|---|---|
| Pilot | 6 largest cells present in both conditions | 3 | 216 | 106,448 | **$0.35** (default_eric $0.14, fairness $0.21) |
| Full | all k>=5 cells in both conditions: default_eric 56 cells (384 of 428 people), fairness 41 cells (210 of 260) | 4 | 2328 | 1,151,140 | **$3.68** |

Pilot task keys are a subset of the full design's keys (same cell, format, condition, sample index), so a cached
pilot is never paid for twice: total worst case **<= $3.68 < $5**. Calls = 3 formats x 2 conditions x cells x samples.
Pilot fake-transport check: 216 calls, 0 invalid, no budget stop.
