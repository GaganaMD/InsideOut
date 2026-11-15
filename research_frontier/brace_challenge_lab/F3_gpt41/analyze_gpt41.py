"""Pilot report (feasibility only) and conversion of the harness cache to the F2 analysis format. Local; no API calls.

    python analyze_gpt41.py pilot   # validity, cost, consistency, choice/p agreement, order sensitivity; GO/NO-GO
    python analyze_gpt41.py full    # writes outputs/full__gpt41.json and runs the unchanged F2 analysis
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OV = HERE.parents[1] / "overnight"
RUN = OV / "runs/live/green_profiles__openai__gpt-4.1"
EST = {"pilot": 0.3073, "full": 1.8178}          # `harness.cli plan` upper bounds, 2026-11-15


def parse(i):
    fmt, cond, order, rest = i.split("|", 3)
    cell, fold, s = rest.rsplit("|", 2)
    return fmt, cond, order, cell, fold, s


def load():
    recs = [json.loads(l) for l in (RUN / "cache.jsonl").read_text(encoding="utf-8").splitlines()]
    ev = [json.loads(l) for l in (RUN / "events.jsonl").read_text(encoding="utf-8").splitlines()] if (RUN / "events.jsonl").exists() else []
    rows = []
    for r in recs:
        fmt, cond, order, cell, fold, s = parse(r["task_id"])
        p = r["result"]["p"]
        rows.append(dict(id=r["task_id"], fmt=fmt, cond=cond, order=order, cell=cell, fold=fold, s=s, p=p,
                         choice=r["result"]["choice"], p_green=p if order == "AB" else 1 - p, cost=r["cost_usd"],
                         pt=r["usage"].get("prompt_tokens", 0), ct=r["usage"].get("completion_tokens", 0),
                         served=r.get("served_model"), provider=r.get("provider"), billed=r["usage"].get("cost")))
    return pd.DataFrame(rows), ev, json.loads((RUN / "summary.json").read_text())


def pilot_report(stage="pilot") -> dict:
    d, ev, summ = load()
    n_inv = sum(e.get("event") == "invalid" for e in ev)
    n_err = sum(e.get("event") == "error" for e in ev)
    att = len(d) + n_inv + n_err
    s0 = d[d.s == "s0"].set_index(["fmt", "cond", "order", "cell", "fold"])
    s1 = d[d.s == "s1"].set_index(["fmt", "cond", "order", "cell", "fold"])
    rep = s1.join(s0[["p", "choice"]], rsuffix="_0", how="inner")
    pair = s0.reset_index().pivot_table(index=["fmt", "cond", "cell", "fold"], columns="order", values="p_green").dropna()
    signed = (pair["AB"] - pair["BA"])
    cost = float(d.cost.sum())
    billed = float(pd.to_numeric(d.billed, errors="coerce").sum()) if d.billed.notna().any() else None
    r = {"attempted": att, "valid": len(d), "invalid": n_inv, "errors": n_err, "valid_rate": len(d) / att if att else None,
         "cost_usd_computed": cost, "cost_usd_billed_by_openrouter": billed, "estimate_upper_usd": EST[stage],
         "prompt_tokens": int(d.pt.sum()), "completion_tokens": int(d.ct.sum()),
         "served_models": sorted(set(map(str, d.served))), "providers": sorted(set(map(str, d.provider))),
         "retries": summ.get("retries"), "stopped_reason": summ.get("stopped_reason"),
         "reask_n": len(rep), "reask_mean_abs_dp": float((rep.p - rep.p_0).abs().mean()) if len(rep) else None,
         "reask_same_choice": float((rep.choice == rep.choice_0).mean()) if len(rep) else None,
         "choice_p_agreement": float(((d.choice == "A") == (d.p >= 0.5)).mean()),
         "p_sd": float(d.p.std()), "p_modal_share": float(d.p.value_counts(normalize=True).iloc[0]),
         "order_gap_mean_abs": float(signed.abs().mean()), "order_gap_signed_AB_minus_BA": float(signed.mean()),
         "mean_p_green_by_fmt_cond": d[d.s == "s0"].groupby(["fmt", "cond"]).p_green.mean().round(3).to_dict()}
    r["mean_p_green_by_fmt_cond"] = {f"{k[0]}|{k[1]}": v for k, v in r["mean_p_green_by_fmt_cond"].items()}
    crit = {"valid_rate>=0.98": (r["valid_rate"] or 0) >= 0.98,
            "cost<=2x_estimate_and<=1": cost <= 2 * EST[stage] and (stage != "pilot" or cost <= 1.0),
            "reask_mean_abs_dp<=0.10": r["reask_mean_abs_dp"] is not None and r["reask_mean_abs_dp"] <= 0.10,
            "reask_same_choice>=0.90": r["reask_same_choice"] is not None and r["reask_same_choice"] >= 0.90,
            "choice_p_agreement>=0.95": r["choice_p_agreement"] >= 0.95,
            "p_not_degenerate": r["p_sd"] > 0.05 and r["p_modal_share"] <= 0.80,
            "served_model_is_gpt41": all("gpt-4.1" in s for s in r["served_models"])}
    r["go_criteria"] = crit
    r["verdict"] = "GO (propose full run; needs separate authorization)" if all(crit.values()) else "NO-GO"
    return r


def to_f2(path: Path) -> Path:
    d, _, _ = load()
    d = d[d.s == "s0"]
    out = {"model_id": "openai/gpt-4.1", "revision": ",".join(sorted(set(map(str, d.served)))), "license": "proprietary (API)",
           "gpu": "n/a (OpenRouter)", "load_s": 0, "score_s": 0, "n_prompts": len(d),
           "results": [{"id": "|".join(i.split("|")[:-1]), "pA": p, "pB": 1 - p, "mass": 1.0} for i, p in zip(d.id, d.p)]}
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(out), encoding="utf-8")
    return path


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "pilot"
    rep = pilot_report(stage)
    (HERE / f"{stage}_report.json").write_text(json.dumps(rep, indent=1, default=str), encoding="utf-8")
    print(json.dumps(rep, indent=1, default=str))
    if stage == "full":
        f2 = to_f2(HERE / "outputs/full__gpt41.json")
        print("converted ->", f2, "; run F2 analyze.py on it")
