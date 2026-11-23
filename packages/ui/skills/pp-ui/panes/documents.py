"""documents -- the LIST OF DOCUMENTS of a file form: every document `team templates --json` says, the house's first,
the package's under a separator, each with the role keys a line of `documents:` gives it to (`DocumentList`); the
roles a document is given to, ticked in an overlay (`RolesScreen`); the source of a house's document typed
(`SourceArea`); what the form asks of the verbs to show and change them (`Documents`). The list writes nothing: it
rewrites the text of `documents:` the form compares with the file, a line it does not understand kept as written."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Awaitable, Callable

from rich.text import Text
from textual.binding import Binding
from textual.widgets import DataTable, OptionList, Static, TextArea
from textual.widgets.option_list import Option

import palette
from model import files
from panes.overlays import Overlay

HOUSE = "house"


@dataclass
class Documents:
    """What a form's list of documents knows and asks: the documents `team templates --json` says (`entries`, each
    `{template, origin, values}`), the documents the list leaves out (`excluded`: in a season's form, the team's), the
    role keys a document may be given to for the form's values (`roles`), the lines a season's preset gives for them
    (`locked`: `(document, key)` each, and the preset's name), and the verbs: `render` (`team templates --render` of a
    document for the form's values and its file as typed, the text with its holes filled, or the refusal), `source` (`team document --json`), `written` (`team document --new |
    --body-file - | --delete`: None when it wrote, else its refusal) and `reread` (the entries read again)."""
    entries: list[dict]
    roles: Callable[[dict], list[str]]
    render: Callable[[str, dict[str, str], str | None], Awaitable[tuple[str | None, str | None]]]
    source: Callable[[str], Awaitable[tuple[str | None, str | None]]]
    written: Callable[[str, str, str | None], Awaitable[str | None]]
    reread: Callable[[], Awaitable[list[dict]]]
    excluded: frozenset[str] = frozenset()
    locked: Callable[[dict], tuple[list[tuple[str, str]], str]] = field(default=lambda values: ([], ""))

    def entry(self, document: str) -> dict | None:
        return next((one for one in self.entries if one.get("template") == document), None)

    def house(self, document: str) -> bool:
        return (self.entry(document) or {}).get("origin") == HOUSE


@dataclass(frozen=True)
class Row:
    """One row of the list: a `document` given to its `keys`, a `locked` line of a preset, a line `kept` as written, or
    a `separator` (its text in `document`)."""
    kind: str
    document: str
    keys: tuple[str, ...] = ()

    def cells(self) -> tuple[str, str]:
        if self.kind == "separator":
            return self.document, ""
        if self.kind == "locked":
            return self.document, f"= {self.keys[0]}"
        return self.document, ", ".join(self.keys) or palette.DOC_NOBODY


def rows_of(documents: Documents, text: str, values: dict) -> list[Row]:
    """-> the rows of the list for the field of `documents:` `text`: the lines the preset gives, locked, under their
    separator; the house's documents; the package's under theirs; then, under theirs, each document a line names that
    the list does not show, kept as written."""
    given = files.documents_by(text)
    locked, preset = documents.locked(values)
    keys = lambda document: tuple(key for key, named in given.items()
                                  if document in named and (document, key) not in locked)
    rows = [Row("locked", document, (key,)) for document, key in locked]
    rows += [Row("separator", palette.doc_preset(preset))] if locked else []
    shown = [one for one in documents.entries if one.get("template") not in documents.excluded]
    rows += [Row("document", str(one["template"]), keys(str(one["template"])))
             for one in shown if one.get("origin") == HOUSE]
    product = [one for one in shown if one.get("origin") != HOUSE]
    rows += ([Row("separator", palette.DOC_PRODUCT)] if product else []) + [
        Row("document", str(one["template"]), keys(str(one["template"]))) for one in product]
    listed = {one.document for one in rows if one.kind in ("document", "locked")}
    kept = [Row("kept", document, (key,)) for key, named in given.items() for document in named
            if document not in listed]
    return rows + ([Row("separator", palette.DOC_KEPT)] if kept else []) + kept


class DocumentList(DataTable):
    """The list of documents of a form, its `text` the field of `documents:` it rewrites; `n`, `e` and `d` ask the
    form (`document_new`, `document_edit`, `document_delete`) for the row under the cursor."""

    DEFAULT_CSS = """
    DocumentList { height: auto; max-height: 30; }
    """
    BINDINGS = [Binding("n", "new", "new", show=False), Binding("e", "edit", "edit text", show=False),
                Binding("d", "delete", "delete", show=False)]
    keys = palette.DOC_KEYS
    holds_values = True             # the form counts its `text` among what is typed (`Overlay.entered`)

    def __init__(self, text: str, **kw) -> None:
        super().__init__(show_header=False, cursor_type="row", cursor_foreground_priority="renderable", **kw)
        self.text = text
        self.rows_shown: list[Row] = []

    def show_rows(self, rows: list[Row]) -> None:
        """The rows shown, the cursor kept on its document -- on the first document at the first showing."""
        if rows == self.rows_shown:
            return
        was = self.row_at_cursor().document if self.rows_shown and self.row_at_cursor() is not None else None
        self.rows_shown = rows
        self.clear(columns=True)            # the columns as wide as the cells they hold now, said
        cells = [row.cells() for row in rows]
        self.add_column("document", width=max([len("document")] + [len(one[0]) for one in cells]))
        self.add_column("role", width=max([len("role")] + [len(one[1]) for one in cells]))
        for row in rows:
            self.add_row(*row.cells())
        at = next((n for n, row in enumerate(rows) if row.kind != "separator" and row.document == was), None)
        if at is None:
            at = next((n for n, row in enumerate(rows) if row.kind != "separator"), 0)
        if rows:
            self.move_cursor(row=at)

    def row_at_cursor(self) -> Row | None:
        at = self.cursor_row
        return self.rows_shown[at] if 0 <= at < len(self.rows_shown) else None

    def choose(self, document: str) -> None:
        at = next((n for n, row in enumerate(self.rows_shown) if row.kind == "document" and row.document == document),
                  None)
        if at is not None:
            self.move_cursor(row=at)

    def action_new(self) -> None:
        self.screen.document_new()

    def action_edit(self) -> None:
        self.screen.document_edit()

    def action_delete(self) -> None:
        self.screen.document_delete()


class SourceArea(TextArea):
    """The source of a house's document typed in the side pane: `escape` throws it away, the form untouched -- once it
    differs from the source it opened on (`opened`), after the form's confirmation (`confirm_leave`). The form does not
    count it among its fields (`apart`): it guards its own typing."""

    BINDINGS = [Binding("escape", "discard", "throw away", show=False)]
    apart = True
    opened = ""                 # the source as it was read, before any key

    def action_discard(self) -> None:
        if self.text != self.opened:
            self.screen.confirm_leave(self.screen.document_discard)
        else:
            self.screen.document_discard()


class RolesScreen(Overlay):
    """The roles a document is given to, ticked: `— nobody`, then each role key; a line chosen -- a click, `enter` --
    or `space` on it ticks it or unticks it, the overlay kept -- `— nobody` unticks every key --; `ctrl+enter` alone
    gives the keys ticked in their order, `escape` nothing -- asked first once a key is ticked or unticked (`held`)."""

    BINDINGS = Overlay.BINDINGS + [Binding("space", "tick", "tick", show=False)]
    keys = [("space", "tick"), palette.SENDS, ("esc", "cancel")]

    def __init__(self, document: str, roles: list[str], ticked: list[str]) -> None:
        super().__init__()
        self.document, self.roles = document, list(dict.fromkeys(roles + [one for one in ticked if one not in roles]))
        self.ticked = [one for one in self.roles if one in ticked]

    def _prompt(self, key: str | None) -> Text:
        if key is None:
            return Text(f"[{'x' if not self.ticked else ' '}] {palette.DOC_NOBODY_OPTION}")
        return Text(f"[{'x' if key in self.ticked else ' '}] {key}")

    def body(self):
        yield Static(palette.strong(self.document), markup=False)
        yield OptionList(Option(self._prompt(None), id="-"), *(Option(self._prompt(key), id=f"k{n}")
                                                               for n, key in enumerate(self.roles)), id="roles")
        yield Static(palette.DOC_ROLES_HELP, classes="help", markup=False)

    def on_mount(self) -> None:
        listed = self.query_one("#roles", OptionList)
        listed.highlighted = 0
        listed.focus()

    def action_tick(self) -> None:
        listed = self.query_one("#roles", OptionList)
        if listed.highlighted is None:
            return
        at = listed.highlighted
        if at == 0:
            self.ticked = []
        else:
            key = self.roles[at - 1]
            self.ticked = ([one for one in self.ticked if one != key] if key in self.ticked
                           else [one for one in self.roles if one in self.ticked or one == key])
        listed.replace_option_prompt("-", self._prompt(None))
        for n, key in enumerate(self.roles):
            listed.replace_option_prompt(f"k{n}", self._prompt(key))

    def held(self) -> list[str]:
        """-> the keys ticked: the choices the overlay holds."""
        return list(self.ticked)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """A line chosen -- a click, `enter` --: ticked or unticked, as `space` does."""
        event.stop()
        event.option_list.highlighted = event.option_index
        self.action_tick()

    def action_send(self) -> None:
        self.dismiss(list(self.ticked))
