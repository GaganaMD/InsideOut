"""Final audit phase 2 (EXPLORATORY sensitivity checks; TRAIN split only; corrected SD/CRT scores).

Tries to falsify the headline: 'census-observable demographics weakly predict temperament (neuroticism, social
desirability) but give little practical predictive value for values and hypothetical choices'.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import LinearRegression, RidgeCV
from sklearn.model_selection import RepeatedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import CONSTRUCTS, ROOT, SEED, TIER_A, load_green, load_people  # noqa: E402

OUT = ROOT / "reports/final_audit/headline_challenge"
NESTED = {
    "age": ["age_band"],
    "age+sex": ["age_band", "sex"],
    "age+sex+income": ["age_band", "sex", "income"],
    "age+sex+income+education+region": ["age_band", "sex", "income", "education", "region"],
    "age+employment": ["age_band", "employment"],
    "full Tier A": TIER_A,
}


def ridge(feats):
    return make_pipeline(ColumnTransformer([("oh", OneHotEncoder(handle_unknown="ignore"), feats)]),
                         RidgeCV(alphas=np.logspace(-2, 3, 30)))


def ols(feats):
    return make_pipeline(ColumnTransformer([("oh", OneHotEncoder(handle_unknown="ignore", drop="first"), feats)]),
                         LinearRegression())


def gbm(feats):
    return make_pipeline(ColumnTransformer([("ord", OrdinalEncoder(), feats)]),
                         HistGradientBoostingRegressor(max_depth=3, learning_rate=0.05, max_iter=200,
                                                       categorical_features=list(range(len(feats))), random_state=SEED))


def cv_r2(df, y, make, feats) -> np.ndarray:
    X, yv = df[feats].astype(str), df[y].to_numpy()
    out = []
    for tr, te in RepeatedKFold(n_splits=5, n_repeats=5, random_state=SEED).split(X):
        p = make(feats).fit(X.iloc[tr], yv[tr]).predict(X.iloc[te])
        out.append(1 - ((yv[te] - p) ** 2).sum() / ((yv[te] - yv[tr].mean()) ** 2).sum())
    return np.array(out)


def summarise(a: np.ndarray) -> dict:
    return dict(mean=a.mean(), lo=a.mean() - 1.96 * a.std(ddof=1) / np.sqrt(5), hi=a.mean() + 1.96 * a.std(ddof=1) / np.sqrt(5))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    p = load_people(corrected=True)
    tr = p[p.split == "train"].reset_index(drop=True)
    res = {}

    # 1-2. nested specifications for neuroticism and social desirability (paired: same folds)
    nest = []
    for y in ["neuroticism", "social_desirability"]:
        base = cv_r2(tr, y, ridge, NESTED["age"])
        for name, feats in NESTED.items():
            r = cv_r2(tr, y, ridge, feats)
            nest.append(dict(construct=y, spec=name, **{f"r2_{k}": v for k, v in summarise(r).items()},
                             **{f"gain_over_age_{k}": v for k, v in summarise(r - base).items()}))
    res["nested"] = pd.DataFrame(nest)

    # 3. alternative model families, full Tier A, all six constructs
    alt = []
    for y in CONSTRUCTS:
        for fam, make in [("ridge", ridge), ("OLS", ols), ("gradient boosting (interactions)", gbm)]:
            alt.append(dict(construct=y, model=fam, **summarise(cv_r2(tr, y, make, TIER_A))))
    res["model_families"] = pd.DataFrame(alt)

    # 4. scale properties: reliability ceiling, floor/ceiling mass, distinct values
    rel = pd.read_csv(ROOT / "reports/final_audit/reliability.csv")
    relmap = {r.construct.split(" ")[0]: r.reliability for r in rel.itertuples()}
    ridge_r2 = res["model_families"].query("model == 'ridge'").set_index("construct")["mean"]
    props = []
    for y, (_, _, (lo, hi)) in CONSTRUCTS.items():
        v = tr[y]
        props.append(dict(construct=y, n_distinct=v.nunique(), share_at_floor=(v == lo).mean(), share_at_ceiling=(v == hi).mean(),
                          sd=v.std(), reliability=relmap.get(y, np.nan), cv_r2_ridge=ridge_r2[y],
                          r2_as_share_of_reliable_variance=ridge_r2[y] / relmap[y] if not np.isnan(relmap.get(y, np.nan)) else np.nan))
    res["scale_properties"] = pd.DataFrame(props)

    # 5. group-level vs individual-level: eta^2 of age band, common-language effect size 65+ vs 18-29
    grp = []
    for y in ["neuroticism", "social_desirability", "green", "crt"]:
        eta = smf.ols(f"{y} ~ C(age_band)", tr).fit().rsquared
        a, b = tr[tr.age_band == "65+"][y].to_numpy(), tr[tr.age_band == "18-29"][y].to_numpy()
        cl = (np.mean(a[:, None] > b[None, :]) + 0.5 * np.mean(a[:, None] == b[None, :]))
        means = tr.groupby("age_band", observed=True)[y].mean()
        grp.append(dict(construct=y, age_band_eta2=eta, mean_18_29=means["18-29"], mean_65plus=means["65+"],
                        d_65_vs_18_29=(means["65+"] - means["18-29"]) / tr[y].std(),
                        prob_random_65plus_scores_higher_than_random_18_29=cl))
    res["group_vs_individual"] = pd.DataFrame(grp)

    # 6. Mega-Study selection: default_eric participants vs other train members, and age-reweighted say-do slope
    g = load_green(corrected=True)
    gtr = g[g.split == "train"].copy()
    inexp = tr.pid.isin(gtr.pid)
    sel = []
    for y in CONSTRUCTS:
        d = (tr.loc[inexp, y].mean() - tr.loc[~inexp, y].mean()) / tr[y].std()
        sel.append(dict(variable=y, std_diff_participants_minus_others=d))
    for band in ["18-29", "30-49", "50-64", "65+"]:
        sel.append(dict(variable=f"share age {band}", participants=float((tr.loc[inexp, "age_band"] == band).mean()),
                        others=float((tr.loc[~inexp, "age_band"] == band).mean())))
    res["selection"] = pd.DataFrame(sel)
    target = tr.age_band.value_counts(normalize=True)
    have = gtr.age_band.value_counts(normalize=True)
    gtr["w"] = gtr.age_band.map(lambda b: target[b] / have[b]).astype(float)
    gtr["green_z"] = (gtr.green - gtr.green.mean()) / gtr.green.std()
    unw = smf.logit("chose_green ~ green_z + green_default", gtr).fit(disp=0)
    wt = smf.glm("chose_green ~ green_z + green_default", gtr, family=__import__("statsmodels.api").api.families.Binomial(),
                 freq_weights=gtr.w).fit()
    res["reweighting"] = dict(OR_green_unweighted=float(np.exp(unw.params.green_z)), OR_green_age_reweighted=float(np.exp(wt.params.green_z)),
                              OR_default_unweighted=float(np.exp(unw.params.green_default)),
                              OR_default_age_reweighted=float(np.exp(wt.params.green_default)),
                              note="age-band weights to the Twin train distribution; freq_weights SEs not reported (point check only)")

    for k, v in res.items():
        (v.round(4).to_csv(OUT / f"{k}.csv", index=False) if isinstance(v, pd.DataFrame)
         else json.dump(v, open(OUT / f"{k}.json", "w"), indent=1))
        print(f"\n== {k}\n", v.round(3).to_string(index=False) if isinstance(v, pd.DataFrame) else json.dumps(v, indent=1))


if __name__ == "__main__":
    main()
