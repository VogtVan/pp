"""Scenario `ui-tasks-list-place` -- the list of the Tasks tab keeps its place (batch la-liste-qui-garde-sa-place), on
the bench's `pp-team` witness replaying the faces of `team` for three declared teams -- `core-review` and `ops` started,
`veille` never (`_tasks`):
- thirty tasks, the cursor on the twentieth, the list scrolled; read again with the same tasks, its scroll and the
  task under the cursor stay; read again with a new task at its head, the same task under the cursor, at the same row
  of the view -- each pair of readings judged by the lines it shows, whatever reading the post makes beside `u`
"""
from __future__ import annotations

from tests.harness import support

S = support(__file__, "tasks")
T, P = S.T, S.P


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-list-place")

    # --- the list keeps its place when the tasks are read again ----------------------------------------------
    crowded = T.crowded(30, opened=())
    touched = {**crowded, "tasks": [{**one, "cost": 0.5} if one["id"] == "T12" else one for one in crowded["tasks"]]}
    newest = {"id": "T31", "at": "2026-10-10T06:31:00+00:00", "text": "task 31 of the reviewer"}
    grown = {**touched, "tasks": touched["tasks"] + [{**touched["tasks"][-1], **newest}]}
    house.use(T.script(states={"core-review": [crowded, touched, touched, grown], "ops": [T.OPS]}))
    house.clear_journal()                                              # the states consumed from the first
    keys = ",".join(["shift+tab,shift+tab"] + ["down"] * 6 + ["tab,tab"] + ["down"] * 24 + ["rest:0.3"] + ["up"] * 5
                    + ["list,u,list,u,list,u,list"])                # the view laid out, the cursor off its last row
    done = house.render("--render", "tasks", "--size", "130x40", "--press", keys)
    noted = next((one.split()[1:] for one in done.stdout.split("\n") if one.startswith("list ")), [])
    places = [(int(top), key, row, int(lines)) for top, key, row, lines in (one.split(":") for one in noted)]
    pairs = list(zip(places, places[1:]))
    same = [(one, two) for one, two in pairs if one[3] == two[3]]          # read again, the same tasks
    grew = [(one, two) for one, two in pairs if two[3] == one[3] + 1]      # read again, T31 at the head
    if (done.returncode == 0 and len(places) == 4 and places[0][0] > 0 and same and len(grew) == 1
            and all(one == two for one, two in same)
            and all(two[1:3] == one[1:3] and two[0] == one[0] + 1 for one, two in grew)):
        held("the list keeps its place when the tasks are read again", f"scrolled {places[0][0]}, "
             f"{places[0][1]} at row {places[0][2]} of the view; the same tasks: {same[0][1]}; T31 at the head: "
             f"{grew[0][0]} -> {grew[0][1]}")
    else:
        failures.append(f"  ✗ list keeps its place        rc={done.returncode} {noted} {done.stdout[-1500:]!r} "
                        f"{done.stderr[-400:]!r}")
    house.use(T.script())
    return 0
