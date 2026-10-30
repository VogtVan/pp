"""transcript -- the TRANSCRIPT of one conversation as a column of BLOCKS, the one scroller of
its tab, its end held in view as blocks arrive, in the order the flow said them. The principal's
message and each of the agent's `words` are a head (the voice's glyph, the hour, the launch) above
the text WHOLE, rendered as MARKDOWN -- tables, code, lists: what the model said, shown once, where it
said it, as ONE widget whose text Rich draws at its width and in the colours of the theme, drawn again when either
changes; the response of a turn -- their composition -- is never shown over them, but for a turn that
said no words (a flow kept before them). Every other event of a turn is ONE LINE, its summary read from
the flow's fields: per launch the `conduction` (the blocks it serves), what the agent did meanwhile --
each call of a tool (`⚙`, updated by its result), ONE line of its thought (`∴`) --, the line of its steps
(counted by kind) and the launch's end (`◀`: its cost). A line whose overlay has a
content to show is LIVE: it takes the focus (`tab`) and opens that content WHOLE in an overlay (`enter`
or a click) -- built when it opens, never before; a line with nothing to show is STALE: the palette's
`STALE` look, no focus, nothing opens -- judged by its event's fields alone, again at each update. The LIVE
mounts each event as it comes (`add`); a PAST -- a run's kept flow, or its exchanges as turns of history, dim --
is built in memory by the same logic, event by event, and mounted in ONE mount that replaces the transcript
(`rebuild`). The verdict is a line; what the
house says (the end of the flow, a refused command, whether the exchanges are conducted, a
package in or out of the run's play, a kind nobody knows) is a dim line. Two classes of line fold on their
own key, by `display` alone -- nothing is rewritten: `c` hides the CONDUCTION (its lines, the steps, the
thought) and shows it again, `b` the CALLS (the calls of tools and their results). The TURN AT THE TOP of the view -- the last turn at the end of the transcript, else the last whose head
stands at or above the top, found by bisection on the heads -- is said to the tab (`TurnShown`) each time it
changes, as the view scrolls or a turn arrives: the tab's bubble follows, and nothing of the transcript is laid out
again; `layouts` counts the arrangements the transcript computed, what the bench reads to say so."""
from __future__ import annotations

from bisect import bisect_right
from typing import Sequence

from rich.text import Text
from textual import events
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static

import palette
from model.dialogue import ENDED, UNREADABLE, Event, Turn
from panes.overlays import EventScreen

SILENT = ("ready", "waiting", "closed", "opened", "context")   # what the frame's status or the gauge says, no block
_LOOKS: dict[str, tuple] = {}                        # the look of a markdown text, by the theme it is drawn in


