"""teams -- the TEAMS tab: WHO the teams are, as the faces of `team` say them.

A menu on the left -- the teams declared, each name in its state's look (`⏸` before a team paused), the
wake-ups under way of each, the questions waiting for the owner, the tasks done not seen, `-` for a team
never started --, and a centre of horizontal bands: the HEAD of the team
chosen (its owner and mandators, its state, its budget and its wake-ups, its net, what waits for the
owner, counted), then its MEMBERS, then the TASKS of the member under the cursor (`panes.sequence.TaskStrip`) and the
SEQUENCE of the task chosen there, centred on that member: its column first, then those it exchanged with alone --
the same component as the Tasks tab's, its thread read once the band's cursor has rested on the task, then fed by the
team's watch. `tab` goes from the members to the band, then to the sequence; `escape` comes back to the members.
The sequence EXPANDS as the frames of the Tasks tab: the glyph `palette.EXPAND` last in its title, lit under the mouse
by the hover every tab shares (`panes.hover`), expands it over the whole centre at a click -- the menu of the teams
kept beside it --, the glyph turned to `palette.COLLAPSE`; the same click, or `escape`, folds it back. Under ~70 columns the menu folds into one line, `team: < … · <state> >`, which `[`
and `]` change -- the screen's breakpoint class, CSS alone. The ceremonies open over the tab (`c`), the
detail of a member too (`d`); `C` opens a conversation with the member's agent under the root of the team, the
dialogue of any run (`ChatAsked`), through the overlay of a new run's parameters the Agents tab pushes (`ask_run`). A
click on a member puts the cursor on it; a double click, or `enter`, opens its run. Nothing is read before the tab is first shown. Then `team status --json`
gives the teams, the first one is chosen, `team status <name> --json` gives it whole, and the tab subscribes
to the team's ONE watch (`faces.team.follow`, shared with the Tasks tab): every object of the watch but
`quiet` asks the team to be read again, and the asks that come while a reading runs make ONE reading after
it. Choosing another team leaves the first team's watch -- ended when nobody else follows it -- and
subscribes to the second's; the post's end ends it.

The teams are read again by a ROUND, never a sleeping loop: `set_timer` after each reading, at
`max(ROUND_FLOOR, ROUND_FACTOR × the reading's cost)`. Measured on 2026-10-10 on a throwaway house
of two declared teams: `./pp team status --json` costs 0.17 s through the console (5 calls, 0.171 to
0.178 s; the bench's witness 0.02 s) -- 20 × 0.17 = 3.4 s, under the floor: the round comes every
10 s, a reading taking 1.7 % of the time. A held `team watch --json` on that house cost 0.17 s of CPU
over 10 s. `u` reads both now.

The tab plays the gestures of a team and of a member: every gesture is a verb of `team` whose argv
`model/gestures.py` makes from what is chosen, asked in an overlay (`ConfirmScreen`, `GestureScreen` -- the
fields of a gesture; no command shown), played by `play_gesture` -- the team's tick apart --, its refusal on the remedy line as the verb
said it, what it did on the status line, the team read again after it. `X` and `R` play only once the name of their target is typed, `X` saying
what it stops as the face counts it; `P` pauses the team, or resumes it when the face says it paused. `b` shows
the owner's inbox (`team inbox --json`) -- a question there answered on its task, `x` marking one message read, `a`
all of them --, `e` the
declaration (`team declaration --json`), read only, and `B` raises the budget, a field changed alone composing
its argument. `N` and `E` open the form of TEAM.md, `S` the form of SEASON.md, one class for both (`ValuesForm`):
their presets read from `team templates --json`, their fields from the texts of `team declaration --json` -- `N`
empty on a name --, the side pane the file as it will be written; `enter` plays `team declare` for the keys changed
alone, `ctrl+s` on a season then `team start`, the post writing no file; a team born is chosen once the teams are read
again, and a refusal of `team declare` opens the form again on its values. The tab computes no state of a team: the next ring of a
ceremony, a wait, what a member has not seen are `team`'s, shown as the face says them; no gesture is hidden
by the state of a team -- the verb judges."""
from __future__ import annotations

import asyncio
import copy
import dataclasses
import json
import time
from datetime import datetime
from typing import Awaitable, Callable

from rich.text import Text

from textual import events
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widgets import DataTable, Static

import palette
import panes
from faces import objects, play_gesture, play_verb
from faces import team as faces
from model import PaneSpec, files, gestures
from model.teams import (COST_BASES, MEMBER_COLUMNS, SEASON_ALL, TEAM_COLUMNS, Activity, MemberRow, TeamBadge, TeamState, ThreadLine,
                         is_activity, member_rows, season_lines)
from model.runs import AgentLine, rooted_name
from panes import live
from panes.agents import ask_run, read_line, said_of
from panes.hover import GlyphHover
from panes.season import SeasonBoard, board_title, season_head, season_title, season_zones, seasons_head, \
    seasons_zones, summary_text, summary_title, plain_of, title_word
from panes.sequence import SequenceView, TaskStrip, Threads
from panes.documents import Documents
from panes.forms import ValuesForm
from panes.overlays import CeremoniesScreen, ConfirmScreen, EventScreen, Field, GestureScreen, InboxScreen, Part

ROUND_FLOOR = 10.0                 # seconds at least between two readings of the teams
ROUND_FACTOR = 20                  # the round waits this many times what a reading cost
INFO, ASK = "info", "ask"            # the kinds of a note on a task: an info owes nothing, an ask its answer
BADGES, STATE, FOLLOW = "teams-badges", "teams-state", "teams-follow"   # the worker groups
GESTURE = "teams-gesture"
REST = 0.3                         # seconds the band's cursor rests on a task before its thread is read
STATS_WIDTH = 130                  # under this width the summary of the season leaves the head its whole band
BORN_LIMITS = {"schedule": "30s"}  # the limits a team to be born opens on: its timer ticks every 30 s



class MembersTable(DataTable):
    """The table of the members: a click puts the cursor on the line it lands on and selects nothing, even on the line
    already under the cursor; a double click (`Click.chain`) selects its line, as `enter` does -- `RowSelected`."""

    _clicking = False                   # a click is being handled: a selection it would make is held
    _held = False                       # the click held one

    async def _on_click(self, event: events.Click) -> None:
        event.prevent_default()             # the table's own handling plays once, here
        self._clicking, self._held = True, False
        try:
            await super()._on_click(event)
        finally:
            self._clicking = False
        if self._held and event.chain >= 2:
            super()._post_selected_message()

    def _post_selected_message(self) -> None:
        if self._clicking:
            self._held = True
        else:
            super()._post_selected_message()


