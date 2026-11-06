"""Scenario `cycle` -- the pattern `control-flow/cycle`, played from its demonstration:
- three laps, each on the element its provider renders, each proven at the PROVE the door writes,
  under the door's law AND a mounted law (the mount standing at lap 3), then the exit -- the door
  popped, the caller resumed with the last production
- the empty entry opens no lap, the line under the token says it
- a provider that refuses ends the cycle, its refusal said under the token
- a token no document provides refuses `cycle-unprovided`
- `-compacted` on a lap in flight asks the token again and finds the same element
- booted as the floor, the door parks its run on the exit; nothing due at the boot, at once
- under the principal's conduction the laps play the same documents
"""
from __future__ import annotations

import json

from conductor import navigation, persistence, render, revive
from tests.harness import demonstrated, demos, plant, principal, traced

DEMOS = ("LAPS.md", "ORPHAN.md", "ROUNDS.md", "SWEEP.md")
TOKEN = "laps"                                        # the token SWEEP.md turns on
REFUSAL = "the list says refuse"
ITERATOR = '''import sys
from pathlib import Path

ROOT = Path.cwd()


def due():
    done = set((ROOT / "laps.done").read_text().split()) if (ROOT / "laps.done").exists() else set()
    for line in (ROOT / "laps.txt").read_text().split():
        if line == "refuse":
            print("%s", file=sys.stderr)
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
''' % REFUSAL


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("cycle", bare=True)
    found = demonstrated("control-flow", "cycle")
    if found != sorted(DEMOS):
        failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    plant(env, "control-flow", "cycle", DEMOS)
    sweep = (demos("control-flow", "cycle") / "SWEEP.md").read_text(encoding="utf-8")
    brief = sweep.split("---\n", 2)[2].strip()
    env.write("procs/SWEEP.md", sweep.replace(
        "kind: proc\n", "kind: proc\nconstraints.production: |\n  D1  a law of the door.\n", 1))
    env.write("procs/RULE.md", "---\nname: RULE\nkind: doc\nconstraints.production: |\n"
              "  M1  a law mounted for the passage.\n---\nmounted matter\n")
    env.write("skills/pp-laps/SKILL.md",
              "---\nname: pp-laps\ndescription: the bench's iterator -- what remains due, and the sink that consumes it\n---\n")
    env.write("skills/pp-laps/pp-laps.py", ITERATOR)
    root = env.root

    def key() -> str:
        return persistence.run_id_of(env.session())

    def proof(*codes: str) -> str:
        return json.dumps([{"code": code, "evidence": "held", "verdict": "ok"} for code in codes])

    def element_of(block) -> str:
        return dict(block.payloads).get(TOKEN, "") if block is not None else ""

    def is_step(block, keyword: str, document: str = "SWEEP") -> bool:
        return (block is not None and block.instruction is not None
                and block.instruction.keyword == keyword and block.document == document)

    def due(elements: str, done: str = "") -> None:
        (root / "laps.txt").write_text(elements, encoding="utf-8")
        (root / "laps.done").write_text(done, encoding="utf-8")

    def fresh(document: str):
        conductor = env.conductor()
        conductor.forget()
        return conductor.start(conductor.boot(document))

    # --- three laps on their element, proven under the door's law and a mounted law -------------
    due("a\nb\nc\n")
    lap1 = fresh("ROUNDS.md")
    env.conductor(key()).mount([{"doc": "procs/RULE.md"}])
    lap1_shown = env.conductor(key()).peek()
    p1 = env.conductor(key()).submit("line a")
    lap2 = env.conductor(key()).submit(proof("D1", "M1"))
    p2 = env.conductor(key()).submit("line b")
    lap3 = env.conductor(key()).submit(proof("D1", "M1"))
    mounted_at_3 = persistence.mounted_of(env.session())
    p3 = env.conductor(key()).submit("line c")
    out = env.conductor(key()).submit(proof("D1", "M1"))
    llm_path = [one.document if one is not None else "" for one in (lap1, p1, lap2, p2, lap3, p3, out)]
    laws3 = [one.code for one in lap3.constraints] if lap3 is not None else []
    proof_laws = [one.code for one in p3.constraints] if p3 is not None else []
    kinds = [one.get("kind") for one in traced(env, key())]
    caller = navigation.current(env.conductor(key())._rebind(persistence.restore(env.session(), revive)))
    resumed = (out is not None and out.document == "ROUNDS" and "SWEEP" not in out.stack
               and caller.procedure.instructions[1].taken == "line c")
    if (is_step(lap1, "INFER") and element_of(lap1) == "a" and brief in render(lap1)
            and "M1" in [one.code for one in lap1_shown.constraints]
            and is_step(p1, "PROVE") and is_step(lap2, "INFER") and element_of(lap2) == "b"
            and is_step(p2, "PROVE") and is_step(lap3, "INFER") and element_of(lap3) == "c"
            and "M1" in laws3 and "D1" in laws3 and mounted_at_3
            and is_step(p3, "PROVE") and "M1" in proof_laws
            and resumed and kinds.count("lap") == 3 and kinds.count("cycle-done") == 1):
        held("three laps, each on its element, each proven, then the exit",
             "the door opens on `a`, proves under D1 and the mounted M1, rewinds on `b` and `c` with "
             "the mount standing, and leaves when the token renders nothing -- the caller resumes "
             "with `line c`, the trace says three laps and one cycle-done")
    else:
        failures.append(f"  ✗ three laps                  {llm_path} {element_of(lap1)!r}/{element_of(lap2)!r}/"
                        f"{element_of(lap3)!r} {laws3} {bool(mounted_at_3)} {proof_laws} {resumed} "
                        f"kinds={kinds.count('lap')}/{kinds.count('cycle-done')}")

    # --- the empty entry: no lap opens, the line under the token --------------------------------
    due("a\nb\nc\n", "a\nb\nc\n")
    closed = fresh("ROUNDS.md")
    said = element_of(closed)
    if (closed is not None and closed.document == "ROUNDS" and "SWEEP" not in closed.stack
            and "nothing due" in said and brief not in render(closed)
            and [one.get("kind") for one in traced(env, key())].count("lap") == 0):
        held("the empty entry opens no lap", "the token asked before the body renders nothing: "
             "neither body nor step, the CALL resolves and the line under the token says it")
    else:
        failures.append(f"  ✗ empty entry                 {closed and closed.stack!r} {said!r}")

    # --- a provider that refuses ends the cycle, its refusal said -------------------------------
    due("refuse\n")
    broken = fresh("ROUNDS.md")
    said = element_of(broken)
    if (broken is not None and "SWEEP" not in broken.stack and "refused (2)" in said and REFUSAL in said
            and any(one.get("kind") == "cycle-done" and one.get("refused") for one in traced(env, key()))):
        held("a provider that refuses ends the cycle", "no lap on a breakdown: the door does not open, "
             "the refusal is said under the token and the trace says why")
    else:
        failures.append(f"  ✗ provider refuses            {said!r}")

    # --- a token nobody provides refuses at the opening -----------------------------------------
    orphan = env.conductor()
    orphan.forget()
    expect("cycle-unprovided", lambda: orphan.start(orphan.boot("ORPHAN.md")))

    # --- -compacted on a lap in flight finds the same element -----------------------------------
    due("x\ny\n")
    fresh("ROUNDS.md")
    env.conductor(key()).submit("line x")
    lap_y = env.conductor(key()).submit(proof("D1"))
    again = env.conductor(key()).compacted()
    if element_of(lap_y) == "y" and element_of(again) == "y" and "SWEEP" in again.stack:
        held("the re-serve asks the token again", "a lap in flight on `y`: -compacted renders `y` "
             "under the token -- the request answers the same element, no cursor was kept")
    else:
        failures.append(f"  ✗ compacted lap               {element_of(lap_y)!r} {element_of(again)!r}")

    # --- the floor: the door booted as the root parks its run on the exit ----------------------
    due("z\n")
    opened = fresh("SWEEP.md")
    env.conductor(key()).submit("line z")
    ended = env.conductor(key()).submit(proof("D1"))
    due("z\n", "z\n")
    never = fresh("SWEEP.md")
    if (is_step(opened, "INFER") and element_of(opened) == "z"
            and ended is not None and ended.wait and "SWEEP" in ended.stack
            and never is not None and never.wait and "nothing due" in element_of(never)):
        held("the floor door parks its run", "booted as the root, the door plays its lap and the run "
             "parks when the token renders nothing; nothing due at the boot, the run parks at once")
    else:
        failures.append(f"  ✗ floor door                  {element_of(opened)!r} "
                        f"{ended and (ended.wait, ended.stack)!r} {never and never.wait!r}")
    env.conductor().forget()

    # --- the principal's conduction: the same laps, the same documents --------------------------
    due("a\nb\nc\n")
    led = env.conductor()
    led.forget()
    steps = [principal(lambda: led.start(led.boot("ROUNDS.md")))]
    led_key = led.run_id
    for answer in ("line a", proof("D1"), "line b", proof("D1"), "line c", proof("D1")):
        steps.append(principal(lambda answer=answer: env.conductor(led_key).submit(answer)))
    led_path = [one.document if one is not None else "" for one in steps]
    if led_path == llm_path and element_of(steps[2]) == "b":
        held("both conductions turn the same laps", f"under the principal's conduction: {led_path}")
    else:
        failures.append(f"  ✗ the principal's laps        {led_path} -- owed {llm_path}")
    env.conductor(led_key).forget()
    return 0
