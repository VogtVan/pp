"""_team_forms -- what the scenarios of the two file forms share (rule 10): the faces of team 1.26.0 the bench's
`pp-team` witness replays -- `team templates --json` one object per template (`preset` or `document`, its directory in
its name), `team declaration --json` with `declared.documents`, `declared.values` and each member's view, `core-review`'s TEAM.md and
SEASON.md as texts --, the keys that type a text, and the readers of the side pane by the regions `boxes` notes."""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")

SIZE = ("--size", "140x60")             # the side pane tall enough for the whole file
KEY_OF = {" ": "space", "/": "slash", "-": "minus", "=": "equals_sign", ".": "full_stop", "|": "vertical_line",
          "_": "underscore", ">": "greater_than_sign", "#": "number_sign", "*": "asterisk", ":": "colon"}

TEMPLATES = [
    {"template": "review/read-commits", "kind": "document", "origin": "package", "description": "a reader reads commits",
     "values": []},
    {"template": "review/read-files", "kind": "document", "origin": "package", "description": "a reader reads files",
     "values": [{"name": "folder", "description": "the folder read", "default": None}]},
    {"template": "seasons/files", "kind": "preset", "origin": "package", "description": "members write files",
     "values": [{"name": "readers", "description": "the role key of who reads", "default": "readers"}],
     "documents": [{"key": "{readers}", "documents": ["review/read-files"]}]},
    {"template": "teams/solo", "kind": "preset", "origin": "package", "description": "one member does every task",
     "values": [], "documents": [], "form": "one", "members": ["solo"], "root": "solo", "reports": [],
     "ceremony": None, "limits": {"budget": 5, "launches": 8, "timeout": 900}, "intention": "solo answers."},
    {"template": "teams/lead-reviewers", "kind": "preset", "origin": "package", "description": "a lead, reviewers",
     "values": [], "documents": [], "form": "star", "members": ["lead", "reviewer"], "root": "lead",
     "reports": [{"from": ["reviewer"], "to": "lead"}], "ceremony": None,
     "limits": {"budget": 5, "launches": 8, "timeout": 900}, "intention": "lead answers."}]

TEAM_TEXT = """---
description: "reviews the PRs"
agents: |
  lead agents/lead
  reviewer agents/reviewer
roles: |
  readers reviewer
documents: |
  all review/read-files
values: |
  folder = notes
budget: 5
---
The owner's word.
"""
SEASON_TEXT = """---
template: seasons/files
values: |
  readers = readers
---
"""


# what each member reads, as `declared.views` says it: the document of `all`, and the season's of the role `readers`
ROLE_DOC = "roles/TEAM-core-review-read-files.md"
VIEWS = [{"member": "lead", "roles": [], "documents": [T.document("TEAM-core-review-read-files.md", "served")]},
         {"member": "reviewer", "roles": ["readers"],
          "documents": [T.document("TEAM-core-review-read-files.md", "served"),
                        T.document(ROLE_DOC, "mounted", ("readers",))]}]


def declaration() -> dict:
    """-> `core-review` as `team declaration --json` says it under team 1.26.0: TEAM.md and SEASON.md as texts, their
    documents by key, the values applied."""
    face = T.declaration("core-review", [("lead", "agents/lead"), ("reviewer", "agents/reviewer")], {"budget": 5.0},
                         roles=(("readers", ["reviewer"]),), season=T.CORE_SEASON, description="reviews the PRs",
                         views=VIEWS)
    declared = {**face["declared"],
                "documents": [{"key": "all", "team": ["review/read-files"], "season": []},
                              {"key": "readers", "team": [], "season": ["review/read-files"]}],
                "values": [{"name": "folder", "value": "notes", "from": "team"},
                           {"name": "readers", "value": "readers", "from": "season"}]}
    declared.pop("compose", None)
    declared.pop("organization", None)
    return {**face, "text": TEAM_TEXT, "declared": declared,
            "season": {"path": "teams/core-review/SEASON.md", "text": SEASON_TEXT, "digest": "def456def456"}}


def script(**extra) -> dict:
    return T.script(templates=TEMPLATES, declarations={**T.DECLARATIONS, "core-review": declaration()}, **extra)


def typed(text: str) -> str:
    """-> the keys that type `text`."""
    return ",".join(KEY_OF.get(char, char) for char in text)


def pane_rows(text: str, zone: str) -> list[str]:
    """-> the rows of the screen inside the zone `zone` the closing `boxes` line notes, inside its border, stripped."""
    line = next((one for one in text.splitlines() if one.startswith("boxes ")), "")
    found = dict(re.findall(r"([\w-]+)=(\d+,\d+,\d+,\d+)", line.split(" | ")[-1]))
    if zone not in found:
        return []
    x, y, w, h = map(int, found[zone].split(","))
    rows = text.splitlines()
    return [rows[n][x + 1:x + w - 1].rstrip(SCROLLBAR).strip(" │").strip()
            for n in range(y + 1, min(y + h - 1, len(rows)))]