class TeamsPane(GlyphHover, Vertical):
    """The Teams tab: the folded menu, then the menu of the teams beside the centre -- the head, the members."""

    DEFAULT_CSS = """
    TeamsPane { height: 1fr; }
    TeamsPane .fold { display: none; height: 1; padding: 0 1; }
    #teams-row { height: 1fr; }
    #teams-list { width: auto; height: 1fr; }
    #teams-centre { width: 1fr; height: 1fr; padding-left: 1; }
    #teams-top { height: auto; }
    #teams-head { width: auto; max-width: 80%; height: auto; padding: 0 1; }
    #teams-stats { width: 1fr; height: auto; padding: 0 1; text-wrap: nowrap; text-overflow: ellipsis; }
    #teams-board { display: none; }
    TeamsPane.slim #teams-stats { display: none; }
    TeamsPane.slim #teams-head { width: 1fr; max-width: 100%; }
    TeamsPane.board #teams-centre > * { display: none; }
    TeamsPane.board #teams-centre > #teams-board { display: block; height: 1fr; }
    TeamsPane.expanded #teams-centre > * { display: none; }
    TeamsPane.expanded #teams-centre > .expanded { display: block; height: 1fr; }
    #teams-members { height: auto; max-height: 40%; }
    #teams-sequence { height: 1fr; }
    """
    BINDINGS = [Binding("escape", "back", show=False)]

    class Read(Message):
        """The chosen team was read: its line for the status."""

        def __init__(self, bar: list[tuple[str, str]]) -> None:
            super().__init__()
            self.bar = bar

    class Refused(Message):
        """A verb the tab played refused: what it said, for the remedy line."""

        def __init__(self, said: str) -> None:
            super().__init__()
            self.said = said

    class MemberAsked(Message):
        """The run of a member is asked, READ, in a tab of the dialogue: the app opens it."""

        def __init__(self, team: str, member: str, path: str, run: str, running: bool) -> None:
            super().__init__()
            self.team, self.member, self.path, self.run, self.running = team, member, path, run, running

    class ChatAsked(Message):
        """A conversation with the agent of a member is asked under the root of its team (`C`), with the flags and
        the name its overlay gave, and the member's vector when the team names one: the app opens it, `agent chat
        <path> <flags> --documents <root> [--vector <vector>]` -- the dialogue of any run, nothing of the team's acts."""

        def __init__(self, team: str, member: str, path: str, root: str, flags: tuple[str, ...] = (),
                     name: str = "", vector: str | None = None) -> None:
            super().__init__()
            self.team, self.member, self.path, self.root = team, member, path, root
            self.flags, self.name, self.vector = tuple(flags), name, vector

    class TaskAsked(Message):
        """A task of a team is asked -- the last ring of a ceremony: the Tasks tab shows it."""

        def __init__(self, team: str, task: str) -> None:
            super().__init__()
            self.team, self.task = team, task

    class Played(Message):
        """A gesture played: its argv, and what it did in words for the status line."""

        def __init__(self, argv: list[str]) -> None:
            super().__init__()
            self.argv, self.said = list(argv), gestures.summary(argv)

    def __init__(self, spec: PaneSpec, house: str, flags: tuple[str, ...] = ()) -> None:
        super().__init__(id=f"pane-{spec.key}")
        self.spec, self.house = spec, house
        self.flags = tuple(flags)          # what followed `--`: its `--harness` rides `S`
        self.badges: list[TeamBadge] = []
        self.team: str | None = None
        self.state: TeamState | None = None
        self._shown = False                # the first showing starts the readings
        self.active = False                # the tab is the one shown: its first table takes the focus
        self._badges_at = self._state_at = None     # the instants of the readings
        self._read_once = False            # the teams were read once
        self._reading = False              # a reading of the team is under way
        self._dirty = False                # an ask came during it: one reading more
        self._switching = asyncio.Lock()   # one change of team at a time: never two watches
        self._watch: faces.Subscription | None = None
        self._round = None
        self._seen: dict[str, int] = {}    # the watch's objects by `team:<event>`, what `--wait` counts
        self._playing = 0                  # gestures under way: a render waits for them
        self._ticking = 0                  # ticks started apart by `T`, their end not seen yet: a render waits for them
        self._want: str | None = None      # a team born from the post, chosen once the teams are read again
        self._activities: dict[str, Activity] = {}   # what the chosen team's watch said of each member's wake-up
        self._rows: tuple[MemberRow, ...] = ()     # the lines of the members: one per open task of a member
        self._row_shown: tuple | None = None       # the line whose task the band was last put on
        self._over: set[str] = set()       # the members whose wake-up ended after their last object
        self.threads = Threads(self, self._sequence_moved, self._face_of)
        self._resting = None               # the timer of the band's cursor resting on a task
        self._filling = False              # a table is being built again: its highlights are no choice
        self._stats: dict | None = None    # the chosen team's season under way or last, as `team stats --json` says it
        self._seasons: dict | None = None  # every season of the chosen team not empty, `team stats --all --json`
        self._base = COST_BASES[0]         # the base the costs are said in, the summary's and the dashboard's: the
                                           # settings' (`set_base`)
        self._board = False                # the dashboard is open over the centre
        self._expanded: str | None = None  # the frame expanded over the centre: `sequence`, None for none
        self._season: int | str | None = None   # the season the dashboard draws: a number, `SEASON_ALL`, None the summary's
        self._titles: dict[str, str] = {}  # the text each title of the stats draws, by its frame: what a click reads

    def compose(self):
        yield Static("", id="teams-fold", classes="fold", markup=False)
        with Horizontal(id="teams-row"):
            with Vertical(id="teams-menu", classes="menu framed"):
                yield panes.table(id="teams-list", zebra_stripes=True)
            with Vertical(id="teams-centre", classes="centre rule-left"):
                with Horizontal(id="teams-top"):
                    yield Static("", id="teams-head", classes="framed", markup=False)
                    yield Static("", id="teams-stats", classes="framed", markup=False)
                yield panes.table(MembersTable, id="teams-members", classes="framed", zebra_stripes=True,
                                  cell_padding=2)
                yield TaskStrip(id="teams-strip", classes="framed")
                yield SequenceView(id="teams-sequence").add_class("framed")
                yield SeasonBoard(id="teams-board", classes="framed")

    def on_mount(self) -> None:
        self.query_one("#teams-list", DataTable).add_columns(*TEAM_COLUMNS)
        self.query_one("#teams-members", DataTable).add_columns(*MEMBER_COLUMNS)
        self.query_one("#teams-menu").border_title = palette.framed("Teams", None, dated=True)
        self.query_one("#teams-members").border_title = palette.framed("Members")
        self.query_one("#teams-strip").border_title = palette.framed("Tasks")
        self._title_sequence()

    # ---------- the readings ----------
    def shown(self) -> None:
        """The tab is shown: the first time, the readings start; the focus goes to the teams."""
        if not self._shown:
            self._shown = True
            self.reread()
        self.focus_table()

    async def settled(self, final: bool = False) -> None:
        """Returns once nothing is being read -- what a render waits for; at once before the first showing."""
        while self._shown and (not self._read_once or self._reading or self._switching.locked() or self._playing
                               or self._ticking
                               or self._resting is not None or self.threads.busy):
            await asyncio.sleep(0.01)

    def reread(self) -> None:
        """`u`, and the first showing: the teams and the chosen team, read now."""
        self.run_worker(self._badges(), group=BADGES, exclusive=True)
        self.ask_state()

    async def _badges(self) -> None:
        """The teams read under the guard; a reading that failed counts as read."""
        try:
            await panes.guarded(self, self._read_badges(), "teams")
        finally:
            self._read_once = True

    async def _read_badges(self) -> None:
        began = time.monotonic()
        found, face = await faces.badges(self.house)
        cost = time.monotonic() - began
        if not live(self):                       # the post left while the face was read
            return
        if face.rc != 0:
            self.post_message(self.Refused(said_of(face)))
        self.badges = [TeamBadge.read(one) for one in found]
        self._badges_at = datetime.now()
        self._fill_teams()
        names = [one.team for one in self.badges]
        if self._want in names:
            await self.choose(self._want)
            self._want = None
        if self.team not in names:
            await self.choose(names[0] if names else None)
        self._read_once = True
        if self._round is not None:
            self._round.stop()
        self._round = self.set_timer(max(ROUND_FLOOR, ROUND_FACTOR * cost), self._next_round)

    def _next_round(self) -> None:
        self.run_worker(self._badges(), group=BADGES, exclusive=True)

    def ask_state(self) -> None:
        """The chosen team to be read again: now, or once after the reading under way."""
        if self._reading:
            self._dirty = True
            return
        self._reading = True
        self.run_worker(self._state_loop(), group=STATE)

    async def _state_loop(self) -> None:
        try:
            while True:
                self._dirty = False
                await panes.guarded(self, self._read_state(), "teams")
                if not self._dirty:
                    return
        finally:
            self._reading = False

    async def _read_state(self) -> None:
        name = self.team
        if name is None:
            self.state = None
        else:
            found, face = await faces.state(self.house, name)
            if not live(self) or name != self.team:   # the post left, or another team was chosen meanwhile
                return
            if face.rc != 0:
                self.post_message(self.Refused(said_of(face)))
            self.state = TeamState.read(found or {"team": name, "started": None})
            self._state_at = datetime.now()
            self._fill_team()                         # the team drawn at once, its stats completing it once read
            stats, seasons = await self._read_stats(name, self.state)
            if not live(self) or name != self.team:
                return
            self._stats, self._seasons = stats, seasons
            self._show_title()
            self._show_stats()
            return
        self._state_at = datetime.now()
        self._fill_team()

    async def _read_stats(self, name: str, state: TeamState) -> tuple[dict | None, dict | None]:
        """-> the stats of the team's seasons, a team started alone: its season under way or last, and every season
        once the dashboard is open -- None for what the verb refused, nothing on the remedy line."""
        if state.started is None:
            return None, None
        found, face = await faces.stats(self.house, name)
        stats = found.get("season") if face.rc == 0 and isinstance(found, dict) and isinstance(found.get("season"), dict) \
            else None
        seasons = None
        if self._board:
            found, face = await faces.stats(self.house, name, every=True)
            seasons = found if face.rc == 0 and isinstance(found, dict) else None
        return stats, seasons

    # ---------- the watch ----------
    async def choose(self, name: str | None) -> None:
        """`name` becomes the chosen team: the watch of the one before ended, one opened on it, the team read."""
        async with self._switching:
            if name == self.team and (name is None or self._watch is not None):
                return
            self.team, self.state = name, None
            self._stats = self._seasons = self._season = None
            self._activities, self._over = {}, set()
            self._show_member()
            if self._watch is not None:
                await self._watch.close()
                self._watch = None
            self.ask_state()
            if name is not None and live(self):
                self._watch = await faces.follow(self.house, name)
                self.run_worker(self._follow(self._watch), group=FOLLOW, exclusive=True)

    async def _follow(self, watch: "faces.Subscription") -> None:
        """The objects of the chosen team's watch, each drawn once: a step or an activity is kept in its member's
        activity, its line of the members and the head of the sequence drawn again -- an activity reads nothing, a
        step reads the team again --; an end of a wake-up ends the activity of its member and run; each is fed to the
        threads kept, a row drawn when it adds one; any other object but `quiet` reads the team again."""
        async for found in watch.events():
            if not live(self) or watch is not self._watch:
                return
            event = str(found.get("event", ""))
            self._seen[f"team:{event}"] = self._seen.get(f"team:{event}", 0) + 1
            member = found.get("agent")
            if (ThreadLine.read(found).step or is_activity(found)) and isinstance(member, str):
                self._activities[member] = Activity.heard(self._activities.get(member), found)
                self._over.discard(member)
                self._fill_members()
                self._activity_moved()
            elif event in ("wake-ended", "wake-failed", "wake-killed") and isinstance(member, str) \
                    and member in self._activities and self._activities[member].run == found.get("run"):
                self._over.add(member)
            if self.team is not None:
                self.threads.heard(self.team, found)
            if event != "quiet" and not is_activity(found):
                self.ask_state()

    async def close(self) -> None:
        """The watch ended, the round stopped -- the post leaves."""
        if self._round is not None:
            self._round.stop()
        if self._watch is not None:
            await self._watch.close()
            self._watch = None

    def saw(self, kind: str) -> int:
        return self._seen.get(kind, 0)

    def counts(self) -> dict[str, int]:
        return dict(self._seen)

    # ---------- what the tab shows ----------
    def _fill(self, key: str, rows: list[tuple]) -> None:
        """A table's lines: their cells updated in place while the table keeps its lines -- its cursor and what hangs
        on it stay --, built again with the cursor on its row otherwise, the highlights of the filling no choice."""
        table = self.query_one(f"#{key}", DataTable)
        if table.row_count == len(rows) and all(str(table.get_cell_at((index, 0))) == str(cells[0])
                                                for index, cells in enumerate(rows)):
            for index, cells in enumerate(rows):
                for column, cell in enumerate(cells):
                    table.update_cell_at((index, column), cell, update_width=True)   # a run born widens its column
            return
        row = table.cursor_row
        self._filling = True
        try:
            table.clear()
            for index, cells in enumerate(rows):
                table.add_row(*cells, key=str(index))
            if rows:
                table.move_cursor(row=max(0, min(row, len(rows) - 1)))
        finally:
            self._filling = False

    def _fill_teams(self) -> None:
        self.query_one("#teams-menu").border_title = palette.framed("Teams", self._badges_at, dated=True)
        table = self.query_one("#teams-list", DataTable)
        self._fill("teams-list", [palette.team_cells(one) for one in self.badges])
        names = [one.team for one in self.badges]
        if self.team in names:
            table.move_cursor(row=names.index(self.team))
        if self.active and self.screen.focused is None and table.row_count:
            table.focus()
        self._show_fold()
        if not self.badges:
            self.query_one("#teams-head", Static).update(palette.no_team())

    def on_resize(self, event: events.Resize) -> None:
        self.set_class(event.size.width < STATS_WIDTH, "slim")

    def _show_fold(self) -> None:
        badge = next((one for one in self.badges if one.team == self.team), None)
        self.query_one("#teams-fold", Static).update(palette.team_fold(self.team, badge))

    def _fill_team(self) -> None:
        state = self.state
        started = state is not None and state.started is not None
        self._fill_members()
        self._show_member()
        head = self.query_one("#teams-head", Static)
        self._show_title()
        self._show_stats()
        if self.team is None:
            head.update(palette.no_team())
        elif not started:
            badge = next((one for one in self.badges if one.team == self.team), None)
            head.update(palette.not_started(badge.shown if badge is not None else self.team))
        else:
            head.update(palette.team_head(state))
        self._show_fold()
        if self.team is not None:
            badge = next((one for one in self.badges if one.team == self.team), None)
            self.post_message(self.Read(palette.team_bar(badge.shown if badge is not None else self.team, badge, state,
                                                         palette.hhmmss(self._state_at))))

    # ---------- the stats of the seasons ----------
    def _show_title(self) -> None:
        """The title of the team's frame: its season and the season's state, as the stats say them once read, as the
        team's face and its badge say them before."""
        state = self.state
        started = state is not None and state.started is not None
        badge = next((one for one in self.badges if one.team == self.team), None)
        shown = badge.shown if badge is not None else self.team or palette.NONE
        season = (badge.season or {}) if badge is not None else {}
        self.query_one("#teams-head", Static).border_title = season_title(
            shown, self._stats if started else None, (state.season or {}).get("n") if started else None,
            season.get("state"))

    def _season_numbers(self) -> list[int]:
        """-> the seasons the dashboard offers, the latest first: those not empty, and the summary's."""
        found = {one.get("season") for one in (self._seasons or {}).get("seasons") or []}
        if self._stats is not None:
            found.add(self._stats.get("season"))
        return sorted((one for one in found if isinstance(one, int)), reverse=True)

    def _board_season(self) -> dict | None:
        """-> the season the dashboard draws: the one chosen among those not empty, else the summary's."""
        if self._season is None or (self._stats is not None and self._season == self._stats.get("season")):
            return self._stats
        return next((one for one in (self._seasons or {}).get("seasons") or [] if one.get("season") == self._season),
                    None)

    def glyph_frames(self) -> dict:
        """-> the frames whose title ends on a glyph: the summary's `EXPAND`, the dashboard's `COLLAPSE`, the
        sequence's -- they shine under the mouse (`GlyphHover`)."""
        return {"stats": (self.query_one("#teams-stats"), self.cells("stats")),
                "board": (self.query_one("#teams-board"), self.cells("board")),
                "sequence": (self.query_one("#teams-sequence"), self.cells("sequence"))}

    def _title_sequence(self) -> None:
        self.entitle("sequence", self.query_one("#teams-sequence"), palette.expandable(
            palette.framed("Sequence"), self._expanded == "sequence", self._hovered == "sequence"))

    def expand(self, key: str | None) -> None:
        """The frame `key` expanded over the centre -- the other bands hidden by the class `expanded`, the menu of the
        teams shown and played --; None folds it back."""
        focused = self.screen.focused
        if key is not None and focused is not None and focused.id in ("teams-members", "teams-strip"):
            self.query_one(f"#teams-{key}").focus()               # the band hidden leaves: the frame takes the keys
        self._expanded = key
        self.set_class(key is not None, "expanded")
        self.query_one("#teams-sequence").set_class(key == "sequence", "expanded")
        self._title_sequence()

    def _titled(self) -> None:
        """The titles of the summary, of the dashboard open and of the sequence, in the base chosen, the glyph under
        the mouse in the look `palette.HOVER`."""
        self._title_sequence()
        label = summary_title(self._base, self._hovered == "stats")
        self.entitle("stats", self.query_one("#teams-stats"), label)
        self._titles["teams-stats"] = plain_of(label)
        if self._board:
            chosen = self._season if self._season is not None else (self._stats or {}).get("season")
            label = board_title(self.team or palette.NONE, self._base, self._season_numbers(), chosen,
                                self._hovered == "board")
            self.entitle("board", self.query_one("#teams-board"), label)
            self._titles["teams-board"] = plain_of(label)

    def set_base(self, base: str) -> None:
        """The base of the costs chosen in the settings: the summary and the dashboard said in it."""
        if base in COST_BASES and base != self._base:
            self._base = base
            if self.is_mounted:
                self._show_stats()

    def _show_stats(self) -> None:
        """The summary of the season beside the head, and the dashboard when it is open, in the base chosen."""
        started = self.state is not None and self.state.started is not None
        self._titled()
        self.query_one("#teams-stats", Static).update(summary_text(self._stats if started else None, self._base))
        if not self._board:
            return
        board = self.query_one("#teams-board", SeasonBoard)
        if self._season == SEASON_ALL:
            board.show(seasons_head(self._seasons), seasons_zones(self._seasons, self._base))
        else:
            one = self._board_season()
            board.show(season_head(one), season_zones(one, (self._seasons or {}).get("median"), self._base))

    def open_board(self, opened: bool) -> None:
        """The dashboard opened over the centre -- the other bands hidden by the class `board`, the menu of the teams
        shown and played --, every season read; or closed, the centre back."""
        self._board = opened
        self.set_class(opened, "board")
        if opened:
            self.expand(None)
            focused = self.screen.focused
            if focused is not None and focused is not self.query_one("#teams-list"):
                self.query_one("#teams-list", DataTable).focus()     # the bands hidden leave: the teams take the keys
            self.ask_state()
        self._show_stats()

    def on_click(self, event: events.Click) -> None:
        """A click on the glyph of the sequence: the sequence expanded, or folded back once expanded. A click on a word
        of the summary's title or of the dashboard's: a season chosen, the dashboard opened or closed."""
        if self.glyph_under(event.screen_x, event.screen_y) == "sequence":
            event.stop()
            self.expand(None if self._expanded == "sequence" else "sequence")
            return
        stats, board = self.query_one("#teams-stats"), self.query_one("#teams-board")
        word = title_word(stats, self._titles.get("teams-stats", ""), event.screen_x, event.screen_y,
                          [palette.EXPAND])
        tabs = [f"[s.{one}]" for one in self._season_numbers()] + [f"[{SEASON_ALL}]"]
        if word is None and self._board:
            word = title_word(board, self._titles.get("teams-board", ""), event.screen_x, event.screen_y,
                              tabs + [palette.COLLAPSE])
        if word is None:
            return
        event.stop()
        if word == palette.EXPAND:
            self.open_board(True)
        elif word == palette.COLLAPSE:
            self.open_board(False)
        else:
            self._season = SEASON_ALL if word == f"[{SEASON_ALL}]" else int(word[3:-1])
            self._show_stats()

    def _fill_members(self) -> None:
        """The lines of the members of the team read -- one per open task of a member, its run there (`member_rows`)
        --, each with what the watch said of its wake-up: on a task's line, the wake-up that plays that task or run."""
        state = self.state
        started = state is not None and state.started is not None
        self._rows = member_rows(state) if started else ()
        self._fill("teams-members", [palette.member_cells(one.line, self._activity_of(one), one.member.member in self._over,
                                                          one.task) for one in self._rows])

    def _activity_of(self, row: MemberRow) -> Activity | None:
        """-> what the watch said of the wake-up of the member of `row`: any, on its line whole; on a task's line, the
        one that plays that task or its run alone."""
        activity = self._activities.get(row.member.member)
        if activity is None or row.task is None:
            return activity
        return activity if activity.task == row.task or (activity.run and activity.run == row.line.run) else None

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if self._filling or event.cursor_row != event.data_table.cursor_row:
            return                                       # a table filled, or a highlight its cursor has left since
        if event.data_table.id == "teams-list":
            row = event.cursor_row
            if 0 <= row < len(self.badges) and self.badges[row].team != self.team:
                self.run_worker(self.choose(self.badges[row].team))
        elif event.data_table.id == "teams-members":
            self._show_member()

    # ---------- the tasks of a member, and the sequence of the one chosen ----------
    def _show_member(self) -> None:
        """The band of the tasks of the member under the cursor, in the order of their birth -- as the face lists them
        on the member and on the team --, its cursor put on the task of the line when the cursor comes to it."""
        row = self._row_under_cursor()
        member = row.member if row is not None else None
        state = self.state
        tasks = {one.id: one for one in state.tasks} if state is not None else {}
        floor = "0000"
        mine = sorted((tasks[one] for one in (member.tasks if member is not None else ()) if one in tasks),
                      key=lambda one: one.at or floor)
        strip = self.query_one("#teams-strip", TaskStrip)
        strip.border_title = palette.framed(f"Tasks of {member.member}" if member is not None else "Tasks")
        line = (self.team, member.member, row.task) if row is not None else None
        at = row.task if row is not None and line != self._row_shown else None   # the team read again: the band stays
        self._row_shown = line
        strip.show(self.team, member.member if member is not None else None, mine, at)
        self._draw_sequence()

    def on_task_strip_chosen(self, message: TaskStrip.Chosen) -> None:
        """The band's cursor on another task: its thread asked once the cursor rests there."""
        if self._resting is not None:
            self._resting.stop()
            self._resting = None
        self._draw_sequence()
        if message.task is not None:
            self._resting = self.set_timer(REST, self._rested)

    def _rested(self) -> None:
        self._resting = None
        key = self._chosen()
        if key is not None:
            self.threads.ask(key)
            self._draw_sequence()

    def _chosen(self) -> tuple[str, str] | None:
        """-> the task the band's cursor stands on, with its team; None without one."""
        task = self.query_one("#teams-strip", TaskStrip).chosen
        return (self.team, task.id) if task is not None and self.team is not None else None

    def _sequence_moved(self, key: tuple[str, str]) -> None:
        if live(self) and key == self._chosen():
            self._draw_sequence()

    def _draw_sequence(self) -> None:
        """The sequence of the task chosen, centred on the member under the cursor -- its activity when its wake-up
        plays that task and goes on; nothing while no thread of it is read."""
        view = self.query_one("#teams-sequence", SequenceView)
        key, member = self._chosen(), self.query_one("#teams-strip", TaskStrip).member
        if key is None or key not in self.threads.threads or member is None:
            view.clear()
            return
        view.show(self.threads.sequence(key, member), self._activities_of(key, member), key[0])

    def _activity_moved(self) -> None:
        """What a wake-up does changed: the head of the sequence drawn again, when a thread of it is read."""
        key, member = self._chosen(), self.query_one("#teams-strip", TaskStrip).member
        if key is not None and key in self.threads.threads and member is not None:
            self.query_one("#teams-sequence", SequenceView).activity(self._activities_of(key, member))

    def _activities_of(self, key: tuple[str, str], member: str) -> dict:
        """-> the activity of `member` when its wake-up plays the task of `key` and goes on, by its name; {} else."""
        activity = self._activities.get(member)
        return {member: activity} if (activity is not None and activity.task == key[1]
                                      and member not in self._over) else {}

    def spin(self, frame: int) -> None:
        """One frame of the spinner: the tasks of the band a wake-up plays."""
        if self.is_attached:
            self.query_one("#teams-strip", TaskStrip).spin(frame)

    def action_back(self) -> None:
        """`escape`: the dashboard closed; the frame expanded folded back; from the band or the sequence back to the
        members; anywhere else, nothing focused."""
        if self._board:
            self.open_board(False)
        elif self._expanded is not None:
            self.expand(None)
        elif self.screen.focused in (self.query_one("#teams-strip"), self.query_one("#teams-sequence")):
            self.query_one("#teams-members", DataTable).focus()
        else:
            self.screen.set_focus(None)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """`enter` or a double click on a member: its run, read in a tab of the dialogue."""
        if event.data_table.id == "teams-members":
            self.inspect_member()

    def focus_table(self) -> None:
        table = self.query_one("#teams-list", DataTable)
        if self.screen.has_class("-narrow"):
            table = self.query_one("#teams-members", DataTable)    # the menu is folded: the members take the keys
        if table.row_count:
            table.focus()
        else:
            self.screen.set_focus(None)

    def step_team(self, by: int) -> None:
        """`[` and `]`: the team before or after the one chosen -- what the folded menu changes."""
        names = [one.team for one in self.badges]
        if not names:
            return
        at = names.index(self.team) if self.team in names else 0
        chosen = names[(at + by) % len(names)]
        self.query_one("#teams-list", DataTable).move_cursor(row=names.index(chosen))
        self.run_worker(self.choose(chosen))

    # ---------- a member ----------
    def _row_under_cursor(self) -> MemberRow | None:
        """-> the line of the members under the cursor: a member, and the open task it says; None without one."""
        state = self.state
        if state is None or state.started is None:
            return None
        row = self.query_one("#teams-members", DataTable).cursor_row
        return self._rows[row] if 0 <= row < len(self._rows) else None

    def _member_under_cursor(self):
        """-> the member of the line under the cursor, whole; None without one."""
        row = self._row_under_cursor()
        return row.member if row is not None else None

    def inspect_member(self) -> None:
        """`i`, `enter` on a member: the run of its line read in a tab of the dialogue -- on a task's line, the run it
        holds there; a member without a run (none yet, `?` before a launch, `—` after a reset) says so on the remedy
        line, and nothing is read."""
        row = self._row_under_cursor()
        member = row.line if row is not None else None
        if member is None or self.team is None:
            self.post_message(self.Refused("no member under the cursor"))
            return
        if not member.run or member.run in ("?", palette.NONE) or not member.path:
            self.post_message(self.Refused(f"{member.member} has no run to inspect"))
            return
        self.post_message(self.MemberAsked(self.team, member.member, member.path, member.run, member.how == "running"))

    async def chat_member(self) -> None:
        """`C` on a member: a conversation with its agent under the root of the team -- the folder of the `path` its
        declaration says (`team declaration --json`), resolved from the house (`faces.root_of`), never a path the post
        composes --, through the overlay of a new run's parameters (`ask_run`), prefilled from the agent's status, the
        root said in its title: `enter` asks the conversation with the flags chosen and the member's vector as its row
        says it (`team status --json`, `members[].vector`, passed as given), `escape` asks nothing. A member
        without a path, or a declaration without one, says so on the remedy line."""
        row = self._row_under_cursor()
        member = row.line if row is not None else None
        if member is None or self.team is None:
            self.post_message(self.Refused("no member under the cursor"))
            return
        if not member.path:
            self.post_message(self.Refused(f"{member.member} has no agent to talk with"))
            return
        team = self.team
        found, face = await faces.declaration(self.house, team)
        root = faces.root_of(self.house, found) if face.rc == 0 and found is not None else None
        if root is None:
            self.post_message(self.Refused(said_of(face) if face.rc != 0 else f"{team}: the declaration says no path"))
            return
        path, name, vector = member.path, member.member, member.vector
        line = await read_line(self, self.house, AgentLine(path))
        ask_run(self, self.house, f"a new run of {palette.agent_label(path, self.house)} under "
                f"{palette.root_mark(rooted_name(root))}", line,
                lambda flags, named: self.post_message(self.ChatAsked(team, name, path, root, flags, named, vector)))

    def member_detail(self) -> None:
        """`d`: the member under the cursor whole -- its run, its tasks, the posts not delivered
        to it yet, the answers of the others it has not seen -- in an overlay."""
        member = self._member_under_cursor()
        if member is None or self.team is None:
            self.post_message(self.Refused("no member under the cursor"))
            return
        self.app.push_screen(EventScreen(Text(f"{self.team} · {member.member}"), lambda: palette.member_detail(member),
                                         label="member"))

    async def member_responses(self) -> None:
        """`a`: the responses of the member under the cursor (`team responses --json --agent`), in an overlay."""
        member = self._member_under_cursor()
        if member is None or self.team is None:
            self.post_message(self.Refused("no member under the cursor"))
            return
        found, face = await faces.responses(self.house, self.team, member.member)
        if face.rc != 0:
            self.post_message(self.Refused(said_of(face)))
            return
        self.app.push_screen(EventScreen(Text(f"{self.team} · {member.member} · {len(found)} response(s)"),
                                         lambda: palette.responses_text(found), label="responses"))

    # ---------- the overlays of the team ----------
    async def show_journal(self) -> None:
        """`l`: the team's whole journal (`team log <name> --json`) in an overlay."""
        if self.team is not None:
            await journal_of(self, self.house, self.team)

    def show_ceremonies(self) -> None:
        """`c`: the ceremonies of the team chosen, in an overlay -- its table, the detail of the line under the cursor,
        `g` rings it at hand (as the principal chosen there), `enter` leads to the task of its last ring."""
        state = self.state
        if self.team is None or state is None or state.started is None:
            self.post_message(self.Refused("no team started under the cursor"))
            return
        team, owner = self.team, state.owner
        senders = ((owner,) if owner else ()) + state.principals

        def ring(name: str, sender: str | None) -> None:
            self._play(gestures.ring(team, name, sender, owner))

        def chosen(task: str | None) -> None:
            if task:
                self.post_message(self.TaskAsked(team, task))
        self.app.push_screen(CeremoniesScreen(team, state, senders, ring), chosen)

    # ---------- the gestures ----------
    def _play(self, argv: list[str] | None, then: Callable[[], Awaitable[None]] | None = None,
              refused: Callable[[str], None] | None = None) -> None:
        if argv is None:
            return
        self._playing += 1
        self.run_worker(self._played(argv, then, refused), group=GESTURE)

    async def _played(self, argv: list[str], then: Callable[[], Awaitable[None]] | None = None,
                      refused: Callable[[str], None] | None = None) -> None:
        """ONE gesture: the argv shown, played as it is; a refusal on the remedy line -- and to `refused`, the form
        the gesture was asked from --, the team read again; `then` once the gesture played, never after a refusal."""
        try:
            ticks = list(argv[:2]) == ["team", "tick"]
            app = self.app                       # the watcher of the tick tells it from a thread of its own
            if ticks:
                self._ticking += 1
            try:
                face = await play_gesture(argv, self.house,
                                          ended=(lambda ended: self._tick_ended(app, ended)) if ticks else None)
            except OSError:
                if ticks:
                    self._ticking -= 1
                raise
            if not live(self):
                return
            if face.rc != 0:
                self.post_message(self.Refused(said_of(face)))
                if refused is not None:
                    refused(said_of(face))
            else:
                self.post_message(self.Played(argv))
            self.reread()
            if face.rc == 0 and then is not None:
                await then()
        finally:
            self._playing -= 1

    def _tick_ended(self, app, face) -> None:
        """A tick started apart by `T` ended -- told from its watcher's thread: seen on the post's loop."""
        try:
            app.call_from_thread(self._tick_seen, face)
        except RuntimeError:
            pass                                 # the post has left: nobody to tell

    def _tick_seen(self, face) -> None:
        """The end of a tick started apart seen: its refusal on the remedy line, the team read again."""
        self._ticking -= 1
        if not live(self):
            return
        if face.rc != 0:
            self.post_message(self.Refused(said_of(face)))
        self.reread()

    def _confirmed(self, title: str, argv: list[str] | None, expect: str | None = None,
                   detail: Text | None = None) -> None:
        """The gesture asked in an overlay -- under `detail`, what it would do --; `enter` plays it -- under `expect`,
        once the name is typed."""
        if argv is None:
            self.post_message(self.Refused("nothing to play here: no team or member under the cursor"))
            return

        def chosen(go: bool | None) -> None:
            if go:
                self._play(argv)
        self.app.push_screen(ConfirmScreen(title, expect, detail), chosen)

    async def stop_all(self, then: Callable[[], Awaitable[None]] | None = None,
                       refused: Callable[[str], None] | None = None) -> None:
        """`X`: the season of the team stopped -- on the team's name typed --, what it stops named as `team status
        --json` says it at that moment (`palette.stop_named`): each open task, who holds it, each recurrence silent
        until the next start; `escape` stops nothing. `then` plays once the stop confirmed is played -- the form it was
        asked from giving way to the season's form, off season (`season_again`); a stop refused keeps the form and goes
        to `refused`, its line of state."""
        team = self.team
        argv = gestures.stop(team, whole=True)
        if team is None or argv is None:
            self.post_message(self.Refused("nothing to play here: no team under the cursor"))
            return
        self._playing += 1                       # until the confirmation stands: a gesture under way
        try:
            found, face = await faces.state(self.house, team)
            if face.rc != 0 or found is None:
                self.post_message(self.Refused(said_of(face) if face.rc != 0 else f"{team}: no state said by team status"))
                return
            state = TeamState.read(found)
            detail = palette.stop_named(state) if state.started is not None else None

            def chosen(go: bool | None) -> None:
                if go:
                    self._play(argv, then, refused)
            await self.app.push_screen(ConfirmScreen(f"stop the season of {team}", team, detail), chosen)   # mounted: its line focused
        finally:
            self._playing -= 1

    async def delete_team(self) -> None:
        """`D`: the team chosen deleted -- what `team delete --json` would remove shown, the agents the face says the
        team alone declares as CHECKS (none checked: `space` checks one, and the verb gains its `--agent`), the
        `--yes` verb played once the team's name is typed; a refusal of the dry run (`team-busy`) on
        the remedy line."""
        team = self.team
        if team is None:
            self.post_message(self.Refused("no team under the cursor"))
            return
        found, face = await faces.delete(self.house, team)
        if face.rc != 0 or found is None:
            self.post_message(self.Refused(said_of(face) if face.rc != 0 else f"{team}: nothing said by team delete"))
            return
        name = str(found.get("name") or team)
        agents = tuple((str(one), str(one)) for one in found.get("agents") or [])

        def recompose(checked: list[str]) -> Text | None:
            return palette.delete_said(found, tuple(checked))

        def chosen(result: object) -> None:
            if result is None or result is False:
                return
            self._play(gestures.delete(team, list(result) if isinstance(result, list) else []))
        self.app.push_screen(ConfirmScreen(f"delete the team {name}" + (f" ({team})" if name != team else ""),
                                           team, palette.delete_said(found),
                                           checks=agents, recompose=recompose, help=palette.AGENTS_CHECK_HELP), chosen)

    def rename_team(self) -> None:
        """`r`: the team chosen renamed -- one field, the new name; `enter` plays `team rename <team> <new>`; the team renamed is chosen once the teams are read again."""
        team = self.team
        if team is None:
            self.post_message(self.Refused("no team under the cursor"))
            return
        fields = (Field("new", "new name", "line", palette.RENAME_HELP, example=f"e.g. {team}-2"),)

        def argv_of(values: dict) -> list[str] | None:
            return gestures.rename(team, values["new"])

        def made(argv: object) -> None:
            if argv:
                self._want = list(argv)[3]
                self._play(list(argv))
        self.app.push_screen(GestureScreen(f"rename the team {team}", fields, argv_of, missing="a new name",
                                           focus="new"), made)

    def toggle_pause(self) -> None:
        """`P`: the team chosen paused -- or resumed when the face says it paused --, written in an overlay: `as` (the
        owner, then the principals)."""
        state = self._started_state()
        if state is None:
            return
        team, owner, paused = self.team, state.owner, state.paused is not None

        def argv_of(values: dict) -> list[str] | None:
            return gestures.pause(team, paused, values["as"], owner)
        fields = (Field("as", "as", "list", palette.AS_HELP, senders_of(state), value=owner),)
        self.app.push_screen(GestureScreen(f"{'resume' if paused else 'pause'} {team}", fields, argv_of,
                                           palette.pause_head(paused)), self._play)

    def tick(self) -> None:
        """`T`: one advance of the team, now."""
        self._confirmed(f"tick {self.team}", gestures.tick(self.team))

    def reset_member(self) -> None:
        """`R`: the run of the member under the cursor forgotten -- on the member's name typed."""
        member = self._member_under_cursor()
        name = member.member if member is not None else None
        self._confirmed(f"forget the run of {name}", gestures.reset(self.team, name), name)

    def new_task(self) -> None:
        """`n`: a new task of the team chosen, written in an overlay -- its name, `to`, `as`, its message."""
        started = self.state is not None and self.state.started is not None
        ask_new_task(self, {self.team: self.state} if started else {}, self.team, choose=False)

    def _face_of(self, team: str) -> TeamState | None:
        """-> the face of `team` as the tab holds it -- the team chosen alone --, None for another team."""
        return self.state if self.state is not None and self.state.team == team else None

    def _started_state(self) -> TeamState | None:
        state = self.state
        if self.team is None or state is None or state.started is None:
            self.post_message(self.Refused("no team started under the cursor"))
            return None
        return state

    def raise_budget(self) -> None:
        """`B`: the team's budget raised -- its budget and its wake-ups prefilled from the face, said above the fields;
        a field changed alone composes its argument, nothing changed plays nothing."""
        state = self._started_state()
        if state is None:
            return
        team, owner = self.team, state.owner
        cap, bound = (state.budget or {}).get("cap"), state.launches.get("bound")
        usd = f"{float(cap):.2f}" if isinstance(cap, (int, float)) else ""
        launches = str(bound) if isinstance(bound, int) else ""

        def changed(typed: str, before: str, kind) -> str | None:
            try:
                return typed if typed and (not before or kind(typed) != kind(before)) else None
            except ValueError:
                return typed or None

        def argv_of(values: dict) -> list[str] | None:
            return gestures.budget(team, changed(values["budget"], usd, float), changed(values["launches"], launches, int),
                                   values["as"], owner)
        fields = (Field("budget", "budget", "line", palette.BUDGET_HELP, value=usd, number="number",
                        example=palette.BUDGET_EXAMPLE),
                  Field("launches", "launches", "line", palette.LAUNCHES_HELP, value=launches, number="integer",
                        example=palette.LAUNCHES_EXAMPLE),
                  Field("as", "as", "list", palette.AS_HELP, senders_of(state), value=owner))
        self.app.push_screen(GestureScreen(f"raise the budget of {team}", fields, argv_of, palette.budget_head(state),
                                           missing="nothing changed"), self._play)

    async def show_inbox(self) -> None:
        """`b`: the owner's inbox of the team chosen (`inbox_of`)."""
        state = self._started_state()
        if state is not None and self.team is not None:
            await inbox_of(self, self.house, self.team, state)

    async def show_declaration(self) -> None:
        """`e`: the declaration of the team chosen (`team declaration --json`) in an overlay, read only, rendered as
        markdown (`palette.declaration_markdown`) -- its path, the verdict of `start`'s judge, the keys a new start
        would change, `TEAM.md` whole."""
        team = self.team
        if team is None:
            self.post_message(self.Refused("no team under the cursor"))
            return
        found, face = await faces.declaration(self.house, team)
        if face.rc != 0 or found is None:
            self.post_message(self.Refused(said_of(face)))
            return
        self.app.push_screen(EventScreen(Text(f"{team} · {found.get('path', 'TEAM.md')}"),
                                         lambda: Text(palette.declaration_markdown(found)), label="declaration",
                                         markdown=True))

    async def open_form(self, team: str | None = None, given: dict | None = None, section: str | None = None) -> None:
        """`N` (no team), `E` (`section` `team`) and `S` (the team chosen): the form of the team's values file --
        TEAM.md for `N` and `E` (`team_form`), SEASON.md for `S` (`season_form`) --, ONE class for both
        (`ValuesForm`). `given` -- the values and the lines a refused call left -- opens the form again on them. The
        opening counts as a gesture under way until the form stands (`settled` waits for it): a key typed meanwhile
        goes to its field, never to the tab under it."""
        self._playing += 1
        try:
            if team is None or section == "team":
                await self.team_form(team, given)
            else:
                await self.season_form(team, given)
        finally:
            self._playing -= 1

    async def _read(self, team: str | None) -> tuple[list[dict], dict | None] | None:
        """-> the templates `team templates --json` says, and the declaration of `team` (`team declaration --json`;
        None without a team); None, the refusal on the remedy line, when a face is refused."""
        found, face = await faces.templates(self.house)
        if face.rc != 0:
            self.post_message(self.Refused(said_of(face)))
            return None
        if team is None:
            return found, None
        read, face = await faces.declaration(self.house, team)
        if face.rc != 0 or read is None:
            self.post_message(self.Refused(said_of(face) if face.rc != 0 else f"{team}: no declaration said"))
            return None
        return found, read

    def _made(self, team: str | None, section: str) -> Callable[[dict | None], None]:
        """-> what a form's result plays: its declares, then its start (`_declared`)."""
        def made(result: dict | None) -> None:
            if result is None:
                return
            self._playing += 1
            self.run_worker(self._declared(result, team, section), group=GESTURE)
        return made

    def _candidate(self, team: str, season: bool):
        """-> what asks pp-team the view by member of a text typed -- `team declaration --text-file - [--season]`
        (`faces.candidate`): its `declared.views`, its verdict and its gap as the side pane shows them, or its refusal
        as the verb said it."""
        async def asked(text: str) -> tuple[Text | None, str | None]:
            found, face = await faces.candidate(self.house, team, text, season)
            if found is None or not isinstance(found.get("declared"), dict):
                return None, (said_of(face) if face.rc != 0
                              else str(((found or {}).get("verdict") or {}).get("refusal") or "no declaration said"))
            return palette.member_view(found["declared"].get("views"), (found.get("verdict") or {}).get("refusal"),
                                       found.get("pending")), None
        return asked

    def _documents(self, found: list[dict], team: str | None, roles: Callable[[dict], list[str]],
                   excluded: frozenset[str] = frozenset(),
                   locked: Callable[[dict], tuple[list[tuple[str, str]], str]] | None = None,
                   season: bool = False) -> Documents:
        """-> what a form's list of documents knows and asks: the documents `team templates --json` says, the role keys
        `roles` gives for the form's values, the documents `excluded`, the lines a season's preset gives (`locked`);
        the text of a document by `team templates --render` -- the team standing, on the form's file as typed
        (`--team <team> --text-file -`, `--season` for SEASON.md's form), its values otherwise --, its source by `team
        document --json`, its writing by `team document --new | --body-file - | --delete` -- the post writes no file."""
        async def render(document: str, values: dict[str, str], file: str | None) -> tuple[str | None, str | None]:
            said, face = await faces.render(self.house, document, values, team, file, season)
            return (str(said.get("text") or ""), None) if said is not None else (None, said_of(face))

        async def source(document: str) -> tuple[str | None, str | None]:
            said, face = await faces.document(self.house, document)
            return (str(said.get("text") or ""), None) if said is not None else (None, said_of(face))

        async def written(document: str, action: str, body: str | None) -> str | None:
            face = await faces.document_written(self.house, document, action, body)
            return None if face.rc == 0 else said_of(face)

        async def reread() -> list[dict]:
            again, face = await faces.templates(self.house)
            return documents_of(again if face.rc == 0 else found)
        return Documents(documents_of(found), roles, render, source, written, reread, excluded,
                         locked or (lambda values: ([], "")))

    async def team_form(self, team: str | None, given: dict | None = None) -> None:
        """`N` and `E`: TEAM.md in its form -- its sections Team (the name of a team to be born, its description, its
        roles), Preset (its preset among the presets of a team `team templates --json` says, then a field per value
        that preset declares -- `values:`), Members (the members, the root, the principals, the edges `<member>... ->
        <member>`), Documents (the list of every document, each given to `all` or to the keys of the roles as typed --
        its lines of `documents:` --, `n`, `e`, `d` played by `team document`; `_documents`), Limits and the owner's
        word, each written by `team declare` (`--report`, `--no-report`, `--body-file -`) --, each field opened on what
        TEAM.md writes, read in the text of `team declaration --json` (`files.read`), never in the file. The side pane
        shows, as each section says it, TEAM.md as `team declare` will write it, made anew at each change, or what each
        member reads as the face says it (`declared.views`): the post computes no view, and once a field changes the
        view is asked of pp-team on the text typed once the keys pause (`team declaration --text-file -`), the last
        call alone shown, its refusal on the line of state. `enter` plays `team declare` for the keys changed
        alone (`gestures.declared_values`), a change the verb cannot write said on the line of state; read only in
        season; nothing starts here. `N` opens on the first preset of a team, its members' names; `N` on the name of a
        team that stands plays nothing; a team to be born opens its limits on `BORN_LIMITS`, played as keys typed."""
        given = dict(given or {})
        typed = dict(given.get("values") or {})
        read_both = await self._read(team)
        if read_both is None:
            return
        found, read = read_both
        presets = {str(one.get("template")): one for one in found
                   if one.get("kind") == "preset" and isinstance(one.get("members"), list)}
        standing = team is not None
        if not standing and not presets:
            self.post_message(self.Refused("no preset of a team said by team templates"))
            return
        text = str((read or {}).get("text") or "")
        opened, body = files.read(text), files.split(text)[1].strip()
        declared = (read or {}).get("declared") if isinstance((read or {}).get("declared"), dict) else {}
        first = next(iter(presets), None)
        value_of = lambda key, otherwise: typed.get(key, otherwise)
        block = lambda key: "\n".join(opened[key]) if isinstance(opened.get(key), list) else ""
        scalar = lambda key: "" if isinstance(opened.get(key), list) else str(opened.get(key) or "")
        members_of = lambda name: [str(one) for one in (presets.get(str(name or "")) or {}).get("members") or []]
        listed = tuple((f"{name} -- {one.get('description', '')}", name) for name, one in presets.items())
        S = palette.TEAM_SECTIONS
        parts = (
            Part("team", S["team"], ((Field("name", "name", "line", palette.TEAM_NAME_HELP, value=value_of("name", "")),)
                                     if not standing else ())
                 + (Field("description", "description", "line", palette.DESCRIPTION_HELP,
                          value=value_of("description", scalar("description"))),
                    Field("roles", "roles", "text", palette.ROLES_HELP, value=value_of("roles", block("roles"))))),
            Part("preset", S["preset"], (Field("template", "preset", "list", palette.PRESET_HELP, listed,
                                               value=value_of("template", scalar("template") if standing else first),
                                               blank=palette.PRESET_BLANK if standing else None),
                                         Field("values", "values", "values", "",
                                               value=value_of("values", block("values"))))),
            Part("members", S["members"], (Field("agents", "members", "text", palette.MEMBERS_HELP,
                                                 value=value_of("agents", block("agents") if standing
                                                                else "\n".join(members_of(first)))),
                                           Field("root", "root", "line", palette.ROOT_HELP,
                                                 value=value_of("root", scalar("root"))),
                                           Field("principals", "principals", "line", palette.PRINCIPALS_HELP,
                                                 value=value_of("principals", " ".join(opened.get("principals") or [])
                                                                if isinstance(opened.get("principals"), list) else ""),
                                                 example=palette.PRINCIPALS_EXAMPLE),
                                           Field("reports", "reports", "text", palette.REPORTS_HELP,
                                                 value=value_of("reports", block("reports")),
                                                 example=palette.REPORTS_EXAMPLE))),
            Part("documents", S["documents"], (Field("documents", "documents", "documents", "",
                                                     value=value_of("documents", block("documents"))),)),
            Part("limits", S["limits"], tuple(
                Field(key, key, "line", help, value=value_of(key, scalar(key) if standing else BORN_LIMITS.get(key, "")),
                      number=number, example=example)
                for key, help, number, example in (("budget", palette.LIMIT_HELP, "number", palette.BUDGET_EXAMPLE),
                                                   ("launches", palette.LIMIT_HELP, "integer", palette.LAUNCHES_EXAMPLE),
                                                   ("parallel", palette.PARALLEL_HELP, "integer", palette.PARALLEL_EXAMPLE),
                                                   ("timeout", palette.LIMIT_HELP, "number", palette.TIMEOUT_EXAMPLE),
                                                   ("schedule", palette.SCHEDULE_HELP, "text", palette.SCHEDULE_EXAMPLE)))),
            Part("word", S["word"], (Field("body", "the owner's word", "text", palette.WORD_HELP,
                                           value=value_of("body", body)),)))
        def preview(values: dict) -> str:
            scalars = {key: (json.dumps(str(values.get(key) or "").strip(), ensure_ascii=False)
                             if key == "description" else str(values.get(key) or "").strip())
                       for key in ("description", "template", "root", "budget", "launches", "parallel", "timeout",
                                   "schedule")
                       if str(values.get(key) or "").strip() and str(values.get(key) or "").strip() != scalar(key)}
            blocks = {key: files.lines_of(values.get(key)) for key in ("agents", "roles", "reports", "documents", "values")
                      if files.lines_of(values.get(key)) != files.lines_of(block(key))}
            principals = str(values.get("principals") or "").split()
            if principals != (opened.get("principals") if isinstance(opened.get("principals"), list) else []):
                blocks["principals"] = principals
            typed_body = str(values.get("body") or "").strip()
            return files.written(text, scalars, blocks, (typed_body + "\n") if typed_body != body else None)

        def plays(values: dict, rows: list, start: bool) -> tuple | str:
            name = team or str(values.get("name") or "").strip()
            if not standing and name in [one.team for one in self.badges]:
                return f"{name} stands already: E changes it"
            made = gestures.declared_values(name, opened, values, default_members=members_of(values.get("template"))
                                            if not standing else (), body=body)
            if isinstance(made, str):
                return made
            return ([gestures.body_input(made, values)], None) if made else palette.NOTHING_CHANGED

        def refill(key: str, values: dict) -> dict:
            return {"agents": "\n".join(members_of(values.get("template")))} if key == "template" and not standing else {}
        form = ValuesForm(f"the team {team}" if standing else palette.NEW_TEAM,
                          palette.season_head(declared) if standing else Text(""), parts, plays, preview, text,
                          "TEAM.md", focus=None if standing else "name", refill=refill,
                          readonly=palette.IN_SEASON if in_season(read) else None,
                          view=palette.member_view(declared.get("views"), ((read or {}).get("verdict") or {}).get("refusal"),
                                                   (read or {}).get("pending")) if standing else "",
                          candidate=self._candidate(team, False) if standing else None,
                          documents=self._documents(found, team, lambda values: role_keys(values.get("roles"))),
                          preset_values=lambda values: declared_by(presets, values))
        await self.app.push_screen(form, self._made(team, "team"))     # mounted: its focus set

    async def season_form(self, team: str, given: dict | None = None) -> None:
        """`S`: SEASON.md in its form -- its sections Preset (its preset among the presets of a season `team templates
        --json` says, then a field per value that preset declares -- `values:`), Documents (the list of the season's
        documents, the team's left out, the lines the preset gives locked -- `preset_lines` --, each other given to
        `all` or to the keys TEAM.md declares), Launch (`work:` read only; the budget, the launches and the silence of
        the season), Members (the table of its lines, `all` then one per member, each edited in its `ProfileScreen`,
        then the context of the season, read in percent as `team start` writes it -- `SEASON_CONTEXT` when SEASON.md
        writes none, off season alone) and the season's word, written by `team declare --season --body-file -` --,
        opened on what SEASON.md writes, read in the `season.text` of `team declaration --json`, never in the file --
        the budget, the launches, the silence and the context on the season's limits SEASON.md writes
        (`declared.season.limits`); the lines from `declared.season` (`season_lines`), the providers of `agent
        providers --json`, the packages `required` greyed. The side pane shows, as each section says it, SEASON.md as
        `team declare --season` will write it, made anew at each change, or what each member reads as the face says it
        (`declared.views`): the post computes no view, and once a field changes the view is asked of pp-team on the
        text typed once the keys pause (`team declaration --text-file -`), the last call alone shown, its refusal on
        the line of state. `enter` plays `team declare --season` for the keys changed alone, the limits and the lines
        of the members with them (`gestures.season`: a limit passed only changed, a member's profile after its
        `--member`); `ctrl+s` plays it -- the context at the form's default and the harness of the post given too --,
        then `team start` without a flag of the season, which opens the season written; a form left as it is writes
        nothing; read only in season, `X` asking the stop."""
        given = dict(given or {})
        typed = dict(given.get("values") or {})
        read_both = await self._read(team)
        if read_both is None:
            return
        found, read = read_both
        if not isinstance(read.get("declared"), dict):
            self.post_message(self.Refused(str((read.get("verdict") or {}).get("refusal") or "the declaration is refused")))
            return
        declared = read["declared"]
        presets = {str(one.get("template")): one for one in found
                   if one.get("kind") == "preset" and not isinstance(one.get("members"), list)}
        text = str((read.get("season") or {}).get("text") or "")
        opened, body = files.read(text), files.split(text)[1].strip()
        found_state, _ = await faces.state(self.house, team)
        state = TeamState.read(found_state or {"team": team, "started": None})
        providers = await play_verb(["agent", "providers", "--json"], self.house)
        offered = {str(one.get("provider", "")): one for one in objects(providers)}
        value_of = lambda key, otherwise: typed.get(key, otherwise)
        block = lambda key: "\n".join(opened[key]) if isinstance(opened.get(key), list) else ""
        scalar = lambda key: "" if isinstance(opened.get(key), list) else str(opened.get(key) or "")
        listed = tuple((f"{name} -- {one.get('description', '')}", name) for name, one in presets.items())
        S = palette.SEASON_SECTIONS
        parts = (
            Part("preset", S["preset"], (Field("template", "preset", "list", palette.SEASON_PRESET_HELP, listed,
                                               value=value_of("template", scalar("template")),
                                               blank=palette.PRESET_BLANK),
                                         Field("values", "values", "values", "",
                                               value=value_of("values", block("values"))))),
            Part("documents", S["documents"], (Field("documents", palette.DOCUMENTS_SEASON, "documents", "",
                                                     value=value_of("documents", block("documents"))),)),
            Part(ValuesForm.LAUNCH, S["launch"], (Field("work", "work", "text", palette.WORK_HELP,
                                                        value=block("work") or scalar("work"), fixed=True),)),
            Part(ValuesForm.MEMBERS, S["members"], ()),
            Part("word", S["word"], (Field("body", "the season's word", "text", palette.WORD_HELP,
                                           value=value_of("body", body)),)))
        opened_lines = season_lines(state, declared, tuple(offered))
        paths = {one.member: one.path for one in opened_lines[1:]}
        lines = ([dataclasses.replace(one, path=one.path or paths.get(one.member)) for one in given["lines"]]
                 if given.get("lines") else copy.deepcopy(opened_lines))
        written = declared.get("season") if isinstance(declared.get("season"), dict) else {}
        limits = written.get("limits") if isinstance(written.get("limits"), dict) else {}
        declared_limits = declared.get("limits") or {}
        opened_context = shown_percent(limits.get("context")) or ("" if in_season(read) else palette.SEASON_CONTEXT)

        def preview(values: dict) -> str:
            scalars = ({"template": str(values.get("template") or "")}
                       if str(values.get("template") or "") and str(values.get("template") or "") != scalar("template")
                       else {})
            blocks = {key: files.lines_of(values.get(key)) for key in ("documents", "values")
                      if files.lines_of(values.get(key)) != files.lines_of(block(key))}
            typed_body = str(values.get("body") or "").strip()
            return files.written(text, scalars, blocks, (typed_body + "\n") if typed_body != body else None)

        def plays(values: dict, rows: list, start: bool) -> tuple | str:
            keys = gestures.declared_values(team, opened, values, season=True, body=body)
            if isinstance(keys, str):
                return keys
            # `enter` writes what the form changed of what it opened on; `ctrl+s` also the context at the form's
            # default and the harness of the post, which the season opens with
            launched = gestures.season(rows, opened_lines, values["season-budget"], values["season-launches"],
                                       limits if start else {**limits, "context": opened_context},
                                       state.required, self.flags if start else (), values["season-silence"],
                                       values["season-context"])
            made = gestures.body_input(gestures.season_declared(team, keys, launched), values)
            started = gestures.season_started(team) if start else None
            if not made and started is None:
                return palette.NOTHING_CHANGED
            return ([made] if made else []), started

        async def offer() -> dict[str, dict]:
            return offered
        silenced = ("SEASON.md" if limits.get("silence") is not None
                    else "TEAM.md" if declared_limits.get("silence") is not None else None)
        helps = {"budget": palette.season_limit_help("budget", declared_limits.get("budget")),
                 "silence": palette.season_silence_help(silenced, declared_limits.get("silence")),
                 "launches": palette.season_limit_help("launches", declared_limits.get("budget-launches")),
                 "budget-label": "season budget",
                 "launches-label": "season launches"}
        form = ValuesForm(palette.season_title(team, state), palette.season_head(declared), parts, plays, preview,
                          text, "SEASON.md", lines=lines,
                          limits={"budget": value_of("season-budget", shown_number(limits.get("budget"))),
                                  "launches": value_of("season-launches", shown_number(limits.get("budget-launches"))),
                                  "silence": value_of("season-silence", shown_number(limits.get("silence"))),
                                  "context": value_of("season-context", opened_context)},
                          providers=list(offered), offer=offer, required=state.required, helps=helps,
                          view=palette.member_view(declared.get("views"), (read.get("verdict") or {}).get("refusal"),
                                                   read.get("pending")),
                          candidate=self._candidate(team, True),
                          readonly=palette.IN_SEASON if in_season(read) else None,
                          stop=(lambda: self.stop_all(then=lambda: self.season_again(form, team), refused=form.say))
                          if in_season(read) else None,
                          documents=self._documents(found, team, lambda values: ["all"] + [
                              str(one.get("role")) for one in declared.get("roles") or [] if isinstance(one, dict)],
                              excluded=frozenset(document for one in declared.get("documents") or []
                                                 if isinstance(one, dict) for document in one.get("team") or []),
                              locked=lambda values: preset_lines(presets, declared, values), season=True),
                          preset_values=lambda values: declared_by(presets, values))
        await self.app.push_screen(form, self._made(team, "season"))     # mounted: its focus set

    async def season_again(self, form: ValuesForm, team: str) -> None:
        """The season of `team` stopped from its form: that form closed, the form of its season opened in its place,
        read anew -- off season, written and started from there."""
        if form.is_attached and self.app.screen is form:
            await form.dismiss(None)
        if live(self):
            await self.open_form(team, None, "season")

    async def _declared(self, result: dict, team: str | None, section: str = "season") -> None:
        """What the form gave, played in its order: each `team declare --json`, then the start, if any. A call refused
        -- or the last `declare` played writing a team its `verdict` says the start refuses -- says the refusal on the
        remedy line with the files written, plays nothing more (no start) and opens the form again on its values -- on
        the team that stands once TEAM.md is written, never a birth to play again; a start refused with no file
        written says its refusal alone. A team born is chosen once the teams are read again."""
        try:
            written: list[str] = []
            first = result["declares"][0] if result["declares"] else None
            name = (first[0] if isinstance(first, tuple) else first)[2] if first else team

            async def again(said: str) -> None:
                self.post_message(self.Refused(palette.declare_refused(said, written)))
                if written:
                    self._want = name
                    self.reread()
                standing = team or (name if "TEAM.md" in written else None)
                given = result["given"] if standing == team else {}
                await self.open_form(standing, {"values": given, "lines": result["lines"]}, section)
            verdict: dict = {"ok": True}
            for one in result["declares"]:
                argv, given = one if isinstance(one, tuple) else (one, None)    # a body goes on the verb's input
                face = await play_verb(argv, self.house, stdin=given)
                if not live(self):
                    return
                if face.rc != 0:
                    await again(said_of(face))
                    return
                written.append("SEASON.md" if "--season" in argv else "TEAM.md")
                said = next(iter(objects(face)), {})
                verdict = said.get("verdict") if isinstance(said.get("verdict"), dict) else {"ok": True}
                self.post_message(self.Played(argv))
            if team is None and result["declares"]:
                self._want = name
            if verdict.get("ok") is False:
                await again(f"pp-team: {verdict.get('refusal') or 'the next start refuses'}")
                return
            if result["start"] is not None:
                face = await play_gesture(result["start"], self.house)
                if not live(self):
                    return
                if face.rc != 0 and written:
                    await again(said_of(face))
                    return
                self.post_message(self.Refused(said_of(face)) if face.rc != 0 else self.Played(result["start"]))
            self.reread()
        finally:
            self._playing -= 1

    async def show_season(self) -> None:
        """`s`: the season of the team chosen READ ONLY -- its lines `all` and one per member from the state the tab
        read (`launch`, `members[].launch`, `season`, `limits` of `team status --json`), its side pane SEASON.md as it
        is written (`season.text` of `team declaration --json`, empty when that face is refused); `no season` on the
        remedy line for a team never started."""
        team, state = self.team, self.state
        if team is None or state is None or state.started is None:
            self.post_message(self.Refused(f"{team or 'the team'}: no season -- s shows the season of a started team"))
            return
        launch = state.launch or {}
        providers = tuple(str(launch["provider"]) for _ in [0] if launch.get("provider"))
        declared = {"agents": [{"member": one.member, "path": one.path} for one in state.members],
                    "root": None, "limits": state.limits}
        lines = season_lines(state, declared, providers)
        n, at = state.season.get("n"), str(state.season.get("at") or (state.started or {}).get("at") or "")
        read, face = await faces.declaration(self.house, team)
        if not live(self):
            return
        text = str(((read or {}).get("season") or {}).get("text") or "") if face.rc == 0 else ""

        async def offer() -> dict[str, dict]:
            return {}
        said = f"season {n if n is not None else palette.NONE}{palette.SEP}started {palette.moment_of(at) if at else palette.NONE}"
        form = ValuesForm(f"season {n if n is not None else ''} of {team} -- read only".replace("  ", " "),
                          Text(f"{len(state.members)} member(s){palette.SEP}{said}"),
                          (Part(ValuesForm.LAUNCH, palette.SEASON_SECTIONS["launch"], ()),), None,
                          lambda values: text, text, file_title="SEASON.md",
                          lines=lines, limits={"budget": shown_number(state.season.get("budget")),
                                               "launches": shown_number(state.season.get("budget-launches"))},
                          providers=list(providers), offer=offer, required=state.required, readonly=said,
                          stop=lambda: self.stop_all(then=lambda: self.season_again(form, team), refused=form.say))
        self.app.push_screen(form)

    @property
    def keys(self) -> list[tuple[str, str]]:
        focused = self.screen.focused if self.is_attached else None
        if focused is not None and focused.id == "teams-strip":
            return list(TaskStrip.keys)
        if focused is not None and focused.id == "teams-sequence":
            return list(SequenceView.keys)
        return [("team:", ""), ("N", "new team"), ("E", "edit team"), ("n", "new task"), ("S", "season"), ("s", "season read only"), ("B", "budget"), ("b", "inbox"), ("e", "declaration"),
                ("P", "pause/resume"), ("X", "stop the season"), ("D", "delete team"), ("r", "rename"), ("T", "tick"), ("c", "ceremonies"), ("l", "journal"), ("member:", ""), ("enter", "its run"), ("C", "chat"), ("d", "detail"),
                ("a", "answers"), ("R", "forget its run"), ("u", "reload")]


