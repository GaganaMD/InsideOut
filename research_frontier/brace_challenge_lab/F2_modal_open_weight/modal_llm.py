"""Open-weight next-token probability scorer on Modal GPU (L4). No API keys, no secrets, no participant data.

Only prompts.jsonl (synthetic cell descriptions, estimated aggregate profiles, public scenario text) is sent.
For each prompt we read the model's next-token distribution after the chat template's assistant prefix and keep
P("A") and P("B") (single tokens) plus their total mass. No sampling: deterministic forward passes.

    cd research_frontier/brace_challenge_lab/F2_modal_open_weight
    PYTHONUTF8=1 PYTHONIOENCODING=utf-8 modal run modal_llm.py --mode smoke --model qwen25_7b
    PYTHONUTF8=1 PYTHONIOENCODING=utf-8 modal run modal_llm.py --mode full  --model qwen25_7b --revision <sha from smoke>
"""
import json
import time
from pathlib import Path

import modal

HERE = Path(__file__).resolve().parent
MODELS = {"qwen25_7b": "Qwen/Qwen2.5-7B-Instruct", "qwen3_4b": "Qwen/Qwen3-4B-Instruct-2507"}
GPU = ["L4", "A10G", "L40S"]                          # fallbacks: L4 capacity was unavailable for 9+ min on 2026-11-14
RATES = {"gpu_h_max": 1.95, "cpu_core_h": 0.0473, "mem_gib_h": 0.008}   # L40S worst case; `modal billing rates`, 2026-11-14
CPU, MEM_GIB = 2.0, 16
TIMEOUT = {"smoke": 1200, "full": 1800}
BUDGET_USD = 5.0

image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("torch==2.5.1", "transformers==4.51.3", "accelerate==1.2.1", "huggingface_hub==0.30.2")
         .env({"HF_HOME": "/cache", "HF_HUB_DISABLE_TELEMETRY": "1"}))
app = modal.App("brace-f2-open-weight", image=image)
cache = modal.Volume.from_name("brace-hf-cache", create_if_missing=True)


def worst_case_usd(mode: str) -> float:
    return TIMEOUT[mode] / 3600 * (RATES["gpu_h_max"] + CPU * RATES["cpu_core_h"] + MEM_GIB * RATES["mem_gib_h"])


@app.function(gpu=GPU, cpu=CPU, memory=MEM_GIB * 1024, timeout=TIMEOUT["full"], retries=0, volumes={"/cache": cache})
def score(model_id: str, revision: str | None, prompts: list[dict], repeat_first: int = 0, batch: int = 16) -> dict:
    import torch
    from huggingface_hub import model_info
    from transformers import AutoModelForCausalLM, AutoTokenizer
    t0 = time.time()
    info = model_info(model_id, revision=revision)
    sha = info.sha
    tok = AutoTokenizer.from_pretrained(model_id, revision=sha)
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(model_id, revision=sha, torch_dtype=torch.bfloat16, device_map="cuda")
    model.eval()
    cache.commit()
    t_load = time.time() - t0
    ids = {L: tok.encode(L, add_special_tokens=False) for L in ("A", "B")}
    assert all(len(v) == 1 for v in ids.values()), ids
    a_id, b_id = ids["A"][0], ids["B"][0]

    def run(ps):
        out = []
        for i in range(0, len(ps), batch):
            chunk = ps[i:i + batch]
            texts = [tok.apply_chat_template(p["messages"], tokenize=False, add_generation_prompt=True) for p in chunk]
            enc = tok(texts, return_tensors="pt", padding=True).to("cuda")
            with torch.no_grad():
                logits = model(**enc).logits[:, -1, :].float()
            prob = torch.softmax(logits, dim=-1)
            top = prob.argmax(-1)
            for p, row, tp, n in zip(chunk, prob, top, enc["attention_mask"].sum(1)):
                pa, pb = float(row[a_id]), float(row[b_id])
                out.append({"id": p["id"], "pA": pa, "pB": pb, "mass": pa + pb, "top_token": tok.decode([int(tp)]),
                            "n_prompt_tokens": int(n)})
        return out
    t1 = time.time()
    res = run(prompts)
    rep = run(prompts[:repeat_first]) if repeat_first else []
    return {"model_id": model_id, "revision": sha, "license": (info.card_data or {}).get("license"),
            "gpu": torch.cuda.get_device_name(0), "load_s": t_load, "score_s": time.time() - t1,
            "results": res, "repeat": rep, "torch": torch.__version__}


@app.local_entrypoint()
def main(mode: str = "smoke", model: str = "qwen25_7b", revision: str = ""):
    assert mode in TIMEOUT and model in MODELS
    assert worst_case_usd(mode) <= BUDGET_USD
    prompts = [json.loads(l) for l in (HERE / "prompts.jsonl").read_text(encoding="utf-8").splitlines()]
    if mode == "smoke":                                   # 4 empty + 4 of each other format, then repeat 8 for determinism
        pick = [p for p in prompts if p["fmt"] == "empty"]
        for f in ("demo", "profile", "narrative"):
            pick += [p for p in prompts if p["fmt"] == f][::97][:4]
        prompts, rep = pick, 8
    else:
        rep = 32
    for p in prompts:                                     # defence in depth: nothing outcome-like leaves the machine
        blob = json.dumps(p["messages"]).lower()
        assert not any(w in blob for w in ("pid", "twin", "chose", "y_human")), p["id"]
    t0 = time.time()
    out = score.remote(MODELS[model], revision or None, [{"id": p["id"], "messages": p["messages"]} for p in prompts], rep)
    out.update(mode=mode, model_key=model, n_prompts=len(prompts), wall_s=time.time() - t0,
               worst_case_usd=worst_case_usd(mode))
    dst = HERE / "outputs" / f"{mode}__{model}.json"
    dst.parent.mkdir(exist_ok=True)
    dst.write_text(json.dumps(out, indent=1), encoding="utf-8")
    r = out["results"]
    rep_diff = max((abs(a["pA"] - b["pA"]) + abs(a["pB"] - b["pB"]) for a, b in zip(r, out["repeat"])), default=None)
    print(json.dumps({"model": out["model_id"], "revision": out["revision"], "license": out["license"], "gpu": out["gpu"],
                      "load_s": round(out["load_s"], 1), "score_s": round(out["score_s"], 1), "wall_s": round(out["wall_s"], 1),
                      "n": len(r), "mean_mass": sum(x["mass"] for x in r) / len(r), "min_mass": min(x["mass"] for x in r),
                      "top_tokens": sorted({x["top_token"] for x in r}), "max_repeat_diff": rep_diff,
                      "worst_case_usd": round(out["worst_case_usd"], 3), "saved": str(dst)}, indent=1))
