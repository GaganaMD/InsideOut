"""Fixed task list (dependency-free; shared by experiments.py and the Modal entrypoint). Never expands at run time."""
SPECS = ["demographics_t07", "demographics_t0", "empty_t07", "full_persona_t07"]
STUDIES = {"default_eric": "binary", "targeting_fairness": "rating_1_9"}
SMOKE = ["A|default_eric|demographics_t07", "B|targeting_fairness|full_persona_t07", "C|targeting_fairness|cv"]


def all_tasks() -> list[str]:
    t = [f"A|{s}|{p}" for s in STUDIES for p in SPECS] + [f"B|{s}|{p}" for s in STUDIES for p in SPECS]
    return t + [f"C|{s}|cv" for s in STUDIES]
