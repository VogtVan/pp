"""Scenario `ui-tasks-recurrence-gestures` -- the gestures on the recurrences of a team (batches la-recurrence-au-poste,
les-gestes-de-la-recurrence), in the overlay `e` opens on the Tasks tab, on the bench's `pp-team` witness: `core-review`
carries `recurrences` (`R1` live with a context limit of 50, `R2` stopped, `R4` every 4 hours); what a gesture plays
is read from the witness's journal, never on screen:
- a recurrence by a duration says its period as team writes it, `4h`
- `x` stops the line under the cursor once its id is typed -- `team stop core-review --recurrence R1` --; without the
  id typed nothing plays
- `m` opens its period, its text and its limit, prefilled from the face; the command carries the fields changed alone:
  the period typed, `--every 'weekday 10:00'`; the text rewritten, `--message`; the limit emptied, `--context off`;
  nothing changed, nothing plays; a `team` that refuses the verb says its refusal on the remedy line
  (`p`, a task given once made to come back: `ui-tasks-recurrence-plan`)
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
R1, R2 = T.RECURRING["recurrences"]
R4 = {**R2, "id": "R4", "name": "veille", "when": {"kind": "interval", "every": "4h", "seconds": 14400}, "stopped": None,
      "next_due": "2026-10-10T13:30"}
LIMITED = {**T.RECURRING, "recurrences": [{**R1, "context": 50}, R2, R4]}
EMPTIED = "team recurrence core-review R1 --context off"
REWRITTEN = "team recurrence core-review R1 --message 'new text'"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-recurrence-gestures", T.script(states={"core-review": [LIMITED], "ops": [T.OPS]}))

    # --- a duration said as team writes it ---------------------------------------------------------------------------
    shown = house.render("--render", "tasks", *SIZE, "--press", "e")
    r4 = next((T.cells_of(one) for one in P.overlay_rows(P.on_top(shown.stdout)) if T.cells_of(one)[:1] == ["R4"]), [])
    if shown.returncode == 0 and r4[1:2] == ["4h"]:
        held("a duration is said as team writes it", f"{r4}")
    else:
        failures.append(f"  ✗ duration                    rc={shown.returncode} {r4} {P.on_top(shown.stdout)[-1200:]!r}")

    # --- x: the stop on the id typed ---------------------------------------------------------------------------------
    house.clear_journal()
    untyped = house.render("--render", "tasks", *SIZE, "--press", "e,x,enter")
    nothing = house.gestures()
    done = house.render("--render", "tasks", *SIZE, "--press", "e,x,R,1,enter")
    if (untyped.returncode == 0 and nothing == [] and "./pp" not in untyped.stdout
            and done.returncode == 0 and house.gestures() == [STOP]):
        held("x stops a recurrence once its id is typed", f"{STOP}; untyped: nothing played, no command on screen")
    else:
        failures.append(f"  ✗ stop                        rc={untyped.returncode},{done.returncode} {nothing} "
                        f"{house.gestures()} {untyped.stdout[-1200:]!r}")

    # --- m: the period changed; a team that does not know the verb ---------------------------------------------------
    keys = f"e,m,{CHANGE}"            # the field opens on its period, selected: what is typed replaces it
    house.clear_journal()
    done = house.render("--render", "tasks", *SIZE, "--press", keys + ",enter")
    played = house.gestures()
    house.use(T.script(states={"core-review": [LIMITED], "ops": [T.OPS]},
                       answers={"recurrence": {"rc": 2, "err": REFUSED + "\n"}}))
    refused = house.render("--render", "tasks", *SIZE, "--press", keys + ",enter")
    remedy = T.remedy_of(refused)
    if (done.returncode == 0 and played == [CHANGED] and refused.returncode == 0 and remedy.startswith(REFUSED[:40])):
        held("m changes the period; a refusal said", f"{played[0]}; refused: {remedy[:60]!r}")
    else:
        failures.append(f"  ✗ change                      rc={done.returncode},{refused.returncode} "
                        f"{played} {remedy!r} {done.stdout[-1500:]!r}")
    house.use(T.script(states={"core-review": [LIMITED], "ops": [T.OPS]}))

    # --- m: the text rewritten, the limit emptied, nothing changed ----------------------------------------------------
    said, codes = [], []
    for keys in ("e,m,tab,ctrl+a,n,e,w,space,t,e,x,t,enter", "e,m,tab,tab,backspace,enter"):
        house.clear_journal()
        emptied = house.render("--render", "tasks", *SIZE, "--press", keys)
        codes.append(emptied.returncode)
        said += house.gestures()
    house.clear_journal()
    unchanged = house.render("--render", "tasks", *SIZE, "--press", "e,m,enter")
    if (codes == [0, 0] and unchanged.returncode == 0 and said == [REWRITTEN, EMPTIED] and house.gestures() == []):
        held("m carries the fields changed alone", f"{said}; nothing changed: nothing played")
    else:
        failures.append(f"  ✗ fields changed              {said} {house.gestures()} {emptied.stdout[-1500:]!r}")

    return 0
