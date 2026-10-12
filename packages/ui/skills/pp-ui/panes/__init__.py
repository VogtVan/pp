"""panes -- one widget per pane of the post: `dialogue.py` the conversations, `agents.py` the
agents and their runs, `teams.py` the teams; `overlays.py` and `transcript.py` what they share."""
from __future__ import annotations

from textual.widget import Widget


def live(widget: Widget) -> bool:
    """-> whether `widget` may still be written: in the post's DOM while the post runs -- false from the
    moment the post leaves, when its widgets are pruned while the last events and reads still arrive."""
    return widget.is_attached and widget.app.is_running
