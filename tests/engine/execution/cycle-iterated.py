"""Scenario `cycle-iterated` -- 6 case(s) (batch le-cycle-qui-finit, 2026-09-09):
- three laps, each on its element, each proven under the door's law AND a mounted law
  (the mount standing at lap 3), then the exit: the door popped, the caller resumed
  with the last production
- the empty entry: no lap opens -- neither body nor step -- the line under the token
- a provider that refuses ends the cycle, its refusal said on the block that follows
- a token no document provides refuses `cycle-unprovided` at the opening
- `-compacted` on a lap in flight asks the token again and finds the same element
- the floor: an iterated door booted as the floor completes its run on the exit
"""
from __future__ import annotations

import json
from conductor import navigation, persistence, render, revive

SKILL = '''import sys
from pathlib import Path

ROOT = Path.cwd()


def due():
    done = set((ROOT / "laps.done").read_text().split()) if (ROOT / "laps.done").exists() else set()
    for line in (ROOT / "laps.txt").read_text().split():
        if line == "refuse":
            print("the list says refuse", file=sys.stderr)
            sys.exit(2)
        if line not in done:
            return line
    return None


if sys.argv[1:] == ["next"]:
    element = due()
    if element:
        print(element)
    sys.exit(0)
production = sys.stdin.read()
element = due()
if element and element in production:
    with open(ROOT / "laps.done", "a") as out:
        out.write(element + "\\n")
sys.exit(0)
'''


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("cycled")
    root = env.root
    env.write("skills/pp-laps/SKILL.md",
              "---\nname: pp-laps\ndescription: the bench's iterator -- what remains due, and the sink that consumes it\n---\n")
    env.write("skills/pp-laps/pp-laps.py", SKILL)
    env.write("procs/LAPS.md", "---\nname: LAPS\nkind: doc\nprovides: laps\nwith: pp-laps next\n---\n")
    env.write("procs/DOOR.md",
              "---\nname: DOOR\nkind: proc\ncycle: laps\nsink: pp-laps\nconstraints.production: |\n"
              "  D1  the lap's line names its element.\nproc: |\n  INFER\n---\none line per element\n")
    env.write("procs/RULE.md",
              "---\nname: RULE\nkind: doc\nconstraints.production: |\n"
              "  M1  the mounted law rides every lap.\n---\nmounted matter\n")
    env.write("procs/CALLER.md",
              "---\nname: CALLER\nkind: proc\nproc: |\n  CALL DOOR.md\n  INFER\n---\ncalls the door, then one more line\n")
    env.write("procs/ORPHAN.md",
              "---\nname: ORPHAN\nkind: proc\ncycle: nobody\nconstraints.production: |\n"
              "  O1  a law.\nproc: |\n  INFER\n---\nnobody provides\n")

    def key() -> str:
        return persistence.run_id_of(env.session())

    def trace() -> list[dict]:
        log = json.loads(env.session().read_text(encoding="utf-8"))["log"]
        lines = (env.made / ".sys" / "state" / log).read_text(encoding="utf-8").splitlines()
        return [json.loads(one) for one in lines if one.strip()]

    def proof(*codes: str) -> str:
        return json.dumps([{"code": code, "evidence": "held", "verdict": "ok"} for code in codes])

    def element_of(block) -> str:
        return dict(block.payloads).get("laps", "")

    def is_infer(block) -> bool:
        return (block is not None and block.instruction is not None
                and block.instruction.keyword == "INFER" and block.document == "DOOR")

    def is_prove(block) -> bool:
        return (block is not None and block.instruction is not None
                and block.instruction.keyword == "PROVE")

    # --- three laps on their element, proven under the door's law and a mounted law ----
    (root / "laps.txt").write_text("a\nb\nc\n", encoding="utf-8")
    (root / "laps.done").write_text("", encoding="utf-8")
    first = env.conductor()
    lap1 = first.start(first.boot("CALLER.md"))
    env.conductor(key()).mount([{"doc": "procs/RULE.md"}])
    lap1_shown = env.conductor(key()).peek()
    p1 = env.conductor(key()).submit("line a")
    lap2 = env.conductor(key()).submit(proof("D1", "M1"))
    p2 = env.conductor(key()).submit("line b")
    lap3 = env.conductor(key()).submit(proof("D1", "M1"))
    mounted_at_3 = persistence.mounted_of(env.session())
    p3 = env.conductor(key()).submit("line c")
    out = env.conductor(key()).submit(proof("D1", "M1"))
    laws3 = [one.code for one in lap3.constraints] if lap3 is not None else []
    proof_laws = [one.code for one in p3.constraints] if p3 is not None else []
    kinds = [one.get("kind") for one in trace()]
    stack = env.conductor(key())._rebind(persistence.restore(env.session(), revive))
    caller = navigation.current(stack)
    resumed = (out is not None and out.document == "CALLER" and "DOOR" not in out.stack
               and caller.procedure.instructions[1].taken == "line c")
    if (is_infer(lap1) and element_of(lap1) == "a" and "one line per element" in render(lap1)
            and "M1" in [one.code for one in lap1_shown.constraints]
            and is_prove(p1) and is_infer(lap2) and element_of(lap2) == "b"
            and is_prove(p2) and is_infer(lap3) and element_of(lap3) == "c"
            and "M1" in laws3 and "D1" in laws3 and mounted_at_3
            and is_prove(p3) and "M1" in proof_laws
            and resumed and kinds.count("lap") == 3 and kinds.count("cycle-done") == 1):
        held("three laps, each on its element, each proven, then the exit",
             "the door opens on `a`, proves under D1 and the mounted M1, rewinds on `b` and `c` "
             "with the mount standing, and leaves when the token renders nothing -- the caller "
             "resumes with `line c`, the trace says three laps and one cycle-done")
    else:
        failures.append(f"  ✗ three laps                  {is_infer(lap1)}/{element_of(lap1)!r}/"
                        f"{is_prove(p1)}/{element_of(lap2)!r}/{element_of(lap3)!r}/{laws3}/"
                        f"{bool(mounted_at_3)}/{proof_laws}/{resumed} kinds={kinds.count('lap')}"
                        f"/{kinds.count('cycle-done')} {out and out.stack!r}")

    # --- the empty entry: no lap opens, the line under the token ---------------------
    (root / "laps.done").write_text("a\nb\nc\n", encoding="utf-8")
    empty = env.conductor()
    empty.forget()
    closed = empty.start(empty.boot("CALLER.md"))
    said = dict(closed.payloads).get("laps", "") if closed is not None else ""
    if (closed is not None and closed.document == "CALLER" and "DOOR" not in closed.stack
            and "nothing due" in said and "one line per element" not in render(closed)
            and [one.get("kind") for one in trace()].count("lap") == 0):
        held("the empty entry opens no lap", "the token asked before the body renders nothing: "
             "neither body nor step, the CALL resolves and the line under the token says it")
    else:
        failures.append(f"  ✗ empty entry                 {closed and closed.stack!r} {said!r}")

    # --- a provider that refuses ends the cycle, its refusal said ---------------------
    (root / "laps.txt").write_text("refuse\n", encoding="utf-8")
    down = env.conductor()
    down.forget()
    broken = down.start(down.boot("CALLER.md"))
    said = dict(broken.payloads).get("laps", "") if broken is not None else ""
    if (broken is not None and "DOOR" not in broken.stack and "refused (2)" in said
            and "the list says refuse" in said
            and any(one.get("kind") == "cycle-done" and one.get("refused") for one in trace())):
        held("a provider that refuses ends the cycle", "no lap on a breakdown: the door does not "
             "open, the refusal is said under the token and the trace says why")
    else:
        failures.append(f"  ✗ provider refuses            {said!r}")

    # --- a token nobody provides refuses at the opening -------------------------------
    orphan = env.conductor()
    orphan.forget()
    expect("cycle-unprovided", lambda: orphan.start(orphan.boot("ORPHAN.md")))

    # --- -compacted on a lap in flight finds the same element -------------------------
    (root / "laps.txt").write_text("x\ny\n", encoding="utf-8")
    (root / "laps.done").write_text("", encoding="utf-8")
    flight = env.conductor()
    flight.forget()
    flight.start(flight.boot("CALLER.md"))
    env.conductor(key()).submit("line x")
    lap_y = env.conductor(key()).submit(proof("D1"))
    again = env.conductor(key()).compacted()
    if element_of(lap_y) == "y" and element_of(again) == "y" and "DOOR" in again.stack:
        held("the re-serve asks the token again", "a lap in flight on `y`: -compacted renders "
             "`y` under the token -- the request answers the same element, no cursor was kept")
    else:
        failures.append(f"  ✗ compacted lap               {element_of(lap_y)!r} {element_of(again)!r}")

    # --- the floor: an iterated door booted as the floor completes on the exit --------
    (root / "laps.txt").write_text("z\n", encoding="utf-8")
    (root / "laps.done").write_text("", encoding="utf-8")
    floor = env.conductor()
    floor.forget()
    opened = floor.start(floor.boot("DOOR.md"))
    env.conductor(key()).submit("line z")
    ended = env.conductor(key()).submit(proof("D1"))
    bare = env.conductor()
    bare.forget()
    (root / "laps.done").write_text("z\n", encoding="utf-8")
    never = bare.start(bare.boot("DOOR.md"))
    if (is_infer(opened) and element_of(opened) == "z"
            and ended is not None and ended.end and "DOOR" in ended.stack
            and never is not None and never.end and "nothing due" in dict(never.payloads).get("laps", "")):
        held("the floor door completes its run", "booted as the floor, the door plays its lap "
             "and the run completes when the token renders nothing; nothing due at the "
             "boot, the run completes at once")
    else:
        failures.append(f"  ✗ floor door                  {element_of(opened)!r} "
                        f"{ended and (ended.end, ended.stack)!r} {never and never.end!r}")
    env.conductor().forget()
    return 0
