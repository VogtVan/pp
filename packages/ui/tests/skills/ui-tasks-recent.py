"""Scenario `ui-tasks-recent` -- the filter `recent` of the Tasks tab, on the bench's `pp-team` witness replaying the
faces of `team` for three declared teams -- `core-review` and `ops` started, `veille` never (`_tasks`):
- on faces dated at the reading: an open task of three days stays, a task resolved two days ago leaves, one resolved
  ten hours ago stays
"""
from __future__ import annotations

from tests.harness import support

S = support(__file__, "tasks")
T, P = S.T, S.P


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-recent")

    # --- recent: the open tasks, and those ended within the day ------------------------------------------
    day = 86400
    core = {**T.CORE, "tasks": [{**one, **dated} for one, dated in zip(T.CORE["tasks"], (
        {"at": T.ago(3 * day + 60), "ended": T.ago(3 * day)},              # T1 stopped three days ago
        {"at": T.ago(2 * day + 3600), "ended": T.ago(2 * day)},            # T2 resolved two days ago
        {"at": T.ago(3 * day), "ended": None}))]}                         # T3 open for three days
    ops = {**T.OPS, "tasks": [{**T.OPS["tasks"][0], "at": T.ago(3600), "ended": None},
                              {**T.OPS["tasks"][1], "at": T.ago(11 * 3600), "ended": T.ago(11 * 3600 - 62 * 60)}]}
    house.use(T.script(states={"core-review": [core], "ops": [ops]}))
    done = house.render("--render", "tasks", "--size", "150x36")
    rows = [name for row in S.rows_of(done.stdout) for name in S.NAMES if name in row]
    kept = ["rotate the certificates", "weekly report", "review PR 88"]
    if done.returncode == 0 and rows == kept:
        held("recent keeps the open tasks and those ended within the day", f"{rows}: T3 open for three days, ops' T2 "
             "resolved ten hours ago; T2 resolved two days ago and T1 stopped three days ago left out")
    else:
        failures.append(f"  ✗ recent                      rc={done.returncode} {rows} {done.stdout[-1500:]!r} "
                        f"{done.stderr[-300:]!r}")
    return 0
