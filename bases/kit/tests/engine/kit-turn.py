"""Scenario `kit-turn` -- the shape of the kit's turn:
- the positions: the bare kit turn goes WORK to AWAIT, no block at an empty position, no NEXT
  table; a neutral witness at each position plays in order, begin before the work, end after it
- the productions at their step: the boot asks its table `=> response`, the turn its work
  `=> response`, the frontier closes on a bare `▶ AWAIT` -- nothing kept for a delivery; the
  bare kit turn owes no checkpoint: its written PROVE resolves on a line, the AWAIT bare
- the words first: under a law of production at `turn.begin` (BEGIN, BG1) the first output
  carries the CAPABILITIES table, BEGIN's line and the TURN's WORK, each `=> response` with its
  document named, the ask section under the WORK, and closes on a bare CONTINUE; the next bare
  call renders the checkpoint `[BG1]` alone, the AWAIT after its proof; the second exchange
  keeps the shape, the ask section without the TURN's brief
"""
from __future__ import annotations

import json
import re

from conductor import compiling, render
from tests.harness import cli, support

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
ASK = "▌ NEXT INSTRUCTION CONTEXT — the ask"
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
    if ("INFER table => response" in stream and "WORK any => response" in stream
            and final_lines == ["▶ AWAIT"] and "ephemeral" not in stream):
        held("the kit's turn says its productions at their step", "`INFER table => response` at the "
             "boot, `WORK any => response` at the turn, `▶ AWAIT` bare")
    else:
        failures.append(f"  ✗ kit channels                {final_lines!r} "
                        f"table={'INFER table => response' in stream} work={'WORK any => response' in stream}")

    turn = run[len(outputs):]                  # the CAPABILITIES table answered: WORK to AWAIT
    final = turn[-1] if turn else None
    if (turn and all(one.output != "proof" for one in turn) and "▶ AWAIT" in texts[-1]
            and not final.judged
            and "no law of production in force" in stream
            and not any(one.section == "production" for one in final.constraints)):
        held("the kit turn owes no checkpoint",
             "no proof block from WORK to AWAIT: the TURN's written PROVE resolves on a line "
             "saying no law of production is in force")
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
                   and any(one.endswith("(CAPABILITIES)") and "=> response" in one for one in lines)
                   and any(one.endswith("(BEGIN)") and "=> response" in one for one in lines)
                   and any(one.startswith("WORK any => response") and one.endswith("(TURN)") for one in lines)
                   and ASK in text and text.index(ASK) > text.index("(BEGIN)")
                   and not any(one.startswith("INFER proof") for one in lines)
                   and tail[:2] == ["▶ CONTINUE", f"./pp {key}"])
    if words_first:
        held("(a) the boot lets the agent speak first", f"run {key}: three `=> response` steps named "
             "(CAPABILITIES, BEGIN, TURN), the ask section under the WORK, a bare CONTINUE, no proof asked")
    else:
        failures.append(f"  ✗ (a) words first             rc={first.returncode} key={key!r} lines={lines} "
                        f"ask={ASK in text} tail={tail[:3]}")

    proving = cli(env.engine, key, cwd=env.root) if key else None
    proof_tail = _closing(proving.stdout) if proving else []
    judged = (cli(env.engine, key, "-", cwd=env.root,
                  stdin=json.dumps([{"code": "BG1", "evidence": "begin 00:00:00", "verdict": "ok"}]))
              if proving else None)
    if (proving is not None and proving.returncode == 0 and "INFER proof [BG1]" in proving.stdout
            and proof_tail[:2] == ["▶ CONTINUE", f"./pp {key} -"] and "=> response" not in proving.stdout
            and judged is not None and judged.returncode == 0 and "▶ AWAIT" in judged.stdout):
        held("(b) the checkpoint comes one block later", "the bare call renders `INFER proof [BG1]` with "
             "its heredoc command and no response step; judged, the AWAIT follows")
    else:
        failures.append(f"  ✗ (b) the checkpoint          rc={proving and proving.returncode} "
                        f"{(proving.stdout if proving else '')[-300:]!r} judged={judged and judged.returncode}")

    second = cli(env.engine, key, "again", cwd=env.root) if key else None
    text2 = second.stdout if second else ""
    lines2 = _instructions(text2)
    if (second is not None and second.returncode == 0 and ASK in text2
            and "NEXT INSTRUCTION CONTEXT — TURN" not in text2
            and any(one.startswith("WORK any => response") and one.endswith("(TURN)") for one in lines2)
            and not any(one.startswith("INFER proof") for one in lines2)
            and _closing(text2)[:2] == ["▶ CONTINUE", f"./pp {key}"]):
        held("(c) the second exchange keeps the shape", "the ask section without the TURN's brief, the "
             "WORK named, the proof on the next call")
    else:
        failures.append(f"  ✗ (c) the second exchange     rc={second and second.returncode} ask={ASK in text2} "
                        f"brief={'NEXT INSTRUCTION CONTEXT — TURN' in text2} lines={lines2} "
                        f"tail={_closing(text2)[:3]}")
    return 0
