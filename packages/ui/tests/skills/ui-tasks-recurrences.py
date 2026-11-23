"""Scenario `ui-tasks-recurrences` -- the recurrences of a team at the post (batch la-recurrence-au-poste), on the
bench's `pp-team` witness: `core-review` carries `recurrences` (`R1` live -- its occurrence T6 open --, `R2` stopped)
and `tasks[].recurrence`, `ops` none:
- `n` on Tasks, its field `every` typed `weekday 09:30`: `enter` plays `--every 'weekday 09:30'`, as the witness's
  journal says it -- no command on screen; the period is passed as typed, never judged
- the Tasks table marks an occurrence in its column `id` (`T6 ↻`), a task of no recurrence as it was (`T3`)
- `e` on Tasks opens the recurrences of the team of the task under the cursor: one line per entry of the face's
  `recurrences`, its id, its period, its name or the start of its text, its member, its last occurrence, its next
  period; a team without one says none
- the overlay `e` at the post (batch les-recurrences-au-poste), `core-review` carrying three recurrences -- `R1`,
  `R2` stopped, `R3` whose occurrence T8 is the task under the cursor --: the stopped one is not listed; `x` says
  that it deletes (`palette.DELETES`); the cursor opens on the recurrence of the task under the cursor's, so that
  `x` and its id typed play `team stop core-review --recurrence R3`; the box is EventScreen's, 95 % of the width,
  90 % of the height
  (its gestures, `x` and `m`: `ui-tasks-recurrence-gestures`)
  (under the `TEAM` filter `all`, every team's, and `enter`: `ui-tasks-recurrences-all`)
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")

SIZE = ("--size", "150x45")
RECURS, NONE = P.palette_constant("RECURS"), P.palette_constant("NONE")
EVERY = "weekday 09:30"
TYPED = ",".join({" ": "space", ":": "colon"}.get(one, one) for one in EVERY)
POSTED = f"team post core-review --every '{EVERY}' --message go --no-tick"


def word(name: str) -> str | None:
    """-> the word `name` of the palette; None when the palette has none."""
    try:
        return P.palette_constant(name)
    except KeyError:
        return None


DELETES = word("DELETES")                                       # what `x` says in `e`
R = support(__file__, "tasks_recurrences")
THREE, DELETED = R.THREE, R.DELETED


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-recurrences", T.script(states={"core-review": [T.RECURRING], "ops": [T.OPS]}))

    # --- n: the field every ----------------------------------------------------------------------------------------
    keys = f"n,g,o,tab,{TYPED}"
    house.clear_journal()
    done = house.render("--render", "tasks", *SIZE, "--press", keys + ",ctrl+enter")
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
    empty = house.render("--render", "tasks", *SIZE, "--press", "shift+tab,down,down,e")
    title = " ".join(P.title_of(P.on_top(empty.stdout)) or [""])
    bare = [T.cells_of(one) for one in P.overlay_rows(P.on_top(empty.stdout))]
    if (done.returncode == 0 and T.in_order(" ".join(first), "R1", "weekday", "09:30", "revue", "lead", "T6")
            and empty.returncode == 0 and "ops" in title and any(NONE in one for one in bare)
            and not any(one[:1] in (["R1"], ["R2"]) for one in bare)):
        held("e shows the recurrences of the team", f"{first}; ops: none")
    else:
        failures.append(f"  ✗ recurrences                 rc={done.returncode},{empty.returncode} {first} "
                        f"{title!r} {bare} {P.on_top(done.stdout)[-1500:]!r}")

    # --- e at the post: the stopped one left out, x deletes, the cursor on the task's, the box wide ---------------
    house.use(T.script(states={"core-review": [THREE], "ops": [T.OPS]}))
    done = house.render("--render", "tasks", *SIZE, "--press", "e")
    top = P.on_top(done.stdout)
    listed = [T.cells_of(one)[0] for one in P.overlay_rows(top) if T.cells_of(one)[:1] in (["R1"], ["R2"], ["R3"])]
    said = next((one for one in P.overlay_rows(top) if "[x]" in one), "")
    if done.returncode == 0 and listed == ["R1", "R3"] and DELETES and f"[x] {DELETES}" in said:
        held("a stopped recurrence leaves e, x deletes", f"{listed}, R2 stopped left out; {said!r}")
    else:
        failures.append(f"  ✗ stopped left out           rc={done.returncode} {listed} {said!r} {top[-1500:]!r}")

    house.clear_journal()
    done = house.render("--render", "tasks", *SIZE, "--press", "e,x,R,3,ctrl+enter")
    if done.returncode == 0 and house.gestures() == [DELETED]:
        held("e opens on the recurrence of the task under the cursor", f"T8 an occurrence of R3: x R3 -> {DELETED}")
    else:
        failures.append(f"  ✗ cursor on the task's       rc={done.returncode} {house.gestures()} "
                        f"{P.on_top(done.stdout)[-1200:]!r}")

    rows = top.split("\n")
    bottom = next((n for n, row in enumerate(rows) if n > 0 and "┗" in row), -1)
    wide = rows[0].index("┓") - rows[0].index("┏") + 1 if "┏" in rows[0] else 0
    high = bottom + 1 if bottom > 0 else 0
    if wide >= int(150 * 0.95) - 1 and high >= int(45 * 0.9) - 1:
        held("the box of e is EventScreen's", f"box {wide}x{high} on 150x45")
    else:
        failures.append(f"  ✗ box                         box={wide}x{high} on 150x45 {top[-1500:]!r}")
    return 0
