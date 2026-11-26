"""tasks -- the TASKS tab: WHAT the teams do, the tasks of every team started, as the faces of `team` say them.

A menu on the left -- the filters `SHOW` (`recent` first: the open tasks and those ended within the day; `running`:
the open tasks; `for you`: the tasks with a question or an end the owner has not seen, as the face's `waiting` lists
them; `stopped`, `resolved`; `recurring`: the live recurrences, those the face says no stop of, the nearest next
period first -- one laid shows there before its first occurrence --; `all`: every task), each with the lines
it keeps, and `TEAM` (`all`, then each team started) -- and a centre of horizontal bands: the TASKS the filters keep, the most recently born first, the teams mingled (the name,
else the start of the text; the team, the state, who holds it, the moment it was born; then what `team stats` says of the task: its elapsed time and its effort, its cost in USD, its
launches, its `do` and its `re`, its failed wake-ups, the largest share of the context its wake-ups left), ten at most in sight, then the BAND of the task under the cursor, three zones and no
frame around them -- its SUMMARY unframed, a line per group of fields, never wrapped; its TEXT in markdown in its own
frame `text`, six rows high, four under `TALL`, none without a text; then ONE of two in the frame below, titled by what
it shows: its SEQUENCE (`panes.sequence`), or its RESULT in markdown, whole. A task resolved that no wake-up plays
opens on its result, any other on its sequence; `v` changes one for the other. Under `recurring` the list takes the
columns of a recurrence and its team (`palette.recurring_row_cells`, the rule of the overlay `e`) and the summary says
the recurrence under the cursor whole, the two frames hidden; a gesture of a task there plays nothing and says so on the remedy line. Under ~70 columns the menu folds into one line,
`show: < … > · team: < … >`, which `[` `]` and `{` `}` change -- the screen's breakpoint class, CSS alone.

The tasks are read at the first showing, then by the ROUND of the Teams tab's measure (`ROUND_FLOOR`,
`ROUND_FACTOR`), on `u`, after a gesture, and at each object of a team's watch but a step and `quiet`: `team
status --json`, then one `team status <name> --json` and one `team stats <name> --all --json` per team started --
the readings asked meanwhile make ONE
after the one under way. The tab subscribes, at its first reading, to the ONE watch of each team started
(`faces.team.follow`, shared with the Teams tab): never a watch per task.

A task a wake-up plays -- the face says it `running` -- turns: the spinner before its name, and the tab's title
counts such tasks, `4·Tasks ⠹ 2` (`live`); the app's spinner turns while a turn of the dialogue or a wake-up
runs, and each frame changes the name cells of those lines alone (`spin`).

The RESULT of a task resolved is read once (`team result <name> <task>`) and kept; while it is read, and when the
verb refuses, the band shows the task's sequence. The result scrolls in its frame: `tab` goes there from the tasks,
`escape` comes back.

The SEQUENCE of the task under the cursor is its thread (`team log <name> --json --task <id>`), read once the cursor
has rested `REST` seconds on the task -- what the watch said of it meanwhile drawn first --, then fed by its team's
watch; under the name of each member, its ACTIVITY on the task (`model.teams.Activity`: the pile of procs of the last
step its wake-up said, in blue, what it does now -- a call of a tool, a thought, its words -- in cyan, the context of
its run beside its name) -- none once an end of that wake-up comes. A step or an activity names its member, its task
and its run (`agent`, `task`, `run`) -- the face says them: the tab never ties one to a task.
`tab` goes into the sequence, where `up` and `down` move its cursor, `enter` opens the row's text whole, `w` leaves
the wake-ups out; `escape` comes back to the tasks.

`enter` on a task opens its THREAD in an overlay, live: its history (`team log <name> --json --task <id>`),
then what its team's watch says that names the task (`task`), an `id` shown once; an end of a wake-up the watch
says without a task reads the history again, which places it by `id` -- as does the first object the overlay
hears, so that nothing written while it opened is lost. `escape` closes it.

The tab plays the gestures of a task, each written in an overlay: `m` writes on the task under the cursor -- `to`,
`as`, `reply to` read from `team status --json`, then the text, the exact command under them --; `r` resumes it --
a message and `as` --; `n` gives a team a new task -- the team, its name, `to`, `as`, its message --; `s`, `k` (the
task's name typed); `l` the journal of the task's team, `b` its owner's inbox (as the Teams tab shows it), `v` its
result, `e` the recurrences of its team -- `x` stops one, `m` changes its period, its text or its context limit, `p`
makes a task given once come back. An occurrence of a recurrence
is marked `↻` beside its id. Every gesture is a verb of `team`, never shown, its refusal on the remedy line as the verb
said it, what it did said on the status line, the tasks read again after it. A new task played from the tab is FOLLOWED: the next reading puts the cursor
on the task its team says that it did not say before, `SHOW` turned to `recent` when the filter in place hides it; a
recurrence laid from the tab (`--every`) the same way, `SHOW` turned to `recurring`. The tab computes no state of a task: a column or a filter reads a field
of the face, counted or cut, never deduced from the journal.

Four frames EXPAND -- the sequence, the text, the result and the list of the tasks --: a glyph last in the title of
each (`palette.EXPAND`) expands it at a click, the sequence and the list over the whole centre, the text and the result
over the whole place under the list -- the menu of the filters stays beside them, shown and played: a filter changed
reads the list expanded again --; the glyph turns to `palette.COLLAPSE`, and the same click folds the frame back. One
frame at a time, by ONE mechanic: the class `expanded` on the frame and on the pane -- `over-centre` or `under-list` beside it
on the pane, the place the frame takes --, the other bands of the centre hidden by the post's CSS alone
(`app.LAYOUT_CSS`, which outranks the pane's own); a frame expanded that the task under the cursor no longer shows
folds back. The glyph under the mouse takes the look `palette.HOVER`, and gives it back once the mouse leaves it -- the
hover every tab shares (`panes.hover`)."""
from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime
from typing import Awaitable, Callable

from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.events import Click
from textual.message import Message
from textual.widgets import DataTable, Static

from rich.text import Text
from textual.binding import Binding

import palette
import panes
from faces import play_gesture
from faces import team as faces
from model import PaneSpec, gestures
from model.task_stats import TaskStats, stats_of
from model.teams import (COST_BASES, COST_COLUMN, ALL, EVERY_TASK, RECURRING, RECURRING_COLUMNS, SHOWS, TASK_COLUMNS, Activity, RecurringRow,
                         TaskRow, TeamBadge, TeamState, Thread, ThreadLine, counted, filtered, is_activity, kept,
                         newcomer, recurrence_newcomer, recurring_of, rows_of)
from panes import live
from panes.agents import said_of
from panes.hover import GlyphHover
from panes.sequence import SequenceView, Threads
from panes.overlays import ConfirmScreen, Field, GestureScreen, Overlay, RecurrencesScreen
from panes.teams import (ROUND_FACTOR, ROUND_FLOOR, ask_new_task, inbox_of, journal_of, member_options, result_of,
                         senders_of, write_on)
from panes.transcript import MarkdownText

EVERY_MEMBER = "all"                 # whom `team resume --to` tells when it tells every member of the season

