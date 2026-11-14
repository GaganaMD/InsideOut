# What this dataset cannot identify, and defects found in the frozen submission

## 1. Non-identifiable quantities
| Question | Why it cannot be answered here |
|---|---|
| Does *ageing* lower neuroticism or raise SD? | **One cross-section:** age, birth cohort and survivorship are perfectly confounded. Any age-band gap = maturation + cohort + differential survival + differential panel entry. Disentangling needs repeated measures (cohort-sequential design). |
| Shape of the age curve | **Only 4 bands**, the top one open-ended (65+). At most 2 df of non-linearity can be tested; within-band trends, late-life reversals (e.g. 80+) and the timing of the 18–40 "maturity" window are invisible. Neuroticism is consistent with linear-in-band (p = 0.70); SD is not (step at 50+, p = 0.003); both statements are about 4 points only. |
| Panel representativeness | Twin-2K-500 is an online, opt-in sample; no weights or ACS margins were used. Who among older adults, low-income adults and young never-married adults joins such panels is unknown, and selection could depend on the very traits measured (e.g. emotional stability, conscientiousness). Within-panel composition differs sharply (65+: 85% White vs 65%). Twin recruitment adds another unknown filter. |
| Style vs substance | A single self-report SD scale cannot separate impression management from genuine adjustment; partialling it out (P1 neuroticism −0.41 → −0.25) is an *upper bound* on the style share, not an estimate. No informant reports, no behavioural measures of temperament. |
| Direction of income ↔ neuroticism | Household income and neuroticism are measured contemporaneously; reverse causation and health confounding (unmeasured) are open. Household income may reflect parents' income for co-resident young adults. |
| Marriage → values | Marital status is a status, not an event; no timing, partner data or pre-partnering measures. The partnered 18–29 comparison group is n = 75 (train). |
| Behavioural mechanisms | **No incentives anywhere**; all "choices" are hypothetical (exploration_log #5). Persona × condition cells are 6–49 people. Nothing about real behaviour is identified. |
| Generalisation | US only; one costed scenario; constructs measured once (CRT KR-20 0.58; dictator single item). |

What *is* identified: (i) randomised default → hypothetical green choice (causal, but population-level only); (ii) predictive, held-out group-mean shifts for neuroticism and SD; (iii) within this sample, the conditional associations reported in `PERSONA_MECHANISMS.md`.

## 2. Defects / over-claims found in the frozen submission (evidence from training data only)
1. **"P3's green gap is concentrated in young never-married men"** (`reports/memo.md` §2; `reports/personas/P3_young_never_married.md` "Sex-composition caveat"; `reports/robustness/persona_stability/persona_stability.md`). The claim rests on a significant (men d −0.40) vs non-significant (women d −0.12) contrast, without an interaction test; both ds are against the *whole* population, in which 18–29 men are already −0.31 z and 18–29 women +0.09 z. Interaction tests: P3 × male −0.14 (−0.45, +0.16); within 18–29, never-married × male +0.18 (−0.31, +0.66). Within age, the never-married gap is −0.41 (men) and **−0.59 (−0.91, −0.28) (women)**. The data do not show the gap is male-specific; what is male-specific is the general youth deficit in green values. Severity: Major (interpretation), no number changes. (`results.csv` rows `2_subgroup`/`2_interaction`, P3 green.)
2. **"Part of the older group's calm profile is self-presentation"** (`memo.md` §2; P1 card "part of the calm is self-description"). The −0.50 → −0.31 attenuation is interpreted as style, but the SD scale also carries substantive personality variance (McCrae & Costa 1983, doi:10.1037/0022-006X.51.6.882), so the adjustment may remove real stability. The sentence should read "up to about a third of the gap is shared with SD; whether that share is style or substance is not identified." Severity: Minor–Major (wording).
3. **"Low income goes with higher neuroticism within every age band"** (`memo.md` §2). On train: +0.37, +0.39, +0.23 and **+0.15 (−0.11, +0.42) at 65+**; the 65+ CI includes 0 and the gradient shrinks with age. "In every band below 65; direction holds but not significant at 65+." Severity: Minor.
4. **Mixed units in held-out gain CIs.** In every `*_evidence.md` held-out table and in `results/holdout_personas.csv`, "Gain (95% CI)" pairs a **percentage** point estimate with a CI in **absolute MAE units** (e.g. P1 social desirability "+11.6% (+0.137, +0.640)": MAE 3.446 − 3.048 = 0.398 is inside that CI, 11.6 is not). Same in `statistical_audit.md` ("+9.3% (CI 0.07–0.50)"). Severity: Minor (presentation); the "CI excludes 0" conclusions are unaffected.
5. **Persona traits that are entirely one criterion** (not an error, but not disclosed precisely): P3's neuroticism and SD carry **zero** within-age marital signal (−0.01; −0.03), and P2's lower SD carries **zero** income signal within age (−0.01). The cards attribute these traits to the conjunction. For these traits, P2 ≈ "18–49" and P3 ≈ "18–29".
6. **P1 "distinct" weak tilts are composition.** P1 green (+0.15, held-out MAE gain CI excluding 0) and spendthrift (−0.13) fall to +0.11 and −0.08 with CIs including 0 after Tier A adjustment. The cards label them "weak difference" (correct), but they should not be read as age effects.

No defect found in: train/test isolation (this workstream never touches test rows), reproduction of frozen train d (script reproduces P1 neuroticism −0.434, P2 +0.4715, P3 green −0.2739 exactly), or the corrected SD/CRT scoring (`assert` in script confirms item-derived neuroticism equals the shipped score).

## 3. What would identify the mechanisms
- Repeated measures of neuroticism/SD in the same people (≥2 waves several years apart) → separates maturation from cohort.
- Exact age (or ≥8 bands) → shape and timing.
- ACS/probability-sample reweighting, or a probability-sample replication → selection.
- Informant reports or behavioural affect measures → style vs substance.
- Income shocks or lagged income → direction of income ↔ neuroticism.
- Partnering events with pre-event green values → marriage → values vs selection.
- Incentivised green choice → anything about behaviour.
