"""Pilot, credential and analysis tests. Mock credentials and mock/dry transports only; the real .env is never loaded.
Run: python -m pytest -q research_frontier/overnight/tests"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import analyze_pilot as ap  # noqa: E402
from harness import cli, credentials  # noqa: E402
from harness.client import redact  # noqa: E402

MOCK_KEY = "mock-key-not-real-0000"


@pytest.fixture(autouse=True)
def no_real_env(monkeypatch):
    """Guarantee no test can read the repository .env or a real key."""
    monkeypatch.setattr(credentials, "load_env_file", lambda *a, **k: False)
    for n in credentials.ENV_NAMES:
        monkeypatch.delenv(n, raising=False)


# ----------------------------------------------------------------------------- credentials
def test_alias_open_router_key_and_redaction(monkeypatch):
    monkeypatch.setenv("OPEN_ROUTER_KEY", MOCK_KEY)
    assert credentials.get_key() == MOCK_KEY and credentials.key_present()
    assert MOCK_KEY not in redact(f"401 invalid key {MOCK_KEY}")


def test_fallback_alias(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", MOCK_KEY)
    assert credentials.get_key() == MOCK_KEY


def test_dotenv_parser_on_temp_file(tmp_path, monkeypatch):
    f = tmp_path / ".env"
    f.write_text(f'OPEN_ROUTER_KEY="{MOCK_KEY}"\n')
    monkeypatch.undo()                                       # use the real loader, but only on this temp file
    for n in credentials.ENV_NAMES:
        monkeypatch.delenv(n, raising=False)
    assert credentials.load_env_file(f) and credentials.get_key() == MOCK_KEY


def test_key_presence_never_triggers_live(monkeypatch):
    monkeypatch.setenv("OPEN_ROUTER_KEY", MOCK_KEY)
    used = {}

    class StubRunner:
        def __init__(self, cfg, client):
            used["transport"] = type(client.transport).__name__
            self.cfg = cfg

        def run(self, tasks):
            (self.cfg.out_dir / "summary.json").write_text("{}")
            return []

    monkeypatch.setattr(cli, "Runner", StubRunner)
    monkeypatch.setattr(cli, "HttpTransport", lambda *a, **k: pytest.fail("HttpTransport constructed"))
    assert cli.main(["dry-run", "--pilot"]) == 0 and used["transport"] == "DryRunTransport"


def test_live_refused_without_exact_confirmation(monkeypatch):
    monkeypatch.setenv("OPEN_ROUTER_KEY", MOCK_KEY)
    monkeypatch.setattr(cli, "HttpTransport", lambda *a, **k: pytest.fail("HttpTransport constructed"))
    assert cli.main(["live", "--pilot", "--confirm", "yes please"]) == 3


def test_live_refused_without_key(monkeypatch):
    monkeypatch.setattr(cli, "HttpTransport", lambda *a, **k: pytest.fail("HttpTransport constructed"))
    assert cli.main(["live", "--pilot", "--confirm", cli.CONFIRM]) == 3


def test_pilot_budget_cap_enforced():
    assert cli.main(["plan", "--pilot", "--budget", "1.01"]) == 2


def test_check_key_output_never_contains_key(monkeypatch, capsys):
    monkeypatch.setenv("OPEN_ROUTER_KEY", MOCK_KEY)
    cli.main(["check-key"])
    out = capsys.readouterr().out
    assert MOCK_KEY not in out and json.loads(out)["key_detected"] is True


# ----------------------------------------------------------------------------- pilot batch
def test_pilot_is_80_calls_k_anonymous_and_id_free():
    from harness.tasks import build_pilot, cells
    from common import load_people
    tasks, keep = build_pilot()
    assert len(tasks) == 80 and len(keep) == 10
    k = cells(load_people()).value_counts()
    for t in tasks:
        blob = json.dumps(t.profile) + json.dumps(t.item)
        for banned in ("pid", "twin", "chose", "green values", "neuroticism"):
            assert banned not in blob.lower()
        if t.profile:
            assert k[" | ".join(t.profile["tier_a"].values())] >= 5


# ----------------------------------------------------------------------------- analysis (synthetic fixtures)
def synthetic():
    rows = []
    for cell, (pg, pr) in {"X": (0.8, 0.4), "Y": (0.6, 0.6)}.items():
        for cond, p in (("green_default", pg), ("grey_default", pr)):
            for s in range(3):
                rows.append(dict(arm="tierA", cond=cond, cell=cell, sample=s, choice="A" if p >= .5 else "B", p=p,
                                 cost=0.0, dry_run=True))
    rec = pd.DataFrame(rows)
    hum = []
    for cell, n, (yg, yr) in (("X", 30, (0.6, 0.2)), ("Y", 10, (0.5, 0.5)), ("Z", 50, (1.0, 0.0))):
        for cond, rate in (("green_default", yg), ("grey_default", yr)):
            m = n // 2
            ones = int(round(rate * m))
            for i in range(m):
                hum.append(dict(pid=len(hum), cell=cell, cond=cond, y=float(i < ones)))
    return rec, pd.DataFrame(hum)


def test_contrast_weights_exact():
    rec, hum = synthetic()
    pw = ap.contrast(rec, hum, "tierA", "participant", nb=200)
    cw = ap.contrast(rec, hum, "tierA", "cell", nb=200)
    assert pw["n_cells"] == 2                                # Z never queried -> excluded from both sides
    assert pw["model_contrast"] == pytest.approx((30 * 0.4 + 10 * 0.0) / 40)
    assert cw["model_contrast"] == pytest.approx((0.4 + 0.0) / 2)
    hx = 0.6 - 0.2
    assert pw["human_contrast"] == pytest.approx((30 * hx + 10 * 0.0) / 40, abs=0.02)
    assert pw["model_ci"][0] <= pw["model_contrast"] <= pw["model_ci"][1]
    assert pw["abs_error"] == pytest.approx(abs(pw["signed_diff"]))


def test_individual_uses_only_matched_participants():
    rec, hum = synthetic()
    ind = ap.individual(rec, hum, "tierA")
    assert ind["n_matched"] == len(hum[hum.cell.isin(["X", "Y"])])


def test_load_run_counts_invalid_and_errors(tmp_path):
    rec = {"key": "k", "task_id": "tierA/green_default/X/s0", "result": {"choice": "A", "p": 0.7}, "cost_usd": 0.001,
           "dry_run": True}
    (tmp_path / "cache.jsonl").write_text(json.dumps(rec) + "\n")
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "invalid"}) + "\n" + json.dumps({"event": "error"}) + "\n")
    df, v = ap.load_run(tmp_path)
    assert len(df) == 1 and v == dict(attempted=3, valid=1, invalid=1, errors=1, valid_rate=pytest.approx(1 / 3),
                                      spend_usd=pytest.approx(0.001), dry_run=True)


# ----------------------------------------------------------------------------- analysis (published GPT-4.1 predictions)
@pytest.mark.skipif(not (HERE.parents[0] / "experiments/external").exists(), reason="published predictions not downloaded")
def test_published_contrasts_match_benchmark_audit():
    ref = pd.read_csv(HERE / "results/benchmark_audit_default_effect.csv").set_index("source")
    hum = ap.load_humans()
    for name, pr in ap.published_records().items():
        c = ap.contrast(pr.assign(arm="empty", cell="ALL"), hum, "empty", "participant", nb=50)
        assert c["model_contrast"] == pytest.approx(ref.loc[name, "ate"], abs=1e-4)
        assert c["human_contrast"] == pytest.approx(ref.loc["Humans", "ate"], abs=1e-4)


def test_auth_error_stops_run_immediately(tmp_path):
    from harness.client import Client, TransportError
    from harness.runner import RunConfig, Runner, RateLimiter
    from harness.tasks import build_pilot

    class Expired:
        calls = 0

        def send(self, payload):
            Expired.calls += 1
            raise TransportError(401, "API key expired")

    cfg = RunConfig(model="m", price_in_per_m=1, price_out_per_m=1, budget_usd=1, max_workers=1, out_dir=tmp_path)
    r = Runner(cfg, Client(Expired(), sleep=lambda s: None), RateLimiter(10**6, sleep=lambda s: None))
    r.run(build_pilot()[0])
    assert Expired.calls == 1 and r.ledger.stopped_reason == "fatal_http_401" and r.ledger.cost_usd < 1e-9