def role_keys(text: object) -> list[str]:
    """-> the keys a document may be given to in the form of a team: `all`, then each key the field `roles` writes."""
    return ["all"] + [line.split()[0] for line in files.lines_of(str(text or ""))]


def documents_of(found: list[dict]) -> list[dict]:
    """-> the documents among what `team templates --json` says, the house's first, in their order."""
    documents = [one for one in found if isinstance(one, dict) and one.get("kind") == "document"]
    return [one for one in documents if one.get("origin") == "house"] + [one for one in documents
                                                                          if one.get("origin") != "house"]


def declared_by(presets: dict[str, dict], values: dict) -> list[dict] | None:
    """-> the values the preset a form chose declares, as `team templates --json` says them (`{name, description,
    default}` each); None when the form chose none."""
    chosen = values.get("template")
    if not chosen:
        return None
    return [one for one in (presets.get(str(chosen)) or {}).get("values") or [] if isinstance(one, dict)]


def preset_lines(presets: dict[str, dict], declared: dict, values: dict) -> tuple[list[tuple[str, str]], str]:
    """-> the lines of `documents:` the season's preset chosen gives, `(document, key)` each -- a key written as a hole
    `{name}` read in the form's values, else in those the declaration applies, else as the preset's default --: those
    of a key the form's own lines do not write, and those the form's line of their key keeps; and the preset's name."""
    name = str(values.get("template") or "")
    preset = presets.get(name) or {}
    typed = files.values_of(str(values.get("values") or ""))
    applied = {str(one.get("name")): str(one.get("value")) for one in declared.get("values") or []
               if isinstance(one, dict) and one.get("value") is not None}
    defaults = {str(one.get("name")): str(one.get("default")) for one in preset.get("values") or []
                if isinstance(one, dict) and one.get("default") is not None}

    def key_of(key: str) -> str:
        hole = key[1:-1] if key.startswith("{") and key.endswith("}") else None
        return (typed.get(hole) or applied.get(hole) or defaults.get(hole) or key) if hole else key
    written = files.documents_by(str(values.get("documents") or ""))
    found = []
    for line in preset.get("documents") or []:
        key = key_of(str((line or {}).get("key") or ""))
        found += [(str(document), key) for document in (line or {}).get("documents") or []
                  if key and (key not in written or str(document) in written[key])]
    return found, name


