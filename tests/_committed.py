"""Compare working-tree outputs with their committed (HEAD) versions, tolerant of platform noise.

Byte-equality is too strict across environments: Windows writes CRLF, and different numpy/BLAS builds differ in the
15th-17th significant digit. CSV/JSON are compared numerically (rtol 1e-9); other text after normalising line endings;
binary files (PNG) are skipped (rendering differs by matplotlib build).
"""
import io
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RTOL = 1e-9


def _git(*args) -> bytes:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=True).stdout


def tracked(paths: list[str]) -> list[str]:
    return [p for p in _git("ls-files", "--", *paths).decode().splitlines() if p]


def _eq_json(a, b) -> bool:
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_eq_json(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_eq_json(x, y) for x, y in zip(a, b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return bool(np.isclose(a, b, rtol=RTOL, atol=1e-12, equal_nan=True))
    return a == b


def _eq_csv(a: bytes, b: bytes) -> bool:
    x, y = pd.read_csv(io.BytesIO(a)), pd.read_csv(io.BytesIO(b))
    if list(x.columns) != list(y.columns) or x.shape != y.shape:
        return False
    for c in x.columns:
        if pd.api.types.is_numeric_dtype(x[c]) and pd.api.types.is_numeric_dtype(y[c]):
            if not np.allclose(x[c], y[c], rtol=RTOL, atol=1e-12, equal_nan=True):
                return False
        elif not x[c].astype(str).equals(y[c].astype(str)):
            return False
    return True


def mismatches(paths: list[str]) -> list[str]:
    bad = []
    for p in tracked(paths):
        f = ROOT / p
        if not f.exists():
            bad.append(f"{p} (missing)")
            continue
        new, old = f.read_bytes(), _git("show", f"HEAD:{p}")
        if p.endswith(".png"):
            continue
        if p.endswith(".csv"):
            ok = _eq_csv(new, old)
        elif p.endswith(".json"):
            ok = _eq_json(json.loads(new), json.loads(old))
        else:
            ok = new.replace(b"\r\n", b"\n") == old.replace(b"\r\n", b"\n")
        if not ok:
            bad.append(p)
    return bad
