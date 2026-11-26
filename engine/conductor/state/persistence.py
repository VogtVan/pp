"""Behaviour: writing the run to a file so it outlives the process.

The slot is written by ONE door, `_store`, and read by ONE, `_read`. A call that advances the run
opens a TRANSACTION on its slot (`begin`): from then on every write of this module STAGES the
state in memory and every read sees it, and the call's end writes the slot once (`commit`) --
or never (`discard`): a refusal raised in the middle of the advance leaves the slot byte for
byte as the call found it. Outside a transaction -- a gesture, a view's offer map, the console's
note of a refusal -- a write arrives at once, as before."""
from __future__ import annotations

import json
import os
from pathlib import Path

from . import instance, record
from ..core import language
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


def reserve(member_meta: Path, run_id: str) -> bool:
    """-> True when the slot of `run_id` was free and is now RESERVED: created exclusively
    (`O_CREAT | O_EXCL`) holding `{}`, which the first save replaces; False when a slot
    already holds the key. Two openings never reserve one key: the file system decides.
    `_mint` draws a key here until one reserves."""
    slot = slot_of(member_meta, run_id)
    slot.parent.mkdir(parents=True, exist_ok=True)
    try:
        handle = os.open(slot, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    except FileExistsError:
        return False
    with os.fdopen(handle, "w", encoding="utf-8") as reserved:
        reserved.write("{}")
    return True


def reserved(session: Path) -> bool:
    """-> True while no save has replaced the slot yet: a reservation (`{}`)."""
    return _read(session) == {}


def _arrive(session: Path, state: dict) -> None:
    """The ONE arrival of a run's saved state: written beside it under a name of its own
    (`record.replace`), then moved into place -- a reader never sees a torn slot, and two
    calls writing the same run never share a temporary."""
    record.replace(session, json.dumps(state, indent=2, ensure_ascii=False))


class _Staged:
    """The state of one slot under a call's transaction: what the call has written so far, and
    whether it wrote anything."""

    __slots__ = ("state", "dirty")

    def __init__(self, state: dict | None) -> None:
        self.state, self.dirty = state, False


_STAGED: dict[Path, _Staged] = {}    # the slots under a transaction of THIS process


def begin(session: Path) -> bool:
    """Opens the TRANSACTION of one call on `session`: the slot is read once, and until `commit`
    or `discard` every write of this module stages its state in memory, every read sees what was
    staged. -> True when this call opened it; False when a call of this process holds it already
    -- the outer call owns the write, the inner one stages into it."""
    if session in _STAGED:
        return False
    _STAGED[session] = _Staged(_disk(session))
    return True


def commit(session: Path) -> None:
    """The ONE write of a call that advanced the run: what it staged arrives at the slot, once --
    nothing when it wrote nothing. The transaction closes."""
    staged = _STAGED.pop(session, None)
    if staged is not None and staged.dirty and staged.state is not None:
        _arrive(session, staged.state)


def discard(session: Path) -> None:
    """A call that refused: what it staged is forgotten, the slot stands as the call found it.
    The transaction closes."""
    _STAGED.pop(session, None)


def _disk(session: Path) -> dict | None:
    """-> the state the file at `session` holds, None when there is no file or it does not read."""
    try:
        state = json.loads(session.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return state if isinstance(state, dict) else None


def _read(session: Path) -> dict | None:
    """The ONE reading of a slot's state: the state a transaction of this process staged, else the
    file's. None when the slot holds no state (no file, or one that does not read)."""
    staged = _STAGED.get(session)
    return staged.state if staged is not None else _disk(session)


def _exists(session: Path) -> bool:
    """-> whether the slot HOLDS a run's state: staged under a transaction, or a file standing."""
    staged = _STAGED.get(session)
    return staged.state is not None if staged is not None else session.exists()


def _store(session: Path, state: dict) -> None:
    """The ONE writing of a slot's state: staged when a transaction of this process holds the slot,
    arrived at once otherwise."""
    staged = _STAGED.get(session)
    if staged is not None:
        staged.state, staged.dirty = state, True
    else:
        _arrive(session, state)


def run_id_of(slot: Path) -> str:
    return slot.stem.removeprefix("session-")


def meta_of(session: Path) -> Path:
    """-> the instance root a slot belongs to -- the inverse of `slot_of`."""
    return session.parents[len(Path(DIRECTORY).parts)]


def trace_of(session: Path) -> str | None:
    """-> the log file the saved run writes to, straight off the raw state -- readable
    even when a full restore would refuse (a discarded run still names its trace)."""
    state = _read(session)
    return state.get("log") if state is not None else None


def segments_of(session: Path) -> list[dict]:
    """-> the LAST RENDERED OUTPUT's segment map -- ordinal, frame, stack, tools,
    constraint lines per heading: what a `-s` call routes against. Addresses
    live with their output: the next rendered output replaces the map."""
    state = _read(session)
    if state is None:
        return []
    return state.get("segments", [])


def set_segments(session: Path, segments: list[dict]) -> None:
    """The offer map's one mutator outside a save: a VIEW replaces it with what it shows."""
    state = _read(session)
    if state is None:
        return
    state["segments"] = segments
    _store(session, state)


def set_emitted(session: Path, codes: list[str]) -> None:
    """Writes the run's list of the laws already shown whole (the codes mode's ledger), outside a save:
    a block built for an output the principal holds open is never served, so the laws only it showed
    leave the list."""
    state = _read(session)
    if state is None:
        return
    state["emitted"] = sorted(codes)
    _store(session, state)


def signals_of(session: Path) -> list:
    """-> the signals the run has latched -- what the bus crossed, held for the
    session; the reading matter of whatever contributor serves them."""
    state = _read(session)
    if state is None:
        return []
    return state.get("signals", [])


def mounted_of(session: Path) -> list:
    """-> the run's standing MOUNTS -- documents hosted into the current view: their
    laws and tools come with every block until the exchange ends. Nothing mounted, []."""
    state = _read(session)
    if state is None:
        return []
    return state.get("mounted", [])


SWITCHES = "switches"   # the run's OWN switches, `{package: "on"|"off"}`: what the launcher gave at
                        # `-new` (`PP_PACKAGES`) and what `-enable`/`-disable` wrote since; a name the run
                        # carries plays as it says, over `package.<name>` of SETTINGS


def switches_in(state: dict) -> dict[str, str]:
    """-> the run's switches a slot's state or a renewal mark carries, `{package: "on"|"off"}`; a slot
    written before the switches (`off: [...]`, a list of the packages the run took out) reads as that
    many `off`."""
    held = state.get(SWITCHES)
    if isinstance(held, dict):
        return {str(name): str(said) for name, said in held.items() if str(said) in ("on", "off")}
    return {str(one): "off" for one in state.get("off") or []}


def switches_of(session: Path) -> dict[str, str]:
    """-> the switches THIS run holds -- the launcher's word at `-new`, the operator's word said to
    the agent since --, `{}` for a fresh run, a reservation or no slot."""
    state = _read(session)
    if state is None:
        return {}
    return switches_in(state)


def set_switches(session: Path, switches: dict) -> None:
    """The switches' one mutator, written apart from the stack save: a process that dies between
    the two leaves the run's play exactly as it was. A slot of before loses its `off` list here:
    the switches say it."""
    state = _read(session)
    if state is None:
        return
    state.pop("off", None)
    if switches:
        state[SWITCHES] = {str(name): str(said) for name, said in switches.items()}
    else:
        state.pop(SWITCHES, None)
    _store(session, state)


def paths_of(session: Path) -> list[str]:
    """-> every document the run HOLDS: its stack frames' paths and its standing
    mounts' names -- what a switch asks before taking a package out of the play."""
    state = _read(session)
    if state is None:
        return []
    found = [str(one.get("document", "")) for one in state.get("frames", [])]
    found += [str(one.get("doc", "")) for one in state.get("mounted", [])
              if isinstance(one, dict)]
    return [one for one in found if one]


def compacted_of(session: Path) -> bool:
    """-> whether a compaction stands DECLARED and unanswered: the agent said its
    host summarized the session, and no output has served the run back yet."""
    state = _read(session)
    if state is None:
        return False
    return bool(state.get("compacted"))


def set_compacted(session: Path, declared: bool) -> None:
    """The declaration's one mutator: the verb ARMS it, the output that re-serves
    CONSUMES it -- written apart from the stack save so a process that dies between
    the two leaves the duty standing, never a run served back twice."""
    state = _read(session)
    if state is None:
        return
    if declared:
        state["compacted"] = True
    else:
        state.pop("compacted", None)
    _store(session, state)


def turns_of(session: Path) -> int:
    """-> the exchanges the run has COMPLETED, as the last save left them: 0 through
    the whole first exchange."""
    state = _read(session)
    if state is None:
        return 0
    return int(state.get("turns", 0))


def boot_of(session: Path) -> int:
    """-> the exchange count at which the agent's context last started from nothing:
    0 for a run's opening, the count at which a compaction was declared since. A slot
    without the field -- a run opened before the field existed -- reads 0."""
    state = _read(session)
    if state is None:
        return 0
    return int(state.get("boot", 0))


def set_boot(session: Path, turns: int) -> None:
    """The boot mark's one mutator: the compaction's declaration writes the count of
    the exchange where the context went -- apart from the stack save, as `compacted`
    is, so the mark stands whatever the process does next."""
    state = _read(session)
    if state is None:
        return
    state["boot"] = int(turns)
    _store(session, state)


def pending_of(session: Path) -> dict:
    """-> what a cut output left waiting: its matter, the groups of its steps, the foot that
    rides its LAST chunk and the readings staged until then: `{"matter", "steps", "tail",
    "head", "staged"}`. Nothing waiting, {}."""
    state = _read(session)
    if state is None:
        return {}
    return state.get("pending", {})


def set_pending(session: Path, pending: dict) -> None:
    """The cut's one mutator: the render SETS what is left, the next chunk CONSUMES it --
    the run's own state, never a file the agent has to open."""
    state = _read(session)
    if state is None:
        return
    if pending:
        state["pending"] = pending
    else:
        state.pop("pending", None)
    _store(session, state)


def add_proven(session: Path, tags: list[str]) -> None:
    """The readings DELIVERED whole join the run's proofs -- written at the render, after the
    step's save: a document is proven by its delivery, its last chunk gone, never by its
    composition."""
    state = _read(session)
    if state is None or not tags:
        return
    state["proven"] = sorted(set(state.get("proven", [])) | set(tags))
    _store(session, state)


def remove_proven(session: Path, tags: list[str]) -> None:
    """The readings of an output CUT under the cap leave the run's proofs until their last
    chunk is delivered -- the step's save came before the render, so the demotion is
    written here."""
    state = _read(session)
    if state is None or not tags:
        return
    state["proven"] = sorted(set(state.get("proven", [])) - set(tags))
    _store(session, state)


def set_mounted(session: Path, mounts: list) -> None:
    """The mounts' one mutator: the mount call SETS them, the exchange rewind
    SWEEPS them -- every other write preserves what stands; under a call's transaction
    the set is staged, and a refusal of the call forgets it."""
    state = _read(session)
    if state is None:
        return
    state["mounted"] = mounts
    _store(session, state)


DEBT = "debt"      # the frames that PRODUCED since the PROVE that covers them: what a written PROVE pays


def debt_of(session: Path) -> list:
    """-> the HOLDERS in debt -- `<depth>:<document>`, one per frame that gave a production
    of the agent's (a PICK, an INFER, a WORK) since the last PROVE that covered it. A PROVE
    written at depth d pays the frames at depth d and deeper: its own, and the callees that
    produced under its laws and popped; a frame below keeps its debt, its laws were not asked."""
    state = _read(session)
    if state is None:
        return []
    return [str(one) for one in state.get(DEBT) or []]


def set_debt(session: Path, holders: list) -> None:
    """The debt's one mutator: a production given adds its frame's holder, a PROVE played
    removes the holders it pays -- written apart from the stack save, as the owed laws are."""
    state = _read(session)
    if state is None:
        return
    kept = [str(one) for one in state.get(DEBT) or []]
    if kept == list(holders):
        return
    if holders:
        state[DEBT] = list(holders)
    else:
        state.pop(DEBT, None)
    _store(session, state)


def owed_of(session: Path) -> list:
    """-> the laws of production a document a SOCKET called left DUE when it left: its
    frame proves nothing at its exit, the next checkpoint names them -- `wire()` lines,
    in the order they were left. Nothing due, []."""
    state = _read(session)
    if state is None:
        return []
    return list(state.get("owed", []))


MATERIAL = "material"   # the launcher's material, `{"name": "work", "path": <path>}`: the tree
                        # the run works on, read by `-new` from `PP_WORKDIR`; no row names it:
                        # a row that names no tree reads it


def material_of(session: Path) -> dict:
    """-> the launcher's material at the slot -- `{"name", "path"}` --, or {} for a run
    that was given none."""
    state = _read(session)
    if state is None:
        return {}
    return dict(state.get(MATERIAL) or {})


def set_material(session: Path, material: dict) -> None:
    """The material's one mutator, written at the opening apart from the stack save; the
    save carries it, a renewal mark keeps it."""
    state = _read(session)
    if state is None:
        return
    if material:
        state[MATERIAL] = dict(material)
    else:
        state.pop(MATERIAL, None)
    _store(session, state)


DOCUMENTS = "documents"   # the launcher's root of documents, an absolute directory: read by
                          # `-new` from `PP_DOCUMENTS`, bound to the run at every call


def documents_of(session: Path) -> str:
    """-> the root of documents the run was given at `-new`, "" for a run given none."""
    state = _read(session)
    if state is None:
        return ""
    return str(state.get(DOCUMENTS) or "")


def set_documents(session: Path, root: str) -> None:
    """The root's one mutator, written at the opening apart from the stack save; the save
    carries it, a renewal mark keeps it."""
    state = _read(session)
    if state is None:
        return
    if root:
        state[DOCUMENTS] = str(root)
    else:
        state.pop(DOCUMENTS, None)
    _store(session, state)


PRINTS = "prints"   # the steps said on `terminal` whose production the agent has not printed yet


def prints_of(session: Path) -> list:
    """-> the prints DUE, in the order their steps were said -- one entry per step rendered
    `=> terminal`: `{"document", "keyword", "form", "instruction", "line", "stack", "refused"}`, the
    line as it was rendered, the stack where the step stood, the prints refused on their form. An
    entry leaves by its print call, by the door that stands for its step (traced `print-by-door`), or at the bound."""
    state = _read(session)
    if state is None:
        return []
    return [dict(one) for one in state.get(PRINTS) or []]


def set_prints(session: Path, entries: list) -> None:
    """The prints' one mutator: an output's close ADDS the steps it said on `terminal`, a print
    call takes its entry out or counts its refusal -- written apart from the stack save, which
    carries it."""
    state = _read(session)
    if state is None:
        return
    if entries:
        state[PRINTS] = [dict(one) for one in entries]
    else:
        state.pop(PRINTS, None)
    _store(session, state)


HELD = "held"   # the output a run HOLDS for the principal's call:
                # the agent's value was judged, its answer waits in the slot, not in the tool


def held_of(session: Path) -> dict:
    """-> the output held for the principal's call -- `{"matter", "steps", "tail", "head", "staged",
    "asks", "at", "chars"}`, the same pieces a cut keeps, with the count of the lines its closing
    block asks, and what a block that renders its step again takes over: `before` (what stands
    before the step it closes on) and `closing` (that step: what names it, what it read) --, or {}
    when none waits. An output the principal holds OPEN (`"open": true`) has rendered no block and
    keeps what its release renders instead: `advance` (the exchange has not advanced: the release
    plays it), `posed` (the addresses the mounts brought into the view), `payloads` and
    `ledger` (the readings the first block rendered carries, `proper` naming those proper to its
    step), `gaps`, `deviation`, `word`, `fusion`."""
    state = _read(session)
    if state is None:
        return {}
    return dict(state.get(HELD) or {})


def set_held(session: Path, held: dict) -> None:
    """The held output's one mutator: the agent's value call SETS it, the principal's bare
    call RELEASES it -- written apart from the stack save, which carries it."""
    state = _read(session)
    if state is None:
        return
    if held:
        state[HELD] = held
    else:
        state.pop(HELD, None)
    _store(session, state)


VIEWING = "viewing"   # the rest of a VIEW cut under the host's cap, in a run its principal
                      # conducts: a peek, a manual, a denial, a switch answered the agent's call
                      # in the tool return; what did not fit waits here for its bare keyed call


def viewing_of(session: Path) -> dict:
    """-> the rest of a view the agent's bare call serves -- `{"matter", "steps", "tail", "head"}`
    --, or {} when none waits."""
    state = _read(session)
    if state is None:
        return {}
    return dict(state.get(VIEWING) or {})


def set_viewing(session: Path, viewing: dict) -> None:
    """The view rest's one mutator: a view cut SETS it, the agent's bare call CONSUMES it, any
    other act of either caller FORGETS it -- written apart from the stack save, which carries it."""
    state = _read(session)
    if state is None:
        return
    if viewing:
        state[VIEWING] = viewing
    else:
        state.pop(VIEWING, None)
    _store(session, state)


def under_way(member_meta: Path) -> list[str]:
    """-> the keys of the runs of this instance that stand mid-exchange -- their slot waiting
    for a production: an agent is at work on them. What a `-new` that names its launcher's run
    (`PP_CONDUCTED_RUN`) asks before opening: such a `-new` is the agent's, and opens nothing."""
    found = []
    for slot in slots(member_meta):
        state = _read(slot)
        if state is None or state.get(RENEWED):
            continue
        if awaits_of(state) != MESSAGE:
            found.append(run_id_of(slot))
    return found


def set_owed(session: Path, lines: list) -> None:
    """The debt's one mutator: a socket document's exit ADDS its laws, a proven
    checkpoint CLEARS them -- written apart from the stack save, as the mounts are."""
    state = _read(session)
    if state is None:
        return
    if lines:
        state["owed"] = list(lines)
    else:
        state.pop("owed", None)
    _store(session, state)


def latch(session: Path, entry: dict) -> None:
    """One crossed signal joins the run's latches: at once outside a call's transaction (a
    refusal the console notes), with the call's one write under it -- a motor's moment that
    a refused call formed is the refused call's, and leaves with it."""
    state = _read(session)
    if state is None:
        return
    held = [one for one in state.get("signals", [])
            if (one.get("signal"), one.get("vector"))
            != (entry.get("signal"), entry.get("vector"))]
    state["signals"] = held + [entry]
    _store(session, state)


def save(session: Path, member: str, stack: Stack, served: dict, log: str | None,
         turns: int = 0, segments: list | None = None,
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
        "segments": segments,
        "signals": signals,
        "mounted": mounted_of(session),   # the hosted documents stand -- their own
                                          # mutator alone sets or sweeps them
        "compacted": compacted_of(session),   # a declared compaction stands until an
                                              # output serves the run back
        "boot": boot_of(session),             # the exchange the context last started at --
                                              # 0 at the opening, set by the compaction
        **({SWITCHES: switches} if (switches := switches_of(session)) else {}),   # the run's own
                                              # switches -- their own mutator sets them, the save carries them
        **({DEBT: debt} if (debt := debt_of(session)) else {}),   # the frames in debt since their PROVE
        "owed": owed_of(session),             # the laws a socket document left due -- their
                                              # own mutator sets them, a proof clears them
        **({PRINTS: prints} if (prints := prints_of(session)) else {}),   # the prints due -- their
                                              # own mutator sets them
        **({HELD: held} if (held := held_of(session)) else {}),   # the output held for the
                                              # principal's call -- its own mutator sets it
        **({VIEWING: viewing} if (viewing := viewing_of(session)) else {}),   # the rest of a
                                              # view the agent's bare call serves -- its own mutator
        **({STOPPED: stopped} if (stopped := stopped_of(session)) else {}),   # the run stopped
                                              # at the repair bound -- its own mutator sets it
        **({MATERIAL: material} if (material := material_of(session)) else {}),   # the
                                              # launcher's material -- its own mutator sets it
        **({DOCUMENTS: root} if (root := documents_of(session)) else {}),   # the launcher's
                                              # root of documents -- its own mutator sets it
        "frames": [_dump(stack.frames, index) for index in range(len(stack.frames))],
    }
    _store(session, state)   # atomic: a half-written run is worse than none -- and staged
                             # under a call's transaction, arrived once at the call's end


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
        "field": frame.field,
        "routed": ([one.wire() for one in frame.routed]
                   if frame.routed is not None else None),
        "instructions": [{"keyword": one.keyword, "argument": one.argument,
                          "taken": one.taken, "given": one.given, "done": one.done,
                          "offset": one.offset, "slot": one.slot, "repairs": one.repairs,
                          "injected": one.injected, "site": one.site, "guard": one.guard,
                          "barrier": one.barrier, "asked": one.asked,
                          "routed": list(one.routed), "refit": list(one.refit)}
                         for one in frame.procedure.instructions],
    }


def restore(session: Path, revive) -> tuple[str, Stack, dict, str | None, int, list, list] | None:
    """-> (member, the WHOLE STACK, what was served, the run's log file name, the
    count of completed turns, the readings proven by content, the codes-mode ledger), or None when no run is under way -- a renewal mark holds
    none: the next keyed call reopens it (`renewed`). `revive(meta,
    path)` is the CALLER's reader of a saved frame's document -> (document, its
    declared procedure, its own laws, its own tools, its cycle): persistence keeps
    what was saved and never reads a document or compiles a law itself -- the
    facade feeds it (a data module imports no process module)."""
    if not _exists(session):
        return None
    state = _read(session)
    if state is None:
        raise ValueError(f"{session} does not read as a run")
    if RENEWED in state:
        return None
    frames: list[Frame] = []
    for index, kept_frame in enumerate(state["frames"]):
        document, declared, own_constraints, own_tools, cycle = revive(
            meta_of(session), Path(kept_frame["document"]))   # a proc-less callee replays its implicit INFER
        saved = kept_frame["instructions"]
        # a run may carry INJECTED instructions (a HOOK expanded) -- the document only
        # vouches for what it DECLARES: when that part no longer matches, the document changed
        # under the run -- the frame plays the steps it saved, and carries the new declaration
        # for the next opening to reseat it on
        written = [(one["keyword"], one["argument"]) for one in saved
                   if not one.get("injected")]
        drifted = written != [(one.keyword, one.argument) for one in declared.instructions]
        procedure = Procedure(instructions=[
            Instruction(keyword=kept["keyword"], argument=kept["argument"],
                        injected=kept.get("injected", False),
                        # a slot saved before the entry table carried `socket: true`: the
                        # socket path, read as such -- no migration, no refusal
                        site=kept.get("site") or ("socket" if kept.get("socket") else ""),
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
                      field=kept_frame.get("field"), routed=routed,
                      declared=declared if drifted else None)
        if kept_frame.get("caller_index") is not None:
            frame.caller = frames[index - 1].procedure.instructions[kept_frame["caller_index"]]
        frames.append(frame)
    return (state["member"], Stack(frames=frames), state.get("served", {}),
            state.get("log"), state.get("turns", 0),
            list(state.get("proven", [])),
            list(state.get("emitted", [])))


def forget(session: Path) -> None:
    _STAGED.pop(session, None)
    session.unlink(missing_ok=True)


def dropped(session: Path) -> None:
    """Forgets the run of `session` with every file of its own beside it, `session-<key>.*`
    -- its locks, a launcher's log; its trace stays (`session-<stamp>Z-<key>.jsonl`): the
    history of a run outlives it. A file the platform keeps open stays, free (Windows)."""
    _STAGED.pop(session, None)
    key = run_id_of(session)
    for path in session.parent.glob(f"session-{key}.*"):
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass


STOPPED = "stopped"   # the mark of a run STOPPED at the repair bound: the step still pends under
                      # it, the stack as it stood, and the run awaits the principal's word --
                      # `{"document", "instruction", "repairs", "miss", "at"}`


def stopped_of(session: Path) -> dict:
    """-> the mark of a run stopped at the repair bound, or {} when the run is not."""
    state = _read(session)
    if state is None:
        return {}
    return dict(state.get(STOPPED) or {})


def set_stopped(session: Path, mark: dict) -> None:
    """The mark's one mutator: the bound SETS it, the call that takes the run up CLEARS it --
    written apart from the stack save, which carries it."""
    state = _read(session)
    if state is None:
        return
    if mark:
        state[STOPPED] = mark
    else:
        state.pop(STOPPED, None)
    _store(session, state)


RENEWED = "renewed"   # the key of a renewal mark: what an upgrade leaves of a run


MESSAGE = "message"         # what a PARKED run waits for: the root of its passage is exhausted
PRODUCTION = "production"   # what a run mid-passage waits for: a step pends


def awaits_of(state: dict) -> str:
    """-> what a saved run waits for -- `message` when its top frame is exhausted or when the run
    is STOPPED at the repair bound (the step pends under the mark, the principal's word takes it
    up), `production` otherwise. The engine pops every exhausted frame but the ROOT of the passage
    before it saves a call's end (the root is decided at one site, the facade's `_root`): an
    exhausted top frame IS the parked root. The saved form of what the next call reads to tell a
    message from a production, and of what whoever makes the run advance reads to know whether to
    speak; no document is read."""
    if state.get(STOPPED):
        return MESSAGE
    frames = state.get("frames") or []
    if not frames:
        return PRODUCTION
    if any(not one.get("done") for one in frames[-1].get("instructions") or []):
        return PRODUCTION
    return MESSAGE


def awaits(session: Path) -> str:
    """-> what the run saved at `session` WAITS for, the one face a launcher reads it with: `message`
    when the root of its passage is exhausted, `production` when a step pends -- `awaits_of` on the
    slot's state; the `awaits` a renewal mark kept, since the mark has no frames; `production` for
    no slot or one that does not read."""
    state = _read(session)
    if state is None:
        return PRODUCTION
    if isinstance(state.get(RENEWED), dict):
        return MESSAGE if state.get("awaits") == MESSAGE else PRODUCTION
    return awaits_of(state)


def renewed(session: Path) -> dict | None:
    """-> the renewal MARK an upgrade left at `session` in place of the run's state --
    `{"renewed": {"at", "from", "to"}, "log", "turns", "switches", "awaits"}` -- or None for a
    run, a reservation or no slot. The mark keeps the key held: the next keyed call reopens
    the run under it."""
    state = _read(session)
    if state is None or not isinstance(state.get(RENEWED), dict):
        return None
    return state


def renew(session: Path, moved_from: dict, moved_to: dict, at: str) -> None:
    """Writes the RENEWAL MARK of the run at `session` in place of its state: the key stays
    held at the same path, and what crosses a version is kept -- the trace's name, the
    exchanges completed, the run's own switches, what it waited for (a message, a
    production). The run's other files (`session-<key>.*`: its locks, a launcher's
    log) go; its trace stays. A mark standing already crosses again: `to` follows the new
    versions, `at` and `from` are kept."""
    state = _read(session) or {}
    standing = state.get(RENEWED)
    if isinstance(standing, dict):
        mark = {**state, RENEWED: {"at": standing.get("at", at),
                                   "from": {**moved_from, **(standing.get("from") or {})},
                                   "to": {**(standing.get("to") or {}), **moved_to}}}
    else:
        mark = {RENEWED: {"at": at, "from": dict(moved_from), "to": dict(moved_to)},
                "log": state.get("log"), "turns": int(state.get("turns", 0)),
                **({SWITCHES: switches} if (switches := switches_in(state)) else {}), "awaits": awaits_of(state),
                **({MATERIAL: state[MATERIAL]} if state.get(MATERIAL) else {}),
                **({DOCUMENTS: state[DOCUMENTS]} if state.get(DOCUMENTS) else {})}
    key = run_id_of(session)
    for path in session.parent.glob(f"session-{key}.*"):
        if path == session:
            continue
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
    _store(session, mark)
