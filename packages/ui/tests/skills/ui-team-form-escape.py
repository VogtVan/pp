"""Scenario `ui-team-form-escape` -- `escape` on the team's form (batch l-echap-qui-garde-la-saisie), cut out of
`ui-team-form-parallel` by case (rule 10), on its house (`_team_form_parallel`): `core-review`, its TEAM.md written with
`parallel: 3`, changed to 2 in the section Limits:
- the form left as it opened closes on `escape`; changed, `escape` asks first (`palette.LEAVE_TYPED`)
- `ctrl+enter` in the confirmation closes the form, nothing played
- `escape` in the confirmation gives the form back, 2 still typed, which `ctrl+enter` then declares
The source of a document typed: `ui-team-form-documents-new`.
"""
from __future__ import annotations

from tests.harness import support

B = support(__file__, "team_form_parallel")
F = B.F
P = F.P


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = B.house(bench, "ui-team-form-escape")

    asked = house.render("--render", "teams", *F.SIZE, "--press", f"{B.PARALLEL},escape,boxes")
    house.clear_journal()
    left = house.render("--render", "teams", *F.SIZE, "--press", f"E,escape,{B.PARALLEL},escape,ctrl+enter,boxes")
    gone = house.gestures()
    if P.asked_to_leave(asked.stdout) and gone == [] and not P.title_of(left.stdout):
        held("escape closes a form as it opened, asks on a form changed", "E, escape: closed, E again; 2 typed, "
             "escape: the confirmation on top; ctrl+enter there: closed, nothing played")
    else:
        failures.append(f"  ✗ escape                      {P.title_of(P.on_top(asked.stdout))} {gone} "
                        f"{P.title_of(left.stdout)}")
    house.clear_journal()
    house.render("--render", "teams", *F.SIZE, "--press", f"{B.PARALLEL},escape,escape,ctrl+enter")
    declared = house.gestures()
    if declared == [B.DECLARED]:
        held("escape in the confirmation gives the form back, ctrl+enter declares", f"{declared}")
    else:
        failures.append(f"  ✗ declared                    {declared}")
    return 0
