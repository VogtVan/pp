"""Scenario `ui-team-form-season-silence-whole` -- the silence of a season's form is a whole number of silent
exchanges, as the launches are (batch le-silence-de-saison-dit, s.1644; cut from `ui-team-form-season-silence` by
case, rule 10), on the bench's `pp-team` witness: `core-review`, SEASON.md without a silence:
- `S`, Launch, the silence: `5m` typed shows `5` -- the field takes digits alone
"""
from __future__ import annotations

from tests.harness import support

F = support(__file__, "team_forms")
T = F.T

TO_SILENCE = F.TO_LAUNCH + ",tab,tab"     # the launch: its budget, its launches, then its silence


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-form-season-silence-whole")
    typed = house.render("--render", "teams", *F.SIZE, "--press", f"S,{TO_SILENCE},5,m,boxes")
    field = F.P.field_of(F.fields(typed.stdout), "silence")
    if field == ["5"]:
        held("the silence takes a whole number", "5m typed: 5")
    else:
        failures.append(f"  ✗ whole number                {field} {typed.stdout[-900:]!r}")
    return 0
