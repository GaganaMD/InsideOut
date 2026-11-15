"""EXPLORATORY persona extension. NOT part of the submission pipeline (run_all.py does not call this).

Added 2026-11-15, after the holdout had been inspected. TRAINING SPLIT ONLY: the test split is never read for
estimation here. Nothing frozen is written. Run from the repository root:

    python research_frontier/persona_extension/persona_extension.py

What it does
1. Re-derives six further scales from item responses and checks each against the shipped score:
   BFI-44 conscientiousness, agreeableness, extraversion, openness; 18-item need for cognition; 12-item self-concept
   clarity. Only scales that match exactly are used.
2. Extended persona profile: d vs the training population for those six scales plus the six pre-registered ones.
3. What each persona isolates: income within ages 18-49 (P2), never-married within 18-29 (P3), 65+ vs 50-64 (P1).
4. Within-persona counterexamples (found by inspecting subgroups, so they are leads, not tests).
5. Two descriptive clusters: correlations before and after removing all ten Tier A variables, Tier A predictability
   of each cluster's composite, a descriptive two-factor solution, and whether each composite predicts the green choice.
6. Say-do: among high green-values scorers, which demographics and traits go with declining the renewable option.

Outputs (this folder): extended_profile.csv, results.json.
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from sklearn.decomposition import FactorAnalysis
from sklearn.model_selection import RepeatedKFold
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from common import PROC, RAW_TWIN, SEED, TIER_A, load_green, load_people, low_income, wilson  # noqa: E402
from personas import load_config, mask, parse_criteria  # noqa: E402
from predictability import model  # noqa: E402

# name: (shipped column, item block, items, reverse-keyed items)
SCALES = {
    "conscientiousness": ("w1_score_conscientiousness", "QID25", [3, 8, 13, 18, 23, 28, 33, 38, 43], [8, 18, 23, 43]),
    "agreeableness": ("w1_score_agreeableness", "QID25", [2, 7, 12, 17, 22, 27, 32, 37, 42], [2, 12, 27, 37]),
    "extraversion": ("w1_score_extraversion", "QID25", [1, 6, 11, 16, 21, 26, 31, 36], [6, 21, 31]),
    "openness": ("w1_score_openness", "QID25", [5, 10, 15, 20, 25, 30, 35, 40, 41, 44], [35, 41]),
    "need_for_cognition": ("w1_score_needforcognition", "QID26", list(range(1, 19)), [3, 4, 5, 7, 8, 9, 12, 16, 17]),
    "self_concept_clarity": ("w3_score_SCC", "QID237", list(range(1, 13)), [1, 2, 3, 4, 5, 7, 8, 9, 10, 12]),
}
OLD = ["neuroticism", "social_desirability", "green", "spendthrift", "crt", "dictator_give"]
ADJ, VAL = ["neuroticism", "conscientiousness", "self_concept_clarity", "social_desirability"], ["green", "openness", "need_for_cognition"]
r2 = lambda x: round(float(x), 3)


def rescored() -> tuple[pd.DataFrame, dict]:
    num = pd.read_csv(RAW_TWIN / "question_catalog_and_human_response_csv/wave1_3_response.csv", low_memory=False).set_index("pid")
    shipped = pd.read_parquet(PROC / "scores.parquet").set_index("pid")
    out, audit = pd.DataFrame(index=num.index), {}
    for name, (col, q, items, rev) in SCALES.items():
        d = num[[f"{q}_{i}" for i in items]].apply(pd.to_numeric, errors="coerce")
        for i in rev:
            d[f"{q}_{i}"] = 6 - d[f"{q}_{i}"]
        out[name] = d.mean(axis=1)
        k = d.shape[1]
        audit[name] = dict(items=k, reverse_keyed=rev, exact_match_with_shipped=r2(np.isclose(out[name], shipped[col].astype(float).reindex(out.index)).mean()),
                           cronbach_alpha=r2(k / (k - 1) * (1 - d.var(ddof=1).sum() / d.sum(axis=1).var(ddof=1))))
        assert audit[name]["exact_match_with_shipped"] == 1.0, name
    return out.reset_index(), audit


def ci(x: pd.Series) -> dict:
    m, se = x.mean(), x.std(ddof=1) / np.sqrt(len(x))
    return dict(n=int(len(x)), d=r2(m), lo=r2(m - 1.96 * se), hi=r2(m + 1.96 * se))


def coef(formula: str, data: pd.DataFrame, term: str) -> dict:
    f = smf.ols(formula, data).fit()
    c = f.conf_int().loc[term]
    return dict(est=r2(f.params[term]), lo=r2(c[0]), hi=r2(c[1]), p=r2(f.pvalues[term]), n=int(f.nobs))


def odds(fit) -> dict:
    c = fit.conf_int()
    return {t: dict(OR=r2(np.exp(fit.params[t])), lo=r2(np.exp(c.loc[t, 0])), hi=r2(np.exp(c.loc[t, 1])), p=r2(fit.pvalues[t])) for t in fit.params.index}


def main() -> None:
    new, audit = rescored()
    T = list(SCALES) + OLD
    df = load_people(corrected=True).merge(new, on="pid")
    tr = df[df.split == "train"].reset_index(drop=True)          # training split only from here on
    mu, sd = tr[T].mean(), tr[T].std(ddof=1)
    for c in T:
        tr["z_" + c] = (tr[c] - mu[c]) / sd[c]
    cfg = load_config()
    M = {k: mask(tr, parse_criteria(v["criteria"], tr)) for k, v in cfg.items()}
    half = np.random.default_rng(SEED).permutation(len(tr)) < len(tr) // 2
    res = {"note": "EXPLORATORY; training split only; not pre-registered; no held-out check", "n_train": len(tr), "scale_audit": audit}

    rows = []
    for k, m in M.items():
        for c in T:
            x = tr.loc[m, c]
            rows.append(dict(persona=cfg[k]["name"], construct=c, status="re-derived from items, exact match" if c in SCALES else "pre-registered construct",
                             raw_mean=r2(x.mean()), p10=r2(x.quantile(.1)), p90=r2(x.quantile(.9)), pop_mean=r2(mu[c]), **ci(tr.loc[m, "z_" + c]),
                             d_half1=r2(tr.loc[m & half, "z_" + c].mean()), d_half2=r2(tr.loc[m & ~half, "z_" + c].mean())))
    pd.DataFrame(rows).to_csv(HERE / "extended_profile.csv", index=False, lineterminator="\n")

    age, emp, inc = tr.age_band.astype(str), tr.employment.astype(str), tr.income.astype(str)
    y = tr[age.isin(["18-29", "30-49"])].assign(low=lambda d: low_income(d.income).astype(int))
    u = tr[age == "18-29"].assign(nm=lambda d: (d.marital.astype(str) == "Never been married").astype(int))
    o = tr[age.isin(["50-64", "65+"])].assign(old=lambda d: (d.age_band.astype(str) == "65+").astype(int))
    res["isolates"] = {
        "P2_low_income_within_18_49_adjusted_for_age_band": {c: coef(f"z_{c} ~ low + C(age_band)", y, "low") for c in T},
        "P3_never_married_within_18_29_adjusted_for_sex_income_education": {c: coef(f"z_{c} ~ nm + C(sex) + C(income) + C(education)", u, "nm") for c in T},
        "P1_65plus_vs_50_64": {c: coef(f"z_{c} ~ old", o, "old") for c in T},
        "age_band_means_in_sd_units": tr.groupby("age_band", observed=True)[["z_" + c for c in T]].mean().round(3).rename(columns=lambda s: s[2:]).to_dict("index"),
        "overlap_train": dict(P2_only=int((M["P2"] & ~M["P3"]).sum()), P3_only=int((M["P3"] & ~M["P2"]).sum()), both=int((M["P2"] & M["P3"]).sum())),
    }

    def subgroup(m, cols): return {c: ci(tr.loc[m, "z_" + c]) for c in cols}
    def contrast(m_in, flag, cols): return {c: coef(f"z_{c} ~ flag", tr[m_in].assign(flag=flag[m_in].astype(int)), "flag") for c in cols}
    c1, c2, c3 = ["neuroticism", "self_concept_clarity", "conscientiousness"], ["neuroticism", "conscientiousness", "extraversion"], ["conscientiousness", "neuroticism", "self_concept_clarity"]
    res["counterexamples"] = {
        "note": "subgroups found by inspecting several splits; uncorrected for that search",
        "P1_income_under_30k": subgroup(M["P1"] & (inc == "Less than $30,000"), c1), "P1_other_incomes": subgroup(M["P1"] & (inc != "Less than $30,000"), c1),
        "P1_under_30k_vs_rest": contrast(M["P1"], inc == "Less than $30,000", c1),
        "P2_full_time": subgroup(M["P2"] & (emp == "Full-time employment"), c2), "P2_not_full_time": subgroup(M["P2"] & (emp != "Full-time employment"), c2),
        "P2_full_time_vs_rest": contrast(M["P2"], emp == "Full-time employment", c2),
        "P3_full_time": subgroup(M["P3"] & (emp == "Full-time employment"), c3), "P3_unemployed": subgroup(M["P3"] & (emp == "Unemployed"), c3),
        "P3_full_time_vs_rest": contrast(M["P3"], emp == "Full-time employment", c3),
    }

    S = ADJ + VAL + ["agreeableness", "extraversion"]
    X = pd.get_dummies(tr[TIER_A].astype(str), drop_first=True).astype(float).to_numpy()
    X = np.column_stack([np.ones(len(tr)), X])
    resid = lambda v: v - X @ np.linalg.lstsq(X, v, rcond=None)[0]
    raw = tr[["z_" + c for c in S]].corr().to_numpy()
    par = pd.DataFrame({c: resid(tr["z_" + c].to_numpy()) for c in S}).corr().to_numpy()
    ix = {c: i for i, c in enumerate(S)}
    blk = lambda Cm, a, b: r2(np.mean([abs(Cm[ix[i], ix[j]]) for i in a for j in b if i != j]))
    tr["adjustment"] = (-tr.z_neuroticism + tr.z_conscientiousness + tr.z_self_concept_clarity) / 3
    tr["open_nfc"] = (tr.z_openness + tr.z_need_for_cognition) / 2
    tr["values3"] = (tr.z_green + tr.z_openness + tr.z_need_for_cognition) / 3

    def cv(v):
        Xc, out = tr[TIER_A].astype(str), []
        for a, b in RepeatedKFold(n_splits=5, n_repeats=5, random_state=SEED).split(Xc):
            p = model(TIER_A).fit(Xc.iloc[a], v[a]).predict(Xc.iloc[b])
            out.append(1 - ((v[b] - p) ** 2).sum() / ((v[b] - v[a].mean()) ** 2).sum())
        return dict(cv_r2=r2(np.mean(out)), heuristic_half_width=r2(1.96 * np.std(out, ddof=1) / np.sqrt(5)))
    fa = FactorAnalysis(n_components=2, rotation="varimax", random_state=0).fit(tr[["z_" + c for c in S]])
    g = load_green(corrected=True)
    gt = g[g.split == "train"].merge(tr[["pid", "adjustment", "open_nfc"] + ["z_" + c for c in T]], on="pid")
    res["two_clusters"] = {
        "note": "descriptive correlations; the factor solution is exploratory and is not a confirmatory model",
        "scales": S, "raw_r": np.round(raw, 3).tolist(), "partial_r_tierA_removed": np.round(par, 3).tolist(),
        "mean_abs_r": {"raw": dict(within_adjustment=blk(raw, ADJ, ADJ), within_values=blk(raw, VAL, VAL), between=blk(raw, ADJ, VAL)),
                       "tierA_removed": dict(within_adjustment=blk(par, ADJ, ADJ), within_values=blk(par, VAL, VAL), between=blk(par, ADJ, VAL))},
        "composite_r": dict(adjustment_vs_values3=r2(tr.adjustment.corr(tr.values3)), tierA_removed=r2(np.corrcoef(resid(tr.adjustment.to_numpy()), resid(tr.values3.to_numpy()))[0, 1]),
                            green_vs_adjustment=r2(tr.z_green.corr(tr.adjustment)), green_vs_open_nfc=r2(tr.z_green.corr(tr.open_nfc))),
        "tierA_predictability": {"adjustment_composite": cv(tr.adjustment.to_numpy()), "open_nfc_composite": cv(tr.open_nfc.to_numpy()),
                                 **{c: cv(tr["z_" + c].to_numpy()) for c in SCALES}},
        "eigenvalues": np.round(np.linalg.eigvalsh(raw)[::-1], 2).tolist(),
        "two_factor_varimax_loadings": {c: [r2(v) for v in fa.components_[:, i]] for i, c in enumerate(S)},
        "green_choice_n": len(gt),
        "choice_on_composites": odds(smf.logit("chose_green ~ green_default + adjustment + open_nfc", gt).fit(disp=0)),
        "choice_on_composites_plus_green": odds(smf.logit("chose_green ~ green_default + z_green + adjustment + open_nfc", gt).fit(disp=0)),
    }

    hi = gt[gt.green >= 4.0].copy()
    hi["decline"] = 1 - hi.chose_green
    hi["low_inc"], hi["older"] = low_income(hi.income).astype(int), hi.age_band.astype(str).isin(["50-64", "65+"]).astype(int)
    hi["female"] = (hi.sex.astype(str) == "Female").astype(int)
    hi["college"] = hi.education.astype(str).isin(["College graduate/some postgrad", "Postgraduate"]).astype(int)

    def rate(s):
        k, n = int(s.sum()), len(s); lo, h = wilson(k, n)
        return dict(k=k, n=n, rate=r2(k / n), lo=r2(lo), hi=r2(h))

    def diff(a, b):
        d, se = a.mean() - b.mean(), np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
        return dict(diff=r2(d), lo=r2(d - 1.96 * se), hi=r2(d + 1.96 * se))
    block = ["low_inc", "older", "female", "college", "z_spendthrift", "z_crt", "z_neuroticism", "z_conscientiousness", "z_openness",
             "z_need_for_cognition", "z_self_concept_clarity"]
    m0 = smf.logit("decline ~ green_default + z_green", hi).fit(disp=0)
    m1 = smf.logit("decline ~ green_default + z_green + " + " + ".join(block), hi).fit(disp=0)
    lr = 2 * (m1.llf - m0.llf)
    p0 = float(hi.decline.mean())
    grid = np.linspace(p0, .95, 600)
    es = NormalIndPower().solve_power(nobs1=len(hi) / 2, alpha=0.05, power=0.8, ratio=1.0)
    mdd = float(grid[np.argmax(np.array([proportion_effectsize(x, p0) for x in grid]) >= es)] - p0)
    res["say_do_high_green"] = {
        "definition": "green values >= 4.0 (the 67th-percentile cut; 41% of train because of ties); participants in the green experiment",
        "n": len(hi), "decline_by_default": {k: rate(s.decline) for k, s in hi.groupby("green_condition")},
        "default_difference_in_decline": diff(hi[hi.green_default == 0].decline, hi[hi.green_default == 1].decline),
        "decline_by_group": {v: dict(yes=rate(hi[hi[v] == 1].decline), no=rate(hi[hi[v] == 0].decline), **diff(hi[hi[v] == 1].decline, hi[hi[v] == 0].decline))
                             for v in ["low_inc", "older", "female", "college"]},
        "decline_by_tightwad_tercile": {str(k): rate(s.decline) for k, s in hi.groupby(pd.qcut(hi.spendthrift, 3, labels=["tightwad", "middle", "spendthrift"]), observed=True)},
        "joint_test_of_11_demographic_and_trait_terms": dict(lr_chi2=r2(lr), df=len(block), p=r2(stats.chi2.sf(lr, len(block)))),
        "decline_model_odds_ratios": odds(m1),
        "power": dict(note="two equal groups, alpha 0.05, power 0.80", smallest_detectable_difference_in_decline_rate=r2(mdd), base_rate=r2(p0)),
    }
    with open(HERE / "results.json", "w", newline="\n") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: res[k] for k in ("scale_audit", "counterexamples", "say_do_high_green")}, indent=1)[:6000])


if __name__ == "__main__":
    main()
