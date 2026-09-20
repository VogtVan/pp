"""Behaviour: writing the run to a file so it outlives the process."""
from __future__ import annotations

import json
import os
from pathlib import Path

from . import instance
from ..core.errors import Refusal
from ..core.model import Constraint, Frame, Instruction, Procedure, Stack

DIRECTORY = instance.STATE


def slot_of(member_meta: Path, run_id: str) -> Path:
    """One SLOT per run: `session-<id>.json`. The slot belongs to the checkout that
    OPENED the run -- it never follows a switch."""
    return member_meta / DIRECTORY / f"session-{run_id}.json"


def slots(member_meta: Path) -> list[Path]:
    """-> every run standing, sorted by name. The traces (`.jsonl`) are not runs."""
    state = member_meta / DIRECTORY
    return sorted(state.glob("session-*.json")) if state.is_dir() else []


def run_id_of(slot: Path) -> str:
    return slot.stem.removeprefix("session-")


def meta_of(session: Path) -> Path:
    """-> the instance root a slot belongs to -- the inverse of `slot_of`."""
    return session.parents[len(Path(DIRECTORY).parts)]


def trace_of(session: Path) -> str | None:
    """-> the log file the saved run writes to, straight off the raw state -- readable
    even when a full restore would refuse (a discarded run still names its trace)."""
    if not session.exists():
        return None
    try:
        return json.loads(session.read_text(encoding="utf-8")).get("log")
    except Exception:
        return None


def segments_of(session: Path) -> list[dict]:
    """-> the LAST RENDERED OUTPUT's segment map -- ordinal, frame, stack, tools,
    constraint lines per heading: what a `-s` call routes against. Addresses
    live with their output: the next rendered output replaces the map."""
    if not session.exists():
        return []
    try:
        return json.loads(session.read_text(encoding="utf-8")).get("segments", [])
    except Exception:
        return []


def signals_of(session: Path) -> list:
    """-> the signals the run has latched -- what the bus crossed, held for the
    session; the reading matter of whatever contributor serves them."""
    if not session.exists():
        return []
    try:
        return json.loads(session.read_text(encoding="utf-8")).get("signals", [])
    except Exception:
        return []


def mounted_of(session: Path) -> list:
    """-> the run's standing MOUNTS -- documents hosted into the current view: their
    laws and tools come with every block until the exchange ends. Nothing mounted, []."""
    if not session.exists():
        return []
    try:
        return json.loads(session.read_text(encoding="utf-8")).get("mounted", [])
    except Exception:
        return []


def off_of(session: Path) -> list:
    """-> the packages THIS run switched off -- the soft switch, the operator's word
    said to the agent and written here; a fresh run switches nothing off."""
    if not session.exists():
        return []
    try:
        return list(json.loads(session.read_text(encoding="utf-8")).get("off", []))
    except Exception:
        return []


def set_off(session: Path, names: list) -> None:
    """The soft switches' one mutator, written apart from the stack save: a process
    that dies between the two leaves the run's play exactly as it was."""
    if not session.exists():
        return
    try:
        state = json.loads(session.read_text(encoding="utf-8"))
    except Exception:
        return
    if names:
        state["off"] = sorted(str(one) for one in names)
    else:
        state.pop("off", None)
    temporary = session.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temporary, session)


def paths_of(session: Path) -> list[str]:
    """-> every document the run HOLDS: its stack frames' paths and its standing
    mounts' names -- what a switch asks before taking a package out of the play."""
    if not session.exists():
        return []
    try:
        state = json.loads(session.read_text(encoding="utf-8"))
    except Exception:
        return []
    found = [str(one.get("document", "")) for one in state.get("frames", [])]
    found += [str(one.get("doc", "")) for one in state.get("mounted", [])
              if isinstance(one, dict)]
    return [one for one in found if one]


def compacted_of(session: Path) -> bool:
    """-> whether a compaction stands DECLARED and unanswered: the agent said its
    host summarized the session, and no output has served the run back yet."""
    if not session.exists():
        return False
    try:
        return bool(json.loads(session.read_text(encoding="utf-8")).get("compacted"))
    except Exception:
        return False


def set_compacted(session: Path, declared: bool) -> None:
    """The declaration's one mutator: the verb ARMS it, the output that re-serves
    CONSUMES it -- written apart from the stack save so a process that dies between
    the two leaves the duty standing, never a run served back twice."""
    if not session.exists():
        return
    try:
        state = json.loads(session.read_text(encoding="utf-8"))
    except Exception:
        return
    if declared:
        state["compacted"] = True
    else:
        state.pop("compacted", None)
    temporary = session.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temporary, session)


