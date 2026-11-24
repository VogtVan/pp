"""Behaviour: the ONE write regime of the shared records.

A shared record (threads, counters, a document several sessions may touch)
is written under a per-file critical section: LOCK, read inside the lock,
modify, ATOMIC replace, release -- two sessions of one member never lose an
update to each other. Readers never take the lock: the atomic replace keeps
every read consistent on its own. The lock is a sibling `.lock` file held
for the shortest span, portable (fcntl on POSIX, msvcrt on Windows).
"""
from __future__ import annotations

import contextlib
import os
import tempfile
from pathlib import Path


@contextlib.contextmanager
def held(path: Path):
    """The critical section of ONE record: exclusive while held, blocking --
    the contention is rare and brief (a read-modify-replace), never spanning
    a serve, a prompt or a subprocess."""
    path.parent.mkdir(parents=True, exist_ok=True)
    gate = path.with_name(path.name + ".lock")
    handle = open(gate, "a+", encoding="utf-8")
    try:
        _acquire(handle)
        try:
            yield
        finally:
            _release(handle)
    finally:
        handle.close()


def _acquire(handle) -> None:
    try:
        import fcntl
        fcntl.flock(handle, fcntl.LOCK_EX)
    except ImportError:              # Windows: the msvcrt region lock stands in
        import msvcrt
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)


def _release(handle) -> None:
    try:
        import fcntl
        fcntl.flock(handle, fcntl.LOCK_UN)
    except ImportError:
        import msvcrt
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)


def replace(path: Path, text: str) -> None:
    """The atomic arrival: a sibling temp file then os.replace -- a reader
    never sees a torn record and never needs the lock."""
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, spot = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}-")
    with os.fdopen(handle, "w", encoding="utf-8") as temp:
        temp.write(text)
    os.replace(spot, path)
