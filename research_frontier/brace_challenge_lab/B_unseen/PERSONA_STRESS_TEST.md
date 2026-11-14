# Persona generator stress test: 25 unseen groups (Workstream B)

**Object under test:** the frozen `src/personas.py build` CLI (corrected scores, which is the default), not modified.
**Thresholds:** `VALIDITY_CRITERIA.md`, written 2026-11-14 23:51 IST before any run. One post-hoc addition is labelled below.
**Runner:** `run_unseen_groups.py`. It runs the CLI by subprocess with `--out outputs/`, and logs every stdout and stderr verbatim in `logs/`.
**Per-group data:** `UNSEEN_GROUP_TESTS.csv`. Supplementary malformed-input probes are in `supplementary_probes.csv`.
**Labelling:** every held-out number below is a **held-out evaluation of the frozen generator**. Nothing was tuned or
selected on it. The single proposed fix (section 6) is checked on a training-only nested split and is **not applied**.

## 1. Method

1. I defined 25 groups (`groups.csv`) that do not appear in `config/personas.json`, `reports/generated/`,
   `reports/final_audit/live_review/` or the README example. They cover 4 broad or whole-population groups,
   5 narrow intersections, 4 age-challenging groups, 2 expected-weak groups, 3 rare groups, 3 overlapping groups,
   1 empty intersection, 1 contradictory group and 3 unsupported definitions (plus the party variable).
2. For each group I ran `python src/personas.py build --name <id_name> --criteria "<criteria>" --out outputs/` and recorded
   the exit code, stdout, stderr and wall time.
3. I recounted membership independently from `outer.parquet` and `split.csv`, using the criteria as a user would mean them:
   clauses are ANDed, and a repeated variable intersects its levels.
4. For each profiled group I ran the held-out evaluation of the frozen generator, using the same estimands as `src/holdout.py`:
   - The prediction is the generator's `Typical` (the shrunken mean). The baseline is the train population mean.
   - MAE gain and held-out d are computed when n_test ≥ 20.
   - 80% p10–p90 coverage is computed when n_test ≥ 30 and the construct has ≥ 10 distinct values. CRT and dictator giving never
     qualified. In `train`, CRT has 5 distinct values and dictator giving has 6 (64% of people give exactly 40).
5. Every T-trigger from the validity criteria was checked automatically. The generated markdown was read for misleading text.

**Missingness:** none. All 2,058 participants have all 10 Tier A variables and all 6 constructs (checked after
`load_people(corrected=True)`). Missingness is therefore not a failure mode here. Missing *behaviour* data is: only about 30% of
the panel took `default_eric`, so behaviour cells are small even for mid-sized groups.

## 2. Outcome counts (25 groups)

| Verdict | n | Groups |
|---|---|---|
| valid | 2 | G01 men, G02 married |
| warn | 11 | G03, G04, G07, G08, G09, G12, G13, G14, G17, G18, G19 |
| abstain (correct) | 11 | G05, G06, G10, G11, G15, G16, G20 (INSUFFICIENT EVIDENCE, exit 0); G21, G22, G23, G25 (rejected, exit 2) |
| **error** | **1** | **G24: silent wrong output** |

There were no crashes on the 25 groups. Of the 5 supplementary probes, one crashed: **X3**, where `--name` contains `/`. It raised a
`FileNotFoundError` traceback and exited 1. **X4** (`--name ../X4_traversal_probe`) wrote its files *outside* `--out`.
The other probes behaved correctly. X1 (trailing `|`) and X5 (missing `=`) exited 2 with clear messages. X2 (extra whitespace) was accepted.

## 3. Results table

"Distinct" constructs show: train d (shrink weight w) → held-out d, with MAE gain. n/e = not evaluable (n_test < 20).

