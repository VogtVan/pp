"""Scenario `doors` -- how a door opens, routes and closes:
- the offer lives with its OUTPUT: a multi-heading output numbers its segments, a single owner
  routes without a number, the number departages, a re-show keeps the addresses, a routed door
  stacks at the pending step, addresses live with their output, the author's § holds the offer
  at the seam
- `PP_DOOR` at `-new`: the door opens above the boot, an unknown door leaves nothing, the
  variable is ignored off `-new`
- a door's argument is said and traced
- the routed door takes the WORK with it
- the dispatch of a name: a proc opens conducted, the injected CALL never replays, the reflex
  renders no block, the catch does not lie, an unknown name gets the usage, a declared harness
  skill is offered, a declared name orients, the indifference invariant
"""
from __future__ import annotations

import re

from conductor import compiling, persistence, render, revive
from tests.harness import cli, session_of, steady, support

run = support(__file__, "run")

DOOR = ("---\nname: DOOR\nkind: proc\ndescription: a door\nconstraints.behavior: |\n"
        "  D1  the door law\nproc: |\n  INFER\n---\nthe door speaks\n")
RINNER = ("---\nname: RINNER\nkind: proc\ndescription: inner\nconstraints.behavior: |\n"
          "  I1  the inner law\ntools: |\n  note-taker\nproc: |\n  INFER\n---\ninner speaks\n")
ROUTER = ("---\nname: ROUTER\nkind: proc\ndescription: outer\nconstraints.behavior: |\n"
          "  O1  the outer law\ntools: |\n  DOOR\nproc: |\n  INFER\n  CALL RINNER.md\n"
          "  FINAL\n---\nspeak then call\n")
BARRED = ("---\nname: BARRED\nkind: proc\ndescription: strict order\ntools: |\n  DOOR\n"
          "proc: |\n  INFER\n  §\n  INFER\n  FINAL\n---\nspeak twice\n")

DAILY = ("---\nproc: |\n  WORK\n---\n# DAILY\n\n"
         "Say yesterday, today and blockers for this agent, then close the exchange.\n")
ROUTE = "---\nname: ROUTE\nkind: proc\ndescription: the root\noutput: any\nproc: |\n  INFER\n---\n\nSay the number.\n"
REVIEW = ("---\nname: REVIEW\nkind: proc\ndescription: a review said inside the turn\noutput: any\n"
          "proc: |\n  WORK\n---\n\nSay ONE line that reviews what the turn has done so far.\n")
OFFERING = "---\nname: TURN\ntools: |\n  +{name}\n---\n"


def _traces(env) -> int:
    """-> how many trace files the instance holds."""
    return len(list((env.made / persistence.DIRECTORY).glob("session-*.jsonl")))


