"""Live-review helper: training-split-only analyses for LIVE_CHALLENGES.md.

Never reads test-split outcomes (rows are filtered to split == "train" immediately after loading).
Never modifies src/. Uses corrected social-desirability and CRT scores (the CLI default).

Usage (from the repository root, Git Bash):
  PYTHONUTF8=1 python research_frontier/brace_challenge_lab/D_review/live_helpers.py noage
  PYTHONUTF8=1 python research_frontier/brace_challenge_lab/D_review/live_helpers.py minn
  PYTHONUTF8=1 python research_frontier/brace_challenge_lab/D_review/live_helpers.py census
  PYTHONUTF8=1 python research_frontier/brace_challenge_lab/D_review/live_helpers.py absent
  PYTHONUTF8=1 python research_frontier/brace_challenge_lab/D_review/live_helpers.py choice
  ... all   (runs every analysis; about 2-4 minutes)
"""
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression, RidgeCV
from sklearn.model_selection import RepeatedKFold, RepeatedStratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from common import CONSTRUCTS, SEED, TIER_A, load_green, load_people  # noqa: E402

ALPHAS = np.logspace(-2, 3, 30)
KEY = ["neuroticism", "social_desirability", "green", "spendthrift", "crt", "dictator_give"]


def train_people() -> pd.DataFrame:
    p = load_people(corrected=True)
    return p[p.split == "train"].reset_index(drop=True)  # test rows dropped before anything else


def ridge(features):
    pre = ColumnTransformer([("oh", OneHotEncoder(handle_unknown="ignore"), features)])
    return make_pipeline(pre, RidgeCV(alphas=ALPHAS))


def cv_r2(df, y, features, repeats=5):
    X, yv, r2 = df[features].astype(str), df[y].to_numpy(), []
    for tr, te in RepeatedKFold(n_splits=5, n_repeats=repeats, random_state=SEED).split(X):
        pred = ridge(features).fit(X.iloc[tr], yv[tr]).predict(X.iloc[te])
        base = yv[tr].mean()
        r2.append(1 - ((yv[te] - pred) ** 2).sum() / ((yv[te] - base) ** 2).sum())
    r2 = np.array(r2)
    se = 1.96 * r2.std(ddof=1) / np.sqrt(5)  # same heuristic interval as src/predictability.py
    return r2.mean(), r2.mean() - se, r2.mean() + se


# ---------------------------------------------------------------- (a) remove age
def noage():
    tr = train_people()
    no_age = [v for v in TIER_A if v != "age_band"]
    print("(a) CV R2 (ridge, 5x5 CV, train n=%d, corrected scores)" % len(tr))
    print(f"{'construct':22s} {'full Tier A':>22s} {'Tier A minus age':>22s} {'age only':>22s}")
    for c in KEY:
        f = cv_r2(tr, c, TIER_A); n = cv_r2(tr, c, no_age); a = cv_r2(tr, c, ["age_band"])
        fmt = lambda t: f"{t[0]:.3f} ({t[1]:.3f},{t[2]:.3f})"
        print(f"{c:22s} {fmt(f):>22s} {fmt(n):>22s} {fmt(a):>22s}")
    # how much age leaks through the other census variables
    tr["age_idx"] = tr.age_band.cat.codes.astype(float)
    leak = cv_r2(tr, "age_idx", no_age)
    print(f"Age-band index (0-3) predicted from the other 9 Tier A variables: CV R2 {leak[0]:.3f} ({leak[1]:.3f},{leak[2]:.3f})")


# ---------------------------------------------------------------- (b) minimum persona size
def d_stats(x, mu0, sd0):
    n = len(x)
    d = (x.mean() - mu0) / sd0
    h = 1.96 * x.std(ddof=1) / np.sqrt(n) / sd0
    return d, d - h, d + h


