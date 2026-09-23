"""Scenario `workflow-acyclic` -- 12 case(s) (batch les-workflows-acycliques, 2026-09-22):
- the inferred path: ROOT calls A; A `next: B.md C.md` + `choose:` asks the agent at a NEXT
  step rendered as a PICK (OPTIONS the names, the prose under `next`); `B.md` elected,
  B enters as a SIBLING of A in ROOT (the heading says `ROOT ▸ B`, never `ROOT ▸ A ▸ B`),
  leaves to D alone, D leaves and ROOT resumes -- two injected CALLs, three `next` lines
- the root's laws alone hold on the path: A's law is not in force at B, ROOT's is everywhere
- the production circulates: B declares `input:` and opens on A's last production
- the provided decision: `decide:` plays the owner's skill -- the name it prints follows;
  a name outside `next:` refuses `next-foreign`, a non-zero exit `next-refused`
- the miss repairs like a PICK: a name outside OPTIONS reopens A, the miss named
- the proof comes before the choice, and no second proof follows it
- the workflow survives a compaction mid-way, and replays under a session cycle
- the socket: a contributor carrying `next:` hands its successor the socket mark
- the build and the parse refuse by name: next-cycle, next-undecided, decision-idle,
  choose-and-decide, next-unplayable, reference-unknown, format-mismatch, next-keyword
- the run refuses by name: next-floor, choose-argument-empty
- the trace says `next` per transition and `-stats` counts the transitions
- the weight: the decision block beside a written PICK of the same options
- nothing moves without `next:`: a run without the key renders the same blocks
"""
from __future__ import annotations

import json
from conductor import compiling, instance, persistence, render, revive
from conductor.state import traces

