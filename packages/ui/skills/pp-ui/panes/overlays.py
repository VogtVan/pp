"""overlays -- what the post asks or shows OVER its screen, the cockpit's way: a modal screen
centred, `width: 80%` up to 100 columns, as tall as its content up to 90 % of the screen,
a heavy border, and its own line of keys at the bottom. Overlays stack: one pushed over
another comes back to it when it closes. The post types nothing outside a conversation's
message line; whatever else it needs from the operator -- a name, the fields of a gesture -- is
asked here, with its help under it."""
from __future__ import annotations

import copy
from dataclasses import dataclass

from rich.text import Text
from textual import events
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.message import Message
from typing import Awaitable, Callable

from textual.screen import ModalScreen
from textual.suggester import SuggestFromList
from textual.widgets import DataTable, Input, Markdown, OptionList, Select, Static, TextArea
from textual.widgets.option_list import Option

import palette
import panes
from model import gestures
from model.runs import EFFORTS, PERMISSIONS, RunLine
from model.teams import CEREMONY_COLUMNS, RECURRENCE_COLUMNS, RECURRING_COLUMNS
from panes.fields import SEND_KEYS, MessageArea


class Overlay(ModalScreen):
    """The shape every overlay of the post takes; `body()` yields what it shows, `foot()` what stays in sight under it
    whatever the body scrolls to, `keys` its line of keys; `escape` (and `q`, where no line takes the letters) closes
    it with nothing -- once what is typed in it differs from what it opened on (`modified`), after a confirmation:
    `ctrl+enter` there leaves, `escape` gives the overlay back as it stood. `ctrl+enter` sends it (`action_send`) from
    any of its fields, a text included; `enter` in a line goes to the next field -- nothing on the last -- and never
    sends."""

    DEFAULT_CSS = """
    Overlay { align: center middle; }
    Overlay > #box { width: 80%; max-width: 100; height: auto; max-height: 90%; padding: 1 2; }
    Overlay #overlay-body { height: auto; }
    Overlay #overlay-foot { height: auto; }
    Overlay #overlay-keys { height: 1; margin-top: 1; }
    """
    BINDINGS = [Binding("escape", "cancel", "close"),
                Binding(",".join(SEND_KEYS), "send", palette.SEND, show=False, priority=True)]
    keys: list[tuple[str, str]] = [("esc", "close")]
    scrolls = True              # the body scrolls inside the box; an overlay whose body scrolls itself says False --
                                # its box then takes the height of the screen (`height: 90%`) and its table `1fr`,
                                # so that the line of keys stays the last row of the box
    FRAME_ROWS = 6              # the box's border and padding, the line of keys and its margin
    guards = True               # `escape` asks before it loses what was typed; the confirmation itself says False
    _opened: tuple | None = None    # what the overlay held once laid out: `entered()` at the opening

    def compose(self):
        with Vertical(id="box"):
            if self.scrolls:    # the foot and the keys stay out of the scroll, always in sight
                scroll = VerticalScroll(id="overlay-body")
                scroll.can_focus = False        # `tab` goes from field to field, the body follows the focus
                with scroll:
                    yield from self.body()
            else:
                yield from self.body()
            with Vertical(id="overlay-foot"):
                yield from self.foot()
            yield Static(palette.keys_line(self.keys), id="overlay-keys", markup=False)

    def body(self):
        return iter(())

    def foot(self):
        return iter(())

    def on_mount(self) -> None:
        self._fit()
        self.call_after_refresh(self._fit)       # the foot measured once laid out
        self.call_after_refresh(self._open_on)   # the fields filled in once laid out

    def _open_on(self) -> None:
        if self._opened is None:
            self._opened = self.entered()

    def entered(self) -> tuple[dict, object]:
        """-> what is typed in the overlay: the value of each field by its id -- a line, a list, a text, and the text
        a holder of values keeps (`holds_values`), a field `apart` left out --, then what the overlay holds of the
        operator's choices beside its fields (`held`)."""
        found: dict = {}
        for one in self.query("*"):
            if one.id is None or getattr(one, "apart", False):
                continue
            if isinstance(one, (Input, Select)):
                found[one.id] = one.value
            elif isinstance(one, TextArea) or getattr(one, "holds_values", False):
                found[one.id] = one.text
        return found, copy.deepcopy(self.held())

    def held(self) -> object:
        """-> the operator's choices the overlay holds beside its fields -- none here."""
        return None

    def modified(self) -> bool:
        """-> whether what is typed differs from what the overlay opened on: a field it opened with holding another
        value, or its choices beside the fields changed -- a field made since counts by the holder it writes to."""
        if self._opened is None:
            return False
        (fields, held), (opened, was) = self.entered(), self._opened
        return held != was or any(fields[key] != value for key, value in opened.items() if key in fields)

    def confirm_leave(self, leave: Callable[[], None]) -> None:
        """The confirmation asked before what was typed is lost: `ctrl+enter` plays `leave`, `escape` gives the
        overlay back, each field as typed."""

        def given(left: bool | None) -> None:
            if left:
                leave()
        self.app.push_screen(ConfirmScreen(palette.LEAVE_TYPED), given)

    def on_resize(self) -> None:
        self._fit()

    def _fit(self) -> None:
        """The body as tall as the box allows -- 90 % of the screen less its frame and its foot -- so that the foot and
        the keys stay in sight and the body scrolls beyond."""
        if self.scrolls and self.query("#overlay-body"):
            foot = self.query_one("#overlay-foot").outer_size.height if self.query("#overlay-foot") else 0
            self.query_one("#overlay-body").styles.max_height = max(3, int(self.size.height * 0.9) - self.FRAME_ROWS
                                                                    - foot)

    def action_cancel(self) -> None:
        if self.guards and self.modified():
            self.confirm_leave(lambda: self.dismiss(None))
            return
        self.dismiss(None)

    def action_send(self) -> None:
        """`ctrl+enter`: what the overlay gives -- nothing, for an overlay that only shows."""

    def on_input_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        self.next_field()

    def next_field(self) -> None:
        """`enter` in a line, or on a closed list: the focus on the next field -- none after the last."""
        chain = self.focus_chain
        if self.focused in chain and chain.index(self.focused) < len(chain) - 1:
            chain[chain.index(self.focused) + 1].focus()


class AskScreen(Overlay):
    """Asks ONE word of the operator -- a prompt, its help, a line: `ctrl+enter` gives the text,
    `escape` gives nothing. Under `empty`, an empty line is an answer of its own
    (`""`), told from `escape`."""

    keys = [palette.SENDS, ("esc", "cancel")]

    def __init__(self, prompt: str, help_text: str, value: str = "", empty: bool = False) -> None:
        super().__init__()
        self.prompt, self.help_text, self.value, self.empty = prompt, help_text, value, empty

    def body(self):
        yield Static(palette.strong(self.prompt), markup=False)
        yield Static(self.help_text, classes="help", markup=False)
        yield Input(self.value, id="ask")

    def on_mount(self) -> None:
        self.query_one("#ask", Input).focus()

    def action_send(self) -> None:
        value = self.query_one("#ask", Input).value.strip()
        self.dismiss(value if self.empty else value or None)


