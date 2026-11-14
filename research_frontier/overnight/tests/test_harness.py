"""Harness tests with mock transports only. No network, no paid calls.  Run: python -m pytest -q research_frontier/overnight/tests"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness import cli  # noqa: E402
from harness.client import Client, DryRunTransport, TransportError  # noqa: E402
from harness.prompts import TEMPLATE_HASH, render  # noqa: E402
from harness.runner import RateLimiter, RunConfig, Runner, Task  # noqa: E402
from harness.schema import InvalidOutput, parse_choice  # noqa: E402

ITEM = {"question": "Q?", "options": {"A": "green", "B": "grey"}, "focal": "A",
        "scenario": "green default scenario", "scenario_neutral": "neutral scenario"}


class Mock:
    def __init__(self, replies):
        self.replies, self.sent = list(replies), []

    def send(self, payload):
        self.sent.append(payload)
        r = self.replies.pop(0) if self.replies else '{"choice": "B", "p": 0.3}'
        if isinstance(r, Exception):
            raise r
        return {"choices": [{"message": {"content": r}}], "usage": {"prompt_tokens": 100, "completion_tokens": 10}}


def cfg(tmp_path, **kw):
    base = dict(model="m", price_in_per_m=1.0, price_out_per_m=2.0, budget_usd=1.0, max_workers=2,
                requests_per_minute=10 ** 6, out_dir=tmp_path)
    base.update(kw)
    return RunConfig(**base)


def tasks(n):
    return [Task(task_id=f"t{i}", arm="tierA", profile={"tier_a": {"age": "65+"}}, item=ITEM, sample=i) for i in range(n)]


def test_schema_accepts_valid_and_fenced():
    assert parse_choice('{"choice": "A", "p": 0.7}', ["A", "B"]) == {"choice": "A", "p": 0.7}
    assert parse_choice('```json\n{"choice": "B", "p": 0}\n```', ["A", "B"])["choice"] == "B"


@pytest.mark.parametrize("bad", ["", "A", '{"choice": "C", "p": 0.5}', '{"choice": "A", "p": 1.5}',
                                 '{"choice": "A"}', '{"choice": "A", "p": true}', 'Sure! {"choice": "A", "p": 0.5}',
                                 '{"choice": "A", "p": 0.5, "why": "x"}'])
def test_schema_rejects_invalid(bad):
    with pytest.raises(InvalidOutput):
        parse_choice(bad, ["A", "B"])


def test_retry_then_success():
    sleeps = []
    m = Mock([TransportError(429), TransportError(503), '{"choice": "A", "p": 0.9}'])
    out = Client(m, sleep=sleeps.append).chat("m", [{"role": "user", "content": "x"}], 0.7, 20)
    assert len(m.sent) == 3 and len(sleeps) == 2 and "choice" in out["choices"][0]["message"]["content"]


def test_non_retryable_error_raises():
    with pytest.raises(TransportError):
        Client(Mock([TransportError(400)]), sleep=lambda s: None).chat("m", [{"role": "user", "content": "x"}], 0.7, 20)


def test_cache_resume_makes_no_new_calls(tmp_path):
    m1 = Mock([])
    Runner(cfg(tmp_path), Client(m1)).run(tasks(5))
    m2 = Mock([])
    r = Runner(cfg(tmp_path), Client(m2))
    r.run(tasks(5))
    assert len(m1.sent) == 5 and len(m2.sent) == 0 and r.ledger.cached == 5


def test_hard_budget_cutoff(tmp_path):
    # each call costs ~ (100*1 + 10*2)/1e6 = 1.2e-4 actual, estimate is higher; budget allows only a few
    r = Runner(cfg(tmp_path, budget_usd=5e-4, max_workers=1), Client(Mock([])))
    r.run(tasks(50))
    assert r.ledger.stopped_reason == "budget" and r.ledger.skipped_budget >= 1
    assert r.ledger.cost_usd <= 5e-4 and r.ledger.calls < 50


def test_invalid_rate_stop(tmp_path):
    r = Runner(cfg(tmp_path, max_workers=1, budget_usd=100), Client(Mock(["not json"] * 200)))
    r.run(tasks(120))
    assert r.ledger.stopped_reason == "invalid_rate" and r.ledger.calls < 120
    assert not (tmp_path / "cache.jsonl").exists()          # invalid outputs are never cached


def test_secret_never_written(tmp_path, monkeypatch):
    secret = "sk-or-SECRET-123"
    monkeypatch.setenv("OPENROUTER_API_KEY", secret)
    r = Runner(cfg(tmp_path), Client(Mock([TransportError(400, f"bad key {secret}")]), sleep=lambda s: None))
    r.run(tasks(1))
    blob = "".join(p.read_text() for p in tmp_path.glob("*") if p.is_file())
    assert secret not in blob and "[REDACTED]" in blob


def test_rate_limiter_spacing():
    t, slept = [0.0], []
    rl = RateLimiter(60, clock=lambda: t[0], sleep=lambda s: (slept.append(s), t.__setitem__(0, t[0] + s)))
    for _ in range(3):
        rl.wait()
    assert slept == [1.0, 1.0]


def test_prompt_arms_and_condition_blind():
    p = {"tier_a": {"age": "65+"}, "disposition": {"green values": "high"}}
    assert "Person:" not in render("empty", p, ITEM)[1]["content"]
    assert "65+" in render("tierA", p, ITEM)[1]["content"] and "green values" not in render("tierA", p, ITEM)[1]["content"]
    assert "neutral scenario" in render("tierA_condition_blind", p, ITEM)[1]["content"]
    assert "green values: high" in render("disposition", p, ITEM)[1]["content"]
    assert len(TEMPLATE_HASH) == 16


def test_dry_run_transport_is_offline_and_valid():
    d = DryRunTransport()
    out = Client(d).chat("m", [{"role": "user", "content": "x"}], 0.7, 20)
    assert d.calls == 1 and parse_choice(out["choices"][0]["message"]["content"], ["A", "B"])


def test_live_mode_refused_without_authorization(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    assert cli.main(["live", "--model", "openai/gpt-4.1-mini", "--confirm", "yes"]) == 3


def test_tasks_are_k_anonymous_train_only_and_id_free():
    from harness.tasks import build, cells
    from common import load_people
    t, mapping, g = build(k_min=5)
    k = cells(load_people()).value_counts()
    for task in t:
        blob = json.dumps(task.profile) + json.dumps(task.item)
        assert "pid" not in blob.lower() and "twin" not in blob.lower() and "chose" not in blob.lower()
        if task.profile:
            cell = " | ".join(task.profile["tier_a"].values())
            assert k[cell] >= 5
    split = __import__("pandas").read_csv(Path(__file__).resolve().parents[3] / "data/split.csv").set_index("pid").split
    assert (split.loc[mapping.pid.unique()] == "train").all()
