"""Download the subset of the official Twin-2K-500 and Mega-Study files this project uses.

Sources (dataset cards):
  https://huggingface.co/datasets/LLM-Digital-Twin/Twin-2K-500
  https://huggingface.co/datasets/LLM-Digital-Twin/Twin-2K-500-Mega-Study
Files land in data/raw/<repo-name>/<repo-relative path>. Per-file download with
retries, because the Hub connection here drops intermittently. Existing files are skipped.
"""
import sys
import time
from pathlib import Path

from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

# Pinned commits (recorded on first successful download; see audit/sources.json).
REVISIONS = {
    "Twin-2K-500": None,
    "Twin-2K-500-Mega-Study": None,
}

TWIN_FILES = [
    "README.md",
    "question_catalog_and_human_response_csv/question_catalog.json",
    "question_catalog_and_human_response_csv/question_catalog_README.md",
    "question_catalog_and_human_response_csv/wave1_3_response.csv",
    "question_catalog_and_human_response_csv/wave1_3_response_label.csv",
    "question_catalog_and_human_response_csv/wave4_response.csv",
    "question_catalog_and_human_response_csv/wave4_response_label.csv",
    "raw_data/wave 1 scores.csv",
    "raw_data/wave 2 scores.csv",
    "raw_data/wave 3 scores.csv",
    "raw_data/wave_1_labels_anonymized.csv",
    "raw_data/wave_1_numbers_anonymized.csv",
]
STUDIES = ["default_eric", "preference_redistribution", "context_effects"]
MEGA_FILES = ["README.md"] + [
    f for s in STUDIES for f in (
        f".dat/{s}/raw_data/response.csv",
        f".dat/{s}/raw_data/survey.qsf",
        f"data/{s}-00000-of-00001.parquet",
    )
]


def fetch(repo: str, filename: str, tries: int = 8) -> None:
    target = RAW / repo / filename
    if target.exists() and target.stat().st_size > 0:
        return
    for i in range(tries):
        try:
            hf_hub_download(f"LLM-Digital-Twin/{repo}", filename, repo_type="dataset",
                            revision=REVISIONS[repo], local_dir=RAW / repo)
            print("ok  ", repo, filename)
            return
        except Exception as e:  # network resets: back off and retry
            print(f"retry {i + 1}/{tries} {filename}: {type(e).__name__}", file=sys.stderr)
            time.sleep(2 + 2 * i)
    raise SystemExit(f"FAILED to download {repo}/{filename}")


def main() -> None:
    for f in TWIN_FILES:
        fetch("Twin-2K-500", f)
    for f in MEGA_FILES:
        fetch("Twin-2K-500-Mega-Study", f)


if __name__ == "__main__":
    main()
