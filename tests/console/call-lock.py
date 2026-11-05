"""Scenario `call-lock` -- a run's call lock and the machine's maintenance lock, as the console meets them:
- the run's call lock held by another process (`call_lock_wait: 1`): `./pp <key>` waits the
  bound then refuses `call-busy`, exit 2, and the slot is byte-identical before and after
- under the same holder, `./pp <key> -peek` and `./pp -stats <key>` answer at once: a reader
  takes no lock
- the holder gone, the same call plays
- `PP_CALL` naming this instance and this run: `call-reentrant`, exit 2, nothing played;
  naming another instance or another key: the call plays
- eight `-mount` at once on one run (the default wait): the eight documents stand at the
  slot and at `-peek`, the slot is valid JSON, no temporary is left behind
- the console drops an inherited `PP_CALL` of another run and names its own: a `-new`
  under a foreign `PP_CALL` opens
- the machine's maintenance lock held exclusive: a keyed call, `-new`, `-reset`, `-peek` and
  `-stats` refuse `maintenance-in-progress` -- every pp process holds the machine shared, readers included; released, the keyed call plays
"""
from __future__ import annotations

import json
import re
import time

from conductor import instance, persistence
from conductor.state import lock
from tests.harness import bench_key, cli, holding, race

DOC = "---\nname: {name}\nkind: doc\ndescription: a throwaway reading\n---\n# {name}\n\nOne line of {name}.\n"


