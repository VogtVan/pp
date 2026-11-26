"""The `journal` domain, layer `model`: what a team's journal and its state are, held as values.

A definition belongs here when it is data about the journal and does nothing: the flags of the verb that shows it, the
kinds of events no version writes any more, the parts of the state a snapshot keeps as they are, the words a face adds
to an event, or a type that carries one of them. Nothing here reads the disk, the clock or the environment.

`Event` is the envelope of one event: the line it was read from, which its `json()` gives back as it was -- its keys in
their order, a key no class names among them --, and its body when its kind is typed. Only a line whose kind has a body
becomes an `Event`, and only when the composer folds it; a line of any other kind stays the dictionary that was read, in
the folds and in the state. `BODIES` maps each kind typed so far to the class of its body; it is made of the tuple
`<D>_BODIES` that the `model.py` of each domain holds, and of `Snapshot`, the body of the journal's own kind.
`TeamState` is the team's state, composed of six parts, one per domain -- season, task, rhythm, wake, budget, health --,
each a class of its domain's `model.py`; a key of the state reads in its own part, and `gone` is a key only once a face
gives it.
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields, replace

from house.model import Body, Typed
from season.model import SEASON_BODIES, SeasonPart
from task.model import TASK_BODIES, TaskPart
from rhythm.model import RHYTHM_BODIES, RhythmPart
from wake.model import WAKE_BODIES, WakePart
from budget.model import BUDGET_BODIES, BudgetPart
from health.model import HEALTH_BODIES, HealthPart
from net.model import NET_BODIES

RETURNED_MARK = " · returns a message never delivered"   # what the text of `log` says of a post that returns a message
LOG_FLAGS = {"task": True, "last": True, "json": False}
DEAD = ("delegation", "terminal", "wait", "wait-met")   # the events no version writes any more, which no face says:
                                                 # the first two (before team 0.33.0) the replay reads, the last two
                                                 # (before team 1.14.0) it skips -- nothing holds a member
PLAIN = ("started", "tasks", "done", "intents", "launched", "stops", "limits", "deferred",
         "delegations", "schedule", "cost", "budget_spent", "seen", "rung", "ends", "fails", "last",
         "seasons", "paused", "routed", "flow", "deleting", "recurrences", "silences",
         "context", "total", "halts", "quotas", "stopped", "since")   # the JSON-ready parts


@dataclass(frozen=True, eq=False)
class Snapshot(Body):
    """`snapshot`: the state packed (`packed`) up to the event `upto`; the replay starts again from the last one."""
    KIND = "snapshot"
    upto: int | None = None
    state: dict | None = None


def bodies_of(*classes) -> dict:
    """-> a kind -> the class of its body, from the classes of every domain; a kind two classes read is refused, both
    named -- two bodies for one kind, an old journal's kind read twice, a subclass without a KIND of its own --, and
    so is a class that `Body.reading` refuses."""
    found: dict = {}
    for made in classes:
        made.reading()                             # a body its reading would wrong refuses here, at load
        for kind in made.KINDS:
            if kind in found:
                first = found[kind]
                raise TypeError(f"the kind `{kind}` has two bodies: {first.__module__}.{first.__qualname__} and "
                                f"{made.__module__}.{made.__qualname__}")
            found[kind] = made
    return found


BODIES = bodies_of(*SEASON_BODIES, *TASK_BODIES, *RHYTHM_BODIES, *WAKE_BODIES, *BUDGET_BODIES, *HEALTH_BODIES,
                   *NET_BODIES, Snapshot)    # the kinds typed so far, of every domain: a kind -> the class of its body


@dataclass(frozen=True, eq=False)
class Event(Typed):
    """ONE event of the journal: the `line` it was read from and the `body` of its kind; `kind`, `id`, `at`, `team`, every
    kind's, are read in the line. `of(line)` makes the event a line carries, its body read by the class `BODIES` gives
    its kind, None for a kind not typed; the composer makes one only of a line it folds whose kind is typed. `json()`
    gives the line back as it was, its keys in their order, a key no class names among them. An event a writer composes
    has a body and no line: `json()` is its body's -- `written` gives it `at`, `id`, `team`."""
    line: dict | None = field(default=None, repr=False)
    body: Body | None = None

    @staticmethod
    def of(line) -> "Event":
        """-> the event a line of the journal carries, its body read when its kind is typed."""
        if type(line) is Event:
            return line
        made = BODIES.get(line.get("kind"))
        return Event(line) if made is None else Event(line, made.of(line))

    @property
    def kind(self) -> str | None:
        return self._line().get("kind")

    @property
    def id(self) -> int | None:
        return self._line().get("id")

    @property
    def at(self) -> str | None:
        return self._line().get("at")

    @property
    def team(self) -> str | None:
        return self._line().get("team")

    def _line(self) -> dict:
        """-> the line the event was read from, or, composed, its body's `json()`: what its properties read."""
        line = self.line
        return line if line is not None else self.body.json()

    def json(self) -> dict:
        return self.line if self.line is not None else self.body.json()


STATE_PARTS = (("season", SeasonPart), ("task", TaskPart), ("rhythm", RhythmPart), ("wake", WakePart),
               ("budget", BudgetPart), ("health", HealthPart))   # the parts of the state, in the order of the domains
WHERE = {one.name: part for part, made in STATE_PARTS for one in fields(made)}   # a key of the state -> its part


@dataclass(frozen=True, eq=False)
class TeamState(Typed):
    """The team's STATE, composed of one part per domain; a key of the state reads in its part (`WHERE`). `gone` is
    no key until a face gives it (`but`)."""
    season: SeasonPart
    task: TaskPart
    rhythm: RhythmPart
    wake: WakePart
    budget: BudgetPart
    health: HealthPart

    @staticmethod
    def of(state: dict) -> "TeamState":
        """-> the state composed from the working mapping a replay folds."""
        return TeamState(**{part: made.of(state) for part, made in STATE_PARTS})

    def json(self) -> dict:
        wake = self.wake
        return {key: getattr(getattr(self, part), key) for key, part in WHERE.items()
                if key != "gone" or wake.gone is not None}

    def but(self, **changed) -> "TeamState":
        """-> the same state, the keys named given new values."""
        parts = {}
        for key, value in changed.items():
            part = WHERE[key]
            parts[part] = replace(parts.get(part, getattr(self, part)), **{key: value})
        return replace(self, **parts)
