"""Scenario `bench-support` -- 3 case(s) (batch les-scenarios-par-maison, 2026-10-07):
- le-module-de-support: a file whose name opens on `_` beside the scenarios of an area is a
  SUPPORT module (tests/README.md, rule 10): the runner never collects it as a scenario, and
  the lint has nothing to say about it
- le-chargement: `support(__file__, "<name>")` loads `_<name>.py` beside the calling scenario,
  its names usable
- le-lint: a support module that exposes `scenario(bench)` is refused by the lint, named with
  its rule -- a scenario is a kebab file, a support module plays nothing
"""
from __future__ import annotations

from tests import harness
from tests.harness import support


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    area = bench.temp() / "tests"               # a throwaway AREA: one scenario, one support module
    area.mkdir()
    (area / "_x.py").write_text("ANSWER = 42\n\n\ndef twice(n):\n    return 2 * n\n", encoding="utf-8")
    (area / "y.py").write_text("def scenario(bench):\n    return 0\n", encoding="utf-8")
    kept = harness.areas
    harness.areas = lambda: [("", area)]        # the runner reads the areas by this name alone
    try:
        names = [name for name, _ in harness.scenarios([])]
        refused = harness.lint(harness.scenarios([]))
        (area / "_bad.py").write_text("def scenario(bench):\n    return 0\n", encoding="utf-8")
        refused_bad = harness.lint(harness.scenarios([]))
    finally:
        harness.areas = kept

    # --- le-module-de-support: never collected, nothing to lint --------------------------
    if names == ["y"] and refused == []:
        held("a support module is never a scenario", "`_x.py` beside `y.py`: the runner collects "
             "`y` alone, the lint says nothing")
    else:
        failures.append(f"  ✗ support collected           names={names} refused={refused}")

    # --- le-chargement: the module beside the scenario, by name ---------------------------
    module = support(str(area / "y.py"), "x")
    if getattr(module, "ANSWER", None) == 42 and module.twice(21) == 42:
        held("support() loads the module beside the scenario", "`support(__file__, 'x')` -> `_x.py`, "
             "ANSWER 42, twice(21) 42")
    else:
        failures.append(f"  ✗ support loaded              {module!r}")

    # --- le-lint: a support module that plays is refused with its rule ---------------------
    if (len(refused_bad) == 1 and "_bad" in refused_bad[0] and "rule 10" in refused_bad[0]
            and "scenario(bench)" in refused_bad[0]):
        held("the lint refuses a support module that plays", refused_bad[0][:90])
    else:
        failures.append(f"  ✗ support that plays          {refused_bad}")
    return 0