def offers(bench) -> None:
    """The offer lives with its OUTPUT: the map of addresses, the route, the seam."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("rt", pin=False)
    rt_made = env.made

    def rt_c():
        return run.conductor_of(env, "t")

    env.write("DOOR.md", DOOR)
    env.write("RINNER.md", RINNER)
    env.write("ROUTER.md", ROUTER)
    routed_text = render(rt_c().start(rt_made / "ROUTER.md"))
    if ("▌ pp · run t · " in routed_text                # the output's heading says its key
            and "▌ [1] ROUTER{" in routed_text
            and "▌ [2] ROUTER ▸ RINNER{" in routed_text):
        held("a multi-heading output numbers its segments", "`[n]` on each heading -- "
             "the address a `-s` gesture routes by; a single-heading output stays bare")
    else:
        failures.append(f"  ✗ segment numbering           {routed_text.splitlines()[0]!r}")
    rt_hit = rt_c().route("note-taker")
    if (rt_hit is not None and rt_hit["ordinal"] == 2 and rt_hit["frame"] == "RINNER"
            and any(one.endswith("I1  the inner law") for one in rt_hit["constraints"])   # the wire form: the section rides the snapshot
            and rt_c().route("absent-name") is None):
        held("a single owner routes without a number", "the popped segment's own list "
             "answers -- scope PER SEGMENT, never a union; offered nowhere stays None")
    else:
        failures.append(f"  ✗ route single owner          {rt_hit!r}")
    expect("address-ambiguous", lambda: rt_c().route("DOOR"))
    rt_at = rt_c().route("DOOR", at=1)
    if rt_at is not None and rt_at["frame"] == "ROUTER":
        held("the number departages", "DOOR lives in [1] and inherited in [2] -- bare "
             "refuses naming both, `@1` settles it")
    else:
        failures.append(f"  ✗ route addressed             {rt_at!r}")
    rt_c().resume(rt_made / "ROUTER.md")
    if rt_c().route("note-taker") is not None:
        held("a re-show keeps the addresses", "resume replaces nothing -- the map lives "
             "with its output, not with the process")
    else:
        failures.append("  ✗ resume keeps map")
    rt_door = rt_c().play("DOOR", route=rt_c().route("note-taker"))
    rt_door_text = render(rt_door) if rt_door else ""
    rt_state = persistence.restore(persistence.slot_of(rt_made, "t"), revive)
    rt_call = next(one for one in rt_state[1].frames[0].procedure.instructions
                   if one.keyword == "CALL" and one.argument == "RINNER.md")
    if ("(routed from [2] RINNER)" in rt_door_text
            and re.search(r"\bI1\b", rt_door_text)   # the inherited law: its text, or its code under medium
            and rt_call.done):
        held("a routed door stacks at the pending step", "0 unwind -- the crossed CALL "
             "stays resolved; the door inherits the OWNING segment's snapshotted laws "
             "(the popped frame's own), and its entry heading says the route")
    else:
        failures.append(f"  ✗ routed door                 call_done={rt_call.done} "
                        f"{rt_door_text.splitlines()[:1]!r}")
    expect("address-stale", lambda: rt_c().route("note-taker", at=2))
    held("addresses live with their output", "the door rendered a fresh output: the old "
         "map is gone -- a kept number refuses by name, never lands elsewhere")

    barred_doc = env.write("BARRED.md", BARRED)
    rt_c().forget()
    barred = rt_c().start(barred_doc)
    rt_bar = rt_c().route("DOOR")
    if (barred is not None and "[1]" not in render(barred)
            and rt_bar is not None and rt_bar["ordinal"] == 1):
        held("the author's § holds the offer at the seam", "the output closes at the "
             "barrier and the offering step's own list answers the gesture there -- "
             "a single-heading output carries no number")
    else:
        failures.append(f"  ✗ barrier strict order        {rt_bar!r} "
                        f"{barred and render(barred)[:60]!r}")


def console_doors(bench) -> None:
    """The doors the console opens: `PP_DOOR` at `-new`, `-s <door> <arg>`, a door routed from
    the turn's WORK -- each case on its own run of one environment."""
    held, failures = bench.held, bench.failures
    env = bench.env("doors")
    env.write("procs/DAILY.md", DAILY)

    # --- the door opens above the boot ---------------------------------------------------------
    key, doored = run.opened(env, door="DAILY.md")
    door_lines = [one for one in run.trace(env, key) if one.get("kind") == "door"]
    if (doored.returncode == 0 and key and "▸ DAILY" in doored.stdout
            and len(door_lines) == 1 and door_lines[0].get("document") == "DAILY.md"):
        held("the door opens above the boot", f"PP_DOOR=DAILY.md at -new: the first output carries "
             f"DAILY, the trace says door (run {key})")
    else:
        failures.append(f"  ✗ door at -new                rc={doored.returncode} key={key!r} "
                        f"door_lines={door_lines} {doored.stdout[-300:]!r} {doored.stderr[-200:]!r}")

    # --- an unknown door leaves nothing --------------------------------------------------------
    slots_before, traces_before = len(persistence.slots(env.made)), _traces(env)
    _, unknown = run.opened(env, door="NOWHERE.md")
    if (unknown.returncode == 2 and "door-unknown" in unknown.stderr
            and len(persistence.slots(env.made)) == slots_before
            and _traces(env) == traces_before):
        held("an unknown door leaves nothing", "PP_DOOR=NOWHERE.md: door-unknown, exit 2, "
             "no slot and no trace beyond the standing run's")
    else:
        failures.append(f"  ✗ door unknown                rc={unknown.returncode} "
                        f"slots={len(persistence.slots(env.made))}/{slots_before} "
                        f"{unknown.stderr[-200:]!r}")

    # --- the variable is ignored off -new -------------------------------------------------------
    plain_key, plain = run.opened(env)
    keyed = cli(env.engine, plain_key, cwd=env.root, env={"PP_DOOR": "DAILY.md"})
    if (plain.returncode == 0 and plain_key and keyed.returncode in (0, 2)
            and "door" not in run.kinds(env, plain_key)):
        held("the variable is ignored off -new", "a keyed call under PP_DOOR stacks nothing: "
             "no door line in the run's trace")
    else:
        failures.append(f"  ✗ door off -new               rc={plain.returncode}/{keyed.returncode} "
                        f"{keyed.stdout[-150:]!r} {keyed.stderr[-150:]!r}")

    # --- a door's argument is said and traced ---------------------------------------------------
    env.write("procs/TURN.md", OFFERING.format(name="ROUTE"))
    env.write("procs/ROUTE.md", ROUTE)
    key, _ = run.opened(env, False, None, None, "the number is 7")
    door = env.cli(key, "-s", "ROUTE", "7")
    first = (door.stdout.splitlines() or [""])[0]
    traced = [one for one in run.trace(env, key) if one.get("kind") == "door-argument"]
    if (door.returncode == 0 and "▸ ROUTE" in door.stdout
            and first.startswith("pp:") and "7" in first.split()
            and traced and traced[0].get("arguments") == ["7"]):
        held("a door's argument is said and traced", "`-s ROUTE 7`: rc 0, the door opened, the first "
             "line is pp's and names the argument, the trace keeps `door-argument` with [\"7\"]")
    else:
        failures.append(f"  ✗ the argument                rc={door.returncode} {door.stdout[:120]!r} traced={traced}")

    # --- the routed door takes the WORK with it -------------------------------------------------
    env.write("procs/TURN.md", OFFERING.format(name="REVIEW"))
    env.write("procs/REVIEW.md", REVIEW)
    key, _ = run.opened(env, False, None, None, "say hello, then review")
    door = env.cli(key, "-s", "REVIEW")
    lines = [line for line in door.stdout.splitlines()
             if line.startswith(("WORK ", "INFER ")) and "=>" in line]
    after = env.cli(key)       # the door's line said: the bare call closes it, the door falls
    turn = next((one for one in run.slot(env, key).get("frames", [])
                 if one.get("document", "").endswith("TURN.md")), {})
    work = next((one for one in turn.get("instructions", []) if one.get("keyword") == "WORK"), {})
    if (door.returncode == 0 and "▸ REVIEW" in door.stdout and len(lines) == 1
            and lines[0].startswith("WORK any => response") and lines[0].endswith("(REVIEW)")
            and work.get("done") is True and "WORK any => response  (TURN)" not in after.stdout):
        held("the routed door takes the WORK with it", "one `WORK` line (REVIEW's) in the door's output, "
             "the TURN's WORK done at the slot, never asked again")
    else:
        failures.append(f"  ✗ the door                    rc={door.returncode} lines={lines} work={work.get('done')} "
                        f"after={[l for l in after.stdout.splitlines() if l.startswith('WORK ')]}")


