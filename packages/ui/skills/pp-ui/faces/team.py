"""team -- the faces of `team` the Teams tab reads: `team status --json` (one object per team
declared), `team status <name> --json` (one team whole), `team log <name> --json [--task <id>]` (the
journal, or a task's history), `team result <name> <task>`, `team inbox <name> --json` (what waits for the
owner), `team stats <name> --json [--all]` (the stats of its seasons) and `team declaration <name> --json` (its `TEAM.md` and the verdict of `start`'s judge), each played
by `play_verb`; and a
`team watch <name> --json` HELD as an asyncio subprocess on the caller's loop, in its own process group.
`watch` writes its objects on STDERR -- its contract, the text as the JSON --, so the face reads stderr line
by line and hands each object over as it is; a line that does not read is skipped. Every watch opened is
known here until it is closed: the entry closes what a crash left.

The post holds ONE watch per team, never one per task: `follow(house, team)` subscribes to the team's
`Shared` watch -- opened at its first subscriber, every object handed to each subscriber from its
subscription on, closed when its last subscriber leaves and when the post leaves. The Teams tab subscribes
to the team chosen, the Tasks tab to every team started, the thread of a task and the read tab of a
member to their team's.

`Follow` is the run of ONE member of a team, followed for a read-only tab of the dialogue, by the objects
of its team's watch whose `agent` is the member AND whose `run` is its key -- `team status --json` gives
both. Its past and its wake-ups come from the run's KEPT FLOW, `agent flow <path> <run> --json`: each
exchange replayed as the events of a lived turn -- the conduction, the calls, the thought, the words, the
answer, the verdict --, and the exchange a step, an activity or an end names by its `launch` (the rank of the
launch in the run) read again (`--exchange <launch>`), its events not shown yet said. A run without a kept flow -- older than agent
0.22.0 -- is followed by its exchanges instead (`agent exchanges <path> <run> --json`): `wake-launched`
reads them again and opens a turn on each new message, a step of the wake-up is a `step`, `wake-ended`
reads them again and closes the turn with its answer and its verdict. It writes nothing and launches no
`agent chat`: the run stays the team's."""
from __future__ import annotations

import asyncio
import json
from asyncio.subprocess import DEVNULL, PIPE
from pathlib import Path
from typing import AsyncIterator

from faces import Face, apart, command_for, end_tree, objects, play_verb
from model.dialogue import Event

GROUP_GRACE = 1.0                  # seconds between the group's SIGTERM and its SIGKILL
LINE_LIMIT = 1024 * 1024           # one object of the watch: an event of the journal, a step of a wake-up
HEARTBEAT = 30                     # seconds without a step before the watch says `quiet`

HELD: set["Watch"] = set()         # the watches open, closed by `close_all` when the post leaves


async def badges(house: str) -> tuple[list[dict], Face]:
    """-> one object per team declared under `teams/`, and the face that said them."""
    face = await play_verb(["team", "status", "--json"], house)
    return objects(face), face


async def state(house: str, name: str) -> tuple[dict | None, Face]:
    """-> the team `name` whole, None when the verb said nothing readable; and the face."""
    face = await play_verb(["team", "status", name, "--json"], house)
    found = objects(face)
    return (found[0] if found else None), face


async def log(house: str, name: str, task: str | None = None) -> tuple[list[dict], Face]:
    """-> the events of the team's journal -- of one task under `task` --, in order; and the face."""
    face = await play_verb(["team", "log", name, "--json"] + (["--task", task] if task else []), house)
    return objects(face), face


async def responses(house: str, name: str, member: str) -> tuple[list[dict], Face]:
    """-> the responses `member` gave in the team, in the journal's order, each with its text whole; and the face."""
    face = await play_verb(["team", "responses", name, "--json", "--agent", member], house)
    return objects(face), face


async def templates(house: str) -> tuple[list[dict], Face]:
    """-> the sorts of templates a team is born from, as `team templates --json` says them -- one object per sort,
    its templates under it --, in their order; and the face."""
    face = await play_verb(["team", "templates", "--json"], house)
    return objects(face), face


async def render(house: str, template: str, values: dict[str, str], team: str | None = None, text: str | None = None,
                 season: bool = False) -> tuple[dict | None, Face]:
    """-> the document a template makes, as `team templates --render <template> --json` says it -- `{template, text,
    values}`, written nowhere --, None when the verb refused (its refusal, `value-missing` naming the hole, in the
    face); and the face. Under `team` with `text`, the values the start takes if `text` is written -- TEAM.md, SEASON.md
    under `season` --: `--team <team> [--season] --text-file -`, the text on the verb's input, no `--value`; otherwise
    `--value <name>=<value>` for each of `values`, `--team <team>` when given. The ONE filling of the holes is the verb's:
    the post fills none."""
    argv = ["team", "templates", "--render", template]
    if team and text is not None:
        argv += ["--team", team, *(["--season"] if season else []), "--text-file", "-"]
    else:
        for name, value in values.items():
            argv += ["--value", f"{name}={value}"]
        argv += ["--team", team] if team else []
    face = await play_verb(argv + ["--json"], house, stdin=text if team and text is not None else None)
    found = objects(face) if face.rc == 0 else []
    return (found[0] if found else None), face


