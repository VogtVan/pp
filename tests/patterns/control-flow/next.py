"""Scenario `next` -- the pattern `control-flow/next`, played from its demonstration:
- the inferred path: ROUTE calls STAGE; STAGE's `next: LEFT.md RIGHT.md` and `choose:` ask the
  agent at a NEXT step rendered as a PICK (the OPTIONS the names, the prose under `next` with
  `@SHELF.state` resolved); LEFT elected enters as a SIBLING of STAGE (`ROUTE ▸ LEFT`), leaves
  alone to TAIL, TAIL leaves and ROUTE resumes -- two injected CALLs, the `next` lines by agent,
  then alone
- only the root's laws ride the path; STAGE's line goes to the tool, its successor LEFT
  declaring `input:`, and LEFT opens on it, served under `input`
- the decided path: `decide:` plays a skill -- the one a document of the instance names first,
  and a package's own, implied -- and the name it prints follows; a name outside `next:` refuses
  `next-foreign`, a non-zero exit `next-refused`
- an election outside the OPTIONS repairs like a PICK; the proof comes before the choice, never
  after it
- a compaction mid-way re-serves the successor; the next message rewinds the root, the injected
  CALLs purged
- a contributor at a socket hands its successor the socket's path
- the trace says `next` per transition and `-stats` counts them; the decision block weighs like a
  written PICK; a CALL without `next:` injects nothing
- the run refuses `next-floor` and `choose-argument-empty`; the build and the parse refuse by name,
  the catalog intact after each refused build
- under the principal's conduction the inferred path plays the same documents
"""
from __future__ import annotations

import json

from conductor import compiling, instance, persistence, render, revive
from conductor.state import traces
from tests.harness import demonstrated, demos, plant, principal, titles, traced

DEMOS = ("BACK.md", "BOTH.md", "CIRCLE.md", "DECIDE.md", "HOLLOW.md", "IDLE.md", "LEFT.md",
         "LONE.md", "RIGHT.md", "ROUTE.md", "SHELF.md", "STAGE.md", "STRAY.md", "TAIL.md",
         "UNDECIDED.md", "WIDE.md", "WRITTEN.md")
PLAYED = ("DECIDE.md", "HOLLOW.md", "LEFT.md", "RIGHT.md", "ROUTE.md", "SHELF.md", "STAGE.md",
          "TAIL.md")
REFUSED = [("next-cycle", ("CIRCLE.md", "BACK.md")), ("next-undecided", ("UNDECIDED.md",)),
           ("decision-idle", ("IDLE.md",)), ("decision-idle", ("LONE.md",)),
           ("choose-and-decide", ("BOTH.md",)), ("next-unplayable", ("STRAY.md",)),
           ("format-mismatch", ("WIDE.md",))]
