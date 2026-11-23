"""Scenario `ui-tasks-recurrence-pause` -- one recurrence paused and resumed from the overlay `e` of the Tasks tab
(batch la-pause-de-recurrence-au-poste, a sibling of `ui-tasks-recurrence-gestures`), on the bench's `pp-team`
witness: `core-review` carries `R1` live, `R2` stopped and `R5` paused by its owner (team 1.4.7: `paused` `{by, at,
id}`, no next period while it sleeps); what a gesture plays is read from the witness's journal, never on screen:
- a paused recurrence says `paused` in place of its next period
- `space` pauses the line under the cursor -- `team pause core-review --recurrence R1`, which ticks nothing -- or resumes
  it when the face says it paused -- `team resume core-review --recurrence R5 --no-tick` --, in a gesture of its `as`
  alone, prefilled with the owner; the status line says what it did (`gestures.summary`); `escape` plays nothing
- `l` launches the line under the cursor now -- `team recurrence core-review R1 --now --no-tick` --, without an overlay
  of its own; the status line says it, the overlay read again stays on top
"""
from __future__ import annotations

import importlib
import shlex
import sys

from tests.harness import SOURCE, support

T = support(__file__, "teams")
P = support(__file__, "dialogue")

SIZE = ("--size", "150x45")
CUT = P.palette_constant("PENDING")   # the status line cuts a long note there
SKILL = SOURCE / "packages" / "ui" / "skills" / "pp-ui"
R1, R2 = T.RECURRING["recurrences"]
R5 = {**R1, "id": "R5", "name": "nuit", "next_due": None, "last": None,
      "paused": {"by": "house", "at": "2026-10-10T09:30:00+00:00", "id": 61}}
SLEEPING = {**T.RECURRING, "recurrences": [R1, R2, R5]}
PAUSE = "team pause core-review --recurrence R1"
RESUME = "team resume core-review --recurrence R5 --no-tick"
LAUNCH = "team recurrence core-review R1 --now --no-tick"


def _says(status: str, summary: str) -> bool:
    """-> whether the status line says `summary`, whole or cut by the post's ellipsis."""
    notes = [one.strip() for one in status.split(P.palette_constant("SEP").strip())]
    return any(one == summary or (one.endswith(CUT) and len(one) > 1 and summary.startswith(one[:-len(CUT)]))
               for one in notes)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-recurrence-pause", T.script(states={"core-review": [SLEEPING], "ops": [T.OPS]}))
    sys.path.insert(0, str(SKILL))
    summary = importlib.import_module("model.gestures").summary

    # --- a paused recurrence says it in place of its next period -----------------------------------------------------
    shown = house.render("--render", "tasks", *SIZE, "--press", "e")
    rows = {cells[0]: cells for cells in (T.cells_of(one) for one in P.overlay_rows(P.on_top(shown.stdout))) if cells}
    if shown.returncode == 0 and rows.get("R5", [])[-1:] == ["paused"] and rows.get("R1", [])[-1:] != ["paused"]:
        held("a paused recurrence says paused", f"R5 {rows['R5']}; R1 {rows['R1']}")
    else:
        failures.append(f"  ✗ paused said                 rc={shown.returncode} {rows.get('R1')} {rows.get('R5')} "
                        f"{P.on_top(shown.stdout)[-1200:]!r}")

    # --- space: R1 paused, R5 resumed, the status line saying it; escape plays nothing --------------------------------
    played, statuses = [], []
    for keys in ("e,space,ctrl+enter", "e,down,down,space,ctrl+enter"):
        house.clear_journal()
        done = house.render("--render", "tasks", *SIZE, "--press", keys)
        played += house.gestures()
        statuses.append(P.status_of(done.stdout))
    house.clear_journal()
    escaped = house.render("--render", "tasks", *SIZE, "--press", "e,space,escape")
    said = [summary(shlex.split(one)) for one in (PAUSE, RESUME)]
    if (played == [PAUSE, RESUME] and all(_says(status, one) for one, status in zip(said, statuses))
            and escaped.returncode == 0 and house.gestures() == []):
        held("space pauses a recurrence, resumes a paused one", f"{played}; status {said}; escape: nothing played")
    else:
        failures.append(f"  ✗ pause                       {played} {statuses} {said} {house.gestures()} "
                        f"{escaped.stdout[-1200:]!r}")

    # --- l: the line under the cursor launched now, the overlay on top -----------------------------------------------
    house.clear_journal()
    launched = house.render("--render", "tasks", *SIZE, "--press", "e,l")
    played = house.gestures()
    said = summary(shlex.split(LAUNCH))
    rows = [cells[0] for cells in (T.cells_of(one) for one in P.overlay_rows(P.on_top(launched.stdout))) if cells]
    if (launched.returncode == 0 and played == [LAUNCH] and _says(P.status_of(launched.stdout), said)
            and {"R1", "R5"} <= set(rows)):
        held("l launches a recurrence now", f"{played}; status {said!r}; the overlay on top {rows}")
    else:
        failures.append(f"  ✗ launch                      rc={launched.returncode} {played} {said!r} {rows} "
                        f"{launched.stdout[-1200:]!r}")

    return 0
