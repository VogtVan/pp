"""transcript -- the TRANSCRIPT of one conversation as a column of BLOCKS, the one scroller of
its tab, in the order the flow said them; a view that FOLLOWS its end stays at its end whatever grows the
transcript or lowers the view, a view the principal raised stays on the row at its top whatever moves above it
(`rest`, where the component holds the view after each layout and each resize -- the view follows from its mount,
from a scroll that reaches the end and from a message the principal sends, which it shows; a scroll that leaves the
end stops it) -- drawn by the Line API: ONE widget, a `panes.virtual_rows.VirtualRows` over a model in memory
(s.1372): the component draws the rows in view alone, keeps each row drawn until a row moves, follows the end and
reads a selection; the view lays its items on rows (`lay`), draws a row (`row_strip`), says its text (`row_text`)
and holds a place of the rows on the content (`anchored`, `laid`); no widget is mounted per event, so a line added
costs the same on 500 events as on 4000. The principal's
message, each of the agent's `words` and each text of the model beside them -- an `aside`, written before a call,
and the `final`, the last message of a launch -- are a head (the voice's glyph, the hour, the launch; the last
message its length too) above the text WHOLE, rendered as MARKDOWN -- tables, code, lists: what the model said,
shown once, where it
said it, as ONE part whose text Rich draws at its width and in the colours of the theme
(`palette.markdown_text`), drawn again when either changes; the response of a turn -- their composition -- is never shown over them, but for a turn that
said no words (a flow kept before them). Every other event of a turn is ONE LINE, its summary read from
the flow's fields: per launch the `conduction` (the blocks it serves), what the agent did meanwhile --
each call of a tool (`⚙`, updated by its result), ONE line of its thought (`∴`) --, the line of its steps
(counted by kind) and the launch's end (`◀`: its cost). A line whose overlay has a
content to show is LIVE: the CURSOR stops on it (`tab`, `shift+tab`: from the message line the last live line,
before the first the transcript itself, past the ends the focus leaves as it left a line), in the look of a
focused line, and opens that content WHOLE in an overlay (`enter` or a click) -- built when it opens, never before;
a line with nothing to show is STALE: the palette's `STALE` look, the cursor passes it, nothing opens -- judged by
its event's fields alone, again at each update. The LIVE places each event in the model as it comes (`add`); a
PAST -- a run's kept flow, or its exchanges as turns of history, dim -- is built by the same logic, event by event,
and laid out once in place of the transcript (`rebuild`). A selection reads the rows' text, the cells before
them left out: `ctrl+a`, `ctrl+c` copy it as before. It is held on the CONTENT, never on rows: its ends are
anchored once, when it is made (`anchored`, asked by the component as it reads the selection's two ends), as the
item each falls in and a place in the item's text a new wrap keeps; what is lit and what is copied are read from
the anchors on the layout of the moment (`laid`) -- whatever moved a row since, the text chosen stays the text lit
and copied. The focus a press of the mouse gives moves neither the cursor nor the view. The verdict is a line;
what the house says (the end of the flow, a refused command, whether the exchanges are conducted, a
package in or out of the run's play, a kind nobody knows) is a dim line. Two classes of line fold on their
own key, by `display` alone -- nothing is rebuilt: `c` hides the CONDUCTION (its lines, the steps, the
thought) and shows it again, `b` the CALLS (the calls of tools and their results), `w` the MODEL's texts beside
its words (the asides and the last messages). An aside is set in, muted and italic -- a note --; a last message
keeps its text plain, a gutter of its own colour along it (`palette.MARK`); the words of a print have neither. A
last message that says nothing -- the hand-back mark, no `text`; blanks alone -- makes no block; one the flow kept
by its length alone, before its text was kept, is a stale line that says so. The TURN AT THE TOP of the view --
the last turn at the end of the transcript, else the last whose head
stands at or above the top, found by bisection on the heads -- is said to the tab (`TurnShown`) each time it
changes, as the view scrolls or a turn arrives: the tab's bubble follows, and nothing of the transcript is laid out
again; `layouts` counts the layouts the transcript computed, what the bench reads to say so."""
from __future__ import annotations

from bisect import bisect_right
from typing import Sequence

from rich.segment import Segment
from rich.text import Text
from textual import events
from textual.binding import Binding
from textual.geometry import Offset, Region, Size
from textual.message import Message
from textual.selection import Selection
from textual.strip import Strip
from textual.widgets import Static

import palette
from model.dialogue import ENDED, UNREADABLE, Event, Turn
from panes.overlays import EventScreen
from panes.virtual_rows import VirtualRows

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


