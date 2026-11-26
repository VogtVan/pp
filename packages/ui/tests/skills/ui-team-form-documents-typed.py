"""Scenario `ui-team-form-documents-typed` -- the text of the document chosen in the list of documents rendered on the
form's TYPED file (batch l-apercu-du-texte-tape, s.1598 s.1599), on the bench's `pp-team` witness (`_documents`): the
post sends `team templates --render <document> --team <team> [--season] --text-file -`, the file its side pane shows on
the verb's input, and no `--value`:
- s.1598: in the form of TEAM.md, `folder` emptied in the hole of `review/read-files` and not written: the text no
  longer says the disk's `notes`, the hole is said as written (`{folder}`)
- s.1599: `tag` emptied in the hole of `notes/release` while SEASON.md gives `tag = 2.0`: the text says `2.0`, the value
  the next start takes
- the form of SEASON.md renders on its own file: `--season --text-file`, SEASON.md's text sent
Its siblings: `ui-team-form-documents-holes` (a hole typed, its value written), `ui-team-form-documents`,
`ui-team-form-documents-raced` (keys typed back to back in a hole whose name Preset holds, cut by case, rule 10).
"""
from __future__ import annotations

import json

from tests.harness import support

D = support(__file__, "documents")
F, T = D.F, D.T

FILES = "down,down,down,down"                  # notes/style, the separator, review/read-commits, review/read-files
EMPTIED = f"E,{D.TO_DOCUMENTS},{FILES},tab,backspace,backspace,backspace,backspace,backspace,{D.PAUSE},boxes"
TAG_EMPTIED = f"E,{D.TO_DOCUMENTS},tab,backspace,backspace,backspace,{D.PAUSE},boxes"


def seasoned() -> dict:
    """-> the script of `_documents` with `tag = 1.0` in TEAM.md and `tag = 2.0` in SEASON.md, the season's applied."""
    face = D.declaration()
    text = face["text"].replace("  folder = notes\n", "  folder = notes\n  tag = 1.0\n")
    season = {**face["season"], "text": face["season"]["text"].replace("  readers = readers\n",
                                                                       "  readers = readers\n  tag = 2.0\n")}
    declared = {**face["declared"], "values": [*face["declared"]["values"], {"name": "tag", "value": "2.0",
                                                                             "from": "season"}]}
    return T.script(templates=D.TEMPLATES, renders=D.RENDERS, sources=D.SOURCES,
                    declarations={**T.DECLARATIONS, "core-review": {**face, "text": text, "season": season,
                                                                     "declared": declared}})


def last_render(house, document: str) -> str:
    """-> the last `templates --render` of `document` the witness answered."""
    return next((one for one in reversed(D.renders(house)) if one.startswith(f"templates --render {document}")), "")


def candidate(said: str) -> str:
    """-> the candidate text a render journaled after `--text-file`, '' without one."""
    _, mark, rest = said.partition("--text-file")
    rest = rest.removeprefix(" --season")
    return json.loads(rest.strip()) if mark and rest.strip() else ""


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-form-documents-typed", D.script())

    # --- s.1598: a value emptied, not written: the disk's is not rendered -----------------------------------------------
    house.clear_journal()
    emptied = house.render("--render", "teams", *D.SIZE, "--press", EMPTIED)
    said, text = last_render(house, "review/read-files"), " ".join(F.zone_rows(emptied.stdout, "form-doc"))
    sent = candidate(said)
    if (sent and "folder" not in sent and "=" not in said.partition("--text-file")[0] and "Read notes." not in text
            and "{folder}" in text):
        held("s.1598: the typed TEAM.md rendered, the emptied value not the disk's", f"{said[:70]!r}; {text.strip()[:40]!r}")
    else:
        failures.append(f"  ✗ s.1598 emptied              {said!r} {text!r}")

    # --- s.1599: emptied in TEAM.md, SEASON.md's value rendered -------------------------------------------------------
    house.use(seasoned())
    house.clear_journal()
    tag = house.render("--render", "teams", *D.SIZE, "--press", TAG_EMPTIED)
    said, text = last_render(house, "notes/release"), " ".join(F.zone_rows(tag.stdout, "form-doc"))
    sent = candidate(said)
    if sent and "tag" not in sent and "tag=" not in said and "Before tag 2.0" in text:
        held("s.1599: SEASON.md's value rendered once TEAM.md's is emptied", f"{said[:70]!r}; {text.strip()[:40]!r}")
    else:
        failures.append(f"  ✗ s.1599 season's value       {said!r} {text!r}")

    # --- the season's form: its own file, under --season ---------------------------------------------------------------
    house.use(D.script())
    house.clear_journal()
    season = house.render("--render", "teams", *D.SIZE, "--press", f"S,{F.TO_SEASON_DOCUMENTS},{D.PAUSE},boxes")
    said, text = last_render(house, "review/read-files"), " ".join(F.zone_rows(season.stdout, "form-doc"))
    if " --text-file --season " in said and "template: seasons/files" in candidate(said) and "Read notes." in text:
        held("the season's form renders on SEASON.md typed", f"{said[:70]!r}; {text.strip()[:40]!r}")
    else:
        failures.append(f"  ✗ season's form               {said!r} {text!r}")
    return 0
