"""overlays -- what the post asks or shows OVER its screen, the cockpit's way: a modal screen
centred, `width: 80%` up to 100 columns, as tall as its content up to 90 % of the screen,
a heavy border, and its own line of keys at the bottom. Overlays stack: one pushed over
another comes back to it when it closes. The post types nothing outside a conversation's
message line; whatever else it needs from the operator -- a name, the fields of a gesture -- is
asked here, with its help under it."""
from __future__ import annotations

from dataclasses import dataclass

from rich.text import Text
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.message import Message
from typing import Awaitable, Callable

from textual.screen import ModalScreen
from textual.suggester import SuggestFromList
from textual.widgets import DataTable, Input, Markdown, OptionList, Select, Static, TextArea
from textual.widgets.option_list import Option

import palette
from model import gestures
from model.runs import EFFORTS, PERMISSIONS, RunLine
from model.teams import CEREMONY_COLUMNS, PROFILE_KEYS, SEASON_COLUMNS, SeasonLine
from panes.fields import MessageArea


class Overlay(ModalScreen):
    """The shape every overlay of the post takes; `body()` yields what it shows, `keys` its
    line of keys; `escape` (and `q`, where no line takes the letters) closes it with nothing."""

    DEFAULT_CSS = """
    Overlay { align: center middle; }
    Overlay > #box { width: 80%; max-width: 100; height: auto; max-height: 90%; padding: 1 2; }
    Overlay #overlay-body { height: auto; }
    Overlay #overlay-keys { height: 1; margin-top: 1; }
    """
    BINDINGS = [Binding("escape", "cancel", "close")]
    keys: list[tuple[str, str]] = [("esc", "close")]
    scrolls = True              # the body scrolls inside the box; an overlay whose body scrolls itself says False
    FRAME_ROWS = 6              # the box's border and padding, the line of keys and its margin

    def compose(self):
        with Vertical(id="box"):
            if self.scrolls:    # the keys stay out of the scroll, always in sight
                scroll = VerticalScroll(id="overlay-body")
                scroll.can_focus = False        # `tab` goes from field to field, the body follows the focus
                with scroll:
                    yield from self.body()
            else:
                yield from self.body()
            yield Static(palette.keys_line(self.keys), id="overlay-keys", markup=False)

    def body(self):
        return iter(())

    def on_mount(self) -> None:
        self._fit()

    def on_resize(self) -> None:
        self._fit()

    def _fit(self) -> None:
        """The body as tall as the box allows -- 90 % of the screen less its frame -- so that the keys stay
        in sight and the body scrolls beyond."""
        if self.scrolls and self.query("#overlay-body"):
            self.query_one("#overlay-body").styles.max_height = max(3, int(self.size.height * 0.9) - self.FRAME_ROWS)

    def action_cancel(self) -> None:
        self.dismiss(None)


