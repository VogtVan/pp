"""sequence -- the SEQUENCE of a task: its exchanges between its participants, one column each, drawn live -- the
one component the Tasks tab shows under a task and the Teams tab under a member, centred on that member there.

`SequenceView` draws a `Sequence` (`model.teams.sequence_of`) with `palette.sequence_text`, in two widgets: the
HEAD -- the names of the columns, the context of each member's wake-up beside its name, the pile of procs each
plays now in blue, what each does now (a call of a tool, a thought, its words: `model.teams.Activity`) in cyan,
the lifelines -- stays in sight; the BODY -- one row per post, wake-up and mark, its text on the right -- scrolls
in both directions when it is wider or taller than the view, and the head follows its horizontal scroll (`left`
`right` slide it). A CURSOR of rows, the row under it said below the drawing, `enter` opening its text whole in an
overlay, rendered as markdown, `w` leaving the wake-ups out or bringing them back; a CLICK on a row puts the cursor
on it, and opens its text when it lands on the text column. A row added keeps the cursor where it stood, unless it
stood on the last row: it follows the last then.

`TaskStrip` is the band of a member's tasks the Teams tab shows above that member's sequence: three lines whatever
their number -- as many tasks as the width holds, in the order of their birth, the oldest on the left, those hidden
on each side counted --, a cursor the arrows move (`left` `right`, `<` `>` a page, `j` the next open task, `home`
`end`), the task under it said below; the task under the cursor is the task the sequence draws, and the one each
member of each team had stays its own while the tab lives.

`Threads` keeps the threads a pane draws, by `(team, task)`: a thread is read by `team log <name> --json --task
<task>` the first time it is asked, then fed by what the team's ONE watch says that names the task -- an end of a
wake-up, which the watch says without a task, reads the thread again, which places each event by its `id`. While
the history is on its way, the sequence of a thread is what the watch said of the task so far, so that the band
draws before `team log` returns; `early` counts, by thread, the rows drawn before its history came."""
from __future__ import annotations

from dataclasses import replace
from typing import Callable

from rich.text import Text
from textual.binding import Binding
from textual.containers import ScrollableContainer, Vertical
from textual.events import Click
from textual.message import Message
from textual.widget import Widget
from textual.geometry import Region
from textual.widgets import Static

import palette
from faces import team as faces
from model.teams import WAKE_ENDS, Sequence, Thread, sequence_of
from panes import live
from panes.agents import said_of
from panes.overlays import EventScreen


SLIDE = 4                   # the cells `left` and `right` slide the body of a sequence by


class SequenceGrid(ScrollableContainer):
    """The body of a sequence: its horizontal scroll is told to the view, so that the head follows it."""

    def watch_scroll_x(self, old_value: float, new_value: float) -> None:
        super().watch_scroll_x(old_value, new_value)
        if isinstance(self.parent, SequenceView):
            self.parent.head_follows(new_value)


