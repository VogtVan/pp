"""sequence_body -- the BODY of a sequence, virtualised: rows of `panes.virtual_rows.VirtualRows`, one row of a
`Sequence` per line of the view, drawn by `palette.sequence_row`. The component keeps each row drawn by its index
and never draws a row out of the view: the view of 50 lines over 425 rows draws 50 of them, and a scroll draws the
rows it uncovers alone.

`show` draws nothing: it keeps its input and asks a refresh, so that N `show` in one frame of the terminal give
one layout and one draw, and a `show` that changes nothing refreshes nothing. At the render, the frame
(`palette.sequence_frame`: the gutter, the step, the x of the columns, the gaps) is laid once when the input
changed (`lay`), and the size told is the width of the longest line by the number of rows. The rows kept are all
dropped when the frame changes -- the width, the columns, the gutter or the step --; otherwise the rows changed in
value, the rows added, and the old and the new row of the cursor are. `drawn` counts the rows drawn since the
mount, `framed` the layouts computed: what a scenario measures.

The body follows its end only when the view that holds it says so (`follows`), and gives no text to a selection.
The module knows neither the head of the sequence, nor the cursor's row brought in sight, nor the click: the view
that holds it (`panes.sequence`) does."""
from __future__ import annotations

from rich.cells import cell_len
from textual.geometry import Size
from textual.strip import Strip

import palette
from model.teams import Sequence
from palette import SequenceFrame
from panes.virtual_rows import VirtualRows


class SequenceBody(VirtualRows, can_focus=False):
    """The rows of a sequence, one per line, drawn on demand and kept by index."""

    def __init__(self, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(id=id, classes=classes)
        self.follows = False           # the view that holds the body says when it follows its end
        self.frame: SequenceFrame | None = None
        self.framed = 0                # the layouts computed
        self._asked: tuple = (Sequence(), 0, None, {})   # the input of the last `show`: what the render lays out
        self._laid: tuple = self._asked                   # the input the frame and the rows kept stand on

    def show(self, sequence: Sequence, width: int, cursor: int | None = None, activities: dict | None = None) -> None:
        """The input kept and a refresh asked; nothing drawn, nothing laid out. An input equal to the last changes
        nothing."""
        asked = (sequence, width, cursor, dict(activities or {}))
        if asked == self._asked:
            return
        self._asked = asked
        self.refresh()

    def lay(self) -> Size | None:
        """The frame laid when the input changed since the last render, the rows kept trimmed with it: -> the size
        of the rows, None when the input stands."""
        if self._asked is self._laid:
            return None
        before, (sequence, width, cursor, activities) = self._laid, self._asked
        frame = palette.sequence_frame(sequence, width, activities)
        self.framed += 1
        if self.frame is None or frame != self.frame:
            self.forget()
        else:
            old, old_cursor, scales = before[0], before[2], self.frame.scales
            self.forget(lambda index: index < len(sequence.rows) and index < len(old.rows)
                        and sequence.rows[index] == old.rows[index] and frame.scales[index] == scales[index]
                        and index != cursor and index != old_cursor)
        self.frame, self._laid = frame, self._asked
        rows = sequence.rows
        widest = max((cell_len(palette.row_note(row)[:frame.note]) for row in rows), default=0)
        return Size(frame.grid + 2 + widest if rows else 0, len(rows))

    def row_strip(self, row: int, lit: tuple[int, int] | None) -> Strip | None:
        """-> the row at `row`, drawn whole on the frame laid."""
        sequence, _, cursor, _ = self._laid
        if self.frame is None or row >= len(sequence.rows):
            return None
        return Strip(list(palette.sequence_row(sequence, self.frame, row, cursor).render(self.app.console))).simplify()