async def document(house: str, template: str) -> tuple[dict | None, Face]:
    """-> the source of a document the house sees, as `team document <template> --json` says it -- `{template, origin,
    kind, path, text}`, nothing written --, None when the verb refused (its refusal in the face); and the face."""
    face = await play_verb(["team", "document", template, "--json"], house)
    found = objects(face) if face.rc == 0 else []
    return (found[0] if found else None), face


async def document_written(house: str, template: str, action: str, body: str | None = None) -> Face:
    """-> the face of `team document <template> --new | --body-file - | --delete --json`: the ONE writer of a house's
    documents under `.pp/teams/templates/` -- `action` `new`, `write` (the text `body` on its input) or `delete`; the
    post writes no file."""
    flag = {"new": ["--new"], "write": ["--body-file", "-"], "delete": ["--delete"]}[action]
    return await play_verb(["team", "document", template, *flag, "--json"], house, stdin=body)


async def inbox(house: str, name: str) -> tuple[dict | None, Face]:
    """-> what waits for the owner in the team -- None when nothing does --; and the face."""
    face = await play_verb(["team", "inbox", name, "--json"], house)
    found = objects(face)
    return (found[0] if found else None), face


async def stats(house: str, name: str, every: bool = False) -> tuple[dict | None, Face]:
    """-> the stats of the team's season under way or last -- of every season not empty, their median and the empty
    ones under `every` --, None when the verb said nothing readable; and the face."""
    face = await play_verb(["team", "stats", name, "--json"] + (["--all"] if every else []), house)
    found = objects(face)
    return (found[0] if found else None), face


async def declaration(house: str, name: str) -> tuple[dict | None, Face]:
    """-> the team's declaration, its verdict and its gap to the start, None when the verb said nothing readable;
    and the face."""
    face = await play_verb(["team", "declaration", name, "--json"], house)
    found = objects(face)
    return (found[0] if found else None), face


async def candidate(house: str, name: str, text: str, season: bool = False) -> tuple[dict | None, Face]:
    """-> the team's declaration as if `text` were written -- TEAM.md, SEASON.md under `season` -- as `team declaration
    <name> --text-file - [--season] --json` says it, the text given on its input, nothing written; None when the verb
    refused (its refusal in the face); and the face."""
    face = await play_verb(["team", "declaration", name, "--text-file", "-"] + (["--season"] if season else [])
                           + ["--json"], house, stdin=text)
    found = objects(face) if face.rc == 0 else []
    return (found[0] if found else None), face


def root_of(house: str, found: dict) -> str | None:
    """-> the root of documents of a team: the folder of the `path` its declaration says (`team declaration --json`,
    relative to the house), resolved from the house -- None when the face says no path. The post composes no path of
    a team: the folder is the face's, the house the post's own."""
    path = found.get("path")
    if not isinstance(path, str) or not path:
        return None
    return str((Path(house) / path).parent.resolve())


async def delete(house: str, name: str) -> tuple[dict | None, Face]:
    """-> what `team delete <name> --json` would remove -- the verb without `--yes` writes nothing --, None when it said
    nothing readable; and the face."""
    face = await play_verb(["team", "delete", name, "--json"], house)
    found = objects(face)
    return (found[0] if found else None), face


async def result(house: str, name: str, task: str) -> Face:
    """-> the face of `team result <name> <task>`: the result as JSON on its stdout, or the refusal."""
    return await play_verb(["team", "result", name, task], house)


class Watch:
    """`team watch <name> --json` held from `open()` to `close()`."""

    def __init__(self, house: str, name: str, heartbeat: int = HEARTBEAT) -> None:
        self.house, self.name = house, name
        self.command: list[str] = command_for(["team", "watch", name, "--json", "--heartbeat", str(heartbeat)], house)
        self._process: asyncio.subprocess.Process | None = None

    async def open(self) -> "Watch":
        self._process = await asyncio.create_subprocess_exec(      # apart: `close` ends its tree whole
            *self.command, stdin=DEVNULL, stdout=DEVNULL, stderr=PIPE, cwd=self.house, limit=LINE_LIMIT, **apart())
        HELD.add(self)
        return self

    async def events(self) -> AsyncIterator[dict]:
        """The objects of the watch, one per line of its stderr, as they come; ends with the watch."""
        assert self._process is not None and self._process.stderr is not None
        while True:
            raw = await self._process.stderr.readline()
            if not raw:
                return
            try:
                found = json.loads(raw.decode("utf-8", "replace"))
            except ValueError:
                continue
            if isinstance(found, dict):
                yield found

    async def close(self) -> None:
        """The watch's whole tree ended."""
        HELD.discard(self)
        process = self._process
        if process is None or process.returncode is not None:
            return
        await end_tree(process, GROUP_GRACE)


