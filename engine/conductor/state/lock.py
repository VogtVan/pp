"""state.lock -- the long file locks.

A run has one: the CALL lock, held by the console for one keyed call and waited for
within a bound by a second call. The MACHINE has one, its MAINTENANCE lock, a
readers/writer lock shared by the machine and every instance that borrows it: every pp
process that resolves an instance holds it SHARED for its whole life (`serving`), and a
verb that rewrites the machine tries it EXCLUSIVE without waiting (`maintaining`). A
launcher's own file beside a run is the launcher's affair: the engine names none. All are file locks, released by the operating
system when the process ends, however it ends -- a lock is never stale -- and a process
it launches does not inherit them. Under POSIX they are `flock`; under Windows
`LockFileEx` on one byte at offset 2**31, past any content: a Windows lock is mandatory
on its range, and the marks the lock files carry stay readable. The Windows path is
written and NOT tested. `record.held` keeps the SHORT critical section of one record;
this module holds a lock LONG, tried without waiting or waited for within a bound.
"""
from __future__ import annotations

import contextlib
import os
import secrets
import time
from dataclasses import dataclass
from pathlib import Path

from ..core.errors import Refusal
from . import instance, persistence

INTERVAL = 0.05     # seconds between two tries while a call waits for the lock
MAINTENANCE = "maintenance.lock"   # the machine's readers/writer lock
MARKERS = "maintenance.d"          # one marker per process holding the machine shared: who holds it
TOKEN = "PP_MAINTENANCE"           # the exclusive holder's token, handed to the engines it launches
WINDOWS_OFFSET = 1 << 31           # the byte a Windows lock covers: past any content of the file
LOCKFILE_FAIL_IMMEDIATELY = 0x1
LOCKFILE_EXCLUSIVE_LOCK = 0x2


@dataclass
class Lease:
    """A lock held: the open file whose lock it is. Released by `release`, or by the
    operating system when the process ends."""
    path: Path
    handle: object

    def release(self) -> None:
        release(self)


def call_of(meta: Path, key: str) -> Path:
    """-> the CALL lock of the run `key` at the instance `meta`: `session-<key>.call.lock`
    beside the run's saved state."""
    return persistence.slot_of(meta, key).with_name(f"session-{key}.call.lock")


def maintenance_of(meta: Path) -> Path:
    """-> the MAINTENANCE lock of the machine `meta` plays: `maintenance.lock` beside the
    runs of the instance that carries the machine -- one lock for the machine and every
    instance that borrows it."""
    return instance.machine_of(meta) / persistence.DIRECTORY / MAINTENANCE


def try_(path: Path, shared: bool = False) -> Lease | None:
    """One try, without waiting, EXCLUSIVE or SHARED: the lease when the lock was free (or,
    shared, held shared only), None when another process -- or another open file of this
    one -- holds it against the mode asked."""
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = open(path, "a+", encoding="utf-8")
    try:
        _lock(handle, shared)
    except OSError:
        handle.close()
        return None
    return Lease(path, handle)


def acquire(path: Path, wait: float, shared: bool = False) -> Lease | None:
    """Tries every INTERVAL for `wait` seconds: the lease as soon as the lock is free,
    None once the bound has passed."""
    deadline = time.monotonic() + max(0.0, wait)
    while True:
        lease = try_(path, shared)
        if lease is not None:
            return lease
        left = deadline - time.monotonic()
        if left <= 0:
            return None
        time.sleep(min(INTERVAL, left))


def release(lease: Lease) -> None:
    """Gives the lock back and closes its file."""
    try:
        _unlock(lease.handle)
    finally:
        lease.handle.close()


def held(path: Path) -> bool:
    """-> whether SOMEONE holds the lock now, in either mode -- an exclusive try, released
    at once when it was free. A lock file that does not exist is held by nobody, and the
    test creates none: the file's presence stays the mark of a taker."""
    if not path.exists():
        return False
    lease = try_(path)
    if lease is None:
        return True
    release(lease)
    return False


@contextlib.contextmanager
def serving(meta: Path):
    """The SHARED hold of a pp process on the machine `meta` plays, for the block's time --
    taken at its entry, before it reads anything. The exclusive held by a maintenance
    verb refuses `maintenance-in-progress`, nothing played. Under the exclusive its own
    parent holds (the token of `maintaining`), it takes nothing: it plays under it."""
    path = maintenance_of(meta)
    if _inherited(path):
        yield None
        return
    lease = try_(path, shared=True)
    if lease is None:
        raise Refusal("maintenance-in-progress",
                      f"the machine at {path.parents[2]} is under maintenance -- replay once it is done")
    marker = _mark(path)
    try:
        yield lease
    finally:
        _unmark(marker)
        release(lease)


