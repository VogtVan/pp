"""chat -- the face of a conversation: `agent chat <path> --json` HELD as an asyncio
subprocess on the caller's loop, its events read line by line as an async iterator, its
commands written on demand. No reader thread, no buffer in between, no polling: the post
gives each conversation a task that consumes `events()`, and the bench proves the face
under `asyncio.run`. The face reads the flow and hands its events over as they are; it judges
nothing and renders nothing -- the dialogue pane does. Two events are the face's own:
`unreadable` (a line of the flow that does not read) and `ended` (the flow ended, with the
exit code and what stderr said -- a refusal before the flow, `agent-unknown` or `run-busy`,
arrives this way)."""
from __future__ import annotations

import asyncio
import json
from asyncio.subprocess import PIPE
from dataclasses import dataclass
from typing import AsyncIterator, Sequence

from faces import apart, command_for, end_tree
from model.dialogue import ENDED, Event

CLOSE_WAIT = 5.0                   # seconds `close` gives the verb after `quit` before ending its group
GROUP_GRACE = 1.0                  # seconds between the group's SIGTERM and its SIGKILL
LINE_LIMIT = 16 * 1024 * 1024      # one event of the flow may carry a whole output of pp
FIRST_WAIT = 10.0                  # seconds the first event of a conversation gets before `chat-silent`


@dataclass
class Opening:
    """A conversation opened on the loop the post will run on, BEFORE the post draws: the
    face, the iterator of its events already started, and the first event read -- `ended`
    when the verb refused before any flow, None when nothing came in time."""
    conversation: "Conversation"
    events: AsyncIterator[Event]
    first: Event | None

    @property
    def refused(self) -> bool:
        return self.first is not None and self.first.kind == ENDED

    @property
    def silent(self) -> bool:
        return self.first is None


def lived(found: list[dict], run: str) -> list[Event]:
    """-> the objects of a run's kept flow (`agent flow --json`) as the events of its conversation."""
    return [Event(str(one.get("kind", "")), str(one.get("at") or ""), run,
                  {key: value for key, value in one.items() if key not in ("kind", "at", "run")}) for one in found]


async def opened(house: str, agent: str, run: str | None = None, flags: Sequence[str] = (),
                 wait: float = FIRST_WAIT) -> Opening:
    """Opens a conversation and reads its first event, within `wait` seconds: what the entry
    does for each agent named at the start, on the app's own loop, so that a refusal is
    relayed before anything is drawn and the flow goes on from the second event."""
    conversation = await Conversation(house, agent, run, flags).open()
    events = conversation.events()
    try:
        first: Event | None = await asyncio.wait_for(events.__anext__(), wait)
    except (asyncio.TimeoutError, StopAsyncIteration):
        first = None
    return Opening(conversation, events, first)


class Conversation:
    """One conversation with one agent of the house, held from `open()` to `close()`. A conversation is DORMANT until
    then: the object stands, no process -- the first gesture that speaks to the verb (`send`, `set`, `conduct`,
    `package`) opens it (`wake`), and `events()` waits for that opening; closing a dormant one plays nothing."""

    def __init__(self, house: str, agent: str, run: str | None = None,
                 flags: Sequence[str] = ()) -> None:
        self.house = house
        self.agent = agent
        self.run = run
        argv = ["agent", "chat", agent, "--json"] + (["--run", run] if run else []) + list(flags)
        self.command: list[str] = command_for(argv, house)      # the exact line, the preview
        self._process: asyncio.subprocess.Process | None = None
        self._stderr: list[str] = []
        self._drain: asyncio.Task | None = None
        self._born = asyncio.Event()                             # set once the process stands
        self.ended = False                                       # `events()` yielded its last

    # ---------- the process ----------
    async def open(self) -> "Conversation":
        self._process = await asyncio.create_subprocess_exec(       # apart: `close` ends its tree whole
            *self.command, stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=self.house, limit=LINE_LIMIT, **apart())
        self._drain = asyncio.create_task(self._read_stderr())
        self._born.set()
        return self

    async def wake(self) -> None:
        """A dormant conversation opened -- the first gesture that speaks to the verb; an open one stays as it is."""
        if self._process is None:
            await self.open()

    @property
    def dormant(self) -> bool:
        return self._process is None

    async def _read_stderr(self) -> None:
        assert self._process is not None and self._process.stderr is not None
        while True:
            line = await self._process.stderr.readline()
            if not line:
                return
            self._stderr.append(line.decode("utf-8", "replace"))

    @property
    def alive(self) -> bool:
        return self._process is not None and self._process.returncode is None

    # ---------- the events ----------
    async def events(self) -> AsyncIterator[Event]:
        """The events of the flow, one per line, as they come; `ended {rc, stderr}` last, when
        the flow closes -- never an exception. A dormant conversation says nothing until it is opened."""
        await self._born.wait()
        assert self._process is not None and self._process.stdout is not None
        while True:
            raw = await self._process.stdout.readline()
            if not raw:
                break
            line = raw.decode("utf-8", "replace").rstrip("\n")
            if line:
                yield Event.read(line)
        rc = await self._process.wait()
        if self._drain is not None:
            await self._drain
        self.ended = True
        yield Event(ENDED, "", "", {"rc": rc, "stderr": "".join(self._stderr)})

    # ---------- the commands ----------
    async def send(self, text: str) -> None:
        await self.wake()
        await self._write({"kind": "message", "text": text})

    async def stop(self) -> None:
        await self._write({"kind": "stop"})

    async def quit(self) -> None:
        await self._write({"kind": "quit"})

    async def set(self, fields: dict) -> None:
        """The policy of the next launches: the model, the budget, the effort -- the verb answers `policy`."""
        await self.wake()
        await self._write({"kind": "set", **fields})

    async def conduct(self, on: bool) -> None:
        """Whether the next exchanges are conducted -- the verb answers `conduct`."""
        await self.wake()
        await self._write({"kind": "conduct", "on": on})

    async def package(self, name: str, on: bool) -> None:
        """A package of the run in or out of its play -- the verb answers `package`."""
        await self.wake()
        await self._write({"kind": "package", "name": name, "on": on})

    async def _write(self, command: dict) -> None:
        if not self.alive or self._process is None or self._process.stdin is None:
            return
        try:
            self._process.stdin.write((json.dumps(command) + "\n").encode("utf-8"))
            await self._process.stdin.drain()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass                   # the flow ended under us: `ended` says so

    # ---------- the end ----------
    async def close(self, timeout: float = CLOSE_WAIT) -> int | None:
        """Ends the conversation: `quit` while it lives, then the verb gets `timeout` seconds to
        end on its own (it terminates its harness itself); past it, its whole group is ended. -> the exit code."""
        if self._process is None:
            return None
        if self.alive:
            await self.quit()
            try:
                await asyncio.wait_for(self._process.wait(), timeout)
            except asyncio.TimeoutError:
                await self._end_group()
        if self._drain is not None:
            await self._drain
        return self._process.returncode

    async def _end_group(self) -> None:
        """The verb's whole tree ended -- `uv`, the console and `pp-agent` with its wake lock leave together."""
        assert self._process is not None
        await end_tree(self._process, GROUP_GRACE)