def _with_wait(env, seconds: int) -> None:
    """The operator's edit: `call_lock_wait` posed at the throwaway's SETTINGS."""
    text = env.read("SETTINGS.md")
    text = re.sub(r"^call_lock_wait: \d+$", f"call_lock_wait: {seconds}", text, count=1, flags=re.M)
    env.write("SETTINGS.md", text)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- one run, a short bound ------------------------------------------------------------------
    short = bench.env("call-lock-short")
    _with_wait(short, 1)
    opened = short.cli("-new")
    if opened.returncode:
        failures.append(f"-new failed: {opened.stderr.strip()[:200]}")
        return len(failures)
    key = bench_key(short.made)
    slot = persistence.slot_of(short.made, key)
    with holding(lock.call_of(short.made, key)):
        before = slot.read_bytes()
        started = time.monotonic()
        busy = short.cli(key)
        waited = time.monotonic() - started
        after = slot.read_bytes()
        if busy.returncode != 2 or "call-busy" not in busy.stderr:
            failures.append(f"a call under a held lock played: rc {busy.returncode} -- {busy.stderr.strip()[:120]}")
        elif before != after:
            failures.append("the refused call changed the slot")
        elif not 0.9 <= waited <= 6.0:
            failures.append(f"call-busy came after {waited:.2f}s for a bound of 1s")
        else:
            held("a held call lock: the call waits its bound, refuses call-busy, touches nothing",
                 f"{waited:.2f}s · exit 2")
        started = time.monotonic()
        peek = short.cli(key, "-peek")
        stats = short.cli("-stats", key)
        readers = time.monotonic() - started
        if peek.returncode or stats.returncode:
            failures.append(f"a reader waited or failed under the lock: {peek.stderr[:80]} {stats.stderr[:80]}")
        elif readers > 1.5:
            failures.append(f"the readers took {readers:.2f}s under a lock of 1s: they waited")
        else:
            held("-peek and -stats answer under the lock: readers take none", f"{readers:.2f}s for both")
    played = short.cli(key)
    if played.returncode:
        failures.append(f"the lock released, the call still fails: {played.stderr.strip()[:120]}")
    else:
        held("the holder gone, the same call plays", "exit 0")

    # --- the nested call ---------------------------------------------------------------------------
    own = f"{short.made}:{key}"
    nested = cli(short.engine, key, "-peek", cwd=short.root, env={"PP_CALL": own})
    # -peek takes no lock and judges no reentrance either: the guard is the writers'
    reentrant = cli(short.engine, key, cwd=short.root, env={"PP_CALL": own})
    foreign_key = cli(short.engine, key, cwd=short.root, env={"PP_CALL": f"{short.made}:ffffff"})
    foreign_home = cli(short.engine, key, cwd=short.root, env={"PP_CALL": f"/elsewhere/.pp:{key}"})
    if reentrant.returncode != 2 or "call-reentrant" not in reentrant.stderr:
        failures.append(f"a nested call on its own run played: rc {reentrant.returncode} -- {reentrant.stderr.strip()[:120]}")
    elif nested.returncode or foreign_key.returncode or foreign_home.returncode:
        failures.append("a call under a foreign PP_CALL, or a peek, was refused: "
                        f"{nested.stderr[:60]} {foreign_key.stderr[:60]} {foreign_home.stderr[:60]}")
    else:
        held("PP_CALL of this run refuses call-reentrant; another key or home plays", "exit 2 · 0 · 0")

    # --- eight mounts at once ------------------------------------------------------------------------
    wide = bench.env("call-lock-wide")
    wide.cli("-new")
    key = bench_key(wide.made)
    slot = persistence.slot_of(wide.made, key)
    names = [f"D{index}" for index in range(1, 9)]
    for name in names:
        wide.write(f"procs/{name}.md", DOC.format(name=name))
    results = race(wide.engine, [[key, "-mount", f"procs/{name}.md"] for name in names], cwd=wide.root)
    mounted = [str(one.get("doc", "")) for one in persistence.mounted_of(slot)]
    state = wide.made / instance.STATE
    leftovers = [one.name for one in state.iterdir() if one.suffix == ".tmp" or one.name.startswith(".session-")]
    try:
        json.loads(slot.read_text(encoding="utf-8"))
        valid = True
    except ValueError:
        valid = False
    codes = [one.returncode for one in results]
    if any(codes):
        failures.append(f"a mount among eight failed: {codes} -- "
                        + " | ".join(one.stderr.strip()[:60] for one in results if one.returncode))
    elif sorted(mounted) != sorted(f"procs/{name}.md" for name in names):
        failures.append(f"eight mounts at once, the slot holds {len(mounted)}: {mounted}")
    elif not valid or leftovers:
        failures.append(f"slot valid {valid}, leftovers {leftovers}")
    else:
        peeked = wide.cli(key, "-peek")      # the standing block re-renders under the eight mounts
        if peeked.returncode:
            failures.append(f"-peek fails under the eight mounts: {peeked.stderr.strip()[:120]}")
        else:
            held("eight mounts at once: all eight stand at the slot, no temporary left, -peek renders",
                 f"{len(mounted)} mounted · slot valid · {len(leftovers)} leftovers")

    # --- an inherited PP_CALL of another run is dropped ----------------------------------------------
    fresh = cli(wide.engine, "-new", cwd=wide.root, env={"PP_CALL": own})
    if fresh.returncode:
        failures.append(f"-new under a foreign PP_CALL refused: {fresh.stderr.strip()[:120]}")
    else:
        held("a -new under another run's PP_CALL opens: the inherited value is dropped", "exit 0")

    # --- the maintenance lock held exclusive: every process refuses, readers included -------------------
    with holding(lock.maintenance_of(wide.made)):
        tried = {"keyed": wide.cli(key), "-new": wide.cli("-new"), "-reset": wide.cli("-reset"),
                 "-peek": wide.cli(key, "-peek"), "-stats": wide.cli("-stats", key)}
    stopped = [name for name, done in tried.items()
               if done.returncode == 2 and "maintenance-in-progress" in done.stderr]
    if stopped == list(tried) and persistence.slot_of(wide.made, key).is_file():
        held("under the maintenance lock: a keyed call, -new, -reset, -peek and -stats refuse "
             "maintenance-in-progress", "exit 2 × 5, the slot intact")
    else:
        failures.append("maintenance lock: " + " · ".join(f"{name} rc {done.returncode} {done.stderr.strip()[:60]}"
                                                         for name, done in tried.items()))
    freed = wide.cli(key)
    if freed.returncode:
        failures.append(f"the maintenance lock released, the keyed call still fails: {freed.stderr.strip()[:120]}")
    else:
        held("the maintenance lock released, the keyed call plays", "exit 0")
    return len(failures)
