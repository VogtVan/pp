"""Scenario `door` -- the pattern `composition/door`, played from its demonstration:
- the offer lives with its output: a multi-heading output numbers its segments, a name one segment
  offers opens without a number, a name two segments offer refuses `address-ambiguous` and `@n`
  settles it, a re-show keeps the addresses, a routed door stacks at the pending step under the
  owning segment's laws, a fresh output retires the old addresses (`address-stale`), the author's
  `§` holds the offer at the seam
- a fused segment offers what each of its steps offers: three steps of two documents under one law read in
  one segment, a name the inner step offers routes at the pending step of the outer one, the map's entry
  naming the last step the output asked with its frame; a view shows that step again with the output's
  offers; `@1` routes, `@2` refuses `address-stale`; a door addressed to a segment plays under that
  segment's laws
- the step asked is shown again in its own frame: an output opened by a step of one document closes at the `§`
  of the document it calls; a view shows that document's step, at its position, never the caller's
- an offered proc opens conducted: stacked over the step that offers it, the offering frame's law
  riding; answered, the passage ends, and the next passage carries no trace of it
- a door's argument is said and traced
- a routed door takes the step's WORK with it
The offers of the turn are carried by the demonstration's overlay of TURN, placed by the test.
"""
from __future__ import annotations

import json
import re

from conductor.core import messages
from conductor import persistence, render, revive
from conductor.core import language
from tests.harness import cli, codes, demonstrated, demos, law, plant, stepped, titles, traced

DRAWER, PATTERN = "composition", "door"
DEMO = demos(DRAWER, PATTERN)
DEMOS = ("BARRED.md", "DOOR.md", "LOBBY.md", "NOTE.md", "NOTETAKER.md", "PORCH.md", "REVIEW.md", "RINNER.md",
         "ROUTE.md", "ROUTER.md", "TURN.offer.md")
KEY = re.compile(r"run ([0-9a-f]{6})")
MARK = f"{messages.MARK} "
# written at the test's time: a caller whose callee closes the output at its `§`, under the same laws
HALLWAY = ("---\nname: HALLWAY\nkind: proc\ndescription: speaks, then calls the nook\nproc: |\n"
           "  INFER\n  CALL NOOK.md\n---\n\nSay where the hallway leads.\n")
NOOK = ("---\nname: NOOK\nkind: proc\ndescription: two steps cut by a section break\nproc: |\n"
        "  INFER\n  §\n  INFER\n---\n\nSay what the nook holds.\n")


def _segments(shown: str) -> list[str]:
    """-> the headings of a rendering's segments: its marked lines that open no section of the engine's list."""
    return [one for one in titles(shown)
            if one.startswith(MARK) and not language.section_of(one.removeprefix(MARK))[0]]


def _asked(shown: str) -> list[str]:
    """-> the document each step line of a rendering names, in order."""
    return [one.rsplit("(", 1)[-1].rstrip(")") for one in shown.splitlines()
            if one.startswith(("INFER ", "WORK ", "PICK ")) and one.endswith(")")]


def _offer(env) -> None:
    """The demonstration's overlay of TURN, placed at its base's name."""
    env.write("procs/TURN.md", (DEMO / "TURN.offer.md").read_text(encoding="utf-8"))


def _opened(env, message: str) -> str:
    """-> the key of a run opened by `-new` on `message`."""
    out = cli(env.engine, "-new", message, cwd=env.root)
    found = KEY.search(out.stdout)
    return found.group(1) if found else ""


