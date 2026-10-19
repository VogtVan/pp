"""Scenario `fusion-and-closing` -- the blocks fuse by invariant anchors, and the closing
dresses for what it carries:
- a production is said at its own step: three CALLed documents before the frontier each say
  `=> response` under their own heading, and the FINAL closes bare
- the FINAL is bare, always: a lone WORK adjacent to the frontier, and an INFER after a CALL,
  both say `=> response`; every closing is `▶ FINAL`
- fusion `max` renders the certain stretch under one INSTRUCTION title; the heading says the
  range; fusion `n` caps it, the CONTINUE hands the rest
- the `§` break holds, the `# §` stays a comment; the `§` holds before a CHAINING step too
- a document pins its own fusion
- produce and prove fuse legally, B-merged; the elided closing extends the range; the real
  turn collapses under one INSTRUCTION; a fused batch repairs whole
- a payload between steps keeps its section; a new scope stacks with its delta; the closing
  after segments is bare
- the response channel: every unconsumed step goes `=> response`
"""
from __future__ import annotations

import re

from conductor import render
from conductor.rendering.render import AREAS
from tests.harness import support

run = support(__file__, "run")

WITNESS = "---\nname: {name}\nkind: proc\ndescription: a witness\nproc: |\n{steps}---\n{name} speaks\n"
PROOF_LINE = re.compile(rf"INFER proof \[P9\] {re.escape(AREAS)} => tool \(heredoc\)")   # the checkpoint's line


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

    called = root("CALLED", "  CALL ALPHA.md\n  CALL BRAVO.md\n  CALL CHARLIE.md\n  FINAL\n")
    shown = render(called)
    if (called.wait and shown.count("INFER any => response") == 3 and arrow(called) == "▶ FINAL"
            and all(f"▌ [{n}] CALLED ▸ {name}" in shown
                    for n, name in ((1, "ALPHA"), (2, "BRAVO"), (3, "CHARLIE")))):
        held("a production is said at its own step", "three documents, three `=> response` lines "
             "under their own headings, the FINAL bare")
    else:
        failures.append(f"  ✗ response at the step        {arrow(called)!r} "
                        f"{shown.count('INFER any => response')}")

    # --- the FINAL is bare, always ------------------------------------------------------------
    bare = root("BARE", "  WORK\n  FINAL\n")
    joined = root("JOINED", "  CALL ALPHA.md\n  INFER\n  FINAL\n")
    if (bare.wait and arrow(bare) == "▶ FINAL" and "WORK any => response" in render(bare)
            and joined.wait and arrow(joined) == "▶ FINAL"
            and render(joined).count("INFER any => response") == 2):
        held("the FINAL is bare, always", "a lone WORK and an INFER after a CALL both say "
             "`=> response`; no name in parentheses, no `=>` on the closing")
    else:
        failures.append(f"  ✗ bare FINAL                  {arrow(bare)!r} / {arrow(joined)!r}")
    env.conductor().forget()

    # --- fusion by invariant anchors: max renders the certain stretch ---------------------------
    def fus_c():
        return run.conductor_of(env)

    trio = env.write("TRIO.md", "---\nname: TRIO\nkind: proc\ndescription: three response steps\n"
                                "proc: |\n  INFER\n  INFER\n  INFER\n  FINAL\n---\nthree things to say\n")
    fused_out = fus_c().start(trio)
    fus_trace = run.kinds(env, "t")
    fused_text = render(fused_out)
    if (fused_out.wait and fus_trace.count("batched") == 3
            and fused_text.count("▌ INSTRUCTION") == 1
            and fused_text.count("INFER any => response") == 3
            and "▶ FINAL" in fused_text.rstrip().splitlines()):
        held("fusion: max renders the certain stretch",
             "three response steps, one output -- the lines collapse under ONE title, "
             "and the FINAL closes bare: each production was said at its step")
    else:
        failures.append(f"  ✗ fusion max                  wait={fused_out.wait} "
                        f"batched={fus_trace.count('batched')} "
                        f"instr={fused_text.count('▌ INSTRUCTION')}")

    if ("▌ TRIO{1-3/4}" in fused_text                       # one segment heading, and
            and fused_text.count("▌ pp · run t · ") == 1      # the output's own says
            and fused_text.count("▌ TRIO") == 1):             # the key, once
        held("the heading says the stretch", "one heading for the fused steps -- the "
             "range {1-3/4}, written once the assembler knows where the merge stopped")
    else:
        failures.append(f"  ✗ fused range                 {fused_text.splitlines()[:1]!r}")

    # --- fusion: n caps the stretch -------------------------------------------------------------
    env.write("SETTINGS.md", "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: 2\n---\n")
    fus_c().forget()
    capped = fus_c().start(trio)
    capped_text = render(capped)
    capped_rest = fus_c().forward("")
    if (capped_text.count("▌ INSTRUCTION") == 1
            and capped_text.count("INFER any => response") == 2 and not capped.wait
            and capped_rest is not None and capped_rest.wait):
        held("fusion: n caps the stretch", "two steps this output, the CONTINUE hands "
             "the rest -- the next call carries the third and the frontier")
    else:
        failures.append(f"  ✗ fusion cap                  {capped_text.count('▌ INSTRUCTION')} "
                        f"{capped_rest and capped_rest.wait}")

    # --- the § break holds and the # § stays a comment ----------------------------------------
    env.write("SETTINGS.md", "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: max\n---\n")
    barred = env.write("BARRED.md", "---\nname: BARRED\nkind: proc\ndescription: a section break\n"
                                    "proc: |\n  INFER\n  §\n  INFER\n  # §\n  INFER\n  FINAL\n---\n"
                                    "broken in two\n")
    fus_c().forget()
    first_half = fus_c().start(barred)
    second_half = fus_c().forward("")
    if (render(first_half).count("▌ INSTRUCTION") == 1 and not first_half.wait
            and second_half is not None and second_half.wait
            and render(second_half).count("▌ INSTRUCTION") == 1
            and render(second_half).count("INFER any => response") == 2):
        held("the § break holds and the # § stays a comment",
             "fusion never crosses the marked step; the commented barrier is inert -- "
             "uncommenting is what arms it")
    else:
        failures.append(f"  ✗ section break               "
                        f"{render(first_half).count('▌ INSTRUCTION')}/"
                        f"{second_half and render(second_half).count('▌ INSTRUCTION')}")

    # --- the anchor decides, never the type: the same break before a CHAINING step -------------
    env.write("CHAINED.md", "---\nname: CHAINED\nkind: doc\n---\n\nread me\n")
    chained = env.write("CHAINBAR.md", "---\nname: CHAINBAR\nkind: proc\ndescription: a break before "
                                       "a chaining step\nproc: |\n  INFER\n  §\n  SERVE CHAINED.md\n"
                                       "  INFER\n  FINAL\n---\nthe anchor decides\n")
    fus_c().forget()
    chain_first = fus_c().start(chained)
    chain_next = fus_c().forward("")
    chain_shown = render(chain_first)
    if (chain_shown.count("▌ INSTRUCTION") == 1
            and "INFORMATION — CHAINED" not in chain_shown
            and chain_next is not None
            and "INFORMATION — CHAINED" in render(chain_next)):
        held("the § holds before a CHAINING step too",
             "a break before SERVE closes the output as one before INFER does -- "
             "the anchor decides, never the type")
    else:
        failures.append(f"  ✗ section break, chaining     "
                        f"{chain_shown.count('▌ INSTRUCTION')} instruction(s), "
                        f"reading served early={'INFORMATION — CHAINED' in chain_shown}")

    # --- a document pins its own fusion ---------------------------------------------------------
    capped_doc = env.write("CAPPED.md", "---\nname: CAPPED\nkind: proc\ndescription: pins its own pace\n"
                                        "fusion: none\nproc: |\n  INFER\n  INFER\n  FINAL\n---\n"
                                        "one by one\n")
    fus_c().forget()
    own_pace = fus_c().start(capped_doc)
    if render(own_pace).count("▌ INSTRUCTION") == 1:
        held("a document pins its own fusion", "`fusion: none` in the front matter -- "
             "the author's pace outranks the instance's max")
    else:
        failures.append(f"  ✗ document fusion             {render(own_pace).count('▌ INSTRUCTION')}")

    # --- produce and prove, fused ---------------------------------------------------------------
    proven_pair = env.write("PAIR.md", "---\nname: PAIR\nkind: proc\ndescription: produce and prove, "
                                       "fused\nconstraints.production: |\n  P9  say it plainly\n"
                                       "proc: |\n  WORK\n---\nthe ask\n")
    fus_c().forget()
    pair = fus_c().start(proven_pair)
    pair_text = render(pair)
    if ("WORK" in pair_text and pair.output == "proof"
            and "your proof on stdin" in pair.next_call
            and pair_text.count("▶ CONTINUE") + pair_text.count("▶ FINAL") == 1
            and pair_text.count("▌ pp · run t · ") == 1
            and pair_text.count("▌ PAIR") == 1
            and pair_text.count("say it plainly") == 1):
        held("produce and prove fuse legally, B-merged", "same frame: one heading, one "
             "CONSTRAINTS -- the proof terminal rides the block; one closing, the proof piped")
    else:
        failures.append(f"  ✗ fused pair                  {pair.next_call!r}")
    if "▌ PAIR{1-2/2}" in pair_text:
        held("the elided closing extends the range", "the proof step's heading is held "
             "by the opener -- {1-2/2} covers the whole B-merge")
    else:
        failures.append(f"  ✗ closing range               {pair_text.splitlines()[:1]!r}")
    if (pair_text.count("▌ INSTRUCTION") == 1
            and "WORK any => response" in pair_text
            and PROOF_LINE.search(pair_text)):
        held("the real turn collapses", "WORK and its briefless proof under ONE "
             "INSTRUCTION title -- nothing rides between them any more")
    else:
        failures.append(f"  ✗ turn collapse               "
                        f"{pair_text.count('▌ INSTRUCTION')}")
    pair_fail = fus_c().submit('[{"code": "P9", "evidence": "off", "verdict": "fail"}]')
    if (pair_fail is not None and pair_fail.repair >= 1 and "WORK" in render(pair_fail)
            and "▌ [2] PAIR{2/2} · REPAIR" in render(pair_fail)):
        held("a fused batch repairs whole", "the failing proof replays the document -- "
             "the batch re-renders, the REPAIR heading never elided (and numbered: "
             "the replay is a multi-heading output): the repaired step's own position")
    else:
        failures.append(f"  ✗ fused repair                {pair_fail and pair_fail.repair}")

    # --- a payload between steps keeps its section ----------------------------------------------
    env.write("NOTE.md", "a note between steps\n")
    split_doc = env.write("SPLIT.md", "---\nname: SPLIT\nkind: proc\ndescription: a reading between "
                                      "steps\nproc: |\n  INFER\n  SERVE NOTE.md\n  INFER\n  FINAL\n---\n"
                                      "say two things\n")
    fus_c().forget()
    split_text = render(fus_c().start(split_doc))
    if split_text.count("▌ INSTRUCTION") == 2 and "a note between steps" in split_text:
        held("a payload between steps keeps its section", "the served reading rides "
             "between the lines -- they never collapse across it")
    else:
        failures.append(f"  ✗ payload splits sections     {split_text.count('▌ INSTRUCTION')}")

    # --- a new scope stacks with its delta --------------------------------------------------------
    env.write("CHILD.md", "---\nname: CHILD\nkind: proc\ndescription: adds a law\nconstraints.behavior: |\n"
                          "  Q2  the child's own law\nproc: |\n  INFER\n---\nthe child speaks\n")
    parent = env.write("PARENT.md", "---\nname: PARENT\nkind: proc\ndescription: crosses a scope\n"
                                    "constraints.behavior: |\n  Q1  the parent's law\nproc: |\n"
                                    "  INFER\n  CALL CHILD.md\n  FINAL\n---\nspeak then call\n")
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
    if (crossed_text.count("▌ [") == 2                 # two segment headings, one
            and crossed_text.count("▌ pp · ") == 1     # output heading above them
            and crossed_text.rstrip().splitlines()[-3] == "▶ FINAL"):
        held("the closing after segments is bare", "two headings for two scopes, then the "
             "signal alone -- no habit, nothing delivered: each production was said at its step")
    else:
        failures.append(f"  ✗ bare closing                heads="
                        f"{crossed_text.count('▌ [')} "
                        f"{crossed_text.rstrip().splitlines()[-3:]!r}")

    # --- the response channel: a four-step turn step by step, each production closed bare ---------
    env.write("SETTINGS.md", "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: none\n"
                             "conduction_effort: none\n---\n")
    env.conductor().forget()
    paused = env.conductor()
    paused.start(env.write("PAUSE.md", WITNESS.format(
        name="PAUSE", steps="  CALL ALPHA.md\n  WORK\n  CALL BRAVO.md\n  FINAL\n")))
    key = paused.run_id
    for _ in range(2):
        env.conductor(key).submit("")
    delivered = env.conductor(key).submit("")         # BRAVO closed bare: the frontier
    rendered = "\n".join(render(one) for one in (called, bare, joined, delivered) if one is not None)
    if (delivered is not None and delivered.wait and arrow(delivered) == "▶ FINAL"
            and rendered.count("=> response") >= 7):
        held("the response channel", "every unconsumed step goes => response, the step-by-step "
             "frontier included")
    else:
        failures.append(f"  ✗ response channel            {rendered.count('=> response')} "
                        f"{arrow(delivered)!r}")
    return 0
