"""Scenario `bench-lines` -- 3 case(s):
- l-etiquette-du-banc: a label past the column keeps a gap before its detail
- le-rapport-par-defaut: the report counts out loud and details on demand
- le-rapport-des-passes: a count that moves between passes is a red of its own
- le-run-du-moment: several runs standing, the bench means the freshest
- les-cibles-de-temps: the targets say, they never redden, and the list stays readable
"""
from __future__ import annotations

import contextlib
import io

import json
import time

from tests.harness import Bench, bench_key, report, report_repeat


def _spoken(results: list[dict], detail: bool = False) -> tuple[str, int]:
    """-> what the report prints for these results, and its exit code."""
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        code = report(results, 0.9, detail=detail)
    return said.getvalue(), code


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # the witness (S4.09, 2026-08-26): `hour once\`2} ...` -- a long label glued to its detail
    probe = Bench()
    spoken = io.StringIO()
    with contextlib.redirect_stdout(spoken):
        probe.held("x" * 40, "detail")
        probe.held("short", "detail")
    lines = spoken.getvalue().splitlines()
    if (len(lines) == 2 and lines[0].endswith("x detail")
            and lines[1] == f"  ✓ {'short':<32}detail"):
        held("a long label keeps its gap",
             "the column holds for a short label; a longer one is followed by one space")
    else:
        failures.append(f"  ✗ bench line                  {lines!r}")

    # --- le-rapport-par-defaut: the report counts out loud and details on demand ------
    made = [{"name": "area/chatty", "out": "  ✓ a green one holds\n", "held": 1,
             "refusals": 0, "failures": [], "seconds": 0.1},
            {"name": "area/quiet", "out": "", "held": 2, "refusals": 1,
             "failures": [], "seconds": 0.2},
            {"name": "area/red", "out": "  ✓ the last one before the fall\n", "held": 1,
             "refusals": 0, "failures": ["  ✗ area/red                     boom"],
             "seconds": 0.3}]
    plain, plain_code = _spoken(made)
    detailed, detailed_code = _spoken(made, detail=True)
    counted = [line for line in plain.splitlines() if " held " in line]
    if (plain_code == 1 and detailed_code == 1
            and "a green one holds" not in plain          # a quiet green keeps its detail
            and "the last one before the fall" in plain   # a failing one always speaks
            and "a green one holds" in detailed
            and counted == [line for line in detailed.splitlines() if " held " in line]
            and "boom" in plain and "1 failure(s)" in plain):
        held("the table counts, the detail waits", "a green scenario's lines wait for the "
             "flag; a failing one renders them with its ✗, and the table is the same either way")
    else:
        failures.append(f"  ✗ the report's default        {counted!r}")

    # --- le-rapport-des-passes: a count that moves between passes is a red ----------
    def pass_of(held_steady: int) -> list[dict]:
        return [{"name": "area/steady", "out": "", "held": 4, "refusals": 0,
                 "failures": [], "seconds": 0.1},
                {"name": "area/moving", "out": "", "held": held_steady, "refusals": 0,
                 "failures": [], "seconds": 0.1}]

    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        shaken = report_repeat([pass_of(3), pass_of(2)], 1.0)
    unmoved = io.StringIO()
    with contextlib.redirect_stdout(unmoved):
        steady = report_repeat([pass_of(3), pass_of(3)], 1.0)
    shaken_said, steady_said = said.getvalue(), unmoved.getvalue()
    if (shaken == 1 and steady == 0 and "area/moving" in shaken_said
            and "3 held / 2 held" in shaken_said and "area/steady" not in shaken_said
            and "1 scenario(s) moved" in shaken_said and "steady." in steady_said):
        held("a count that moves is a red", "two passes of one selection: the scenario "
             "whose count changed is named with what it held pass by pass, the steady one "
             "is not -- and two identical passes say the bench is steady")
    else:
        failures.append(f"  ✗ the passes compared         {shaken}/{steady} "
                        f"{shaken_said.splitlines()[-3:]!r}")

    if "`-detail`" in plain and "1 scenario(s)" in plain and "`-detail`" not in detailed:
        held("the silence says itself", "one line names how many scenarios keep their "
             "detail and the flag that renders it -- under the flag there is nothing to say")
    else:
        failures.append(f"  ✗ the silence is announced    {plain.splitlines()[-4:]!r}")
    # --- le-run-du-moment: several runs standing, the bench means the freshest --------
    env = bench.env("many")
    state = env.made / ".sys" / "state"
    state.mkdir(parents=True, exist_ok=True)
    for name, log in (("aaaaaa", "session-a.jsonl"), ("ffffff", "session-f.jsonl")):
        (state / f"session-{name}.json").write_text(json.dumps({"log": log}), encoding="utf-8")
        time.sleep(0.01)                     # the slots are written one after the other
    meant = bench_key(env.made)
    again = bench_key(env.made)
    if meant == "ffffff" == again:
        held("several runs standing, the freshest is meant", "two slots side by side: the "
             "bench names the one written last, twice in a row -- an instance carries one "
             "run per conversation, and a fixture says which it means")
    else:
        failures.append(f"  ✗ the run meant               {meant!r} then {again!r}")
    # --- les-cibles-de-temps: the targets say, and the list stays readable ------------
    slow = [{"name": f"area/slow-{i}", "out": "", "held": 1, "refusals": 0,
             "failures": [], "seconds": 30.0} for i in range(12)]
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        verdict = report(slow, 50.0)
    lines = said.getvalue().splitlines()
    warned = [line for line in lines if "took" in line and "target" in line]
    rest = [line for line in lines if "more over the" in line]
    walled = [line for line in lines if "the wall took" in line]
    if (verdict == 0 and len(warned) == 5 and len(rest) == 1 and "7" in rest[0]
            and not walled and "green." in said.getvalue()):
        held("the targets say, they never redden", "twelve scenarios over the target render "
             "five lines and one for the seven others; a wall under its own target says "
             "nothing, and the verdict is green -- a target is a word, never a failure")
    else:
        failures.append(f"  ✗ the time targets            rc={verdict} warned={len(warned)} "
                        f"rest={rest!r} wall={len(walled)}")
    return 0
