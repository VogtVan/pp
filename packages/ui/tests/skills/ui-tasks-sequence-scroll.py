"""Scenario `ui-tasks-sequence-scroll` -- the scroll of a sequence is the operator's (plan pp-fixes, batch
la-sequence-qui-suit-sans-figer, s.1365): T3's thread of 425 rows on the bench's `pp-team` witness, the Tasks tab
played under Textual's pilot at 180x50, the body's `scroll_y` read:
- the view at the end, then scrolled by hand -- `scroll_to`, then the mouse wheel up --, a row and an activity coming
  leave `scroll_y` where the hand put it
- `up` puts the cursor on a row in sight
- the cursor on the last row and the view at the end, a row added: the view follows the end, the cursor on the new row
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

HAND = 200                  # the row the hand scrolls the body to, before the wheel
WATCH = [{"sleep": 5.0}, T.long_post(T.LONG, "lead", "reviewer"), T.lead_act(0), {"sleep": 4.0},
         T.long_post(T.LONG + 1, "reviewer", "lead")]
PROBE = """
async def probe(app, pilot, view, out):
    out["read"] = await until(pilot, lambda: len(view.shown) >= ROWS)
    grid = view.query_one(".sequence-grid")
    out["ended"] = await until(pilot, lambda: 0 < grid.max_scroll_y == grid.scroll_y)
    grid.scroll_to(y=%d, animate=False)
    await pilot.pause()
    grid.post_message(events.MouseScrollUp(grid, 2, 2, 0, -1, 0, False, False, False))
    await pilot.pause()
    await pilot.pause()
    hand = round(grid.scroll_y)
    out["early"] = app.saw("team:post")
    await until(pilot, lambda: app.saw("team:post") >= 1 and app.saw("team:activity") >= 1)
    await app.pane_settled()
    await pilot.pause()
    await pilot.pause()
    out["kept"] = [hand, round(grid.scroll_y), len(view.shown)]
    await pilot.press("tab")
    await pilot.press("up")
    await pilot.pause()
    await pilot.pause()
    out["up"] = [view.cursor, round(grid.scroll_y), grid.scrollable_content_region.height]
    await pilot.press("end")
    await pilot.pause()
    await pilot.pause()
    out["end"] = [view.cursor, len(view.shown), round(grid.scroll_y), round(grid.max_scroll_y), app.saw("team:post")]
    await until(pilot, lambda: app.saw("team:post") >= 2)
    await app.pane_settled()
    await pilot.pause()
    await pilot.pause()
    out["followed"] = [view.cursor, len(view.shown), round(grid.scroll_y), round(grid.max_scroll_y),
                       grid.scrollable_content_region.height]
""" % HAND


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-sequence-scroll", T.long_script(WATCH))
    [(rc, said, err)] = T.piloted(bench, house, "ui-tasks-sequence-scroll", PROBE, "tasks")
    if rc != 0 or not said:
        failures.append(f"  ✗ probe                       rc={rc} {err[-1500:]!r}")
        return 0
    if not said.get("read") or not said.get("ended") or said.get("early"):
        failures.append(f"  ✗ thread                      read={said.get('read')} at the end={said.get('ended')} "
                        f"early={said.get('early')}")
        return 0

    # --- a scroll by hand is kept when a row and an activity come ----------------------------------------------
    hand, after, rows = said.get("kept") or [None, None, 0]
    if hand is not None and 0 < hand < HAND and after == hand and rows == T.LONG + 1:
        held("a scroll by hand is kept", f"scroll_to {HAND} then the wheel: scroll_y {hand}; a row and an activity "
             f"came ({rows} rows): scroll_y {after}")
    else:
        failures.append(f"  ✗ scroll by hand              scroll_y {hand} by hand, {after} after a row and an "
                        f"activity ({rows} rows)")

    # --- `up` puts the cursor in sight -------------------------------------------------------------------------
    cursor, top, height = said.get("up") or [None, 0, 0]
    if cursor == T.LONG - 1 and top <= cursor < top + height:
        held("up puts the cursor in sight", f"the cursor on row {cursor}, scroll_y {top}, {height} lines in sight")
    else:
        failures.append(f"  ✗ up                          cursor={cursor} scroll_y={top} height={height}")

    # --- at the end, a row added is followed ---------------------------------------------------------------------
    end = said.get("end") or [None, 0, None, None, 0]
    cursor, rows, top, bottom, height = said.get("followed") or [None, 0, None, None, 0]
    if (end[0] == end[1] - 1 == T.LONG and end[2] == end[3] and end[4] == 1
            and cursor == rows - 1 == T.LONG + 1 and top == bottom and top <= cursor < top + height):
        held("at the end, a row added is followed", f"end: cursor {end[0]}, scroll_y {end[2]} of {end[3]}; a row "
             f"added: cursor {cursor}, scroll_y {top} of {bottom}")
    else:
        failures.append(f"  ✗ follow the end              end={end} followed={said.get('followed')}")
    return 0
