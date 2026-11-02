"""Scenario `sockets` -- what the sockets serve and where they cut:
- the turn's sockets are declared by the base, HOOKed by TURN, said by the catalog and inert
  without a contributor
- the cut at the turn's end belongs to the contributor that needs it: a floor with nothing at
  `turn.end` closes the WORK's output on AWAIT; a pass opening on `§` at `turn.end` keeps the
  cut, its socket's scripted reading computed at the advance, after the work
The call at a HOOK, the mount, the entry socket, the guard and the order are the patterns
`composition/hook`, `mount`, `initialize` and `qualifiers`; a contributor's payload and its body
are `context/payload`.
"""
from __future__ import annotations

import os
import re

from conductor import contributions, instance, render
from tests.harness import cli, vendor

SAYS = "{name} says hi"
PASS = """name: witness
version: 0.0.1
description: a package whose pass plays after the work, on its own socket
requires: [kit]
contributes:
  sockets: [thr.begin]
"""
THR = """---
name: THR
kind: proc
description: the pass -- opens on a section break, hooks its own socket, then works
attach: turn.end
proc: |
  §
  HOOK thr.begin
  WORK
---

THR: the pass.
"""
STAMP = """---
name: STAMP
kind: doc
description: a reading on the pass's socket, computed by a script that counts its runs
mount: witness.thr.begin
provides: witness-stamp
with: pp-witness-stamp now
payloads: witness-stamp
---

STAMP says how many times its script ran.
"""
STAMPED = "stamp #"
STAMP_SKILL = """#!/usr/bin/env python3
import os
p = os.environ["STAMP_FILE"]
n = sum(1 for _ in open(p)) + 1 if os.path.exists(p) else 1
open(p, "a").write(f"run {n}\\n")
print(f"%s{n}")
""" % STAMPED
FLOOR = """---
name: FLOOR
kind: proc
description: the floor -- the two sockets around the WORK, no section break
output: any
proc: |
  HOOK turn.begin
  WORK
  HOOK turn.end
---

the floor: answer the ask.
"""


def _boot_block(env):
    opener = env.conductor()
    return opener.start(opener.boot("BOOT.md"))


def _boot(env) -> str:
    return render(_boot_block(env))


def _roomy(env) -> None:
    """The boot serves the standing orders in the block: a cap at the host's default would
    cut it, and a chunk closes on its own CONTINUE -- a case that reads the WHOLE output
    raises the cap; the fusion stays the instance's (max)."""
    settings = env.made / "SETTINGS.md"
    settings.write_text(settings.read_text(encoding="utf-8").replace(
        "max_harness_tool_output: 25000", "max_harness_tool_output: 200000"), encoding="utf-8")


def _closing(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.startswith("▶")]


def turn_sockets(bench) -> None:
    """The turn's sockets stand inert."""
    held, failures = bench.held, bench.failures
    bare = bench.env("bare-turn")
    boot_bare = _boot(bare)
    turn = instance.resolve(bare.made, "TURN.md").read_text(encoding="utf-8")
    declared = next((one for one in contributions.composed(bare.made)
                     if one["kind"] == "sockets" and one["package"] == "kit"), {})
    sockets = [str(one) for one in declared.get("value") or []]
    catalog = (bare.made / ".sys" / "tools.md").read_text(encoding="utf-8")
    said = next((line.split(":", 1)[1].strip().split(", ") for line in catalog.splitlines()
                 if line.startswith("- **`kit`** sockets:")), [])
    if ({"turn.begin", "turn.end"} <= set(sockets) and said == sockets
            and all(f"HOOK {one}" in turn for one in ("turn.begin", "turn.end"))
            and SAYS.format(name="").strip() not in boot_bare):
        held("the turn's sockets stand inert", "the base declares them, TURN hooks begin and end, "
             "the catalog says them, a bare instance plays no contributor")
    else:
        failures.append(f"  ✗ turn sockets                 declared={sockets} said={said} "
                        "-- missing in TURN or leaking into a bare boot")


def turn_end_cut(bench) -> None:
    """The cut at the turn's end: AWAIT with nothing at `turn.end`, CONTINUE under a pass."""
    held, failures = bench.held, bench.failures

    # --- nothing at turn.end: the WORK's output closes on AWAIT --------------------------
    env = bench.env("floor-alone", pin=False)
    _roomy(env)
    env.write("procs/FLOOR.md", FLOOR)
    env.cli("-build")
    shown = render(env.conductor("t").start(env.made / "procs" / "FLOOR.md"))   # the floor is the ROOT
    if _closing(shown) == ["▶ AWAIT"] and "FLOOR{2/3}" in shown:
        held("an empty turn's end closes on AWAIT", "one output: the WORK's block, the parked closing at "
             "its foot, no bare call to play")
    else:
        failures.append(f"  ✗ floor alone                  {_closing(shown)}")

    # --- a pass opening on § keeps the cut; its socket's reading comes after the work ----
    env = bench.env("floor-pass", pin=False)
    _roomy(env)
    vendor(env.made, "witness", PASS, {"THR": THR, "STAMP": STAMP}, {"pp-witness-stamp": STAMP_SKILL})
    env.write("procs/FLOOR.md", FLOOR)
    built = env.cli("-build")
    stamp = str(env.made.parent / "stamps.txt")
    at = {"PP_DOOR": "FLOOR.md", "STAMP_FILE": stamp}
    opened = cli(env.engine, "-new", cwd=env.root, env=at)
    found = re.search(r"run (\w{6})", opened.stdout)
    runs = lambda: open(stamp).read().count("\n") if os.path.exists(stamp) else 0  # noqa: E731
    if built.returncode == 0 and found and "▶ CONTINUE" in _closing(opened.stdout) and runs() == 0 \
            and "witness-stamp" not in opened.stdout:
        held("the pass's leading § holds the cut", "the WORK's output closes on CONTINUE; the "
             "script of the pass's socket has not run")
    else:
        failures.append(f"  ✗ pass cut                     rc={built.returncode} {_closing(opened.stdout)} "
                        f"runs={runs()} {(opened.stderr or built.stderr)[-160:]!r}")
        return
    advanced = cli(env.engine, found.group(1), cwd=env.root, env=at)
    if ("INFORMATION — witness-stamp" in advanced.stdout and f"{STAMPED}1" in advanced.stdout
            and runs() == 1 and "THR" in advanced.stdout):
        held("the socket's reading comes after the work", "the advance renders the pass with the "
             "reading its script computed then, once")
    else:
        failures.append(f"  ✗ pass reading                 runs={runs()} {_closing(advanced.stdout)} "
                        f"{advanced.stderr[-160:]!r}")


def scenario(bench) -> int:
    turn_sockets(bench)
    turn_end_cut(bench)
    return 0
