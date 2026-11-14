"""Strict JSON output validation."""
import json
import re


class InvalidOutput(ValueError):
    pass


def parse_choice(text: str, option_keys: list[str]) -> dict:
    """Accept a single JSON object (optionally inside ```json fences). Require 'choice' in option_keys and 0<=p<=1."""
    if not isinstance(text, str) or not text.strip():
        raise InvalidOutput("empty output")
    t = text.strip()
    m = re.fullmatch(r"```(?:json)?\s*(\{.*\})\s*```", t, re.S)
    if m:
        t = m.group(1)
    if not (t.startswith("{") and t.endswith("}")):
        raise InvalidOutput("not a bare JSON object")
    try:
        obj = json.loads(t)
    except json.JSONDecodeError as e:
        raise InvalidOutput(f"bad json: {e}") from e
    if set(obj) != {"choice", "p"}:
        raise InvalidOutput(f"unexpected keys {sorted(obj)}")
    if obj["choice"] not in option_keys:
        raise InvalidOutput(f"choice {obj['choice']!r} not in {option_keys}")
    p = obj["p"]
    if isinstance(p, bool) or not isinstance(p, (int, float)) or not 0 <= p <= 1:
        raise InvalidOutput(f"p out of range: {p!r}")
    return {"choice": obj["choice"], "p": float(p)}