class Shared:
    """ONE `team watch <name> --json` for every subscriber of the post: opened at the first subscription,
    each object handed to every subscriber from its subscription on, closed when the last one leaves."""

    def __init__(self, house: str, name: str) -> None:
        self.house, self.name = house, name
        self.watch = Watch(house, name)
        self._queues: list[asyncio.Queue] = []
        self._reader: asyncio.Task | None = None
        self._lock = asyncio.Lock()

    async def subscribe(self) -> "Subscription":
        async with self._lock:
            if self._reader is None:
                await self.watch.open()
                self._reader = asyncio.ensure_future(self._read())
            queue: asyncio.Queue = asyncio.Queue()
            self._queues.append(queue)
        return Subscription(self, queue)

    async def _read(self) -> None:
        async for found in self.watch.events():
            for queue in list(self._queues):
                queue.put_nowait(found)
        for queue in list(self._queues):
            queue.put_nowait(None)                   # the watch ended: each subscription ends

    async def leave(self, queue: asyncio.Queue) -> None:
        async with self._lock:
            if queue in self._queues:
                self._queues.remove(queue)
            if self._queues:
                return
            if SHARED.get((self.house, self.name)) is self:
                del SHARED[(self.house, self.name)]
            await self.watch.close()


class Subscription:
    """One subscriber of a team's shared watch: its objects from the subscription on, until `close()`."""

    def __init__(self, shared: Shared, queue: asyncio.Queue) -> None:
        self.shared, self._queue = shared, queue
        self.closed = False

    @property
    def pending(self) -> int:
        """-> the objects handed and not taken yet."""
        return self._queue.qsize()

    async def events(self) -> AsyncIterator[dict]:
        while not self.closed:
            found = await self._queue.get()
            if found is None:
                return
            yield found

    async def close(self) -> None:
        if not self.closed:
            self.closed = True
            self._queue.put_nowait(None)
            await self.shared.leave(self._queue)


SHARED: dict[tuple[str, str], Shared] = {}   # the watch of each team the post follows


async def follow(house: str, name: str) -> Subscription:
    """-> a subscription to the team's ONE watch, opened at its first subscriber."""
    shared = SHARED.get((house, name))
    if shared is None:
        shared = SHARED[(house, name)] = Shared(house, name)
    return await shared.subscribe()


async def flow(house: str, path: str, run: str, exchange: int | None = None) -> tuple[list[dict], Face]:
    """-> the kept flow of a run -- of one exchange under `exchange` -- as `agent flow --json` says it; and the face."""
    face = await play_verb(["agent", "flow", path, run, "--json"] + (["--exchange", str(exchange)] if exchange else []),
                           house)
    return objects(face), face


async def close_all() -> None:
    """Every watch still open, closed -- what the post does when it leaves."""
    SHARED.clear()
    for one in list(HELD):
        await one.close()


def _event(kind: str, at: str, run: str, **fields) -> Event:
    return Event(kind, at, run, fields)


