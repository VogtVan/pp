"""forms -- the FILE FORMS of the post: a form that shows, beside its fields, the file of a team it writes -- `TEAM.md`,
`SEASON.md` -- and what each member reads of it, in a frame that never moves (`FileForm`); the form of a team's values
file stands on it, one class for both files (`ValuesForm`)."""
from __future__ import annotations

from typing import Awaitable, Callable

from rich.text import Text
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import ContentSwitcher, DataTable, Input, Markdown, Select, Static, Tab, Tabs, TextArea

import palette
import panes
from model import files
from model.teams import PROFILE_KEYS, SEASON_COLUMNS, SeasonLine
from panes.documents import Documents, DocumentList, RolesScreen, Row, SourceArea, rows_of
from panes.fields import FormArea
from panes.overlays import AskScreen, Field, Overlay, ParamSelect, Part, ProfileScreen


class FileForm(Overlay):
    """A FILE FORM: a box of ONE size -- 90 % of the screen, 160 columns at most --, whatever it shows. On top its
    title and what it acts on (`head`, two rows), then the bar of its SECTIONS (`parts`); under them, on the left, the
    fields of the section shown, scrolled in their zone, its scrollbar always there; on the right the SIDE pane, on
    the whole height of the fields' zone, showing what `palette.SIDE_PANES` says of the section shown (`pane`): the
    file as it will be written (`file`, under `file_title`, rendered as markdown by Textual's `Markdown` as the overlay
    `e` renders a declaration -- its keys in a block of code, its body, `palette.file_markdown` --), what each member reads (`view`, under `view_title`), the holes of the document chosen over its text
    (`#form-holes`, `#form-doc`), or the words of the section, its first field rendered as markdown as it is typed
    (`words_of`, under the section's title) -- each zone scrolled on its own, the zones of the other panes hidden; the
    words' section gives its field the whole height of its zone. At the bottom the line of state (`status`, two rows)
    and the line of keys. No zone folds or follows its content: `ctrl+pagedown` and `ctrl+pageup` show the next and
    the previous section, as a click on its title does, whatever field holds the focus -- a table's own scroll never
    takes them; `tab` past the last field of a section goes to the first field of the next, `shift+tab` before the
    first to the last of the previous. In a text field (`FormArea`), `enter` goes to the line and `tab` leaves it; while
    a list of documents holds the focus, the line of keys offers the list's own keys. The pane of the
    document holds its holes, its text rendered (`#form-doc-text`) and its source typed (`#form-doc-source`). The
    titles of the side pane's zones read as the titles of the post's framed zones. A section yields its fields
    (`section`), each its title, its widget and its help under it (`unit`); `ids` names each field's widget. A form
    with no section shows one, `section_title`, which yields what `section` yields for it."""

    DEFAULT_CSS = """
    FileForm > #box { width: 90%; max-width: 160; height: 90%; max-height: 90%; padding: 0 1; }
    FileForm #form-head { height: 3; }
    FileForm #form-title { height: 1; }
    FileForm #form-said { height: 2; overflow: hidden; }
    FileForm #form-bar { height: 2; }
    FileForm #form-middle { height: 1fr; }
    FileForm #form-fields { width: 1fr; height: 1fr; }
    FileForm .form-section { height: 1fr; overflow-y: scroll; scrollbar-gutter: stable; padding-right: 1; }
    FileForm .field { height: 1; margin-top: 1; }
    FileForm .unit { height: auto; }
    FileForm .form-fill > .unit { height: 1fr; }
    FileForm .form-fill MessageArea { height: 1fr; max-height: 100%; }
    FileForm #form-side { width: 45%; height: 1fr; margin-left: 1; }
    FileForm .form-pane { height: 1fr; overflow-y: scroll; border: round $border-blurred; padding: 0 1;
                          border-title-color: $text; border-title-style: bold; }
    FileForm #form-status { height: 2; }
    FileForm #form-status > Static { height: 1; }
    FileForm #overlay-keys { margin-top: 0; }
    """
    BINDINGS = Overlay.BINDINGS + [Binding("ctrl+pagedown", "section(1)", "next section", show=False, priority=True),
                                   Binding("ctrl+pageup", "section(-1)", "previous section", show=False, priority=True),
                                   Binding("tab", "step(1)", "next field", show=False),
                                   Binding("shift+tab", "step(-1)", "previous field", show=False)]
    scrolls = False             # each zone scrolls itself: the box keeps its size
    keys = [("ctrl+pgdn", "next section"), ("tab", "next field"), ("esc", "close")]
    section_title = "fields"    # the one section of a form given none
    ZONES = {"file": ("form-file",), "view": ("form-view",), "document": ("form-holes", "form-doc"),
             "words": ("form-words",)}      # the zones of each pane of the side

    def __init__(self, title: str, head: Text | str = "", parts: tuple[Part, ...] = (), file: str = "",
                 view: Text | str = "", file_title: str = "file", view_title: str = "by member") -> None:
        super().__init__()
        self.title_text, self.head = title, head
        self.parts = tuple(parts) or (Part("", self.section_title, ()),)
        self.file, self.view, self.file_title, self.view_title = file, view, file_title, view_title
        self.fields = tuple(one for part in self.parts for one in part.fields)
        self.ids = {one.key: f"field-{n}" for n, one in enumerate(self.fields)}     # a key may be any text
        self.shown = 0
        self._drawn: dict[str, str] = {}        # the source each markdown of the side pane was last given

    def body(self):
        with Vertical(id="form-head"):
            yield Static(palette.strong(self.title_text), id="form-title", markup=False)
            yield Static(self.head, id="form-said", markup=False)
        bar = Tabs(*(Tab(part.title, id=f"section-{n}") for n, part in enumerate(self.parts)), id="form-bar",
                   classes="form-zone")
        bar.can_focus = False                       # `tab` goes from field to field; the bar follows the keys
        yield bar
        with Horizontal(id="form-middle"):
            with ContentSwitcher(initial="fields-0", id="form-fields", classes="form-zone"):
                for n, part in enumerate(self.parts):
                    filled = " form-fill" if self.pane_of(part) == "words" else ""
                    scroll = VerticalScroll(id=f"fields-{n}", classes=f"form-section{filled}")
                    scroll.can_focus = False        # the zone follows the focus
                    with scroll:
                        yield from self.section(part)
            with Vertical(id="form-side"):
                first = self.pane_of(self.parts[0])
                for kind in dict.fromkeys(self.pane_of(part) for part in self.parts):
                    for ident, title, content in self._zones(kind):
                        pane = VerticalScroll(id=ident, classes="form-zone form-pane")
                        pane.can_focus = False
                        pane.border_title = title
                        pane.display = kind == first
                        with pane:
                            yield from content

    def _zones(self, kind: str) -> list[tuple[str, str, list]]:
        """-> the zones of the side pane `kind`: each its id, its title and what it holds."""
        if kind == "view":
            return [("form-view", self.view_title, [Static(self.view, id="form-view-text", markup=False)])]
        if kind == "words":
            part = next(one for one in self.parts if self.pane_of(one) == "words")
            said = str(part.fields[0].value or "") if part.fields else ""
            self._drawn["form-words-text"] = palette.plain(said)
            return [("form-words", part.title, [Markdown(self._drawn["form-words-text"], id="form-words-text")])]
        if kind == "document":
            source = SourceArea("", id="form-doc-source")
            source.display = False
            return [("form-holes", "", []), ("form-doc", "", [Markdown("", id="form-doc-text"), source])]
        source = self._drawn["form-file-text"] = palette.plain(palette.file_markdown(self.file))
        return [("form-file", self.file_title, [Markdown(source, id="form-file-text")])]

    @staticmethod
    def pane_of(part: Part) -> str:
        """-> what the side pane shows beside the section `part`, as `palette.SIDE_PANES` says it."""
        return palette.SIDE_PANES.get(part.key, palette.SIDE_PANE)

    @property
    def pane(self) -> str:
        """-> what the side pane shows beside the section shown."""
        return self.pane_of(self.parts[self.shown])

    def words_of(self, values: dict) -> str | None:
        """-> the words the side pane renders: the value of the first field of the section whose pane they are; None
        for a form without one."""
        part = next((one for one in self.parts if self.pane_of(one) == "words" and one.fields), None)
        return None if part is None else str(values.get(part.fields[0].key) or "")

    def section(self, part: Part):
        """What a section shows: its fields, one after the other."""
        for one in part.fields:
            yield from self.unit(one)

    def unit(self, one: Field):
        """One field: its title, its widget, its help -- in a box of its own, shown or hidden whole."""
        ident = self.ids[one.key]
        with Vertical(classes="unit", id=f"unit-{ident}"):
            yield Static(palette.field_title(one.label), classes="field", markup=False)
            if one.kind == "list":
                held = any(value == one.value for _, value in one.options)
                widget = ParamSelect(list(one.options), id=ident, allow_blank=one.blank is not None or not one.options,
                                     value=one.value if held else Select.NULL, prompt=one.blank or "")
            elif one.kind == "text":
                widget = FormArea(str(one.value or ""), id=ident, placeholder=one.example)
            elif one.kind == "documents":
                yield DocumentList(str(one.value or ""), id=ident)
                return
            elif one.kind == "values":
                yield ValueFields(str(one.value or ""), id=ident)
                return
            else:
                widget = Input(str(one.value or ""), id=ident, type=one.number, placeholder=one.example)
            widget.disabled = one.fixed
            yield widget
            yield Static(one.help, classes="help", markup=False)

    def foot(self):
        with Vertical(id="form-status", classes="form-zone"):
            yield from self.status()

    def status(self):
        """The rows of the line of state."""
        yield Static("", id="form-state", markup=False)

    def keys_shown(self) -> list[tuple[str, str]]:
        """-> the line of keys as the focus asks it: `keys`, after the list's own while a list of documents the
        operator can tick holds the focus; while a text the operator can type in holds it, after `enter` and what it
        does there (`FORM_TEXT_ENTER`)."""
        focused = self.focused
        if isinstance(focused, DocumentList) and not self.closed():
            return [*focused.keys, *self.keys]
        if isinstance(focused, FormArea) and not focused.disabled and not focused.read_only:
            return [("enter", palette.FORM_TEXT_ENTER), *self.keys]
        return list(self.keys)

    def closed(self) -> bool:
        """-> whether the form shows its file without writing it: a form read only."""
        return False

    def switched(self) -> None:
        """The section shown changed: the side pane shows the zones of its pane, and no other."""
        shown = self.ZONES.get(self.pane, ())
        for zones in self.ZONES.values():
            for ident in zones:
                for zone in self.query(f"#{ident}"):
                    zone.display = ident in shown

    def _keys_follow(self) -> None:
        if self.query("#overlay-keys"):
            self.query_one("#overlay-keys", Static).update(palette.keys_line(self.keys_shown()))

    def on_descendant_focus(self, event) -> None:
        self._keys_follow()

    def on_descendant_blur(self, event) -> None:
        self._keys_follow()

    def side(self, file: str | None = None, view: Text | str | None = None, words: str | None = None) -> None:
        """The side pane shows `file`, `view` and `words` -- those given, in the zones the form holds."""
        if file is not None:
            self.file = file
            self._markdown("form-file-text", palette.file_markdown(file))
        if view is not None:
            self.view = view
            for one in self.query("#form-view-text"):
                one.update(view)
        if words is not None:
            self._markdown("form-words-text", words)

    def _markdown(self, ident: str, source: str) -> None:
        """The markdown `ident` of the side pane drawn anew on `source` when it changed: its update asked and left to
        the widget, which draws its updates one after the other -- nothing waits for it, nothing is left waiting when
        the form closes."""
        source = palette.plain(source)
        found = self.query(f"#{ident}")
        if found and self._drawn.get(ident) != source:
            self._drawn[ident] = source
            found.first().update(source)

    def show_section(self, index: int, last: bool = False) -> None:
        """The section `index` shown, its bar following, the focus on its first field -- its last under `last`."""
        index %= len(self.parts)
        if index != self.shown:
            self.shown = index
            self.query_one("#form-fields", ContentSwitcher).current = f"fields-{index}"
            self.query_one("#form-bar", Tabs).active = f"section-{index}"
            self.switched()

        def focused() -> None:
            chain = self.focus_chain
            if chain:
                self._focus_kept(chain[-1] if last else chain[0])
        focused()                               # at once: the section switched shows its fields already
        self.call_after_refresh(focused)        # and once laid out, should the chain have moved

    def _focus_kept(self, widget) -> None:
        """`widget` focused -- unless the focus already stands on it or inside it: a list a key unrolled before the
        form was laid out keeps its options focused, and the key after it moves their cursor."""
        focused = self.focused
        if focused is widget or (focused is not None and widget in focused.ancestors):
            return
        widget.focus()

    def focus_on(self, selector: str) -> None:
        """The widget `selector` focused, the section that holds it shown first -- at once, so that a key typed right
        after the opening reaches it, and once laid out again when the section was switched."""
        widget = self.query_one(selector)
        held = next((one for one in widget.ancestors if "form-section" in one.classes), None)
        index = int(str(held.id).removeprefix("fields-")) if held is not None else self.shown
        if index != self.shown:
            self.shown = index
            self.query_one("#form-fields", ContentSwitcher).current = f"fields-{index}"
            self.query_one("#form-bar", Tabs).active = f"section-{index}"
            self.switched()
            self.call_after_refresh(self._focus_kept, widget)
        widget.focus()

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """A click on a section's title: that section shown -- an activation the bar has already left behind (the
        bar set by the keys since) shows nothing."""
        event.stop()
        if event.tab.id != self.query_one("#form-bar", Tabs).active:
            return
        index = int(str(event.tab.id).removeprefix("section-"))
        if index != self.shown:
            self.show_section(index)

    def action_section(self, by: int) -> None:
        self.show_section(self.shown + by)

    def next_field(self) -> None:
        """`enter` in a line, or on a closed list: the next field, across sections -- none after the last of the
        last section."""
        chain = self.focus_chain
        if self.focused in chain and chain.index(self.focused) == len(chain) - 1 and self.shown == len(self.parts) - 1:
            return
        self.action_step(1)

    def action_step(self, by: int) -> None:
        """`tab`, `shift+tab`: the next field, the previous one -- across sections at a section's edge."""
        chain = self.focus_chain
        at = chain.index(self.focused) if self.focused in chain else None
        if at is not None and 0 <= at + by < len(chain):
            chain[at + by].focus()
        elif len(self.parts) > 1:
            self.show_section(self.shown + by, last=by < 0)
        elif chain:
            (chain[0] if by > 0 else chain[-1]).focus()


