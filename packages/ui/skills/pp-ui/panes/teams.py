"""teams -- the TEAMS tab: WHO the teams are, as the faces of `team` say them.

A menu on the left -- the teams declared, each name in its state's look (`⏸` before a team paused), the
wake-ups under way of each, the questions waiting for the owner, the tasks done not seen, `-` for a team
never started --, and a centre of horizontal bands: the HEAD of the team
chosen (its owner and mandators, its state, its budget and its wake-ups, its net, what waits for the
owner, counted), then its MEMBERS. Under ~70 columns the menu folds into one line, `team: < … · <state> >`, which `[`
and `]` change -- the screen's breakpoint class, CSS alone. The ceremonies open over the tab (`c`), the
detail of a member too (`d`). Nothing is read before the tab is first shown. Then `team status --json`
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

The tab plays the gestures of a team and of a member: every gesture is a verb `./pp team …` whose argv
`model/gestures.py` makes from what is chosen, SHOWN before it plays (`ConfirmScreen`, `GestureScreen` -- the
fields of a gesture, the command under them), played by `play_verb`, its refusal on the remedy line as the verb
said it, the team read again after it. `X` and `R` play only once the name of their target is typed, `X` saying
what it stops as the face counts it; `P` pauses the team, or resumes it when the face says it paused. `b` shows
the owner's inbox (`team inbox --json`) -- a question there answered on its task, `x` marking it seen --, `e` the
declaration (`team declaration --json`), read only, and `B` raises the budget, a field changed alone composing
its argument. `N` gives birth to a team from a template: the form reads `team templates --json`, its fields set by the
template chosen, and plays `team new` as it shows it -- a field left as it opened composing no flag, the post
writing no file --; the team born is chosen once the teams are read again, and `ctrl+s` starts it too, by the path
of `S`; a refusal of `team new` opens the form again on its values. The tab computes no state of a team: the next ring of a
ceremony, a wait, what a member has not seen are `team`'s, shown as the face says them; no gesture is hidden
by the state of a team -- the verb judges."""
from __future__ import annotations

import asyncio
import json
import time

from rich.text import Text

from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widgets import DataTable, Static

import palette
from faces import objects, play_verb
from faces import team as faces
from model import PaneSpec, gestures
from model.teams import MEMBER_COLUMNS, TEAM_COLUMNS, TeamBadge, TeamState, ThreadLine, season_lines
from panes import live
from panes.agents import said_of, tail_of
from panes.overlays import CeremoniesScreen, ConfirmScreen, EventScreen, Field, GestureScreen, InboxScreen, \
    SeasonScreen

ROUND_FLOOR = 10.0                 # seconds at least between two readings of the teams
ROUND_FACTOR = 20                  # the round waits this many times what a reading cost
BADGES, STATE, FOLLOW = "teams-badges", "teams-state", "teams-follow"   # the worker groups
GESTURE = "teams-gesture"



