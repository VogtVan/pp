"""Scenario `serve` -- the ledger that says what a block served:
- a line per payload in the block's order, each line says where it came from, the package is
  attributed, a spared reading keeps its line, a gone document is `missing`, the measure never
  moved, a re-serve says what comes back
- a payload says its provider and a refusal and a re-read say theirs, a door's element says its own
SERVE, its rows and the mount's readings are the pattern `context/serve`; a payload served once is
`context/payload`; what a sink said back is `outputs/sink`.
"""
from __future__ import annotations

import re

from conductor import render
from tests.harness import support

run = support(__file__, "run")

# --- the witness package: one provider that speaks, one that refuses
REFUSES = "#!/usr/bin/env python3\nimport sys\nsys.stderr.write('it refuses\\n')\nsys.exit(2)\n"
SPEAKS = "#!/usr/bin/env python3\nprint('the witness skill says hello')\n"
WITNESS = {"GIVER": ("witness", "pp-witness", SPEAKS),
           "BREAKER": ("witness-broken", "pp-witness-broken", REFUSES)}

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



def _blocks(env, key: str) -> list[dict]:
    """-> every block event of the run's own trace, in order."""
    return [one for one in run.trace(env, key) if one.get("kind") == "block"]


def _lines(env, key: str, subject: str | None = None) -> list[dict]:
    """-> every ledger line of the run's blocks, of `subject` when named."""
    return [line for one in _blocks(env, key) for line in (one.get("served") or [])
            if subject is None or line.get("subject") == subject]


def _tune(env, fusion: str, body_serve: str) -> None:
    """The settings a case plays under: the fusion of instructions and how a body rides."""
    settings = env.made / "SETTINGS.md"
    text = settings.read_text(encoding="utf-8")
    text = re.sub(r"^instructions_fusion: \S+", f"instructions_fusion: {fusion}", text, flags=re.M)
    text = re.sub(r"^proc_body_serve: \S+", f"proc_body_serve: {body_serve}", text, flags=re.M)
    settings.write_text(text, encoding="utf-8")


def _booted(env, key: str):
    """-> the first block of a fresh run under `key`, booted."""
    runner = run.conductor_of(env, key)
    return runner.start(runner.boot("BOOT.md"))


