"""Bounded, resumable, unattended Modal batch for the offline experiments (CPU only; no API calls; no secrets).

    cd research_frontier/overnight/offline
    PYTHONUTF8=1 modal run --detach modal_app.py --mode smoke --run-id smoke-YYYYMMDD-HHMM
    PYTHONUTF8=1 modal run --detach modal_app.py --mode full  --run-id full-YYYYMMDD
    modal volume get brace-overnight-results <run-id> ./results_remote/      # retrieve (any time later)

Design
  * The local entrypoint only SPAWNS a remote orchestrator and exits; with --detach the app keeps running after the
    laptop disconnects. The orchestrator fans out one worker call per task (fixed list; never expands).
  * Durable storage: Modal Volume `brace-overnight-results`, layout <run_id>/{manifest.json, results/, progress/,
    failures/, summary.json, DONE}. Each task's result is committed as soon as it finishes; a re-run with the same
    run_id skips tasks whose result exists (resume after worker restarts or a crashed orchestrator).
  * Bounds: fixed task list; worker timeout 30 min, 1 retry; at most 4 concurrent workers; orchestrator timeout 3 h.
    Worst-case compute (all tasks hit timeout twice) is computed in COST below and must stay under COST_CEILING_USD.
  * Uploaded data: only the two bundle parquets (pseudonymous rows, training participants only) baked into the image.
    No .env, no keys, no Modal secrets are attached.
"""
import json
import time
import traceback
from pathlib import Path

import modal

HERE = Path(__file__).resolve().parent
APP = "brace-overnight-offline"
VOL = "brace-overnight-results"
STUDIES = ["default_eric", "targeting_fairness"]
WORKER = dict(cpu=1.0, memory=1024, timeout=1800, max_containers=4, retries=modal.Retries(max_retries=1))
ORCH = dict(cpu=0.25, memory=512, timeout=3 * 3600, retries=0)
RATES = {"cpu_core_h": 0.0473, "mem_gib_h": 0.008}          # `modal billing rates`, checked 2026-11-14
COST_CEILING_USD = 5.0
PARAMS = {"smoke": {"nb": 200, "repeats": 2}, "failtest": {"nb": 50, "repeats": 1}, "full": {"nb": 10000, "repeats": 100}}


def worst_case_cost(n_tasks: int) -> float:
    w = (WORKER["cpu"] * RATES["cpu_core_h"] + WORKER["memory"] / 1024 * RATES["mem_gib_h"]) * WORKER["timeout"] / 3600
    o = (ORCH["cpu"] * RATES["cpu_core_h"] + ORCH["memory"] / 1024 * RATES["mem_gib_h"]) * ORCH["timeout"] / 3600
    return n_tasks * w * (1 + WORKER["retries"].max_retries) + o


image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("numpy==2.0.0", "pandas==2.3.1", "scikit-learn==1.6.1", "pyarrow==24.0.0")
         .add_local_python_source("experiments", "tasklist")
         .add_local_file(HERE / "bundle/default_eric.parquet", "/data/default_eric.parquet")
         .add_local_file(HERE / "bundle/targeting_fairness.parquet", "/data/targeting_fairness.parquet"))
app = modal.App(APP, image=image)
vol = modal.Volume.from_name(VOL, create_if_missing=True)
ROOT = Path("/results")


def _safe(task: str) -> str:
    return task.replace("|", "__")


def _write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, indent=1, default=float), encoding="utf-8")
    tmp.replace(path)                                         # atomic within the volume
    vol.commit()


@app.function(volumes={str(ROOT): vol}, **WORKER)
def work(run_id: str, task: str, nb: int, repeats: int) -> dict:
    import experiments as ex
    vol.reload()
    base = ROOT / run_id
    res_path = base / "results" / f"{_safe(task)}.json"
    if res_path.exists():
        return {"task": task, "status": "skipped_existing"}
    t0 = time.time()
    _write(base / "progress" / f"{_safe(task)}.json", {"task": task, "status": "started", "t": t0})
    try:
        out = ex.run_task(task, Path("/data"), nb=nb, repeats=repeats)
    except Exception as e:                                    # record, then let Modal's single retry happen
        _write(base / "failures" / f"{_safe(task)}.json",
               {"task": task, "error": repr(e)[:500], "traceback": traceback.format_exc()[-4000:], "t": time.time()})
        raise
    out["runtime_s"] = time.time() - t0
    _write(res_path, out)
    _write(base / "progress" / f"{_safe(task)}.json", {"task": task, "status": "done", "t": time.time(),
                                                        "runtime_s": out["runtime_s"]})
    return {"task": task, "status": "done", "runtime_s": out["runtime_s"]}


@app.function(volumes={str(ROOT): vol}, **ORCH)
def orchestrate(run_id: str, tasks: list[str], nb: int, repeats: int, bundle_manifest: dict) -> dict:
    base = ROOT / run_id
    vol.reload()
    started = time.time()
    _write(base / "manifest.json", {"run_id": run_id, "tasks": tasks, "nb": nb, "repeats": repeats,
                                    "bundle": bundle_manifest, "worker": {k: str(v) for k, v in WORKER.items()},
                                    "worst_case_cost_usd": worst_case_cost(len(tasks)), "started": started})
    outs = list(work.map([run_id] * len(tasks), tasks, [nb] * len(tasks), [repeats] * len(tasks),
                         return_exceptions=True))
    status = []
    for t, o in zip(tasks, outs):
        status.append({"task": t, "status": "failed", "error": repr(o)[:300]} if isinstance(o, BaseException) else o)
    summary = {"run_id": run_id, "n_tasks": len(tasks), "done": sum(s["status"] == "done" for s in status),
               "skipped_existing": sum(s["status"] == "skipped_existing" for s in status),
               "failed": sum(s["status"] == "failed" for s in status), "tasks": status,
               "started": started, "ended": time.time(), "wall_s": time.time() - started}
    _write(base / "summary.json", summary)
    _write(base / "DONE", {"ended": time.time(), "failed": summary["failed"]})
    return summary


@app.local_entrypoint()
def main(mode: str = "smoke", run_id: str = ""):
    import tasklist
    assert mode in PARAMS, mode
    assert run_id and all(c.isalnum() or c in "-_" for c in run_id), "pass --run-id (letters, digits, - and _)"
    tasks = {"full": tasklist.all_tasks(), "smoke": list(tasklist.SMOKE),
             "failtest": ["A|default_eric|no_such_spec"]}[mode]          # failtest: deliberate KeyError
    cost = worst_case_cost(len(tasks))
    assert cost <= COST_CEILING_USD, f"worst-case cost ${cost:.2f} exceeds ceiling"
    manifest = json.loads((HERE / "bundle_manifest.json").read_text(encoding="utf-8"))
    bm = {s: {k: manifest["studies"][s][k] for k in ("n_train", "sha256", "bytes")} for s in STUDIES}
    call = orchestrate.spawn(run_id, tasks, PARAMS[mode]["nb"], PARAMS[mode]["repeats"], bm)
    print(json.dumps({"mode": mode, "run_id": run_id, "tasks": len(tasks), "worst_case_cost_usd": round(cost, 3),
                      "function_call_id": call.object_id, "volume": VOL}, indent=1))