def in_season(read: dict | None) -> bool:
    """-> whether a team is in season, as `team declaration --json` says its last start: `started.state` `running`."""
    return ((read or {}).get("started") or {}).get("state") == "running"


def shown_number(value: object) -> str:
    """-> a number as a field shows it: `2`, `2.5`; empty for none."""
    return f"{value:g}" if isinstance(value, float) else str(value) if value is not None else ""


def shown_percent(value: object) -> str:
    """-> a share of the context window as its field shows it: `90` for `90%` as `team start` writes it; empty for
    none."""
    return str(value).strip().removesuffix("%").strip() if value is not None else ""


def senders_of(state: TeamState) -> tuple[tuple[str, str], ...]:
    """-> the principals a gesture posts as, as options: the owner first -- who writes no `--as` --, then the
    mandators."""
    return tuple((one, one) for one in ((state.owner,) if state.owner else ()) + state.principals)


def member_options(state: TeamState) -> tuple[tuple[str, str], ...]:
    """-> the members of the season as the options of a list, the root marked (`palette.ROOT_MARK`)."""
    return tuple((f"{one.member} {palette.ROOT_MARK}" if one.member == state.root else one.member, one.member)
                 for one in state.members)


def write_on(pane, state: TeamState, team: str, task: str, reply: object = None, inbox: dict | None = None,
             then: Callable[[list[str] | None], None] | None = None,
             play: Callable[[list[str]], Awaitable[str | None]] | None = None) -> None:
    """`m`: a note -- or a reply -- on `task` of `team`, written in an overlay pushed over the screen on top: its `kind`
    (`info` at the opening, or `ask`, a question the member owes an answer to; a reply is neither, and an `ask` beside
    a reply plays nothing), `to` (the members, the root marked; the root at the opening of a note, blank at the opening
    of a reply and again once a reply is chosen -- a note left blank goes to the holders, a reply to the author of what
    it answers, no `--to`), `as` (the owner, then the principals), `reply to` (the questions waiting
    for the owner on the task and the team's notices that wait for their answer, as the face's `waiting` lists them --
    and as `inbox`, the inbox the owner chose `reply` in, lists them: the face, read at its own round, may not hold them
    yet; `reply` chosen at the opening), the text. The argv made -- None on `escape` -- goes to `then`, the pane's
    `_play` without it; under `play`, it plays under the overlay (`GestureScreen`), which a refusal keeps open."""
    owner = state.owner
    asked = (state.waiting.get("questions") or []) + [one for one in state.waiting.get("notices") or [] if one.get("awaits")]
    held = {one.get("id") for one in asked}
    asked += [one for one in ((inbox or {}).get("questions") or []) + [
        one for one in (inbox or {}).get("notices") or [] if one.get("awaits")] if one.get("id") not in held]
    questions = tuple((palette.question_option(one), one.get("id")) for one in asked
                      if one.get("task") == task)
    members = member_options(state)
    root = state.root if state.root in {value for _, value in members} else None
    fields = (Field("kind", "kind", "list", palette.KIND_HELP, ((INFO, INFO), (ASK, ASK)), value=INFO),
              Field("to", "to", "list", palette.TO_HELP, members, blank="the holders",
                    value=root if reply is None else None),
              Field("as", "as", "list", palette.AS_HELP, senders_of(state), value=owner),
              Field("reply", "reply to", "list", palette.REPLY_HELP, questions, value=reply,
                    blank="nothing: a plain note"),
              Field("text", "text", "text", palette.TEXT_HELP))

    def argv_of(values: dict) -> list[str] | None:
        if values["kind"] == ASK and values["reply"] is not None:
            return None
        return gestures.post(team, values["text"], task, values["to"], values["reply"], values["as"], owner,
                             ask=values["kind"] == ASK)

    def missing(values: dict) -> str:
        if values["kind"] == ASK and values["reply"] is not None:
            return palette.ASK_REPLY_MISSING
        return palette.TEXT_MISSING

    def refill(key: str, values: dict) -> dict:
        """A reply chosen: `to` blank, the reply going to the author of what it answers; none, the root again."""
        return {"to": root if values.get("reply") is None else None} if key == "reply" else {}
    line = next((one for one in state.tasks if one.id == task), None)
    pane.app.push_screen(GestureScreen(f"write on {palette.task_title(line) if line else task} of {team}", fields,
                                       argv_of, missing=missing, focus="text", refill=refill, play=play),
                         then or (None if play else pane._play))


