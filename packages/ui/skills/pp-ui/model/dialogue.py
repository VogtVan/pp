"""dialogue -- the typed state of a CONVERSATION with an agent, read from the flow of
`agent chat --json`: pure dataclasses, no I/O, no Textual, no import from any other
module of the post. An event is what the flow said, by its `kind`; a turn is one exchange
(the principal's message, the launches it took, its verdict); the transcript keeps them
in order and deduces the turns. A thread is one open conversation as the post's column
shows it -- its agent, its run, its state, the hour of its last event, what the operator
has not read, its title --, and the dialogue is the threads the post holds and the active one."""
from __future__ import annotations

import json
from dataclasses import dataclass, field

HOUSE = "house"                    # the voice of what the house itself says
VOICES: dict[str, str] = {         # a kind -> the voice that speaks it; any other kind is the house's
    "principal": "principal",
    "agent": "agent",
    "conduction": "conduction",
    "step": "step",
    "conduct": HOUSE,              # the house says whether the next exchanges are conducted
    "package": HOUSE,              # the house says a package of the run in or out of its play
}
UNREADABLE = "unreadable"          # the face's own: a line of the flow that does not read
ENDED = "ended"                    # the face's own: the flow ended, with the exit code
OWN = (UNREADABLE, ENDED)


def voice_of(kind: str) -> str:
    """-> the voice a kind speaks with; a kind nobody knows is the house's, never an error."""
    return VOICES.get(kind, HOUSE)


def command_of(line: object) -> dict:
    """-> the command a `refused` names in its `line` -- the JSON object the post itself wrote to the
    verb --, `{}` when the line is no such object."""
    try:
        found = json.loads(line) if isinstance(line, str) else None
    except ValueError:
        return {}
    return found if isinstance(found, dict) else {}


@dataclass(frozen=True)
class Event:
    """One line of the flow: its `kind`, `at` and `run` taken out, every other field kept
    as the flow said it."""
    kind: str
    at: str
    run: str
    fields: dict

    @staticmethod
    def read(line: str) -> "Event":
        """-> the event a line of the flow carries, or an `unreadable` event keeping the line."""
        try:
            data = json.loads(line)
        except ValueError:
            data = None
        if not isinstance(data, dict) or not data.get("kind"):
            return Event(UNREADABLE, "", "", {"line": line})
        rest = {key: value for key, value in data.items() if key not in ("kind", "at", "run")}
        return Event(str(data["kind"]), str(data.get("at") or ""), str(data.get("run") or ""), rest)

    @property
    def voice(self) -> str:
        return voice_of(self.kind)

    @property
    def own(self) -> bool:
        """Whether the face itself said this event, not the flow."""
        return self.kind in OWN


@dataclass
class Turn:
    """One exchange: the principal's message, then what each launch brought (`conduction`
    and `agent` events, in order), the steps of the run, the response and the verdict. A
    turn of HISTORY comes from `agent exchanges --json` -- what the house kept --, not from the flow:
    the message, the answer kept, its cost and its launches -- closed by definition."""
    exchange: int
    message: str
    launches: list[Event] = field(default_factory=list)
    steps: list[Event] = field(default_factory=list)
    response: Event | None = None
    verdict: Event | None = None
    history: bool = False
    at: str = ""
    answer: str | None = None
    cost_usd: float | None = None
    played: int | None = None        # the launches a history turn took
    error: str | None = None

    @property
    def state(self) -> str:
        return str(self.verdict.fields.get("state", "")) if self.verdict else ""

    @property
    def done(self) -> bool:
        return self.history or self.verdict is not None