class ConfirmScreen(Overlay):
    """A gesture asked before it plays -- its title, and under `detail` what it would do, as the verb said it --:
    `ctrl+enter` gives True -- the caller plays it --, `enter` too while no line holds the focus; `escape` gives
    nothing. Under `expect`, what destroys: a line where the name of its target must be typed as it is, and
    `ctrl+enter` gives nothing until it is -- the gap said under the line. Under `checks` -- `(label, value)` each --,
    a list of CHECKS under the detail, none checked: `space` on a line checks it or unchecks it, and `recompose`,
    given the values checked, gives the detail anew, followed; the list takes the focus, `tab` goes to the line;
    `ctrl+enter` then gives the values checked, a list, in place of True. Its `escape` never asks: it is the overlay
    that asks."""

    guards = False
    BINDINGS = Overlay.BINDINGS + [Binding("enter", "send", "play", show=False),
                                   Binding("space", "toggle", "check", show=False)]
    keys = [palette.SENDS, ("esc", "cancel")]

    def __init__(self, title: str, expect: str | None = None, detail: Text | None = None,
                 checks: tuple[tuple[str, str], ...] = (), recompose: Callable[[list[str]], Text | None] | None = None,
                 help: str = "") -> None:
        super().__init__()
        self.title_text, self.expect, self.detail = title, expect, detail
        self.checks, self.recompose, self.help, self.checked = tuple(checks), recompose, help, []
        if self.checks:
            self.keys = [("space", "check"), ("tab", "the name"), palette.SENDS, ("esc", "cancel")]

    def body(self):
        yield Static(palette.strong(self.title_text), markup=False)
        if self.detail is not None:
            yield Static(self.detail, id="detail", markup=False)
        if self.checks:
            yield OptionList(*(Option(palette.check_row(label, False), id=value) for label, value in self.checks),
                             id="checks")
            if self.help:
                yield Static(self.help, classes="help", markup=False)
        if self.expect is not None:
            yield Static(palette.typed_help(self.expect), classes="help", markup=False)
            yield Input("", id="typed")
            yield Static("", id="typed-gap", markup=False)

    def on_mount(self) -> None:
        super().on_mount()
        if self.checks:
            self.query_one("#checks", OptionList).focus()
        elif self.expect is not None:
            self.query_one("#typed", Input).focus()

    def action_toggle(self) -> None:
        """`space` on the list: the line under the cursor checked or unchecked, the detail anew."""
        if not self.checks or not self.query("#checks"):
            return
        listed = self.query_one("#checks", OptionList)
        if self.focused is not listed or listed.highlighted is None:
            return
        value = listed.get_option_at_index(listed.highlighted).id
        if value in self.checked:
            self.checked.remove(value)
        else:
            self.checked.append(value)
        listed.replace_option_prompt(value, palette.check_row(next(label for label, one in self.checks if one == value),
                                                               value in self.checked))
        if self.recompose is not None:
            self.detail = self.recompose(list(self.checked))
            if self.detail is not None and self.query("#detail"):
                self.query_one("#detail", Static).update(self.detail)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        event.stop()
        self.action_send()

    def action_send(self) -> None:
        if self.expect is not None and self.query_one("#typed", Input).value.strip() != self.expect:
            self.query_one("#typed-gap", Static).update(palette.bad(f"type {self.expect} to play it -- nothing played"))
            if self.query("#typed"):
                self.query_one("#typed", Input).focus()
            return
        self.dismiss(list(self.checked) if self.checks else True)


@dataclass(frozen=True)
class Field:
    """One field of a gesture's overlay: its key, its label, its kind -- `list` (a closed list of `options`, each
    `(prompt, value)`; `blank` the prompt of its empty choice, None for a list that always holds a value), `line`
    (one line; `number` its `Input` type, `number` or `integer`), `text` (several lines) --, its help, its value
    at the opening, and the `example` a free field left empty shows in its place (`e.g. 2.5`)."""
    key: str
    label: str
    kind: str
    help: str
    options: tuple = ()
    value: object = None
    blank: str | None = None
    number: str = "text"
    example: str = ""
    under: tuple[str, str] | None = None     # `(list, value)`: shown only while the list `list` holds `value`
    fixed: bool = False                      # read only: shown, never typed


@dataclass(frozen=True)
class Part:
    """One SECTION of a file form (`panes.forms.FileForm`), shown by its title in the form's bar: its key, its title,
    its fields."""
    key: str
    title: str
    fields: tuple[Field, ...]