def dispatch(bench) -> None:
    """The dispatch of a name on a member's turn: a proc, a skill, a stranger, a harness name."""
    held, failures = bench.held, bench.failures
    env = bench.env("ctx")
    made = env.made
    env.write("NOTE.md", "---\nname: NOTE\nkind: doc\ndescription: a reading of the member\n---\n\n"
                         "the note the member reads every session\n")
    env.write("procs/CAPS.md", "---\nname: CAPS\nkind: proc\ndescription: the member's brief\n"
                               "proc: |\n  INFER\n---\n\nthe witness's capabilities, asked once\n")
    env.write_member("serve: |\n  reference: NOTE.md\nconstraints.behavior: |\n"
                     "  A1  the agent's own law rides the block\n",
                     body="the witness agent", proc="SERVE\n  CALL CAPS.md", name="AGENT")

    def ctx():
        return run.conductor_of(env, None)

    def state() -> bytes:
        return session_of(made).read_bytes()

    booted = ctx()
    booted.resume(booted.boot("BOOT.md"))
    ctx().submit("")     # -> TURN stands, the base's offers alone

    # --- an UPPER name is a PROC, opened through pp -- conducted, scoped, purged ----------------
    env.write("procs/NOTE.md", "---\nname: NOTE\nkind: proc\ndescription: a scratch note, agent-opened\n"
                               "output: line\nproc: |\n  INFER\n---\njot the note down\n")
    env.write("procs/TURN.md",       # the overlay offers NOTE and arms a law of the turn's own:
              "---\nname: TURN\ntools: |\n  +NOTE\nconstraints.behavior: |\n"    # the stack carries it down
              "  +TB1  the turn's law rides every frame above it\n---\n")
    # an offer stands with the OUTPUT that carries it: the overlay written mid-exchange
    # reaches the screen and the router at the next advance, never before
    noted = [one.name for one in ctx().submit("").tools]
    seen_at_view = [one.name for one in ctx().peek().tools]
    note_offered, stranger_offered = "NOTE" in noted, "STRANGER" in noted
    opened = ctx().play("NOTE")
    if (note_offered and not stranger_offered and seen_at_view == noted
            and opened.document == "NOTE" and "▸ NOTE" in opened.stack
            and any(c.code == "TB1" for c in opened.constraints)):
        held("a proc opens conducted", "+NOTE offered by overlay -- the view shows the "
             "output's own list, and the proc plays STACKED over the turn, TB1 riding")
    else:
        failures.append(f"  ✗ play                        {note_offered}/{stranger_offered} "
                        f"{opened and opened.stack!r}")

    noted_back = ctx().submit("")
    replayed_clean = ctx().resume(ctx().boot("BOOT.md"))
    if (noted_back.document == "TURN" and not noted_back.wait
            and replayed_clean.document == "TURN"
            and "NOTE" not in replayed_clean.stack):
        held("the injected CALL never replays", "answered, the turn's own step returns; NOTE is purged clean")
    else:
        failures.append(f"  ✗ injected purge              {noted_back.document}/"
                        f"{replayed_clean.stack!r}")

    # --- the reflex IS the call: a LOCAL skill the member offers plays in one gesture; an
    # unoffered sibling proves the catch
    for name, line in (("pp-note", "nothing noted"), ("pp-hush", "hushed")):
        env.write(f"skills/{name}/SKILL.md", f"---\nname: {name}\ndescription: a local skill\n---\n\n{name}\n")
        env.write(f"skills/{name}/{name}.py",
                  f"def main(arguments):\n    print('{name}: {line}')\n    return 0\n")
    env.write("procs/TURN.md", "---\nname: TURN\ntools: |\n  +NOTE\n  +pp-note\n---\n")   # the offer lives
    compiling.build_tools(made)                                                              # with the step that stands
    ctx().forget()
    ctx().resume(ctx().boot("BOOT.md"))
    ctx().submit("")     # -> TURN stands: the member's pp-note offered
    before_reflex = state()
    reflex = env.cli("-s", "pp-note", "now")
    if (reflex.returncode == 0 and "pp ·" not in reflex.stdout
            and "pp-note: nothing noted" in reflex.stdout and state() == before_reflex):
        held("the reflex renders no block", "one scope in view: the skill's output alone, "
             "and the run does not move")
    else:
        failures.append(f"  ✗ dispatch gesture            rc={reflex.returncode} "
                        f"{reflex.stdout[:150]!r} {reflex.stderr[:80]!r}")

    frozen_catch = state()
    env.write("procs/HUSH.md",
              "---\nname: HUSH\nkind: proc\ndescription: an unoffered proc\nproc: |\n  INFER\n---\n\nhush\n")
    compiling.build_tools(made)
    denied = [env.cli("-s", "pp-hush", "now"), env.cli("-s", "HUSH")]
    if (all(one.returncode == 2 and "DEVIATION" in one.stdout and "REPAIR" not in one.stdout
            for one in denied)
            and state() == frozen_catch):
        held("the catch does not lie", "out of scope -- script or proc: rc 2, a DEVIATION "
             "section, no REPAIR heading, state byte-identical, nothing played")
    else:
        failures.append(f"  ✗ dispatch catch              rc={[one.returncode for one in denied]} "
                        f"{denied[0].stdout[:120]!r}")

    frozen_ghost = state()
    ghost = env.cli("frobnicate")
    if ghost.returncode != 0 and state() == frozen_ghost:
        held("an unknown name gets the usage", "nothing resolved, nothing played -- the run's state "
             "byte-identical")
    else:
        failures.append(f"  ✗ dispatch unknown            rc={ghost.returncode}")

    # --- declared harness names offered, the indifference invariant --------------------------
    env.write("procs/TURN.md", "---\nname: TURN\ntools: |\n  +NOTE\n  +brainstorm\n---\n")
    ctx().submit("")            # the offer stands with the output that carries it
    ghost_block = ctx().peek()
    ghost_tool = next((one for one in ghost_block.tools if one.name == "brainstorm"), None)
    if (ghost_tool is not None and ghost_tool.description == ""
            and "brainstorm" in render(ghost_block)):
        held("a declared harness skill is offered", "+name suffices -- name-only in the block, scoped like any tool")
    else:
        failures.append(f"  ✗ declared offered            {ghost_tool}")

    frozen_orient = state()
    oriented = env.cli("-s", "brainstorm")
    if (oriented.returncode == 0 and "▌" not in oriented.stdout
            and "REPAIR" not in oriented.stdout and state() == frozen_orient):
        held("a declared name orients", "pp has nothing to run -- the harness does: rc 0, no "
             "block, no REPAIR, the run unmoved")
    else:
        failures.append(f"  ✗ declared dispatch           rc={oriented.returncode} "
                        f"{oriented.stdout[:120]!r}")

    before_copy = steady(render(ctx().peek()))
    catalog_before = compiling.render_tools(made)
    harness_copy = env.root / ".claude" / "skills" / "turn"
    harness_copy.mkdir(parents=True, exist_ok=True)
    (harness_copy / "SKILL.md").write_text(
        next((made / ".sys" / "vendor").glob("kit@*/procs/TURN.md")).read_text(encoding="utf-8"),
        encoding="utf-8")
    if (steady(render(ctx().peek())) == before_copy
            and compiling.render_tools(made) == catalog_before):
        held("the indifference invariant", "a proc registered at the harness changes NOTHING for pp -- byte-identical")
    else:
        failures.append("  ✗ indifference                the harness copy leaked into pp")


def scenario(bench) -> int:
    offers(bench)
    console_doors(bench)
    dispatch(bench)
    return 0
