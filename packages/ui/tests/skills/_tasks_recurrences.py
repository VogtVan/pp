"""_tasks_recurrences -- what the scenarios of the overlay `e` of the Tasks tab share (rule 10): `core-review` carrying
three recurrences -- `R1`, `R2` stopped, `R3` whose occurrence T8 is the task under the cursor -- and the stop `x`
plays on `R3`."""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

R1, R2 = T.RECURRENCES
R3 = {**R1, "id": "R3", "name": "veille", "text": "watch the gateway", "to": "reviewer",
      "last": {"period": "2026-10-10", "task": "T8", "state": "open"}}
T8 = {**T.T6, "id": "T8", "name": "veille 2026-10-10 09:40", "text": "watch the gateway", "recurrence": "R3",
      "at": "2026-10-10T09:40:00+00:00", "holders": ["reviewer"], "to": "reviewer"}
THREE = {**T.RECURRING, "tasks": T.RECURRING["tasks"] + [T8], "recurrences": [R1, R2, R3]}
DELETED = "team stop core-review --recurrence R3 --no-tick"