class GestureScreen(Overlay):
    """A gesture written in an overlay: its title, what it acts on said above its fields (`head`), its fields --
    each with its help under it --; no command is shown. `ctrl+enter` from any field -- a text included, where
    `enter` goes to the line -- gives the argv `argv_of` makes of their values, and the caller plays it;
    when `argv_of` makes none, nothing is given and `missing` is said under the fields, written at `ctrl+enter` and
    never while a value is typed -- a text, or what it gives of the values; `escape` gives nothing. `follow`,
    given the values, gives the lists whose options move with them -- the members of the team chosen. `refill`,
    given the key of a list just changed and the values, gives the fields that list sets anew -- a template's
    members and limits. Under `also`, `ctrl+s` gives `("also", argv)`: the caller plays it, then what `also` names.
    `given` keeps the values the gesture was given with. Under `play`, `ctrl+enter` plays the argv under the overlay --
    `play(argv)` gives what awaits the verb's answer: None once played, else what it said refusing --: played, the
    overlay closes and gives the argv played; refused, it stays, each field as typed, and the refusal -- `refused`,
    its code and its phrase -- is said under the fields until the next `ctrl+enter`; while the verb plays,
    `ctrl+enter` and `escape` do nothing."""

    DEFAULT_CSS = """
    GestureScreen #gesture-head { height: auto; margin-bottom: 1; }
    GestureScreen .field { height: 1; margin-top: 1; }
    GestureScreen #gesture-gap { height: auto; }
    """
    BINDINGS = Overlay.BINDINGS + [Binding("ctrl+s", "also", "also", show=False)]
    keys = [palette.SENDS, ("tab", "next field"), ("esc", "cancel")]

    def __init__(self, title: str, fields: tuple[Field, ...], argv_of: Callable[[dict], list[str] | None],
                 head: Text | None = None, missing: str | Callable[[dict], str] = "", focus: str | None = None,
                 follow: Callable[[dict], dict[str, tuple]] | None = None,
                 refill: Callable[[str, dict], dict] | None = None, also: str | None = None,
                 play: Callable[[list[str]], Awaitable[str | None]] | None = None) -> None:
        super().__init__()
        self.title_text, self.fields, self.argv_of, self.head = title, tuple(fields), argv_of, head
        self.missing, self.focus_key, self.follow, self.refill, self.also = missing, focus, follow, refill, also
        self.play = play
        self.refused: tuple[str, str] | None = None    # the code and the phrase of the last refusal, under `play`
        self._playing = False
        self._options = {one.key: tuple(one.options) for one in self.fields if one.kind == "list"}
        self._lists = {one.key: one.value for one in self.fields if one.kind == "list"}   # each list's value, as last set
        self.given: dict = {}
        if also:
            self.keys = [palette.SENDS, ("ctrl+s", also), ("tab", "next field"), ("esc", "cancel")]

    def body(self):
        yield Static(palette.strong(self.title_text), markup=False)
        if self.head is not None:
            yield Static(self.head, id="gesture-head", markup=False)
        for one in self.fields:
            yield Static(palette.field_title(one.label), classes="field", markup=False)
            if one.kind == "list":
                held = any(value == one.value for _, value in one.options)
                yield ParamSelect(list(one.options), id=f"field-{one.key}",
                                  allow_blank=one.blank is not None or not one.options,
                                  value=one.value if held else Select.NULL, prompt=one.blank or "")
            elif one.kind == "text":
                yield MessageArea(str(one.value or ""), id=f"field-{one.key}", placeholder=one.example)
            else:
                yield Input(str(one.value or ""), id=f"field-{one.key}", type=one.number, placeholder=one.example)
            yield Static(one.help, classes="help", markup=False)

    def foot(self):
        yield Static("", id="gesture-gap", markup=False)

    def on_mount(self) -> None:
        super().on_mount()
        key = self.focus_key or (self.fields[0].key if self.fields else None)
        if key is not None:
            self.query_one(f"#field-{key}").focus()
        self._show()

    def values(self) -> dict:
        """-> the value of each field: a list's choice (None for its empty one), a line or a text stripped."""
        found: dict = {}
        for one in self.fields:
            widget = self.query_one(f"#field-{one.key}")
            if isinstance(widget, Select):
                found[one.key] = None if widget.value in (Select.NULL, Select.BLANK) else widget.value
            elif isinstance(widget, TextArea):
                found[one.key] = widget.text.strip()
            else:
                found[one.key] = widget.value.strip()
        return found

    def _show(self) -> None:
        """The gap under the fields: the last refusal, when the verb refused the gesture; else nothing."""
        if self.query("#gesture-gap"):
            code, phrase = self.refused or ("", "")
            said = " -- ".join(one for one in (code, phrase) if one)
            self.query_one("#gesture-gap", Static).update(palette.bad(f"{palette.WARNING} {said}") if said else "")

    def _moved(self) -> None:
        """A value changed: the lists that follow it set again when their options moved, the gap said anew -- the last
        refusal, else nothing."""
        if self.follow is not None:
            for key, options in self.follow(self.values()).items():
                options = tuple(options)
                if self._options.get(key) != options:
                    self._options[key] = options
                    self.query_one(f"#field-{key}", Select).set_options(options)
        self._show()

    def on_input_changed(self, event: Input.Changed) -> None:
        self._moved()

    def on_select_changed(self, event: Select.Changed) -> None:
        self._moved()
        key = str(event.select.id or "").removeprefix("field-")
        value = None if event.value in (Select.NULL, Select.BLANK) else event.value
        if self.refill is None or self._lists.get(key) == value:
            return
        self._lists[key] = value
        for name, given in self.refill(key, self.values()).items():
            widget = self.query_one(f"#field-{name}")
            if isinstance(widget, Select):
                widget.value = Select.NULL if given is None else given
            elif isinstance(widget, TextArea):
                widget.load_text(str(given or ""))
            else:
                widget.value = str(given or "")

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        self._moved()

    def _made(self) -> list[str] | None:
        """-> the argv the values make, the values kept; None, and why said under the fields."""
        self.given = self.values()
        argv = self.argv_of(self.given)
        if argv is None:
            missing = self.missing(self.given) if callable(self.missing) else self.missing
            self.query_one("#gesture-gap", Static).update(palette.bad(f"nothing to play -- {missing}"))
        return argv

    def action_send(self) -> None:
        if self._playing:
            return
        argv = self._made()
        if argv is None:
            return
        if self.play is None:
            self.dismiss(argv)
            return
        self._playing, self.refused = True, None
        self._show()
        self.run_worker(self._played(argv, self.play(argv)))

    async def _played(self, argv: list[str], answer: Awaitable[str | None]) -> None:
        """The verb's answer to the gesture played under the overlay: played, the overlay closed; refused, said."""
        try:
            said = await answer
        finally:
            self._playing = False
        if said is None:
            self.dismiss(argv)
            return
        self.refused = gestures.refusal(said)
        self._show()

    def action_cancel(self) -> None:
        if not self._playing:
            super().action_cancel()

    def action_also(self) -> None:
        """`ctrl+s`, under `also`: the argv given with the word that the caller plays what `also` names after it."""
        if self.also:
            argv = self._made()
            if argv is not None:
                self.dismiss(("also", argv))


class InboxList(OptionList):
    """The list of the inbox: a click on a row highlights it -- the pane shows it -- and selects nothing; `enter` alone
    answers, through the screen."""

    async def _on_click(self, event: events.Click) -> None:
        event.prevent_default()
        clicked = event.style.meta.get("option")
        if clicked is not None and not self.get_option_at_index(clicked).disabled:
            self.highlighted = clicked


