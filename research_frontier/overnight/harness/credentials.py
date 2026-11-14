"""API-key handling. The key value is never printed, logged, returned in messages, cached or written anywhere.

Supported variable names (first non-empty wins): OPEN_ROUTER_KEY (the repository's .env), OPENROUTER_API_KEY (alias).
The .env file is loaded ONLY when explicitly requested (live mode or `check-key`); it is never loaded in tests.
"""
import os
import subprocess
from pathlib import Path

ENV_NAMES = ("OPEN_ROUTER_KEY", "OPENROUTER_API_KEY")
ROOT = Path(__file__).resolve().parents[3]
DOTENV = ROOT / ".env"


def load_env_file(path: Path = DOTENV) -> bool:
    """Load KEY=VALUE pairs into os.environ without overriding existing variables. Returns True if the file existed."""
    if not path.exists():
        return False
    try:
        from dotenv import load_dotenv
        load_dotenv(path, override=False)
    except ImportError:                       # minimal fallback parser
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.removeprefix("export ").split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    return True


def get_key() -> str | None:
    for name in ENV_NAMES:
        v = os.getenv(name)
        if v and v.strip():
            return v.strip()
    return None


def key_present() -> bool:
    return get_key() is not None


def secret_values() -> list[str]:
    return [v for v in (os.getenv(n) for n in ENV_NAMES) if v]


def dotenv_is_safe(path: Path = DOTENV) -> dict:
    """Checks that .env is git-ignored and untracked (never reads or reveals its contents)."""
    rel = path.relative_to(ROOT).as_posix()
    run = lambda *a: subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)
    return {"exists": path.exists(), "ignored": run("check-ignore", "-q", rel).returncode == 0,
            "tracked": run("ls-files", "--error-unmatch", rel).returncode == 0,
            "in_history": bool(run("log", "--all", "--oneline", "--", rel).stdout.strip())}
