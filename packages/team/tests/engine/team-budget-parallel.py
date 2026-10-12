"""Scenario `team-budget-parallel` -- 1 case(s) (batch la-part-calculee, 2026-10-11: row 75 of the study § 18,
team 0.29.0): a wake-up's allowance is its PART of the team's rest -- min((budget - the cost kept) / k, the rest no
wake-up under way holds), k the wake-ups that may play together, min(`parallel`, the members); k without
`parallel:` is `team-budget-members`'s. The case names the invariant of `team-sim-reframe.py` it replays.
- (a) the members due together launch together (I10p, I10r): `budget: 1`, `parallel: 2`, three members; l delegates
  to r1 and r2 -- two intents of 0.5 each, no `deferred`, both wake-ups under way at once
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "l": [{"sleep": 0.1, "cost": 0, "body": {"do": ["r1", "r2"]}}, {"sleep": 0.1, "cost": 0, "body": {"done": "both"}}],
        "r1": [{"sleep": 1.5, "cost": 0.2, "body": {"done": True}}],
        "r2": [{"sleep": 1.5, "cost": 0.2, "body": {"done": True}}]})
    by_kind, all_ended, parts_held, peak = T.by_kind, T.all_ended, T.parts_held, T.peak

    # --- (a) the members due together launch together -- I10p, I10r ------------------------------------------
    h.declare("pair", "---\nagents: |\n  l agents/l\n  r1 agents/r1\n  r2 agents/r2\nreports: |\n  r1 r2 -> l\n"
                      "root: l\nparallel: 2\nbudget: 1\nschedule: off\n---\nShare the rest.\n")
    started = h.call("team", "start", "pair", "--message", "review PR 11", *h.harnessed)
    done = h.settled("pair", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    found = h.events("pair")
    parts = {one["agent"]: one.get("allowance") for one in by_kind(found, "wake-intent") if one["agent"] != "l"}
    if (started.returncode == 0 and done and parts == {"r1": 0.5, "r2": 0.5} and not by_kind(found, "deferred")
            and peak(found) == 2 and parts_held(found, 1.0, 2)):
        held("(a) the members due together launch together", "budget 1, parallel 2: r1 and r2 get 0.5 each, no "
             "deferred, both under way at once -- I10p, I10r")
    else:
        failures.append(f"  ✗ (a) together               rc={started.returncode} done={done} parts={parts} "
                        f"deferred={by_kind(found, 'deferred')} peak={peak(found)} held={parts_held(found, 1.0, 2)}")

    return 0
