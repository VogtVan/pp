"""tasks -- the TASKS tab: WHAT the teams do, the tasks of every team started, as the faces of `team` say them.

A menu on the left -- the filters `SHOW` (`recent` first: the open tasks and those ended within the day; `running`:
the open tasks; `for you`: the tasks with a question or an end the owner has not seen, as the face's `waiting` lists
them; `stopped`, `resolved`, `all`), each with the tasks it keeps, and `TEAM` (`all`, then each team started) -- and a
centre of horizontal bands: the TASKS the filters keep, the most recently born first, the teams mingled (the name,
else the start of the text; the team, the state, who holds it, the progress counted on the face's delegations, the
cost, the moment it was born), then the BAND of the task under the cursor -- its detail, then ONE of two: its
SEQUENCE (`panes.sequence`), or its RESULT in markdown, whole. A task resolved that no wake-up plays opens on its
result, any other on its sequence; `v` changes one for the other. Under ~70 columns the menu folds into one line,
`show: < … > · team: < … >`, which `[` `]` and `{` `}` change -- the screen's breakpoint class, CSS alone.

The tasks are read at the first showing, then by the ROUND of the Teams tab's measure (`ROUND_FLOOR`,
`ROUND_FACTOR`), on `u`, after a gesture, and at each object of a team's watch but a step and `quiet`: `team
status --json`, then one `team status <name> --json` per team started -- the readings asked meanwhile make ONE
after the one under way. The tab subscribes, at its first reading, to the ONE watch of each team started
(`faces.team.follow`, shared with the Teams tab): never a watch per task.

A task a wake-up plays -- the face says it `running` -- turns: the spinner before its name, and the tab's title
counts such tasks, `4·Tasks ⠹ 2` (`live`); the app's spinner turns while a turn of the dialogue or a wake-up
runs, and each frame changes the name cells of those lines alone (`spin`).

The RESULT of a task resolved is read once (`team result <name> <task>`) and kept; while it is read, and when the
verb refuses, the band shows the task's sequence. The result scrolls in its frame: `tab` goes there from the tasks,
`escape` comes back.

The SEQUENCE of the task under the cursor is its thread (`team log <name> --json --task <id>`), read once the cursor
has rested `REST` seconds on the task, then fed by its team's watch; under the name of each member, in blue, the pile
of procs of the last step its wake-up said on the task -- none once an end of that wake-up comes. A step names its
member, its task and its run (`agent`, `task`, `run`) -- the face says them: the tab never ties a step to a task.
`tab` goes into the sequence, where `up` and `down` move its cursor, `enter` opens the row's text whole, `w` leaves
the wake-ups out; `escape` comes back to the tasks.

`enter` on a task opens its THREAD in an overlay, live: its history (`team log <name> --json --task <id>`),
then what its team's watch says that names the task (`task`), an `id` shown once; an end of a wake-up the watch
says without a task reads the history again, which places it by `id` -- as does the first object the overlay
hears, so that nothing written while it opened is lost. `escape` closes it.

The tab plays the gestures of a task, each written in an overlay: `m` writes on the task under the cursor -- `to`,
`as`, `reply to` read from `team status --json`, then the text, the exact command under them --; `r` resumes it --
a message and `as` --; `n` gives a team a new task -- the team, its name, `to`, `as`, its message --; `s`, `k` (the
task's name typed); `l` the journal of the task's team, `v` its result. Every gesture is a verb `./pp team …` shown before it plays, its refusal on the remedy line as the verb
said it, the tasks read again after it. A new task played from the tab is FOLLOWED: the next reading puts the cursor
on the task its team says that it did not say before, `SHOW` turned to `recent` when the filter in place hides it. The tab computes no state of a task: a column or a filter reads a field
of the face, counted or cut, never deduced from the journal."""
from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime

from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.widgets import DataTable, Static

from rich.text import Text
from textual.binding import Binding

import palette
import panes
from faces import play_verb
from faces import team as faces
from model import PaneSpec, gestures
from model.teams import (ALL, SHOWS, TASK_COLUMNS, TaskRow, TeamBadge, TeamState, Thread, ThreadLine, counted,
                         filtered, newcomer, rows_of)
from panes import live
from panes.agents import said_of
from panes.sequence import SequenceView, Threads
from panes.overlays import ConfirmScreen, Field, GestureScreen, Overlay
from panes.teams import ROUND_FACTOR, ROUND_FLOOR, ask_new_task, journal_of, result_of, senders_of, write_on
from panes.transcript import MarkdownText

READ, FOLLOW, GESTURE, RESULT = "tasks-read", "tasks-follow", "tasks-gesture", "tasks-result"
ENDS = ("wake-ended", "wake-failed", "wake-killed")   # the events that end a wake-up
REST = 0.3                     # seconds the cursor rests on a task before its thread is read


