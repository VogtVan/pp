"""The flow of an exchange, judged: whether a command the harness played calls the agent's console."""
from __future__ import annotations

import shlex


def pp_called(shell: str | None, console: str) -> bool:
    """-> whether a command calls the agent's console: its first word `./pp`, or the console by its
    absolute path."""
    try:
        words = shlex.split(shell or "")
    except ValueError:
        words = (shell or "").split()
    return bool(words) and words[0] in ("./pp", console)
