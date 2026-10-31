"""Scenario `door` -- the pattern `composition/door`, played from its demonstration:
- the offer lives with its output: a multi-heading output numbers its segments, a name one segment
  offers opens without a number, a name two segments offer refuses `address-ambiguous` and `@n`
  settles it, a re-show keeps the addresses, a routed door stacks at the pending step under the
  owning segment's laws, a fresh output retires the old addresses (`address-stale`), the author's
  `§` holds the offer at the seam
- an offered proc opens conducted: stacked over the step that offers it, the offering frame's law
  riding; answered, the passage ends, and the next passage carries no trace of it
- a door's argument is said and traced
- a routed door takes the step's WORK with it -- under both conductions
The offers of the turn are carried by the demonstration's overlay of TURN, placed by the test.
"""
from __future__ import annotations

import json
import re

from conductor import persistence, render, revive
from tests.harness import PRINCIPAL, cli, codes, demonstrated, demos, law, plant, traced

DRAWER, PATTERN = "composition", "door"
DEMO = demos(DRAWER, PATTERN)
DEMOS = ("BARRED.md", "DOOR.md", "NOTE.md", "NOTETAKER.md", "REVIEW.md", "RINNER.md", "ROUTE.md",
         "ROUTER.md", "TURN.offer.md")
KEY = re.compile(r"run ([0-9a-f]{6})")


def _offer(env) -> None:
    """The demonstration's overlay of TURN, placed at its base's name."""
    env.write("procs/TURN.md", (DEMO / "TURN.offer.md").read_text(encoding="utf-8"))


def _opened(env, message: str, marked: bool = False) -> str:
    """-> the key of a run opened by `-new` on `message`, under the principal's mark when asked."""
    out = cli(env.engine, "-new", message, cwd=env.root, env={PRINCIPAL: "true"} if marked else None)
    found = KEY.search(out.stdout)
    return found.group(1) if found else ""


