"""Scenario `ui-team-form-season-documents-dropped` -- a line of `documents:` equal to the line the season's preset gives
for its key is taken out of the field at the gesture of the list (batch la-ligne-du-preset-recopiee, cut from
`ui-team-form-season-documents`), on the bench's `pp-team` witness replaying the faces of team 1.26.0: `core-review`,
its SEASON.md on the preset `seasons/files`:
- `readers` ticked then unticked on `review/read-commits`: the line left equals the preset's for that key, so the field
  drops it -- the file of the side pane writes no line of `documents:`, writing plays no `--document` (s.1608)
- a line that NARROWS the preset's is kept: the preset gives `readers review/read-commits notes/style`, SEASON.md writes
  `readers review/read-commits notes/release`; `readers` unticked on `notes/release` leaves `readers review/read-commits`,
  notes/style still left out -- the line stays in the file and in `--document` (todo la-ligne-reduite-gardee, A2)
Its siblings: `ui-team-form-season-documents` (the list of the season's documents, the preset's line locked).
"""
from __future__ import annotations

from tests.harness import support

F = support(__file__, "team_forms")
D = support(__file__, "documents")
T = F.T

TICKED = f"S,{F.TO_SEASON_DOCUMENTS},down,down,down,enter,{F.FIRST_ROLE},ctrl+enter"    # readers ticked on read-commits
NARROWED = "readers review/read-commits notes/release"        # SEASON.md's line: the preset's notes/style left out
UNTICKED = f"S,{F.TO_SEASON_DOCUMENTS},down,down,enter,{F.FIRST_ROLE},ctrl+enter"     # past the preset's line and its
#                                                                                   separator: notes/release, readers off
KEPT = "team declare core-review --season --document 'readers review/read-commits' --json"


def narrowed() -> dict:
    """-> the script with `seasons/files` giving `{readers} review/read-commits notes/style` and SEASON.md writing
    `NARROWED`: the house's documents of `_documents` listed."""
    templates = [dict(one, documents=[{"key": "{readers}", "documents": ["review/read-commits", "notes/style"]}])
                 if one["template"] == "seasons/files" else one for one in F.TEMPLATES]
    face = F.declaration()
    text = face["season"]["text"].replace("  readers = readers\n", f"  readers = readers\ndocuments: |\n  {NARROWED}\n")
    season = {**face["season"], "text": text}
    return T.script(templates=[D.RELEASE, D.STYLE, *templates], renders=D.RENDERS, sources=D.SOURCES,
                    declarations={**T.DECLARATIONS, "core-review": {**face, "season": season}})


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-form-season-documents-dropped", F.script())

    # --- the key ticked then unticked: no line copies the preset's (s.1608) ------------------------------------------
    untick = f"{TICKED},enter,{F.FIRST_ROLE},ctrl+enter"
    house.clear_journal()
    back = house.render("--render", "teams", *F.SIZE, "--press", f"{untick},ctrl+pagedown,boxes")     # Launch: the file
    house.render("--render", "teams", *F.SIZE, "--press", f"{untick},{F.WRITE}")
    file = F.zone_rows(back.stdout, "form-file")
    if (any("template: seasons/files" in one for one in file)
            and not any("documents:" in one or "readers review/read-files" in one for one in file)
            and not any("--document" in one for one in house.gestures())):
        held("a key of the preset ticked then unticked leaves no line", f"{house.gestures()}; {[one for one in file if one]}")
    else:
        failures.append(f"  ✗ no line copies the preset   {house.gestures()} {file}")

    # --- a line narrowing the preset's, a document unticked: the line stays (A2) ----------------------------------------
    house.use(narrowed())
    house.clear_journal()
    left = house.render("--render", "teams", *F.SIZE, "--press", f"{UNTICKED},ctrl+pagedown,boxes")      # Launch: the file
    house.render("--render", "teams", *F.SIZE, "--press", f"{UNTICKED},{F.WRITE}")
    file = F.zone_rows(left.stdout, "form-file")
    if "documents: |" in file and "readers review/read-commits" in file and house.gestures() == [KEPT]:
        held("a line narrowing the preset's stays once a document is unticked", f"{house.gestures()}")
    else:
        failures.append(f"  ✗ narrowed line kept          {house.gestures()} {[one for one in file if one]}")
    return 0
