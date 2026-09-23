"""Behaviour: what counts as the AGENT going off, and how often it may try again.

Only a move the tool WATCHED counts -- an answer it was handed. It cannot tell a
caller who ignored a block from one who just arrived, so re-serving is simply
where the run stands, not something to hold against anyone.

A deviation is not a refusal either. A refusal means the document or the environment
is wrong and the agent cannot mend it -- the run stops. A deviation means the agent's
move missed: the DOCUMENT reopens (the pointer returns to its first instruction,
chained steps replay), the miss named -- and the repair counts survive the reopening.
"""
from __future__ import annotations

from .errors import Refusal
from .model import Instruction


def empty_answer(instruction: Instruction) -> str:
    return f"you submitted an empty answer to `{instruction}`."


def wrong_answer(instruction: Instruction, answer: str) -> str:
    return (f"`{answer}` is not in OPTIONS ({', '.join(instruction.options)}). "
            "Take one of them, verbatim.")


def register(instruction: Instruction, allowed: int) -> None:
    """Counts one deviation, and hands back to the operator once the bound is reached --
    the bound is the INSTANCE's (`SETTINGS.md`), never a constant of this module."""
    instruction.repairs += 1
    if instruction.repairs > allowed:
        raise Refusal("repair-exhausted",
                      f"`{instruction}` was repaired {allowed} times and still misses -- "
                      "the operator has to look at it")
