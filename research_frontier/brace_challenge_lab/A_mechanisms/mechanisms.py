"""Workstream A — why do the personas fit? Mechanism / confounding / composition / response-style checks.

TRAINING SPLIT ONLY (split == 'train', n = 1,442). Corrected social-desirability and CRT scores (load_people(corrected=True)).
No test-split data are analysed here; frozen held-out numbers are only quoted in the markdown deliverables.
Run:  PYTHONUTF8=1 python research_frontier/brace_challenge_lab/A_mechanisms/mechanisms.py
Outputs (same folder): results.csv (long format), results.json (summary blocks).
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "src"))
from common import CONSTRUCTS, RAW_TWIN, SEED, TIER_A, low_income, load_people  # noqa: E402

RNG = np.random.default_rng(SEED)
CAT = RAW_TWIN / "question_catalog_and_human_response_csv"
ROWS: list[dict] = []
SUMMARY: dict = {}


def add(section, persona, construct, model, est, lo, hi, p=np.nan, n_member=np.nan, n_other=np.nan, subgroup="", note=""):
    ROWS.append(dict(section=section, persona=persona, construct=construct, model=model, subgroup=subgroup,
                     n_member=n_member, n_other=n_other, est=est, lo=lo, hi=hi, p=p, note=note))


# ------------------------------------------------------------------ data (train only)
people = load_people(corrected=True)
tr = people[people.split == "train"].copy().reset_index(drop=True)
assert len(tr) == 1442 and (tr.split == "train").all()

# item-level response-style variables (merged by pid; only train pids kept)
num = pd.read_csv(CAT / "wave1_3_response.csv", usecols=["pid"] + [f"QID25_{i}" for i in (4, 9, 14, 19, 24, 29, 34, 39)])
lab = pd.read_csv(CAT / "wave1_3_response_label.csv", usecols=["pid"] + [f"QID27_{i}" for i in range(1, 14)])
N_FWD, N_REV = [4, 14, 19, 29, 39], [9, 24, 34]
items = num[["pid"]].copy()
items["neu_fwd"] = num[[f"QID25_{i}" for i in N_FWD]].mean(axis=1)
items["neu_rev"] = (6 - num[[f"QID25_{i}" for i in N_REV]]).mean(axis=1)
for i in (4, 9, 14, 19, 24, 29, 34, 39):
    items[f"bfi_n{i}"] = num[f"QID25_{i}"] if i in N_FWD else 6 - num[f"QID25_{i}"]
T = {i: lab[f"QID27_{i}"].astype(str).str.strip().str.upper().eq("TRUE").astype(int) for i in range(1, 14)}
items["sd_truekeyed"] = sum(T[i] for i in (5, 7, 9, 10, 13)) / 5            # share desirable among TRUE-keyed
items["sd_falsekeyed"] = sum(1 - T[i] for i in (1, 2, 3, 4, 6, 8, 11, 12)) / 8  # share desirable among FALSE-keyed
items["acq_true_count"] = sum(T[i] for i in range(1, 14))                    # raw count of 'True' answers
tr = tr.merge(items, on="pid", how="left")
assert len(tr) == 1442 and tr.neu_fwd.notna().all()
# sanity: item-derived neuroticism reproduces the score
assert np.allclose((5 * tr.neu_fwd + 3 * tr.neu_rev) / 8, tr.neuroticism)

# standardise every outcome on the TRAIN population (matches persona-report d convention)
OUT = list(CONSTRUCTS) + ["neu_fwd", "neu_rev", "sd_truekeyed", "sd_falsekeyed", "acq_true_count"] + \
      [f"bfi_n{i}" for i in (4, 9, 14, 19, 24, 29, 34, 39)]
for c in OUT:
    tr[c + "_z"] = (tr[c] - tr[c].mean()) / tr[c].std()

tr["P1"] = (tr.age_band == "65+").astype(int)
tr["P2"] = (tr.age_band.isin(["18-29", "30-49"]) & low_income(tr.income)).astype(int)
tr["P3"] = ((tr.age_band == "18-29") & (tr.marital == "Never been married")).astype(int)
tr["lowinc"] = low_income(tr.income).astype(int)
tr["ba"] = tr.education.isin(["College graduate/some postgrad", "Postgraduate"]).astype(int)
tr["male"] = (tr.sex == "Male").astype(int)
tr["white"] = (tr.race == "White").astype(int)
tr["age_num"] = tr.age_band.astype(str).map({"18-29": 0, "30-49": 1, "50-64": 2, "65+": 3}).astype(int)
tr["region5"] = tr.region.astype(str).str.split(" ").str[0]
tr["student"] = (tr.employment == "Student").astype(int)
SUMMARY["n_train"] = len(tr)
SUMMARY["persona_n_train"] = {p: int(tr[p].sum()) for p in ("P1", "P2", "P3")}

# defining variables per persona (excluded from adjustment sets); citizen dropped (4 'No' in whole panel)
DEF = {"P1": {"age_band"}, "P2": {"age_band", "income"}, "P3": {"age_band", "marital"}}
BASE_COV = ["region5", "sex", "education", "race", "marital", "income", "hh_size"]
TARGETS = {"P1": ["neuroticism", "social_desirability", "spendthrift", "green"],
           "P2": ["neuroticism", "social_desirability", "green"],
           "P3": ["neuroticism", "green", "social_desirability"]}


def ols(formula, data, term):
    f = smf.ols(formula, data).fit(cov_type="HC3")
    ci = f.conf_int().loc[term]
    return float(f.params[term]), float(ci[0]), float(ci[1]), float(f.pvalues[term])


def cov_terms(p, extra=()):
    return " + ".join(f"C({c})" for c in BASE_COV if c not in DEF[p]) + "".join(f" + {e}" for e in extra)


# ------------------------------------------------------------------ 1. adjustment for observable confounders
for p, cons in TARGETS.items():
    for c in CONSTRUCTS:
        y = c + "_z"
        m = tr[p] == 1
        d_pop = (tr.loc[m, c].mean() - tr[c].mean()) / tr[c].std()
        add("1_adjust", p, c, "d_vs_population (frozen convention, reproduces train d)", d_pop, np.nan, np.nan,
            n_member=int(m.sum()), n_other=len(tr) - int(m.sum()))
        e = ols(f"{y} ~ {p}", tr, p)
        add("1_adjust", p, c, "m0 member vs non-member", *e, n_member=int(m.sum()), n_other=int((~m).sum()))
        e = ols(f"{y} ~ {p} + {cov_terms(p)}", tr, p)
        add("1_adjust", p, c, "m1 + non-defining Tier A (region,sex,educ,race,marital,income,hh_size)", *e)
        e = ols(f"{y} ~ {p} + {cov_terms(p)} + C(employment)", tr, p)
        add("1_adjust", p, c, "m2 = m1 + employment (possible mediator)", *e)
        if c != "social_desirability":
            e = ols(f"{y} ~ {p} + {cov_terms(p)} + social_desirability_z", tr, p)
            add("1_adjust", p, c, "m3 = m1 + social desirability (style OR substance)", *e)
        if p == "P2":  # within-age-band contrast for the income component
            e = ols(f"{y} ~ lowinc + C(age_band) + {' + '.join(f'C({v})' for v in BASE_COV if v != 'income')}",
                    tr[tr.age_band.isin(['18-29', '30-49'])], "lowinc")
            add("1_adjust", p, c, "m4 within 18-49: low income vs not, adj age band + Tier A", *e)
        if p == "P3":  # within 18-29: never married vs other marital statuses
            sub = tr[tr.age_band == "18-29"]
            e = ols(f"{y} ~ P3", sub, "P3")
            add("1_adjust", p, c, "m5 within 18-29: never-married vs other (unadjusted)", *e,
                n_member=int(sub.P3.sum()), n_other=int((sub.P3 == 0).sum()))
            e = ols(f"{y} ~ P3 + C(sex) + C(income) + C(education) + C(race) + C(region5) + C(hh_size)", sub, "P3")
            add("1_adjust", p, c, "m6 within 18-29, adj sex,income,educ,race,region,hh_size", *e)
            e = ols(f"{y} ~ P3 + C(sex) + C(income) + C(education) + C(race) + C(region5) + C(hh_size) + C(employment)",
                    sub, "P3")
            add("1_adjust", p, c, "m7 = m6 + employment (incl. student)", *e)
            if c == "green":
                e = ols(f"{y} ~ P3 + C(sex) + C(income) + C(education) + C(race) + C(region5) + C(hh_size) + C(party)",
                        sub, "P3")
                add("1_adjust", p, c, "m8 SENSITIVITY (non-Tier-A): m6 + party", *e)
                e = ols(f"{y} ~ P3 + {cov_terms(p)} + C(party)", tr, p)
                add("1_adjust", p, c, "m9 SENSITIVITY (non-Tier-A): m1 + party", *e)

# P1 neuroticism with BOTH social desirability and employment
e = ols(f"neuroticism_z ~ P1 + {cov_terms('P1')} + C(employment) + social_desirability_z", tr, "P1")
add("1_adjust", "P1", "neuroticism", "m10 = m1 + employment + social desirability", *e)

# ------------------------------------------------------------------ 2. subgroup reversals
def diff_ci(a, b, B=2000):
    a, b = np.asarray(a, float), np.asarray(b, float)
    est = a.mean() - b.mean()
    bs = [RNG.choice(a, len(a)).mean() - RNG.choice(b, len(b)).mean() for _ in range(B)]
    return est, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


SUBGROUPS = {
    "sex=Male": tr.sex == "Male", "sex=Female": tr.sex == "Female",
    "income<50k": tr.lowinc == 1, "income>=50k": tr.lowinc == 0,
    "BA+": tr.ba == 1, "no BA": tr.ba == 0,
    "race=White": tr.race == "White", "race=Black": tr.race == "Black", "race=Hispanic": tr.race == "Hispanic",
    "race=Asian": tr.race == "Asian", "race=non-White": tr.race != "White",
}
for p, cons in TARGETS.items():
    for c in cons:
        for g, gm in SUBGROUPS.items():
            if p == "P2" and g.startswith("income"):
                continue  # income defines P2
            sub = tr[gm]
            a, b = sub.loc[sub[p] == 1, c + "_z"], sub.loc[sub[p] == 0, c + "_z"]
            if len(a) < 20:
                add("2_subgroup", p, c, "member - non-member (z), bootstrap CI", np.nan, np.nan, np.nan,
                    n_member=len(a), n_other=len(b), subgroup=g, note="n_member < 20: not estimated")
                continue
            est, lo, hi = diff_ci(a, b)
            add("2_subgroup", p, c, "member - non-member (z), bootstrap CI", est, lo, hi,
                n_member=len(a), n_other=len(b), subgroup=g)
        # formal interaction tests
        for mod in ("male", "lowinc", "ba", "white"):
            if p == "P2" and mod == "lowinc":
                continue
            f = smf.ols(f"{c}_z ~ {p} * {mod}", tr).fit(cov_type="HC3")
            t = f"{p}:{mod}"
            ci = f.conf_int().loc[t]
            add("2_interaction", p, c, f"{p} x {mod} interaction (z)", float(f.params[t]), float(ci[0]),
                float(ci[1]), float(f.pvalues[t]))
# P3 within 18-29, by sex (the memo's composition claim), never-married vs other 18-29
for c in ("green", "neuroticism", "social_desirability"):
    for g in ("Male", "Female"):
        sub = tr[(tr.age_band == "18-29") & (tr.sex == g)]
        a, b = sub.loc[sub.P3 == 1, c + "_z"], sub.loc[sub.P3 == 0, c + "_z"]
        est, lo, hi = diff_ci(a, b)
        add("2_subgroup", "P3", c, "within 18-29: never-married - other (z)", est, lo, hi, n_member=len(a),
            n_other=len(b), subgroup=f"sex={g}")
    sub = tr[tr.age_band == "18-29"]
    f = smf.ols(f"{c}_z ~ P3 * male", sub).fit(cov_type="HC3")
    ci = f.conf_int().loc["P3:male"]
    add("2_interaction", "P3", c, "within 18-29: never-married x male (z)", float(f.params["P3:male"]),
        float(ci[0]), float(ci[1]), float(f.pvalues["P3:male"]))

# ------------------------------------------------------------------ 3. age-band shape (4 bands only)
for c in list(CONSTRUCTS) + ["neu_fwd", "neu_rev", "sd_truekeyed", "sd_falsekeyed", "acq_true_count"]:
    for band in ["18-29", "30-49", "50-64", "65+"]:
        s = tr.loc[tr.age_band == band, c + "_z"]
        se = s.std() / np.sqrt(len(s))
        add("3_age_shape", "all", c, "band mean (z)", s.mean(), s.mean() - 1.96 * se, s.mean() + 1.96 * se,
            n_member=len(s), subgroup=band)
    lin = smf.ols(f"{c}_z ~ age_num", tr).fit()
    cat = smf.ols(f"{c}_z ~ C(age_band)", tr).fit()
    F = ((lin.ssr - cat.ssr) / 2) / (cat.ssr / cat.df_resid)
    from scipy import stats
    pF = float(1 - stats.f.cdf(F, 2, cat.df_resid))
    ci = lin.conf_int().loc["age_num"]
    add("3_age_shape", "all", c, "linear trend per band step (z); p = departure-from-linearity F(2,df)",
        float(lin.params.age_num), float(ci[0]), float(ci[1]), pF)
    # adjusted for Tier A non-age
    adj = smf.ols(f"{c}_z ~ age_num + C(sex) + C(education) + C(race) + C(income) + C(marital) + C(region5) + C(hh_size)",
                  tr).fit(cov_type="HC3")
    ci = adj.conf_int().loc["age_num"]
    add("3_age_shape", "all", c, "linear trend per band step, adj non-age Tier A (z)", float(adj.params.age_num),
        float(ci[0]), float(ci[1]), float(adj.pvalues.age_num))

# age x income interaction for neuroticism (is income gradient the same at every age?)
for band in ["18-29", "30-49", "50-64", "65+"]:
    sub = tr[tr.age_band == band]
    est, lo, hi = diff_ci(sub.loc[sub.lowinc == 1, "neuroticism_z"], sub.loc[sub.lowinc == 0, "neuroticism_z"])
    add("3_age_shape", "all", "neuroticism", "low income - other within band (z)", est, lo, hi,
        n_member=int(sub.lowinc.sum()), n_other=int((sub.lowinc == 0).sum()), subgroup=band)

# ------------------------------------------------------------------ 4. composition decompositions
def band_mean(c):
    return tr.groupby("age_band")[c + "_z"].mean()


# P2: how much of P2's neuroticism d is age composition vs income-within-age?
p2 = tr[tr.P2 == 1]
for c in ("neuroticism", "social_desirability", "green"):
    total = p2[c + "_z"].mean()
    age_expected = (p2.age_band.value_counts(normalize=True) * band_mean(c)).dropna().sum()
    add("4_composition", "P2", c, "P2 mean z (vs pop)", total, np.nan, np.nan, n_member=len(p2))
    add("4_composition", "P2", c, "expected from age-band mix alone", age_expected, np.nan, np.nan,
        note="sum_b share_b(P2) * mean_z(band b, all incomes)")
    add("4_composition", "P2", c, "remainder = income-within-age", total - age_expected, np.nan, np.nan)
    for band in ["18-29", "30-49"]:
        s = p2.loc[p2.age_band == band, c + "_z"]
        se = s.std() / np.sqrt(len(s))
        add("4_composition", "P2", c, "P2 mean z within band", s.mean(), s.mean() - 1.96 * se, s.mean() + 1.96 * se,
            n_member=len(s), subgroup=band)
    s = p2.loc[p2.student == 0, c + "_z"]
    se = s.std() / np.sqrt(len(s))
    add("4_composition", "P2", c, "P2 mean z excluding students", s.mean(), s.mean() - 1.96 * se,
        s.mean() + 1.96 * se, n_member=len(s))
SUMMARY["P2_share_18_29"] = float((p2.age_band == "18-29").mean())
SUMMARY["P2_share_unemployed"] = float((p2.employment == "Unemployed").mean())
SUMMARY["pop_share_unemployed"] = float((tr.employment == "Unemployed").mean())
SUMMARY["P2_share_students"] = float(p2.student.mean())

# bootstrap CI for P2 decomposition (neuroticism)
bs = []
for _ in range(2000):
    t = tr.iloc[RNG.integers(0, len(tr), len(tr))]
    bm = t.groupby("age_band")["neuroticism_z"].mean()
    q = t[t.P2 == 1]
    tot = q.neuroticism_z.mean()
    ae = (q.age_band.value_counts(normalize=True) * bm).dropna().sum()
    bs.append((tot, ae, tot - ae))
bs = np.array(bs)
SUMMARY["P2_neuro_decomp_bootCI"] = {k: [float(np.percentile(bs[:, i], 2.5)), float(np.percentile(bs[:, i], 97.5))]
                                     for i, k in enumerate(["total", "age_mix", "income_within_age"])}

# P3 green: sex composition and other composition
y29 = tr[tr.age_band == "18-29"]
SUMMARY["P3_composition"] = {
    "share_male_P3": float(y29[y29.P3 == 1].male.mean()), "share_male_other18_29": float(y29[y29.P3 == 0].male.mean()),
    "share_student_P3": float(y29[y29.P3 == 1].student.mean()),
    "share_lowinc_P3": float(y29[y29.P3 == 1].lowinc.mean()), "share_lowinc_other18_29": float(y29[y29.P3 == 0].lowinc.mean()),
    "share_BA_P3": float(y29[y29.P3 == 1].ba.mean()), "share_BA_other18_29": float(y29[y29.P3 == 0].ba.mean()),
    "share_hh1_P3": float((y29[y29.P3 == 1].hh_size == "1").mean()),
    "share_republican_P3": float((y29[y29.P3 == 1].party == "Republican").mean()),
    "share_republican_other18_29": float((y29[y29.P3 == 0].party == "Republican").mean()),
    "marital_other18_29": y29[y29.P3 == 0].marital.value_counts().to_dict(),
    "n_18_29": len(y29), "n_P3": int(y29.P3.sum()),
}
for c in ("green", "neuroticism"):
    gm = y29.groupby(["P3", "sex"], observed=True)[c + "_z"].mean()
    raw_gap = y29.loc[y29.P3 == 1, c + "_z"].mean() - y29.loc[y29.P3 == 0, c + "_z"].mean()
    # sex-standardised gap: average of within-sex gaps weighted by the 18-29 sex mix
    w = y29.sex.value_counts(normalize=True)
    std_gap = sum(w[s] * (gm[(1, s)] - gm[(0, s)]) for s in ("Male", "Female"))
    # gap explained by sex mix = P3 mean if it had the other group's sex mix
    p3_reweighted = sum(y29[y29.P3 == 0].sex.value_counts(normalize=True)[s] * gm[(1, s)] for s in ("Male", "Female"))
    add("4_composition", "P3", c, "within 18-29: raw never-married gap (z)", raw_gap, np.nan, np.nan)
    add("4_composition", "P3", c, "within 18-29: sex-standardised gap (z)", std_gap, np.nan, np.nan)
    add("4_composition", "P3", c, "within 18-29: gap if P3 had other-18-29 sex mix", p3_reweighted -
        y29.loc[y29.P3 == 0, c + "_z"].mean(), np.nan, np.nan)
    for (k, s), v in gm.items():
        add("4_composition", "P3", c, "cell mean z", v, np.nan, np.nan,
            n_member=int(((y29.P3 == k) & (y29.sex == s)).sum()), subgroup=f"P3={k}, sex={s}")
# who drives the gap: other 18-29 by marital status green means
for mst, s in y29.groupby("marital", observed=True):
    sm = s.green_z
    se = sm.std() / np.sqrt(len(sm)) if len(sm) > 1 else np.nan
    add("4_composition", "P3", "green", "18-29 green mean z by marital status", sm.mean(), sm.mean() - 1.96 * se,
        sm.mean() + 1.96 * se, n_member=len(sm), subgroup=mst)
for mst in ["Never been married", "Married", "Living with a partner", "Divorced"]:
    for band in ["18-29", "30-49", "50-64"]:
        s = tr[(tr.age_band == band) & (tr.marital == mst)].green_z
        if len(s) >= 20:
            se = s.std() / np.sqrt(len(s))
            add("4_composition", "P3", "green", "green mean z by marital x band", s.mean(), s.mean() - 1.96 * se,
                s.mean() + 1.96 * se, n_member=len(s), subgroup=f"{band}|{mst}")

# P1 composition: retired share, education, and within-65+ retired vs not
p1 = tr[tr.P1 == 1]
SUMMARY["P1_composition"] = {"share_retired": float((p1.employment == "Retired").mean()),
                             "share_BA": float(p1.ba.mean()), "share_BA_under65": float(tr[tr.P1 == 0].ba.mean()),
                             "share_male": float(p1.male.mean()), "share_white": float(p1.white.mean()),
                             "share_white_under65": float(tr[tr.P1 == 0].white.mean()),
                             "share_lowinc": float(p1.lowinc.mean()), "share_married": float((p1.marital == "Married").mean())}
for band in ["50-64", "65+"]:
    sub = tr[tr.age_band == band]
    r = sub.employment == "Retired"
    if r.sum() >= 20 and (~r).sum() >= 20:
        est, lo, hi = diff_ci(sub.loc[r, "neuroticism_z"], sub.loc[~r, "neuroticism_z"])
        add("4_composition", "P1", "neuroticism", "retired - not retired (z), within band", est, lo, hi,
            n_member=int(r.sum()), n_other=int((~r).sum()), subgroup=band)

# ------------------------------------------------------------------ 5. response style / measurement checks
for p in ("P1", "P2", "P3"):
    for c in ("neu_fwd", "neu_rev", "sd_truekeyed", "sd_falsekeyed", "acq_true_count"):
        e = ols(f"{c}_z ~ {p}", tr, p)
        add("5_response_style", p, c, "member vs non-member (z)", *e, n_member=int(tr[p].sum()))
        e = ols(f"{c}_z ~ {p} + {cov_terms(p)}", tr, p)
        add("5_response_style", p, c, "m1 adjusted (z)", *e)
    for i in (4, 9, 14, 19, 24, 29, 34, 39):
        e = ols(f"bfi_n{i}_z ~ {p}", tr, p)
        add("5_response_style", p, f"bfi_n{i}{'R' if i in N_REV else ''}", "item member vs non-member (z)", *e)
SUMMARY["corr_sd_neuroticism_train"] = float(tr.social_desirability.corr(tr.neuroticism))
SUMMARY["corr_sd_green_train"] = float(tr.social_desirability.corr(tr.green))
SUMMARY["corr_acq_sd_train"] = float(tr.acq_true_count.corr(tr.social_desirability))
SUMMARY["corr_neufwd_neurev_train"] = float(tr.neu_fwd.corr(tr.neu_rev))

# ------------------------------------------------------------------ write
res = pd.DataFrame(ROWS)
for c in ("est", "lo", "hi", "p"):
    res[c] = res[c].astype(float).round(4)
res.to_csv(HERE / "results.csv", index=False)
json.dump(SUMMARY, open(HERE / "results.json", "w"), indent=1, default=float)
print(f"wrote {len(res)} rows; train n = {len(tr)}")
