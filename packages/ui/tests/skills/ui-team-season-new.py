"""Scenario `ui-team-season-new` -- `E` on a team at work changes the team, on the bench's witnesses (`_teams`):
`core-review`, in its first season -- its declaration (`team declaration --json`: its members, its role `make`, its
season's preset `seasons/files`, the season SEASON.md writes) --; what plays read from the witness's journal, no command
on screen:
- `E`, a member and a role added: `team declare core-review --member c agents/c --role watch c` alone -- no flag for a
  field left as it opened, no start: the form of a team starts nothing
Its siblings, cut by case (rule 10): `ui-team-season-preset` (another preset of the season, then the season),
`ui-team-season-verdict` (a verdict refused stops the start), `ui-team-season-member` (a member's line edited),
`ui-team-season-packages` (the packages of `all`), `ui-team-season-kept` (what the verb cannot write),
`ui-team-season-again` (the form on the files, nothing changed, and the refusals).
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
F = support(__file__, "team_forms")   # the keys that type, the readers of a form by its zones


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-season-new", agents=T.SEASON_AGENTS)

    # --- E: a member and a role added, TEAM.md alone written ----------------------------------------------------------
    added = ",".join(["E,tab,end,enter," + F.typed("watch c"), F.team_to("Members"),      # the roles on Team
                      "down,down,end,enter," + F.typed("c agents/c"), "ctrl+pageup,ctrl+pageup,ctrl+enter"])  # Team's line writes
    house.clear_journal()
    done = house.render("--render", "teams", *T.SEASON_SMALL, "--press", added)
    wanted = ["team declare core-review --member c agents/c --role watch c --json"]
    if done.returncode == 0 and house.gestures() == wanted:
        held("E: a member and a role added, TEAM.md alone", f"{wanted}")
    else:
        failures.append(f"  ✗ member and role             rc={done.returncode} {house.gestures()} {done.stdout[-2500:]!r} "
                        f"{done.stderr[-400:]!r}")

    return 0