@contextlib.contextmanager
def maintaining(meta: Path, verb: str):
    """The EXCLUSIVE hold of `verb` on the machine `meta` plays, tried without waiting: a
    pp process active under the machine refuses `maintenance-busy`, nothing read, nothing
    written. Held, the lock file carries a fresh token, handed in `PP_MAINTENANCE` to what
    the verb launches: an engine it delegates to plays under this hold."""
    path = maintenance_of(meta)
    if _inherited(path):
        yield None
        return
    lease = try_(path)
    if lease is None:
        found = holders(path)
        named = f" ({'; '.join(found)})" if found else ""
        raise Refusal("maintenance-busy",
                      f"`{verb}` needs the machine at {path.parents[2]} alone, and a pp process "
                      f"is active under it{named} -- replay once it has ended")
    token = secrets.token_hex(8)
    handle = lease.handle
    handle.seek(0)
    handle.truncate()
    handle.write(token)
    handle.flush()
    before = os.environ.get(TOKEN)
    os.environ[TOKEN] = token
    try:
        yield lease
    finally:
        if before is None:
            os.environ.pop(TOKEN, None)
        else:
            os.environ[TOKEN] = before
        release(lease)


def _mark(path: Path) -> Path | None:
    """Writes the marker of THIS process beside the maintenance lock `path`: its pid as the
    name, its command and the hour it took the machine. -> the marker, None when it could not
    be written (the lock holds without it)."""
    import json
    import sys
    from datetime import datetime, timezone
    marker = path.parent / MARKERS / str(os.getpid())
    try:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(json.dumps({"command": " ".join(["pp", *sys.argv[1:]])[:160],
                                      "at": datetime.now(timezone.utc).isoformat(timespec="seconds")}),
                          encoding="utf-8")
    except OSError:
        return None
    return marker


def _unmark(marker: Path | None) -> None:
    if marker is not None:
        try:
            marker.unlink(missing_ok=True)
        except OSError:
            pass


def holders(path: Path) -> list[str]:
    """-> the processes that hold the machine of the lock `path` shared, said one each from their
    markers; a marker of a process gone is removed -- its lock went with it."""
    import json
    home = path.parent / MARKERS
    found = []
    for marker in sorted(home.iterdir()) if home.is_dir() else []:
        if not marker.name.isdigit():
            continue
        if not _alive(int(marker.name)):
            _unmark(marker)
            continue
        try:
            said = json.loads(marker.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            said = {}
        found.append(f"pid {marker.name}: `{said.get('command', 'pp')}` since {said.get('at', '?')}")
    return found


def _alive(pid: int) -> bool:
    """-> whether the process `pid` still runs; under Windows a marker is taken as alive."""
    if os.name == "nt":
        return True
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _inherited(path: Path) -> bool:
    """-> whether this process plays under the exclusive its PARENT holds: the token in its
    environment is the one the lock file carries, and the lock is held. A token inherited
    by mistake passes only under the maintenance that wrote it."""
    token = os.environ.get(TOKEN, "")
    if not token:
        return False
    try:
        written = path.read_text(encoding="utf-8").strip()
    except OSError:
        return False
    return written == token and held(path)


def _lock(handle, shared: bool) -> None:
    try:
        import fcntl
    except ImportError:
        _windows(handle, shared, unlock=False)
        return
    fcntl.flock(handle, (fcntl.LOCK_SH if shared else fcntl.LOCK_EX) | fcntl.LOCK_NB)


def _unlock(handle) -> None:
    try:
        import fcntl
    except ImportError:
        _windows(handle, False, unlock=True)
        return
    fcntl.flock(handle, fcntl.LOCK_UN)


def _windows(handle, shared: bool, unlock: bool) -> None:
    """`LockFileEx` / `UnlockFileEx` on the byte at WINDOWS_OFFSET -- never waiting; a
    failure raises OSError, as `flock` does. Written, not tested."""
    import ctypes
    import msvcrt
    from ctypes import wintypes

    class Overlapped(ctypes.Structure):
        _fields_ = [("Internal", ctypes.c_size_t), ("InternalHigh", ctypes.c_size_t),
                    ("Offset", wintypes.DWORD), ("OffsetHigh", wintypes.DWORD),
                    ("hEvent", wintypes.HANDLE)]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    where = Overlapped(0, 0, WINDOWS_OFFSET & 0xFFFFFFFF, WINDOWS_OFFSET >> 32, None)
    native = wintypes.HANDLE(msvcrt.get_osfhandle(handle.fileno()))
    if unlock:
        done = kernel.UnlockFileEx(native, 0, 1, 0, ctypes.byref(where))
    else:
        flags = LOCKFILE_FAIL_IMMEDIATELY | (0 if shared else LOCKFILE_EXCLUSIVE_LOCK)
        done = kernel.LockFileEx(native, flags, 0, 1, 0, ctypes.byref(where))
    if not done:
        raise OSError(ctypes.get_last_error(), "LockFileEx refused")
