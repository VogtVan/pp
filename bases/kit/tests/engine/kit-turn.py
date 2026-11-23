"""Scenario `kit-turn` -- the shape of the kit's turn:
- the positions: the bare kit turn goes WORK to AWAIT, no block at an empty position, no NEXT
  table; a neutral witness at each position plays in order, begin before the work, end after it
- the productions at their step: the boot asks its table `=> terminal`, the turn its work
  `=> terminal`, the frontier closes on a bare `▶ AWAIT` and no line goes `=> response` --
  nothing kept for a delivery; the
  bare kit turn owes no checkpoint: its written PROVE resolves on a line, the AWAIT bare
- the proof in the output: under a law of production at `turn.begin` (BEGIN, BG1) the first
  output carries MEMBER's presentation, the CAPABILITIES table, BEGIN's line and the TURN's WORK,
  each `=> terminal` with its document named, the ask section under the WORK, then the checkpoint
  `[BG1]` on the heredoc channel, no closing; each print the output names is answered by the
  call due next -- the next print, then the proof's heredoc --, the AWAIT after the proof, no
  line `=> response`; the second exchange keeps the shape, the ask section without the TURN's
  brief
"""
from __future__ import annotations

import json
import re

from conductor.core import messages
from conductor import Conductor, compiling, render
from conductor.core import language
from tests.harness import cli, support, titled, traced

SAID = f"=> {language.TERMINAL}"       # a step said while the work goes on
RESPONSE = f"=> {language.RESPONSE}"   # the channel no step goes by

kit = support(__file__, "kit")

NOTE = """---
name: {name}
kind: proc
description: a witness of the {socket} position
attach: {socket}
proc: |
  HOOK {lower}.read
---

{name} says hi
"""
KEY = re.compile(r"run ([0-9a-f]{6})")
BEGIN = ("---\nname: BEGIN\nkind: proc\ndescription: a contributor at the turn's beginning\n"
         "attach: turn.begin\noutput: any\nconstraints.production: |\n"
         "  BG1  the opening line says begin and the hour, nothing else.\nproc: |\n  INFER\n---\n\n"
         "Before the work: say ONE line that opens on begin and gives the hour the block says.\n")
ASK = titled(language.CONTEXT, "the ask")
FUSED = "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: max\nmax_harness_tool_output: 200000\n---\n"   # every yield fused, one output


def _closing(text: str) -> list[str]:
    """-> the lines of an output from its closing marker on."""
    lines = text.splitlines()
    at = max((i for i, one in enumerate(lines) if one.startswith("▶ ")), default=len(lines))
    return lines[at:]


def _whole(env, first) -> str:
    """-> the output whole: a boot cut at the cap continues on the bare keyed call."""
    text, key = first.stdout, (KEY.search(first.stdout).group(1) if KEY.search(first.stdout) else "")
    for _ in range(12):
        tail = _closing(text)
        if not key or not tail or "a reading continues" not in tail[-1]:
            break
        text = text + "\n" + cli(env.engine, key, cwd=env.root).stdout
    return text


