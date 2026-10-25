"""dialogue -- the POST OF CONVERSATIONS: a nested row of tabs inside the dialogue tab, ONE tab
per conversation -- its transcript above (the one scroller), its message line below, its own
`Conversation` held on the app's loop and its own task that consumes the face's events:
switching tabs reloads nothing, a conversation of the background goes on and counts what it
says that the operator has not read (bold on its tab's title). With no conversation open the
tab says where to open one (the Agents tab). Every event is rendered by its VOICE through the
palette, in the transcript (`panes/transcript.py`): the principal and the answer of a turn in
markdown under their head, each conduction, the steps of each launch and each word of the agent
on a line of its own that opens whole (`c` hides the lines of conduction and of steps and shows
them again), the verdict stamped, the end of a flow with its exit code -- a tab
whose flow ended stays, `x` alone closes it. Above the transcript, the BUBBLE says the principal's message of the
turn at the top of the view, rewritten only when that turn changes; beside the message line, the GAUGE says the
run's context as `agent stats --json` says it, read again after each verdict and at the opening of a run taken up. The conversations open are the post's MEMORY,
kept each time a tab opens or closes (`memory.keep`); given back at the post's opening, each tab stands at once with
its conversation DORMANT -- no `agent chat` before a gesture speaks to it -- and its run's exchanges read when the
tab is first shown, shown as history. `u` reads the active tab's past again -- its kept flow, else its exchanges -- built in
one mount; a tab whose turn runs reloads nothing. What the house says (`refused`, `ended`)
goes to the frame's remedy too, the state to its status.

A tab may hold the run of a MEMBER of a team, READ: its thread marks the team and the member, its source is
a `faces.team.Follow` -- the run's past, then its wake-ups as the team's watch says them --, and the view
has a banner and no message line: nothing is sent, no `agent chat` holds the run's wake lock, and the
memory does not keep it (opened again, it would be a conversation)."""
from __future__ import annotations

import asyncio
from typing import AsyncIterator

from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widgets import Button, Static, TabbedContent, TabPane

import memory
import palette
from faces import objects, play_verb
from faces.chat import Conversation, Opening, lived
from faces.team import flow
from model import PaneSpec
from model.dialogue import ENDED, Dialogue, Event, Thread, Transcript
from model.runs import Catalogue, RunLine
from panes import live
from panes.fields import MessageArea
from panes.agents import said_of
from panes.overlays import AskScreen, PackagesScreen, RunParamsScreen, StatsScreen
from panes.transcript import TranscriptView

TABS = "conversations"               # the id of the nested row of tabs
GAUGE_WAIT = 10.0                    # the bound of a render's wait for the gauges being read


