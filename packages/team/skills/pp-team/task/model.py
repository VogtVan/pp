"""The `task` domain, layer `model`: what a task and a member's act are, held as plain values.

A definition belongs here when it is data about the tasks of a team and the acts its members send, and does nothing: the
forms of an act and their keys, the verbs of before, the flags of the verbs that post, resume or read the inbox, the
shape that opens an act in a member's words, or a type -- the refusal of an act, the frozen classes that carry a task.
Nothing here reads the disk, the clock or the environment.

It also holds the bodies of the task's ten kinds of event -- `TaskBorn` (the kind `task`), `Post`, `Done`, `Stopped`,
`Returned`, `Resumed`, `Deferred`, `InboxRead`, `InboxSeen`, and `Terminal`, the kind of a journal of before team 0.33.0
-- in the tuple `TASK_BODIES` that `journal/model.py` reads to decode the journal. The key `from` is a word Python keeps
for itself: a body that carries it reads it in the field `sender`, and its `json()` gives it back under `from`.

It holds the CARRIER `Task`, one task of the team as its fold made it: a frozen class born when the state is composed,
which keeps the dictionary it comes from -- its `json()` gives that dictionary back as it is, a key the fold never wrote
staying absent; a reader reads it by its attributes. And it holds the task's part of the team's state, a frozen
class whose fields are typed by what they hold: `tasks` holds a `Task` per task, and the events the part keeps -- the
messages, the results, the deferred launches -- are events, read from the journal or decoded from a snapshot.

Its bodies are read as every body is (`Body.of`): their table `KEYS` reads `from` in `sender`, and the fields the task's
fold read without a condition -- the `task` of `task`, `done` and `terminal`, the `agent` of `terminal`, the `message`
of `returned` -- are required: a line without them stops the replay.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, fields

from house.model import Body, Part, Typed

ELEMENTS = {"do": {"do"}, "ask": {"ask"}, "re": {"re", "text"}, "info": {"info"}}   # an act's forms and their keys
RETIRED_VERBS = ("done", "reply", "escalate", "note")   # the verbs of before -- an answer's until team 0.33.0, the
#                                                  principal's note until 0.47.0 --: read in a journal alone
POST_FLAGS = {"message": True, "to": True, "task": True, "reply": True, "stop": False, "as": True, "name": True,
              "every": True, "context": True, "description": True, "no-tick": False, "vector": True, "ask": False}
INBOX_FLAGS = {"seen": False, "json": False, "id": True}
RESUME_FLAGS = {"task": True, "message": True, "recurrence": True, "as": True, "no-tick": False, "quota": False,
                "member": True, "to": True}
RESUMED = "the task resumes"                     # the note of a resume that names no message
ACT_OPENED = re.compile(r'\{\s*"(?:do|ask|re|info)"\s*:')   # an object that opens on the key of a form


class Refused(Exception):
    """An act the tick refuses to route, said to the member: its form broken (`act_formed`, `candidates_of`) or its
    sense wrong -- a member nobody declared, a `do` off the edges, a `re` citing a message never delivered to the
    member."""


@dataclass(frozen=True, eq=False)
class TaskBorn(Body):
    """`task`: a task is born -- posted by the owner, opened by a recurrence or a ceremony; `sender` is the key
    `from`."""
    KIND = "task"
    KEYS = {"sender": "from"}
    task: str
    sender: str | None = None
    to: str | None = None
    name: str | None = None
    text: str | None = None
    ceremony: str | None = None
    period: str | None = None
    recurrence: str | None = None
    now: bool | None = None
    by: str | None = None
    vectors: list | None = None
    context: int | None = None


@dataclass(frozen=True, eq=False)
class Post(Body):
    """`post`: one message of a task -- a do, an ask, a re, an info, a notice, a stop; `sender` is the key `from`. The
    keys a post carries at times: `re` the message it answers, `by` who wrote it in a member's place, `about` the
    member a notice speaks of, the flags of the tick's answers and notices."""
    KIND = "post"
    KEYS = {"sender": "from"}
    task: str | None = None
    sender: str | None = None
    to: str | None = None
    verb: str | None = None
    text: str | None = None
    re: int | None = None
    by: str | None = None
    about: str | None = None
    info: bool | None = None
    vector: str | None = None
    suspected: bool | None = None
    returned: bool | None = None
    house: bool | None = None
    halted: bool | None = None
    cause: str | None = None
    relaunch: bool | None = None
    timer: bool | None = None
    why: str | None = None


