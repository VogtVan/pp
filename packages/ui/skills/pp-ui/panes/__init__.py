"""panes -- one widget per pane of the post: `dialogue.py` the conversations, `agents.py` the
agents and their runs, `teams.py` the teams; `overlays.py` and `transcript.py` what they share."""
from __future__ import annotations

from typing import Awaitable

from textual.widget import Widget
from textual.widgets import DataTable


def live(widget: Widget) -> bool:
    """-> whether `widget` may still be written: in the post's DOM while the post runs -- false from the
    moment the post leaves, when its widgets are pruned while the last events and reads still arrive."""
    return widget.is_attached and widget.app.is_running


async def guarded(pane: Widget, reading: Awaitable, what: str) -> None:
    """A reading of a pane played under its GUARD: what it raises goes to the remedy line through the pane's
    `Refused` -- `<what>: <the error>` --, never further; the post stands and the next reading comes as before."""
    try:
        await reading
    except Exception as error:         # noqa: BLE001 -- the guard of a reading: anything it raises stops here
        if live(pane):
            pane.post_message(pane.Refused(f"{what}: {type(error).__name__} {error}".rstrip()))


def table(**kw) -> DataTable:
    """-> a table of the post, the ONE way one is made: a row cursor unless said, and under the cursor each cell keeps
    its own colour -- a state said in red stays red there --, the cursor keeping the theme's background."""
    kw.setdefault("cursor_type", "row")
    return DataTable(cursor_foreground_priority="renderable", **kw)