class ConversationView(Vertical):
    """One conversation's tab: the bubble of the turn at the top, the transcript and the message line, on one
    `Thread` and one `Conversation`; beside the line, the gauge of the run's context and the stop button -- shown
    while a turn runs, gone at rest."""

    DEFAULT_CSS = """
    ConversationView { height: 1fr; }
    ConversationView > #read-only { dock: top; height: 1; padding: 0 1; }
    ConversationView > #paused { height: 1; padding: 0 1; }
    ConversationView > #bubble { height: 1; padding: 0 1; }
    ConversationView > #line { dock: bottom; height: auto; }
    ConversationView > #line > MessageArea { width: 1fr; }
    ConversationView > #line > #stop { width: auto; min-width: 10; }
    ConversationView > #line > #context { width: auto; height: 3; padding: 1 1 0 1; }
    """

    def __init__(self, thread: Thread, conversation: Conversation, pane_id: str) -> None:
        super().__init__(id=f"view-{pane_id}")
        self.thread = thread
        self.conversation = conversation
        self.pane_id = pane_id
        self.counts: dict[str, int] = {}

    @property
    def read_only(self) -> bool:
        return self.thread.read_only

    def compose(self):
        banner = Static(palette.PAUSED_BANNER, id="paused", markup=False)
        banner.display = not self.thread.conducted and not self.read_only
        if self.read_only:
            yield Static(palette.read_only_banner(self.thread.member, self.thread.team), id="read-only", markup=False)
        bubble = Static("", id="bubble", markup=False)
        bubble.display = False                          # no turn yet
        yield bubble
        yield TranscriptView(steps_alone=self.read_only)
        yield banner                                    # just above the message line, under the transcript
        stop = Button(palette.STOP, id="stop", variant="error")
        stop.display = self.thread.busy and not self.read_only
        box = MessageArea(placeholder=self._placeholder(), id="message", disabled=self.read_only)
        line = Horizontal(Static(palette.context_gauge(None), id="context", markup=False), box, stop, id="line", classes="rule-top")
        line.display = not self.read_only               # a run read: nothing to send
        yield line

    def _placeholder(self) -> str:
        if self.thread.busy:
            return "the agent is working -- enter waits for its answer"
        if not self.thread.conducted:
            return palette.PAUSED_LINE
        return f"message to {self.thread.agent} -- enter sends"

    def _show_conducted(self) -> None:
        """`pp off` in the tab itself, read from the thread alone: the banner above the message line, the line
        bordered -- both gone once the exchanges are conducted again."""
        self.query_one("#paused", Static).display = not self.thread.conducted and not self.read_only
        self.query_one(MessageArea).set_class(not self.thread.conducted, "paused")

    @property
    def transcript(self) -> TranscriptView:
        return self.query_one(TranscriptView)

    def on_transcript_view_turn_shown(self, message: TranscriptView.TurnShown) -> None:
        """The turn at the top of the view changed: the bubble rewritten, its one line alone."""
        message.stop()
        bubble = self.query_one("#bubble", Static)
        bubble.update(message.said, layout=False)
        bubble.display = True

    def show_context(self, context: dict | None) -> None:
        """The gauge of the run's context, as `agent stats --json` said it (`None`: the face said none)."""
        self.query_one("#context", Static).update(palette.context_gauge(context))

    def rebind(self, thread: Thread, conversation: Conversation) -> None:
        """A new conversation under this view, on a thread made anew: the transcript kept -- the
        memory of the events is the tab's --, the message line open again."""
        self.thread, self.conversation = thread, conversation
        box = self.query_one(MessageArea)
        box.disabled = False
        box.placeholder = self._placeholder()
        self._show_conducted()

    async def show_history(self, exchanges: list[dict]) -> None:
        """The run's past exchanges, as `agent exchanges` says them, shown dim -- the transcript built in one mount."""
        await self.transcript.rebuild(history=Transcript.history(exchanges))

    # ---------- the events ----------
    async def take(self, event: Event, active: bool) -> None:
        """One event of the flow: the thread grows, the transcript gets the event's block; the
        message line stays open while a turn runs -- what is typed there kept, dim, `enter`
        waiting for the end of the turn -- and closes for good when the flow ended."""
        self.thread.take(event, active)
        self.counts[event.kind] = self.counts.get(event.kind, 0) + 1
        if not live(self):
            return
        await self.transcript.add(event)
        if not live(self):                       # the tab closed, or the post left, while the block was mounting
            return
        if self.read_only:                       # no line, no stop: the run is the team's
            return
        box = self.query_one(MessageArea)
        box.set_class(self.thread.busy, "busy")
        self.query_one("#stop", Button).display = self.thread.busy
        self._show_conducted()
        if event.kind == ENDED:
            box.disabled = True
            box.placeholder = "the conversation ended -- x closes the tab"
            return
        box.placeholder = self._placeholder()

    # ---------- the gestures ----------
    def toggle_conduction(self) -> None:
        self.transcript.toggle_conduction()

    def toggle_calls(self) -> None:
        self.transcript.toggle_calls()

    def select_all(self) -> None:
        """`ctrl+a`: the whole transcript selected, as the mouse would."""
        self.transcript.text_select_all()

    async def stop(self) -> bool:
        """`stop` to the verb while an exchange runs -> whether one was running; a run read is never stopped."""
        if not self.thread.busy or self.read_only:
            return False
        await self.conversation.stop()
        return True

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """The stop button, clicked or `enter` on it: the turn under way stopped."""
        if event.button.id == "stop":
            event.stop()
            await self.stop()

    def focus_line(self) -> None:
        box = self.query_one(MessageArea)
        if not box.disabled:
            box.focus()

    async def on_message_area_submitted(self, event: MessageArea.Submitted) -> None:
        event.stop()
        text = event.text.strip()
        if text and not self.thread.busy:
            await self.conversation.send(text)
            event.area.clear()

    @property
    def keys(self) -> list[tuple[str, str]]:
        calls = ("b", f"calls: {'hidden' if self.transcript.calls_hidden else 'shown'}")
        if self.read_only:
            return [("c", f"steps: {'hidden' if self.transcript.conduction_hidden else 'shown'}"), calls,
                    ("s", "stats"), ("u", "reload"), ("x", "close")]
        return [("c", f"conduction: {'hidden' if self.transcript.conduction_hidden else 'shown'}"), calls,
                ("enter", "waits" if self.thread.busy else "send"),
                *([("ctrl+g", "stop the turn")] if self.thread.busy else []),
                ("o", f"pp: {'on' if self.thread.conducted else 'off'}"), ("k", "packages"),
                ("s", "stats"),
                ("p", "params"), ("u", "reload"), ("x", "close"), ("i", "write")]


