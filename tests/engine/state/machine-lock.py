"""Scenario `machine-lock` -- 7 case(s) (batch le-verrou-de-la-machine, 2026-10-03): the machine's
maintenance lock is a readers/writer lock -- every pp process holds it shared for its life, a verb
that rewrites the machine tries it exclusive and never waits. Every race is FORGED with real
processes (a keyed call held open on its stdin, an opening held in an `exec:` on a FIFO), never by
a delay:
- a keyed call in flight at an agent that borrows the house's machine: `doctor`, `add`, `remove`
  and `-sync` at the house refuse `maintenance-busy`, the machine untouched (inodes and ctimes)
- the same call ended: `doctor` at the house plays
- an opening held in its boot (`-new` blocked in an `exec:`): `upgrade` with a move refuses
  `maintenance-busy`, the pins stand; let go, the opening completes and the upgrade then moves
- a keyed call in flight, then `-reset`: refused `call-busy`, the slot stands; ended, `-reset` forgets
- the exclusive held: `-peek`, the keyless `./pp` and `version` refuse `maintenance-in-progress`
- the exclusive held: `-new` refuses `maintenance-in-progress` and leaves no slot
- two processes at once under the shared lock: a keyed call in flight and `-peek` on its run
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from pathlib import Path

from conductor import install, instance, persistence
from conductor.state import lock
from tests.harness import INSTANCE, bench_key, cli, holding

BOUND = 30.0        # the deadline of a condition awaited -- never a delay that synchronizes

HOLD_DOC = """---
name: HOLD
kind: proc
description: holds the opening in its boot until the bench lets go
attach: boot.ready
exec: pp-hold hold
proc: |
  INFER
---

held
"""
HOLD_CONTRACT = "---\nname: pp-hold\ndescription: the bench's hold on an opening\n---\n\npp-hold\n"
HOLD_SKILL = """import sys
from pathlib import Path
Path({ready!r}).write_text("ready", encoding="utf-8")
with open({fifo!r}, encoding="utf-8") as fifo:
    fifo.read()
"""


def _until(condition, what: str) -> None:
    """Waits for a CONDITION, polled, within BOUND -- the race is the condition's."""
    deadline = time.monotonic() + BOUND
    while not condition():
        if time.monotonic() > deadline:
            raise RuntimeError(f"never reached: {what}")
        time.sleep(0.02)


