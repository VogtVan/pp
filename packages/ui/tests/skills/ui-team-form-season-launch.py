"""Scenario `ui-team-form-season-launch` -- the launch keys of a season written by `team declare --season` (batch
les-cles-de-lancement-ecrites, s.1648), on the bench's `pp-team` witness:
- `core-review`, its season written with `budget: 2`, `silence: 30m` and `context: 90%`: the budget changed alone,
  `enter` plays `team declare core-review --season --budget 7 --json` -- the limit written without a start
- `core-review` in its first season, SEASON.md without a context: `lead`'s line edited (its model typed, `plan`
  switched off), `ctrl+s` plays `team declare core-review --season --context 90 --member lead --model haiku --package
  plan=off --json` -- the form's context at its default, then the profile --, then `team start core-review` without a
  flag of the season
- the same season left as it is, `enter` on its budget: nothing played, the line of state `NOTHING_CHANGED` -- the
  context at the form's default is no change (A3)
"""
from __future__ import annotations

from tests.harness import support

F = support(__file__, "team_forms")
T, P = F.T, F.P

SEASON = {**T.CORE_SEASON, "limits": {"budget": 2.0, "silence": "30m", "context": "90%"}}
FACE = T.declaration("core-review", [("lead", "agents/lead"), ("reviewer", "agents/reviewer")], {"budget": 1.0},
                     template="teams/supervisor-workers", season=SEASON)
BUDGETED = "team declare core-review --season --budget 7 --json"
MEMBER = f"S,{T.TO_LINES},down,enter,h,a,i,k,u,{T.TO_PACKAGES},enter,space,ctrl+enter,ctrl+enter"
NOTHING = P.palette_constant("NOTHING_CHANGED")
PROFILED = ["team declare core-review --season --context 90 --member lead --model haiku --package plan=off --json",
            "team start core-review --no-tick"]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    limited = T.Teams(bench, "ui-team-form-season-launch", T.script(declarations={**T.DECLARATIONS, "core-review": FACE}))
    limited.render("--render", "teams", *F.SIZE, "--press", f"S,{F.TO_LAUNCH},end,backspace,7,ctrl+enter")
    budgeted = limited.gestures()
    if budgeted == [BUDGETED]:
        held("enter writes the budget changed alone", BUDGETED)
    else:
        failures.append(f"  ✗ budget                      {budgeted}")

    member = T.Teams(bench, "ui-team-form-season-launch-member", agents=T.SEASON_AGENTS)
    left = member.render("--render", "teams", *T.SEASON_SMALL, "--press", f"S,{F.TO_LAUNCH},ctrl+enter,boxes")
    said, untouched = F.state(left.stdout), member.gestures()
    if left.returncode == 0 and untouched == [] and said.split(" -- ")[-1] == NOTHING:    # its reason, after the gap's head
        held("enter on a season left as it is plays nothing", f"{untouched}; {said!r}")
    else:
        failures.append(f"  ✗ left as it is               rc={left.returncode} {untouched} {said!r}")
    member.clear_journal()
    member.render("--render", "teams", *T.SEASON_SMALL, "--press", MEMBER + ",ctrl+s")
    profiled = member.gestures()
    if profiled == PROFILED:
        held("ctrl+s declares the profile, then starts without a flag", " ; ".join(PROFILED))
    else:
        failures.append(f"  ✗ profile                     {profiled}")
    return 0
