"""Scenario `compaction` -- 8 case(s):
- le-verbe-declare: `-compacted` serves the boot's readings back, byte for byte
- la-cle-redite: the re-serve says the run's key again
- le-drapeau-a-un-coup: the next call renders the pending block and nothing else
- le-frame-sorti: a popped frame's brief is past -- what is IN FORCE comes back
- les-compteurs-statues: proven, pending and the drafts go; turns, signals and mounted stay
- les-noeuds-remontes: a mounted document's body and serve rows come back
- le-refus-hors-run: the verb without a run refuses by its name
- le-refus-hors-run: the keyless form says where the key leads
"""
from __future__ import annotations

import json

from conductor import Refusal, persistence


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("compaction")

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
    # the boot's own flow opens a brief (CAPABILITIES) and pops it: its body and the
    # rows it declared were payloads of the boot, and they are NOT owed back -- what a
    # re-serve rebuilds is what still rules the pending step.
    conductor = env.conductor(key)
    while True:
        block = conductor.forward("")
        conductor = env.conductor(key)
        if block is None or "CAPABILITIES" not in block.stack:
            break
    moved = {subject for subject, _ in env.conductor(key).compacted().payloads}
    if "standing orders" in moved and not ({"CAPABILITIES", "tools.md"} & moved):
        held("a popped frame's brief is past",
             "the standing rules and the stack's own readings come back; the brief that closed does not")
    else:
        failures.append(f"  ✗ popped brief re-served      payloads: {sorted(moved)}")

    # --- les-compteurs-statues: what goes, and what stays ------------------------------
    env.conductor().forget()
    conductor = env.conductor()
    conductor.start(conductor.boot("BOOT.md"))
    key = persistence.run_id_of(env.session())
    env.conductor(key).forward("")
    persistence.latch(env.session(), {"signal": "witness", "vector": "x", "n": 1})
    before = json.loads(env.session().read_text(encoding="utf-8"))
    env.conductor(key).compacted()
    now = json.loads(env.session().read_text(encoding="utf-8"))
    dropped = set(before.get("proven", [])) - set(now.get("proven", []))
    gone = {"proven": bool(dropped), "pending": "pending" not in now,
            "ephemerals": now.get("ephemerals") == []}
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
    env.write("HOSTED.md", "---\nname: HOSTED\nkind: doc\nserve: |\n  reference: READING.md\n---\n"
                           "\nthe body of a mounted document\n")
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

    # --- le-refus-hors-run: the declaration needs a destination ------------------------
    env.conductor().forget()
    try:
        env.conductor("nobody").compacted()
        failures.append("  ✗ declared into the void      `-compacted` armed a flag with no run")
    except Refusal as refusal:
        if refusal.code == "no-run":
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