class InboxScreen(Overlay):
    """The owner's inbox of a team, as `team inbox <name> --json` says it, in a box as large as `EventScreen`'s: under
    its title the pane that says the message under the cursor whole, following it -- its head in its look, then its text
    drawn as markdown at the pane's width (`MarkdownText`, as a task's result), framed and titled like the zones of the
    post, half the box high at least whatever the terminal, a vertical bar when the message goes beyond --, then the
    questions waiting for the owner, the team's notices, the infos, the tasks done and the posts returned since the
    inbox was last seen, in the order of `palette.inbox_lines` (the latest first in each group), each on ONE row
    (`palette.inbox_row`) the list cuts by `…`. A click on a row shows it and opens nothing; `enter` on a question
    writes its reply through `reply` -- the caller pushes the reply OVER the inbox and gives, once the reply is sent,
    the inbox read again; when `team` refused the reply, its refusal, said on the line under the list until the
    cursor moves or the inbox is read again; None when nothing was sent: the inbox stays, its cursor where it was --;
    `enter` on any other row says on that line that it takes no reply; `x` marks the one message under the cursor
    read through `read` -- the caller plays it and gives True when it was played: its row leaves, the overlay stays;
    the refusal `team` said when it refused, said on the line under the list like a refused reply, the row kept; False
    when nothing was played --; `a` gives `seen`, all read; `escape` and `q` give nothing. The inbox closes on those
    three keys alone."""

    DEFAULT_CSS = """
    InboxScreen > #box { width: 95%; max-width: 160; height: 90%; }
    InboxScreen #inbox { height: 1fr; min-height: 2; text-wrap: nowrap; text-overflow: ellipsis; }
    InboxScreen #inbox-whole { height: 1fr; overflow-y: auto; margin-top: 1; margin-bottom: 1; }
    InboxScreen #inbox-head { height: auto; margin-bottom: 1; }
    InboxScreen #inbox-text { height: auto; }
    InboxScreen #inbox-gap { height: auto; }
    """
    BINDINGS = Overlay.BINDINGS + [Binding("q", "cancel", "close"), Binding("x", "read", "read", show=False),
                                   Binding("a", "seen", "all read", show=False),
                                   Binding("enter", "send", "reply", show=False, priority=True)]
    keys = [palette.SENDS, ("x", "read"), ("a", "all read"), ("esc", "close")]
    scrolls = False             # its list scrolls itself, the pane and the keys under it

    def __init__(self, team: str, found: dict | None,
                 read: Callable[[object], Awaitable[bool | str]] | None = None,
                 reply: Callable[[tuple], Awaitable[dict | None]] | None = None) -> None:
        super().__init__()
        self.team, self.lines, self.read, self.reply = team, palette.inbox_lines(found), read, reply

    def body(self):
        from panes.transcript import MarkdownText      # transcript imports this module: the widget is read when drawn
        yield Static(palette.strong(f"inbox of {self.team}"), markup=False)
        if self.lines:
            with VerticalScroll(id="inbox-whole", classes="framed"):
                yield Static("", id="inbox-head", markup=False)
                yield MarkdownText("", id="inbox-text")
            yield InboxList(*self._options(), id="inbox")
        else:
            yield Static(palette.dim(f"{palette.NONE}  nothing waits for you"), id="inbox-empty", markup=False)

    def foot(self):
        yield Static("", id="inbox-gap", markup=False)

    def _options(self) -> list[Option]:
        return [Option(palette.inbox_row(line[0]), id=str(index)) for index, line in enumerate(self.lines)]

    def on_mount(self) -> None:
        super().on_mount()
        if self.lines:
            self.query_one("#inbox-whole", VerticalScroll).border_title = palette.framed("message")
            self.query_one("#inbox", OptionList).focus()
            self._show()

    def _fit(self) -> None:
        super()._fit()
        self.call_after_refresh(self._half)     # the box laid out at the size of the screen first

    def _half(self) -> None:
        """The pane of the message half the box high, rounded up -- the list takes the rest."""
        box = self.query_one("#box").region.height if self.query("#box") else 0
        if box and self.query("#inbox-whole"):
            self.query_one("#inbox-whole", VerticalScroll).styles.height = -(-box // 2)

    def _chosen(self) -> int | None:
        """-> the index in `lines` of the message under the cursor, None without one."""
        if not self.lines:
            return None
        listed = self.query_one("#inbox", OptionList)
        if listed.highlighted is None:
            return None
        return int(listed.get_option_at_index(listed.highlighted).id or 0)

    def _show(self) -> None:
        if not self.query("#inbox-text"):
            return
        index = self._chosen()
        head, source = (Text(""), "") if index is None else self.lines[index][3:]
        self.query_one("#inbox-head", Static).update(palette.plain_text(head))
        text = self.query_one("#inbox-text")
        text.show(source)
        text.display = bool(source)              # a task done says its head alone
        self.query_one("#inbox-whole", VerticalScroll).scroll_home(animate=False)

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        event.stop()
        self._clear_gap()
        self._show()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        event.stop()             # selecting a row opens nothing: `enter` is the screen's, a click highlights

    def _clear_gap(self) -> None:
        """Empties the line under the list: what it said was about the row and the inbox of that moment, so it goes
        when the cursor moves or the inbox is read again."""
        if self.query("#inbox-gap"):
            self.query_one("#inbox-gap", Static).update("")

    def action_send(self) -> None:
        index = self._chosen()
        if index is None:
            return
        question = self.lines[index][1]
        if question is None:
            self.query_one("#inbox-gap", Static).update(
                palette.bad("this line takes no reply: enter answers a question, or a notice that waits for you"))
            return
        if self.reply is not None:
            self.run_worker(self._reply(question), group="inbox-reply", exclusive=True)

    async def _reply(self, question: tuple) -> None:
        found = await self.reply(question)
        if not self.is_attached:
            return
        if isinstance(found, str):
            self.query_one("#inbox-gap", Static).update(palette.bad(found))
        elif found is not None:
            self.refill(found)

    def refill(self, found: dict | None) -> None:
        """The inbox read again: its rows said anew, the cursor on the same row as far as the list reaches."""
        if not self.query("#inbox"):
            return
        listed = self.query_one("#inbox", OptionList)
        at = listed.highlighted
        self._clear_gap()
        self.lines = palette.inbox_lines(found)
        listed.clear_options()
        listed.add_options(self._options())
        if self.lines:
            listed.highlighted = min(at or 0, len(self.lines) - 1)
        self._show()

    def action_read(self) -> None:
        index = self._chosen()
        if index is not None and self.read is not None:
            self.run_worker(self._read(index), group="inbox-read", exclusive=True)

    async def _read(self, index: int) -> None:
        done = await self.read(self.lines[index][2])
        if not self.is_attached:
            return
        if isinstance(done, str):
            self.query_one("#inbox-gap", Static).update(palette.bad(done))
        elif done:
            self.query_one("#inbox", OptionList).remove_option(str(index))
            self._show()

    def action_seen(self) -> None:
        self.dismiss("seen")


class PackagesScreen(Overlay):
    """The packages of a run, an editor of its own: one line per package with its state for the run
    -- the state a switch waiting will give, said `… pending` --; a line chosen -- a click, `enter` -- or `space` on it
    toggles it in the overlay alone, nothing sent, the overlay kept; `ctrl+enter` alone gives the lines changed,
    `{name: on}`; `escape` gives nothing -- asked first once a line is toggled (`held`). A package `required` -- held by what launches the run -- is greyed, marked
    `required`, and never toggles; `staged` opens the overlay on lines already changed."""

    BINDINGS = Overlay.BINDINGS + [Binding("q", "cancel", "close"), Binding("space", "toggle", "toggle", show=False)]
    keys = [("space", "toggle"), palette.SENDS, ("esc", "cancel")]

    def __init__(self, title: str, states: dict[str, bool], pending: dict[str, bool],
                 required: frozenset[str] = frozenset(), staged: dict[str, bool] | None = None) -> None:
        super().__init__()
        self.title_text, self.pending, self.required = title, dict(pending), frozenset(required)
        self.base = {name: self.pending.get(name, on) for name, on in states.items()}
        self.staged = {**self.base, **{name: on for name, on in (staged or {}).items()
                                       if name in self.base and name not in self.required}}

    def _row(self, name: str) -> str:
        return palette.package_row(name, self.base[name], self.staged[name], name in self.pending,
                                   name in self.required)

    def body(self):
        yield Static(palette.strong(self.title_text), markup=False)
        yield OptionList(*(Option(self._row(name), id=name, disabled=name in self.required) for name in self.base),
                         id="packages")
        yield Static(palette.packages_help(bool(self.required)), classes="help", id="packages-help", markup=False)

    def on_mount(self) -> None:
        self.query_one("#packages", OptionList).focus()

    def held(self) -> dict[str, bool]:
        """-> the state of each line as toggled: the choices the overlay holds."""
        return dict(self.staged)

    def action_toggle(self) -> None:
        listed = self.query_one("#packages", OptionList)
        if listed.highlighted is None:
            return
        name = listed.get_option_at_index(listed.highlighted).id
        if name in self.staged and name not in self.required:
            self.staged[name] = not self.staged[name]
            listed.replace_option_prompt(name, self._row(name))

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """A line chosen -- a click, `enter` --: toggled, as `space` does."""
        event.stop()
        event.option_list.highlighted = event.option_index
        self.action_toggle()

    def action_send(self) -> None:
        self.dismiss({name: on for name, on in self.staged.items() if on != self.base[name]})


class ThemeScreen(Overlay):
    """The themes of Textual, light ones first, then the dark, the `ansi-*` last, the current one
    marked: the theme under the cursor applies once the cursor has rested `PREVIEW_REST` seconds -- a
    preview; a move meanwhile starts the wait again, so a key held runs through the list without
    applying each theme --, `ctrl+enter` (or `enter`) applies it at once and gives its name, `escape` gives nothing and the
    theme of before comes back."""

    PREVIEW_REST = 0.4                # seconds the cursor rests before the theme under it applies:
                                      # one change costs 63-65 ms (2026-10-13), a key held repeats ~30 times a second
    BINDINGS = Overlay.BINDINGS + [Binding("q", "cancel", "close")]
    keys = [palette.SENDS, ("esc", "restores")]

    def __init__(self, current: str) -> None:
        super().__init__()
        self.current = current
        self._preview = None              # the timer of the preview waiting for the cursor to rest

    def names(self) -> list[str]:
        """-> the themes the app knows, in the order of the list."""
        found = self.app.available_themes
        plain = [name for name in found if not name.startswith("ansi-")]
        return ([name for name in plain if not found[name].dark] + [name for name in plain if found[name].dark]
                + sorted(name for name in found if name.startswith("ansi-")))

    def body(self):
        yield Static(palette.strong("theme"), markup=False)
        yield OptionList(*(Option(f"{name}  ●" if name == self.current else name, id=name) for name in self.names()),
                         id="themes")

    def on_mount(self) -> None:
        listed = self.query_one("#themes", OptionList)
        names = self.names()
        if self.current in names:
            listed.highlighted = names.index(self.current)
        listed.focus()

    def action_send(self) -> None:
        self.query_one("#themes", OptionList).action_select()

    def _rested(self) -> None:
        """Stops the preview waiting, if any."""
        if self._preview is not None:
            self._preview.stop()
            self._preview = None

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        event.stop()
        self._rested()
        name = event.option.id
        if name and name != self.app.theme:

            def preview() -> None:
                self._preview = None
                self.app.theme = name
            self._preview = self.set_timer(self.PREVIEW_REST, preview)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        event.stop()
        self._rested()
        if event.option.id:
            self.app.theme = event.option.id
        self.dismiss(event.option.id)

    def action_cancel(self) -> None:
        self._rested()
        self.app.theme = self.current
        self.dismiss(None)


class StatsScreen(Overlay):
    """The statistics of a run: the sums `agent stats` gives and the detail of the conduction
    as the engine says it."""

    BINDINGS = Overlay.BINDINGS + [Binding("q", "cancel", "close")]

    def __init__(self, line: RunLine, data: dict) -> None:
        super().__init__()
        self.line, self.data = line, data

    def body(self):
        yield Static(palette.stats_text(self.line, self.data), id="stats", markup=False)


class EventScreen(Overlay):
    """An event of a conversation WHOLE: its title on ONE line -- the label of its kind, then its
    summary, cut at the width --, its content under it, without `U+FE0F` (`palette.plain_text`: drawn
    on the columns the terminal draws, copied as shown) -- folded to the width, never wider,
    scrolled when taller, selectable (`ctrl+c` copies the selection, as everywhere in the post). What
    the agent wrote -- its answer at a launch, its words -- and a team's declaration render as markdown
    (`markdown`); any other content as the text it is. The content is built when the overlay opens: a line of the transcript
    carries no more than its summary until then."""

    DEFAULT_CSS = """
    EventScreen > #box { width: 95%; max-width: 160; height: 90%; }
    EventScreen #event-title { height: 1; text-wrap: nowrap; text-overflow: ellipsis; margin-bottom: 1; }
    EventScreen #event-body { height: 1fr; }
    """
    BINDINGS = Overlay.BINDINGS + [Binding("q", "cancel", "close")]
    keys = [("esc", "close")]
    scrolls = False             # its body scrolls itself, under the title

    def __init__(self, summary: Text, whole: Callable[[], Text], label: str = "", markdown: bool = False) -> None:
        super().__init__()
        self.summary, self.whole, self.label, self.markdown = summary, whole, label, markdown

    def body(self):
        title = palette.event_title(self.label, self.summary) if self.label else self.summary
        yield Static(title, id="event-title", markup=False)
        with VerticalScroll(id="event-body"):
            if self.markdown:
                yield Markdown(palette.plain(self.whole().plain), id="event-text")
            else:
                yield Static(palette.plain_text(self.whole()), id="event-text", markup=False)

    def on_mount(self) -> None:
        self.query_one("#event-body").focus()

    def select_all(self) -> None:
        """`ctrl+a`: the event's whole text selected, as the mouse would."""
        self.query_one("#event-text").text_select_all()


class CeremoniesScreen(Overlay):
    """The ceremonies of a team: their table -- the progress of each last ring, the next ring as `team` computed
    it --, under it the detail of the line under the cursor, then the principal a ring is played as. `g` rings the ceremony under the cursor at hand -- the caller plays it, the overlay
    closes --; `ctrl+enter` -- or `enter` on the table -- gives the task of its last ring, a ceremony never rung said
    under the table."""

    DEFAULT_CSS = """
    CeremoniesScreen #ceremonies { height: auto; max-height: 12; }
    CeremoniesScreen #ceremony-detail { height: auto; margin-top: 1; }
    CeremoniesScreen #ceremony-as-row { height: auto; margin-top: 1; }
    CeremoniesScreen #ceremony-as-row .label { width: auto; padding: 0 1 0 0; }
    CeremoniesScreen #ceremony-as { width: 1fr; }
    """
    BINDINGS = Overlay.BINDINGS + [Binding("q", "cancel", "close"), Binding("g", "ring", "ring", show=False)]
    keys = [("g", "ring now"), palette.SENDS, ("tab", "as"), ("esc", "close")]

    def __init__(self, team: str, state, senders: tuple[str, ...], ring: Callable[[str, str | None], None]) -> None:
        super().__init__()
        self.team, self.state, self.senders, self.ring = team, state, tuple(senders), ring

    def body(self):
        yield Static(palette.strong(f"ceremonies of {self.team}"), markup=False)
        table = panes.table(id="ceremonies", zebra_stripes=True)
        table.add_columns(*CEREMONY_COLUMNS)
        for index, one in enumerate(self.state.ceremonies):
            table.add_row(*palette.ceremony_cells(one), key=str(index))
        yield table
        yield Static("", id="ceremony-detail", markup=False)
        with Horizontal(id="ceremony-as-row"):
            yield Static("as", classes="label", markup=False)
            yield ParamSelect([(one, one) for one in self.senders], id="ceremony-as", allow_blank=not self.senders,
                              value=self.senders[0] if self.senders else Select.NULL, compact=True)

    def on_mount(self) -> None:
        super().on_mount()
        self.query_one("#ceremonies", DataTable).focus()
        self._show()

    def _chosen(self):
        row = self.query_one("#ceremonies", DataTable).cursor_row
        ceremonies = self.state.ceremonies
        return ceremonies[row] if 0 <= row < len(ceremonies) else None

    def _sender(self) -> str | None:
        value = self.query_one("#ceremony-as", Select).value
        return value if isinstance(value, str) else None

    def _show(self, gap: Text | str = "") -> None:
        ceremony = self._chosen()
        detail = palette.ceremony_detail(ceremony, self.state.ceremonies) if ceremony else Text("")
        if gap:
            detail.append_text(palette.bad(gap) if isinstance(gap, str) else gap)
        self.query_one("#ceremony-detail", Static).update(detail)

    def on_data_table_row_highlighted(self, event) -> None:
        self._show()

    def on_select_changed(self, event: Select.Changed) -> None:
        self._show()

    def on_data_table_row_selected(self, event) -> None:
        event.stop()
        self.action_send()

    def action_send(self) -> None:
        ceremony = self._chosen()
        task = (ceremony.last or {}).get("task") if ceremony is not None else None
        if not task:
            self._show(f"{ceremony.name} was never rung: no task to show" if ceremony else "no ceremony")
            return
        self.dismiss(task)

    def action_ring(self) -> None:
        ceremony = self._chosen()
        if ceremony is None:
            return
        self.ring(ceremony.name, self._sender())
        self.dismiss(None)


class RecurrencesScreen(Overlay):
    """The RECURRENCES the caller gives -- `RecurringRow`s, as `team status <name> --json` says them --: those of ONE
    team when `team` names it (`palette.recurrence_cells`), those of every team under `team` None, each line its team
    (`palette.recurring_row_cells`, the columns of the Tasks list under `recurring`); `none` without one, the cursor on
    the line of `chosen` -- `(team, id)` -- when it is there, else on the first; the box EventScreen's, the table filling
    it. Every gesture names the team of the line under the cursor, the ids `R<n>` being a team's own, and goes to
    `gesture` -- `x` `("stop", <team>, <id>)`, said `palette.DELETES`; `m` `("change", <team>, <id>)`; `space`
    `("toggle", <team>, <id>)`, paused, or resumed when the face says it paused; `l` `("launch", <team>, <id>)`, one
    occurrence opened now, without a confirmation -- it erases nothing --; `p` `("plan", <team>)`, the line's team,
    None without a line --: the caller pushes the gesture OVER the overlay and gives, once it is played, the lines read
    again (`refill`), None when nothing was played -- the overlay back on top either way. It closes on `escape` and `q`
    alone: no gesture and no `enter` closes it."""

    DEFAULT_CSS = """
    RecurrencesScreen > #box { width: 95%; max-width: 160; height: 90%; }
    RecurrencesScreen #recurrences { height: 1fr; }
    """
    BINDINGS = Overlay.BINDINGS + [Binding("q", "cancel", "close"), Binding("x", "stop", "stop", show=False),
                                   Binding("m", "change", "change", show=False), Binding("p", "plan", "plan", show=False),
                                   Binding("space", "toggle", "pause", show=False),
                                   Binding("l", "launch", "launch now", show=False)]
    keys = [("x", palette.DELETES), ("m", "changes it"), ("space", "pauses or resumes it"), ("l", "launches it now"),
            ("p", "makes a task come back"), ("esc", "close")]
    scrolls = False             # its table scrolls itself, the line of keys the last row of the box

    def __init__(self, team: str | None, lines: list, chosen: tuple[str, str] | None = None,
                 gesture: Callable[[tuple], Awaitable[list | None]] | None = None) -> None:
        super().__init__()
        self.team, self.lines, self.chosen, self.gesture = team, list(lines), chosen, gesture

    def body(self):
        yield Static(palette.strong(f"recurrences of {self.team if self.team is not None else 'every team'}"),
                     markup=False)
        yield Static(palette.dim(f"{palette.NONE}  no recurrence: `n` and its field every lay one"),
                     id="recurrences-none", markup=False)
        table = panes.table(id="recurrences", zebra_stripes=True)
        table.add_columns(*(RECURRENCE_COLUMNS if self.team is not None else RECURRING_COLUMNS))
        yield table

    def _rows(self, table: DataTable) -> None:
        """The lines in the table -- the table shown with one line at least, `none` said without."""
        table.clear()
        for index, one in enumerate(self.lines):
            cells = palette.recurrence_cells(one.line, one.off) if self.team is not None else palette.recurring_row_cells(one)
            table.add_row(*cells, key=str(index))
        table.display = bool(self.lines)
        self.query_one("#recurrences-none", Static).display = not self.lines

    def on_mount(self) -> None:
        super().on_mount()
        table = self.query_one("#recurrences", DataTable)
        self._rows(table)
        if self.lines:
            keys = [(one.team, one.line.id) for one in self.lines]
            if self.chosen in keys:
                table.move_cursor(row=keys.index(self.chosen))
            table.focus()

    def refill(self, lines: list) -> None:
        """The lines read again: said anew, the cursor on the same row as far as the list reaches."""
        table = self.query_one("#recurrences", DataTable)
        row = table.cursor_row
        self.lines = list(lines)
        self._rows(table)
        if self.lines:
            table.move_cursor(row=max(0, min(row, len(self.lines) - 1)))
            table.focus()

    def _chosen(self):
        """-> the line under the cursor, a `RecurringRow`; None without one."""
        if not self.lines:
            return None
        row = self.query_one("#recurrences", DataTable).cursor_row
        return self.lines[row] if 0 <= row < len(self.lines) else None

    def _give(self, asked: tuple) -> None:
        """A gesture asked: pushed over the overlay by the caller, the lines read again once it is played."""
        if self.gesture is not None:
            self.run_worker(self._gestured(asked), group="recurrence-gesture", exclusive=True)

    async def _gestured(self, asked: tuple) -> None:
        lines = await self.gesture(asked)
        if lines is not None and self.is_attached:
            self.refill(lines)

    def _line(self, what: str) -> None:
        chosen = self._chosen()
        if chosen is not None:
            self._give((what, chosen.team, chosen.line.id))

    def action_stop(self) -> None:
        self._line("stop")

    def action_change(self) -> None:
        self._line("change")

    def action_toggle(self) -> None:
        self._line("toggle")

    def action_launch(self) -> None:
        self._line("launch")

    def action_plan(self) -> None:
        """`p`: a task of the line's team given once, to make come back -- the caller writes the gesture."""
        chosen = self._chosen()
        self._give(("plan", chosen.team if chosen is not None else None))


class ParamSelect(Select, inherit_bindings=False):
    """A list of the post's overlays: `space`, `down` or `up` unrolls it; closed, `enter` goes to the next field
    as a line does; unrolled, its options take `enter` and choose."""

    BINDINGS = [Binding("space,down,up", "show_overlay", "list", show=False),
                Binding("enter", "next_field", "next field", show=False)]

    def action_next_field(self) -> None:
        self.screen.next_field()


class ListOptions(OptionList):
    """The list of a `ListInput`, floating over the overlay as a `Select`'s does: `escape` folds it, the
    line left as it was."""

    BINDINGS = [Binding("escape", "fold", "fold", show=False)]

    def action_fold(self) -> None:
        self.parent.fold()


class ListArrow(Static):
    """The arrow at the right of a `ListInput` -- `▼` folded, `▲` unrolled: a click unrolls or folds its list."""

    class Clicked(Message):
        """The arrow was clicked."""

    def on_click(self, event) -> None:
        event.stop()
        self.post_message(self.Clicked())


class ListInput(Vertical):
    """A line that lists, as a `Select` does: free text -- a compact `Input`, the names it knows suggested
    as they are typed -- and the arrow of a list at its right, in one bordered row; under it the list of
    those names, on the overlay layer: unrolled, it floats over the fields below and moves none. `down` or
    a click on the arrow unrolls it: a line empty or holding an exact name lists EVERY name, the cursor on
    that name; the start of a name lists those it begins (any case); a line no name begins with lists them
    all. In the list `enter` fills the line and folds it, `escape` folds it and leaves the line as it was.
    `enter` in the line goes to the next field, as in any line; a folded list takes no `tab`."""

    DEFAULT_CSS = """
    ListInput { height: auto; }
    ListInput > .list-line { height: auto; width: 1fr; padding: 0 1 0 2; }
    ListInput > .list-line > Input { width: 1fr; height: 1; padding: 0; }
    ListInput .arrow { box-sizing: content-box; width: 1; height: 1; padding: 0 0 0 1; }
    ListInput .up-arrow { display: none; }
    ListInput.-expanded .down-arrow { display: none; }
    ListInput.-expanded .up-arrow { display: block; }
    ListInput > ListOptions { width: 1fr; height: auto; max-height: 12; display: none;
                              overlay: screen; constrain: none inside; }
    ListInput.-expanded > ListOptions { display: block; }
    """
    BINDINGS = [Binding("down", "unroll", "list", show=False)]

    def __init__(self, value: str, *, id: str, items: list[str], placeholder: str = "") -> None:
        super().__init__(id=f"{id}-field")
        self.value, self.line_id, self.items, self.placeholder = value, id, list(items), placeholder

    def compose(self):
        with Horizontal(classes="list-line"):
            yield Input(self.value, id=self.line_id, suggester=SuggestFromList(self.items),
                        placeholder=self.placeholder, compact=True)
            yield ListArrow("▼", classes="arrow down-arrow")
            yield ListArrow("▲", classes="arrow up-arrow")
        yield ListOptions(id=f"{self.line_id}-options")

    def offer(self, items: list[str]) -> None:
        """The names the line knows: suggested as they are typed, listed by `down`."""
        self.items = list(items)
        self.query_one(Input).suggester = SuggestFromList(self.items)

    def listed(self) -> tuple[list[str], int]:
        """-> the names the list shows for what the line holds, and the one the cursor stands on."""
        typed = self.query_one(Input).value.strip().casefold()
        names = [one.casefold() for one in self.items]
        if not typed or typed in names:
            return self.items, names.index(typed) if typed in names else 0
        return [one for one in self.items if one.casefold().startswith(typed)] or self.items, 0

    def action_unroll(self) -> None:
        shown, at = self.listed()
        if not shown:
            return
        options = self.query_one(ListOptions)
        options.clear_options()
        options.add_options(shown)
        self.add_class("-expanded")
        options.highlighted = at
        options.focus(scroll_visible=False)

    def fold(self, refocus: bool = True) -> None:
        if refocus:
            self.query_one(Input).focus()
        self.remove_class("-expanded")

    def on_list_arrow_clicked(self, event: ListArrow.Clicked) -> None:
        event.stop()
        if self.has_class("-expanded"):
            self.fold()
        else:
            self.action_unroll()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        event.stop()
        line = self.query_one(Input)
        line.value = str(event.option.prompt)
        line.cursor_position = len(line.value)
        self.fold()

    def on_descendant_blur(self, event) -> None:
        if isinstance(event.widget, ListOptions) and self.has_class("-expanded"):
            self.fold(refocus=False)        # the focus gone elsewhere: the list folds behind it


class PackagesLine(Static):
    """The line `packages` of a profile: the state of each package for the run; `enter` or a click asks its
    overlay."""

    DEFAULT_CSS = """
    PackagesLine { height: auto; padding: 0 1; }
    """
    BINDINGS = [Binding("enter", "open", "packages", show=False)]
    can_focus = True

    class Opened(Message):
        """The line asks the overlay of the packages."""

    def action_open(self) -> None:
        self.post_message(self.Opened())

    def on_click(self, event) -> None:
        event.stop()
        self.post_message(self.Opened())


class ProfileScreen(Overlay):
    """The PROFILE of a launch, the ONE form of the post wherever it launches something: the provider (the
    providers the house is wired with), the model (a `ListInput`: free, the names the adapter declares suggested
    and listed), the budget, the effort (a `ListInput` of its five words), the permission regime -- each with its
    help under it, prefilled with `defaults` -- then the line `packages`: the state of each package beyond the base
    (`packages`, with the switches still `pending`), `enter` on it opening them in their overlay, where the
    packages the caller holds (`required`) do not toggle; the lines changed come back to the line, and nothing is
    sent before the profile is confirmed. A caller says what it shows: `budget` False leaves the budget out,
    `packages` None the line. What each provider spells and names comes from `offer` -- `agent providers --json`,
    read once as the screen opens, the suggestions and the helps following it. `ctrl+enter` from any field gives
    the profile filled in, `packages` the lines changed -- of a run
    under way (`running`), the provider fixed and greyed, the ones CHANGED alone --; `space` unrolls a list, `down`
    the names of a line; `escape` gives nothing. Under `inherit` -- a member's line of a season --, a field left
    empty says « as all » and the value of `all` it takes; `staged` opens the line of the packages on switches
    already made."""

    def __init__(self, title: str, providers: list[str], offer: Callable[[], Awaitable[dict[str, dict]]],
                 defaults: dict, running: bool = False, budget: bool = True,
                 packages: dict[str, bool] | None = None, pending: dict[str, bool] | None = None,
                 required: frozenset[str] = frozenset(), inherit: dict | None = None,
                 staged: dict[str, bool] | None = None, readonly: bool = False) -> None:
        super().__init__()
        self.title_text, self.providers, self.offer = title, list(providers), offer
        self.offered: dict[str, dict] = {}
        self.defaults, self.running, self.budget = dict(defaults), running, budget
        self.packages = None if packages is None else dict(packages)
        self.pending, self.required = dict(pending or {}), frozenset(required)
        self.inherit = None if inherit is None else dict(inherit)
        self.staged: dict[str, bool] = dict(staged or {})   # the lines changed in the overlay of the packages
        self.readonly = readonly                             # shown, never edited: its fields closed, ctrl+enter closes it
        self.keys = ([("escape", "closes")] if readonly
                     else [palette.SENDS, ("space", "lists"), ("escape", "cancels")])

    def _offer(self, provider: str | None) -> dict:
        return self.offered.get(provider or "", {}) if provider else {}

    def body(self):
        yield from self.profile()

    def on_mount(self) -> None:
        if self.readonly:
            for one in self.query(Input):
                one.disabled = True
            for one in self.query(Select):
                one.disabled = True
            self.query_one("#model", Input).focus()
            return
        self.query_one("#model", Input).focus()
        self.run_worker(self._offered())

    def profile(self):
        """The fields of the profile, the line of the packages last."""
        provider = self.defaults.get("provider")
        offer = self._offer(provider)
        models, spells = list(offer.get("models") or []), list(offer.get("spells") or [])
        yield Static(palette.strong(self.title_text), markup=False)
        yield Static(palette.field_title("provider"), classes="field", markup=False)
        yield ParamSelect([(one, one) for one in self.providers], id="provider",
                          allow_blank=len(self.providers) != 1 or self.inherit is not None,
                          value=provider if provider in self.providers else Select.NULL, disabled=self.running,
                          prompt=self._as_all("provider", "the house's own choice"))
        yield Static(palette.params_help("provider", self.providers, self.running), classes="help", markup=False)
        yield Static(palette.field_title("model"), classes="field", markup=False)
        yield ListInput(str(self.defaults.get("model") or ""), id="model", items=models,
                        placeholder=self._as_all("model", palette.model_example(models)))
        yield Static(palette.params_help("model", models), classes="help", markup=False, id="model-help")
        if self.budget:
            yield Static(palette.field_title("budget"), classes="field", markup=False)
            budget = self.defaults.get("max_budget_usd")
            yield Input(f"{float(budget):g}" if isinstance(budget, (int, float)) else "", id="budget", type="number",
                        placeholder=palette.BUDGET_EXAMPLE)
            yield Static(palette.params_help("budget", spells), classes="help", markup=False, id="budget-help")
        yield Static(palette.field_title("effort"), classes="field", markup=False)
        yield ListInput(str(self.defaults.get("effort") or ""), id="effort", items=list(EFFORTS),
                        placeholder=self._as_all("effort", palette.EFFORT_EXAMPLE))
        yield Static(palette.params_help("effort", spells), classes="help", markup=False, id="effort-help")
        yield Static(palette.field_title("permissions"), classes="field", markup=False)
        regime = self.defaults.get("permissions")
        yield ParamSelect([(one, one) for one in PERMISSIONS], id="permissions", allow_blank=True,
                     value=regime if regime in PERMISSIONS else Select.NULL,
                     prompt=self._as_all("permissions", "auto -- the harness's own judgment"))
        yield Static(palette.permissions_help(regime, spells), classes="help", markup=False, id="permissions-help")
        if self.packages is not None:
            yield Static(palette.field_title("packages"), classes="field", markup=False)
            yield PackagesLine(self._packages_text(), id="packages-line", markup=False)
            yield Static(palette.PACKAGES_LINE_HELP, classes="help", markup=False)

    def _as_all(self, key: str, otherwise: str) -> str:
        """-> what an empty field says: under `inherit`, as all and the value it takes; else `otherwise`."""
        if self.inherit is None:
            return otherwise
        return palette.as_all(self.inherit.get(key))

    def held(self) -> dict[str, bool]:
        """-> the switches of packages changed in their overlay: a choice the profile holds beside its fields."""
        return dict(self.staged)

    def _base(self) -> dict[str, bool]:
        """-> the state of each package for the run, a switch waiting counted as played."""
        return {name: self.pending.get(name, on) for name, on in (self.packages or {}).items()}

    def _packages_text(self) -> str:
        return palette.packages_line(self._base(), self.staged, self.required)

    def on_packages_line_opened(self, event: PackagesLine.Opened) -> None:
        event.stop()
        if self.readonly:
            return

        def given(changed: dict[str, bool] | None) -> None:
            if changed is None:
                return
            self.staged = dict(changed)
            self.query_one("#packages-line", PackagesLine).update(self._packages_text())
            self.focus_next()
        self.app.push_screen(PackagesScreen("packages of the run", self.packages or {}, self.pending,
                                            self.required, self.staged), given)

    async def _offered(self) -> None:
        self.offered = await self.offer()
        self._follow()

    def on_select_changed(self, event: Select.Changed) -> None:
        self._follow()

    def _follow(self) -> None:
        """The suggestions and the helps follow the provider chosen and what its adapter declares --
        nothing once the screen is leaving: its fields go before a late answer of the face."""
        if not self.query("#provider") or not self.query("#model"):
            return
        provider = self.query_one("#provider", Select).value
        offer = self._offer(provider if isinstance(provider, str) else None)
        models, spells = list(offer.get("models") or []), list(offer.get("spells") or [])
        self.query_one("#model-field", ListInput).offer(models)
        if self.inherit is None:
            self.query_one("#model", Input).placeholder = palette.model_example(models)
        self.query_one("#model-help", Static).update(palette.params_help("model", models))
        if self.budget:
            self.query_one("#budget-help", Static).update(palette.params_help("budget", spells))
        self.query_one("#effort-help", Static).update(palette.params_help("effort", spells))
        regime = self.query_one("#permissions", Select).value
        self.query_one("#permissions-help", Static).update(
            palette.permissions_help(regime if isinstance(regime, str) else None, spells))

    def parameters(self) -> dict | None:
        """-> the profile filled in -- `packages` the lines changed --, or None when the effort is no word pp knows
        (said in its help)."""
        provider = self.query_one("#provider", Select).value
        found = {"provider": provider if isinstance(provider, str) else "",
                 "model": self.query_one("#model", Input).value.strip(),
                 "max_budget_usd": self.query_one("#budget", Input).value.strip() if self.budget else "",
                 "effort": self.query_one("#effort", Input).value.strip()}
        regime = self.query_one("#permissions", Select).value
        found["permissions"] = regime if isinstance(regime, str) else ""
        if found["effort"] and found["effort"] not in EFFORTS:
            self.query_one("#effort-help", Static).update(palette.bad(f"effort: one of {', '.join(EFFORTS)}"))
            return None
        if found["max_budget_usd"]:
            found["max_budget_usd"] = float(found["max_budget_usd"])
        if self.staged:
            found["packages"] = dict(self.staged)
        return {key: value for key, value in found.items() if value not in ("", None)}

    def action_send(self) -> None:
        if self.readonly:
            self.dismiss(None)
            return
        found = self.parameters()
        if found is None:
            return
        if self.running:              # a run under way: what changed, the provider aside
            found = {key: value for key, value in found.items()
                     if key != "provider" and value != self.defaults.get(key)}
        self.dismiss(found)


class RunParamsScreen(ProfileScreen):
    """The parameters of a run: its profile (`ProfileScreen`), then its NAME under it, with its help -- prefilled
    from `defaults` like the rest, given with them as `name`."""

    def body(self):
        yield from self.profile()
        yield Static(palette.field_title("name"), classes="field", markup=False)
        yield Input(str(self.defaults.get("name") or ""), id="name", placeholder=palette.NAME_EXAMPLE)
        yield Static(palette.params_help("name", []), classes="help", markup=False)

    def parameters(self) -> dict | None:
        found = super().parameters()
        if found is not None and self.query_one("#name", Input).value.strip():
            found["name"] = self.query_one("#name", Input).value.strip()
        return found
