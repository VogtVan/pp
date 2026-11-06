"""Scenario `ui-tasks-recurrence-plan` -- `p` in the overlay `e` of the Tasks tab makes a task given once come back
(batch les-gestes-de-la-recurrence), on the bench's `pp-team` witness: `core-review` carries T1 and T3 given once, T2
opened by the meeting `daily`, T6 by the recurrence `R1`:
- the task is chosen among those no recurrence and no meeting opened (`T1`, `T3`; not `T2`, `T6`), its period typed --
  `team recurrence core-review --task T3 --every 'day 08:00'`, played as the witness's journal says it, no command on
  screen --; a refusal of `team` on the remedy line
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")

SIZE = ("--size", "150x45")
LIMITED = T.RECURRING
PLANNED = "team recurrence core-review --task T3 --every 'day 08:00'"
PLAN = ",".join({" ": "space", ":": "colon"}.get(one, one) for one in "day 08:00")
RECURRENT = "pp-team: task-recurrent -- T3 was opened by a recurrence"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-recurrence-plan", T.script(states={"core-review": [LIMITED], "ops": [T.OPS]}))

    # --- p: a task given once made to come back ------------------------------------------------------------------------
    keys = f"e,p,space,down,enter,tab,{PLAN}"
    shown = house.render("--render", "tasks", *SIZE, "--press", "e,p,space")
    offered = [one for one in ("T1", "T2", "T3", "T6") if f" {one}" in P.on_top(shown.stdout)]
    house.clear_journal()
    done = house.render("--render", "tasks", *SIZE, "--press", keys + ",enter")
    played = house.gestures()
    house.use(T.script(states={"core-review": [LIMITED], "ops": [T.OPS]},
                       answers={"recurrence": {"rc": 2, "err": RECURRENT + "\n"}}))
    refused = house.render("--render", "tasks", *SIZE, "--press", keys + ",enter")
    if (shown.returncode == done.returncode == refused.returncode == 0 and "./pp" not in shown.stdout
            and offered == ["T1", "T3"] and played == [PLANNED] and T.remedy_of(refused).startswith(RECURRENT[:30])):
        held("p makes a task given once come back", f"offered {offered}; {played[0]}; refused: {T.remedy_of(refused)[:50]!r}")
    else:
        failures.append(f"  ✗ plan                        rc={shown.returncode},{done.returncode} "
                        f"{offered} {played} {T.remedy_of(refused)!r} {done.stdout[-1500:]!r}")
    return 0