def minn(n_splits=20):
    tr = train_people()
    singles = [(v, str(l)) for v in TIER_A for l in tr[v].cat.categories]
    groups = [[s] for s in singles] + [[a, b] for a, b in itertools.combinations(singles, 2) if a[0] != b[0]]
    masks = []
    for g in groups:
        m = np.ones(len(tr), bool)
        for v, l in g:
            m &= tr[v].astype(str).to_numpy() == l
        if m.sum() >= 30:
            masks.append(m)
    rng = np.random.default_rng(SEED)
    rows = []
    for s in range(n_splits):
        inner = rng.random(len(tr)) < 0.7  # inner-train / inner-validation, both inside the train split
        for c in KEY:
            y = tr[c].to_numpy()
            mu0, sd0 = y[inner].mean(), y[inner].std(ddof=1)
            for m in masks:
                a, b = m & inner, m & ~inner
                if a.sum() < 20 or b.sum() < 8:
                    continue
                d, lo, hi = d_stats(pd.Series(y[a]), mu0, sd0)
                if not (abs(d) >= 0.20 and (lo > 0 or hi < 0)):
                    continue  # only constructs the CLI would label "distinct"
                dv = (y[b].mean() - mu0) / sd0
                rows.append(dict(split=s, construct=c, n_train=int(a.sum()), d=d, d_val=dv,
                                 rep=(np.sign(dv) == np.sign(d)) and abs(dv) >= 0.10))
    r = pd.DataFrame(rows)
    r["bucket"] = pd.cut(r.n_train, [19, 29, 59, 99, 199, 10_000], labels=["20-29", "30-59", "60-99", "100-199", "200+"])
    out = r.groupby("bucket", observed=True).agg(labels=("rep", "size"), replicated=("rep", "mean"),
                                                 median_abs_d=("d", lambda s: s.abs().median()),
                                                 median_val_over_train=("d_val", lambda s: np.nan))
    out["median_val_over_train"] = r.groupby("bucket", observed=True).apply(lambda g: (g.d_val / g.d).median())
    print(f"(b) Nested train-only replication of 'distinct' labels: {n_splits} random 70/30 inner splits;")
    print("    groups = all 1- and 2-level Tier A conjunctions with >=30 train members; replicated = same sign and |d_val|>=0.10")
    print(out.round(3).to_string())
    print("Analytic d CI half-width ~ 1.96/sqrt(n):", {n: round(1.96 / np.sqrt(n), 2) for n in (30, 60, 100, 200, 400)})


# ---------------------------------------------------------------- (c) public census fields only
def census():
    tr = train_people()
    specs = {
        "age+sex": ["age_band", "sex"],
        "short-form-like (age, sex, race, hh_size)": ["age_band", "sex", "race", "hh_size"],
        "+ region": ["age_band", "sex", "race", "hh_size", "region"],
        "full Tier A (ACS-type)": TIER_A,
    }
    print("(c) CV R2 by available field set (ridge, 5x5 CV, train only, corrected scores)")
    for c in KEY:
        print(c + ": " + "; ".join(f"{k} {cv_r2(tr, c, v)[0]:.3f}" for k, v in specs.items()))


# ---------------------------------------------------------------- (d) group absent from training
def absent():
    tr = train_people()
    print("(d) Leave-one-level-out: fit ridge on train rows WITHOUT level L (L unseen), predict members of L.")
    print("    Units: train-population SD. 'pop-mean error' = |actual d| (what you get by predicting the population mean).")
    print(f"{'variable=level':45s} {'n':>4s} {'construct':20s} {'actual d':>9s} {'pred d (L absent)':>18s} {'pop-mean err':>12s} {'model err':>10s}")
    for v in ["age_band", "employment", "race", "education", "marital"]:
        for lvl in tr[v].cat.categories:
            m = tr[v].astype(str) == str(lvl)
            if m.sum() < 30:
                continue
            for c in ["neuroticism", "social_desirability", "green"]:
                mu, sd = tr[c].mean(), tr[c].std(ddof=1)
                fit = ridge(TIER_A).fit(tr.loc[~m, TIER_A].astype(str), tr.loc[~m, c])
                pred = fit.predict(tr.loc[m, TIER_A].astype(str)).mean()
                act = (tr.loc[m, c].mean() - mu) / sd
                pd_ = (pred - mu) / sd
                print(f"{(v + '=' + str(lvl))[:45]:45s} {int(m.sum()):4d} {c:20s} {act:+9.2f} {pd_:+18.2f} {abs(act):12.2f} {abs(act - pd_):10.2f}")


