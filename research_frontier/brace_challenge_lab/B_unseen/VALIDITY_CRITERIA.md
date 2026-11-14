# Workstream B: validity criteria for unseen-group personas

**Written:** 2026-11-14 23:51 IST. Written before any of the 25 stress-test groups was run and before any
held-out member of those groups was looked at. The thresholds below are fixed. They were not changed after the results came in.

**Object under test:** the frozen generator `src/personas.py build` (corrected scores, which is the default). Its logic is not modified.
The held-out numbers in this workstream are labelled **"held-out evaluation of frozen generator"**. They are used only
to describe how the generator behaves. They are never used to tune it, select from it or change it.

## 1. What counts as a valid persona

A persona for a group G is **valid** when all of these hold:

1. The criteria are well-formed. Every variable is Tier A, every level exists exactly as spelled, and no variable is given twice.
   The generator either builds a profile or refuses with a non-zero exit and a message that names the problem.
2. The membership the generator reports (`n_total`, `n_train`, `n_test`) matches an independent recount from
   `data/processed/outer.parquet` and `data/split.csv`, using the criteria **as the user meant them**.
3. `n_train ≥ 60`. Between 30 and 59 the profile is reported but carries a warning.
4. G is not effectively the whole population: share of the panel < 0.90.
5. No construct carries a confidence label (*distinct* or *weak*) that the reported "Typical" value contradicts (see T9).
6. The green-choice behaviour estimates are only shown when each default-condition cell has n ≥ 20, which is the generator's own rule.
7. The run exits cleanly. Any Python traceback counts as an error.

## 2. Abstention triggers (the generator SHOULD refuse or withhold a profile)

| ID | Trigger | Expected generator behaviour | If it does not happen |
|---|---|---|---|
| A1 | Unknown variable (not in Tier A) | exit 2, message names the variable | silent acceptance = CRITICAL |
| A2 | Non-Tier-A survey variable (party, ideology) without `--allow-party` | exit 2 | acceptance = CRITICAL |
| A3 | Misspelled or unknown level, including case or whitespace variants | exit 2, valid levels listed | silent mapping or acceptance = HIGH |
| A4 | Same variable given twice (`sex=Male; sex=Female`), i.e. contradictory criteria | exit 2, or empty group, or explicit warning | silently keeping only one clause = CRITICAL (silent wrong output) |
| A5 | Empty intersection (n_total = 0) | INSUFFICIENT EVIDENCE, no profile | any profile = CRITICAL |
| A6 | n_train < 30 | INSUFFICIENT EVIDENCE (generator rule MIN_N_TRAIN = 30) | profile shown = HIGH |
| A7 | Malformed syntax (no `=`, empty level, trailing `|`) | exit 2 | traceback = MEDIUM; silent acceptance = HIGH |
| A8 | Behaviour cell n < 20 per condition | that cell reported as INSUFFICIENT EVIDENCE (generator rule) | rate shown as a finding = HIGH |

## 3. Warning triggers (profile allowed, but the live answer must caveat it)

| ID | Trigger (fixed threshold) | Why |
|---|---|---|
| T1 | 30 ≤ n_train < 60 | Mean CIs are about ±0.25 SD or wider |
| T2 | n_test < 20: held-out evaluation **not evaluable**. 20 ≤ n_test < 40: evaluable but imprecise | We cannot check the persona |
| T3 | Share of panel ≥ 0.90 | d ≈ 0 by construction, so the persona is just the population |
| T4 | Any level used has fewer than 30 people in the full panel (e.g. `Pacific (HI, AK)` n = 16, `citizen=No` n = 4, `Less than high school` n = 17) | Rare category, so cells cannot be supported |
| T5 | Heavy shrinkage: weight w < 0.5 on a construct the generator labels *distinct* or *weak* | The headline number and the label disagree |
| T6 | 95% CI of the raw mean wider than 25% of the scale range | The estimate is uninformative |
| T7 | Typical p10–p90 member range covers ≥ 80% of the scale range | "Typical member" language is empty |
| T8 | Behaviour cell 20 ≤ n < 40 (Wilson CI half-width usually > 0.13) | Behaviour claim is fragile |
| T9 | Label/estimate inconsistency: label *distinct* but the shrunken Typical is less than 0.10 pop-SD from the population mean, or Typical lies outside the raw-mean 95% CI | Contradictory output |
| T10 | Group overlaps strongly with an already-reported persona or criterion (e.g. a level that implies another variable) | Redundant or overlapping criteria |
| T11 | Held-out sign flip: construct labelled *distinct* on train, held-out d has the opposite sign and \|held-out d\| ≥ 0.10, with n_test ≥ 20 | Non-replication |
| T12 | Held-out 80% interval coverage < 0.65 (n_test ≥ 30, continuous constructs only) | Miscalibrated spread |

## 4. Held-out evaluation rules (pure evaluation; nothing is tuned)

- Prediction for a held-out member = the generator's `typical_shrunk`. The baseline is the train population mean, as in `src/holdout.py`.
- **MAE gain** = 100 × (MAE_pop − MAE_persona) / MAE_pop. It is reported only if n_test ≥ 20.
- **Held-out d** = (test-member mean − train population mean) / train population SD. It is reported only if n_test ≥ 20.
- **80% coverage** = share of held-out members inside the generator's p10–p90. It is reported only if n_test ≥ 30
  **and** the construct has ≥ 10 distinct observed values in the panel. CRT (0–4, 5 values) is excluded because quantile
  intervals on a 5-point integer scale have lumpy, non-nominal coverage. Any other construct that fails the ≥ 10 rule is excluded too.
- Behaviour is not evaluated on held-out members. The cells are too small for nearly all new groups.

## 5. Verdict rules

- **valid**: status ok, all of section 1 holds, and no T-trigger fires except T2 (lack of test data alone does not
  invalidate a training-built persona; it only means it is unchecked).
- **warn**: status ok but at least one of T1, T3–T12 fires.
- **abstain**: the generator refused (exit 2) or returned INSUFFICIENT EVIDENCE. This is the **correct** outcome for A1–A7 cases.
- **error**: a traceback or crash, or a **silent wrong output**: exit 0 with a profile whose membership does not match the
  user's stated criteria (A4), or a profile for a case that should have been refused.

## 6. Severity scale for failures

- **CRITICAL**: a silent wrong answer that a live reviewer would not spot from the output alone.
- **HIGH**: a misleading claim that is visible in the output but stated with unwarranted confidence.
- **MEDIUM**: a crash or unhelpful refusal on reasonable input.
- **LOW**: a cosmetic or documentation issue.