class DialoguePane(Vertical):
    """The dialogue: one tab per conversation open, or the word of where to open one."""

    DEFAULT_CSS = """
    DialoguePane { height: 1fr; }
    DialoguePane > TabbedContent { height: 1fr; }
    #empty { height: auto; padding: 1 2; }
    """

    class Said(Message):
        """An event of the flow reached a conversation -- the frame updates its lines."""

        def __init__(self, event: Event, thread: Thread, active: bool) -> None:
            super().__init__()
            self.event = event
            self.thread = thread
            self.active = active

    class Activated(Message):
        """The active conversation changed (None: no conversation open)."""

        def __init__(self, view: ConversationView | None) -> None:
            super().__init__()
            self.view = view

    class Named(Message):
        """A run was named from its tab: the Agents tab reads the faces again."""

    class Refused(Message):
        """A verb the dialogue played refused: what it said, for the remedy line."""

        def __init__(self, said: str) -> None:
            super().__init__()
            self.said = said

    def __init__(self, spec: PaneSpec, house: str = "", started: list[Opening] = (),
                 agents: list[tuple[str, str | None]] = (), flags: tuple[str, ...] = (),
                 histories: list[list[dict] | None] = ()) -> None:
        super().__init__(id=f"pane-{spec.key}")
        self.spec = spec
        self.house = house
        self.flags = tuple(flags)           # what followed `--`: every conversation opened carries it
        self.dialogue = Dialogue()
        self._started = list(started)       # opened before the post drew, on this same loop
        self._agents = list(agents)         # (agent, run) of each, in order
        self._histories = list(histories)   # the history of each; None: read once its tab stands (the memory's)
        self._views: dict[str, ConversationView] = {}
        self._serial = 0
        self._adopted = False               # the conversations of the start are in their tabs
        self.frame = 0                      # the spinner's frame, turned by the app while a turn runs
        self._kept: list[tuple[str, str]] | None = None   # what the memory says, once written
        self._gauging = 0                   # the readings of a gauge under way
        self._reading = 0                   # the pasts of tabs being read
        self._owed: set[str] = set()        # the tabs given back whose past is read when they are first shown

    # ---------- composition ----------
    def compose(self):
        yield Static(palette.empty_dialogue(), id="empty", markup=False)
        yield TabbedContent(id=TABS)

    def on_mount(self) -> None:
        self._show_empty()
        # the conversations of the start are adopted once the screen is drawn: the row of
        # tabs has then applied its own initial activation, which would otherwise undo ours
        self.call_after_refresh(self._adopt_started)

    async def _adopt_started(self) -> None:
        last = None
        asked = []
        for index, ((agent, run), started) in enumerate(zip(self._agents, self._started)):
            history = self._histories[index] if index < len(self._histories) else []
            last = await self.adopt(Thread(agent, run or ""), started.conversation, started.events,
                                    started.first, activate=False, history=history or [])
            if history is None and run:
                asked.append(last)
        if last is not None:         # ONE activation, after every tab stands
            self.query_one(f"#{TABS}", TabbedContent).active = last.pane_id
        self._adopted = True
        self._owed |= {view.pane_id for view in asked}   # the memory's tabs: each past read when its tab is shown
        self._past_when_shown(self.active_view)

    def _past_when_shown(self, view: ConversationView | None) -> None:
        """The tab shown reads its run's past once, if it is a tab given back that has not read it yet."""
        if view is None or view.pane_id not in self._owed:
            return
        self._owed.discard(view.pane_id)
        self._reading += 1
        self.run_worker(self._history_of(view), group=view.pane_id)

    async def _history_of(self, view: ConversationView) -> None:
        """A tab of the memory in HISTORY: its run's exchanges (`agent exchanges --json`) shown dim -- unless its
        conversation woke meanwhile, its own events then the tab's."""
        try:
            face = await play_verb(["agent", "exchanges", view.thread.agent, view.thread.run, "--json"], self.house)
            if face.rc != 0:
                self.post_message(self.Refused(said_of(face)))
            elif view.pane_id in self._views and live(view) and getattr(view.conversation, "dormant", False):
                await view.show_history(objects(face))
        finally:
            self._reading -= 1

    def reload_active(self) -> None:
        """`u`: the active tab's past read again -- its kept flow (`agent flow --json`), else its exchanges -- and
        built in one mount; a tab whose turn runs, or with no run yet, reloads nothing and says why."""
        view = self.active_view
        if view is None:
            return
        if view.thread.busy:
            self.post_message(self.Refused(f"{view.thread.agent}: a turn runs -- u reloads once it ended"))
            return
        if not view.thread.run:
            self.post_message(self.Refused(f"{view.thread.agent}: no run yet -- nothing to reload"))
            return
        self._reading += 1
        self.run_worker(self._reload(view), group=view.pane_id)

    async def _reload(self, view: ConversationView) -> None:
        try:
            agent, run = view.thread.agent, view.thread.run
            found, face = await flow(self.house, agent, run)
            past = lived(found, run) if face.rc == 0 else []
            if not past:
                face = await play_verb(["agent", "exchanges", agent, run, "--json"], self.house)
            if face.rc != 0:
                self.post_message(self.Refused(said_of(face)))
                return
            if view.pane_id not in self._views or not live(view):
                return
            if past:
                await view.transcript.rebuild(past)
            else:
                await view.show_history(objects(face))
        finally:
            self._reading -= 1

    async def settled(self) -> None:
        """Returns once the conversations of the start are in their tabs -- what a render waits for."""
        while not self._adopted:
            await asyncio.sleep(0.01)

    def _show_empty(self) -> None:
        self.query_one("#empty", Static).display = not self._views
        self.query_one(f"#{TABS}", TabbedContent).display = bool(self._views)

    # ---------- the conversations, opened and closed ----------
    async def adopt(self, thread: Thread, conversation: Conversation, events: AsyncIterator[Event],
                    first: Event | None = None, activate: bool = True, history: list[dict] = (),
                    past: list[Event] = ()) -> ConversationView:
        """A conversation the app opened, in a tab of its own: its past first -- its history (`exchanges`), or its
        kept flow, built in one mount --, its first event when it was read already, then a task on the rest of its
        flow."""
        self._serial += 1
        pane_id = f"conv-{self._serial}"
        view = ConversationView(thread, conversation, pane_id)
        tabs = self.query_one(f"#{TABS}", TabbedContent)
        await tabs.add_pane(TabPane(thread.label, view, id=pane_id))
        self._views[pane_id] = view
        self._show_empty()
        self.dialogue.open(thread)
        if history:
            await view.show_history(list(history))
        elif past:
            await view.transcript.rebuild(past)
        if activate:
            tabs.active = pane_id
        if first is not None:
            await self._take(view, first)
        self.run_worker(self._consume(view, events), name=pane_id, group=pane_id)
        self._remember()
        return view

    def view_of(self, agent: str, run: str | None) -> ConversationView | None:
        """-> the view that holds the run `run` of `agent`, None without a run or such a view -- a view
        is known by its thread's agent and run, never by what its flow said in words."""
        if not run:
            return None
        return next((view for view in self._views.values()
                     if view.thread.agent == agent and view.thread.run == run), None)

    def activate_view(self, view: ConversationView) -> None:
        """The view's tab made the active one."""
        self.query_one(f"#{TABS}", TabbedContent).active = view.pane_id

    async def take_up(self, view: ConversationView, conversation: Conversation,
                      events: AsyncIterator[Event]) -> None:
        """A FINISHED view of a run taken up IN PLACE: its tab and its transcript kept, a new
        conversation under it on a thread made anew (its state, its unread), the history not
        replayed -- the transcript carries it --; then a task on the new flow, the view active."""
        await view.conversation.close()
        self.workers.cancel_group(self, view.pane_id)
        index = self.dialogue.threads.index(view.thread)
        thread = Thread(view.thread.agent, view.thread.run, name=view.thread.name)
        self.dialogue.threads[index] = thread
        view.rebind(thread, conversation)
        self.activate_view(view)
        self._retitle(view)
        self.run_worker(self._consume(view, events), name=view.pane_id, group=view.pane_id)
        self._remember()

    async def _consume(self, view: ConversationView, events: AsyncIterator[Event]) -> None:
        async for event in events:
            if not live(self):                   # the post leaves: its widgets go, the flow is no longer read
                return
            await self._take(view, event)

    async def _take(self, view: ConversationView, event: Event) -> None:
        active = self.active_view is view
        known = view.thread.run
        await view.take(event, active)
        if view.pane_id not in self._views:      # the tab closed while its block was mounting
            return
        if event.kind == "opened" and view.thread.naming and view.thread.run:
            await self._play_naming(view)
        if (not view.read_only and view.thread.run
                and (event.kind == "verdict" or (event.kind == "ready" and event.fields.get("resumed") is True))):
            self._gauging += 1
            self.run_worker(self._gauge(view, view.thread.agent, view.thread.run), group=view.pane_id)
        self._retitle(view)
        self.post_message(self.Said(event, view.thread, active))
        if view.thread.run != known:
            self._remember()

    async def _gauge(self, view: ConversationView, agent: str, run: str) -> None:
        """The gauge of a run read again: `agent stats <agent> <run> --json`, its `context` alone; a refusal, or a run
        without `context`, says `—`."""
        try:
            face = await play_verb(["agent", "stats", agent, run, "--json"], self.house)
            found = objects(face) if face.rc == 0 else []
            if view.pane_id in self._views and live(view):
                view.show_context(found[0].get("context") if found else None)
        finally:
            self._gauging -= 1

    async def gauged(self, seconds: float = GAUGE_WAIT) -> None:
        """Returns once no gauge is being read, no tab reads its past and no read tab reads its run again, or after
        `seconds` -- what a render waits for before it prints."""
        deadline = asyncio.get_event_loop().time() + seconds
        while (self._gauging or self._reading
               or any(getattr(one.conversation, "busy", False) for one in self._views.values())) \
                and asyncio.get_event_loop().time() < deadline:
            await asyncio.sleep(0.01)

    def _retitle(self, view: ConversationView) -> None:
        tabs = self.query_one(f"#{TABS}", TabbedContent)
        tabs.get_tab(view.pane_id).label = palette.tab_label(
            view.thread.label, view.thread.unread, view.thread.busy, self.frame, not view.thread.conducted,
            bool(view.thread.pending), palette.seconds_since(view.thread.turn_at))

    def _turn_title(self, view: ConversationView) -> None:
        """One frame of a title under way: the glyph alone changes, the width stays, so the title is
        repainted without being relabelled -- a relabel moves the row's underline again at every
        frame, and the post never rests while a turn runs."""
        tab = self.query_one(f"#{TABS}", TabbedContent).get_tab(view.pane_id)
        Static.update(tab, palette.tab_label(view.thread.label, view.thread.unread, True, self.frame,
                                             not view.thread.conducted, bool(view.thread.pending),
                                             palette.seconds_since(view.thread.turn_at)))

    @property
    def busy(self) -> bool:
        """Whether a turn runs in any conversation."""
        return any(view.thread.busy for view in self._views.values())

    def spin(self, frame: int) -> None:
        """One frame of the spinner: the titles of the conversations under way turn."""
        self.frame = frame
        for view in self._views.values():
            if view.thread.busy:
                self._turn_title(view)

    def _remember(self) -> None:
        """The conversations open, with their runs known, kept in the post's memory -- each pair
        once, written when they changed."""
        pairs = list(dict.fromkeys((view.thread.agent, view.thread.run) for view in self._views.values()
                                   if view.thread.run and not view.read_only))
        if pairs != self._kept:
            self.app.kept_later(memory.keep, pairs)
            self._kept = pairs

    async def _close_view(self, view: ConversationView) -> None:
        await view.conversation.close()
        self.workers.cancel_group(self, view.pane_id)   # its flow consumed no more: the tab leaves
        index = self.dialogue.threads.index(view.thread)
        self.dialogue.close(index)
        del self._views[view.pane_id]
        await self.query_one(f"#{TABS}", TabbedContent).remove_pane(view.pane_id)
        self._show_empty()
        self._remember()
        if not self._views:
            self.post_message(self.Activated(None))

    async def close_active(self) -> bool:
        """`x`: closes the active conversation's tab (the verb gets `quit`, its run stands).
        -> whether a conversation was closed."""
        view = self.active_view
        if view is None:
            return False
        await self._close_view(view)
        return True

    async def close_all(self) -> None:
        """`q`: every conversation gets `quit`, bounded, before the post leaves; the memory keeps them."""
        for view in list(self._views.values()):
            await view.conversation.close()

    # ---------- the statistics of a run under way ----------
    async def show_stats(self, line: RunLine | None) -> None:
        """`s` on a tab: `agent stats --json` of its run, stacked in an overlay -- `line` the run as the
        catalogue knows it, else one made of the thread's agent and key; no run yet, the remedy says it."""
        view = self.active_view
        if view is None:
            return
        thread = view.thread
        if not thread.run:
            self.post_message(self.Refused(f"{thread.agent}: no run yet -- the statistics wait for the run to open"))
            return
        face = await play_verb(["agent", "stats", thread.agent, thread.run, "--json"], self.house)
        found = objects(face)
        if face.rc != 0 or not found:
            self.post_message(self.Refused(said_of(face)))
            return
        self.app.push_screen(StatsScreen(line or RunLine(thread.agent, thread.run, name=thread.name), found[0]))

    # ---------- the parameters of a run under way ----------
    def ask_params(self) -> bool:
        """`p` on a tab: the overlay of the run's parameters, the provider fixed, the models and the
        spells read from `agent providers --json` as it opens, the packages as the flow said them; `enter` sends
        the CHANGED ones as a `set` -- the verb answers `policy`, or `refused` on the remedy line --, a name
        changed played by `agent name`: at once on a run the flow named, at its `opened` otherwise; then one
        `package` per package changed, as `k` sends them."""
        view = self.active_view
        if view is None:
            return False
        if view.read_only:
            return True                          # a run read: nothing is sent to it
        thread = view.thread
        defaults = {**thread.policy, **({"provider": thread.provider} if thread.provider else {}), "name": thread.name}

        async def offer() -> dict[str, dict]:
            face = await play_verb(["agent", "providers", "--json"], self.house)
            if face.rc != 0:
                self.post_message(self.Refused(said_of(face)))
            return {str(one.get("provider", "")): one for one in objects(face)}

        async def changed(found: dict | None) -> None:
            name = (found or {}).pop("name", None)
            packages = (found or {}).pop("packages", None) or {}
            if name:
                await self.name_run(view, name)
            if found:
                await view.conversation.set(found)
            for package, on in packages.items():
                await view.conversation.package(package, on)
        states = ({str(one.get("name", "")): one.get("on") is True for one in thread.packages}
                  if thread.packages is not None else None)
        self.app.push_screen(RunParamsScreen(f"run {thread.run or '(opening)'} · provider fixed",
                                             [thread.provider] if thread.provider else [], offer, defaults,
                                             running=True, packages=states, pending=thread.pending), changed)
        return True

    # ---------- the conduction and the packages of a run under way ----------
    async def toggle_conduct(self) -> bool:
        """`o` on a tab: `conduct` to the verb, the conduction of the next exchanges the other way
        round -- the tab, the status and the footer follow the `conduct` the verb answers, a
        `refused` goes to the remedy."""
        view = self.active_view
        if view is None:
            return False
        if view.read_only:
            return True                          # a run read: nothing is sent to it
        await view.conversation.conduct(not view.thread.conducted)
        return True

    def ask_packages(self) -> bool:
        """`k` on a tab: the run's packages, as the flow said them, in their overlay -- toggled there
        without sending anything; at `enter`, one `package` per line changed, the switches the verb
        holds waiting until it plays them (the tab and the status say so). A flow that said no
        packages: the remedy says so, nothing is sent."""
        view = self.active_view
        if view is None:
            return False
        if view.read_only:
            return True                          # a run read: nothing is sent to it
        thread = view.thread
        if thread.packages is None:
            self.post_message(self.Refused(f"{thread.agent}: no package list in this flow"))
            return True
        states = {str(one.get("name", "")): one.get("on") is True for one in thread.packages}

        async def applied(changed: dict[str, bool] | None) -> None:
            for name, on in (changed or {}).items():
                await view.conversation.package(name, on)
        self.app.push_screen(PackagesScreen(f"packages of run {thread.run or '(opening)'}", states, thread.pending),
                             applied)
        return True

    # ---------- the name of a run ----------
    async def name_run(self, view: ConversationView, name: str) -> None:
        """A name typed for the view's run: played at once when the flow said the run's key, held for the run's
        `opened` otherwise -- the tab says it meanwhile."""
        if view.thread.run:
            await self.rename(view, name)
            return
        view.thread.naming = view.thread.name = name
        self._retitle(view)

    async def _play_naming(self, view: ConversationView) -> None:
        """The name held for a run that was opening, played now that `opened` said its key; refused, the tab goes
        back to the run's key."""
        name, view.thread.naming, view.thread.name = view.thread.naming, "", ""
        await self.rename(view, name)
        self._retitle(view)

    async def rename(self, view: ConversationView, name: str) -> None:
        """`agent name <agent> <run> <name>` played; the tab says the name; a refusal goes to the remedy."""
        if not view.thread.run:
            self.post_message(self.Refused("no run yet: the name waits for the run to open"))
            return
        face = await play_verb(["agent", "name", view.thread.agent, view.thread.run, name], self.house)
        if face.rc != 0:
            self.post_message(self.Refused(said_of(face)))
            return
        view.thread.name = name
        self._retitle(view)
        self.post_message(self.Named())

    def follow_names(self, catalogue: Catalogue) -> None:
        """A name given elsewhere (the Agents tab) reaches the tab of its run."""
        for view in self._views.values():
            known = catalogue.find(view.thread.agent, view.thread.run)
            if known is not None and known.name and known.name != view.thread.name:
                view.thread.name = known.name
                self._retitle(view)

    # ---------- the tabs ----------
    @property
    def active_view(self) -> ConversationView | None:
        tabs = self.query_one(f"#{TABS}", TabbedContent)
        return self._views.get(str(tabs.active))

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        if event.tabbed_content.id != TABS:
            return
        event.stop()
        view = self._views.get(str(event.pane.id))
        if view is not None:
            self.dialogue.activate(self.dialogue.threads.index(view.thread))
            self._retitle(view)
            self.screen.set_focus(None)          # the line of the tab left takes no key: `i` goes to this one
            self._past_when_shown(view)
        self.post_message(self.Activated(view))

    def focus_active(self) -> None:
        """The dialogue shown: no line takes the focus, the letters act -- `i` alone goes to the message line."""
        self.screen.set_focus(None)

    def step(self, delta: int) -> None:
        """`ctrl+right` / `ctrl+left`: the neighbouring conversation, around."""
        ids = list(self._views)
        if not ids:
            return
        tabs = self.query_one(f"#{TABS}", TabbedContent)
        at = ids.index(str(tabs.active)) if str(tabs.active) in ids else 0
        tabs.active = ids[(at + delta) % len(ids)]

    def saw(self, kind: str) -> int:
        """-> how many events of that kind reached ANY conversation (what `--wait` watches)."""
        return sum(one.counts.get(kind, 0) for one in self._views.values())

    def counts(self) -> dict[str, int]:
        """-> every kind seen by any conversation, with its count."""
        seen: dict[str, int] = {}
        for view in self._views.values():
            for kind, count in view.counts.items():
                seen[kind] = seen.get(kind, 0) + count
        return seen

    @property
    def keys(self) -> list[tuple[str, str]]:
        view = self.active_view
        if view is None:
            return [("n", "open")]
        return view.keys + ([("^←→", "tabs")] if len(self._views) > 1 else [])
