"""hover -- the GLYPH of a frame that expands under the mouse, one mechanism for every tab that has such frames: the
glyph last in a frame's title (`palette.expandable`) takes the look `palette.HOVER` while the mouse stands on it, and
gives it back once the mouse leaves it -- the Tasks tab's frames, the Teams tab's summary of the season and its
dashboard.

A pane takes it by `GlyphHover`: it writes each title by `entitle`, which measures the label as it writes it, says
its frames by key with the cells of their labels (`glyph_frames`), and draws their titles again (`_titled`), reading
`_hovered`, the key of the frame whose glyph is under the mouse."""
from __future__ import annotations

from textual.content import Content
from textual.events import Leave, MouseMove
from textual.widget import Widget


def cells_of(label: str) -> int:
    """-> the cells a title's markup draws -- the label as written, its escaped brackets (`\\[USD]`) one cell each."""
    return Content.from_markup(label).cell_length


def on_glyph(frame: Widget, label: int, x: int, y: int) -> bool:
    """-> whether the screen cell (x, y) is the glyph last in the title of `frame`, shown, its label `label` cells
    long: its top edge, past the corner and the line -- and the blank a corner sets before the label --, the label's
    last cell; never on a label cut short, nor on a frame without a label."""
    if not frame.display or label <= 0:
        return False
    region = frame.region
    corner = frame.styles.border_left[0] not in ("", "none", "hidden")
    if y != region.y or label > region.width - 2 - 4 * corner:
        return False
    return x == region.x + 1 + 2 * corner + label - 1


class GlyphHover:
    """The hover of the glyphs of a pane's frames: the mouse moved in the pane lights the glyph it stands on and puts
    out the one it left; the mouse gone from the pane, or from the frame whose glyph shines, puts it out."""

    _hovered: str | None = None          # the key of the frame whose glyph is under the mouse
    _cells: dict[str, int] | None = None   # the cells of each label written by `entitle`, by key

    def glyph_frames(self) -> dict[str, tuple[Widget, int]]:
        """-> the frames whose title ends on a glyph, by key, each with the cells of its label (`cells`)."""
        raise NotImplementedError

    def entitle(self, key: str, frame: Widget, label: str) -> None:
        """Writes `label` as the title of the frame `key`, its cells measured as written -- the markup Textual gives
        back loses the escapes of its brackets."""
        if self._cells is None:
            self._cells = {}
        self._cells[key] = cells_of(label)
        frame.border_title = label

    def cells(self, key: str) -> int:
        """-> the cells of the label `entitle` wrote last on the frame `key`; 0 before any."""
        return (self._cells or {}).get(key, 0)

    def _titled(self) -> None:
        """Draws the titles of the frames again, the glyph of `_hovered` in the look `palette.HOVER`."""
        raise NotImplementedError

    def glyph_under(self, x: int, y: int) -> str | None:
        """-> the key of the frame whose glyph is the screen cell (x, y); None elsewhere."""
        return next((key for key, (frame, label) in self.glyph_frames().items() if on_glyph(frame, label, x, y)), None)

    def _hover(self, key: str | None) -> None:
        """The glyph of the frame `key` under the mouse -- None: no glyph --, the titles drawn again when it changes."""
        if key != self._hovered:
            self._hovered = key
            self._titled()

    def on_mouse_move(self, event: MouseMove) -> None:
        self._hover(self.glyph_under(event.screen_x, event.screen_y))

    def on_leave(self, event: Leave) -> None:
        if event.node is self or (self._hovered is not None
                                  and event.node is self.glyph_frames().get(self._hovered, (None, 0))[0]):
            self._hover(None)
