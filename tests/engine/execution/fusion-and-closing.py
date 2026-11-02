"""Scenario `fusion-and-closing` -- the blocks fuse by invariant anchors, and the closing
dresses for what it carries:
- a production is said at its own step: three CALLed documents before the frontier each say
  `=> words` under their own heading, and the AWAIT closes bare
- the AWAIT is bare, always: a lone WORK adjacent to the frontier, and an INFER after a CALL,
  both say `=> words`; every closing is `▶ AWAIT`
- produce and prove fuse legally, B-merged; the elided closing extends the range; the real
  turn collapses under one INSTRUCTION
- a payload between steps keeps its section; a new scope stacks with its delta; the closing
  after segments is bare
- a `§` writes `section` on the trace with the marked step, once per break, under the LLM's and
  the principal's conduction alike (batch les-zones-muettes, 2026-10-29)
"""
from __future__ import annotations

import re

from conductor import render
from conductor.rendering.render import AREAS
from tests.harness import support

run = support(__file__, "run")

WITNESS = "---\nname: {name}\nkind: proc\ndescription: a witness\nproc: |\n{steps}---\n{name} speaks\n"
PROOF_LINE = re.compile(rf"INFER proof \[P9\] {re.escape(AREAS)} => tool  \(")   # the checkpoint's line



def _opening(text: str, mark: str) -> int:
    """-> how many lines of a rendering open on `mark`: a section or a closing opens a line,
    and a document served in the output may name the marks in its own text."""
    return sum(1 for one in text.splitlines() if one.startswith(mark))

