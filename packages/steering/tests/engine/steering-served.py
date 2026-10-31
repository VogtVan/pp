"""Scenario `steering-served` -- what steering serves at the end of the turn:
- the kit alone closes an exchange on the work: no block at the empty socket, no NEXT
- kit + steering closes every exchange on NEXT alone: no THREADS block, no
  `steering-threads` reading in any block
- a second contributor of the same socket stands beside NEXT in one exchange; which one
  first is nobody's business here -- the socket's order is the engine's
- a producer package's standing line reaches the turn at its own turn.end block, beside
  NEXT, in the requires topology of the homes; the acquit ends it
- the LEDGER is served again after a declared compaction
- the STEERING space, offered at TURN: opened, it plays its welcome once -- the archives swept, the
  board served to an INFER in the form `steering-board` the package declares -- then its WORK
  under ST5 and ST6; the next message plays the WORK alone; closed, it gives back the root it
  was opened from
- NEXT takes its clients' semantics by composition: an overlay's law binds, its prose
  lands after the base's
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from conductor import compiling, events, instance, reading, render
from conductor.core import language
from tests.harness import na_proof, support

S = support(__file__, "steering")

MANIFEST = """name: witness
version: 0.0.1
description: a package whose events reach the steering surface
requires: [kit]
contributes:
  events:
    sectors:
      watch: {icon: 👁, default: true}
    vectors:
      witness-spot: {verify: pp-witness-spot}
    signals:
      noticed: {threshold: "@SETTINGS.witness_patience", priority: 2, standing: true}
"""
FRAGMENT = ("---\nname: SETTINGS\nkind: doc\nwitness_patience: 2\n---\n\n"
            "# Witness\n\n- `witness_patience` -- how many sightings cross.\n")
# the order at the socket is the requires topology of the homes, then the NAME
CONSUMER = ("---\nname: AWATCH\nkind: proc\ndescription: the witness's own consumer, "
            "carrying its standing lines into the turn\noutput: line\nattach: turn.end\n"
            # the same document provides its token and consumes it
            "provides: witness-sightings\nwith: pp-witness lines\n"
            "payloads: witness-sightings\nproc: |\n  WORK\n---\n\n"
            "# AWATCH\n\nThe lines under `INFORMATION — witness-sightings` are this producer's own: "
            "formulate each one, the surface carries them.\n")
PAYLOAD = '''#!/usr/bin/env python3
"""The witness's payload: the standing entries of the bus, one line each."""
import json
from pathlib import Path

for parent in Path(__file__).resolve().parents:
    if (parent / ".sys" / "instance.yaml").is_file():
        record = parent / ".sys" / "records" / "events.json"
        break
held = json.loads(record.read_text(encoding="utf-8")) if record.is_file() else {}
for key, entry in sorted(held.items()):
    if key.startswith("standing|"):          # the record's own key shape, nothing else held
        print(entry.get("text", ""))
