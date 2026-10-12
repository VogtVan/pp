"""transcript -- the TRANSCRIPT of one conversation as a column of BLOCKS, the one scroller of
its tab, its end held in view as blocks arrive, in the order the flow said them. The principal's
message and the answer of a turn (its `response`) are a head (the voice's glyph, the hour) above
the text rendered as MARKDOWN -- tables, code, lists. Every other event of a turn is ONE LINE, its
summary read from the flow's fields: per launch the `conduction` (the blocks it serves), what the
agent did meanwhile -- each call of a tool (`⚙`, updated by its result), ONE line of its thought (`∴`),
its intermediate words (`◀`; the last ones not twice when the agent's answer repeats them) --, the line
of its steps (counted by kind) and what the agent answered at that launch. A line whose overlay has a
content to show is LIVE: it takes the focus (`tab`) and opens that content WHOLE in an overlay (`enter`
or a click) -- built when it opens, never before; a line with nothing to show is STALE: the palette's
`STALE` look, no focus, nothing opens -- judged by its event's fields alone, again at each update. The verdict is a line; a run taken up shows its past turns dim first; what the
house says (the end of the flow, a refused command, whether the exchanges are conducted, a
package in or out of the run's play, a kind nobody knows) is a dim line. `c` hides the lines of
conduction, of steps, of calls and of thought, and shows them again, by `display` alone -- nothing is
rewritten. The TURN AT THE TOP of the view -- the last turn at the end of the transcript, else the last whose head
stands at or above the top, found by bisection on the heads -- is said to the tab (`TurnShown`) each time it
changes, as the view scrolls or a turn arrives: the tab's bubble follows, and nothing of the transcript is laid out
again; `layouts` counts the arrangements the transcript computed, what the bench reads to say so."""
from __future__ import annotations

from bisect import bisect_right

from rich.text import Text
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.message import Message
from textual.widgets import Markdown, Static

import palette
from model.dialogue import ENDED, UNREADABLE, Event, Turn
from panes.overlays import EventScreen

SILENT = ("ready", "waiting", "closed", "opened")   # what the frame's status says, no block
KEPT = ("agent", "step")                   # what may follow a launch's last words without showing them


class EventLine(Static, can_focus=True):
    """One event as one line: its summary, and its content opened whole in `EventScreen` -- LIVE when it
    has a content to show, STALE otherwise (the `STALE` look, no focus, nothing opens)."""

    BINDINGS = [Binding("enter", "open", "open", show=False)]

    def __init__(self, summary: Text, event: Event | None = None, classes: str = "") -> None:
        super().__init__(summary, markup=False, classes=f"line {classes}".strip())
        self.event = event
        self.show(summary)

    def has_content(self) -> bool:
        """-> whether the overlay has something to show: the text the event carries, not blank."""
        return bool(str(self.event.fields.get("text") or "").strip()) if self.event else False

    def show(self, summary: Text) -> None:
        """The line drawn with its summary, judged again: live as the palette made it, or stale."""
        self.summary = summary
        live = self.has_content()
        self.set_class(not live, palette.STALE)
        self.update(summary if live else palette.stale(summary))

    def allow_focus(self) -> bool:
        return self.has_content()

    def whole(self) -> Text:
        """-> what the line stands for, whole: the text the event carries."""
        return Text(str(self.event.fields.get("text") or "") if self.event else "")

    def kind_label(self) -> str:
        """-> the label of the line's kind, read from its event's `kind` by the palette's table."""
        return palette.event_label(self.event.kind, self.event.fields) if self.event else ""

    def action_open(self) -> None:
        if self.has_content():
            self.app.push_screen(EventScreen(self.summary, self.whole, self.kind_label(),
                                             self.event is not None and self.event.kind in palette.MARKDOWN_KINDS))

    def on_click(self) -> None:
        self.action_open()


class StepsLine(EventLine):
    """The steps of one launch on one line, counted by kind; opened, each step on its line."""

    def __init__(self, steps: list[Event]) -> None:
        self.steps = list(steps)
        super().__init__(palette.steps_line(self.steps), classes="conduction")

    def kind_label(self) -> str:
        return palette.event_label("step")

    def has_content(self) -> bool:
        return bool(self.steps)

    def take(self, step: Event, hidden: bool) -> None:
        self.steps.append(step)
        self.show(palette.steps_line(self.steps))
        self.display = not hidden

    def whole(self) -> Text:
        said = Text()
        for one in self.steps:
            said.append_text(palette.step_line(one.at, str(one.fields.get("event", "")),
                                               {k: v for k, v in one.fields.items() if k != "event"}))
            said.append("\n")
        return said