READ, FOLLOW, GESTURE, RESULT = "tasks-read", "tasks-follow", "tasks-gesture", "tasks-result"
ENDS = ("wake-ended", "wake-failed", "wake-killed")   # the events that end a wake-up
REST = 0.3                     # seconds the cursor rests on a task before its thread is read
LISTED = 10                    # the rows of tasks the list shows at most
EXPANDS = {"sequence": "over-centre", "text": "under-list", "result": "under-list",   # the frames that expand: where
           "list": "over-centre"}


class TasksPane(GlyphHover, Vertical):
    """The Tasks tab: the folded menu, then the filters beside the centre -- the tasks, the band of the one chosen."""

    DEFAULT_CSS = """
    TasksPane { height: 1fr; }
    TasksPane .fold { display: none; height: 1; padding: 0 1; }
    #tasks-row { height: 1fr; }
    #tasks-show { height: auto; }
    #tasks-team { height: 1fr; }
    #tasks-centre { width: 1fr; height: 1fr; padding-left: 1; }
    #tasks-list { height: auto; max-height: 12; }   /* its header and ten tasks under its line: `_fit_list` */
    #tasks-detail { height: auto; padding: 0 1; text-wrap: nowrap; text-overflow: ellipsis; }
    #tasks-detail.whole { text-wrap: wrap; }
    #tasks-text { height: 7; padding: 0 1; }        /* six rows under its line; framed whole or short: app.py */
    #tasks-text-body { height: auto; }
    #tasks-sequence { height: 1fr; min-height: 6; padding: 0 1; }
    #tasks-result { height: 1fr; padding: 0 1; }
    #tasks-result-text { height: auto; }
    TasksPane .absent { display: none !important; }            /* a zone of the band with nothing to show */
    """
    BINDINGS = [Binding("escape", "back", show=False)]

    class Read(Message):
        """The tasks were read: their line for the status."""

        def __init__(self, bar: str) -> None:
            super().__init__()
            self.bar = bar

    class Refused(Message):
        """A verb the tab played refused: what it said, for the remedy line."""

        def __init__(self, said: str) -> None:
            super().__init__()
            self.said = said

    class Played(Message):
        """A gesture played: its argv, and what it did in words for the status line."""

        def __init__(self, argv: list[str]) -> None:
            super().__init__()
            self.argv, self.said = list(argv), gestures.summary(argv)

    def __init__(self, spec: PaneSpec, house: str) -> None:
        super().__init__(id=f"pane-{spec.key}")
        self.spec, self.house = spec, house
        self.states: dict[str, TeamState] = {}   # the teams started, as `status <name> --json` says them
        self.stats: dict[tuple[str, str], TaskStats] = {}   # each task's by (team, task), as `team stats` says it
        self.rows: list[TaskRow] = []            # the tasks the filters keep, in the table's order
        self.recurring: list[RecurringRow] = []  # under `recurring`: the live recurrences `TEAM` keeps, in that order
        self._columns = TASK_COLUMNS             # the columns the list shows
        self._titles = TASK_COLUMNS              # their titles: a task's cost titled by the base chosen
        self.base = COST_BASES[0]                # the base of the costs, the one the Teams tab's selector chose
        self._keys: list[tuple[str, str]] = []   # the (team, id) of each line of the list, in its order
        self.show, self.team = SHOWS[0], ALL     # the filters
        self._names: dict[str, str] = {}         # each team's identity -> the name the post shows it by
        self._teams: list[str] = []              # the teams started, in the order of the face
        self._shown = False
        self.active = False                      # the tab is the one shown: the tasks take the focus once read
        self._read_once = False
        self._reading = False
        self._dirty = False
        self._read_at = None                   # the instant of the last reading
        self._round = None
        self._seen: dict[str, int] = {}          # the task watch's objects by `team:<event>`, what `--wait` counts
        self._follows: dict[str, faces.Subscription] = {}   # the watch of each team started, subscribed once
        self._activities: dict[tuple[str, str], dict[str, Activity]] = {}   # by (team, task): each member's activity
        self._over: set[tuple[str, str, str]] = set()   # (team, task, member): its wake-up ended after its last object
        self.threads = Threads(self, self._sequence_moved, lambda team: self.states.get(team))
        self._modes: dict[tuple[str, str], str] = {}    # what `v` chose the band shows of a task: `result`, `sequence`
        self._resting = None                     # the timer of the cursor resting on a task
        self.frame = 0                           # the spinner's frame, as the app turns it
        self._thread_screen: "ThreadScreen | None" = None
        self._playing = 0
        self._filling = False                    # the menus are being filled: their highlights are no choice
        self._asked: tuple[str, str] | None = None  # a (team, task) to put the cursor on once read
        self._launched: tuple[str, set[str]] | None = None   # a new task posted: its team, the tasks it said before
        self._laid: tuple[str, set[str]] | None = None       # a recurrence laid: its team, the recurrences it said before
        self._results: dict[tuple[str, str], str | None] = {}   # the result of each task resolved, read once
        self._resulting: set[tuple[str, str]] = set()          # a result being read
        self._expanded: str | None = None                       # the frame expanded: a key of `EXPANDS`
        self._hovered: str | None = None                        # the frame whose glyph is under the mouse
        self._labels = {"text": palette.framed("text"), "sequence": palette.framed("sequence"),   # the label of each
                        "result": palette.framed("result"), "list": palette.framed("Tasks")}      # frame that expands,
                                                                                                    # its glyph aside

    def compose(self):
        yield Static("", id="tasks-fold", classes="fold", markup=False)
        with Horizontal(id="tasks-row"):
            with Vertical(id="tasks-menu", classes="menu"):
                yield panes.table(id="tasks-show", classes="framed", show_header=False)
                yield panes.table(id="tasks-team", classes="framed", show_header=False)
            with Vertical(id="tasks-centre", classes="centre rule-left"):
                yield panes.table(id="tasks-list", classes="framed", zebra_stripes=True, cell_padding=1)
                yield Static("", id="tasks-detail", markup=False)
                with VerticalScroll(id="tasks-text", classes="framed", can_focus=False):   # its wheel, not `tab`
                    yield MarkdownText("", id="tasks-text-body")
                sequence = SequenceView(id="tasks-sequence")
                sequence.add_class("framed")
                yield sequence
                with VerticalScroll(id="tasks-result", classes="framed absent"):
                    yield MarkdownText("", id="tasks-result-text")

    def on_mount(self) -> None:
        self.query_one("#tasks-show", DataTable).add_columns("show", "n")
        self.query_one("#tasks-team", DataTable).add_columns("team")
        table = self.query_one("#tasks-list", DataTable)
        table.add_columns(*TASK_COLUMNS)
        self.watch(table, "show_horizontal_scrollbar", self._fit_list, init=False)
        self._titled()                                     # the frames of the band say what they show

    def on_resize(self) -> None:
        self.call_after_refresh(self._fit_list)            # the frame of the list as the screen's size draws it

    def _fit_list(self, *_) -> None:
        """The list's height: its header and `LISTED` rows of tasks at most, inside its frame -- its horizontal
        scrollbar under them when the columns are wider than the list, never in place of a task."""
        table = self.query_one("#tasks-list", DataTable)
        scrollbar = table.styles.scrollbar_size_horizontal if table.show_horizontal_scrollbar else 0
        table.styles.max_height = (None if self._expanded == "list"          # expanded: the pane's height, its CSS
                                   else table.styles.gutter.height + 1 + LISTED + scrollbar)

    # ---------- the frames that expand ----------
    def expand(self, key: str | None) -> None:
        """The frame `key` expanded over its place -- the other bands hidden by the CSS of `expanded` --; None folds
        back the frame expanded."""
        focused = self.screen.focused
        if (key is not None and focused is not None and focused.id in ("tasks-sequence", "tasks-result")
                and focused.id != f"tasks-{key}"):
            self.query_one("#tasks-list", DataTable).focus()     # the band hidden leaves: the tasks take the keys
        self._expanded = key
        self.set_class(key is not None, "expanded")
        for place in set(EXPANDS.values()):
            self.set_class(EXPANDS.get(key) == place, place)
        for one in EXPANDS:
            self.query_one(f"#tasks-{one}").set_class(one == key, "expanded")
        self._titled()
        self._fit_list()

    def _titled(self) -> None:
        """The title of each frame that expands: its label, then its glyph, as the frame stands."""
        for key, label in self._labels.items():
            self.entitle(key, self.query_one(f"#tasks-{key}"),
                         palette.expandable(label, key == self._expanded, key == self._hovered))

    def glyph_frames(self) -> dict:
        """-> the frames that expand, by key, with the cells of their labels: the glyph of their titles shines under
        the mouse (`GlyphHover`)."""
        return {key: (self.query_one(f"#tasks-{key}"), self.cells(key)) for key in EXPANDS}

    def on_click(self, event: Click) -> None:
        """A click on the glyph of a frame that expands: the frame expanded, or folded back once expanded."""
        key = self.glyph_under(event.screen_x, event.screen_y)
        if key is not None:
            event.stop()
            self.expand(None if self._expanded == key else key)

    # ---------- the readings ----------
    def shown(self) -> None:
        """The tab is shown: the first time, the tasks are read; the focus goes to the tasks."""
        if not self._shown:
            self._shown = True
            self.reread()
        self.focus_table()

    async def settled(self, final: bool = False) -> None:
        """Returns once nothing is being read -- what a render waits for: the tasks, a gesture, a last call, the
        history of a thread opened."""
        while self._shown and (not self._read_once or self._reading or self._playing or self._resting is not None
                               or self.threads.busy or self._resulting
                               or (self._thread_screen is not None and self._thread_screen.reading)):
            await asyncio.sleep(0.01)

    def reread(self) -> None:
        """`u`, the first showing, a gesture played, the Teams tab's team read again: the tasks, read now -- or once
        after the reading under way."""
        if not self._shown:
            return
        if self._reading:
            self._dirty = True
            return
        self._reading = True
        self.run_worker(self._read_loop(), group=READ)

    async def _read_loop(self) -> None:
        try:
            while True:
                self._dirty = False
                await panes.guarded(self, self._read(), "tasks")
                if not self._dirty:
                    return
        finally:
            self._read_once = True
            self._reading = False

    async def _read(self) -> None:
        began = time.monotonic()
        found, face = await faces.badges(self.house)
        if not live(self):
            return
        if face.rc != 0:
            self.post_message(self.Refused(said_of(face)))
        badges = [TeamBadge.read(obj) for obj in found]
        teams = [one.team for one in badges if one.started is not None]
        self._names = {one.team: one.shown for one in badges}
        read = await asyncio.gather(*(faces.state(self.house, name) for name in teams),
                                    *(faces.stats(self.house, name, every=True) for name in teams))
        if not live(self):
            return
        states, said = {}, {}
        for name, (obj, one), (found, face) in zip(teams, read[:len(teams)], read[len(teams):]):
            if one.rc != 0:
                self.post_message(self.Refused(said_of(one)))
            states[name] = TeamState.read(obj or {"team": name, "started": None})
            if face.rc == 0:                           # a refusal of `stats` says no stats, nothing on the remedy line
                said.update({(name, task): line for task, line in stats_of(found).items()})
        self._teams, self.states, self.stats, self._read_at = teams, states, said, datetime.now()
        for name in [one for one in self._follows if one not in teams]:   # a team deleted or never started again
            await self._follows.pop(name).close()
        for name in teams:                             # the ONE watch of each team started, subscribed once
            if name not in self._follows and live(self):
                self._follows[name] = await faces.follow(self.house, name)
                self.run_worker(self._follow(name, self._follows[name]), group=FOLLOW)
        if self.team != ALL and self.team not in teams:
            self.team = ALL
        self._fill()
        self._read_once = True
        if self._round is not None:
            self._round.stop()
        self._round = self.set_timer(max(ROUND_FLOOR, ROUND_FACTOR * (time.monotonic() - began)), self.reread)

    async def close(self) -> None:
        """The subscriptions left, the round stopped -- the post leaves."""
        if self._round is not None:
            self._round.stop()
        for one in list(self._follows.values()):
            await one.close()
        self._follows.clear()

    # ---------- what the teams' watches say ----------
    async def _follow(self, team: str, watch: "faces.Subscription") -> None:
        """The objects of a team's watch, each drawn once: a step or an activity is kept in its member's activity on
        the task it names, the head of its sequence drawn again; an end of a wake-up ends the activity of its member
        and run; each is fed to the threads kept, a row drawn when it adds one; any other object but `quiet` reads the
        tasks again."""
        async for found in watch.events():
            if not live(self):
                return
            event = str(found.get("event", ""))
            self._seen[f"team:{event}"] = self._seen.get(f"team:{event}", 0) + 1
            if ThreadLine.read(found).step or is_activity(found):
                task, member = found.get("task"), found.get("agent")
                if isinstance(task, str) and isinstance(member, str):
                    kept = self._activities.setdefault((team, task), {})
                    kept[member] = Activity.heard(kept.get(member), found)
                    self._over.discard((team, task, member))
                    self._activity_moved((team, task))
                self.threads.heard(team, found)
                continue
            if event in ENDS:
                member = found.get("agent")
                for (named, task), activities in self._activities.items():
                    one = activities.get(member) if named == team and isinstance(member, str) else None
                    if one is not None and one.run == found.get("run"):
                        self._over.add((team, task, member))
            self.threads.heard(team, found)
            if event != "quiet":
                self.reread()

    def saw(self, kind: str) -> int:
        return self._seen.get(kind, 0)

    def counts(self) -> dict[str, int]:
        return dict(self._seen)

    # ---------- what the tab shows ----------
    def _fill(self) -> None:
        """The menus with their counts, the tasks the filters keep -- or the live recurrences, under `recurring`, in
        their own columns --, the band, the folded line, the status."""
        states = [self.states[name] for name in self._teams]
        every, recurring = rows_of(states), recurring_of(states)
        self._follow_launched(every)
        self._follow_laid(recurring)
        current = self._key_under_cursor()               # read on the lines the table still shows
        self.rows = filtered(every, self.show, self.team)
        self.recurring = kept(recurring, self.team) if self.show == RECURRING else []
        numbers = counted(every, recurring, self.team)
        self._filling = True
        try:
            self._menu("tasks-show", [palette.filter_cells(show, numbers[show]) for show in SHOWS], SHOWS.index(self.show))
            teams = [ALL] + self._teams
            self._menu("tasks-team", [palette.filter_cells(self._names.get(one, one)) for one in teams],
                       teams.index(self.team))
            if self.show == RECURRING:
                self._columns_of(RECURRING_COLUMNS)
                keys = [(one.team, one.line.id) for one in self.recurring]
                self._list([palette.recurring_row_cells(one) for one in self.recurring], keys, current)
            else:
                self._columns_of(TASK_COLUMNS, tuple(palette.COST_TITLES[self.base] if one == COST_COLUMN else one
                                                     for one in TASK_COLUMNS))
                keys = [(one.team, one.task.id) for one in self.rows]
                self._list([palette.task_row_cells(one, self.frame, self.stats.get(key), self.base)
                            for one, key in zip(self.rows, keys)], keys, current)
            if self._asked in keys:
                table = self.query_one("#tasks-list", DataTable)
                table.move_cursor(row=keys.index(self._asked))
                self._asked = None
                table.focus()
        finally:
            self._filling = False
        if self.active and self.screen.focused is None and (self.rows or self.recurring):
            self.query_one("#tasks-list", DataTable).focus()
        for key, title in (("tasks-show", "Show"), ("tasks-team", "Team")):
            self.query_one(f"#{key}").border_title = palette.framed(title, self._read_at, dated=key == "tasks-show")
        self.query_one("#tasks-fold", Static).update(
            f"{palette.folded('show', self.show)}{palette.SEP}{palette.folded('team', self._names.get(self.team, self.team))}")
        self._show_band()
        if self.show != RECURRING and self._resting is None and None not in (key := self._picked()) \
                and key not in self.threads.threads:
            self._resting = self.set_timer(REST, self._rested)   # armed here: the highlight that also arms it comes later
        shown, total = ((len(self.recurring), len(recurring)) if self.show == RECURRING else (len(self.rows), len(every)))
        self.post_message(self.Read(palette.tasks_bar(shown, total, self.show, self._names.get(self.team, self.team),
                                                      palette.hhmmss(self._read_at) if self._read_at else "",
                                                      "recurrence(s)" if self.show == RECURRING else "task(s)")))

    def _columns_of(self, columns: tuple, titles: tuple | None = None) -> None:
        """The list's columns: those of a task, or of a recurrence under `recurring`, under their `titles` -- set again
        when either changes."""
        titles = titles or columns
        if columns != self._columns or titles != self._titles:
            table = self.query_one("#tasks-list", DataTable)
            table.clear(columns=True)
            table.add_columns(*titles)
            self._columns, self._titles, self._keys = columns, titles, []

    def set_base(self, base: str) -> None:
        """The base of the costs chosen in the settings: the cost of each task said in it, its column
        titled by it."""
        if base in COST_BASES and base != self.base:
            self.base = base
            if self._shown:
                self._fill()

    def _follow_launched(self, every: list[TaskRow]) -> None:
        """The task a post of the tab gave birth to, once its team says it: the cursor to be put on it, and `SHOW`
        turned to `recent` -- `TEAM` to `all` -- when the filters in place hide it."""
        if self._launched is None:
            return
        team, known = self._launched
        task = newcomer(self.states.get(team), known)
        if task is None:
            return
        self._launched, self._asked = None, (team, task)
        row = next((one for one in every if (one.team, one.task.id) == (team, task)), None)
        if row is not None and row not in filtered(every, self.show, self.team):
            self.show = SHOWS[0]
            if self.team not in (ALL, team):
                self.team = ALL

    def _follow_laid(self, recurring: list[RecurringRow]) -> None:
        """The recurrence a post of the tab laid, once its team says it: the cursor to be put on it, and `SHOW` turned
        to `recurring` -- `TEAM` to `all` -- when the filters in place hide it."""
        if self._laid is None:
            return
        team, known = self._laid
        laid = recurrence_newcomer(self.states.get(team), known)
        if laid is None:
            return
        self._laid, self._asked = None, (team, laid)
        if any((one.team, one.line.id) == (team, laid) for one in recurring):
            self.show = RECURRING
            if self.team not in (ALL, team):
                self.team = ALL

    def _menu(self, key: str, rows: list[tuple], at: int) -> None:
        """A menu's lines: their cells updated in place while the menu keeps its lines -- its cursor is the
        operator's, never moved under keys still coming --, built again with the cursor on `at` otherwise."""
        table = self.query_one(f"#{key}", DataTable)
        if table.row_count != len(rows) or any(str(table.get_cell_at((index, 0))) != str(cells[0])
                                               for index, cells in enumerate(rows)):
            self._rows(key, rows, at)
            return
        for index, cells in enumerate(rows):
            for column, cell in enumerate(cells):
                table.update_cell_at((index, column), cell)

    def _list(self, rows: list[tuple], keys: list[tuple[str, str]], current: tuple[str, str] | None) -> None:
        """The list's lines: their cells updated in place while the list keeps its keys -- nothing moves, neither its
        scroll nor its cursor --; built again otherwise, the line under the cursor followed by its key and kept at the
        same row of the view while it is still there, the cursor on the first line when it is not."""
        table = self.query_one("#tasks-list", DataTable)
        if keys == self._keys and table.row_count == len(rows):
            for index, cells in enumerate(rows):
                for column, cell in enumerate(cells):
                    table.update_cell_at((index, column), cell)
            return
        view = table.cursor_row - round(table.scroll_y)          # the cursor's row in the view, before
        self._keys = keys
        self._rows("tasks-list", rows, 0)
        if current in keys:
            at = keys.index(current)
            table.move_cursor(row=at, scroll=False)
            table.call_after_refresh(table.scroll_to, y=max(0, at - view), animate=False)   # once its height is known

    def _rows(self, key: str, rows: list[tuple], at: int) -> None:
        table = self.query_one(f"#{key}", DataTable)
        table.clear()
        for index, cells in enumerate(rows):
            table.add_row(*cells, key=str(index))
        if rows:
            table.move_cursor(row=max(0, min(at, len(rows) - 1)))

    def _row_under_cursor(self) -> TaskRow | None:
        """-> the task under the cursor; None under `recurring`, whose lines are no task."""
        row = self.query_one("#tasks-list", DataTable).cursor_row
        return self.rows[row] if self._columns == TASK_COLUMNS and 0 <= row < len(self.rows) else None

    def _recurring_under_cursor(self) -> RecurringRow | None:
        """-> the recurrence under the cursor, under `recurring`; None otherwise."""
        row = self.query_one("#tasks-list", DataTable).cursor_row
        return self.recurring[row] if self._columns == RECURRING_COLUMNS and 0 <= row < len(self.recurring) else None

    def _key_under_cursor(self) -> tuple[str, str] | None:
        """-> (team, id) of the line under the cursor -- a task, or a recurrence."""
        task, line = self._row_under_cursor(), self._recurring_under_cursor()
        return (task.team, task.task.id) if task else (line.team, line.line.id) if line else None

    def _show_band(self) -> None:
        """The band of the task under the cursor, three zones under the table and no frame around them: its summary
        (`palette.task_detail`), its text in markdown in its own frame -- none without a text --, then ONE of two in
        the frame below, titled by what it shows: its sequence, or its result in markdown once read -- a task resolved
        that no wake-up plays shows its result unless `v` chose its sequence."""
        if self.show == RECURRING:
            self._show_recurrence()
            return
        row = self._row_under_cursor()
        detail = self.query_one("#tasks-detail", Static)
        detail.remove_class("whole")
        key = (row.team, row.task.id) if row is not None else None
        detail.update(palette.task_detail(row.task, row.team, len(self.asks_of(key))) if row else
                      palette.dim(f"{palette.NONE}  no task {self.show} here"))
        text = self.query_one("#tasks-text")
        _shows(text, bool(row and row.task.text))
        body = self.query_one("#tasks-text-body", MarkdownText)
        if _shown(text) and body.source != row.task.text:
            body.show(row.task.text)
            text.scroll_home(animate=False)                  # another text: read from its top
        resolved = row is not None and row.task.state == "resolved" and not row.task.running
        if resolved and key not in self._results:
            self._ask_result(key)
        source = self._results.get(key) if resolved else None
        shown = source is not None and self._modes.get(key, "result") == "result"
        sequence, result = self.query_one("#tasks-sequence", SequenceView), self.query_one("#tasks-result")
        if self.screen.focused in (sequence, result) and (_shown(sequence), _shown(result)) != (not shown, shown):
            self.query_one("#tasks-list", DataTable).focus()    # what was focused leaves: the tasks take the keys
        _shows(sequence, not shown)
        _shows(result, shown)
        self._fold_absent()
        if shown:
            self.query_one("#tasks-result-text", MarkdownText).show(source)
        elif key is not None and key in self.threads.threads:
            sequence.show(self.threads.sequence(key), self._activities_of(key), row.team, self.asks_of(key))
        else:
            sequence.clear()

    def _show_recurrence(self) -> None:
        """Under `recurring`: the recurrence under the cursor whole in the summary, wrapped -- neither text, nor
        sequence, nor result."""
        line = self._recurring_under_cursor()
        sequence, result = self.query_one("#tasks-sequence", SequenceView), self.query_one("#tasks-result")
        if self.screen.focused in (sequence, result):
            self.query_one("#tasks-list", DataTable).focus()
        for one in (sequence, result, self.query_one("#tasks-text")):
            _shows(one, False)
        self._fold_absent()
        sequence.clear()
        detail = self.query_one("#tasks-detail", Static)
        detail.add_class("whole")
        detail.update(palette.recurrence_detail(line.line, line.label or line.team)
                      if line else palette.dim(f"{palette.NONE}  no recurrence here"))

    def _fold_absent(self) -> None:
        """The frame expanded folds back when the band no longer shows it."""
        if self._expanded is not None and not _shown(self.query_one(f"#tasks-{self._expanded}")):
            self.expand(None)

    def _sequence_moved(self, key: tuple[str, str]) -> None:
        """A thread kept moved: its sequence drawn again when it is the task under the cursor's, shown."""
        sequence = self.query_one("#tasks-sequence", SequenceView) if live(self) else None
        if sequence is not None and _shown(sequence) and key == self._picked():
            sequence.show(self.threads.sequence(key), self._activities_of(key), key[0], self.asks_of(key))

    def _activity_moved(self, key: tuple[str, str]) -> None:
        """What a wake-up does on a task changed: the head of its sequence drawn again when it is the task under the
        cursor's, shown."""
        sequence = self.query_one("#tasks-sequence", SequenceView) if live(self) else None
        if (sequence is not None and _shown(sequence) and key == self._picked()
                and key in self.threads.threads):
            sequence.activity(self._activities_of(key))

    def _activities_of(self, key: tuple[str, str]) -> dict[str, Activity]:
        """-> the activity of each member whose wake-up under way plays the task."""
        return {member: one for member, one in self._activities.get(key, {}).items() if key + (member,) not in self._over}

    def _rested(self) -> None:
        """The cursor rested on a task: its thread asked -- read the first time."""
        self._resting = None
        key = self._picked()
        if key[0] is not None:
            self.threads.ask(key)
            self._show_band()

    def _ask_result(self, key: tuple[str, str]) -> None:
        """The result of a task resolved to be read -- once."""
        if key in self._resulting:
            return
        self._resulting.add(key)
        self.run_worker(self._read_result(key), group=RESULT)

    async def _read_result(self, key: tuple[str, str]) -> None:
        """`team result <name> <task>`: kept as markdown; a refusal on the remedy line, kept as none."""
        try:
            face = await faces.result(self.house, *key)
            if not live(self):
                return
            if face.rc != 0:
                self.post_message(self.Refused(said_of(face)))
                self._results[key] = None
            else:
                try:
                    value = json.loads(face.out)
                except ValueError:
                    value = face.out.strip()
                self._results[key] = palette.result_markdown(value)
        finally:
            self._resulting.discard(key)
        if live(self) and self._picked() == key:
            self._show_band()

    @property
    def live(self) -> int:
        """The tasks the face says a wake-up plays, in every team started -- what the tab's title counts."""
        return sum(1 for state in self.states.values() for task in state.tasks if task.running)

    def spin(self, frame: int) -> None:
        """One frame of the spinner: the name cell of each line a wake-up plays, and nothing else."""
        self.frame = frame
        if not self.is_attached:
            return
        table = self.query_one("#tasks-list", DataTable)
        for index, row in enumerate(self.rows):
            if row.task.running and index < table.row_count:
                table.update_cell_at((index, 1), palette.task_name_cell(row.task, frame))

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if self._filling or event.cursor_row != event.data_table.cursor_row:
            return                                       # a menu filled, or a highlight its cursor has left since
        key = event.data_table.id
        if key == "tasks-show" and 0 <= event.cursor_row < len(SHOWS) and SHOWS[event.cursor_row] != self.show:
            self.show = SHOWS[event.cursor_row]
            self._fill()
        elif key == "tasks-team":
            teams = [ALL] + self._teams
            if 0 <= event.cursor_row < len(teams) and teams[event.cursor_row] != self.team:
                self.team = teams[event.cursor_row]
                self._fill()
        elif key == "tasks-list":
            self._show_band()
            if self.show == RECURRING:
                return
            if self._resting is not None:
                self._resting.stop()
            self._resting = self.set_timer(REST, self._rested)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """`enter` on a task: its thread, in an overlay."""
        if event.data_table.id == "tasks-list":
            event.stop()
            self.open_thread()

    def focus_table(self) -> None:
        table = self.query_one("#tasks-list", DataTable)
        if table.row_count:
            table.focus()
        else:
            self.screen.set_focus(None)

    def step(self, menu: str, by: int) -> None:
        """`[` `]` the `SHOW` before or after, `{` `}` the `TEAM` -- what the folded menu changes."""
        if menu == "show":
            self.show = SHOWS[(SHOWS.index(self.show) + by) % len(SHOWS)]
        else:
            teams = [ALL] + self._teams
            self.team = teams[(teams.index(self.team) + by) % len(teams)] if self.team in teams else ALL
        self._fill()

    def focus_task(self, team: str, task: str) -> None:
        """A task asked from elsewhere -- the last ring of a ceremony: every task of its team shown, the cursor on it."""
        self.show, self.team, self._asked = EVERY_TASK, team, (team, task)
        if self._read_once:
            self._fill()
        self.reread()

    # ---------- the thread of a task ----------
    def open_thread(self) -> None:
        """`enter`: the thread of the task under the cursor, live, in an overlay."""
        row = self._row_under_cursor()
        if row is None:
            self.post_message(self.Refused("no task under the cursor"))
            return
        screen = ThreadScreen(self, row.team, row.task.id, palette.task_title(row.task))
        self._thread_screen = screen

        def closed(_: object) -> None:
            if self._thread_screen is screen:
                self._thread_screen = None
        self.app.push_screen(screen, closed)

    def asks_of(self, key: tuple[str, str] | None) -> tuple[int, ...]:
        """-> the ids of the asks of the task `key` -- `(team, task)` -- that wait for the principal's answer, as the
        team's face lists them (`waiting.questions`: the asks of an open task no answer cites)."""
        state = self.states.get(key[0]) if key is not None else None
        if state is None:
            return ()
        return tuple(one.get("id") for one in state.waiting.get("questions") or [] if one.get("task") == key[1])

    @property
    def asks(self) -> int:
        """The asks to the owner that wait for an answer, in every team started -- what the tab's title badges."""
        return sum(len(self.open_ids(team)) for team in self.states)

    @property
    def unread(self) -> int:
        """The messages of the inbox `b` opens -- the team of the line under the cursor, else the `TEAM` filter's --,
        as that team's face counts them; 0 without a team at hand."""
        team = (self._team_of_line() if self.is_attached else None) or (self.team if self.team != ALL else None)
        state = self.states.get(team) if team is not None else None
        return state.inbox if state is not None else 0

    def open_ids(self, team: str) -> set:
        """-> the ids of the questions the face counts as waiting for the owner, in `team`."""
        state = self.states.get(team)
        if state is None:
            return set()
        return {one.get("id") for one in (state.waiting.get("questions") or [])
                + [one for one in state.waiting.get("notices") or [] if one.get("awaits")]}

    # ---------- writing on a task ----------
    def write(self) -> None:
        """`m`: a note or a reply on the task under the cursor, written in an overlay."""
        row = self._row_under_cursor()
        state = self.states.get(row.team) if row is not None else None
        if row is None or state is None:
            self.post_message(self.Refused("no task under the cursor"))
            return
        write_on(self, state, row.team, row.task.id, play=self._in_form)

    # ---------- the gestures ----------
    def _play(self, argv: list[str] | None) -> None:
        if argv is None:
            return
        self._look_for(argv)
        self._playing += 1
        self.run_worker(self._played(argv), group=GESTURE)

    def _in_form(self, argv: list[str]) -> Awaitable[str | None]:
        """The `play` of a form of the tab (`GestureScreen`): the gesture played under its overlay, counted among the
        gestures under way -> what awaits its answer, None once played, else what `team` said refusing it."""
        self._look_for(argv)
        self._playing += 1
        return self._refused_by(argv)

    def _look_for(self, argv: list[str]) -> None:
        """A new task or a recurrence laid by `argv`: followed once its team says it."""
        if argv[:2] == ["team", "post"] and "--every" in argv:
            state = self.states.get(argv[2])
            self._laid = (argv[2], {one.id for one in state.recurrences} if state is not None else set())
        elif argv[:2] == ["team", "post"] and "--task" not in argv:
            state = self.states.get(argv[2])
            self._launched = (argv[2], {one.id for one in state.tasks} if state is not None else set())

    async def _played(self, argv: list[str]) -> bool:
        """ONE gesture played (`_refused_by`) -> whether `team` played it."""
        return await self._refused_by(argv) is None

    async def _refused_by(self, argv: list[str]) -> str | None:
        """ONE gesture: the argv shown, played as it is; a refusal on the remedy line, the tasks read again -> None
        once `team` played it, else what it said refusing it (`""` once the tab has left). The caller counted it among
        the gestures under way (`_playing`)."""
        try:
            face = await play_gesture(argv, self.house)
            if not live(self):
                return ""
            if face.rc != 0:
                self.post_message(self.Refused(said_of(face)))
                if argv[:2] == ["team", "post"]:
                    self._launched = self._laid = None
            else:
                self.post_message(self.Played(argv))
            self.reread()
            return None if face.rc == 0 else said_of(face)
        finally:
            self._playing -= 1

    def _confirmed(self, title: str, argv: list[str] | None, expect: str | None = None,
                   then: Callable[[list[str] | None], None] | None = None) -> None:
        """The gesture asked in an overlay pushed over the screen on top; `ctrl+enter` plays it, `enter` too while no line
        holds the focus -- under `expect`, the line of the name holds it: `ctrl+enter` alone plays, once the name is
        typed. Under `then`, the argv confirmed -- None on `escape` or with nothing to play -- goes to `then`
        instead of being played here."""
        if argv is None:
            self.post_message(self.Refused("nothing to play here: no task under the cursor"))
            if then is not None:
                then(None)
            return

        def chosen(go: bool | None) -> None:
            if then is not None:
                then(argv if go else None)
            elif go:
                self._play(argv)
        self.app.push_screen(ConfirmScreen(title, expect), chosen)

    def _picked(self) -> tuple[str | None, str | None]:
        """-> (team, task) of the task under the cursor; (None, None) on no task -- a recurrence is none."""
        row = self._row_under_cursor()
        return (row.team, row.task.id) if row is not None else (None, None)

    def _team_of_line(self) -> str | None:
        """-> the team of the line under the cursor, a task's or a recurrence's."""
        key = self._key_under_cursor()
        return key[0] if key is not None else None

    def _title(self) -> str:
        """The task under the cursor as a title says it: `T3 · review PR 88`."""
        row = self._row_under_cursor()
        return palette.task_title(row.task) if row is not None else palette.NONE

    def stop_task(self) -> None:
        """`s`: the task under the cursor stopped -- shown, then played."""
        team, task = self._picked()
        self._confirmed(f"stop {self._title()}", gestures.stop(team, task))

    def kill_task(self) -> None:
        """`k`: the task under the cursor stopped and its wake-ups ended -- on the task's id typed."""
        team, task = self._picked()
        self._confirmed(f"kill the wake-ups of {self._title()}", gestures.stop(team, task, kill=True), task)

    def resume_task(self) -> None:
        """`r`: the task under the cursor taken back, written in an overlay -- whom it tells (`all`, then the members of
        the season, the root marked (`member_options`) and chosen at the opening; a face that says no root opens on no choice, no
        `--to`: the members the verb revives), a message (empty: none, `team`'s own words) and the principal it is taken
        back as."""
        team, task = self._picked()
        state = self.states.get(team or "")
        if gestures.resume(team, task) is None or state is None:
            self.post_message(self.Refused("no task under the cursor"))
            return
        owner = state.owner
        members = member_options(state)
        root = state.root if state.root in {value for _, value in members} else None
        fields = (Field("to", "to", "list", palette.RESUME_TO_HELP, ((EVERY_MEMBER, EVERY_MEMBER),) + members,
                        value=root, blank=None if root else palette.RESUME_TO_BLANK),
                  Field("message", "message", "text", palette.RESUME_HELP, example=palette.RESUME_EXAMPLE),
                  Field("as", "as", "list", palette.AS_HELP, senders_of(state), value=owner))
        self.app.push_screen(GestureScreen(f"resume {self._title()} of {team}", fields,
                                           lambda values: gestures.resume(team, task, values["message"], values["as"],
                                                                          owner, values["to"]),
                                           focus="message", play=self._in_form))

    def new_task(self) -> None:
        """`n`: a new task, written in an overlay -- its team among those started, the one the `TEAM` filter names
        first, else the one of the task under the cursor."""
        team = self.team if self.team != ALL else self._team_of_line()
        ask_new_task(self, dict(self.states), team or (self._teams[0] if self._teams else None), choose=True,
                     play=self._in_form)

    def _team_at_hand(self) -> str | None:
        """-> the team of the task under the cursor, else the one the `TEAM` filter names, else None -- said on the
        remedy line."""
        team = self._team_of_line() or (self.team if self.team != ALL else None)
        if team is None:
            self.post_message(self.Refused("choose a task or a team"))
        return team

    async def show_journal(self) -> None:
        """`l`: the whole journal of the team of the task under the cursor -- or of the `TEAM` filter's -- in an overlay."""
        team = self._team_at_hand()
        if team is not None:
            await journal_of(self, self.house, team)

    async def show_inbox(self) -> None:
        """`b`: the owner's inbox of the team of the task under the cursor -- or of the `TEAM` filter's -- in an overlay
        (`inbox_of`): `enter` on a question writes its reply on its task, `x` marks the message under the cursor read,
        `a` the inbox all read."""
        team = self._team_at_hand()
        state = self.states.get(team) if team is not None else None
        if team is not None and state is not None:
            await inbox_of(self, self.house, team, state)

    async def show_recurrences(self) -> None:
        """`e`: the recurrences in an overlay (`RecurrencesScreen`), as the faces the tab read say them -- the live ones
        alone, those they say no stop of --: under the `TEAM` filter `all`, those of every team started, each line its
        team (`recurring_of`); under a team chosen there, that team's alone. The cursor opens on the recurrence the task
        under the cursor is an occurrence of -- or on the line under the cursor under `recurring` --. Every gesture plays
        on the team of the line under the cursor, never another, written in an overlay pushed OVER `e` (`gesture`):
        played, `e` comes back on top read again -- the team's face read anew --; abandoned, `e` comes back as it was.
        `x` there deletes the line once its id is typed (`team stop --recurrence`, the stop the journal keeps), `m`
        changes its period, its text and its context limit in a gesture prefilled from the face -- the command carries
        the fields changed alone (`team recurrence --every --message --context`, `off` for a limit emptied) --, `space`
        pauses it -- or resumes it when the face says it paused -- in a gesture of its `as` alone (`team pause|resume
        --recurrence`), `p` makes a task given once of the line's team come back (`team recurrence --task`) -- without a
        line, the team at hand's --; a refusal of `team` on the remedy line."""
        scope = self.team
        if scope != ALL and self.states.get(scope) is None:
            return

        def lines_of(states: dict[str, TeamState]) -> list[RecurringRow]:
            if scope == ALL:
                return recurring_of([states[name] for name in self._teams if name in states])
            state = states.get(scope)
            return ([RecurringRow(scope, one, state.shown, state.off_season) for one in state.recurrences
                     if one.stopped is None]
                    if state is not None else [])
        row, line = self._row_under_cursor(), self._recurring_under_cursor()
        under = ((row.team, row.task.recurrence) if row is not None and row.task.recurrence
                 else (line.team, line.line.id) if line is not None else None)

        async def gesture(asked: tuple) -> list[RecurringRow] | None:
            """ONE gesture of `e`, written over it: -> the lines read again once `team` played it, None when nothing
            was played."""
            what, team, *recurrence = asked
            if what == "plan" and team is None:
                team = scope if scope != ALL else self._team_at_hand()
            state = self.states.get(team) if team is not None else None
            if state is None:
                return None
            written: asyncio.Future = asyncio.get_running_loop().create_future()

            def then(argv: list[str] | None) -> None:
                if not written.done():
                    written.set_result(argv)
            found = next((one for one in state.recurrences if one.id == recurrence[0]), None) if recurrence else None
            if what == "plan":
                self._plan_task(team, state, then)
            elif what == "stop":
                self._confirmed(f"delete the recurrence {recurrence[0]} of {team}",
                                gestures.stop(team, recurrence=recurrence[0]), recurrence[0], then)
            elif found is not None and what == "change":
                self._change_recurrence(team, found, then)
            elif found is not None and what == "toggle":
                self._toggle_recurrence(team, found, state, then)
            elif found is not None and what == "launch":
                then(gestures.launch(team, found.id))
            else:
                return None
            argv = await written
            if argv is None or not live(self):
                return None
            self._playing += 2                  # the gesture, and the reading of its team after it
            try:
                if not await self._played(argv) or not live(self):
                    return None
                obj, face = await faces.state(self.house, team)
                if not live(self):
                    return None
                if face.rc != 0:
                    return lines_of(self.states)
                return lines_of({**self.states, team: TeamState.read(obj or {"team": team, "started": None})})
            finally:
                self._playing -= 1
        await self.app.push_screen(RecurrencesScreen(None if scope == ALL else self._names.get(scope, scope),
                                                     lines_of(self.states), under, gesture))

    def _change_recurrence(self, team: str, line, then: Callable[[list[str] | None], None] | None = None) -> None:
        """`m` in `e`: the period, the text and the context limit of a recurrence, prefilled from the face; the command
        carries the fields changed alone -- a limit emptied is `off` --, none when nothing changed. The argv made goes
        to `then`, the pane's `_play` without it."""
        text = (line.text or "").strip()
        fields = (Field("every", "every", "line", palette.EVERY_CHANGE_HELP, value=line.every,
                        example=palette.EVERY_EXAMPLE),
                  Field("message", "message", "text", palette.TEXT_CHANGE_HELP, value=text),
                  Field("context", "context", "line", palette.CONTEXT_CHANGE_HELP, value=line.limit,
                        example=palette.CONTEXT_EXAMPLE))

        def argv_of(values: dict) -> list[str] | None:
            return gestures.recur(team, line.id, values["every"] if values["every"] != line.every else None,
                                  values["message"] if values["message"] != text else None,
                                  (values["context"] or "off") if values["context"] != line.limit else None)
        self.app.push_screen(GestureScreen(f"change the recurrence {line.id} of {team}", fields, argv_of,
                                           missing="a change", focus="every"), then or self._play)

    def _toggle_recurrence(self, team: str, line, state: TeamState,
                           then: Callable[[list[str] | None], None] | None = None) -> None:
        """`space` in `e`: the recurrence paused -- or resumed when the face says it paused --, written in an overlay:
        `as` (the owner, then the principals), as `P` pauses a team. The argv made goes to `then`, the pane's `_play`
        without it."""
        owner, paused = state.owner, line.paused is not None

        def argv_of(values: dict) -> list[str] | None:
            return gestures.pause_recurrence(team, line.id, paused, values["as"], owner)
        fields = (Field("as", "as", "list", palette.AS_HELP, senders_of(state), value=owner),)
        self.app.push_screen(GestureScreen(f"{'resume' if paused else 'pause'} the recurrence {line.id} of {team}",
                                           fields, argv_of), then or self._play)

    def _plan_task(self, team: str, state: TeamState, then: Callable[[list[str] | None], None] | None = None) -> None:
        """`p` in `e`: a task of the team that no recurrence and no meeting opened, made to come back -- its period and
        its context limit as typed. The argv made goes to `then` -- None when the team has no such task --, the pane's
        `_play` without it."""
        once = [one for one in state.tasks if one.recurrence is None and one.ceremony is None]
        if not once:
            self.post_message(self.Refused(f"no task given once in {self._names.get(team, team)}"))
            if then is not None:
                then(None)
            return
        fields = (Field("task", "task", "list", palette.PLAN_TASK_HELP,
                        tuple((palette.task_title(one), one.id) for one in once), value=once[0].id),
                  Field("every", "every", "line", palette.EVERY_HELP, example=palette.EVERY_EXAMPLE),
                  Field("context", "context", "line", palette.CONTEXT_HELP, example=palette.CONTEXT_EXAMPLE))
        self.app.push_screen(GestureScreen(f"make a task of {team} come back", fields,
                                           lambda values: gestures.plan(team, values["task"], values["every"],
                                                                        values["context"]),
                                           missing="a period", focus="task"), then or self._play)

    async def show_result(self) -> None:
        """`v`: the band of a task resolved changes its result for its sequence, or back; on a task still open, the
        verb's `task-open` on the remedy line."""
        team, task = self._picked()
        if team is None or task is None:
            self.post_message(self.Refused("no task under the cursor"))
            return
        if (team, task) not in self._results:
            await result_of(self, self.house, team, task, self._title())
            return
        self._modes[(team, task)] = "sequence" if self._modes.get((team, task), "result") == "result" else "result"
        if self._modes[(team, task)] == "sequence":
            self.threads.ask((team, task))
        self._show_band()

    def action_back(self) -> None:
        """`escape`: from the sequence or the result back to the tasks; anywhere else, nothing focused."""
        if self.screen.focused in (self.query_one("#tasks-sequence"), self.query_one("#tasks-result")):
            self.query_one("#tasks-list", DataTable).focus()
        else:
            self.screen.set_focus(None)

    @property
    def keys(self) -> list[tuple[str, str]]:
        focused = self.screen.focused if self.is_attached else None
        if focused is not None and focused.id == "tasks-sequence":
            return list(SequenceView.keys)
        if focused is not None and focused.id == "tasks-result":
            return [("result:", ""), ("↑↓ pgup pgdn", "scroll"), ("v", "sequence"), ("esc", "list")]
        if self.show == RECURRING:
            return [("recurrence:", ""), ("e", "recurrences"), ("l", "journal"), ("b", "inbox"), ("n", "new task"),
                    ("tab", "band, filters"), ("u", "reload")]
        return [("task:", ""), ("enter", "thread"), ("m", "message"), ("s", "stop"), ("k", "kill"), ("r", "resume"),
                ("v", "result/sequence"), ("l", "journal"), ("b", "inbox"), ("e", "recurrences"), ("n", "new task"),
                ("tab", "band, filters"),
                ("u", "reload")]


