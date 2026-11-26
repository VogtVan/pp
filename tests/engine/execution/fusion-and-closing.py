"""Scenario `fusion-and-closing` -- the blocks fuse by invariant anchors, and the closing
dresses for what it carries:
- a production is said at its own step: three CALLed documents before the frontier, under the same
  laws, each say their line in ONE segment, the line naming its document, all three on the channel
  `terminal` -- the output ends on the last, pending, no closing; no step goes `response`
- the AWAIT is bare, always: a lone WORK adjacent to the frontier, and an INFER after a CALL,
  keep `=> terminal`; the principal's bare call that ends the passage closes on `▶ AWAIT`
  alone, no call under it
- no last message is asked: the bare AWAIT a judged proof opens carries no added line, and moves
  neither what the stack awaits nor a position; the step said before a `§` keeps `terminal`
- produce and prove fuse legally, B-merged; the elided closing extends the range; the real
  turn collapses under one INSTRUCTION
- a reading served between two steps stands at the head of their segment, their lines under one
  INSTRUCTION title; a new scope stacks with its delta; segments end on their last step, no closing
- a `§` writes `section` on the trace with the marked step, once per break (batch les-zones-muettes,
  2026-10-29)
"""
from __future__ import annotations

import re

from conductor import persistence, render
from conductor.core import language
from conductor.core.messages import AREAS
from conductor.rendering.render import last_line
from tests.harness import printed, stepped, support, titled, titles

run = support(__file__, "run")

WITNESS = "---\nname: {name}\nkind: proc\ndescription: a witness\nproc: |\n{steps}---\n{name} speaks\n"
SAID, LAST = f"=> {language.TERMINAL}  (", f"=> {language.RESPONSE}  ("   # a step said to the principal, a last message
PROOF_LINE = re.compile(rf"INFER proof \[P9\] {re.escape(AREAS)} => {language.TOOL_HEREDOC}  \(")   # the checkpoint's line



def _opening(text: str, mark: str) -> int:
    """-> how many lines of a rendering open on `mark`: a section or a closing opens a line,
    and a document served in the output may name the marks in its own text."""
    return sum(1 for one in text.splitlines() if one.startswith(mark))

