"""faces -- the ONE seam between the post and the verbs of `pp`.

The post reads the `--json` faces of the house's verbs and plays its gestures through them;
every call goes through `play_verb` (on the app's loop, a task), nothing else spawns a process;
the readings under way are counted (`under_way`) and every start and end of one is told to the
watcher the app sets (`watched`). The bench replaces the verbs without touching this code:
`PP_UI_FACES=<dir>` names a directory of executables, one per verb (`<dir>/agent`, `<dir>/team`),
played in place of the console with the same arguments, and `PP_UI_TIMEOUT=<seconds>` sets the
bound of a call. `chat.py` holds a conversation on the flow of `agent chat --json`; the Agents
tab reads the faces of `agent`. Every process the post starts is chosen and started HERE, by system: the
house's console (`pp`, `pp.cmd` under Windows), started apart from the post (`apart`) -- under Windows on a
hidden console of its own, so that the console of the post and its keys stay the post's -- and its whole tree
ended by `end_tree`."""
from __future__ import annotations

import asyncio
import json
import os
import signal
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

CREATE_NEW_PROCESS_GROUP = 0x00000200   # the values of Windows' process creation flags, read on any system
CREATE_NO_WINDOW = 0x08000000
TIMEOUT = 30.0                       # one bounded call of a verb, unless `PP_UI_TIMEOUT` says another
TIMED_OUT = -1                       # the exit code of a face whose verb passed its bound
_UNDER_WAY: list[tuple[str, ...]] = []    # the verbs being played now, in their order
_watcher: list[Callable[[], None]] = []   # told at every start and end of a call


def bound() -> float:
    """-> the bound of one call: `PP_UI_TIMEOUT` when it holds a positive number, else `TIMEOUT`."""
    try:
        given = float(os.environ.get("PP_UI_TIMEOUT", ""))
    except ValueError:
        return TIMEOUT
    return given if given > 0 else TIMEOUT


def under_way() -> list[tuple[str, ...]]:
    """-> the verbs being played now, each as its first two words (`agent status`)."""
    return list(_UNDER_WAY)


def watched(callback: Callable[[], None]) -> None:
    """`callback` is told, on the loop, at every start and end of a call."""
    _watcher[:] = [callback]


def _told() -> None:
    for callback in _watcher:
        callback()


@dataclass(frozen=True)
class Face:
    """What a verb answered: its words, its exit code and its two streams."""
    argv: tuple[str, ...]
    rc: int
    out: str
    err: str


def command_for(argv: Sequence[str], house: str, system: str = os.name) -> list[str]:
    """-> the command line a call takes: the witness of `PP_UI_FACES` when it carries the
    verb, the house's own console otherwise -- `<house>/pp`, `<house>/pp.cmd` under Windows."""
    witness = os.environ.get("PP_UI_FACES")
    if witness:
        stand_in = Path(witness) / argv[0]
        if stand_in.is_file():
            return [str(stand_in), *argv[1:]]
    return [str(Path(house) / ("pp.cmd" if system == "nt" else "pp")), *argv]


def apart(system: str = os.name) -> dict:
    """-> the arguments that start a process apart from the post: under Windows a hidden console and a process
    group of its own, elsewhere a session of its own -- its group, which `end_tree` ends whole."""
    if system == "nt":
        return {"creationflags": CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP}
    return {"start_new_session": True}


def in_place(system: str = os.name) -> bool:
    """-> whether this process may give its place to another program (`os.execvp`): not under Windows, where exec
    starts a new process and ends this one, so that whoever waits for this one -- the console -- would give the
    terminal back to its shell while the new one draws."""
    return system != "nt"


def ender(pid: int, system: str = os.name) -> list[str] | None:
    """-> the command that ends the tree of `pid` under Windows; None elsewhere, where its group is signalled."""
    return ["taskkill", "/T", "/F", "/PID", str(pid)] if system == "nt" else None


async def end_tree(process: asyncio.subprocess.Process, grace: float) -> None:
    """The process and everything it started ended: under Windows by `ender`; elsewhere its group gets SIGTERM,
    then SIGKILL `grace` seconds later for what the SIGTERM left."""
    command = ender(process.pid)
    if command is not None:
        killer = await asyncio.create_subprocess_exec(*command, stdin=asyncio.subprocess.DEVNULL,
                                                      stdout=asyncio.subprocess.DEVNULL,
                                                      stderr=asyncio.subprocess.DEVNULL, **apart())
        await killer.wait()
        await process.wait()
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        await asyncio.wait_for(process.wait(), grace)
    except asyncio.TimeoutError:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    await process.wait()


async def play_verb(argv: Sequence[str], house: str, timeout: float | None = None) -> Face:
    """Plays ONE verb of the house on the running loop -- a task, never a thread --, captured,
    bounded, apart from the post and reading nothing of its input; past the bound the verb's tree is ended -- or
    found ended already -- and its face is a failure (`TIMED_OUT`, nothing of what it said kept), `err` naming the
    verb and the bound."""
    limit = bound() if timeout is None else timeout
    said = tuple(argv[:2])
    _UNDER_WAY.append(said)
    _told()
    try:
        process = await asyncio.create_subprocess_exec(*command_for(argv, house), stdin=asyncio.subprocess.DEVNULL,
                                                       stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                                                       cwd=house, **apart())
        try:
            out, err = await asyncio.wait_for(process.communicate(), limit)
        except asyncio.TimeoutError:
            await end_tree(process, 0)     # the verb and what it started: nothing left to hold its pipes
            await process.communicate()
            return Face(tuple(argv), TIMED_OUT, "", f"{' '.join(said)}: verb-timeout -- {limit:.0f}s")
        return Face(tuple(argv), int(process.returncode or 0), out.decode("utf-8", "replace"),
                    err.decode("utf-8", "replace"))
    finally:
        _UNDER_WAY.remove(said)
        _told()


def objects(face: Face) -> list[dict]:
    """-> the JSON objects a face printed, one per line; a line that does not read is skipped."""
    found = []
    for line in face.out.splitlines():
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except ValueError:
            continue
        if isinstance(data, dict):
            found.append(data)
    return found
