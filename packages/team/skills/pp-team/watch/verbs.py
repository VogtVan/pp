"""The `watch` domain, layer `verbs`: the command line of the watch.

A definition belongs here when it plays the watch: it reads the verb's arguments, starts the watch and refuses with the
usage. What the watch says of each event is said by `watch/acts.py`. A verb is where the skill meets its caller: it may
print, end the call and use every other layer.
"""
from __future__ import annotations


from house.rules import team_doc
from house.store import machine_house, named_team, refuse
from house.verbs import flags
from watch.model import WATCH_FLAGS
from watch.acts import watched


def watch(rest: list[str]) -> int:
    root, conductor = machine_house()                      # the house's team, whatever instance reads it
    name, rest = named_team(conductor, rest)
    asked = flags(rest, WATCH_FLAGS)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    return watched(root, conductor, name, asked)
