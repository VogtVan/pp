"""An exchange: the message sent and the response kept, as their records write them, the account of its launches
and its issue."""
from __future__ import annotations

from dataclasses import dataclass, field, replace

from model.cost import Budget, Sums
from model.material import Push, Workdir
from model.policy import Policy
from model.record import _read, _written, only_named
from model.vector import Mount
from model.words import ANSWER_BOUND

TAIL = 300                      # the characters kept of what a harness said last on its stderr


@dataclass(frozen=True)
class Said:
    """What the model said once in an exchange: the `launch` it said it in, its `text`. `keys` and `kept` stand
    for words read alone: what gives them back as they were."""
    launch: int | None = None
    text: str | None = None
    keys: tuple[str, ...] | None = None
    kept: tuple = ()

    @staticmethod
    def of(words) -> "Said | None":
        """-> the words an item of a response's `words` carries, a key it does not name kept for `json()`;
        None when the item is no mapping."""
        return Said(**_read(Said, words)) if isinstance(words, dict) else None

    def json(self) -> dict:
        """-> the item of `words`: the one read, as it was; the one composed, `launch` then `text`."""
        return _written(self)


@dataclass(frozen=True)
class Final:
    """The last message of ONE launch: the `launch` it ended, its `chars` and its `text` -- its blanks stripped;
    the hand-back mark alone counts no characters and has no text (None), blanks alone an empty text. `keys` and
    `kept` stand for a final read alone: what gives it back as it was."""
    launch: int | None = None
    chars: int | None = None
    text: str | None = only_named()
    keys: tuple[str, ...] | None = None
    kept: tuple = ()

    @staticmethod
    def of(final) -> "Final | None":
        """-> the final an item of a response's `finals` carries; None when the item is no mapping."""
        return Final(**_read(Final, final)) if isinstance(final, dict) else None

    def json(self) -> dict:
        """-> the item of `finals`: the one read, as it was; the one composed, `launch`, `chars`, then `text` when
        it has one."""
        return _written(self)

    def over(self) -> bool:
        """-> whether the last message held more than `ANSWER_BOUND` characters: an overrun."""
        return int(self.chars or 0) > ANSWER_BOUND


@dataclass(frozen=True)
class Message:
    """One line of `messages.jsonl`: the hour, who sent it (`from`), the agent it is sent `to`, the `run`, the
    `message` (null for an exchange without one), the `policy` of its launch; `conducted` false for an exchange
    the house does not conduct, the `tag` and the `pid` of a wake-up that names them. `keys` and `kept` stand for
    a line read alone: what gives it back as it was."""
    at: str | None = None
    sender: str | None = field(default=None, metadata={"key": "from"})
    to: str | None = None
    run: str | None = None
    message: str | None = None
    policy: Policy = field(default_factory=Policy, metadata={"of": Policy.of})
    conducted: bool | None = only_named()
    tag: str | None = only_named()
    pid: int | None = only_named()
    keys: tuple[str, ...] | None = None
    kept: tuple = ()

    @staticmethod
    def of(line: dict) -> "Message":
        """-> the message a line of `messages.jsonl` carries; a key it does not name is kept for `json()`."""
        return Message(**_read(Message, line))

    def json(self) -> dict:
        """-> the line `messages.jsonl` holds: the one read, as it was; the one composed, `at`, `from`, `to`,
        `run`, `message` and `policy` always, `conducted`, `tag` and `pid` when named."""
        return _written(self)


@dataclass(frozen=True)
class Response:
    """One line of `responses.jsonl`: the hour, the `agent`, the `run`, the `index` of the response in its run,
    the `response` composed of the launches' words (null when the model said nothing), the cost and the session's
    cumul, the `launches`, the `denials`, the `error` and the harness's exit code; the `budget` a cap stopped, the
    `quota` a provider's limit said, `conducted` false for an exchange the house does not conduct, the `flow`'s
    sums, `tokens_sent` what the calls of its launches sent the model (None when the adapter measures none),
    the output `pending` for the next wake-up, the `words` -- the productions pp took --, the `finals` -- the
    last message of each launch, its length and its text -- and the `overruns` among them, the `model` and the
    `effort` asked.
    `keys` and
    `kept` stand for a line read alone: what gives it back as it was."""
    at: str | None = None
    agent: str | None = None
    run: str | None = None
    index: int | None = None
    response: str | None = None
    cost_usd: float | None = None
    session_cost_usd: float | None = None
    launches: int | None = None
    denials: list | None = None
    error: str | None = None
    harness_rc: int | None = None
    budget: dict | None = only_named()
    quota: dict | None = only_named()
    conducted: bool | None = only_named()
    flow: Sums | None = field(default=None, metadata={"of": Sums.of})
    tokens_sent: int | None = None
    pending: str | None = only_named()
    words: tuple | None = field(default=None, metadata={"each": Said.of})
    finals: tuple | None = field(default=None, metadata={"each": Final.of})
    overruns: int | None = None
    model: str | None = None
    effort: str | None = None
    keys: tuple[str, ...] | None = None
    kept: tuple = ()

    @staticmethod
    def of(line: dict) -> "Response":
        """-> the response a line of `responses.jsonl` carries; a key it does not name is kept for `json()`."""
        return Response(**_read(Response, line))

    def json(self) -> dict:
        """-> the line `responses.jsonl` holds: the one read, as it was; the one composed, every key but
        `budget`, `quota`, `conducted` and `pending`, written when named."""
        return _written(self)


