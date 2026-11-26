"""Scenario `ui-team-form-team-born` -- the form of a team starts nothing and writes a team born (batch
les-formulaires-jumeaux; cut from `ui-team-form-team`, rule 10), on the bench's `pp-team` witness replaying the faces of
team 1.26.0:
- the form of a team has no `ctrl+s`: it plays nothing
- `N`, a name typed: the field schedule says `30s` and the side pane's TEAM.md `schedule: 30s`; `enter` plays `team
  declare <name> --template <the first preset of a team> --schedule 30s --json` -- a team born ticks every 30 s unless
  its schedule is changed (batch le-schedule-a-30s-a-la-creation)
- `E` on `core-review` written with `schedule: 2m`: the field says `2m`, `enter` plays nothing -- nothing changed
- `E` (batch les-volets-par-onglet): the root typed on Members, then on Limits the budget, the launches, the timeout and
  the schedule -- the parallel, between the launches and the timeout, left as it stands --, `enter` plays `team declare
  core-review --root reviewer --budget 7 --launches 9 --timeout 60 --schedule 5m --json` -- each key on its field (todo
  les-cles-root-et-budget)
"""
from __future__ import annotations

from tests.harness import support

F = support(__file__, "team_forms")
T = F.T

BORN = "team declare ram --template teams/solo --schedule 30s --json"
TO_SCHEDULE = F.team_to("Limits") + ",tab,tab,tab,tab"   # Limits: budget, launches, parallel, timeout, schedule
SCHEDULED = {**F.declaration(), "text": F.TEAM_TEXT.replace("budget: 5\n", "budget: 5\nschedule: 2m\n", 1)}
LIMITED = "team declare core-review --root reviewer --budget 7 --launches 9 --timeout 60 --schedule 5m --json"
# Members: the members, then the root; Limits, two sections further: the budget, the launches, the parallel passed over,
# the timeout, the schedule
TYPED = (f"E,{F.team_to('Members')},tab,{F.typed('reviewer')},{F.section(2)},end,backspace,7,tab,9,tab,tab,6,0,tab,5,m,"
         "ctrl+enter")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-form-team-born", F.script())

    # --- ctrl+s on E plays nothing; N: a team born from the first preset of a team ------------------------------------
    house.clear_journal()
    house.render("--render", "teams", *F.SIZE, "--press", "E,ctrl+s,escape,N,r,a,m,ctrl+enter")
    if house.gestures() == [BORN]:
        held("ctrl+s plays nothing on a team's form; N writes a team born", f"ctrl+s: nothing; N: {BORN}")
    else:
        failures.append(f"  ✗ ctrl+s, N                   {house.gestures()}")

    # --- N: the schedule of a team born, 30s, on its field and in TEAM.md --------------------------------------------
    born = house.render("--render", "teams", *F.SIZE, "--press", f"N,r,a,m,{TO_SCHEDULE},boxes")
    shown, file_rows = F.P.field_of(F.fields(born.stdout), "schedule"), F.pane_rows(born.stdout, "form-file")
    if shown == ["30s"] and "schedule: 30s" in file_rows:
        held("a team born opens on schedule 30s", f"{shown}; schedule: 30s in TEAM.md")
    else:
        failures.append(f"  ✗ schedule born               {shown} {file_rows}")

    # --- E on a TEAM.md written with schedule: 2m: the field keeps it, nothing to play -------------------------------
    house.use(T.script(templates=F.TEMPLATES, declarations={**T.DECLARATIONS, "core-review": SCHEDULED}))
    house.clear_journal()
    kept = house.render("--render", "teams", *F.SIZE, "--press", f"E,{TO_SCHEDULE},ctrl+enter,boxes")
    shown = F.P.field_of(F.fields(kept.stdout), "schedule")
    if shown == ["2m"] and house.gestures() == []:
        held("a team that stands keeps its schedule", f"{shown}; enter: nothing played")
    else:
        failures.append(f"  ✗ schedule kept               {shown} {house.gestures()}")
    house.use(F.script())

    # --- E, the root on Members, the limits on Limits ----------------------------------------------------------------
    house.clear_journal()
    house.render("--render", "teams", *F.SIZE, "--press", TYPED)
    if house.gestures() == [LIMITED]:
        held("the root written from Members, the limits from Limits", LIMITED)
    else:
        failures.append(f"  ✗ limits                      {house.gestures()}")
    return 0
