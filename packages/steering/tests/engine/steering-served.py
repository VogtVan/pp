"""Scenario `steering-served` -- what the steering surface serves the turn:
- the kit alone closes an exchange on the work: no block at the empty socket, no NEXT
- kit + steering opens NEXT after the work, in its own output, before the closing
- a second contributor of the same socket stands beside NEXT in one exchange; which one
  first is nobody's business here -- the socket's order is the engine's
- the surface reads its OWN front: the NEXT block carries the `steering-threads` table, a
  row per thread with a step to do, the waiting steps at the ⏸ line with their reason
- a producer package's standing line reaches the turn at its own turn.end block, beside
  NEXT, in the requires topology of the homes; the acquit ends it
- the LEDGER mounted at `boot.ready` serves the open threads once, at the session's first
  block, and again after a declared compaction
- NEXT takes its clients' semantics by composition: an overlay's law binds, its prose
  lands after the base's
"""
from __future__ import annotations

from conductor import compiling, events, instance, reading, render
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
        if "INFER proof" in render(pending):
            env.conductor("t").submit(na_proof(pending))
            break
        if "FINAL" in (pending.next_call or ""):
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


def _thread(record: dict, name: str) -> str:
    return next(tid for tid, one in record["threads"].items() if one["name"] == name)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- the kit alone: the socket is empty, the turn goes from the work to the closing ------
    bare = bench.env("nxkit")
    exchanges = _exchanges(bare, 3)
    documents = set().union(*(_documents(one) for one in exchanges))
    tables = [render(one) for group in exchanges for one in group if "| thread" in render(one)]
    if "NEXT" not in documents and not tables:
        held("the kit alone closes without NEXT",
             "three exchanges: no block at the empty socket, no threads table -- FINAL stands on its own")
    else:
        failures.append(f"  ✗ kit alone                  {sorted(documents)} tables={len(tables)}")

    # --- kit + steering: NEXT opens after the work ---------------------------------------------
    env = bench.env("served", packages=("steering",))
    made = env.made
    opened = ["NEXT" in _documents(one) for one in _exchanges(env, 3)]
    if all(opened):
        held("kit + steering opens NEXT after the work",
             "every exchange: the turn.end contributor renders its own output before the closing")
    else:
        failures.append(f"  ✗ next at turn.end           {opened}")

    # --- two contributors stand together, in whichever order the engine gives them ------------
    # the witness is the instance's own document: the area composes nothing it does not require
    env.write("procs/ZWITNESS.md",
              "---\nname: ZWITNESS\nkind: proc\ndescription: a witness attached at turn.end\n"
              "attach: turn.end\noutput: line\nproc: |\n  WORK\n---\n\nZWITNESS says hi\n")
    compiling.build_tools(made)
    attached = set(instance.attached(made, "turn.end"))
    together = _documents(_exchanges(env, 1)[0])
    if attached == {"THREADS.md", "ZWITNESS.md"} and {"NEXT", "ZWITNESS"} <= together:
        held("two contributors of turn.end render",
             "the surface and a witness open in the same exchange -- the order is the engine's, asserted nowhere")
    else:
        failures.append(f"  ✗ two contributors           attached={sorted(attached)} together={sorted(together)}")

    # --- the surface reads its own FRONT, the front of the moment ------------------------------
    keeper = S.keeper_module(made)
    step_text, note, reason = "the step the surface must show", "the thread of the moment", "waits for the release"
    keeper.open_thread(made, "le-fil-du-front", f"le-pas-du-front | {step_text}\n")
    keeper.open_thread(made, "le-fil-actif", "a-un | the step to do\n", note=note)
    keeper.open_thread(made, "le-fil-en-attente", "w-un | the waiting step\n")
    record = keeper.load(made)
    parked = _thread(record, "le-fil-en-attente")
    keeper.block(made, parked, record["threads"][parked]["steps"][0], reason)
    shown = next((render(one) for one in _exchanges(env, 1)[0] if one.document == "NEXT"), "")
    if ("INFORMATION — steering-threads" in shown and "| le-fil-du-front |" in shown
            and "| `le-pas-du-front` |" in shown and "| threads | shipped |" not in shown
            and step_text not in shown):
        held("the surface reads its own front",
             "kit + steering: the NEXT block carries `steering-threads` -- the table with the open "
             "thread and the NAME of its pointed step, its text left out -- with no other "
             "package to consume the token")
    else:
        failures.append(f"  ✗ the surface reads its own front   {(shown[:200] if shown else 'no NEXT block')!r}")

    # a thread whose steps all wait has no row: its waiting step reaches the ⏸ line with its reason
    rows = [line for line in shown.splitlines() if line.startswith("| ") and not line.startswith("| initiative |")]
    pause = next((line for line in shown.splitlines() if line.startswith("⏸")), "")
    waits = [one for one in pause.removeprefix("⏸").split(" · ") if "le-fil-en-attente" in one]
    if (any(row.startswith(f"| le-fil-actif | {note} |") for row in rows)
            and not any(row.startswith("| le-fil-en-attente |") for row in rows)
            and len(waits) == 1 and "`w-un`" in waits[0] and f"({reason})" in waits[0]):
        held("the front of the moment at the NEXT block",
             "the thread with a step to do keeps its row and its note; the thread whose steps all wait "
             "has none, its step reaches the ⏸ line with its reason")
    else:
        failures.append(f"  ✗ the front of the moment     rows={rows} pause={pause!r}")

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
             "its own block carries the standing line and the surface stands in the same exchange -- no other package anywhere")
    else:
        failures.append(f"  ✗ arrival                    documents={documents} arrived={arrived}")

    # the socket expands in the requires topology of the homes: a producer whose home comes
    # after the surface's renders after it, and no declaration can say otherwise
    homes = [one.name.split("@")[0] for one in instance.vendored(made)]
    order = list(instance.attached(made, "turn.end"))
    if (homes.index("steering") < homes.index("witness")
            and "AWATCH.md" in order and order.index("THREADS.md") < order.index("AWATCH.md")):
        held("the socket's order is the homes' topology",
             "the producer's home follows steering's, so its block follows the surface -- the sequence a carried line needs is declared nowhere")
    else:
        failures.append(f"  ✗ topology order             homes={homes} order={order}")

    fell = events.acquit(made, "witness-spot:door")
    after = [render(one) for one in _exchanges(env, 1)[0] if one is not None and one.document == "AWATCH"]
    quiet = not any(sighting in one for one in after)
    if fell >= 2 and "witness-spot:door" not in events.counters(made) and quiet:
        held("the acquit ends it", "counter and standing entry fall together; the next exchange carries nothing")
    else:
        failures.append(f"  ✗ acquit                     fell={fell} quiet={quiet}")

    # --- the ledger: once at the boot, again after a compaction --------------------------------
    token = "steering-ledger"
    keeper.open_thread(made, "le-fil-du-registre", "une-etape-faite\nune-etape-a-faire | le travail qui reste\n",
                       note="le pourquoi du fil")
    tid = _thread(keeper.load(made), "le-fil-du-registre")
    keeper.done(made, tid, keeper.load(made)["threads"][tid]["steps"][0])
    booted = _boot(env)
    ledger = dict(booted.payloads).get(token, "") if booted is not None else ""
    if (f"~ le-fil-du-registre [{tid}]" in ledger and "le pourquoi du fil" in ledger
            and "une-etape-a-faire" in ledger and "une-etape-faite" not in ledger):
        held("the boot serves the ledger", "the first block carries `steering-ledger`: the open thread with its "
             "id and note, its step still to do -- the delivered one left out")
    else:
        failures.append(f"  ✗ ledger at boot              {ledger[:160]!r}")

    # the rest of the boot exchange, then one more
    later = _close(env) + [env.conductor("t").submit("the operator's next message")] + _close(env)
    if not [block for block in later if block is not None and token in dict(block.payloads)]:
        held("the next exchange does not re-read it", "the blocks after the boot carry no `steering-ledger`: the "
             "session works from what it did")
    else:
        failures.append("  ✗ ledger re-served            a later block carries the ledger again")

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
    if f"INFORMATION — {token}" in whole and f"~ le-fil-du-registre [{tid}]" in whole:
        held("a compaction serves it back", "`-compacted` by the console re-serves the boot's documents, the "
             "ledger among them")
    else:
        failures.append(f"  ✗ ledger after compaction     {whole[-240:]!r}")

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
    if ("ZZ9" in laws and "NX1" in laws and ordered and over_text.endswith(paragraph)
            and over_hash != alone_hash):
        held("a client's overlay composes onto the base",
             "its law joins NX1, its prose lands after the base's, one hash over the whole")
    else:
        failures.append(f"  ✗ overlay composes           laws={laws} ordered={ordered} "
                        f"tail={over_text[-80:]!r}")
    return 0
