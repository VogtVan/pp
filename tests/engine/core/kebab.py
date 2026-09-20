"""Scenario `kebab` -- 1 case(s), in the monolith's order:
- kebab(): lowercase, runs of anything else become one dash, trimmed at the edges -
"""
from __future__ import annotations

from conductor import instance


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- kebab(): lowercase, runs of anything else become one dash, trimmed at the edges -
    if (instance.kebab("My Workspace") == "my-workspace"
            and instance.kebab("sw7_hub--infra!!") == "sw7-hub-infra"
            and instance.kebab("--Edges--") == "edges"):
        held("kebab() normalizes", "lowercase, one dash per run, no leading/trailing dash")
    else:
        failures.append("  ✗ kebab()")
    return 0