class TasksPane(Vertical):
    """The Tasks tab: the folded menu, then the filters beside the centre -- the tasks, the band of the one chosen."""

    DEFAULT_CSS = """
    TasksPane { height: 1fr; }
    TasksPane .fold { display: none; height: 1; padding: 0 1; }
    #tasks-row { height: 1fr; }
    #tasks-menu { width: 22; max-width: 35%; height: 1fr; }
    #tasks-menu .title, #tasks-centre .title { height: 1; padding: 0 1; }
    #tasks-show { height: auto; }
    #tasks-team { height: 1fr; }
    #tasks-centre { width: 1fr; height: 1fr; padding-left: 1; }
    #tasks-menu .title.rule-top { height: 2; margin-top: 1; }
    #tasks-list { height: auto; max-height: 45%; }
    #tasks-band { height: 1fr; padding: 0 1; margin-top: 1; }
    #tasks-detail { height: auto; }
    #tasks-sequence { height: 1fr; min-height: 6; margin-top: 1; }
    #tasks-result { height: 1fr; margin-top: 1; display: none; }
    #tasks-result-text { height: auto; }
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
        """A gesture played: its command, for the status line."""

        def __init__(self, command: str) -> None:
            super().__init__()
            self.command = command

    def __init__(self, spec: PaneSpec, house: str) -> None:
        super().__init__(id=f"pane-{spec.key}")
        self.spec, self.house = spec, house
        self.states: dict[str, TeamState] = {}   # the teams started, as `status <name> --json` says them
        self.rows: list[TaskRow] = []            # the tasks the filters keep, in the table's order
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
        self._steps: dict[tuple[str, str], dict[str, ThreadLine]] = {}   # by (team, task): each member's last step
        self._over: set[tuple[str, str, str]] = set()   # (team, task, member): its wake-up ended after its last step
        self.threads = Threads(self, self._sequence_moved)
        self._modes: dict[tuple[str, str], str] = {}    # what `v` chose the band shows of a task: `result`, `sequence`
        self._resting = None                     # the timer of the cursor resting on a task
        self.frame = 0                           # the spinner's frame, as the app turns it
        self._thread_screen: "ThreadScreen | None" = None
        self._playing = 0
        self._filling = False                    # the menus are being filled: their highlights are no choice
        self._asked: tuple[str, str] | None = None  # a (team, task) to put the cursor on once read
        self._launched: tuple[str, set[str]] | None = None   # a new task posted: its team, the tasks it said before
        self._results: dict[tuple[str, str], str | None] = {}   # the result of each task resolved, read once
        self._resulting: set[tuple[str, str]] = set()          # a result being read

    def compose(self):
        yield Static("", id="tasks-fold", classes="fold", markup=False)
        with Horizontal(id="tasks-row"):
            with Vertical(id="tasks-menu", classes="menu"):
                yield Static(palette.section_title("Show", ""), id="tasks-show-title", classes="title", markup=False)
                yield panes.table(id="tasks-show", show_header=False)
                yield Static(palette.section_title("Team", ""), id="tasks-team-title", classes="title rule-top",
                             markup=False)
                yield panes.table(id="tasks-team", show_header=False)
            with Vertical(id="tasks-centre", classes="centre rule-left"):
                yield Static(palette.section_title("Tasks", ""), id="tasks-list-title", classes="title", markup=False)
                yield panes.table(id="tasks-list", zebra_stripes=True, cell_padding=2)
                with Vertical(id="tasks-band", classes="rule-top"):
                    yield Static("", id="tasks-detail", markup=False)
                    yield SequenceView(id="tasks-sequence")
                    with VerticalScroll(id="tasks-result"):
                        yield MarkdownText("", id="tasks-result-text")

    def on_mount(self) -> None:
        self.query_one("#tasks-show", DataTable).add_columns("show", "n")
        self.query_one("#tasks-team", DataTable).add_columns("team")
        self.query_one("#tasks-list", DataTable).add_columns(*TASK_COLUMNS)

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
        read = await asyncio.gather(*(faces.state(self.house, name) for name in teams))
        if not live(self):
            return
        states = {}
        for name, (obj, one) in zip(teams, read):
            if one.rc != 0:
                self.post_message(self.Refused(said_of(one)))
            states[name] = TeamState.read(obj or {"team": name, "started": None})
        self._teams, self.states, self._read_at = teams, states, datetime.now()
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
        """The objects of a team's watch: each fed to the threads kept; a step is kept as its member's last on the task
        it names, an end of a wake-up ends the pile of its member and run, any other object but `quiet` reads the tasks
        again."""
        async for found in watch.events():
            if not live(self):
                return
            event = str(found.get("event", ""))
            self._seen[f"team:{event}"] = self._seen.get(f"team:{event}", 0) + 1
            self.threads.heard(team, found)
            line = ThreadLine.read(found)
            if line.step:
                task, member = found.get("task"), found.get("agent")
                if isinstance(task, str) and isinstance(member, str):
                    self._steps.setdefault((team, task), {})[member] = line
                    self._over.discard((team, task, member))
                    self._show_band()
                continue
            if event in ENDS:
                member = found.get("agent")
                for (named, task), steps in self._steps.items():
                    step = steps.get(member) if named == team and isinstance(member, str) else None
                    if step is not None and step.fields.get("run") == found.get("run"):
                        self._over.add((team, task, member))
            if event != "quiet":
                self.reread()

    def saw(self, kind: str) -> int:
        return self._seen.get(kind, 0)

    def counts(self) -> dict[str, int]:
        return dict(self._seen)

    # ---------- what the tab shows ----------
    def _fill(self) -> None:
        """The menus with their counts, the tasks the filters keep, the band, the folded line, the status."""
        every = rows_of([self.states[name] for name in self._teams])
        self._follow_launched(every)
        current = self._row_under_cursor()               # read on the rows the table still shows
        self.rows = filtered(every, self.show, self.team)
        numbers = counted(every, self.team)
        self._filling = True
        try:
            self._menu("tasks-show", [palette.filter_cells(show, numbers[show]) for show in SHOWS], SHOWS.index(self.show))
            teams = [ALL] + self._teams
            self._menu("tasks-team", [palette.filter_cells(self._names.get(one, one)) for one in teams],
                       teams.index(self.team))
            self._rows("tasks-list", [palette.task_row_cells(one, self.frame) for one in self.rows], 0)
            keys = [(one.team, one.task.id) for one in self.rows]
            wanted = self._asked or ((current.team, current.task.id) if current is not None else None)
            if wanted in keys:
                self.query_one("#tasks-list", DataTable).move_cursor(row=keys.index(wanted))
                if self._asked is not None:
                    self._asked = None
                    self.query_one("#tasks-list", DataTable).focus()
        finally:
            self._filling = False
        if self.active and self.screen.focused is None and self.rows:
            self.query_one("#tasks-list", DataTable).focus()
        for key, title in (("tasks-show", "Show"), ("tasks-team", "Team"), ("tasks-list", "Tasks")):
            self.query_one(f"#{key}-title", Static).update(
                palette.section_title(title, self._read_at, dated=key == "tasks-show"))
        self.query_one("#tasks-fold", Static).update(
            f"{palette.folded('show', self.show)}{palette.SEP}{palette.folded('team', self._names.get(self.team, self.team))}")
        self._show_band()
        self.post_message(self.Read(palette.tasks_bar(len(self.rows), len(every), self.show,
                                                      self._names.get(self.team, self.team),
                                                      palette.hhmmss(self._read_at) if self._read_at else "")))

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

    def _rows(self, key: str, rows: list[tuple], at: int) -> None:
        table = self.query_one(f"#{key}", DataTable)
        table.clear()
        for index, cells in enumerate(rows):
            table.add_row(*cells, key=str(index))
        if rows:
            table.move_cursor(row=max(0, min(at, len(rows) - 1)))

    def _row_under_cursor(self) -> TaskRow | None:
        row = self.query_one("#tasks-list", DataTable).cursor_row
        return self.rows[row] if 0 <= row < len(self.rows) else None

    def _show_band(self) -> None:
        """The task under the cursor whole, then ONE of two: its sequence, or its result in markdown once read -- a
        task resolved that no wake-up plays shows its result unless `v` chose its sequence."""
        row = self._row_under_cursor()
        self.query_one("#tasks-detail", Static).update(palette.task_detail(row.task, row.team) if row else
                                                      palette.dim(f"{palette.NONE}  no task {self.show} here"))
        key = (row.team, row.task.id) if row is not None else None
        resolved = row is not None and row.task.state == "resolved" and not row.task.running
        if resolved and key not in self._results:
            self._ask_result(key)
        source = self._results.get(key) if resolved else None
        shown = source is not None and self._modes.get(key, "result") == "result"
        sequence, result = self.query_one("#tasks-sequence", SequenceView), self.query_one("#tasks-result")
        if self.screen.focused in (sequence, result) and (sequence.display, result.display) != (not shown, shown):
            self.query_one("#tasks-list", DataTable).focus()    # what was focused leaves: the tasks take the keys
        sequence.display, result.display = not shown, shown
        if shown:
            self.query_one("#tasks-result-text", MarkdownText).show(source)
        elif key is not None and key in self.threads.threads:
            sequence.show(self.threads.sequence(key), self._stacks(key), row.team)
        else:
            sequence.clear()

    def _sequence_moved(self, key: tuple[str, str]) -> None:
        """A thread kept moved: the band drawn again when it is the task under the cursor's."""
        if live(self) and key == self._picked():
            self._show_band()

    def _stacks(self, key: tuple[str, str]) -> dict[str, str]:
        """-> the pile of procs each member's wake-up under way plays on the task, from its last step there."""
        return {member: str(step.fields.get("stack") or "") for member, step in self._steps.get(key, {}).items()
                if key + (member,) not in self._over and step.kind == "block"}

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
        self.show, self.team, self._asked = ALL, team, (team, task)
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
        write_on(self, state, row.team, row.task.id)

    # ---------- the gestures ----------
    def _play(self, argv: list[str] | None) -> None:
        if argv is None:
            return
        if argv[:2] == ["team", "post"] and "--task" not in argv:   # a new task: followed once its team says it
            state = self.states.get(argv[2])
            self._launched = (argv[2], {one.id for one in state.tasks} if state is not None else set())
        self._playing += 1
        self.run_worker(self._played(argv), group=GESTURE)

    async def _played(self, argv: list[str]) -> None:
        """ONE gesture: the argv shown, played as it is; a refusal on the remedy line, the tasks read again."""
        try:
            face = await play_verb(argv, self.house)
            if not live(self):
                return
            if face.rc != 0:
                self.post_message(self.Refused(said_of(face)))
                if argv[:2] == ["team", "post"]:
                    self._launched = None
            else:
                self.post_message(self.Played(gestures.preview(argv)))
            self.reread()
        finally:
            self._playing -= 1

    def _confirmed(self, title: str, argv: list[str] | None, expect: str | None = None) -> None:
        """The command in an overlay; `enter` plays it -- under `expect`, once the name is typed."""
        if argv is None:
            self.post_message(self.Refused("nothing to play here: no task under the cursor"))
            return

        def chosen(go: bool | None) -> None:
            if go:
                self._play(argv)
        self.app.push_screen(ConfirmScreen(title, gestures.preview(argv), expect), chosen)

    def _picked(self) -> tuple[str | None, str | None]:
        row = self._row_under_cursor()
        return (row.team, row.task.id) if row is not None else (None, None)

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
        """`r`: the task under the cursor taken back, written in an overlay -- a message to the members it revives
        (empty: none, `team`'s own words) and the principal it is taken back as."""
        team, task = self._picked()
        state = self.states.get(team or "")
        if gestures.resume(team, task) is None or state is None:
            self.post_message(self.Refused("no task under the cursor"))
            return
        owner = state.owner
        fields = (Field("message", "message", "text", palette.RESUME_HELP, example=palette.RESUME_EXAMPLE),
                  Field("as", "as", "list", palette.AS_HELP, senders_of(state), value=owner))
        self.app.push_screen(GestureScreen(f"resume {self._title()} of {team}", fields,
                                           lambda values: gestures.resume(team, task, values["message"], values["as"],
                                                                          owner),
                                           focus="message"), self._play)

    def new_task(self) -> None:
        """`n`: a new task, written in an overlay -- its team among those started, the one the `TEAM` filter names
        first, else the one of the task under the cursor."""
        team = self.team if self.team != ALL else self._picked()[0]
        ask_new_task(self, dict(self.states), team or (self._teams[0] if self._teams else None), choose=True)

    async def show_journal(self) -> None:
        """`l`: the whole journal of the team of the task under the cursor -- or of the `TEAM` filter's -- in an overlay."""
        team = self._picked()[0] or (self.team if self.team != ALL else None)
        if team is not None:
            await journal_of(self, self.house, team)

    async def show_result(self) -> None:
        """`v`: the band of a task resolved changes its result for its sequence, or back; on a task still open, the
        verb's `task-open` on the remedy line."""
        team, task = self._picked()
        if team is None or task is None:
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
        return [("task:", ""), ("enter", "thread"), ("m", "message"), ("s", "stop"), ("k", "kill"), ("r", "resume"),
                ("v", "result/sequence"), ("l", "journal"), ("n", "new task"), ("tab", "band, filters"), ("u", "reload")]


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
        if not self.is_attached:
            return
        self.query_one("#thread-live", Static).update(palette.live_line(self.thread.live, self.thread.live_over))
        self.query_one("#thread-lines", Static).update(palette.thread_text(self.thread.lines,
                                                                            self.pane.open_ids(self.team)))
        self.query_one("#thread-body").scroll_end(animate=False)

    async def on_unmount(self) -> None:
        if self._watch is not None:
            await self._watch.close()
