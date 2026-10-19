"""Behaviour: writing the run to a file so it outlives the process."""
from __future__ import annotations

import json
import os
from pathlib import Path

from . import instance, record
from ..core import language
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
    try:
        return session.read_text(encoding="utf-8").strip() == "{}"
    except OSError:
        return False


def _arrive(session: Path, state: dict) -> None:
    """The ONE arrival of a run's saved state: written beside it under a name of its own
    (`record.replace`), then moved into place -- a reader never sees a torn slot, and two
    calls writing the same run never share a temporary."""
    record.replace(session, json.dumps(state, indent=2, ensure_ascii=False))


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
    _arrive(session, state)


MODE = "conducted_by"   # who makes the run advance: the slot holds it for a run its principal
PRINCIPAL = "principal"  # conducts; absent, the LLM conducts it -- today's run, its slot unchanged


def mode_of(session: Path) -> str:
    """-> the run's conduction mode: `principal`, or "" for a run the LLM conducts."""
    if not session.exists():
        return ""
    try:
        return str(json.loads(session.read_text(encoding="utf-8")).get(MODE, ""))
    except Exception:
        return ""


def set_mode(session: Path, mode: str) -> None:
    """The mode's one mutator, written at the opening apart from the stack save; the save
    carries it, a renewal mark keeps it."""
    if not session.exists():
        return
    try:
        state = json.loads(session.read_text(encoding="utf-8"))
    except Exception:
        return
    if mode:
        state[MODE] = mode
    else:
        state.pop(MODE, None)
    _arrive(session, state)


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
    _arrive(session, state)


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
    _arrive(session, state)


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
    _arrive(session, state)


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
    _arrive(session, state)


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
    _arrive(session, state)


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
    _arrive(session, state)


def owed_of(session: Path) -> list:
    """-> the laws of production a document a SOCKET called left DUE when it left: its
    frame proves nothing at its exit, the next checkpoint names them -- `wire()` lines,
    in the order they were left. Nothing due, []."""
    if not session.exists():
        return []
    try:
        return list(json.loads(session.read_text(encoding="utf-8")).get("owed", []))
    except Exception:
        return []


MATERIAL = "material"   # the launcher's material, `{"name": "work", "path": <path>}`: the tree
                        # the run works on, read by `-new` from `PP_WORKDIR`, named by `@work`


def material_of(session: Path) -> dict:
    """-> the launcher's material at the slot -- `{"name", "path"}` --, or {} for a run
    that was given none."""
    if not session.exists():
        return {}
    try:
        return dict(json.loads(session.read_text(encoding="utf-8")).get(MATERIAL) or {})
    except Exception:
        return {}


def set_material(session: Path, material: dict) -> None:
    """The material's one mutator, written at the opening apart from the stack save; the
    save carries it, a renewal mark keeps it."""
    if not session.exists():
        return
    try:
        state = json.loads(session.read_text(encoding="utf-8"))
    except Exception:
        return
    if material:
        state[MATERIAL] = dict(material)
    else:
        state.pop(MATERIAL, None)
    _arrive(session, state)


DOCUMENTS = "documents"   # the launcher's root of documents, an absolute directory: read by
                          # `-new` from `PP_DOCUMENTS`, bound to the run at every call


def documents_of(session: Path) -> str:
    """-> the root of documents the run was given at `-new`, "" for a run given none."""
    if not session.exists():
        return ""
    try:
        return str(json.loads(session.read_text(encoding="utf-8")).get(DOCUMENTS) or "")
    except Exception:
        return ""


def set_documents(session: Path, root: str) -> None:
    """The root's one mutator, written at the opening apart from the stack save; the save
    carries it, a renewal mark keeps it."""
    if not session.exists():
        return
    try:
        state = json.loads(session.read_text(encoding="utf-8"))
    except Exception:
        return
    if root:
        state[DOCUMENTS] = str(root)
    else:
        state.pop(DOCUMENTS, None)
    _arrive(session, state)


HELD = "held"   # the output a run its principal conducts HOLDS for the principal's call:
                # the agent's value was judged, its answer waits in the slot, not in the tool


def held_of(session: Path) -> dict:
    """-> the output held for the principal's call -- `{"matter", "tail", "head", "staged",
    "at", "chars"}`, the same pieces a cut keeps --, or {} when none waits."""
    if not session.exists():
        return {}
    try:
        return dict(json.loads(session.read_text(encoding="utf-8")).get(HELD) or {})
    except Exception:
        return {}


def set_held(session: Path, held: dict) -> None:
    """The held output's one mutator: the agent's value call SETS it, the principal's bare
    call RELEASES it -- written apart from the stack save, which carries it."""
    if not session.exists():
        return
    try:
        state = json.loads(session.read_text(encoding="utf-8"))
    except Exception:
        return
    if held:
        state[HELD] = held
    else:
        state.pop(HELD, None)
    _arrive(session, state)


VIEWING = "viewing"   # the rest of a VIEW cut under the host's cap, in a run its principal
                      # conducts: a peek, a manual, a denial, a switch answered the agent's call
                      # in the tool return; what did not fit waits here for its bare keyed call


def viewing_of(session: Path) -> dict:
    """-> the rest of a view the agent's bare call serves -- `{"matter", "tail", "head"}` --,
    or {} when none waits."""
    if not session.exists():
        return {}
    try:
        return dict(json.loads(session.read_text(encoding="utf-8")).get(VIEWING) or {})
    except Exception:
        return {}


def set_viewing(session: Path, viewing: dict) -> None:
    """The view rest's one mutator: a view cut SETS it, the agent's bare call CONSUMES it, any
    other act of either caller FORGETS it -- written apart from the stack save, which carries it."""
    if not session.exists():
        return
    try:
        state = json.loads(session.read_text(encoding="utf-8"))
    except Exception:
        return
    if viewing:
        state[VIEWING] = viewing
    else:
        state.pop(VIEWING, None)
    _arrive(session, state)


