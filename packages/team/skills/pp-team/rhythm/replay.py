"""The `rhythm` domain, layer `replay`: the fold of the journal's events into the rhythm's part of the state.

A definition belongs here when it folds an event into the rhythm's part -- the ceremonies rung, the recurrences laid,
sounded by a task, skipped, stopped, paused, taken back or changed, and counted afresh from a new season -- or when it
is `RHYTHM_FOLDS`, the table that maps a kind of event to its fold. A fold is a function `f(state, before, one)`: it
takes one event of the journal and writes the keys of its part of the state, and nothing else. `before` shows the parts
that follow this one as they stood before the event -- at `team-started`, the season that stood before it; the composer
of `journal/replay.py` calls the folds, kind by kind, in the order of the domains. A fold reads nothing but the state,
`before` and the event, prints nothing and writes nothing to disk.

The rhythm's fold reads its seven kinds by the attributes of their typed event -- its body, its `at`, its `id` -- but
one: `recurrence-changed` writes a key to say what changes, even with the value `null`, which takes a recurrence's
context limit off. So the fold reads on the event's line which keys change, and on the body their value. It reads
`team-started` and `task`, the kinds of `season` and of `task` it takes, by their attributes too. It reads by key the
mapping it folds and the recurrence being folded: it writes the recurrence's dictionary as before, and the
`Recurrence` is born from it when the state is composed.
"""
from __future__ import annotations


def rhythm_team_started(state: dict, before: dict, one: dict) -> None:
    """`team-started`."""
    since = one.body.since
    if since:                                         # after a stop: nothing passed off season is caught up
        for recurrence in state["recurrences"].values():
            recurrence["since"], recurrence["first"] = since, 1


def rhythm_task(state: dict, before: dict, one: dict) -> None:
    """`task`."""
    body = one.body
    recurrence = state["recurrences"].get(body.recurrence)
    if recurrence is not None:                        # an occurrence: its period sounded, none for one launched now
        if body.period is not None:
            recurrence["sounded"].append(body.period)
        recurrence["last"] = body.task


def rhythm_ceremony_due(state: dict, before: dict, one) -> None:
    """`ceremony-due`."""
    body = one.body
    state["rung"].setdefault(str(body.ceremony), []).append(str(body.period))


def rhythm_recurrence(state: dict, before: dict, one) -> None:
    """`recurrence`: `team post --every`: a task that comes back."""
    body = one.body
    state["recurrences"][body.recurrence] = {
        "id": body.recurrence, "from": body.sender, "to": body.to, "text": body.text,
        "name": body.name, "when": body.when, "since": body.since, "at": one.at,
        "context": body.context, "description": body.description, "first": 0, "stopped": None,
        "paused": None, "sounded": [],
        "task": body.task,
        "last": body.task}                            # a recurrence born of a task: its origin its last occurrence


def rhythm_recurrence_skipped(state: dict, before: dict, one) -> None:
    """`recurrence-skipped`: the occurrence before still open: the period sounded."""
    recurrence = state["recurrences"].get(one.body.recurrence)
    if recurrence is not None:
        recurrence["sounded"].append(one.body.period)


def rhythm_recurrence_stopped(state: dict, before: dict, one) -> None:
    """`recurrence-stopped`: `team stop --recurrence`."""
    recurrence = state["recurrences"].get(one.body.recurrence)
    if recurrence is not None:
        recurrence["stopped"] = {"by": one.body.by, "at": one.at, "id": one.id}


def rhythm_recurrence_paused(state: dict, before: dict, one) -> None:
    """`recurrence-paused`: `team pause --recurrence`: it sounds nothing until resumed."""
    recurrence = state["recurrences"].get(one.body.recurrence)
    if recurrence is not None:
        recurrence["paused"] = {"by": one.body.by, "at": one.at, "id": one.id}


def rhythm_recurrence_resumed(state: dict, before: dict, one) -> None:
    """`recurrence-resumed`: `team resume --recurrence`: nothing caught up."""
    recurrence = state["recurrences"].get(one.body.recurrence)
    if recurrence is not None:
        recurrence["paused"], recurrence["since"], recurrence["first"] = None, one.body.since, 1


def rhythm_recurrence_changed(state: dict, before: dict, one) -> None:
    """`recurrence-changed`: `team recurrence`: what it carries replaced. A key the line carries is a change, its value
    None too (`context: None`, the limit taken off): the line says which keys changed, the body their values."""
    body, line = one.body, one.line
    recurrence = state["recurrences"].get(body.recurrence)
    if recurrence is not None and "when" in line:      # a duration a change gives: its first slot one later
        recurrence["when"], recurrence["since"] = body.when, body.since
        recurrence["first"] = 1
    if recurrence is not None and "context" in line:
        recurrence["context"] = body.context
    if recurrence is not None and "text" in line:      # the occurrences to come open with it
        recurrence["text"] = body.text
    if recurrence is not None and "description" in line:
        recurrence["description"] = body.description


# The fold of the part `rhythm` of the state: what ONE event writes in it -- the recurrences the owner posted and the
# periods they sounded, the ceremonies rung. `before` holds what a fold reads of a part that follows its own in the
# order of the domains, as it stood before the event.
RHYTHM_FOLDS = {"team-started": rhythm_team_started, "task": rhythm_task, "ceremony-due": rhythm_ceremony_due,
              "recurrence": rhythm_recurrence, "recurrence-skipped": rhythm_recurrence_skipped,
              "recurrence-stopped": rhythm_recurrence_stopped, "recurrence-paused": rhythm_recurrence_paused,
              "recurrence-resumed": rhythm_recurrence_resumed, "recurrence-changed": rhythm_recurrence_changed}
