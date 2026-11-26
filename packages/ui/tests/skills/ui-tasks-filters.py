"""Scenario `ui-tasks-filters` -- the filters of the Tasks tab, on the bench's `pp-team` witness replaying the faces of
`team` for three declared teams -- `core-review` and `ops` started, `veille` never (`_tasks`):
- the tasks with a question or an end not seen, every task -- the teams mingled by birth --, a team alone
"""
from __future__ import annotations

from tests.harness import support

S = support(__file__, "tasks")
T, P = S.T, S.P


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-filters")

    # --- the filters -------------------------------------------------------------------------------
    every = [name for _, one in sorted(S.TASKS, key=lambda pair: pair[1]["at"], reverse=True)
             for name in S.NAMES if name in (one.get("name") or one["text"])]
    all_tasks = S.every_task()                 # the filter of every task, read from model/teams.py, never retyped
    for keys, expected, what in (("shift+tab,shift+tab,down,down", {"review PR 88", "daily 2026-10-10", "weekly report"},
                                  "for you"),
                                 ("shift+tab,shift+tab,down,down,down,down,down,down", set(S.NAMES), all_tasks),
                                 ("shift+tab,down", {"review PR 88"}, "a team alone")):
        done = house.render("--render", "tasks", "--size", "150x36", "--press", keys)
        rows = S.rows_of(done.stdout)
        found = {name for name in S.NAMES if any(name in one for one in rows)}
        ordered = what != all_tasks or (all_tasks is not None and f"show {all_tasks}" in P.status_of(done.stdout)
                                        and [name for row in rows for name in S.NAMES if name in row] == every)
        if done.returncode == 0 and found == expected and len(rows) == len(expected) and ordered:
            held(f"the filter {what}", f"--press {keys}: {sorted(found)}")
        else:
            failures.append(f"  ✗ filter {what!s:<20} rc={done.returncode} {sorted(found)} {rows} "
                            f"{done.stdout[-1500:]!r} {done.stderr[-300:]!r}")
    return 0
