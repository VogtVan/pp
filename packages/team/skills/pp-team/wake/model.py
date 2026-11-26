"""The `wake` domain, layer `model`: what a wake-up is, held as plain values.

A definition belongs here when it is data about the wake-ups of a team's members and does nothing: the names of the
files the tick and the followers keep beside the journal, the words of the head of a member's message, the bounds of the
retries, the halts, the suspicion and the history, the shape of a refusal's code, the flags of the verbs that read the
answers or reset a member, or a type that carries one of them. Nothing here reads the disk, the clock or the
environment.

It also holds the bodies of the wake-ups' twelve kinds of event -- `WakeIntent`, `WakeLaunched`, `WakeEnded`,
`WakeFailed`, `WakeHalted`, `WakeKilled`, `WakeRefused`, `WakeRouted`, `QuotaReached`, `QuotaLifted`, `RunRenewed` and
`RunReset` -- in the tuple `WAKE_BODIES` that `journal/model.py` reads to decode the journal. A field a line does not
carry is `None`, an old journal's missing keys among them -- but for the fields the wake-ups' fold read without a
condition, which are required: the `tag` of every kind the fold indexes by it, the `agent` of `wake-killed`, the
`agent` and the `task` of `wake-intent`; a line without them stops the replay. The key `name-refused` of `wake-launched` is no Python name: the body's table `KEYS`
reads it in the field `name_refused`, and its `json()` gives it back under `name-refused`.

And it holds the wake-ups' part of the team's state, a frozen class whose fields are typed by what they hold. The events
the part keeps -- the intents and the launches by their tag, the ends, the failures, the halts -- are the events read,
or after a snapshot the dictionaries it kept; `gone` stays `None` until a face gives it.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from house.model import Body, Part

TICK_MARK = "tick.pending"       # beside the journal: a tick asked while another played
TICK_CURSOR = "tick.cursor"      # beside the journal: how far the tick read messages.jsonl, the tags it keeps
FOLLOW_LOG = "follow.log"        # beside the journal: what the followers of the launches said
OWED = "you owe an answer"                       # what the head says of a message whose debt stands
MEMBER_TYPE = "member"                           # the profile `agent add` gives a member born by a start
DEFAULT_RETRIES = 1                              # wake-ups played again after a dead one, unless TEAM.md says
HALT_AFTER = 3                                   # the same failure in a row of a member on a task: launched there no more
HARNESS_SPARED = ("quota", "budget-spent", "interrupted")   # the errors of a kept response that are no harness error
ANSWERED_FOR = {                                 # what the head says of a `re` the tick wrote in a member's place, by its cause:
    "returned": "[the team wrote this answer in {member}'s place: {member} never received your message #{id} and will "
                "not receive it. The message is closed: if you still need it, send it again in a new message, to "
                "another member now or to {member} once it answers again]",
    "suspected": "[the team wrote this answer in {member}'s place: {member} was given your message #{id} and did not "
                 "answer it. The message is closed: if you still need it, send it again in a new message, to "
                 "another member now or to {member} once it answers again]",
    "failed": "[the team wrote this answer in {member}'s place: the launch of {member} that carried your message "
              "#{id} failed, and the next line says why. The message is closed: if you still need it, send it again "
              "in a new message]"}
#                                                  a message no intent carried, a message an intent carried, a launch that failed
HANDED_BACK = "[your message #{id}, as you wrote it:]"   # the head line of the message such a `re` cites, its text under it
HANDED_BACK_VECTOR = "[your message #{id}, as you wrote it, with its vector {vector}:]"   # the same, for a message that carries a vector
DEFAULT_SUSPECT_MAX = 600                        # seconds: the longest interval a suspected member waits, unless TEAM.md says
REFUSAL_CODE = re.compile(r"^[\w.-]+: ([a-z0-9]+(?:-[a-z0-9]+)*)(?: --|$)", re.M)   # a refusal's head: its code
RESPONSES_FLAGS = {"since": True, "agent": True, "task": True, "last": True, "json": False}
RESET_FLAGS = {"member": True}
HISTORY_CHARS = 200                              # a message's text in a reopened run's history
RUN_NAME_CHARS = 60                              # a run's name, as `agent name` bounds it


@dataclass(frozen=True, eq=False)
class WakeIntent(Body):
    """`wake-intent`: the tick wakes a member on a task -- the messages the launch carries, the run it resumes."""
    KIND = "wake-intent"
    tag: str
    agent: str
    task: str
    path: str | None = None
    run: str | None = None
    messages: list | None = None
    continued: bool | None = None
    beat: int | None = None
    relance: str | None = None
    allowance: float | None = None


@dataclass(frozen=True, eq=False)
class WakeLaunched(Body):
    """`wake-launched`: the launcher started the run of an intent; `name_refused` is the key `name-refused`."""
    KIND = "wake-launched"
    KEYS = {"name_refused": "name-refused"}
    tag: str
    agent: str | None = None
    run: str | None = None
    pid: int | None = None
    launch: int | None = None
    model: str | None = None
    provider: str | None = None
    space: str | None = None
    name_refused: str | None = None



@dataclass(frozen=True, eq=False)
class WakeEnded(Body):
    """`wake-ended`: a launch ended on a response -- the run's state, its cost, the rank of its flow, its context."""
    KIND = "wake-ended"
    tag: str
    agent: str | None = None
    run: str | None = None
    launch: int | None = None
    state: str | None = None
    cost: float | None = None
    flow: int | None = None
    context: dict | None = None
    tokens: int | None = None