| ID | Group | Category | train / test | Generator status | Constructs labelled *distinct* | Verdict |
|---|---|---|---|---|---|---|
| G01 | broad_men | broad | 706 / 308 | ok | none (four "weak difference", \|d\| ≤ 0.14) | valid |
| G02 | broad_married | broad | 570 / 243 | ok | none (neuro −0.18 "weak" → −0.20, gain +2.3%) | valid |
| G03 | age_band = all four levels | whole population | 1442 / 616 | ok | none (d = 0.00 by construction) | warn |
| G04 | citizen=Yes | whole population | 1438 / 616 | ok | none | warn |
| G05 | Black women 30–49 | narrow | 28 / 20 | INSUFFICIENT (28 < 30) | — | abstain |
| G06 | Asian postgraduates | narrow | 25 / 5 | INSUFFICIENT | — | abstain |
| G07 | self-employed men 50+ | narrow | 47 / 27 | ok | spend −0.42 (w 0.36) → −0.47, gain +2.3% | warn |
| G08 | 65+ and income < $30k | age-challenge | 40 / 17 | ok | green +0.45 (w 0.40) → n/e; SD +0.35 (w 0.41) → n/e; **CRT −0.39 (w 0.04)** → n/e | warn |
| G09 | 18–29 and income $100k+ | age-challenge | 58 / 21 | ok | none | warn |
| G10 | 18–29 and married | age-challenge | 26 / 16 | INSUFFICIENT | — | abstain |
| G11 | widowed, under 65 | age-challenge / rare | 29 / 13 | INSUFFICIENT (29 < 30) | — | abstain |
| G12 | divorced/separated, living alone | narrow | 82 / 43 | ok | green +0.25 (w 0.49) → +0.16, gain +4.2%; **CRT −0.28 (w 0.10)** → −0.14, gain −0.2% | warn |
| G13 | home-makers | weak expected | 45 / 21 | ok | neuro +0.71 (w 0.75) → +0.40, gain +14.3% | warn |
| G14 | Midwest, associate degree | weak expected | 32 / 17 | ok | neuro +0.43 (w 0.61) → n/e | warn |
| G15 | Pacific (HI, AK) | rare | 14 / 2 | INSUFFICIENT | — | abstain |
| G16 | less than high school | rare | 14 / 3 | INSUFFICIENT | — | abstain |
| G17 | students | rare / overlap (85% in P3) | 53 / 25 | ok | green −0.32 (w 0.35) → −0.28, gain +2.8%; neuro +0.37 (w 0.79) → +0.73, gain +16.8% | warn |
| G18 | retired and 65+ | overlap (subset of P1) | 98 / 45 | ok | SD +0.43 (w 0.66) → +0.39, gain +10.8%; neuro −0.49 (w 0.84) → −0.43, gain +9.8% | warn |
| G19 | never married, under 50 | overlap (51% in P3) | 387 / 173 | ok | SD −0.22 (w 0.89) → −0.25, gain +2.1%; neuro +0.32 (w 0.95) → +0.39, gain +5.3% | warn |
| G20 | non-citizen and 65+ | empty | 0 / 0 | INSUFFICIENT (n_train = 0) | — | abstain |
| G21 | `occupation=Nurse` | unknown variable | — | exit 2 | — | abstain |
| G22 | `sex=female` | case misspelling | — | exit 2 | — | abstain |
| G23 | `region=South` | abbreviated level | — | exit 2 | — | abstain |
| G24 | `sex=Male; sex=Female` | contradictory | 736 / 308 | **ok (should be empty)** | none | **error** |
| G25 | `party=Democrat` | Tier B | — | exit 2 | — | abstain |

**Replication of *distinct* labels (held-out evaluation of frozen generator).** Ten *distinct* labels had n_test ≥ 20.
All ten kept their sign on held-out members, so no T11 trigger fired. Magnitudes moved a lot in small groups: G13
neuroticism went from +0.71 to +0.40, G17 neuroticism from +0.37 to +0.73, and G12 CRT from −0.28 to −0.14. Four *distinct*
labels (G08 ×3, G14) could not be checked at all.

