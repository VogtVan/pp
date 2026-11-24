"""Scenario `ui-team-season-verdict` -- a verdict refused stops the start of a season (cut from `ui-team-season-new`,
rule 10), on the bench's witnesses (`_teams`): `core-review`, in its first season, a declaration `start` would refuse
already (`entry-missing`):
- `S` says its verdict in the view by member; `make` ticked on `git/branches` in the list of documents and `ctrl+s`:
  `team declare --season` writes -- the document's line, the context at the form's default -- and its verdict says a
  refusal (`member-held`) -- the remedy line says it and that SEASON.md is written, the form open again on the team,
  no `team start` played
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
F = support(__file__, "team_forms")   # the keys that type, the readers of a form by its zones
P = F.P

DECLARED_ILL = "entry-missing -- teams/core-review/TEAM.md: entries: `nightly` names no task."   # before any call
HELD = "member-held -- teams/core-review/TEAM.md: agents: `reviewer` holds T3, still open."   # what declare writes


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-season-verdict", agents=T.SEASON_AGENTS)

    # --- a verdict refused: said at the opening, and after a declare that writes; no start -------------------------
    ill = {**T.DECLARATIONS["core-review"], "verdict": {"ok": False, "refusal": DECLARED_ILL}}
    house.use(T.script(declarations={**T.DECLARATIONS, "core-review": ill},
                       answers={"declare": {"verdict": {"ok": False, "refusal": HELD}}}))
    house.clear_journal()
    # the list of the season: the preset's line, locked, its separator, then git/branches -- `make` ticked on it; the
    # form open again, its Members show the view by member
    done = house.render("--render", "teams", *T.SEASON_SIZE, "--press",
                        f"S,{F.TO_SEASON_DOCUMENTS},down,down,enter,{F.FIRST_ROLE},ctrl+enter,ctrl+s,{F.TO_LINES},boxes")
    remedy, view = T.remedy_of(done), F.zone_rows(done.stdout, "form-view")
    title = P.title_of(done.stdout) or [""]
    noted = [row for row in view if DECLARED_ILL.split()[0] in row.split()]
    wanted = ["team declare core-review --season --document 'make git/branches' --context 90 --json"]
    if (done.returncode == 0 and house.gestures() == wanted and HELD.split()[0] in remedy.split()
            and "SEASON.md" in remedy.split() and "core-review" in title[0].split() and noted):
        held("a verdict refused stops the start", f"{wanted}; {remedy[-60:]!r}; the form open again, {noted[0]!r}")
    else:
        failures.append(f"  ✗ verdict                     rc={done.returncode} {house.gestures()} {remedy!r} {title} "
                        f"{view} {done.stdout[-1500:]!r} {done.stderr[-300:]!r}")
    return 0