class TeamsPane(Vertical):
    """The Teams tab: the folded menu, then the menu of the teams beside the centre -- the head, the members."""

    DEFAULT_CSS = """
    TeamsPane { height: 1fr; }
    TeamsPane .fold { display: none; height: 1; padding: 0 1; }
    #teams-row { height: 1fr; }
    #teams-menu { width: 30; max-width: 40%; height: 1fr; }
    #teams-menu .title, #teams-centre .title { height: 1; padding: 0 1; }
    #teams-list { height: 1fr; }
    #teams-centre { width: 1fr; height: 1fr; padding-left: 1; }
    #teams-head { height: auto; padding: 0 1; margin-bottom: 1; }
    #teams-centre .title.rule-top { height: 2; }
    #teams-members { height: 1fr; }
    """

    class Read(Message):
        """The chosen team was read: its line for the status."""

        def __init__(self, bar: str) -> None:
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

    class TaskAsked(Message):
        """A task of a team is asked -- the last ring of a ceremony: the Tasks tab shows it."""

        def __init__(self, team: str, task: str) -> None:
            super().__init__()
            self.team, self.task = team, task

    class Played(Message):
        """A gesture played: its command, for the status line."""

        def __init__(self, command: str) -> None:
            super().__init__()
            self.command = command

    def __init__(self, spec: PaneSpec, house: str, flags: tuple[str, ...] = ()) -> None:
        super().__init__(id=f"pane-{spec.key}")
        self.spec, self.house = spec, house
        self.flags = tuple(flags)          # what followed `--`: its `--harness` rides `S`
        self.badges: list[TeamBadge] = []
        self.team: str | None = None
        self.state: TeamState | None = None
        self._shown = False                # the first showing starts the readings
        self.active = False                # the tab is the one shown: its first table takes the focus
        self._badges_at = self._state_at = ""
        self._read_once = False            # the teams were read once
        self._reading = False              # a reading of the team is under way
        self._dirty = False                # an ask came during it: one reading more
        self._switching = asyncio.Lock()   # one change of team at a time: never two watches
        self._watch: faces.Subscription | None = None
        self._round = None
        self._seen: dict[str, int] = {}    # the watch's objects by `team:<event>`, what `--wait` counts
        self._playing = 0                  # gestures under way: a render waits for them
        self._want: str | None = None      # a team born from the post, chosen once the teams are read again
        self._steps: dict[str, ThreadLine] = {}   # the last step the chosen team's watch said of each member
        self._over: set[str] = set()       # the members whose wake-up ended after their last step

    def compose(self):
        yield Static("", id="teams-fold", classes="fold", markup=False)
        with Horizontal(id="teams-row"):
            with Vertical(id="teams-menu", classes="menu"):
                yield Static(palette.section_title("Teams", ""), id="teams-list-title", classes="title", markup=False)
                yield DataTable(id="teams-list", cursor_type="row", zebra_stripes=True)
            with Vertical(id="teams-centre", classes="centre rule-left"):
                yield Static("", id="teams-head", markup=False)
                yield Static(palette.section_title("Members", ""), id="teams-members-title", classes="title rule-top",
                             markup=False)
                yield DataTable(id="teams-members", cursor_type="row", zebra_stripes=True, cell_padding=2)

    def on_mount(self) -> None:
        self.query_one("#teams-list", DataTable).add_columns(*TEAM_COLUMNS)
        self.query_one("#teams-members", DataTable).add_columns(*MEMBER_COLUMNS)

    # ---------- the readings ----------
    def shown(self) -> None:
        """The tab is shown: the first time, the readings start; the focus goes to the teams."""
        if not self._shown:
            self._shown = True
            self.reread()
        self.focus_table()

    async def settled(self, final: bool = False) -> None:
        """Returns once nothing is being read -- what a render waits for; at once before the first showing."""
        while self._shown and (not self._read_once or self._reading or self._switching.locked() or self._playing):
            await asyncio.sleep(0.01)

    def reread(self) -> None:
        """`u`, and the first showing: the teams and the chosen team, read now."""
        self.run_worker(self._read_badges(), group=BADGES, exclusive=True)
        self.ask_state()

    async def _read_badges(self) -> None:
        began = time.monotonic()
        found, face = await faces.badges(self.house)
        cost = time.monotonic() - began
        if not live(self):                       # the post left while the face was read
            return
        if face.rc != 0:
            self.post_message(self.Refused(said_of(face)))
        self.badges = [TeamBadge.read(one) for one in found]
        self._badges_at = palette.hhmmss()
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
        self.run_worker(self._read_badges(), group=BADGES, exclusive=True)

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
                await self._read_state()
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
        self._state_at = palette.hhmmss()
        self._fill_team()

    # ---------- the watch ----------
    async def choose(self, name: str | None) -> None:
        """`name` becomes the chosen team: the watch of the one before ended, one opened on it, the team read."""
        async with self._switching:
            if name == self.team and (name is None or self._watch is not None):
                return
            self.team, self.state = name, None
            self._steps, self._over = {}, set()
            if self._watch is not None:
                await self._watch.close()
                self._watch = None
            self.ask_state()
            if name is not None and live(self):
                self._watch = await faces.follow(self.house, name)
                self.run_worker(self._follow(self._watch), group=FOLLOW, exclusive=True)

    async def _follow(self, watch: "faces.Subscription") -> None:
        async for found in watch.events():
            if not live(self) or watch is not self._watch:
                return
            event = str(found.get("event", ""))
            self._seen[f"team:{event}"] = self._seen.get(f"team:{event}", 0) + 1
            member = found.get("agent")
            line = ThreadLine.read(found)
            if line.step and isinstance(member, str):
                self._steps[member] = line
                self._over.discard(member)
            elif event in ("wake-ended", "wake-failed", "wake-killed") and isinstance(member, str) \
                    and member in self._steps and self._steps[member].fields.get("run") == found.get("run"):
                self._over.add(member)
            if event != "quiet":
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
        table = self.query_one(f"#{key}", DataTable)
        row = table.cursor_row
        table.clear()
        for index, cells in enumerate(rows):
            table.add_row(*cells, key=str(index))
        if rows:
            table.move_cursor(row=max(0, min(row, len(rows) - 1)))

    def _fill_teams(self) -> None:
        self.query_one("#teams-list-title", Static).update(palette.section_title("Teams", self._badges_at))
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

    def _show_fold(self) -> None:
        badge = next((one for one in self.badges if one.team == self.team), None)
        self.query_one("#teams-fold", Static).update(palette.team_fold(self.team, badge))

    def _fill_team(self) -> None:
        state = self.state
        started = state is not None and state.started is not None
        self._fill("teams-members", [palette.member_cells(one, self._steps.get(one.member), one.member in self._over)
                                     for one in state.members] if started else [])
        self.query_one("#teams-members-title", Static).update(
            palette.section_title("Members", self._state_at if started else ""))
        head = self.query_one("#teams-head", Static)
        if self.team is None:
            head.update(palette.no_team())
        elif not started:
            head.update(palette.not_started(self.team))
        else:
            head.update(palette.team_head(state, self._state_at))
        self._show_fold()
        if self.team is not None:
            badge = next((one for one in self.badges if one.team == self.team), None)
            self.post_message(self.Read(palette.team_bar(self.team, badge, state, self._state_at)))

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.data_table.id == "teams-list":
            row = event.cursor_row
            if 0 <= row < len(self.badges) and self.badges[row].team != self.team:
                self.run_worker(self.choose(self.badges[row].team))

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """`enter` on a member: its run, read in a tab of the dialogue."""
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
    def _member_under_cursor(self):
        state = self.state
        if state is None or state.started is None:
            return None
        row = self.query_one("#teams-members", DataTable).cursor_row
        return state.members[row] if 0 <= row < len(state.members) else None

    def inspect_member(self) -> None:
        """`i`, `enter` on a member: its run read in a tab of the dialogue -- a member without a run (none yet,
        `?` before a launch, `—` after a reset) says so on the remedy line, and nothing is read."""
        member = self._member_under_cursor()
        if member is None or self.team is None:
            self.post_message(self.Refused("no member under the cursor"))
            return
        if not member.run or member.run in ("?", palette.NONE) or not member.path:
            self.post_message(self.Refused(f"{member.member} has no run to inspect"))
            return
        self.post_message(self.MemberAsked(self.team, member.member, member.path, member.run, member.how == "running"))

    def member_detail(self) -> None:
        """`d`: the member under the cursor whole -- its run, its tasks, whom it waits for, the posts not delivered
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
        self.app.push_screen(CeremoniesScreen(team, state, senders, ring,
                                              lambda name, sender: gestures.preview(
                                                  gestures.ring(team, name, sender, owner) or [])), chosen)

    # ---------- the gestures ----------
    def _play(self, argv: list[str] | None) -> None:
        if argv is None:
            return
        self._playing += 1
        self.run_worker(self._played(argv), group=GESTURE)

    async def _played(self, argv: list[str]) -> None:
        """ONE gesture: the argv shown, played as it is; a refusal on the remedy line, the team read again."""
        try:
            face = await play_verb(argv, self.house)
            if not live(self):
                return
            if face.rc != 0:
                self.post_message(self.Refused(said_of(face)))
            else:
                self.post_message(self.Played(gestures.preview(argv)))
            self.reread()
        finally:
            self._playing -= 1

    def _confirmed(self, title: str, argv: list[str] | None, expect: str | None = None,
                   detail: Text | None = None) -> None:
        """The command in an overlay -- under `detail`, what it would do --; `enter` plays it -- under `expect`, once
        the name is typed."""
        if argv is None:
            self.post_message(self.Refused("nothing to play here: no team or member under the cursor"))
            return

        def chosen(go: bool | None) -> None:
            if go:
                self._play(argv)
        self.app.push_screen(ConfirmScreen(title, gestures.preview(argv), expect, detail), chosen)

    def stop_all(self) -> None:
        """`X`: every open task of the team stopped -- on the team's name typed; what it stops counted on the face."""
        state = self.state
        detail = palette.stop_said(state) if state is not None and state.started is not None else None
        self._confirmed(f"stop all tasks of {self.team}", gestures.stop(self.team, whole=True), self.team, detail)

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
        cap, bound = (state.budget or {}).get("cap"), state.wakes.get("bound")
        usd = f"{float(cap):.2f}" if isinstance(cap, (int, float)) else ""
        wakes = str(bound) if isinstance(bound, int) else ""

        def changed(typed: str, before: str, kind) -> str | None:
            try:
                return typed if typed and (not before or kind(typed) != kind(before)) else None
            except ValueError:
                return typed or None

        def argv_of(values: dict) -> list[str] | None:
            return gestures.budget(team, changed(values["budget"], usd, float), changed(values["wakes"], wakes, int),
                                   values["as"], owner)
        fields = (Field("budget", "budget", "line", palette.BUDGET_HELP, value=usd, number="number"),
                  Field("wakes", "wakes", "line", palette.WAKES_HELP, value=wakes, number="integer"),
                  Field("as", "as", "list", palette.AS_HELP, senders_of(state), value=owner))
        self.app.push_screen(GestureScreen(f"raise the budget of {team}", fields, argv_of, palette.budget_head(state),
                                           missing="nothing changed"), self._play)

    async def show_inbox(self) -> None:
        """`b`: the owner's inbox of the team chosen (`team inbox --json`) in an overlay -- `enter` on a question writes
        its reply on its task, `x` marks the inbox seen, the command shown under the lines."""
        state = self._started_state()
        if state is None:
            return
        team = self.team
        found, face = await faces.inbox(self.house, team)
        if face.rc != 0:
            self.post_message(self.Refused(said_of(face)))
            return

        def chosen(answer: object) -> None:
            if answer == "seen":
                self._play(gestures.seen(team))
            elif isinstance(answer, tuple):
                task, question = answer
                write_on(self, state, team, task, question)
        self.app.push_screen(InboxScreen(team, found, gestures.preview(gestures.seen(team) or [])), chosen)

    async def show_declaration(self) -> None:
        """`e`: the declaration of the team chosen (`team declaration --json`) in an overlay, read only -- its path,
        the verdict of `start`'s judge, the keys a new start would change, `TEAM.md` whole."""
        team = self.team
        if team is None:
            self.post_message(self.Refused("no team under the cursor"))
            return
        found, face = await faces.declaration(self.house, team)
        if face.rc != 0 or found is None:
            self.post_message(self.Refused(said_of(face)))
            return
        self.app.push_screen(EventScreen(Text(f"{team} · {found.get('path', 'TEAM.md')}"),
                                         lambda: palette.declaration_text(found), label="declaration"))

    async def new_team(self, given: dict | None = None) -> None:
        """`N`: a team written from a template, in an overlay -- the templates read from `team templates --json`, the
        fields of the one chosen set from it (members, ceremony, limits), the command under them; `enter` plays `team
        new`, `ctrl+s` plays it then starts the team born. `given`: the values the form opens again on."""
        found, face = await faces.templates(self.house)
        if face.rc != 0 or not found:
            self.post_message(self.Refused(said_of(face) if face.rc != 0 else "no template said by team templates"))
            return
        templates = {str(one.get("template")): one for one in found}
        given = dict(given or {})

        def of(name: str | None) -> dict:
            return templates.get(name or "") or next(iter(templates.values()))

        def defaults(name: str | None) -> dict:
            template, limits = of(name), of(name).get("limits") or {}
            return {"members": "\n".join(str(one) for one in template.get("members") or []),
                    "ceremony": "yes" if template.get("ceremony") else "no", "root": None,
                    **{key: str(limits.get(key, "")) for key in ("budget", "wakes", "timeout")}}

        def members(text: str | None) -> tuple:
            names = [line.split()[0] for line in str(text or "").splitlines() if line.strip()]
            return tuple((one, one) for one in dict.fromkeys(names))

        def ceremonies(name: str | None) -> tuple:
            line = of(name).get("ceremony")
            return ((str(line), "yes"), ("left out", "no")) if line else (("none: the template has none", "no"),)
        chosen = given.get("template") if given.get("template") in templates else next(iter(templates))
        values = {**defaults(chosen), "name": "", "principals": "", "schedule": "", **given, "template": chosen}
        fields = (Field("template", "template", "list", palette.TEMPLATE_HELP,
                        tuple((f"{name} -- {one.get('description', '')}", name) for name, one in templates.items()),
                        value=chosen),
                  Field("name", "name", "line", palette.TEAM_NAME_HELP, value=values["name"]),
                  Field("members", "members", "text", palette.MEMBERS_HELP, value=values["members"]),
                  Field("root", "root", "list", palette.FIRST_HELP, members(values["members"]), value=values["root"],
                        blank="the first member"),
                  Field("principals", "principals", "line", palette.PRINCIPALS_HELP, value=values["principals"]),
                  Field("ceremony", "ceremony", "list", palette.CEREMONY_HELP, ceremonies(chosen),
                        value=values["ceremony"]),
                  Field("budget", "budget", "line", palette.LIMIT_HELP, value=values["budget"], number="number"),
                  Field("wakes", "wakes", "line", palette.LIMIT_HELP, value=values["wakes"], number="integer"),
                  Field("timeout", "timeout", "line", palette.LIMIT_HELP, value=values["timeout"], number="number"),
                  Field("schedule", "schedule", "line", palette.SCHEDULE_HELP, value=values["schedule"]))

        def argv_of(typed: dict) -> list[str] | None:
            template = of(typed.get("template"))
            return gestures.new(typed["name"], typed.get("template"), typed["members"],
                                [str(one) for one in template.get("members") or []], typed["root"], typed["principals"],
                                not (template.get("ceremony") and typed["ceremony"] == "no"),
                                {key: typed[key] for key in ("budget", "wakes", "timeout")},
                                {key: str(value) for key, value in (template.get("limits") or {}).items()},
                                typed["schedule"])

        def gap(typed: dict) -> str:
            return gestures.new_gap(typed["name"], typed["members"],
                                    [str(one) for one in of(typed.get("template")).get("members") or []]) \
                or "a template"
        screen = GestureScreen("a new team", fields, argv_of, missing=gap, focus="name",
                               follow=lambda typed: {"root": members(typed.get("members")),
                                                     "ceremony": ceremonies(typed.get("template"))},
                               refill=lambda key, typed: defaults(typed.get("template")) if key == "template" else {},
                               also="create and start")

        def made(result: object) -> None:
            if result is None:
                return
            start = isinstance(result, tuple)
            argv = result[1] if start else result
            self._playing += 1
            self.run_worker(self._create(list(argv), dict(screen.given), start), group=GESTURE)
        self.app.push_screen(screen, made)

    async def _create(self, argv: list[str], given: dict, start: bool) -> None:
        """`team new` played as shown: refused, the form opens again on its values; written, the team born is chosen
        once the teams are read again -- and, under `start`, started by the path of `S`."""
        try:
            face = await play_verb(argv, self.house)
            if not live(self):
                return
            if face.rc != 0:
                self.post_message(self.Refused(said_of(face)))
                await self.new_team(given)
                return
            self.post_message(self.Played(gestures.preview(argv)))
            self._want = argv[2]
            self.reread()
            if start:
                await self.start_team(argv[2])
        finally:
            self._playing -= 1

    async def start_team(self, team: str | None = None) -> None:
        """`S`: a SEASON of the team chosen -- or of `team`, born from the post -- in its overlay: the lines the next
        start writes, read from the faces alone -- the members of `declared` (`team declaration --json`), what the
        season of before gave (`team status --json`: `launch`, `members[].launch`, `season`, `limits`) or, for a first
        season, what each member's agent last played (`agent status <path> --json`, one call per path) -- the
        providers of `agent providers --json` for their profiles, the packages `required` greyed; the command under
        the fields (`gestures.season`), the `--harness` given after `--` to the post before any `--member`. A
        declaration `start` would refuse opens nothing: its refusal goes to the remedy line."""
        team = team or self.team
        if team is None:
            return
        found, face = await faces.declaration(self.house, team)
        if face.rc != 0 or found is None:
            self.post_message(self.Refused(said_of(face) if face.rc != 0 else f"{team}: no declaration said"))
            return
        declared = found.get("declared")
        if not isinstance(declared, dict):
            refusal = (found.get("verdict") or {}).get("refusal") or "the declaration is refused"
            self.post_message(self.Refused(str(refusal)))
            return
        said, face = await faces.state(self.house, team)
        state = TeamState.read(said or {"team": team, "started": None})
        given = await play_verb(["agent", "providers", "--json"], self.house)
        offered = {str(one.get("provider", "")): one for one in objects(given)}
        paths = list(dict.fromkeys(str(one.get("path", "")) for one in declared.get("agents") or []
                                   if isinstance(one, dict) and one.get("path")))
        faced = await asyncio.gather(*(play_verb(["agent", "status", path, "--json"], self.house) for path in paths))
        agents = {path: tail_of(objects(one)) for path, one in zip(paths, faced) if one.rc == 0}
        lines = season_lines(state, declared, agents, tuple(offered))
        started = state.started is not None
        limits = dict(state.limits if started else declared.get("limits") or {})
        owed = not started or state.open_tasks == 0
        declared_limits = declared.get("limits") or {}

        async def offer() -> dict[str, dict]:
            return offered

        def shown(value: object) -> str:
            return f"{value:g}" if isinstance(value, float) else str(value) if value is not None else ""

        def argv_of(rows: list, values: dict) -> list[str] | None:
            return gestures.season(team, rows, values["message"], values["name"], values["budget"], values["wakes"],
                                   declared_limits, owed, state.required, self.flags)
        helps = {"budget": palette.season_limit_help("budget", declared_limits.get("budget")),
                 "wakes": palette.season_limit_help("wakes", declared_limits.get("budget-wakes")),
                 "message": palette.season_message_help(owed)}
        await self.app.push_screen(SeasonScreen(palette.season_title(team, state), palette.season_head(declared), lines,
                                                {"budget": shown(limits.get("budget")),
                                                 "wakes": shown(limits.get("budget-wakes"))},
                                                argv_of, list(offered), offer, state.required, helps,
                                                missing="the team's first message"), self._play)   # mounted: its focus set

    @property
    def keys(self) -> list[tuple[str, str]]:
        return [("team:", ""), ("N", "new team"), ("n", "new task"), ("S", "start"), ("B", "budget"), ("b", "inbox"), ("e", "declaration"),
                ("P", "pause/resume"), ("X", "stop all tasks"), ("T", "tick"), ("c", "ceremonies"), ("l", "journal"), ("member:", ""), ("enter", "its run"), ("d", "detail"),
                ("a", "answers"), ("R", "forget its run"), ("u", "reload")]


