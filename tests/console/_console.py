"""Support module of `tests/console/` (rule 10): what the console hosts share -- the door a
launcher names above the boot, its witness member and the sibling it calls, the key of the
run an instance holds. Never collected; a host loads it by `support(__file__, "console")`.
"""
from __future__ import annotations

from pathlib import Path

from tests.harness import session_of

DOOR = {"PP_DOOR": "AGENT.md"}      # the witness, opened above the boot at every -new

WITNESS = """---
name: AGENT
kind: proc
description: the witness the console's verbs are exercised on
constraints.production: |
  W1  the witness produces what the step names, nothing else.
tools: |
  CAPABILITIES
proc: |
  WORK
  CALL LISTER.md
  PICK one
  WORK
  FINAL
---

the witness member.
"""

LISTER = """---
name: LISTER
kind: proc
description: hands a list downstream
output: json
proc: |
  INFER
---

the siblings
"""


def key_of(made: Path) -> str:
    """-> the key of the run the instance `made` holds, read from its slot's name."""
    return session_of(made).name[len("session-"):-len(".json")]
