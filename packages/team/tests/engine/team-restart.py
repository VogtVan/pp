"""Scenario `team-restart` -- 1 case(s) (batch l-equipe-au-reel, 2026-10-02; split out of
`team-review` by les-scenarios-par-maison, 2026-10-07): a team started again.
- `budget-wakes` counts from the start: two wake-ups on a first task, a second start under
  `budget-wakes: 2` still plays its own
"""
from __future__ import annotations

import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "uw": [{"sleep": 0.1, "body": "prose"},
               {"sleep": 0.1, "body": {"done": "first"}},
               {"sleep": 0.1, "body": {"done": "second"}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    # --- budget-wakes counts from the start --------------------------------------------------------
    h.declare("restart", "---\nagents: |\n  uw uw\nroot: uw\nbudget-wakes: 2\n---\nStart twice.\n")
    first_w = h.call("team", "start", "restart", "--message", "first", *h.harnessed)
    done_w1 = h.settled("restart", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=60)
    second_w = h.call("team", "start", "restart", "--message", "second", *h.harnessed)
    done_w2 = h.settled("restart", lambda found: bool(by_kind(found, "done", task="T2")) and all_ended(found), timeout=30)
    found_w = h.events("restart")
    starts = by_kind(found_w, "team-started")
    after_second = [one for one in by_kind(found_w, "wake-intent") if starts and one["id"] > starts[-1]["id"]]
    if (first_w.returncode == 0 and second_w.returncode == 0 and done_w1 and done_w2
            and len(after_second) == 1 and not by_kind(found_w, "budget-spent")):
        held("budget-wakes counts from the start", "two wake-ups on T1, then a second start under "
             "budget-wakes 2 plays its own: done T2, no budget-spent")
    else:
        failures.append(f"  ✗ wakes since start           {first_w.returncode}/{second_w.returncode} "
                        f"done={done_w1}/{done_w2} after={len(after_second)} "
                        f"spent={by_kind(found_w, 'budget-spent')}")

    return 0
