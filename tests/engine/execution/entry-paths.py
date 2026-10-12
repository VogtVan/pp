"""Scenario `entry-paths` -- 8 case(s) (plan core, batch l-entree-unique-d-un-document):
- the entries are ONE table: every path a document enters by names what it applies, read at
  the engine's own module (`conductor.execution.entry.ENTRIES`)
- a document a SOCKET calls owes the proof of its own laws of production: `attach:` + a law
  -> the turn's checkpoint names it, one proof for the turn, no step more
- the debt survives the socket's successor: a `next:` leaving a socket document carries the
  same deferral
- a written CALL still proves its own laws at its exit, a mounted document at the frontier
- the floor serves its `payloads:` and the rows its overlays add, at the opening, as a CALL does
- the re-serve replays the `serve:` sections a frame's SERVEs already played -- not the
  others; a mount replays all its rows
- a socket document WITHOUT a law of production leaves the turn as it was: no proof
- a slot saved with the old mark (`socket: true`) reads back as the socket path
"""
from __future__ import annotations

import json

from conductor import compiling, instance, persistence, render

WITNESS = """name: witness
version: 0.0.1
description: a package providing a payload to the entry paths
requires: [kit]
"""
GIVER = """---
name: GIVER
kind: doc
description: the provider of the witness token
provides: witness
with: pp-witness hello
---

GIVER gives
"""
SKILL = "#!/usr/bin/env python3\nimport sys\nprint('the witness skill says', *sys.argv[1:])\n"

TRIAGE = """---
name: TRIAGE
kind: proc
description: a socket document with a law of its own
attach: turn.begin
output: line
constraints.production: |
  TG1  the line opens on one class.
proc: |
  INFER
---

Classify the message.
"""
QUIET = """---
name: QUIET
kind: proc
description: a socket document without a law of production
attach: turn.begin
output: line
proc: |
  INFER
---

Say one line.
"""
LEAVER = """---
name: LEAVER
kind: proc
description: a socket document that leaves to a successor
attach: turn.begin
output: line
next: |
  AFTER.md
proc: |
  INFER
---

Leave.
"""
AFTER = """---
name: AFTER
kind: proc
description: the successor of a socket document, with a law of its own
output: line
constraints.production: |
  AF1  the successor's line lands.
proc: |
  INFER
---

After.
"""
FLOOR = """---
name: FLOOR
kind: proc
description: a floor that declares a payload
payloads: witness
proc: |
  WORK
---

the floor
"""
FLOOR_OVERLAY = """---
name: FLOOR
serve: |
  reference: EXTRA.md
---
"""
PACED = """---
name: PACED
kind: proc
description: a floor with two serve sections, one SERVE played
serve: |
  reference: FIRST.md

  reference: SECOND.md
proc: |
  SERVE
  WORK
  SERVE
  WORK
---

paced
"""
HOSTED = """---
name: HOSTED
kind: doc
serve: |
  reference: FIRST.md

  reference: SECOND.md
---

hosted
"""


def _pin_witness(made) -> None:
    root = made / ".sys" / "vendor" / "witness@0.0.1"
    (root / "procs").mkdir(parents=True, exist_ok=True)
    (root / "package.yaml").write_text(WITNESS, encoding="utf-8")
    (root / "procs" / "GIVER.md").write_text(GIVER, encoding="utf-8")
    home = root / "skills" / "pp-witness"
    home.mkdir(parents=True, exist_ok=True)
    (home / "SKILL.md").write_text("---\nname: pp-witness\ndescription: a witness script\n---\n\nw\n",
                                   encoding="utf-8")
    (home / "pp-witness.py").write_text(SKILL, encoding="utf-8")
    pins = instance.read(made)
    pins["packages"]["witness"] = "0.0.1"
    instance.write(made, pins)


def _drive(env, first, cap: int = 12) -> list:
    """Advance to the frontier with bare submits -> every block met, the proofs piped n/a
    for the codes the checkpoint names."""
    seen = [first]
    while seen[-1] is not None and "▶ FINAL" not in render(seen[-1]) and len(seen) < cap:
        last = seen[-1]
        if last.instruction is not None and last.instruction.keyword == "PROVE":
            answer = json.dumps([{"code": code, "evidence": "bench", "verdict": "n/a"}
                                 for code in last.judged])
        else:
            answer = ""                       # a draft closes on the bare call
        seen.append(env.conductor("t").submit(answer))
    return [one for one in seen if one is not None]


