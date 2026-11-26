"""The `house` domain, layer `verbs`: what the house gives to every verb of pp-team.

A definition belongs here when it serves the command line itself: it reads a verb's arguments, or refuses them with
the usage. A verb is where the skill meets its caller: it may print, end the call and use every other layer.
"""
from __future__ import annotations

from house.model import MANY, RETIRED_FLAGS, USAGE
from house.store import refuse


def retired_flags(rest: list[str]) -> None:
    """A flag of before (`--wakes`, `--budget-wakes`: the bounds counted wake-ups) refuses `flag-retired`
    naming the flag that took its place; nothing is parsed after it."""
    for flag in rest:
        if flag in RETIRED_FLAGS:
            refuse(f"flag-retired -- `{flag}`: the bounds count launches -- say `{RETIRED_FLAGS[flag]}`.")


def flags(rest: list[str], table: dict[str, bool]) -> dict:
    """-> the verb's flags from its table (True: takes a value), a flag of `MANY` as the list of its values;
    anything else is the usage."""
    found: dict = {name: ([] if name in MANY else None if takes else False) for name, takes in table.items()}
    index = 0
    while index < len(rest):
        word = rest[index]
        name = word[2:] if word.startswith("--") else ""
        if name not in table:
            refuse(USAGE)
        if table[name]:
            if index + 1 >= len(rest):
                refuse(USAGE)
            if name in MANY:
                found[name].append(rest[index + 1])
            else:
                found[name] = rest[index + 1]
            index += 2
        else:
            found[name] = True
            index += 1
    return found
