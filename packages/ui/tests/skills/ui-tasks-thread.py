"""Scenario `ui-tasks-thread` -- the thread of a task draws before its history returns (batch la-sequence-vivante), on
the bench's `pp-team` witness whose `log` tarries two seconds:
- the band draws what the watch said of the task before `team log` returned: a post #46 relayed at 0.5 s is a row of the
  sequence before the history (the render's word `rows`), and the whole thread once it returned
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    script = T.script(log={"core-review": T.TEAM_LOG, "core-review/T3": [{"sleep": 2.0}] + T.T3_LOG,
                           "core-review/T2": T.T2_LOG},
                      watch={"core-review": [{"sleep": 0.5}, T.WRITTEN, {"sleep": 0.2}, T.STEP]})
    house = T.Teams(bench, "ui-tasks-thread", script)
    done = house.render("--render", "tasks", "--size", "150x40", "--press", "wait:team:post,rows")
    noted = next((one[5:] for one in reversed(done.stdout.split("\n")) if one.startswith("rows ")), "")
    ids = [one["id"] for one in T.T3_LOG if one["event"] == "post"] + [T.WRITTEN["id"]]
    if (done.returncode == 0 and noted == "1" and all(f"#{one} " in done.stdout for one in ids)):
        held("the thread draws before the log returns", f"{noted} row drawn before the history, {len(ids)} after it")
    else:
        failures.append(f"  ✗ before the log              rc={done.returncode} rows={noted!r} "
                        f"{done.stdout[-1500:]!r} {done.stderr[-300:]!r}")
    return 0
