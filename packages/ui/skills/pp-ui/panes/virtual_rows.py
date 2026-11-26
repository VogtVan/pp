"""virtual_rows -- ROWS drawn on demand: `VirtualRows`, a `ScrollView` over rows a view lays out and draws one by
one, the rows out of sight never drawn. The component holds what such a view does whatever its rows are; the view
says its rows.

The LAYOUT is the view's (`lay`): the component asks for it before the rows are drawn and whenever the view calls
`_settle` -- a view that lays its rows as its data arrives calls it then --, tells the virtual size, and holds the
view where it stands. The STRIPS are kept by row, as the view draws them (`row_strip`): whole, uncropped, without
the widget's base style -- `render_line` lays that style under the strip and crops it at the horizontal scroll, so a
strip kept outlives a scroll and a change of the base style; `forget` drops the strips a layout moved; `drawn`
counts the rows drawn since the mount.

The END is FOLLOWED by a state (`_following`): true from the mount and whenever a scroll of the reader reaches
the end or goes to it, false when one leaves it. Every scroll is the reader's -- the wheel, the scrollbar, the
keys, a scroll under way toward its target -- but the one the component plays itself (`_hold`, under `_own`): after
each layout and at each resize it brings the view to its rest (`rest`): the end while the view follows it and
`follows` allows it, nowhere otherwise -- a view whose rows move above it says its own rest. A layout laid while
the rows are drawn is held after the refresh: no scroll is played under a row's draw.

A SELECTION reads the rows of a view that gives their text (`SELECTS`, `row_text`). The component reads the two
ends of a drag as places of the rows -- the place Textual read in the row drawn, or its own where Textual reads
none or reads the view's cells: the margin, the border, the scrollbar, a pointer out of the view (`_spot`) --, and
the open ends of a selection the mouse makes from another widget as the edges of the rows in view. What the view
holds of a place while its rows move is the view's (`anchored`), and so is the selection laid on the rows of the
moment (`laid`); one cut of a row (`_cut`) says the characters lit and the characters copied, row by row.

The contract of a view: `lay`, `row_strip`; `rest` and `scrolled` when its rows move above it; `SELECTS`,
`row_text`, `anchored` and `laid` when a selection reads it."""
from __future__ import annotations

from typing import Callable

from rich.style import Style as RichStyle
from textual import events
from textual.geometry import Offset, Size
from textual.scroll_view import ScrollView
from textual.selection import Selection
from textual.strip import Strip
from textual.style import Style


