"""The `health` domain, layer `faces`: how a team's health is put into words.

A definition belongs here when it turns the state into what a member or a user reads -- the lines and the face of a
member's health -- and gives it back without printing it. It reads the state by its parts, the members on the start's
body (`state.season.started.body.agents`). The words for a member that does not answer, which the team
writes in its place, are a rule (`not_answering`, `health/rules.py`).
"""
from __future__ import annotations

from wake.rules import suspicion_of


def health_lines(state: dict, member: str) -> str:
    """-> the HEALTH VIEW a wake-up's head carries: one line per other member suspected, the hour of its try --
    '' when nobody is."""
    found = []
    started = state.season.started
    for other in list((started.body.agents if started is not None else None) or {}):
        suspicion = suspicion_of(state, other) if other != member else None
        if suspicion is not None:
            found.append(f"[not answering at the moment: {other} -- tried again at {suspicion['until']:%H:%M:%S}]")
    return "\n".join(found)


def health_face(state: dict, member: str) -> dict | None:
    """-> the member's HEALTH as the face says it: `{suspected, falls, cause, tried_at, repents}` -- `cause` of the
    last fall, `fall` or `silence` (row 115); `tried_at` the local hour of its try to the second while it is
    suspected --, None for a member that never fell since the season began."""
    health = (state.health.health or {}).get(member)
    if not health:
        return None
    suspicion = suspicion_of(state, member)
    return {"suspected": suspicion is not None, "falls": int(health.get("falls") or 0), "cause": health.get("cause"),
            "tried_at": suspicion["until"].strftime("%Y-%m-%dT%H:%M:%S") if suspicion else None,
            "repents": int(health.get("repents") or 0)}
