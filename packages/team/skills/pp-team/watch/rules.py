"""The `watch` domain, layer `rules`: what a watch decides from the values it is given.

A definition belongs here when it computes its answer from the state and its arguments: the seconds a flag names,
whether nothing can move any more. A value that is no number of seconds, or one below its floor, DECLINES
`<flag>-invalid` with the text the refusal prints, and the watch (`watch/acts.py`) refuses it, `--heartbeat` before
`--for`. It reads no disk, no clock and no environment and prints nothing: what needs the system belongs to `store`.
"""
from __future__ import annotations

from house.model import decline
from task.rules import dues, loud
from wake.rules import open_intents


def seconds_of(asked: dict, flag: str, floor: float) -> float | None:
    """-> the seconds a flag names, at least `floor`; None without the flag. DECLINES `<flag>-invalid` for a value
    that is no number of seconds at least `floor`."""
    if asked[flag] is None:
        return None
    try:
        value = float(asked[flag])
    except ValueError:
        value = -1.0
    if value < floor:
        decline(f"{flag}-invalid -- `--{flag} {asked[flag]}`: a number of seconds, at least {floor:g}.")
    return value


def quiescent(state: dict) -> bool:
    """-> whether nothing can move: no intent without an end, and no task open -- or nothing a
    tick could still launch on them: no agent has a message due, or the budget is spent, or
    the due tasks' wake-ups are."""
    if open_intents(state):
        return False
    if not any(one.state == "open" for one in state.task.tasks.values()) or state.budget.budget_spent:
        return True
    started = state.season.started
    for agent in (started.body.agents if started is not None else None) or {}:
        if any(task not in state.budget.launches_spent and loud(state, box) for task, box in dues(state, agent)):
            return False
    return True
