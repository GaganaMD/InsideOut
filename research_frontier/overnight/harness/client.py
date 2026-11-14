"""OpenRouter chat client with pluggable transport, retries and secret hygiene.

The API key is read from the OPENROUTER_API_KEY environment variable only at send time; it is never stored on the
object, logged, cached or checkpointed. Use MockTransport (tests) or DryRunTransport (no network) by default.
"""
import json
import os
import random
import time
import urllib.error
import urllib.request

URL = "https://openrouter.ai/api/v1/chat/completions"
RETRY_STATUS = {408, 409, 425, 429, 500, 502, 503, 504}


class TransportError(Exception):
    def __init__(self, status: int, message: str = ""):
        super().__init__(f"HTTP {status}: {message[:200]}")
        self.status = status


def redact(text: str) -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "")
    out = text.replace(key, "[REDACTED]") if key else text
    return out


class HttpTransport:
    """Real network transport. Only constructed when the caller explicitly opts in to paid calls."""

    def __init__(self, timeout: float = 60.0):
        self.timeout = timeout

    def send(self, payload: dict) -> dict:
        key = os.environ.get("OPENROUTER_API_KEY")
        if not key:
            raise RuntimeError("OPENROUTER_API_KEY is not set")
        req = urllib.request.Request(URL, data=json.dumps(payload).encode(), method="POST",
                                     headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            raise TransportError(e.code, redact(e.read().decode(errors="ignore"))) from None
        except (urllib.error.URLError, TimeoutError) as e:
            raise TransportError(599, redact(str(e))) from None


class DryRunTransport:
    """No network. Returns a deterministic valid response so the whole pipeline can be exercised for free."""

    def __init__(self):
        self.calls = 0

    def send(self, payload: dict) -> dict:
        self.calls += 1
        n_in = sum(len(m["content"]) for m in payload["messages"]) // 4
        return {"choices": [{"message": {"content": '{"choice": "A", "p": 0.5}'}}],
                "usage": {"prompt_tokens": n_in, "completion_tokens": 12}, "dry_run": True}


class Client:
    def __init__(self, transport, max_retries: int = 5, base_delay: float = 1.0, sleep=time.sleep):
        self.transport, self.max_retries, self.base_delay, self.sleep = transport, max_retries, base_delay, sleep

    def chat(self, model: str, messages: list[dict], temperature: float, max_tokens: int, seed: int | None = None) -> dict:
        payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens,
                   "response_format": {"type": "json_object"}}
        if seed is not None:
            payload["seed"] = seed
        for attempt in range(self.max_retries + 1):
            try:
                return self.transport.send(payload)
            except TransportError as e:
                if e.status not in RETRY_STATUS or attempt == self.max_retries:
                    raise
                self.sleep(self.base_delay * (2 ** attempt) * (1 + 0.25 * random.random()))
        raise RuntimeError("unreachable")
