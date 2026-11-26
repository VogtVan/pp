"""The `season` domain, layer `replay`: the fold of the journal's events into the season's part of the state.

A definition belongs here when it folds an event into the season's part -- the season started or stopped, paused or
taken back, its limits, its net turned off, a delete begun -- or when it is `SEASON_FOLDS`, the table that maps a kind
of event to its fold. A fold is a function `f(state, before, one)`: it takes one event of the journal and writes the
keys of its part of the state, and nothing else. `before` shows the parts that follow this one as they stood before the
event -- at `team-started`, the season that stood before it; the composer of `journal/replay.py` calls the folds, kind
by kind, in the order of the domains. A fold reads nothing but the state, `before` and the event, prints nothing and
writes nothing to disk.

The season's fold also takes `budget-raised`, a kind of the `budget` domain: the bounds it raises are the season's
`limits`, and the budget's fold, which comes after, may not write a key of the season's part.

The season's fold reads the kinds of its own domain and `budget-raised` by the attributes of their typed event -- its
body, its `at`, its `id` -- and no longer translates the bounds of an old journal: the body has read them under the keys
of today. The state keeps the `team-started` event under `started`, its line as it was read. `schedule-off`, a kind of
`net`, reaches the fold as a typed event, and the fold reads nothing of it.

A fold reads the mapping it folds, not the typed state, so it calls no rule. The rules of the season that a fold needs
have their TWINS here, each with the body its rule had before the rules read the typed state: `member_folded`
(`is_member`), `principal_folded` (`is_principal`), `kept_folded` (`launch_kept`) and `profile_folded` (`profile_of`).
A twin reads the start it finds in the mapping by its attributes, and the mapping by key; before the first start it
gets `None`. The folds of `task`, `health` and `wake` call them; a twin calls only twins.
"""
from __future__ import annotations


def season_team_started(state: dict, before: dict, one) -> None:
    """`team-started`: a season: the counts afresh, the runs kept. Its body reads the bounds of before under the keys
    of today; the state keeps the event, its line as it was read."""
    body = one.body
    state["started"] = one
    state["seasons"] = int(state.get("seasons") or 0) + 1
    state["schedule"] = True
    state["limits"] = {**dict(body.limits or {}),
                       **{key: value for key, value in (body.season or {}).items() if value is not None}}
    state["stopped"], state["since"] = None, body.since


def season_season_stopped(state: dict, before: dict, one) -> None:
    """`season-stopped`: `team stop <team>`: the season ends, its pause with it."""
    body = one.body
    state["stopped"] = {"by": body.by, "at": one.at, "id": one.id, "tasks": body.tasks, "recurrences": body.recurrences}
    state["paused"] = None


def season_schedule_off(state: dict, before: dict, one: dict) -> None:
    """`schedule-off`."""
    state["schedule"] = False


def season_budget_raised(state: dict, before: dict, one) -> None:
    """`budget-raised`: `team budget` raised a bound; its body reads `wakes`, the field of before (team 0.39.0), as
    `launches`."""
    body = one.body
    if body.budget is not None:
        state["limits"]["budget"] = float(body.budget)
    if body.launches is not None:
        state["limits"]["budget-launches"] = int(body.launches)


def season_paused(state: dict, before: dict, one) -> None:
    """`paused`: `team pause`: nobody woken, nothing rung."""
    state["paused"] = {"by": one.body.by, "at": one.at, "id": one.id}


def season_unpaused(state: dict, before: dict, one) -> None:
    """`unpaused`: `team resume` without a task: the team back."""
    state["paused"] = None


def season_deleting(state: dict, before: dict, one) -> None:
    """`deleting`: `team delete --yes`: the team lives no more."""
    state["deleting"] = True


def member_folded(state: dict, name) -> bool:
    """-> whether `name` is a member of the season, as a fold reads it, on the mapping it folds: the twin of
    `is_member`, which reads the typed state."""
    started = state["started"]
    return name in ((started.body.agents if started is not None else None) or {})


def principal_folded(state: dict, name) -> bool:
    """-> whether `name` is one a team answers to, as a fold reads it, on the mapping it folds: the twin of
    `is_principal`, which reads the typed state -- its owner, a mandator of `principals:`, or the team itself."""
    started = state["started"]
    if started is None:
        return False
    return name is not None and (name == started.body.owner or name == started.team
                                 or name in (started.body.principals or []))


def kept_folded(started: dict, member: str) -> dict:
    """-> `{model, provider}` a member's launch takes from the season, as a fold reads it: the twin of `launch_kept`
    -- its profile's, else the team's launch, `null` when neither names one."""
    kept = (started.body.launch if started is not None else None) or {}   # None before the first season
    profile = profile_folded(started, member)
    return {key: profile.get(key) if profile.get(key) is not None else kept.get(key) for key in ("model", "provider")}


def profile_folded(started: dict, member: str | None) -> dict:
    """-> the member's profile of the season (`team-started.profiles`) as a fold reads it, {} for none: the twin of
    `profile_of`."""
    profiles = started.body.profiles if started is not None else None
    return dict(((profiles or {}).get(member) or {})) if member else {}


# The fold of the part `season` of the state: what ONE event writes in it -- the season started, stopped, paused, its
# limits (raised by `budget-raised`), its schedule, the team deleting. `before` holds what a fold reads of a part that
# follows its own in the order of the domains, as it stood before the event.
SEASON_FOLDS = {"team-started": season_team_started, "season-stopped": season_season_stopped,
              "schedule-off": season_schedule_off, "budget-raised": season_budget_raised, "paused": season_paused,
              "unpaused": season_unpaused, "deleting": season_deleting}