class EventLine:
    """One event as one line of the transcript: its summary, and its content opened whole in `EventScreen` -- LIVE
    when it has a content to show, STALE otherwise (the `STALE` look, the cursor passes it, nothing opens). A line
    is a thing of the model, no widget: the view draws it, `version` says when its summary changed, `changed` tells
    the view so."""

    def __init__(self, summary: Text, event: Event | None = None, classes: str = "") -> None:
        self.event = event
        self.classes = f"line {classes}".strip().split()
        self.display = True
        self.version = 0
        self.changed = None                    # the view's hook, set when it places the line
        self.index = -1                        # its place in the view's items
        self.show(summary)

    def has_class(self, name: str) -> bool:
        return name in self.classes

    def has_content(self) -> bool:
        """-> whether the overlay has something to show: the text the event carries, not blank."""
        return bool(str(self.event.fields.get("text") or "").strip()) if self.event else False

    def show(self, summary: Text) -> None:
        """The line given its summary, judged again at its next draw: live as the palette made it, or stale."""
        self.summary = summary
        self.version += 1
        if self.changed is not None:
            self.changed(self)

    def drawn(self) -> Text:
        """-> what the line draws: its summary when live, its words alone when stale."""
        return self.summary if self.has_content() else palette.stale(self.summary)

    def whole(self) -> Text:
        """-> what the line stands for, whole: the text the event carries."""
        return Text(str(self.event.fields.get("text") or "") if self.event else "")

    def kind_label(self) -> str:
        """-> the label of the line's kind, read from its event's `kind` by the palette's table."""
        return palette.event_label(self.event.kind, self.event.fields) if self.event else ""


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
        self.display = not hidden
        self.show(palette.steps_line(self.steps))

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


class Words:
    """A markdown source, a part of a block: drawn whole by `palette.markdown_text` at the width of its text."""

    def __init__(self, source: str) -> None:
        self.source = source


class Block:
    """A block of the transcript: its voice (`principal`, `agent`, `aside`, `final`, `history`, `verdict`, `house`)
    and its parts in order -- a head or a line of the house (a text wrapped at the width), the words (`Words`, in
    markdown)."""

    def __init__(self, voice: str, *parts: Text | Words) -> None:
        self.voice = voice
        self.parts = list(parts)
        self.display = True
        self.version = 0
        self.index = -1


def solid(char: str) -> bool:
    """-> whether a character stays where it is when its text is wrapped anew: neither a blank nor a line of a box."""
    return not char.isspace() and not "\u2500" <= char <= "\u257f"


class Anchor:
    """An end of a selection held on the content: the item it falls in, held by its identity -- the items it was
    taken among kept, to find it again by its key once `rebuild` made the items anew -- and a place in the item's
    text that a new wrap keeps: the characters a wrap never moves (`solid`) before the one it leans on -- the next on
    its row, else the one before --, the blanks between that character and the place, and, on a row of blanks
    alone, the rows between. `under` says the place is a character the pointer stands on: the later end of a drag
    takes it whole; a place past its row's text takes none."""

    __slots__ = ("item", "items", "count", "after", "blanks", "rows", "under")

    def __init__(self, item, items: list, count: int, after: bool, blanks: int, rows: int = 0,
                 under: bool = False) -> None:
        self.item, self.items, self.count, self.after, self.blanks, self.rows = item, items, count, after, blanks, rows
        self.under = under


MARGIN = {"principal": 4, "aside": 2}        # the cells left blank before a block of that voice
GUTTER = 2                                   # the cells before a line and before the words of a block
CURSOR, STALE_LOOK, HISTORY, PRINCIPAL = ("transcript--cursor", "transcript--stale", "transcript--history",
                                          "transcript--principal")
ASIDE_LOOK, FINAL_LOOK = "transcript--aside", "transcript--final"
LOOKS = {"principal": PRINCIPAL, "history": HISTORY, "aside": ASIDE_LOOK}   # the look of a block's rows, by voice
MARKED = {"final": FINAL_LOOK}               # a voice whose words have a gutter: `palette.MARK` in that look
MODEL = ("aside", "final")                   # the voices `w` folds: the model's texts beside its words


