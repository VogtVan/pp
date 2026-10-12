"""Scenario `team-resume-budget` -- 1 case(s) (batch le-budget-de-l-equipe, 2026-10-11: row 76 of the study
§ 18, team 0.22.0): `team resume` judges the team's budget BEFORE whether the task is blocked, and names its
remedy; the resumes of a blocked task are `team-resume-blocked`'s. The case names the invariant of
`team-sim-reframe.py` it replays.
- (d) a task the budget alone holds (I10): under `budget-wakes: 1` only, the reply finds the bound spent;
  `team resume` refuses `budget-spent` -- never `task-not-blocked` -- and names `team budget`
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "k": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which day?"}}},
              {"sleep": 0.1, "body": {"done": "never"}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    # --- (d) a task the budget alone holds: resume says budget-spent and its remedy -- I10 ---------------
    h.declare("held", "---\nagents: |\n  k agents/k\nroot: k\nbudget-wakes: 1\nschedule: off\n---\nOne wake-up.\n")
    started_k = h.call("team", "start", "held", "--message", "cut the branch", *h.harnessed)
    asked_k = h.settled("held", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), 60)
    ask_k = next((one["id"] for one in by_kind(h.events("held"), "post", verb="ask")), -1)
    replied_k = h.call("team", "post", "held", "--task", "T1", "--reply", str(ask_k), "--message", "monday")
    spent_k = by_kind(h.events("held"), "budget-spent")
    before_k = h.journal_of("held").read_bytes()
    refused_k = h.call("team", "resume", "held", "--task", "T1")
    if (started_k.returncode == 0 and asked_k and replied_k.returncode == 0 and spent_k and refused_k.returncode == 2
            and "budget-spent" in refused_k.stderr and "task-not-blocked" not in refused_k.stderr
            and "team budget" in refused_k.stderr and h.journal_of("held").read_bytes() == before_k):
        held("(d) a task the budget alone holds", "budget-wakes 1 spent at the reply: team resume refuses "
             "budget-spent, never task-not-blocked, and names team budget -- I10")
    else:
        failures.append(f"  ✗ (d) the budget alone holds rc={started_k.returncode}/{replied_k.returncode}/"
                        f"{refused_k.returncode} asked={asked_k} spent={spent_k} {refused_k.stderr.strip()[-220:]!r}")
    return 0