class ToolLine(EventLine):
    """A call of a tool on one line, updated when its result comes; opened, its input then its result."""

    def __init__(self, event: Event) -> None:
        self.result: dict | None = None
        super().__init__(palette.tool_line(event.at, event.fields, None), event, "conduction")

    def has_content(self) -> bool:
        return True                            # its input shows from the call on, before its result

    def took(self, result: Event) -> None:
        self.result = dict(result.fields)
        self.show(palette.tool_line(self.event.at, self.event.fields, self.result))

    def whole(self) -> Text:
        return palette.call_whole(self.event.fields, self.result)


class ResultLine(EventLine):
    """The result of a call the flow never announced; opened, what the tool gave back."""

    def __init__(self, event: Event) -> None:
        super().__init__(palette.result_line(event.at, event.fields), event, "conduction")

    def has_content(self) -> bool:
        return bool(str(self.event.fields.get("content") or "").strip())

    def whole(self) -> Text:
        return Text(str(self.event.fields.get("content") or ""))


class ThinkingLine(EventLine):
    """The thought of ONE launch on one line, updated by each count or text the flow says; opened,
    every text it said -- a count alone is no content: the line stays stale until a text comes."""

    def __init__(self, event: Event) -> None:
        self.texts: list[str] = []
        self.tokens: int | None = None
        super().__init__(Text(), event, "conduction")
        self.take(event)

    def take(self, event: Event) -> None:
        if isinstance(event.fields.get("tokens"), int):
            self.tokens = event.fields["tokens"]
        if str(event.fields.get("text") or "").strip():
            self.texts.append(str(event.fields["text"]))
        self.show(palette.thinking_line(event.at, event.fields.get("launch"), self.tokens,
                                        self.texts[0] if self.texts else ""))

    def has_content(self) -> bool:
        return bool(self.texts)

    def whole(self) -> Text:
        return Text("\n\n".join(self.texts))