class AskScreen(Overlay):
    """Asks ONE word of the operator -- a prompt, its help, a line: `enter` gives the text,
    `escape` gives nothing. With `preview`, the exact command the word makes shows under the
    line and follows it as it is typed. Under `empty`, an empty line is an answer of its own
    (`""`), told from `escape`."""

    keys = [("enter", "confirm"), ("esc", "cancel")]

    def __init__(self, prompt: str, help_text: str, value: str = "",
                 preview: Callable[[str], str] | None = None, empty: bool = False) -> None:
        super().__init__()
        self.prompt, self.help_text, self.value, self.preview, self.empty = prompt, help_text, value, preview, empty

    def body(self):
        yield Static(palette.strong(self.prompt), markup=False)
        yield Static(self.help_text, classes="help", markup=False)
        yield Input(self.value, id="ask")
        if self.preview is not None:
            yield Static(self.preview(self.value), id="preview", markup=False)

    def on_mount(self) -> None:
        self.query_one("#ask", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        if self.preview is not None:
            self.query_one("#preview", Static).update(self.preview(event.value.strip()))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        self.dismiss(event.value.strip() if self.empty else event.value.strip() or None)


class ConfirmScreen(Overlay):
    """A gesture's command shown WHOLE before it plays -- under `detail`, what it would do, as the verb said it --:
    `enter` gives True -- the caller plays it --, `escape` gives nothing. Under `expect`, what destroys: a line where the name of its target must be typed as it is,
    and `enter` gives nothing until it is -- the gap said under the line."""

    BINDINGS = Overlay.BINDINGS + [Binding("enter", "confirm", "play", show=False)]
    keys = [("enter", "plays"), ("esc", "cancel")]

    def __init__(self, title: str, command: str, expect: str | None = None, detail: Text | None = None) -> None:
        super().__init__()
        self.title_text, self.command, self.expect, self.detail = title, command, expect, detail

    def body(self):
        yield Static(palette.strong(self.title_text), markup=False)
        if self.detail is not None:
            yield Static(self.detail, id="detail", markup=False)
        yield Static(self.command, id="command", markup=False)
        if self.expect is not None:
            yield Static(palette.typed_help(self.expect), classes="help", markup=False)
            yield Input("", id="typed")
            yield Static("", id="typed-gap", markup=False)

    def on_mount(self) -> None:
        if self.expect is not None:
            self.query_one("#typed", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        self.action_confirm()

    def action_confirm(self) -> None:
        if self.expect is not None and self.query_one("#typed", Input).value.strip() != self.expect:
            self.query_one("#typed-gap", Static).update(palette.bad(f"type {self.expect} to play it -- nothing played"))
            return
        self.dismiss(True)


@dataclass(frozen=True)
class Field:
    """One field of a gesture's overlay: its key, its label, its kind -- `list` (a closed list of `options`, each
    `(prompt, value)`; `blank` the prompt of its empty choice, None for a list that always holds a value), `line`
    (one line; `number` its `Input` type, `number` or `integer`), `text` (several lines) --, its help, and its value
    at the opening."""
    key: str
    label: str
    kind: str
    help: str
    options: tuple = ()
    value: object = None
    blank: str | None = None
    number: str = "text"


class GestureScreen(Overlay):
    """A gesture written in an overlay: its title, what it acts on said above its fields (`head`), its fields --
    each with its help under it --, then the command `argv_of` makes of their values, followed as they change:
    what is shown is what plays. `enter` from any field -- a closed list included; in a text, `shift+enter` goes
    to the line -- gives that argv, and the caller plays it; when `argv_of` makes none, nothing is given and
    `missing` is said under the command -- a text, or what it gives of the values; `escape` gives nothing. `follow`,
    given the values, gives the lists whose options move with them -- the members of the team chosen. `refill`,
    given the key of a list just changed and the values, gives the fields that list sets anew -- a template's
    members and limits. Under `also`, `ctrl+s` gives `("also", argv)`: the caller plays it, then what `also` names.
    `given` keeps the values the gesture was given with."""

    DEFAULT_CSS = """
    GestureScreen #gesture-head { height: auto; margin-bottom: 1; }
    GestureScreen .field { height: 1; margin-top: 1; }
    GestureScreen #gesture-command { height: auto; margin-top: 1; }
    GestureScreen #gesture-gap { height: auto; }
    """
    BINDINGS = Overlay.BINDINGS + [Binding("enter", "submit", "play", show=False),
                                   Binding("ctrl+s", "also", "also", show=False)]
    keys = [("enter", "plays"), ("tab", "next field"), ("esc", "cancel")]

    def __init__(self, title: str, fields: tuple[Field, ...], argv_of: Callable[[dict], list[str] | None],
                 head: Text | None = None, missing: str | Callable[[dict], str] = "", focus: str | None = None,
                 follow: Callable[[dict], dict[str, tuple]] | None = None,
                 refill: Callable[[str, dict], dict] | None = None, also: str | None = None) -> None:
        super().__init__()
        self.title_text, self.fields, self.argv_of, self.head = title, tuple(fields), argv_of, head
        self.missing, self.focus_key, self.follow, self.refill, self.also = missing, focus, follow, refill, also
        self._options = {one.key: tuple(one.options) for one in self.fields if one.kind == "list"}
        self._lists = {one.key: one.value for one in self.fields if one.kind == "list"}   # each list's value, as last set
        self.given: dict = {}
        if also:
            self.keys = [("enter", "plays"), ("ctrl+s", also), ("tab", "next field"), ("esc", "cancel")]

    def body(self):
        yield Static(palette.strong(self.title_text), markup=False)
        if self.head is not None:
            yield Static(self.head, id="gesture-head", markup=False)
        for one in self.fields:
            yield Static(one.label, classes="field", markup=False)
            if one.kind == "list":
                held = any(value == one.value for _, value in one.options)
                yield ParamSelect(list(one.options), id=f"field-{one.key}",
                                  allow_blank=one.blank is not None or not one.options,
                                  value=one.value if held else Select.NULL, prompt=one.blank or "")
            elif one.kind == "text":
                yield MessageArea(str(one.value or ""), id=f"field-{one.key}")
            else:
                yield Input(str(one.value or ""), id=f"field-{one.key}", type=one.number)
            yield Static(one.help, classes="help", markup=False)
        yield Static("", id="gesture-command", markup=False)
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
        if not self.query("#gesture-command"):
            return
        argv = self.argv_of(self.values())
        self.query_one("#gesture-command", Static).update(palette.preview_line(gestures.preview(argv) if argv else ""))
        self.query_one("#gesture-gap", Static).update("")

    def _moved(self) -> None:
        """A value changed: the lists that follow it set again when their options moved, then the command."""
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

    def on_input_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        self.action_submit()

    def on_message_area_submitted(self, event: MessageArea.Submitted) -> None:
        event.stop()
        self.action_submit()

    def _made(self) -> list[str] | None:
        """-> the argv the values make, the values kept; None, and why said under the command."""
        self.given = self.values()
        argv = self.argv_of(self.given)
        if argv is None:
            missing = self.missing(self.given) if callable(self.missing) else self.missing
            self.query_one("#gesture-gap", Static).update(palette.bad(f"nothing to play -- {missing}"))
        return argv

    def action_submit(self) -> None:
        argv = self._made()
        if argv is not None:
            self.dismiss(argv)

    def action_also(self) -> None:
        """`ctrl+s`, under `also`: the argv given with the word that the caller plays what `also` names after it."""
        if self.also:
            argv = self._made()
            if argv is not None:
                self.dismiss(("also", argv))


class InboxScreen(Overlay):
    """The owner's inbox of a team, as `team inbox <name> --json` says it: the questions waiting for the owner, the
    tasks done and the posts returned since the inbox was last seen, one line each, then the command of `x`.
    `enter` on a question gives `(task, id)` -- the caller writes the reply on its task --; `x` gives `seen`, the
    command shown under the lines; `escape` gives nothing."""

    DEFAULT_CSS = """
    InboxScreen #inbox { height: auto; max-height: 16; }
    InboxScreen #inbox-command { height: auto; margin-top: 1; }
    InboxScreen #inbox-gap { height: auto; }
    """
    BINDINGS = Overlay.BINDINGS + [Binding("q", "cancel", "close"), Binding("x", "seen", "seen", show=False)]
    keys = [("enter", "reply"), ("x", "seen"), ("esc", "close")]

    def __init__(self, team: str, found: dict | None, seen: str) -> None:
        super().__init__()
        self.team, self.lines, self.seen = team, palette.inbox_lines(found), seen

    def body(self):
        yield Static(palette.strong(f"inbox of {self.team}"), markup=False)
        if self.lines:
            yield OptionList(*(Option(text, id=str(index)) for index, (text, _) in enumerate(self.lines)), id="inbox")
        else:
            yield Static(palette.dim(f"{palette.NONE}  nothing waits for you"), id="inbox-empty", markup=False)
        yield Static(Text.assemble(("x marks it seen  ", ""), palette.preview_line(self.seen)), id="inbox-command",
                     markup=False)
        yield Static("", id="inbox-gap", markup=False)

    def on_mount(self) -> None:
        super().on_mount()
        if self.lines:
            self.query_one("#inbox", OptionList).focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        event.stop()
        _, question = self.lines[int(event.option.id or 0)]
        if question is None:
            self.query_one("#inbox-gap", Static).update(palette.bad("enter replies to a question -- this line is none"))
            return
        self.dismiss(question)

    def action_seen(self) -> None:
        self.dismiss("seen")


class PackagesScreen(Overlay):
    """The packages of a run, an editor of its own: one line per package with its state for the run
    -- the state a switch waiting will give, said `… pending` --; `space` toggles the line under the
    cursor in the overlay alone, nothing sent; `enter` gives the lines changed, `{name: on}`;
    `escape` gives nothing. A package `required` -- held by what launches the run -- is greyed, marked
    `required`, and never toggles; `staged` opens the overlay on lines already changed."""

    BINDINGS = Overlay.BINDINGS + [Binding("q", "cancel", "close"), Binding("space", "toggle", "toggle", show=False)]
    keys = [("space", "toggle"), ("enter", "apply"), ("esc", "cancel")]

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

    def action_toggle(self) -> None:
        listed = self.query_one("#packages", OptionList)
        if listed.highlighted is None:
            return
        name = listed.get_option_at_index(listed.highlighted).id
        if name in self.staged and name not in self.required:
            self.staged[name] = not self.staged[name]
            listed.replace_option_prompt(name, self._row(name))

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        event.stop()
        self.dismiss({name: on for name, on in self.staged.items() if on != self.base[name]})


class ThemeScreen(Overlay):
    """The themes of Textual, light ones first, then the dark, the `ansi-*` last, the current one
    marked: the theme under the cursor applies at once -- a preview --, `enter` gives its name,
    `escape` gives nothing and the theme of before comes back."""

    BINDINGS = Overlay.BINDINGS + [Binding("q", "cancel", "close")]
    keys = [("enter", "keeps"), ("esc", "restores")]

    def __init__(self, current: str) -> None:
        super().__init__()
        self.current = current

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

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        event.stop()
        if event.option.id:
            self.app.theme = event.option.id                 # the preview

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        event.stop()
        self.dismiss(event.option.id)

    def action_cancel(self) -> None:
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
    the agent wrote -- its answer at a launch, its words (`markdown`) -- renders as markdown; any other
    content as the text it is. The content is built when the overlay opens: a line of the transcript
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
    it --, under it the detail of the line under the cursor, then the principal a ring is played as and the exact
    command of the ring. `g` rings the ceremony under the cursor at hand -- the caller plays it, the overlay
    closes --; `enter` gives the task of its last ring, a ceremony never rung said under the table."""

    DEFAULT_CSS = """
    CeremoniesScreen #ceremonies { height: auto; max-height: 12; }
    CeremoniesScreen #ceremony-detail { height: auto; margin-top: 1; }
    CeremoniesScreen #ceremony-as-row { height: auto; margin-top: 1; }
    CeremoniesScreen #ceremony-as-row .label { width: auto; padding: 0 1 0 0; }
    CeremoniesScreen #ceremony-as { width: 1fr; }
    """
    BINDINGS = Overlay.BINDINGS + [Binding("q", "cancel", "close"), Binding("g", "ring", "ring", show=False)]
    keys = [("g", "ring now"), ("enter", "its last task"), ("tab", "as"), ("esc", "close")]

    def __init__(self, team: str, state, senders: tuple[str, ...], ring: Callable[[str, str | None], None],
                 preview: Callable[[str, str | None], str]) -> None:
        super().__init__()
        self.team, self.state, self.senders, self.ring, self.preview = team, state, tuple(senders), ring, preview

    def body(self):
        yield Static(palette.strong(f"ceremonies of {self.team}"), markup=False)
        table = DataTable(id="ceremonies", cursor_type="row", zebra_stripes=True)
        table.add_columns(*CEREMONY_COLUMNS)
        for index, one in enumerate(self.state.ceremonies):
            table.add_row(*palette.ceremony_cells(one), key=str(index))
        yield table
        yield Static("", id="ceremony-detail", markup=False)
        with Horizontal(id="ceremony-as-row"):
            yield Static("as", classes="label", markup=False)
            yield ParamSelect([(one, one) for one in self.senders], id="ceremony-as", allow_blank=not self.senders,
                              value=self.senders[0] if self.senders else Select.NULL, compact=True)
        yield Static("", id="ceremony-command", markup=False)

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
        detail = palette.ceremony_detail(ceremony, self.state.ceremonies, self.state.tasks) if ceremony else Text("")
        if gap:
            detail.append_text(palette.bad(gap) if isinstance(gap, str) else gap)
        self.query_one("#ceremony-detail", Static).update(detail)
        self.query_one("#ceremony-command", Static).update(
            palette.preview_line(self.preview(ceremony.name, self._sender()) if ceremony else ""))

    def on_data_table_row_highlighted(self, event) -> None:
        self._show()

    def on_select_changed(self, event: Select.Changed) -> None:
        self._show()

    def on_data_table_row_selected(self, event) -> None:
        event.stop()
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


class ParamSelect(Select, inherit_bindings=False):
    """A list of the post's overlays: `space`, `down` or `up` unrolls it, `enter` is left to the
    overlay that holds it -- closed, the list validates its screen as a line does; unrolled, its
    options take `enter` and choose."""

    BINDINGS = [Binding("space,down,up", "show_overlay", "list", show=False)]


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
    `enter` in the line is the screen's; a folded list takes no `tab`."""

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
    read once as the screen opens, the suggestions and the helps following it. `enter` in any field but the line
    of the packages, a closed list included, gives the profile filled in, `packages` the lines changed -- of a run
    under way (`running`), the provider fixed and greyed, the ones CHANGED alone --; `space` unrolls a list, `down`
    the names of a line; `escape` gives nothing. Under `inherit` -- a member's line of a season --, a field left
    empty says « as all » and the value of `all` it takes; `staged` opens the line of the packages on switches
    already made."""

    BINDINGS = Overlay.BINDINGS + [Binding("enter", "submit", "validate", show=False)]

    def __init__(self, title: str, providers: list[str], offer: Callable[[], Awaitable[dict[str, dict]]],
                 defaults: dict, running: bool = False, budget: bool = True,
                 packages: dict[str, bool] | None = None, pending: dict[str, bool] | None = None,
                 required: frozenset[str] = frozenset(), inherit: dict | None = None,
                 staged: dict[str, bool] | None = None) -> None:
        super().__init__()
        self.title_text, self.providers, self.offer = title, list(providers), offer
        self.offered: dict[str, dict] = {}
        self.defaults, self.running, self.budget = dict(defaults), running, budget
        self.packages = None if packages is None else dict(packages)
        self.pending, self.required = dict(pending or {}), frozenset(required)
        self.inherit = None if inherit is None else dict(inherit)
        self.staged: dict[str, bool] = dict(staged or {})   # the lines changed in the overlay of the packages
        self.keys = [("enter", "sets" if running else "opens"), ("space", "lists"), ("escape", "cancels")]

    def _offer(self, provider: str | None) -> dict:
        return self.offered.get(provider or "", {}) if provider else {}

    def body(self):
        yield from self.profile()

    def profile(self):
        """The fields of the profile, the line of the packages last."""
        provider = self.defaults.get("provider")
        offer = self._offer(provider)
        models, spells = list(offer.get("models") or []), list(offer.get("spells") or [])
        yield Static(palette.strong(self.title_text), markup=False)
        yield Static("provider", classes="field", markup=False)
        yield ParamSelect([(one, one) for one in self.providers], id="provider",
                          allow_blank=len(self.providers) != 1 or self.inherit is not None,
                          value=provider if provider in self.providers else Select.NULL, disabled=self.running,
                          prompt=self._as_all("provider", "the house's own choice"))
        yield Static(palette.params_help("provider", self.providers, self.running), classes="help", markup=False)
        yield Static("model", classes="field", markup=False)
        yield ListInput(str(self.defaults.get("model") or ""), id="model", items=models,
                        placeholder=self._as_all("model", "the provider's default"))
        yield Static(palette.params_help("model", models), classes="help", markup=False, id="model-help")
        if self.budget:
            yield Static("budget", classes="field", markup=False)
            budget = self.defaults.get("max_budget_usd")
            yield Input(f"{float(budget):g}" if isinstance(budget, (int, float)) else "", id="budget", type="number",
                        placeholder="no bound")
            yield Static(palette.params_help("budget", spells), classes="help", markup=False, id="budget-help")
        yield Static("effort", classes="field", markup=False)
        yield ListInput(str(self.defaults.get("effort") or ""), id="effort", items=list(EFFORTS),
                        placeholder=self._as_all("effort", "the model's default"))
        yield Static(palette.params_help("effort", spells), classes="help", markup=False, id="effort-help")
        yield Static("permissions", classes="field", markup=False)
        regime = self.defaults.get("permissions")
        yield ParamSelect([(one, one) for one in PERMISSIONS], id="permissions", allow_blank=True,
                     value=regime if regime in PERMISSIONS else Select.NULL,
                     prompt=self._as_all("permissions", "auto -- the harness's own judgment"))
        yield Static(palette.permissions_help(regime, spells), classes="help", markup=False, id="permissions-help")
        if self.packages is not None:
            yield Static("packages", classes="field", markup=False)
            yield PackagesLine(self._packages_text(), id="packages-line", markup=False)
            yield Static(palette.PACKAGES_LINE_HELP, classes="help", markup=False)

    def _as_all(self, key: str, otherwise: str) -> str:
        """-> what an empty field says: under `inherit`, as all and the value it takes; else `otherwise`."""
        if self.inherit is None:
            return otherwise
        return palette.as_all(self.inherit.get(key))

    def _base(self) -> dict[str, bool]:
        """-> the state of each package for the run, a switch waiting counted as played."""
        return {name: self.pending.get(name, on) for name, on in (self.packages or {}).items()}

    def _packages_text(self) -> str:
        return palette.packages_line(self._base(), self.staged, self.required)

    def on_packages_line_opened(self, event: PackagesLine.Opened) -> None:
        event.stop()

        def given(changed: dict[str, bool] | None) -> None:
            if changed is None:
                return
            self.staged = dict(changed)
            self.query_one("#packages-line", PackagesLine).update(self._packages_text())
            self.focus_next()
        self.app.push_screen(PackagesScreen("packages of the run", self.packages or {}, self.pending,
                                            self.required, self.staged), given)

    def on_mount(self) -> None:
        self.query_one("#model", Input).focus()
        self.run_worker(self._offered())

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

    def on_input_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        self.action_submit()

    def action_submit(self) -> None:
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
        yield Static("name", classes="field", markup=False)
        yield Input(str(self.defaults.get("name") or ""), id="name", placeholder="no name")
        yield Static(palette.params_help("name", []), classes="help", markup=False)

    def parameters(self) -> dict | None:
        found = super().parameters()
        if found is not None and self.query_one("#name", Input).value.strip():
            found["name"] = self.query_one("#name", Input).value.strip()
        return found


class SeasonScreen(Overlay):
    """The SEASON of a team, what `S` opens: what the next start writes said on top (`head`), the budget and the
    wake-ups of the season, the table of its lines -- `all`, then one per member of the declaration, each saying what
    it carries (a member: what it changes of `all`, `·` the rest) and its switches of packages --, the first task
    (its name, its message), then the command `argv_of` makes of the lines and the fields, followed as they change:
    what is shown is what plays. `enter` on a line opens its `ProfileScreen` -- no budget; a member's field left
    empty is `all`'s; the packages `required` greyed -- and the line takes what it gives. `ctrl+s` -- or `enter` in a
    field -- gives the argv; when `argv_of` makes none, `missing` is said under the command; `escape` gives nothing.
    The overlay composes no field of a launch itself: each line is edited in its profile."""

    DEFAULT_CSS = """
    SeasonScreen > #box { width: 95%; max-width: 140; }
    SeasonScreen #season-head { height: auto; margin-bottom: 1; }
    SeasonScreen .field { height: 1; margin-top: 1; }
    SeasonScreen #season-lines { height: auto; max-height: 14; }
    SeasonScreen #season-command { height: auto; margin-top: 1; }
    SeasonScreen #season-gap { height: auto; }
    """
    BINDINGS = Overlay.BINDINGS + [Binding("ctrl+s", "start", "start", show=False)]
    keys = [("enter", "edits a line"), ("ctrl+s", "starts"), ("tab", "next field"), ("esc", "cancel")]

    def __init__(self, title: str, head: Text, lines: list[SeasonLine], fields: dict,
                 argv_of: Callable[[list[SeasonLine], dict], list[str] | None], providers: list[str],
                 offer: Callable[[], Awaitable[dict[str, dict]]], required: frozenset[str] = frozenset(),
                 helps: dict | None = None, missing: str = "") -> None:
        super().__init__()
        self.title_text, self.head, self.lines, self.argv_of = title, head, list(lines), argv_of
        self.fields, self.providers, self.offer, self.required = dict(fields), list(providers), offer, frozenset(required)
        self.helps, self.missing = dict(helps or {}), missing

    def body(self):
        yield Static(palette.strong(self.title_text), markup=False)
        yield Static(self.head, id="season-head", markup=False)
        yield Static("budget", classes="field", markup=False)
        yield Input(str(self.fields.get("budget") or ""), id="season-budget", type="number", placeholder="TEAM.md's")
        yield Static(self.helps.get("budget", ""), classes="help", markup=False)
        yield Static("wakes", classes="field", markup=False)
        yield Input(str(self.fields.get("wakes") or ""), id="season-wakes", type="integer", placeholder="TEAM.md's")
        yield Static(self.helps.get("wakes", ""), classes="help", markup=False)
        yield Static("lines", classes="field", markup=False)
        table = DataTable(id="season-lines", cursor_type="row", zebra_stripes=True)
        table.add_columns(*SEASON_COLUMNS)
        yield table
        yield Static(palette.SEASON_LINES_HELP, classes="help", markup=False)
        yield Static("name", classes="field", markup=False)
        yield Input("", id="season-name", placeholder="no name")
        yield Static(palette.NAME_HELP, classes="help", markup=False)
        yield Static("message", classes="field", markup=False)
        yield MessageArea("", id="season-message")
        yield Static(self.helps.get("message", ""), classes="help", markup=False)
        yield Static("", id="season-command", markup=False)
        yield Static("", id="season-gap", markup=False)

    def on_mount(self) -> None:
        super().on_mount()
        self._fill()
        self.query_one("#season-message").focus()
        self._show()

    def _fill(self) -> None:
        table = self.query_one("#season-lines", DataTable)
        row = table.cursor_row
        table.clear()
        for index, line in enumerate(self.lines):
            table.add_row(*palette.season_cells(line, self.lines[0]), key=str(index))
        if self.lines:
            table.move_cursor(row=max(0, min(row, len(self.lines) - 1)))

    def values(self) -> dict:
        """-> the fields of the season: the budget, the wake-ups, the first task's name and message, stripped."""
        return {"budget": self.query_one("#season-budget", Input).value.strip(),
                "wakes": self.query_one("#season-wakes", Input).value.strip(),
                "name": self.query_one("#season-name", Input).value.strip(),
                "message": self.query_one("#season-message", TextArea).text.strip()}

    def _show(self) -> None:
        if not self.query("#season-command"):
            return
        argv = self.argv_of(self.lines, self.values())
        self.query_one("#season-command", Static).update(palette.preview_line(gestures.preview(argv) if argv else ""))
        self.query_one("#season-gap", Static).update("")

    def on_input_changed(self, event: Input.Changed) -> None:
        self._show()

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        self._show()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """`enter` on a line: its profile, the line taking what it gives."""
        event.stop()
        index = event.cursor_row
        if not 0 <= index < len(self.lines):
            return
        line, whole = self.lines[index], self.lines[0]
        member = line.member is not None
        base = line.packages
        if member and base is not None:          # what `all` switches, as the member's line starts from
            base = {name: whole.switches.get(name, on) for name, on in base.items()}

        def given(found: dict | None) -> None:
            if found is None:
                return
            profile = {key: str(found[key]) for key in PROFILE_KEYS if found.get(key)}
            line.profile = ({key: value for key, value in profile.items() if whole.profile.get(key) != value}
                            if member else profile)
            line.switches = dict(found.get("packages") or {})
            self._fill()
            self._show()
        label = f"{line.member} in the season" if member else "all the members of the season"
        self.app.push_screen(ProfileScreen(label, self.providers, self.offer, line.profile, budget=False,
                                           packages=base, required=self.required,
                                           inherit=whole.profile if member else None, staged=line.switches), given)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        self.action_start()

    def on_message_area_submitted(self, event: MessageArea.Submitted) -> None:
        event.stop()
        self.action_start()

    def action_start(self) -> None:
        argv = self.argv_of(self.lines, self.values())
        if argv is None:
            self.query_one("#season-gap", Static).update(palette.bad(f"nothing to play -- {self.missing}"))
            return
        self.dismiss(argv)
