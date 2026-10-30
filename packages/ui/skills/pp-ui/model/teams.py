"""teams -- the typed state of the TEAMS tab: the teams of the house and the state of one, as the
faces of `team` say them (`team status --json`, `team status <name> --json`); pure dataclasses, no
I/O, no Textual. A field the face leaves out stays empty: nothing is deduced here -- a team's state
is `team`'s to compute, the post shows it."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone

TEAM_COLUMNS = ("team", "run", "msg", "done")
TASK_COLUMNS = ("id", "task", "team", "state", "holder", "prog", "cost", "at")
MEMBER_COLUMNS = ("member", "agent", "run", "state", "tasks", "owes", "live")
CEREMONY_COLUMNS = ("ceremony", "progress", "next", "due", "last")
SHOWS = ("recent", "running", "for you", "stopped", "resolved", "all")   # the filters of the Tasks tab, `recent` first
RECENT = timedelta(hours=24)       # `recent` keeps a task ended within this window, and every open one
ALL = "all"                                                     # the TEAM filter that keeps every team


def _dict(value: object) -> dict:
    return value if isinstance(value, dict) else {}


def _list(value: object) -> list:
    return value if isinstance(value, list) else []


def _int(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _str(value: object) -> str | None:
    return value if isinstance(value, str) else None


@dataclass(frozen=True)
class TeamBadge:
    """One team as `team status --json` without a name says it: its identity (`team`, its directory) and the name it
    is shown by (`name`, its `TEAM.md`'s), its start (None for a
    team never started), its tasks counted by state, the wake-ups under way, the agents' questions to the
    owner and the team's notices to them, as the inbox counts them, the tasks done the owner has not seen, the
    last event; its state (`never`, `paused`, `working`, `idle`, `waiting`), the guards a waiting team
    waits on, in the order the face gives them, and who paused it and when."""
    team: str
    started: dict | None = None
    tasks: dict = field(default_factory=dict)
    running: int | None = None
    asks: int | None = None
    last: dict | None = None
    done: int | None = None
    state: str | None = None
    waiting_on: tuple[str, ...] = ()
    paused: dict | None = None
    notices: int | None = None
    name: str = ""

    @staticmethod
    def read(obj: dict) -> "TeamBadge":
        started = obj.get("started")
        return TeamBadge(str(obj.get("team", "")), started if isinstance(started, dict) else None,
                         _dict(obj.get("tasks")), _int(obj.get("running")), _int(obj.get("asks")),
                         obj.get("last") if isinstance(obj.get("last"), dict) else None, _int(obj.get("done")),
                         _str(obj.get("state")), tuple(str(one) for one in _list(obj.get("waiting_on"))),
                         obj.get("paused") if isinstance(obj.get("paused"), dict) else None, _int(obj.get("notices")),
                         _str(obj.get("name")) or "")

    @property
    def shown(self) -> str:
        """The team as the post says it: its name, its identity when the face says none."""
        return self.name or self.team

    @property
    def for_owner(self) -> int | None:
        """What waits for the owner's word, as the inbox counts it: the questions and the notices; None when the face
        says neither."""
        if self.asks is None and self.notices is None:
            return None
        return (self.asks or 0) + (self.notices or 0)


@dataclass(frozen=True)
class TaskLine:
    """One task as the face says it: its name and its text, its last event, its state, who gave it and to
    whom, its ceremony and period, its messages counted, the `resumed` that took it back, who holds it, its
    `do`s between members (`dos`: `{id, from, to, answered}`) and waits, the wake-ups under way on it (`running`:
    `{member, tag, run, since, allowance, relance}`), its cost, the hour it was born (`at`) and the hour it ended
    (`ended`, None while it is open)."""
    id: str
    state: str = ""
    name: str | None = None
    text: str | None = None
    last: dict | None = None
    sender: str | None = None
    to: str | None = None
    ceremony: str | None = None
    period: str | None = None
    messages: int | None = None
    resumed: int | None = None
    holders: tuple[str, ...] = ()
    dos: tuple[dict, ...] = ()
    waits: tuple[dict, ...] = ()
    running: tuple[dict, ...] = ()
    cost: float | None = None          # the dollars its wake-ups reported; None when the face says none
    at: str | None = None
    ended: str | None = None

    @staticmethod
    def read(obj: dict) -> "TaskLine":
        return TaskLine(str(obj.get("id", "")), str(obj.get("state") or ""), _str(obj.get("name")), _str(obj.get("text")),
                        obj.get("last") if isinstance(obj.get("last"), dict) else None,
                        _str(obj.get("from")), _str(obj.get("to")), _str(obj.get("ceremony")), _str(obj.get("period")), _int(obj.get("messages")),
                        _int(obj.get("resumed")), tuple(str(one) for one in _list(obj.get("holders"))),
                        tuple(one for one in _list(obj.get("dos")) if isinstance(one, dict)),
                        tuple(one for one in _list(obj.get("waits")) if isinstance(one, dict)),
                        tuple(one for one in _list(obj.get("running")) if isinstance(one, dict)),
                        float(obj["cost"]) if isinstance(obj.get("cost"), (int, float))
                        and not isinstance(obj.get("cost"), bool) else None, _str(obj.get("at")), _str(obj.get("ended")))


@dataclass(frozen=True)
class MemberLine:
    """One member as the face says it: the agent that plays it, its one run and how it stands, the
    hour its wake-up under way was launched, its tasks, whom it waits for, the posts not delivered to
    it yet (`pending`), the answers of the others it has not seen (`unseen`), the messages it still owes
    (`owes`: `{id, verb, from, task, reminded}`) and its health (`{suspected, falls, tried_at, repents}`, None
    for a member never fallen)."""
    member: str
    path: str | None = None
    run: str | None = None
    how: str | None = None
    since: str | None = None
    tasks: tuple[str, ...] = ()
    waits: tuple[str, ...] = ()
    pending: tuple[dict, ...] = ()
    unseen: tuple[dict, ...] = ()
    launch: dict | None = None        # what its next wake-up gets: the team's launch, its profile over it
    owes: tuple[dict, ...] = ()
    health: dict | None = None

    @staticmethod
    def read(obj: dict) -> "MemberLine":
        return MemberLine(str(obj.get("member", "")), _str(obj.get("path")), _str(obj.get("run")), _str(obj.get("how")),
                          _str(obj.get("since")), tuple(str(one) for one in _list(obj.get("tasks"))),
                          tuple(str(one) for one in _list(obj.get("waits"))),
                          tuple(one for one in _list(obj.get("pending")) if isinstance(one, dict)),
                          tuple(one for one in _list(obj.get("unseen")) if isinstance(one, dict)),
                          obj.get("launch") if isinstance(obj.get("launch"), dict) else None,
                          tuple(one for one in _list(obj.get("owes")) if isinstance(one, dict)),
                          obj.get("health") if isinstance(obj.get("health"), dict) else None)


@dataclass(frozen=True)
class CeremonyLine:
    """One ceremony as the face says it: its rhythm (`every` and its `when`, or `after` another), its
    participants and facilitator, its quorum, its next ring and whether the next tick rings it -- both
    computed by `team` --, its last ring and who answered it."""
    name: str
    mode: str = ""
    when: dict | None = None
    after: str | None = None
    participants: tuple[str, ...] = ()
    facilitator: str | None = None
    quorum: int | None = None
    next_due: str | None = None
    due: bool | None = None
    last: dict | None = None
    progress: tuple[dict, ...] = ()

    @staticmethod
    def read(obj: dict) -> "CeremonyLine":
        due = obj.get("due")
        return CeremonyLine(str(obj.get("name", "")), str(obj.get("mode") or ""),
                            obj.get("when") if isinstance(obj.get("when"), dict) else None, _str(obj.get("after")),
                            tuple(str(one) for one in _list(obj.get("participants"))), _str(obj.get("facilitator")),
                            _int(obj.get("quorum")), _str(obj.get("next_due")), due if isinstance(due, bool) else None,
                            obj.get("last") if isinstance(obj.get("last"), dict) else None,
                            tuple(one for one in _list(obj.get("progress")) if isinstance(one, dict)))


@dataclass(frozen=True)
class TeamState:
    """One team as `team status <name> --json` says it; `started` None for a team never started. `season` its last
    start (`n`, and the budget and the wake-ups that season gave itself), `launch` what its next wake-up gets,
    `required` the packages a member may not switch off -- a team never started says it too; `state`,
    `waiting_on` and `paused` as the badge reads them."""
    team: str
    started: dict | None = None
    owner: str | None = None
    principals: tuple[str, ...] = ()
    changed: bool = False
    limits: dict = field(default_factory=dict)
    schedule: dict = field(default_factory=dict)
    cost: float | None = None
    budget_spent: bool = False
    budget: dict | None = None
    launches: dict = field(default_factory=dict)
    last: dict | None = None
    tasks: tuple[TaskLine, ...] = ()
    members: tuple[MemberLine, ...] = ()
    ceremonies: tuple[CeremonyLine, ...] = ()
    owner_inbox: tuple[dict, ...] = ()
    waiting: dict = field(default_factory=dict)
    season: dict = field(default_factory=dict)
    launch: dict | None = None
    required: frozenset[str] = frozenset()
    state: str | None = None
    waiting_on: tuple[str, ...] = ()
    paused: dict | None = None
    name: str = ""

    @staticmethod
    def read(obj: dict) -> "TeamState":
        started = obj.get("started")
        cost = obj.get("cost")
        return TeamState(str(obj.get("team", "")), started if isinstance(started, dict) else None,
                         _str(obj.get("owner")), tuple(str(one) for one in _list(obj.get("principals"))),
                         obj.get("changed") is True, _dict(obj.get("limits")), _dict(obj.get("schedule")),
                         float(cost) if isinstance(cost, (int, float)) else None, obj.get("budget_spent") is True,
                         obj.get("budget") if isinstance(obj.get("budget"), dict) else None, _dict(obj.get("launches")), obj.get("last") if isinstance(obj.get("last"), dict) else None,
                         tuple(TaskLine.read(one) for one in _list(obj.get("tasks")) if isinstance(one, dict)),
                         tuple(MemberLine.read(one) for one in _list(obj.get("members")) if isinstance(one, dict)),
                         tuple(CeremonyLine.read(one) for one in _list(obj.get("ceremonies")) if isinstance(one, dict)),
                         tuple(one for one in _list(obj.get("owner_inbox")) if isinstance(one, dict)),
                         _dict(obj.get("waiting")), _dict(obj.get("season")),
                         obj.get("launch") if isinstance(obj.get("launch"), dict) else None,
                         frozenset(str(one) for one in _list(obj.get("required"))), _str(obj.get("state")),
                         tuple(str(one) for one in _list(obj.get("waiting_on"))),
                         obj.get("paused") if isinstance(obj.get("paused"), dict) else None, _str(obj.get("name")) or "")

    @property
    def shown(self) -> str:
        """The team as the post says it: its name, its identity when the face says none."""
        return self.name or self.team

    @property
    def open_tasks(self) -> int:
        """The tasks the face says open."""
        return sum(1 for one in self.tasks if one.state == "open")


@dataclass(frozen=True)
class TaskRow:
    """One line of the Tasks tab: a task and the team it belongs to -- its identity, and the name it is shown by --,
    and whether something of it waits for the owner -- a question on it, or its end not seen yet, as the face's
    `waiting` lists them."""
    team: str
    task: TaskLine
    for_you: bool = False
    label: str = ""


def instant(iso: str | None) -> datetime | None:
    """-> the instant a face dated (ISO 8601), aware; None when it is absent or does not parse."""
    try:
        moment = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return moment if moment.tzinfo is not None else moment.astimezone()


def rows_of(states: list[TeamState]) -> list[TaskRow]:
    """-> the tasks of every team started, the most recently born first, the teams mingled; a task the face dates
    no birth of last, in the order of the teams then of their tasks."""
    rows = []
    for state in states:
        if state.started is None:
            continue
        asked = {str(one.get("task")) for one in (state.waiting.get("questions") or [])
                 + [one for one in state.waiting.get("notices") or [] if isinstance(one, dict) and one.get("awaits")]
                 if isinstance(one, dict)}
        done = {str(one) for one in state.waiting.get("done") or []}
        rows += [TaskRow(state.team, task, task.id in asked or task.id in done, state.shown) for task in state.tasks]
    floor = datetime.min.replace(tzinfo=timezone.utc)
    return sorted(rows, key=lambda row: instant(row.task.at) or floor, reverse=True)


def newcomer(state: TeamState | None, known: set[str]) -> str | None:
    """-> the task of a team the face says now and did not say among `known` -- the one born last when several are --;
    None when there is none."""
    born = [one for one in (state.tasks if state is not None else ()) if one.id not in known]
    floor = datetime.min.replace(tzinfo=timezone.utc)
    return max(born, key=lambda one: instant(one.at) or floor).id if born else None


def recent(task: TaskLine, now: datetime | None = None) -> bool:
    """-> whether a task is RECENT: open, or ended within `RECENT` -- its `ended`, else its last event, for a face
    that says no end."""
    if task.state == "open":
        return True
    ended = instant(task.ended or (task.last or {}).get("at"))
    return ended is not None and (now or datetime.now(timezone.utc)) - ended <= RECENT


def shown(row: TaskRow, show: str, now: datetime | None = None) -> bool:
    """-> whether a row passes the `SHOW` filter: `recent` the open tasks and those ended within the day, `running`
    the open tasks, `for you` those the owner has to see, `stopped`, `resolved`, `all` -- read from the face's state,
    dates and `waiting`."""
    if show == "recent":
        return recent(row.task, now)
    if show == "running":
        return row.task.state == "open"
    if show == "for you":
        return row.for_you
    if show in ("stopped", "resolved"):
        return row.task.state == show
    return True


def filtered(rows: list[TaskRow], show: str, team: str, now: datetime | None = None) -> list[TaskRow]:
    """-> the rows both filters keep."""
    return [one for one in rows if shown(one, show, now) and (team == ALL or one.team == team)]


def counted(rows: list[TaskRow], team: str, now: datetime | None = None) -> dict[str, int]:
    """-> how many rows each `SHOW` keeps under the `TEAM` filter."""
    return {show: len(filtered(rows, show, team, now)) for show in SHOWS}


def progress(task: TaskLine) -> tuple[int, int] | None:
    """-> the `do`s of a task between members answered over its `do`s, counted on the face's list; None without
    one."""
    if not task.dos:
        return None
    return sum(1 for one in task.dos if one.get("answered") is not None), len(task.dos)


@dataclass(frozen=True)
class ThreadLine:
    """One object of a task's thread as the faces give it: an EVENT of the journal (`log --json`,
    `watch --json`: it names its `team`, carries its `id`) or a STEP of a wake-up (`watch --json`: the
    `agent`, its `run`, the step's `event`, no team); `fields` the rest, as the face said them."""
    kind: str
    at: str = ""
    id: int | None = None
    step: bool = False
    fields: dict = field(default_factory=dict)

    @staticmethod
    def read(obj: dict) -> "ThreadLine":
        step = "team" not in obj
        rest = {key: value for key, value in obj.items() if key not in ("at", "team", "event", "id")}
        return ThreadLine(str(obj.get("event", "")), str(obj.get("at") or ""), _int(obj.get("id")), step, rest)


@dataclass
class Thread:
    """The thread of ONE task: its events in the order of their `id` -- the history, the live flow, and
    the history read again once the task's watch has spoken (it follows the journal from then on) --,
    each `id` shown once; the last step of a wake-up of the task, and whether a wake-up ended after it.
    The live flow that comes before the history is read is held, then added after it."""
    task: str
    lines: list[ThreadLine] = field(default_factory=list)
    seen: set[int] = field(default_factory=set)
    live: ThreadLine | None = None
    live_over: bool = False
    read: bool = False
    held: list[ThreadLine] = field(default_factory=list)

    def history(self, objects: list[dict]) -> None:
        """The history `log --task` gave, then what the live flow said meanwhile."""
        for one in objects:
            self._add(ThreadLine.read(one))
        self.read = True
        held, self.held = self.held, []
        for one in held:
            self._add(one)

    def merge(self, objects: list[dict]) -> None:
        """The history read again: what it says that the thread lacks takes its place by `id`."""
        for one in objects:
            self._add(ThreadLine.read(one))

    def add(self, obj: dict) -> None:
        """One object of the task's watch: held until the history is read."""
        line = ThreadLine.read(obj)
        if not self.read:
            self.held.append(line)
        else:
            self._add(line)

    def _add(self, line: ThreadLine) -> None:
        if line.step:
            self.live, self.live_over = line, False
            return
        if line.kind == "quiet":
            return
        if line.id is not None:
            if line.id in self.seen:
                return                      # shown already: the history read it, or the flow said it twice
            self.seen.add(line.id)
            at = len(self.lines)
            while at and self.lines[at - 1].id is not None and self.lines[at - 1].id > line.id:
                at -= 1                     # an event the first reading missed takes its place by `id`
            self.lines.insert(at, line)
        else:
            self.lines.append(line)
        if line.kind in ("wake-ended", "wake-failed") and self.live is not None:
            self.live_over = True


WAKES = ("wake-intent", "wake-launched")                       # the events that open a wake-up of a member
WAKE_ENDS = ("wake-ended", "wake-failed", "wake-killed")        # the events that end it
MARKS = {"wait-met": "agent", "stopped": "by", "done": "from"}   # an event drawn on one column: the field naming it


@dataclass(frozen=True)
class SequenceRow:
    """One row of a sequence: a POST -- an arrow from the column `source` to the column `target`, its `verb` (`do`,
    `ask`, `re` citing `re`, `stop`; `notice` from the team, `source` None) and its text --, a WAKE of the member of
    `source` (its `run`, its `cost` once ended, `over` then, its `relance` when the face says it is a reminder), or a
    MARK of an event on the column `source` (`wait-met`, `stopped`, `done`, its kind in `verb`)."""
    kind: str
    id: int | None
    at: str
    source: str | None
    target: str | None = None
    verb: str = ""
    re: int | None = None
    text: str = ""
    run: str | None = None
    cost: float | None = None
    over: bool = False
    relance: str | None = None


@dataclass(frozen=True)
class Sequence:
    """The exchanges of one task between its participants: the COLUMNS, the principal who gave the task first, then
    each member in the order it appears -- under a `focus`, that member first, then those it exchanged with alone --,
    and the ROWS in the order of the journal's `id`; `start` the instant the task was born, as its journal dates it."""
    columns: tuple[str, ...] = ()
    rows: tuple[SequenceRow, ...] = ()
    focus: str | None = None
    start: str | None = None


def sequence_of(lines: list[ThreadLine], focus: str | None = None) -> Sequence:
    """-> the sequence of a task's thread: one row per post, per wake-up -- its intent, its launch and its end joined
    by their `tag` --, per event of `MARKS`; the events a wake-up's steps or the task's birth say are no row, the
    birth its `start` (the first row's instant when the thread holds no birth). Under `focus`, the rows where that
    member sends, receives, wakes or is marked, and the columns those rows name."""
    rows: list[SequenceRow] = []
    wakes: dict[str, int] = {}                       # a wake-up's tag -> its row
    principal = start = None
    for line in lines:
        f = line.fields
        if line.step:
            continue
        if line.kind == "task" and principal is None:
            principal, start = _str(f.get("from")), line.at or None
        elif line.kind == "post":
            notice = f.get("verb") == "notice"
            rows.append(SequenceRow("post", line.id, line.at, None if notice else _str(f.get("from")), _str(f.get("to")),
                                    str(f.get("verb") or ""), _int(f.get("re")), str(f.get("text") or "")))
        elif line.kind in WAKES or line.kind in WAKE_ENDS:
            tag = _str(f.get("tag"))
            at = wakes.get(tag) if tag is not None else None
            if at is None:
                wakes[tag or f"#{line.id}"] = len(rows)
                rows.append(SequenceRow("wake", line.id, line.at, _str(f.get("agent")), run=_str(f.get("run")),
                                        relance=_str(f.get("relance"))))
                at = len(rows) - 1
            if line.kind in WAKE_ENDS:
                cost = f.get("cost")
                rows[at] = replace(rows[at], over=True, cost=float(cost) if isinstance(cost, (int, float))
                                   and not isinstance(cost, bool) else None)
        elif line.kind in MARKS:
            rows.append(SequenceRow("mark", line.id, line.at, _str(f.get(MARKS[line.kind])), verb=line.kind))
    if focus is not None:
        rows = [one for one in rows if focus in (one.source, one.target)]
    named = [principal] if principal is not None and focus is None else []
    for one in rows:
        named += [name for name in (one.source, one.target) if name is not None]
    columns = list(dict.fromkeys(name for name in named if name is not None))
    if focus is not None and focus in columns:
        columns.remove(focus)
        columns.insert(0, focus)
    return Sequence(tuple(columns), tuple(rows), focus, start or (rows[0].at if rows else None))


PROFILE_KEYS = ("provider", "model", "effort", "permissions")   # what a line of a season carries, as `team start` takes it
SEASON_COLUMNS = ("line", "agent", "provider", "model", "effort", "perms", "packages")


@dataclass
class SeasonLine:
    """One line of a season: `all` (`member` None) or a member of the declaration, the path of its agent, what it
    carries of a launch (`profile`: for a member, what differs from `all` -- the rest is `all`'s), its switches of
    packages (`{name: on}`), and the packages its agent plays as the declaration says them -- born or not yet
    (`{name: on}`, None when the face says none; for `all`, those of every member, on where one is on)."""
    member: str | None
    path: str | None = None
    profile: dict = field(default_factory=dict)
    switches: dict = field(default_factory=dict)
    packages: dict | None = None


def switches_of(said: object) -> dict[str, bool]:
    """-> the switches a face says, `["plan=off"]`, as `{name: on}`."""
    found: dict[str, bool] = {}
    for one in _list(said):
        name, _, state = str(one).partition("=")
        if name and state in ("on", "off"):
            found[name] = state == "on"
    return found


def packages_of(said: object) -> dict[str, bool] | None:
    """-> the packages a member of `team declaration --json` says, `[{name, on}]`, as `{name: on}` -- what its agent
    plays, or what its birth gives when it is not born yet (team 0.38.0); None when it says none."""
    if not isinstance(said, list):
        return None
    return {str(one.get("name", "")): one.get("on") is True for one in said if isinstance(one, dict)}


def _profile(found: dict, providers: tuple[str, ...]) -> dict:
    """-> what a launch or a policy carries of a line: each key it gives, the provider only when the house is
    wired with it."""
    kept = {key: str(found[key]) for key in PROFILE_KEYS if found.get(key)}
    if kept.get("provider") and kept["provider"] not in providers:
        del kept["provider"]
    return kept


def _over(profile: dict, whole: dict) -> dict:
    """-> what a member's profile changes of `all`'s."""
    return {key: value for key, value in profile.items() if whole.get(key) != value}


def season_lines(state: TeamState | None, declared: dict, agents: dict[str, dict],
                 providers: tuple[str, ...]) -> list[SeasonLine]:
    """-> the lines of the season the next start writes: `all`, then one per member of `declared`, in its order.
    A team at work starts from its face -- `all` from its `launch`, each member from its own (`members[].launch`, its
    switches with it), a member the declaration adds from nothing; a first season from what each member's agent last
    played (`agents`: the last object of `agent status <path> --json` by path, a member born alone) -- `all` from the
    root's agent. A member keeps what differs from `all`. The packages of every line are the declaration's: what each
    member's agent plays, or what its birth gives."""
    members = [(str(one.get("member", "")), str(one.get("path", ""))) for one in _list(declared.get("agents"))
               if isinstance(one, dict)]
    said = {str(one.get("member", "")): packages_of(one.get("packages")) for one in _list(declared.get("agents"))
            if isinstance(one, dict)}
    union: dict[str, bool] = {}
    for name, _ in members:
        for package, on in (said.get(name) or {}).items():
            union[package] = union.get(package, False) or on
    lines: list[SeasonLine] = []
    if state is not None and state.started is not None:
        whole = _profile(state.launch or {}, providers)
        launched = {one.member: one.launch for one in state.members}
        lines.append(SeasonLine(None, None, whole, {}, union))
        for name, path in members:
            launch = launched.get(name) or {}
            lines.append(SeasonLine(name, path, _over(_profile(launch, providers), whole),
                                    switches_of(launch.get("packages")), said.get(name)))
        return lines

    def played(path: str) -> dict:
        last = _dict((agents.get(path) or {}).get("last"))
        return _profile({**_dict(last.get("policy")), "provider": last.get("provider")}, providers)
    root = next((path for name, path in members if name == declared.get("root")), members[0][1] if members else "")
    whole = played(root)
    lines.append(SeasonLine(None, None, whole, {}, union))
    for name, path in members:
        lines.append(SeasonLine(name, path, _over(played(path), whole), {}, said.get(name)))
    return lines
