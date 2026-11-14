"""Offline experiments + Modal batch bounds. No network, no Modal calls (modal_app is parsed, not imported)."""
import ast
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

OFF = Path(__file__).resolve().parents[1] / "offline"
sys.path.insert(0, str(OFF))
import experiments as ex  # noqa: E402
import tasklist  # noqa: E402

BUNDLE = OFF / "bundle"


def fixture(n=400, ate_h=0.2, ate_l=0.1, seed=0):
    rng = np.random.default_rng(seed)
    t = np.repeat([0, 1], n // 2)
    yh = (rng.random(n) < 0.4 + ate_h * t).astype(float)
    yl = (rng.random(n) < 0.4 + ate_l * t).astype(float)
    df = pd.DataFrame({"row": range(n), "treat": t, "y_human": yh, "cell": np.where(np.arange(n) % 10 < 9, [f"c{i % 9}" for i in range(n)], "OTHER")})
    for s in tasklist.SPECS:
        df[f"y_{s}"] = yl
    for c in ex.TIER_A:
        df[c] = rng.choice(["a", "b", "c"], n)
    for a in ("green", "social_desirability", "spendthrift", "crt", "dictator_give", "neuroticism"):
        df[f"att_{a}"] = rng.normal(size=n)
    return df


def test_task_list_fixed_and_bounded():
    t = tasklist.all_tasks()
    assert len(t) == 18 and len(set(t)) == 18 and set(tasklist.SMOKE) <= set(t)


def test_effect_recovery_exact_on_fixture():
    df = fixture()
    r = ex.effect_recovery(df, "full_persona_t07", nb=200)
    h = df[df.treat == 1].y_human.mean() - df[df.treat == 0].y_human.mean()
    l = df[df.treat == 1].y_full_persona_t07.mean() - df[df.treat == 0].y_full_persona_t07.mean()
    assert r["human_ate"] == pytest.approx(h) and r["llm_ate"] == pytest.approx(l)
    assert r["diff_llm_minus_human_ci"][0] <= r["diff_llm_minus_human"] <= r["diff_llm_minus_human_ci"][1]


def test_calibration_and_information_value_run_on_fixture():
    df = fixture()
    b = ex.calibration(df, "demographics_t07", "binary", nb=50)
    assert 0 <= b["distribution"]["total_variation"] <= 1 and b["cell"]["n_cells"] == 9
    c = ex.information_value(df, "binary", repeats=1, nb=50)
    assert set(c["models"]) == set(ex.MODELS) and all(np.isfinite(v["mean_loss"]) for v in c["models"].values())


def test_worst_case_cost_under_ceiling_and_no_secrets():
    src = (OFF / "modal_app.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    consts = {n.targets[0].id: ast.literal_eval(n.value) for n in tree.body
              if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id in ("RATES", "COST_CEILING_USD")}
    worker_h = 1800 / 3600 * (1.0 * consts["RATES"]["cpu_core_h"] + 1.0 * consts["RATES"]["mem_gib_h"])
    orch = 3 * (0.25 * consts["RATES"]["cpu_core_h"] + 0.5 * consts["RATES"]["mem_gib_h"])
    assert 18 * worker_h * 2 + orch < consts["COST_CEILING_USD"] == 5.0
    for banned in ("modal.Secret", "secrets=", "OPEN_ROUTER", "gpu=", "add_local_dir"):
        assert banned not in src
    import re
    uploads = re.findall(r'add_local_file\(HERE / "([^"]+)"', src)
    assert uploads == ["bundle/default_eric.parquet", "bundle/targeting_fairness.parquet"]
    assert "max_retries=1" in src and "timeout=1800" in src and "max_containers=4" in src


@pytest.mark.skipif(not (BUNDLE / "default_eric.parquet").exists(), reason="bundle not built")
def test_bundle_is_pseudonymous_training_only_and_reproduces_known_effects():
    for s in tasklist.STUDIES:
        df = ex.load(BUNDLE, s)
        assert not {"pid", "TWIN_ID"} & set(df.columns) and df.row.is_unique
        assert not any(c.startswith(("QID", "w1_", "w2_", "w3_")) for c in df.columns)
    e = ex.effect_recovery(ex.load(BUNDLE, "default_eric"), "demographics_t07", nb=50)
    assert e["human_ate"] == pytest.approx(0.2174, abs=1e-4) and e["llm_ate"] == pytest.approx(0.1106, abs=1e-4)
    f = ex.load(BUNDLE, "targeting_fairness")
    assert len(f) == 260 and f.treat.sum() == 135                    # women-targeted text = Segment 2 (label inverted)
