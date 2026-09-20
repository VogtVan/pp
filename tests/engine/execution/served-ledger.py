"""Scenario `served-ledger` -- 9 case(s) (plan core, batch l-origine-au-payload):
- every payload of a block has its LEDGER line, in the same order, and the block's text does not move
- each line says where the matter came from and who asked: the marble, a body, a serve row with its nature, a mount, a payload with its provider
- the package is the ASKING document's own, `instance` for the operator's space and `engine` for the marble
- a reading already proven is SPARED: its line stands, with the mass it avoided, and nothing enters the block
- a gone document is `missing` and a refusing provider is `refused`; a compaction's re-serve says `reserved`
- `payloads` keeps its shape and its figures: what the measure reads never moved
- a payload says its provider skill and its package, a refusing provider is `refused`, a body re-read on purpose is `forced`
- a compaction's re-serve writes `reserved` for what it serves back
- an iterated door's element says `cycle`, and what a sink said back says `sink`
"""
from __future__ import annotations

import json
import re

from conductor import Conductor, discovery, instance, render

WITNESS = """---
name: AGENT
kind: proc
description: the witness member
serve: |
  reference: NOTE.md
constraints.behavior: |
  M1  your name is AGENT
proc: |
  SERVE
  CALL INNER.md
  INFER
---

The witness member.
"""
INNER = """---
name: INNER
kind: proc
description: a called document
serve: |
  code: NOTE.md GONE.md
proc: |
  SERVE
  INFER
---

The inner body.
"""


WITNESS_PACKAGE = """name: witness
version: 0.0.1
description: a package that provides one payload that serves and one that refuses
requires: [kit]
"""
PROVIDER = """---
name: {name}
kind: doc
description: a provider of the witness package
provides: {token}
with: {skill}
---

{name} gives
"""
ASKER = """---
name: ASKER
kind: proc
description: a document that asks for both payloads
payloads: witness witness-broken
proc: |
  INFER
---

ASKER asks
"""
SINKER = """---
name: SINKER
kind: proc
description: a document whose production goes to a sink
sink: pp-witness
proc: |
  INFER
---

SINKER hands its production over
"""
LOOPER = """---
name: LOOPER
kind: proc
description: an iterated door on the witness token
cycle: witness
proc: |
  INFER
---

LOOPER turns once per element
"""
SPEAKS = "#!/usr/bin/env python3\nprint('the witness skill says hello')\n"
REFUSES = "#!/usr/bin/env python3\nimport sys\nsys.stderr.write('it refuses\\n')\nsys.exit(2)\n"


def _pin_witness(made) -> None:
    """A witness package pinned by hand: two providers at their own documents, one skill
    that speaks, one that refuses -- the composition that shows a payload's origin."""
    root = made / ".sys" / "vendor" / "witness@0.0.1"
    (root / "procs").mkdir(parents=True, exist_ok=True)
    (root / "package.yaml").write_text(WITNESS_PACKAGE, encoding="utf-8")
    (root / "procs" / "GIVER.md").write_text(
        PROVIDER.format(name="GIVER", token="witness", skill="pp-witness"), encoding="utf-8")
    (root / "procs" / "BREAKER.md").write_text(
        PROVIDER.format(name="BREAKER", token="witness-broken", skill="pp-witness-broken"),
        encoding="utf-8")
    for name, code in (("pp-witness", SPEAKS), ("pp-witness-broken", REFUSES)):
        home = root / "skills" / name
        home.mkdir(parents=True, exist_ok=True)
        (home / "SKILL.md").write_text(f"---\nname: {name}\ndescription: a witness script\n---\n\n{name}\n",
                                       encoding="utf-8")
        (home / f"{name}.py").write_text(code, encoding="utf-8")
    pins = instance.read(made)
    pins["packages"]["witness"] = "0.0.1"
    instance.write(made, pins)