class Follow:
    """The run of ONE member of a team, read: its past, then its wake-ups as they come -- held from `open()`
    to `close()`, with the face of a conversation the dialogue needs (`events`, `close`, `ended`) and nothing
    to send."""

    def __init__(self, house: str, team: str, member: str, path: str, run: str) -> None:
        self.house, self.team, self.member, self.path, self.run = house, team, member, path, run
        self.watch: Subscription | None = None
        self.ended = False
        self.flowed: dict[int, int] = {}     # the events of the kept flow shown, by exchange; empty without a flow
        self._replay: list[Event] = []       # the kept flow read at the opening, said first
        self.reading = 0                     # an exchange read again and not said whole yet: a render waits for it
        self._opened: set[int] = set()       # the exchanges shown, past or live
        self._closed: set[int] = set()       # the exchanges whose answer is shown
        self._open: int | None = None        # the exchange of the turn under way
        self._pending: list[dict] = []       # the exchange of a wake-up under way at the opening, opened live

    async def open(self) -> "Follow":
        """The subscription taken FIRST, so that nothing written while the past is read is lost."""
        self.watch = await follow(self.house, self.team)
        return self

    async def kept(self) -> tuple[bool, Face]:
        """The run's kept flow read: its exchanges to say first. -> whether the run keeps a flow, and the face."""
        found, face = await flow(self.house, self.path, self.run)
        self._replay = self._unseen(found)
        return bool(self.flowed), face

    def replayed(self) -> list[Event]:
        """-> the kept flow read at the opening, handed once -- the dialogue builds it in one mount; `events()` then
        goes on from the run's present."""
        said, self._replay = self._replay, []
        return said

    def _unseen(self, found: list[dict], exchange: int | None = None) -> list[Event]:
        """-> the objects of a kept flow not shown yet, as events -- counted by exchange, an exchange opening at its
        `opened` (or the one asked)."""
        said: list[Event] = []
        current, seen = exchange, {}
        for one in found:
            if one.get("kind") == "opened" and isinstance(one.get("exchange"), int):
                current = one["exchange"]
            if current is None:
                continue
            seen[current] = seen.get(current, 0) + 1
            if seen[current] > self.flowed.get(current, 0):
                self.flowed[current] = seen[current]
                said.append(Event(str(one.get("kind", "")), str(one.get("at") or ""), self.run,
                                  {key: value for key, value in one.items() if key not in ("kind", "at", "run")}))
        return said

    async def exchanges(self) -> tuple[list[dict], Face]:
        face = await play_verb(["agent", "exchanges", self.path, self.run, "--json"], self.house)
        return objects(face), face

    def past(self, exchanges: list[dict], running: bool) -> list[dict]:
        """-> the exchanges to replay as history: all of them, but the last when a wake-up of the member plays
        and it has no answer yet -- that one opens live, first of the events."""
        for one in exchanges:
            index = one.get("index")
            if isinstance(index, int):
                self._opened.add(index)
                self._closed.add(index)
        last = exchanges[-1] if exchanges else None
        if running and last is not None and last.get("response") is None and isinstance(last.get("index"), int):
            self._closed.discard(last["index"])
            self._opened.discard(last["index"])
            self._pending = [last]
            return exchanges[:-1]
        self._pending = []
        return exchanges

    @property
    def busy(self) -> bool:
        """Whether an object of the watch waits to be taken, or an exchange is being read again -- what a render
        waits for."""
        return bool(self.reading or (self.watch is not None and self.watch.pending))

    def mine(self, found: dict) -> bool:
        """Whether an object of the watch is this member's run: its `agent` the member AND its `run` the key."""
        return found.get("agent") == self.member and found.get("run") == self.run

    def _sync(self, exchanges: list[dict]) -> list[Event]:
        """The exchanges read again: a new message opens a turn, an answer come closes it."""
        said: list[Event] = []
        for one in exchanges:
            index = one.get("index")
            if not isinstance(index, int):
                continue
            at = str(one.get("at") or "")
            if index not in self._opened:
                self._opened.add(index)
                self._open = index
                said.append(_event("principal", at, self.run, exchange=index, text=str(one.get("message") or "")))
            if index not in self._closed and one.get("response") is not None:
                self._closed.add(index)
                self._open = None if self._open == index else self._open
                said.append(_event("response", at, self.run, index=index, response=one.get("response")))
                said.append(_event("verdict", at, self.run, exchange=index, state="parked",
                                   cost_usd=one.get("cost_usd"), launches=one.get("launches")))
        return said

    async def events(self):
        """The turns of the member's wake-ups, as they come; `ended` when the watch ends."""
        for event in self._replay:
            yield event
        for event in self._sync(self._pending):
            yield event
        assert self.watch is not None
        async for found in self.watch.events():
            if not self.mine(found):
                continue
            kind = str(found.get("event", ""))
            if self.flowed:                                         # the kept flow: the launch named, read again
                if isinstance(found.get("launch"), int):
                    self.reading += 1
                    try:
                        again, _face = await flow(self.house, self.path, self.run, found["launch"])
                        for event in self._unseen(again, found["launch"]):
                            yield event
                    finally:
                        self.reading -= 1
            elif "id" not in found and found.get("event") != "activity":   # a step of the wake-up
                fields = {key: value for key, value in found.items() if key not in ("at", "agent", "run")}
                yield Event("step", str(found.get("at") or ""), self.run, fields)
            elif kind in ("wake-launched", "wake-ended"):
                exchanges, _face = await self.exchanges()
                for event in self._sync(exchanges):
                    yield event
        self.ended = True
        yield Event("ended", "", self.run, {"rc": 0, "stderr": ""})

    async def close(self) -> None:
        """The subscription left -- the team's watch ends with its last subscriber: nothing of the member's run is
        touched."""
        if self.watch is not None:
            await self.watch.close()