class TranscriptView(VirtualRows, can_focus=True):
    """The blocks and lines of one conversation, in the order the flow said them, drawn by the Line API: rows of
    `VirtualRows` -- the items laid at the width, each on the rows its text takes."""

    SELECTS = True                               # a selection reads the rows' text, the cells before them left out
    COMPONENT_CLASSES = {CURSOR, STALE_LOOK, HISTORY, PRINCIPAL,   # the principal's look: the palette's, the bubble's
                         ASIDE_LOOK, FINAL_LOOK}
    DEFAULT_CSS = """
    TranscriptView { height: 1fr; padding: 0 1; overflow-x: hidden; }
    """
    BINDINGS = [Binding("tab", "step(1)", "next", show=False),
                Binding("shift+tab", "step(-1)", "previous", show=False),
                Binding("enter", "open", "open", show=False)]

    class TurnShown(Message):
        """The turn at the top of the view changed: the bubble's line of its message."""

        def __init__(self, said: Text) -> None:
            super().__init__()
            self.said = said

    def __init__(self, steps_alone: bool = False) -> None:
        super().__init__(id="transcript")
        self.conduction_hidden = False
        self.calls_hidden = False
        self.model_hidden = False
        self.steps_alone = steps_alone           # a run read: its steps come without a conduction before them
        self._steps: StepsLine | None = None     # the steps' line of the launch under way
        self._early: list[Event] = []            # steps said before the turn's first conduction
        self._calls: dict[str, ToolLine] = {}     # the calls of the turn, by their id
        self._thought: ThinkingLine | None = None   # the thought of the launch under way
        self._worded = False                     # whether the turn under way said words
        self._turns: list[tuple[Block, Text]] = []   # the head of each turn, in order, and its bubble's line
        self._top = -1                           # the turn at the top of the view, as last said
        self._items: list[Block | EventLine] = []    # the model: every block and line, in order
        self._rows: dict[int, tuple] = {}        # by id of an item: (its key, its rows) -- (Text, indent, look)
        self._tops: list[int] = []               # the first row of each item, laid at `_width`
        self._total = 0                          # the rows of the transcript, laid at `_width`
        self._dirty = 0                          # the first item whose place or height may have changed
        self._touched: list[EventLine] = []      # the lines whose summary changed since the last layout
        self._width = 0                          # the width the layout stands on
        self._held: Anchor | None = None         # a view that does not follow: the row at its top, held on the content
        self._sent: Block | None = None          # the principal's message the view shows until something follows it
        self._lit: tuple | None = None           # the selection read last, and the layout it was read on
        self.cursor: EventLine | None = None     # the line the keys act on; None: the transcript itself
        self.layouts = 0                         # the layouts computed anew

    def on_mount(self) -> None:
        self.watch(self.app, "theme", self._themed, init=False)
        self.watch(self.screen, "focused", self._focused, init=False)

    # ---------- the blocks ----------
    async def add(self, event: Event) -> None:
        """One event of the flow, as the block or the line its kind makes -- the LIVE: placed in the model as it
        comes, nothing mounted; the view draws what shows. A message the principal sends brings the view back: it
        follows the end again, and shows the message from its head until something follows it -- in a run read,
        nobody sends from here: a message leaves the view where it stands."""
        made = self._build(event)
        for item, before in made:
            self._place(item, before)
        self._sent = None
        if event.kind == "principal" and not self.steps_alone:
            self._following, self._held, self._sent = True, None, made[0][0]
        self._moved()
        if event.kind == "principal":
            self.call_after_refresh(self._judge)

    async def rebuild(self, events: Sequence[Event] = (), history: Sequence[Turn] = ()) -> None:
        """A PAST: the turns of history, then the events of a kept flow, built in the model by the same logic as the
        live -- the transcript of before taken out with it --, laid out once; the turn at the top judged once."""
        self._steps, self._early, self._calls, self._thought, self._worded = None, [], {}, None, False
        self._turns, self._top, self._items, self._rows, self._tops, self._total = [], -1, [], {}, [], 0
        self._touched, self.cursor = [], None
        for turn in history:
            for item in self._history(turn):
                self._place(item, None)
        for event in events:
            for item, before in self._build(event):
                self._place(item, before)
        self._dirty = 0
        self._moved()
        self.call_after_refresh(self._judge)

    def _place(self, item: Block | EventLine, before: EventLine | None) -> None:
        """An item put in the model: at the end, or before the line it goes before."""
        at = before.index if before is not None and 0 <= before.index < len(self._items) \
            and self._items[before.index] is before else len(self._items)
        self._items.insert(at, item)
        for index in range(at, len(self._items)):
            self._items[index].index = index
        self._dirty = min(self._dirty, at)
        if isinstance(item, EventLine):
            item.changed = self._touched.append

    def _moved(self) -> None:
        """What changed in the model laid out at once -- the view held where it stands --, drawn again at the next
        refresh."""
        self._settle()
        self.forget()
        self.refresh()

    def _build(self, event: Event) -> list[tuple[Block | EventLine, EventLine | None]]:
        """-> what one event makes, each item with the line it goes before (`None`: at the end) -- the turn's
        state moved, a line of the turn updated in place."""
        f = event.fields
        if event.kind == "principal":
            self._steps, self._early, self._calls, self._thought = None, [], {}, None
            self._worded = False
            head = Block("principal", palette.principal_head(event.at), Words(str(f.get("text", ""))))
            self._turns.append((head, palette.bubble_line(event.at, str(f.get("text", "")))))
            return [(head, None)]
        if event.kind == "conduction":
            line = self._line(EventLine(palette.conduction_line(event.at, f), event, "conduction"))
            self._thought = None
            self._steps = StepsLine(self._early)
            self._early = []
            return [(line, None), (self._line(self._steps), None)]
        if event.kind == "step":
            made: list[tuple[Block | EventLine, EventLine | None]] = []
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
        if event.kind == "aside":
            return self._voiced("aside", palette.aside_head(event.at, f.get("launch")), f.get("text"))
        if event.kind == "final":
            if isinstance(f.get("text"), str):
                return self._voiced("final", palette.final_head(event.at, f.get("launch"), f.get("chars")), f["text"])
            if isinstance(f.get("chars"), int) and f["chars"] > 0:     # a last message kept by its length alone
                return [(self._line(EventLine(palette.final_kept_line(event.at, f.get("launch"), f["chars"]), event,
                                              "model")), None)]
            return []
        if event.kind == "agent":
            made = []
            if not self._worded and str(f.get("text") or "").strip():   # a flow kept before the words: its text
                made = self._said(event.at, f.get("launch"), str(f["text"]))
            return made + [(self._line(EventLine(palette.agent_line(event.at, f), event, "agent")), None)]
        if event.kind == "response":
            answer = f.get("response")
            if self._worded:                     # a turn that said no words: its response, the one text it has
                return []
            return [(Block("agent", palette.response_head(event.at),
                           Words(str(answer) if answer is not None else "(no response)")), None)]
        if event.kind == "verdict":
            return [(Block("verdict", palette.verdict_line(event.at, str(f.get("state", "")), f.get("cost_usd"),
                                                           f.get("launches"), f.get("reason"))), None)]
        if event.kind == "conduct":
            return [(Block("house", palette.conduct_line(event.at, f.get("on") is True)), None)]
        if event.kind == "package":
            return [(Block("house", palette.package_line(event.at, str(f.get("name", "")), f.get("on") is True)),
                     None)]
        if event.kind == "space":
            return [(Block("house", palette.space_line(event.at, f.get("name"), f.get("open") is True,
                                                       f.get("pending") is True)), None)]
        if event.kind == ENDED:
            return [(Block("house", palette.ended_line(f.get("rc"), str(f.get("stderr", "")))), None)]
        if event.kind == UNREADABLE:
            return [(Block("house", palette.dim(f"{palette.TRACE} a line that does not read: "
                                                f"{str(f.get('line', ''))[:80]}")), None)]
        if event.kind not in SILENT:
            return [(Block("house", palette.house_line(event.at, event.kind, f)), None)]
        return []

    def _history(self, turn: Turn) -> list[Block]:
        """A past turn of a run taken up: the message and the answer kept, dim, its head saying `history #n`."""
        head = Block("history", palette.history_head(turn, palette.PRINCIPAL))
        self._turns.append((head, palette.bubble_line(turn.at, turn.message, turn.exchange)))
        return [head, Block("history", palette.history_head(turn, palette.AGENT),
                            Words(turn.answer if turn.answer is not None else "(no response)"))]

    def _line(self, line: EventLine) -> EventLine:
        """A line, shown or folded as the toggles say."""
        line.display = self._shown(line)
        return line

    def _said(self, at: str, launch: object, text: str) -> list[tuple[Block | EventLine, EventLine | None]]:
        """Words of the agent at a launch, as a block of their own: the head, then the text whole in markdown."""
        if not text.strip():
            return []
        self._worded = True
        return [(Block("agent", palette.words_head(at, launch), Words(text)), None)]

    def _voiced(self, voice: str, head: Text, text: object) -> list[tuple[Block | EventLine, EventLine | None]]:
        """A text of the model beside its words, as a block of its own: the head, then the text whole in markdown,
        folded while `w` hides them; none for a text of blanks alone."""
        if not str(text or "").strip():
            return []
        block = Block(voice, head, Words(str(text)))
        block.display = not self.model_hidden
        return [(block, None)]

    def _shown(self, line: EventLine) -> bool:
        """A line of conduction shows unless `c` hid them, a steps' line once its launch said a step; a line of a
        call unless `b` hid them; a line of the model's texts unless `w` hid them; any other line always."""
        if line.has_class("calls"):
            return not self.calls_hidden
        if line.has_class("model"):
            return not self.model_hidden
        if not line.has_class("conduction"):
            return True
        return not self.conduction_hidden and (not isinstance(line, StepsLine) or bool(line.steps))

    def nodes(self) -> int:
        """-> the parts of the last block of the agent: its head and its words, -1 with no such block."""
        blocks = [one for one in self._items if isinstance(one, Block) and one.voice == "agent"]
        return len(blocks[-1].parts) if blocks else -1

    # ---------- the layout: the rows of each item at the width ----------
    def _looked(self) -> tuple:
        theme = self.app.theme
        if theme not in _LOOKS:
            _LOOKS[theme] = palette.markdown_look(self.app.get_css_variables(), self.app.current_theme.dark)
        return _LOOKS[theme]

    def _rows_of(self, item: Block | EventLine) -> list[tuple[Text, int, str | None]]:
        """-> the rows an item draws at the width laid, each (its text, the cells before it, its look) -- kept
        until the width, the theme or the item changes; none for an item folded."""
        if not item.display:
            return []
        key = (self._width, self.app.theme, item.version)
        kept = self._rows.get(id(item))
        if kept is not None and kept[0] == key:
            return kept[1]
        console, width = self.app.console, self._width
        if isinstance(item, EventLine):
            text = item.drawn().copy()
            text.no_wrap, text.overflow = True, "ellipsis"
            text.truncate(max(width - GUTTER, 1), overflow="ellipsis")
            rows = [(text, GUTTER, None if item.has_content() else STALE_LOOK)]
        else:
            margin = MARGIN.get(item.voice, 0)
            look = LOOKS.get(item.voice)
            rows = []
            for part in item.parts:
                if isinstance(part, Words):
                    inner = max(width - margin - GUTTER, 1)
                    drawn, indent = palette.markdown_text(part.source, inner, self._looked()), margin + GUTTER
                else:
                    inner, drawn, indent = max(width - margin, 1), part, margin
                for line in console.render_lines(drawn, console.options.update_width(inner), pad=False):
                    row = Text()
                    for segment in line:
                        if not segment.control:
                            row.append(segment.text, segment.style)
                    rows.append((row, indent, look))
        self._rows[id(item)] = (key, rows)
        return rows

    def lay(self) -> Size | None:
        """The layout laid again from the first item that may have moved: the width changed lays it whole; a line
        whose summary changed keeps its place unless it folded or unfolded; -> the size of the rows when they were
        laid anew, None when no row moved."""
        width = self.scrollable_content_region.width
        if width <= 0:
            return None
        if width != self._width:
            self._width, self._dirty = width, 0
        for line in self._touched:
            index = line.index
            if 0 <= index < len(self._tops) and self._items[index] is line:
                laid = (self._tops[index + 1] if index + 1 < len(self._tops) else self._total) - self._tops[index]
                if laid != (1 if line.display else 0):
                    self._dirty = min(self._dirty, index)
        if self._touched:
            self._touched.clear()                # in place: the lines placed append to this list
            self.forget()
        if self._dirty >= len(self._items) and len(self._tops) == len(self._items):
            return None
        start = min(self._dirty, len(self._tops))
        del self._tops[start:]
        top = self._tops[-1] + len(self._rows_of(self._items[start - 1])) if start else 0
        for item in self._items[start:]:
            self._tops.append(top)
            top += len(self._rows_of(item))
        self._dirty, self._total = len(self._items), top
        self.forget()
        self.layouts += 1
        return Size(width, top)

    def rest(self) -> int | None:
        """-> the row the top of the view rests on once the rows are laid or its height changed: the end when it
        follows it -- no lower than the head of a message of the principal nothing follows yet --, else the row its
        top is anchored on, wherever the layout laid it; a top whose item is folded stands on the next row shown."""
        if len(self._tops) != len(self._items):
            return None
        if self._following:
            target = self.max_scroll_y
            sent = self._sent
            if sent is not None and 0 <= sent.index < len(self._items) and self._items[sent.index] is sent:
                target = min(target, self._tops[sent.index])
            return target
        place = self._where(self._held) if self._held is not None else None
        return None if place is None else min(self._tops[place[0]] + (place[1] or 0), self.max_scroll_y)

    def scrolled(self) -> None:
        """The principal scrolled the view: a message shown from its head is let go; a view that left its end
        anchors the row at its top on the content."""
        self._sent = None
        self._held = None if self._following else self.anchored(Offset(0, self.scroll_offset.y))

    def on_resize(self) -> None:
        """The view resized: laid out at its width before the component holds it where it stands."""
        self._settle()

    def _at(self, row: int) -> tuple[Block | EventLine, int] | None:
        """-> the item that draws the row `row` of the transcript and the row within it, None past the end."""
        if not self._items or len(self._tops) != len(self._items) or row < 0 or row >= self._total:
            return None
        index = bisect_right(self._tops, row) - 1
        return self._items[index], row - self._tops[index]

    def row_strip(self, row: int, lit: tuple[int, int] | None) -> Strip | None:
        """-> the strip of a row: its cells before (the margin blank, the gutter in its look), its text with the
        offsets a selection reads -- the characters `lit` in the selection's look --, the rest in its look; None
        past the transcript."""
        found = self._at(row)
        if found is None:
            return None
        item, within = found
        text, indent, look = self._rows_of(item)[within]
        style = self.get_component_rich_style(look) if look is not None else None
        if item is self.cursor and self.has_focus:
            cursor = self.get_component_rich_style(CURSOR)
            style = cursor if style is None else style + cursor
        if lit is not None:
            text = text.copy()
            text.stylize(self.selected_look(self.rich_style if style is None else self.rich_style + style), *lit)
        margin, width = MARGIN.get(item.voice, 0) if isinstance(item, Block) else 0, self.size.width
        body = Strip(list(text.render(self.app.console)))
        if style is not None:
            body = body.apply_style(style)
        body = body.apply_offsets(0, row)
        rest = width - indent - body.cell_length
        if rest > 0:                             # the blank past the text: its end, for a click or a drag
            body = Strip.join([body, Strip.blank(rest, style).apply_offsets(len(text), row)])
        body = body.crop(0, max(0, width - indent)).simplify()
        # the cells before the text, each its own segment at the text's start: one segment would count its cells;
        # the first cell of the gutter of a marked voice's words draws its mark
        marked = MARKED.get(item.voice) if isinstance(item, Block) and indent > margin else None
        before = [Strip([Segment(palette.MARK, self.get_component_rich_style(marked))]).apply_offsets(0, row)
                  if marked is not None and x == margin else
                  Strip.blank(1, None if x < margin else style).apply_offsets(0, row)
                  for x in range(min(indent, width))]
        return Strip.join([*before, body])

    def row_text(self, row: int) -> str | None:
        """-> the text of a row of the transcript as laid now, the cells before it left out; None past its end."""
        found = self._at(row)
        return self._rows_of(found[0])[found[1]][0].plain if found is not None else None

    # ---------- the anchors: a place of the rows held on the content, and laid again ----------
    def anchored(self, offset: Offset, under: bool = False) -> Anchor | None:
        """-> the anchor of a place of the layout laid now: a place above the transcript its start, below it its end,
        past its row's text the end of that text; `under`: the place is the character under the pointer, when it
        has one."""
        if not self._total or len(self._tops) != len(self._items):
            return None
        if offset.y < 0:
            offset = Offset(0, 0)
        elif offset.y >= self._total:
            item, within = self._at(self._total - 1)
            offset = Offset(len(self._rows_of(item)[within][0].plain), self._total - 1)
        item, within = self._at(offset.y)
        rows = [row[0].plain for row in self._rows_of(item)]
        row = rows[within]
        x = min(max(offset.x, 0), len(row))      # the blank drawn past a row's text is no place of the text
        under = under and x < len(row)
        count = sum(map(solid, "".join(rows[:within]))) + sum(map(solid, row[:x]))
        ahead = next((at for at in range(x, len(row)) if solid(row[at])), None)
        if ahead is not None:                    # leans on the next character of its row
            return Anchor(item, self._items, count, False, ahead - x, under=under)
        behind = next((at for at in range(x - 1, -1, -1) if solid(row[at])), None)
        if behind is not None:                   # leans on the character before it on its row
            return Anchor(item, self._items, count, True, x - behind - 1, under=under)
        lean = next((n for n in range(within - 1, -1, -1) if any(map(solid, rows[n]))), -1)
        return Anchor(item, self._items, count, True, x, within - lean if lean >= 0 else within, under)

    def laid(self) -> Selection | None:
        """-> the selection as the layout of the moment lays its anchors; None when nothing is selected, when an end's
        item is gone, when both ends' items are folded, or when its start falls after its end. A folded end is read
        on the nearest row shown INSIDE the selection: a start at the start of the next one, an end at the end of
        the one before. A drag's two places are read in their order, its end past the character under the pointer
        when the pointer stood on one."""
        if self._ends is None or self.text_selection is None:
            return None
        self._settle()
        start, end, drag = self._ends
        seen = (self.layouts, id(self._items), len(self._items), self._width, start.item.version, end.item.version)
        if self._lit is not None and self._lit[0] is self._ends and self._lit[1] == seen:
            return self._lit[2]
        laid = None
        places = [self._where(start), self._where(end)]
        if None not in places and len(self._tops) == len(self._items):
            later = end
            if drag and self._order(places[1]) < self._order(places[0]):
                places.reverse()
                later = start
            (first, within, x), (last, ending, y) = places
            if within is not None or ending is not None:
                begin = Offset(x, self._tops[first] + within) if within is not None else self._inward(first, False)
                close = Offset(y + (1 if drag and later.under else 0), self._tops[last] + ending) \
                    if ending is not None else self._inward(last, True)
                if begin is not None and close is not None and (begin.y, begin.x) <= (close.y, close.x):
                    laid = Selection(begin, close)
        self._lit = (self._ends, seen, laid)
        return laid

    @staticmethod
    def _order(place: tuple) -> tuple:
        index, within, x = place
        return index, -1 if within is None else within, 0 if x is None else x

    def _where(self, anchor: Anchor) -> tuple | None:
        """-> where an anchor stands in the layout: its item's index and the row and character within it -- the row
        None when the item is folded --; None when its item is gone."""
        index = self._found(anchor)
        if index is None:
            return None
        rows = [row[0].plain for row in self._rows_of(self._items[index])]
        if not rows:
            return index, None, None
        return (index, *self._located(anchor, rows))

    def _found(self, anchor: Anchor) -> int | None:
        """-> the index of an anchor's item among the items: the item itself; else -- `rebuild` made them anew -- the
        item of the same key and the same rank among the items of that key; None when there is none."""
        item = anchor.item
        if 0 <= item.index < len(self._items) and self._items[item.index] is item:
            return item.index
        if anchor.items is self._items or not 0 <= item.index < len(anchor.items) \
                or anchor.items[item.index] is not item:
            return None
        key = self._key(item)
        rank = sum(1 for one in anchor.items[:item.index] if self._key(one) == key)
        same = [n for n, one in enumerate(self._items) if self._key(one) == key]
        if rank >= len(same):
            return None
        anchor.item, anchor.items = self._items[same[rank]], self._items
        return same[rank]

    @staticmethod
    def _key(item: Block | EventLine) -> tuple:
        """-> what finds an item again among items made anew: its event's kind, instant, run, launch and id; for a
        block, its voice and its text; for the steps' line, its first step."""
        if isinstance(item, Block):
            return ("block", item.voice, tuple(part.source if isinstance(part, Words) else part.plain
                                               for part in item.parts))
        event = item.event if item.event is not None else (item.steps[0] if getattr(item, "steps", None) else None)
        if event is None:
            return (type(item).__name__,)
        return (type(item).__name__, event.kind, event.at, event.run, str(event.fields.get("launch")),
                str(event.fields.get("id", "")))

    @staticmethod
    def _located(anchor: Anchor, rows: list[str]) -> tuple[int, int]:
        """-> the row and the character of an anchor in its item's rows as laid now: the character it leans on
        found by its count, then the blanks between it and the place, or the rows between on a row of blanks."""
        target = anchor.count + (0 if anchor.after else 1)
        if target == 0:                          # nothing before it in the item: counted from its first row
            within = min(anchor.rows, len(rows) - 1)
            return within, min(anchor.blanks, len(rows[within]))
        seen = 0
        for within, text in enumerate(rows):
            for at, char in enumerate(text):
                if not solid(char):
                    continue
                seen += 1
                if seen < target:
                    continue
                if not anchor.after:
                    for _ in range(anchor.blanks):
                        if at > 0 and not solid(text[at - 1]):
                            at -= 1
                    return within, at
                if anchor.rows:
                    below = min(within + anchor.rows, len(rows) - 1)
                    return below, min(anchor.blanks, len(rows[below]))
                return within, min(at + 1 + anchor.blanks, len(text))
        return len(rows) - 1, len(rows[-1])

    def _inward(self, index: int, end: bool) -> Offset | None:
        """-> where a folded end is read: a start at the start of the next row shown, an end at the end of the row
        shown before; None when there is none."""
        shown = range(index - 1, -1, -1) if end else range(index + 1, len(self._items))
        near = next((n for n in shown if self._rows_of(self._items[n])), None)
        if near is None:
            return None
        if not end:
            return Offset(0, self._tops[near])
        rows = self._rows_of(self._items[near])
        return Offset(len(rows[-1][0].plain), self._tops[near] + len(rows) - 1)

    def on_focus(self) -> None:
        self._moved()                            # the cursor's line takes its look

    def on_blur(self) -> None:
        self._moved()

    def _themed(self, theme: str) -> None:
        self._dirty = 0
        self._moved()

    # ---------- the turn at the top of the view ----------
    def _judge(self) -> None:
        """The turn at the top of the view, said to the tab when it changed: the last turn at the end of the
        transcript, else the last whose head stands at or above the top of the view."""
        if not self._turns or not self.is_attached:
            return
        self._settle()
        if len(self._tops) != len(self._items):
            return
        if self.is_vertical_scroll_end:
            index = len(self._turns) - 1
        else:
            index = max(0, bisect_right(self._turns, self.scroll_y, key=lambda turn: self._tops[turn[0].index]) - 1)
        if index != self._top:
            self._top = index
            self.post_message(self.TurnShown(self._turns[index][1]))

    def watch_scroll_y(self, old_value: float, new_value: float) -> None:
        super().watch_scroll_y(old_value, new_value)
        self._judge()

    # ---------- the cursor: the lines the keys and the mouse open ----------
    def _live(self) -> list[EventLine]:
        """-> the lines the cursor stops on: shown, with a content to open."""
        return [one for one in self._items if isinstance(one, EventLine) and one.display and one.has_content()]

    def _focused(self, old, new) -> None:
        """The focus come to the transcript: on its last live line when the keys bring it back from below (`shift+tab`
        from the message line), on the transcript itself when it comes from above or when a press of the mouse gives
        it -- Textual gives the focus while the button is down (`Screen._mouse_down_offset`), before the press
        reaches the view: the rows under the pointer stay where they are."""
        if new is not self or old is self:
            return
        chain = self.screen.focus_chain
        below = old is not None and old in chain and self in chain and chain.index(old) > chain.index(self)
        pressed = getattr(self.screen, "_mouse_down_offset", None) is not None
        live = self._live() if below and not pressed else []
        self._point(live[-1] if live else None)

    def _point(self, line: EventLine | None) -> None:
        """The cursor on a line, brought into view."""
        self.cursor = line
        self.forget()
        self.refresh()
        if line is not None:
            self._settle()
            if 0 <= line.index < len(self._tops):
                self.scroll_to_region(Region(0, self._tops[line.index], max(self._width, 1), 1), animate=False,
                                      immediate=True)

    def action_step(self, by: int) -> None:
        """`tab`, `shift+tab`: the cursor to the next live line, or the previous; past the last, or before the
        first, the focus leaves the transcript as it would leave a line."""
        live = self._live()
        at = live.index(self.cursor) if self.cursor in live else (-1 if by > 0 else len(live))
        nxt = at + by
        if by < 0 and self.cursor is not None and nxt < 0:
            self._point(None)                    # before the first line: the transcript itself
        elif 0 <= nxt < len(live) and not (by < 0 and self.cursor is None):
            self._point(live[nxt])
        else:
            self._point(None)
            if by > 0:
                self.screen.focus_next()
            else:
                self.screen.focus_previous()

    def action_open(self) -> None:
        """`enter`: the line under the cursor opened whole."""
        if self.cursor is not None:
            self._open(self.cursor)

    def _open(self, line: EventLine) -> None:
        if line.has_content():
            self.app.push_screen(EventScreen(line.summary, line.whole, line.kind_label(),
                                             line.event is not None and line.event.kind in palette.MARKDOWN_KINDS))

    def on_click(self, event: events.Click) -> None:
        """A click on a live line: the cursor on it, the line opened."""
        offset = event.get_content_offset(self)
        found = self._at(offset.y + self.scroll_offset.y) if offset is not None else None
        if found is not None and isinstance(found[0], EventLine) and found[0].has_content():
            self._point(found[0])
            self._open(found[0])

    # ---------- the gestures ----------
    def toggle_conduction(self) -> None:
        """`c`: every line of conduction, of steps and of thought hidden, or shown again."""
        self.conduction_hidden = not self.conduction_hidden
        self._refold("conduction")

    def toggle_calls(self) -> None:
        """`b`: every line of a call of a tool and of its result hidden, or shown again."""
        self.calls_hidden = not self.calls_hidden
        self._refold("calls")

    def toggle_model(self) -> None:
        """`w`: every aside and every last message of the model -- their blocks, the lines of the last messages kept by
        their length alone -- hidden, or shown again."""
        self.model_hidden = not self.model_hidden
        self._refold("model")

    def _refold(self, kind: str) -> None:
        for line in self._items:
            if isinstance(line, EventLine) and line.has_class(kind):
                line.display = self._shown(line)
            elif kind == "model" and isinstance(line, Block) and line.voice in MODEL:
                line.display = not self.model_hidden
        if self.cursor is not None and not self.cursor.display:
            self.cursor = None
        self._dirty = 0
        self._moved()
        self.call_after_refresh(self._judge)
