"""The `rhythm` domain, layer `model`: what a ceremony and a recurrence are, held as plain values.

A definition belongs here when it is data about the team's rhythm and does nothing: the units of a recurrence's
duration, the flags of the verbs that ring a ceremony or set a recurrence, or a type that carries one of them. Nothing
here reads the disk, the clock or the environment.

It also holds the bodies of the rhythm's seven kinds of event -- `CeremonyDue`, `RecurrenceBorn` (the kind
`recurrence`), `RecurrenceChanged`, `RecurrencePaused`, `RecurrenceResumed`, `RecurrenceSkipped` and `RecurrenceStopped`
-- in the tuple `RHYTHM_BODIES` that `journal/model.py` reads to decode the journal. The key `from` of `recurrence` is a
word Python keeps for itself: the body reads it in the field `sender`, and its `json()` gives it back under `from`. The
`recurrence` of a `recurrence` is required, as the fold read it without a condition: a line without it stops the replay.

It holds the CARRIER `Recurrence`, one recurrence as its fold made it: a frozen class born when the state is composed,
which keeps the dictionary it comes from -- its `json()` gives that dictionary back as it is, a key the fold never wrote
staying absent; a reader reads it by its attributes. And it holds the rhythm's part of the team's state, typed:
`recurrences` holds a `Recurrence` per recurrence, `rung` the periods each ceremony rang.
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields

from house.model import HOUR, MINUTE, Body, Part, Typed

RECURRENCE_FLAGS = {"every": True, "context": True, "message": True, "task": True, "description": True, "as": True,
                    "now": False, "no-tick": False}
RING_FLAGS = {"as": True, "no-tick": False}
UNITS = {"m": MINUTE, "h": HOUR, "d": 24 * HOUR}  # the units of a recurrence's duration


@dataclass(frozen=True, eq=False)
class CeremonyDue(Body):
    """`ceremony-due`: a ceremony rings for a period -- `by` who rang it at hand, None for its own hour."""
    KIND = "ceremony-due"
    ceremony: str | None = None
    period: str | None = None
    by: str | None = None


@dataclass(frozen=True, eq=False)
class RecurrenceBorn(Body):
    """`recurrence`: `team post --every` -- a task that comes back, as its writers write it; `sender` is the key `from`,
    a word Python keeps, and `json()` gives it back under that key."""
    KIND = "recurrence"
    recurrence: str
    sender: str | None = None
    to: str | None = None
    name: str | None = None
    text: str | None = None
    when: dict | None = None
    since: str | None = None
    context: int | None = None
    task: str | None = None
    description: str | None = None

    @classmethod
    def of(cls, line: dict) -> "RecurrenceBorn":
        return super().of({**line, "sender": line.get("from")})

    def json(self) -> dict:
        return {("from" if key == "sender" else key): value for key, value in super().json().items()}


@dataclass(frozen=True, eq=False)
class RecurrenceChanged(Body):
    """`recurrence-changed`: `team recurrence` -- what it carries replaced. A key the line carries is a change, its
    value None too (`context: None`: the limit taken off): a reader asks the line which keys it carries."""
    KIND = "recurrence-changed"
    recurrence: str | None = None
    when: dict | None = None
    since: str | None = None
    context: int | None = None
    text: str | None = None
    description: str | None = None
    by: str | None = None


@dataclass(frozen=True, eq=False)
class RecurrencePaused(Body):
    """`recurrence-paused`: `team pause --recurrence` -- it sounds nothing until resumed."""
    KIND = "recurrence-paused"
    recurrence: str | None = None
    by: str | None = None


@dataclass(frozen=True, eq=False)
class RecurrenceResumed(Body):
    """`recurrence-resumed`: `team resume --recurrence` -- nothing caught up, its periods counted from `since`."""
    KIND = "recurrence-resumed"
    recurrence: str | None = None
    by: str | None = None
    since: str | None = None


@dataclass(frozen=True, eq=False)
class RecurrenceSkipped(Body):
    """`recurrence-skipped`: a period sounded while the occurrence before is still `open`."""
    KIND = "recurrence-skipped"
    recurrence: str | None = None
    period: str | None = None
    open: str | None = None


@dataclass(frozen=True, eq=False)
class RecurrenceStopped(Body):
    """`recurrence-stopped`: `team stop --recurrence`."""
    KIND = "recurrence-stopped"
    recurrence: str | None = None
    by: str | None = None


RHYTHM_BODIES: tuple = (CeremonyDue, RecurrenceBorn, RecurrenceChanged, RecurrencePaused, RecurrenceResumed,
                        RecurrenceSkipped, RecurrenceStopped)   # the bodies of this domain's kinds: `journal/model.py`
#                                                                 reads them


@dataclass(frozen=True, eq=False)
class Recurrence(Typed):
    """ONE recurrence of the team, as its fold made it: what it opens, for whom, how often and since when, the periods
    it sounded and its last occurrence, its pause and its stop; `sender` is the key `from`. It keeps the dictionary it
    comes from (`json()`): a key the fold never wrote stays absent."""
    id: str | None = None
    sender: str | None = None
    to: str | None = None
    text: str | None = None
    name: str | None = None
    when: dict | None = None
    since: str | None = None
    at: str | None = None
    context: int | None = None
    description: str | None = None
    first: int | None = None
    stopped: dict | None = None
    paused: dict | None = None
    sounded: list | None = None
    task: str | None = None
    last: str | None = None
    held: dict = field(default_factory=dict, repr=False)

    @staticmethod
    def of(held: dict) -> "Recurrence":
        return Recurrence(**{key: value for key, value in held.items() if key in RECURRENCE_FIELDS},
                          sender=held.get("from"), held=held)

    def json(self) -> dict:
        return self.held


RECURRENCE_FIELDS = frozenset(one.name for one in fields(Recurrence)) - {"sender", "held"}   # the keys a recurrence
#                                                                                              names by their own name


@dataclass(frozen=True, eq=False)
class RhythmPart(Part):
    """The part `rhythm` of the team's state -- the rhythm: the ceremonies rung and the recurrences. `recurrences`
    holds a `Recurrence` per recurrence, born here from the dictionary the fold wrote."""
    rung: dict[str, list]                  # ceremony -> the periods it rang
    recurrences: dict[str, Recurrence]     # recurrence id -> the recurrence

    @classmethod
    def of(cls, state: dict) -> "RhythmPart":
        made = {one.name: state.get(one.name) for one in fields(cls)}
        made["recurrences"] = {key: Recurrence.of(one) if type(one) is dict else one
                               for key, one in (made["recurrences"] or {}).items()}
        return cls(**made)
