"""Reproducible README figures (SVG + PNG) and their source-data tables.

    python tools/make_figures.py          # after run_all.py (needs data/processed and the committed result files)

Figure 1  Held-out R2 by construct: frozen confirmatory ridge model (Tier A, fitted on train), scored on the frozen
          test split. Social desirability and CRT use the corrected item-level scores (post-audit re-scoring of the SAME
          model; the shipped scores are defective). 95% intervals: bootstrap over held-out participants CONDITIONAL ON THE
          FITTED MODEL (model-refit uncertainty is not included; see research_frontier/01_project_red_team.md A1-a).
          Checks: point estimates must equal results/holdout_predictability.csv (unaffected constructs) and
          reports/final_audit/corrected_scores/predictability_sd_crt.csv (SD, CRT).
Figure 2  Persona standardized differences (d vs train population) with 95% CIs, training members vs held-out members,
          corrected SD/CRT. Checks against reports/personas/*.json (frozen) and corrected_scores/personas_sd_crt.csv.
Figure 3  EXPLORATORY, train only (n = 428): out-of-fold Brier change vs the prevalence baseline for the hypothetical
          green-energy choice. Inputs: reports/exploratory/oof_predictions.csv and
          reports/robustness/demographic_complexity/oof_green.csv (same participants and folds; checked).
          95% intervals: paired participant bootstrap.
Figure numbers follow the order in which the README displays the figures (Figure 4 = tools/render_mermaid.py).
Nothing here selects models or changes any frozen output.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from common import CONSTRUCTS, TIER_A, load_people  # noqa: E402
from personas import load_config, mask, parse_criteria  # noqa: E402
from predictability import model  # noqa: E402

FIG = ROOT / "figures"
DATA = FIG / "data"
SEED, NB = 20261114, 2000
# Okabe-Ito colour-blind-safe palette
BLUE, ORANGE, GREEN, GREY, VERM, SKY = "#0072B2", "#E69F00", "#009E73", "#7f7f7f", "#D55E00", "#56B4E9"
NICE = {"green": "Green values", "social_desirability": "Social desirability†", "spendthrift": "Spendthrift",
        "crt": "Cognitive reflection (CRT)†", "dictator_give": "Dictator giving", "neuroticism": "Neuroticism"}
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "svg.hashsalt": "brace",
                     "svg.fonttype": "path", "font.family": "DejaVu Sans"})


def save(fig, name):
    fig.savefig(FIG / f"{name}.svg", metadata={"Date": None, "Creator": None})
    fig.savefig(FIG / f"{name}.png", dpi=200, metadata={"Software": None})
    plt.close(fig)


# ----------------------------------------------------------------------------- Figure 1
def fig1() -> pd.DataFrame:
    p = load_people(corrected=True)
    tr, te = p[p.split == "train"], p[p.split == "test"]
    frozen = pd.read_csv(ROOT / "results/holdout_predictability.csv").set_index("construct")
    corr = pd.read_csv(ROOT / "reports/final_audit/corrected_scores/predictability_sd_crt.csv").set_index("construct")
    rng = np.random.default_rng(SEED)
    rows = []
    for c in CONSTRUCTS:
        m = model(TIER_A).fit(tr[TIER_A].astype(str), tr[c])
        y, pred, base = te[c].to_numpy(), m.predict(te[TIER_A].astype(str)), tr[c].mean()
        r2 = lambda i: 1 - ((y[i] - pred[i]) ** 2).sum() / ((y[i] - base) ** 2).sum()
        est = r2(np.arange(len(y)))
        ref = corr.loc[c, "test_r2_corrected"] if c in corr.index else frozen.loc[c, "test_r2"]
        assert abs(est - ref) < 1e-3, (c, est, ref)  # reference files are rounded to 4 decimals
        boot = [r2(rng.integers(0, len(y), len(y))) for _ in range(NB)]
        rows.append(dict(construct=c, heldout_r2=est, lo=np.quantile(boot, .025), hi=np.quantile(boot, .975),
                         n_test=len(y), scoring="corrected (post-audit)" if c in corr.index else "frozen confirmatory",
                         legacy_heldout_r2=frozen.loc[c, "test_r2"]))
    d = pd.DataFrame(rows).sort_values("heldout_r2")
    d.round(4).to_csv(DATA / "fig1_heldout_r2.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    yy = np.arange(len(d))
    for i, r in enumerate(d.itertuples()):
        col = BLUE if r.scoring.startswith("frozen") else ORANGE
        ax.plot([r.lo, r.hi], [i, i], color=col, lw=2, solid_capstyle="butt")
        ax.plot(r.heldout_r2, i, "o", color=col, ms=7, mfc=col if col == BLUE else "white", mew=2)
        ax.text(max(r.hi, r.heldout_r2) + 0.006, i, f"{r.heldout_r2:.2f}", va="center", fontsize=9)
    ax.axvline(0, color="black", lw=0.8)
    ax.set_yticks(yy, [NICE[c] for c in d.construct])
    ax.set_xlim(-0.06, 0.30)
    ax.set_xlabel("Held-out R² (n = 616): variance explained by 10 census-style variables")
    fig.suptitle("What census-observable facts predict about each construct (held-out data)", x=0.01, ha="left",
                 fontsize=11, fontweight="bold")
    h1 = ax.plot([], [], "o", color=BLUE, label="frozen confirmatory estimate")[0]
    h2 = ax.plot([], [], "o", color=ORANGE, mfc="white", mew=2, label="† corrected item-level scoring (post-audit)")[0]
    ax.legend(handles=[h1, h2], loc="lower right", frameon=False, fontsize=8.5)
    fig.text(0.01, 0.01, "R² = share of individual-level variance predicted for held-out participants (vs the population mean). "
             "Bars = 95% bootstrap\nintervals conditional on the fitted model; they omit model-refit uncertainty, "
             "which is larger for the weakest constructs.", fontsize=7.5, color="#333333")
    fig.tight_layout(rect=(0, 0.1, 1, 0.95))
    save(fig, "fig1_heldout_r2")
    return d


# ----------------------------------------------------------------------------- Figure 2
def fig_green_choice() -> pd.DataFrame:
    a = pd.read_csv(ROOT / "reports/exploratory/oof_predictions.csv")
    b = pd.read_csv(ROOT / "reports/robustness/demographic_complexity/oof_green.csv")
    assert (a.pid.to_numpy() == b.pid.to_numpy()).all() and (a.y == b.y).all() and (a.fold == b.fold).all()
    assert np.allclose(a.M0, b.D0) and np.allclose(a.M1, b.D2)  # same baseline and same full-Tier-A model
    y = a.y.to_numpy()
    models = [  # (column, frame, label, group)
        ("D1", b, "Age + income + education", "Demographics only"),
        ("M1", a, "All 10 census variables", "Demographics only"),
        ("D3", b, "All 10, strongly regularised", "Demographics only"),
        ("D4", b, "All 10, regularisation tuned", "Demographics only"),
        ("M1D", a, "All 10 + randomised default", "+ randomised default"),
        ("M2", a, "All 10 + measured green values", "+ measured green values"),
        ("M3", a, "All 10 + green values + default", "+ measured green values"),
    ]
    brier = lambda p, i: np.mean((y[i] - p[i]) ** 2)
    base = a.M0.to_numpy()
    rng = np.random.default_rng(SEED)
    idx = [rng.integers(0, len(y), len(y)) for _ in range(NB)]
    allidx = np.arange(len(y))
    rows = [dict(model="M0", label="Prevalence baseline", group="Baseline", brier=brier(base, allidx),
                 d_brier=0.0, lo=np.nan, hi=np.nan)]
    for col, f, lab, grp in models:
        p = f[col].to_numpy()
        diffs = [brier(p, i) - brier(base, i) for i in idx]
        rows.append(dict(model=col, label=lab, group=grp, brier=brier(p, allidx), d_brier=brier(p, allidx) - brier(base, allidx),
                         lo=np.quantile(diffs, .025), hi=np.quantile(diffs, .975)))
    d = pd.DataFrame(rows)
    d.round(5).to_csv(DATA / "fig3_green_choice_brier.csv", index=False)

    colors = {"Demographics only": GREY, "+ randomised default": ORANGE, "+ measured green values": GREEN}
    sub = d[d.model != "M0"].reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    for i, r in sub.iterrows():
        yy = len(sub) - 1 - i
        ax.plot([r.lo, r.hi], [yy, yy], color=colors[r.group], lw=2)
        ax.plot(r.d_brier, yy, "o", color=colors[r.group], ms=7)
        ax.text(0.031, yy, f"Brier {r.brier:.3f}", va="center", fontsize=8.5, color="#333333")
    ax.axvline(0, color="black", lw=0.8)
    ax.set_yticks(range(len(sub)), list(sub.label[::-1]))
    ax.set_xlim(-0.06, 0.045)
    ax.set_xlabel(f"Δ out-of-fold Brier vs prevalence baseline (Brier {d.brier[0]:.3f});  ← better")
    fig.suptitle("Does measuring one attitude beat demographics?\nEXPLORATORY · training split only (n = 428)",
                 x=0.01, ha="left", fontsize=10.5, fontweight="bold")
    for g, c in colors.items():
        ax.plot([], [], "o", color=c, label=g)
    ax.legend(loc="upper left", frameon=False, fontsize=8.5)
    fig.text(0.01, 0.01, "Outcome: a HYPOTHETICAL survey choice of a \\$39/month renewable tariff over a \\$32 one (not a purchase). "
             "Logistic models; same\nparticipants and 5 folds for every model; preprocessing inside folds; bars = 95% paired "
             "participant-bootstrap intervals.", fontsize=7.5, color="#333333")
    fig.tight_layout(rect=(0, 0.1, 1, 0.92))
    save(fig, "fig3_green_choice_brier")
    return d


# ----------------------------------------------------------------------------- Figure 3
def fig_personas() -> pd.DataFrame:
    p = load_people(corrected=True)
    tr, te = p[p.split == "train"], p[p.split == "test"]
    corr = pd.read_csv(ROOT / "reports/final_audit/corrected_scores/personas_sd_crt.csv")
    rows = []
    for key, cfg in load_config().items():
        crit = parse_criteria(cfg["criteria"], p)
        mt, mh = tr[mask(tr, crit)], te[mask(te, crit)]
        frozen = {r["construct"]: r for r in pd.read_json(ROOT / f"reports/personas/{cfg['name']}.json", typ="series")["inner"]}
        for c in CONSTRUCTS:
            mu0, sd0 = tr[c].mean(), tr[c].std(ddof=1)
            d_tr = (mt[c].mean() - mu0) / sd0
            se_tr = mt[c].std(ddof=1) / np.sqrt(len(mt)) / sd0
            d_te = (mh[c].mean() - mu0) / sd0
            se_te = mh[c].std(ddof=1) / np.sqrt(len(mh)) / sd0
            if c in ("social_desirability", "crt"):
                ref = corr[(corr.persona == cfg["name"]) & (corr.construct == c)].iloc[0]
                assert abs(d_tr - ref.d_train_corrected) < 1e-3 and abs(d_te - ref.d_test_corrected) < 1e-3
            else:
                assert abs(d_tr - frozen[c]["d"]) < 1e-9 and abs(d_tr - 1.96 * se_tr - frozen[c]["d_lo"]) < 1e-9
            rows.append(dict(persona=key, persona_name=cfg["name"], construct=c, n_train=len(mt), n_test=len(mh),
                             d_train=d_tr, lo_train=d_tr - 1.96 * se_tr, hi_train=d_tr + 1.96 * se_tr,
                             d_heldout=d_te, lo_heldout=d_te - 1.96 * se_te, hi_heldout=d_te + 1.96 * se_te,
                             scoring="corrected" if c in ("social_desirability", "crt") else "frozen (unaffected)"))
    d = pd.DataFrame(rows)
    d.round(4).to_csv(DATA / "fig2_persona_d.csv", index=False)

    titles = {"P1": "P1 · age 65+", "P2": "P2 · age 18–49, income < $50k", "P3": "P3 · age 18–29, never married"}
    order = ["neuroticism", "social_desirability", "green", "spendthrift", "crt", "dictator_give"]
    fig, axes = plt.subplots(1, 3, figsize=(9.6, 3.9), sharey=True)
    for ax, key in zip(axes, ["P1", "P2", "P3"]):
        s = d[d.persona == key].set_index("construct").loc[order]
        ax.axvspan(-0.2, 0.2, color="#eeeeee", zorder=0)
        ax.axvline(0, color="black", lw=0.8)
        for i, c in enumerate(order):
            r, yy = s.loc[c], len(order) - 1 - i
            ax.plot([r.lo_train, r.hi_train], [yy + 0.15] * 2, color=BLUE, lw=2)
            ax.plot(r.d_train, yy + 0.15, "o", color=BLUE, ms=5.5)
            ax.plot([r.lo_heldout, r.hi_heldout], [yy - 0.15] * 2, color=VERM, lw=2)
            ax.plot(r.d_heldout, yy - 0.15, "s", color=VERM, ms=5.5, mfc="white", mew=1.6)
        if key == "P3":
            gy = len(order) - 1 - order.index("green")
            ax.annotate("fragile: mostly men;\nholds in 3 of 6 redefinitions", xy=(-0.12, gy), xytext=(0.06, gy),
                        va="center",
                        fontsize=7.5, color=VERM, arrowprops=dict(arrowstyle="->", color=VERM, lw=0.8))
        ax.set_title(f"{titles[key]}\n(n = {int(s.n_train.iloc[0])} train / {int(s.n_test.iloc[0])} held out)", fontsize=9)
        ax.set_xlim(-1.0, 1.0)
        ax.set_xlabel("d vs population (SD units)", fontsize=8.5)
    axes[0].set_yticks(range(len(order)), [NICE[c] for c in order[::-1]])
    axes[0].plot([], [], "o", color=BLUE, label="training members (persona built here)")
    axes[0].plot([], [], "s", color=VERM, mfc="white", mew=1.6, label="held-out members (never used to build it)")
    fig.legend(loc="lower center", ncol=2, frameon=False, fontsize=8.5, bbox_to_anchor=(0.5, 0.06))
    fig.suptitle("Persona differences from the population, with 95% confidence intervals", x=0.01, ha="left",
                 fontsize=11, fontweight="bold")
    fig.text(0.01, 0.005, "Grey band: |d| < 0.2 (small). † corrected item-level scores (shipped scores are defective). "
             "Group mean differences, not individual predictions:\na random 65+ panelist is still more neurotic than a random "
             "18–29-year-old 25% of the time.", fontsize=7.5, color="#333333")
    fig.tight_layout(rect=(0, 0.14, 1, 0.95))
    save(fig, "fig2_persona_d")
    return d


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    for f in (fig1, fig_personas, fig_green_choice):
        print(f.__name__, "\n", f().round(3).to_string(index=False))


if __name__ == "__main__":
    main()