SCROLLBAR = " ▁▂▃▄▅▆▇█▔▀▕▏"            # what a scrollbar draws at the right of a zone


def zone_rows(text: str, zone: str, inner: bool = True) -> list[str]:
    """-> the rows of the screen inside the zone `zone` -- inside its border under `inner` --, stripped."""
    line = next((one for one in text.splitlines() if one.startswith("boxes ")), "")
    found = dict(re.findall(r"([\w-]+)=(\d+,\d+,\d+,\d+)", line.split(" | ")[-1]))
    if zone not in found:
        return []
    x, y, w, h = map(int, found[zone].split(","))
    cut = 1 if inner else 0
    rows = text.splitlines()
    return [rows[n][x + cut:x + w - cut].rstrip(SCROLLBAR).strip(" │").strip()
            for n in range(y + cut, min(y + h - cut, len(rows)))]


def fields(text: str) -> list[str]:
    """-> the rows of the zone of the fields: what `P.field_of` and `N.help_under` read."""
    return zone_rows(text, "form-fields", inner=False)


def state(text: str) -> str:
    """-> what the line of state of a form says, its rows joined."""
    return " ".join(one for one in zone_rows(text, "form-status", inner=False) if one)


def section(n: int) -> str:
    """-> the keys that show the section `n` sections further."""
    return ",".join(["ctrl+pagedown"] * n)


# the sections of the two forms, in their order, and the side pane each shows -- the zones `boxes` notes for it: the file
# as it will be written, the view by member, the holes and the text of the document chosen, the words rendered
TEAM_TABS = ["Team", "Preset", "Members", "Documents", "Limits", "Owner's word"]
SEASON_TABS = ["Preset", "Documents", "Launch", "Members", "Season's word"]
PANES = {"file": ("form-file",), "view": ("form-view",), "document": ("form-holes", "form-doc"), "words": ("form-words",)}
TEAM_PANES = ["file", "file", "view", "document", "file", "words"]
SEASON_PANES = ["file", "document", "file", "view", "words"]


def team_to(tab: str) -> str:
    """-> the keys that show the section `tab` of the team's form from its first, Team -- each focused on its first
    field."""
    return section(TEAM_TABS.index(tab))


def season_to(tab: str) -> str:
    """-> the keys that show the section `tab` of the season's form from its first, Preset, which `S` opens on."""
    return section(SEASON_TABS.index(tab))


# the season's form opens on its section Preset, its preset focused; its documents one section further, the list
# focused; its launch two sections further, the work read only: the budget, the launches, the silence; its members
# three sections further: the table of its lines first, focused, then the context
TO_SEASON_DOCUMENTS = season_to("Documents")
TO_LAUNCH = season_to("Launch")
TO_LINES = season_to("Members")
NEW_LINE = f"[enter] {P.palette_constant('FORM_TEXT_ENTER')}"   # what the line of keys offers in a text field alone


def keys_row(text: str) -> str:
    """-> the line of keys of the overlay on top: its row that offers `[esc]`; '' without one."""
    return next((row for row in P.overlay_rows(text) if "[esc]" in row), "")


def tabs_row(text: str) -> list[str]:
    """-> the titles of the bar of sections of a form, in their order: the row of the overlay that holds the first."""
    row = next((one for one in P.overlay_rows(text) if one.startswith("Preset ") or one.startswith("Team ")), "")
    return [one for one in re.split(r"\s{2,}", row.strip()) if one]


def by_member(view: list[str], members: list[str]) -> dict[str, str]:
    """-> what the view by member says of each of `members`: the row that opens on its name and the rows that follow
    it, up to the next member's -- a member's documents wrap over several rows."""
    found: dict[str, list[str]] = {name: [] for name in members}
    current = None
    for row in view:
        head = row.split(":")[0].split()[:1]
        if head and head[0] in found:
            current = head[0]
        elif not row:
            current = None
        if current is not None:
            found[current].append(row)
    return {name: " ".join(rows) for name, rows in found.items()}


def document_rows(text: str) -> list[list[str]]:
    """-> the rows of the list of documents a capture shows in the zone of the fields: each its cells (what two blanks
    or more part), from the row under its title (`Documents`, `Documents of the season`) on; a separator `── … ──` one
    cell."""
    found, seen = [], False
    for row in fields(text):
        if row in ("Documents", "Documents of the season"):
            seen = True
            continue
        if seen and row.strip(" ▁▂▃▄▅▆▇█▎"):
            found.append([one for one in re.split(r"\s{2,}", row.strip(" │┃▎")) if one])
    return found


def role_of(text: str, document: str) -> str | None:
    """-> the role cell of `document` in the list of documents, None when it is not listed."""
    return next((" ".join(one[1:]) for one in document_rows(text) if one[:1] == [document]), None)


WRITE = "ctrl+enter"                   # the key that writes the form, from any of its fields
# what `enter` on a document's role opens: `— nobody`, then `all`, then each role key; the cursor on the first
ALL, FIRST_ROLE = "down,enter", "down,down,enter"   # a row chosen ticks it (batch les-paquets-qui-basculent)
