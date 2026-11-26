"""The `journal` domain, layer `rules`: what the journal's events say, and what a snapshot writes.

A definition belongs here when it computes its answer from a list of events or the values it is given: the events of
one task; whether a snapshot may be taken (`snapshot_asked`); the `snapshot` composed from the last event's number and
the state already packed (`snapshot_of`). It reads no disk, no clock and no environment and prints nothing: what
needs the system belongs to `store`, and the state is packed by the verb.
"""
from __future__ import annotations

from house.model import Declined
from journal.model import Snapshot


def of_task(events: list[dict], task: str) -> list[dict]:
    """-> the events of one task: those that name it, and the launches and ends of the
    intents it opened (found by their tag)."""
    tags = {one.get("tag") for one in events if one.get("kind") == "wake-intent" and one.get("task") == task}
    return [one for one in events if one.get("task") == task or (one.get("tag") in tags and one.get("kind") != "wake-intent")]


def snapshot_asked(state: dict) -> None:
    """`team snapshot` judged before the state is packed: `Declined("team-not-started")` before any start."""
    if state.season.started is None:
        raise Declined("team-not-started")


def snapshot_of(upto: int, packed: dict) -> list:
    """-> `snapshot {upto, state}`: the state packed (`packed`, by the verb) up to the event `upto`."""
    return [Snapshot.made(upto=upto, state=packed)]
