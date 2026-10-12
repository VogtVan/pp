"""Scenario `locks` -- 12 case(s) (batch la-concurrence-du-run, 2026-09-30):
- `try_` takes a free lock and gives a lease; a second open file of this process meets
  its own lock: None -- a lock is per open file, not per process
- a lock held by ANOTHER process: `try_` answers None and `held` says True
- `acquire(wait=0.5)` under that holder waits the bound and answers None, in 0.4 to 1.5 s
- the holder releases: `try_` succeeds at once and `held` says False
- a holder KILLED leaves the lock free: the operating system released it with the process
- `call_of` names `session-<key>.call.lock` beside the slot; the module names no launcher's file
  (batch le-reveil-rendu-au-lanceur: `wake_of` and `available` gone)
- two `-new` in one second: two traces, each named by its key; `-stats 1` counts two runs
  and `_stamp_of` reads their hour from the name
Second part (batch le-verrou-de-la-machine, 2026-10-03), the two modes:
- a lock held SHARED by another process: a shared try succeeds beside it, an exclusive try
  answers None and `held` says True
- a lock held EXCLUSIVE by another process: a shared try answers None
- `maintenance_of` names the lock of the MACHINE: an instance that borrows names its machine's
- `maintaining` holds the exclusive and writes its token, handed in `PP_MAINTENANCE`; a process
  launched under it enters `serving` and `maintaining` without taking anything; the token
  of another maintenance waits its turn, and a token whose lock is free takes the lock
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from conductor import install, instance, persistence
from conductor.state import lock, traces
from tests.harness import INSTANCE, PRODUCT_ENGINE, cli

HOLDER = """
import sys
sys.path.insert(0, sys.argv[1])
from pathlib import Path
from conductor.state import lock
lease = lock.try_(Path(sys.argv[2]), shared=sys.argv[3] == "shared")
print("held" if lease else "busy", flush=True)
sys.stdin.readline()
if lease:
    lock.release(lease)
"""


PROBE = """
import sys
sys.path.insert(0, sys.argv[1])
from pathlib import Path
from conductor.state import lock
with lock.serving(Path(sys.argv[2])) as a, lock.maintaining(Path(sys.argv[2]), "probe") as b:
    print("under" if a is None and b is None else "took")