**Individual-level value.** The MAE gain over the population mean is ≥ 9% only for neuroticism or social desirability
in G13, G17 and G18. Everywhere else it is between −3.4% and +7.3%. **Dictator giving's gain is 0.0% in every group**,
because τ² = 0, so the generator always predicts the population mean.

**80% interval coverage** (n_test ≥ 30, continuous constructs: G01–G04, G12, G18, G19, G24) ranged from 0.67 to 0.89.
The lowest values were G12 spendthrift at 0.67 and G19 neuroticism at 0.70. None fell below the 0.65 trigger, so the
p10–p90 spreads are roughly calibrated where they can be checked.

**Non-distinct constructs that moved a lot on held-out members** (labelled "not distinguishable" on train):
- G09 neuroticism: +0.13 → +0.62 (n_test = 21)
- G09 dictator giving: −0.14 → −0.49
- G07 green: +0.05 → −0.48 (n_test = 27)
- G13 CRT: −0.19 → −0.50

"Not distinguishable" in a group of 40–60 means *unknown*, not *same as population*.

## 4. Fragile and misleading cases (quotes are verbatim generator output)

### 4.1 CRITICAL: contradictory criteria silently become a different group (G24)
Input `sex=Male; sex=Female`. The command exits 0 and prints `ok`. `parse_criteria` does `crit[var] = lv`, so the later clause overwrites
the earlier one. The generated file reads:
> `**Outer-layer definition:** sex = Female` · `**n** = 1044 (50.7% of the panel); built from 736 train members, 308 held out.`

The intended intersection is empty (n = 0). The same mechanism affects any repeated variable, including a realistic live
refinement such as `age_band=18-29|30-49; income=…; age_band=30-49`: the generator keeps only the last `age_band` clause, with no warning.
The only clue is the echoed definition line.

### 4.2 HIGH: a *distinct* label next to a "Typical" value that is the population mean (G08, G12)
In G08 (65+, income < $30k):
> `| Cognitive reflection (0-4) | 2.40 | 1.57–2.38 | 0.0–3.1 (1.29) | -0.39 (-0.75, -0.04) | 10% | distinct |`

- The population CRT mean is 2.42. Shrinkage weight is 0.04, so "Typical" sits 0.02 SD from the population **and outside the raw-mean CI**.
- The label is computed from the raw d, while the headline value is shrunk. A reader sees "distinct" and a Typical that is not distinct.
- This is also a CRT-lower-in-older-people claim. The project explicitly *withdrew* that claim for P1 as a scoring artefact. Here it reappears
  with corrected scores, in a 40-person cell, with no held-out check possible (n_test = 17).
- G08 green values show the same pattern: `| Green values (1-5) | 3.71 | 3.74–4.22 | … | +0.45 (+0.21, +0.69) | 20% | distinct |`, with Typical below the CI.
- G12 has it too: `| Cognitive reflection (0-4) | 2.39 | 1.86–2.36 | … | -0.27 (-0.50, -0.05) | 10% | distinct |`. Its held-out d halved to −0.14 and its MAE gain was −0.2%.

T5 (heavy shrinkage on a labelled construct) fired in 5 of the 15 profiled groups: G07, G08, G12, G17 and G24.
In G24, dictator giving is labelled "weak difference" with w = 0.00.
The shrink weight is in the JSON only. **The markdown never shows it.**

### 4.3 HIGH: the "% on other side of pop. median" column ignores ties (all groups; worst for dictator giving and CRT)
`share_opposite_side_of_pop_median` counts only members strictly on the other side. Ties at the median are left out. In
training, 64% of people give exactly the median dictator amount (40) and 39% score exactly the CRT median (3).

Recount for G08 dictator giving:

| Below median | At median | Above median |
|---|---|---|
| 12% | 72% | 15% |

The card prints `12%` "on other side", which invites the reading that about 88% give more than the typical person. Only 15% do.

In G14: `| Dictator giving … | 39.42 | 38.18–51.82 | 40.0–60.0 (19.67) | +0.30 (-0.07, +0.68) | 6% | not distinguishable from population |`.
That `6%` sits next to a "not distinguishable" label.

