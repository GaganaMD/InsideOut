# Live challenges: one constraint changes

**Rules.**
- Every new computation uses the **training split only**, with corrected SD and CRT scores (the CLI default). The test split is not read for any new analysis.
- `src/` is not modified.
- The helper `D_review/live_helpers.py` drops test rows immediately after loading. It imports `src/common.py` read-only.
- Outputs from this rehearsal are in `D_review/cli_outputs/`. Commands were run from the repository root in Git Bash.
- Numbers marked **RUN** were obtained in this session. Nothing here is a benchmark result.

Setup (once):
```bash
cd brace-personas
export PYTHONUTF8=1
O=research_frontier/brace_challenge_lab/D_review/cli_outputs
H=research_frontier/brace_challenge_lab/D_review/live_helpers.py
python src/personas.py list-levels        # exact level strings; region levels embed state lists
```

Live hygiene for every CLI call:
- Read the **"Outer-layer definition"** line and n back to the reviewer before interpreting anything. A repeated variable is silently overwritten (`sex=Male; sex=Female` profiles all women, exit 0).
- Use `|` inside one clause, never the same variable twice.
- Cost: each CLI build took **2.3–2.7 s** (RUN, 8 timed builds). The helper analyses took 1–3 min each.

---

## (a) Remove age as a predictor

**What changes.** Age is the main thing census data "sees" (age alone: neuroticism R² 0.074 of 0.151). Without it, does the outer→inner signal vanish, or does age leak back in through proxies (retired, student, widowed, never married)?

**Commands**
```bash
python $H noage                                                          # ridge CV R², with vs without age_band
python src/personas.py build --name a_retired --criteria "employment=Retired" --out $O
python src/personas.py build --name a_lowincome_allages --criteria 'income=Less than $30,000|$30,000-$50,000' --out $O
```

**Expected qualitatively.** Neuroticism R² falls but does not collapse, because employment and marital status proxy age. Values stay near zero either way. A "retired" persona reproduces most of P1. Income alone gives a much weaker neuroticism shift than P2, because P2's shift is half age.

**RUN results** (`cli_outputs/helper_noage.txt`, train n = 1,442)

| Construct | Full Tier A | Tier A minus age | Age only |
|---|---|---|---|
| Neuroticism | 0.151 (0.121, 0.181) | **0.117** (0.093, 0.142) | 0.074 |
| Social desirability | 0.062 (0.042, 0.083) | **0.040** (0.024, 0.056) | 0.038 |
| Green values | 0.023 | 0.023 | 0.001 |
| Spendthrift | 0.037 | 0.038 | −0.001 |
| CRT | 0.006 | 0.007 | −0.001 |
| Dictator giving | 0.002 | 0.002 | 0.000 |

- **Age leaks back.** The age-band index is predicted from the other 9 Tier A variables with CV R² **0.455** (0.423, 0.488). Removing the age column does not remove age information.
- **`employment=Retired`** (171 train): neuroticism d **−0.40** (−0.54, −0.27), SD **+0.30** (+0.16, +0.45), both "distinct". Green values −0.01. Compare P1 (65+): −0.43 / +0.39. The proxy reproduces P1.
- **Low income at all ages** (538 train): neuroticism only **+0.18** (+0.09, +0.27), "weak". P2 (18–49 and low income) is +0.47. Green −0.05, not distinguishable.

**Line for the room.** "Dropping age costs about a fifth of neuroticism's predictability and a third of SD's, because employment and marital status carry age. Values were never age-driven, so nothing changes there. If the reason for removing age is fairness or compliance, proxies defeat it."

---

## (b) Require a minimum persona sample size

**What changes.** `MIN_N_TRAIN = 30` is hard-coded in `src/personas.py`. Don't edit it. Instead, show what the threshold *should* be, and filter CLI output by n.

**Commands**
```bash
python $H minn          # nested train-only replication of "distinct" labels by group size (20 inner 70/30 splits)
# Size of any CLI group: line 4 of its report
python src/personas.py build --name b_check --criteria "<criteria>" --out $O && sed -n 4p $O/b_check.md
```
Rule of thumb, no code needed: the CI half-width of d is about 1.96/√n, so n = 30 → ±0.36, n = 100 → ±0.20, n = 400 → ±0.10.