class SequenceView(Vertical, can_focus=True):
    """The sequence of one task, drawn -- its head in sight, its body scrolling --, with its cursor and the row under
    it said."""

    DEFAULT_CSS = """
    SequenceView { height: 1fr; }
    SequenceView > .sequence-head { height: auto; max-height: 4; overflow: hidden hidden; }
    SequenceView > .sequence-grid { height: 1fr; overflow-x: auto; overflow-y: auto; }
    SequenceView .sequence-lines { width: auto; height: auto; text-wrap: nowrap; }
    SequenceView > .sequence-said { height: auto; max-height: 4; margin-top: 1; }
    """
    BINDINGS = [Binding("up", "move(-1)", show=False), Binding("down", "move(1)", show=False),
                Binding("home", "move(-1000000)", show=False), Binding("end", "move(1000000)", show=False),
                Binding("left", "slide(-1)", show=False), Binding("right", "slide(1)", show=False),
                Binding("enter", "whole", show=False), Binding("w", "wakes", show=False)]
    keys = [("sequence:", ""), ("↑↓", "message"), ("←→", "slide"), ("enter", "whole text"), ("w", "wakes"),
            ("esc", "list")]

    def __init__(self, id: str, team: str = "") -> None:
        super().__init__(id=id)
        self.team = team
        self.sequence = Sequence()
        self.activities: dict = {}          # by member: what its wake-up does now (`model.teams.Activity`)
        self.cursor: int | None = None
        self.wakes = True

    def compose(self):
        with Vertical(classes="sequence-head"):
            yield Static("", classes="sequence-lines", markup=False)
        with SequenceGrid(classes="sequence-grid"):
            yield Static("", classes="sequence-lines", markup=False)
        yield Static("", classes="sequence-said", markup=False)

    def on_mount(self) -> None:
        self.query_one(".sequence-grid").can_focus = False
        self.query_one(".sequence-head").can_focus = False

    def head_follows(self, x: float) -> None:
        """The head slid to the body's horizontal scroll: its lines offset by as much, its container clipping them."""
        if self.is_attached:
            self.query_one(".sequence-head .sequence-lines", Static).styles.offset = (-round(x), 0)

    @property
    def shown(self) -> list:
        """-> the rows drawn: every row, the wake-ups left out under `w`."""
        return [one for one in self.sequence.rows if self.wakes or one.kind != "wake"]

    def show(self, sequence: Sequence, activities: dict | None = None, team: str = "") -> None:
        """The sequence drawn again: the cursor stays on its row, or follows the last row when it stood there."""
        before = len(self.shown)
        followed = self.cursor is None or self.cursor >= before - 1
        self.sequence, self.activities, self.team = sequence, dict(activities or {}), team or self.team
        rows = len(self.shown)
        self.cursor = (rows - 1 if followed else min(self.cursor, rows - 1)) if rows else None
        self._draw(scroll=followed)

    def clear(self) -> None:
        """Nothing drawn: no task chosen."""
        self.sequence, self.activities, self.cursor = Sequence(), {}, None
        if self.is_attached:
            for one in self.query(".sequence-lines"):
                one.update("")
            self.query_one(".sequence-said", Static).update("")

    def on_resize(self) -> None:
        self._draw()

    def _draw(self, scroll: bool = False) -> None:
        if not self.is_attached:
            return
        head, body = palette.sequence_text(replace(self.sequence, rows=tuple(self.shown)), max(40, self.size.width - 2),
                                           self.cursor, self.activities)
        self.query_one(".sequence-head .sequence-lines", Static).update(head)
        self.query_one(".sequence-grid .sequence-lines", Static).update(body)
        row = self.shown[self.cursor] if self.cursor is not None else None
        self.query_one(".sequence-said", Static).update(palette.sequence_said(row, self.team))
        grid = self.query_one(".sequence-grid", ScrollableContainer)
        if self.cursor is not None:
            self.call_after_refresh(grid.scroll_to_region, Region(0, self.cursor, 1, 1), animate=False)
        elif scroll:
            grid.scroll_end(animate=False)

    def action_slide(self, by: int) -> None:
        """`left` `right`: the body slid `SLIDE` cells, the head with it."""
        self.query_one(".sequence-grid", ScrollableContainer).scroll_relative(x=by * SLIDE, animate=False)

    def action_move(self, by: int) -> None:
        rows = len(self.shown)
        if not rows:
            return
        self.cursor = max(0, min(rows - 1, (self.cursor if self.cursor is not None else rows - 1) + by))
        self._draw()

    def action_wakes(self) -> None:
        row = self.shown[self.cursor] if self.cursor is not None else None
        self.wakes = not self.wakes
        rows = self.shown
        self.cursor = (rows.index(row) if row in rows else len(rows) - 1) if rows else None
        self._draw()

    def action_whole(self) -> None:
        """`enter`: the text of the row under the cursor, whole, rendered as markdown."""
        row = self.shown[self.cursor] if self.cursor is not None else None
        if row is None:
            return
        summary = palette.sequence_said(row, self.team).split("\n")[0]
        self.app.push_screen(EventScreen(summary, lambda: palette.sequence_whole(row), label="message", markdown=True))

    def on_click(self, event: Click) -> None:
        """A click on the body: the cursor on the row under it; on the text column, its text whole. The row and the
        column are read from the screen position and the grid's scroll, whatever widget the click reached."""
        grid = self.query_one(".sequence-grid", ScrollableContainer)
        if not self.shown or event.screen_offset not in grid.content_region:
            return
        x = event.screen_x - grid.content_region.x + round(grid.scroll_x)
        y = event.screen_y - grid.content_region.y + round(grid.scroll_y)
        if y >= len(self.shown):
            return
        event.stop()
        self.focus()
        self.cursor = y
        self._draw()
        gutter, step = palette.sequence_layout(self.sequence, max(40, self.size.width - 2), self.activities)
        if x >= gutter + len(self.sequence.columns) * step + 2:
            self.action_whole()


