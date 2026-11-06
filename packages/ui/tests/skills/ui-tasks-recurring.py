"""Scenario `ui-tasks-recurring` -- the filter `recurring` of the Tasks tab (batch les-taches-planifiees), on the
bench's `pp-team` witness: `core-review` carries `recurrences` (`R1` live -- its occurrence T6 open --, `R2` stopped,
`R3` laid and never sounded), `ops` none:
- `SHOW` `recurring` lists the live recurrences of every team -- `R3` before `R1`, its next period the nearest; `R2`,
  stopped, left out -- in the columns of a recurrence and its team; its count is the rows it lists, `0` under a team
  without one; the band says `R3` whole; `s` on it plays nothing and says why on the remedy line
- a recurrence laid from the tab is FOLLOWED: once its team says it, the cursor is on it and `SHOW` turns to
  `recurring`
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")

SIZE = ("--size", "150x45")
NONE, SEP = P.palette_constant("NONE"), P.palette_constant("SEP")
EVERY = "weekday 09:30"
TYPED = ",".join({" ": "space", ":": "colon"}.get(one, one) for one in EVERY)
POSTED = f"team post core-review --every '{EVERY}' --message go"
# a recurrence laid and never sounded: its next period before R1's
R3 = {"id": "R3", "name": "veille", "text": "watch the CVE feeds of the gateway", "from": "house", "to": "reviewer",
      "when": {"kind": "day", "at": "07:00"}, "since": "2026-10-10T09:40:00", "next_due": "2026-10-11T07:00",
      "due": False, "stopped": None, "last": None}
LAID = {**T.RECURRING, "recurrences": T.RECURRING["recurrences"] + [R3]}
RECURRING = "shift+tab,shift+tab,down,down,down,down,down"   # SHOW `recurring`, after `resolved`


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-recurring", T.script(states={"core-review": [LAID], "ops": [T.OPS]}))
    keys = f"n,g,o,tab,{TYPED}"

    # --- SHOW recurring: the live recurrences, in their own columns ---------------------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", *SIZE, "--press", RECURRING + ",s")   # `s` on R3, the line first
    menu, centre = T.sides_of(done.stdout)
    ids = [cells[0] for cells in (T.cells_of(row) for row in centre) if cells and cells[0] in ("R1", "R2", "R3")]
    r3 = T.cells_by_name(centre, "id", "R3")
    count = next((T.cells_of(one)[-1] for one in menu if T.cells_of(one)[:1] == ["recurring"]), None)
    band = T.band_rows(centre)
    status = P.status_of(done.stdout)
    alone = house.render("--render", "tasks", *SIZE, "--press", "shift+tab,down,down")
    zero = next((T.cells_of(one)[-1] for one in T.sides_of(alone.stdout)[0] if T.cells_of(one)[:1] == ["recurring"]), None)
    if (done.returncode == 0 and ids == ["R3", "R1"] and count == str(len(ids))
            and [r3.get(one) for one in ("every", "task", "team", "to", "last", "next")]
            == ["day 07:00", "veille", "core-review", "reviewer", NONE, "2026-10-11 07:00"]
            and any(row.startswith(f"R3{SEP}") for row in band) and any(R3["text"] in row for row in band)
            and "2/2" in status and "show recurring" in status
            and house.gestures() == [] and T.remedy_of(done)
            and alone.returncode == 0 and zero == "0"):
        held("recurring lists the live recurrences", f"{ids} count {count}, R3 {r3}; band R3; status {status!r}; "
             f"s on R3 plays nothing: {T.remedy_of(done)!r}; ops: {zero}")
    else:
        failures.append(f"  ✗ recurring                   rc={done.returncode} {ids} {count} {r3} {band[:3]} {status!r} "
                        f"{house.gestures()} {T.remedy_of(done)!r} {zero!r} {done.stdout[-1800:]!r} "
                        f"{done.stderr[-300:]!r}")

    # --- a recurrence laid from the tab follows ------------------------------------------------------------------
    house.use(T.script(states={"core-review": [T.RECURRING, LAID], "ops": [T.OPS]}))
    house.clear_journal()
    done = house.render("--render", "tasks", *SIZE, "--press", keys + ",enter")
    band = T.band_rows(T.sides_of(done.stdout)[1])
    status = P.status_of(done.stdout)
    if (done.returncode == 0 and house.gestures() == [POSTED] and band[:1] and band[0].startswith(f"R3{SEP}")
            and "show recurring" in status):
        held("a recurrence laid follows", f"{POSTED!r}: R3 under the cursor, {status!r}")
    else:
        failures.append(f"  ✗ laid follows                rc={done.returncode} {house.gestures()} {band[:2]} {status!r} "
                        f"{done.stdout[-1800:]!r} {done.stderr[-300:]!r}")
    house.use(T.script())

    return 0
