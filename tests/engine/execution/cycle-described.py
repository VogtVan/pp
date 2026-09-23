"""Scenario `cycle-described` -- 9 case(s) (batch le-field-declaratif, 2026-09-22):
- the described door: two lines of front matter, no skill -- the FIELD step served with
  the prose as its brief (`@Doc.field` resolved), the agent's array accepted, three laps
  each on its element under `field`, each proven, then the exit; no `provider` line
- an empty array: nothing due, no lap opens, the line under `field` says it
- the FORM alone is judged: not JSON, not an array, a twin, an empty element, a non-scalar
  each repair with the miss named -- an array of integers passes like an array of paths
- the head stays: two looks at the standing block, the frame's field unchanged
- `-compacted` on a lap in flight re-serves the head, the slot carries the field
- a `@Doc.field` that resolves to nothing refuses `field-argument-empty`
- the floor: a described door booted as the floor completes its run; empty, at once
- the trace: `lap` per lap, one `cycle-done`, the ledger's origin `cycle` under `field`
- the build and the parse refuse by name: cycle-and-field, field-empty, field-unplayable,
  field-keyword
- the weight: the lap block of a described door beside a provided door's, same instance
"""
from __future__ import annotations

import json
from conductor import compiling, navigation, persistence, render, revive

SKILL = '''import sys
if sys.argv[1:] == ["next"]:
    print("alpha")
sys.exit(0)
'''


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("described")
    env.write("LIST.md", "---\nname: LIST\nkind: doc\nitems: alpha beta gamma\n---\n")
    env.write("procs/DOOR.md",
              "---\nname: DOOR\nkind: proc\nfield: |\n  The words of @LIST.items, one lap each.\n"
              "constraints.production: |\n  D1  the lap's line names its element.\n"
              "proc: |\n  INFER\n---\none line per element\n")
    env.write("procs/CALLER.md",
              "---\nname: CALLER\nkind: proc\nproc: |\n  CALL DOOR.md\n  INFER\n---\ncalls the door, then one more line\n")
    env.write("procs/HOLLOW.md",
              "---\nname: HOLLOW\nkind: proc\nfield: |\n  Everything under @LIST.absent.\n"
              "proc: |\n  INFER\n---\nnothing resolves\n")
    env.write("procs/CALLHOLLOW.md",
              "---\nname: CALLHOLLOW\nkind: proc\nproc: |\n  CALL HOLLOW.md\n  INFER\n---\ncalls the hollow door\n")
    # the provided twin -- the same door, its iterator a skill -- for the weight beside
    env.write("skills/pp-laps/SKILL.md",
              "---\nname: pp-laps\ndescription: the bench's iterator -- one element, always due\n---\n")
    env.write("skills/pp-laps/pp-laps.py", SKILL)
    env.write("procs/LAPS.md", "---\nname: LAPS\nkind: doc\nprovides: laps\nwith: pp-laps next\n---\n")
    env.write("procs/TWIN.md",
              "---\nname: TWIN\nkind: proc\ncycle: laps\nconstraints.production: |\n"
              "  D1  the lap's line names its element.\nproc: |\n  INFER\n---\none line per element\n")

    def key() -> str:
        return persistence.run_id_of(env.session())

    def trace() -> list[dict]:
        log = json.loads(env.session().read_text(encoding="utf-8"))["log"]
        lines = (env.made / ".sys" / "state" / log).read_text(encoding="utf-8").splitlines()
        return [json.loads(one) for one in lines if one.strip()]

    def proof(*codes: str) -> str:
        return json.dumps([{"code": code, "evidence": "held", "verdict": "ok"} for code in codes])

    def field_of(block) -> str:
        return dict(block.payloads).get("field", "") if block is not None else ""

    def is_field(block) -> bool:
        return (block is not None and block.instruction is not None
                and block.instruction.keyword == "FIELD" and block.document == "DOOR")

    def is_infer(block, name: str = "DOOR") -> bool:
        return (block is not None and block.instruction is not None
                and block.instruction.keyword == "INFER" and block.document == name)

    def is_prove(block) -> bool:
        return (block is not None and block.instruction is not None
                and block.instruction.keyword == "PROVE")

    def door_field() -> list | None:
        stack = env.conductor(key())._rebind(persistence.restore(env.session(), revive))
        for frame in stack.frames:
            if frame.document.name == "DOOR":
                return frame.field
        return None

    def fresh(document: str):
        conductor = env.conductor()
        conductor.forget()
        return conductor.start(conductor.boot(document))

    # --- the described door: prose served, array accepted, three laps, the exit -------
    ask = fresh("CALLER.md")
    shown = render(ask) if ask is not None else ""
    lap1 = env.conductor(key()).submit('["alpha", "beta", "gamma"]')
    p1 = env.conductor(key()).forward("")     # the lap speaks chat: the bare call closes it
    lap2 = env.conductor(key()).submit(proof("D1"))
    p2 = env.conductor(key()).forward("")
    lap3 = env.conductor(key()).submit(proof("D1"))
    p3 = env.conductor(key()).forward("")
    out = env.conductor(key()).submit(proof("D1"))
    kinds = [one.get("kind") for one in trace()]
    stack = env.conductor(key())._rebind(persistence.restore(env.session(), revive))
    caller = navigation.current(stack)
    resumed = (out is not None and out.document == "CALLER" and "DOOR" not in out.stack
               and caller.document.name == "CALLER")
    brief_ok = ("alpha beta gamma" in field_of(ask) and "@LIST" not in field_of(ask)
                and "NEXT INSTRUCTION CONTEXT — field" in shown and "INFER field => tool (heredoc)" in shown
                and "(your field on stdin" in shown)
    if (is_field(ask) and brief_ok
            and is_infer(lap1) and field_of(lap1) == "alpha" and is_prove(p1)
            and is_infer(lap2) and field_of(lap2) == "beta" and is_prove(p2)
            and is_infer(lap3) and field_of(lap3) == "gamma" and is_prove(p3)
            and resumed and kinds.count("lap") == 3 and kinds.count("cycle-done") == 1
            and kinds.count("provider") == 0):
        held("the described door turns on its prose, no skill",
             "the FIELD step serves the prose with `@LIST.items` resolved as `INFER field => tool "
             "(heredoc)`; the array accepted, the door opens on `alpha`, proves, rewinds on `beta` and "
             "`gamma`, and leaves when nothing remains -- three laps, one cycle-done, not one provider line")
    else:
        failures.append(f"  ✗ described door              field={is_field(ask)} brief={brief_ok} "
                        f"{field_of(lap1)!r}/{field_of(lap2)!r}/{field_of(lap3)!r} resumed={resumed} "
                        f"kinds={kinds.count('lap')}/{kinds.count('cycle-done')}/{kinds.count('provider')}")

    # --- an empty array: nothing due, no lap opens ----------------------------------
    fresh("CALLER.md")
    closed = env.conductor(key()).submit("[]")
    if (closed is not None and closed.document == "CALLER" and "DOOR" not in closed.stack
            and "nothing due" in field_of(closed)
            and [one.get("kind") for one in trace()].count("lap") == 0):
        held("an empty array opens no lap", "nothing due: neither body step nor lap, the CALL "
             "resolves and the line under `field` says it")
    else:
        failures.append(f"  ✗ empty array                 {closed and closed.stack!r} {field_of(closed)!r}")

    # --- the FORM alone is judged, never the nature ---------------------------------
    faults = [("not json", "not one valid JSON value"), ('{"a": 1}', "not a JSON array"),
              ('["a", "a"]', "appears twice"), ('["a", ""]', "is empty"), ('[[1]]', "not a scalar")]
    seen = []
    for answer, expected in faults:
        fresh("CALLER.md")
        back = env.conductor(key()).submit(answer)
        seen.append(is_field(back) and expected in (back.deviation or "") and back.repair == 1)
    fresh("CALLER.md")
    numbers = env.conductor(key()).submit("[1, 2]")
    fresh("CALLER.md")
    paths = env.conductor(key()).submit('["no/such/file.md", "nor/this/one.md"]')
    if (all(seen) and is_infer(numbers) and field_of(numbers) == "1"
            and is_infer(paths) and field_of(paths) == "no/such/file.md"):
        held("the form is judged, the nature never", "five faults of form each repair with the miss "
             "named -- not JSON, not an array, a twin, an empty element, a non-scalar -- while an "
             "array of integers and an array of paths that exist nowhere both open their lap")
    else:
        failures.append(f"  ✗ form judged                 {seen} {field_of(numbers)!r} {field_of(paths)!r}")

    # --- the head stays: two looks, the field unchanged; -compacted re-serves it ------
    fresh("CALLER.md")
    env.conductor(key()).submit('["x", "y"]')
    env.conductor(key()).peek()
    env.conductor(key()).peek()
    before = door_field()
    env.conductor(key()).forward("")
    lap_y = env.conductor(key()).submit(proof("D1"))
    mid = door_field()
    again = env.conductor(key()).compacted()
    slot = json.loads(env.session().read_text(encoding="utf-8"))
    kept = [one.get("field") for one in slot["frames"] if one["document"].endswith("DOOR.md")]
    if (before == ["x", "y"] and mid == ["y"] and field_of(lap_y) == "y"
            and field_of(again) == "y" and "DOOR" in again.stack and kept == [["y"]]):
        held("the head stays until the lap closes, and survives a compaction",
             "two looks leave the field at [x, y]; the closed lap drops `x`; -compacted renders "
             "`y` again from the frame, and the slot carries [y] -- no counter anywhere")
    else:
        failures.append(f"  ✗ head and compaction         {before!r} {mid!r} {field_of(lap_y)!r} "
                        f"{field_of(again)!r} {kept!r}")

    # --- a reference that resolves to nothing refuses -------------------------------
    hollow = env.conductor()
    hollow.forget()
    expect("field-argument-empty", lambda: hollow.start(hollow.boot("CALLHOLLOW.md")))

    # --- the floor: a described door as the floor completes; empty, at once ----------
    opened = fresh("DOOR.md")
    lap_z = env.conductor(key()).submit('["z"]')
    env.conductor(key()).forward("")
    ended = env.conductor(key()).submit(proof("D1"))
    fresh("DOOR.md")
    never = env.conductor(key()).submit("[]")
    if (is_field(opened) and is_infer(lap_z) and field_of(lap_z) == "z"
            and ended is not None and ended.end and "DOOR" in ended.stack
            and never is not None and never.end and "the run completes" in field_of(never)):
        held("the floor door completes its run", "booted as the floor, the door asks its field, "
             "plays its lap and the run completes when nothing remains; an empty field completes "
             "the run at once")
    else:
        failures.append(f"  ✗ floor door                  {is_field(opened)} {field_of(lap_z)!r} "
                        f"{ended and (ended.end, ended.stack)!r} {never and (never.end, field_of(never))!r}")

    # --- the trace and the ledger ---------------------------------------------------
    fresh("CALLER.md")
    env.conductor(key()).submit('["a", "b"]')
    env.conductor(key()).forward("")
    env.conductor(key()).submit(proof("D1"))
    env.conductor(key()).forward("")
    env.conductor(key()).submit(proof("D1"))
    events = trace()
    kinds = [one.get("kind") for one in events]
    origins = [(entry.get("subject"), entry.get("origin"))
               for one in events if one.get("kind") == "block"
               for entry in one.get("served", [])]
    if (kinds.count("lap") == 2 and kinds.count("cycle-done") == 1
            and ("field", "cycle") in origins):
        held("the trace says the laps, the ledger the origin", "two `lap` lines and one "
             "`cycle-done`; the served ledger carries `field` with the origin `cycle`, as a "
             "provided door's token does")
    else:
        failures.append(f"  ✗ trace and ledger            laps={kinds.count('lap')} "
                        f"done={kinds.count('cycle-done')} origins={origins[:6]!r}")

    # --- the weight: the lap block of the described door beside the provided twin ----
    def lap_weight(document: str, at: str) -> int:
        # the described door's procedure holds its injected FIELD step: its lap stands
        # at {2/2}, the provided twin's at {1/1}
        for one in reversed(trace()):
            if (one.get("kind") == "block" and one.get("stack", "").endswith(f"{document}{{{at}}}")
                    and not one.get("wait")):
                return int(one.get("weight", {}).get("total", 0))
        return 0
    # both doors as the floor, and the SECOND lap of each: the first output of a run
    # carries the marble, a rewound lap carries the element and the step alone
    fresh("DOOR.md")
    env.conductor(key()).submit('["alpha", "beta"]')
    env.conductor(key()).forward("")
    env.conductor(key()).submit(proof("D1"))
    described = lap_weight("DOOR", "1/1")        # the rewind purged the injected FIELD step
    fresh("TWIN.md")
    env.conductor(key()).forward("")
    env.conductor(key()).submit(proof("D1"))
    provided = lap_weight("TWIN", "1/1")
    if described and provided and abs(described - provided) < 200:
        held("the lap block weighs like a provided door's",
             f"second lap, both doors the floor of a run on one instance: described {described} c, "
             f"provided {provided} c -- the element under `field` or under `laps`, nothing else differs")
    else:
        failures.append(f"  ✗ lap weight                  described={described} provided={provided}")

    # --- the build and the parse refuse by name -------------------------------------
    lint = bench.env("described-lint")
    lint.write("procs/BOTH.md",
               "---\nname: BOTH\nkind: proc\ncycle: laps\nfield: |\n  a field\nproc: |\n  INFER\n---\nboth\n")
    expect("cycle-and-field", lambda: compiling.build_tools(lint.made))
    (lint.made / "procs" / "BOTH.md").unlink()
    # a BARE key declares nothing (the reader drops it): the empty one is `field: ""`
    lint.write("procs/BLANK.md", "---\nname: BLANK\nkind: proc\nfield: \"\"\nproc: |\n  INFER\n---\nblank\n")
    expect("field-empty", lambda: compiling.build_tools(lint.made))
    (lint.made / "procs" / "BLANK.md").unlink()
    lint.write("procs/NOPROC.md", "---\nname: NOPROC\nkind: doc\nfield: |\n  a field\n---\nno proc\n")
    expect("field-unplayable", lambda: compiling.build_tools(lint.made))
    (lint.made / "procs" / "NOPROC.md").unlink()
    lint.write("procs/KEYWORD.md",
               "---\nname: KEYWORD\nkind: proc\nfield: |\n  a field\nproc: |\n  FIELD\n  INFER\n---\nwritten\n")
    written = lint.conductor()
    written.forget()
    expect("field-keyword", lambda: written.start(written.boot("KEYWORD.md")))
    env.conductor().forget()
    return 0
