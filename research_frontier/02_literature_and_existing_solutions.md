# 02 · Literature and existing solutions

## How sources were verified
- Three search passes on 2026-11-14, by Claude subagents with web search, each told to report only sources whose record they actually found.
- Records checked: publisher pages, arXiv abstract or HTML, DOI/Crossref, PubMed, RePEc, PMLR, the ACL Anthology, institutional repositories.
- Many full texts were paywalled (PNAS/PubMed returned 403 or CAPTCHA; ScienceDirect, Springer and Nature returned 403). In those cases the numbers come from abstracts or index records and are marked † (from an abstract, index record or project page).
- ‡ marks figures taken from a **secondary** source (a citing work or thesis) and not checked against the original.

**Evidence types:** PR = peer-reviewed · PP = preprint · WP = working paper · DS = dataset paper · REV = review or commentary.

**Correction to a subagent report:** one pass attached PMC2922931 to Soto et al. (2011). That PMC record is Noftle & Fleeson (2010), checked by direct fetch during the submission polish. Soto et al.'s volume and pages are therefore treated as unverified.

## A. LLM simulation, generative agents and digital twins

1. **Peng, Gui, Brucks, … & Toubia (2025; v5 2026).** *Digital Twins as Funhouse Mirrors: Five Key Distortions.* arXiv:2509.19088. https://arxiv.org/abs/2509.19088. PP.
   - **Data and method:** Our Mega-Study source: 19 pre-registered studies, 164 outcomes, 1,784 unique Twin-2K-500 participants. GPT-4.1 twins under different persona specifications.
   - **Findings (v5 HTML):** Individual accuracy is 0.748 with the full persona, **0.746 demographics-only (14 variables)**, 0.734 with an empty persona and 0.629 random (full vs demographics, p = 0.37). Correlation with humans: full 0.197, **demographics-only 0.145**, empty 0.080. Twin SDs are smaller than human SDs on 154 of 164 outcomes.
   - **Relation to us:** The most directly relevant prior result, on the **same people and outcomes**. It **supports** our conclusion and is the existing "LLM from basic facts" baseline that the brief mentions.
   - **Limitations:** LLM-specific; reports accuracy and r, not R² against a population-mean baseline.
   - **Suggests:** Put our regression's per-outcome r next to their 0.145 on the identical outcomes.
2. **Toubia, Gui, Peng, Merlau, Li & Chen (2025).** *Twin-2K-500: A dataset for building digital twins of over 2,000 people based on their answers to over 500 questions.* arXiv:2505.17479. https://arxiv.org/abs/2505.17479. DS/PP.
   - **Data:** Prolific US sample quota-matched on age, sex and ethnicity; 4 waves (Jan–Feb 2025); 2,058 completers.
   - **Findings:** Human test–retest 81.72% on wave-4 repeated items. GPT-4.1-mini text-persona twin 71.72%, which is 87.67% of test–retest; random 59.17%.
   - **Relation to us:** Our data source. Whether it reports a demographics-only baseline is **unverified** (about 55% of the text was read). Its wave-4 retest covers heuristics-and-biases items, **not** our scales, so it gives no reliability ceiling for them.
3. **Park, Zou, Kamphorst, … Willer & Bernstein (2024; v3 2026).** arXiv:2411.10109. https://arxiv.org/abs/2411.10109. PP.
   - v1 title: *Generative Agent Simulations of 1,000 People*; v3 title: *LLM Agents Grounded in Self-Reports Enable General-Purpose Simulation of Individuals*.
   - **Data:** 1,052 US adults; agents built from 2-hour interviews, surveys, or both.
   - **Findings:** Accuracy on General Social Survey items, normalised by each person's own test–retest: interview 83%, survey 82%, both 86%, **demographics-only 74%**.
   - **Relation to us:** **Partly challenges** "demographics carry little". On normalised categorical accuracy, demographics reach a high floor. But accuracy on categorical items is dominated by base rates; it is not variance explained.
   - **Suggests:** Report a retest-normalised metric next to R² so the two literatures can be compared.
4. **Park, O'Brien, Cai, Morris, Liang & Bernstein (2023).** *Generative Agents: Interactive Simulacra of Human Behavior.* UIST '23. https://arxiv.org/abs/2304.03442 (ACM DOI 10.1145/3586183.3606763, seen in search results only). PR.
   - A believability study in a sandbox with 25 agents; no real people are predicted.
   - **Relation to us:** Neutral; architecture background only.
5. **Argyle, Busby, Fulda, Gubler, Rytting & Wingate (2023).** *Out of One, Many: Using Language Models to Simulate Human Samples.* Political Analysis 31(3):337–351. DOI 10.1017/pan.2023.2; arXiv:2209.06899. PR.
   - "Silicon samples" from demographic backstories reproduce **subgroup distributions** (algorithmic fidelity).
   - **Relation to us:** Compatible. Demographics carry **group-level** signal; this is the group/individual distinction we draw.
