"""Behaviour: the session log -- the conduction's own trace, one file per run.

Append-only JSONL, written and never read back: the engine records, a human (or an
outside tool) reads. The trace belongs to the INSTANCE -- whatever harness sits above,
the chronology survives here, and the files outlive `new`/`reset`/`sync`: only the
run's STATE dies, never its story.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def fresh(directory: Path) -> str:
    """-> a log file name for a run opening NOW -- stamped to the second, microseconds
    only when a same-second run already claimed the name."""
    now = datetime.now(timezone.utc)
    name = f"session-{now:%Y%m%dT%H%M%SZ}.jsonl"
    if (directory / name).exists():
        name = f"session-{now:%Y%m%dT%H%M%S.%fZ}.jsonl"
    return name


def record(path: Path, kind: str, **data) -> None:
    """Appends ONE event: `at` (UTC), `kind`, and whatever the caller says -- a trace,
    never a state: nothing in the engine ever reads it back."""
    line = json.dumps({"at": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                       "kind": kind, **data}, ensure_ascii=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
