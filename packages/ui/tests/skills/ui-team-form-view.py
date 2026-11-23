"""Scenario `ui-team-form-view` -- the view by member of the season's form is pp-team's, never the post's (batch
les-formulaires-jumeaux, decision of 12/11 22:00), on the bench's `pp-team` witness (`_team_form_view`):
- `S` shows `declared.views`: `reviewer` reads the preset's document of its role, `lead` does not
- `all` ticked on `git/branches` in the list (batch la-liste-des-documents), then ticked off, in the same overlay: the text is the one the view shown is of -- no call, the line of
  state says nothing is being made
- `all` ticked: once the keys pause, `team declaration core-review --text-file - --season --json` is played on the
  text as it will be written -- ONE call for the keys typed -- and the view is the one it says (`candidates`: the new
  line's document for `lead`)
Its refusal, and `E`, are `ui-team-form-view-left`'s.
"""
from __future__ import annotations

from tests.harness import support

V = support(__file__, "team_form_view")
F = V.F


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = V.T.Teams(bench, "ui-team-form-view", V.script())
    pending = V.constant("VIEW_PENDING")

    # `S`, a line typed then taken back before the keys pause: the view of the opening, nothing being made
    opened = house.render("--render", "teams", *F.SIZE, "--press", f"S,{V.UNTICKED},{V.TO_VIEW},boxes")
    house.clear_journal()
    rested = house.render("--render", "teams", *F.SIZE, "--press",
                          f"S,{V.UNTICKED},rest:1,{V.TO_VIEW},boxes")
    back = V.asked(house)
    house.clear_journal()
    typed = house.render("--render", "teams", *F.SIZE, "--press", f"S,{V.TICK},rest:1,{V.TO_VIEW},boxes")
    asked = V.asked(house)
    views = [F.zone_rows(one.stdout, "form-view") for one in (opened, rested, typed)]
    if V.opening(views[0]):
        held("S shows pp-team's view by member", f"reviewer: {V.ROLE_DOC}; lead not")
    else:
        failures.append(f"  ✗ view opened                 {views[0]} {F.state(opened.stdout)!r}")
    if (pending not in F.state(opened.stdout) and not back and pending not in F.state(rested.stdout)
            and V.opening(views[1])):
        held("a line taken back before the pause: no call, nothing being made", f"state {F.state(rested.stdout)!r}")
    else:
        failures.append(f"  ✗ taken back                  {F.state(opened.stdout)!r} {back} "
                        f"{F.state(rested.stdout)!r}")
    if (len(asked) == 1 and V.LINE in asked[0] and asked[0].startswith(V.ASKED + " --season")
            and V.LINE_DOC in V.member(views[2], "lead") and V.ROLE_DOC in V.member(views[2], "reviewer")):
        held("a line typed: the view pp-team says of the text typed, one call",
             f"{asked[0][:70]}…; lead: {V.LINE_DOC}")
    else:
        failures.append(f"  ✗ view of the text typed      {asked} {views[2]} {F.state(typed.stdout)!r}")
    return 0
