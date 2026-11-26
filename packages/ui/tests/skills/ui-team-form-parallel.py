"""Scenario `ui-team-form-parallel` -- the bound `parallel:` of TEAM.md in the section Limits of the team's form (batch
le-parallel-au-formulaire), cut out of `ui-team-form-limits` by case (rule 10), on the bench's `pp-team` witness:
`core-review`, its TEAM.md written with `parallel: 3` (`_team_form_parallel`):
- `E`, Limits: the field parallel, after the launches, shows 3
- changed to 2: the side pane shows `parallel: 2`; `ctrl+enter` plays `team declare core-review --parallel 2 --json` alone
What `escape` does on the form changed: `ui-team-form-escape`.
"""
from __future__ import annotations

from tests.harness import support

B = support(__file__, "team_form_parallel")
F = B.F
P = F.P


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = B.house(bench, "ui-team-form-parallel")

    limits = house.render("--render", "teams", *F.SIZE, "--press", f"E,{B.TO_PARALLEL},boxes")
    typed = house.render("--render", "teams", *F.SIZE, "--press", f"{B.PARALLEL},boxes")
    shown = P.field_of(F.fields(limits.stdout), "parallel")
    file_rows = F.pane_rows(typed.stdout, "form-file")
    if shown == ["3"] and "parallel: 2" in file_rows:
        held("parallel opens on TEAM.md", f"{shown}; changed: parallel: 2 in the file")
    else:
        failures.append(f"  ✗ opened                      {shown} {file_rows} {limits.stdout[-1200:]!r}")
    house.clear_journal()
    house.render("--render", "teams", *F.SIZE, "--press", f"{B.PARALLEL},ctrl+enter")
    declared = house.gestures()
    if declared == [B.DECLARED]:
        held("ctrl+enter declares the parallel changed", f"{declared}")
    else:
        failures.append(f"  ✗ declared                    {declared}")
    return 0