def _blocks(made) -> list[dict]:
    """-> every block line of the instance's newest trace, in order."""
    log = sorted((made / ".sys" / "state").glob("session-*.jsonl"))[-1]
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()
            if line.strip() and json.loads(line).get("kind") == "block"]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("ledger", ("continuity",))
    made = env.made
    env.write("MEMBER.md", WITNESS)
    env.write("INNER.md", INNER)
    env.write("NOTE.md", "---\nname: NOTE\nkind: doc\ndescription: a note\n---\n\nThe note's body.\n")
    member = discovery.instance_member(made / ".sys" / "engine" / "pp.py")

    def conductor(key: str = "t") -> Conductor:
        return Conductor(member, discovery.siblings_around(member),
                         made / ".sys" / "engine" / "pp.py", key)

    one = conductor()
    text = render(one.start(one.boot("BOOT.md")))
    blocks = _blocks(made)
    first = blocks[0]
    ledger = first.get("served") or []
    payloads = first.get("payloads") or {}

    # --- one line per payload, in the same order, and the block's text stands ---------
    served = [line for line in ledger if line.get("state") != "spared"]
    titles = [line["subject"] for line in served]
    sections = re.findall(r"^▌ INFORMATION — (.+)$", text, flags=re.M)
    if (titles and sections and titles[:len(sections)] == sections
            and set(payloads) <= set(titles)):
        held("a line per payload, in the block's order",
             f"{len(served)} line(s) for {len(sections)} INFORMATION section(s), the same "
             "subjects in the same order -- the ledger reads as the block reads")
    else:
        failures.append(f"  ✗ the order                   {titles!r} vs {sections!r}")

    # --- the origins, and who asked ----------------------------------------------------
    origins = {}
    for line in ledger:            # a subject served twice keeps BOTH lines: the first wins here
        origins.setdefault(line["subject"],
                           (line.get("origin"), line.get("by"), line.get("nature")))
    if (origins.get("standing orders", ("",))[0] == "marble"
            and origins.get("AGENT", ("",))[0] == "body"
            and origins.get("NOTE.md") == ("serve", "MEMBER", "reference")
            and any(v[0] == "mount" for v in origins.values())):
        held("each line says where it came from",
             "the marble at the boot, the member's body, `NOTE.md` served by a row of MEMBER "
             "with its declared nature (`reference`), and continuity's RECALL mounted at the "
             "socket -- a subject asked twice keeps both its lines")
    else:
        failures.append(f"  ✗ the origins                 {origins!r}")

    # --- the package of the asking document --------------------------------------------
    packages = {line["subject"]: line.get("package") for line in ledger}
    if (packages.get("standing orders") == "engine" and packages.get("AGENT") == "instance"
            and packages.get("NOTE.md") == "instance"
            and any(value == "continuity" for value in packages.values())):
        held("the package is attributed", "`engine` for the marble, `instance` for the "
             "operator's own documents, `continuity` for what its package serves")
    else:
        failures.append(f"  ✗ the packages                {packages!r}")

    # --- a reading already proven is SPARED --------------------------------------------
    spared = [line for block in _blocks(made) for line in (block.get("served") or [])
              if line.get("state") == "spared"]
    if spared and all(line.get("spared") for line in spared):
        held("a spared reading keeps its line", f"{len(spared)} line(s) `spared`, each with "
             "the mass it avoided -- what was invisible before is counted now")
    else:
        failures.append(f"  ✗ spared                      {spared[:2]!r}")

    # --- a gone document is missing -----------------------------------------------------
    missing = [line for block in _blocks(made) for line in (block.get("served") or [])
               if line.get("state") == "missing"]
    if missing and missing[0].get("origin") == "serve" and missing[0].get("by"):
        held("a gone document is `missing`", f"`{missing[0]['subject']}` -- the row that "
             f"asked it is named ({missing[0]['by']}), and the block says so in its place")
    else:
        failures.append(f"  ✗ missing                     {missing[:1]!r}")

    # --- `payloads` did not move ---------------------------------------------------------
    shaped = all(isinstance(pair, list) and len(pair) == 2 and all(isinstance(n, int) for n in pair)
                 for pair in payloads.values())
    weighed = first.get("weight", {}).get("payload")
    total = sum(pair[0] for pair in payloads.values())
    if shaped and weighed == total:
        held("the measure never moved", f"`payloads` is still {{subject: [chars, tokens]}} and "
             f"its sum ({total} c) is the block's payload part -- the readers of the measure "
             "read what they always read")
    else:
        failures.append(f"  ✗ payloads                    {shaped} {weighed} vs {total}")
    # --- a payload's provider, a refusal, a body re-read on purpose -----------------------
    lab = bench.env("ledger-payloads")
    _pin_witness(lab.made)
    lab.write("ASKER.md", ASKER)
    lab.write("MEMBER.md", """---
name: AGENT
kind: proc
description: the witness member
proc: |
  CALL ASKER.md
  CALL ASKER.md
  INFER
---

The member calls ASKER twice.
""")
    settings = lab.made / "SETTINGS.md"
    settings.write_text(settings.read_text(encoding="utf-8")
                        .replace("proc_body_serve: once", "proc_body_serve: always"), encoding="utf-8")
    lab_member = discovery.instance_member(lab.made / ".sys" / "engine" / "pp.py")
    runner = Conductor(lab_member, discovery.siblings_around(lab_member),
                       lab.made / ".sys" / "engine" / "pp.py", "p")
    block = runner.start(runner.boot("BOOT.md"))
    for _ in range(6):
        if block is None or block.wait:
            break
        block = runner.forward("")
    lines = [line for one in _blocks(lab.made) for line in (one.get("served") or [])]
    given = next((line for line in lines if line.get("subject") == "witness"), {})
    broken = next((line for line in lines if line.get("subject") == "witness-broken"), {})
    forced = [line for line in lines if line.get("state") == "forced"]
    if (given.get("origin") == "payload" and given.get("with") == "pp-witness"
            and given.get("package") == "witness" and given.get("by") == "ASKER"
            and broken.get("state") == "refused" and broken.get("with") == "pp-witness-broken"
            and forced and forced[0].get("subject") == "ASKER"):
        held("a payload says its provider, a refusal and a re-read say theirs",
             "`witness` served by the skill pp-witness of the package witness, asked by ASKER; "
             "`witness-broken` refused by pp-witness-broken; ASKER's body CALLed again under "
             "`proc_body_serve: always` is `forced`")
    else:
        failures.append(f"  ✗ payloads and states        given={given!r} broken={broken.get('state')!r} "
                        f"forced={[line.get('subject') for line in forced]!r}")

    # --- an iterated door's element, and what a sink said back ---------------------------
    door = bench.env("ledger-doors")
    _pin_witness(door.made)
    door.write("SINKER.md", SINKER)
    door.write("LOOPER.md", LOOPER)
    door.write("MEMBER.md", """---
name: AGENT
kind: proc
description: the witness member
proc: |
  CALL SINKER.md
  CALL LOOPER.md
  INFER
---

The member hands a production to a sink, then opens a door.
""")
    door_member = discovery.instance_member(door.made / ".sys" / "engine" / "pp.py")
    walker = Conductor(door_member, discovery.siblings_around(door_member),
                       door.made / ".sys" / "engine" / "pp.py", "d")
    step = walker.start(walker.boot("BOOT.md"))
    for _ in range(5):
        if step is None or step.wait:
            break
        step = walker.forward("a production for the step")
    door_lines = [line for one in _blocks(door.made) for line in (one.get("served") or [])]
    lap = next((line for line in door_lines if line.get("origin") == "cycle"), {})
    sank = next((line for line in door_lines if line.get("origin") == "sink"), {})
    if (lap.get("by") == "LOOPER" and lap.get("state") == "served"
            and sank.get("with") == "pp-witness" and sank.get("chars")):
        held("a door's element and a sink say theirs", f"LOOPER's element `{lap.get('subject')}` "
             "is `cycle`, asked by the door itself; what pp-witness said back from SINKER's "
             f"production is `sink` ({sank.get('chars')} c)")
    else:
        failures.append(f"  ✗ cycle and sink              lap={lap!r} sink={sank!r} "
                        f"origins={sorted({line.get('origin') for line in door_lines})!r}")

    # --- a compaction's re-serve says `reserved` ------------------------------------------
    back = conductor()
    back.compacted()
    reserved = [line for line in (_blocks(made)[-1].get("served") or [])
                if line.get("state") == "reserved"]
    if reserved and any(line.get("origin") == "marble" for line in reserved):
        held("a re-serve says what comes back", f"{len(reserved)} line(s) `reserved` after "
             "`-compacted`, the marble among them -- the matter a summary took away, served "
             "back and said so")
    else:
        failures.append(f"  ✗ reserved                    {[line.get('state') for line in (_blocks(made)[-1].get('served') or [])]!r}")
    return 0