**Expected qualitatively.** Small groups get more "distinct" labels with bigger d (selection on noise), replicate less often, and shrink more toward zero in fresh data.

**RUN results** (`cli_outputs/helper_minn.txt`). Groups are every 1- and 2-level Tier A conjunction with ≥ 30 train members. A label replicates if inner-validation d has the same sign and |d| ≥ 0.10.

| Inner-train n | "Distinct" labels (pooled over 20 splits) | Replicated | Median \|d\| (train) | Median d_val / d_train |
|---|---|---|---|---|
| 20–29 | 1,492 | 64.8% | 0.46 | 0.46 |
| 30–59 | 3,955 | 66.4% | 0.38 | 0.57 |
| 60–99 | 2,714 | 69.5% | 0.29 | 0.65 |
| 100–199 | 1,910 | 75.0% | 0.27 | 0.75 |
| 200+ | 259 | 75.3% | 0.23 | 0.79 |

**Caveats.**
- Labels overlap across groups and splits, so they are not independent. Read the trend, not the levels.
- Validation sets are about 0.43× the inner-train size, so some non-replication is validation noise.
- This is the same rule as `B_unseen/nested_training_label_check.csv`, but over all groups.

**Line for the room.** "Below 100, expect a labelled effect to come back about half its size, and roughly a third of labels not to replicate. I'd set 100 for labels, 30–99 for 'exploratory, unlabelled', and under 30 for refusal. The current CLI's 30 is a refusal floor, not a confidence floor."

---

## (c) Only publicly available census fields

**What changes.** A client usually has published census tables, not individual Tier A records. Two consequences:
1. **Fewer fields.** The decennial short form is roughly age, sex, race/ethnicity and household size; income, education, employment, marital status and citizenship come from the sample-based ACS. *This field list is from general knowledge, not from a repository file. Verify it before quoting.*
2. **Marginals, not joint records.** You can describe a geography's mix, not individuals.

**Commands**
```bash
python $H census        # ridge CV R² for field subsets
```

**Expected qualitatively.** Neuroticism loses the income and employment part. SD barely changes (age-driven). Values stay near zero.

**RUN results** (`cli_outputs/helper_census.txt`; CV R², train)

| Construct | Age + sex | Short-form-like (age, sex, race, hh_size) | + region | Full Tier A |
|---|---|---|---|---|
| Neuroticism | 0.089 | 0.098 | 0.095 | **0.151** |
| Social desirability | 0.037 | **0.066** | 0.064 | 0.062 |
| Green values | 0.007 | 0.008 | 0.006 | 0.023 |
| Spendthrift | 0.016 | 0.028 | 0.028 | 0.037 |
| CRT | 0.001 | 0.006 | 0.004 | 0.006 |
| Dictator giving | 0.003 | 0.002 | 0.001 | 0.002 |

- With short-form fields, neuroticism predictability drops by about a third (0.151 → 0.098). SD is unchanged or slightly higher; race and household size help it.
- Green values fall to about 0.01.
- *Not run:* reweighting to real ACS margins. No ACS data are in the repo.

**Line for the room.** "With only published fields you keep most of the age-linked self-presentation signal and lose a third of the temperament signal. You had nothing on values to begin with. And with marginals you can only describe a geography's mix: an ecological, group-level claim, never a person-level one."

---

## (d) A group absent from the training data

**What changes.** Brace names a group that has zero or nearly zero members in the panel, for example non-citizens, Pacific (HI, AK), 18–29 retirees, or a non-US population.

**Commands**
```bash
python src/personas.py build --name d_noncitizen    --criteria "citizen=No" --out $O
python src/personas.py build --name d_retired_18_29 --criteria "age_band=18-29; employment=Retired" --out $O
python src/personas.py build --name d_pacific       --criteria "region=Pacific (HI, AK)" --out $O
python $H absent        # simulate absence: drop each level from training, predict its members from the other variables
```

**Expected qualitatively.** The CLI refuses (INSUFFICIENT EVIDENCE, but exit 0). When a level is truly unseen, a model can only borrow from correlated variables. For age-defined groups it should do *worse* than the population mean.

