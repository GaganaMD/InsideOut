"""B. Green-energy say-do analysis (H2-H5). Train split only; the holdout check lives in holdout.py.

Outcome: hypothetical choice of the $39/month renewable supplier over the $32 one (default_eric).
'Say' = GREEN values (standardised on train). Default condition is randomised between subjects.
"""
import json

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from common import RESULTS, SEED, load_green, low_income

N_BOOT = 1000
PRIMARY = "chose_green ~ green_z * green_default + low_inc"


def prep(df: pd.DataFrame, mu: float, sd: float) -> pd.DataFrame:
    df = df.copy()
    df["green_z"] = (df.green - mu) / sd
    df["low_inc"] = low_income(df.income).astype(int)
    df["sd_z"] = (df.social_desirability - df.social_desirability.mean()) / df.social_desirability.std()
    return df


def ames(fit, df: pd.DataFrame) -> dict:
    """Average marginal effects in probability points (counterfactual predictions)."""
    p = lambda d: fit.predict(d).mean()
    up = df.assign(green_z=df.green_z + 1)
    on, off = df.assign(green_default=1), df.assign(green_default=0)
    out = {"ame_green_1sd": p(up) - p(df), "ame_default": p(on) - p(off)}
    for c in (0, 1):
        sub = df.assign(green_default=c)
        out[f"ame_green_1sd_{'greendef' if c else 'greydef'}"] = p(sub.assign(green_z=sub.green_z + 1)) - p(sub)
    out["default_minus_green"] = out["ame_default"] - out["ame_green_1sd"]
    return out


def fit_summary(fit) -> list[dict]:
    ci = fit.conf_int()
    return [dict(term=t, coef=fit.params[t], se=fit.bse[t], p=fit.pvalues[t], OR=np.exp(fit.params[t]),
                 OR_lo=np.exp(ci.loc[t, 0]), OR_hi=np.exp(ci.loc[t, 1])) for t in fit.params.index]


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    g = load_green()
    tr0 = g[g.split == "train"]
    mu, sd = tr0.green.mean(), tr0.green.std(ddof=1)
    json.dump({"green_mu_train": mu, "green_sd_train": sd}, open(RESULTS / "saydo_scaling.json", "w"))
    tr = prep(tr0, mu, sd)
    report = {"n_train": len(tr), "cells": tr.groupby(["green_condition", "low_inc"]).size()
              .rename("n").reset_index().to_dict("records")}

    # Randomisation check: does Tier A / GREEN predict condition? (should not)
    bal = smf.logit("green_default ~ green_z + low_inc + C(age_band) + C(education) + C(sex)", tr).fit(disp=0)
    report["randomisation_check_llr_p"] = bal.llr_pvalue

    fit = smf.logit(PRIMARY, tr).fit(disp=0)
    report["primary_formula"] = PRIMARY
    report["primary"] = fit_summary(fit)
    report["primary_pseudo_r2"] = fit.prsquared
    point = ames(fit, tr)

    rng = np.random.default_rng(SEED)
    boots = []
    for _ in range(N_BOOT):
        b = tr.sample(len(tr), replace=True, random_state=rng.integers(1 << 31))
        try:
            boots.append(ames(smf.logit(PRIMARY, b).fit(disp=0), b))
        except Exception:  # separation in a resample
            continue
    bt = pd.DataFrame(boots)
    report["ames"] = {k: dict(est=v, lo=bt[k].quantile(.025), hi=bt[k].quantile(.975)) for k, v in point.items()}
    report["n_boot_ok"] = len(bt)

    # H5: GREEN x income only if every income x condition cell has >= 40 in train
    min_cell = tr.groupby(["green_condition", "low_inc"]).size().min()
    if min_cell >= 40:
        f5 = smf.logit("chose_green ~ green_z * green_default + green_z * low_inc", tr).fit(disp=0)
        report["h5"] = {"min_cell": int(min_cell), "terms": fit_summary(f5)}
    else:
        report["h5"] = {"min_cell": int(min_cell), "status": "infeasible: a cell has < 40"}

    # Sensitivities (labelled): social desirability adjustment; party; descriptive say-do quadrant
    fs = smf.logit("chose_green ~ green_z * green_default + low_inc + sd_z", tr).fit(disp=0)
    report["sens_social_desirability"] = fit_summary(fs)
    fd = smf.logit("chose_green ~ green_z * green_default + low_inc + C(age_band) + C(education) + C(sex)",
                   tr).fit(disp=0)
    report["sens_demographic_adjusted"] = fit_summary(fd)  # randomisation check flagged age/education imbalance
    fp = smf.logit("chose_green ~ green_z * green_default + low_inc + C(party)", tr).fit(disp=0)
    report["sens_party"] = fit_summary(fp)
    tr["high_green"] = tr.green_z > 0
    q = tr.groupby(["green_condition", "high_green"]).chose_green.agg(["size", "mean"]).reset_index()
    report["say_do_table"] = q.to_dict("records")
    # Say-do gap: share of high-GREEN (top tercile) who decline the green option when it costs effort+money
    top = tr[tr.green >= tr.green.quantile(2 / 3)]
    for c in ("grey_default", "green_default"):
        s = top[top.green_condition == c]
        report[f"gap_top_tercile_decline_{c}"] = dict(n=len(s), share_decline=1 - s.chose_green.mean())

    json.dump(report, open(RESULTS / "saydo.json", "w"), indent=1, default=float)
    pd.DataFrame(report["primary"]).round(4).to_csv(RESULTS / "saydo_primary_terms.csv", index=False)
    print(json.dumps({k: report[k] for k in ["n_train", "randomisation_check_llr_p", "ames", "primary_pseudo_r2"]},
                     indent=1, default=float))
    print(pd.DataFrame(report["primary"]).round(3).to_string(index=False))
    print("H5:", report["h5"].get("status", "fitted"), "min cell", report["h5"]["min_cell"])
    print(pd.DataFrame(report["h5"].get("terms", [])).round(3).to_string(index=False))
    print("SD-adjusted:\n", pd.DataFrame(report["sens_social_desirability"]).round(3).to_string(index=False))
    print(q.round(3).to_string(index=False))
    print({k: v for k, v in report.items() if k.startswith("gap_")})


if __name__ == "__main__":
    main()
