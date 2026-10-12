"""Scenario `capture-prompt-presets` -- 1 case(s) (batch la-base-temoin-du-banc, 2026-10-06;
the kit's row of the effort table, moved from `tests/engine/state/effort-table.py`):
- `capture_prompt`, the kit's bare key, presets light=false, medium=true, full=true under
  `effective` -- the mechanism is the engine's, the values the kit's
"""
from __future__ import annotations

from conductor import reading, settings

PRESETS = {"light": False, "medium": True, "full": True}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    made = bench.env("efforts").made
    seen = {}
    for level in PRESETS:
        (made / "SETTINGS.md").write_text(
            f"---\nname: SETTINGS\nkind: doc\nconduction_effort: {level}\n---\n", encoding="utf-8")
        merged = settings.effective(reading.read(made / "SETTINGS.md").front, made)
        seen[level] = merged.get("capture_prompt")
    if seen == PRESETS:
        held("the kit presets capture_prompt by effort", "light leaves the prompt alone, "
             "medium and full capture it -- the kit's fragment, read under `effective`")
    else:
        failures.append(f"  ✗ capture_prompt presets      {seen!r}")
    return 0
