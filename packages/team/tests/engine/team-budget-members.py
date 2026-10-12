"""Scenario `team-budget-members` -- 1 case(s) (batch la-part-calculee, 2026-10-11: row 75 of the study § 18,
team 0.29.0): without `parallel:`, k -- the wake-ups that may play together -- is the members; the parts under
`parallel:` are `team-budget-parallel`'s. The case names the invariant of `team-sim-reframe.py` it replays.
- (b) k without `parallel:` (I10r): three members, no `parallel:` -- k = 3; a1 ends at 0.2 while a2 plays, and every
  intent's part is min((1 - the cost kept) / 3, the rest)
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "a": [{"sleep": 0.1, "cost": 0, "body": {"do": ["a1", "a2"]}}, {"sleep": 0.1, "cost": 0, "body": {"done": "both"}}],
        "a1": [{"sleep": 0.2, "cost": 0.2, "body": {"done": True}}],
        "a2": [{"sleep": 2.0, "cost": 0.1, "body": {"done": True}}]})
    by_kind, all_ended, parts_held = T.by_kind, T.all_ended, T.parts_held

    # --- (b) k without parallel: -- the members, three -- I10r ---------------------------------------------
    h.declare("trio", "---\nagents: |\n  a agents/a\n  a1 agents/a1\n  a2 agents/a2\nreports: |\n  a1 a2 -> a\n"
                      "root: a\nbudget: 1\nschedule: off\n---\nThree parts.\n")
    started_b = h.call("team", "start", "trio", "--message", "review PR 12", *h.harnessed)
    done_b = h.settled("trio", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    found = h.events("trio")
    parts = [(one["agent"], one.get("allowance")) for one in by_kind(found, "wake-intent")]
    if started_b.returncode == 0 and done_b and parts[:3] == [("a", 0.333333), ("a1", 0.333333), ("a2", 0.333333)] \
            and len(parts) == 4 and parts_held(found, 1.0, 3):
        held("(b) k without parallel:", f"three members: k 3, parts {parts} -- each min((1 - cost) / 3, the rest) "
             "-- I10r")
    else:
        failures.append(f"  ✗ (b) k without parallel    rc={started_b.returncode} done={done_b} parts={parts} "
                        f"held={parts_held(found, 1.0, 3)}")
    return 0
