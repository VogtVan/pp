"""faces -- the ONE seam between the post and the verbs of `pp`.

The post reads the `--json` faces of the house's verbs and plays its gestures through them;
every call goes through `run_verb` (outside a loop) or `play_verb` (on the app's loop, a
task), nothing else spawns a process. The bench replaces the verbs without touching this
code: `PP_UI_FACES=<dir>` names a directory of executables, one per verb (`<dir>/agent`,
`<dir>/team`), played in place of the console with the same arguments. `chat.py` holds a
conversation on the flow of `agent chat --json`; the Agents tab reads the faces of `agent`."""
from __future__ import annotations

import asyncio
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

TIMEOUT = 30.0                       # one bounded call of a verb


@dataclass(frozen=True)
class Face:
    """What a verb answered: its words, its exit code and its two streams."""
    argv: tuple[str, ...]
    rc: int
    out: str
    err: str


def command_for(argv: Sequence[str], house: str) -> list[str]:
    """-> the command line a call takes: the witness of `PP_UI_FACES` when it carries the
    verb, the house's own console otherwise (`<house>/pp`, `pp.cmd` on Windows)."""
    witness = os.environ.get("PP_UI_FACES")
    if witness:
        stand_in = Path(witness) / argv[0]
        if stand_in.is_file():
            return [str(stand_in), *argv[1:]]
    console = Path(house) / "pp"
    if not console.is_file() and (Path(house) / "pp.cmd").is_file():
        console = Path(house) / "pp.cmd"
    return [str(console), *argv]


def run_verb(argv: Sequence[str], house: str, timeout: float = TIMEOUT) -> Face:
    """Plays ONE verb of the house, captured, from the house's root -- the preview the
    operator sees before a gesture is exactly `command_for`."""
    done = subprocess.run(command_for(argv, house), capture_output=True, text=True,
                          cwd=house, timeout=timeout)
    return Face(tuple(argv), done.returncode, done.stdout, done.stderr)


async def play_verb(argv: Sequence[str], house: str, timeout: float = TIMEOUT) -> Face:
    """Plays ONE verb of the house on the running loop -- a task, never a thread --, captured,
    bounded; past the bound the verb is killed -- or found ended already -- and the face says so on `err`."""
    process = await asyncio.create_subprocess_exec(*command_for(argv, house), stdout=asyncio.subprocess.PIPE,
                                                   stderr=asyncio.subprocess.PIPE, cwd=house)
    try:
        out, err = await asyncio.wait_for(process.communicate(), timeout)
    except asyncio.TimeoutError:
        try:
            process.kill()
        except ProcessLookupError:
            pass                       # the verb ended as its bound passed
        out, err = await process.communicate()
        return Face(tuple(argv), -1, out.decode("utf-8", "replace"),
                    err.decode("utf-8", "replace") + f"\nverb-timeout -- {timeout:.0f}s")
    return Face(tuple(argv), int(process.returncode or 0), out.decode("utf-8", "replace"),
                err.decode("utf-8", "replace"))


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
