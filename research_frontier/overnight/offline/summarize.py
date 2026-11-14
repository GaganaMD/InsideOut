"""Turn a retrieved run folder into a markdown report (local; no network).

    modal volume get brace-overnight-results <run-id> research_frontier/overnight/runs/modal/
    python research_frontier/overnight/offline/summarize.py research_frontier/overnight/runs/modal/<run-id>
"""
import json
import sys
from pathlib import Path


def f(x, d=3):
    return "n/a" if x is None or x != x else f"{x:+.{d}f}" if isinstance(x, float) else str(x)


def ci(c, d=3):
    return f"[{c[0]:.{d}f}, {c[1]:.{d}f}]"


def main(run: Path) -> str:
    s = json.loads((run / "summary.json").read_text(encoding="utf-8"))
    R = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted((run / "results").glob("*.json"))}
    out = [f"# Run {s['run_id']}", "", f"Tasks {s['n_tasks']}: done {s['done']}, resumed {s['skipped_existing']}, "
           f"failed {s['failed']}; wall {s['wall_s']:.0f} s.", ""]
    for t in s["tasks"]:
        if t["status"] == "failed":
            out.append(f"- FAILED {t['task']}: {t.get('error', '')[:200]}")
    out += ["", "## A. Treatment-effect recovery (training participants; published GPT-4.1 answers)", "",
            "| Study | Spec | Human ATE [95% CI] | LLM ATE [95% CI] | LLM - human [95% CI] | Same sign (boot share) |",
            "|---|---|---|---|---|---|"]
    for r in (r for r in R.values() if r["experiment"] == "A"):
        out.append(f"| {r['study']} | {r['spec']} | {f(r['human_ate'])} {ci(r['human_ate_ci'])} | {f(r['llm_ate'])} "
                   f"{ci(r['llm_ate_ci'])} | {f(r['diff_llm_minus_human'])} {ci(r['diff_llm_minus_human_ci'])} | "
                   f"{r['sign_agrees']} ({r['boot_share_same_sign']:.2f}) |")
    out += ["", "## B. Matched calibration", "",
            "| Study | Spec | Bias | SD ratio LLM/human [CI] | Individual r [CI] | Fit vs constant baseline | TV distance | Cell-mean r (cells) |",
            "|---|---|---|---|---|---|---|---|"]
    for r in (r for r in R.values() if r["experiment"] == "B"):
        i, c = r["individual"], r["individual_ci"]
        fit = (f"Brier {i['brier']:.3f} vs {i['brier_constant_baseline']:.3f}" if "brier" in i
               else f"MAE {i['mae']:.2f} vs {i['mae_constant_baseline']:.2f}")
        cell = r.get("cell", {})
        out.append(f"| {r['study']} | {r['spec']} | {f(i['bias'])} | {i['sd_ratio']:.2f} {ci(c['sd_ratio'], 2)} | "
                   f"{f(i['corr'])} {ci(c['corr'], 2)} | {fit} | {r['distribution']['total_variation']:.2f} | "
                   f"{f(cell.get('corr_cell_means'))} ({cell.get('n_cells', 0)}) |")
    out += ["", "## C. Information value (repeated 5-fold CV within training; loss reduction, positive = first model better)", ""]
    for r in (r for r in R.values() if r["experiment"] == "C"):
        out += [f"**{r['study']}** ({r['loss']}, constant baseline {r['constant_baseline_loss']:.4f}, {r['repeats']} repeats)", "",
                "| Model | Mean loss | Skill vs constant |", "|---|---|---|"]
        out += [f"| {m} | {v['mean_loss']:.4f} | {f(v['skill_vs_constant'])} |" for m, v in r["models"].items()]
        out += ["", "| Contrast | Loss reduction [95% CI] | Share of baseline |", "|---|---|---|"]
        out += [f"| {k} | {f(v['loss_reduction'], 4)} {ci(v['ci'], 4)} | {f(v['share_of_baseline'])} |"
                for k, v in r["contrasts"].items()]
        out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    run = Path(sys.argv[1])
    md = main(run)
    (run / "report.md").write_text(md, encoding="utf-8")
    print(md)
