"""Scenario `events-to-next` -- a producer's line reaches the steering surface (plan
pp-split, phase steering, batch les-evenements-dans-next):
- a witness package declares its own events and its payload, pushes, crosses its
  threshold and holds a standing entry -- with no improvement package at all
- its consumer document opens at turn.end and carries that line into the turn
- the NEXT block follows in the SAME exchange: turning the line into a step is the
  agent's work, and this scenario never judges its prose
- the acquit drops counter and entry together, and the line does not come back
"""
from __future__ import annotations

from conductor import compiling, events, instance, render

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
            # the provider lives at the DOCUMENT since le-payload-au-document: the same
            # document provides its token and consumes it
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


def _exchange(env) -> list:
    """One exchange after the boot; -> its blocks, from the work's output to the closing."""
    opener = env.conductor("t")
    opener.start(opener.boot("BOOT.md"))
    blocks, pending, steps = [], env.conductor("t").submit(""), 0
    while pending is not None and steps < 8:
        steps += 1
        blocks.append(pending)
        if "INFER proof" in render(pending):
            env.conductor("t").forward("", skip=True)
            break
        if "FINAL" in (pending.next_call or ""):
            break
        pending = env.conductor("t").submit("")
    return blocks


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    env = bench.env("evnext", packages=("steering",))
    made = env.made
    _witness(made)
    compiling.build_tools(made)

    # --- publication: the count crosses its own threshold, the entry stands ---------------
    first = events.push(made, "witness", "noticed", vector="witness-spot:door")
    second = events.push(made, "witness", "noticed", vector="witness-spot:door")
    events.stand(made, "noticed", "witness-spot:door", "the witness saw the door left open")
    standing = [one for one in events.standing_entries(made) if one["vector"] == "witness-spot:door"]
    if first is None and second is not None and second["n"] == 2 and standing:
        held("the producer publishes and stands",
             "two pushes cross witness_patience, the entry holds -- no improvement package in the composition")
    else:
        failures.append(f"  ✗ publication                first={first} second={second} standing={standing}")

    # --- the line arrives at the turn, beside the surface, in one exchange ---------------
    blocks = _exchange(env)
    documents = [one.document for one in blocks if one is not None]
    carried = [render(one) for one in blocks if one is not None and one.document == "AWATCH"]
    arrived = bool(carried) and "the witness saw the door left open" in carried[0]
    if arrived and {"AWATCH", "NEXT"} <= set(documents):
        held("the producer's line reaches the turn",
             "its own block carries the standing line and the surface stands in the same exchange -- no improvement anywhere")
    else:
        failures.append(f"  ✗ arrival                    documents={documents} arrived={arrived}")

    # --- the sequence is the HOMES' topology, nobody's declaration ------------------------
    homes = [one.name.split("@")[0] for one in instance.vendored(made)]
    order = instance.attached(made, "turn.end")
    # the socket expands in the requires topology of the homes: a producer whose home
    # comes after the surface's renders after it, and no declaration can say otherwise
    later = homes.index("steering") < homes.index("witness") and order == ("THREADS.md", "AWATCH.md")
    if later:
        held("the socket's order is the homes' topology",
             "the producer's home follows steering's, so its block follows the surface -- the sequence a carried line needs is declared nowhere")
    else:
        failures.append(f"  ✗ topology order             homes={homes} order={order}")

    # --- the acquit drops both, and the line does not come back ---------------------------
    fell = events.acquit(made, "witness-spot:door")
    after = [render(one) for one in _exchange(env) if one is not None and one.document == "AWATCH"]
    quiet = not any("the witness saw the door left open" in one for one in after)
    if fell >= 2 and "witness-spot:door" not in events.counters(made) and quiet:
        held("the acquit ends it", "counter and standing entry fall together; the next exchange carries nothing")
    else:
        failures.append(f"  ✗ acquit                     fell={fell} quiet={quiet}")
    return 0
