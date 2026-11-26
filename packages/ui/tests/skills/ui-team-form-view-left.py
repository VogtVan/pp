"""Scenario `ui-team-form-view-left` -- the view by member left as it stands when nothing asks another (batch
les-formulaires-jumeaux, cut from `ui-team-form-view`), on the bench's `pp-team` witness (`_team_form_view`):
- `E` shows the same view as `S` at its opening, on its Members (batch les-volets-par-onglet)
- `E` on a TEAM.md whose body stands after a blank line asks no view at its opening: the text as it will be written is
  the file as it stands
- the candidate refused: its refusal goes to the line of state, the view left as it stood
"""
from __future__ import annotations

from tests.harness import support

V = support(__file__, "team_form_view")
F = V.F


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = V.T.Teams(bench, "ui-team-form-view-left", V.script())

    house.clear_journal()
    team = house.render("--render", "teams", *F.SIZE, "--press", "E,rest:1,boxes")
    viewed = house.render("--render", "teams", *F.SIZE, "--press", f"E,{F.team_to('Members')},rest:1,boxes")
    asked = V.asked(house)
    view = F.zone_rows(viewed.stdout, "form-view")
    if V.opening(view):
        held("E shows the same view", f"reviewer: {V.ROLE_DOC}")
    else:
        failures.append(f"  ✗ E view                      {view}")
    if not asked and "The owner's word." in " ".join(F.zone_rows(team.stdout, "form-file")):
        held("a body after a blank line: E asks no view at its opening", "the file shown as it stands")
    else:
        failures.append(f"  ✗ blank line                  {asked} {F.state(team.stdout)!r} "
                        f"{F.zone_rows(team.stdout, 'form-file')}")

    # --- the candidate refused: the refusal on the line of state, the view left as it stood -----------------------
    house.use(V.script(candidate_refusal=V.REFUSAL))
    refused = house.render("--render", "teams", *F.SIZE, "--press", f"S,{V.TICK},rest:1,{V.TO_VIEW},boxes")
    if "role-unknown" in F.state(refused.stdout).split() and V.opening(F.zone_rows(refused.stdout, "form-view")):
        held("a candidate refused: said, the view left", F.state(refused.stdout)[:80])
    else:
        failures.append(f"  ✗ refused                     {F.state(refused.stdout)!r} "
                        f"{F.zone_rows(refused.stdout, 'form-view')}")
    return 0
