"""Scenario `effort-table` -- the decided light / medium / full table (plan pp-split,
batch la-distribution-des-reglages): `effective` renders three DISTINCT levels,
key by key -- the engine's four protocol keys and the fragments' own presets.
"""
from __future__ import annotations

from conductor import reading, settings

TABLE = {   # key -> (light, medium, full), the operator's table of 2026-09-05
    "verbatim_constraints": (False, False, True),
    "instructions_fusion": ("max", "max", "none"),
    "proc_body_serve": ("once", "once", "always"),
    "capture_prompt": (False, True, True),
    "continuity_memory_frequency": ("5", "3", "1"),
    "improvement_next_max": (1, 2, 3),
}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    made = bench.env("efforts", packages=("continuity", "improvement")).made
    seen = {}
    for level in ("light", "medium", "full"):
        (made / "SETTINGS.md").write_text(
            f"---\nname: SETTINGS\nkind: doc\nconduction_effort: {level}\n---\n", encoding="utf-8")
        merged = settings.effective(reading.read(made / "SETTINGS.md").front, made)
        seen[level] = {key: merged.get(key) for key in TABLE}
    wrong = [(key, level, seen[level][key], want)
             for key, wants in TABLE.items()
             for level, want in zip(("light", "medium", "full"), wants)
             if seen[level][key] != want]
    if not wrong and seen["medium"] != seen["full"] and seen["light"] != seen["medium"]:
        held("the effort table, three distinct levels", "light and medium keep the laws in codes "
             "and the body once, medium captures the prompt, full fuses nothing and says everything; "
             "continuity 5 / 3 / 1, improvement 1 / 2 / 3 -- key by key under `effective`")
    else:
        failures.append(f"  ✗ effort table                {wrong!r}")
    if "improvement_reflex" not in seen["light"] and "improvement_reflex" not in merged:
        held("no switch on the reflex", "`improvement_reflex` presets nothing and is seeded nowhere")
    else:
        failures.append("  ✗ improvement_reflex survives")
    return 0
