"""Scenario `model-layers` -- 1 case(s), in the monolith's order:
- the model crosses every layer because it depends on none of them
"""
from __future__ import annotations

import ast
from conductor import reading
from tests.harness import ENGINE


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- the model crosses every layer because it depends on none of them -------------
    tree = ast.parse((ENGINE / "conductor" / "core" / "model.py").read_text(encoding="utf-8"))
    inner = [n for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and (n.level or 0) > 0]
    if not inner:
        held("model.py depends on nothing", "the data objects cross every layer")
    else:
        failures.append(f"  ✗ model.py imports          {[n.module for n in inner]}")

    front = reading.front_matter(["description: >-", "  one", "  two", "proc: |", "  PICK x"])
    if front["description"] == "one two" and front["proc"] == "PICK x":
        held("block scalars", "`>` folds into prose, `|` keeps the procedure's lines")
    else:
        failures.append(f"  ✗ block scalars             {front}")
    return 0
