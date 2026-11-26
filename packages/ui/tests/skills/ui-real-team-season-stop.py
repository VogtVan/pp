"""Scenario `ui-real-team-season-stop` -- a season stopped from the post on the REAL verbs of `team` (team 1.27.0, cut
from `ui-real-team-season-next`, rule 10): `essai`, its first season started by the console without a task, the witness
as its harness:
- `S` in season opens the form read only; `X` and the team's name typed play `team stop`: the journal's
  `season-stopped`, the face off season
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real_team")
SIZE = ("--size", "200x60")
STOP = f"S,X,{','.join(R.TEAM)},ctrl+enter"   # in season: the form read only, X, the team's name typed


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    team = R.RealTeam(bench, "ui-real-team-season-stop", {})
    begun = team.call("team", "start", R.TEAM, *team.harnessed, "--no-tick")
    team.settled(lambda events: any(one.get("kind") == "team-started" for one in events))

    # --- S in season: read only; X stops the season ------------------------------------------------------------------
    halted = team.render("--render", "teams", *SIZE, "--press", STOP)
    stopped = team.kinds("season-stopped")
    if begun.returncode == 0 and halted.returncode == 0 and len(stopped) == 1 and team.state().get("season", {}).get("state") == "stopped":
        held("S in season stops it from its form", f"season-stopped #{stopped[0].get('id')}, the face off season")
    else:
        failures.append(f"  ✗ stopped                     rc={halted.returncode} {stopped} {team.state().get('season')} "
                        f"{halted.stdout[-1500:]!r} {halted.stderr[-300:]!r}")

    return 0