### 4.4 MEDIUM: insufficient behaviour cells still print a confidence interval
The rate is hidden, but the Wilson CI is still printed. A reader can infer it. In G13 (home-makers):
> `| green_default | 5 | INSUFFICIENT EVIDENCE (n=5 < 20) | 0.57–1.00 | 58% (n=222) |`

All 5 chose renewable. A "0.57–1.00" next to "58%" invites a "home-makers go green" story from 5 people. G14 shows
`0.51–1.00` (n = 4). The rule of fewer than 20 per cell is applied correctly. The display undermines it.

### 4.5 MEDIUM: the 30-person cliff and unverifiable profiles
- G11 (n_train = 29) and G05 (28) abstain.
- G14 (n_train = 32) gets a full profile with `Neuroticism … +0.43 (+0.10, +0.77) … distinct`.
- G14 has n_test = 17, so nobody, including the generator, can check that number.
- **The generator's output for a new group contains no held-out check at all** (only `build-config` personas get one), and no
  warning when n_test < 20.

### 4.6 LOW: whole-population groups render `nan%`
G03 (`age_band=18-29|30-49|50-64|65+`) returns a "persona" with every d = +0.00 and
> `| Green values (1-5) | 3.53 | 3.47–3.58 | 2.0–4.7 (1.00) | +0.00 (-0.05, +0.05) | nan% | not distinguishable from population |`

There is no warning that the group is the whole panel. G04 (citizen=Yes, 99.8%) is the same without the `nan`.

### 4.7 Correctly handled (no action needed)
- Unknown variable (G21), case variant (G22), abbreviated region (G23), Tier B party (G25), trailing `|` (X1) and missing `=` (X5) were all
  rejected with exit 2 and messages that list valid options. Note, though, that `region=South` is rejected:
  the user must type `South (TX, OK, AR, LA, KY, TN, MS, AL, WV, DC, MD, DE, VA, NC, SC, GA, FL)` exactly, which is a live-typing hazard.
- Empty (G20) and small groups (G05, G06, G10, G11, G15, G16) returned INSUFFICIENT EVIDENCE. They exit **0**, though, so a
  script cannot tell them from success by exit code.
- Behaviour cells under 20 were never reported as a rate. The say/do block applied its n < 10 rule.

## 5. Interpretation for the live review
- The generator is **safe on refusal paths** and **honest about cell sizes**. Its dangerous failures are (a) the silent
  duplicate-variable overwrite and (b) labels and columns that overstate what a small group shows: raw-d labels next to
  shrunk values, a median-split column that ignores ties, and CIs printed for insufficient cells.
- Robust signals in new groups match the project's main finding. Age-linked neuroticism and social desirability carry
  nearly all individual-level value (G13, G17, G18, G19). Green values, CRT, spendthrift and dictator giving rarely beat the
  population mean by more than about 4%.
- Age-challenging groups (G08, G09) are where narrative risk is highest:
  - G08's neuroticism d is −0.09, CI (−0.40, +0.22). P1's −0.43 lies just outside that CI. This suggests an attenuated 65+
    calm, but with 40 people and no held-out check possible (n_test = 17).
  - G09's neuroticism d is +0.13, CI (−0.10, +0.37), against +0.43 for all train 18–29s, which lies just outside. The 21
    held-out members, however, are at +0.62.
  - The honest answer is "suggestive, not established", not "income cancels age".

## 6. Proposals (NOT applied; checked on training data only)
1. **Reject repeated variables** in `parse_criteria` (exit 2: "variable given twice; use `|` for OR"). This is a correctness fix and needs no data validation.
2. **Label on the shrunken estimate.** Call a construct *distinct* only if |Typical − pop| / SD ≥ 0.20 as well as the current rule.
   Otherwise show "raw difference, heavily shrunk (w = …)", and print w in the table.
   - *Training-only nested check* (`nested_training_label_check.csv`): the train split was divided 70/30 with seed 20261114,
     and the unchanged `build()` was run on inner-train and scored on inner-validation for the 9 groups with ≥ 20 inner-validation members.
   - Under the current rule, 8 constructs were labelled *distinct*. 5 of the 8 (0.62) replicated with the same sign and |d| ≥ 0.10.
   - The proposed rule kept 3, and all 3 replicated. It also dropped 2 that did replicate (G12 CRT, G19 SD).
   - This is **too few labels to establish anything**. It is directionally consistent with the proposal, not proof.