@dataclass
class Transcript:
    """The events in order, the turns deduced from them: a `principal` event opens a turn,
    the launches, steps, response and verdict that follow belong to it."""
    events: list[Event] = field(default_factory=list)
    turns: list[Turn] = field(default_factory=list)

    def add(self, event: Event) -> None:
        self.events.append(event)
        if event.kind == "principal":
            number = event.fields.get("exchange")
            self.turns.append(Turn(int(number) if isinstance(number, int) else len(self.turns) + 1,
                                   str(event.fields.get("text", ""))))
            return
        if not self.turns:
            return
        turn = self.turns[-1]
        if event.kind in ("conduction", "agent"):
            turn.launches.append(event)
        elif event.kind == "step":
            turn.steps.append(event)
        elif event.kind == "response":
            turn.response = event
        elif event.kind == "verdict":
            turn.verdict = event

    @staticmethod
    def history(exchanges: list[dict]) -> list[Turn]:
        """-> the run's past exchanges (the objects of `agent exchanges --json`) as turns of history -- what a run
        taken up shows first, the turns of the live flow untouched."""
        turns = []
        for one in exchanges:
            number = one.get("index")
            cost, played = one.get("cost_usd"), one.get("launches")
            turns.append(Turn(int(number) if isinstance(number, int) else len(turns) + 1,
                              str(one.get("message", "")), history=True, at=str(one.get("at") or ""),
                              answer=one.get("response") if isinstance(one.get("response"), str) else None,
                              cost_usd=float(cost) if isinstance(cost, (int, float)) else None,
                              played=played if isinstance(played, int) else None,
                              error=str(one["error"]) if one.get("error") else None))
        return turns

    @property
    def current(self) -> Turn | None:
        """The exchange under way, None when the conversation waits."""
        return self.turns[-1] if self.turns and not self.turns[-1].done else None


SPEAKING = ("agent", "verdict", "refused", ENDED)   # the kinds that count as unread on a background thread


@dataclass
class Thread:
    """One open conversation, as the column of the post shows it: the agent, the run (known at
    `opened`), its transcript, its state, the hour of its last event, the events the operator
    has not read while another thread was active, and its title -- the first message."""
    agent: str
    run: str = ""
    transcript: Transcript = field(default_factory=Transcript)
    state: str = "opening"
    last_at: str = ""
    unread: int = 0
    title: str = ""
    name: str = ""                   # the run's name: the one `agent name` keeps, or the one typed for a run opening
    naming: str = ""                 # a name typed before the run was opened: played once `opened` says the key
    provider: str = ""               # the harness the run plays, as `ready` and `opened` say it
    policy: dict = field(default_factory=dict)   # the policy in force: `ready`, `opened`, then each `policy` after a `set`
    conducted: bool = True           # whether the next exchanges are conducted: `ready`, `opened`, then each `conduct`
    packages: list[dict] | None = None   # the run's packages `{name, on}` as `ready`, `opened` and `package` say them; None unsaid
    cap: dict | None = None          # the run's cap `{set, applied}` as `ready` and `opened` say it; None unsaid
    budget: dict | None = None       # the run's budget `{cap, spent, left}` as `ready`, `opened` and `verdict` say
                                     # it; None without a cap or unsaid
    turn_at: str = ""                # the hour the turn under way began: its principal's line
    pending: dict[str, bool] = field(default_factory=dict)   # the switches sent and not played yet, `{name: on}`:
                                     # `ready` says them, a `package` with `pending` adds or lifts one, a refused
                                     # `package` lifts its own
    team: str = ""                   # a run a member of a team holds, READ in its tab: the team, and the member
    member: str = ""

    @property
    def read_only(self) -> bool:
        """Whether the thread is the run of a member of a team, read: nothing is sent to it."""
        return bool(self.team)

    @property
    def label(self) -> str:
        """The title of the thread's tab: the name chosen, else `<agent> · <key>`, else the agent."""
        if self.name:
            return self.name
        return f"{self.agent} · {self.run}" if self.run else self.agent

    def take(self, event: Event, active: bool = True) -> None:
        """Takes one event of the flow: the transcript grows, the run, the state, the hour and
        the title follow; a speaking event on a thread that is not active counts as unread."""
        self.transcript.add(event)
        f = event.fields
        if event.run and not self.run:
            self.run = event.run
        if event.at:
            self.last_at = event.at
        if event.kind in ("ready", "opened"):       # the run as the flow judged it: before any message, then at each opening
            if event.kind == "opened":
                self.state = f"exchange {f.get('exchange', '?')}"
            if isinstance(f.get("provider"), str):
                self.provider = f["provider"]
            if isinstance(f.get("policy"), dict):
                self.policy = dict(f["policy"])
            if isinstance(f.get("packages"), list):
                self.packages = [dict(one) for one in f["packages"] if isinstance(one, dict)]
            if isinstance(f.get("conducted"), bool) and (event.kind == "ready" or f["conducted"] is False):
                self.conducted = f["conducted"]
            if isinstance(f.get("cap"), dict):
                self.cap = dict(f["cap"])
            if "budget" in f:
                self.budget = dict(f["budget"]) if isinstance(f["budget"], dict) else None
            if event.kind == "ready" and isinstance(f.get("pending"), list):
                self.pending = {str(one["name"]): one.get("on") is True for one in f["pending"]
                                if isinstance(one, dict) and "name" in one}
        elif event.kind == "conduct":
            if isinstance(f.get("on"), bool):
                self.conducted = f["on"]
        elif event.kind == "package":
            if isinstance(f.get("packages"), list):
                self.packages = [dict(one) for one in f["packages"] if isinstance(one, dict)]
            if isinstance(f.get("name"), str):
                if f.get("pending") is True:
                    self.pending[f["name"]] = f.get("on") is True
                else:
                    self.pending.pop(f["name"], None)
        elif event.kind == "refused":
            asked = command_of(f.get("line"))
            if asked.get("kind") == "package" and isinstance(asked.get("name"), str):
                self.pending.pop(asked["name"], None)
        elif event.kind == "policy":
            if isinstance(f.get("policy"), dict):
                self.policy = dict(f["policy"])
        elif event.kind == "principal":
            self.state = f"exchange {f.get('exchange', '?')}"
            self.turn_at = event.at
            if not self.title:
                self.title = str(f.get("text", ""))
        elif event.kind in ("conduction", "agent"):
            self.state = f"exchange {f.get('exchange', '?')} · launch {f.get('launch', '?')}"
        elif event.kind == "verdict":
            self.state = str(f.get("state", "")) or "verdict"
            if "budget" in f:
                self.budget = dict(f["budget"]) if isinstance(f["budget"], dict) else None
        elif event.kind == "waiting":
            self.state = "waiting"
        elif event.kind == ENDED:
            self.state = f"ended rc {f.get('rc')}"
        if not active and event.kind in SPEAKING:
            self.unread += 1

    @property
    def busy(self) -> bool:
        """Whether a turn is under way: from the principal's line to the verdict, unless the flow ended."""
        return self.transcript.current is not None and not self.state.startswith(ENDED)

    @property
    def params(self) -> list[str]:
        """What the run plays, as the status says it: provider, model, budget, effort -- '' where unknown; the
        budget's figure is the policy's cap, which the gauge of `budget` replaces once the flow says it."""
        budget = self.policy.get("max_budget_usd")
        return [self.provider, str(self.policy.get("model") or ""),
                f"{float(budget):g} USD" if isinstance(budget, (int, float)) else "", str(self.policy.get("effort") or "")]

    @property
    def hour(self) -> str:
        """HH:MM:SS of the last event, '' before any."""
        return self.last_at[11:19] if len(self.last_at) >= 19 else ""

    @property
    def line(self) -> str:
        """What the column says of this thread: `<agent> · run <key> · <state> · HH:MM:SS`, then
        the unread count when any, then the title when any."""
        parts = [self.agent, f"run {self.run}" if self.run else "no run yet", self.state]
        if self.hour:
            parts.append(self.hour)
        if self.unread:
            parts.append(f"{self.unread} unread")
        if self.title:
            parts.append(self.title)
        return " · ".join(parts)