@dataclass(frozen=True, eq=False)
class WakeFailed(Body):
    """`wake-failed`: a launch that failed -- its reason, final or not, the run it leaves, a refusal of the house."""
    KIND = "wake-failed"
    tag: str
    agent: str | None = None
    task: str | None = None
    final: bool | None = None
    reason: str | None = None
    cost: float | None = None
    run: str | None = None
    flow: int | None = None
    state: str | None = None
    harness_rc: int | None = None
    house: bool | None = None
    vectors: list | None = None
    space: str | None = None
    share: object = None
    spent: object = None


@dataclass(frozen=True, eq=False)
class WakeHalted(Body):
    """`wake-halted`: the same failure in a row of a member on a task: launched there no more."""
    KIND = "wake-halted"
    agent: str | None = None
    task: str | None = None
    reason: str | None = None
    count: int | None = None


@dataclass(frozen=True, eq=False)
class WakeKilled(Body):
    """`wake-killed`: `team stop --kill` ended a launch under way."""
    KIND = "wake-killed"
    tag: str
    agent: str
    task: str | None = None
    run: str | None = None
    pid: int | None = None


@dataclass(frozen=True, eq=False)
class WakeRefused(Body):
    """`wake-refused`: an act read in a launch's flow that the team refused, at its rank, and why."""
    KIND = "wake-refused"
    tag: str
    agent: str | None = None
    run: str | None = None
    launch: int | None = None
    words: int | None = None
    line: int | None = None
    why: str | None = None


@dataclass(frozen=True, eq=False)
class WakeRouted(Body):
    """`wake-routed`: an act read in a launch's flow and routed, at its rank; `nowhere` on a stopped task."""
    KIND = "wake-routed"
    tag: str
    agent: str | None = None
    run: str | None = None
    launch: int | None = None
    words: int | None = None
    line: int | None = None
    nowhere: bool | None = None


@dataclass(frozen=True, eq=False)
class QuotaReached(Body):
    """`quota-reached`: a launch ended on the provider's usage limit -- the member held until `until`."""
    KIND = "quota-reached"
    tag: str
    agent: str | None = None
    task: str | None = None
    run: str | None = None
    launch: int | None = None
    state: str | None = None
    cost: float | None = None
    flow: int | None = None
    until: str | None = None
    said: str | None = None


@dataclass(frozen=True, eq=False)
class QuotaLifted(Body):
    """`quota-lifted`: `team resume --quota` -- the owner lifts the provider's limit of the members named."""
    KIND = "quota-lifted"
    by: str | None = None
    members: list | None = None


@dataclass(frozen=True, eq=False)
class RunRenewed(Body):
    """`run-renewed`: the run detached from its carrier before a wake-up -- why, and what it measured."""
    KIND = "run-renewed"
    member: str | None = None
    recurrence: str | None = None
    task: str | None = None
    run: str | None = None
    why: str | None = None
    was: dict | None = None
    now: dict | None = None
    used: float | None = None
    limit: int | None = None


@dataclass(frozen=True, eq=False)
class RunReset(Body):
    """`run-reset`: `team reset` forgot one run of the member."""
    KIND = "run-reset"
    member: str | None = None
    run: str | None = None


WAKE_BODIES: tuple = (WakeIntent, WakeLaunched, WakeEnded, WakeFailed, WakeHalted, WakeKilled, WakeRefused, WakeRouted,
                      QuotaReached, QuotaLifted, RunRenewed, RunReset)   # this domain's bodies: `journal/model.py` reads them


@dataclass(frozen=True, eq=False)
class WakePart(Part):
    """The part `wake` of the team's state -- the wake-ups: intents, launches, routes, ends, failures, kills, the
    runs by carrier, the flows, the quotas and the halts -- and `gone`, the launches nobody holds, which a face
    alone gives (`state.but(gone=...)`) and which is no key of the state before."""
    intents: dict[str, "Event"]            # tag -> its `wake-intent`
    launched: dict[str, "Event"]           # tag -> its `wake-launched`
    ended: set[str]                        # the tags of the launches over
    failures: dict[tuple, int]             # (member, task) -> its failures counted
    runs: dict[str, dict]                  # member -> carrier -> the run it holds there
    killed: set[str]                       # the tags of the launches killed
    kills: set[tuple]                      # (member, task) of a kill
    ends: list["Event"]                    # the `wake-ended` events
    fails: list["Event"]                   # the `wake-failed` events
    reset: dict[str, int]                  # member -> the id of its last `run-reset`
    fell: set[tuple]                       # (member, task) whose terminal a final failure wrote
    routed: dict[str, int]                 # tag -> the rank of its flow the acts reached
    flow: dict[str, int]                   # run -> the rank of its flow read
    standing: set[tuple]                   # (member, task) whose run stands
    house: set[str]                        # the tags of the launches the house refused
    context: dict[str, dict | None]        # member -> the context its last exchange left
    halts: list["Event"]                   # the `wake-halted` events that hold
    quotas: dict[str, dict]                # member -> the provider's limit that holds it
    gone: set | None = None                # the launches nobody holds: a face's alone
