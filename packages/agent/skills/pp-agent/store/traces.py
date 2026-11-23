"""The run read at the agent: its slot and its trace, through the engine's faces."""
from __future__ import annotations

import json
from pathlib import Path

from model.exchange import Response
from model.run import Traced
from store.refusal import refuse


def faced_slots(conductor, meta: Path) -> list[Path]:
    """-> the runs the faces show of an agent: all its slots."""
    return conductor.persistence.slots(meta)


def counted_since(conductor, meta: Path, key: str,
                  answered: list[Response]) -> tuple[list[Response], int | None]:
    """-> (the responses of the run whose flow fills its context now, the index of the first of them
    when a compaction was declared, else None): after `-compacted` the slot's `boot` mark holds the
    count of exchanges the engine had, so the flow counts from the response after the conducted one of
    that rank -- a bare exchange the engine never saw counts on the side of the compaction it follows."""
    boot = conductor.persistence.boot_of(conductor.persistence.slot_of(meta, key))
    if boot <= 0:
        return answered, None
    seen = 0
    for at, one in enumerate(answered):
        if one.conducted is not False:
            seen += 1
            if seen == boot:
                return answered[at + 1:], int(one.index or at + 1) + 1
    return answered, None


def run_known(conductor, meta: Path, key: str) -> bool:
    """Whether a run of the agent wears that key."""
    persistence = conductor.persistence
    return key in {persistence.run_id_of(one) for one in persistence.slots(meta)}


def trace_events(conductor, meta: Path, key: str) -> list[Traced]:
    """-> the events the run's trace holds, in order -- [] when no trace stands."""
    persistence = conductor.persistence
    slot = persistence.slot_of(meta, key)
    log = persistence.trace_of(slot)
    if not log or not (slot.parent / log).is_file():
        return []
    found = []
    for line in (slot.parent / log).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            found.append(Traced.of(json.loads(line)))
        except ValueError:
            continue
    return found


def captured(conductor, meta: Path, key: str) -> list[str]:
    """-> the productions the run's trace holds as pp took them, in order: the text `given` of each `answer` a
    print call left -- said on the channel of a production said to the principal, naming its document --, as the
    trace holds it. A print pp refused and a debt it lifted leave none."""
    import importlib
    said = importlib.import_module(f"{conductor.__name__}.core.language").TERMINAL
    return [one.given for one in trace_events(conductor, meta, key)
            if one.kind == "answer" and one.channel == said and one.document and one.given is not None]


def captures(conductor, meta: Path, key: str):
    """-> the reader of the captures of ONE exchange, made when it begins: each call renders the productions the
    run's trace holds that no call before rendered, the oldest first -- `most` of them at most, all without it --,
    none of what the trace held before the exchange."""
    seen = len(captured(conductor, meta, key))

    def fresh(most: int | None = None) -> list[str]:
        nonlocal seen
        found = captured(conductor, meta, key)
        new = found[seen:] if most is None else found[seen:seen + most]
        seen += len(new)
        return new
    return fresh


def standing_of(conductor, meta: Path, key: str) -> str:
    """-> `parked` | `standing`, read at the run's SLOT by the engine's face (`persistence.awaits`):
    parked when the stack waits for the principal's message (the passage over: AWAIT), standing
    when a step pends. The trace is never read for it."""
    persistence = conductor.persistence
    return "parked" if persistence.awaits(persistence.slot_of(meta, key)) == persistence.MESSAGE else "standing"


def spaces_of(conductor, meta: Path, key: str) -> dict | None:
    """-> the SPACES the run's last block said (`spaces {open, openable}` of the trace's `block` event, beta.36):
    the spaces open, from the outermost to the root, and the names the output offers that `-open` would let open,
    each with its segment when several offer it; None without a block, or under an engine that said none."""
    blocks = [one for one in trace_events(conductor, meta, key) if one.kind == "block"]
    return blocks[-1].spaces if blocks else None


def stack_of(conductor, meta: Path, key: str) -> str:
    """-> the stack of the last block the run's trace rendered (`BOOT ▸ MEMBER ▸ TURN{2/4}`), the
    label a face shows beside the state; "" without a block. Display alone: nothing is decided on it."""
    blocks = [one for one in trace_events(conductor, meta, key) if one.kind == "block"]
    return blocks[-1].stack if blocks else ""


def tracing(conductor):
    """-> the engine's `state.log` module: the one reader of a run's trace (`follow`,
    `step_of`, `said`), shared with whoever else follows a run."""
    import importlib
    return importlib.import_module(f"{conductor.__name__}.state.log")


def documents_kept(conductor, meta: Path, key: str | None, documents: str | None) -> tuple[str, bool]:
    """-> (the root of documents the run was opened with, as its slot keeps it -- '' for none --, whether
    `documents` names another): without a run, or without a root named, nothing is read and none is another."""
    if key is None or documents is None:
        return "", False
    held = conductor.persistence.documents_of(conductor.persistence.slot_of(meta, key))
    return held, Path(documents) != Path(held or ".")


def refusal_traced(conductor, meta: Path, key: str) -> str | None:
    """-> the detail of the last refusal the run's trace holds, None when it holds none."""
    refused = [one for one in trace_events(conductor, meta, key) if one.kind == "refusal"]
    return refused[-1].detail if refused else None


def engine_purge_of(conductor):
    """-> the engine's `state.purge` module, `purge-unsupported` before beta.66."""
    try:
        import importlib
        return importlib.import_module(f"{conductor.__name__}.state.purge")
    except ImportError:
        refuse("purge-unsupported -- the house's engine predates `./pp -purge` (beta.66): `./pp upgrade` first.")