class TaskStrip(Widget, can_focus=True):
    """The band of a member's tasks: three lines, its cursor on the task the sequence below draws."""

    DEFAULT_CSS = """
    TaskStrip { height: 4; padding: 0 1; }
    """
    BINDINGS = [Binding("left", "move(-1)", show=False), Binding("right", "move(1)", show=False),
                Binding("less_than_sign", "page(-1)", show=False), Binding("greater_than_sign", "page(1)", show=False),
                Binding("home", "move(-1000000)", show=False), Binding("end", "move(1000000)", show=False),
                Binding("j", "next_open", show=False)]
    keys = [("tasks:", ""), ("←→", "task"), ("< >", "page"), ("j", "next open"), ("home end", "first, last"),
            ("tab", "sequence"), ("esc", "members")]

    class Chosen(Message):
        """The task under the cursor changed: the sequence draws it -- None, no task."""

        def __init__(self, task: str | None) -> None:
            super().__init__()
            self.task = task

    def __init__(self, id: str, classes: str = "") -> None:
        super().__init__(id=id, classes=classes)
        self.team: str | None = None
        self.member: str | None = None
        self.tasks: list = []
        self._kept: dict[tuple[str | None, str], str] = {}   # (team, member) -> the task its cursor stood on
        self.at = 0
        self.first = 0
        self.frame = 0

    @property
    def chosen(self):
        """-> the task under the cursor, None without one."""
        return self.tasks[self.at] if self.tasks else None

    def show(self, team: str | None, member: str | None, tasks: list) -> None:
        """The tasks of `member` of `team`, oldest first: the cursor on the task that member's cursor stood on, else
        on the newest open task, else on the newest; the sequence is told when the task under it changed."""
        before = self.chosen.id if self.chosen is not None else None
        kept = self._kept.get((team, member)) if member is not None else None
        self.team, self.member, self.tasks = team, member, list(tasks)
        ids = [one.id for one in self.tasks]
        opened = [index for index, one in enumerate(self.tasks) if one.state == "open"]
        self.at = ids.index(kept) if kept in ids else (opened[-1] if opened else max(0, len(ids) - 1))
        self._keep()
        self.refresh()
        after = self.chosen.id if self.chosen is not None else None
        if after != before:
            self.post_message(self.Chosen(after))

    def _keep(self) -> None:
        if self.member is not None and self.chosen is not None:
            self._kept[(self.team, self.member)] = self.chosen.id

    def _shown(self) -> int:
        return palette.strip_shown(self.tasks, max(20, self.size.width - 2), self.frame)

    def render(self) -> Text:
        shown = self._shown()
        if self.at < self.first:
            self.first = self.at
        elif shown and self.at >= self.first + shown:
            self.first = self.at - shown + 1
        self.first = max(0, min(self.first, max(0, len(self.tasks) - shown)))
        return palette.strip_text(self.member, self.tasks, self.at, self.first, shown, self.frame)

    def spin(self, frame: int) -> None:
        """One frame of the spinner: drawn again when a task of the band is played by a wake-up."""
        self.frame = frame
        if any(one.running for one in self.tasks):
            self.refresh()

    def _go(self, at: int) -> None:
        if not self.tasks:
            return
        at = max(0, min(len(self.tasks) - 1, at))
        if at != self.at:
            self.at = at
            self._keep()
            self.refresh()
            self.post_message(self.Chosen(self.chosen.id))

    def action_move(self, by: int) -> None:
        self._go(self.at + by)

    def action_page(self, by: int) -> None:
        self._go(self.at + by * max(1, self._shown()))

    def action_next_open(self) -> None:
        """`j`: the next open task after the cursor, the first one again past the last."""
        opened = [index for index, one in enumerate(self.tasks) if one.state == "open"]
        if opened:
            self._go(next((one for one in opened if one > self.at), opened[0]))


