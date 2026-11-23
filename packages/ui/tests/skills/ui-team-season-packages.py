"""Scenario `ui-team-season-packages` -- `S` on a team at work, the packages of `all` switched in its profile, on the
bench's witnesses (`_teams`): `core-review`, in its first season -- its declaration (the season SEASON.md writes: its
whole set, `reviewer`'s own), its face (what a member may not switch off, `required`); what plays read from the
witness's journal:
- `steering` switched off on `all`: `--package steering=off` alone, the package changed, never once per member
- `team`, required: drawn in a look of its own in the packages of `all`, the cursor never on it, never composed `off`;
  `plan` switched off on `all`, `reviewer`'s `plan=off` is no change any more: nothing of its packages composed
Its siblings: `ui-team-season-new`, `ui-team-season-member`, `ui-team-season-again`.
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the readers of a capture and of the palette's source


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-season-packages", agents=T.SEASON_AGENTS)

    # --- a switch of `all`, member by member ---------------------------------------------------------------------
    whole = f"S,{T.TO_LINES},enter,{T.TO_PACKAGES},enter,down,enter,ctrl+enter,ctrl+enter"   # steering chosen: toggled
    house.clear_journal()
    done = house.render("--render", "teams", *T.SEASON_SMALL, "--press", whole + ",ctrl+s")
    wanted = "team declare core-review --season --context 90 --package steering=off --json"
    if done.returncode == 0 and house.gestures() == [wanted, T.NEXT]:
        held("steering off on all, in all's set alone", wanted)
    else:
        failures.append(f"  ✗ all switch                  rc={done.returncode} {house.gestures()} {done.stdout[-2500:]!r} "
                        f"{done.stderr[-400:]!r}")

    # --- `team`, required ----------------------------------------------------------------------------------------
    required = f"S,{T.TO_LINES},enter,{T.TO_PACKAGES},enter,down,down,space"   # the second down would stand on `team`
    shown = house.render("--render", "teams", *T.SEASON_SMALL, "--press", required, "--styles")
    top = P.on_top(shown.stdout)
    looks = {name: T.look_of(top, name) for name in ("plan", "steering", "team")}
    house.clear_journal()
    done = house.render("--render", "teams", *T.SEASON_SMALL, "--press", required + ",ctrl+enter,ctrl+enter,ctrl+s")
    # the space lands on `plan`, the cursor past `team`: plan off in all's set, reviewer's plan=off no change
    wanted = "team declare core-review --season --context 90 --package plan=off --json"
    if (shown.returncode == 0 and "team" in T.REQUIRED and all(looks.values())
            and looks["team"] not in (looks["plan"], looks["steering"]) and done.returncode == 0
            and house.gestures() == [wanted, T.NEXT] and "team=off" not in wanted.split()):
        held("team required: greyed, never off", f"its look {looks['team']} beside {looks['steering']}; "
             f"{house.gestures()}")
    else:
        failures.append(f"  ✗ required                    rc={shown.returncode},{done.returncode} {looks} {house.gestures()} "
                        f"{P.ANSI.sub('', top)[-2500:]!r}")
    return 0
