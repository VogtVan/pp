"""_team_form_word -- what `ui-team-form-word` and `ui-team-form-edges` share (rule 10): `core-review` off season, its
TEAM.md with one edge `reviewer -> lead` and a body."""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

EDGED = T.declaration("core-review", [("lead", "agents/lead"), ("reviewer", "agents/reviewer"),
                                      ("scribe", "agents/scribe")], {"budget": 1.0},
                      template="teams/supervisor-workers", roles=(("make", ["lead"]),), season=T.CORE_SEASON,
                      reports=("reviewer -> lead",), body="The owner's word.\n")