class MarkdownText(Static):
    """A markdown text as ONE widget: its source drawn by Rich (`palette.markdown_text`) at the width of its text --
    the widget's less its gutter -- and in the look of the app's theme, drawn again when the width or the theme
    changes."""

    def __init__(self, source: str, id: str | None = None) -> None:
        super().__init__("", markup=False, classes="markdown-text", id=id)
        self.source = source
        self._width = 0

    def on_mount(self) -> None:
        self.watch(self.app, "theme", self._themed, init=False)

    def show(self, source: str) -> None:
        """Another source, drawn at once when the width is known."""
        if source != self.source:
            self.source = source
            if self._width:
                self._draw()

    def on_resize(self, event: events.Resize) -> None:
        width = event.size.width - self.styles.gutter.width
        if width > 0 and width != self._width:
            self._width = width
            self._draw()

    def _themed(self, theme: str) -> None:
        if self._width:
            self._draw()

    def _draw(self) -> None:
        theme = self.app.theme
        if theme not in _LOOKS:
            _LOOKS[theme] = palette.markdown_look(self.app.get_css_variables(), self.app.current_theme.dark)
        self.update(palette.markdown_text(self.source, self._width, _LOOKS[theme]))


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
        super().__init__(palette.tool_line(event.at, event.fields, None), event, "calls")

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
        super().__init__(palette.result_line(event.at, event.fields), event, "calls")

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
    TranscriptView > .block.principal { margin: 0 0 0 4; background: $primary 12%; }
    TranscriptView > .line { height: 1; padding: 0 0 0 2; }
    TranscriptView MarkdownText { padding: 0 0 0 2; }
    """

    class TurnShown(Message):
        """The turn at the top of the view changed: the bubble's line of its message."""

        def __init__(self, said: Text) -> None:
            super().__init__()
            self.said = said

    def __init__(self, steps_alone: bool = False) -> None:
        super().__init__(id="transcript")
        self.conduction_hidden = False
        self.calls_hidden = False
        self.steps_alone = steps_alone           # a run read: its steps come without a conduction before them
        self._steps: StepsLine | None = None     # the steps' line of the launch under way
        self._early: list[Event] = []            # steps said before the turn's first conduction
        self._calls: dict[str, ToolLine] = {}     # the calls of the turn, by their id
        self._thought: ThinkingLine | None = None   # the thought of the launch under way
        self._worded = False                     # whether the turn under way said words
        self._turns: list[tuple[Vertical, Text]] = []   # the head of each turn, in order, and its bubble's line
        self._top = -1                           # the turn at the top of the view, as last said
        self._arranged = None                    # the last arrangement computed
        self.layouts = 0                         # the arrangements computed anew

    def on_mount(self) -> None:
        self.anchor()

    # ---------- the blocks ----------
    async def add(self, event: Event) -> None:
        """One event of the flow, as the block or the line its kind makes -- the LIVE: mounted as it comes."""
        for widget, before in self._build(event):
            if before is not None and before.is_mounted:
                await self.mount(widget, before=before)
            else:
                await self.mount(widget)
        if event.kind == "principal":
            self.call_after_refresh(self._judge)

    async def rebuild(self, events: Sequence[Event] = (), history: Sequence[Turn] = ()) -> None:
        """A PAST: the turns of history, then the events of a kept flow, built in memory by the same logic as the
        live, then mounted in ONE mount that takes the transcript of before out with it; the turn at the top judged
        once."""
        self._steps, self._early, self._calls, self._thought, self._worded = None, [], {}, None, False
        self._turns, self._top = [], -1
        built: list[Widget] = []
        for turn in history:
            built += self._history(turn)
        for event in events:
            for widget, before in self._build(event):
                if before is not None and before in built:
                    built.insert(built.index(before), widget)
                else:
                    built.append(widget)
        with self.app.batch_update():
            await self.remove_children()
            if built:
                await self.mount_all(built)
        self.call_after_refresh(self._judge)

    def _build(self, event: Event) -> list[tuple[Widget, EventLine | None]]:
        """-> what one event makes, each widget with the line it goes before (`None`: at the end) -- the turn's
        state moved, a line of the turn updated in place; nothing mounted."""
        f = event.fields
        if event.kind == "principal":
            self._steps, self._early, self._calls, self._thought = None, [], {}, None
            self._worded = False
            head = self._block("principal", Static(palette.principal_head(event.at), markup=False),
                               MarkdownText(str(f.get("text", ""))))
            self._turns.append((head, palette.bubble_line(event.at, str(f.get("text", "")))))
            return [(head, None)]
        if event.kind == "conduction":
            line = self._line(EventLine(palette.conduction_line(event.at, f), event, "conduction"))
            self._thought = None
            self._steps = StepsLine(self._early)
            self._early = []
            return [(line, None), (self._line(self._steps), None)]
        if event.kind == "step":
            made: list[tuple[Widget, EventLine | None]] = []
            if self._steps is None and self.steps_alone:
                self._steps = StepsLine([])
                made.append((self._line(self._steps), None))
            if self._steps is None:
                self._early.append(event)
            else:
                self._steps.take(event, self.conduction_hidden)
            return made
        if event.kind == "tool":
            call = ToolLine(event)
            self._calls[str(f.get("id", ""))] = call
            return [(self._line(call), self._steps)]
        if event.kind == "tool-result":
            call = self._calls.get(str(f.get("id", "")))
            if call is None:
                return [(self._line(ResultLine(event)), self._steps)]
            call.took(event)
            return []
        if event.kind == "thinking":
            if self._thought is None:
                self._thought = ThinkingLine(event)
                return [(self._line(self._thought), self._steps)]
            self._thought.take(event)
            return []
        if event.kind == "words":
            return self._said(event.at, f.get("launch"), str(f.get("text") or ""))
        if event.kind == "agent":
            made = []
            if not self._worded and str(f.get("text") or "").strip():   # a flow kept before the words: its text
                made = self._said(event.at, f.get("launch"), str(f["text"]))
            return made + [(self._line(EventLine(palette.agent_line(event.at, f), event, "agent")), None)]
        if event.kind == "response":
            answer = f.get("response")
            if self._worded:                     # a turn that said no words: its response, the one text it has
                return []
            return [(self._block("agent", Static(palette.response_head(event.at), markup=False),
                                 MarkdownText(str(answer) if answer is not None else "(no response)")), None)]
        if event.kind == "verdict":
            return [(self._block("verdict", Static(palette.verdict_line(event.at, str(f.get("state", "")),
                                                                        f.get("cost_usd"), f.get("launches"),
                                                                        f.get("reason")), markup=False)), None)]
        if event.kind == "conduct":
            return [(self._block("house", Static(palette.conduct_line(event.at, f.get("on") is True), markup=False)),
                     None)]
        if event.kind == "package":
            return [(self._block("house", Static(palette.package_line(event.at, str(f.get("name", "")),
                                                                      f.get("on") is True), markup=False)), None)]
        if event.kind == ENDED:
            return [(self._block("house", Static(palette.ended_line(f.get("rc"), str(f.get("stderr", ""))),
                                                 markup=False)), None)]
        if event.kind == UNREADABLE:
            return [(self._block("house", Static(palette.dim(f"{palette.TRACE} a line that does not read: "
                                                             f"{str(f.get('line', ''))[:80]}"), markup=False)), None)]
        if event.kind not in SILENT:
            return [(self._block("house", Static(palette.house_line(event.at, event.kind, f), markup=False)), None)]
        return []

    def _history(self, turn: Turn) -> list[Widget]:
        """A past turn of a run taken up: the message and the answer kept, dim, its head saying `history #n`."""
        head = self._block("history", Static(palette.history_head(turn, palette.PRINCIPAL), markup=False))
        self._turns.append((head, palette.bubble_line(turn.at, turn.message, turn.exchange)))
        return [head, self._block("history", Static(palette.history_head(turn, palette.AGENT), markup=False),
                                  MarkdownText(turn.answer if turn.answer is not None else "(no response)"))]

    @staticmethod
    def _block(voice: str, *children) -> Vertical:
        return Vertical(*children, classes=f"block {voice}")

    def _line(self, line: EventLine) -> EventLine:
        """A line, shown or folded as the toggles say."""
        line.display = self._shown(line)
        return line

    def _said(self, at: str, launch: object, text: str) -> list[tuple[Widget, EventLine | None]]:
        """Words of the agent at a launch, as a block of their own: the head, then the text whole in markdown."""
        if not text.strip():
            return []
        self._worded = True
        return [(self._block("agent", Static(palette.words_head(at, launch), markup=False),
                             MarkdownText(text)), None)]

    def _shown(self, line: EventLine) -> bool:
        """A line of conduction shows unless `c` hid them, a steps' line once its launch said a step; a line of a
        call unless `b` hid them; any other line always."""
        if line.has_class("calls"):
            return not self.calls_hidden
        if not line.has_class("conduction"):
            return True
        return not self.conduction_hidden and (not isinstance(line, StepsLine) or bool(line.steps))

    # ---------- the turn at the top of the view ----------
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
        """`c`: every line of conduction, of steps and of thought hidden, or shown again."""
        self.conduction_hidden = not self.conduction_hidden
        self._refold(".conduction")

    def toggle_calls(self) -> None:
        """`b`: every line of a call of a tool and of its result hidden, or shown again."""
        self.calls_hidden = not self.calls_hidden
        self._refold(".calls")

    def _refold(self, selector: str) -> None:
        for line in self.query(selector):
            line.display = self._shown(line)
        self.call_after_refresh(self._judge)