# ---------------------------------------------------------------- (e) hypothetical choice instead of attitude
def choice(repeats=20, B=2000):
    g = load_green(corrected=True)
    g = g[g.split == "train"].reset_index(drop=True)
    crit = {"P1": {"age_band": ["65+"]},
            "P2": {"age_band": ["18-29", "30-49"], "income": ["Less than $30,000", "$30,000-$50,000"]},
            "P3": {"age_band": ["18-29"], "marital": ["Never been married"]}}
    for k, cr in crit.items():
        m = np.ones(len(g), bool)
        for v, lv in cr.items():
            m &= g[v].astype(str).isin(lv).to_numpy()
        g[k] = m.astype(int)
        print(f"{k}: {m.sum()} of {len(g)} train default_eric participants")
    g["green_z"] = (g.green - g.green.mean()) / g.green.std(ddof=1)
    y = g.chose_green.to_numpy()

    def lr(num, cat=()):
        parts = [("num", StandardScaler(), list(num))]
        if cat:
            parts.append(("oh", OneHotEncoder(handle_unknown="ignore"), list(cat)))
        return make_pipeline(ColumnTransformer(parts), LogisticRegression(C=1.0, max_iter=2000))

    models = {
        "condition only": (["green_default"], []),
        "condition + persona membership (P1,P2,P3)": (["green_default", "P1", "P2", "P3"], []),
        "condition + Tier A": (["green_default"], TIER_A),
        "condition + green values": (["green_default", "green_z"], []),
    }
    oof = {k: np.zeros((repeats, len(g))) for k in models}
    X = g[["green_default", "green_z", "P1", "P2", "P3", *TIER_A]].copy()
    X[TIER_A] = X[TIER_A].astype(str)
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=repeats, random_state=SEED)
    strat = g.green_condition.astype(str) + y.astype(str)
    for i, (a, b) in enumerate(cv.split(X, strat)):
        r = i // 5
        for k, (num, cat) in models.items():
            oof[k][r, b] = lr(num, cat).fit(X.iloc[a], y[a]).predict_proba(X.iloc[b])[:, 1]
    se = {k: ((v - y) ** 2).mean(0) for k, v in oof.items()}  # per-person Brier averaged over repeats
    base = se["condition only"]
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, len(g), (B, len(g)))
    print(f"(e) default_eric train n={len(g)}; out-of-fold Brier, 5-fold x {repeats} repeats, L2 logistic C=1;")
    print("    delta = model - condition-only (negative = better); 95% participant bootstrap")
    for k, v in se.items():
        dlt = v - base
        bs = dlt[idx].mean(1)
        print(f"  {k:45s} Brier {v.mean():.4f}  delta {dlt.mean():+.4f} ({np.percentile(bs, 2.5):+.4f}, {np.percentile(bs, 97.5):+.4f})")
    print("Persona choice rates on train (rate, n) by condition:")
    for k in ["P1", "P2", "P3"]:
        s = g[g[k] == 1].groupby("green_condition").chose_green.agg(["mean", "size"]).round(2)
        print(f"  {k}: " + "; ".join(f"{c} {r['mean']:.2f} (n={int(r['size'])})" for c, r in s.iterrows()))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    fns = dict(noage=noage, minn=minn, census=census, absent=absent, choice=choice)
    for name in (fns if cmd == "all" else [cmd]):
        fns[name]()
        print()