class VirtualRows(ScrollView):
    """Rows laid out by the view and drawn on demand: their strips kept, the end followed, a selection read."""

    SELECTS = False                              # whether a selection reads the rows: the view gives their text

    def __init__(self, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(id=id, classes=classes)
        self.drawn = 0                           # the rows drawn since the mount
        self.follows = True                      # whether the view holds its end while it stands there
        self._strips: dict[int, Strip] = {}      # by row, the strip drawn -- whole, without the base style
        self._following = True                   # whether the view stands at its end by the reader's scroll
        self._own = False                        # whether the scroll under way is the component's own (`_hold`)
        self._ends: tuple | None = None          # the selection's ends as the view holds them (start, end, a drag's)
        self._taken: Selection | None = None     # the selection the ends were taken from
        self._pressed = None                     # the start of the drag the ends belong to, Textual's own
        self._grip = None                        # what the view holds of that drag's start, taken at its first
        self._down: tuple | None = None          # the last press of the mouse: its cell of the screen, the scroll then

    # ---------- what the view says ----------
    def lay(self) -> Size | None:
        """The view's layout, laid again when what it shows changed: -> the size of its rows -- the width of the
        widest, their number -- when it laid them anew, None when nothing moved. The view drops there the strips
        the layout moved (`forget`)."""
        raise NotImplementedError

    def row_strip(self, row: int, lit: tuple[int, int] | None) -> Strip | None:
        """-> the strip of a row: whole, uncropped, without the widget's base style, its segments carrying the
        offsets a selection reads when the view has one; `lit`: the characters a selection takes, drawn in its
        look; None when the view draws no such row."""
        raise NotImplementedError

    def row_text(self, row: int) -> str | None:
        """-> the text of a row a selection reads, None for a row it leaves out."""
        return None

    def anchored(self, place: Offset, under: bool = False):
        """-> what the view holds of a place of its rows -- the row `place.y`, the character `place.x` --, to find
        it again once the rows moved; `under`: the place is the character under the pointer. None for no place."""
        raise NotImplementedError

    def laid(self) -> Selection | None:
        """-> the selection as the rows of the moment lay the ends held (`_ends`), its two ends said; None when
        nothing is selected."""
        raise NotImplementedError

    def rest(self) -> int | None:
        """-> the row the top of the view rests on once its rows are laid or its height changed: the end while the
        view follows it, None to stay where it stands."""
        return self.max_scroll_y if self.follows and self._following else None

    def scrolled(self) -> None:
        """The reader scrolled the view: what a view holds of where it stands is taken here."""

    # ---------- the layout, the strips ----------
    def forget(self, keep: Callable[[int], bool] | None = None) -> None:
        """The strips kept dropped -- all of them, or those of the rows `keep` does not keep."""
        if keep is None:
            self._strips.clear()
        else:
            self._strips = {row: strip for row, strip in self._strips.items() if keep(row)}

    def _settle(self, drawing: bool = False) -> None:
        """The view's layout laid when it moved, the virtual size told, then the view held where it stands (`_hold`)
        -- after the refresh when the layout is laid while the rows are drawn (`drawing`): no scroll is played
        under a row's draw."""
        size = self.lay()
        if size is None:
            return
        if size != self.virtual_size:
            self.virtual_size = size
        if drawing:
            self.call_after_refresh(self._hold)
        else:
            self._hold()

    def render_lines(self, crop):
        self._settle(True)
        return super().render_lines(crop)

    def render_line(self, y: int) -> Strip:
        """The row at `y + scroll_offset.y`, drawn once and kept until a layout moves it, the base style laid under
        it, cropped at `scroll_offset.x` to the width of the view; a row a selection takes characters of is drawn
        anew, lit; blank past the rows and under the horizontal scrollbar."""
        self._settle(True)
        scroll_x, scroll_y = self.scroll_offset
        base, width = self.rich_style, self.size.width
        row = y + scroll_y
        if y >= self.scrollable_content_region.height or not 0 <= row < self.virtual_size.height:
            return Strip.blank(width, base)
        lit = self._span(row)
        strip = self._strips.get(row) if lit is None else None
        if strip is None:
            strip = self.row_strip(row, lit)
            if strip is None:
                return Strip.blank(width, base)
            self.drawn += 1
            if lit is None:
                self._strips[row] = strip
        return strip.apply_style(base).crop_extend(scroll_x, scroll_x + width, base)

    # ---------- the end followed ----------
    def _hold(self) -> None:
        """The view brought to its rest (`rest`), once its rows are laid or its height changed. The one scroll the
        component plays itself: `watch_scroll_y` reads no gesture of the reader in it."""
        if not self.is_attached:
            return
        target = self.rest()
        if target is not None and target != self.scroll_offset.y:
            self._own = True
            try:
                self.scroll_to(y=target, animate=False, force=True)
            finally:
                self._own = False

    def on_resize(self) -> None:
        """The view resized -- its own size, or a neighbour's that takes rows from it: held where it stands."""
        self._hold()

    def watch_scroll_y(self, old_value: float, new_value: float) -> None:
        """The view scrolled. A scroll the component does not play itself is the reader's: the view follows its
        end when that scroll reaches it or goes to it -- the target of a scroll under way counts."""
        super().watch_scroll_y(old_value, new_value)
        if not self._own:
            self._following = max(new_value, self.scroll_target_y) >= self.max_scroll_y
            self.scrolled()

    # ---------- the selection ----------
    def _span(self, row: int) -> tuple[int, int] | None:
        """-> the characters of a row the selection takes, None for a row it takes nothing of."""
        if not self.SELECTS or self._ends is None:
            return None
        selection = self.laid()
        text = self.row_text(row) if selection is not None else None
        return self._cut(selection, row, len(text)) if text is not None else None

    @staticmethod
    def _cut(laid: Selection, row: int, length: int) -> tuple[int, int] | None:
        """-> the characters of the row `row`, `length` long, a selection laid takes -- what is lit and what is
        copied, both read here: from its start on its first row, to its end on its last, never past the row's
        text; None for a row out of it or a row it takes nothing of."""
        if not laid.start.y <= row <= laid.end.y:
            return None
        start = min(laid.start.x, length) if row == laid.start.y else 0
        end = min(laid.end.x, length) if row == laid.end.y else length
        return (start, end) if start < end else None

    def selected_look(self, under: RichStyle) -> RichStyle:
        """-> the look of selected cells over `under`, built as Textual builds it (`Style.from_styles` of
        `screen--selection`): its background laid over the row's, the text in its own colour when the selection's
        foreground is transparent."""
        chosen = Style.from_styles(self.screen.get_component_styles("screen--selection"))
        laid = (Style.from_rich_style(under) + chosen).rich_style
        clear = chosen.foreground is None or chosen.foreground.a == 0
        return RichStyle(color=None if clear else laid.color, bgcolor=laid.bgcolor, bold=chosen.bold,
                         italic=chosen.italic, underline=chosen.underline, reverse=chosen.reverse)

    def get_selection(self, selection: Selection) -> tuple[str, str] | None:
        """-> the text under the view's selection, read from the ends held on the layout of the moment: each row
        from its first to its last, cut as `render_line` lights it; a row without text left out."""
        if not self.SELECTS:
            return None
        self._settle()
        laid = self.laid()
        if laid is None:
            return None
        taken = []
        for row in range(laid.start.y, laid.end.y + 1):
            text = self.row_text(row)
            if text is not None:
                start, end = self._cut(laid, row, len(text)) or (0, 0)
                taken.append(text[start:end])
        return "\n".join(taken), "\n"

    def selection_updated(self, selection: Selection | None) -> None:
        """A selection made -- the mouse, `ctrl+a` --: its ends taken on the rows of this instant, as the view holds
        them (`anchored`). A drag pressed in the view keeps what it holds of its start, taken at its first
        selection; the end that follows the pointer is taken anew at each; a drag is new when Textual holds another
        start (the mouse pressed again). Both are places the component reads (`_spot`): the selection ends under the
        pointer, on the edge of the rows in view when the pointer left them. An open end is the edge of the rows in
        view while the mouse selects from another widget, else the first or the last character of the rows as laid
        now: the selection never grows over a text not chosen."""
        if not self.SELECTS:
            return
        self.refresh()
        if selection is None:
            self._ends = self._taken = self._grip = None
            return
        self._settle()
        screen = self.screen
        state = screen._select_state
        held = screen._selecting and state is not None and state.end is not None    # the mouse is selecting
        drag = held and state.start.content_widget is self and state.start.content_offset is not None
        if not drag and selection == self._taken and self._ends is not None:
            return
        self._taken = selection
        scroll = self.scroll_offset.y
        if drag:
            start = state.start
            if start is not self._pressed or self._grip is None:
                cell = start.container_initial_offset + start.container_pointer_delta
                then = self._down[1] if self._down is not None and self._down[0] == cell else scroll
                self._pressed, self._grip = start, self.anchored(self._spot(cell, start.content_offset, then), True)
            read = state.end.content_offset if state.end.content_widget is self else None
            ends = (self._grip, self.anchored(self._spot(state.screen_offset, read, scroll), True), True)
        elif held and (selection.start is None or selection.end is None):
            region = self.scrollable_content_region
            first = self._spot(Offset(region.x, region.y - 1), None, scroll) if selection.start is None \
                else self._spot(state.screen_offset, selection.start, scroll)
            last = self._spot(Offset(region.x, region.bottom), None, scroll) if selection.end is None \
                else self._spot(state.screen_offset, selection.end, scroll)
            ends = (self.anchored(first), self.anchored(last), False)
        else:
            ends = (self.anchored(selection.start or Offset(0, 0)),
                    self.anchored(Offset(0, self.virtual_size.height) if selection.end is None else selection.end),
                    False)
        self._ends = ends if ends[0] is not None and ends[1] is not None else None

    def on_mouse_down(self, event: events.MouseDown) -> None:
        """A press of the mouse: its cell of the screen and the scroll of that instant kept, for the drag it may
        start on the margin or the border."""
        self._down = (event.screen_offset, self.scroll_offset.y)

    def _spot(self, cell: Offset, read: Offset | None, scroll: int) -> Offset:
        """-> the place of the rows under a cell of the screen, the view scrolled by `scroll` rows: the place
        Textual read in the row drawn there (`read`) when the cell is in the rows in view; else the component's own
        -- Textual reads the cells of the margin and of the border in the view's rows, not the content's, and none
        on the scrollbar or out of the view: the start of the row for a cell before it, its end for a cell after it,
        the start of the first row in view for a cell above them, the end of the last for a cell below."""
        region, rows = self.scrollable_content_region, self.virtual_size.height
        if read is not None and region.contains_point(cell):
            return read
        if not rows:
            return Offset(0, 0)
        first, last = min(scroll, rows - 1), min(scroll + region.height, rows) - 1
        row = scroll + cell.y - region.y
        if row < first:
            return Offset(0, first)
        if row > last:
            return Offset(len(self.row_text(last) or ""), last)
        return Offset(0 if cell.x < region.x else len(self.row_text(row) or ""), row)
