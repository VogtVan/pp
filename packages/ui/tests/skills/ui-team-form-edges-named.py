"""Scenario `ui-team-form-edges-named` -- an edge of `reports:` named and written as pp-team names and writes it (batch
les-formulaires-jumeaux, decision of 12/11 22:00; cut from `ui-team-form-edges`, rule 10), on the bench's `pp-team`
witness, `core-review` off season, its TEAM.md with one edge `reviewer -> lead`:
- an edge rewritten with blanks of its own: the side pane -- of Preset, beside Members -- writes it as pp-team does,
  `reviewer scribe -> lead`, in place of the line to the same member; `--report 'reviewer scribe -> lead'`
"""
from __future__ import annotations

from tests.harness import support

F = support(__file__, "team_forms")
W = support(__file__, "team_form_word")
T = F.T

TO_REPORTS = F.team_to("Members") + ",tab,tab,tab"     # Members: the members, the root, the principals, the edges


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-form-edges-named", T.script(declarations={**T.DECLARATIONS, "core-review": W.EDGED}))

    # --- an edge rewritten: named and written as pp-team writes it -----------------------------------------------------
    odd = f"E,{TO_REPORTS},shift+end,backspace," + F.typed("reviewer") + ",space,space,space," + F.typed("scribe ->") \
        + ",space,space," + F.typed("lead")
    house.clear_journal()
    shown = house.render("--render", "teams", *F.SIZE, "--press", f"{odd},ctrl+pageup,boxes")    # Preset: the file
    file = F.zone_rows(shown.stdout, "form-file")
    house.render("--render", "teams", *F.SIZE, "--press", f"{odd},ctrl+pagedown,{F.WRITE}")
    wanted = ["team declare core-review --report 'reviewer scribe -> lead' --json"]
    at = file.index("reports: |") if "reports: |" in file else -1
    if file[at + 1:at + 2] == ["reviewer scribe -> lead"] and house.gestures() == wanted:
        held("an edge named and written as pp-team writes it", f"{file[at:at + 2]}; {wanted[0]}")
    else:
        failures.append(f"  ✗ edge written                {file} {house.gestures()}")
    return 0