def _proofs(seen) -> list:
    return [tuple(one.judged) for one in seen
            if one.instruction is not None and one.instruction.keyword == "PROVE"]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- the entries are ONE table, read at the engine's module ----------------------------
    try:
        from conductor.execution import entry
        table = dict(entry.ENTRIES)
    except Exception as missing:              # before the batch: no such module
        table = {}
        failures.append(f"  ✗ the entry table             {type(missing).__name__}: {missing}")
    wanted = {"floor", "call", "door", "socket", "cadence", "successor", "lap", "mount",
              "reserve", "reserve-mount"}
    if table and wanted <= set(table) and "defer" in table["socket"] and "proof" in table["call"]:
        held("the entries are one table", f"{len(table)} paths, each naming what it applies -- "
             "the socket defers its proof, the call proves at its exit")
    elif table:
        failures.append(f"  ✗ the entry table             {sorted(table)}")

    # --- a socket document's own law is proven at the frontier -----------------------------
    env = bench.env("entry-socket")
    env.write("procs/TRIAGE.md", TRIAGE)
    compiling.build_tools(env.made)
    opener = env.conductor("t")
    seen = _drive(env, opener.start(opener.boot("TURN.md")))
    proofs = _proofs(seen)
    final = render(seen[-1]) if seen else ""
    if proofs == [("TG1",)] and "▶ FINAL" in final:
        held("a socket document's law is proven", "attach: + TG1 -> ONE checkpoint at the "
             "frontier naming TG1, no proof at the socket's exit")
    else:
        failures.append(f"  ✗ socket law unproven         proofs={proofs} {final[-120:]!r}")

    # --- the debt rides the socket's successor ------------------------------------------
    succ = bench.env("entry-successor")
    succ.write("procs/LEAVER.md", LEAVER)
    succ.write("procs/AFTER.md", AFTER)
    compiling.build_tools(succ.made)
    opener = succ.conductor("t")
    seen = _drive(succ, opener.start(opener.boot("TURN.md")))
    proofs = _proofs(seen)
    if proofs == [("AF1",)]:
        held("the successor of a socket defers too", "LEAVER -> AFTER: AF1 proven at the "
             "frontier, once, not at AFTER's exit")
    else:
        failures.append(f"  ✗ successor law               proofs={proofs}")

    # --- a socket document without a law changes nothing -------------------------------
    quiet = bench.env("entry-quiet")
    quiet.write("procs/QUIET.md", QUIET)
    compiling.build_tools(quiet.made)
    opener = quiet.conductor("t")
    seen = _drive(quiet, opener.start(opener.boot("TURN.md")))
    if not _proofs(seen) and seen and "no law of production in force" in render(seen[-1]):
        held("a lawless socket document owes nothing", "QUIET plays, the FINAL owes no proof")
    else:
        failures.append(f"  ✗ quiet socket                proofs={_proofs(seen)}")

    # --- the floor serves its payloads and its overlays' rows at the opening ------------
    floor = bench.env("entry-floor")
    _pin_witness(floor.made)
    floor.write("EXTRA.md", "---\nname: EXTRA\nkind: doc\n---\n\nthe extra reading\n")
    path = floor.write("procs/FLOOR.md", FLOOR)
    floor.write("FLOOR.md", FLOOR_OVERLAY)
    compiling.build_tools(floor.made)
    opener = floor.conductor("t")
    first = opener.start(path)
    subjects = [subject for subject, _ in first.payloads] if first is not None else []
    if "witness" in subjects and "EXTRA.md" in subjects:
        held("the floor serves its payloads and overlay rows", f"{subjects}")
    else:
        failures.append(f"  ✗ floor entry                 payloads={subjects}")

    # --- the re-serve replays the sections already played, a mount all its rows ---------
    paced = bench.env("entry-reserve")
    paced.write("FIRST.md", "---\nname: FIRST\nkind: doc\n---\n\nthe first section\n")
    paced.write("SECOND.md", "---\nname: SECOND\nkind: doc\n---\n\nthe second section\n")
    paced.write("HOSTED.md", HOSTED)
    floor_path = paced.write("procs/PACED.md", PACED)
    compiling.build_tools(paced.made)
    opener = paced.conductor("t")
    opener.start(floor_path)                     # SERVE 1 played, the WORK stands
    key = persistence.run_id_of(paced.session())
    again = {subject for subject, _ in paced.conductor(key).compacted().payloads}
    if "FIRST.md" in again and "SECOND.md" not in again:
        held("the re-serve keeps the SERVE pace", "the section its SERVE played comes back, "
             "the one still to play does not")
    else:
        failures.append(f"  ✗ re-serve pace               payloads={sorted(again)}")
    paced.conductor(key).mount([{"doc": "HOSTED.md"}])
    mounted = {subject for subject, _ in paced.conductor(key).compacted().payloads}
    if {"FIRST.md", "SECOND.md"} <= mounted:
        held("a mount replays all its rows", "HOSTED's two sections come back whole")
    else:
        failures.append(f"  ✗ mount rows                  payloads={sorted(mounted)}")

    # --- a slot saved with the old mark reads back as the socket path -------------------
    old = bench.env("entry-old-slot")
    old.write("procs/TRIAGE.md", TRIAGE)
    compiling.build_tools(old.made)
    opener = old.conductor("t")
    block = opener.start(opener.boot("TURN.md"))
    slot = old.session()
    state = json.loads(slot.read_text(encoding="utf-8"))
    for frame in state["frames"]:
        for one in frame["instructions"]:
            if one.get("argument") == "TRIAGE.md":
                one.pop("site", None)
                one["socket"] = True
    slot.write_text(json.dumps(state), encoding="utf-8")
    seen = _drive(old, old.conductor("t").forward(""))
    if block is not None and _proofs(seen) == [("TG1",)]:
        held("an old slot reads back", "`socket: true` read as the socket path -- the debt "
             "deferred to the frontier, no refusal")
    else:
        failures.append(f"  ✗ old slot                    proofs={_proofs(seen)}")
    return 0
