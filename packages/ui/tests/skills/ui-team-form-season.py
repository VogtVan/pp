"""Scenario `ui-team-form-season` -- the form of a season writes SEASON.md by `team declare --season` and starts it
(batch les-formulaires-jumeaux), on the bench's `pp-team` witness replaying the faces of team 1.26.0:
- `S` on `core-review`, its documents: `all` ticked on `review/read-commits` in the list (batch
  la-liste-des-documents) shows in the side pane of Launch, in SEASON.md's block (batch les-volets-par-onglet) -- the
  view by member is `ui-team-form-view`'s
- `enter` plays `team declare core-review --season --document … --json`, nothing else
- `ctrl+s` plays it with `--context 90` -- the season's context, empty in SEASON.md, at the form's default --, then
  `team start core-review` without a flag of the season
The refusals of `ctrl+s`: `ui-team-form-season-refused` (cut by case, rule 10).
"""
from __future__ import annotations

from tests.harness import support

F = support(__file__, "team_forms")
T = F.T

DOCUMENT = "all review/read-commits"
# the list of the season: the preset's line, locked, its separator, the package's separator, then review/read-commits
TYPED = f"S,{F.TO_SEASON_DOCUMENTS},down,down,down,enter,{F.ALL},ctrl+enter"
DECLARED = "team declare core-review --season --document 'all review/read-commits' --json"
STARTED = [DECLARED.replace(" --json", " --context 90 --json"), T.NEXT]   # the context at its default


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-form-season", F.script())

    # --- the side pane of Launch: SEASON.md as it will be written ------------------------------------------------------
    shown = house.render("--render", "teams", *F.SIZE, "--press", f"{TYPED},ctrl+pagedown,boxes")
    file_rows = F.pane_rows(shown.stdout, "form-file")
    if shown.returncode == 0 and DOCUMENT in file_rows and "template: seasons/files" in file_rows:
        held("the side pane of Launch follows the fields", f"{DOCUMENT!r} in SEASON.md")
    else:
        failures.append(f"  ✗ side pane                   rc={shown.returncode} {file_rows} "
                        f"{shown.stdout[-1500:]!r} {shown.stderr[-300:]!r}")

    # --- enter writes SEASON.md; ctrl+s writes it, then starts ---------------------------------------------------------
    house.clear_journal()
    house.render("--render", "teams", *F.SIZE, "--press", f"{TYPED},{F.WRITE}")
    written = house.gestures()
    house.clear_journal()
    house.render("--render", "teams", *F.SIZE, "--press", f"{TYPED},ctrl+s")
    started = house.gestures()
    if written == [DECLARED] and started == STARTED:
        held("enter writes SEASON.md, ctrl+s writes then starts", f"{DECLARED}; then {STARTED}")
    else:
        failures.append(f"  ✗ enter, ctrl+s               {written} {started}")

    return 0
