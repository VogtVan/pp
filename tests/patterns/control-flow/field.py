"""Scenario `field` -- the pattern `control-flow/field`, played from its demonstration:
- the described door turns on its prose, no skill: the FIELD step serves the prose as its brief
  (`@LEDGER.accounts` resolved), its line names the engine's form `field` -- its definition
  bounded by the module's FIELD_MAX, its closing restating no shape --, the agent's array
  accepted, three laps under `field`, each proven, then the exit, no `provider` line
- an empty array opens no lap
- the FORM alone is judged: not JSON, not an array, a twin, an empty element, a non-scalar each
  repair; an array of integers or of paths that exist nowhere passes
- the head stays under looks and survives `-compacted`
- a `@Doc.field` that resolves to nothing refuses `field-argument-empty`
- booted as the floor, the door parks its run; an empty field parks it at once
- the trace says the laps, the ledger the origin `cycle`
- the lap block weighs like a provided door's (the door of `control-flow/cycle` beside)
- the build and the parse refuse `cycle-and-field`, `field-empty`, `field-unplayable`, `field-keyword`
- under the principal's conduction the laps play the same documents
"""
from __future__ import annotations

import json

from conductor import compiling, navigation, persistence, render, revive
from conductor.core import language
from tests.harness import demonstrated, demos, plant, principal, titles, traced

DEMOS = ("ACCOUNTS.md", "BLANK.md", "BOTH.md", "HOLLOW.md", "LEDGER.md", "LOOSE.md", "MONTH.md",
         "WRITTEN.md")
PLAYED = ("ACCOUNTS.md", "HOLLOW.md", "LEDGER.md", "MONTH.md")
REFUSED = [("cycle-and-field", "BOTH.md"), ("field-empty", "BLANK.md"), ("field-unplayable", "LOOSE.md")]
FAULTS = [("not json", "not one valid JSON value"), ('{"a": 1}', "not a JSON array"),
          ('["a", "a"]', "appears twice"), ('["a", ""]', "is empty"), ('[[1]]', "not a scalar")]