DECIDER = '''import sys
word = sys.argv[-1] if sys.argv[1:] else ""
if word == "pick":
    print("RIGHT.md")
elif word == "foreign":
    print("Z.md")
else:
    sys.exit(1)
'''
PACKAGE = "name: fork\nversion: 0.0.1\ndescription: a package whose skill decides\nrequires: [kit]\n"
MESSAGE = "the operator's next message"
LINE = "the draft line"     # the production a fork hands its successor that declares `input:`


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("next", bare=True)
    found = demonstrated("control-flow", "next")
    if found != sorted(DEMOS):
        failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    text = {name: (demos("control-flow", "next") / name).read_text(encoding="utf-8") for name in DEMOS}
    plant(env, "control-flow", "next", PLAYED)
    env.write("skills/pp-route/SKILL.md", "---\nname: pp-route\ndescription: the bench's decider\n---\n")
    env.write("skills/pp-route/pp-route.py", DECIDER)
    state = next(line for line in text["SHELF.md"].splitlines() if line.startswith("state: "))
    decided = next(line for line in text["DECIDE.md"].splitlines() if line.startswith("decide: "))

    def lawful(name: str, code: str) -> None:
        """The demonstration `name` planted with one law of production, `code`."""
        env.write(f"procs/{name}", text[name].replace(
            "kind: proc\n", f"kind: proc\nconstraints.production: |\n  {code}  a law of the case.\n", 1))

    def routed(target: str) -> None:
        """ROUTE planted calling `target` in the place of STAGE, without a law."""
        env.write("procs/ROUTE.md", text["ROUTE.md"].replace("CALL STAGE.md", f"CALL {target}"))

    def key() -> str:
        return persistence.run_id_of(env.session())

    def fresh(document: str):
        conductor = env.conductor()
        conductor.forget()
        return conductor.start(conductor.boot(document))

    def nexts() -> list[tuple]:
        return [(one.get("document"), one.get("successor"), one.get("by"))
                for one in traced(env, key()) if one.get("kind") == "next"]

    def proof(*codes: str) -> str:
        return json.dumps([{"code": code, "evidence": "held", "verdict": "ok"} for code in codes])

    def is_step(block, keyword: str, document: str) -> bool:
        return (block is not None and block.instruction is not None
                and block.instruction.keyword == keyword and block.document == document)

    def stack() -> list:
        return env.conductor(key())._rebind(persistence.restore(env.session(), revive)).frames

    def codes(block) -> list[str]:
        return [one.code for one in block.constraints] if block is not None else []

    def documents(blocks) -> list[str]:
        return [one.document if one is not None else "" for one in blocks]

    # --- the inferred path: STAGE asks, LEFT follows as a sibling, TAIL alone, ROUTE resumes ----
    lawful("ROUTE.md", "R1")
    lawful("STAGE.md", "S1")
    a = fresh("ROUTE.md")
    a_done = env.conductor(key()).submit(LINE)
    proved = env.conductor(key()).submit(proof("R1", "S1"))
    shown = render(proved) if proved is not None else ""
    b = env.conductor(key()).submit("LEFT.md")
    b_done = env.conductor(key()).forward("")
    d_done = env.conductor(key()).forward("")
    llm_path = documents([a, a_done, proved, b, b_done, d_done])
    root = [one for one in stack() if one.document.name == "ROUTE"]
    injected = ([(one.keyword, one.argument, one.injected) for one in root[0].procedure.instructions]
                if root else [])
    if (is_step(a, "INFER", "STAGE") and is_step(a_done, "PROVE", "STAGE")
            and is_step(proved, "NEXT", "STAGE") and list(proved.options) == ["LEFT.md", "RIGHT.md"]
            and state.split(": ", 1)[1] in dict(proved.payloads).get("next", "")
            and "▌ NEXT INSTRUCTION CONTEXT — next" in titles(shown)
            and any(line.startswith("PICK next") and "=> tool" in line for line in shown.splitlines())
            and is_step(b, "INFER", "LEFT") and b.stack.startswith("ROUTE ▸ LEFT{")
            and "STAGE" not in b.stack.split(" ▸ ")
            and is_step(b_done, "INFER", "TAIL") and b_done.stack.startswith("ROUTE ▸ TAIL{")
            and is_step(d_done, "INFER", "ROUTE")
            and injected == [("CALL", "STAGE.md", False), ("CALL", "LEFT.md", True),
                             ("CALL", "TAIL.md", True), ("INFER", "", False)]
            and nexts() == [("STAGE", "LEFT.md", "agent"), ("LEFT", "TAIL.md", "alone")]):
        held("the inferred path plays in two frames",
             "STAGE's NEXT step offers LEFT.md and RIGHT.md as a PICK under the prose, its reference "
             "resolved; LEFT stands at `ROUTE ▸ LEFT`, leaves alone to TAIL, and ROUTE resumes -- "
             "two CALLs injected, the `next` lines by agent then alone")
    else:
        failures.append(f"  ✗ inferred path               {llm_path} options={proved and list(proved.options)!r} "
                        f"b={b and b.stack!r} injected={injected!r} nexts={nexts()!r}")

    # --- the root's laws alone ride the path; the production circulates -------------------------
    fresh("ROUTE.md")
    env.conductor(key()).submit(LINE)
    env.conductor(key()).submit(proof("R1", "S1"))
    b = env.conductor(key()).submit("LEFT.md")
    seeds = [one.seed for one in stack() if one.document.name == "LEFT"]
    given = [one.given for one in stack()[0].procedure.instructions if one.argument == "STAGE.md"]
    if ("R1" in codes(b) and "S1" not in codes(b) and seeds == [LINE] and given == [LINE]
            and dict(b.payloads).get("input") == LINE):
        held("the root's laws alone, the production circulates",
             f"LEFT's block says R1 and not S1; LEFT opened on STAGE's line ({seeds[0]!r}), served "
             "under `input`")
    else:
        failures.append(f"  ✗ laws and seed               codes={codes(b)!r} seeds={seeds!r} given={given!r}")

    # --- the decided path: the instance's skill named first, then a package's own -------------
    routed("DECIDE.md")
    fresh("ROUTE.md")
    by_instance = env.conductor(key()).submit(LINE)
    instance_by = nexts()
    for word, code in (("foreign", "next-foreign"), ("broken", "next-refused")):
        env.write("procs/DECIDE.md", text["DECIDE.md"].replace(decided, decided.rsplit(" ", 1)[0] + f" {word}"))
        fresh("ROUTE.md")
        expect(code, lambda: env.conductor(key()).submit(LINE))
    (env.made / "procs" / "DECIDE.md").unlink()
    vendored = env.made / ".sys" / "vendor" / "fork@0.0.1"
    (vendored / "procs").mkdir(parents=True)
    (vendored / "skills" / "pp-fork").mkdir(parents=True)
    (vendored / "package.yaml").write_text(PACKAGE, encoding="utf-8")
    (vendored / "procs" / "DECIDE.md").write_text(text["DECIDE.md"], encoding="utf-8")
    (vendored / "skills" / "pp-fork" / "SKILL.md").write_text(
        "---\nname: pp-fork\ndescription: the package's decider\n---\n", encoding="utf-8")
    (vendored / "skills" / "pp-fork" / "pp-fork.py").write_text(DECIDER, encoding="utf-8")
    pins = instance.read(env.made)
    pins["packages"]["fork"] = "0.0.1"
    instance.write(env.made, pins)
    compiling.build_tools(env.made)
    fresh("ROUTE.md")
    by_package = env.conductor(key()).submit(LINE)
    if (is_step(by_instance, "INFER", "RIGHT") and by_instance.stack.startswith("ROUTE ▸ RIGHT{")
            and instance_by == [("DECIDE", "RIGHT.md", "skill")]
            and is_step(by_package, "INFER", "RIGHT") and nexts() == [("DECIDE", "RIGHT.md", "skill")]):
        held("the decided path", "the skill prints `RIGHT.md` and RIGHT follows as a sibling, `by: skill` -- "
             "named first by a document of the instance, implied by a package's own; a name outside "
             "`next:` refuses next-foreign, a non-zero exit next-refused")
    else:
        failures.append(f"  ✗ decided path               {by_instance and by_instance.stack!r} "
                        f"{instance_by!r} {by_package and by_package.stack!r} {nexts()!r}")

    # --- the miss repairs like a PICK; the proof precedes the choice ------------------------------
    lawful("ROUTE.md", "R1")
    fresh("ROUTE.md")
    env.conductor(key()).submit(LINE)
    first = env.conductor(key()).submit(proof("R1", "S1"))
    missed = env.conductor(key()).submit("Z.md")
    again = env.conductor(key()).submit(LINE)
    proved = env.conductor(key()).submit(proof("R1", "S1"))
    b = env.conductor(key()).submit("LEFT.md")
    events = traced(env, key())
    kinds = [one.get("kind") for one in events]
    answers = [one.get("instruction", "").strip() for one in events if one.get("kind") == "answer"]
    if (is_step(first, "NEXT", "STAGE") and is_step(missed, "INFER", "STAGE") and missed.repair == 1
            and "Z.md" in (missed.deviation or "")
            and is_step(again, "PROVE", "STAGE") and is_step(proved, "NEXT", "STAGE")
            and is_step(b, "INFER", "LEFT") and kinds.count("repair") == 1
            and answers.count("PROVE") == 2 and answers.count("NEXT") == 2):
        held("the miss repairs, the proof precedes the choice",
             "`Z.md` reopens STAGE with the miss named (REPAIR 1); each pass of STAGE proves BEFORE "
             "the NEXT step, and no proof follows the choice")
    else:
        failures.append(f"  ✗ miss and order              first={first and first.instruction.keyword} "
                        f"missed={missed and (missed.document, missed.repair, missed.deviation)!r} "
                        f"again={again and again.instruction.keyword} answers={answers!r}")

    # --- a compaction mid-way; the next message rewinds the root, the injected CALLs purged -----
    fresh("ROUTE.md")
    env.conductor(key()).submit(LINE)
    env.conductor(key()).submit(proof("R1", "S1"))
    env.conductor(key()).submit("LEFT.md")
    back = env.conductor(key()).compacted()
    tail = env.conductor(key()).forward("")
    last = env.conductor(key()).forward("")            # ROUTE's last step: its block closes on AWAIT
    rewound = env.conductor(key()).submit(MESSAGE)
    route = [one for one in stack() if one.document.name == "ROUTE"]
    kept = [one.argument for one in route[0].procedure.instructions if one.injected] if route else None
    if (back is not None and "LEFT" in back.stack and is_step(tail, "INFER", "TAIL")
            and is_step(last, "INFER", "ROUTE") and last.wait
            and is_step(rewound, "INFER", "STAGE") and kept == []):
        held("a compaction mid-way, the root rewound",
             "-compacted at LEFT re-serves LEFT and TAIL still follows; the root parked, the next "
             "message replays from `CALL STAGE.md`, the injected CALLs purged")
    else:
        failures.append(f"  ✗ compaction and rewind       back={back and back.stack!r} tail={tail and tail.document!r} "
                        f"last={last and (last.stack, last.wait)!r} rewound={rewound and rewound.stack!r} kept={kept!r}")

    # --- the socket: a contributor's successor keeps the socket's path ---------------------------
    env.write("procs/HOST.md", "---\nname: HOST\nkind: proc\nproc: |\n  HOOK host.read\n  INFER\n---\nthe host\n")
    env.write("procs/GUEST.md",
              "---\nname: GUEST\nkind: proc\nattach: host.read\nnext: TAIL.md\nproc: |\n  INFER\n---\nthe guest\n")
    g = fresh("HOST.md")
    gone = env.conductor(key()).forward("")
    host = [one for one in stack() if one.document.name == "HOST"]
    marks = [(one.argument, one.site) for one in host[0].procedure.instructions if one.injected] if host else None
    if (is_step(g, "INFER", "GUEST") and is_step(gone, "INFER", "TAIL")
            and marks == [("GUEST.md", "socket"), ("TAIL.md", "socket")]):
        held("the socket path travels", "the contributor's successor is injected on the socket's path too")
    else:
        failures.append(f"  ✗ socket                      {g and g.document} {gone and gone.document} {marks!r}")

    # --- the trace and -stats -------------------------------------------------------------------
    state_dir = env.made / ".sys" / "state"
    lines = [json.loads(one) for path in sorted(state_dir.glob("session-*.jsonl"))
             for one in path.read_text(encoding="utf-8").splitlines() if one.strip()]
    transitions = sum(1 for one in lines if one.get("kind") == "next")
    said = traces.render(traces.runs(state_dir), None, None)
    figures = traces.summary(traces.runs(state_dir))
    if transitions >= 8 and figures["transitions"] == transitions and f"{transitions} transition(s)" in said:
        held("the trace and -stats", f"{transitions} `next` lines counted as transitions at the "
             "period's line and in the JSON")
    else:
        failures.append(f"  ✗ stats                       {transitions} {figures.get('transitions')!r}")

    # --- the weight: the decision block beside a written PICK of the same options ---------------
    plant(env, "steps", "pick", ("TRIAGE.md",))
    fresh("TRIAGE.md")
    written = env.conductor(key()).submit(json.dumps(["LEFT.md", "RIGHT.md"]))
    lawful("ROUTE.md", "R1")
    fresh("ROUTE.md")
    env.conductor(key()).submit(LINE)
    decision = env.conductor(key()).submit(proof("R1", "S1"))
    w_pick, w_next = len(render(written)), len(render(decision))
    if is_step(written, "PICK", "TRIAGE") and is_step(decision, "NEXT", "STAGE") and abs(w_pick - w_next) < 400:
        held("the decision block weighs like a PICK",
             f"written PICK {w_pick} c, injected NEXT {w_next} c on one instance -- the brief and the heading alone differ")
    else:
        failures.append(f"  ✗ weight                      pick={w_pick} next={w_next}")

    # --- nothing moves without `next:` ----------------------------------------------------------
    routed("RIGHT.md")
    one = render(fresh("ROUTE.md"))
    two = render(env.conductor(key()).forward(""))
    plain = [(k.keyword, k.injected) for k in stack()[0].procedure.instructions]
    quiet = ("▌ INFORMATION — next" not in titles(one) + titles(two)
             and not any(line.startswith("PICK next") for line in two.splitlines()))
    if quiet and plain == [("CALL", False), ("INFER", False)]:
        held("nothing moves without next:", "a plain CALL renders no `next`, injects nothing")
    else:
        failures.append(f"  ✗ plain                       {plain!r}")

    # --- the run refuses by name ----------------------------------------------------------------
    floor = env.conductor()
    floor.forget()
    expect("next-floor", lambda: floor.start(floor.boot("STAGE.md")))
    routed("HOLLOW.md")
    fresh("ROUTE.md")
    expect("choose-argument-empty", lambda: env.conductor(key()).submit(LINE))
    env.conductor().forget()

    # --- the principal's conduction: the inferred path, the same documents ----------------------
    lawful("ROUTE.md", "R1")
    led = env.conductor()
    led.forget()
    steps = [principal(lambda: led.start(led.boot("ROUTE.md")))]
    led_key = led.run_id
    steps.append(principal(lambda: env.conductor(led_key).submit(LINE)))
    steps.append(principal(lambda: env.conductor(led_key).submit(proof("R1", "S1"))))
    steps.append(principal(lambda: env.conductor(led_key).submit("LEFT.md")))
    steps.append(principal(lambda: env.conductor(led_key).forward("")))
    steps.append(principal(lambda: env.conductor(led_key).forward("")))
    if documents(steps) == llm_path and steps[3] is not None and steps[3].stack.startswith("ROUTE ▸ LEFT{"):
        held("both conductions take the same path", f"under the principal's conduction: {documents(steps)}")
    else:
        failures.append(f"  ✗ the principal's path        {documents(steps)} -- owed {llm_path}")
    env.conductor(led_key).forget()

    # --- the build and the parse refuse by name (a house of its own) ----------------------------
    lint = bench.env("next-lint", bare=True)
    plant(lint, "control-flow", "next", ("LEFT.md", "RIGHT.md", "TAIL.md"))
    catalog = lint.made / ".sys" / "tools.md"
    compiling.build_tools(lint.made)
    before = catalog.read_bytes()
    seen = []
    for code, names in REFUSED:
        plant(lint, "control-flow", "next", names)
        expect(code, lambda: compiling.build_tools(lint.made))
        seen.append(catalog.read_bytes() == before)
        for name in names:
            (lint.made / "procs" / name).unlink()
    lint.write("procs/NOWHERE-BOUND.md",
               "---\nname: NOWHERE-BOUND\nkind: proc\nnext: NOWHERE.md\nproc: |\n  INFER\n---\nnowhere\n")
    expect("reference-unknown", lambda: compiling.build_tools(lint.made))
    seen.append(catalog.read_bytes() == before)
    (lint.made / "procs" / "NOWHERE-BOUND.md").unlink()
    plant(lint, "control-flow", "next", ("WRITTEN.md",))
    written = lint.conductor()
    written.forget()
    expect("next-keyword", lambda: written.start(written.boot("WRITTEN.md")))
    if all(seen):
        held("the catalog stands after every refused build", f"{len(seen)} refusals, tools.md identical")
    else:
        failures.append(f"  ✗ catalog moved               {seen!r}")
    return 0
