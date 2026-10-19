"""Scenario `cycles` -- a door that turns: the provided `cycle:` door and the described `field:`
door, side by side.
- the provided door: three laps, each on its element, each proven under the door's law AND a
  mounted law (the mount standing at lap 3), then the exit -- the door popped, the caller
  resumed with the last production; the empty entry opens no lap, the line under the token;
  a provider that refuses ends the cycle, its refusal said; a token no document provides
  refuses `cycle-unprovided`; `-compacted` on a lap in flight asks the token again and finds
  the same element; booted as the floor, the door completes its run on the exit
- the described door: two lines of front matter, no skill -- the FIELD step serves the prose
  as its brief (`@Doc.field` resolved), the agent's array accepted, three laps under `field`,
  each proven, then the exit, no `provider` line; an empty array opens no lap; the FORM alone
  is judged (not JSON, not an array, a twin, an empty element, a non-scalar each repair, an
  array of integers or of paths passes); the head stays under looks and survives
  `-compacted`; a `@Doc.field` that resolves to nothing refuses `field-argument-empty`; the
  floor completes, empty at once; the trace says the laps, the ledger the origin `cycle`; the
  lap block weighs like a provided door's; the build and the parse refuse `cycle-and-field`,
  `field-empty`, `field-unplayable`, `field-keyword`
"""
from __future__ import annotations

import json

from conductor import compiling, navigation, persistence, render, revive
from tests.harness import support

run = support(__file__, "run")

BRIEF = "one line per element"
CALLER = ("---\nname: CALLER\nkind: proc\nproc: |\n  CALL DOOR.md\n  INFER\n---\n"
          "calls the door, then one more line\n")
LAPS = "---\nname: LAPS\nkind: doc\nprovides: laps\nwith: pp-laps next\n---\n"

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
ALWAYS = '''import sys
if sys.argv[1:] == ["next"]:
    print("alpha")
sys.exit(0)
'''


def _key(env) -> str:
    """-> the key of the run standing at the environment."""
    return persistence.run_id_of(env.session())


def _trace(env) -> list[dict]:
    """-> every event of the standing run's trace, in order."""
    return run.trace(env, _key(env))


def _proof(*codes: str) -> str:
    """-> a proof that says every code held."""
    return json.dumps([{"code": code, "evidence": "held", "verdict": "ok"} for code in codes])


def _is_prove(block) -> bool:
    return (block is not None and block.instruction is not None
            and block.instruction.keyword == "PROVE")


def _is_infer(block, name: str = "DOOR") -> bool:
    return (block is not None and block.instruction is not None
            and block.instruction.keyword == "INFER" and block.document == name)