ALWAYS = '''import sys
if sys.argv[1:] == ["next"]:
    print("alpha")
sys.exit(0)
'''


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("field", bare=True)
    found = demonstrated("control-flow", "field")
    if found != sorted(DEMOS):
        failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    text = {name: (demos("control-flow", "field") / name).read_text(encoding="utf-8") for name in DEMOS}
    plant(env, "control-flow", "field", PLAYED)
    law = "kind: proc\nconstraints.production: |\n  D1  a law of the door.\n"
    env.write("procs/ACCOUNTS.md", text["ACCOUNTS.md"].replace("kind: proc\n", law, 1))
    listed = next(line for line in text["LEDGER.md"].splitlines() if line.startswith("accounts: "))
    accounts = listed.split(": ", 1)[1].split()
    # the provided twin -- the door of `control-flow/cycle`, its iterator one element always due
    plant(env, "control-flow", "cycle", ("LAPS.md",))
    sweep = (demos("control-flow", "cycle") / "SWEEP.md").read_text(encoding="utf-8")
    env.write("procs/SWEEP.md", sweep.replace("kind: proc\n", law, 1))
    env.write("skills/pp-laps/SKILL.md", "---\nname: pp-laps\ndescription: the bench's iterator -- one element, always due\n---\n")
    env.write("skills/pp-laps/pp-laps.py", ALWAYS)

    def key() -> str:
        return persistence.run_id_of(env.session())

    def proof(*codes: str) -> str:
        return json.dumps([{"code": code, "evidence": "held", "verdict": "ok"} for code in codes])

    def field_of(block) -> str:
        return dict(block.payloads).get("field", "") if block is not None else ""

    def is_step(block, keyword: str, document: str = "ACCOUNTS") -> bool:
        return (block is not None and block.instruction is not None
                and block.instruction.keyword == keyword and block.document == document)

    def door_field() -> list | None:
        stack = env.conductor(key())._rebind(persistence.restore(env.session(), revive))
        return next((frame.field for frame in stack.frames if frame.document.name == "ACCOUNTS"), None)

    def fresh(document: str):
        conductor = env.conductor()
        conductor.forget()
        return conductor.start(conductor.boot(document))

    # --- the described door: prose served, array accepted, three laps, the exit ----------------
    ask = fresh("MONTH.md")
    shown = render(ask) if ask is not None else ""
    lap1 = env.conductor(key()).submit(json.dumps(accounts))
    p1 = env.conductor(key()).forward("")
    lap2 = env.conductor(key()).submit(proof("D1"))
    p2 = env.conductor(key()).forward("")
    lap3 = env.conductor(key()).submit(proof("D1"))
    p3 = env.conductor(key()).forward("")
    out = env.conductor(key()).submit(proof("D1"))
    llm_path = [one.document if one is not None else "" for one in (ask, lap1, p1, lap2, p2, lap3, p3, out)]
    kinds = [one.get("kind") for one in traced(env, key())]
    caller = navigation.current(env.conductor(key())._rebind(persistence.restore(env.session(), revive)))
    resumed = (out is not None and out.document == "MONTH" and "ACCOUNTS" not in out.stack
               and caller.document.name == "MONTH")
    brief_ok = (" ".join(accounts) in field_of(ask) and "@LEDGER" not in field_of(ask)
                and "▌ NEXT INSTRUCTION CONTEXT — field" in titles(shown)
                and any(line.startswith("INFER field") and "=> tool (heredoc)" in line
                        for line in shown.splitlines())
                and "(your field on stdin" in shown and "JSON array" not in shown.split("▶", 1)[-1]
                and str(language.FIELD_MAX) in compiling.format_enumeration(env.made)["field"][1])
    if (is_step(ask, "FIELD") and brief_ok
            and is_step(lap1, "INFER") and field_of(lap1) == accounts[0] and is_step(p1, "PROVE")
            and is_step(lap2, "INFER") and field_of(lap2) == accounts[1] and is_step(p2, "PROVE")
            and is_step(lap3, "INFER") and field_of(lap3) == accounts[2] and is_step(p3, "PROVE")
            and resumed and kinds.count("lap") == 3 and kinds.count("cycle-done") == 1
            and kinds.count("provider") == 0):
        held("the described door turns on its prose, no skill",
             "the FIELD step serves the prose with its reference resolved as `INFER field => tool "
             "(heredoc)`; the array accepted, the door turns three laps, each proven, and leaves when "
             "nothing remains -- three laps, one cycle-done, not one provider line")
    else:
        failures.append(f"  ✗ described door              {llm_path} brief={brief_ok} "
                        f"{field_of(lap1)!r}/{field_of(lap2)!r}/{field_of(lap3)!r} resumed={resumed} "
                        f"kinds={kinds.count('lap')}/{kinds.count('cycle-done')}/{kinds.count('provider')}")

    # --- an empty array: nothing due, no lap opens -----------------------------------------------
    fresh("MONTH.md")
    closed = env.conductor(key()).submit("[]")
    if (closed is not None and closed.document == "MONTH" and "ACCOUNTS" not in closed.stack
            and "nothing due" in field_of(closed)
            and [one.get("kind") for one in traced(env, key())].count("lap") == 0):
        held("an empty array opens no lap", "nothing due: neither body step nor lap, the CALL resolves "
             "and the line under `field` says it")
    else:
        failures.append(f"  ✗ empty array                 {closed and closed.stack!r} {field_of(closed)!r}")

    # --- the FORM alone is judged, never the nature ----------------------------------------------
    seen = []
    for answer, expected in FAULTS:
        fresh("MONTH.md")
        back = env.conductor(key()).submit(answer)
        seen.append(is_step(back, "FIELD") and expected in (back.deviation or "") and back.repair == 1)
    fresh("MONTH.md")
    numbers = env.conductor(key()).submit("[1, 2]")
    fresh("MONTH.md")
    paths = env.conductor(key()).submit('["no/such/file.md", "nor/this/one.md"]')
    if (all(seen) and is_step(numbers, "INFER") and field_of(numbers) == "1"
            and is_step(paths, "INFER") and field_of(paths) == "no/such/file.md"):
        held("the form is judged, the nature never", "five faults of form each repair with the miss "
             "named -- not JSON, not an array, a twin, an empty element, a non-scalar -- while an "
             "array of integers and an array of paths that exist nowhere both open their lap")
    else:
        failures.append(f"  ✗ form judged                 {seen} {field_of(numbers)!r} {field_of(paths)!r}")

    # --- the head stays: two looks, the field unchanged; -compacted re-serves it -----------------
    fresh("MONTH.md")
    env.conductor(key()).submit('["x", "y"]')
    env.conductor(key()).peek()
    env.conductor(key()).peek()
    before = door_field()
    env.conductor(key()).forward("")
    lap_y = env.conductor(key()).submit(proof("D1"))
    mid = door_field()
    again = env.conductor(key()).compacted()
    slot = json.loads(env.session().read_text(encoding="utf-8"))
    kept = [one.get("field") for one in slot["frames"] if one["document"].endswith("ACCOUNTS.md")]
    if (before == ["x", "y"] and mid == ["y"] and field_of(lap_y) == "y"
            and field_of(again) == "y" and "ACCOUNTS" in again.stack and kept == [["y"]]):
        held("the head stays until the lap closes, and survives a compaction",
             "two looks leave the field at [x, y]; the closed lap drops `x`; -compacted renders `y` "
             "again from the frame, and the slot carries [y] -- no counter anywhere")
    else:
        failures.append(f"  ✗ head and compaction         {before!r} {mid!r} {field_of(lap_y)!r} "
                        f"{field_of(again)!r} {kept!r}")

    # --- a reference that resolves to nothing refuses --------------------------------------------
    env.write("procs/MONTH.md", text["MONTH.md"].replace("CALL ACCOUNTS.md", "CALL HOLLOW.md"))
    hollow = env.conductor()
    hollow.forget()
    expect("field-argument-empty", lambda: hollow.start(hollow.boot("MONTH.md")))
    env.write("procs/MONTH.md", text["MONTH.md"])

    # --- the floor: the described door as the root parks its run; empty, at once -----------------
    opened = fresh("ACCOUNTS.md")
    lap_z = env.conductor(key()).submit('["z"]')
    env.conductor(key()).forward("")
    ended = env.conductor(key()).submit(proof("D1"))
    fresh("ACCOUNTS.md")
    never = env.conductor(key()).submit("[]")
    if (is_step(opened, "FIELD") and is_step(lap_z, "INFER") and field_of(lap_z) == "z"
            and ended is not None and ended.wait and "ACCOUNTS" in ended.stack
            and never is not None and never.wait):
        held("the floor door parks its run", "booted as the root, the door asks its field, plays its "
             "lap and the run parks when nothing remains; an empty field parks the run at once")
    else:
        failures.append(f"  ✗ floor door                  {is_step(opened, 'FIELD')} {field_of(lap_z)!r} "
                        f"{ended and (ended.wait, ended.stack)!r} {never and (never.wait, field_of(never))!r}")

    # --- the trace and the ledger ---------------------------------------------------------------
    fresh("MONTH.md")
    env.conductor(key()).submit('["a", "b"]')
    env.conductor(key()).forward("")
    env.conductor(key()).submit(proof("D1"))
    env.conductor(key()).forward("")
    env.conductor(key()).submit(proof("D1"))
    events = traced(env, key())
    kinds = [one.get("kind") for one in events]
    origins = [(entry.get("subject"), entry.get("origin"))
               for one in events if one.get("kind") == "block" for entry in one.get("served", [])]
    if kinds.count("lap") == 2 and kinds.count("cycle-done") == 1 and ("field", "cycle") in origins:
        held("the trace says the laps, the ledger the origin", "two `lap` lines and one `cycle-done`; "
             "the served ledger carries `field` with the origin `cycle`, as a provided door's token does")
    else:
        failures.append(f"  ✗ trace and ledger            laps={kinds.count('lap')} "
                        f"done={kinds.count('cycle-done')} origins={origins[:6]!r}")

    # --- the weight: the second lap of the described door beside the provided door's ------------
    def lap_weight(document: str) -> int:
        for one in reversed(traced(env, key())):
            if (one.get("kind") == "block" and one.get("stack", "").endswith(f"{document}{{1/2}}")
                    and not one.get("wait")):
                return int(one.get("weight", {}).get("total", 0))
        return 0
    fresh("ACCOUNTS.md")
    env.conductor(key()).submit('["alpha", "beta"]')
    env.conductor(key()).forward("")
    env.conductor(key()).submit(proof("D1"))
    weight_described = lap_weight("ACCOUNTS")
    fresh("SWEEP.md")
    env.conductor(key()).submit("line alpha")
    env.conductor(key()).submit(proof("D1"))
    weight_provided = lap_weight("SWEEP")
    if weight_described and weight_provided and abs(weight_described - weight_provided) < 200:
        held("the lap block weighs like a provided door's",
             f"second lap, both doors the root of a run on one instance: described {weight_described} c, "
             f"provided {weight_provided} c")
    else:
        failures.append(f"  ✗ lap weight                  described={weight_described} provided={weight_provided}")
    env.conductor().forget()

    # --- the principal's conduction: the same laps, the same documents --------------------------
    led = env.conductor()
    led.forget()
    steps = [principal(lambda: led.start(led.boot("MONTH.md")))]
    led_key = led.run_id
    steps.append(principal(lambda: env.conductor(led_key).submit(json.dumps(accounts))))
    for _ in range(3):
        steps.append(principal(lambda: env.conductor(led_key).forward("")))
        steps.append(principal(lambda: env.conductor(led_key).submit(proof("D1"))))
    led_path = [one.document if one is not None else "" for one in steps]
    if led_path == llm_path and field_of(steps[3]) == accounts[1]:
        held("both conductions turn the same laps", f"under the principal's conduction: {led_path}")
    else:
        failures.append(f"  ✗ the principal's laps        {led_path} -- owed {llm_path}")
    env.conductor(led_key).forget()

    # --- the build and the parse refuse by name (a house of its own) ----------------------------
    lint = bench.env("field-lint", bare=True)
    for code, name in REFUSED:
        plant(lint, "control-flow", "field", (name,))
        expect(code, lambda: compiling.build_tools(lint.made))
        (lint.made / "procs" / name).unlink()
    plant(lint, "control-flow", "field", ("WRITTEN.md",))
    written = lint.conductor()
    written.forget()
    expect("field-keyword", lambda: written.start(written.boot("WRITTEN.md")))
    return 0