**RUN results**
- **CLI refusals, all exit 0.**

  | Group | n_train / n_test | Result |
  |---|---|---|
  | `citizen=No` | 4 / 0 | `INSUFFICIENT EVIDENCE: n_train=4 < 30` |
  | `age_band=18-29; employment=Retired` | 0 / 1 | refused |
  | Pacific (HI, AK) | 14 / 2 | refused |

- **Leave-one-level-out simulation** (`cli_outputs/helper_absent.txt`). Ridge is fitted on train rows without level L; members of L are predicted. Errors are in train-SD units.
  - **Age bands absent:** the model is worse than predicting the population mean in 10 of 12 band × construct rows; one ties (50–64 SD) and one is better (50–64 green).
    - 65+ neuroticism: actual −0.43, predicted **+0.10** (wrong sign; error 0.54 vs 0.43).
    - 18–29 neuroticism: actual +0.43, predicted −0.09 (error 0.52 vs 0.43).
  - **When the absent level is a proxy for something the model still sees, transport works.**
    - Students (absent): neuroticism actual +0.37, predicted +0.43 (error 0.06 vs 0.37).
    - Unemployed: actual +0.50, predicted +0.24 (error 0.26 vs 0.50).
  - **Overall,** the model beat the population mean in 34 of 78 level × construct rows: neuroticism 15/26, SD 10/26, green 9/26.

**Line for the room.** "There's no data on this group, so there's no persona. The tool refuses, correctly. If I extrapolated from neighbouring groups, my own simulation says I'd do worse than the population average whenever the missing group is defined by age, and only help when it's a proxy for something the model already sees. For a non-US group, nothing here transfers. I'd field 5–10 domain items with that group."

---

## (e) Outcome changes from attitude prediction to hypothetical choice prediction

**What changes.** Instead of "what is this group's average neuroticism or green values?", the question becomes "will this group pick the $39 renewable tariff?" (Mega-Study `default_eric`, hypothetical, n = 428 train).

**Commands**
```bash
python src/personas.py build --name e_65plus        --criteria "age_band=65+" --out $O        # see the "Behaviour" block
python src/personas.py build --name e_bachelor_plus --criteria "education=College graduate/some postgrad|Postgraduate" --out $O
python $H choice        # out-of-fold Brier: condition vs +personas vs +Tier A vs +green values (5-fold x 20, train only)
```

**Expected qualitatively.** Persona choice rates sit within noise of the population. Demographics add nothing or hurt. One measured attitude helps a lot. The randomised default dominates the group differences.

**RUN results**
- **CLI behaviour blocks** (train). Population: grey default 36% (n = 206), green default 58% (n = 222).
  - 65+: 43% (n = 49) and 55% (n = 40).
  - Graduates: 36% (n = 97) and 57% (n = 121).
  - All within the population CIs.
- **Out-of-fold** (`cli_outputs/helper_choice.txt`; Δ vs condition-only; negative = better; 95% participant bootstrap)

  | Model | Brier | Δ vs condition only |
  |---|---|---|
  | Condition only | 0.2375 | — |
  | + persona membership (P1, P2, P3) | 0.2411 | **+0.0036 (+0.0017, +0.0055)**: worse |
  | + Tier A (L2, C = 1) | 0.2518 | **+0.0144 (+0.0013, +0.0275)**: worse |
  | + green values | 0.2022 | **−0.0353 (−0.0512, −0.0202)**: better |

- Persona members in the experiment (train): P1 89, P2 69, P3 33. P3's cells are 16 and 17, below the 20-per-cell rule.
- Consistent with the frozen exploratory result: M3 vs M1D −0.035 (`reports/exploratory/values_vs_demographics.md`).

**Line for the room.** "Switching from attitudes to choices is where census personas stop working. Adding persona membership makes out-of-fold prediction worse. What moves the choice is the randomised default (+25 points, causal) and a measured green-values scale. And this is a survey vignette, not a purchase."

---

## Not run (say so if asked)
- ACS reweighting or any census-margin raking.
- Any held-out/test-split computation. Prohibited for new analysis.
- Any LLM call, including the open-weight benchmark. Its results are not to be cited.
