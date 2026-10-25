"""Scenario `entry` -- the paths a document enters by:
- the entries are ONE table (`conductor.execution.entry.ENTRIES`), each path
  naming what it applies; a socket document's own law of production is proven once at the
  TURN's written PROVE, its successor by its own PROVE, a lawless one owes nothing, a slot saved with the old
  mark `socket: true` reads back as the socket path; the floor serves its `payloads:` and its
  overlays' rows; the re-serve replays the `serve:` sections its SERVEs played, a mount all
  its rows
What a document does AT its entry, `exec:`, is the pattern `automation/exec`.
"""
from __future__ import annotations

import json

from conductor import compiling, instance, persistence, render

CONTRACT = "---\nname: {name}\ndescription: {said}\n---\n\n{name}\n"

# --- the entry paths ------------------------------------------------------------------------

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
GIVER_SKILL = "#!/usr/bin/env python3\nimport sys\nprint('the witness skill says', *sys.argv[1:])\n"

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
  PROVE
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

def _pin(made, name: str, manifest: str, files: dict[str, str]) -> None:
    """A witness package pinned by hand at `made`: its manifest and `files` under its root."""
    root = made / ".sys" / "vendor" / f"{name}@0.0.1"
    root.mkdir(parents=True, exist_ok=True)
    (root / "package.yaml").write_text(manifest, encoding="utf-8")
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    pins = instance.read(made)
    pins["packages"][name] = "0.0.1"
    instance.write(made, pins)






def _drive(env, first, cap: int = 12) -> list:
    """Advance to the frontier with bare submits -> every block met, the proofs piped n/a
    for the codes the checkpoint names."""
    seen = [first]
    while seen[-1] is not None and not seen[-1].wait and len(seen) < cap:
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
            if one.instruction is not None and one.instruction.keyword == "PROVE" and not one.wait]


def _socket_env(bench, name: str, documents: dict[str, str]):
    """-> an environment whose `documents` (relpath -> text) are written and cataloged."""
    env = bench.env(name)
    for relpath, text in documents.items():
        env.write(relpath, text)
    compiling.build_tools(env.made)
    return env


def _key(env) -> str:
    return persistence.run_id_of(env.session())