def arrow(block) -> str:
    """-> the closing line of a rendered block: the one the arrow opens."""
    return run.closing(render(block)).splitlines()[0] if block is not None else ""


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("fusion", pin=False)
    made = env.made

    # --- a production is said at its own step -------------------------------------------------
    for name in ("ALPHA", "BRAVO", "CHARLIE"):
        env.write(f"{name}.md", WITNESS.format(name=name, steps="  INFER\n"))

    def root(name: str, steps: str):
        path = env.write(f"{name}.md", WITNESS.format(name=name, steps=steps))
        env.conductor().forget()
        return env.conductor().start(path)

    called = root("CALLED", "  CALL ALPHA.md\n  CALL BRAVO.md\n  CALL CHARLIE.md\n")
    shown = render(called)
    if (called.wait and shown.count("INFER any => words") == 3 and arrow(called) == "▶ AWAIT"
            and all(f"▌ [{n}] CALLED ▸ {name}" in shown
                    for n, name in ((1, "ALPHA"), (2, "BRAVO"), (3, "CHARLIE")))):
        held("a production is said at its own step", "three documents, three `=> words` lines "
             "under their own headings, the AWAIT bare")
    else:
        failures.append(f"  ✗ response at the step        {arrow(called)!r} "
                        f"{shown.count('INFER any => words')}")

    # --- the AWAIT is bare, always ------------------------------------------------------------
    bare = root("BARE", "  WORK\n")
    joined = root("JOINED", "  CALL ALPHA.md\n  INFER\n")
    if (bare.wait and arrow(bare) == "▶ AWAIT" and "WORK any => words" in render(bare)
            and joined.wait and arrow(joined) == "▶ AWAIT"
            and render(joined).count("INFER any => words") == 2):
        held("the AWAIT is bare, always", "a lone WORK and an INFER after a CALL both say "
             "`=> words`; no name in parentheses, no `=>` on the closing")
    else:
        failures.append(f"  ✗ bare AWAIT                  {arrow(bare)!r} / {arrow(joined)!r}")
    env.conductor().forget()

    def fus_c():
        return run.conductor_of(env)

    env.write("SETTINGS.md", "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: max\n---\n")

    # --- produce and prove, fused ---------------------------------------------------------------
    proven_pair = env.write("PAIR.md", "---\nname: PAIR\nkind: proc\ndescription: produce and prove, "
                                       "fused\nconstraints.production: |\n  P9  say it plainly\n"
                                       "proc: |\n  WORK\n  PROVE\n---\nthe ask\n")
    fus_c().forget()
    pair = fus_c().start(proven_pair)
    pair_text = render(pair)
    if ("WORK" in pair_text and pair.output == "proof"
            and pair.next_call.endswith("<proof>\nEOF")
            and _opening(pair_text, "▶ CONTINUE") + _opening(pair_text, "▶ AWAIT") == 1
            and _opening(pair_text, "▌ pp · run t · ") == 1
            and _opening(pair_text, "▌ PAIR") == 1
            and pair_text.count("say it plainly") == 1):
        held("produce and prove fuse legally, B-merged", "same frame: one heading, one "
             "CONSTRAINTS -- the written PROVE rides the block; one closing, the proof piped")
    else:
        failures.append(f"  ✗ fused pair                  {pair.next_call!r}")
    if "▌ PAIR{1-2/2}" in pair_text:
        held("the elided closing extends the range", "the proof step's heading is held "
             "by the opener -- {1-2/2} covers the whole B-merge")
    else:
        failures.append(f"  ✗ closing range               {pair_text.splitlines()[:1]!r}")
    if (_opening(pair_text, "▌ INSTRUCTION") == 1
            and "WORK any => words" in pair_text
            and PROOF_LINE.search(pair_text)):
        held("the real turn collapses", "WORK and its written, briefless PROVE under ONE "
             "INSTRUCTION title -- nothing rides between them any more")
    else:
        failures.append(f"  ✗ turn collapse               "
                        f"{_opening(pair_text, '▌ INSTRUCTION')}")

    # --- a payload between steps keeps its section ----------------------------------------------
    env.write("NOTE.md", "a note between steps\n")
    split_doc = env.write("SPLIT.md", "---\nname: SPLIT\nkind: proc\ndescription: a reading between "
                                      "steps\nproc: |\n  INFER\n  SERVE NOTE.md\n  INFER\n---\n"
                                      "say two things\n")
    fus_c().forget()
    split_text = render(fus_c().start(split_doc))
    if _opening(split_text, "▌ INSTRUCTION") == 2 and "a note between steps" in split_text:
        held("a payload between steps keeps its section", "the served reading rides "
             "between the lines -- they never collapse across it")
    else:
        failures.append(f"  ✗ payload splits sections     {_opening(split_text, '▌ INSTRUCTION')}")

    # --- a new scope stacks with its delta --------------------------------------------------------
    env.write("CHILD.md", "---\nname: CHILD\nkind: proc\ndescription: adds a law\nconstraints.behavior: |\n"
                          "  Q2  the child's own law\nproc: |\n  INFER\n---\nthe child speaks\n")
    parent = env.write("PARENT.md", "---\nname: PARENT\nkind: proc\ndescription: crosses a scope\n"
                                    "constraints.behavior: |\n  Q1  the parent's law\nproc: |\n"
                                    "  INFER\n  CALL CHILD.md\n---\nspeak then call\n")
    fus_c().forget()
    crossed_text = render(fus_c().start(parent))
    if (crossed_text.count("the parent's law") == 1
            and crossed_text.count("the child's own law") == 1
            and "[Q1]" in crossed_text):
        held("a new scope stacks with its delta", "the child's law verbatim, the parent's "
             "already-said text held as a code -- verbatim once per output")
    else:
        failures.append(f"  ✗ delta verbatim              "
                        f"p={crossed_text.count(chr(39) + 's law')} "
                        f"[Q1]={'[Q1]' in crossed_text}")

    # --- the closing after segments is bare ------------------------------------------------------
    if (_opening(crossed_text, "▌ [") == 2                 # two segment headings, one
            and _opening(crossed_text, "▌ pp · ") == 1     # output heading above them
            and crossed_text.rstrip().splitlines()[-2] == "▶ AWAIT"):   # the command alone closes
        held("the closing after segments is bare", "two headings for two scopes, then the "
             "signal alone -- no habit, nothing delivered: each production was said at its step")
    else:
        failures.append(f"  ✗ bare closing                heads="
                        f"{_opening(crossed_text, '▌ [')} "
                        f"{crossed_text.rstrip().splitlines()[-2:]!r}")

    # --- a § writes `section` with the marked step, in both conductions ----------------------------
    paced = env.write("PACED.md", WITNESS.format(name="PACED", steps="  INFER\n  §\n  INFER\n"))
    sectioned = {}
    for led, value in (("llm", None), ("principal", "true")):
        fus_c().forget()
        opener = fus_c()
        first = run.under(value, lambda: opener.start(paced))
        key = opener.run_id
        after_first = [str(one.get("instruction")).strip() for one in run.trace(env, key) if one.get("kind") == "section"]
        second = run.under(value, lambda: env.conductor(key).forward(""))
        after_second = sum(1 for one in run.trace(env, key) if one.get("kind") == "section")
        sectioned[led] = (first is not None, second is not None, after_first, after_second)
    if all(opened and crossed and marked == ["INFER"] and count == 1
           for opened, crossed, marked, count in sectioned.values()):
        held("a § writes `section` with the marked step", "one `section` line naming the INFER it opens after "
             "the first output, none more after the second, under both conductions")
    else:
        failures.append(f"  ✗ the section traced          {sectioned}")

    return 0
