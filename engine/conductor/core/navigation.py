"""Behaviour: moving inside a frame. The pointer is DERIVED -- there is no second place to look."""
from __future__ import annotations

from . import language
from .errors import Refusal
from .model import Data, Frame, Instruction, Stack


def pointer(frame: Frame) -> int:
    """-> the index of the first instruction not yet done."""
    return next((i for i, one in enumerate(frame.procedure.instructions) if not one.done),
                len(frame.procedure))


def exhausted(frame: Frame) -> bool:
    return pointer(frame) >= len(frame.procedure)


def position(frame: Frame) -> int:
    """1-based, for the agent: `2/3` reads better than `index 1`. An exhausted frame
    stands AT its last instruction, never past it."""
    return min(pointer(frame) + 1, len(frame.procedure))


def peek(frame: Frame) -> Instruction:
    if exhausted(frame):
        raise Refusal("frame-exhausted", f"{frame.document.name} has no instruction left")
    return frame.procedure.instructions[pointer(frame)]


def upstream(frame: Frame) -> Data:
    """-> what the last instruction that PRODUCES something gave: the pipeline flows past the rest."""
    for earlier in reversed(frame.procedure.instructions[:pointer(frame)]):
        if not language.transparent(earlier.keyword):
            return earlier.given
    return frame.seed          # a callee with an `input:` opens on its caller's production


def give(instruction: Instruction, data: Data) -> None:
    instruction.given, instruction.done = data, True


def current(stack: Stack) -> Frame:
    if not stack.frames:
        raise Refusal("stack-empty", "no frame in flight")
    return stack.frames[-1]


def push(stack: Stack, frame: Frame) -> None:
    """CALL opens a frame -- it becomes `current`, the caller waits underneath."""
    stack.frames.append(frame)


def pop(stack: Stack) -> Frame:
    """The callee is exhausted -- drop it, its caller's frame resurfaces as `current`."""
    return stack.frames.pop()


def rewind(frame: Frame) -> None:
    """A cycling frame -- the session floor, or an iterated door with an element due --
    does not leave when exhausted: its instructions reset, ready to play again, the frame
    stays exactly where it is, never popped back to its caller.
    Runtime-injected instructions (an agent-opened proc) are PURGED, not reset: reset,
    they would replay every cycle the agent never asked for again."""
    frame.procedure.instructions = [one for one in frame.procedure.instructions
                                    if not one.injected]
    for instruction in frame.procedure.instructions:
        instruction.given, instruction.done = None, False
        instruction.offset, instruction.slot, instruction.repairs = 0, 0, 0


def reopen(frame: Frame) -> None:
    """A REPAIR reopens the WHOLE document: the pointer returns to the first
    instruction, chained steps will replay -- but the repair COUNTS survive, or the
    bound would never hand back to the operator. Injected instructions are purged,
    exactly like `rewind`."""
    frame.procedure.instructions = [one for one in frame.procedure.instructions
                                    if not one.injected]
    for instruction in frame.procedure.instructions:
        instruction.given, instruction.done = None, False
        instruction.offset, instruction.slot = 0, 0


def render(stack: Stack, at: int | None = None) -> str:
    """The stack is a PROJECTION of what ran -- never a retelling. An ancestor sits
    on its CALL for as long as its callee lives: its counter is a dead badge, and a
    runtime injection makes its total drift -- the path stays, bare; the ACTIVE
    frame alone carries the pointer. `at` names that pointer when the caller shows a
    step other than the one the frame stands on -- a view re-showing what an output
    asked for."""
    if not stack.frames:
        return ""
    ancestors = [frame.document.name for frame in stack.frames[:-1]]
    active = stack.frames[-1]
    return " ▸ ".join(ancestors + [
        f"{active.document.name}{{{at or position(active)}/{len(active.procedure)}}}"])
