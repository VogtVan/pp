"""Scenario `ui-tasks-recurring` -- the filter `recurring` of the Tasks tab (batch les-taches-planifiees), on the
bench's `pp-team` witness: `core-review` carries `recurrences` (`R1` live -- its occurrence T6 open --, `R2` stopped,
`R3` laid and never sounded, `R5` paused), `ops` none:
- `SHOW` `recurring` lists the live recurrences of every team -- `R3` before `R1`, its next period the nearest; `R5`,
  paused, last, `paused` in place of its next period; `R2`, stopped, left out -- in the columns of a recurrence and its team; its count is the rows it lists, `0` under a team
  without one; the band says `R3` whole; `s` on it plays nothing and says why on the remedy line
- a recurrence laid from the tab is FOLLOWED: once its team says it, the cursor is on it and `SHOW` turns to
  `recurring`
- a team out of season (s.1703): core-review's last season `stopped` -- under `recurring` each cell of R3's line is
  italic and its next period is `palette.OFF_SEASON`, R5 `paused` as before; the same line in the overlay `e` of
  core-review; in season (the first render) no cell of R3's line is italic
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")

SIZE = ("--size", "150x45")
NONE, SEP = P.palette_constant("NONE"), P.palette_constant("SEP")
EVERY = "weekday 09:30"
TYPED = ",".join({" ": "space", ":": "colon"}.get(one, one) for one in EVERY)
POSTED = f"team post core-review --every '{EVERY}' --message go --no-tick"
# a recurrence laid and never sounded: its next period before R1's
R3 = {"id": "R3", "name": "veille", "text": "watch the CVE feeds of the gateway", "from": "house", "to": "reviewer",
      "when": {"kind": "day", "at": "07:00"}, "since": "2026-10-10T09:40:00", "next_due": "2026-10-11T07:00",
      "due": False, "stopped": None, "last": None}
# a recurrence paused by its owner (team 1.4.7): no next period while it sleeps
R5 = {**T.RECURRING["recurrences"][0], "id": "R5", "name": "nuit", "next_due": None, "last": None,
      "paused": {"by": "house", "at": "2026-10-10T09:30:00+00:00", "id": 61}}
SLEEPING = {**T.RECURRING, "recurrences": T.RECURRING["recurrences"] + [R5]}
LAID = {**SLEEPING, "recurrences": SLEEPING["recurrences"] + [R3]}
RECURRING = "shift+tab,shift+tab,down,down,down,down,down"   # SHOW `recurring`, after `resolved`
OFF = {**LAID, "season": {**LAID["season"], "state": "stopped",
                          "stopped": {"at": "2026-10-10T10:00:00+00:00", "by": "house", "id": 70}}}   # out of season
CORE_ALONE = "shift+tab,down,e"                              # TEAM core-review, then its recurrences


def off_season() -> str | None:
    try:
        return P.palette_constant("OFF_SEASON")
    except KeyError:
        return None


def runs_of(text: str, within: str) -> list[tuple[bool, str]]:
    """-> the runs of the first raw row of a `--styles` capture whose bare text holds `within`: (italic, its text)."""
    for row in text.split("\n"):
        if within not in P.ANSI.sub("", row):
            continue
        found, current = [], ""
        for part in re.split(r"(\x1b\[[0-9;]*m)", row):
            sgr = P.SGR.fullmatch(part)
            if sgr:
                current = sgr.group(1)
            elif part.strip():
                found.append((_italic(current), part))
        return found
    return []


def _italic(params: str) -> bool:
    """-> whether SGR parameters say italic (`3`), the colours' own numbers (`38;2;r;g;b`, `48;5;n`) skipped."""
    tokens, at = params.split(";"), 0
    while at < len(tokens):
        if tokens[at] in ("38", "48") and at + 1 < len(tokens):
            at += 5 if tokens[at + 1] == "2" else 3
            continue
        if tokens[at] == "3":
            return True
        at += 1
    return False


