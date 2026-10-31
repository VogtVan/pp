"""Scenario `qualifiers` -- the pattern `composition/qualifiers`, played from its demonstration:
- `when:` on a contributor guards it: false, the attached proc is not called, the mounted
  document does not enter, the document a host's `mounts:` names does not enter while an unguarded
  contributor at the same socket does; true, each plays
- the derived order at a socket: a package's contributor before the instance's, then by name
- `order: <socket> before <package>` on a contributor puts it before that package's contributors,
  and moves nothing else; two contributors that each want to come first refuse `order-cycle`
The package the order needs is written at the test's time: `crew` opens `yard.open`.
"""
from __future__ import annotations

from conductor import compiling
from tests.harness import codes, demonstrated, demos, plant, vendor

DRAWER, PATTERN = "composition", "qualifiers"
DEMOS = ("ATRIUM.md", "CANDLE.md", "CLERK.md", "EAGER.md", "GATEHOUSE.md", "LANTERN.md",
         "PORTER.md", "SWITCH.md", "WICK.md")
CREW = """name: crew
version: 0.0.1
description: a witness package that opens a socket of its own
requires: [kit]
contributes:
  sockets: [yard.open]
"""
YARD = """---
name: YARD
kind: proc
description: the package's host
proc: |
  HOOK yard.open
  INFER
---

the yard
"""
HAND = """---
name: HAND
kind: proc
description: the package's own contributor at its socket
attach: crew.yard.open
{order}proc: |
  INFER
---

the hand
"""
RIVAL = """name: rival
version: 0.0.1
description: a second witness package at the same socket
requires: [crew]
"""
RIVAL_DOC = """---
name: RIVAL
kind: proc
description: a contributor that wants to come first
attach: crew.yard.open
order: |
  crew.yard.open before crew
proc: |
  INFER
---

the rival
"""


def _played(env, floor, host: str, cap: int = 6) -> list[str]:
    """-> the documents of the blocks from the floor's opening to its own step."""
    block, seen = env.conductor().start(floor), []
    while block is not None and len(seen) < cap:
        seen.append(block.document)
        if block.document == host:
            break
        block = env.conductor().submit("")
    env.conductor().forget()
    return seen


def _switch(env, value: str) -> None:
    """SWITCH, planted, its `open:` field set to `value`."""
    text = (demos(DRAWER, PATTERN) / "SWITCH.md").read_text(encoding="utf-8")
    env.write("procs/SWITCH.md", text.replace("open: false", f"open: {value}"))


def guard(bench) -> None:
    """`when:` on an attached, a mounted and a host-named contributor."""
    held, failures = bench.held, bench.failures
    env = bench.env("qualifiers-guard", bare=True)
    plant(env, DRAWER, PATTERN, ("ATRIUM.md", "CANDLE.md", "GATEHOUSE.md", "LANTERN.md",
                                 "PORTER.md", "SWITCH.md", "WICK.md"))
    gatehouse, atrium = env.made / "procs" / "GATEHOUSE.md", env.made / "procs" / "ATRIUM.md"
    shut = _played(env, gatehouse, "GATEHOUSE")
    shut_gate = codes(env.conductor().start(gatehouse))
    env.conductor().forget()
    shut_atrium = codes(env.conductor().start(atrium))
    env.conductor().forget()
    if (shut == ["GATEHOUSE"] and "QL1" not in shut_gate and "QL2" not in shut_atrium
            and "QL3" in shut_atrium):
        held("a guard not due plays nothing", "SWITCH open: false -- PORTER is not called, LANTERN "
             "does not enter GATEHOUSE, CANDLE does not enter ATRIUM while the unguarded WICK does")
    else:
        failures.append(f"  ✗ the guard shut              played={shut} gate={shut_gate} atrium={shut_atrium}")
    _switch(env, "true")
    opened = _played(env, gatehouse, "GATEHOUSE")
    gate = env.conductor().start(gatehouse)
    open_gate = codes(gate)
    env.conductor().forget()
    open_atrium = codes(env.conductor().start(atrium))
    env.conductor().forget()
    if (opened == ["PORTER", "GATEHOUSE"] and gate.stack.startswith("GATEHOUSE ▸ PORTER{")
            and "QL1" in open_gate and "QL2" in open_atrium):
        held("a guard due plays", "SWITCH open: true -- PORTER is called in its frame, LANTERN's QL1 "
             "and CANDLE's QL2 enter")
    else:
        failures.append(f"  ✗ the guard open              played={opened} gate={open_gate} atrium={open_atrium}")


def order(bench) -> None:
    """The derived order, the preference that inverts it, the cycle that refuses."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("qualifiers-order", bare=True)
    vendor(env.made, "crew", CREW, {"YARD": YARD, "HAND": HAND.format(order="")})
    plant(env, DRAWER, PATTERN, ("CLERK.md",))
    compiling.build_tools(env.made)
    yard = env.made / ".sys" / "vendor" / "crew@0.0.1" / "procs" / "YARD.md"
    derived = _played(env, yard, "YARD")
    if derived == ["HAND", "CLERK", "YARD"]:
        held("the derived order", "at crew's yard.open, the package's HAND before the instance's "
             "CLERK, then YARD's own step")
    else:
        failures.append(f"  ✗ the derived order           {derived}")
    plant(env, DRAWER, PATTERN, ("EAGER.md",))
    compiling.build_tools(env.made)
    preferred = _played(env, yard, "YARD")
    if preferred == ["EAGER", "HAND", "CLERK", "YARD"]:
        held("a preference moves its declarant alone", "EAGER writes `crew.yard.open before crew` and plays "
             "before the package's HAND; CLERK, which writes nothing, keeps its rank after HAND")
    else:
        failures.append(f"  ✗ the preference              {preferred}")

    cycle = bench.env("qualifiers-cycle", bare=True)
    vendor(cycle.made, "crew", CREW, {"YARD": YARD, "HAND": HAND.format(
        order="order: |\n  crew.yard.open before rival\n")})
    vendor(cycle.made, "rival", RIVAL, {"RIVAL": RIVAL_DOC})
    compiling.build_tools(cycle.made)
    cycle_yard = cycle.made / ".sys" / "vendor" / "crew@0.0.1" / "procs" / "YARD.md"
    expect("order-cycle", lambda: cycle.conductor().start(cycle_yard))


def scenario(bench) -> int:
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        bench.failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    guard(bench)
    order(bench)
    return 0
