"""Scenario `ui-team-season-member` -- `S` on a team at work, a member's line edited in its profile, on the bench's
witnesses (`_teams`): `core-review`, in its first season -- its declaration (`team declaration --json`: the season
SEASON.md writes, `reviewer` on its own model and set; `scribe` added) --; what plays read from the witness's
journal, no command on screen:
- a member edited in its profile composes its own `--member` and nothing else: its model typed, `plan` switched off
- its line's packages drawn as those of `reviewer`, whose face says `plan=off`; `scribe`, declared, plays `all`'s
Its siblings: `ui-team-season-new`, `ui-team-season-packages`, `ui-team-season-again`.
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the readers of a capture and of the palette's source

AS_ALL = P.palette_constant("AS_ALL")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-season-member", agents=T.SEASON_AGENTS)

    member = f"S,{T.TO_LINES},down,enter,h,a,i,k,u,{T.TO_PACKAGES},enter,space,ctrl+enter,ctrl+enter"
    shown = house.render("--render", "teams", *T.SEASON_SMALL, "--press", member + ",boxes")
    lead = T.season_line(shown.stdout, "lead", "agents/lead")
    reviewer = T.season_line(shown.stdout, "reviewer", "agents/reviewer")
    scribe = T.season_line(shown.stdout, "scribe", "agents/scribe")
    house.clear_journal()
    done = house.render("--render", "teams", *T.SEASON_SMALL, "--press", member + ",ctrl+s")
    wanted = ["team declare core-review --season --context 90 --member lead --model haiku --package plan=off --json",
              T.NEXT]
    if (done.returncode == 0 and house.gestures() == wanted and "./pp" not in shown.stdout
            and lead[3:4] == ["haiku"]):
        held("a member edited composes its own --member", wanted[0])
    else:
        failures.append(f"  ✗ member edited               rc={shown.returncode},{done.returncode} {lead} "
                        f"{house.gestures()} {shown.stdout[-2500:]!r} {done.stderr[-400:]!r}")
    if (shown.returncode == 0 and lead and reviewer and lead[-1] == reviewer[-1] != AS_ALL and scribe[-1:] == [AS_ALL]
            and done.returncode == 0 and house.gestures() == wanted):
        held("plan off on a member's line", f"lead {lead[-1]!r} as reviewer's; {wanted}")
    else:
        failures.append(f"  ✗ member switch               {lead} {reviewer} {scribe} {house.gestures()}")
    return 0