def _slot(env, key: str) -> dict:
    path = persistence.slot_of(env.made, key)
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def offers(bench) -> None:
    """The map of addresses an output carries, the route, the seam."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("door", pin=False)
    plant(env, DRAWER, PATTERN, ("BARRED.md", "DOOR.md", "LOBBY.md", "NOTETAKER.md", "PORCH.md", "RINNER.md",
                                 "ROUTER.md"))
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

    # --- a door addressed to a segment plays under that segment's laws ---------------------------
    ridden = []
    for at in (1, 2):
        c().start(router)
        door = c().play("DOOR", route=c().route("DOOR", at=at))
        text = render(door) if door is not None else ""
        ridden.append((text.count(f"(routed from [{at}] "), [code for code in ("O1", "I1", "D1")
                                                              if re.search(rf"\b{code}\b", text)]))
        c().forget()
    if ridden == [(1, ["O1", "D1"]), (1, ["O1", "I1", "D1"])]:
        held("an addressed door plays under its segment's laws", "DOOR@1 opens under ROUTER's O1 and its own "
             "D1, DOOR@2 under RINNER's I1 too; each heading says the segment it was routed from")
    else:
        failures.append(f"  ✗ the addressed door          {ridden!r}")

    # --- a fused segment offers what each of its steps offers --------------------------------------
    fused = render(c().start(env.made / "procs" / "LOBBY.md"))
    entry = c().route("NOTETAKER")
    view = c().peek()
    if (len(_segments(fused)) == 1 and _asked(fused) == ["LOBBY", "PORCH", "LOBBY"]
            and entry is not None and (entry["ordinal"], entry["frame"], entry["at"]) == (1, "LOBBY", 3)
            and view is not None and (view.document, view.position) == ("LOBBY", 3)
            and "NOTETAKER" in [one.name for one in view.tools]):
        held("a fused segment offers what its steps offer", f"LOBBY's two steps and PORCH's under "
             f"`{_segments(fused)[0]}`; NOTETAKER, offered by PORCH's step, routes at LOBBY's step 3, the "
             "last step the output asked; the view shows that step again with the output's offers")
    else:
        failures.append(f"  ✗ the fused segment           {_segments(fused)} {_asked(fused)} {entry!r} "
                        f"view={view and (view.document, view.position, [one.name for one in view.tools])!r}")
    expect("address-stale", lambda: c().route("NOTETAKER", at=2))
    through = c().play("NOTETAKER", route=c().route("NOTETAKER", at=1))
    through_text = render(through) if through is not None else ""
    heads = _segments(through_text)
    if (len(heads) == 1 and "LOBBY ▸ NOTETAKER" in heads[0] and "(routed from [1] LOBBY)" in heads[0]
            and re.search(r"\bL1\b", through_text)):
        held("`@1` routes on the segment that remains", "NOTETAKER@1 opens over LOBBY under L1, its heading "
             "saying the route; `@2` names no segment of the output")
    else:
        failures.append(f"  ✗ the address on a fused segment {heads} {through_text[:300]!r}")
    c().forget()

    # --- the step asked is shown again, in the frame that asked it ----------------------------------
    env.write("procs/HALLWAY.md", HALLWAY)
    env.write("procs/NOOK.md", NOOK)
    broken = render(c().start(env.made / "procs" / "HALLWAY.md"))
    kept = (persistence.segments_of(persistence.slot_of(env.made, "t")) or [{}])[-1]
    shown = c().peek()
    if (len(_segments(broken)) == 1 and "HALLWAY{" in _segments(broken)[0] and _asked(broken) == ["HALLWAY", "NOOK"]
            and (kept.get("frame"), kept.get("at")) == ("NOOK", 1)
            and shown is not None and (shown.document, shown.position, shown.total) == ("NOOK", 1, 2)
            and shown.command.startswith("INFER") and "NOOK{1/2}" in shown.stack):
        held("the step asked is shown again in its own frame", f"`{_segments(broken)[0]}` opens the output, "
             "NOOK's first step closes it at the `§`: the map's entry names NOOK at 1, and the view shows "
             f"`{shown.stack}` with its step -- never the caller's frame, never the step behind the `§`")
    else:
        failures.append(f"  ✗ the step asked, another frame {_segments(broken)} {_asked(broken)} "
                        f"kept={(kept.get('frame'), kept.get('at'))} "
                        f"view={shown and (shown.document, shown.position, shown.command, shown.stack)!r}")
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
    turn = stepped(lambda: env.conductor(key))     # the boot's lines printed, then the turn's output
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
    block = stepped(lambda: env.conductor(key))
    for _ in range(12):                              # bounded: a run that stops moving fails the case, never loops
        if block is None or block.wait:
            break
        block = stepped(lambda: env.conductor(key), "[]" if block.judged else "")
    reopened = env.conductor(key).submit("the next message")
    if (block is not None and block.wait and reopened is not None and reopened.document == "TURN"
            and "NOTE" not in reopened.stack):
        held("the injected CALL never replays", "NOTE answered, the passage ends and parks; the next "
             "message reopens TURN with no NOTE in its stack")
    else:
        failures.append(f"  ✗ the purge                   {block and block.wait!r} {reopened and reopened.stack!r}")
    env.conductor(key).forget()


def console(bench) -> None:
    """The argument of a door, the WORK a routed door takes."""
    held, failures = bench.held, bench.failures
    env = bench.env("door-console")
    plant(env, DRAWER, PATTERN, ("NOTE.md", "REVIEW.md", "ROUTE.md"))
    _offer(env)

    key = _opened(env, "the number is 7")
    door = env.cli(key, "-s", "ROUTE", "7")
    first = (door.stdout.splitlines() or [""])[0]
    said = [one for one in traced(env, key) if one.get("kind") == "door-argument"]
    if (door.returncode == 0 and "▸ ROUTE" in door.stdout and first == messages.argument_ignored("7")
            and said and said[0].get("arguments") == ["7"]):
        held("a door's argument is said and traced", "`-s ROUTE 7`: ROUTE opens, pp's first line names "
             "the argument, the trace keeps `door-argument` with [\"7\"]")
    else:
        failures.append(f"  ✗ the argument                rc={door.returncode} {door.stdout[:120]!r} {said}")

    key = _opened(env, "say hello, then review")
    door = cli(env.engine, key, "-s", "REVIEW", cwd=env.root)
    lines = [line for line in door.stdout.splitlines()
             if line.startswith(("WORK ", "INFER ")) and "=>" in line]
    after = None
    for document in env.conductor(key).prints_due():   # the door's WORK printed first: it moves the run
        after = cli(env.engine, key, "-print", document, "-", cwd=env.root, stdin="reviewed")
    if after is None or not after.stdout.strip() or after.stdout.startswith("pp: "):
        after = cli(env.engine, key, cwd=env.root)
    turn = next((one for one in _slot(env, key).get("frames", [])
                 if one.get("document", "").endswith("TURN.md")), {})
    work = next((one for one in turn.get("instructions", []) if one.get("keyword") == "WORK"), {})
    if (door.returncode == 0 and "▸ REVIEW" in door.stdout and len(lines) == 1
            and lines[0].startswith("WORK ") and lines[0].endswith("(REVIEW)")
            and work.get("done") is True and "(TURN)" not in " ".join(
                one for one in after.stdout.splitlines() if one.startswith("WORK "))):
        held("the routed door takes the WORK", "REVIEW's WORK is the one line of the door's "
             "output, the turn's WORK done at the slot and never asked again")
    else:
        failures.append(f"  ✗ the WORK taken              rc={door.returncode} {lines} {work.get('done')}")


def scenario(bench) -> int:
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        bench.failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    offers(bench)
    conducted(bench)
    console(bench)
    return 0