def _slot(env, key: str) -> dict:
    path = persistence.slot_of(env.made, key)
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def offers(bench) -> None:
    """The map of addresses an output carries, the route, the seam."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("door", pin=False)
    plant(env, DRAWER, PATTERN, ("BARRED.md", "DOOR.md", "NOTETAKER.md", "RINNER.md", "ROUTER.md"))
    router = env.made / "procs" / "ROUTER.md"

    def c():
        return env.conductor("t")

    shown = render(c().start(router))
    if "▌ pp · run t · " in shown and "▌ [1] ROUTER{" in shown and "▌ [2] ROUTER ▸ RINNER{" in shown:
        held("a multi-heading output numbers its segments", "`[1]` ROUTER, `[2]` ROUTER ▸ RINNER, "
             "the output's heading saying its key")
    else:
        failures.append(f"  ✗ the segments                {shown.splitlines()[:3]!r}")
    inner_law = law(DRAWER, PATTERN, "RINNER.md", "I1")
    hit = c().route("NOTETAKER")
    if (hit is not None and hit["ordinal"] == 2 and hit["frame"] == "RINNER"
            and any(one.endswith(inner_law) for one in hit["constraints"]) and c().route("ABSENT") is None):
        held("a single owner routes without a number", "NOTETAKER, offered by [2] alone, routes to RINNER "
             "under its law I1; a name offered nowhere routes nowhere")
    else:
        failures.append(f"  ✗ the single owner            {hit!r}")
    expect("address-ambiguous", lambda: c().route("DOOR"))
    settled = c().route("DOOR", at=1)
    if settled is not None and settled["frame"] == "ROUTER":
        held("the number settles it", "DOOR is offered by [1] and inherited by [2]: bare it refuses, "
             "`@1` routes to ROUTER")
    else:
        failures.append(f"  ✗ the addressed route         {settled!r}")
    c().resume(router)
    if c().route("NOTETAKER") is not None:
        held("a re-show keeps the addresses", "the map lives with its output, not with the call")
    else:
        failures.append("  ✗ the re-show                 the map is gone")
    door = c().play("NOTETAKER", route=c().route("NOTETAKER"))
    door_text = render(door) if door is not None else ""
    state = persistence.restore(persistence.slot_of(env.made, "t"), revive)
    crossed = next(one for one in state[1].frames[0].procedure.instructions
                   if one.keyword == "CALL" and one.argument == "RINNER.md")
    if "(routed from [2] RINNER)" in door_text and re.search(r"\bI1\b", door_text) and crossed.done:
        held("a routed door stacks at the pending step", "NOTETAKER opens under RINNER's laws, its "
             "heading saying the route; the CALL it crossed stays resolved")
    else:
        failures.append(f"  ✗ the routed door             done={crossed.done} codes={codes(door)} "
                        f"routed={'(routed from [2] RINNER)' in door_text} {door_text[:400]!r}")
    expect("address-stale", lambda: c().route("NOTETAKER", at=2))
    c().forget()

    barred = c().start(env.made / "procs" / "BARRED.md")
    at_seam = c().route("DOOR")
    if barred is not None and "[1]" not in render(barred) and at_seam is not None and at_seam["ordinal"] == 1:
        held("the author's § holds the offer at the seam", "BARRED closes at its `§`: one heading, "
             "no number, DOOR routed by the offering step's own list")
    else:
        failures.append(f"  ✗ the seam                    {at_seam!r}")
    c().forget()


def conducted(bench) -> None:
    """An offered proc opens conducted over the turn, and leaves nothing to the next passage."""
    held, failures = bench.held, bench.failures
    env = bench.env("door-conducted")
    plant(env, DRAWER, PATTERN, ("NOTE.md", "REVIEW.md", "ROUTE.md"))
    env.write_member()                              # the boot opens on the member's step

    opener = env.conductor()
    opener.start(opener.boot("BOOT.md"))
    key = opener.run_id
    _offer(env)                                     # written mid-exchange: it reaches the next output
    turn = env.conductor(key).submit("")
    view = env.conductor(key).peek()
    offered = [one.name for one in turn.tools] if turn is not None else []
    opened = env.conductor(key).play("NOTE")
    if ("NOTE" in offered and [one.name for one in view.tools] == offered
            and opened is not None and opened.document == "NOTE"
            and "▸ NOTE" in opened.stack and "TB1" in codes(opened)):
        held("an offered proc opens conducted", "the overlay written mid-exchange reaches TURN's next output, "
             "the view showing that output's own list; NOTE plays stacked over the turn, TB1 riding")
    else:
        failures.append(f"  ✗ the conducted door          {offered} "
                        f"{opened and opened.stack!r}")
    block = env.conductor(key).submit("")
    while block is not None and not block.wait:
        block = env.conductor(key).submit("[]" if block.judged else "")
    reopened = env.conductor(key).submit("the next message")
    if (block is not None and block.wait and reopened is not None and reopened.document == "TURN"
            and "NOTE" not in reopened.stack):
        held("the injected CALL never replays", "NOTE answered, the passage ends and parks; the next "
             "message reopens TURN with no NOTE in its stack")
    else:
        failures.append(f"  ✗ the purge                   {block and block.wait!r} {reopened and reopened.stack!r}")
    env.conductor(key).forget()


def console(bench) -> None:
    """The argument of a door, the WORK a routed door takes -- under both conductions."""
    held, failures = bench.held, bench.failures
    env = bench.env("door-console")
    plant(env, DRAWER, PATTERN, ("NOTE.md", "REVIEW.md", "ROUTE.md"))
    _offer(env)

    key = _opened(env, "the number is 7")
    door = env.cli(key, "-s", "ROUTE", "7")
    first = (door.stdout.splitlines() or [""])[0]
    said = [one for one in traced(env, key) if one.get("kind") == "door-argument"]
    if (door.returncode == 0 and "▸ ROUTE" in door.stdout and first.startswith("pp:")
            and "7" in first.split() and said and said[0].get("arguments") == ["7"]):
        held("a door's argument is said and traced", "`-s ROUTE 7`: ROUTE opens, pp's first line names "
             "the argument, the trace keeps `door-argument` with [\"7\"]")
    else:
        failures.append(f"  ✗ the argument                rc={door.returncode} {door.stdout[:120]!r} {said}")

    for label, marked in (("LLM", False), ("principal", True)):
        mark = {PRINCIPAL: "true"} if marked else None
        key = _opened(env, "say hello, then review", marked)
        door = cli(env.engine, key, "-s", "REVIEW", cwd=env.root, env=mark)
        lines = [line for line in door.stdout.splitlines()
                 if line.startswith(("WORK ", "INFER ")) and "=>" in line]
        after = cli(env.engine, key, cwd=env.root, env=mark)
        turn = next((one for one in _slot(env, key).get("frames", [])
                     if one.get("document", "").endswith("TURN.md")), {})
        work = next((one for one in turn.get("instructions", []) if one.get("keyword") == "WORK"), {})
        if (door.returncode == 0 and "▸ REVIEW" in door.stdout and len(lines) == 1
                and lines[0].startswith("WORK ") and lines[0].endswith("(REVIEW)")
                and work.get("done") is True and "(TURN)" not in " ".join(
                    one for one in after.stdout.splitlines() if one.startswith("WORK "))):
            held(f"the routed door takes the WORK ({label})", "REVIEW's WORK is the one line of the door's "
                 "output, the turn's WORK done at the slot and never asked again")
        else:
            failures.append(f"  ✗ the WORK taken ({label})      rc={door.returncode} {lines} {work.get('done')}")


def scenario(bench) -> int:
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        bench.failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    offers(bench)
    conducted(bench)
    console(bench)
    return 0
