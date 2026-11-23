"""Scenario `ui-team-form-limits` -- the silence and the context of a season open on SEASON.md and reach `team declare
--season` only changed, as its budget does (batch les-formulaires-jumeaux, decision of 12/11 22:00), on the bench's `pp-team`
witness: `core-review`, its season written with `silence: 3` (silent exchanges) and `context: 90%` -- the context as `team start`
writes it, in percent (batch les-reglages-des-formulaires, todo le-context-en-pourcent):
- `S`: the field silence (Launch) shows 3, the field context (Members) 90 -- SEASON.md's, read in percent
- `ctrl+s` with nothing changed: `team start core-review` alone, no declare -- `90` is `90%`
- the silence changed to 5: `team declare core-review --season --silence 5`, then the start without a flag
"""
from __future__ import annotations

from tests.harness import support

F = support(__file__, "team_forms")
T, P = F.T, F.P

SEASON = {**T.CORE_SEASON, "limits": {"budget": 2.0, "silence": 3, "context": "90%"}}
FACE = T.declaration("core-review", [("lead", "agents/lead"), ("reviewer", "agents/reviewer")], {"budget": 1.0},
                     template="teams/supervisor-workers", season=SEASON)
TO_SILENCE = F.section(2) + ",tab,tab"        # the launch: its budget, its launches, then its silence
SILENCED = ["team declare core-review --season --silence 5 --json", "team start core-review --no-tick"]
LEFT = "team start core-review --no-tick"     # SEASON.md's limits as they stand: no flag


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-form-limits", T.script(declarations={**T.DECLARATIONS, "core-review": FACE}))

    launch = house.render("--render", "teams", *F.SIZE, "--press", f"S,{F.TO_LAUNCH},boxes")
    members = house.render("--render", "teams", *F.SIZE, "--press", f"S,{F.TO_LINES},boxes")
    opened = {"silence": P.field_of(F.fields(launch.stdout), "silence"),
              "context": P.field_of(F.fields(members.stdout), "context")}
    house.clear_journal()
    house.render("--render", "teams", *F.SIZE, "--press", "S,ctrl+s")
    left = house.gestures()
    house.clear_journal()
    house.render("--render", "teams", *F.SIZE, "--press", f"S,{TO_SILENCE},end,backspace,5,ctrl+s")
    changed = house.gestures()
    if opened == {"silence": ["3"], "context": ["90"]}:
        held("silence and context open on SEASON.md", f"{opened}")
    else:
        failures.append(f"  ✗ opened                      {opened}")
    if left == [LEFT] and changed == SILENCED:
        held("only a changed limit reaches the start", f"{left}; {changed}")
    else:
        failures.append(f"  ✗ start                       {left} {changed}")
    return 0
