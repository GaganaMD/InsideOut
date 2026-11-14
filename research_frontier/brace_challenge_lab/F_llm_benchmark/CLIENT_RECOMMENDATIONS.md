# Client recommendations: when to use LLM personas, when to collect survey data

Evidence base (state it whenever these are quoted): two hypothetical-choice studies from the Twin-2K-500 Mega-Study
(green-energy default, n = 428; targeting fairness, n = 260), training participants only, published GPT-4.1 digital
twins (Peng et al. 2025, arXiv:2509.19088) compared with simple statistical baselines. Exploratory, one model family,
not a validated benchmark. Numbers: `MODEL_COMPARISON.csv`, `CALIBRATION_AND_FAILURES.md`.

## 1. What the evidence says (short)
1. **Demographic personas did not beat a simple baseline.** Recalibrated GPT-4.1 demographic twins: Brier 0.241 vs
   0.237 for "same rate for everyone in a condition" (difference -0.004, CI -0.017 to +0.009). Census statistical
   models did no better (+0.002, CI -0.005 to +0.008). The LLM persona probably saw *more* than census data (party,
   ideology, religion), and still added nothing detectable over a persona-free prompt.
2. **Raw synthetic answers are overconfident.** Scored as given, they were worse than predicting the base rate for
   everyone (Brier 0.41 vs 0.25).
3. **Effect sizes are unreliable, directions less so.** Signs of two randomised effects were right in 8 of 8
   published runs; sizes were 0.4-0.7x the human effect with personas and 4x without.
4. **Synthetic samples lose the tails.** On a 1-9 fairness scale, a third of people answered 9 and a quarter 5 or
   lower; the demographic twin almost never did either.
5. **Small groups are where personas do worst.** Errors on groups of 10-39 people were larger than using the
   population average.
6. **Measured attitudes are what predict.** A twin built from a person's full survey (~500 answers) improved
   prediction by about 9% on the green choice; a 6-item attitude scale plus the condition did as well without an LLM.

## 2. Use an LLM persona when
- You need **directional screening** of many intervention variants before any fieldwork, and a wrong magnitude is
  cheap (the next step is a human test anyway).
- You are drafting materials (survey wording, stimulus copy, hypotheses), not forecasting numbers.
- You have a **validated calibration** for this kind of task (section 4) and report LLM numbers with that
  calibration attached.

## 3. Collect survey data instead when
- The deliverable is an **effect size**, a share of people, or a distribution (e.g. "how many will object").
- The decision concerns a **small or specific group** (a sub-segment, a minority, a region).
- The outcome is likely driven by **values or attitudes** (green values, fairness views): measure 5-10 targeted
  items. In our data one 6-item scale (odds ratio about 3 per SD on the green choice) beat every demographic and
  LLM-demographic approach.
- Heterogeneity matters (targeting, segmentation, risk of backlash in the tails).
- The cost of a wrong answer exceeds the cost of a small, targeted survey (compare the two explicitly per project;
  this analysis did not price fieldwork).

## 4. Minimum evidence before relying on LLM personas for a client
1. **Same-task back-test:** on at least 3 past studies of the same type with human results, the LLM (with
   probability elicitation, fixed prompt and model id) must beat the condition/population average on Brier or
   squared error, with CIs excluding zero.
2. **Effect calibration:** predicted vs human effects across those studies; report the ratio and its spread. Use
   LLM effect sizes only after applying it, and never outside its range.
3. **Distribution check:** total-variation distance and SD ratio vs humans; refuse tail claims if SD ratio < 0.7.
4. **Group check:** errors for every reported subgroup vs the population-average baseline; do not report subgroups
   where the LLM is worse.
5. **Information audit:** document exactly what the persona contained (fields, survey items) and confirm no target
   leakage. Survey-answer personas measure the value of the survey, not of the LLM.
6. **Reproducibility:** fixed template hash, model version as served, temperature, sample count, date, cost.

## 5. Open question this workstream prepared but could not run
Whether giving an LLM an explicit, statistically estimated attitude profile for a demographic group (D) improves
on demographics alone (C). This is the cheapest possible upgrade to a demographic persona and directly tests
whether the negative result is a prompting artefact. Ready to run: `PROMPT_VARIANTS.md` (pilot <= $0.35, full
<= $3.68 upper bound). Blocked: OpenRouter path blocked (expired key); open-weight path on Modal handled in
`F2_modal_open_weight/` — a DIFFERENT model family, never to be substituted for GPT-4.1 results. Until it runs, the
recommendation above stands: for group attitudes and choices, measure, do not simulate.
