"""Scenario `compaction` -- 9 case(s):
- le-verbe-declare: `-compacted` serves the boot's readings back, byte for byte
- la-cle-redite: the re-serve says the run's key again
- le-drapeau-a-un-coup: the next call renders the pending block and nothing else
- le-frame-sorti: a popped frame's brief is past -- what is IN FORCE comes back
- les-compteurs-statues: proven and pending go; turns, signals and mounted stay; no `ephemerals` key at the slot
- les-noeuds-remontes: a mounted document's body and serve rows come back
- la-re-serve-refusee: a re-serve that refuses leaves the declaration at the slot -- the flag and
  the boot mark, nothing else of the slot moved -- and the next call re-serves; its refusal says so by its
  field `armed`, which the console reads: exit 2, the constant `messages.ARMED` on its second line; the next
  call that carries the declaration and refuses in its turn is armed as well, the slot unmoved
- le-refus-hors-run: the verb without a run refuses by its name
- le-refus-hors-run: the keyless form says where the key leads
"""
from __future__ import annotations

import json

from conductor import Refusal, persistence
from conductor.core import messages
from tests.harness import na_proof, stepped

HOSTED = "---\nname: HOSTED\nkind: doc\nserve: |\n  reference: %s\n---\n\nthe body of a mounted document\n"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("compaction")
    env.write_member()        # the boot opens on the member's brief: a frame to pop, a step before the frontier

    # --- le-verbe-declare: at the boot, every reading is still in force ----------------
    conductor = env.conductor()
    booted = conductor.start(conductor.boot("BOOT.md"))
    served = {subject: text for subject, text in booted.payloads}
    key = persistence.run_id_of(env.session())

    declared = env.conductor(key).compacted()
    again = {subject: text for subject, text in declared.payloads}
    missing = [subject for subject, text in served.items() if again.get(subject) != text]
    if served and not missing:
        held("the boot's readings come back",
             f"{len(served)} payload(s) re-served byte for byte: {', '.join(sorted(served))}")
    else:
        failures.append(f"  ✗ readings lost               served {sorted(served)}, missing {missing}")

    # --- la-cle-redite: the key may have gone with the context -------------------------
    if declared.run_key == key:
        held("the re-serve says the key again", f"`{key}` rides the block, as a fresh run's first output")
    else:
        failures.append(f"  ✗ key silent                  run_key={declared.run_key!r}, expected {key!r}")

    # --- le-drapeau-a-un-coup: one call re-serves, the next does not -------------------
    state = json.loads(env.session().read_text(encoding="utf-8"))
    after = env.conductor(key).forward("")
    quiet = {subject for subject, _ in after.payloads}
    if "compacted" not in state and not (quiet & set(served)):
        held("the declaration is consumed once",
             "the re-serve cleared the flag; the next call carries none of the boot's readings")
    else:
        failures.append(f"  ✗ flag survived               compacted={state.get('compacted')}, again={sorted(quiet)}")

    # --- le-frame-sorti: the stack is what governs, and only it ------------------------
    # the boot's own flow opens a brief (the member attached at boot.initialize) and pops it:
    # its body was a payload of the boot, and it is NOT owed back -- what a re-serve
    # rebuilds is what still rules the pending step.
    conductor = env.conductor(key)
    while True:
        block = stepped(lambda: env.conductor(key), by="forward")
        conductor = env.conductor(key)
        if block is None or "MEMBER" not in block.stack:
            break
    moved = {subject for subject, _ in env.conductor(key).compacted().payloads}
    if "standing orders" in moved and "MEMBER" not in moved:
        held("a popped frame's brief is past",
             "the standing rules and the stack's own readings come back; the brief that closed does not")
    else:
        failures.append(f"  ✗ popped brief re-served      payloads: {sorted(moved)}")

    # --- les-compteurs-statues: what goes, and what stays ------------------------------
    env.conductor().forget()
    conductor = env.conductor()
    conductor.start(conductor.boot("BOOT.md"))
    key = persistence.run_id_of(env.session())
    stepped(lambda: env.conductor(key), by="forward")
    persistence.latch(env.session(), {"signal": "witness", "vector": "x", "n": 1})
    before = json.loads(env.session().read_text(encoding="utf-8"))
    env.conductor(key).compacted()
    now = json.loads(env.session().read_text(encoding="utf-8"))
    dropped = set(before.get("proven", [])) - set(now.get("proven", []))
    gone = {"proven": bool(dropped), "pending": "pending" not in now,
            "ephemerals": "ephemerals" not in now and "ephemerals" not in before}
    kept = {"turns": now.get("turns") == before.get("turns"),
            "signals": now.get("signals") == before.get("signals"),
            "mounted": now.get("mounted") == before.get("mounted"),
            "frames": len(now.get("frames", [])) == len(before.get("frames", []))}
    if all(gone.values()) and all(kept.values()):
        held("the counters are ruled one by one",
             f"cleared: {', '.join(sorted(gone))} ({len(dropped)} proof(s) dropped of "
             f"{len(before.get('proven', []))}) | kept: {', '.join(sorted(kept))}")
    else:
        failures.append(f"  ✗ counter wrong               cleared {gone}, kept {kept}")

    # --- les-noeuds-remontes: the mount's matter is served again -----------------------
    env.write("READING.md", "---\nname: READING\nkind: doc\n---\n\nthe reading a row names\n")
    env.write("HOSTED.md", HOSTED % "READING.md")
    env.conductor().forget()
    conductor = env.conductor()
    conductor.start(conductor.boot("BOOT.md"))
    key = persistence.run_id_of(env.session())
    env.conductor(key).mount([{"doc": "HOSTED.md", "body": True}])
    carried = {subject for subject, _ in env.conductor(key).compacted().payloads}
    if {"HOSTED", "READING.md"} <= carried:
        held("a mounted node comes back whole",
             "its body and its serve rows ride the re-serve -- the mount rendered them once")
    else:
        failures.append(f"  ✗ mount not re-served         payloads: {sorted(carried)}")

    # --- la-re-serve-refusee: the declaration stands, the next call carries the duty ----
    # the second exchange, so the boot mark is told from the opening's; the mounted document's
    # row turns unreadable after the mount: the re-serve refuses on it, the declaration is past
    block = env.conductor(key).forward("")
    for _ in range(12):
        if block is None or block.wait:
            break
        block = stepped(lambda: env.conductor(key), na_proof(block) if block.judged else "", by="forward")
    env.conductor(key).forward("the next message")
    env.conductor(key).mount([{"doc": "HOSTED.md", "body": True}])
    env.write("HOSTED.md", HOSTED % "READING.md[..]")
    found = json.loads(env.session().read_text(encoding="utf-8"))
    try:
        env.conductor(key).compacted()
        refused, said = "", None
    except Refusal as refusal:
        refused, said = refusal.code, refusal.armed
    armed = json.loads(env.session().read_text(encoding="utf-8"))
    declared = {**found, "compacted": True, "boot": found.get("turns")}   # the slot as found, the declaration on it
    console = env.cli(key, "-compacted")                  # the console on the same refusal
    unmoved = json.loads(env.session().read_text(encoding="utf-8")) == armed
    try:
        env.conductor(key).forward("")                    # the next call while the row is still unreadable
        carried, owing = "", None
    except Refusal as refusal:
        carried, owing = refusal.code, refusal.armed
    still = json.loads(env.session().read_text(encoding="utf-8")) == armed
    env.write("HOSTED.md", HOSTED % "READING.md")
    owed = env.conductor(key).forward("")
    back = {subject for subject, _ in owed.payloads} if owed is not None else set()
    consumed = json.loads(env.session().read_text(encoding="utf-8"))
    if (refused == "serve-range-malformed" and said is True and armed.get("compacted") is True
            and armed.get("turns", 0) >= 1 and armed.get("boot") == armed.get("turns") and armed == declared
            and console.returncode == 2 and messages.ARMED in console.stderr and unmoved
            and carried == refused and owing is True and still
            and {"standing orders", "HOSTED", "READING.md"} <= back and "compacted" not in consumed):
        held("a refused re-serve leaves the declaration armed",
             f"`{refused}` on the mounted row, its refusal armed: the flag and the boot mark ({armed.get('boot')}) "
             "stand at the slot, nothing else of it moved; the console exits 2 and says the armed line; the next "
             "call refuses armed too while the row stays unreadable, the slot unmoved; the row mended, the call "
             "after re-serves the boot's readings and the mount, and clears the flag")
    else:
        failures.append(f"  ✗ declaration lost            refused={refused!r} armed={said} "
                        f"compacted={armed.get('compacted')} boot={armed.get('boot')} turns={armed.get('turns')} "
                        f"alone={armed == declared} moved={sorted(k for k in set(armed) | set(declared) if armed.get(k) != declared.get(k))} "
                        f"console={console.returncode} line={messages.ARMED in console.stderr} unmoved={unmoved} "
                        f"next={carried!r} armed={owing} still={still} "
                        f"back={sorted(back)} cleared={'compacted' not in consumed}")

    # --- le-refus-hors-run: the declaration needs a destination ------------------------
    env.conductor().forget()
    try:
        env.conductor("nobody").compacted()
        failures.append("  ✗ declared into the void      `-compacted` armed a flag with no run")
    except Refusal as refusal:
        if refusal.code == "no-run" and refusal.armed is False:
            held("the verb refuses out of a run", f"`{refusal.code}` -- nothing armed, nothing played")
        else:
            failures.append(f"  ✗ wrong refusal               {refusal.code}")
    keyless = env.cli("-compacted")
    if keyless.returncode == 2 and "no-run" in keyless.stderr:
        held("the keyless form says where the key leads",
             "`./pp -compacted` refuses `no-run` and names `./pp <key> -compacted`")
    else:
        failures.append(f"  ✗ keyless accepted            exit {keyless.returncode} -- "
                        f"{keyless.stderr.strip()[:80]}")
    return 0