def turns_of(session: Path) -> int:
    """-> the exchanges the run has COMPLETED, as the last save left them: 0 through
    the whole first exchange."""
    if not session.exists():
        return 0
    try:
        return int(json.loads(session.read_text(encoding="utf-8")).get("turns", 0))
    except Exception:
        return 0


def boot_of(session: Path) -> int:
    """-> the exchange count at which the agent's context last started from nothing:
    0 for a run's opening, the count at which a compaction was declared since. A slot
    without the field -- a run opened before the field existed -- reads 0."""
    if not session.exists():
        return 0
    try:
        return int(json.loads(session.read_text(encoding="utf-8")).get("boot", 0))
    except Exception:
        return 0


def set_boot(session: Path, turns: int) -> None:
    """The boot mark's one mutator: the compaction's declaration writes the count of
    the exchange where the context went -- apart from the stack save, as `compacted`
    is, so the mark stands whatever the process does next."""
    if not session.exists():
        return
    try:
        state = json.loads(session.read_text(encoding="utf-8"))
    except Exception:
        return
    state["boot"] = int(turns)
    temporary = session.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temporary, session)


def pending_of(session: Path) -> dict:
    """-> the matter a cut block left waiting, with the tail that rides its LAST chunk and
    the readings staged until then: `{"matter", "tail", "head", "staged"}`. Nothing
    waiting, {}."""
    if not session.exists():
        return {}
    try:
        return json.loads(session.read_text(encoding="utf-8")).get("pending", {})
    except Exception:
        return {}


def set_pending(session: Path, pending: dict) -> None:
    """The cut's one mutator: the render SETS what is left, the next chunk CONSUMES it --
    the run's own state, never a file the agent has to open."""
    if not session.exists():
        return
    try:
        state = json.loads(session.read_text(encoding="utf-8"))
    except Exception:
        return
    if pending:
        state["pending"] = pending
    else:
        state.pop("pending", None)
    temporary = session.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temporary, session)


def add_proven(session: Path, tags: list[str]) -> None:
    """The readings DELIVERED whole join the run's proofs -- written at the render, after the
    step's save: a document is proven by its delivery, its last chunk gone, never by its
    composition."""
    if not session.exists() or not tags:
        return
    try:
        state = json.loads(session.read_text(encoding="utf-8"))
    except Exception:
        return
    state["proven"] = sorted(set(state.get("proven", [])) | set(tags))
    temporary = session.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temporary, session)


def remove_proven(session: Path, tags: list[str]) -> None:
    """The readings of an output CUT under the cap leave the run's proofs until their last
    chunk is delivered -- the step's save came before the render, so the demotion is
    written here."""
    if not session.exists() or not tags:
        return
    try:
        state = json.loads(session.read_text(encoding="utf-8"))
    except Exception:
        return
    state["proven"] = sorted(set(state.get("proven", [])) - set(tags))
    temporary = session.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temporary, session)


def set_mounted(session: Path, mounts: list) -> None:
    """The mounts' one mutator: the mount call SETS them, the exchange rewind
    SWEEPS them -- every other write preserves what stands."""
    if not session.exists():
        return
    try:
        state = json.loads(session.read_text(encoding="utf-8"))
    except Exception:
        return
    state["mounted"] = mounts
    temporary = session.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temporary, session)


def latch(session: Path, entry: dict) -> None:
    """One crossed signal joins the run's latches -- immediate and atomic: a motor's
    moment (a refusal, a repair) may never reach a stack save."""
    if not session.exists():
        return
    try:
        state = json.loads(session.read_text(encoding="utf-8"))
    except Exception:
        return
    held = [one for one in state.get("signals", [])
            if (one.get("signal"), one.get("vector"))
            != (entry.get("signal"), entry.get("vector"))]
    state["signals"] = held + [entry]
    temporary = session.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temporary, session)


def save(session: Path, member: str, stack: Stack, served: dict, log: str | None,
         turns: int = 0, ephemerals: list | None = None, segments: list | None = None,
         signals: list | None = None, proven: list | None = None,
         emitted: list | None = None) -> None:
    if segments is None:
        segments = segments_of(session)   # a re-show keeps the standing addresses
    if signals is None:
        signals = signals_of(session)     # untouched latches stand
    state = {
        "member": member,
        "served": served,
        "proven": sorted(proven or []),   # the readings this run proved, by content --
                                          # a document is never served twice
        "emitted": sorted(emitted or []),  # the codes-mode ledger: laws whose text
                                          # the run has rendered once already
        "log": log,
        "turns": turns,
        "ephemerals": list(ephemerals or []),   # the drafts' documents, in step order
        "segments": segments,
        "signals": signals,
        "mounted": mounted_of(session),   # the hosted documents stand -- their own
                                          # mutator alone sets or sweeps them
        "compacted": compacted_of(session),   # a declared compaction stands until an
                                              # output serves the run back
        "boot": boot_of(session),             # the exchange the context last started at --
                                              # 0 at the opening, set by the compaction
        "off": off_of(session),               # the run's soft switches -- their own
                                              # mutator sets them, the save carries them
        "frames": [_dump(stack.frames, index) for index in range(len(stack.frames))],
    }
    session.parent.mkdir(parents=True, exist_ok=True)
    temporary = session.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temporary, session)   # atomic: a half-written run is worse than none