def _in_flight(engine: Path, meta: Path, key: str, cwd: Path) -> subprocess.Popen:
    """A keyed call held OPEN: `./pp <key> -` waits on its stdin, past its call lock -- a pp
    process alive under the machine, as long as the bench wants it (the run's readings all
    served first: a chunk waiting would answer at once)."""
    proc = subprocess.Popen([sys.executable, str(engine), "--instance", str(meta), key, "-"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, cwd=cwd)
    _until(lambda: proc.poll() is not None or lock.held(lock.call_of(meta, key)),
           f"the call on {key} holding its lock")
    if proc.poll() is not None:
        raise RuntimeError(f"the call on {key} ended at once: {proc.stderr.read()[-200:]}")
    return proc


def _ended(proc: subprocess.Popen) -> None:
    proc.communicate(input="", timeout=BOUND)


def _machine(meta: Path) -> dict[str, tuple[int, int]]:
    """-> every file and directory of the machine (engine, vendor) by inode and ctime: a rewrite
    -- a copy over a file, an exchanged tree -- moves one or the other."""
    found = {}
    for part in ("engine", "vendor"):
        for path in [meta / ".sys" / part, *sorted((meta / ".sys" / part).rglob("*"))]:
            if "__pycache__" in path.parts:
                continue
            stat = path.stat()
            found[str(path.relative_to(meta))] = (stat.st_ino, stat.st_ctime_ns)
    found["instance.yaml"] = (0, hash((meta / ".sys" / "instance.yaml").read_bytes()))
    return found


def _bumped(manifest: Path) -> str:
    """The kit's version at the source copy, raised by one on its last number -> the new version."""
    text = manifest.read_text(encoding="utf-8")
    found = re.search(r"^version: (\S+)$", text, re.M)
    assert found, text[:200]
    head, last = found.group(1).rsplit(".", 1)
    new = f"{head}.{int(last) + 1}"
    manifest.write_text(text.replace(f"version: {found.group(1)}", f"version: {new}", 1), encoding="utf-8")
    return new


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- a house and an agent that borrows its machine -----------------------------------------------
    ws = bench.temp() / "house"
    house = bench.install(ws / INSTANCE, ["monitoring"])
    engine = house / ".sys" / "engine" / "pp.py"
    agent = install.install(engine, ws / "agents" / "a1" / INSTANCE, [], slug="a1", doors=False, borrow=True)
    opened = cli(engine, "--instance", str(agent), "-new", cwd=agent.parent)
    if opened.returncode:
        failures.append(f"-new at the agent failed: {opened.stderr.strip()[-200:]}")
        return len(failures)
    key = bench_key(agent)
    for _ in range(30):                          # the boot's reading, chunk by chunk: a call held
        if "a reading continues" not in opened.stdout:   # open must reach its stdin
            break
        opened = cli(engine, "--instance", str(agent), key, cwd=agent.parent)

    # --- a call in flight at the agent: the machine's verbs refuse, the machine untouched ------------
    before = _machine(house)
    flight = _in_flight(engine, agent, key, agent.parent)
    try:
        verbs = {"doctor": ["doctor"], "add": ["add", "continuity"], "remove": ["remove", "monitoring"],
                 "-sync": ["-sync"]}
        told = {name: cli(engine, *argv, cwd=ws) for name, argv in verbs.items()}
    finally:
        _ended(flight)
    after = _machine(house)
    refused = [name for name, done in told.items()
               if done.returncode == 2 and "maintenance-busy" in done.stderr]
    if refused == list(verbs) and before == after and "continuity" not in instance.pins(house):
        held("a call in flight at a borrower: doctor, add, remove, -sync refuse maintenance-busy",
             f"{len(refused)} refused, the machine's {len(before)} entries untouched")
    else:
        failures.append("  ✗ machine verbs under a call  "
                        + " · ".join(f"{name} rc={done.returncode} {done.stderr.strip()[-90:]!r}"
                                     for name, done in told.items())
                        + f" · untouched={before == after}")

    # --- the call ended: the repair plays -------------------------------------------------------------
    repaired = cli(engine, "doctor", cwd=ws)
    if repaired.returncode == 0:
        held("the call ended, doctor at the house plays", "exit 0")
    else:
        failures.append(f"  ✗ doctor after the call      rc={repaired.returncode} {repaired.stderr.strip()[-200:]!r}")

    # --- an opening held in its boot: the upgrade refuses ----------------------------------------------
    source_engine = bench.source_with("kit-witness")
    source = source_engine.parent.parent
    ws2 = bench.temp() / "opening"
    made = install.install(source_engine, ws2 / INSTANCE, [])
    console = made / ".sys" / "engine" / "pp.py"
    ready, fifo = ws2 / "hold.ready", ws2 / "hold.fifo"
    os.mkfifo(fifo)
    (made / "procs").mkdir(parents=True, exist_ok=True)
    (made / "procs" / "HOLD.md").write_text(HOLD_DOC, encoding="utf-8")
    (made / "skills" / "pp-hold").mkdir(parents=True, exist_ok=True)
    (made / "skills" / "pp-hold" / "SKILL.md").write_text(HOLD_CONTRACT, encoding="utf-8")
    (made / "skills" / "pp-hold" / "pp-hold.py").write_text(
        HOLD_SKILL.format(ready=str(ready), fifo=str(fifo)), encoding="utf-8")
    pinned = instance.pins(made)["kit"]
    target = _bumped(source / "bases" / "kit" / "package.yaml")
    opening = subprocess.Popen([sys.executable, str(console), "-new"], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, cwd=ws2)
    try:
        _until(lambda: ready.exists() or opening.poll() is not None, "the opening held in its boot")
        cut = cli(console, "upgrade", cwd=ws2)
        pins_under = instance.pins(made)["kit"]
    finally:
        with open(fifo, "w", encoding="utf-8") as letting:
            letting.write("go")
        opening.communicate(timeout=BOUND)
    moved = cli(console, "upgrade", cwd=ws2)
    if (opening.returncode == 0 and cut.returncode == 2 and "maintenance-busy" in cut.stderr
            and pins_under == pinned and moved.returncode == 0 and instance.pins(made)["kit"] == target
            and persistence.slots(made)
            and all(persistence.renewed(one) is not None for one in persistence.slots(made))):
        held("an opening held in its boot: the upgrade refuses maintenance-busy; let go, it moves",
             f"kit stays {pinned} under the opening, then {pinned} -> {target}, the opened run renewed")
    else:
        failures.append(f"  ✗ upgrade under an opening    opening rc={opening.returncode} "
                        f"cut rc={cut.returncode} {cut.stderr.strip()[-160:]!r} kit under={pins_under} "
                        f"moved rc={moved.returncode} kit={instance.pins(made)['kit']} "
                        f"slots={[one.name for one in persistence.slots(made)]}")

    # --- -reset under a call in flight ------------------------------------------------------------------
    env = bench.env("machine-lock-reset")
    env.cli("-new")
    key3 = bench_key(env.made)
    flight = _in_flight(env.engine, env.made, key3, env.root)
    try:
        dropped = env.cli("-reset")
        standing = persistence.slot_of(env.made, key3).is_file()
    finally:
        _ended(flight)
    later = env.cli("-reset")
    if (dropped.returncode == 2 and "call-busy" in dropped.stderr and standing
            and later.returncode == 0 and not persistence.slot_of(env.made, key3).exists()):
        held("-reset under a call in flight refuses call-busy, the slot stands; ended, it forgets",
             f"exit 2 then 0 on {key3}")
    else:
        failures.append(f"  ✗ -reset under a call        rc={dropped.returncode} {dropped.stderr.strip()[-160:]!r} "
                        f"standing={standing} later rc={later.returncode}")

    # --- the exclusive held: every process refuses, readers included -------------------------------------
    env.cli("-new")
    key4 = bench_key(env.made)
    with holding(env.made / ".sys" / "state" / "maintenance.lock"):
        readers = {"-peek": env.cli(key4, "-peek"), "./pp": env.cli(), "version": env.cli("version")}
        opening = env.cli("-new")
        slots = len(persistence.slots(env.made))
    stopped = [name for name, done in readers.items()
               if done.returncode == 2 and "maintenance-in-progress" in done.stderr]
    if stopped == list(readers):
        held("under the exclusive: -peek, ./pp and version refuse maintenance-in-progress", "exit 2 · 2 · 2")
    else:
        failures.append("  ✗ readers under the exclusive "
                        + " · ".join(f"{name} rc={done.returncode} {done.stderr.strip()[-80:]!r}"
                                     for name, done in readers.items()))
    if opening.returncode == 2 and "maintenance-in-progress" in opening.stderr and slots == 1:
        held("under the exclusive: -new refuses maintenance-in-progress and reserves no slot", "one slot, as before")
    else:
        failures.append(f"  ✗ -new under the exclusive    rc={opening.returncode} "
                        f"{opening.stderr.strip()[-160:]!r} slots={slots}")

    # --- two processes at once under the shared lock -------------------------------------------------------
    flight = _in_flight(env.engine, env.made, key4, env.root)
    try:
        peeked = env.cli(key4, "-peek")
    finally:
        _ended(flight)
    if peeked.returncode == 0:
        held("a call in flight and -peek on its run play together: the shared lock is shared", "exit 0")
    else:
        failures.append(f"  ✗ two processes shared       rc={peeked.returncode} {peeked.stderr.strip()[-160:]!r}")
    return len(failures)
