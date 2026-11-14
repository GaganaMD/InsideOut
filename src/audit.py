"""First-hour data audit + frozen participant split.

Reads only files fetched by src/download.py. Writes:
  data/processed/outer.parquet       outer-layer variables (labels) per pid
  data/processed/scores.parquet      pre-computed construct scores per pid (waves 1-3)
  data/processed/mega_<study>.parquet  tidy outcome tables for the three audited studies
  data/split.csv                     frozen 70/30 participant split (pid, split)
  audit/*.json|csv                   audit tables reported in audit/AUDIT.md

Split is made from pid + outer-layer strata only; no outcome or inner-layer variable is read
before it is written. Re-running reproduces it byte-for-byte (checked against its sha256).
"""
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TWIN = ROOT / "data/raw/Twin-2K-500"
MEGA = ROOT / "data/raw/Twin-2K-500-Mega-Study"
PROC = ROOT / "data/processed"
AUD = ROOT / "audit"
SEED = 20261114
TEST_FRAC = 0.30
STUDIES = ["default_eric", "preference_redistribution", "context_effects"]

# ---------------------------------------------------------------- outer layer
# QIDs and option labels verified against question_catalog.json (BlockName = Demographics).
OUTER = {
    # qid: (name, tier, observability rationale)
    "QID11": ("region", "A", "Census region of residence; ACS/decennial census."),
    "QID12": ("sex", "A", "Sex at birth; census/ACS."),
    "QID13": ("age_band", "A", "Age; census/ACS. Collected only in 4 bands (18-29/30-49/50-64/65+)."),
    "QID14": ("education", "A", "Educational attainment; ACS."),
    "QID15": ("race", "A", "Race/Hispanic origin; census/ACS (survey collapses Hispanic into race)."),
    "QID16": ("citizen", "A", "Citizenship; ACS."),
    "QID17": ("marital", "A", "Marital/partner status; ACS."),
    "QID21": ("income", "A", "Household/family income band; ACS."),
    "QID23": ("hh_size", "A", "Household size; census/ACS."),
    "QID24": ("employment", "A", "Employment status; ACS/CPS (ACS lacks 'home-maker'/'student' as labels)."),
    "QID20": ("party", "B", "Self-identified party. Proxy for voter-file party registration, public in "
                            "~30 states only; self-ID != registration. Use only with ablation."),
    "QID18": ("religion", "DROP", "Census does not ask religion; only county-level estimates exist "
                                  "and region-level linkage is too coarse."),
    "QID19": ("religious_attendance", "DROP", "Behavioural self-report; only knowable by surveying."),
    "QID22": ("ideology", "DROP", "Attitudinal self-report; inner layer by definition."),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_catalog() -> dict:
    cat = json.load(open(TWIN / "question_catalog_and_human_response_csv/question_catalog.json",
                         encoding="utf-8"))
    items = cat if isinstance(cat, list) else list(cat.values())
    return {q["QuestionID"]: q for q in items}


def build_outer(cat: dict) -> pd.DataFrame:
    lab = pd.read_csv(TWIN / "question_catalog_and_human_response_csv/wave1_3_response_label.csv",
                      usecols=["pid", *OUTER], low_memory=False)
    assert lab.pid.is_unique and len(lab) == 2058
    rows = []
    for qid, (name, tier, why) in OUTER.items():
        opts = cat[qid].get("Options")
        vals = lab[qid]
        unexpected = sorted(set(vals.dropna()) - set(opts or []))
        rows.append(dict(qid=qid, name=name, tier=tier, question=cat[qid]["QuestionText"],
                         options=" | ".join(opts or []), n_missing=int(vals.isna().sum()),
                         unexpected_values=" | ".join(map(str, unexpected)),
                         distribution=json.dumps(vals.value_counts(dropna=False).to_dict()),
                         observability=why))
    pd.DataFrame(rows).to_csv(AUD / "variable_map_outer.csv", index=False)
    outer = lab.rename(columns={q: v[0] for q, v in OUTER.items()})
    for qid, (name, _, _) in OUTER.items():  # ordered categoricals in catalog order
        outer[name] = pd.Categorical(outer[name], categories=cat[qid]["Options"], ordered=True)
    return outer


def build_scores() -> pd.DataFrame:
    frames = []
    for w in (1, 2, 3):
        d = pd.read_csv(TWIN / f"raw_data/wave {w} scores.csv").rename(columns={"TWIN_ID": "pid"})
        assert d.pid.is_unique and len(d) == 2058
        d = d.rename(columns={c: f"w{w}_{c}" for c in d.columns if c != "pid"})
        frames.append(d.set_index("pid"))
    s = pd.concat(frames, axis=1).reset_index()
    rows = []
    for c in s.columns[1:]:
        num = pd.to_numeric(s[c], errors="coerce")
        rows.append(dict(column=c, wave=int(c[1]), dtype=str(s[c].dtype),
                         n_missing=int(s[c].isna().sum()), n_non_numeric=int(num.isna().sum() - s[c].isna().sum()),
                         mean=num.mean(), sd=num.std(), min=num.min(), max=num.max(),
                         n_unique=int(s[c].nunique())))
    pd.DataFrame(rows).round(3).to_csv(AUD / "scores_dictionary.csv", index=False)
    return s


def make_split(outer: pd.DataFrame) -> pd.DataFrame:
    """Stratified on age_band x education(college or not) only. Deterministic."""
    college = outer.education.isin(["College graduate/some postgrad", "Postgraduate"])
    strata = outer.age_band.astype(str) + "|" + np.where(college, "coll", "nocoll")
    rng = np.random.default_rng(SEED)
    test = set()
    for _, idx in outer.groupby(strata, observed=True).groups.items():
        pids = np.sort(outer.loc[idx, "pid"].to_numpy())
        k = int(round(TEST_FRAC * len(pids)))
        test.update(rng.choice(pids, size=k, replace=False).tolist())
    split = pd.DataFrame({"pid": np.sort(outer.pid.to_numpy())})
    split["split"] = np.where(split.pid.isin(test), "test", "train")
    return split


def read_qualtrics(study: str) -> tuple[pd.Series, pd.DataFrame]:
    r = pd.read_csv(MEGA / f".dat/{study}/raw_data/response.csv", low_memory=False)
    qtext, d = r.iloc[0], r.iloc[2:].copy()  # row0 = question text, row1 = ImportId JSON
    d["pid"] = pd.to_numeric(d["TWIN_ID"], errors="coerce").astype("Int64")
    return qtext, d


def tidy_default_eric(d: pd.DataFrame) -> pd.DataFrame:
    # Choice labels verified in survey.qsf:
    #   OPTOUT_Green: 1 = Stay with GreenGrid ($39), 2 = Switch to Twon ($32)   [green is default]
    #   OPTIN_Green : 1 = Stay with Twon ($32),     2 = Switch to GreenGrid ($39) [grey is default]
    out = d[["pid"]].copy()
    oo, oi = pd.to_numeric(d.OPTOUT_Green, errors="coerce"), pd.to_numeric(d.OPTIN_Green, errors="coerce")
    out["green_condition"] = np.select([oo.notna(), oi.notna()], ["green_default", "grey_default"], "missing")
    out["chose_green"] = np.where(oo.notna(), oo == 1, np.where(oi.notna(), oi == 2, np.nan))
    po, pi_ = pd.to_numeric(d.OPTOUT_Organ, errors="coerce"), pd.to_numeric(d.OPTIN_Organ, errors="coerce")
    out["organ_condition"] = np.select([po.notna(), pi_.notna()], ["donor_default", "nondonor_default"], "missing")
    # organ: option 1 = accept current status in both conditions -> donor iff opt-out & 1, or opt-in & 2
    out["organ_donor"] = np.where(po.notna(), po == 1, np.where(pi_.notna(), pi_ == 2, np.nan))
    return out


def tidy_redistribution(d: pd.DataFrame) -> pd.DataFrame:
    keep = ["GOVT_RESPONSIBILITY", "HLTHTAX", "GETAHEAD", "FAIR", "IMMJOBS_GSS", "AFFRMACT_GSS",
            "ATTENTION_CHECK", "PRES20_GSS", "VOTE20_GSS", "SETTYPE"]
    out = d[["pid"]].copy()
    for c in keep:
        out[c] = pd.to_numeric(d[c], errors="coerce")
    return out


def tidy_context(d: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in d.columns if re.match(r"^(Bin\.|Comp_|Attr_)", c)]
    out = d[["pid"]].copy()
    for c in cols:
        out[c] = pd.to_numeric(d[c], errors="coerce")
    return out


def main() -> None:
    PROC.mkdir(parents=True, exist_ok=True)
    AUD.mkdir(exist_ok=True)
    cat = load_catalog()

    # 1. provenance
    files = sorted(p for p in (ROOT / "data/raw").rglob("*") if p.is_file() and ".cache" not in p.parts)
    json.dump([{"path": str(p.relative_to(ROOT)).replace("\\", "/"), "bytes": p.stat().st_size,
                "sha256": sha256(p)} for p in files], open(AUD / "sources.json", "w"), indent=1)

    # 2. outer layer + split (BEFORE reading any inner-layer or outcome data)
    outer = build_outer(cat)
    split = make_split(outer)
    split_path = ROOT / "data/split.csv"
    if split_path.exists():
        old = pd.read_csv(split_path)
        assert old.equals(split), "split.csv differs from deterministic regeneration - refusing to overwrite"
    split.to_csv(split_path, index=False, lineterminator="\n")
    outer.to_parquet(PROC / "outer.parquet", index=False)

    # 3. inner layer scores
    scores = build_scores()
    scores.to_parquet(PROC / "scores.parquet", index=False)

    # 4. Mega-Study studies: join + tidy outcomes
    join, exp = {}, {}
    twin_pids = set(outer.pid)
    tidy = {"default_eric": tidy_default_eric, "preference_redistribution": tidy_redistribution,
            "context_effects": tidy_context}
    for s in STUDIES:
        qtext, d = read_qualtrics(s)
        pq = pd.read_parquet(MEGA / f"data/{s}-00000-of-00001.parquet")
        t = tidy[s](d).merge(split, on="pid", how="left")
        t.to_parquet(PROC / f"mega_{s}.parquet", index=False)
        qsf = open(MEGA / f".dat/{s}/raw_data/survey.qsf", encoding="utf-8", errors="ignore").read()
        join[s] = dict(raw_rows=len(d), raw_pid_missing=int(d.pid.isna().sum()),
                       raw_pid_unique=int(d.pid.nunique()), parquet_rows=len(pq),
                       parquet_pid_format=str(pq.PID.iloc[0]),
                       parquet_pid_set_equals_raw=set(pq.PID.astype(str).str.replace("pid_", "").astype(int)) == set(d.pid.dropna().astype(int)),
                       in_twin=int(d.pid.isin(twin_pids).sum()),
                       train=int((t.split == "train").sum()), test=int((t.split == "test").sum()),
                       finished_all=bool((pd.to_numeric(d.Finished) == 1).all()),
                       incentive_terms_in_qsf={w: len(re.findall(w, qsf, re.I)) for w in
                                               ["bonus", "real money", "lottery", "randomly selected",
                                                "fixed fee", "incentive"]},
                       incentive_context=[m.group(0)[:200] for m in
                                          re.finditer(r".{0,100}(incentive|fixed fee).{0,100}", qsf, re.I)][:3])
    g = pd.read_parquet(PROC / "mega_default_eric.parquet")
    exp["default_eric_green"] = (g.groupby(["green_condition", "split"]).chose_green
                                 .agg(["size", "mean"]).round(3).reset_index().to_dict("records"))
    exp["default_eric_organ"] = (g.groupby(["organ_condition", "split"]).organ_donor
                                 .agg(["size", "mean"]).round(3).reset_index().to_dict("records"))
    json.dump(join, open(AUD / "join_stats.json", "w"), indent=1)
    json.dump(exp, open(AUD / "experiment_cells.json", "w"), indent=1)

    # 5. union of Mega-Study participation vs non-participation, by outer layer (selection check)
    part = outer[["pid", "age_band", "education", "party", "income"]].copy()
    for s in STUDIES:
        part[s] = part.pid.isin(pd.read_parquet(PROC / f"mega_{s}.parquet").pid.dropna().astype(int))
    sel = []
    for v in ["age_band", "education", "party", "income"]:
        for s in STUDIES:
            tab = pd.crosstab(part[v], part[s], normalize="columns").round(3)
            for lvl in tab.index:
                sel.append(dict(variable=v, level=lvl, study=s,
                                share_participants=tab.loc[lvl, True], share_nonparticipants=tab.loc[lvl, False]))
    pd.DataFrame(sel).to_csv(AUD / "selection_by_study.csv", index=False)

    # 6. persona feasibility (outer-layer definitions only)
    college = ["College graduate/some postgrad", "Postgraduate"]
    personas = {
        "P1_retirees_65plus": (outer.age_band == "65+") & (outer.employment == "Retired"),
        "P2_young_grads_lowinc": (outer.age_band == "18-29") & outer.education.isin(college)
                                 & outer.income.isin(["Less than $30,000", "$30,000-$50,000"]),
        "P2b_young_grads_any_income": (outer.age_band == "18-29") & outer.education.isin(college),
        "P2c_under50_grads_lowinc": outer.age_band.isin(["18-29", "30-49"]) & outer.education.isin(college)
                                    & outer.income.isin(["Less than $30,000", "$30,000-$50,000"]),
        "P3_republicans_tierB": outer.party == "Republican",
        "P3alt_noncollege_men_50plus_south_midwest": (outer.sex == "Male") & outer.age_band.isin(["50-64", "65+"])
            & ~outer.education.isin(college)
            & outer.region.astype(str).str.startswith(("South", "Midwest")),
    }
    feas = []
    gm = g.merge(outer[["pid"]], on="pid")
    for name, mask in personas.items():
        pids = set(outer.loc[mask, "pid"])
        row = dict(persona=name, n=len(pids),
                   n_train=int(split[split.pid.isin(pids)].split.eq("train").sum()),
                   n_test=int(split[split.pid.isin(pids)].split.eq("test").sum()))
        for s in STUDIES:
            t = pd.read_parquet(PROC / f"mega_{s}.parquet")
            t = t[t.pid.isin(pids)]
            row[f"{s}_train"], row[f"{s}_test"] = int((t.split == "train").sum()), int((t.split == "test").sum())
        gg = gm[gm.pid.isin(pids)]
        for c in ["green_default", "grey_default"]:
            row[f"green_{c}_n"] = int((gg.green_condition == c).sum())
        feas.append(row)
    pd.DataFrame(feas).to_csv(AUD / "persona_feasibility.csv", index=False)

    # 7. income median band (for the 'below median' definition)
    inc = outer.income.cat.codes
    med = outer.income.cat.categories[int(np.median(inc[inc >= 0]))]
    json.dump({"split_sha256": sha256(split_path), "seed": SEED, "test_frac": TEST_FRAC,
               "n_train": int((split.split == "train").sum()), "n_test": int((split.split == "test").sum()),
               "income_median_band": str(med)}, open(AUD / "split_meta.json", "w"), indent=1)
    print("audit complete")


if __name__ == "__main__":
    main()
