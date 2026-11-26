"""The `admin` domain, layer `rules`: what a delete decides.

A definition belongs here when it computes its answer from the team's state alone: what `team delete` writes before it
removes anything -- `deleting`, composed by `made`; nothing when the delete is already said; `Declined` by its code
while a task is open or a wake-up under way (`team-busy`), whose sentence the verb says. It reads no disk, no clock
and no environment and prints nothing: what needs the system belongs to `store` or to the verb.
"""
from __future__ import annotations

from house.model import Declined
from season.model import Deleting
from wake.rules import open_intents


def deleting_of(state: dict) -> list:
    """-> what `team delete --yes` writes before anything is removed: `deleting`, nothing when it stands already; a
    task open or a wake-up under way meanwhile, `Declined("team-busy", the open tasks)`."""
    at_work = [one.id for one in state.task.tasks.values() if one.state == "open"]
    if at_work or open_intents(state):
        raise Declined("team-busy", at_work)
    return [] if state.season.deleting else [Deleting.made()]
