"""Scenario `ui-tasks-recurrences` -- the recurrences of a team at the post (batch la-recurrence-au-poste), on the
bench's `pp-team` witness: `core-review` carries `recurrences` (`R1` live -- its occurrence T6 open --, `R2` stopped)
and `tasks[].recurrence`, `ops` none:
- `n` on Tasks, its field `every` typed `weekday 09:30`: `enter` plays `--every 'weekday 09:30'`, as the witness's
  journal says it -- no command on screen; the period is passed as typed, never judged
- the Tasks table marks an occurrence in its column `id` (`T6 ↻`), a task of no recurrence as it was (`T3`)
- `e` on Tasks opens the recurrences of the team of the task under the cursor: one line per entry of the face's
  `recurrences`, its id, its period, its name or the start of its text, its member, its last occurrence, its next
  period or its stop; a team without one says none
  (its gestures, `x` and `m`: `ui-tasks-recurrence-gestures`)
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")

SIZE = ("--size", "150x45")
RECURS, NONE = P.palette_constant("RECURS"), P.palette_constant("NONE")
EVERY = "weekday 09:30"
TYPED = ",".join({" ": "space", ":": "colon"}.get(one, one) for one in EVERY)
POSTED = f"team post core-review --every '{EVERY}' --message go"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-recurrences", T.script(states={"core-review": [T.RECURRING], "ops": [T.OPS]}))

    # --- n: the field every ----------------------------------------------------------------------------------------
    keys = f"n,g,o,tab,{TYPED}"
    house.clear_journal()
    done = house.render("--render", "tasks", *SIZE, "--press", keys + ",enter")
    if done.returncode == 0 and house.gestures() == [POSTED]:
        held("n lays a recurrence as typed", POSTED)
    else:
        failures.append(f"  ✗ every                       rc={done.returncode} "
                        f"{house.gestures()} {done.stdout[-1500:]!r} {done.stderr[-300:]!r}")

    # --- the mark of an occurrence -----------------------------------------------------------------------------------
    done = house.render("--render", "tasks", *SIZE)
    centre = T.sides_of(done.stdout)[1]
    occurrence = T.cells_by_name(centre, "id", f"T6 {RECURS}")
    plain = T.cells_by_name(centre, "id", "T3")
    if done.returncode == 0 and occurrence.get("task") == T.T6["name"] and plain.get("task") == "review PR 88":
        held("an occurrence is marked in the column id", f"T6 {RECURS} {occurrence.get('task')!r}; T3 as it was")
    else:
        failures.append(f"  ✗ mark                        rc={done.returncode} {occurrence} {plain} {done.stdout[-1500:]!r}")

    # --- e: the recurrences of the team ------------------------------------------------------------------------------
    done = house.render("--render", "tasks", *SIZE, "--press", "e")
    rows = [T.cells_of(one) for one in P.overlay_rows(P.on_top(done.stdout))]
    first = next((one for one in rows if one[:1] == ["R1"]), [])
    second = next((one for one in rows if one[:1] == ["R2"]), [])
    empty = house.render("--render", "tasks", *SIZE, "--press", "shift+tab,down,down,e")
    title = " ".join(P.title_of(P.on_top(empty.stdout)) or [""])
    bare = [T.cells_of(one) for one in P.overlay_rows(P.on_top(empty.stdout))]
    if (done.returncode == 0 and T.in_order(" ".join(first), "R1", "weekday", "09:30", "revue", "lead", "T6")
            and T.in_order(" ".join(second), "R2", "day", "18:00", "reviewer") and "stopped" in second
            and empty.returncode == 0 and "ops" in title and any(NONE in one for one in bare)
            and not any(one[:1] in (["R1"], ["R2"]) for one in bare)):
        held("e shows the recurrences of the team", f"{first}; {second}; ops: none")
    else:
        failures.append(f"  ✗ recurrences                 rc={done.returncode},{empty.returncode} {first} {second} "
                        f"{title!r} {bare} {P.on_top(done.stdout)[-1500:]!r}")

    return 0
