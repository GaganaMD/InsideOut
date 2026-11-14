"""Shared loaders: outer layer, constructs (with ST-TW re-scored), split, green-energy outcomes."""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data/processed"
RAW_TWIN = ROOT / "data/raw/Twin-2K-500"
RESULTS = ROOT / "results"
SEED = 20261114

TIER_A = ["region", "sex", "age_band", "education", "race", "citizen", "marital", "income", "hh_size", "employment"]
TIER_B = ["party"]

CONSTRUCTS = {
    # name: (source column, label, range)
    "green": ("w1_score_GREEN", "Green values (1-5)", (1, 5)),
    "social_desirability": ("w2_score_socialdesirability", "Social desirability (0-13)", (0, 13)),
    "spendthrift": ("st_tw_rescored", "Tightwad(4)-spendthrift(26)", (4, 26)),
    "crt": ("w1_crt2_score", "Cognitive reflection (0-4)", (0, 4)),
    "dictator_give": ("w3_score_dictator_sender", "Dictator giving, % of $5 (hypothetical)", (0, 100)),
    "neuroticism": ("w1_score_neuroticism", "Neuroticism (1-5)", (1, 5)),
}


def rescore_st_tw() -> pd.DataFrame:
    """Tightwad-spendthrift (Rick et al. 2008): Q31 (1-11) + Q32 (1-5) + (6-Q33) + (6-Q34); high = spendthrift.

    The shipped `score_ST-TW` scores QID31 answers 6 and 11 (options whose labels carry text) as 0.
    """
    r = pd.read_csv(RAW_TWIN / "question_catalog_and_human_response_csv/wave1_3_response.csv",
                    usecols=["pid", "QID31", "QID32", "QID33", "QID34"])
    r["st_tw_rescored"] = r.QID31 + r.QID32 + (6 - r.QID33) + (6 - r.QID34)
    return r[["pid", "st_tw_rescored"]]


SD_TRUE_KEYED = [5, 7, 9, 10, 13]          # Reynolds (1982) Form C: socially desirable answer = TRUE
SD_FALSE_KEYED = [1, 2, 3, 4, 6, 8, 11, 12]  # socially desirable answer = FALSE


def rescore_sd_crt() -> pd.DataFrame:
    """Item-level re-scoring of social desirability and CRT-2 from the cleaned catalog CSV (final audit).

    The shipped scores are reproduced exactly by case-/format-sensitive string matching on the raw exports:
      social desirability counts only 'TRUE'/'FALSE', so 178 people whose export reads 'True'/'False' are mis-scored;
      CRT-2 accepts only 'Emily' and the strings '0', '2', '8', so 'emily' or '8.0' answers are marked wrong.
    Here: SD = Form C keying, case-insensitive; CRT-2 = name equals 'emily' (case-insensitive, trailing '.' removed)
    plus numeric answers 0 / 2 / 8.
    """
    lab = pd.read_csv(RAW_TWIN / "question_catalog_and_human_response_csv/wave1_3_response_label.csv",
                      usecols=["pid", *[f"QID27_{i}" for i in range(1, 14)],
                               "QID52_TEXT", "QID53_TEXT", "QID54_TEXT", "QID55_TEXT"])
    true = {i: lab[f"QID27_{i}"].astype(str).str.strip().str.upper().eq("TRUE") for i in range(1, 14)}
    sd = sum(true[i].astype(int) for i in SD_TRUE_KEYED) + sum((~true[i]).astype(int) for i in SD_FALSE_KEYED)
    num = lambda c: pd.to_numeric(lab[c], errors="coerce")
    name = lab.QID52_TEXT.astype(str).str.strip().str.lower().str.rstrip(".")
    crt = (name == "emily").astype(int) + (num("QID53_TEXT") == 0).astype(int) \
        + (num("QID54_TEXT") == 2).astype(int) + (num("QID55_TEXT") == 8).astype(int)
    return pd.DataFrame({"pid": lab.pid, "sd_rescored": sd.astype(float), "crt_rescored": crt.astype(float)})


def load_people(corrected: bool = False) -> pd.DataFrame:
    """One row per participant: pid, split, Tier A/B outer layer (categoricals), 6 constructs.

    corrected=False (default) reproduces every original, frozen result (shipped SD and CRT scores).
    corrected=True replaces social desirability and CRT with item-level re-scores (final audit; see rescore_sd_crt).
    """
    outer = pd.read_parquet(PROC / "outer.parquet")
    scores = pd.read_parquet(PROC / "scores.parquet").merge(rescore_st_tw(), on="pid")
    split = pd.read_csv(ROOT / "data/split.csv")
    df = outer[["pid", *TIER_A, *TIER_B]].merge(split, on="pid")
    cons = scores[["pid"]].copy()
    for name, (col, _, _) in CONSTRUCTS.items():
        cons[name] = pd.to_numeric(scores[col], errors="raise").astype(float)
    if corrected:
        rs = cons[["pid"]].merge(rescore_sd_crt(), on="pid", how="left")
        assert rs.sd_rescored.notna().all() and rs.crt_rescored.notna().all()
        cons["social_desirability"], cons["crt"] = rs.sd_rescored.to_numpy(), rs.crt_rescored.to_numpy()
    df = df.merge(cons, on="pid")
    assert len(df) == 2058 and df.pid.is_unique
    return df


def load_green(corrected: bool = False) -> pd.DataFrame:
    """default_eric green-energy item joined to people. chose_green: 1 = chose $39 renewable."""
    g = pd.read_parquet(PROC / "mega_default_eric.parquet")[["pid", "green_condition", "chose_green"]]
    g = g[g.green_condition.isin(["green_default", "grey_default"])].copy()
    g["pid"] = g.pid.astype(int)
    g["chose_green"] = g.chose_green.astype(float).astype(int)
    g["green_default"] = (g.green_condition == "green_default").astype(int)
    return g.merge(load_people(corrected), on="pid", how="inner")


def low_income(s: pd.Series) -> pd.Series:
    return s.isin(["Less than $30,000", "$30,000-$50,000"])


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    den = 1 + z ** 2 / n
    c = (p + z ** 2 / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / den
    return (c - h, c + h)
