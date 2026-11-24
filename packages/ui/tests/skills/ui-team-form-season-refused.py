"""Scenario `ui-team-form-season-refused` -- the refusals of `ctrl+s` in the form of a season (batch
les-formulaires-jumeaux; cut from `ui-team-form-season`, rule 10), on the bench's `pp-team` witness replaying the faces of
team 1.26.0, `all` ticked on `review/read-commits` in the list of the season's documents:
- a `declare --season` refused under `ctrl+s` plays no `start`: the refusal on the remedy line by its code, the form
  open again on its values -- its line of documents -- (taken from `ui-team-new-start`, where TEAM.md's declare stood)
- a `start` refused after SEASON.md written: the refusal and the file written on the remedy line, the form open again
  on the team's season and its values (taken from `ui-team-new-start`)
"""
from __future__ import annotations

from tests.harness import support

F = support(__file__, "team_forms")
T = F.T

DOCUMENT = "all review/read-commits"
# the list of the season: the preset's line, locked, its separator, the package's separator, then review/read-commits
TYPED = f"S,{F.TO_SEASON_DOCUMENTS},down,down,down,enter,{F.ALL},ctrl+enter"
AGAIN = f"ctrl+s,{F.TO_SEASON_DOCUMENTS},boxes"     # the form open again on its values: its list read
DECLARED = "team declare core-review --season --document 'all review/read-commits' --context 90 --json"
STARTED = T.NEXT
REFUSAL = "pp-team: value-missing -- teams/core-review/SEASON.md: `readers` has no default.\n"
STARTLESS = "pp-team: rendered-edited -- teams/core-review/TEAM-core-review-read-files.md was edited by hand.\n"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-form-season-refused", F.script())

    # --- a declare --season refused: no start, the form open again on its values ----------------------------------
    house.use(F.script(answers={"declare --season": {"rc": 2, "err": REFUSAL}}))
    house.clear_journal()
    refused = house.render("--render", "teams", *F.SIZE, "--press", f"{TYPED},{AGAIN}")
    remedy, kept = T.remedy_of(refused), F.role_of(refused.stdout, "review/read-commits")
    if (refused.returncode == 0 and house.gestures() == [DECLARED] and "value-missing" in remedy.split()
            and kept == "all"):
        held("a refused declare --season starts nothing", f"{house.gestures()}; {remedy[:60]!r}; the form open again "
             f"on {DOCUMENT!r}")
    else:
        failures.append(f"  ✗ declare refused             {house.gestures()} {remedy!r} {kept} {refused.stdout[-1500:]!r}")

    # --- a start refused after SEASON.md written: what is written said, the form open again -----------------------
    house.use(F.script(answers={"start": {"rc": 2, "err": STARTLESS}}))
    house.clear_journal()
    unstarted = house.render("--render", "teams", *F.SIZE, "--press", f"{TYPED},{AGAIN}")
    remedy, kept = T.remedy_of(unstarted), F.role_of(unstarted.stdout, "review/read-commits")
    wanted = [DECLARED, STARTED]
    if (unstarted.returncode == 0 and house.gestures() == wanted and "rendered-edited" in remedy.split()
            and "SEASON.md" in remedy.split() and kept == "all"):
        held("a refused start after SEASON.md written", f"{wanted}; {remedy[-60:]!r}; the form open again on its values")
    else:
        failures.append(f"  ✗ start refused               {house.gestures()} {remedy!r} {kept} "
                        f"{unstarted.stdout[-1500:]!r}")
    return 0