def _shows(zone, shown: bool) -> None:
    """A zone of the band shown, or hidden when it has nothing to show (the class `absent`) -- a class, so that the CSS
    of a frame expanded hides it too."""
    zone.set_class(not shown, "absent")


def _shown(zone) -> bool:
    """-> whether a zone of the band has something to show."""
    return not zone.has_class("absent")


class ThreadScreen(Overlay):
    """The THREAD of one task, live: its history (`team log <name> --json --task <id>`), then what its team's ONE
    watch says that names the task, an `id` shown once, `live:` the last step of a wake-up on it, `[open]` on a
    question the face counts as waiting for the owner. An end of a wake-up -- which the watch says without a task --
    and the first object the overlay hears read the history again, which places each event by its `id`."""

    DEFAULT_CSS = """
    ThreadScreen > #box { width: 95%; max-width: 160; height: 90%; }
    ThreadScreen #thread-title { height: 1; text-wrap: nowrap; text-overflow: ellipsis; margin-bottom: 1; }
    ThreadScreen #thread-body { height: 1fr; }
    ThreadScreen #thread-live { height: 1; text-wrap: nowrap; text-overflow: ellipsis; }
    ThreadScreen #thread-lines { height: auto; text-wrap: nowrap; text-overflow: ellipsis; }
    """
    BINDINGS = Overlay.BINDINGS + [Binding("q", "cancel", "close")]
    keys = [("esc", "close")]
    scrolls = False             # its body scrolls itself, under the title

    def __init__(self, pane: TasksPane, team: str, task: str, label: str) -> None:
        super().__init__()
        self.pane, self.team, self.task_id, self.label = pane, team, task, label
        self.thread = Thread(task)
        self._opening = True                # the history is being read at the opening
        self._watch: faces.Subscription | None = None
        self._merging = False
        self._again = False

    def body(self):
        yield Static(palette.event_title("thread", Text(f"{self.team}{palette.SEP}{self.label}")),
                     id="thread-title", markup=False)
        with VerticalScroll(id="thread-body"):
            yield Static("", id="thread-live", markup=False)
            yield Static("", id="thread-lines", markup=False)

    def on_mount(self) -> None:
        super().on_mount()
        self.query_one("#thread-body").focus()
        self.run_worker(self._open(), group="thread-open")

    async def _open(self) -> None:
        """The team's watch subscribed FIRST, then the history read: what the watch says meanwhile is held."""
        try:
            self._watch = await faces.follow(self.pane.house, self.team)
            self.run_worker(self._follow(self._watch), group="thread-follow")
            found, face = await faces.log(self.pane.house, self.team, self.task_id)
            if face.rc != 0:
                self.pane.post_message(self.pane.Refused(said_of(face)))
            self.thread.history(found)
            self._show()
        finally:
            self._opening = False

    @property
    def reading(self) -> bool:
        """Whether the history is being read -- what a render waits for."""
        return self._opening or self._merging

    async def _follow(self, watch: "faces.Subscription") -> None:
        first = True
        async for found in watch.events():
            if not self.is_attached:
                return
            event = str(found.get("event", ""))
            if first or (event in ENDS and "task" not in found):
                first = False
                self._merge()
            if found.get("task") == self.task_id:
                self.thread.add(found)
                self._show()

    def _merge(self) -> None:
        """The history read again -- now, or once after the reading under way."""
        if self._merging:
            self._again = True
            return
        self._merging = True
        self.run_worker(self._merged(), group="thread-merge")

    async def _merged(self) -> None:
        try:
            while True:
                self._again = False
                found, face = await faces.log(self.pane.house, self.team, self.task_id)
                if face.rc == 0 and self.is_attached:
                    self.thread.merge(found)
                    self._show()
                if not self._again:
                    return
        finally:
            self._merging = False

    def _show(self) -> None:
        """The thread drawn -- the one way every worker of the overlay draws; nothing once its children left, the
        overlay closing while it is still attached."""
        if not self.is_attached:
            return
        try:
            live, lines = self.query_one("#thread-live", Static), self.query_one("#thread-lines", Static)
            body = self.query_one("#thread-body")
        except NoMatches:
            return
        live.update(palette.live_line(self.thread.live, self.thread.live_over))
        lines.update(palette.thread_text(self.thread.lines, self.pane.open_ids(self.team)))
        body.scroll_end(animate=False)

    async def on_unmount(self) -> None:
        if self._watch is not None:
            await self._watch.close()