SKILL = '''import sys
if sys.argv[1:] == ["next"]:
    print("C.md")
elif sys.argv[1:] == ["foreign"]:
    print("Z.md")
else:
    sys.exit(1)
'''
WITNESS = """name: wf
version: 0.0.1
description: a package whose skill decides a successor
requires: [kit]
"""


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("workflow")
    env.write("LIST.md", "---\nname: LIST\nkind: doc\nchoices: framed or waiting\n---\n")
    env.write("procs/ROOT.md",
              "---\nname: ROOT\nkind: proc\nconstraints.production: |\n  R1  the root's law.\n"
              "proc: |\n  CALL A.md\n  INFER\n---\nthe root calls A, then one more line\n")
    env.write("procs/A.md",
              "---\nname: A\nkind: proc\nnext: B.md C.md\nchoose: |\n  B when the batch is @LIST.choices, C otherwise.\n"
              "output: line\nconstraints.production: |\n  A1  A's own law.\nproc: |\n  INFER\n---\nA speaks one line\n")
    env.write("procs/B.md",
              "---\nname: B\nkind: proc\nnext: D.md\ninput: line\nproc: |\n  INFER\n---\nB takes A's line\n")
    env.write("procs/C.md", "---\nname: C\nkind: proc\nproc: |\n  INFER\n---\nC\n")
    env.write("procs/D.md", "---\nname: D\nkind: proc\nproc: |\n  INFER\n---\nD\n")

    def key() -> str:
        return persistence.run_id_of(env.session())

    def trace() -> list[dict]:
        log = json.loads(env.session().read_text(encoding="utf-8"))["log"]
        lines = (env.made / ".sys" / "state" / log).read_text(encoding="utf-8").splitlines()
        return [json.loads(one) for one in lines if one.strip()]

    def nexts() -> list[tuple]:
        return [(one.get("document"), one.get("successor"), one.get("by"))
                for one in trace() if one.get("kind") == "next"]

    def proof(*codes: str) -> str:
        return json.dumps([{"code": code, "evidence": "held", "verdict": "ok"} for code in codes])

    def is_step(block, keyword: str, document: str) -> bool:
        return (block is not None and block.instruction is not None
                and block.instruction.keyword == keyword and block.document == document)

    def stack() -> list:
        return env.conductor(key())._rebind(persistence.restore(env.session(), revive)).frames

    def fresh(document: str):
        conductor = env.conductor()
        conductor.forget()
        return conductor.start(conductor.boot(document))

    def codes(block) -> list[str]:
        return [one.code for one in block.constraints] if block is not None else []

    # --- the inferred path: A asks, B follows as a sibling, D alone, ROOT resumes -------
    a = fresh("ROOT.md")                                   # A{1/1}: INFER line -> tool? no: chat
    a_done = env.conductor(key()).forward("")              # A's line said; the proof of A1 stands
    proved = env.conductor(key()).submit(proof("A1"))      # then the NEXT step
    shown = render(proved) if proved is not None else ""
    b = env.conductor(key()).submit("B.md")                # B enters, sibling of A
    b_done = env.conductor(key()).forward("")              # B leaves alone to D
    d_done = env.conductor(key()).forward("")              # D leaves, ROOT resumes
    root = [one for one in stack() if one.document.name == "ROOT"]
    injected = ([(one.keyword, one.argument, one.injected) for one in root[0].procedure.instructions]
                if root else [])
    if (is_step(a, "INFER", "A") and is_step(proved, "NEXT", "A")
            and list(proved.options) == ["B.md", "C.md"]
            and "framed or waiting" in dict(proved.payloads).get("next", "")
            and "NEXT INSTRUCTION CONTEXT — next" in shown and "PICK next options => tool" in shown
            and is_step(b, "INFER", "B") and b.stack.startswith("ROOT ▸ B{") and "A" not in b.stack.split(" ▸ ")
            and is_step(b_done, "INFER", "D") and b_done.stack.startswith("ROOT ▸ D{")
            and is_step(d_done, "INFER", "ROOT")
            and injected == [("CALL", "A.md", False), ("CALL", "B.md", True), ("CALL", "D.md", True), ("INFER", "", False)]
            and nexts() == [("A", "B.md", "agent"), ("B", "D.md", "alone")]):
        held("the inferred path plays in two frames",
             "A's NEXT step renders `PICK next options => tool` with OPTIONS B.md C.md and the prose "
             "under `next` (`@LIST.choices` resolved); B.md elected, B stands at `ROOT ▸ B`, leaves "
             "alone to D, D leaves and ROOT resumes -- two CALLs injected after `CALL A.md`, "
             "`next` lines by agent then alone")
    else:
        failures.append(f"  ✗ inferred path               a={is_step(a, 'INFER', 'A')} "
                        f"next={is_step(proved, 'NEXT', 'A')} options={proved and list(proved.options)!r} "
                        f"b={b and b.stack!r} d={b_done and b_done.stack!r} root={d_done and d_done.document!r} "
                        f"injected={injected!r} nexts={nexts()!r}")

    # --- the root's laws alone hold; the production circulates -------------------------
    fresh("ROOT.md")
    env.conductor(key()).forward("")
    env.conductor(key()).submit(proof("A1"))
    b = env.conductor(key()).submit("B.md")
    seeds = [one.seed for one in stack() if one.document.name == "B"]
    a_given = [one.given for one in stack()[0].procedure.instructions if one.argument == "A.md"]
    if ("R1" in codes(b) and "A1" not in codes(b) and seeds and seeds[0] == a_given[0]):
        held("the root's laws alone, the production circulates",
             f"B's block says R1 and not A1; B opened on A's production as its seed ({seeds[0]!r})")
    else:
        failures.append(f"  ✗ laws and seed               codes={codes(b)!r} seeds={seeds!r} given={a_given!r}")

    # --- the provided decision: the owner's skill says the successor --------------------
    (env.made / ".sys" / "vendor").mkdir(parents=True, exist_ok=True)
    pkg = env.made / ".sys" / "vendor" / "wf@0.0.1"
    (pkg / "procs").mkdir(parents=True)
    (pkg / "skills" / "pp-wf").mkdir(parents=True)
    (pkg / "package.yaml").write_text(WITNESS, encoding="utf-8")
    (pkg / "skills" / "pp-wf" / "SKILL.md").write_text(
        "---\nname: pp-wf\ndescription: the witness decider\n---\n", encoding="utf-8")
    (pkg / "skills" / "pp-wf" / "pp-wf.py").write_text(SKILL, encoding="utf-8")
    (pkg / "procs" / "A2.md").write_text(
        "---\nname: A2\nkind: proc\nnext: B.md C.md\ndecide: next\nproc: |\n  INFER\n---\nA2\n",
        encoding="utf-8")
    (pkg / "procs" / "A3.md").write_text(
        "---\nname: A3\nkind: proc\nnext: B.md C.md\ndecide: foreign\nproc: |\n  INFER\n---\nA3\n",
        encoding="utf-8")
    (pkg / "procs" / "A4.md").write_text(
        "---\nname: A4\nkind: proc\nnext: B.md C.md\ndecide: broken\nproc: |\n  INFER\n---\nA4\n",
        encoding="utf-8")
    pins = instance.read(env.made)
    pins["packages"]["wf"] = "0.0.1"
    instance.write(env.made, pins)
    compiling.build_tools(env.made)
    for name in ("A2", "A3", "A4"):
        env.write(f"procs/ROOT{name}.md",
                  f"---\nname: ROOT{name}\nkind: proc\nproc: |\n  CALL {name}.md\n  INFER\n---\nroot of {name}\n")
    fresh("ROOTA2.md")
    c = env.conductor(key()).forward("")
    fresh("ROOTA3.md")
    expect("next-foreign", lambda: env.conductor(key()).forward(""))
    fresh("ROOTA4.md")
    expect("next-refused", lambda: env.conductor(key()).forward(""))
    if is_step(c, "INFER", "C") and c.stack.startswith("ROOTA2 ▸ C{"):
        held("the provided decision", "the owner's skill prints `C.md`: C follows as a sibling, "
             "`by: skill`; `Z.md` refuses next-foreign, a non-zero exit next-refused")
    else:
        failures.append(f"  ✗ provided decision           {c and (c.document, c.stack)!r}")

    # --- the miss repairs like a PICK; the proof precedes the choice --------------------
    fresh("ROOT.md")
    env.conductor(key()).forward("")
    first = env.conductor(key()).submit(proof("A1"))
    missed = env.conductor(key()).submit("Z.md")
    again = env.conductor(key()).forward("")               # A replayed: its line, then the proof
    proved = env.conductor(key()).submit(proof("A1"))
    b = env.conductor(key()).submit("B.md")
    kinds = [one.get("kind") for one in trace()]
    answers = [one.get("instruction", "").strip() for one in trace() if one.get("kind") == "answer"]
    if (is_step(first, "NEXT", "A") and is_step(missed, "INFER", "A") and missed.repair == 1
            and "not in OPTIONS" in (missed.deviation or "")
            and is_step(again, "PROVE", "A") and is_step(proved, "NEXT", "A")
            and is_step(b, "INFER", "B") and kinds.count("repair") == 1
            and answers.count("PROVE") == 2 and answers.count("NEXT") == 2):
        held("the miss repairs, the proof precedes the choice",
             "`Z.md` reopens A with the miss named (REPAIR 1); each pass of A proves BEFORE the "
             "NEXT step, and no proof follows the choice")
    else:
        failures.append(f"  ✗ miss and order              first={first and first.instruction.keyword} "
                        f"missed={missed and (missed.document, missed.repair, missed.deviation)!r} "
                        f"again={again and again.instruction.keyword} answers={answers!r}")

    # --- a compaction mid-way, and the session cycle ------------------------------------
    fresh("ROOT.md")
    env.conductor(key()).forward("")
    env.conductor(key()).submit(proof("A1"))
    env.conductor(key()).submit("B.md")
    back = env.conductor(key()).compacted()
    d = env.conductor(key()).forward("")
    env.write("procs/LOOP.md",
              "---\nname: LOOP\nkind: proc\ncycle: true\nproc: |\n  CALL A.md\n  INFER\n  FINAL\n---\nthe loop\n")
    fresh("LOOP.md")
    env.conductor(key()).forward("")
    env.conductor(key()).submit(proof("A1"))
    env.conductor(key()).submit("B.md")
    env.conductor(key()).forward("")
    env.conductor(key()).forward("")                       # D, then LOOP's INFER + FINAL
    turn2 = env.conductor(key()).forward("")               # the rewind: A again
    loop = [one for one in stack() if one.document.name == "LOOP"]
    kept = [one.argument for one in loop[0].procedure.instructions if one.injected] if loop else None
    if (back is not None and "B" in back.stack and is_step(d, "INFER", "D")
            and is_step(turn2, "INFER", "A") and kept == []):
        held("a compaction mid-way, a session cycle",
             "-compacted at B re-serves B and D still follows; under `cycle: true` the next "
             "exchange replays from `CALL A.md`, the injected CALLs purged")
    else:
        failures.append(f"  ✗ compaction and cycle        back={back and back.stack!r} d={d and d.document!r} "
                        f"turn2={turn2 and turn2.stack!r} kept={kept!r}")

    # --- the socket: a contributor's successor carries the mark -------------------------
    env.write("procs/HOST.md",
              "---\nname: HOST\nkind: proc\nproc: |\n  HOOK host.read\n  INFER\n---\nthe host\n")
    env.write("procs/GUEST.md",
              "---\nname: GUEST\nkind: proc\nattach: host.read\nnext: D.md\nproc: |\n  INFER\n---\nthe guest\n")
    g = fresh("HOST.md")
    dd = env.conductor(key()).forward("")
    host = [one for one in stack() if one.document.name == "HOST"]
    marks = [(one.argument, one.socket) for one in host[0].procedure.instructions if one.injected] if host else None
    if is_step(g, "INFER", "GUEST") and is_step(dd, "INFER", "D") and marks == [("GUEST.md", True), ("D.md", True)]:
        held("the socket mark travels", "the contributor's successor is injected as a socket CALL too")
    else:
        failures.append(f"  ✗ socket                      g={g and g.document} dd={dd and dd.document} marks={marks!r}")

    # --- the trace and -stats -----------------------------------------------------------
    said = traces.render(traces.runs(env.made / ".sys" / "state"), None, None)
    figures = traces.summary(traces.runs(env.made / ".sys" / "state"))
    if figures["transitions"] >= 8 and f"{figures['transitions']} transition(s)" in said:
        held("the trace and -stats", f"{figures['transitions']} `next` lines counted as transitions "
             "at the period's line and in the JSON")
    else:
        failures.append(f"  ✗ stats                       {figures.get('transitions')!r}")

    # --- the weight: the decision block beside a written PICK of the same options ------
    env.write("procs/PICKER.md",
              "---\nname: PICKER\nkind: proc\noutput: json\nproc: |\n  INFER\n  PICK next\n---\nB when the batch is framed or waiting, C otherwise.\n")
    fresh("PICKER.md")
    written = env.conductor(key()).submit('["B.md", "C.md"]')
    fresh("ROOT.md")
    env.conductor(key()).forward("")
    decided = env.conductor(key()).submit(proof("A1"))
    w_pick, w_next = len(render(written)), len(render(decided))
    if is_step(written, "PICK", "PICKER") and is_step(decided, "NEXT", "A") and abs(w_pick - w_next) < 400:
        held("the decision block weighs like a PICK",
             f"written PICK {w_pick} c, injected NEXT {w_next} c on one instance -- the brief and the heading alone differ")
    else:
        failures.append(f"  ✗ weight                      pick={w_pick} next={w_next}")

    # --- nothing moves without `next:` --------------------------------------------------
    env.write("procs/PLAIN.md", "---\nname: PLAIN\nkind: proc\nproc: |\n  CALL C.md\n  INFER\n---\nplain\n")
    one = render(fresh("PLAIN.md"))
    two = render(env.conductor(key()).forward(""))
    plain = [(k.keyword, k.injected) for k in stack()[0].procedure.instructions]
    # the first output carries the card, which TEACHES `PICK next`: the served section
    # and the step alone say whether a transition played
    quiet = ("INFORMATION — next" not in one and "INFORMATION — next" not in two
             and "PICK next options" not in two)
    if quiet and plain == [("CALL", False), ("INFER", False)]:
        held("nothing moves without next:", "a plain CALL renders no `next`, injects nothing")
    else:
        failures.append(f"  ✗ plain                       {plain!r}")

    # --- the run refuses by name --------------------------------------------------------
    floor = env.conductor()
    floor.forget()
    expect("next-floor", lambda: floor.start(floor.boot("A.md")))
    env.write("procs/HOLLOW.md",
              "---\nname: HOLLOW\nkind: proc\nnext: B.md C.md\nchoose: |\n  under @LIST.absent\nproc: |\n  INFER\n---\nhollow\n")
    env.write("procs/ROOTH.md", "---\nname: ROOTH\nkind: proc\nproc: |\n  CALL HOLLOW.md\n  INFER\n---\nroot\n")
    fresh("ROOTH.md")
    expect("choose-argument-empty", lambda: env.conductor(key()).forward(""))
    env.conductor().forget()

    # --- the build and the parse refuse by name -----------------------------------------
    lint = bench.env("workflow-lint")
    lint.write("procs/T.md", "---\nname: T\nkind: proc\nproc: |\n  INFER\n---\nt\n")
    cases = [
        ("next-cycle", {"X.md": "next: Y.md\n", "Y.md": "next: X.md\n"}),
        ("next-undecided", {"X.md": "next: Y.md T.md\n", "Y.md": ""}),
        ("decision-idle", {"X.md": "next: T.md\nchoose: |\n  pick\n"}),
        ("decision-idle", {"X.md": "choose: |\n  pick\n"}),
        ("choose-and-decide", {"X.md": "next: Y.md T.md\nchoose: |\n  pick\ndecide: next\n", "Y.md": ""}),
        ("reference-unknown", {"X.md": "next: NOWHERE.md\n"}),
        ("format-mismatch", {"X.md": "next: Y.md\noutput: table\n", "Y.md": "input: json\n"}),
    ]
    catalog = (lint.made / ".sys" / "tools.md")
    compiling.build_tools(lint.made)
    before = catalog.read_bytes()
    seen = []
    for code, files in cases:
        for name, extra in files.items():
            lint.write(f"procs/{name}", f"---\nname: {name[:-3]}\nkind: proc\n{extra}proc: |\n  INFER\n---\n{name}\n")
        expect(code, lambda: compiling.build_tools(lint.made))
        seen.append(catalog.read_bytes() == before)
        for name in files:
            (lint.made / "procs" / name).unlink()
    lint.write("procs/REF.md", "---\nname: REF\nkind: doc\nnext: T.md\n---\nno proc\n")
    expect("next-unplayable", lambda: compiling.build_tools(lint.made))
    (lint.made / "procs" / "REF.md").unlink()
    lint.write("procs/KEYWORD.md", "---\nname: KEYWORD\nkind: proc\nproc: |\n  NEXT\n  INFER\n---\nwritten\n")
    written = lint.conductor()
    written.forget()
    expect("next-keyword", lambda: written.start(written.boot("KEYWORD.md")))
    if all(seen):
        held("the catalog stands after every refused build", f"{len(seen)} refusals, tools.md identical")
    else:
        failures.append(f"  ✗ catalog moved               {seen!r}")
    return 0
