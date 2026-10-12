"""Scenario `ui-real-team-budget` -- the budget of a team raised at the post, on the REAL verbs of `team` (plan ui,
batch le-reel-du-centre), its wake-ups played by the team witness, never a provider: `essai` under `budget: 3`,
started -- `B` raises the budget to 5 by the real `team budget`: `budget-raised` at the journal, `status --json`
says the cap 5 (the inbox is `ui-real-team-inbox`'s, the declaration `ui-real-team-declaration`'s)
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real_team")
ERASE = ",".join(["backspace"] * 4)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    team = R.RealTeam(bench, "ui-real-team-budget", {"lead": [{"body": {"done": "started"}}]}, R.BUDGETED)
    begun = team.start("go")
    started = team.settled(lambda events: any(one.get("kind") == "done" and one.get("task") == "T1" for one in events))

    raised = team.render("--render", "teams", "--size", "200x50", "--press", f"B,{ERASE},5,enter")
    events = team.kinds("budget-raised")
    cap = (team.state().get("budget") or {}).get("cap")
    if (begun.returncode == 0 and started and raised.returncode == 0 and len(events) == 1 and events[0].get("budget") == 5
            and cap == 5 and not team.alive()):
        held("B raises the budget on the real verb", f"budget-raised #{events[0].get('id')} budget 5; status --json cap {cap}")
    else:
        failures.append(f"  ✗ budget                      started={started} events={events} cap={cap} alive={team.alive()} "
                        f"{raised.stdout[-1200:]!r} {raised.stderr[-300:]!r}")
    return 0