def ledger(bench) -> None:
    """The ledger of a member's first block: one line per payload, its origin, its package,
    what is spared, what is gone, the measure -- and the re-serve of a compaction."""
    held, failures = bench.held, bench.failures
    env = bench.env("ledger", ("greeter",))       # the greeter MOUNTS a document at boot.initialize
    env.write("INNER.md", INNER)
    env.write("NOTE.md", "---\nname: NOTE\nkind: doc\ndescription: a note\n---\n\nThe note's body.\n")
    env.write_member("serve: |\n  reference: NOTE.md\nconstraints.behavior: |\n  M1  your name is AGENT\n",
                     body="The witness member.", proc="SERVE\n  CALL INNER.md\n  INFER", name="AGENT")
    text = render(_booted(env, "t"))
    blocks = _blocks(env, "t")
    first = blocks[0]
    lines = first.get("served") or []
    payloads = first.get("payloads") or {}

    # --- one line per payload, in the same order, and the block's text stands ---------
    served = [line for line in lines if line.get("state") != "spared"]
    titles = [line["subject"] for line in served]
    sections = re.findall(r"^▌ INFORMATION — (.+)$", text, flags=re.M)
    if titles and sections and titles[:len(sections)] == sections and set(payloads) <= set(titles):
        held("a line per payload, in the block's order",
             f"{len(served)} line(s) for {len(sections)} INFORMATION section(s), the same "
             "subjects in the same order -- the ledger reads as the block reads")
    else:
        failures.append(f"  ✗ the order                   {titles!r} vs {sections!r}")

    # --- the origins, and who asked ----------------------------------------------------
    origins = {}
    for line in lines:             # a subject served twice keeps BOTH lines: the first wins here
        origins.setdefault(line["subject"], (line.get("origin"), line.get("by"), line.get("nature")))
    if (origins.get("standing orders", ("",))[0] == "marble"
            and origins.get("AGENT", ("",))[0] == "body"
            and origins.get("NOTE.md") == ("serve", "MEMBER", "reference")
            and any(v[0] == "mount" for v in origins.values())):
        held("each line says where it came from",
             "the marble at the boot, the member's body, `NOTE.md` served by a row of MEMBER "
             "with its declared nature (`reference`), and the greeter's GREETING mounted at the "
             "socket -- a subject asked twice keeps both its lines")
    else:
        failures.append(f"  ✗ the origins                 {origins!r}")

    # --- the package of the asking document --------------------------------------------
    packages = {line["subject"]: line.get("package") for line in lines}
    if (packages.get("standing orders") == "engine" and packages.get("AGENT") == "instance"
            and packages.get("NOTE.md") == "instance"
            and any(value == "greeter" for value in packages.values())):
        held("the package is attributed", "`engine` for the marble, `instance` for the "
             "operator's own documents, `greeter` for what its package serves")
    else:
        failures.append(f"  ✗ the packages                {packages!r}")

    # --- a reading already proven is SPARED --------------------------------------------
    spared = [line for line in _lines(env, "t") if line.get("state") == "spared"]
    if spared and all(line.get("spared") for line in spared):
        held("a spared reading keeps its line", f"{len(spared)} line(s) `spared`, each with "
             "the mass it avoided -- what was invisible before is counted now")
    else:
        failures.append(f"  ✗ spared                      {spared[:2]!r}")

    # --- a gone document is missing -----------------------------------------------------
    missing = [line for line in _lines(env, "t") if line.get("state") == "missing"]
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

    # --- a compaction's re-serve says `reserved` ------------------------------------------
    run.conductor_of(env, "t").compacted()
    reserved = [line for line in (_blocks(env, "t")[-1].get("served") or [])
                if line.get("state") == "reserved"]
    if reserved and any(line.get("origin") == "marble" for line in reserved):
        held("a re-serve says what comes back", f"{len(reserved)} line(s) `reserved` after "
             "`-compacted`, the marble among them -- the matter a summary took away, served "
             "back and said so")
    else:
        failures.append(f"  ✗ reserved                    {[line.get('state') for line in (_blocks(env, 't')[-1].get('served') or [])]!r}")


def provenance(bench) -> None:
    """The provenance of a payload, of a refusal, of a re-read and of a door's element."""
    held, failures = bench.held, bench.failures
    env = bench.env("payloads")
    run.pin_package(env.made, "witness", WITNESS)

    # --- a payload's provider, a refusal, a body re-read on purpose -----------------------
    env.write("ASKER.md", ASKER)
    env.write_member(body="The member calls ASKER twice.", proc="CALL ASKER.md\n  CALL ASKER.md\n  INFER",
                     name="AGENT")
    _tune(env, "none", "always")
    runner = run.conductor_of(env, "p")
    block = runner.start(runner.boot("BOOT.md"))
    for _ in range(6):
        if block is None or block.wait:
            break
        block = runner.forward("")
    lines = _lines(env, "p")
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

    # --- an iterated door's element ----------------------------------------------------------
    env.write("LOOPER.md", LOOPER)
    env.write_member(body="The member opens a door.", proc="CALL LOOPER.md\n  INFER", name="AGENT")
    _tune(env, "none", "always")
    walker = run.conductor_of(env, "d")
    step = walker.start(walker.boot("BOOT.md"))
    for _ in range(5):
        if step is None or step.wait:
            break
        step = walker.forward("a production for the step")
    door_lines = _lines(env, "d")
    lap = next((line for line in door_lines if line.get("origin") == "cycle"), {})
    if lap.get("by") == "LOOPER" and lap.get("state") == "served":
        held("a door's element says its own", f"LOOPER's element `{lap.get('subject')}` "
             "is `cycle`, asked by the door itself")
    else:
        failures.append(f"  ✗ the door's element          lap={lap!r} "
                        f"origins={sorted({line.get('origin') for line in door_lines})!r}")


def scenario(bench) -> int:
    ledger(bench)
    provenance(bench)
    return 0