def ask_new_task(pane, states: dict[str, TeamState], team: str | None, choose: bool,
                 play: Callable[[list[str]], Awaitable[str | None]] | None = None) -> None:
    """`n`: a new task, written in an overlay -- under `choose` its team among those `states` holds, `team` first;
    its name (none: no `--name`), `to` (the members of the team; left on its root, no `--to`), `as`, its message,
    `every`, the period it comes back at (none: given once; typed: `--every` as typed, `team` judges it), and
    `context`, the context limit of a recurrence (passed as typed with a period only). Under `play`, it plays under the
    overlay (`GestureScreen`), which a refusal keeps open; else the pane's `_play` plays it."""
    if team is None or team not in states:
        pane.post_message(pane.Refused("a new task: choose a team started first"))
        return

    def members(name: str | None) -> tuple:
        state = states.get(name or team)
        return tuple((one.member, one.member) for one in state.members) if state is not None else ()

    def senders(name: str | None) -> tuple:
        state = states.get(name or team)
        return senders_of(state) if state is not None else ()
    fields = ((Field("team", "team", "list", palette.TEAM_HELP, tuple((one, one) for one in states), value=team),)
              if choose else ()) + (
        Field("name", "name", "line", palette.NAME_HELP, example=palette.NAME_EXAMPLE),
        Field("to", "to", "list", palette.ROOT_HELP, members(team), blank="the root"),
        Field("as", "as", "list", palette.AS_HELP, senders(team), value=states[team].owner),
        Field("message", "message", "text", palette.TASK_HELP),
        Field("every", "every", "line", palette.EVERY_HELP, example=palette.EVERY_EXAMPLE),
        Field("context", "context", "line", palette.CONTEXT_HELP, example=palette.CONTEXT_EXAMPLE))

    def argv_of(values: dict) -> list[str] | None:
        chosen = values.get("team") or team
        state = states.get(chosen)
        return gestures.post(chosen, values["message"], None, values["to"], None, values["as"],
                             state.owner if state is not None else None, values["name"], values["every"],
                             values["context"])

    def follow(values: dict) -> dict[str, tuple]:
        return {"to": members(values.get("team")), "as": senders(values.get("team"))} if choose else {}
    pane.app.push_screen(GestureScreen(f"a new task of {team}" if not choose else "a new task", fields, argv_of,
                                       missing="the task's message", focus="message", follow=follow, play=play),
                         None if play else pane._play)


