"""state.purge -- what the engine keeps of a run, removed for good: its slot (or the renewal mark
that stands in its place), every `session-<key>.*` beside it, and every trace of its key. A run is
named by its key, or found by its age: the last write of its trace, of its slot when it has no
trace. A trace that names no run -- one written before a trace carried its key -- goes by age
alone. Nothing here takes a lock: the console holds each run's call lock around the removal,
then removes the lock's file once released.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from . import persistence, traces


def _state(meta: Path) -> Path:
    return meta / persistence.DIRECTORY


def files_of(meta: Path, key: str) -> list[Path]:
    """-> every file the engine keeps of the run `key`: `session-<key>.*` (its slot or mark, its
    call lock, whatever a launcher put beside them) and every trace that run wrote."""
    state = _state(meta)
    if not state.is_dir():
        return []
    own = set(state.glob(f"session-{key}.*"))
    own |= {state / name for name, run in traces.keys_of(state).items() if run == key}
    return sorted(path for path in own if path.is_file())


def known(meta: Path) -> list[str]:
    """-> the key of every run the state directory keeps something of: a slot or a mark, or a
    trace that names its run."""
    state = _state(meta)
    if not state.is_dir():
        return []
    found = {persistence.run_id_of(slot) for slot in persistence.slots(meta)}
    found |= {run for run in traces.keys_of(state).values() if run}
    return sorted(found)


def keyless(meta: Path) -> list[Path]:
    """-> the traces that name no run."""
    state = _state(meta)
    if not state.is_dir():
        return []
    keyed = traces.keys_of(state)
    return sorted(path for path in state.glob("session-*.jsonl") if not keyed.get(path.name))


def last_write(files: list[Path]) -> datetime | None:
    """-> when a run was last written: its newest trace, or its slot when it has no trace."""
    written = [one for one in files if one.suffix == ".jsonl"] or \
              [one for one in files if one.suffix == ".json"]
    if not written:
        return None
    return datetime.fromtimestamp(max(one.stat().st_mtime for one in written), timezone.utc)


def planned(meta: Path, keys: list[str], before: datetime | None) -> list[dict]:
    """-> what a purge removes, one entry per run -- `{"key", "files", "bytes"}`, `key` empty for
    a trace that names no run --: the runs named, or every run and keyless trace last written
    before `before`. Reads only."""
    entries = []
    if before is None:
        for key in keys:
            entries.append({"key": key, "files": files_of(meta, key)})
    else:
        for key in known(meta):
            files = files_of(meta, key)
            written = last_write(files)
            if written is not None and written < before:
                entries.append({"key": key, "files": files})
        for path in keyless(meta):
            if datetime.fromtimestamp(path.stat().st_mtime, timezone.utc) < before:
                entries.append({"key": "", "files": [path]})
    for entry in entries:
        entry["bytes"] = sum(one.stat().st_size for one in entry["files"])
    return entries


def removed(meta: Path, entries: list[dict], held: set[Path]) -> list[Path]:
    """Removes the files of each entry -- and, for a run, every `session-<key>.*` that stands
    now -- but the files of the locks `held`: the purge holds them open, and an open file is never
    removed (Windows refuses it). A file another process holds open -- the wake lock of the
    launcher that asked the purge -- is left in place. A file already gone is no error. -> the
    files left."""
    state = _state(meta)
    left = []
    for entry in entries:
        paths = set(entry["files"])
        if entry["key"]:
            paths |= set(state.glob(f"session-{entry['key']}.*"))
        left += _unlinked(sorted(paths - held))
    return left


def released(paths: list[Path]) -> list[Path]:
    """Removes the files of the locks a purge held, once released. -> those a call took in
    between and holds open (refused under Windows): left in place."""
    return _unlinked(paths)


def _unlinked(paths: list[Path]) -> list[Path]:
    """Removes each file. -> those another process holds open, which Windows refuses to remove."""
    left = []
    for path in paths:
        try:
            path.unlink(missing_ok=True)
        except PermissionError:
            left.append(path)
    return left