def under_way(member_meta: Path) -> list[str]:
    """-> the keys of the runs this instance's PRINCIPAL conducts that stand mid-exchange --
    their slot not at the frontier: an agent is at work on them. What an unmarked `-new`
    asks before opening: such a `-new` is the agent's, and opens nothing."""
    found = []
    for slot in slots(member_meta):
        try:
            state = json.loads(slot.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(state, dict) or state.get(RENEWED) or state.get(MODE) != PRINCIPAL:
            continue
        if not frontier_of(state):
            found.append(run_id_of(slot))
    return found


def set_owed(session: Path, lines: list) -> None:
    """The debt's one mutator: a socket document's exit ADDS its laws, a proven
    checkpoint CLEARS them -- written apart from the stack save, as the mounts are."""
    if not session.exists():
        return
    try:
        state = json.loads(session.read_text(encoding="utf-8"))
    except Exception:
        return
    if lines:
        state["owed"] = list(lines)
    else:
        state.pop("owed", None)
    _arrive(session, state)


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
    _arrive(session, state)


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
        "off": off_of(session),               # the run's soft switches -- their own
                                              # mutator sets them, the save carries them
        "owed": owed_of(session),             # the laws a socket document left due -- their
                                              # own mutator sets them, a proof clears them
        **({MODE: mode} if (mode := mode_of(session)) else {}),   # the run's mode, when its
                                              # principal conducts it -- its own mutator sets it
        **({HELD: held} if (held := held_of(session)) else {}),   # the output held for the
                                              # principal's call -- its own mutator sets it
        **({VIEWING: viewing} if (viewing := viewing_of(session)) else {}),   # the rest of a
                                              # view the agent's bare call serves -- its own mutator
        **({MATERIAL: material} if (material := material_of(session)) else {}),   # the
                                              # launcher's material -- its own mutator sets it
        **({DOCUMENTS: root} if (root := documents_of(session)) else {}),   # the launcher's
                                              # root of documents -- its own mutator sets it
        "frames": [_dump(stack.frames, index) for index in range(len(stack.frames))],
    }
    _arrive(session, state)   # atomic: a half-written run is worse than none


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
    if not session.exists():
        return None
    state = json.loads(session.read_text(encoding="utf-8"))
    if RENEWED in state:
        return None
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
                      field=kept_frame.get("field"), routed=routed)
        if kept_frame.get("caller_index") is not None:
            frame.caller = frames[index - 1].procedure.instructions[kept_frame["caller_index"]]
        frames.append(frame)
    return (state["member"], Stack(frames=frames), state.get("served", {}),
            state.get("log"), state.get("turns", 0),
            list(state.get("proven", [])),
            list(state.get("emitted", [])))


def forget(session: Path) -> None:
    session.unlink(missing_ok=True)


def dropped(session: Path) -> None:
    """Forgets the run of `session` with every file of its own beside it, `session-<key>.*`
    -- its locks, a launcher's log; its trace stays (`session-<stamp>Z-<key>.jsonl`): the
    history of a run outlives it. A file the platform keeps open stays, free (Windows)."""
    key = run_id_of(session)
    for path in session.parent.glob(f"session-{key}.*"):
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass


RENEWED = "renewed"   # the key of a renewal mark: what an upgrade leaves of a run


def frontier_of(state: dict) -> bool:
    """-> whether a saved run waits for the principal's message: the pending step of its top
    frame -- its last step when the frame is exhausted -- is a FINAL. The saved form of what
    the next call reads to tell a message from a production; no document is read."""
    frames = state.get("frames") or []
    steps = (frames[-1].get("instructions") or []) if frames else []
    if not steps:
        return False
    pending = next((index for index, one in enumerate(steps) if not one.get("done")), len(steps) - 1)
    return steps[pending].get("keyword") == language.FINAL


def renewed(session: Path) -> dict | None:
    """-> the renewal MARK an upgrade left at `session` in place of the run's state --
    `{"renewed": {"at", "from", "to"}, "log", "turns", "off", "frontier"[, "conducted_by"]}` -- or None for a
    run, a reservation or no slot. The mark keeps the key held: the next keyed call reopens
    the run under it."""
    try:
        state = json.loads(session.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(state, dict) or not isinstance(state.get(RENEWED), dict):
        return None
    return state


def renew(session: Path, moved_from: dict, moved_to: dict, at: str) -> None:
    """Writes the RENEWAL MARK of the run at `session` in place of its state: the key stays
    held at the same path, and what crosses a version is kept -- the trace's name, the
    exchanges completed, the packages the run switched off, whether it waited for the
    principal's message, its conduction mode. The run's other files (`session-<key>.*`: its locks, a launcher's
    log) go; its trace stays. A mark standing already crosses again: `to` follows the new
    versions, `at` and `from` are kept."""
    state = json.loads(session.read_text(encoding="utf-8"))
    standing = state.get(RENEWED)
    if isinstance(standing, dict):
        mark = {**state, RENEWED: {"at": standing.get("at", at),
                                   "from": {**moved_from, **(standing.get("from") or {})},
                                   "to": {**(standing.get("to") or {}), **moved_to}}}
    else:
        mark = {RENEWED: {"at": at, "from": dict(moved_from), "to": dict(moved_to)},
                "log": state.get("log"), "turns": int(state.get("turns", 0)),
                "off": list(state.get("off", [])), "frontier": frontier_of(state),
                **({MODE: state[MODE]} if state.get(MODE) else {}),
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
    _arrive(session, mark)
