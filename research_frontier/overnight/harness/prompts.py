"""Fixed, versioned prompt templates. Any wording change changes TEMPLATE_HASH and therefore the cache key."""
import hashlib
import json

SYSTEM = ("You simulate how a person with the described characteristics would answer a survey question. "
          "Answer as that person would, not as an expert. Respond with JSON only.")

# Information arms (pre-analysis plan): what the model is allowed to see beyond the scenario.
ARMS = {
    "empty": [],                                   # scenario only
    "tierA": ["tier_a"],                           # census-observable demographics only
    "tierA_condition_blind": ["tier_a"],           # demographics, neutral scenario without the default manipulation
    "disposition": ["tier_a", "disposition"],      # demographics + binned measured disposition (e.g. green values)
    # 2026-11-15 green_profiles experiment: a pre-rendered AGGREGATE block (no individual data), shown verbatim
    "tierA_profile": ["tier_a", "text_block"],     # demographics + statistically estimated profile (numbers)
    "narrative": ["text_block"],                   # the same numbers inside a narrative persona (demographics in prose)
}

USER_TEMPLATE = """{profile_block}Scenario:
{scenario}

Question: {question}
Options:
{options}

Reply with exactly this JSON and nothing else: {{"choice": "<one of {option_keys}>", "p": <your probability, 0-1, that this person picks option {focal}>}}"""


def profile_block(profile: dict, fields: list[str]) -> str:
    lines = []
    if "tier_a" in fields:
        for k, v in profile.get("tier_a", {}).items():
            lines.append(f"- {k}: {v}")
    if "disposition" in fields and profile.get("disposition"):
        for k, v in profile["disposition"].items():
            lines.append(f"- {k}: {v}")
    parts = ["Person:\n" + "\n".join(lines)] if lines else []
    if "text_block" in fields and profile.get("text_block"):
        parts.append(profile["text_block"])
    return ("\n\n".join(parts) + "\n\n") if parts else ""


def render(arm: str, profile: dict, item: dict) -> list[dict]:
    if arm not in ARMS:
        raise ValueError(f"unknown arm {arm}")
    scen = item["scenario_neutral"] if arm == "tierA_condition_blind" else item["scenario"]
    opts = "\n".join(f"{k}: {v}" for k, v in item["options"].items())
    user = USER_TEMPLATE.format(profile_block=profile_block(profile, ARMS[arm]), scenario=scen, question=item["question"],
                                options=opts, option_keys=" | ".join(item["options"]), focal=item["focal"])
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


TEMPLATE_HASH = hashlib.sha256(json.dumps([SYSTEM, USER_TEMPLATE, ARMS], sort_keys=True).encode()).hexdigest()[:16]
