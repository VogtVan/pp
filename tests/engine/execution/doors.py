"""Scenario `doors` -- the door a launcher opens and the names a script answers to:
- `PP_DOOR` at `-new`: the door opens above the boot, an unknown door leaves nothing, the
  variable is ignored off `-new`
- the dispatch of a script's name: the reflex renders no block, the catch does not lie, an
  unknown name gets the usage
The offer, the route, the door's argument and the WORK it takes are the pattern
`composition/door`; the harness's names are `composition/adoption`.
"""
from __future__ import annotations

from conductor import compiling, persistence
from tests.harness import cli, session_of, support

run = support(__file__, "run")

DAILY = ("---\nproc: |\n  WORK\n---\n# DAILY\n\n"
         "Say yesterday, today and blockers for this agent, then close the exchange.\n")


def _traces(env) -> int:
    """-> how many trace files the instance holds."""
    return len(list((env.made / persistence.DIRECTORY).glob("session-*.jsonl")))


def console_doors(bench) -> None:
    """The door a launcher opens: `PP_DOOR` at `-new` -- each case on its own run of one
    environment."""
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


def dispatch(bench) -> None:
    """The dispatch of a script's name on a member's turn: the reflex, the catch, a stranger."""
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

    # --- the reflex IS the call: a LOCAL skill the member offers plays in one gesture; an
    # unoffered sibling proves the catch
    for name, line in (("pp-note", "nothing noted"), ("pp-hush", "hushed")):
        env.write(f"skills/{name}/SKILL.md", f"---\nname: {name}\ndescription: a local skill\n---\n\n{name}\n")
        env.write(f"skills/{name}/{name}.py",
                  f"def main(arguments):\n    print('{name}: {line}')\n    return 0\n")
    env.write("procs/TURN.md", "---\nname: TURN\ntools: |\n  +pp-note\n---\n")   # the offer lives
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


def scenario(bench) -> int:
    console_doors(bench)
    dispatch(bench)
    return 0
