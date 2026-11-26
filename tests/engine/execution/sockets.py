"""Scenario `sockets` -- what the sockets serve and where they cut:
- the turn's sockets are declared by the base, HOOKed by TURN, said by the catalog and inert
  without a contributor
- the cut at the turn's end belongs to the contributor that needs it: the WORK's output ends on
  the WORK, pending; with nothing at `turn.end` the principal's bare call after its print parks the
  run on AWAIT alone; a pass opening on `§` at `turn.end` keeps the cut, its socket's scripted
  reading computed after the work, never before
- a proc that imports: an overlay of TURN imports HOUSE -- it enters at TURN's entry, before the
  contributors of `turn.initialize`, held by TURN's frame and naming it; its laws at the park and at
  the next exchange, its body served once, nothing mounted again, served back after a compaction
- a refused advance writes nothing: a contributor at a socket whose import no document answers
  refuses `mount-missing` and leaves the slot byte for byte as the call found it -- mid-passage (the
  step the call resolved stands again, the next call replays it) and at the opening of a parked
  run (the run stays parked, the next messages refuse the same way); the cause lifted, the next
  message opens the exchange on its first step as the ask, no deviation, the trace keeping every
  refusal
The call at a HOOK, the mount, the entry socket, the guard and the order are the patterns
`composition/hook`, `mount`, `initialize` and `qualifiers`; a contributor's payload and its body
are `context/payload`.
"""
from __future__ import annotations

import json
import os
import re

