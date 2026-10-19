"""app -- the FRAME of the post (the cockpit's "charpente v2", kept): a header docked at the
top (the brand on the left, the house's root on the right), native tabs the digits and the
mouse switch, a footer docked at the bottom (the keys of the active pane, on as many lines as
the width asks · the remedy · the status), and the body of the pane as the ONE scroller. The
screen holds at any size by CSS: `dock` for what never moves, `1fr` for the body, `auto` for the
footer; a resize lays the keys out again on the new width, between two keys.

The state the screen renders is REACTIVE: `house`, `status` and `remedy` are reactive
attributes, each watched by the widget that shows it; the clock re-dates the status every
second -- every datum shown carries the hour of its reading. The tabs come in the order
dialogue · agents · teams · tasks: the dialogue carries the conversations open (those named at the
post's opening, each opened on this loop before the post drew, those its memory gives back, dormant, and
those asked from the Agents tab), the Agents tab the agents of the house and the runs of each, the Teams tab the teams of
the house and the Tasks tab what they do, each read from the first time it is shown. Under
`NARROW` columns the screen carries the class `-narrow` (`HORIZONTAL_BREAKPOINTS`): the menus of the
Teams and Tasks tabs fold into one line, by their CSS alone. The app is the ONE opener of a
conversation: the Agents tab asks, the app opens and shows it."""
from __future__ import annotations

from rich.cells import cell_len
from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.content import Content
from textual.reactive import reactive
from textual.widgets import Static, TabbedContent, TabPane

import memory
import palette
from faces import objects, play_verb
from faces.chat import Conversation, Opening, lived
from faces.team import Follow, flow
from model import PANES, House, pane
from model.dialogue import ENDED, Thread
from panes.agents import AgentsPane, said_of
from panes.dialogue import DialoguePane
from panes.overlays import EventScreen, Field, GestureScreen, ThemeScreen
from panes.tasks import TasksPane
from panes.teams import TeamsPane

STATUS_PERIOD = 1.0                  # the status line re-dates itself at this pace
SPIN_PERIOD = 0.2                    # the spinner turns at this pace, while a turn runs only
POST_TABS = "post"                   # the id of the post's own row of tabs
NARROW = 70                          # under this width the menus of the Teams and Tasks tabs fold into one line
TEAMS = ("teams", "tasks")           # the tabs of the teams

# the GEOMETRY alone -- dock, heights, widths, padding; every colour and weight is the
# palette's (`THEME_CSS`), composed below
LAYOUT_CSS = """
#header { dock: top; height: 1; }
#brand { width: auto; padding: 0 1; }
#ctxbar { width: 1fr; text-align: right; padding: 0 1; }
TabbedContent { height: 1fr; }
#footer { dock: bottom; height: auto; }
#keys { height: auto; padding: 0 1; }
#remedy, #status { height: 1; padding: 0 1; }
Screen.-narrow .menu { display: none; }
Screen.-narrow .fold { display: block; }
Screen.-narrow .centre { padding-left: 0; }
"""


