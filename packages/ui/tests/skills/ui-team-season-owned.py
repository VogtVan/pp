"""Scenario `ui-team-season-owned` -- the owner's own line of documents, in the form of TEAM.md, and a SEASON.md
without a season (cut from `ui-team-season-again`, rule 10), on the bench's witnesses (`_teams`); what plays read from
the witness's journal:
- on the owner's `core-review` (`OWNED`: its own line of documents `all git/trunk`, SEASON.md writing no season): `E`
  shows TEAM.md with its members, its role and that line; the line `all` of `S` on the launch of the season under way;
  the line changed in the list of documents (`all` ticked on `git/branches`, taken off `git/trunk`) plays `team
  declare core-review --document 'all git/branches'`; `all` taken off `git/trunk` alone, `--no-document all`, and
  the form of the season left as it is then declares the context at the form's default (`team declare core-review
  --season --context 90`) and starts the season: `team start core-review` with no flag
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
F = support(__file__, "team_forms")    # the readers of a form by its zones, the keys that type

TO_DOCUMENTS = F.team_to("Documents")    # in the form of a team: Documents -- its list: git/branches under the
#                                          cursor, then git/trunk


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-season-owned", T.script(declarations={**T.DECLARATIONS, "core-review": T.OWNED}),
                    agents=T.SEASON_AGENTS)

    # --- the owner's own line of documents and a SEASON.md without a season -----------------------------------------
    team = house.render("--render", "teams", *T.SEASON_SIZE, "--press", "E,boxes")
    file = F.zone_rows(team.stdout, "form-file")
    owned = T.OWNED["declared"]
    lines = ([f"{one['member']} {one['path']}" for one in owned["agents"]]
             + [" ".join([one["role"], *one["members"]]) for one in owned["roles"]] + ["all git/trunk"])
    shown = house.render("--render", "teams", *T.SEASON_SIZE, "--press", f"S,{T.TO_LINES},boxes")
    whole = T.season_line(shown.stdout, "all", "—")
    launch = [T.LAUNCH["provider"], T.LAUNCH["model"], T.LAUNCH["effort"]]
    if team.returncode == 0 and shown.returncode == 0 and all(one in file for one in lines) and whole[2:5] == launch:
        held("E shows TEAM.md, its own line; S the season under way", f"{lines}; all {whole}")
    else:
        failures.append(f"  ✗ own line shown              rc={team.returncode},{shown.returncode} {file} {whole}")
    house.clear_journal()
    other = house.render("--render", "teams", *T.SEASON_SMALL, "--press",
                         f"E,{TO_DOCUMENTS},enter,{F.ALL},ctrl+enter,down,enter,{F.ALL},ctrl+enter,{F.WRITE}")
    changed = house.gestures()
    house.clear_journal()
    blank = house.render("--render", "teams", *T.SEASON_SMALL, "--press",
                         f"E,{TO_DOCUMENTS},down,enter,{F.ALL},ctrl+enter,{F.WRITE},S,ctrl+s")
    wanted = [["team declare core-review --document 'all git/branches' --json"],
              ["team declare core-review --no-document all --json", T.NEXT_DECLARED, T.NEXT]]
    if other.returncode == 0 and blank.returncode == 0 and [changed, house.gestures()] == wanted:
        held("the team's own line changed, then taken out", f"{wanted}")
    else:
        failures.append(f"  ✗ own line                    rc={other.returncode},{blank.returncode} {changed} "
                        f"{house.gestures()} {blank.stdout[-1500:]!r} {blank.stderr[-300:]!r}")
    return 0
