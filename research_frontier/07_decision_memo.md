# 07 · Research decision memo

**Verdict: SUBMIT WITH MINOR FIXES.** Two README caption sentences blur or overstate results and should be corrected (with your approval). No CRITICAL issue was found, and no new experiment is needed before submission.

## 1. Strongest elements
- **Process integrity.** Frozen, hashed split. Falsifiers pre-registered before modelling, with H1 honestly falsified. The holdout was used once. Later work is labelled and training-only, with leakage tests.
- **Measurement auditing.** Three mis-scored shipped scales were found and each reproduced exactly from the raw exports. One had created a spurious CRT age decline.
- **The headline survives every challenge we could mount** (`reports/final_audit/headline_challenge.md`).
  - New training-only X1: demographics *degrade* green-choice prediction at n = 428. Dropping them improves Brier by 0.012 and the calibration slope goes from 0.70 to 0.99.
  - X3: all six robust persona traits keep 56–77% of their size after adjusting for the other census variables.

## 2. Most serious unresolved weaknesses
1. **No real behaviour.** The choice is hypothetical and mirrors Pichert & Katsikopoulos (2008): their uptake was 68%/41%, ours 58%/36%. Hypothetical bias (List & Gallet 2001; Murphy et al. 2005) means choice *levels* may not transfer.
2. **Census-marginal inference (Brace's real use case) is untested.** We predict individuals within a non-representative online panel.
3. **Figure 1's intervals hold the model fixed.** They are about 2–3× too narrow for CRT and green values (`01_project_red_team.md`). There is no multiplicity control across 18 persona cells.
4. **Construct overlap.** The green-values purchasing and cost items out-predict the concern/identity items (X2). Say "environmental disposition", not "attitude".
5. **No LLM baseline of our own.** The relevant external one is Peng et al. (2025), on the same participants.

## 3. Prior work: what it does and does not establish
- **Established:**
  - demographics-only LLM twins barely beat empty personas on these participants (Peng et al.: r 0.145 vs 0.080; full persona 0.197);
  - persona variables explain under 10% of variance (Hu & Collier 2024);
  - mass prediction plateaus near R² ≈ 0.2 (Salganik et al. 2020; figure from a secondary summary);
  - green defaults work in the field (Ebeling & Lotz 2015: 7% vs 69%).
- **Not established:**
  - a transparent non-LLM held-out floor on this panel;
  - whether the attitude effect shrinks as cost rises in the *same* people;
  - which mechanism drives green defaults (Jachimowicz et al. 2019: weaker and heterogeneous in the environmental domain).

## 4. What we can claim without overstating novelty
The negative result is a **replication**, not a discovery. Modest contributions:
1. A pre-registered statistical baseline that complements the LLM-twin literature on the same panel.
2. A data-quality finding: three of six shipped scale scores are mis-scored, two in an age-dependent way.
3. A small-sample caution: demographics added to an attitude can hurt prediction (exploratory).

## 5. The ten frameworks
| Decision | Frameworks |
|---|---|
| Retain as mechanisms | Low-cost / attitude–behaviour consistency (merging the TPB attitude path); default mechanisms (with Prospect Theory's reference dependence as one rival) |
| Retain as methodology only | Falsificationism; Mill's method of difference; Bayesian shrinkage; Hume |
| Drop as theory claims | Social Cognitive Theory; Cognitive Dissonance; behaviourism; Dual-Process (CRT is not a dual-process test) |

No behavioural theory was directly tested (`03_theory_audit.md`).

## 6. Highest-value next experiment
**Cost × incentive.**
- Re-contact about 1,200 Twin-2K-500 participants (green values already measured).
- Randomise the premium ($0/$7/$20) × hypothetical vs incentive-compatible choice.
- Test whether the green-values slope shrinks with cost (falsifiable interaction; `05_theory_prioritization.md`).
- It targets weakness 1 with the panel's unique asset.

**Not worth delaying submission:** it needs new data, ethics approval and a budget. Present it as the proposed next step. The optional no-API LLM baseline from published Mega-Study predictions (`06_llm_experiment_roadmap.md`, step 0) has unverified feasibility and would mostly confirm Peng et al.

## 7. Now, later, not at all
- **Now (about 10 minutes, needs approval):**
  - Figure 2 caption: the default adds ΔBrier ≈ −0.013 beyond green values, not "little";
  - Figure 1: note that intervals hold the model fixed;
  - replace "group-level signal" with individual-level R² wording (`08_visual_and_communication_audit.md` items 1–3);
  - after pushing, check that the Mermaid diagram renders on GitHub.
- **Later:**
  - step 0 LLM baseline;
  - the cost × incentive study;
  - a default-mechanism study (disclaimer, effort, active-choice, willingness-to-accept/willingness-to-pay arms);
  - ACS reweighting.
- **Not at all:**
  - more demographic model variants (six families already agree);
  - Dual-Process or Prospect Theory tests on current data;
  - any held-out re-analysis.

**Justification.** No finding changes a headline conclusion. The issues are caption precision and already-disclosed external validity, and the new exploratory results strengthen the central claim (X1, X3) while refining one phrase (X2).