6. **Santurkar, Durmus, Ladhak, Lee, Liang & Hashimoto (2023).** *Whose Opinions Do Language Models Reflect?* ICML 2023, PMLR 202. arXiv:2303.17548. PR.
   - Language-model opinions diverge from 60 US demographic groups. The gap remains when the model is steered to a group, and people aged 65+ are poorly represented.
   - **Relation to us:** Indirect support.
7. **Bisbee, Clinton, Dorff, Kenkel & Larson (2024).** *Synthetic Replacements for Human Survey Data? The Perils of Large Language Models.* Political Analysis 32(4):401–416. DOI 10.1017/pan.2024.5. PR.
   - **Findings:** Synthetic ANES means match the real ones. But 48% of regression coefficients differ significantly, 32% of those flip sign, and the synthetic SD is 16.1 vs 31.4 for humans. Results drift over time and with prompt wording.
   - **Relation to us:** Supports. Persona-conditioned outputs mis-state the demographic → attitude structure.
   - **Suggests:** Compare coefficients, not only accuracy.
8. **Hu & Collier (2024).** *Quantifying the Persona Effect in LLM Simulations.* ACL 2024 (long), 10289–10307. https://aclanthology.org/2024.acl-long.554. PR.
   - **Findings:** Persona variables explain **< 10%** of annotation variance. How much persona prompting helps an LLM tracks how much variance those variables explain.
   - **Relation to us:** The **closest methodological analogue**, and directly supporting.
9. **Hewitt, Ashokkumar, Ghezae & Willer (2024).** *Predicting Results of Social Science Experiments Using Large Language Models.* WP. https://ai4pb.stanford.edu/projects/predicting-results-of-social-science-experiments-using-large-language-models.
   - **Findings:** GPT-4 predicts **average treatment effects** across 70 pre-registered survey experiments with r = 0.85.
   - Journal publication **unverified**.
   - **Relation to us:** Aggregate effects can be predictable even when individuals are not.
10. **Aher, Arriaga & Kalai (2023).** *Using Large Language Models to Simulate Multiple Humans and Replicate Human Subject Studies.* ICML 2023, PMLR 202. arXiv:2208.10264. PR.
    - Classic studies replicate in aggregate; "hyper-accuracy" distortion appears.
    - **Relation to us:** Neutral.
11. **Wang, Morgenstern & Dickerson.** *Large language models that replace human participants can harmfully misportray and flatten identity groups.* arXiv:2402.01908. PP; Nature Machine Intelligence acceptance claimed on arXiv, DOI **unverified**.
    - **Relation to us:** Supports. Demographic conditioning yields flattened stereotypes.

## B. Profiling, predictability and prediction vs explanation

12. **Kosinski, Stillwell & Graepel (2013).** *Private traits and attributes are predictable from digital records of human behavior.* PNAS 110(15):5802–5805. DOI 10.1073/pnas.1218772110. PR.
    - **Findings:** Likes from more than 58k volunteers predict sensitive traits (AUC 0.88–0.95 for some)†.
    - **Relation to us:** Rich **behavioural** traces predict traits; coarse demographics do not. A contrast that supports us.
13. **Youyou, Kosinski & Stillwell (2015).** *Computer-based personality judgments are more accurate than those made by humans.* PNAS 112(4). DOI 10.1073/pnas.1418680112. PR.
    - **Findings:** Likes-based personality prediction r = 0.56 (vs friends 0.49), rising to 0.66†.
    - **Relation to us:** Gives a ceiling for comparison. Our neuroticism R² of 0.17 is r ≈ 0.41, below the behavioural-data ceiling.
14. **Matz, Kosinski, Nave & Stillwell (2017).** *Psychological targeting as an effective approach to digital mass persuasion.* PNAS 114(48):12714–12719. DOI 10.1073/pnas.1710966114. PR.
    - Critique: Eckles, Gordon & Johnson (2018) PNAS 115(23):E5254–E5255, arguing ad-delivery optimisation confounds the design.
    - **Relation to us:** Even group-level targeting effects are contested.
15. **Salganik et al. (2020).** *Measuring the predictability of life outcomes with a scientific mass collaboration.* PNAS 117(15):8398–8403. DOI 10.1073/pnas.1915006117. PR.
    - **Findings:** 160 teams with thousands of variables barely beat a 4-variable expert benchmark. Holdout R² was about 0.2 at best‡.
    - **Relation to us:** **Strongly supports** low individual predictability as a general phenomenon.
    - **Suggests:** Add a 2–4-variable "expert" baseline (age + sex).
