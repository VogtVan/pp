"""The `tick` domain, layer `verbs`: the command line of the tick.

A definition belongs here when it plays the verb that ticks one team or every team of the house: it reads the verb's
arguments, plays the tick, and refuses with the usage. A verb is where the skill meets its caller: it may print, end the
call and use every other layer.
"""
from __future__ import annotations

import os
import sys

from house.model import USAGE
from house.rules import team_doc
from house.store import house, named_team, refuse
from net.model import TIMER_ENV, TIMER_TICKING
from net.rules import kept_path
from net.acts import needing
from tick.acts import ticked


def tick(rest: list[str]) -> int:
    TIMER_TICKING[0] = os.environ.pop(TIMER_ENV, "") == "1"     # the timer's own tick: taken out, no child inherits it
    root, conductor = house()
    if rest == ["--all", "--entry"]:              # the relaunch entry: the PATH of the process that laid it, taken up
        kept = kept_path(root)
        if kept.is_file():
            os.environ["PATH"] = kept.read_text(encoding="utf-8")
        rest = ["--all"]
    if rest == ["--all"]:
        for name in needing(root):                 # the house's relaunch entry at logon: every team in need
            try:
                ticked(root, conductor, name)
            except SystemExit as failed:           # a team that refuses is said; the others advance
                if failed.code not in (0, None):
                    sys.stderr.write(f"pp-team: {name} · tick failed, the other teams advance\n")
        return 0
    name, rest = named_team(conductor, rest)
    if rest:
        refuse(USAGE)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    run, said = os.environ.get("PP_AGENT_RUN", "").strip(), os.environ.get("PP_AGENT_STATE", "").strip()
    ticked(root, conductor, name, (run, said) if run and said else None)   # an on-end tick says its launch's end
    return 0
