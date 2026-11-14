"""Resumable runner: cache + checkpoint, concurrency + rate limit, token/cost accounting, hard budget cutoff."""
import hashlib
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from .client import Client, redact

FATAL_STATUS = {401, 402, 403}                      # auth / payment errors stop the whole run
from .prompts import TEMPLATE_HASH, render
from .schema import InvalidOutput, parse_choice


@dataclass
class RunConfig:
    model: str
    price_in_per_m: float           # USD per 1M prompt tokens (verified from provider before a paid run)
    price_out_per_m: float          # USD per 1M completion tokens
    budget_usd: float               # hard cap; nothing new is sent once spent + reserve would exceed it
    temperature: float = 0.7
    max_tokens: int = 40
    max_workers: int = 4
    requests_per_minute: int = 60
    out_dir: Path = Path("research_frontier/overnight/runs/dry")
    max_invalid_rate: float = 0.02  # stop if malformed outputs exceed this share (after 50 calls)


@dataclass
class Task:
    task_id: str                    # cell/arm/item/sample id; NEVER a participant ID
    arm: str
    profile: dict
    item: dict
    sample: int = 0

    def key(self, cfg: RunConfig) -> str:
        blob = json.dumps([cfg.model, cfg.temperature, cfg.max_tokens, TEMPLATE_HASH, self.arm, self.profile,
                           self.item, self.sample], sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()


@dataclass
class Ledger:
    calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    invalid: int = 0
    cached: int = 0
    skipped_budget: int = 0
    stopped_reason: str = ""
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False)


class RateLimiter:
    def __init__(self, rpm: int, clock=time.monotonic, sleep=time.sleep):
        self.interval, self.clock, self.sleep, self.next, self.lock = 60.0 / max(rpm, 1), clock, sleep, 0.0, threading.Lock()

    def wait(self):
        with self.lock:
            now = self.clock()
            if now < self.next:
                self.sleep(self.next - now)
            self.next = max(now, self.next) + self.interval


class Runner:
    def __init__(self, cfg: RunConfig, client: Client, limiter: RateLimiter | None = None):
        self.cfg, self.client = cfg, client
        self.limiter = limiter or RateLimiter(cfg.requests_per_minute)
        cfg.out_dir.mkdir(parents=True, exist_ok=True)
        self.cache_path = cfg.out_dir / "cache.jsonl"       # completed results (resume source)
        self.log_path = cfg.out_dir / "events.jsonl"        # errors / budget events (redacted)
        self.ledger = Ledger()
        self.cache = self._load_cache()
        self.stop = threading.Event()

    def _load_cache(self) -> dict:
        cache = {}
        if self.cache_path.exists():
            for line in self.cache_path.read_text(encoding="utf-8").splitlines():
                rec = json.loads(line)
                cache[rec["key"]] = rec
        return cache

    def _append(self, path: Path, rec: dict):
        with self.ledger.lock, open(path, "a", encoding="utf-8") as f:
            f.write(redact(json.dumps(rec)) + "\n")

    def cost(self, usage: dict) -> float:
        return (usage.get("prompt_tokens", 0) * self.cfg.price_in_per_m + usage.get("completion_tokens", 0) * self.cfg.price_out_per_m) / 1e6

    def estimate(self, messages: list[dict]) -> float:
        n_in = sum(len(m["content"]) for m in messages) / 3.5      # conservative chars-per-token
        return self.cost({"prompt_tokens": n_in, "completion_tokens": self.cfg.max_tokens})

    def _one(self, task: Task):
        k = task.key(self.cfg)
        if k in self.cache:
            with self.ledger.lock:
                self.ledger.cached += 1
            return self.cache[k]
        if self.stop.is_set():
            return None
        messages = render(task.arm, task.profile, task.item)
        est = self.estimate(messages)
        with self.ledger.lock:
            if self.ledger.cost_usd + est > self.cfg.budget_usd:
                self.ledger.skipped_budget += 1
                self.ledger.stopped_reason = "budget"
                self.stop.set()
                return None
            self.ledger.cost_usd += est                         # reserve before sending
        self.limiter.wait()
        try:
            resp = self.client.chat(self.cfg.model, messages, self.cfg.temperature, self.cfg.max_tokens)
        except Exception as e:
            with self.ledger.lock:
                self.ledger.cost_usd -= est
            self._append(self.log_path, {"event": "error", "task": task.task_id, "error": str(e)[:300]})
            if getattr(e, "status", None) in FATAL_STATUS:     # bad/expired key or no credit: never keep sending
                with self.ledger.lock:
                    self.ledger.stopped_reason = f"fatal_http_{e.status}"
                self.stop.set()
            return None
        usage = resp.get("usage", {})
        actual = self.cost(usage)
        text = resp["choices"][0]["message"]["content"]
        with self.ledger.lock:
            self.ledger.cost_usd += actual - est
            self.ledger.calls += 1
            self.ledger.prompt_tokens += usage.get("prompt_tokens", 0)
            self.ledger.completion_tokens += usage.get("completion_tokens", 0)
        try:
            parsed, valid = parse_choice(text, list(task.item["options"])), True
        except InvalidOutput as e:
            parsed, valid = {"error": str(e)[:200]}, False
            with self.ledger.lock:
                self.ledger.invalid += 1
                if self.ledger.calls >= 50 and self.ledger.invalid / self.ledger.calls > self.cfg.max_invalid_rate:
                    self.ledger.stopped_reason = "invalid_rate"
                    self.stop.set()
        rec = {"key": k, "task_id": task.task_id, "arm": task.arm, "sample": task.sample, "model": self.cfg.model,
               "template": TEMPLATE_HASH, "valid": valid, "result": parsed, "usage": usage, "cost_usd": actual,
               "served_model": resp.get("model"), "provider": resp.get("provider"), "generation_id": resp.get("id"),
               "dry_run": bool(resp.get("dry_run"))}
        if valid:                                             # only valid results are cached (invalid ones retry on resume)
            self._append(self.cache_path, rec)
            self.cache[k] = rec
        else:
            self._append(self.log_path, {"event": "invalid", **{x: rec[x] for x in ("task_id", "arm", "result")}})
        return rec

    def run(self, tasks: list[Task]) -> list:
        with ThreadPoolExecutor(max_workers=self.cfg.max_workers) as ex:
            results = list(ex.map(self._one, tasks))
        summary = {k: v for k, v in self.ledger.__dict__.items() if k != "lock"}
        summary["retries"] = list(getattr(self.client, "retries", []))
        (self.cfg.out_dir / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
        return results