def all_italic(runs: list[tuple[bool, str]], *values: str) -> bool:
    """-> whether each value stands in a run drawn italic."""
    return bool(runs) and all(any(italic and one in part for italic, part in runs) for one in values)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-recurring", T.script(states={"core-review": [LAID], "ops": [T.OPS]}))
    keys = f"n,g,o,tab,{TYPED}"

    # --- SHOW recurring: the live recurrences, in their own columns ---------------------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", *SIZE, "--press", RECURRING + ",s", "--styles")   # `s` on R3, first
    in_season = runs_of(done.stdout, R3["name"])
    done.stdout = P.ANSI.sub("", done.stdout)
    menu, centre = T.sides_of(done.stdout)
    ids = [cells[0] for cells in (T.cells_of(row) for row in centre) if cells and cells[0] in ("R1", "R2", "R3", "R5")]
    r3, r5 = T.cells_by_name(centre, "id", "R3"), T.cells_by_name(centre, "id", "R5")
    count = next((T.cells_of(one)[-1] for one in menu if T.cells_of(one)[:1] == ["recurring"]), None)
    band = T.band_rows(centre)
    status = P.status_of(done.stdout)
    alone = house.render("--render", "tasks", *SIZE, "--press", "shift+tab,down,down")
    zero = next((T.cells_of(one)[-1] for one in T.sides_of(alone.stdout)[0] if T.cells_of(one)[:1] == ["recurring"]), None)
    if (done.returncode == 0 and ids == ["R3", "R1", "R5"] and count == str(len(ids)) and r5.get("next") == "paused"
            and [r3.get(one) for one in ("every", "task", "team", "to", "last", "next")]
            == ["day 07:00", "veille", "core-review", "reviewer", NONE, "2026-10-11 07:00"]
            and any(row.startswith(f"R3{SEP}") for row in band) and any(R3["text"] in row for row in band)
            and f"{len(ids)}/{len(ids)}" in status and "show recurring" in status
            and house.gestures() == [] and T.remedy_of(done)
            and alone.returncode == 0 and zero == "0"):
        held("recurring lists the live recurrences", f"{ids} count {count}, R3 {r3}, R5 {r5}; band R3; status {status!r}; "
             f"s on R3 plays nothing: {T.remedy_of(done)!r}; ops: {zero}")
    else:
        failures.append(f"  ✗ recurring                   rc={done.returncode} {ids} {count} {r3} {r5} {band[:3]} {status!r} "
                        f"{house.gestures()} {T.remedy_of(done)!r} {zero!r} {done.stdout[-1800:]!r} "
                        f"{done.stderr[-300:]!r}")

    # --- a recurrence laid from the tab follows ------------------------------------------------------------------
    house.use(T.script(states={"core-review": [SLEEPING, LAID], "ops": [T.OPS]}))
    house.clear_journal()
    done = house.render("--render", "tasks", *SIZE, "--press", keys + ",ctrl+enter")
    band = T.band_rows(T.sides_of(done.stdout)[1])
    status = P.status_of(done.stdout)
    if (done.returncode == 0 and house.gestures() == [POSTED] and band[:1] and band[0].startswith(f"R3{SEP}")
            and "show recurring" in status):
        held("a recurrence laid follows", f"{POSTED!r}: R3 under the cursor, {status!r}")
    else:
        failures.append(f"  ✗ laid follows                rc={done.returncode} {house.gestures()} {band[:2]} {status!r} "
                        f"{done.stdout[-1800:]!r} {done.stderr[-300:]!r}")

    # --- a team out of season: its recurrences in italic, their next period said off -- s.1703 -------------------
    mark = off_season()
    house.use(T.script(states={"core-review": [OFF], "ops": [T.OPS]}))
    listed = house.render("--render", "tasks", *SIZE, "--press", RECURRING, "--styles")
    overlay = house.render("--render", "tasks", *SIZE, "--press", CORE_ALONE, "--styles")
    plain = P.ANSI.sub("", listed.stdout)
    r3, r5 = (T.cells_by_name(T.sides_of(plain)[1], "id", one) for one in ("R3", "R5"))
    in_list, in_overlay = runs_of(listed.stdout, R3["name"]), runs_of(overlay.stdout, R3["name"])
    if (listed.returncode == 0 and overlay.returncode == 0 and mark and r3.get("next") == mark
            and r5.get("next") == "paused"
            and all_italic(in_list, "R3", "day 07:00", R3["name"], "core-review", "reviewer", mark)
            and all_italic(in_overlay, "R3", "day 07:00", R3["name"], "reviewer", mark)
            and in_season and not any(italic for italic, _ in in_season if R3["name"] in _)):
        held("a team out of season: its recurrences in italic", f"R3's next {r3.get('next')!r} = OFF_SEASON, R5 "
             f"{r5.get('next')!r}; every cell of R3 italic in the list and in e; in season R3 upright")
    else:
        failures.append(f"  ✗ out of season               rc={listed.returncode}/{overlay.returncode} mark={mark!r} "
                        f"r3={r3} r5={r5} list={in_list} e={in_overlay} in season={in_season} "
                        f"{P.ANSI.sub('', overlay.stdout)[-1500:]!r}")
    house.use(T.script())

    return 0
