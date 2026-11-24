"""Support of the scenarios `team-role-documents*` (rule 10): the house of the documents of a role -- the shelf of
`_templates.py` laid, the team `rd` declared (`ma` holds `make`, `mi` `inspect`, `mb` both, `mn` none) under
`SEASON.md` naming the preset `seasons/split` -- and the readings the scenarios share; loaded by `support(__file__, "roles")`, never
collected as a scenario."""
from __future__ import annotations

import os
import re
import subprocess
import sys

from conductor import context
from tests.harness import support

T = support(__file__, "team")
S = support(__file__, "templates")
TITLE = re.compile(r"^▌ INFORMATION — (.+)$", re.M)
DONE = {"sleep": 0.1, "body": {"done": "ok"}}
RD = ("---\nagents: |\n  ma agents/ma\n  mi agents/mi\n  mb agents/mb\n  mn agents/mn\nroot: ma\n"
      "roles: |\n  make ma mb\n  inspect mi mb\nschedule: off\n---\nHold the roles.\n")


def titles(prompt: str) -> list[str]:
    return TITLE.findall(prompt)


def section(prompt: str, name: str) -> str:
    """-> the last `▌ <name>` section of a prompt, up to the next section."""
    at = prompt.rfind(f"\n▌ {name}\n")
    if at < 0:
        return ""
    end = prompt.find("\n▌ ", at + 2)
    return prompt[at + 1:end if end >= 0 else len(prompt)]


def declared(h) -> None:
    """The house's shelf laid and the team `rd` declared under `SEASON.md` naming `seasons/split`."""
    S.laid(h.house / "teams" / "templates", S.SHELF)
    h.declare("rd", RD)
    (h.teams / "rd" / "SEASON.md").write_text("---\ntemplate: seasons/split\n---\n", encoding="utf-8")


def script(h, verb: str, *args: str, path: str, run: str = "", stdin: str | None = None):
    """`pp-team <verb>` played as the engine plays it for an agent: the vendored script, `PP_HOME` the agent's instance,
    `PP_RUN` its run."""
    env = {**os.environ, **h.env, "PP_HOME": str(h.meta_of(path)), context.VARIABLE: run}
    return subprocess.run([sys.executable, str(h.team_module()), verb, *args], capture_output=True, text=True,
                          input=stdin, cwd=str(h.ws), env=env)