from conductor import contributions, instance, persistence, render
from tests.harness import agents, cli, codes, na_proof, printed, traced, vendor

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
HOUSE = """---
name: HOUSE
kind: doc
description: the laws the overlay of TURN mounts at the turn's beginning
constraints.behavior: |
  HS1  say where you stand first.
constraints.production: |
  HP1  every measure comes with its unit.
---

The house.
"""
NOTE = """---
name: PASS
kind: doc
description: the note the overlay of TURN mounts at the turn's end
constraints.behavior: |
  PS1  close on one line.
---

The pass.
"""
BADGE = """---
name: BADGE
kind: doc
description: mounted at TURN's entry, after what TURN imports
mount: turn.initialize
constraints.production: |
  BG1  every answer carries the badge.
---

The badge of the entry.
"""
HOUSE_BODY = "The house of the imports: one charter, read once."
TURN_IMPORTS = """---
name: TURN
imports: |
  HOUSE.md
---
"""
HEAD = """---
name: HEAD
kind: doc
description: mounted at the turn's beginning, with the house it imports
mount: turn.begin
imports: |
  HOUSE.md
---

The head of the turn.
"""
TAIL = """---
name: TAIL
kind: doc
description: mounted at the turn's end, with the note it imports
mount: turn.end
imports: |
  PASS.md
---

The tail of the turn.
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
    """The cut at the turn's end: AWAIT alone with nothing at `turn.end`, the pass's reading after the work."""
    held, failures = bench.held, bench.failures

    # --- nothing at turn.end: the principal's call after the WORK's print parks the run ----
    env = bench.env("floor-alone", pin=False)
    _roomy(env)
    env.write("procs/FLOOR.md", FLOOR)
    env.cli("-build")
    shown = render(env.conductor("t").start(env.made / "procs" / "FLOOR.md"))   # the floor is the ROOT
    parked = printed(env, "t") or env.conductor("t").submit("")                 # the WORK printed, the bare call
    ended = render(parked) if parked is not None else ""
    if (_closing(shown) == [] and "FLOOR{2/3}" in shown
            and parked is not None and parked.wait and _closing(ended) == ["▶ AWAIT"]):
        held("an empty turn's end parks on AWAIT", "the WORK's output ends on the WORK, no closing; the "
             "principal's bare call after its print parks the run, AWAIT alone")
    else:
        failures.append(f"  ✗ floor alone                  {_closing(shown)} {_closing(ended)}")

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
    if built.returncode == 0 and found and _closing(opened.stdout) == [] and runs() == 0 \
            and "witness-stamp" not in opened.stdout:
        held("the pass's leading § holds the cut", "the WORK's output ends on the WORK; the "
             "script of the pass's socket has not run")
    else:
        failures.append(f"  ✗ pass cut                     rc={built.returncode} {_closing(opened.stdout)} "
                        f"runs={runs()} {(opened.stderr or built.stderr)[-160:]!r}")
        return
    key = found.group(1)
    said = cli(env.engine, key, "-print", "FLOOR", "-", cwd=env.root, env={**at, **agents(key)},
               stdin="said\n")                                  # the agent's print of the work
    advanced = cli(env.engine, key, cwd=env.root, env=at)       # the principal's bare call
    rendered = said.stdout + advanced.stdout
    if ("INFORMATION — witness-stamp" in rendered and f"{STAMPED}1" in rendered
            and runs() == 1 and "THR" in rendered):
        held("the socket's reading comes after the work", "the work printed, the principal's call renders the "
             "pass with the reading its script computed then, once")
    else:
        failures.append(f"  ✗ pass reading                 runs={runs()} {_closing(advanced.stdout)} "
                        f"{said.stdout[-120:]!r} {advanced.stderr[-160:]!r}")


def turn_imports(bench) -> None:
    """TURN imports HOUSE: at its entry, before `turn.initialize`'s contributors, held by its frame."""
    held, failures = bench.held, bench.failures
    env = bench.env("turn-imports")
    _roomy(env)
    env.write("procs/HOUSE.md", HOUSE.replace("The house.", HOUSE_BODY))
    env.write("procs/BADGE.md", BADGE)
    env.write("procs/TURN.md", TURN_IMPORTS)
    built = env.cli("-build")
    opener = env.conductor()
    first = opener.start(opener.boot("BOOT.md"), "the first ask")
    key = opener.run_id
    slot = persistence.slot_of(env.made, key)
    view = lambda: [(one["doc"], one.get("import", ""), one.get("held", ""))   # noqa: E731
                    for one in persistence.mounted_of(slot)]
    mounted = lambda: [one.get("docs") for one in traced(env, key) if one.get("kind") == "mounted"]  # noqa: E731
    entry = view()
    laws = codes(first)
    if (built.returncode == 0 and entry == [("HOUSE.md", "TURN.md", "1:TURN"), ("BADGE.md", "", "1:TURN")]
            and all(one in laws for one in ("HS1", "HP1", "BG1")) and laws.index("HP1") < laws.index("BG1")
            and HOUSE_BODY in render(first) and mounted() == [["HOUSE.md"], ["BADGE.md"]]):
        held("a proc's imports enter first", "TURN's overlay imports HOUSE: it enters at TURN's entry before "
             "BADGE, both held by 1:TURN, HOUSE naming TURN, its body served")
    else:
        failures.append(f"  ✗ the turn's import            rc={built.returncode} view={entry} {laws} "
                        f"mounted={mounted()} {built.stderr[-160:]!r}")
        return
    proving = printed(env, key)
    parked = env.conductor(key).submit(na_proof(proving)) if proving is not None and proving.judged else proving
    at_park = codes(env.conductor(key).peek())
    again = env.conductor(key).forward("the second ask")
    if (parked is not None and parked.wait and "HP1" in at_park and "BG1" in at_park
            and "HP1" in codes(again) and HOUSE_BODY not in render(again)
            and view() == entry and len(mounted()) == 2):
        held("the frame holds its imports", "HP1 and BG1 at the park and at the next exchange, HOUSE's body "
             "not served again, the view as the entry left it, nothing mounted again")
    else:
        failures.append(f"  ✗ the held import              parked={parked and parked.wait} {at_park} "
                        f"{codes(again)} view={view()} mounted={mounted()}")
    restored = {subject: text for subject, text in env.conductor(key).compacted().payloads}
    if any(HOUSE_BODY in text for text in restored.values()) and "HOUSE" in restored:
        held("a held import comes back after a compaction", "`-compacted`: HOUSE's body rides the re-serve, "
             "the frame still holding it")
    else:
        failures.append(f"  ✗ the import compacted         payloads: {sorted(restored)}")


def _state(raw: bytes) -> dict:
    """-> a slot's state, the latched signals apart: the refusal motor latches a code refused
    twice from the console's note of the refusal, outside the call that refused."""
    state = json.loads(raw.decode("utf-8"))
    state.pop("signals", None)
    return state


def _standing(block) -> tuple:
    """-> what a standing block says of the run: its stack, whether it waits, its step, its codes."""
    return (block.stack, block.wait, block.instruction.keyword, codes(block))