"""


def _holder(path: Path, mode: str = "exclusive") -> subprocess.Popen:
    """Another process that takes the lock, in `mode`, and holds it until a line arrives on its
    stdin."""
    proc = subprocess.Popen([sys.executable, "-c", HOLDER, str(PRODUCT_ENGINE.parent), str(path), mode],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    assert proc.stdout is not None
    proc.stdout.readline()          # "held": the lock is its
    return proc


def _let_go(proc: subprocess.Popen) -> None:
    assert proc.stdin is not None
    proc.stdin.write("\n")
    proc.stdin.flush()
    proc.wait(timeout=10)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    room = Path(tempfile.mkdtemp(prefix="pp-locks-"))
    path = room / "one.lock"

    # --- a free lock, and a second open file of the same process ---------------------------
    lease = lock.try_(path)
    if lease is None:
        failures.append("a free lock was not taken")
    else:
        again = lock.try_(path)
        if again is not None:
            failures.append("a second open file of this process took the lock its first holds")
            lock.release(again)
        else:
            held("a free lock gives a lease; a second open file meets it", f"{path.name}")
        lock.release(lease)

    # --- another process holds it -------------------------------------------------------------
    holder = _holder(path)
    try:
        if lock.try_(path) is not None:
            failures.append("try_ took a lock another process holds")
        elif not lock.held(path):
            failures.append("held() said free under another process's lock")
        else:
            held("under another process's lock: try_ None, held True", "one holder, one try")
        started = time.monotonic()
        got = lock.acquire(path, wait=0.5)
        waited = time.monotonic() - started
        if got is not None:
            failures.append("acquire got a lock another process holds")
            lock.release(got)
        elif not 0.4 <= waited <= 1.5:
            failures.append(f"acquire(wait=0.5) came back after {waited:.2f}s")
        else:
            held("acquire waits its bound then answers None", f"{waited:.2f}s for wait=0.5")
    finally:
        _let_go(holder)
    if lock.held(path):
        failures.append("the holder released and held() still says busy")
    after = lock.try_(path)
    if after is None:
        failures.append("the holder released and try_ still answers None")
    else:
        lock.release(after)
        held("the holder released: held False, try_ succeeds", "released by the holder")

    # --- a holder killed -------------------------------------------------------------------------
    holder = _holder(path)
    holder.kill()
    holder.wait(timeout=10)
    freed = lock.try_(path)
    if freed is None:
        failures.append("a killed holder kept its lock")
    else:
        lock.release(freed)
        held("a killed holder leaves the lock free", "the OS released it with the process")

    # --- the paths ------------------------------------------------------------------------------
    env = bench.env("locks")
    slot = persistence.slot_of(env.made, "abc123")
    call = lock.call_of(env.made, "abc123")
    if call != slot.with_name("session-abc123.call.lock") or hasattr(lock, "wake_of") or hasattr(lock, "available"):
        failures.append(f"lock paths: {call.name}, wake_of {hasattr(lock, 'wake_of')}, available {hasattr(lock, 'available')}")
    else:
        held("call_of names the run's call lock; no launcher's file is the engine's", call.name)
    maintenance = getattr(lock, "maintenance_of", lambda meta: None)(env.made)
    if maintenance != slot.parent / "maintenance.lock":
        failures.append(f"maintenance lock path: {maintenance}")
    else:
        held("maintenance_of names the instance's one maintenance lock beside the runs", maintenance.name)

    # --- two -new in one second: a trace each, named by its key --------------------------------------
    import re
    first = cli(env.engine, "-new", cwd=env.root)
    second = cli(env.engine, "-new", cwd=env.root)
    keys = [m.group(1) if (m := re.search(r"run ([0-9a-f]{6})", one.stdout)) else "?" for one in (first, second)]
    state = env.made / instance.STATE
    named = {one.name for one in state.glob("session-*.jsonl")}
    a = [one for one in named if one.endswith(f"-{keys[0]}.jsonl")]
    b = [one for one in named if one.endswith(f"-{keys[1]}.jsonl")]
    stats = env.cli("-stats", "1")
    if first.returncode or second.returncode:
        failures.append(f"-new failed: {first.stderr.strip()} {second.stderr.strip()}")
    elif len(a) != 1 or len(b) != 1 or keys[0] == keys[1]:
        failures.append(f"traces named by key: {sorted(named)} keys={keys}")
    elif keys[0] not in stats.stdout or keys[1] not in stats.stdout:
        failures.append(f"-stats does not count both runs: {stats.stdout[:200]}")
    elif traces._stamp_of(state / a[0]) == Path(a[0]).stem:
        failures.append(f"_stamp_of could not read the hour of {a[0]}")
    else:
        held("two -new in one second: a trace each, named by its key, both counted",
             f"{a[0]} · {b[0]}")

    # --- the two modes ----------------------------------------------------------------------------
    two = room / "two.lock"
    holder = _holder(two, "shared")
    try:
        beside = lock.try_(two, shared=True)
        alone = lock.try_(two)
        if beside is None or alone is not None or not lock.held(two):
            failures.append(f"under a shared holder: shared {beside is not None}, exclusive {alone is not None}")
        else:
            held("under a shared holder: a shared try succeeds, an exclusive one answers None", "held True")
        for one in (beside, alone):
            if one is not None:
                lock.release(one)
    finally:
        _let_go(holder)
    holder = _holder(two)
    try:
        if lock.try_(two, shared=True) is not None:
            failures.append("a shared try took a lock another process holds exclusive")
        else:
            held("under an exclusive holder: a shared try answers None", "one holder, one try")
    finally:
        _let_go(holder)

    # --- the machine's lock, and the token of a maintenance ---------------------------------------
    house = bench.install(room / "house" / INSTANCE)
    borrower = install.install(house / ".sys" / "engine" / "pp.py", room / "house" / "agents" / "a" / INSTANCE,
                               [], slug="a", doors=False, borrow=True)
    machine_lock = lock.maintenance_of(borrower)
    if machine_lock != house / ".sys" / "state" / "maintenance.lock" or lock.maintenance_of(house) != machine_lock:
        failures.append(f"maintenance_of: {machine_lock}")
    else:
        held("maintenance_of names the machine's lock, for the machine and its borrower", machine_lock.name)
    with lock.maintaining(house, "probe") as lease:
        token = os.environ.get(lock.TOKEN, "")
        written = machine_lock.read_text(encoding="utf-8").strip()
        under = subprocess.run([sys.executable, "-c", PROBE, str(PRODUCT_ENGINE.parent), str(borrower)],
                               capture_output=True, text=True)
        foreign = subprocess.run([sys.executable, "-c", PROBE, str(PRODUCT_ENGINE.parent), str(borrower)],
                                 capture_output=True, text=True, env={**os.environ, lock.TOKEN: "0" * 16})
    stale = subprocess.run([sys.executable, "-c", PROBE, str(PRODUCT_ENGINE.parent), str(borrower)],
                           capture_output=True, text=True, env={**os.environ, lock.TOKEN: token})
    if (lease is not None and token and written == token and under.stdout.strip() == "under"
            and foreign.returncode != 0 and "maintenance-in-progress" in foreign.stderr
            and stale.stdout.strip() == "took" and lock.TOKEN not in os.environ):
        held("a maintenance hands its token: its child plays under it; a foreign token waits its turn, "
             "a stale one takes the lock", "under · maintenance-in-progress · took")
    else:
        failures.append(f"the token: written={written == token} under={under.stdout.strip()!r} "
                        f"{under.stderr.strip()[-120:]!r} foreign={foreign.returncode} "
                        f"{foreign.stderr.strip()[-80:]!r} stale={stale.stdout.strip()!r} {stale.stderr.strip()[-120:]!r}")
    return len(failures)
