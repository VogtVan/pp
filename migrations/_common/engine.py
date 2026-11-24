"""_common.engine -- the house's own engine, borrowed by the migration: imported from the house
(`<house>/.pp/.sys/engine`), its maintenance lock, its store, its console.

The engine is imported AFRESH at each `mounted`: the check reads the lock with the engine of the
starting version, the gestures write with the engine the upgrade put in its place."""
from __future__ import annotations

import importlib
import os
import secrets
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from .house import ENGINE, INSTANCE
from .refusal import Refused

def mounted(root: Path):
    """-> the `conductor` package of the house's engine, imported afresh: whatever an earlier mount
    imported is forgotten first."""
    path = str(Path(root) / INSTANCE / ENGINE)
    for name in [one for one in sys.modules if one == "conductor" or one.startswith("conductor.")]:
        del sys.modules[name]
    while path in sys.path:
        sys.path.remove(path)
    sys.path.insert(0, path)
    importlib.invalidate_caches()
    return importlib.import_module("conductor")


def store_of(engine, meta: Path):
    """-> the store of the instance `meta`, by the engine mounted."""
    return engine.store.of(meta)


def busy(root: Path) -> bool:
    """-> whether a pp process holds the house's machine now: its maintenance lock tried exclusive
    and released at once, by the house's own engine -- nothing created when the lock is absent."""
    lock = importlib.import_module("conductor.state.lock")
    return lock.held(lock.maintenance_of(Path(root) / INSTANCE))


@dataclass
class Hold:
    """The house's maintenance lock held EXCLUSIVE by the migration: the lease the house's engine
    gave, and that engine's lock module -- the one that releases it."""
    lease: object
    lock: object


def take(root: Path) -> Hold:
    """Takes the house's maintenance lock EXCLUSIVE, without waiting and WITHOUT its token: nothing
    is written in the lock's file (created empty when no pp ever ran in the house -- a file of the
    machine every pp creates). A pp process living in the house refuses `house-busy`. From now on
    every pp process launched in the house refuses `maintenance-in-progress`."""
    lock = importlib.import_module("conductor.state.lock")
    lease = lock.try_(lock.maintenance_of(Path(root) / INSTANCE))
    if lease is None:
        raise Refused("house-busy", f"a pp process lives in the house at {root} -- end it, then replay")
    return Hold(lease, lock)


def arm(hold: Hold) -> None:
    """Writes the hold's TOKEN, once the backup stands: in the lock's file and in the environment,
    by the lock module's own constants, as its `maintaining` does -- `./pp upgrade` and `./pp doctor`,
    launched by the frame, then play under this hold, and no other pp process plays at all."""
    token = secrets.token_hex(8)
    handle = hold.lease.handle
    handle.seek(0)
    handle.truncate()
    handle.write(token)
    handle.flush()
    os.environ[hold.lock.TOKEN] = token


def give(hold: Hold) -> None:
    """Gives the house back: its token out of the environment, its lock released."""
    os.environ.pop(hold.lock.TOKEN, None)
    hold.lock.release(hold.lease)


def console(root: Path, *args: str) -> subprocess.CompletedProcess:
    """The house's console, played by its engine under this interpreter (it carries what the engine
    requires): `./pp <args>` at the house's root."""
    engine = Path(root) / INSTANCE / ENGINE / "pp.py"
    return subprocess.run([sys.executable, str(engine), *args], cwd=root, capture_output=True,
                          text=True, stdin=subprocess.DEVNULL, env=dict(os.environ))
