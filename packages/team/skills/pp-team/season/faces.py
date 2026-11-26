"""The `season` domain, layer `faces`: how a season is put into words.

A definition belongs here when it turns a season's values into what a user reads -- a sentence about a team out of its
season, in it, or paused -- and gives it back without printing it. The face of a launch, which reads the set a member's
run plays, is an act (`launch_face`, `season/acts.py`); the words of a refused context limit, which a rule writes, are a
rule (`context_invalid`, `season/rules.py`).
"""
from __future__ import annotations




def off_season(name: str, state: dict) -> str:
    """-> the refusal `season-stopped` of a gesture that needs a season under way."""
    stopped = state.season.stopped or {}
    return (f"season-stopped -- {name} is off season since #{stopped.get('id')} (`team stop`): `team start {name}` "
            "opens the next season.")


def in_season(name: str, state: dict, what: str) -> str | None:
    """-> the refusal `season-running` of `what` -- a write of `TEAM.md` or `SEASON.md`, a start -- while a season
    is under way (started, not stopped), None off season or before a first start."""
    if state.season.started is None or state.season.stopped:
        return None
    return (f"season-running -- {name} is in season since #{state.season.started.id}: {what} waits off season -- "
            f"`team stop {name}` ends the season, then write, then `team start {name}`.")


def paused_face(state: dict) -> dict | None:
    """-> `{by, at}` of the pause that stands, None when the team is not paused."""
    paused = state.season.paused
    return None if not paused else {"by": paused.get("by"), "at": paused.get("at")}
