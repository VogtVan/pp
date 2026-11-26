"""The `season` domain, layer `model`: what a season is, held as plain values.

A definition belongs here when it is data about a season -- the time from a team's start to its stop -- and does
nothing: the flags of the verbs that open, hold and close it, the keys of `SEASON.md` and of a member's profile, the
limits a season sets over `TEAM.md`'s, the states that close a task, or a type that carries one of them. Nothing here
reads the disk, the clock or the environment.

It also holds the season's part of the team's state -- a frozen class, a field per key of the state its fold writes,
each typed by what it holds; `started` is the `team-started` event, or after a snapshot the dictionary the snapshot kept
-- and the bodies of the season's six kinds of event: `TeamStarted`, `SeasonStopped`, `Paused`, `Unpaused`, `Deleting`
and `ScheduleOff`, in the tuple `SEASON_BODIES` that `journal/model.py` reads to decode the journal. `ScheduleOff` is
here, not in `net/`, because the season folds it and `resolution` (`task/rules.py`) writes it: `task` may read
`season`, which comes before it, and not `net`, which comes after.

A body reads what an old journal wrote under the keys of today: `TeamStarted` reads the bounds `wakes` and
`budget-wakes` of its `limits` and its `season` as `launches` and `budget-launches`, and the key `season-digest` as the
field `season_digest`, which its `json()` gives back under the key. The line itself is never rewritten.
"""
from __future__ import annotations

from dataclasses import dataclass

from house.model import Body, Part
from declaration.model import RETIRED_LIMITS

CLOSED = ("stopped", "resolved")
LAUNCH_FLAGS = {"provider": True, "harness": True, "model": True, "permissions": True, "effort": True}
START_FLAGS = {"message": True, "to": True, "name": True, "no-tick": False, "budget": True, "budget-launches": True,
               "silence": True, "context": True, **LAUNCH_FLAGS}
PROFILE_KEYS = ("provider", "model", "effort", "permissions")   # what a member's profile may replace
STOP_FLAGS = {"task": True, "kill": False, "recurrence": True, "json": False, "no-tick": False}
PAUSE_FLAGS = {"recurrence": True, "as": True}
SEASON_LIMITS = ("budget", "budget-launches", "silence", "context")   # the season's own limits, over TEAM.md's
PROFILE_LINE = ("provider", "model", "effort", "permissions", "silence")   # a profile line's keys, beside
#                                                 `package.<name>`
SEASON_KEYS = ("template", "values", "documents", *LAUNCH_FLAGS, *SEASON_LIMITS, "packages", "profiles", "work")
SEASON_LAUNCH = (*SEASON_LIMITS, *LAUNCH_FLAGS)   # the season's flags of `start` that `declare --season` takes too
#                                                 what SEASON.md may say in its front matter

# --- the declaration read: its text, its verdict, its gap to the start ---------------------------

PENDING = ("agents", "reports", "root", "principals", "ceremonies", "entries", "limits", "schedule", "roles",
           "template", "values")
SEASON_PENDING = ("launch", "season", "packages", "profiles", "work")   # the season's, from SEASON.md

# --- the verbs -----------------------------------------------------------------------------

MEMBER_FLAGS = {"provider": True, "model": True, "effort": True, "permissions": True, "package": True, "silence": True}
LAUNCH_KEYS = ("harness", "provider", "model", "permissions", "effort")


@dataclass(frozen=True, eq=False)
class TeamStarted(Body):
    """`team-started`: a season opens -- what `start` read of `TEAM.md` and `SEASON.md`, in the order it writes them.
    `limits` and `season` read under the keys of today; `season_digest` is the key `season-digest`."""
    KIND = "team-started"
    agents: dict | None = None
    reports: list | None = None
    root: str | None = None
    principals: list | None = None
    owner: str | None = None
    ceremonies: list | None = None
    entries: dict | None = None
    roles: dict | None = None
    work: str | None = None
    launch: dict | None = None
    limits: dict | None = None
    season: dict | None = None
    packages: list | None = None
    profiles: dict | None = None
    schedule: int | None = None
    unit: str | None = None
    digest: str | None = None
    template: dict | None = None
    values: dict | None = None
    documents: list | None = None
    rendered: dict | None = None
    season_digest: str | None = None
    since: str | None = None

    @classmethod
    def of(cls, line: dict) -> "TeamStarted":
        read = {**line, "season_digest": line.get("season-digest")}
        for key in ("limits", "season"):       # the bounds of a journal of team 0.39.0 counted wake-ups
            if isinstance(line.get(key), dict):
                read[key] = {RETIRED_LIMITS.get(name, name): value for name, value in line[key].items()}
        return super().of(read)

    def json(self) -> dict:
        made = super().json()
        return {("season-digest" if key == "season_digest" else key): value for key, value in made.items()}


@dataclass(frozen=True, eq=False)
class SeasonStopped(Body):
    """`season-stopped`: `team stop <team>` -- the season ends, with the tasks and the recurrences it closes."""
    KIND = "season-stopped"
    by: str | None = None
    tasks: list | None = None
    recurrences: list | None = None


@dataclass(frozen=True, eq=False)
class Paused(Body):
    """`paused`: `team pause` -- nobody woken, nothing rung."""
    KIND = "paused"
    by: str | None = None


@dataclass(frozen=True, eq=False)
class Unpaused(Body):
    """`unpaused`: `team resume` without a task -- the team back."""
    KIND = "unpaused"
    by: str | None = None


@dataclass(frozen=True, eq=False)
class Deleting(Body):
    """`deleting`: `team delete --yes` -- the team lives no more."""
    KIND = "deleting"


@dataclass(frozen=True, eq=False)
class ScheduleOff(Body):
    """`schedule-off`: the team needs its net no more -- nothing open, nothing to ring."""
    KIND = "schedule-off"


SEASON_BODIES: tuple = (TeamStarted, SeasonStopped, Paused, Unpaused, Deleting,   # the bodies of this domain's kinds:
                        ScheduleOff)                                              # `journal/model.py` reads them


@dataclass(frozen=True, eq=False)
class SeasonPart(Part):
    """The part `season` of the team's state -- the season: its start, its limits, its schedule, its pause and stop,
    the last event."""
    started: "Event | None"              # the `team-started` event; a snapshot's, the dictionary it kept
    schedule: bool
    limits: dict
    last: dict | None
    seasons: int
    paused: dict | None
    deleting: bool
    stopped: dict | None
    since: str | None
