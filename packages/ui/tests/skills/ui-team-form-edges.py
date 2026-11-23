"""Scenario `ui-team-form-edges` -- the edges written from the form of TEAM.md (batch les-formulaires-jumeaux, team
1.27.0, cut from `ui-team-form-word`, rule 10), on the bench's `pp-team` witness, `core-review` off season, its TEAM.md
with one edge `reviewer -> lead`:
- an edge typed in Members (batch les-volets-par-onglet): `team declare core-review --report 'scribe -> lead'` -- an
  edge goes by the member it reports to; the edge taken out: `--no-report lead`
- an edge rewritten as pp-team writes it: `ui-team-form-edges-named` (cut by case, rule 10)
"""
from __future__ import annotations

from tests.harness import support

F = support(__file__, "team_forms")
W = support(__file__, "team_form_word")
T = F.T

TO_REPORTS = F.team_to("Members") + ",tab,tab,tab"     # Members: the members, the root, the principals, the edges
OUT = F.WRITE                      # from the edges themselves: `ctrl+enter` writes from any field


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-form-edges", T.script(declarations={**T.DECLARATIONS, "core-review": W.EDGED}))

    # --- the edges: one added beside the one TEAM.md writes, then that one taken out ---------------------------------
    house.render("--render", "teams", *F.SIZE, "--press", f"E,{TO_REPORTS},end,enter," + F.typed("scribe -> lead") + f",{OUT}")
    added = house.gestures()
    house.clear_journal()
    house.render("--render", "teams", *F.SIZE, "--press", f"E,{TO_REPORTS},shift+end,backspace,{OUT}")
    wanted = [["team declare core-review --report 'scribe -> lead' --json"], ["team declare core-review --no-report lead --json"]]
    if [added, house.gestures()] == wanted:
        held("an edge written, an edge taken out", f"{wanted}")
    else:
        failures.append(f"  ✗ edges                       {added} {house.gestures()}")

    return 0
