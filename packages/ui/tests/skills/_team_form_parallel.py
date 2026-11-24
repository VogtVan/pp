"""_team_form_parallel -- what `ui-team-form-parallel` and `ui-team-form-escape` share (rule 10): `core-review` off
season, its TEAM.md written with `parallel: 3`, and the keys that change it to 2 in the section Limits of its form."""
from __future__ import annotations

from tests.harness import support

F = support(__file__, "team_forms")

BOUND = {**F.declaration(), "text": F.TEAM_TEXT.replace("budget: 5\n", "budget: 5\nparallel: 3\n", 1)}
TO_PARALLEL = F.team_to("Limits") + ",tab,tab"   # Limits: its budget, its launches, then its parallel
PARALLEL = f"E,{TO_PARALLEL},end,backspace,{F.typed('2')}"
DECLARED = "team declare core-review --parallel 2 --json"


def house(bench, name: str):
    """-> the house of the case `name`: the bench's `pp-team` witness, `core-review` written with `parallel: 3`."""
    return F.T.Teams(bench, name, F.T.script(templates=F.TEMPLATES, declarations={**F.T.DECLARATIONS, "core-review": BOUND}))