def refused_advance(bench) -> None:
    """A refused advance writes nothing: the slot as the call found it, the block that stood,
    the next message the ask once the cause is lifted."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("refused-advance")
    env.write("procs/HOUSE.md", HOUSE)
    env.write("procs/PASS.md", NOTE)
    env.write("procs/HEAD.md", HEAD)
    env.write("procs/TAIL.md", TAIL)
    env.cli("-build")
    opener = env.conductor()
    first = opener.start(opener.boot("BOOT.md"), "the first ask")
    key = opener.run_id
    slot = persistence.slot_of(env.made, key)
    if not (first.instruction.keyword == "WORK" and "HP1" in codes(first) and not first.wait):
        failures.append(f"  ✗ the head imports             {first.stack!r} {codes(first)}")
        return
    conductor = lambda: env.conductor(key)   # noqa: E731

    # --- a refusal in the middle of an advance: the step resolved stands again ------------
    (env.made / "procs" / "PASS.md").unlink()
    before = slot.read_bytes()
    stood = _standing(conductor().peek())
    expect("mount-missing", lambda: conductor().printed(first.document, "said"))
    after = slot.read_bytes()
    standing = _standing(conductor().peek())
    if after == before and standing == stood and standing[2] == "WORK":
        held("a refusal mid-advance writes nothing", "the WORK resolved by the call stands again, "
             "the slot byte for byte as before")
    else:
        failures.append(f"  ✗ mid-advance refusal          same={after == before} {standing!r} vs {stood!r}")
    env.write("procs/PASS.md", NOTE)
    proving = printed(env, key)                  # the WORK handed: the run moves to the proof
    if proving is None or not proving.judged:
        failures.append(f"  ✗ the next call replays        {proving and proving.stack!r}")
        return
    parked = conductor().submit(na_proof(proving))
    if not parked.wait:
        failures.append(f"  ✗ the passage parks            {parked.stack!r}")
        return

    # --- a refusal at the opening of a parked run: the run stays parked ------------------
    (env.made / "procs" / "HOUSE.md").unlink()
    before = slot.read_bytes()
    stood = _standing(conductor().peek())
    refused = env.cli(key, "suite")
    after = slot.read_bytes()
    standing = _standing(conductor().peek())
    if (refused.returncode == 2 and "mount-missing" in refused.stderr and after == before
            and standing == stood and standing[1]):
        held("a refused opening leaves the run parked", "the message refuses `mount-missing`, "
             "the view renders the closing that parked the run, the slot byte for byte as before")
    else:
        failures.append(f"  ✗ refused opening              rc={refused.returncode} same={after == before} "
                        f"{standing!r} vs {stood!r} {refused.stderr[-160:]!r}")
    again = [env.cli(key), env.cli(key, "encore")]
    if (all(one.returncode == 2 and "mount-missing" in one.stderr for one in again)
            and _state(slot.read_bytes()) == _state(before)
            and _standing(conductor().peek()) == stood):
        held("every call refuses the same way", "the bare call and the next message refuse "
             "`mount-missing`; the state stands, the signals of the refusal motor apart")
    else:
        failures.append(f"  ✗ refused again                rc={[one.returncode for one in again]} "
                        f"{_standing(conductor().peek())!r}")

    # --- the cause lifted: the next message opens the exchange, its text the ask ----------
    env.write("procs/HOUSE.md", HOUSE)
    reopened = conductor().forward("retour")
    events = [json.loads(line) for line in
              (slot.parent / json.loads(slot.read_text(encoding="utf-8"))["log"])
              .read_text(encoding="utf-8").splitlines() if line.strip()]
    prompts = [at for at, one in enumerate(events) if one.get("kind") == "prompt"]
    refusals = [one.get("code") for one in events if one.get("kind") == "refusal"]
    since = events[prompts[-1]:] if prompts else []
    mounted = [one for one in since if one.get("kind") == "mounted"]
    if (reopened.instruction.keyword == "WORK" and not reopened.deviation and not reopened.wait
            and "HP1" in codes(reopened) and since and since[0].get("text") == "retour"
            and len(mounted) == 1 and mounted[0].get("docs") == ["HOUSE.md", "HEAD.md"]
            and refusals == ["mount-missing"] * 3
            and persistence.turns_of(slot) == 1):
        held("the next message opens the exchange", "its text traced as the prompt, the turn on its "
             "first step without deviation, HOUSE and HEAD mounted once, the three refusals kept in the trace")
    else:
        failures.append(f"  ✗ reopened exchange            {reopened.stack!r} dev={reopened.deviation!r} "
                        f"prompt={since[:1]!r} mounted={len(mounted)} refusals={refusals} "
                        f"turns={persistence.turns_of(slot)}")


def scenario(bench) -> int:
    turn_sockets(bench)
    turn_end_cut(bench)
    turn_imports(bench)
    refused_advance(bench)
    return 0