class PostApp(App):
    TITLE = palette.BRAND
    AUTO_FOCUS = None                # nothing takes the focus by itself: `i` goes to the message line
    HORIZONTAL_BREAKPOINTS = [(0, "-narrow"), (NARROW, "-wide")]
    CSS = palette.THEME_CSS + LAYOUT_CSS
    BINDINGS = [Binding("q", "quit", "quit"),
                Binding("escape", "escape", "leave the line", show=False),
                Binding("ctrl+g", "stop_turn", "stop the turn", show=False, priority=True),
                Binding("c", "toggle_conduction", "conduction", show=False),
                Binding("i", "write", "write", show=False),
                Binding("n", "new", "open", show=False),
                Binding("x", "close_tab", "close", show=False),
                Binding("r", "resume_task", "resume", show=False),
                Binding("u", "reread", "reload", show=False),
                Binding("p", "params", "params", show=False),
                Binding("o", "conduct", "conduct", show=False),
                Binding("k", "packages", "packages", show=False),
                Binding("s", "stats", "stats", show=False),
                Binding("a", "add_agent", "add", show=False),
                Binding("t", "theme", "theme", show=False),
                Binding("U", "maintain", "upgrade", show=False),
                Binding("l", "journal", "journal", show=False),
                Binding("v", "result", "result", show=False),
                Binding("m", "message", "message", show=False),
                Binding("S", "start_team", "start", show=False),
                Binding("N", "new_team", "new team", show=False),
                Binding("X", "stop_all", "stop all tasks", show=False),
                Binding("P", "pause", "pause", show=False),
                Binding("T", "tick", "tick", show=False),
                Binding("R", "reset_member", "reset", show=False),
                Binding("g", "ring", "ring", show=False),
                Binding("d", "detail", "detail", show=False),
                Binding("b", "inbox", "inbox", show=False),
                Binding("e", "declaration", "declaration", show=False),
                Binding("B", "budget", "budget", show=False),
                Binding("left_square_bracket", "step('show', -1)", "previous", show=False),
                Binding("right_square_bracket", "step('show', 1)", "next", show=False),
                Binding("left_curly_bracket", "step('team', -1)", "previous team", show=False),
                Binding("right_curly_bracket", "step('team', 1)", "next team", show=False),
                Binding("ctrl+c", "copy", "copy", show=False, priority=True),
                Binding("ctrl+a", "select_all", "select all", show=False, priority=True),
                Binding("ctrl+right", "next_tab", "next", show=False, priority=True),
                Binding("ctrl+left", "previous_tab", "previous", show=False, priority=True)] + [
        Binding(one.digit, f"show_pane('{one.key}')", one.key, show=False) for one in PANES]

    house: reactive[House] = reactive(House("", ""), init=False)
    status: reactive[Content] = reactive(Content(""), init=False)
    remedy: reactive[str] = reactive("", init=False)

    def __init__(self, house: House, started: list[Opening] = (),
                 agents: list[tuple[str, str | None]] = (), flags: tuple[str, ...] = (),
                 histories: list[list[dict] | None] = ()) -> None:
        super().__init__()
        self._house = house
        self._started = list(started)     # conversations OPEN on this loop, their first event read
        self._agents = list(agents)       # (agent, run) of each, in order
        self._flags = tuple(flags)        # what followed `--`: to every conversation the post opens, its `--harness` to `S`
        self._histories = list(histories) # the history of each; None: read once its tab stands (the memory's)
        self._states = {"dialogue": "no conversation open" if not started else "opening", "agents": "reading the agents",
                        "teams": "reading the teams", "tasks": "reading the tasks"}
        self._shown = PANES[0].key
        self._spin = None                 # the spinner's timer: alive while a turn runs somewhere
        self._frame = 0
        self._note = memory.relaunched()  # what a gesture said, on the status until the next event -- at the
                                          # opening, the maintenance verb the post asked before it was played again
        self._relaunched = bool(self._note)   # opened again by a maintenance: its console relaunches no more
        self._kept = None                 # the widget focused when the terminal's focus left

    # ---------- composition ----------
    def compose(self) -> ComposeResult:
        # markup=False on every Static that renders DATA: a `[...]` in a path or a verb's
        # answer is never parsed as markup
        with Horizontal(id="header"):
            yield Static(palette.BRAND, id="brand", markup=False)
            yield Static("", id="ctxbar", markup=False)
        with TabbedContent(id=POST_TABS, initial=f"tab-{PANES[0].key}"):
            for one in PANES:
                with TabPane(f"{one.digit}·{one.title}", id=f"tab-{one.key}"):
                    if one.key == "dialogue":
                        yield DialoguePane(one, self._house.root, self._started, self._agents, self._flags,
                                           self._histories)
                    elif one.key == "agents":
                        yield AgentsPane(one, self._house.root)
                    elif one.key == "teams":
                        yield TeamsPane(one, self._house.root, self._flags)
                    else:
                        yield TasksPane(one, self._house.root)
        with Vertical(id="footer", classes="rule-top"):
            yield Static("", id="keys", markup=False)
            yield Static("", id="remedy", markup=False)
            yield Static("", id="status", markup=False)

    def on_mount(self) -> None:
        if memory.theme() in self.available_themes:   # the theme the post was left in
            self.theme = memory.theme()
        self.house = self._house
        self._show_keys(PANES[0].key)
        self._tick()
        self.set_interval(STATUS_PERIOD, self._tick)

    # ---------- the application's focus, as the terminal says it ----------
    def on_app_blur(self, event: events.AppBlur) -> None:
        """The terminal's focus gone to another window: the widget focused kept, then left -- its cursor stops --, the
        application's focus off. Textual's own reaction would style every widget of the screen again, the hidden tabs
        too; it is prevented, and what it does besides is done here."""
        event.prevent_default()
        self._kept = self.screen.focused
        self.set_reactive(App.app_focus, False)
        self.screen.set_focus(None)

    def on_app_focus(self, event: events.AppFocus) -> None:
        """The terminal's focus back: the application's focus on, and the widget kept focused again, without scrolling,
        when it still stands on the screen shown and nothing took the focus meanwhile."""
        event.prevent_default()
        self.set_reactive(App.app_focus, True)
        kept, self._kept = self._kept, None
        if kept is not None and kept.is_attached and kept.screen is self.screen and self.screen.focused is None:
            self.screen.set_focus(kept, scroll_visible=False)

    async def settled(self) -> None:
        """Returns once the conversations of the start are in their tabs and the agents were
        read once -- what a render waits for before it presses a key."""
        await self.dialogue.settled()
        await self.agents.settled()

    async def pane_settled(self, final: bool = False) -> None:
        """Returns once the pane shown read what its showing asked -- the Teams tab's readings; `final`,
        the thread of a task whose cursor rests too; the dialogue's gauges being read."""
        if self._shown == "dialogue":
            await self.dialogue.gauged()
        elif self._shown == "teams":
            await self.teams.settled(final)
        elif self._shown == "tasks":
            await self.tasks.settled(final)
        elif self._shown == "agents":
            await self.agents.opened()

    # ---------- the reactive state, watched by what shows it ----------
    def watch_house(self, house: House) -> None:
        if not self.is_running:
            return
        self.query_one("#brand", Static).update(f"{palette.BRAND}{palette.SEP}{house.name}")
        self.query_one("#ctxbar", Static).update(house.root)

    def watch_status(self, status: Content) -> None:
        if self.is_running:
            self.query_one("#status", Static).update(status)

    def watch_remedy(self, remedy: str) -> None:
        if self.is_running:
            self.query_one("#remedy", Static).update(remedy)

    def _tick(self) -> None:
        """The status line re-dated: the turn's glyph and how long it has run, the pane's state, the last note --
        nothing once the post leaves, its frame pruned while a tick or an event may still come."""
        if not self.is_running:
            return
        state = self._states.get(self._shown, "")
        view = self.dialogue.active_view if self._shown == "dialogue" else None
        turn = (palette.turning(self._frame, palette.seconds_since(view.thread.turn_at)), " ") \
            if view is not None and view.thread.busy else ()
        clock = palette.hhmmss()
        head = f"{self.house.name}{palette.SEP}"
        room = self.size.width - 2 - cell_len(head + palette.SEP + clock) - (cell_len(turn[0].plain) + 1 if turn else 0)
        state = palette.fit_status(state, room) if isinstance(state, list) else state   # a pane said in parts
        left = room - cell_len(str(state)) - (len(palette.SEP) if state else 0)          # the note takes what is left
        note = palette.fit_note(self._note, left)
        self.status = Content.assemble(*turn, head, state, palette.SEP if state else "", note, clock)

    def _follow_turns(self) -> None:
        """The spinner starts with the first turn of the dialogue or the first wake-up the Tasks tab says under way,
        and stops when neither runs any more."""
        busy = self.dialogue.busy or self.tasks.live > 0
        if busy and self._spin is None:
            self._spin = self.set_interval(SPIN_PERIOD, self._turn)
        elif not busy and self._spin is not None:
            self._spin.stop()
            self._spin = None

    def _turn(self) -> None:
        """One frame of the spinner: the titles of the turns under way, the lines of the tasks a wake-up plays and the
        title of their tab, the status."""
        if not self.is_running:
            return
        self._frame += 1
        self.dialogue.spin(self._frame)
        self.tasks.spin(self._frame)
        self._title_tasks()
        self._tick()
        self._follow_turns()

    def _title_tasks(self) -> None:
        """The title of the Tasks tab: `4·Tasks`, and the tasks a wake-up plays counted beside the spinner."""
        spec = next(one for one in PANES if one.key == "tasks")
        tab = self.query_one(f"#{POST_TABS}", TabbedContent).get_tab(f"tab-{spec.key}")
        label = palette.pane_label(spec.digit, spec.title, self.tasks.live, self._frame)
        if str(tab.label) != label:
            tab.label = label

    def spinning(self) -> int:
        """-> 1 while the spinner's interval is alive, 0 otherwise -- what the bench reads."""
        return 0 if self._spin is None else 1

    def layouts(self) -> int:
        """-> the arrangements the active conversation's transcript computed, -1 with no conversation open."""
        view = self.dialogue.active_view
        return view.transcript.layouts if view is not None else -1

    def nodes(self) -> int:
        """-> the widgets the last block of the agent's words in the active conversation's transcript holds, -1 with no
        such block."""
        view = self.dialogue.active_view
        blocks = list(view.transcript.query(".block.agent")) if view is not None else []
        return sum(1 for _ in blocks[-1].walk_children()) if blocks else -1

    @property
    def dialogue(self) -> DialoguePane:
        return self.query_one(DialoguePane)

    @property
    def agents(self) -> AgentsPane:
        return self.query_one(AgentsPane)

    @property
    def teams(self) -> TeamsPane:
        return self.query_one(TeamsPane)

    @property
    def tasks(self) -> TasksPane:
        return self.query_one(TasksPane)

    # ---------- the conversations' events, said by the dialogue pane ----------
    def on_dialogue_pane_said(self, message: DialoguePane.Said) -> None:
        if not self.is_running:
            return
        event, f, thread = message.event, message.event.fields, message.thread
        self._note = ""
        if message.active:
            state = self._state_of(thread)
            if event.kind == "opened":
                state += (" · resumed" if f.get("resumed") else "") + (" · standing taken up" if f.get("standing") else "")
            self._states["dialogue"] = state
            if event.kind in ("opened", "waiting"):
                self.remedy = palette.cap_note(thread.agent, thread.cap)   # a raised cap is said while it holds
        if event.kind == "refused":
            self.remedy = f"{thread.agent}: refused {f.get('code', '?')} -- " + \
                (str(f["detail"])[:80] if f.get("detail") else str(f.get("line", ""))[:60])
        elif event.kind == ENDED:
            said = str(f.get("stderr", "")).strip().splitlines()
            self.remedy = f"{thread.agent}: ended rc {f.get('rc')}" + (f" -- {said[0][:70]}" if said else "")
        elif event.kind == "verdict":
            self.agents.reread()                         # the run moved: the Agents tab says so
        self._follow_turns()
        self._tick()
        self._show_keys(self._shown)

    def on_dialogue_pane_activated(self, message: DialoguePane.Activated) -> None:
        if not self.is_running:
            return
        view = message.view
        if view is None:
            self._states["dialogue"] = "no conversation open"
        else:
            self._states["dialogue"] = self._state_of(view.thread)
        self._tick()
        self._show_keys(self._shown)

    @staticmethod
    def _state_of(thread: Thread) -> Content:
        """A conversation on the status: the agent, the run, its state, whether it is conducted
        (`pp on`, `pp off`), then what it plays -- provider · model · budget · effort, `—` where unknown; the
        budget its gauge once the flow says it (`budget 0.42/2.00 USD ▰▰▱▱▱▱▱▱▱▱`) --, then the switches of
        packages waiting (`packages: steering off …`)."""
        run = f"run {thread.run}" if thread.run else "no run yet"
        waiting = palette.waiting_line(thread.pending)
        provider, model, cap, effort = [one or palette.NONE for one in thread.params]
        return Content(palette.SEP).join([thread.agent, run, thread.state, f"pp {'on' if thread.conducted else 'off'}",
                                          provider, model, palette.budget_gauge(thread.budget) or cap, effort]
                                         + ([waiting] if waiting else []))

    def on_dialogue_pane_named(self, message: DialoguePane.Named) -> None:
        self.agents.reread()

    def on_dialogue_pane_refused(self, message: DialoguePane.Refused) -> None:
        self.remedy = message.said[:110]

    # ---------- the agents, said by the Agents tab ----------
    def on_agents_pane_reloaded(self, message: AgentsPane.Reloaded) -> None:
        catalogue = message.catalogue
        agents = len([one for one in catalogue.agents if one.agent != palette.HOUSE])   # the house is no agent of its own
        self._states["agents"] = f"{agents} agent(s) · {catalogue.runs} run(s) · read {catalogue.read_at}"
        self.dialogue.follow_names(catalogue)
        self._tick()
        self._show_keys(self._shown)

    def on_agents_pane_refused(self, message: AgentsPane.Refused) -> None:
        self.remedy = message.said[:110]

    # ---------- the teams, said by the Teams tab ----------
    def on_teams_pane_read(self, message: TeamsPane.Read) -> None:
        self._states["teams"] = message.bar
        self.tasks.reread()                              # the team moved: the tasks are read again, once shown
        self._tick()

    def on_teams_pane_refused(self, message: TeamsPane.Refused) -> None:
        self.remedy = message.said[:110]

    def on_teams_pane_task_asked(self, message: TeamsPane.TaskAsked) -> None:
        """The last ring of a ceremony asked: the Tasks tab shows every task of its team, the cursor on it."""
        self.show_pane("tasks")
        self.tasks.focus_task(message.team, message.task)

    # ---------- the tasks, said by the Tasks tab ----------
    def on_tasks_pane_read(self, message: TasksPane.Read) -> None:
        self._states["tasks"] = message.bar
        self._title_tasks()
        self._follow_turns()
        self._tick()

    def on_tasks_pane_refused(self, message: TasksPane.Refused) -> None:
        self.remedy = message.said[:110]

    def on_tasks_pane_played(self, message: TasksPane.Played) -> None:
        self._note = f"played {message.command}"
        self._tick()

    async def on_teams_pane_member_asked(self, message: TeamsPane.MemberAsked) -> None:
        await self.open_member(message.team, message.member, message.path, message.run, message.running)

    async def on_agents_pane_member_asked(self, message: AgentsPane.MemberAsked) -> None:
        await self.open_member(message.team, message.member, message.path, message.run, False)

    async def open_member(self, team: str, member: str, path: str, run: str, running: bool) -> None:
        """The run of a member of a team, READ in a tab of the dialogue -- one run, one tab: a tab that holds it is
        activated. Its source is a `Follow`: the team's watch subscribed first, then the run's kept flow read --
        its exchanges built as lived turns, in one mount --, or, for a run without a kept flow, its exchanges, the
        last one opening live when a wake-up of the member plays. No `agent chat` is launched."""
        view = self.dialogue.view_of(path, run)
        if view is not None:
            self.show_pane("dialogue")
            self.call_after_refresh(self.dialogue.activate_view, view)
            return
        follow = await Follow(self._house.root, team, member, path, run).open()
        flowed, face = await follow.kept()
        past: list[dict] = []
        if not flowed:
            exchanges, face = await follow.exchanges()
            past = follow.past(exchanges, running)
        if face.rc != 0:
            self.remedy = said_of(face)[:110]
        thread = Thread(path, run, name=f"{team}/{member}", team=team, member=member)
        self.show_pane("dialogue")
        self.call_after_refresh(self.dialogue.adopt, thread, follow, follow.events(), None, True, past,
                                follow.replayed())

    def on_teams_pane_played(self, message: TeamsPane.Played) -> None:
        self._note = f"played {message.command}"
        self._tick()

    async def on_agents_pane_open_asked(self, message: AgentsPane.OpenAsked) -> None:
        """The ONE opener of a conversation at the gesture -- one run, one tab: a LIVE view of the run
        asked is activated and nothing is launched; a FINISHED one is taken up in place, its transcript
        kept; otherwise the run's past is read -- its kept flow (`flow --json`), built as lived turns in one mount
        before the conversation's own events, else its exchanges (`exchanges --json`) as history --, the conversation
        opened on the app's loop and adopted by the dialogue in a tab of its own, the dialogue shown;
        a refusal of the verb arrives as its first event and stays in its tab. A new run (`n`, no key)
        always opens."""
        view = self.dialogue.view_of(message.agent, message.run)
        if view is not None and not view.conversation.ended:
            self.show_pane("dialogue")
            self.call_after_refresh(self.dialogue.activate_view, view)
            return
        history = message.history
        past = []
        if view is None and message.run and history is None:   # a tab is born: the run's past first
            found, _ = await flow(self._house.root, message.agent, message.run)
            past = lived(found, message.run)
            if not past:                         # no kept flow: the exchanges the house kept
                face = await play_verb(["agent", "exchanges", message.agent, message.run, "--json"], self._house.root)
                if face.rc != 0:
                    self.remedy = said_of(face)[:110]
                history = objects(face)
        conversation = await Conversation(self._house.root, message.agent, message.run,
                                          self._flags + message.flags).open()   # the overlay's after those of `--`
        if view is not None:
            self.show_pane("dialogue")
            self.call_after_refresh(self.dialogue.take_up, view, conversation, conversation.events())
            return
        known = self.agents.catalogue.find(message.agent, message.run or "")
        thread = Thread(message.agent, message.run or "", name=known.name if known else message.name,
                        naming="" if known else message.name)   # a name typed for a new run: played at its `opened`
        self.show_pane("dialogue")
        # adopted once the dialogue is drawn: its row of tabs, hidden until now, applies its
        # own activation as it shows, which would otherwise undo the new tab's
        self.call_after_refresh(self.dialogue.adopt, thread, conversation, conversation.events(), None,
                                True, history or [], past)

    def saw(self, kind: str) -> int:
        """-> how many events of that kind the conversations took -- `team:<event>` the objects of the
        Teams tab's watch (what `--wait` watches)."""
        if kind.startswith("team:"):
            return self.teams.saw(kind) + self.tasks.saw(kind)
        return self.dialogue.saw(kind)

    def counts(self) -> dict[str, int]:
        found = {**self.dialogue.counts(), **self.teams.counts()}
        for kind, count in self.tasks.counts().items():
            found[kind] = found.get(kind, 0) + count
        return found

    # ---------- the gestures ----------
    def action_toggle_conduction(self) -> None:
        """`c`: the lines of conduction hidden or shown -- on the Teams tab, the ceremonies of the team."""
        if self._shown == "teams":
            self.teams.show_ceremonies()
            return
        view = self.dialogue.active_view
        if self._shown == "dialogue" and view is not None:
            view.toggle_conduction()
            self._show_keys(self._shown)

    def action_copy(self) -> None:
        """`ctrl+c`: the selection copied to the terminal's clipboard; the status says how much."""
        text = self.screen.get_selected_text()
        if text:
            self.copy_to_clipboard(text)
            self._note = f"copied {len(text)} chars"
        else:
            self._note = "nothing selected"
        self._tick()

    def action_select_all(self) -> None:
        """`ctrl+a`: the event an overlay shows, whole, or the active conversation's whole transcript."""
        if isinstance(self.screen, EventScreen):
            self.screen.select_all()
            return
        view = self.dialogue.active_view
        if self._shown == "dialogue" and view is not None:
            view.select_all()

    async def action_escape(self) -> None:
        """Escape: leave the line, so the letters act -- during a turn as at rest; it never stops a turn."""
        self.screen.set_focus(None)

    async def action_stop_turn(self) -> None:
        """`ctrl+g`: the turn under way on the active conversation stopped -- what the stop button does."""
        view = self.dialogue.active_view
        if self._shown == "dialogue" and view is not None:
            await view.stop()

    def action_write(self) -> None:
        """`i`: back to the active conversation's line -- on the Teams tab, the run of the member under the
        Members cursor, read in a tab of the dialogue."""
        view = self.dialogue.active_view
        if self._shown == "dialogue" and view is not None:
            view.focus_line()
        elif self._shown == "teams":
            self.teams.inspect_member()

    def action_new(self) -> None:
        """`n`: on the Agents tab, a new conversation with the agent under the cursor; elsewhere,
        the Agents tab -- where conversations are opened."""
        if self._shown == "agents":
            self.agents.new_run()
        elif self._shown == "teams":
            self.teams.new_task()
        elif self._shown == "tasks":
            self.tasks.new_task()
        else:
            self.show_pane("agents")

    def action_params(self) -> None:
        """`p`: the parameters of the active conversation's run, in their overlay."""
        if self._shown == "dialogue":
            self.dialogue.ask_params()

    async def action_conduct(self) -> None:
        """`o`: the conduction of the active conversation's next exchanges, the other way round."""
        if self._shown == "dialogue":
            await self.dialogue.toggle_conduct()

    async def action_stats(self) -> None:
        """`s`: the statistics of the active conversation's run, in their overlay."""
        if self._shown == "dialogue":
            view = self.dialogue.active_view
            known = self.agents.catalogue.find(view.thread.agent, view.thread.run) if view is not None else None
            await self.dialogue.show_stats(known)
        elif self._shown == "tasks":
            self.tasks.stop_task()

    def action_packages(self) -> None:
        """`k`: the packages of the active conversation's run, in their overlay."""
        if self._shown == "dialogue":
            self.dialogue.ask_packages()
        elif self._shown == "tasks":
            self.tasks.kill_task()

    def action_theme(self) -> None:
        """`t`: the overlay of the themes -- the one under the cursor shows at once; the one chosen is
        kept for the next opening, `escape` brings the theme of before back."""
        def chosen(name: str | None) -> None:
            if name:
                memory.keep_theme(name)
            self._show_keys(self._shown)
        self.push_screen(ThemeScreen(self.theme), chosen)

    def action_maintain(self) -> None:
        """`U`: `upgrade` or `doctor` of the machine, its command shown as every gesture's, then the post's
        opening again (`./pp ui`). Chosen, the verb is written for the console (`memory.relaunch`) and the post
        leaves on the code that asks the console to play it -- its conversations and watches closed as it leaves,
        their hold on the machine given back -- then to open the post again on its tabs."""
        if self._relaunched:
            self.remedy = "opened again after a maintenance: quit, then ./pp ui, to ask another"
            return

        def chosen(argv: list[str] | None) -> None:
            if not isinstance(argv, list) or not argv:
                return
            code = memory.relaunch(argv[0])
            if code is None:
                self.remedy = "no installed instance here: nothing to upgrade"
                return
            self.exit(return_code=code)
        verbs = (("upgrade -- the machine from its source", "upgrade"), ("doctor -- the machine repaired", "doctor"))
        self.push_screen(GestureScreen(
            "upgrade or repair the machine", (Field("verb", "verb", "list",
                                                    "the post closes, the verb plays, the post opens again",
                                                    verbs, "upgrade"),),
            lambda values: [values["verb"]] if values.get("verb") in ("upgrade", "doctor") else None,
            head=palette.dim("then the post opens again on its tabs: ./pp ui")), chosen)

    async def action_add_agent(self) -> None:
        """`a` on the Agents tab: a new agent, its path asked, its command shown first -- on the Teams tab, the
        responses of the member under the Members cursor."""
        if self._shown == "agents":
            self.agents.ask_add()
        elif self._shown == "teams":
            await self.teams.member_responses()

    async def action_close_tab(self) -> None:
        """`x`: the active conversation's tab closed."""
        if self._shown == "dialogue":
            await self.dialogue.close_active()
            self._show_keys(self._shown)

    def action_resume_task(self) -> None:
        """`r` on the Tasks tab: the task under the cursor resumed -- a run is named in its parameters (`p`)."""
        if self._shown == "tasks":
            self.tasks.resume_task()

    # ---------- the gestures of the Teams tab alone ----------
    def action_message(self) -> None:
        """`m` on the Tasks tab: a note or a reply on the task under the cursor, written in an overlay."""
        if self._shown == "tasks":
            self.tasks.write()

    async def action_start_team(self) -> None:
        if self._shown == "teams":
            await self.teams.start_team()

    async def action_new_team(self) -> None:
        """`N`: a team born from a template, on the Teams tab."""
        if self._shown == "teams":
            await self.teams.new_team()

    def action_stop_all(self) -> None:
        if self._shown == "teams":
            self.teams.stop_all()

    def action_pause(self) -> None:
        """`P` on the Teams tab: the team chosen paused, or resumed."""
        if self._shown == "teams":
            self.teams.toggle_pause()

    def action_tick(self) -> None:
        if self._shown == "teams":
            self.teams.tick()

    def action_reset_member(self) -> None:
        if self._shown == "teams":
            self.teams.reset_member()

    def action_ring(self) -> None:
        """`g` on the Teams tab: the ceremonies of the team, where `g` rings the one under the cursor."""
        if self._shown == "teams":
            self.teams.show_ceremonies()

    async def action_inbox(self) -> None:
        """`b`: on the Teams tab the owner's inbox of the team chosen; on the Dialogue tab the lines of the calls of
        the active conversation hidden or shown."""
        if self._shown == "teams":
            await self.teams.show_inbox()
            return
        view = self.dialogue.active_view
        if self._shown == "dialogue" and view is not None:
            view.toggle_calls()
            self._show_keys(self._shown)

    async def action_declaration(self) -> None:
        """`e` on the Teams tab: the declaration of the team chosen, read only."""
        if self._shown == "teams":
            await self.teams.show_declaration()

    def action_budget(self) -> None:
        """`B` on the Teams tab: the budget of the team chosen raised."""
        if self._shown == "teams":
            self.teams.raise_budget()

    def action_detail(self) -> None:
        """`d` on the Teams tab: the member under the cursor, whole."""
        if self._shown == "teams":
            self.teams.member_detail()

    def action_step(self, menu: str, by: int) -> None:
        """`[` `]` and `{` `}`: the folded menus changed -- the team on the Teams tab, `SHOW` and `TEAM` on Tasks."""
        if self._shown == "teams":
            self.teams.step_team(by)
        elif self._shown == "tasks":
            self.tasks.step(menu, by)

    async def action_journal(self) -> None:
        """`l`: the journal of the team -- the one chosen on the Teams tab, the task's on the Tasks tab."""
        if self._shown == "teams":
            await self.teams.show_journal()
        elif self._shown == "tasks":
            await self.tasks.show_journal()

    async def action_result(self) -> None:
        """`v` on the Tasks tab: the result of the task under the cursor."""
        if self._shown == "tasks":
            await self.tasks.show_result()

    def action_reread(self) -> None:
        """`u`: the tab shown read again -- the teams, the tasks, the agents; on the dialogue, the active tab's past."""
        if self._shown == "teams":
            self.teams.reread()
        elif self._shown == "tasks":
            self.tasks.reread()
        elif self._shown == "dialogue":
            self.dialogue.reload_active()
        else:
            self.agents.reread()

    def action_next_tab(self) -> None:
        self.dialogue.step(+1)

    def action_previous_tab(self) -> None:
        self.dialogue.step(-1)

    async def action_quit(self) -> None:
        await self.dialogue.close_all()
        await self.teams.close()
        await self.tasks.close()
        self.exit()

    # ---------- the tabs ----------
    def action_show_pane(self, key: str) -> None:
        self.show_pane(key)

    def show_pane(self, key: str) -> None:
        self.query_one(f"#{POST_TABS}", TabbedContent).active = f"tab-{key}"
        self._shown_now(key)

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        if event.tabbed_content.id == POST_TABS:
            self._shown_now(str(event.pane.id).removeprefix("tab-"))

    def _shown_now(self, key: str) -> None:
        self._shown = key
        self.teams.active = key == "teams"
        self.tasks.active = key == "tasks"
        if key == "agents":
            self.agents.focus_table()
        elif key == "teams":
            self.teams.shown()
        elif key == "tasks":
            self.tasks.shown()
        elif key == "dialogue":
            self.dialogue.focus_active()
        self._tick()
        self._show_keys(key)

    def _show_keys(self, key: str) -> None:
        """The keys of the pane shown, on as many lines as the width asks -- the footer grows with them."""
        if not self.is_running:
            return
        shown = [("q", "quit")] + [(one.digit, one.key) for one in PANES if one.key != key]
        shown += getattr(self.query_one(f"#pane-{pane(key).key}"), "keys", [])
        shown += [("U", "upgrade"), ("t", f"theme: {self.theme}")]
        self.query_one("#keys", Static).update(palette.keys_lines(shown, max(1, self.size.width - 2)))

    def on_resize(self) -> None:
        self._show_keys(self._shown)