3. **Report below / at / above** the population median instead of "% on other side", or exclude ties explicitly.
4. **Suppress the CI** for insufficient behaviour cells.
5. **Warn on n_test < 20** ("cannot be checked on held-out data") and on share ≥ 0.90 ("this is the population").
6. **Sanitise `--name`** (reject path separators and `..`). Add case-insensitive or prefix matching for levels, and echo the resolved level back.

## 7. Five hardest groups for live practice

| # | Group | Why it is hard | What a good live answer must say |
|---|---|---|---|
| 1 | **G08: age 65+ and income < $30k** (n = 40/17) | Three *distinct* labels. Two have "Typical" outside the raw CI. CRT is *distinct* with shrink weight 0.04. Held-out check impossible. Behaviour 12/7 per cell. 100% inside P1 | "Forty people. I would not quote green +0.45 or CRT −0.39 as findings: the shrunken estimates are near the population, the CRT-age pattern was an artefact at the population level, and none of it can be checked on the 17 held-out members. Neuroticism is −0.09 (CI −0.40 to +0.22), just short of P1's −0.43. That hints that low income dampens the older-age calm, but it is one 40-person cell and cannot be checked. No behavioural claim (12 and 7 per condition)." |
| 2 | **G24-type: a variable typed twice** (e.g. `sex=Male; sex=Female`, or a refined `age_band`) | Exit 0, `ok`, a 1,044-person profile of a different group. Only the echoed definition line reveals it | Read the **Outer-layer definition** line and the n back to the requester *before* interpreting anything. Say: "The tool kept only the last clause; the group you asked for has n = 0 (or n = …), so there is no persona." Flag it as a known generator defect. |
| 3 | **G09: age 18–29 and income $100k+** (n = 58/21) | Challenges the age gradient. Every construct is "not distinguishable" on train, but held-out neuroticism is +0.62. Green-default cell n = 0. 65% inside P3 | "On 58 training members, neuroticism is +0.13 (CI −0.10 to +0.37), just below the +0.43 for all 18–29s, which hints that income offsets youth. But the 21 held-out members are at +0.62, i.e. the usual young-adult level or above. Undetermined. Do not claim income offsets youth. There is no behaviour data (8 and 0 per condition)." |
| 4 | **G14: Midwest with associate degree** (n = 32/17), against G11 widowed under 65 (n = 29, abstains) | Two training members above the cliff, it gets a *distinct* neuroticism +0.43 that cannot be checked (n_test = 17). One member below the cliff (G11, 29), it gets nothing. The dictator column prints 6% "on other side" | "This is barely above the 30 minimum. The one 'distinct' trait has a CI from +0.10 to +0.77 and no held-out check. I would treat it as a hypothesis. Nothing about Midwest or associate degree is known to drive neuroticism here. Behaviour: 4 per cell, nothing to say. The 6% median column is a tie artefact." |
| 5 | **G17: students** (n = 53/25) | 85% overlap with P3. Green *distinct* −0.32 but shrink weight 0.35. Neuroticism +0.37 → +0.73 held out. Behaviour 4/2 | "This is largely P3 again, so its traits are age traits. Higher neuroticism is the reliable part and held up (+0.73 on 25 held-out people, about 17% better individual prediction). Lower green values are shrunk by two-thirds and only cut error by about 3%. Treat them as weak. Only 6 training students took the green experiment, so no behaviour claim." |

Honourable mention: **G03/G04 (the whole population)**. The tool returns a "persona" with every d = 0.00 and `nan%`. The right answer
is "this is the panel average, not a persona".