class TranscriptView(VerticalScroll):
    """The blocks of one conversation, in the order the flow said them."""

    DEFAULT_CSS = """
    TranscriptView { height: 1fr; padding: 0 1; }
    TranscriptView > .block { height: auto; }
    TranscriptView > .line { height: 1; padding: 0 0 0 2; }
    TranscriptView Markdown { margin: 0; padding: 0 0 0 2; }
    TranscriptView MarkdownParagraph { margin: 0; }
    """

    class TurnShown(Message):
        """The turn at the top of the view changed: the bubble's line of its message."""

        def __init__(self, said: Text) -> None:
            super().__init__()
            self.said = said

    def __init__(self, steps_alone: bool = False) -> None:
        super().__init__(id="transcript")
        self.conduction_hidden = False
        self.steps_alone = steps_alone           # a run read: its steps come without a conduction before them
        self._steps: StepsLine | None = None     # the steps' line of the launch under way
        self._early: list[Event] = []            # steps said before the turn's first conduction
        self._calls: dict[str, ToolLine] = {}     # the calls of the turn, by their id
        self._thought: ThinkingLine | None = None   # the thought of the launch under way
        self._words: Event | None = None         # the launch's last words, shown once something else of it comes
        self._turns: list[tuple[Vertical, Text]] = []   # the head of each turn, in order, and its bubble's line
        self._top = -1                           # the turn at the top of the view, as last said
        self._arranged = None                    # the last arrangement computed
        self.layouts = 0                         # the arrangements computed anew

    def on_mount(self) -> None:
        self.anchor()

    # ---------- the blocks ----------
    async def add(self, event: Event) -> None:
        """One event of the flow, as the block or the line its kind makes."""
        f = event.fields
        if self._words is not None and event.kind not in KEPT:
            await self._said(self._words)
        if event.kind == "principal":
            self._steps, self._early, self._calls, self._thought = None, [], {}, None
            head = await self._block("principal", Static(palette.principal_head(event.at), markup=False),
                                     Markdown(palette.plain(str(f.get("text", "")))))
            self._turn(head, palette.bubble_line(event.at, str(f.get("text", ""))))
        elif event.kind == "conduction":
            await self._line(EventLine(palette.conduction_line(event.at, f), event, "conduction"))
            self._thought = None
            self._steps = StepsLine(self._early)
            self._early = []
            await self._line(self._steps)
        elif event.kind == "step":
            if self._steps is None and self.steps_alone:
                self._steps = StepsLine([])
                await self._line(self._steps)
            if self._steps is None:
                self._early.append(event)
            else:
                self._steps.take(event, self.conduction_hidden)
        elif event.kind == "tool":
            call = ToolLine(event)
            self._calls[str(f.get("id", ""))] = call
            await self._line(call, self._steps)
        elif event.kind == "tool-result":
            call = self._calls.get(str(f.get("id", "")))
            if call is None:
                await self._line(ResultLine(event), self._steps)
            else:
                call.took(event)
        elif event.kind == "thinking":
            if self._thought is None:
                self._thought = ThinkingLine(event)
                await self._line(self._thought, self._steps)
            else:
                self._thought.take(event)
        elif event.kind == "words":
            self._words = event
        elif event.kind == "agent":
            held, self._words = self._words, None
            if held is not None and str(held.fields.get("text") or "") != str(f.get("text") or ""):
                await self._said(held)
            await self._line(EventLine(palette.agent_line(event.at, f), event, "agent"))
        elif event.kind == "response":
            answer = f.get("response")
            await self._block("agent", Static(palette.response_head(event.at), markup=False),
                              Markdown(palette.plain(str(answer)) if answer is not None else "(no response)"))
        elif event.kind == "verdict":
            await self._block("verdict", Static(palette.verdict_line(event.at, str(f.get("state", "")), f.get("cost_usd"),
                                                                     f.get("launches"), f.get("reason")), markup=False))
        elif event.kind == "conduct":
            await self._block("house", Static(palette.conduct_line(event.at, f.get("on") is True), markup=False))
        elif event.kind == "package":
            await self._block("house", Static(palette.package_line(event.at, str(f.get("name", "")), f.get("on") is True),
                                              markup=False))
        elif event.kind == ENDED:
            await self._block("house", Static(palette.ended_line(f.get("rc"), str(f.get("stderr", ""))), markup=False))
        elif event.kind == UNREADABLE:
            await self._block("house", Static(palette.dim(f"{palette.TRACE} a line that does not read: "
                                                          f"{str(f.get('line', ''))[:80]}"), markup=False))
        elif event.kind not in SILENT:
            await self._block("house", Static(palette.house_line(event.at, event.kind, f), markup=False))

    async def add_history(self, turn: Turn) -> None:
        """A past turn of a run taken up: the message and the answer kept, dim, its head saying `history #n`."""
        head = await self._block("history", Static(palette.history_head(turn, palette.PRINCIPAL), markup=False))
        self._turn(head, palette.bubble_line(turn.at, turn.message, turn.exchange))
        await self._block("history", Static(palette.history_head(turn, palette.AGENT), markup=False),
                          Markdown(palette.plain(turn.answer) if turn.answer is not None else "(no response)"))

    async def _block(self, voice: str, *children) -> Vertical:
        block = Vertical(*children, classes=f"block {voice}")
        await self.mount(block)
        return block

    async def _line(self, line: EventLine, before: EventLine | None = None) -> None:
        """A line at the end, or before the steps' line of its launch when it says what the launch did."""
        line.display = self._shown(line)
        if before is not None and before.is_mounted:
            await self.mount(line, before=before)
        else:
            await self.mount(line)

    async def _said(self, words: Event) -> None:
        """Words of the agent during a launch, as one of its lines."""
        self._words = None
        await self._line(EventLine(palette.agent_line(words.at, words.fields), words, "agent"), self._steps)

    def _shown(self, line: EventLine) -> bool:
        """A line of conduction shows unless `c` hid them; a steps' line once its launch said a step."""
        if not line.has_class("conduction"):
            return True
        return not self.conduction_hidden and (not isinstance(line, StepsLine) or bool(line.steps))

    # ---------- the turn at the top of the view ----------
    def _turn(self, head: Vertical, said: Text) -> None:
        """A turn's head added: the turn at the top judged once the head is laid out."""
        self._turns.append((head, said))
        self.call_after_refresh(self._judge)

    def _judge(self) -> None:
        """The turn at the top of the view, said to the tab when it changed: the last turn at the end of the
        transcript, else the last whose head stands at or above the top of the view."""
        if not self._turns or not self.is_attached:
            return
        if self.is_vertical_scroll_end:
            index = len(self._turns) - 1
        else:
            index = max(0, bisect_right(self._turns, self.scroll_y, key=lambda turn: turn[0].virtual_region.y) - 1)
        if index != self._top:
            self._top = index
            self.post_message(self.TurnShown(self._turns[index][1]))

    def watch_scroll_y(self, old_value: float, new_value: float) -> None:
        super().watch_scroll_y(old_value, new_value)
        self._judge()

    def arrange(self, size, optimal: bool = False):
        """Textual's arrangement of the blocks, counted each time it is computed anew rather than taken from its
        cache."""
        arranged = super().arrange(size, optimal)
        if arranged is not self._arranged:
            self._arranged = arranged
            self.layouts += 1
        return arranged

    # ---------- the gestures ----------
    def toggle_conduction(self) -> None:
        """`c`: every line of conduction, of steps, of calls and of thought hidden, or shown again."""
        self.conduction_hidden = not self.conduction_hidden
        for line in self.query(".conduction"):
            line.display = self._shown(line)
        self.call_after_refresh(self._judge)
