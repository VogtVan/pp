"""Scenario `ui-tasks-launched` -- the task launched from the Tasks tab, on the bench's `pp-team` witness replaying the
faces of `team` for three declared teams -- `core-review` and `ops` started, `veille` never (`_tasks`):
- `n` played under `resolved`, the new task -- the id the face did not say before -- under the cursor, the filter
  turned to `recent` on the status line; the task resolved by the team, the cursor still on it
"""
from __future__ import annotations

import re

from tests.harness import support

S = support(__file__, "tasks")
T, P = S.T, S.P


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-launched")

    # --- the task launched follows ---------------------------------------------------------------------------
    born = {**T.T4, "at": T.ago(30), "ended": None}
    after = {**T.CORE, "tasks": T.CORE["tasks"] + [born]}
    resolved = {**T.CORE, "tasks": T.CORE["tasks"] + [{**born, "state": "resolved", "holders": [], "ended": T.ago(5)}]}
    house.use(T.script(states={"core-review": [T.CORE, after, resolved], "ops": [T.OPS]},
                       watch={"core-review": [{"sleep": 5.0}, T.event("09:14:00", "done", 49, task="T4")]}))
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "150x40", "--press",
                        "shift+tab,shift+tab,down,down,down,down,n,g,o,ctrl+enter", "--wait", "team:done")
    lines = [one.strip() for one in T.sides_of(done.stdout)[1] if one.strip()]
    first = next((one for one in lines if re.match(r"T\d\s", one)), "")
    band = next((one for one in lines if one.startswith(f"T4{P.palette_constant('SEP')}")), "")
    status = P.status_of(done.stdout)
    if (done.returncode == 0 and house.gestures() == [S.NEW] and first.startswith("T4")
            and "resolved" in band and "show recent" in status):
        held("the task launched follows", f"{S.NEW!r} under resolved: T4 first and under the cursor, "
             f"{band[:30]!r} once the team resolved it; the status says {status.split(' · ')[1:3]}")
    else:
        failures.append(f"  ✗ launched follows            rc={done.returncode} {house.gestures()} {first!r} {band!r} "
                        f"{status!r} {done.stdout[-1800:]!r} {done.stderr[-400:]!r}")
    house.use(T.script())
    return 0