def senders_of(state: TeamState) -> tuple[tuple[str, str], ...]:
    """-> the principals a gesture posts as, as options: the owner first -- who writes no `--as` --, then the
    mandators."""
    return tuple((one, one) for one in ((state.owner,) if state.owner else ()) + state.principals)


def write_on(pane, state: TeamState, team: str, task: str, reply: object = None) -> None:
    """`m`: a note -- or a reply -- on `task` of `team`, written in an overlay: `to` (the members; left on the
    holders, no `--to`), `as` (the owner, then the principals), `reply to` (the questions waiting for the owner on
    the task, as the face's `waiting` lists them; `reply` chosen at the opening), the text."""
    owner = state.owner
    questions = tuple((palette.question_option(one), one.get("id")) for one in state.waiting.get("questions") or []
                      if one.get("task") == task)
    fields = (Field("to", "to", "list", palette.TO_HELP, tuple((one.member, one.member) for one in state.members),
                    blank="the holders"),
              Field("as", "as", "list", palette.AS_HELP, senders_of(state), value=owner),
              Field("reply", "reply to", "list", palette.REPLY_HELP, questions, value=reply,
                    blank="nothing: a plain note"),
              Field("text", "text", "text", palette.TEXT_HELP))

    def argv_of(values: dict) -> list[str] | None:
        return gestures.post(team, values["text"], task, values["to"], values["reply"], values["as"], owner)
    pane.app.push_screen(GestureScreen(f"write on {task} of {team}", fields, argv_of, missing="a text to post",
                                       focus="text"), pane._play)