def _dump(frames: list[Frame], index: int) -> dict:
    frame = frames[index]
    caller_index = None
    if frame.caller is not None:
        caller_index = next(i for i, one in enumerate(frames[index - 1].procedure.instructions)
                            if one is frame.caller)
    return {
        "document": str(frame.document.path),
        "caller_index": caller_index,
        "seed": frame.seed,
        "routed": ([str(one) for one in frame.routed]
                   if frame.routed is not None else None),
        "instructions": [{"keyword": one.keyword, "argument": one.argument,
                          "taken": one.taken, "given": one.given, "done": one.done,
                          "offset": one.offset, "slot": one.slot, "repairs": one.repairs,
                          "injected": one.injected, "socket": one.socket, "guard": one.guard,
                          "barrier": one.barrier, "asked": one.asked,
                          "routed": list(one.routed), "refit": list(one.refit)}
                         for one in frame.procedure.instructions],
    }


def restore(session: Path, revive) -> tuple[str, Stack, dict, str | None, int, list, list] | None:
    """-> (member, the WHOLE STACK, what was served, the run's log file name, the
    count of completed turns, the documents of the drafts standing since the last frontier, the
    readings proven by content), or None when no run is under way. `revive(meta,
    path)` is the CALLER's reader of a saved frame's document -> (document, its
    declared procedure, its own laws, its own tools, its cycle): persistence keeps
    what was saved and never reads a document or compiles a law itself -- the
    facade feeds it (a data module imports no process module)."""
    if not session.exists():
        return None
    state = json.loads(session.read_text(encoding="utf-8"))
    frames: list[Frame] = []
    for index, kept_frame in enumerate(state["frames"]):
        document, declared, own_constraints, own_tools, cycle = revive(
            meta_of(session), Path(kept_frame["document"]))   # a proc-less callee replays its implicit INFER
        saved = kept_frame["instructions"]
        # a run may carry INJECTED instructions (a HOOK expanded) -- the document only
        # vouches for what it DECLARES: that part must still match, or it changed under us.
        written = [(one["keyword"], one["argument"]) for one in saved
                   if not one.get("injected")]
        if written != [(one.keyword, one.argument) for one in declared.instructions]:
            raise Refusal("session-stale",
                          f"{document.name} no longer declares the instructions the saved "
                          "run was playing -- the document changed under it")
        procedure = Procedure(instructions=[
            Instruction(keyword=kept["keyword"], argument=kept["argument"],
                        injected=kept.get("injected", False), socket=kept.get("socket", False),
                        guard=kept.get("guard", ""),
                        barrier=kept.get("barrier", False), asked=kept.get("asked", False),
                        routed=tuple(kept.get("routed", ())))
            for kept in saved])
        for one, kept in zip(procedure.instructions, saved):
            one.taken, one.given, one.done = kept["taken"], kept["given"], kept["done"]
            one.offset, one.slot = kept["offset"], kept.get("slot", 0)
            one.repairs = kept["repairs"]
            one.refit = tuple(kept.get("refit", ()))
        routed = kept_frame.get("routed")
        if routed is not None:
            # a routed callee inherits its SNAPSHOT, never the caller chain -- the
            # same laws stand however many processes the frame's life spans
            routed = tuple(Constraint.parse(line) for line in routed)
            constraints = routed + own_constraints
        else:
            constraints = (own_constraints if index == 0
                           else frames[index - 1].constraints + own_constraints)
        if index == 0:
            tools = own_tools
        else:      # a name is offered ONCE at a step -- the same dedup the runner applies
            offered = {one.name for one in frames[index - 1].tools}
            tools = frames[index - 1].tools + tuple(one for one in own_tools
                                                    if one.name not in offered)
        frame = Frame(document=document, procedure=procedure, constraints=constraints, tools=tools,
                      cycle=cycle, seed=kept_frame.get("seed"),
                      routed=routed)
        if kept_frame.get("caller_index") is not None:
            frame.caller = frames[index - 1].procedure.instructions[kept_frame["caller_index"]]
        frames.append(frame)
    return (state["member"], Stack(frames=frames), state.get("served", {}),
            state.get("log"), state.get("turns", 0), list(state.get("ephemerals", [])),
            list(state.get("proven", [])),
            list(state.get("emitted", [])))


def forget(session: Path) -> None:
    session.unlink(missing_ok=True)