def entry_paths(bench) -> None:
    """The ENTRIES table, the socket's deferred proof, the floor's services, the re-serve."""
    held, failures = bench.held, bench.failures

    # --- the entries are ONE table, read at the engine's module ----------------------------
    from conductor.execution import entry
    table = dict(entry.ENTRIES)
    wanted = {"floor", "call", "door", "socket", "cadence", "successor", "lap", "mount",
              "reserve", "reserve-mount"}
    if (wanted <= set(table) and "defer" in table["socket"]
            and not any("proof" in steps for steps in table.values())):
        held("the entries are one table", f"{len(table)} paths, each naming what it applies -- "
             "the socket defers its laws to the next written PROVE, no path proves by itself")
    else:
        failures.append(f"  ✗ the entry table             {sorted(table)}")

    # --- a socket document's own law is proven at the frontier -----------------------------
    socket = _socket_env(bench, "entry-socket", {"procs/TRIAGE.md": TRIAGE})
    opener = socket.conductor("t")
    seen = _drive(socket, opener.start(opener.boot("TURN.md")))
    proofs = _proofs(seen)
    final = render(seen[-1]) if seen else ""
    if proofs == [("TG1",)] and "▶ AWAIT" in final:
        held("a socket document's law is proven", "attach: + TG1 -> ONE checkpoint at the "
             "TURN's written PROVE naming TG1, no proof at the socket's exit")
    else:
        failures.append(f"  ✗ socket law unproven         proofs={proofs} {final[-120:]!r}")

    # --- a slot saved with the old mark reads back as the socket path -------------------
    socket.conductor("t").forget()
    opener = socket.conductor("t")
    block = opener.start(opener.boot("TURN.md"))
    slot = socket.session()
    state = json.loads(slot.read_text(encoding="utf-8"))
    for frame in state["frames"]:
        for one in frame["instructions"]:
            if one.get("argument") == "TRIAGE.md":
                one.pop("site", None)
                one["socket"] = True
    slot.write_text(json.dumps(state), encoding="utf-8")
    seen = _drive(socket, socket.conductor("t").forward(""))
    if block is not None and _proofs(seen) == [("TG1",)]:
        held("an old slot reads back", "`socket: true` read as the socket path -- the debt "
             "deferred to the frontier, no refusal")
    else:
        failures.append(f"  ✗ old slot                    proofs={_proofs(seen)}")

    # --- the debt rides the socket's successor ------------------------------------------
    succ = _socket_env(bench, "entry-successor", {"procs/LEAVER.md": LEAVER, "procs/AFTER.md": AFTER})
    opener = succ.conductor("t")
    proofs = _proofs(_drive(succ, opener.start(opener.boot("TURN.md"))))
    if proofs == [("AF1",)]:
        held("the successor of a socket proves by its own PROVE", "LEAVER -> AFTER: AF1 proven "
             "once, at the PROVE AFTER writes; the TURN's PROVE then owes nothing")
    else:
        failures.append(f"  ✗ successor law               proofs={proofs}")

    # --- a socket document without a law changes nothing -------------------------------
    quiet = _socket_env(bench, "entry-quiet", {"procs/QUIET.md": QUIET})
    opener = quiet.conductor("t")
    seen = _drive(quiet, opener.start(opener.boot("TURN.md")))
    if not _proofs(seen) and seen and "no law of production in force" in "".join(render(one) for one in seen):
        held("a lawless socket document owes nothing", "QUIET plays, the TURN's PROVE resolves on its line, "
             "the AWAIT owes no proof")
    else:
        failures.append(f"  ✗ quiet socket                proofs={_proofs(seen)}")

    # --- the floor serves its payloads and its overlays' rows at the opening ------------
    floor = bench.env("entry-floor")
    _pin(floor.made, "witness", WITNESS, {
        "procs/GIVER.md": GIVER,
        "skills/pp-witness/SKILL.md": CONTRACT.format(name="pp-witness", said="a witness script"),
        "skills/pp-witness/pp-witness.py": GIVER_SKILL,
    })
    floor.write("EXTRA.md", "---\nname: EXTRA\nkind: doc\n---\n\nthe extra reading\n")
    path = floor.write("procs/FLOOR.md", FLOOR)
    floor.write("FLOOR.md", FLOOR_OVERLAY)
    compiling.build_tools(floor.made)
    first = floor.conductor("t").start(path)
    subjects = [subject for subject, _ in first.payloads] if first is not None else []
    if "witness" in subjects and "EXTRA.md" in subjects:
        held("the floor serves its payloads and overlay rows", f"{subjects}")
    else:
        failures.append(f"  ✗ floor entry                 payloads={subjects}")

    # --- the re-serve replays the sections already played, a mount all its rows ---------
    floor.write("FIRST.md", "---\nname: FIRST\nkind: doc\n---\n\nthe first section\n")
    floor.write("SECOND.md", "---\nname: SECOND\nkind: doc\n---\n\nthe second section\n")
    floor.write("HOSTED.md", HOSTED)
    paced = floor.write("procs/PACED.md", PACED)
    compiling.build_tools(floor.made)
    opener = floor.conductor("t")
    opener.forget()
    opener.start(paced)                          # SERVE 1 played, the WORK stands
    key = _key(floor)
    again = {subject for subject, _ in floor.conductor(key).compacted().payloads}
    if "FIRST.md" in again and "SECOND.md" not in again:
        held("the re-serve keeps the SERVE pace", "the section its SERVE played comes back, "
             "the one still to play does not")
    else:
        failures.append(f"  ✗ re-serve pace               payloads={sorted(again)}")
    floor.conductor(key).mount([{"doc": "HOSTED.md"}])
    mounted = {subject for subject, _ in floor.conductor(key).compacted().payloads}
    if {"FIRST.md", "SECOND.md"} <= mounted:
        held("a mount replays all its rows", "HOSTED's two sections come back whole")
    else:
        failures.append(f"  ✗ mount rows                  payloads={sorted(mounted)}")


def scenario(bench) -> int:
    entry_paths(bench)
    return 0