def ask_new_task(pane, states: dict[str, TeamState], team: str | None, choose: bool) -> None:
    """`n`: a new task, written in an overlay -- under `choose` its team among those `states` holds, `team` first;
    its name (none: no `--name`), `to` (the members of the team; left on its root, no `--to`), `as`, its message."""
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
        Field("name", "name", "line", palette.NAME_HELP),
        Field("to", "to", "list", palette.ROOT_HELP, members(team), blank="the root"),
        Field("as", "as", "list", palette.AS_HELP, senders(team), value=states[team].owner),
        Field("message", "message", "text", palette.TASK_HELP))

    def argv_of(values: dict) -> list[str] | None:
        chosen = values.get("team") or team
        state = states.get(chosen)
        return gestures.post(chosen, values["message"], None, values["to"], None, values["as"],
                             state.owner if state is not None else None, values["name"])

    def follow(values: dict) -> dict[str, tuple]:
        return {"to": members(values.get("team")), "as": senders(values.get("team"))} if choose else {}
    pane.app.push_screen(GestureScreen(f"a new task of {team}" if not choose else "a new task", fields, argv_of,
                                       missing="the task's message", focus="message", follow=follow), pane._play)


async def journal_of(pane, house: str, team: str) -> None:
    """`l`: a team's whole journal (`team log <name> --json`) in an overlay."""
    found, face = await faces.log(house, team)
    if face.rc != 0:
        pane.post_message(pane.Refused(said_of(face)))
        return
    lines = [ThreadLine.read(one) for one in found]
    pane.app.push_screen(EventScreen(Text(f"{team} · {len(lines)} event(s)"), lambda: palette.thread_text(lines),
                                     label="journal"))


async def result_of(pane, house: str, team: str, task: str) -> None:
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
    pane.app.push_screen(EventScreen(Text(f"{team} · {task}"), lambda: palette.result_text(value), label="result"))
