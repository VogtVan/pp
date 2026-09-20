"""state.context -- what a script the engine launched may ask about ITS run: the key,
the exchange under way, whether the run is new or has just (re)started. The engine
names the run in the environment of the process that binds it (`PP_RUN`, set at the
facade's binding, inherited by every subprocess it launches, read directly by a
gesture played in the same process); the face reads that run's slot and writes
nothing. Without the variable there is no run to speak of: `context-no-run`; a key
no slot holds: `run-unknown`.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from . import persistence
from ..core.errors import Refusal

VARIABLE = "PP_RUN"     # the run's key, in the environment of the process that binds it


@dataclass(frozen=True)
class Context:
    """One run as a script sees it, read once from its slot: nothing here moves the run."""
    key: str
    turns: int      # the exchanges COMPLETED -- 0 through the whole first exchange
    boot: int       # the exchange count at which the agent's context last started from nothing

    def exchange(self) -> int:
        """-> the number of the exchange under way, 1 at the first."""
        return self.turns + 1

    def is_new(self) -> bool:
        """-> whether this is the run's first exchange."""
        return self.turns == 0

    def is_boot(self) -> bool:
        """-> whether the agent's context started from nothing at this exchange: the
        run's first, or the one where a compaction was declared."""
        return self.turns == self.boot


def current(meta: Path) -> Context:
    """-> the context of the run `PP_RUN` names at the instance `meta`, read from its
    slot as the last save left it. A read, never a write: the slot is byte-identical
    after the call."""
    key = os.environ.get(VARIABLE, "").strip()
    if not key:
        raise Refusal("context-no-run",
                      "no run designates this script -- `PP_RUN` is unset: a script asks "
                      "its run only when the engine launched it under a keyed call")
    slot = persistence.slot_of(meta, key)
    if not slot.exists():
        raise Refusal("run-unknown", f"`{key}` -- no run holds that key")
    return Context(key=key, turns=persistence.turns_of(slot), boot=persistence.boot_of(slot))
