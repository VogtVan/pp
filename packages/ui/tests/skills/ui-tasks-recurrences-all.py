"""Scenario `ui-tasks-recurrences-all` -- the overlay `e` of the Tasks tab under the `TEAM` filter `all` (batch
les-recurrences-de-toutes-les-equipes), on the bench's `pp-team` witness: `core-review` carrying three recurrences --
`R1`, `R2` stopped, `R3` whose occurrence T8 is the task under the cursor --, `ops` a live recurrence of its own, `R1`,
the id `core-review`'s also bears:
- `e` under `all` lists the live recurrences of every team, each line its team, the cursor on the recurrence of the
  task under the cursor's; `x` on the line of `ops` plays `team stop ops --recurrence R1` -- the team the line's, never
  the task's (s.1461); a team chosen at the filter keeps the overlay to that team
- `enter` on a line of `e` leaves the overlay open (s.1462); `escape` and `q` close it
- a gesture of `e` opens OVER it (batch les-gestes-par-dessus-les-recurrences, s.1462 read again): `x` and the id typed,
  `enter` plays `team stop core-review --recurrence R3` and gives `e` back on top, read again -- `R3`, stopped, gone;
  `x` then `escape`, `m` then `escape` play nothing and give `e` back on top
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")
R = support(__file__, "tasks_recurrences")

SIZE = ("--size", "150x45")
THREE, DELETED = R.THREE, R.DELETED
# a live recurrence of the second team, its id the one `core-review`'s R1 bears, its next period after theirs
OPS_R1 = {**R.R1, "name": "rotation", "text": "rotate the certificates", "to": "sre", "next_due": "2026-10-13T07:00",
          "last": None}
OPS_RECURRING = {**T.OPS, "recurrences": [OPS_R1]}
OTHER = "team stop ops --recurrence R1 --no-tick"
# what `core-review` says once R3 is stopped: the face read again after `x`
STOPPED = {**THREE, "recurrences": THREE["recurrences"][:2] + [
    {**R.R3, "stopped": {"by": "house", "at": "2026-10-10T09:50:00+00:00", "id": 62}}]}
DELETES = P.palette_constant("DELETES")


def listed(done) -> list[str]:
    """-> the ids of the recurrences the overlay on top lists, when it is `e` -- its line of keys says `x` deletes."""
    rows = P.overlay_rows(P.on_top(done.stdout))
    if not any(f"[x] {DELETES}" in one for one in rows):
        return []
    return [T.cells_of(one)[0] for one in rows if T.cells_of(one)[:1] in (["R1"], ["R2"], ["R3"])]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-recurrences-all", T.script(states={"core-review": [THREE], "ops": [OPS_RECURRING]}))

    # --- e under TEAM all: the recurrences of every team, x on the line of the other team ---------------------------
    done = house.render("--render", "tasks", *SIZE, "--press", "e")
    lines = [T.cells_of(one) for one in P.overlay_rows(P.on_top(done.stdout))]
    lines = [one for one in lines if one[:1] in (["R1"], ["R3"])]
    teams = sorted((one[0], next((team for team in ("core-review", "ops") if team in one), None)) for one in lines)
    house.clear_journal()
    other = house.render("--render", "tasks", *SIZE, "--press", "e,down,x,R,1,ctrl+enter")
    played = house.gestures()
    alone = house.render("--render", "tasks", *SIZE, "--press", "shift+tab,down,e")    # TEAM core-review
    kept = [T.cells_of(one) for one in P.overlay_rows(P.on_top(alone.stdout))]
    kept = [one for one in kept if one[:1] in (["R1"], ["R3"])]
    if (done.returncode == 0 and teams == [("R1", "core-review"), ("R1", "ops"), ("R3", "core-review")]
            and other.returncode == 0 and played == [OTHER]
            and alone.returncode == 0 and [one[0] for one in kept] == ["R1", "R3"]
            and not any("ops" in one for one in kept)):
        held("e under all lists every team, x plays on the line's team", f"{teams}; down,x R1 -> {played}; "
             f"TEAM core-review: {[one[0] for one in kept]}")
    else:
        failures.append(f"  ✗ every team                  rc={done.returncode},{other.returncode},{alone.returncode} "
                        f"{teams} {played} {kept} {P.on_top(done.stdout)[-1500:]!r}")

    # --- a gesture over e: played, e back read again; abandoned, e back ------------------------------------------
    house.use(T.script(states={"core-review": [THREE, STOPPED], "ops": [T.OPS]}))
    house.clear_journal()
    entered = house.render("--render", "tasks", *SIZE, "--press", "e,enter,x,R,3,ctrl+enter")
    played, after = house.gestures(), listed(entered)
    if entered.returncode == 0 and played == [DELETED] and after == ["R1"]:
        held("a gesture played from e gives e back, read again", f"x R3 -> {played}; e on top: {after}")
    else:
        failures.append(f"  ✗ e back after a gesture      rc={entered.returncode} {played} {after} "
                        f"{P.on_top(entered.stdout)[-1500:]!r}")
    house.clear_journal()
    back = house.render("--render", "tasks", *SIZE, "--press", "e,x,escape,m,escape")
    played, again = house.gestures(), listed(back)
    if back.returncode == 0 and played == [] and again == ["R1", "R3"]:
        held("a gesture abandoned gives e back", f"x esc, m esc: nothing played; e on top: {again}")
    else:
        failures.append(f"  ✗ e back after escape        rc={back.returncode} {played} {again} "
                        f"{P.on_top(back.stdout)[-1500:]!r}")

    # --- enter leaves the overlay open; escape and q close it -----------------------------------------------------
    house.clear_journal()
    open_rows = house.render("--render", "tasks", *SIZE, "--press", "e,enter")
    still = listed(open_rows)
    closed = {}
    for key in ("escape", "q"):
        gone = house.render("--render", "tasks", *SIZE, "--press", f"e,{key}")
        closed[key] = (gone.returncode, listed(gone))
    if open_rows.returncode == 0 and still == ["R1", "R3"] and closed == {"escape": (0, []), "q": (0, [])}:
        held("enter leaves e open, escape and q close it", f"e,enter: {still}; {closed}")
    else:
        failures.append(f"  ✗ enter keeps e open          rc={open_rows.returncode} {still} {closed} "
                        f"{P.on_top(open_rows.stdout)[-1500:]!r}")
    return 0
