"""Behaviour: the session log -- the conduction's own trace, one file per run.

Append-only JSONL: the engine records and never reads it back for its own decisions;
whoever FOLLOWS a run -- a human, the house's `pp-agent run`, a team's `pp-team watch` --
reads it here, the one reader (`tail`, `follow`, `step_of`, `said`). The trace belongs to
the INSTANCE -- whatever harness sits above, the chronology survives here, and the files
outlive `new`/`reset`/`sync`: only the run's STATE dies, never its story.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def fresh(directory: Path, key: str) -> str:
    """-> the trace's file name for the run `key` opening NOW, its file CREATED here and
    exclusively: `session-<UTC to the second>Z-<key>.jsonl`, the microseconds added when a
    same-second trace of that key already stands -- two openings never share a trace,
    whatever the second they fall in."""
    directory.mkdir(parents=True, exist_ok=True)
    stamp = f"{datetime.now(timezone.utc):%Y%m%dT%H%M%S}Z"
    while True:
        name = f"session-{stamp}-{key}.jsonl"
        try:
            os.close(os.open(directory / name, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644))
        except FileExistsError:
            stamp = f"{datetime.now(timezone.utc):%Y%m%dT%H%M%S.%f}Z"
            continue
        return name


def record(path: Path, kind: str, **data) -> None:
    """Appends ONE event: `at` (UTC), `kind`, and whatever the caller says -- a trace,
    never a state: the engine's decisions never read it back."""
    line = json.dumps({"at": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                       "kind": kind, **data}, ensure_ascii=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


# --- reading a trace as it grows ------------------------------------------------------------

class Tail:
    """A JSONL file READ as it grows, never written: `fresh()` renders the lines added since
    the last reading, parsed; a line still being written waits for its end; a file not there
    yet is read once it is. `from_end` starts past what the file holds now."""

    def __init__(self, path: Path | None, from_end: bool = False):
        self.path = path
        self.offset, self.partial = 0, b""
        if from_end and path is not None and path.is_file():
            self.offset = path.stat().st_size

    def fresh(self) -> list[dict]:
        if self.path is None or not self.path.is_file():
            return []
        with self.path.open("rb") as handle:
            handle.seek(self.offset)
            chunk = handle.read()
            self.offset = handle.tell()
        lines = (self.partial + chunk).split(b"\n")
        self.partial = lines.pop()
        found = []
        for line in lines:
            try:
                found.append(json.loads(line.decode("utf-8")))
            except ValueError:
                continue
        return found


class Follow(Tail):
    """A RUN's trace followed: the file is found through the run's slot once the engine has
    written it -- a run not opened yet is found at a later reading."""

    def __init__(self, meta: Path, key: str, from_end: bool = False):
        self.meta, self.key, self.from_end = meta, key, from_end
        super().__init__(self._find(), from_end)

    def _find(self) -> Path | None:
        from . import persistence
        slot = persistence.slot_of(self.meta, self.key)
        try:
            name = persistence.trace_of(slot) if slot.is_file() else None
        except Exception:                            # a slot being written reads next time
            name = None
        return slot.parent / name if name else None

    def fresh(self) -> list[dict]:
        if self.path is None:
            self.path = self._find()
            if self.path is not None and self.from_end and self.path.is_file():
                self.offset = self.path.stat().st_size
        return super().fresh()


def tail(path: Path, from_end: bool = False) -> Tail:
    """-> a reader of the JSONL file at `path` as it grows."""
    return Tail(path, from_end)


def follow(meta: Path, key: str, from_end: bool = False) -> Follow:
    """-> a reader of the run `key`'s trace at the instance `meta`, as it grows."""
    return Follow(meta, key, from_end)


def step_of(event: dict) -> tuple[str, str, dict] | None:
    """-> (what a step of a run's trace says to whoever follows it, its kind, its fields for
    a JSON line), or None for an event that marks no step (a cut, a chunk, a served weight)."""
    kind = event.get("kind")
    if kind == "new":
        return "opened", kind, {}
    if kind == "reopened":
        return "reopened", kind, {}
    if kind == "block":
        stack, waits = str(event.get("stack", "")), bool(event.get("wait"))
        return (f"{stack} · parked" if waits else stack), kind, {"stack": stack, "wait": waits}
    if kind == "answer":
        return "answer", kind, {}
    if kind == "refusal":
        return f"refused {event.get('code', '')}".strip(), kind, {"code": event.get("code")}
    if kind == "repair":
        return f"repair {event.get('document', '')}".strip(), kind, {"document": event.get("document")}
    if kind == "repair-in-place":
        return "repair in place", kind, {}
    if kind == "blocked":
        codes = [str(one.get("code", "")) for one in event.get("gaps") or []]
        return f"gap declared {' '.join(codes)}".strip(), kind, {"codes": codes}
    if kind == "gesture":
        return f"skill {event.get('name', '')}".strip(), kind, {"name": event.get("name")}
    if kind == "compacted":
        return "compacted", kind, {}
    return None


def said(key: str, line: str, kind: str, fields: dict, as_json: bool, who: str | None = None) -> None:
    """Writes one line of progress on stderr: `[HH:MM:SS] <key> · <line>` -- the agent before
    the key when one is named --, or its JSON form `{at, run, event, …}` with `agent`."""
    if as_json:
        text = json.dumps({"at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                           **({"agent": who} if who else {}), "run": key, "event": kind, **fields},
                          ensure_ascii=False)
    else:
        text = f"[{datetime.now().strftime('%H:%M:%S')}] {who + ' · ' if who else ''}{key} · {line}"
    sys.stderr.write(text + "\n")
    sys.stderr.flush()
