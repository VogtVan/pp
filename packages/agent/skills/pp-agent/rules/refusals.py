"""What the engine refused, read on the output of a call -- the form of its refusal line handed by the caller
(`model.refusal.RefusalLine`, read in the engine's messages by `store.houses.refusal_line`), never typed here."""
from __future__ import annotations

import re
from typing import Protocol

from model.refusal import RefusalLine


class Played(Protocol):
    """A process that ended, as a judgment reads it: its exit code and what it wrote on its two outputs."""
    returncode: int
    stdout: str
    stderr: str


def refused_mount(line: RefusalLine, played: Played, script: str, key: str) -> tuple[str, str]:
    """-> (cause, detail) of a `-s <script> mount <id>` that did not mount: the engine's refusal line, its
    code and its detail; else the script's own refusal, `<script>: <code> -- <detail>` on its last line; else
    `offer-absent` when the engine answered the standing block (a name the output does not offer is DENIED,
    never refused by a code); else `mount-refused` with the last line said."""
    if line.word in (played.stderr or "") + (played.stdout or ""):
        return refused_switch(line, played)
    last = next((one.strip() for one in reversed((played.stderr or "").splitlines()) if one.strip()), "")
    own = re.match(rf"^{re.escape(script)}: ([a-z0-9-]+) -- (.*)$", last)
    if own is not None:
        return own.group(1), own.group(2)
    if not last and (played.stdout or "").strip():
        return "offer-absent", f"`{script}` is not offered by the root of the exchange of run {key}"
    return "mount-refused", last or cause_of(line, played.stdout or "") or f"`{script} mount` exited {played.returncode}"


def refusal_of(line: RefusalLine, played: Played) -> str:
    """-> what the engine refused, in one line: its `REFUSED` line without the prefix, else the
    last line it printed, '' when it printed nothing."""
    lines = (played.stderr or played.stdout).strip().splitlines()
    said = next((one for one in lines if line.word in one), lines[-1] if lines else "").strip()
    return said.removeprefix(line.voice)


def unrefused(line: RefusalLine, said: str) -> str:
    """-> a refusal line of the engine without its head: `<code> — <detail>`."""
    return said.removeprefix(line.head)


def cause_of(line: RefusalLine, text: str) -> str:
    """-> the cause an error of the engine says: its refusal line, else its last line that says something --
    the exception and its message under a traceback."""
    said = [one.strip() for one in text.splitlines() if one.strip()]
    return next((one for one in said if one.startswith(line.head.rstrip(" —"))), said[-1] if said else "")


def refused_switch(line: RefusalLine, played: Played) -> tuple[str, str]:
    """-> (code, detail) of a switch the engine refused: its refusal line read, its code and its detail."""
    parts = refusal_of(line, played).split(line.separator)
    if parts[0] == line.word and len(parts) > 1:
        return parts[1].strip(), line.separator.join(parts[2:]).strip()
    return refusal_of(line, played), ""


def refused_space(line: RefusalLine, played: Played) -> tuple[str, str]:
    """-> (code, detail) of a `-open`/`-close` the engine refused: its refusal line, its code and its detail, or
    `offer-absent` with the block's last line when the engine answered the pending block (a name the output does
    not offer is DENIED, never refused by a code)."""
    if line.word in (played.stderr or "") + (played.stdout or ""):
        return refused_switch(line, played)
    return "offer-absent", cause_of(line, played.stdout or played.stderr)
