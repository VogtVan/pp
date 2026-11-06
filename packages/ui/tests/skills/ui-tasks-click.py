"""Scenario `ui-tasks-click` -- a click on the sequence of a task (batch l-inbox-et-les-taches), on the bench's `pp-team`
witness, T3's thread holding a post written in markdown:
- a click on the text of a row opens its message whole in an overlay titled by the row, rendered as markdown -- the
  emphasis drawn, its marks gone -- as `enter` does
- a click on the grid of a row puts the cursor on it and opens nothing
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")

CURSOR = P.palette_constant("CURSOR")
MARKED = {**T.T3_LOG[2], "text": "read the **whole** PR"}          # #44, the second row of the sequence
LOG = [T.T3_LOG[0], T.T3_LOG[1], MARKED, T.T3_LOG[3], T.T3_LOG[4]]
BODY = "#tasks-sequence .sequence-grid .sequence-lines"              # the rows of the sequence of the Tasks tab
TEXT_X, GRID_X = 90, 40         # a cell of the text column, a cell of the grid, at 200 columns, where nothing scrolls sideways
ROW_Y = 1                       # the second row, #44


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-click", T.script(log={"core-review": T.TEAM_LOG, "core-review/T3": LOG,
                                                           "core-review/T2": T.T2_LOG}))

    # --- a click on the text opens the message, in markdown ------------------------------------------------------
    done = house.render("--render", "tasks", "--size", "200x40", "--press", f"click:{BODY}:{TEXT_X}:{ROW_Y}")
    title, rows = P.title_of(done.stdout), [one for one in P.overlay_rows(done.stdout) if one]
    keyed = house.render("--render", "tasks", "--size", "200x40", "--press", "tab,home,down,enter")
    keyed_rows = [one for one in P.overlay_rows(keyed.stdout) if one]
    if (done.returncode == 0 and title and f"#{MARKED['id']}" in title[0] and "message" in title[0]
            and any("whole" in row and "**" not in row for row in rows[1:]) and not any("**" in row for row in rows)
            and keyed.returncode == 0 and keyed_rows[1:] == rows[1:]):
        held("a click on the text opens the message in markdown", f"{title[0]!r}; the emphasis drawn without its marks; "
             "the same overlay as enter")
    else:
        failures.append(f"  ✗ click on the text           rc={done.returncode}/{keyed.returncode} {title} {rows!r} "
                        f"{keyed_rows!r} {done.stdout[-1200:]!r} {done.stderr[-300:]!r}")

    # --- a click on the grid moves the cursor --------------------------------------------------------------------
    done = house.render("--render", "tasks", "--size", "200x40", "--press", f"click:{BODY}:{GRID_X}:{ROW_Y}")
    rows = [one for one in P.overlay_rows(done.stdout) if one]
    marked = next((one for one in done.stdout.split("\n") if CURSOR in one and f"#{MARKED['id']} " in one), "")
    if done.returncode == 0 and not rows and marked:
        held("a click on the grid moves the cursor", f"the cursor on #{MARKED['id']}, no overlay")
    else:
        failures.append(f"  ✗ click on the grid           rc={done.returncode} rows={rows!r} marked={marked!r} "
                        f"{done.stdout[-1200:]!r}")
    return 0
