"""Workstream C: re-assessment of the "say-do gap" claim (default_eric green-energy choice).

TRAINING participants only (split == 'train'). Frozen held-out numbers are quoted from results/ only, never recomputed.
Seed 20261114. Local CPU only. Writes only into this folder.

Run from repo root:  PYTHONUTF8=1 python research_frontier/brace_challenge_lab/C_saydo/saydo_reassessment.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from scipy.integrate import trapezoid
import warnings
warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "src"))
from common import RAW_TWIN, SEED, load_green, load_people, low_income, wilson  # noqa: E402

B = int(__import__("os").environ.get("NBOOT", 1000))  # override only for smoke tests
rng = np.random.default_rng(SEED)
OUT = {}
EXT = ROOT / "research_frontier/overnight/external/default_eric"
CAT = RAW_TWIN / "question_catalog_and_human_response_csv"
GREEN_ITEMS = [f"QID235_{i}" for i in range(1, 7)]

# ------------------------------------------------------------------ data
cat = {q["QuestionID"]: q for q in json.load(open(CAT / "question_catalog.json", encoding="utf-8"))}
OUT["green_items"] = dict(zip(cat["QID235"]["csv_columns"], cat["QID235"]["Rows"]))
OUT["green_response_scale"] = cat["QID235"]["Columns"]

twin = pd.read_csv(CAT / "wave1_3_response.csv", usecols=["pid", *GREEN_ITEMS, "QID287_3"])
people = load_people(corrected=True)
tw_train = twin.merge(people[["pid", "split", "green"]], on="pid")
tw_train = tw_train[tw_train.split == "train"]
assert np.allclose(tw_train[GREEN_ITEMS].mean(axis=1), tw_train.green), "GREEN != mean of QID235 items"

# survey order (green block first vs organ block first) from the raw Qualtrics display-order columns
raw = pd.read_csv(EXT / "response.csv", low_memory=False).iloc[2:]
order = pd.DataFrame({"pid": pd.to_numeric(raw.TWIN_ID, errors="coerce"),
                      "green_first": raw.FL_344_DO_FL_345.notna().astype(int)}).dropna()
order["pid"] = order.pid.astype(int)
start_dates = pd.to_datetime(raw.StartDate, errors="coerce")
OUT["mega_fielding_dates"] = [str(start_dates.min().date()), str(start_dates.max().date())]
try:
    w1 = pd.read_csv(RAW_TWIN / "raw_data/wave_1_labels_anonymized.csv", usecols=["StartDate"], low_memory=False)
    d1 = pd.to_datetime(w1.StartDate, errors="coerce").dropna()
    OUT["twin_wave1_dates"] = [str(d1.min().date()), str(d1.max().date())]
except Exception as e:  # noqa: BLE001
    OUT["twin_wave1_dates"] = f"unavailable: {e}"

org = pd.read_parquet(ROOT / "data/processed/mega_default_eric.parquet")[["pid", "organ_condition", "organ_donor"]]
org["pid"] = org.pid.astype(int)

g = load_green(corrected=True)
g = g[g.split == "train"].merge(order, on="pid", how="left").merge(org, on="pid", how="left") \
    .merge(twin[["pid", *GREEN_ITEMS, "QID287_3"]], on="pid", how="left")
assert len(g) == 428 and g.green_first.notna().all()
mu, sd = g.green.mean(), g.green.std(ddof=1)
g["green_z"] = (g.green - mu) / sd
g["low_inc"] = low_income(g.income).astype(int)
# Tier A, sparse levels collapsed (documented): Pacific->West, <HS->HS, Separated->Divorced, Student/Home-maker->Other;
# citizenship dropped (1 non-citizen in this sample).
g["region_c"] = g.region.astype(str).str.split(" ").str[0].replace({"Pacific": "West"})
g["edu_c"] = g.education.astype(str).replace({"Less than high school": "High school graduate"})
g["marital_c"] = g.marital.astype(str).replace({"Separated": "Divorced"})
g["emp_c"] = g.employment.astype(str).replace({"Student": "Other", "Home-maker": "Other"})
g["ba_plus"] = g.education.astype(str).isin(["College graduate/some postgrad", "Postgraduate"]).astype(int)
for c in ["sex", "age_band", "race", "income", "hh_size"]:
    g[c] = g[c].astype(str)
TIER = "C(region_c) + C(sex) + C(age_band) + C(edu_c) + C(race) + C(marital_c) + C(income) + C(hh_size) + C(emp_c)"
OUT["n_train"] = len(g)
OUT["green_mu_sd_train"] = [mu, sd]


def boot(fn, df, n=B):
    vals = []
    for _ in range(n):
        b = df.sample(len(df), replace=True, random_state=int(rng.integers(1 << 31)))
        try:
            vals.append(fn(b))
        except Exception:  # noqa: BLE001  (separation / singular resample)
            continue
    return pd.DataFrame(vals)


def summar(point: dict, bt: pd.DataFrame) -> dict:
    return {k: dict(est=float(v), lo=float(bt[k].quantile(.025)), hi=float(bt[k].quantile(.975)),
                    n_boot_ok=int(bt[k].notna().sum())) for k, v in point.items()}


def p(fit, d):
    return float(fit.predict(d).mean())


# ------------------------------------------------------------------ 1. reliability of GREEN
def alpha(X: pd.DataFrame) -> float:
    k = X.shape[1]
    return k / (k - 1) * (1 - X.var(ddof=1).sum() / X.sum(axis=1).var(ddof=1))


Xall = tw_train[GREEN_ITEMS]
a_boot = [alpha(Xall.sample(len(Xall), replace=True, random_state=int(rng.integers(1 << 31)))) for _ in range(B)]
OUT["alpha_all_train"] = dict(n=len(Xall), est=alpha(Xall), lo=float(np.quantile(a_boot, .025)),
                              hi=float(np.quantile(a_boot, .975)))
OUT["alpha_choice_sample"] = dict(n=len(g), est=alpha(g[GREEN_ITEMS]))
tot = Xall.sum(axis=1)
OUT["item_rest_r"] = {c: float(np.corrcoef(Xall[c], tot - Xall[c])[0, 1]) for c in GREEN_ITEMS}
OUT["alpha_if_dropped"] = {c: alpha(Xall.drop(columns=c)) for c in GREEN_ITEMS}
OUT["green_ceiling_share_eq5"] = float((g.green == 5).mean())
OUT["green_skew"] = float(stats.skew(g.green))

# ------------------------------------------------------------------ 2. Tier-A adjusted model, AMEs
F_MAIN = f"chose_green ~ green_z + green_default + {TIER}"
F_INT = f"chose_green ~ green_z * green_default + {TIER}"


def ame_main(d):
    f = smf.logit(F_MAIN, d).fit(disp=0, maxiter=200)
    return {"ame_green_1sd": p(f, d.assign(green_z=d.green_z + 1)) - p(f, d),
            "ame_default": p(f, d.assign(green_default=1)) - p(f, d.assign(green_default=0))}


fit_main = smf.logit(F_MAIN, g).fit(disp=0, maxiter=200)
OUT["tierA_model"] = dict(formula=F_MAIN, pseudo_r2=float(fit_main.prsquared),
                          OR_green=float(np.exp(fit_main.params.green_z)),
                          OR_green_ci=[float(x) for x in np.exp(fit_main.conf_int().loc["green_z"])],
                          OR_default=float(np.exp(fit_main.params.green_default)),
                          OR_default_ci=[float(x) for x in np.exp(fit_main.conf_int().loc["green_default"])])
bt = boot(ame_main, g)
OUT["tierA_ames"] = summar(ame_main(g), bt)
# unadjusted comparator (same sample, no Tier A)
fu = smf.logit("chose_green ~ green_z + green_default", g).fit(disp=0)
OUT["unadjusted_ame_green_1sd"] = p(fu, g.assign(green_z=g.green_z + 1)) - p(fu, g)


# ------------------------------------------------------------------ 3. GREEN x default on the probability scale
def ame_int(d):
    f = smf.logit(F_INT, d).fit(disp=0, maxiter=200)
    out = {}
    for c, nm in ((0, "grey"), (1, "green")):
        s = d.assign(green_default=c)
        out[f"ame_green_1sd_{nm}def"] = p(f, s.assign(green_z=s.green_z + 1)) - p(f, s)
    out["diff_green_minus_grey"] = out["ame_green_1sd_greendef"] - out["ame_green_1sd_greydef"]
    out["OR_interaction"] = float(np.exp(f.params["green_z:green_default"]))
    # default effect at low (-1SD) vs high (+1SD) GREEN
    for z, nm in ((-1, "lowgreen"), (1, "highgreen")):
        s = d.assign(green_z=z)
        out[f"default_effect_at_{nm}"] = p(f, s.assign(green_default=1)) - p(f, s.assign(green_default=0))
    return out


bt = boot(ame_int, g)
OUT["interaction_prob_scale_tierA"] = summar(ame_int(g), bt)
# linear probability model check (robust SE)
lpm = smf.ols(f"chose_green ~ green_z * green_default + {TIER}", g).fit(cov_type="HC3")
OUT["lpm_interaction"] = dict(coef=float(lpm.params["green_z:green_default"]),
                              ci=[float(x) for x in lpm.conf_int().loc["green_z:green_default"]],
                              slope_grey=float(lpm.params.green_z))

# ------------------------------------------------------------------ 4. order / organ-block contamination checks
chk = {}
for term, f in {"green_first": "chose_green ~ green_default * green_first + green_z",
                "organ_donor_default": "chose_green ~ green_default * C(organ_condition) + green_z",
                "greenz_x_first": "chose_green ~ green_z * green_first + green_default"}.items():
    ff = smf.logit(f, g).fit(disp=0)
    chk[term] = {k: dict(OR=float(np.exp(v)), p=float(ff.pvalues[k])) for k, v in ff.params.items() if k != "Intercept"}
chk["rates_by_order_condition"] = g.groupby(["green_first", "green_condition"]).chose_green.agg(["size", "mean"]) \
    .reset_index().to_dict("records")
OUT["contamination_checks"] = chk

# ------------------------------------------------------------------ 5. subgroup heterogeneity of the GREEN slope
subdefs = {"age": ("age_band", None), "income": ("low_inc", None), "sex": ("sex", None), "education": ("ba_plus", None)}
sub = {}
pvals = {}
for name, (var, _) in subdefs.items():
    f_full = f"chose_green ~ green_z * C({var}) + green_default + {TIER}"
    f_red = f"chose_green ~ green_z + green_default + {TIER}"
    full, red = smf.logit(f_full, g).fit(disp=0, maxiter=200), smf.logit(f_red, g).fit(disp=0, maxiter=200)
    lr = 2 * (full.llf - red.llf)
    dfd = full.df_model - red.df_model
    pvals[name] = float(stats.chi2.sf(lr, dfd))
    levels = sorted(g[var].unique())

    def fn(d, var=var, f_full=f_full, levels=levels):
        ft = smf.logit(f_full, d).fit(disp=0, maxiter=200)
        o = {}
        for L in levels:
            s = d[d[var] == L]
            o[f"{var}={L}"] = p(ft, s.assign(green_z=s.green_z + 1)) - p(ft, s)
        return o

    bt = boot(fn, g, n=min(500, B))
    res = summar(fn(g), bt)
    for L in levels:
        res[f"{var}={L}"]["n"] = int((g[var] == L).sum())
    sub[name] = dict(lr_test_p=pvals[name], ames=res)
ps = pd.Series(pvals).sort_values()
m = len(ps)
holm = {k: float(min(1.0, max((m - j) * ps.iloc[j] for j in range(i + 1)))) for i, k in enumerate(ps.index)}
for k in sub:
    sub[k]["holm_p"] = holm[k]
OUT["subgroups"] = sub

# ------------------------------------------------------------------ 6. content overlap: item-level & reduced scale
items = {}
for c in GREEN_ITEMS:
    d = g.assign(iz=(g[c] - g[c].mean()) / g[c].std())
    f = smf.logit(f"chose_green ~ iz + green_default + {TIER}", d).fit(disp=0, maxiter=200)
    items[c] = dict(text=OUT["green_items"][c], OR=float(np.exp(f.params.iz)),
                    ame_1sd=p(f, d.assign(iz=d.iz + 1)) - p(f, d))
OUT["item_level"] = items
g["green4"] = g[["QID235_1", "QID235_2", "QID235_4", "QID235_5"]].mean(axis=1)  # drop purchase(3) & inconvenience(6)
d = g.assign(g4z=(g.green4 - g.green4.mean()) / g.green4.std())


def ame4(d):
    f = smf.logit(f"chose_green ~ g4z + green_default + {TIER}", d).fit(disp=0, maxiter=200)
    return {"ame_green4_1sd": p(f, d.assign(g4z=d.g4z + 1)) - p(f, d)}


OUT["reduced_scale_no_behavioural_items"] = summar(ame4(d), boot(ame4, d, n=min(500, B)))
# a different method/content: policy support for carbon-free electricity by 2035 (Twin QID287_3)
d = g.dropna(subset=["QID287_3"]).assign(pz=lambda x: (x.QID287_3 - x.QID287_3.mean()) / x.QID287_3.std())
f = smf.logit(f"chose_green ~ pz + green_default + {TIER}", d).fit(disp=0, maxiter=200)
OUT["policy_item_carbonfree_electricity"] = dict(n=len(d), OR=float(np.exp(f.params.pz)),
                                                 ame_1sd=p(f, d.assign(pz=d.pz + 1)) - p(f, d),
                                                 r_with_green=float(np.corrcoef(d.QID287_3, d.green)[0, 1]))

# ------------------------------------------------------------------ 7. "gap" threshold sensitivity (descriptive)
thr = {}
grey, gr = g[g.green_condition == "grey_default"], g[g.green_condition == "green_default"]
defs = {"top 10% (>= p90)": g.green.quantile(.9), "top 20% (>= p80)": g.green.quantile(.8),
        "frozen 'top third' (>= p66.7)": g.green.quantile(2 / 3), "above median": g.green.quantile(.5),
        "mean >= 4.5 ('agree' on avg)": 4.5, "GREEN == 5 (all 'agree strongly')": 5.0}
for k, t in defs.items():
    row = {"threshold": float(t), "share_of_sample": float((g.green >= t).mean())}
    for nm, s in (("grey", grey), ("green", gr)):
        s = s[s.green >= t]
        k_dec = int((1 - s.chose_green).sum())
        lo, hi = wilson(k_dec, len(s))
        row[f"{nm}_default"] = dict(n=len(s), decline=k_dec / len(s) if len(s) else np.nan, lo=lo, hi=hi)
    thr[k] = row
# every item >= 4 ("agree a little" or more on all six)
s_all = g[(g[GREEN_ITEMS] >= 4).all(axis=1)]
for nm in ("grey_default", "green_default"):
    s = s_all[s_all.green_condition == nm]
    k_dec = int((1 - s.chose_green).sum())
    thr.setdefault("all six items >= 4", {"share_of_sample": float(len(s_all) / len(g))})[nm] = \
        dict(n=len(s), decline=k_dec / len(s), ci=wilson(k_dec, len(s)))
OUT["gap_threshold_sensitivity"] = thr
# frozen-claim check: the "top third" actually contains this share of the sample
OUT["frozen_top_third_actual_share"] = float((g.green >= g.green.quantile(2 / 3)).mean())
# default effect within the frozen top-third group (causal, randomised)
top = g[g.green >= g.green.quantile(2 / 3)]
pg, pr = top[top.green_default == 1].chose_green.mean(), top[top.green_default == 0].chose_green.mean()
btd = []
for _ in range(B):
    b = top.sample(len(top), replace=True, random_state=int(rng.integers(1 << 31)))
    btd.append(b[b.green_default == 1].chose_green.mean() - b[b.green_default == 0].chose_green.mean())
OUT["default_effect_in_top_third"] = dict(n=len(top), est=float(pg - pr), lo=float(np.quantile(btd, .025)),
                                          hi=float(np.quantile(btd, .975)))

# ------------------------------------------------------------------ 8. attenuation / perfect-measurement bound
# Grey-default arm only. Probit P(green) = Phi(a + b*X). Classical error on standardised scale:
# X = sqrt(r) T + sqrt(1-r) e, T ~ N(0,1). Then b_obs = b_T sqrt(r) / sqrt(1 + b_T^2 (1-r)), a_obs = a_T / sqrt(1 + b_T^2 (1-r)).
# Invert; then decline share among top third of TRUE T = E[1 - Phi(a_T + b_T T) | T > z_{2/3}].
zq = stats.norm.ppf(2 / 3)
tgrid = np.linspace(zq, 6, 4001)
wts = stats.norm.pdf(tgrid) / (1 - stats.norm.cdf(zq))


def decline_true(a_o, b_o, r):
    den = r - b_o ** 2 * (1 - r)
    if den <= 0:
        return np.nan, np.nan
    bT = b_o / np.sqrt(den)
    aT = a_o * np.sqrt(1 + bT ** 2 * (1 - r))
    return float(trapezoid((1 - stats.norm.cdf(aT + bT * tgrid)) * wts, tgrid)), float(bT)


def att(d, rs=(1.0, 0.89, 0.80, 0.70, 0.60)):
    dz = d.assign(xz=(d.green - d.green.mean()) / d.green.std())
    f = smf.probit("chose_green ~ xz", dz).fit(disp=0)
    out = {}
    for r in rs:
        v, bT = decline_true(f.params.Intercept, f.params.xz, r)
        out[f"decline_top_third_true_r{r:.2f}"] = v
        out[f"probit_slope_true_r{r:.2f}"] = bT
    return out


gg = grey.copy()
OUT["attenuation_grey_arm"] = summar(att(gg), boot(att, gg))
OUT["attenuation_note"] = ("r=1.00 is the model-based decline among top-third of OBSERVED GREEN under a normal latent; "
                           "r=alpha (~0.89) corrects for item-sampling error only; 0.80-0.60 represent additional "
                           "transient/occasion error over the 3-5 month gap (no retest of GREEN exists, so not identified).")

json.dump(OUT, open(HERE / "saydo_reassessment_results.json", "w"), indent=1, default=float)

# compact console summary
print(json.dumps({k: OUT[k] for k in ["alpha_all_train", "tierA_ames", "unadjusted_ame_green_1sd",
                                      "interaction_prob_scale_tierA", "lpm_interaction",
                                      "default_effect_in_top_third", "frozen_top_third_actual_share",
                                      "reduced_scale_no_behavioural_items", "policy_item_carbonfree_electricity",
                                      "mega_fielding_dates", "twin_wave1_dates"]}, indent=1, default=float))
print(pd.DataFrame({k: {"OR": v["OR"], "ame": v["ame_1sd"]} for k, v in items.items()}).T.round(3))
for k, v in sub.items():
    print(k, "LR p", round(v["lr_test_p"], 3), "holm", round(v["holm_p"], 3),
          {kk: (round(vv["est"], 3), round(vv["lo"], 3), round(vv["hi"], 3), vv["n"]) for kk, vv in v["ames"].items()})
for k, v in thr.items():
    print(k, json.dumps(v, default=float))
print(json.dumps(OUT["contamination_checks"], default=float, indent=0)[:2500])
print(json.dumps(OUT["attenuation_grey_arm"], indent=0, default=float))
print("item-rest", {k: round(v, 3) for k, v in OUT["item_rest_r"].items()}, "ceiling", OUT["green_ceiling_share_eq5"],
      "skew", OUT["green_skew"])