@dataclass
class Dialogue:
    """The conversations the post holds, in the order they were opened, and the ACTIVE one --
    the one the transcript shows; `-1` while none is open."""
    threads: list[Thread] = field(default_factory=list)
    active: int = -1

    def open(self, thread: Thread) -> int:
        """-> the index of the thread added; the first one opened becomes active."""
        self.threads.append(thread)
        if self.active < 0:
            self.active = 0
        return len(self.threads) - 1

    def activate(self, index: int) -> Thread:
        """Makes a thread the active one: what it held unread is read now."""
        self.active = index
        thread = self.threads[index]
        thread.unread = 0
        return thread

    def close(self, index: int) -> Thread:
        """Takes a thread out; the active one follows -- the previous thread, or none."""
        thread = self.threads.pop(index)
        if not self.threads:
            self.active = -1
        elif index < self.active or self.active >= len(self.threads):
            self.active = max(0, self.active - 1)
        return thread

    def take(self, index: int, event: Event) -> None:
        """Hands an event of the flow to its thread, which knows whether it is active."""
        self.threads[index].take(event, active=index == self.active)

    @property
    def current(self) -> Thread | None:
        return self.threads[self.active] if 0 <= self.active < len(self.threads) else None

    def lines(self) -> list[str]:
        """What the column renders, one line per thread in order."""
        return [one.line for one in self.threads]