@dataclass(frozen=True)
class Stop:
    """A provider's stop, as the adapter read it in a launch's output: its `kind` (`quota`, a usage limit), the
    hour it lasts `until` (None when the provider names none) and what the provider `said`."""
    kind: str = "quota"
    until: str | None = None
    said: str = ""

    @staticmethod
    def of(answer) -> "Stop | None":
        """-> the stop an adapter's answer says under `stop`; None when it says none, or says it in another shape
        than a quota's: the kind `quota`, what the provider said, an hour or none."""
        stop = answer.get("stop") if isinstance(answer, dict) else None
        if not (isinstance(stop, dict) and stop.get("kind") == "quota" and isinstance(stop.get("said"), str)
                and (stop.get("until") is None or isinstance(stop.get("until"), str))):
            return None
        return Stop(kind="quota", until=stop.get("until"), said=stop["said"])


@dataclass(frozen=True)
class Launch:
    """What the adapter read of ONE launch that answered: the `session` the harness lives in, its `cost_usd` as
    the adapter counts it, the `denials` in the order they came, the `error` the harness said, and the provider's
    `stop` when the adapter read one."""
    session: str | None = None
    cost_usd: float | None = None
    denials: tuple = ()
    error: str | None = None
    stop: Stop | None = None

    @staticmethod
    def of(answer: dict, stop: Stop | None = None) -> "Launch":
        """-> the launch the engine's face read (`adapters.answer`: its four keys, the session owed), the
        provider's `stop` beside."""
        return Launch(session=answer["session"], cost_usd=answer.get("cost_usd"),
                      denials=tuple(answer.get("denials") or ()), error=answer.get("error"), stop=stop)


@dataclass(frozen=True)
class Account:
    """The account of the launches of ONE exchange, summed launch after launch: what the adapter read of the last
    one that answered, the exit code of the last one that ended and the tail of its stderr (None and nothing
    while none ended) -- never its stdout, where its last message stands --, the launches played, their cost summed and the session's cumul, the denials and the stray
    runs in the order they came, whether the bound of launches or the run's cap stopped the loop, whether a SIGINT
    ended it, the session, the flow's sums,
    the tokens its calls sent the model, words and finals as they stood when the loop ended, the output the next
    wake-up owes its launch."""
    answered: Launch | None = None
    harness_rc: int | None = None
    harness_stderr: str = ""
    launches: int = 0
    cost_usd: float | None = None
    session_cost_usd: float | None = None
    denials: tuple = ()
    strays: tuple[str, ...] = ()
    spent: bool = False
    budget_spent: bool = False
    interrupted: bool = False
    session: str | None = None
    flow: Sums = field(default_factory=Sums)
    tokens_sent: int | None = None
    words: tuple = ()
    finals: tuple = ()
    pending: str | None = None

    def ended(self, returncode: int, stderr: str) -> "Account":
        """-> the account once a launch ended: its exit code and the tail of its stderr."""
        return replace(self, harness_rc=returncode, harness_stderr=stderr.strip()[-TAIL:])


@dataclass(frozen=True)
class Issue:
    """The issue of ONE exchange: `dry` alone for a dry run; else the run's `key`, `kept` the response's record
    line (None when nothing was kept: `reason` says why), the `account` of its launches, `said` (`parked`,
    `standing`, `stopped`, `interrupted`, `unconducted`), `arrived`, the `stack` the run stands on, its
    `exchanges`, `standing` (a standing run taken up), `sent_back` (the material's push), the `bound` of
    launches, `interrupted`, `after` (the run's last wake-up was interrupted) and the run's `budget` under a cap."""
    dry: bool = False
    key: str | None = None
    kept: Response | None = None
    reason: str | None = None
    account: Account = field(default_factory=Account)
    said: str = ""
    arrived: bool = False
    stack: str = ""
    exchanges: int = 0
    standing: bool = False
    sent_back: Push | None = None
    bound: int = 0
    interrupted: bool = False
    after: bool = False
    budget: Budget | None = None


@dataclass(frozen=True)
class Terms:
    """What the judgments of ONE exchange settled before any launch: whether it is an `opening` (no run yet)
    and `bare` (an exchange the house does not conduct); the `policy` of its launches, the `beat` of its
    heartbeat and the `bound` of its launches; the `head` of a caller's command, or the `provider`; the
    `grammar` its output is read in and the `scope` its cost is read in; whether the launch declares the
    `marble`; the `cap` of the outputs served at the prompt; the root of `documents` asked; what the run
    `spent` so far; the house's `slug`; whether the call has `taken` the launcher's lock itself; the repository
    to `work` on, by its path; the vectors `due` and their `mounts`; the `session` a resume reopens; the material's
    `entry` -- the run's own, or the one a clone will place --; the git `identity` the harness gets with a
    material, pairs of a variable and its value; the `packages` an opening is composed with."""
    opening: bool
    bare: bool
    policy: Policy
    beat: int
    bound: int
    head: tuple[str, ...]
    provider: str | None
    grammar: str
    scope: str | None
    marble: bool
    cap: int | None
    documents: str | None
    spent: float
    slug: str
    taken: bool
    work: str | None
    due: tuple[str, ...]
    mounts: tuple[Mount, ...]
    session: str | None
    entry: Workdir | None
    identity: tuple
    packages: str | None


@dataclass(frozen=True)
class Footing:
    """Where ONE exchange stands once opened or taken up: the run's `key`; the first `output` its launches
    read; whether the run was `standing`, taken up where a wake-up left it; whether the exchange comes `after`
    an interrupted wake-up; the `number` of the exchange in its run; the `neighbours`, the agent's other runs
    under way -- a key, its hour, the head of its message each --; the material's `entry` as it stands, the
    clone placed at an opening."""
    key: str
    output: str
    standing: bool
    after: bool
    number: int
    neighbours: tuple
    entry: Workdir | None
