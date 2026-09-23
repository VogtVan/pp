"""Scenario `turn-positions` -- 2 case(s) (plan pp-split, batch le-turn-sans-opinion):
- the bare kit turn goes WORK to FINAL: no block at an empty position, no NEXT table
- a neutral witness at each position plays in order: begin before the work, end after it
"""
from __future__ import annotations

from conductor import compiling, render
from tests.harness import na_proof

NOTE = """---
name: {name}
kind: proc
description: a witness of the {socket} position
attach: {socket}
proc: |
  HOOK {lower}.read
---

{name} says hi
"""


def _drive(env, opening, cap: int = 8) -> list:
    """Advance to the frontier: WORK's production is ephemeral, a checkpoint takes
    the bench's n/a proof -- the submits carry the whole turn."""
    seen = [opening]
    while (seen[-1] is not None and "▶ FINAL" not in render(seen[-1]) and len(seen) < cap):
        last = seen[-1]
        seen.append(env.conductor("t").submit(
            na_proof(last) if "INFER proof" in render(last) else ""))
    return [one for one in seen if one is not None]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- the bare kit turn: WORK to FINAL, nothing at the empty positions -------------
    bare = bench.env("turn-bare")
    opener = bare.conductor("t")
    seen = _drive(bare, opener.start(opener.boot("TURN.md")))
    texts = [render(one) for one in seen]
    if (seen and seen[0].document == "TURN" and seen[0].instruction.keyword == "WORK"
            and "▶ FINAL" in texts[-1]
            and all(one.document == "TURN" for one in seen)
            and all("says hi" not in text for text in texts)
            and all("| thread" not in text and "NEXT" not in one.stack
                    for one, text in zip(seen, texts))):
        held("the bare turn goes WORK to FINAL", "empty positions render no block, "
             "no NEXT table rides the closing")
    else:
        failures.append(f"  ✗ bare turn                    {[one.stack for one in seen]!r}")

    # --- a neutral witness at each position: begin before the work, end after it ------
    heard = bench.env("turn-heard")
    heard.write("procs/BEGIN.md", NOTE.format(name="BEGIN", socket="turn.begin", lower="begin"))
    heard.write("procs/END.md", NOTE.format(name="END", socket="turn.end", lower="end"))
    compiling.build_tools(heard.made)
    opener = heard.conductor("t")
    seen = _drive(heard, opener.start(opener.boot("TURN.md")))
    texts = [render(one) for one in seen]
    stream = "\n".join(texts)
    at_work = next((i for i, one in enumerate(seen)
                    if one.instruction is not None and one.instruction.keyword == "WORK"), None)
    at_begin = next((i for i, text in enumerate(texts) if "BEGIN says hi" in text), None)
    at_end = next((i for i, text in enumerate(texts) if "END says hi" in text), None)
    if (at_work is not None and at_begin is not None and at_end is not None
            and at_begin <= at_work < at_end and "▶ FINAL" in texts[-1]
            and stream.find("BEGIN says hi") < stream.find("END says hi")):
        held("the positions carry their witnesses", "BEGIN plays before the work, "
             "END after it, the frontier still closes")
    else:
        failures.append(f"  ✗ witnessed turn               begin={at_begin} work={at_work} "
                        f"end={at_end}")
    return 0
