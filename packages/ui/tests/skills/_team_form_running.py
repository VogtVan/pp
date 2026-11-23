"""_team_form_running -- what `ui-team-form-running` and `ui-team-form-running-panes` share (rule 10): `core-review` in
season (`started.state` `running` in `team declaration --json`), its open tasks T3 and T6, its live recurrence R1."""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

RUNNING = T.declaration("core-review", [("lead", "agents/lead"), ("reviewer", "agents/reviewer")], {"budget": 1.0},
                        template="teams/supervisor-workers", roles=(("make", ["lead"]),), season=T.CORE_SEASON,
                        running=True)
STATE = T.RECURRING


def script() -> dict:
    return T.script(declarations={**T.DECLARATIONS, "core-review": RUNNING},
                    states={"core-review": [STATE], "ops": [T.OPS]})