class ValueFields(Vertical):
    """The values a preset declares, in the section Preset of a form: one field each (`value_fields`), or the line that
    says there is none to give; `text` is the field of `values:` -- the one writer of the form's values, which each
    value typed sets by its name, on Preset as in the holes of a document --, `opened` the values it opened on."""

    DEFAULT_CSS = """
    ValueFields { height: auto; }
    """

    holds_values = True             # the form counts its `text` among what is typed (`Overlay.entered`)

    def __init__(self, text: str, id: str) -> None:
        super().__init__(id=id)
        self.text = text
        self.opened = files.values_of(text)     # the values the file gives, as the form opened
        self.made: list = []        # the fields it opens with

    def compose(self):
        yield from self.made


def value_fields(declared: list, given: dict[str, str], prefix: str, closed: bool) -> tuple[list, dict[str, str]]:
    """-> one field per value `declared` -- `{name, description, default}` each: its title, its line opened on `given`,
    its default as an example, its description under it --, its id `<prefix>-<n>`, closed under `closed`; and the name
    of the value each id types."""
    made, names = [], {}
    for n, one in enumerate(one for one in declared if isinstance(one, dict)):
        ident, name, default = f"{prefix}-{n}", str(one.get("name")), one.get("default")
        names[ident] = name
        field = Input(given.get(name, ""), id=ident, placeholder=f"e.g. {default}" if default not in (None, "") else "")
        field.disabled = closed
        made += [Static(palette.field_title(name), classes="field", markup=False), field,
                 Static(str(one.get("description") or ""), classes="help", markup=False)]
    return made, names


