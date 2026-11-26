"""_documents -- what the scenarios of the list of documents share (rule 10): `core-review`'s TEAM.md naming
`review/read-files` and, on a second line of the same key, the team's own file `notes.md` for every member,
`notes/release` for the role `readers`; the
house's documents `notes/release` and `notes/style` -- one hole each, `tag`, no default -- before the package's
`review/read-commits` (no hole) and `review/read-files` (`folder`); the bench's `pp-team` witness says their sources
(`document --json`) and renders them (`templates --render`); the keys that reach the list and read it."""
from __future__ import annotations

from tests.harness import support

F = support(__file__, "team_forms")
T, P = F.T, F.P

TAG = [{"name": "tag", "description": "the tag released", "default": None}]
RELEASE = {"template": "notes/release", "kind": "document", "origin": "house", "description": "what a release checks",
           "values": TAG}
STYLE = {"template": "notes/style", "kind": "document", "origin": "house", "description": "how the notes are written",
         "values": TAG}
BODIES = {"notes/release": "# Release\n\nBefore tag {tag}: run the bench.\n",
          "notes/style": "# Style\n\nTag {tag} in short sentences.\n",
          "review/read-commits": "# Commits\n\nRead the commits.\n",
          "review/read-files": "# Files\n\nRead {folder}.\n"}
PACKAGE = [one for one in F.TEMPLATES if one["kind"] == "document"]       # review/read-commits, review/read-files
TEMPLATES = [RELEASE, STYLE] + F.TEMPLATES
DECLARED = {one["template"]: one["values"] for one in [RELEASE, STYLE] + PACKAGE}
SOURCES = {name: "---\ndescription: a document\n---\n" + body for name, body in BODIES.items()}
RENDERS = {name: {"text": body, "values": DECLARED[name]} for name, body in BODIES.items()}
LINES = "  all review/read-files\n  readers notes/release\n  all notes.md\n"     # the key `all` written on two lines
SAID = {name: body.splitlines()[2] for name, body in BODIES.items()}     # the line of each text under its title
TAGGED = SAID["notes/style"].replace("{tag}", "1.0")                     # notes/style's line rendered for tag 1.0


def declaration(running: bool = False) -> dict:
    """-> `core-review` as `F.declaration` says it, its documents the lines `LINES`."""
    face = F.declaration()
    text = face["text"].replace("  all review/read-files\n", LINES)
    started = {**face["started"], "state": "running"} if running else face["started"]
    return {**face, "text": text, "started": started}


def script(running: bool = False, **extra) -> dict:
    return T.script(templates=TEMPLATES, renders=RENDERS, sources=SOURCES,
                    declarations={**T.DECLARATIONS, "core-review": declaration(running)}, **extra)


SIZE = F.SIZE
TO_DOCUMENTS = F.team_to("Documents")  # `E`: Documents, its first document under the cursor
WRITE, ALL = F.WRITE, F.ALL
PAUSE = "rest:1"                       # past the pause after which the text is rendered anew


rows, role_of = F.document_rows, F.role_of       # the readers of the list


def renders(house) -> list[str]:
    """-> the `templates --render` calls the witness answered, each with its values."""
    return [one for one in house.journal_lines() if one.startswith("templates --render")]


def bodies(house) -> list[str]:
    """-> the bodies a gesture read on its standard input, as the witness journaled them."""
    import json
    return [json.loads(one[len("body "):]) for one in house.journal_lines() if one.startswith("body ")]