'''


def _witness(made) -> None:
    """Writes the producer INTO the bench instance -- no package of the product."""
    root = made / ".sys" / "vendor" / "witness@0.0.1"
    (root / "settings").mkdir(parents=True)
    (root / "procs").mkdir()
    (root / "package.yaml").write_text(MANIFEST, encoding="utf-8")
    (root / "settings" / "SETTINGS.md").write_text(FRAGMENT, encoding="utf-8")
    (root / "procs" / "AWATCH.md").write_text(CONSUMER, encoding="utf-8")
    home = root / "skills" / "pp-witness"
    home.mkdir(parents=True)
    (home / "SKILL.md").write_text(
        "---\nname: pp-witness\ndescription: the witness payload\n---\n\npp-witness\n",
        encoding="utf-8")
    (home / "pp-witness.py").write_text(PAYLOAD, encoding="utf-8")
    spot = root / "skills" / "pp-witness-spot"                # the family's verifier: every slug is a node
    spot.mkdir(parents=True)
    (spot / "SKILL.md").write_text("---\nname: pp-witness-spot\ndescription: the witness verifier\n---\n\npp-witness-spot\n", encoding="utf-8")
    (spot / "pp-witness-spot.py").write_text("#!/usr/bin/env python3\nimport sys\nsys.stdin.read()\nraise SystemExit(0)\n", encoding="utf-8")
    pins = instance.read(made)
    pins["packages"]["witness"] = "0.0.1"
    instance.write(made, pins)


def _boot(env):
    """Opens the run with a boot, fused up to the WORK step; -> its first block."""
    opener = env.conductor("t")
    return opener.start(opener.boot("BOOT.md"))


def _close(env) -> list:
    """-> the blocks from the work's own output to the closing -- every turn.end contributor
    stands among them; a proof is answered n/a."""
    blocks, pending = [], env.conductor("t").submit("")
    for _ in range(12):
        if pending is None:
            break
        blocks.append(pending)
        if pending.judged:
            env.conductor("t").submit(na_proof(pending))
            break
        if pending.wait:
            break
        pending = env.conductor("t").submit("")
    return blocks


def _exchanges(env, count: int) -> list[list]:
    """Drives `count` exchanges after a boot; -> the blocks of each."""
    _boot(env)
    played = [_close(env)]
    for _ in range(count - 1):
        env.conductor("t").submit("a message")       # the operator's message: the WORK
        played.append(_close(env))
    return played


def _documents(blocks) -> set:
    return {one.document for one in blocks if one is not None}


def _payloads(blocks) -> set:
    """-> every reading token the blocks served."""
    return {token for one in blocks if one is not None for token in dict(one.payloads)}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- the kit alone: the socket is empty, the turn goes from the work to the closing ------
    bare = bench.env("nxkit")
    exchanges = _exchanges(bare, 3)
    documents = set().union(*(_documents(one) for one in exchanges))
    if "NEXT" not in documents and not any(_payloads(one) & {"steering-threads"} for one in exchanges):
        held("the kit alone closes without NEXT",
             "three exchanges: no block at the empty socket -- AWAIT stands on its own")
    else:
        failures.append(f"  ✗ kit alone                  {sorted(documents)}")

    # --- kit + steering: NEXT alone after the work ---------------------------------------------
    env = bench.env("served", packages=("steering",))
    made = env.made
    played = _exchanges(env, 3)
    opened = ["NEXT" in _documents(one) for one in played]
    passes = [one for group in played for one in _documents(group) if one == "THREADS"]
    tables = [group for group in played if "steering-threads" in _payloads(group)]
    if all(opened) and not passes and not tables:
        held("kit + steering closes on NEXT alone",
             "every exchange: NEXT after the work, no THREADS block, no `steering-threads` reading")
    else:
        failures.append(f"  ✗ next alone                 opened={opened} threads={len(passes)} tables={len(tables)}")

    # --- two contributors stand together, in whichever order the engine gives them ------------
    # the witness is the instance's own document: the area composes nothing it does not require
    env.write("procs/ZWITNESS.md",
              "---\nname: ZWITNESS\nkind: proc\ndescription: a witness attached at turn.end\n"
              "attach: turn.end\noutput: line\nproc: |\n  WORK\n---\n\nZWITNESS says hi\n")
    compiling.build_tools(made)
    attached = set(instance.attached(made, "turn.end"))
    together = _documents(_exchanges(env, 1)[0])
    if attached == {"NEXT.md", "ZWITNESS.md"} and {"NEXT", "ZWITNESS"} <= together:
        held("two contributors of turn.end render",
             "NEXT and a witness open in the same exchange -- the order is the engine's, asserted nowhere")
    else:
        failures.append(f"  ✗ two contributors           attached={sorted(attached)} together={sorted(together)}")

    # --- a producer's standing line: published, carried at turn.end, acquitted -----------------
    _witness(made)
    compiling.build_tools(made)
    first = events.push(made, "witness", "noticed", vector="witness-spot:door")
    second = events.push(made, "witness", "noticed", vector="witness-spot:door")
    sighting = "the witness saw the door left open"
    events.stand(made, "noticed", "witness-spot:door", sighting)
    standing = [one for one in events.standing_entries(made) if one["vector"] == "witness-spot:door"]
    if first is None and second is not None and second["n"] == 2 and standing:
        held("the producer publishes and stands",
             "two pushes cross witness_patience, the entry holds -- no other package in the composition")
    else:
        failures.append(f"  ✗ publication                first={first} second={second} standing={standing}")

    blocks = _exchanges(env, 1)[0]
    documents = [one.document for one in blocks if one is not None]
    carried = [render(one) for one in blocks if one is not None and one.document == "AWATCH"]
    arrived = bool(carried) and sighting in carried[0]
    if arrived and {"AWATCH", "NEXT"} <= set(documents):
        held("the producer's line reaches the turn",
             "its own block carries the standing line and NEXT stands in the same exchange -- no other package anywhere")
    else:
        failures.append(f"  ✗ arrival                    documents={documents} arrived={arrived}")

    # the socket expands in the requires topology of the homes: a producer whose home comes
    # after steering's renders after NEXT, and no declaration can say otherwise
    homes = [one.name.split("@")[0] for one in instance.vendored(made)]
    order = list(instance.attached(made, "turn.end"))
    if (homes.index("steering") < homes.index("witness")
            and "AWATCH.md" in order and order.index("NEXT.md") < order.index("AWATCH.md")):
        held("the socket's order is the homes' topology",
             "the producer's home follows steering's, so its block follows NEXT -- declared nowhere")
    else:
        failures.append(f"  ✗ topology order             homes={homes} order={order}")

    fell = events.acquit(made, "witness-spot:door")
    after = [render(one) for one in _exchanges(env, 1)[0] if one is not None and one.document == "AWATCH"]
    quiet = not any(sighting in one for one in after)
    if fell >= 2 and "witness-spot:door" not in events.counters(made) and quiet:
        held("the acquit ends it", "counter and standing entry fall together; the next exchange carries nothing")
    else:
        failures.append(f"  ✗ acquit                     fell={fell} quiet={quiet}")

    # --- the ledger after a compaction ---------------------------------------------------------
    token = "steering-ledger"
    keeper = S.keeper_module(made)
    keeper.add(made, "un-pas-du-registre", "le travail qui reste", [], None)
    sid = next(one for one, step in keeper.load(made)["steps"].items() if step["name"] == "un-pas-du-registre")
    # the compaction by the console, as the agent declares it: a run of its own, its boot drained first
    opened = env.cli("-new")
    key = opened.stdout.split("run ", 1)[1].split()[0]
    shown = opened.stdout
    while "a reading continues" in shown:
        shown = env.cli(key).stdout
    declared = env.cli(key, "-compacted").stdout
    whole = declared
    while "a reading continues" in declared:
        declared = env.cli(key).stdout
        whole += declared
    if f"INFORMATION — {token}" in whole and f"[s.{sid.rsplit('.', 1)[1]}]" in whole:
        held("a compaction serves it back", "`-compacted` by the console re-serves the boot's documents, the "
             "ledger among them")
    else:
        failures.append(f"  ✗ ledger after compaction     {whole[-240:]!r}")

    # --- the STEERING space: its welcome once, then its WORK; closed ---------------------------
    now = datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc)
    kept_clock = os.environ.get("PP_NOW")
    try:
        os.environ["PP_NOW"] = (now - timedelta(days=16)).isoformat()
        keeper.add(made, "un-pas-endormi", "un travail laisse seize jours", [], None)
        os.environ["PP_NOW"] = (now - timedelta(days=2)).isoformat()
        keeper.add(made, "un-pas-vivant", "un travail touche avant-hier", ["le-lot"], None)
        steps = keeper.load(made)["steps"]
        asleep = next(one for one, step in steps.items() if step["name"] == "un-pas-endormi")
        os.environ["PP_NOW"] = now.isoformat()
        before = _boot(env)
        offered = "STEERING" in {one.name for one in compiling.effective(made, reading.read(instance.resolve(made, "TURN.md")))[1]}
        conductor = env.conductor("t")
        welcome = conductor.open("STEERING", route=conductor.route("STEERING"))
        board = dict(welcome.payloads).get("steering-board", "") if welcome is not None else ""
        work, seen = env.conductor("t").submit("the board, in tables"), []
        while work is not None and work.document != "STEERING" and len(seen) < 3:   # the welcome's frame closes first
            seen.append(work.document)
            work = env.conductor("t").submit("")
        codes = {one.code for one in work.constraints} if work is not None else set()
        swept = keeper.load(made)["steps"][asleep]["archived"] is not None
        _close(env)
        again = env.conductor("t").submit("a message in the space")
        replayed = again is not None and (again.document == "STEERING-BOARD" or "steering-board" in dict(again.payloads))
        back = env.conductor("t").close()
    finally:
        if kept_clock is None:
            os.environ.pop("PP_NOW", None)
        else:
            os.environ["PP_NOW"] = kept_clock
    form = compiling.format_enumeration(made).get("steering-board")
    if (offered and welcome is not None and welcome.root == "STEERING" and welcome.document == "STEERING-BOARD"
            and welcome.output == "steering-board" and "#le-lot" in board and "steering-archived" not in dict(welcome.payloads)
            and swept and work is not None and work.document == "STEERING" and {"ST5", "ST6"} <= codes
            and again is not None and again.document == "STEERING" and not replayed
            and form is not None and form[0] == language.WORDS
            and back is not None and before is not None and back.root == before.root):
        held("the STEERING space opens on its welcome, once", "offered at TURN; opened, STEERING-BOARD sweeps and serves "
             "the board to an INFER in the form steering-board (words), then the WORK under ST5 and ST6; the next message "
             "plays the WORK alone; closed, the root it was opened from is back")
    else:
        failures.append(f"  ✗ the space                  offered={offered} root={getattr(welcome, 'root', None)} "
                        f"first={getattr(welcome, 'document', None)}/{getattr(welcome, 'output', None)} swept={swept} "
                        f"work={getattr(work, 'document', None)} via={seen} codes={sorted(codes)} again={getattr(again, 'document', None)} "
                        f"replayed={replayed} form={form} back={getattr(back, 'root', None)} board={board[:80]!r}")

    # --- NEXT composes its clients: the base alone first, then an overlay ----------------------
    conductor = env.conductor("t")
    base = instance.resolve(made, "NEXT.md")
    alone_text, alone_hash = conductor._composed(base)
    absent = [word for word in ("served", "@<member>") if word in alone_text.lower()]
    tail = alone_text.rstrip().splitlines()[-1]     # the base's own last line, read at run time
    if not absent and (alone_text, alone_hash) == reading.served(base):
        held("the base alone names no client",
             "no client vocabulary survives the document; with no overlay the served bytes are its own")
    else:
        failures.append(f"  ✗ base alone                 client words={absent}")

    paragraph = "The client's paragraph lands after the base.\n"
    env.write("procs/NEXT.md", "---\nname: NEXT\nconstraints.behavior: |\n"
              "  ZZ9  the client's own semantics ride here.\n---\n\n" + paragraph)
    over = instance.resolve(made, "NEXT.md")
    laws = [one.code for one in compiling.effective(made, reading.read(over))[0]]
    over_text, over_hash = conductor._composed(over)
    ordered = -1 < over_text.find(tail) < over_text.find(paragraph)
    if "ZZ9" in laws and ordered and over_text.endswith(paragraph) and over_hash != alone_hash:
        held("a client's overlay composes onto the base",
             "its law binds, its prose lands after the base's, one hash over the whole")
    else:
        failures.append(f"  ✗ overlay composes           laws={laws} ordered={ordered} "
                        f"tail={over_text[-80:]!r}")
    return 0