def provided(bench) -> None:
    """The provided door: `cycle: <token>`, a skill names each lap's element."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("cycled")
    root = env.root
    env.write("skills/pp-laps/SKILL.md",
              "---\nname: pp-laps\ndescription: the bench's iterator -- what remains due, and the sink that consumes it\n---\n")
    env.write("skills/pp-laps/pp-laps.py", ITERATOR)
    env.write("procs/LAPS.md", LAPS)
    env.write("procs/DOOR.md",
              "---\nname: DOOR\nkind: proc\ncycle: laps\nsink: pp-laps\nconstraints.production: |\n"
              f"  D1  the lap's line names its element.\nproc: |\n  INFER\n---\n{BRIEF}\n")
    env.write("procs/RULE.md",
              "---\nname: RULE\nkind: doc\nconstraints.production: |\n"
              "  M1  the mounted law rides every lap.\n---\nmounted matter\n")
    env.write("procs/CALLER.md", CALLER)
    env.write("procs/ORPHAN.md",
              "---\nname: ORPHAN\nkind: proc\ncycle: nobody\nconstraints.production: |\n"
              "  O1  a law.\nproc: |\n  INFER\n---\nnobody provides\n")

    def key() -> str:
        return _key(env)

    def element_of(block) -> str:
        return dict(block.payloads).get("laps", "")

    # --- three laps on their element, proven under the door's law and a mounted law ----
    (root / "laps.txt").write_text("a\nb\nc\n", encoding="utf-8")
    (root / "laps.done").write_text("", encoding="utf-8")
    first = env.conductor()
    lap1 = first.start(first.boot("CALLER.md"))
    env.conductor(key()).mount([{"doc": "procs/RULE.md"}])
    lap1_shown = env.conductor(key()).peek()
    p1 = env.conductor(key()).submit("line a")
    lap2 = env.conductor(key()).submit(_proof("D1", "M1"))
    p2 = env.conductor(key()).submit("line b")
    lap3 = env.conductor(key()).submit(_proof("D1", "M1"))
    mounted_at_3 = persistence.mounted_of(env.session())
    p3 = env.conductor(key()).submit("line c")
    out = env.conductor(key()).submit(_proof("D1", "M1"))
    laws3 = [one.code for one in lap3.constraints] if lap3 is not None else []
    proof_laws = [one.code for one in p3.constraints] if p3 is not None else []
    kinds = [one.get("kind") for one in _trace(env)]
    stack = env.conductor(key())._rebind(persistence.restore(env.session(), revive))
    caller = navigation.current(stack)
    resumed = (out is not None and out.document == "CALLER" and "DOOR" not in out.stack
               and caller.procedure.instructions[1].taken == "line c")
    if (_is_infer(lap1) and element_of(lap1) == "a" and BRIEF in render(lap1)
            and "M1" in [one.code for one in lap1_shown.constraints]
            and _is_prove(p1) and _is_infer(lap2) and element_of(lap2) == "b"
            and _is_prove(p2) and _is_infer(lap3) and element_of(lap3) == "c"
            and "M1" in laws3 and "D1" in laws3 and mounted_at_3
            and _is_prove(p3) and "M1" in proof_laws
            and resumed and kinds.count("lap") == 3 and kinds.count("cycle-done") == 1):
        held("three laps, each on its element, each proven, then the exit",
             "the door opens on `a`, proves under D1 and the mounted M1, rewinds on `b` and `c` "
             "with the mount standing, and leaves when the token renders nothing -- the caller "
             "resumes with `line c`, the trace says three laps and one cycle-done")
    else:
        failures.append(f"  ✗ three laps                  {_is_infer(lap1)}/{element_of(lap1)!r}/"
                        f"{_is_prove(p1)}/{element_of(lap2)!r}/{element_of(lap3)!r}/{laws3}/"
                        f"{bool(mounted_at_3)}/{proof_laws}/{resumed} kinds={kinds.count('lap')}"
                        f"/{kinds.count('cycle-done')} {out and out.stack!r}")

    # --- the empty entry: no lap opens, the line under the token ---------------------
    (root / "laps.done").write_text("a\nb\nc\n", encoding="utf-8")
    empty = env.conductor()
    empty.forget()
    closed = empty.start(empty.boot("CALLER.md"))
    said = dict(closed.payloads).get("laps", "") if closed is not None else ""
    if (closed is not None and closed.document == "CALLER" and "DOOR" not in closed.stack
            and "nothing due" in said and BRIEF not in render(closed)
            and [one.get("kind") for one in _trace(env)].count("lap") == 0):
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
            and REFUSAL in said
            and any(one.get("kind") == "cycle-done" and one.get("refused") for one in _trace(env))):
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
    lap_y = env.conductor(key()).submit(_proof("D1"))
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
    ended = env.conductor(key()).submit(_proof("D1"))
    bare = env.conductor()
    bare.forget()
    (root / "laps.done").write_text("z\n", encoding="utf-8")
    never = bare.start(bare.boot("DOOR.md"))
    if (_is_infer(opened) and element_of(opened) == "z"
            and ended is not None and ended.end and "DOOR" in ended.stack
            and never is not None and never.end and "nothing due" in dict(never.payloads).get("laps", "")):
        held("the floor door completes its run", "booted as the floor, the door plays its lap "
             "and the run completes when the token renders nothing; nothing due at the "
             "boot, the run completes at once")
    else:
        failures.append(f"  ✗ floor door                  {element_of(opened)!r} "
                        f"{ended and (ended.end, ended.stack)!r} {never and never.end!r}")
    env.conductor().forget()


def described(bench) -> None:
    """The described door: `field: <prose>`, the agent answers the elements as an array."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("described")
    env.write("LIST.md", "---\nname: LIST\nkind: doc\nitems: alpha beta gamma\n---\n")
    env.write("procs/DOOR.md",
              "---\nname: DOOR\nkind: proc\nfield: |\n  The words of @LIST.items, one lap each.\n"
              "constraints.production: |\n  D1  the lap's line names its element.\n"
              f"proc: |\n  INFER\n---\n{BRIEF}\n")
    env.write("procs/CALLER.md", CALLER)
    env.write("procs/HOLLOW.md",
              "---\nname: HOLLOW\nkind: proc\nfield: |\n  Everything under @LIST.absent.\n"
              "proc: |\n  INFER\n---\nnothing resolves\n")
    env.write("procs/CALLHOLLOW.md",
              "---\nname: CALLHOLLOW\nkind: proc\nproc: |\n  CALL HOLLOW.md\n  INFER\n---\ncalls the hollow door\n")
    # the provided twin -- the same door, its iterator a skill -- for the weight beside
    env.write("skills/pp-laps/SKILL.md",
              "---\nname: pp-laps\ndescription: the bench's iterator -- one element, always due\n---\n")
    env.write("skills/pp-laps/pp-laps.py", ALWAYS)
    env.write("procs/LAPS.md", LAPS)
    env.write("procs/TWIN.md",
              "---\nname: TWIN\nkind: proc\ncycle: laps\nconstraints.production: |\n"
              f"  D1  the lap's line names its element.\nproc: |\n  INFER\n---\n{BRIEF}\n")

    def key() -> str:
        return _key(env)

    def field_of(block) -> str:
        return dict(block.payloads).get("field", "") if block is not None else ""

    def is_field(block) -> bool:
        return (block is not None and block.instruction is not None
                and block.instruction.keyword == "FIELD" and block.document == "DOOR")

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
    lap2 = env.conductor(key()).submit(_proof("D1"))
    p2 = env.conductor(key()).forward("")
    lap3 = env.conductor(key()).submit(_proof("D1"))
    p3 = env.conductor(key()).forward("")
    out = env.conductor(key()).submit(_proof("D1"))
    kinds = [one.get("kind") for one in _trace(env)]
    stack = env.conductor(key())._rebind(persistence.restore(env.session(), revive))
    caller = navigation.current(stack)
    resumed = (out is not None and out.document == "CALLER" and "DOOR" not in out.stack
               and caller.document.name == "CALLER")
    brief_ok = ("alpha beta gamma" in field_of(ask) and "@LIST" not in field_of(ask)
                and "NEXT INSTRUCTION CONTEXT — field" in shown and "INFER field => tool (heredoc)" in shown
                and "(your field on stdin" in shown)
    if (is_field(ask) and brief_ok
            and _is_infer(lap1) and field_of(lap1) == "alpha" and _is_prove(p1)
            and _is_infer(lap2) and field_of(lap2) == "beta" and _is_prove(p2)
            and _is_infer(lap3) and field_of(lap3) == "gamma" and _is_prove(p3)
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
            and [one.get("kind") for one in _trace(env)].count("lap") == 0):
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
    if (all(seen) and _is_infer(numbers) and field_of(numbers) == "1"
            and _is_infer(paths) and field_of(paths) == "no/such/file.md"):
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
    lap_y = env.conductor(key()).submit(_proof("D1"))
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
    ended = env.conductor(key()).submit(_proof("D1"))
    fresh("DOOR.md")
    never = env.conductor(key()).submit("[]")
    if (is_field(opened) and _is_infer(lap_z) and field_of(lap_z) == "z"
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
    env.conductor(key()).submit(_proof("D1"))
    env.conductor(key()).forward("")
    env.conductor(key()).submit(_proof("D1"))
    events = _trace(env)
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
        for one in reversed(_trace(env)):
            if (one.get("kind") == "block" and one.get("stack", "").endswith(f"{document}{{{at}}}")
                    and not one.get("wait")):
                return int(one.get("weight", {}).get("total", 0))
        return 0
    # both doors as the floor, and the SECOND lap of each: the first output of a run
    # carries the marble, a rewound lap carries the element and the step alone
    fresh("DOOR.md")
    env.conductor(key()).submit('["alpha", "beta"]')
    env.conductor(key()).forward("")
    env.conductor(key()).submit(_proof("D1"))
    weight_described = lap_weight("DOOR", "1/1")        # the rewind purged the injected FIELD step
    fresh("TWIN.md")
    env.conductor(key()).forward("")
    env.conductor(key()).submit(_proof("D1"))
    weight_provided = lap_weight("TWIN", "1/1")
    if weight_described and weight_provided and abs(weight_described - weight_provided) < 200:
        held("the lap block weighs like a provided door's",
             f"second lap, both doors the floor of a run on one instance: described {weight_described} c, "
             f"provided {weight_provided} c -- the element under `field` or under `laps`, nothing else differs")
    else:
        failures.append(f"  ✗ lap weight                  described={weight_described} "
                        f"provided={weight_provided}")
    env.conductor().forget()

    # --- the build and the parse refuse by name (a house of its own: each refusal its document)
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


def scenario(bench) -> int:
    provided(bench)
    described(bench)
    return 0