def arrow(block) -> str:
    """-> the closing line of a rendered block: the one the arrow opens, "" when it closes on none."""
    lines = run.closing(render(block)).splitlines() if block is not None else []
    return lines[0] if lines else ""


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
    lines = [one for one in shown.splitlines() if one.startswith("INFER any => ")]
    if (not called.wait and [SAID in one for one in lines] == [True, True, True] and LAST not in shown
            and not called.response and arrow(called) == ""
            and [one.rsplit("(", 1)[-1].rstrip(")") for one in lines] == ["ALPHA", "BRAVO", "CHARLIE"]
            and _opening(shown, "▌ CALLED ▸ ") == 1 and _opening(shown, "▌ [") == 0):
        held("a production is said at its own step", "three documents under the same laws, three lines in "
             "one segment, each naming its document, all three on `terminal`, no `response`, no closing")
    else:
        failures.append(f"  ✗ response at the step        {arrow(called)!r} {lines} {called.response!r}")

    # --- the AWAIT is bare, always ------------------------------------------------------------
    def ended(name: str, steps: str):
        # the frontier output, then the principal's bare call once its prints are handed: the passage ends
        front = root(name, steps)
        return front, stepped(lambda: env.conductor())

    bare, bare_end = ended("BARE", "  WORK\n")
    joined, joined_end = ended("JOINED", "  CALL ALPHA.md\n  INFER\n")
    def channels(block) -> list[bool]:
        # the step lines of an output, each said on `terminal` or not; a boot's card quotes lines of its own
        return [SAID in one for one in render(block).splitlines() if one.startswith(("WORK ", "INFER "))]

    if (arrow(bare) == "" and not bare.response and channels(bare) == [True]
            and arrow(joined) == "" and not joined.response and channels(joined) == [True, True]
            and LAST not in render(bare) and LAST not in render(joined)
            and all(one is not None and one.wait and run.closing(render(one)).splitlines() == ["▶ AWAIT"]
                    for one in (bare_end, joined_end))):
        held("the AWAIT is bare, always", "a lone WORK keeps `=> terminal`, and an INFER behind a CALL "
             "the same, both lines on `terminal`; no name in parentheses, no `=>` on the closing")
    else:
        failures.append(f"  ✗ bare AWAIT                  {arrow(bare)!r} / {arrow(joined)!r} "
                        f"{arrow(bare_end)!r} / {arrow(joined_end)!r} {bare.response!r} "
                        f"said={channels(bare)}/{channels(joined)}")
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
            and pair.channel == language.TOOL_HEREDOC and not pair.next_call
            and _opening(pair_text, "▶ CONTINUE") + _opening(pair_text, "▶ AWAIT") == 0
            and _opening(pair_text, "▌ pp · run t · ") == 1
            and _opening(pair_text, "▌ PAIR") == 1
            and pair_text.count("say it plainly") == 1):
        held("produce and prove fuse legally, B-merged", "same frame: one heading, one "
             "CONSTRAINTS -- the written PROVE rides the block; no closing, the proof's line names its channel")
    else:
        failures.append(f"  ✗ fused pair                  {pair.next_call!r}")
    if "▌ PAIR{1-2/2}" in pair_text:
        held("the elided closing extends the range", "the proof step's heading is held "
             "by the opener -- {1-2/2} covers the whole B-merge")
    else:
        failures.append(f"  ✗ closing range               {pair_text.splitlines()[:1]!r}")
    if (titles(pair_text).count(titled(language.INSTRUCTION)) == 1
            and f"WORK any {SAID}" in pair_text and not pair.response and LAST not in pair_text
            and PROOF_LINE.search(pair_text)):
        held("the real turn collapses", "WORK and its written, briefless PROVE under ONE "
             "INSTRUCTION title -- nothing rides between them any more; a value the tool result "
             "answers asks no last message: the WORK keeps `terminal`, no line is added")
    else:
        failures.append(f"  ✗ turn collapse               "
                        f"{titles(pair_text).count(titled(language.INSTRUCTION))} response={pair.response!r}")

    # --- the bare AWAIT a judged proof opens carries no added line -------------------------------
    printed(env, "t")                    # the WORK said on `terminal`: handed before the proof is judged
    judge = fus_c()
    parked = judge.submit(run.proof_of(pair_text))
    parked_text = judge.rendered(parked) if parked is not None else ""   # the seam an output leaves by
    added = last_line("PAIR")
    if (parked is not None and parked.wait and not parked.response and not parked.command
            and arrow(parked) == "▶ AWAIT" and added not in parked_text and LAST not in parked_text
            and titled(language.INSTRUCTION) not in titles(parked_text)
            and parked.total == pair.total and persistence.awaits_of(run.slot(env, "t")) == persistence.MESSAGE
            and "response-added" not in [one.get("kind") for one in run.trace(env, "t")]):
        held("the bare AWAIT asks no last message",
             "the proof judged, the block that parks the run renders no step and adds no line: no "
             "INSTRUCTION, no `empty` on `response` over the AWAIT; the frame counts its two steps as before "
             "and the stack awaits a message, no `response-added` traced")
    else:
        failures.append(f"  ✗ the added line              response={getattr(parked, 'response', None)!r} "
                        f"{parked_text[-200:]!r} total={getattr(parked, 'total', None)}/{pair.total}")

    # --- no last message is traced where the output leaves -------------------------------------------
    lone = env.write("LONE.md", WITNESS.format(name="LONE", steps="  WORK\n"))
    fus_c().forget()
    teller = fus_c()
    told = teller.start(lone)
    told_text = teller.rendered(told)                         # the seam an output leaves by
    kinds = [one.get("kind") for one in run.trace(env, "t")]
    if (not told.response and SAID in told_text and LAST not in told_text
            and "response" not in kinds and "response-added" not in kinds):
        held("no last message is traced", "a lone WORK keeps `terminal` where the output is rendered: "
             "neither `response` nor `response-added` traced")
    else:
        failures.append(f"  ✗ the response traced         {told.response!r} {kinds}")

    # --- a reading served between two steps stands at the head of their segment ------------------
    env.write("NOTE.md", "a note between steps\n")
    split_doc = env.write("SPLIT.md", "---\nname: SPLIT\nkind: proc\ndescription: a reading between "
                                      "steps\nproc: |\n  INFER\n  SERVE NOTE.md\n  INFER\n---\n"
                                      "say two things\n")
    fus_c().forget()
    split_titles = titles(render(fus_c().start(split_doc)))
    note, asked = titled(language.INFORMATION, "NOTE.md"), titled(language.INSTRUCTION)
    if (split_titles.count(asked) == 1 and split_titles.count(note) == 1
            and split_titles.index(note) < split_titles.index(titled(language.CONTEXT, "SPLIT"))
            < split_titles.index(asked)):
        held("a reading served between two steps stands at the head", "the note the second step brings "
             "reads before the brief of the first; the two lines stand under ONE INSTRUCTION title")
    else:
        failures.append(f"  ✗ the reading between steps   {split_titles}")

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

    # --- segments end on their last step, no closing -----------------------------------------------
    if (_opening(crossed_text, "▌ [") == 2                 # two segment headings, one
            and _opening(crossed_text, "▌ pp · ") == 1     # output heading above them
            and not run.closing(crossed_text)):            # the last step pending: no closing
        held("segments end on their last step", "two headings for two scopes, no closing -- no habit, "
             "nothing delivered: each production was said at its step, the last one pending")
    else:
        failures.append(f"  ✗ bare closing                heads="
                        f"{_opening(crossed_text, '▌ [')} "
                        f"{crossed_text.rstrip().splitlines()[-2:]!r}")

    # --- a § writes `section` with the marked step ------------------------------------------------
    paced = env.write("PACED.md", WITNESS.format(name="PACED", steps="  INFER\n  §\n  INFER\n"))
    fus_c().forget()
    opener = fus_c()
    first = opener.start(paced)
    key = opener.run_id
    said_first = render(first) if first is not None else ""
    after_first = [str(one.get("instruction")).strip() for one in run.trace(env, key) if one.get("kind") == "section"]
    second = env.conductor(key).forward("")
    after_second = sum(1 for one in run.trace(env, key) if one.get("kind") == "section")
    if first is not None and second is not None and after_first == ["INFER"] and after_second == 1:
        held("a § writes `section` with the marked step", "one `section` line naming the INFER it opens after "
             "the first output, none more after the second")
    else:
        failures.append(f"  ✗ the section traced          {(first is not None, second is not None, after_first, after_second)}")
    # the step said before the `§`: the output ends there, the step keeps `terminal`
    if SAID in said_first and LAST not in said_first:
        held("the step before the break keeps `terminal`", "the INFER before the `§` is said on `terminal`: "
             "the output ends on it, no `response`")
    else:
        failures.append(f"  ✗ the step before the break   {said_first[-160:]!r}")

    return 0
