"""The `rhythm` domain, layer `faces`: how a ceremony is put into words.

A definition belongs here when it turns a ceremony's values into what a member or a user reads -- its rhythm said, and
the sentences of a recurrence unknown or stopped (`recurrence_unknown`, `recurrence_was_stopped`), which the verbs and
the acts of the rhythm say for the codes its rules decline -- and gives it back without printing it. What a ring asks of
the facilitator and of each participant, which a decision writes into the task it opens, is a rule (`consignes`,
`rhythm/rules.py`).
"""
from __future__ import annotations


def said_when(when: dict) -> str:
    """-> a recurrence's period as the faces say it after `every`: `weekday 09:30`, or `4h`."""
    return str(when.get("every")) if when.get("kind") == "interval" else f"{when.get('kind')} {when.get('at')}"


def recurrence_unknown(name: str, called: str, ids: list[str]) -> str:
    """-> the sentence of `recurrence-unknown`: the id called, and the recurrences the team holds."""
    return f"recurrence-unknown -- no recurrence `{called}` of {name}: the recurrences are {', '.join(ids) or 'none'}."


def recurrence_was_stopped(recurrence: dict) -> str:
    """-> the sentence of `recurrence-stopped`: the recurrence, and the event that stopped it."""
    return f"recurrence-stopped -- {recurrence.id} was stopped at #{recurrence.stopped['id']}."