16. **Yarkoni & Westfall (2017).** *Choosing prediction over explanation in psychology.* Perspectives on Psychological Science 12(6):1100–1122. DOI 10.1177/1745691617693393. PR/REV.
    - **Relation to us:** Supports our cross-validated, held-out framing.
17. **Hofman et al. (2021).** *Integrating explanation and prediction in computational social science.* Nature 595:181–188. DOI 10.1038/s41586-021-03659-0. PR/REV.
    - **Relation to us:** Supports pairing explanation (age gradients) with prediction (low R²).
18. **Robinson (1950).** *Ecological correlations and the behavior of individuals.* American Sociological Review 15(3):351–357. PR.
    - **Relation to us:** The classic statement of the group/individual gap; our core caveat.
19. **Costa, Terracciano & McCrae (2001).** *Gender differences in personality traits across cultures.* JPSP 81(2):322–331. DOI 10.1037/0022-3514.81.2.322. PR. The full PDF was read.
    - **Findings:** US women are higher on neuroticism with d ≈ 0.51. Differences are "small relative to individual variation".
    - **Relation to us:** External benchmark. Sex alone ≈ R² 0.06; our sex increment is +0.015 (`headline_challenge/nested.csv`), smaller than the literature implies.
20. **Roberts, Walton & Viechtbauer (2006).** Psychological Bulletin 132(1):1–25. DOI 10.1037/0033-2909.132.1.1. PR (meta-analysis of *longitudinal* studies).
    - Emotional stability rises mainly at ages 20–40.
    - **Relation to us:** Supports age as the main demographic driver of neuroticism. Our data are cross-sectional.
21. **Graham et al. (2020).** *Trajectories of Big Five personality traits: a coordinated analysis of 16 longitudinal samples.* European Journal of Personality 34(3):301–321. DOI 10.1002/per.2259. PR.
    - Reports late-life *increases* in neuroticism in some samples.
    - **Relation to us:** **Challenges** a simple "older = calmer" story; our 65+ band can't resolve late-life change.
22. **Hedge, Powell & Sumner (2018).** *The reliability paradox.* Behavior Research Methods 50(3):1166–1186. DOI 10.3758/s13428-017-0935-1. PR.
    - **Relation to us:** Supports treating CRT and dictator giving as unreliable for individual differences.
23. **Matz, Appel & Kosinski (2020).** *Privacy in the age of psychological targeting.* Current Opinion in Psychology 31:116–121. DOI 10.1016/j.copsyc.2019.08.010. PR/REV.
    - **Relation to us:** Ethical framing. Low individual predictability limits harm, but group stereotyping is the risk our personas carry.

## C. Attitude–behaviour, defaults and choice architecture

24. **Ajzen (1991).** *The theory of planned behavior.* OBHDP 50(2):179–211. DOI 10.1016/0749-5978(91)90020-T. PR. Reply to critics: Ajzen (2015) Health Psychology Review 9(2):131–137.
25. **Sniehotta, Presseau & Araújo-Soares (2014).** *Time to retire the theory of planned behaviour.* Health Psychology Review 8(1):1–7. DOI 10.1080/17437199.2013.869710. REV.
26. **Webb & Sheeran (2006).** Psychological Bulletin 132(2):249–268. DOI 10.1037/0033-2909.132.2.249. PR, meta-analysis of 47 experiments.
    - **Findings:** An intention change of d = 0.66 produced a behaviour change of d = 0.36†.
    - **Relation to us:** Real behaviour would show *larger* gaps than our hypothetical choice.
27. **Kollmuss & Agyeman (2002).** *Mind the Gap.* Environmental Education Research 8(3):239–260. DOI 10.1080/13504620220145401. REV.
28. **Diekmann & Preisendörfer (2003).** *Green and greenback: The behavioral effects of environmental attitudes in low-cost and high-cost situations.* Rationality and Society 15(4):441–472. DOI 10.1177/1043463103154002. PR.
    - The low-cost hypothesis.
    - **Relation to us:** Our $7/month premium is low-cost, so the green-values effect may be inflated relative to costlier real decisions.
29. **Johnson & Goldstein (2003).** *Do defaults save lives?* Science 302(5649):1338–1339. DOI 10.1126/science.1091721. PR.
    - Hypothetical online experiment‡ with a design like ours (the organ-donor items in `default_eric`).
30. **Pichert & Katsikopoulos (2008).** *Green defaults: Information presentation and pro-environmental behaviour.* Journal of Environmental Psychology 28(1):63–73. DOI 10.1016/j.jenvp.2007.09.004. PR.
    - **Findings‡:** Relocation scenario with a green supplier vs a cheaper one (30 vs 25/month): green default 68%, grey default 41%, neutral 67%.
    - **Relation to us:** **Our scenario closely mirrors this design**; ours gives 58% vs 36%, so `default_eric` is effectively a conceptual replication. The original stimulus wording is unverified, and the names "GreenGrid" and "Twon" were not found in any source.