@dataclass(frozen=True, eq=False)
class Done(Body):
    """`done`: the root answered the opening -- the task resolves on its result."""
    KIND = "done"
    task: str
    result: object = None


@dataclass(frozen=True, eq=False)
class Stopped(Body):
    """`stopped`: the task stops, whoever holds it."""
    KIND = "stopped"
    task: str | None = None
    by: str | None = None


@dataclass(frozen=True, eq=False)
class Returned(Body):
    """`returned`: a message never delivered goes back to its author."""
    KIND = "returned"
    message: int
    to: str | None = None


@dataclass(frozen=True, eq=False)
class Resumed(Body):
    """`resumed`: `team resume --task` takes the task back; `sender` is the key `from` -- what held it."""
    KIND = "resumed"
    KEYS = {"sender": "from"}
    task: str | None = None
    by: str | None = None
    sender: list | None = None


@dataclass(frozen=True, eq=False)
class Deferred(Body):
    """`deferred`: a member due, its share spent by the wake-ups under way -- `reserved` what they hold."""
    KIND = "deferred"
    agent: str | None = None
    task: str | None = None
    reserved: float | None = None


@dataclass(frozen=True, eq=False)
class InboxRead(Body):
    """`inbox-read`: one message the owner marked read."""
    KIND = "inbox-read"
    message: int | None = None


@dataclass(frozen=True, eq=False)
class InboxSeen(Body):
    """`inbox-seen`: the owner's cursor -- every message up to `upto` seen."""
    KIND = "inbox-seen"
    upto: int | None = None


@dataclass(frozen=True, eq=False)
class Terminal(Body):
    """`terminal`, of a journal written before team 0.33.0: the member terminal on the task."""
    KIND = "terminal"
    agent: str
    task: str


TASK_BODIES: tuple = (TaskBorn, Post, Done, Stopped, Returned, Resumed, Deferred, InboxRead, InboxSeen,
                      Terminal)   # the bodies of this domain's kinds: `journal/model.py` reads them


@dataclass(frozen=True, eq=False)
class Task(Typed):
    """ONE task of the team, as its fold made it: who opened it for whom, its text, its state and when it ended, its
    messages, the ceremony or the recurrence it comes from, its cost and its last event; `sender` is the key `from`.
    It keeps the dictionary it comes from (`json()`): a key the fold never wrote stays absent."""
    id: str | None = None
    sender: str | None = None
    to: str | None = None
    text: str | None = None
    state: str | None = None
    messages: list | None = None
    ceremony: str | None = None
    period: str | None = None
    name: str | None = None
    at: str | None = None
    ended: str | None = None
    recurrence: str | None = None
    context: int | None = None
    vectors: list | None = None
    by: str | None = None
    cost: float | None = None
    last: dict | None = None
    held: dict = field(default_factory=dict, repr=False)

    @staticmethod
    def of(held: dict) -> "Task":
        named = TASK_FIELDS
        return Task(**{key: value for key, value in held.items() if key in named},
                    sender=held.get("from"), held=held)

    def json(self) -> dict:
        return self.held


TASK_FIELDS = frozenset(one.name for one in fields(Task)) - {"sender", "held"}   # the keys a task names by their own name


@dataclass(frozen=True, eq=False)
class TaskPart(Part):
    """The part `task` of the team's state -- the tasks: their messages and debts, the delegations and terminals,
    what was delivered and returned, the owner's box. `tasks` holds a `Task` per task, born here from the dictionary
    the fold wrote; the events kept (`messages`, `done`, `deferred`) are the events read, a snapshot's the dictionaries
    it kept."""
    tasks: dict[str, Task]                 # task id -> the task
    messages: dict[int, "Event"]           # message id -> its `post`
    delivered: set[int]
    terminals: set[tuple]                  # (member, task)
    delegations: list[dict]
    done: dict[str, "Event"]               # task id -> its `done`
    returned: set[int]
    deferred: list["Event"]                # the `deferred` events
    returned_to: dict[int, str]
    stops: dict[str, list]                 # member -> the ids of the stops posted to it
    seen: int
    read: set[int]
    resumed: dict[str, int]                # task id -> the id of its last `resumed`
    debts: dict[int, object]               # message id -> None (open), the answer's id, or "closed"

    @classmethod
    def of(cls, state: dict) -> "TaskPart":
        made = {one.name: state.get(one.name) for one in fields(cls)}
        made["tasks"] = {key: Task.of(one) if type(one) is dict else one for key, one in (made["tasks"] or {}).items()}
        return cls(**made)
