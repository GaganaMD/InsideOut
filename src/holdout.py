"""E. Held-out validation on the frozen test split. Every model/persona is fitted on TRAIN; test is only scored.

The first run is recorded in results/holdout_first_run.json (git commit + timestamp) and never overwritten.
Later runs (e.g. via run_all.py) recompute the same deterministic numbers; nothing here is tuned on test.
"""
import datetime
import json
import subprocess

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from common import CONSTRUCTS, RESULTS, ROOT, SEED, TIER_A, load_green, load_people, low_income
from personas import build, load_config, mask, parse_criteria
from predictability import model
from saydo import PRIMARY, prep

N_BOOT = 2000


def boot_ci(x: np.ndarray, rng) -> tuple[float, float]:
    if len(x) < 2:
        return (np.nan, np.nan)
    b = rng.choice(x, size=(N_BOOT, len(x)), replace=True).mean(axis=1)
    return float(np.quantile(b, .025)), float(np.quantile(b, .975))


def main() -> None:
    rng = np.random.default_rng(SEED)
    people, green = load_people(), load_green()
    train, test = people[people.split == "train"], people[people.split == "test"]

    # 1. Personas: shrunken persona mean vs train population mean, on held-out members
    rows, beh = [], []
    gtr, gte = green[green.split == "train"], green[green.split == "test"]
    pop_rate = gtr.groupby("green_condition").chose_green.mean()
    for key, p in load_config().items():
        crit = parse_criteria(p["criteria"], people)
        rep = build(p["name"], crit, people, green)
        te = test[mask(test, crit)]
        for r in rep["inner"]:
            c = r["construct"]
            y = te[c].to_numpy()
            e_p, e_0 = np.abs(y - r["typical_shrunk"]), np.abs(y - r["pop_mean"])
            lo, hi = boot_ci(e_0 - e_p, rng)
            pq = train[c].quantile([.1, .9])
            rows.append(dict(persona=p["name"], construct=c, n_test=len(y), train_d=r["d"],
                             distinct_on_train=r["confidence"] == "distinct",
                             test_d=(y.mean() - r["pop_mean"]) / r["pop_sd"],
                             mae_persona=e_p.mean(), mae_pop=e_0.mean(),
                             gain_pct=100 * (e_0.mean() - e_p.mean()) / e_0.mean(), gain_lo=lo, gain_hi=hi,
                             cov_persona=float(((y >= r["p10"]) & (y <= r["p90"])).mean()),
                             cov_pop=float(((y >= pq[.1]) & (y <= pq[.9])).mean())))
        # behaviour: persona's train rate by condition vs population train rate, scored on test members
        gm = gte[gte.pid.isin(te.pid)]
        rate = {b["condition"]: b["rate"] for b in rep["green_choice"]}
        ok = {b["condition"]: b["status"] == "ok" for b in rep["green_choice"]}
        for cond, s in gm.groupby("green_condition"):
            y = s.chose_green.to_numpy()
            pr = rate[cond] if ok[cond] else pop_rate[cond]  # insufficient -> falls back to population
            beh.append(dict(persona=p["name"], condition=cond, n_test=len(y), test_rate=y.mean(),
                            persona_train_rate=rate[cond], used_persona_rate=ok[cond],
                            pop_train_rate=pop_rate[cond], brier_persona=((y - pr) ** 2).mean(),
                            brier_pop=((y - pop_rate[cond]) ** 2).mean()))
    hp = pd.DataFrame(rows)
    hp.round(4).to_csv(RESULTS / "holdout_personas.csv", index=False)
    pd.DataFrame(beh).round(4).to_csv(RESULTS / "holdout_persona_behaviour.csv", index=False)

    # 2. Predictability map: ridge fitted on all train, scored on test
    pm = []
    for c in CONSTRUCTS:
        m = model(TIER_A).fit(train[TIER_A].astype(str), train[c])
        pred, y, base = m.predict(test[TIER_A].astype(str)), test[c].to_numpy(), train[c].mean()
        pm.append(dict(construct=c, n_test=len(y), test_r2=1 - ((y - pred) ** 2).sum() / ((y - base) ** 2).sum(),
                       mae_model=np.abs(y - pred).mean(), mae_baseline=np.abs(y - base).mean()))
    pd.DataFrame(pm).round(4).to_csv(RESULTS / "holdout_predictability.csv", index=False)

    # 3. Say-do: train-fitted model scored on test; plus test-only refit for sign replication
    sc = json.load(open(RESULTS / "saydo_scaling.json"))
    tr, te = prep(gtr, sc["green_mu_train"], sc["green_sd_train"]), prep(gte, sc["green_mu_train"], sc["green_sd_train"])
    fit = smf.logit(PRIMARY, tr).fit(disp=0)
    p_model = fit.predict(te).clip(1e-6, 1 - 1e-6)
    p_cond = te.green_condition.map(pop_rate)
    p_int = np.full(len(te), gtr.chose_green.mean())
    y = te.chose_green.to_numpy()
    ll = lambda p: float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))
    refit = smf.logit(PRIMARY, te).fit(disp=0)
    ci = refit.conf_int()
    sd_out = dict(n_test=len(te),
                  logloss=dict(model=ll(p_model), condition_only=ll(p_cond), intercept_only=ll(p_int)),
                  brier=dict(model=float(((y - p_model) ** 2).mean()), condition_only=float(((y - p_cond) ** 2).mean()),
                             intercept_only=float(((y - p_int) ** 2).mean())),
                  test_refit={t: dict(OR=float(np.exp(refit.params[t])), lo=float(np.exp(ci.loc[t, 0])),
                                      hi=float(np.exp(ci.loc[t, 1]))) for t in refit.params.index})
    top = te[te.green >= gtr.green.quantile(2 / 3)]
    sd_out["gap_top_tercile_decline"] = {c: dict(n=len(s), share=float(1 - s.chose_green.mean()))
                                         for c, s in top.groupby("green_condition")}
    json.dump(sd_out, open(RESULTS / "holdout_saydo.json", "w"), indent=1)

    first = RESULTS / "holdout_first_run.json"
    if not first.exists():
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        json.dump({"first_run_utc": datetime.datetime.utcnow().isoformat(), "git_commit": commit}, open(first, "w"))

    print(hp[["persona", "construct", "n_test", "train_d", "test_d", "mae_persona", "mae_pop", "gain_pct",
              "gain_lo", "gain_hi", "cov_persona", "cov_pop"]].round(3).to_string(index=False))
    print(pd.DataFrame(beh).round(3).to_string(index=False))
    print(pd.DataFrame(pm).round(3).to_string(index=False))
    print(json.dumps(sd_out, indent=1))


if __name__ == "__main__":
    main()
