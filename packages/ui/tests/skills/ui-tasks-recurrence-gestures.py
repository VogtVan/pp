"""Scenario `ui-tasks-recurrence-gestures` -- the gestures on a recurrence of a team (batch la-recurrence-au-poste),
in the overlay `e` opens on the Tasks tab, on the bench's `pp-team` witness: `core-review` carries `recurrences` (`R1`
live, `R2` stopped):
- `x` stops the line under the cursor once its id is typed -- `team stop core-review --recurrence R1`, shown first --;
  without the id typed nothing plays
- `m` opens its period, selected, and plays `team recurrence core-review R1 --every 'weekday 10:00'` as shown; a
  `team` that refuses the verb says its refusal on the remedy line
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")

SIZE = ("--size", "150x45")
STOP = "team stop core-review --recurrence R1"
CHANGED = "team recurrence core-review R1 --every 'weekday 10:00'"
CHANGE = ",".join({" ": "space", ":": "colon"}.get(one, one) for one in "weekday 10:00")
REFUSED = "pp-team: usage: pp-team start <name> ... | stop <name> [--task <id>] [--kill] [--no-tick]"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-recurrence-gestures", T.script(states={"core-review": [T.RECURRING], "ops": [T.OPS]}))

    # --- x: the stop on the id typed ---------------------------------------------------------------------------------
    house.clear_journal()
    shown = house.render("--render", "tasks", *SIZE, "--press", "e,x")
    preview = T.preview_in(shown, "./pp team stop")
    untyped = house.render("--render", "tasks", *SIZE, "--press", "e,x,enter")
    nothing = house.gestures()
    done = house.render("--render", "tasks", *SIZE, "--press", "e,x,R,1,enter")
    if (shown.returncode == 0 and preview == f"./pp {STOP}" and untyped.returncode == 0 and nothing == []
            and done.returncode == 0 and house.gestures() == [STOP]):
        held("x stops a recurrence once its id is typed", f"{preview}; untyped: nothing played")
    else:
        failures.append(f"  ✗ stop                        rc={shown.returncode},{done.returncode} {preview!r} {nothing} "
                        f"{house.gestures()} {shown.stdout[-1200:]!r}")

    # --- m: the period changed; a team that does not know the verb ---------------------------------------------------
    keys = f"e,m,{CHANGE}"            # the field opens on its period, selected: what is typed replaces it
    shown = house.render("--render", "tasks", *SIZE, "--press", keys)
    preview = T.overlay_preview(shown, "./pp team recurrence")
    house.clear_journal()
    done = house.render("--render", "tasks", *SIZE, "--press", keys + ",enter")
    played = house.gestures()
    house.use(T.script(states={"core-review": [T.RECURRING], "ops": [T.OPS]},
                       answers={"recurrence": {"rc": 2, "err": REFUSED + "\n"}}))
    refused = house.render("--render", "tasks", *SIZE, "--press", keys + ",enter")
    remedy = T.remedy_of(refused)
    if (shown.returncode == 0 and preview == f"./pp {CHANGED}" and done.returncode == 0 and played == [CHANGED]
            and refused.returncode == 0 and remedy.startswith(REFUSED[:40])):
        held("m changes the period; a refusal said", f"{preview}; refused: {remedy[:60]!r}")
    else:
        failures.append(f"  ✗ change                      rc={shown.returncode},{done.returncode},{refused.returncode} "
                        f"{preview!r} {played} {remedy!r} {shown.stdout[-1500:]!r}")
    return 0