def preset_kept(text: str, locked: list[tuple[str, str]], keys: list[str]) -> str:
    """-> the field of `documents:` with, for each key of `keys` a season's preset gives and the field does not write
    yet, the line of the preset's documents of that key: a line the field writes replaces the preset's whole, so the
    first one written takes them with it."""
    written = files.documents_by(text)
    lines = [" ".join([key, *[document for document, one in locked if one == key]]) for key in dict.fromkeys(keys)
             if key not in written and any(one == key for _, one in locked)]
    return "\n".join([*files.lines_of(text), *lines])


def preset_dropped(text: str, preset: list[tuple[str, str]]) -> str:
    """-> the field of `documents:` without each line that only repeats the season's preset: a line whose documents
    are exactly those of the WHOLE line the preset gives for its key (`preset`, `(document, key)` each, read without
    the form's own lines), compared as sets, order aside. Such a line changes nothing at the start, so SEASON.md
    never copies it; a line that gives fewer documents than the preset's, or more, stays."""
    given = {key: {document for document, one in preset if one == key} for _, key in preset}
    return "\n".join(line for line in files.lines_of(text) if set(line.split()[1:]) != given.get(line.split()[0]))


class ValuesForm(FileForm):
    """The form of a team's VALUES FILE -- `TEAM.md` (`N`, `E`), `SEASON.md` (`S`, `s`) --, ONE class for both, on the
    frame of a file form: its title, what it acts on (`head`), its sections (`parts`), each field with its help under
    it -- a field `under` a list's value shown only while the list holds it, a field `fixed` shown read only --; for
    a season (`lines` given), the LAUNCH closing the section `launch` -- its budget, its launches, its silence -- and
    its MEMBERS the section `members` -- the table of its lines first, `all`, then one per member, each saying what it
    carries and its switches of packages, then its context --; a form with no section `members` closes its section
    `launch` with both. No task opens with a season. The side pane shows the file as it
    will be written, as `preview` makes it of the values at each change -- never read from a file --, and the view by
    member pp-team says of that text, asked by `candidate` once the keys pause -- `view` at the opening. `enter` on a
    line of the members opens its `ProfileScreen` and the line takes what it gives. `ctrl+enter` from any field gives
    what `plays` makes of the values and the lines -- `(declares, None)` --; for a
    season, `ctrl+s` the same and the start -- `(declares, start)` --: the caller plays them in that order; when `plays` makes a reason instead, it is said
    on the line of state. `follow`, given the values, gives the lists whose options move with them; `refill`, given
    the key of a list just changed and the values, the fields it sets anew; `members`, given the values, the `(name,
    path)` the lines of the season follow. A form `readonly` -- a team in season, the season shown by `s` -- shows
    its file and plays nothing, the reason on the line of state; given its `stop`, `X` asks the stop of the team
    there. `escape` gives nothing. Its values (`values`, `ValueFields`): Preset shows a field per value the preset
    chosen declares (`preset_values`, None for no preset), made anew when the preset changes; a value typed there or in
    a hole of a document is a line of `values:`, set by its name -- every field of that name following --, a value no
    field shows kept as written. Its list of documents (`documents`, `panes.documents`): `enter` ticks the roles of
    the document under the cursor -- the field of `documents:` rewritten, never written before the form's `ctrl+enter` --;
    the document chosen shows its holes and its text, rendered anew once the keys pause; `n`, `e` (`e` again writes,
    `escape` throws away) and `d` play `team document` on a house's document -- one a role holds in the form is not
    deleted, the product's is read only."""

    DEFAULT_CSS = """
    ValuesForm #season-lines { height: auto; max-height: 14; }
    """
    BINDINGS = FileForm.BINDINGS + [Binding("ctrl+s", "start", "start", show=False),
                                    Binding("X", "stop", "stop", show=False)]
    LAUNCH, MEMBERS = "launch", "members"   # the sections the launch and the members of a season close
    PAUSE = 0.4                         # seconds without a key before the view by member is asked again
    section_title = "season"

    def __init__(self, title: str, head: Text | str, parts: tuple[Part, ...],
                 plays: Callable[[dict, list[SeasonLine], bool], tuple | str] | None,
                 preview: Callable[[dict], str] | None = None, file: str = "", file_title: str = "",
                 lines: list[SeasonLine] | None = None, limits: dict | None = None, providers: list[str] = (),
                 offer: Callable[[], Awaitable[dict[str, dict]]] | None = None, required: frozenset[str] = frozenset(),
                 helps: dict | None = None, readonly: str | None = None, view: Text | str = "",
                 focus: str | None = None, follow: Callable[[dict], dict[str, tuple]] | None = None,
                 refill: Callable[[str, dict], dict] | None = None,
                 members: Callable[[dict], list[tuple[str, str]]] | None = None,
                 stop: Callable[[], Awaitable[None]] | None = None,
                 candidate: Callable[[str], Awaitable[tuple[Text | None, str | None]]] | None = None,
                 documents: Documents | None = None,
                 preset_values: Callable[[dict], list | None] | None = None) -> None:
        super().__init__(title, head, parts, file=file, view=view, file_title=file_title,
                         view_title=palette.VIEW_TITLE)
        self.preset_values = preset_values
        self._preset_declared: object = ()     # the values the fields of Preset show: none made yet
        self._preset_made = 0                   # the fields of Preset made: each its own ids
        self._remade: tuple = ()                # the fields of Preset made anew last, leaving and coming: what `settled` waits on
        self._typed: dict[str, str] = {}        # each field of a value shown, on Preset or a hole: its id -> its name
        self.plays, self.preview, self.candidate = plays, preview, candidate
        self._view_timer = None
        self._view_asked = 0            # the views asked: the last one alone is shown
        self._view_for = file           # the text the view shown is of: the file as it stands at the opening
        self._view_note: Text | str = ""    # what the line of state says of that view: being made, refused, nothing
        self.launching = lines is not None
        self.lines = list(lines or [])
        self.limits, self.providers, self.offer, self.required = dict(limits or {}), list(providers), offer, frozenset(required)
        self.helps, self.focus_key = dict(helps or {}), focus
        self.follow, self.refill, self.members = follow, refill, members
        self._options = {one.key: tuple(one.options) for one in self.fields if one.kind == "list"}
        self._lists = {one.key: one.value for one in self.fields if one.kind == "list"}   # each list's value, as last set
        keys = [part.key for part in self.parts]
        self.launch_at = keys.index(self.LAUNCH) if self.LAUNCH in keys else len(keys) - 1
        self.members_at = keys.index(self.MEMBERS) if self.MEMBERS in keys else self.launch_at
        self.stop = stop                # the stop of the team, asked by `X` when read only
        self.docs = documents           # the list of documents: what it knows and what it asks of the verbs
        self.doc: Row | None = None     # the row of the list chosen: its holes and its text shown
        self.editing: str | None = None     # the document whose source is typed
        self._doc_made = 0                  # the holes made: each its own ids
        self._doc_timer = None
        self.readonly = readonly        # a file SHOWN, never written -- in season: the reason said on the line of
        if readonly is not None:        # state, the fields closed, `enter` on a line its profile closed, no `ctrl+s`
            self.keys = ([("enter", "shows a line")] if self.launching else []) + (
                [("X", "stop the season")] if stop is not None else []) + [("ctrl+pgdn", "next section"),
                                                                           ("esc", "close")]
        elif self.launching:
            self.keys = [palette.SENDS, ("ctrl+s", "writes and starts"), ("ctrl+pgdn", "next section"),
                         ("tab", "next field"), ("esc", "cancel")]
        else:
            self.keys = [palette.SENDS, ("ctrl+pgdn", "next section"), ("tab", "next field"), ("esc", "cancel")]

    def unit(self, one: Field):
        """One field, as `FileForm` makes it; the values of Preset opened on the fields of the preset the form opens
        on, made at once -- a key typed right after the opening reaches them."""
        for widget in super().unit(one):
            if isinstance(widget, ValueFields) and self.preset_values is not None:
                declared = self.preset_values({field.key: field.value for field in self.fields})
                widget.made = self._value_widgets(declared, widget.text)
            yield widget

    def _value_widgets(self, declared: list | None, text: str) -> list:
        """-> the fields of Preset for the values `declared`, each opened on `text`; the line that says there is none to
        give when it declares none, or when no preset is chosen (None)."""
        self._typed = {ident: name for ident, name in self._typed.items() if not ident.startswith("value-")}
        self._preset_made += 1
        made, names = value_fields(declared or [], files.values_of(text), f"value-{self._preset_made}", self.closed())
        self._typed.update(names)
        self._preset_declared = declared
        said = palette.PRESET_NONE if declared is None else palette.PRESET_NO_VALUE
        return made or [Static(said, classes="help", markup=False)]

    def section(self, part: Part):
        yield from super().section(part)
        if self.launching and part is self.parts[self.launch_at]:
            yield from self._launch()
        if self.launching and part is self.parts[self.members_at]:
            yield from self._members()

    def _limit(self, ident: str, label: str, kind: str, example: str, help: str):
        """A limit of the season: its title, its field opened on `limits`, its help."""
        yield Static(palette.field_title(label), classes="field", markup=False)
        yield Input(str(self.limits.get(ident.removeprefix("season-")) or ""), id=ident, type=kind, placeholder=example)
        yield Static(help, classes="help", markup=False)

    def _launch(self):
        """The season's launch: its budget, its launches, its silence."""
        for one in (
                ("season-budget", self.helps.get("budget-label", "budget"), "number", palette.SEASON_BUDGET_EXAMPLE,
                 self.helps.get("budget", "")),
                ("season-launches", self.helps.get("launches-label", "launches"), "integer", palette.LAUNCHES_EXAMPLE,
                 self.helps.get("launches", "")),
                ("season-silence", "silence", "integer", palette.SILENCE_EXAMPLE,
                 self.helps.get("silence", palette.SILENCE_HELP))):
            yield from self._limit(*one)

    def _members(self):
        """The season's members: the table of its lines -- `all`, then one per member --, then its context."""
        yield Static(palette.field_title("members"), classes="field", markup=False)
        table = panes.table(id="season-lines", zebra_stripes=True)
        table.add_columns(*SEASON_COLUMNS)
        yield table
        yield Static(palette.SEASON_LINES_HELP, classes="help", markup=False)
        yield from self._limit("season-context", "context", "integer", palette.SEASON_CONTEXT_EXAMPLE,
                               palette.SEASON_CONTEXT_HELP)

    def status(self):
        yield Static("", id="season-note", markup=False)
        yield Static("", id="season-gap", markup=False)

    def on_mount(self) -> None:
        super().on_mount()
        self._fill()
        self._shown()
        if self.readonly is not None:
            for one in list(self.query(Input)) + list(self.query(TextArea)) + list(self.query(Select)):
                one.disabled = True
            if self.launching:
                self.focus_on("#season-lines")
        elif self.focus_key in self.ids:
            self.focus_on(f"#{self.ids[self.focus_key]}")
        elif self.fields:
            self.show_section(0)
        self._show()
        self._doc_listed()
        self.switched()
        self._preset_follow()
        self.call_after_refresh(self._preview)     # the fields laid out: the side pane made of their values

    def _fill(self) -> None:
        if not self.launching:
            return
        table = self.query_one("#season-lines", DataTable)
        row = table.cursor_row
        table.clear()
        for index, line in enumerate(self.lines):
            table.add_row(*palette.season_cells(line, self.lines[0]), key=str(index))
        if self.lines:
            table.move_cursor(row=max(0, min(row, len(self.lines) - 1)))

    def _shown(self) -> None:
        """Each field `under` a list shown while that list holds its value, hidden whole otherwise."""
        if not self.fields:
            return
        values = self.values()
        for one in self.fields:
            if one.under is not None:
                self.query_one(f"#unit-{self.ids[one.key]}").display = values.get(one.under[0]) == one.under[1]

    def held(self) -> tuple[list[tuple[dict, dict]], bool]:
        """-> what the form holds beside its fields: the profile and the switches of each line of a season, and
        whether the source of a document is typed -- open (`editing`) and other than the source it opened on: a
        source counts for the form wherever the focus stands, its own `escape` asking only while it holds it."""
        area = self.query("#form-doc-source")
        typed = self.editing is not None and bool(area) and area.first().text != area.first().opened
        return [(dict(line.profile), dict(line.switches)) for line in self.lines], typed

    def values(self) -> dict:
        """-> the value of each field -- a list's choice (None for its empty one), a line or a text stripped --, and
        for a season its launch's and its context under `season-…`."""
        found: dict = {}
        for one in self.fields:
            widget = self.query_one(f"#{self.ids[one.key]}")
            if isinstance(widget, (DocumentList, ValueFields)):
                found[one.key] = widget.text
            elif isinstance(widget, Select):
                found[one.key] = None if widget.value in (Select.NULL, Select.BLANK) else widget.value
            elif isinstance(widget, TextArea):
                found[one.key] = widget.text.strip()
            else:
                found[one.key] = widget.value.strip()
        if self.launching:
            for ident in ("season-budget", "season-launches", "season-silence", "season-context"):
                found[ident] = self.query_one(f"#{ident}", Input).value.strip()
        return found

    def _preview(self) -> None:
        """The side pane's file made anew of the values, as it will be written; the view by member asked of pp-team on
        that text once the keys pause (`candidate`, `PAUSE`), never computed here."""
        values = self.values()
        words = self.words_of(values)
        if words is not None:
            self.side(words=words)
        if self.preview is None or not self.query("#form-file-text"):
            return
        file = self.preview(values)
        self.side(file=file)
        if self.candidate is None or self.readonly is not None:
            return
        if self._view_timer is not None:
            self._view_timer.stop()
            self._view_timer = None
        if file == self._view_for:      # the text the view shown is of: nothing to ask, the line says that view's state
            self.query_one("#season-note", Static).update(self._view_note)
            return
        self._view_timer = self.set_timer(self.PAUSE, lambda: self._ask_view(file))
        self.query_one("#season-note", Static).update(palette.dim(palette.VIEW_PENDING))

    def _ask_view(self, file: str) -> None:
        self._view_timer = None
        self._view_asked, self._view_for = self._view_asked + 1, file
        self._view_note = palette.dim(palette.VIEW_PENDING)
        self.run_worker(self._view(self._view_asked, file))

    async def _view(self, asked: int, file: str) -> None:
        """The view pp-team says of `file`, shown when no later call was asked; its refusal on the line of state, the
        view left as it stood -- the line left to the keys typed since, while their pause runs."""
        view, refusal = await self.candidate(file)
        if asked != self._view_asked or not self.is_attached:
            return
        if view is not None:
            self.side(view=view)
        self._view_note = "" if view is not None else palette.bad(refusal or "")
        if self._view_timer is None:
            self.query_one("#season-note", Static).update(self._view_note)

    def _show(self) -> None:
        if not self.query("#season-note"):
            return
        if self.readonly is not None:
            self.query_one("#season-note", Static).update(palette.dim(self.readonly))
            return
        self.query_one("#season-gap", Static).update("")

    def _moved(self) -> None:
        """A value changed: the lists that follow it set again when their options moved -- each keeping its value
        while the new options still hold it --, the lines of the season following the members, the gap cleared, the
        side pane made anew."""
        if self.fields and self.follow is not None:
            for key, options in self.follow(self.values()).items():
                options = tuple(options)
                if key in self.ids and self._options.get(key) != options:
                    self._options[key] = options
                    select = self.query_one(f"#{self.ids[key]}", Select)
                    was = select.value
                    select.set_options(options)
                    if was in [value for _, value in options]:
                        select.value = was
        if self.fields and self.members is not None and self.lines:
            named = self.members(self.values())
            kept = {line.member: line for line in self.lines[1:]}
            lines = [self.lines[0]] + [kept.get(name) or SeasonLine(name, path) for name, path in named]
            for line, (name, path) in zip(lines[1:], named):
                line.path = path
            if [(one.member, one.path) for one in lines] != [(one.member, one.path) for one in self.lines]:
                self.lines = lines
                self._fill()
        self._doc_listed()
        self._show()
        self._preview()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id in self._typed:
            self._value_typed(self._typed[event.input.id], event.value.strip())
            return
        self._moved()

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        self._moved()

    def on_select_changed(self, event: Select.Changed) -> None:
        self._moved()
        self._preset_follow()
        key = next((name for name, ident in self.ids.items() if ident == event.select.id), None)
        value = None if event.value in (Select.NULL, Select.BLANK) else event.value
        if key is not None and self.refill is not None and self._lists.get(key) != value:
            self._lists[key] = value
            for name, given in self.refill(key, self.values()).items():
                widget = self.query_one(f"#{self.ids[name]}")
                if isinstance(widget, Select):
                    widget.value = Select.NULL if given is None else given
                elif isinstance(widget, TextArea):
                    widget.load_text(str(given or ""))
                else:
                    widget.value = str(given or "")
        self._shown()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """`enter` on a line: its profile, the line taking what it gives -- on the list of documents, its roles."""
        event.stop()
        if isinstance(event.data_table, DocumentList):
            self._doc_roles(event.data_table)
            return
        index = event.cursor_row
        if not 0 <= index < len(self.lines) or self.offer is None:
            return
        line, whole = self.lines[index], self.lines[0]
        member, readonly = line.member is not None, self.readonly is not None
        base, staged = line.packages, line.switches   # `all`: its set, what the operator changes of it
        if member and readonly:                       # a season shown: the set the member's face says, as it is
            base, staged = (line.packages if line.packages is not None else whole.played()), {}
        elif member:                                  # a member's line starts from the set `all` plays
            base = whole.played()

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
                                           inherit=whole.profile if member else None, staged=staged,
                                           readonly=readonly), given)

    def action_send(self) -> None:
        """`ctrl+enter`: the form gives what it writes."""
        self._give(False)

    def action_start(self) -> None:
        self._give(True)

    def check_action(self, action: str, parameters: tuple) -> bool | None:
        """`ctrl+s` starts a season's form alone; `X` is the stop of a season read only, given its `stop` --
        elsewhere the key goes to the field."""
        if action == "start":
            return self.launching and self.readonly is None
        if action == "stop":
            return self.readonly is not None and self.stop is not None
        return super().check_action(action, parameters)

    # --- the list of documents ---------------------------------------------------------------------------------------

    def closed(self) -> bool:
        return self.readonly is not None

    def _doc_list(self) -> DocumentList | None:
        found = self.query(DocumentList)
        return found.first() if found else None

    def _doc_listed(self) -> None:
        """The list of documents shown for the values as they stand: its rows made anew when they moved."""
        listed = self._doc_list()
        if listed is not None and self.docs is not None:
            listed.show_rows(rows_of(self.docs, listed.text, self.values()))

    def switched(self) -> None:
        """The side pane of the section shown, as `FileForm` shows it; on the pane of the document, the holes and the
        text -- or the source typed -- of the document chosen."""
        super().switched()
        if self.docs is None or self.pane != "document" or not self.query("#form-doc-text"):
            return
        self.query_one("#form-doc-text").display = self.editing is None
        self.query_one("#form-doc-source").display = self.editing is not None
        listed = self._doc_list()
        self.doc = listed.row_at_cursor() if listed is not None else None
        self.run_worker(self._show_document(self.doc), group="document", exclusive=True)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """The cursor of the list on a row: its document shown in the side pane."""
        if not isinstance(event.data_table, DocumentList):
            return
        event.stop()
        row = event.data_table.row_at_cursor()
        if row == self.doc or self.pane != "document":
            self.doc = row
            return
        self.doc = row
        if self.editing is not None:
            self.document_discard(focus=False)
        self.run_worker(self._show_document(row), group="document", exclusive=True)

    def _doc_titles(self, row: Row | None) -> None:
        document = row.document if row is not None and row.kind != "separator" else ""
        self.query_one("#form-holes").border_title = palette.doc_values_title(document) if document else ""
        self.query_one("#form-doc").border_title = (palette.DOC_TEXT_EDITING if self.editing is not None
                                                     else palette.DOC_TEXT_TITLE if self.docs.house(document)
                                                     and not self.closed() else palette.DOC_TEXT_READ_ONLY)

    async def _show_document(self, row: Row | None) -> None:
        """The holes of the document of `row` -- one field per value it declares, opened on the form's `values:` -- and
        its text, as the verbs say them."""
        self._doc_titles(row)
        holes = self.query_one("#form-holes")
        await holes.remove_children()
        self._typed = {ident: name for ident, name in self._typed.items() if not ident.startswith("hole-")}
        entry = self.docs.entry(row.document) if row is not None and row.kind != "separator" else None
        if entry is None:
            said = palette.DOC_KEPT_SAID if row is not None and row.kind == "kept" else ""
            await holes.mount(Static(said, classes="help", markup=False))
            await self.query_one("#form-doc-text", Markdown).update("")
            return
        self._doc_made += 1
        made, names = value_fields(entry.get("values") or [], files.values_of(self.values().get("values") or ""),
                                   f"hole-{self._doc_made}", self.closed())
        self._typed.update(names)
        await holes.mount(*(made or [Static(palette.DOC_NO_HOLE, classes="help", markup=False)]))
        await self._doc_render(entry)

    async def _doc_render(self, entry: dict) -> None:
        """The text of a document, its holes filled by `team templates --render` with the form's values and its file as
        typed (`preview`); a value missing, its source as the house sees it -- the hole said as written."""
        document = str(entry.get("template"))
        given = files.values_of(self.values().get("values") or "")
        names = [str(one.get("name")) for one in entry.get("values") or [] if isinstance(one, dict)]
        text, refusal = await self.docs.render(document, {name: given[name] for name in names if given.get(name)},
                                               self.preview(self.values()) if self.preview is not None else None)
        if text is None:
            source, refused = await self.docs.source(document)
            text = files.split(source)[1] if source is not None else (refused or refusal or "")
        if self.doc is not None and self.doc.document == document and self.is_attached:
            await self.query_one("#form-doc-text", Markdown).update(text)

    # --- the values ---------------------------------------------------------------------------------------------------

    def _values_box(self) -> ValueFields | None:
        found = self.query(f"#{self.ids['values']}") if "values" in self.ids else None
        return found.first() if found else None

    def _preset_follow(self) -> None:
        """The fields of Preset made anew when the values the preset chosen declares changed; a value the preset left
        declared and nothing declares now -- neither the preset chosen nor a document of the list -- given back to what
        the file gave of it: a value typed taken out of `values:`, a value the file gives kept as it is."""
        box = self._values_box()
        if self.preset_values is None or box is None:
            return
        declared = self.preset_values(self.values())
        if declared == self._preset_declared:
            return
        names = lambda found: {str(one.get("name")) for one in found or [] if isinstance(one, dict)}
        documents = {name for entry in (self.docs.entries if self.docs is not None else [])
                     for name in names(entry.get("values"))}
        for name in sorted(names(self._preset_declared) - names(declared) - documents):
            if files.values_of(box.text).get(name, "") != box.opened.get(name, ""):
                self._value_typed(name, box.opened.get(name, ""))
        # the fields of the preset chosen in the place of the others, their ids new: asked of the box, the form goes
        # on; what waits for the form to be settled waits on them -- on the last ones alone: the fields made before
        # them leave with the others
        self._remade = (box.remove_children(), box.mount(*self._value_widgets(declared, box.text)))

    async def settled(self) -> None:
        """Returns once the fields of Preset are those of the preset its list shows, in their box -- what a render
        waits for before it reads the form. The list is read here: its choice may not have reached the form yet."""
        self._preset_follow()
        while self._remade:
            remade, self._remade = self._remade, ()
            for one in remade:
                await one

    def _value_typed(self, name: str, value: str) -> None:
        """A value typed -- on Preset, or in a hole of the document chosen --: set by its name in `values:`, the one
        writer of the form's values, every other field of that name following without a `Changed` of its own -- the
        operator's keys alone are followed, so two fields of one name never echo each other --, the side pane made
        anew; the text of the document chosen rendered anew once the keys pause."""
        box = self._values_box()
        if box is None:
            return
        if files.values_of(box.text).get(name, "") != value:
            box.text = files.values_merged(box.text, {name: value})
            for ident, one in self._typed.items():
                other = self.query(f"#{ident}")
                if one == name and other and other.first().value.strip() != value:
                    with other.first().prevent(Input.Changed):
                        other.first().value = value
            self._moved()
        if self._doc_timer is not None:
            self._doc_timer.stop()
        row = self.doc
        entry = self.docs.entry(row.document) if row is not None and self.docs is not None else None
        if entry is not None:
            self._doc_timer = self.set_timer(self.PAUSE, lambda: self.run_worker(self._doc_render(entry), group="text",
                                                                                 exclusive=True))

    def _doc_roles(self, listed: DocumentList) -> None:
        """`enter` on the list: the roles its document is given to, ticked in their overlay; a line of the preset or one
        kept as written said on the line of state."""
        row = listed.row_at_cursor()
        if self.closed() or row is None or row.kind == "separator":
            return
        if row.kind == "locked":
            self.say(palette.doc_locked(self.docs.locked(self.values())[1]))
            return
        if row.kind == "kept":
            self.say(palette.DOC_KEPT_SAID)
            return

        def given(keys: list[str] | None) -> None:
            if keys is None:
                return
            locked = self.docs.locked(self.values())[0]
            keys = list(keys) + [key for document, key in locked if document == row.document and key not in keys]
            listed.text = preset_dropped(files.documents_given(preset_kept(listed.text, locked, keys), row.document, keys),
                                         self.docs.locked({**self.values(), "documents": ""})[0])
            self._moved()
        self.app.push_screen(RolesScreen(row.document, self.docs.roles(self.values()),
                                         files.keys_given(listed.text, row.document)), given)

    def _doc_house_row(self) -> Row | None:
        """-> the row of a house's document under the cursor; None, said on the line of state, otherwise."""
        listed = self._doc_list()
        row = listed.row_at_cursor() if listed is not None else None
        if self.closed() or row is None or row.kind not in ("document", "locked"):
            return None
        if not self.docs.house(row.document):
            self.say(palette.DOC_READ_ONLY)
            return None
        return row

    def document_new(self) -> None:
        """`n` on the list: a house's document born by `team document --new`, chosen, its source open."""
        if self.closed() or self.docs is None:
            return

        async def made(name: str) -> None:
            refusal = await self.docs.written(name, "new", None)
            if refusal is not None:
                self.say(refusal)
                return
            await self._doc_reread(name)
            await self._doc_edit(name)
        self.app.push_screen(AskScreen(palette.DOC_NEW_PROMPT, palette.DOC_NEW_HELP),
                             lambda name: self.run_worker(made(name)) if name else None)

    def document_edit(self) -> None:
        """`e` on the list: the source of a house's document open in the side pane; `e` again writes it by `team
        document --body-file -`."""
        row = self._doc_house_row()
        if row is None:
            return
        if self.editing == row.document:
            self.run_worker(self._doc_write(row.document))
        else:
            self.run_worker(self._doc_edit(row.document))

    async def _doc_edit(self, document: str) -> None:
        source, refusal = await self.docs.source(document)
        if source is None:
            self.say(refusal or "")
            return
        area = self.query_one("#form-doc-source", SourceArea)
        area.load_text(source)
        area.opened = source
        self.editing = document
        self.switched_text()
        area.focus()

    async def _doc_write(self, document: str) -> None:
        refusal = await self.docs.written(document, "write", self.query_one("#form-doc-source", SourceArea).text)
        if refusal is not None:
            self.say(refusal)
            return
        self.editing = None
        self.switched_text()
        self.said_done(palette.doc_done(document, "written"))
        entry = self.docs.entry(document)
        if entry is not None:
            await self._doc_render(entry)

    def switched_text(self) -> None:
        """The text of the document or its source, as `editing` says."""
        self.query_one("#form-doc-text").display = self.editing is None
        self.query_one("#form-doc-source").display = self.editing is not None
        self._doc_titles(self.doc)

    def document_discard(self, focus: bool = True) -> None:
        """`escape` in the source: thrown away, the text shown again, nothing written."""
        self.editing = None
        self.switched_text()
        listed = self._doc_list()
        if focus and listed is not None:
            listed.focus()

    def document_delete(self) -> None:
        """`d` on the list: a house's document given to nobody, deleted by `team document --delete` once its name is
        typed; one a role holds in the form said on the line of state, nothing played."""
        row = self._doc_house_row()
        if row is None:
            return
        keys = files.keys_given(self._doc_list().text, row.document)
        if keys:
            self.say(palette.doc_given(row.document, keys))
            return

        async def deleted() -> None:
            refusal = await self.docs.written(row.document, "delete", None)
            if refusal is not None:
                self.say(refusal)
                return
            await self._doc_reread(None)
            self.said_done(palette.doc_done(row.document, "deleted"))
        self.app.push_screen(AskScreen(palette.doc_delete_prompt(row.document), palette.DOC_DELETE_HELP),
                             lambda typed: self.run_worker(deleted()) if typed == row.document else None)

    async def _doc_reread(self, chosen: str | None) -> None:
        """The documents read again, the list made anew -- `chosen` under its cursor."""
        self.docs.entries = await self.docs.reread()
        listed = self._doc_list()
        listed.show_rows(rows_of(self.docs, listed.text, self.values()))
        if chosen is not None:
            listed.choose(chosen)
        self.doc = listed.row_at_cursor()
        await self._show_document(self.doc)

    def said_done(self, said: str) -> None:
        """What a gesture of the list did, on the line of state."""
        self.query_one("#season-gap", Static).update(palette.dim(said))

    def say(self, said: str) -> None:
        """A word on the line of state -- none once the form is closed."""
        if self.is_attached and self.query("#season-gap"):
            self.query_one("#season-gap", Static).update(palette.bad(said))

    async def action_stop(self) -> None:
        if self.readonly is not None and self.stop is not None:
            await self.stop()

    def _give(self, start: bool) -> None:
        """What `plays` makes of the values and the lines, given with them -- the start under `start`; a reason said
        on the line of state."""
        if self.readonly is not None or self.plays is None:
            return
        values = self.values()
        made = self.plays(values, self.lines, start)
        if isinstance(made, str):
            self.query_one("#season-gap", Static).update(palette.bad(f"nothing to play -- {made}"))
            return
        declares, started = made
        self.dismiss({"declares": list(declares), "start": started, "given": values, "lines": self.lines})
