"""Scenario `ui-team-form-season-documents` -- the list of documents of the season's form, on the bench's `pp-team`
witness replaying the faces of team 1.26.0: `core-review`, its SEASON.md on the preset `seasons/files` (cut from
`ui-team-form-season-tabs`):
- Documents lists the season's documents alone (batch la-liste-des-documents): the line the preset `seasons/files`
  gives -- `review/read-files` to its role `readers` -- locked (`= readers`), never the team's line of the same document
  (`all`); `enter` on it changes nothing, the line of state says why
- `readers`, a key the preset gives, ticked on `review/read-commits`: the line SEASON.md writes for it takes the
  preset's documents with it -- `--document 'readers review/read-files review/read-commits'` -- and `review/read-files`
  stays shown locked (todo le-preset-garde-ses-lignes)
Its siblings: `ui-team-form-season-tabs` (the sections of the season's form), `ui-team-form-documents` (the list of
the team's form), `ui-team-form-season-documents-dropped` (a line equal to the preset's, cut from this one).
"""
from __future__ import annotations

from tests.harness import support

F = support(__file__, "team_forms")
T = F.T

KEPT = "team declare core-review --season --document 'readers review/read-files review/read-commits' --json"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-form-season-documents", F.script())

    # --- Documents: the season's documents, the preset's line locked ------------------------------------------------
    house.clear_journal()
    listed = house.render("--render", "teams", *F.SIZE, "--press", f"S,{F.TO_SEASON_DOCUMENTS},enter,boxes")
    rows = F.document_rows(listed.stdout)
    if (rows[:1] == [["review/read-files", "= readers"]] and F.role_of(listed.stdout, "review/read-commits") == "—"
            and ["review/read-files", "all"] not in rows and "seasons/files" in F.state(listed.stdout)
            and house.gestures() == []):
        held("the season's documents, the preset's line locked", f"{rows}; {F.state(listed.stdout)[:60]!r}")
    else:
        failures.append(f"  ✗ season's documents          {rows} {F.state(listed.stdout)!r} {house.gestures()} "
                        f"{listed.stdout[-1500:]!r}")

    # --- a key of the preset ticked: its line keeps the preset's documents, still locked ------------------------------
    ticked = f"S,{F.TO_SEASON_DOCUMENTS},down,down,down,enter,{F.FIRST_ROLE},ctrl+enter"    # the preset's line, its
    #                                                                                     separators, read-commits
    house.clear_journal()
    kept = house.render("--render", "teams", *F.SIZE, "--press", f"{ticked},boxes")
    house.render("--render", "teams", *F.SIZE, "--press", f"{ticked},{F.WRITE}")
    rows = F.document_rows(kept.stdout)
    if (house.gestures() == [KEPT] and rows[:1] == [["review/read-files", "= readers"]]
            and F.role_of(kept.stdout, "review/read-commits") == "readers"):
        held("a key of the preset ticked keeps the preset's documents", f"{KEPT}; {rows[:1]}")
    else:
        failures.append(f"  ✗ preset's line kept          {house.gestures()} {rows}")
    return 0