class Threads:
    """The threads of the tasks a pane draws in sequence, by `(team, task)`: each read once when first asked, then
    fed by the team's watch; `drawn` is called with the key of a thread that moved."""

    def __init__(self, pane, drawn: Callable[[tuple[str, str]], None]) -> None:
        self.pane, self.drawn = pane, drawn
        self.threads: dict[tuple[str, str], Thread] = {}
        self._reading: set[tuple[str, str]] = set()
        self._again: set[tuple[str, str]] = set()
        self._shown: dict[tuple[str, str], int] = {}   # by thread: the rows its sequence held before its history
        self.early: dict[tuple[str, str], int] = {}    # by thread: the rows drawn when its history came

    @property
    def busy(self) -> bool:
        """Whether a thread is being read -- what a render waits for."""
        return bool(self._reading)

    def ask(self, key: tuple[str, str]) -> Thread:
        """-> the thread of a task, its history asked the first time."""
        if key not in self.threads:
            self.threads[key] = Thread(key[1])
            self._read(key)
        return self.threads[key]

    def heard(self, team: str, found: dict) -> None:
        """One object of a team's watch: added to the thread of the task it names; an end of a wake-up said without
        a task reads every thread of the team again."""
        task = found.get("task")
        if isinstance(task, str) and (team, task) in self.threads:
            self.threads[(team, task)].add(found)
            self.drawn((team, task))
        elif str(found.get("event", "")) in WAKE_ENDS and "task" not in found:
            for key in [one for one in self.threads if one[0] == team]:
                self._read(key)

    def _read(self, key: tuple[str, str]) -> None:
        if key in self._reading:
            self._again.add(key)
            return
        self._reading.add(key)
        self.pane.run_worker(self._reading_of(key), group="sequence-read")

    async def _reading_of(self, key: tuple[str, str]) -> None:
        """`team log <name> --json --task <task>`: the history at the first reading, merged by `id` after it."""
        try:
            while True:
                self._again.discard(key)
                found, face = await faces.log(self.pane.house, *key)
                if not live(self.pane):
                    return
                if face.rc != 0:
                    self.pane.post_message(self.pane.Refused(said_of(face)))
                thread = self.threads[key]
                if thread.read:
                    thread.merge(found)
                else:
                    self.early[key] = self._shown.get(key, 0)
                    thread.history(found)
                self.drawn(key)
                if key not in self._again:
                    return
        finally:
            self._reading.discard(key)

    def early_rows(self, key: tuple[str, str]) -> int:
        """-> the rows the band drew of a thread before its history came -- those drawn so far while it is on its
        way --, -1 for a thread never asked."""
        return self.early.get(key, self._shown.get(key, -1 if key not in self.threads else 0))

    def sequence(self, key: tuple[str, str], focus: str | None = None) -> Sequence:
        """-> the sequence of a thread kept, centred on `focus` when given -- of what the watch said of it while its
        history is on its way."""
        thread = self.threads.get(key)
        if thread is None:
            return Sequence()
        if thread.read:
            return sequence_of(thread.lines, focus)
        found = sequence_of(thread.held, focus)
        self._shown[key] = len(found.rows)
        return found
