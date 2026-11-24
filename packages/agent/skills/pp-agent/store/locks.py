"""The locks of the house: the wake lock of a run and the mark its launcher writes in it, the birth lock,
the lock of a repository."""
from __future__ import annotations

import json
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from model.refusal import WorkFailure
from model.run import Mark
from model.text import first_line
from store.clock import now
from store.houses import bootstrap
from store.settings import call_wait


def locks(conductor):
    """-> the engine's `state.lock` module: the wake lock a wake-up holds, the machine's
    maintenance lock a detached wake-up holds shared."""
    import importlib
    return importlib.import_module(f"{conductor.__name__}.state.lock")


def marked(lease, message: str, launched: int) -> None:
    """Writes the wake-up's MARK into the wake lock file it holds: the hour it started, the
    head of its message -- what a neighbour's line reads while the lock is held -- and how
    many responses the run had before this launch: a wake-up over that added none is DEAD."""
    handle = lease.handle
    handle.seek(0)
    handle.truncate()
    handle.write(json.dumps({"at": now(), "message": first_line(message),
                             "responses": launched}, ensure_ascii=False) + "\n")
    handle.flush()


def standing_mark(lease, message: str) -> None:
    """Writes the MARK of a wake-up that launched nothing on the exchange its message opened: the hour, the head of
    its message, no `responses` -- no launch was awaited, so the run reads standing, never dead."""
    handle = lease.handle
    handle.seek(0)
    handle.truncate()
    handle.write(json.dumps({"at": now(), "message": first_line(message)}, ensure_ascii=False) + "\n")
    handle.flush()


def held_mark(lease, message: str) -> None:
    """Writes the MARK of a conversation that takes the wake lock of a run it resumes, before any
    message: the hour of the take, the head of the run's last message -- what a neighbour's line
    reads meanwhile --, `held: "chat"`; an interruption the mark before carried is kept, for the
    next message to say it; no `responses` -- no wake-up's outcome is awaited before a launch."""
    handle = lease.handle
    handle.seek(0)
    try:
        before = json.loads(handle.read())
    except ValueError:
        before = {}
    mark = {"at": now(), "message": first_line(message), "held": "chat"}
    if isinstance(before, dict) and before.get("interrupted") is True:
        mark["interrupted"] = True
    handle.seek(0)
    handle.truncate()
    handle.write(json.dumps(mark, ensure_ascii=False) + "\n")
    handle.flush()


def interrupted_mark(lease) -> None:
    """Adds `interrupted: true` to the MARK of the wake-up that holds `lease` -- its hour, its
    message and its responses kept: the next wake-up of the run reads it before it writes its own
    mark, which clears it."""
    handle = lease.handle
    handle.seek(0)
    try:
        mark = json.loads(handle.read())
    except ValueError:
        mark = {}
    handle.seek(0)
    handle.truncate()
    handle.write(json.dumps({**(mark if isinstance(mark, dict) else {}), "interrupted": True},
                            ensure_ascii=False) + "\n")
    handle.flush()


def mark_of(lock, meta: Path, key: str) -> Mark:
    """-> the mark the last launcher of `key` wrote into its wake lock file, the mark of nothing
    when there is none or it does not read."""
    try:
        return Mark.of(json.loads(launch_of(meta, key).read_text(encoding="utf-8")))
    except (OSError, ValueError):
        return Mark()


def launch_of(meta: Path, key: str) -> Path:
    """-> the LAUNCHER's file of the run `key`, `session-<key>.wake.lock` beside the run's
    slot: the lock a wake-up holds for its whole life and the mark it writes. The path is
    this package's published contract (README) -- the engine names none."""
    core, _ = bootstrap()
    return core(__file__).persistence.slot_of(meta, key).with_name(f"session-{key}.wake.lock")


def wake_log_of(lock, meta: Path, key: str) -> Path:
    """-> the wake LOG of the run `key`, `session-<key>.wake.log` beside its wake lock: the
    launcher's file, where a detached wake-up writes what `run` says on stderr."""
    return launch_of(meta, key).with_name(f"session-{key}.wake.log")


def under_way(lock, persistence, meta: Path, key: str | None = None) -> list[tuple[str, str, str]]:
    """-> (key, since HH:MM, the head of the message) of every run of the agent whose wake
    lock is held -- a wake-up under way, its slot reserved or opened -- but `key`: the local
    hour of its mark and the first line of its message; a mark the file does not carry reads
    as `?`."""
    found = []
    state = meta / persistence.DIRECTORY
    for path in sorted(state.glob("session-*.wake.lock")) if state.is_dir() else []:
        other = path.name.removeprefix("session-").split(".", 1)[0]
        if other == key or not lock.held(path):
            continue
        since, head = "?", "?"
        try:
            mark = json.loads(path.read_text(encoding="utf-8"))
            since = datetime.fromisoformat(str(mark.get("at"))).astimezone().strftime("%H:%M")
            head = first_line(str(mark.get("message", ""))) or "?"
        except (OSError, ValueError, AttributeError, TypeError):
            pass
        found.append((other, since, head))
    return found


def repo_lock_of(root: Path, conductor, repo: Path) -> Path:
    """-> the house's lock file for ONE target repository: `.sys/state/work-<digest>.lock`,
    the digest of the repository's absolute path -- the repository itself is never written
    but by its refs."""
    import hashlib
    digest = hashlib.sha1(str(repo).encode("utf-8")).hexdigest()[:12]
    return root / conductor.persistence.DIRECTORY / f"work-{digest}.lock"


@contextmanager
def under_repo_lock(conductor, root: Path, repo: Path):
    """The clone and the push of one repository, one wake-up at a time: the lock acquired
    within `call_lock_wait`, `work-busy` beyond."""
    lock = locks(conductor)
    path = repo_lock_of(root, conductor, repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    lease = lock.acquire(path, wait=call_wait(conductor, root))
    if lease is None:
        raise WorkFailure(f"work-busy -- another wake-up clones or pushes {repo} and has not finished within "
                          "call_lock_wait: replay once it has.")
    try:
        yield lease
    finally:
        lock.release(lease)


def birth_lock_of(root: Path, conductor, path: str) -> Path:
    """-> the house's BIRTH lock for one agent's path: `.sys/state/born-<digest>.lock`, the
    digest of the path -- the lock a caller's start takes too, so that one path is born once."""
    import hashlib
    digest = hashlib.sha1(path.encode("utf-8")).hexdigest()[:12]
    return root / conductor.persistence.DIRECTORY / f"born-{digest}.lock"
