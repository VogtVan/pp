"""The `wake` domain, layer `store`: where the wake-ups meet the disk, the clock and the environment.

A definition belongs here when it reaches the system for a wake-up: it reads the house's record of the launches from
where it last stopped and keeps its cursor, tests whether a run's wake lock is held, reads how old a quota is, or finds
the working directory of a run. A file written whole is written by `placed`, a tool of the whole skill in
`house/store.py`. It never writes the journal: an act does. What it reads, it gives back; a judgement that needs no
system belongs to a rule, and the launches nobody holds, read then judged, belong to `wake/acts.py`.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from house.rules import agent_meta, journal_of, record_of
from house.store import launch_of, locks
from documents.model import MESSAGES
from wake.model import TICK_CURSOR


def aged(launch: dict) -> float:
    """-> the launch's age in seconds: the journal's UTC `at` against the real UTC clock
    (`PP_NOW` plays no part here: a timeout compares two wall-clock stamps)."""
    try:
        born = datetime.fromisoformat(str(launch.at))
    except ValueError:
        return 0.0
    return (datetime.now(timezone.utc) - born).total_seconds()


def messages_cursor(root: Path, name: str, state: dict) -> dict[str, dict]:
    """-> the tags `agent start` wrote at the house's `messages.jsonl` for launches the journal does not
    know the launch of yet, each with its `run` and `pid`: the record is read INCREMENTALLY, from the byte
    the cursor `tick.cursor` beside the journal reached (whole lines alone), under the tick's lock; the
    tags of intents launched or ended leave the cursor. What a late `wake-launched` and the bounds'
    count of the launches read, in place of the record whole."""
    cursor_path = journal_of(root, name).parent / TICK_CURSOR
    try:
        cursor = json.loads(cursor_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        cursor = {}
    offset, tags = int(cursor.get("offset") or 0), dict(cursor.get("tags") or {})
    record = record_of(root, MESSAGES)
    if record.is_file():
        with record.open("rb") as handle:
            handle.seek(offset)
            raw = handle.read()
        whole = raw[:raw.rfind(b"\n") + 1] if b"\n" in raw else b""
        for line in whole.decode("utf-8", "replace").splitlines():
            try:
                one = json.loads(line)
            except ValueError:
                continue
            if isinstance(one, dict) and one.get("tag"):
                tags[str(one["tag"])] = {"run": one.get("run"), "pid": one.get("pid")}
        offset += len(whole)
    tags = {tag: one for tag, one in tags.items() if tag in state.wake.intents and tag not in state.wake.launched
            and tag not in state.wake.ended or tag not in state.wake.intents}
    cursor_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = cursor_path.with_name(f".{cursor_path.name}.{os.getpid()}")
    temporary.write_text(json.dumps({"offset": offset, "tags": tags}), encoding="utf-8")
    os.replace(temporary, cursor_path)
    return tags


def material_of(root: Path, work: str) -> Path:
    """-> the repository `work:` of SEASON.md names: absolute, `~` expanded, a relative path read
    from the house's root."""
    path = Path(work).expanduser()
    return path if path.is_absolute() else root.parent / path


def held_run(root: Path, conductor, path: str, run: str) -> bool:
    """-> whether the run's wake lock is held at the agent `path`: a wake-up of it plays, or has
    kept its answer and is still releasing -- the reap's own test. Resumed now, `agent start
    --run` would refuse `run-busy`; the end of that wake-up ticks once the lock is free."""
    return locks(conductor).held(launch_of(conductor, agent_meta(root, path), run))
