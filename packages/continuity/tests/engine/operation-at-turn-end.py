"""Scenario `operation-at-turn-end` -- the consignation attaches to the turn (plan
pp-split, phase continuity, batch l-operation-du-tour):
- OPERATIONS opens at `turn.end` when its guard is due: the n-th completed exchange,
  nothing before, nothing at the others; the key at 0 never plays; the kit alone never
- the block opens AFTER the work's own output (the turn's `§`), with `pp-continuity`
  offered: the consignation lands in the record from there
- the order at the socket is the requires topology then the name, the instance's own last
"""
from __future__ import annotations

import json

from conductor import compiling, contributions, instance, render
from tests.harness import na_proof


def _exchanges(env, count: int, message: str = "a message", probe=None):
    """Drives `count` exchanges after the boot; -> the block each exchange rendered
    right after the work (where a turn.end contributor would open). `probe(n, block)`
    is called there, while that output is the current one."""
    after_work = []
    opener = env.conductor("t")
    opener.start(opener.boot("BOOT.md"))            # the boot fuses up to the WORK step
    for n in range(1, count + 1):
        if n > 1:
            env.conductor("t").submit(message)       # the operator's message: the WORK
        block = env.conductor("t").submit("")        # past the work: what turn.end opens
        after_work.append(block)
        if probe is not None:
            probe(n, block)
        pending = block
        while pending is not None and pending.command != "INFER" and not pending.wait:
            pending = env.conductor("t").submit("")  # a contributor's own step, then the checkpoint
                                                     # -- or the frontier itself: a vanilla member owes no proof
        if pending is not None and pending.command == "INFER":
            env.conductor("t").submit(na_proof(pending))   # the proof piped n/a: FINAL
    return after_work


def _opens_operations(block) -> bool:
    return block is not None and "▸ OPERATIONS{" in render(block)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- the cadence: the n-th completed exchange, nothing before --------------------------
    cad = bench.env("opcad", packages=("continuity",))
    blocks = _exchanges(cad, 4)
    opened = [_opens_operations(b) for b in blocks]
    if opened == [False, False, False, True]:
        held("OPERATIONS opens at the n-th completed exchange",
             "frequency 3 (the effort's preset): exchanges 1-3 silent, the 4th opens OPERATIONS at turn.end")
    else:
        failures.append(f"  ✗ operation cadence          {opened}")

    # --- the offer alive after the work, the record written ----------------------------------
    land = bench.env("opland", packages=("continuity",))
    record = land.made / ".sys" / "records" / "operations.jsonl"
    seen = {}

    def probe(n, block):
        if n != 4:
            return
        c = land.conductor("t")
        # ONE reader of what is offered: the offer map of the current output
        routed = c.route("pp-continuity")
        before = record.read_text(encoding="utf-8") if record.is_file() else ""
        rc, out, err = contributions.run_skill(
            land.made, "pp-continuity", ["register", "the consignation lands after the work"])
        after = record.read_text(encoding="utf-8") if record.is_file() else ""
        seen.update(shown=render(block), routed=routed, before=before, rc=rc, err=err,
                    lines=[json.loads(one) for one in after.splitlines() if one.strip()])

    _exchanges(land, 4, probe=probe)
    if (seen and "pp-continuity" in seen["shown"] and seen["routed"] is not None and seen["rc"] == 0
            and seen["before"] == "" and len(seen["lines"]) == 1
            and seen["lines"][0]["entry"] == "the consignation lands after the work"):
        held("the consignation lands from the block after the work",
             "the OPERATIONS block offers pp-continuity (routed on the fused output); `register` writes ONE dated line")
    else:
        failures.append(f"  ✗ consignation lands         routed={seen.get('routed') is not None} "
                        f"rc={seen.get('rc')} {str(seen.get('err', ''))[-80:]!r} lines={len(seen.get('lines', []))}")

    # --- the key at 0: never -------------------------------------------------------------------
    never = bench.env("opnever", packages=("continuity",))
    settings = never.read("SETTINGS.md")
    assert "continuity_memory_frequency: 3" in settings, settings[:200]
    never.write("SETTINGS.md", settings.replace("continuity_memory_frequency: 3", "continuity_memory_frequency: 0"))
    if not any(_opens_operations(b) for b in _exchanges(never, 4)):
        held("the key at 0 never opens OPERATIONS", "continuity_memory_frequency 0 (the bench's effort is none: the key rules): four exchanges, no block")
    else:
        failures.append("  ✗ key at 0                   OPERATIONS opened")

    # --- the kit alone: never, and no offer ----------------------------------------------------
    bare = bench.env("opkit")
    renders = [render(b) for b in _exchanges(bare, 4) if b is not None]
    if not any("OPERATIONS" in one or "pp-continuity" in one for one in renders):
        held("the kit alone consigns nothing", "four exchanges: no OPERATIONS block, no pp-continuity offer")
    else:
        failures.append("  ✗ kit alone                  OPERATIONS or pp-continuity appeared")

    # --- the order at the socket: topology then name, the instance's own last -----------------
    witness = bench.env("oporder", packages=("continuity",))
    witness.write("procs/ZWITNESS.md",
                  "---\nname: ZWITNESS\nkind: proc\ndescription: a witness attached at turn.end\n"
                  "attach: turn.end\noutput: line\nproc: |\n  WORK\n---\n\nZWITNESS says hi\n")
    compiling.build_tools(witness.made)
    order = instance.attached(witness.made, "turn.end")
    sequence = []

    def in_order(n, block):
        if n == 4:
            sequence.append(block.document)                     # the first contributor's own block
            sequence.append(witness.conductor("t").submit("").document)   # the next advance: the second

    _exchanges(witness, 4, probe=in_order)
    if order == ("OPERATIONS.md", "ZWITNESS.md") and sequence == ["OPERATIONS", "ZWITNESS"]:
        held("the order at turn.end is topology then name, the instance last",
             "continuity's OPERATIONS opens before the instance's ZWITNESS, each in its own output -- no rank declared anywhere")
    else:
        failures.append(f"  ✗ order at turn.end          {order} {sequence}")
    return 0