31. **Ebeling & Lotz (2015).** *Domestic uptake of green energy promoted by opt-out tariffs.* Nature Climate Change 5(9):868–871. DOI 10.1038/nclimate2681. PR.
    - **Findings†:** Field RCT with about 42k households; real uptake 7.2% opt-in vs 69.1% opt-out. Green vote share predicted uptake **only under opt-in**.
    - **Relation to us:** Predicts a *negative* values × default interaction. That is our H4, which was inconclusive.
32. **Jachimowicz, Duncan, Weber & Johnson (2019).** *When and why defaults influence decisions: a meta-analysis of default effects.* Behavioural Public Policy 3(2):159–186. DOI 10.1017/bpp.2018.43. PR.
    - **Findings:** 58 studies, d = 0.68 (CI 0.53–0.83). Defaults are weaker in the environmental domain. Endorsement and endowment drive them.
33. **List & Gallet (2001)**, Environmental & Resource Economics 20(3):241–254 (DOI not seen), and **Murphy, Allen, Stevens & Weatherhead (2005)**, ERE 30(3):313–325, DOI 10.1007/s10640-004-3332-z. PR meta-analyses.
    - **Findings:** Hypothetical values overstate actual values (mean factor about 3; median ratio 1.35, right-skewed). Choice formats reduce the bias.
34. **Hedlin & Sunstein (2016).** *Does active choosing promote green energy use?* Ecology Law Quarterly 43:107. PR (law review); DOI not seen.
    - **Findings‡:** An active choice outperformed the green default in a hypothetical design (56% vs 39%).
    - **Relation to us:** Challenges the assumption that a default maximises uptake.
35. **Vetter & Kutzner (2016).** *Nudge me if you can.* Comprehensive Results in Social Psychology. DOI 10.1080/23743603.2016.1139390. PR.
    - **Findings‡:** A replication of Pichert & Katsikopoulos with a default odds ratio of about 4, where environmental attitude did *not* predict the choice.
    - **Relation to us:** **Contrasts** with our OR ≈ 2.5–3; the attitude measure and its timing matter.
36. **Kahneman & Tversky (1979).** *Prospect theory.* Econometrica 47(2):263–291. DOI 10.2307/1914185. PR.

## Comparison matrix

| System or study | Predicts individuals? | Input | Outcome | Held-out evaluation | Baseline | Uncertainty | Real behaviour? |
|---|---|---|---|---|---|---|---|
| **This project** | Yes, plus group personas | 10 census variables (+1 attitude scale, exploratory) | 6 scales, hypothetical choice | Frozen 30% holdout | Population mean / prevalence | Bootstrap and Wald, partly fixed-model | No |
| Peng et al. 2025 | Yes (LLM twins) | Full persona / 14 demographics / empty | 164 Mega-Study outcomes | Yes | Empty and random persona | Significance tests | No |
| Park et al. 2024 | Yes (LLM agents) | Interview / survey / demographics | GSS, Big Five, games | Yes, test–retest normalised | Demographics-only agent | Normalised accuracy | Partly (games) |
| Argyle et al. 2023; Bisbee et al. 2024 | Group distributions | Demographic backstories | ANES items | Comparison with real survey | Human sample | Distribution comparison | No |
| Hu & Collier 2024 | Yes | Persona variables | Annotation judgements | Yes | Linear regression | Variance decomposition | No |
| Kosinski et al. 2013; Youyou et al. 2015 | Yes | Digital footprints | Traits | Cross-validation | Human judges | — | — |
| Salganik et al. 2020 | Yes | Thousands of survey variables | Life outcomes | Common-task holdout | 4-variable expert model | — | Yes (life outcomes) |
| Ebeling & Lotz 2015 | Group (RCT) | Default arm, county vote | Real tariff uptake | Randomised field trial | Opt-in arm | — | **Yes** |

## Where this project overlaps prior work, and what might be distinct
- **Not novel:**
  - that demographics predict individuals weakly (Salganik; Hu & Collier; Peng et al. on these very participants);
  - that defaults shift green choices (Pichert & Katsikopoulos; Ebeling & Lotz);
  - that attitudes predict hypothetical choices better than demographics do.
- **Possibly distinct, modestly:**
  1. A transparent, pre-registered, **non-LLM statistical baseline** with held-out R² on the same panel that the LLM-twin literature uses. It gives a direct quantitative floor for "what demographics carry" that LLM papers report only as accuracy or r.
  2. The finding that **three shipped scale scores in a widely used benchmark dataset are mis-scored**, two in an age-dependent way. That matters for anyone benchmarking digital twins on Twin-2K-500. It is a data-quality contribution, not a psychological one.
  3. An explicit decomposition showing that, at n ≈ 400, **adding demographics to a measured attitude degrades prediction** (training-only X1).