def _instructions(text: str) -> list[str]:
    """-> the instruction lines of an output that name a channel."""
    return [line for line in text.splitlines()
            if line.startswith(("WORK ", "INFER ", "PICK ")) and "=>" in line]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- the bare kit turn: WORK to AWAIT, nothing at the empty positions -------------
    bare = bench.env("turn-bare")
    opener = bare.conductor("t")
    seen = kit.drive(bare, opener.start(opener.boot("TURN.md")))
    texts = [render(one) for one in seen]
    if (seen and seen[0].document == "TURN" and seen[0].instruction.keyword == "WORK"
            and "▶ AWAIT" in texts[-1]
            and all(one.document == "TURN" for one in seen)
            and all("says hi" not in text for text in texts)
            and all("| thread" not in text and "NEXT" not in one.stack
                    for one, text in zip(seen, texts))):
        held("the bare turn goes WORK to AWAIT", "empty positions render no block, "
             "no NEXT table rides the closing")
    else:
        failures.append(f"  ✗ bare turn                    {[one.stack for one in seen]!r}")

    # --- a neutral witness at each position: begin before the work, end after it ------
    heard = bench.env("turn-heard")
    heard.write("procs/BEGIN.md", NOTE.format(name="BEGIN", socket="turn.begin", lower="begin"))
    heard.write("procs/END.md", NOTE.format(name="END", socket="turn.end", lower="end"))
    compiling.build_tools(heard.made)
    opener = heard.conductor("t")
    seen = kit.drive(heard, opener.start(opener.boot("TURN.md")))
    texts = [render(one) for one in seen]
    stream = "\n".join(texts)
    at_work = next((i for i, one in enumerate(seen)
                    if one.instruction is not None and one.instruction.keyword == "WORK"), None)
    at_begin = next((i for i, text in enumerate(texts) if "BEGIN says hi" in text), None)
    at_end = next((i for i, text in enumerate(texts) if "END says hi" in text), None)
    if (at_work is not None and at_begin is not None and at_end is not None
            and at_begin <= at_work < at_end and "▶ AWAIT" in texts[-1]
            and stream.find("BEGIN says hi") < stream.find("END says hi")):
        held("the positions carry their witnesses", "BEGIN plays before the work, "
             "END after it, the frontier still closes")
    else:
        failures.append(f"  ✗ witnessed turn               begin={at_begin} work={at_work} "
                        f"end={at_end}")

    # --- a vanilla run, boot to frontier: the productions at their step ---------------
    vanilla = bench.env("vanilla")
    outputs = kit.boot(vanilla)
    run = outputs[:-1] + kit.drive(vanilla, outputs[-1])
    texts = [render(one) for one in run]
    stream = "\n".join(texts)
    final_lines = [line for line in texts[-1].splitlines() if line.startswith("▶ ")]
    table, work = f"INFER table => {language.TERMINAL}", f"WORK any => {language.TERMINAL}"
    if (table in stream and work in stream and RESPONSE not in stream
            and final_lines == ["▶ AWAIT"] and "ephemeral" not in stream):
        held("the kit's turn says its productions at their step", f"`{table}` at the boot and `{work}` at the "
             "turn, where the bare call follows each; the `▶ AWAIT` that parks the run stands bare, no line "
             "goes `=> response`")
    else:
        failures.append(f"  ✗ kit channels                {final_lines!r} "
                        f"table={table in stream} work={work in stream}")

    turn = run[len(outputs):]                  # the CAPABILITIES table answered: WORK to AWAIT
    final = turn[-1] if turn else None
    if (turn and all(one.output != "proof" for one in turn) and "▶ AWAIT" in texts[-1]
            and not final.judged
            and messages.nothing_in_force() not in stream
            and messages.nothing_in_force() in [one.get("said") for one in traced(vanilla, "t")
                                                 if one.get("kind") == "prove-idle"]
            and not any(one.section == "production" for one in final.constraints)):
        held("the kit turn owes no checkpoint",
             "no proof block from WORK to AWAIT: the TURN's written PROVE resolves without a line, "
             "its trace saying no law of production is in force")
    else:
        failures.append(f"  ✗ kit checkpoint             {[(one.document, one.output) for one in turn]!r} "
                        f"{final and final.wait!r}")
    vanilla.conductor("t").forget()

    # --- the words first: a law of production at `turn.begin` -------------------------
    env = bench.env("words-first")
    env.write("SETTINGS.md", FUSED)
    env.write("procs/BEGIN.md", BEGIN)
    first = cli(env.engine, "-new", "bonjour", cwd=env.root)
    key = KEY.search(first.stdout).group(1) if KEY.search(first.stdout) else ""
    text = _whole(env, first)
    lines = _instructions(text)
    tail = _closing(text)
    words_first = (first.returncode == 0 and key
                   and any(one.endswith("(MEMBER)") and SAID in one for one in lines)
                   and any(one.endswith("(CAPABILITIES)") and SAID in one for one in lines)
                   and any(one.endswith("(BEGIN)") and SAID in one for one in lines)
                   and any(one.startswith(f"WORK any {SAID}") and one.endswith("(TURN)") for one in lines)
                   and ASK in text and text.index(ASK) > text.index("(BEGIN)")
                   and any(one.startswith("INFER proof [BG1]") and one.endswith("(TURN)")
                           and f"=> {language.TOOL_HEREDOC}" in one for one in lines)
                   and not tail)
    if words_first:
        held("(a) the proof closes the boot's output", f"run {key}: four `=> terminal` steps named "
             "(MEMBER, CAPABILITIES, BEGIN, TURN), the ask section under the WORK, then `INFER proof [BG1]` on the "
             "heredoc channel, no closing")
    else:
        failures.append(f"  ✗ (a) words first             rc={first.returncode} key={key!r} lines={lines} "
                        f"ask={ASK in text} tail={tail[:3]}")

    names = [one.rsplit("(", 1)[-1].rstrip(")") for one in lines if SAID in one] if key else []
    nexts = ([messages.next_print(name) for name in names[1:]]
             + [messages.next_value("TURN", key, piped=True)])
    printed = [cli(env.engine, key, "-print", name, "-", cwd=env.root, stdin=f"{name} said\n")
               for name in names]
    judged = (cli(env.engine, key, "-", cwd=env.root,
                  stdin=json.dumps([{"code": "BG1", "evidence": "begin 00:00:00", "verdict": "ok"}]))
              if printed else None)
    if (printed and all(one.returncode == 0 and one.stdout.strip() == messages.printed("more", due)
                        for one, due in zip(printed, nexts))
            and judged is not None and judged.returncode == 0 and "▶ AWAIT" in judged.stdout
            and RESPONSE not in judged.stdout):
        held("(b) the prints, then the proof", f"the {len(names)} prints the output names ({', '.join(names)}), "
             "each answered by the call due next, the last by the proof's heredoc; the proof judged, the "
             "AWAIT follows, no line `=> response`")
    else:
        failures.append(f"  ✗ (b) the prints and the proof names={names} {[(one.returncode, one.stdout.strip()[:80]) for one in printed]} "
                        f"judged={judged and (judged.returncode, judged.stdout[-300:])!r}")

    second = cli(env.engine, key, "again", cwd=env.root) if key else None
    text2 = second.stdout if second else ""
    lines2 = _instructions(text2)
    if (second is not None and second.returncode == 0 and ASK in text2
            and messages.titled(language.CONTEXT, "TURN") not in text2
            and any(one.startswith(f"WORK any {SAID}") and one.endswith("(TURN)") for one in lines2)
            and any(one.startswith("INFER proof [BG1]") for one in lines2)
            and not _closing(text2)):
        held("(c) the second exchange keeps the shape", "the ask section without the TURN's brief, the "
             "WORK named, the proof in the same output")
    else:
        failures.append(f"  ✗ (c) the second exchange     rc={second and second.returncode} ask={ASK in text2} "
                        f"brief={messages.titled(language.CONTEXT, 'TURN') in text2} lines={lines2} "
                        f"tail={_closing(text2)[:3]}")
    return 0
