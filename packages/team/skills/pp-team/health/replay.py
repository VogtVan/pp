"""The `health` domain, layer `replay`: the fold of the journal's events into the health's part of the state.

A definition belongs here when it folds an event into the health's part -- each member's falls and its suspicion, its
repentance when it answers again, the silences the tick wrote -- or when it is `HEALTH_FOLDS`, the table that maps a
kind of event to its fold. A fold is a function `f(state, before, one)`: it takes one event of the journal and writes
the keys of its part of the state, and nothing else. `before` shows the parts that follow this one as they stood before
the event -- at `team-started`, the season that stood before it; the composer of `journal/replay.py` calls the folds,
kind by kind, in the order of the domains. A fold reads nothing but the state, `before` and the event, prints nothing
and writes nothing to disk.

The health's fold reads by the attributes of their typed event -- its body, its `at`, its `id` -- `silence`, its one
kind, and the five kinds of other domains it takes: `team-started`, `post`, `resumed`, `wake-ended` and `wake-failed`;
so too an intent the mapping keeps. It reads by key the mapping it folds.
"""
from __future__ import annotations

from season.replay import member_folded
from task.replay import members_folded


def health_team_started(state: dict, before: dict, one: dict) -> None:
    """`team-started`."""
    state["health"] = {}                              # nobody suspected at a season's start


def health_post(state: dict, before: dict, one: dict) -> None:
    """`post`."""
    body = one.body
    if member_folded(state, body.sender) and body.by != "tick":   # an act of a member suspected by
        health = state["health"].get(body.sender) or {}        # silence lifts it: it repents (row 115)
        if health.get("falls") and health.get("cause") == "silence":
            health.update({"falls": 0, "repents": int(health.get("repents") or 0) + 1})


def health_silence(state: dict, before: dict, one) -> None:
    """`silence`: the member's silence fell: a fall of the detector (row 115)."""
    state["silences"].append(one)
    health = state["health"].setdefault(one.body.agent, {"falls": 0, "repents": 0})
    health.update({"falls": int(health.get("falls") or 0) + 1, "at": one.at, "cause": "silence", "id": one.id})


def health_wake_ended(state: dict, before: dict, one: dict) -> None:
    """`wake-ended`."""
    intent = state["intents"].get(one.body.tag)
    health = state["health"].get(intent.body.agent if intent is not None else None) or {}
    if health.get("falls") and health.get("cause") != "silence":   # a fallen member answered: it repents;
        #                                              a silence is lifted by an act of its alone (row 115)
        health.update({"falls": 0, "repents": int(health.get("repents") or 0) + 1})


def health_wake_failed(state: dict, before: dict, one: dict) -> None:
    """`wake-failed`."""
    body = one.body
    intent = state["intents"].get(body.tag)
    if (intent is not None and body.final and not body.house   # the house refused: nothing done
            and (state["tasks"].get(intent.body.task) or {}).get("state") != "stopped"):
        health = state["health"].setdefault(intent.body.agent, {"falls": 0, "repents": 0})   # SUSPECTED
        health.update({"falls": int(health.get("falls") or 0) + 1, "at": one.at, "cause": "fall",
                       "id": one.id})


def health_resumed(state: dict, before: dict, one: dict) -> None:
    """`resumed`: `team resume`: the owner trusts its members again."""
    for member in members_folded(state, one.body.task):
        if (state["health"].get(member) or {}).get("falls"):
            state["health"][member]["falls"] = 0


# The fold of the part `health` of the state: what ONE event writes in it -- the members suspected (`falls`, the last
# fall, its cause) and the silences that fell; a member repents when a fallen one answers. `before` holds what a fold
# reads of a part that follows its own in the order of the domains, as it stood before the event.
HEALTH_FOLDS = {"team-started": health_team_started, "post": health_post, "silence": health_silence,
              "wake-ended": health_wake_ended, "wake-failed": health_wake_failed, "resumed": health_resumed}