async def inbox_of(pane, house: str, team: str, state: TeamState) -> None:
    """`b`: the owner's inbox of `team` (`team inbox --json`) in an overlay -- `enter` on a question writes its reply
    on its task (`write_on`, the question among its choices even when the team's face does not hold it yet) in an
    overlay pushed OVER the inbox: sent, the post played and the inbox read again; `escape`, nothing played -- the
    inbox back on top either way --; `x` marks the one message under the cursor read (`team inbox --seen --id`) and
    the overlay stays, `a` marks the inbox all read (`team inbox --seen`) and closes it; a refusal of a verb on the
    remedy line; a reply or a read that `team` refuses (`task-closed`, `team-unknown`, …) is said on the remedy line
    and under the inbox's list too, and the inbox stays open."""
    found, face = await faces.inbox(house, team)
    if face.rc != 0:
        pane.post_message(pane.Refused(said_of(face)))
        return
    held = {"inbox": found, "refused": None}

    async def played(argv: list[str]) -> bool:
        """ONE gesture of the inbox -- counted among the pane's gestures under way --: whether `team` played it; when
        it refused, its refusal is kept for the inbox to say."""
        pane._playing += 1
        try:
            done = await play_gesture(argv, house)
            if not live(pane):
                return False
            held["refused"] = said_of(done) if done.rc != 0 else None
            pane.post_message(pane.Refused(held["refused"]) if done.rc != 0 else pane.Played(argv))
            pane.reread()
            return done.rc == 0
        finally:
            pane._playing -= 1

    async def read(message: object) -> bool | str:
        """ONE message marked read: True when `team` played it; the refusal `team` said, when it refused; False when
        nothing was played."""
        argv = gestures.read(team, message)
        if argv is None:
            return False
        if await played(argv):
            return True
        return (held["refused"] or False) if live(pane) else False

    async def reply(question: tuple) -> dict | str | None:
        """The reply to `question` -- `(task, id)` -- written over the inbox: -> the inbox read again once the reply is
        played; the refusal `team` said, when it refused the reply; None when nothing was sent or the inbox could not
        be read again."""
        task, asked = question
        written: asyncio.Future = asyncio.get_running_loop().create_future()

        def then(argv: list[str] | None) -> None:
            if not written.done():
                written.set_result(argv)
        write_on(pane, state, team, task, asked, held["inbox"], then)
        argv = await written
        if argv is None:
            return None
        if not await played(argv):
            return held["refused"] if live(pane) else None
        if not live(pane):
            return None
        again, face = await faces.inbox(house, team)
        if face.rc != 0:
            return None
        held["inbox"] = again
        return again

    def chosen(answer: object) -> None:
        if answer == "seen":
            pane._play(gestures.seen(team))
    pane.app.push_screen(InboxScreen(team, found, read, reply), chosen)


async def journal_of(pane, house: str, team: str) -> None:
    """`l`: a team's whole journal (`team log <name> --json`) in an overlay."""
    found, face = await faces.log(house, team)
    if face.rc != 0:
        pane.post_message(pane.Refused(said_of(face)))
        return
    lines = [ThreadLine.read(one) for one in found]
    pane.app.push_screen(EventScreen(Text(f"{team} · {len(lines)} event(s)"), lambda: palette.thread_text(lines),
                                     label="journal"))


async def result_of(pane, house: str, team: str, task: str, title: str = "") -> None:
    """`v`: a task's result (`team result <name> <task>`) in an overlay; a refusal -- `task-open` -- on the remedy
    line as the verb said it."""
    face = await faces.result(house, team, task)
    if face.rc != 0:
        pane.post_message(pane.Refused(said_of(face)))
        return
    try:
        value = json.loads(face.out)
    except ValueError:
        value = face.out.strip()
    pane.app.push_screen(EventScreen(Text(f"{team}{palette.SEP}{title or task}"), lambda: palette.result_text(value),
                                     label="result"))
