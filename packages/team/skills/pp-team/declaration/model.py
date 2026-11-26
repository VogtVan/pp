"""The `declaration` domain, layer `model`: what a team's declaration is, held as plain values.

A definition belongs here when it is data about `TEAM.md` and the verbs that write or read it, and does nothing: the
flags of those verbs, the bounds of a name or a description, the step of the team's net when `TEAM.md` says none, the
ways a ceremony is timed and the days it may name, the limits that bound the tick and the names they had before, or a
type that carries one of them. Nothing here reads the disk, the clock or the environment.

It holds two CARRIERS, frozen classes that keep no dictionary and are read by their attributes: `Team`, the team as it
plays, born in `judged` (`declaration/rules.py`); and `Ceremony`, one ceremony as its line of `ceremonies:` declares it,
born in `ceremony_of` (`declaration/rules.py`). A `Team` holds its ceremonies as `Ceremony`. Each `json()` gives the
dictionary it was born as, its keys in their order -- a `Team` gives each ceremony by its own `json()` -- and that
dictionary is what `team-started` writes and a `--json` face prints. The ceremony of a task in the state is no
`Ceremony`: it is a `Task`.

A team is made of MEMBERS: `agents: |` of `TEAM.md` declares one `<name> <path>` per line -- the
member's NAME, a slug unique in the team, then the PATH of the agent that plays it; one path may
come back, several members on one agent. The journal (its `agent` field is the member's name), the
inbox, `status` and the head of every wake-up (`[team <team> · you are <member>]`) speak names;
every call to the house -- `agent start`, a wake lock, a record of the house, a birth -- is
addressed by the member's path, read at `team-started.agents` (`{name: path}`).
"""
from __future__ import annotations

from dataclasses import dataclass

from house.model import Typed

TICK_LOCK = "tick.lock"          # beside the journal: one tick at a time
DEFAULT_SCHEDULE = 300                           # seconds between two ticks of the net, unless TEAM.md says
DECLARATION_FLAGS = {"json": False, "season": False, "text-file": True}   # `declaration`: a candidate text read
NAME_CHARS = 80                                  # a task's name: one line a user types, read in a table
DESCRIPTION_CHARS = 200                          # a team's or a recurrence's description: one sentence read in a table
DECLARE_FLAGS = {"season": 0, "json": 0, "template": 1, "value": 1, "no-value": 1, "document": 1, "no-document": 1,
                 "body-file": 1, "member": 2, "no-member": 1, "role": None, "no-role": 1, "root": 1, "principal": 1,
                 "budget": 1, "launches": 1, "parallel": 1, "timeout": 1, "schedule": 1, "description": 1, "report": 1,
                 "no-report": 1}                 # the flags of `declare`:
#                                                 the words each takes -- None: a key, then its members up to the next flag
DECLARE_MANY = ("value", "no-value", "document", "no-document", "member", "no-member", "role", "no-role", "principal",
                "report", "no-report")
#                                                 the flags `declare` takes several times
DECLARE_TEAM = ("member", "no-member", "role", "no-role", "root", "principal", "budget", "launches", "parallel",
                "timeout", "schedule", "description", "report", "no-report")       # the flags of TEAM.md alone: the usage under `--season`
DECLARE_PAIRS = (("value", "no-value"), ("document", "no-document"), ("member", "no-member"), ("role", "no-role"),
                 ("report", "no-report"))
#                                                 a flag and its contrary: one line of a block written, taken out
MODES = ("every", "after")       # a ceremony's rhythm: at a period, or after another ceremony
DOWS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")   # the days `every <dow> HH:MM` may name
LIMITS = ("parallel", "budget", "retries", "timeout", "launches", "budget-launches", "suspect-max", "silence")   # the keys of TEAM.md that bound the tick
RETIRED_LIMITS = {"wakes": "launches", "budget-wakes": "budget-launches"}   # the keys of before: refused by name where written,
#                                                                            read where a journal already wrote them


@dataclass(frozen=True, eq=False)
class Ceremony(Typed):
    """ONE ceremony as its line of `ceremonies:` declares it: born in `ceremony_of` (`declaration/rules.py`) -- its
    name, its mode (`every`, `after`), what it follows, its period, its participants, its facilitator, its quorum
    (None: all) and the line itself. `json()`: the dictionary it was born as, the one `team-started` writes."""
    name: str
    mode: str
    after: str | None
    when: dict | None                      # `when_of`: {kind, at}, None for a ceremony `after` another
    participants: list
    facilitator: str
    quorum: int | None
    text: str                              # the line as TEAM.md writes it

    def json(self) -> dict:
        return {"name": self.name, "mode": self.mode, "after": self.after, "when": self.when,
                "participants": self.participants, "facilitator": self.facilitator, "quorum": self.quorum,
                "text": self.text}


@dataclass(frozen=True, eq=False)
class Team(Typed):
    """The team as it PLAYS: born in `judged` (`declaration/rules.py`), what `TEAM.md` and its preset declare, judged
    whole. `ceremonies` holds `Ceremony`; `json()` gives the dictionary it was born as, its keys in their order, each
    ceremony as its own `json()` -- and that dictionary is what `team-started` writes and a `--json` face prints."""
    agents: dict                           # member -> the path of its agent
    reports: list                          # [{from: [member, ...], to: member}]
    root: str
    principals: list
    ceremonies: list                       # [Ceremony]
    entries: dict                          # trigger -> document
    roles: dict                            # role key -> [member, ...]
    limits: dict                           # `limits_of`
    schedule: int | None                   # `schedule_of`: seconds, None for `off`
    name: str
    description: str | None
    digest: str
    template: dict | None                  # {template, origin, values}, None without a preset
    applied: list                          # [{name, value, from}]
    read: dict                             # what `documents_of` read of TEAM.md
    intention: str

    def json(self) -> dict:
        return {"agents": self.agents, "reports": self.reports, "root": self.root, "principals": self.principals,
                "ceremonies": [one.json() for one in self.ceremonies], "entries": self.entries, "roles": self.roles,
                "limits": self.limits, "schedule": self.schedule, "name": self.name, "description": self.description,
                "digest": self.digest, "template": self.template, "applied": self.applied, "read": self.read,
                "intention": self.intention}
