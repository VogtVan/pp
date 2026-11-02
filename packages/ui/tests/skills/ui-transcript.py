"""Scenario `ui-transcript` -- the transcript of a conversation as LINES of events, on the bench's `pp-chat` witness:
- a turn reads in the order the flow said it: the message, then per launch the conduction's line (`◇`, the launch,
  the block it serves, `parked` on a waiting one, its size), the line of its steps (counted by kind), the agent's
  words as a block, whole, the agent's line (`◀`, the launch, its cost); then the verdict; no fold, no line of pp's
  output in the transcript
- `enter` on a conduction's line opens it WHOLE in an overlay: its 80 lines, each folded to the width, the last one
  read after `end`; `escape` brings the transcript back with the focus on the line (`enter` opens it again)
- the line of a launch's steps opened lists the steps one per line, the refusal among them
- `ctrl+a` then `ctrl+c` copies the transcript, and in the overlay its whole text: the status says how many chars
- three productions in one launch (the script swapped by `use()`): three blocks, in order, the launch's line its
  metadata alone, no answer composed over them
The words as markdown are `ui-transcript-overlays`'s, the folds of `c` and `b` `ui-tools`'s.
"""
from __future__ import annotations

import re

from tests.harness import support

P = support(__file__, "dialogue")

TURN = "i,h,i,enter,wait:waiting"
FIRST = P.LONG.split(" -- ", 1)[0]          # `line 01`: the head of the conduction's first line
LAST = P.LONG.split("\n")[-1]              # its last line, whole


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-transcript", P.long_script())
    render = post.render
    sent = ("ag1", "--render", "dialogue", "--size", "120x40")

    # --- the order of a turn: per launch its conduction, its steps, the agent; the answer, the verdict ------
    shown = render(*sent, "--press", "i,h,i,enter", "--wait", "waiting")
    text = shown.stdout
    rows = text.split("\n")

    def at(pattern: str) -> int:
        return next((n for n, row in enumerate(rows) if re.search(pattern, row)), -1)

    order = [at(r"▶ \d\d:\d\d:\d\d"),
             at(r"◇ \d\d:\d\d:\d\d · launch 1 · BOOT ▸ MEMBER ▸ TURN\{2/4\} \+1 · \d+ chars"),
             at(r"· \d\d:\d\d:\d\d · 3 step\(s\) · launch ×1 · refusal ×1 · repair ×1"),
             at(r"^\s*the agent says one\s*$"),
             at(r"◀ \d\d:\d\d:\d\d · launch 1 · 0\.01 USD\s*$"),
             at(r"◇ \d\d:\d\d:\d\d · launch 2 · BOOT ▸ MEMBER ▸ TURN\{4/4\} \+1 · parked · [\d.]+k chars"),
             at(r"· \d\d:\d\d:\d\d · 1 step\(s\) · block ×1"),
             at(r"^\s*the agent says two\s*$"),
             at(r"◀ \d\d:\d\d:\d\d · launch 2 · 0\.02 USD\s*$"),
             at(r"✓ parked")]
    if (shown.returncode == 0 and -1 not in order and order == sorted(order) and len(set(order)) == len(order)
            and "▌ pp · run" not in text and LAST not in text and "▸ conduction" not in text):
        held("a turn reads in the order of the flow", f"rows {order}: the message, ◇ launch 1 (TURN{{2/4}} +1), "
             "3 step(s), its words, ◀ launch 1, ◇ launch 2 (TURN{4/4} +1 · parked), 1 step(s), its words, ◀ launch 2, "
             "✓ parked; no fold, no line of pp's output")
    else:
        failures.append(f"  ✗ order                       rc={shown.returncode} order={order} {text!r} {shown.stderr[-300:]!r}")

    # --- enter on the second conduction opens it whole; end reads its last line; escape comes back ---------
    to_second = f"{TURN},shift+tab,shift+tab"         # from the message line: the steps of launch 2, ◇ 2 (◀ 2 opens nothing)
    opened = render(*sent, "--press", f"{to_second},enter")
    ended = render(*sent, "--press", f"{to_second},enter,end")
    back = render(*sent, "--press", f"{to_second},enter,end,escape")
    again = render(*sent, "--press", f"{to_second},enter,end,escape,enter")
    wrapped = [row for row in ended.stdout.split("\n") if "a reading served whole" in row and "line " not in row]
    if (opened.returncode == 0 and FIRST in opened.stdout and "launch 2 · BOOT" in opened.stdout
            and "[esc]" in opened.stdout
            and ended.returncode == 0 and LAST in ended.stdout and wrapped
            and back.returncode == 0 and LAST not in back.stdout and "✓ parked" in back.stdout
            and again.returncode == 0 and FIRST in again.stdout):
        held("a conduction opens whole", "enter: the overlay titled `launch 2 · BOOT…`, line 01 on top; end: line 80 "
             f"read, {len(wrapped)} row(s) of folded text; escape: the transcript back; enter again: the same overlay")
    else:
        failures.append(f"  ✗ overlay                     rc={opened.returncode}/{ended.returncode}/{back.returncode} "
                        f"{opened.stdout!r} / {ended.stdout!r} / {back.stdout[:300]!r} / {again.stdout[:300]!r}")

    # --- the steps of launch 1: opened, one per line, the refusal among them --------------------------
    steps = render(*sent, "--press", f"{to_second},shift+tab,enter")   # ◀ 1 opens nothing: the steps of launch 1
    if (steps.returncode == 0 and re.search(r"launch  launch=1 chars=1200", steps.stdout)
            and "refusal  code=budget" in steps.stdout and "repair  n=1" in steps.stdout):
        held("the steps of a launch open one per line", "launch, refusal code=budget, repair n=1")
    else:
        failures.append(f"  ✗ steps                       rc={steps.returncode} {steps.stdout!r} {steps.stderr[-300:]!r}")

    # --- ctrl+a, ctrl+c: the transcript copied; in the overlay, its whole text ----------------------------
    copied = render(*sent, "--press", f"{TURN},ctrl+a,ctrl+c")
    copied_o = render(*sent, "--press", f"{to_second},enter,ctrl+a,ctrl+c")
    said = re.search(r"copied (\d+) chars", copied.stdout)
    said_o = re.search(r"copied (\d+) chars", copied_o.stdout)
    whole = len(P.LONG)
    if (copied.returncode == 0 and said and int(said.group(1)) >= len("the agent says one")
            and copied_o.returncode == 0 and said_o and abs(int(said_o.group(1)) - whole) <= 1):
        held("ctrl+a, ctrl+c copies", f"the transcript: {said.group(0)}; the overlay: {said_o.group(0)} "
             f"(the output is {whole} chars)")
    else:
        failures.append(f"  ✗ copy                        rc={copied.returncode}/{copied_o.returncode} "
                        f"{copied.stdout[-400:]!r} / {copied_o.stdout[-400:]!r}")

    # --- three productions in one launch: three blocks of the agent, no answer over them ---------------
    post.use(P.words_script())
    worded = render(*sent, "--press", "i,h,i,enter", "--wait", "waiting")
    w_rows = worded.stdout.split("\n")
    blocks = [n for one in P.PRODUCTIONS for n, row in enumerate(w_rows) if row.strip() == one]
    metadata = [row for row in w_rows if re.search(r"◀ \d\d:\d\d:\d\d · launch 1 · 0\.01 USD", row)]
    answered = [row for row in w_rows if re.search(r"◀ \d\d:\d\d:\d\d · the answer", row)]
    if (worded.returncode == 0 and len(blocks) == 3 and blocks == sorted(blocks) and not answered
            and len(metadata) == 1 and not any(one in metadata[0] for one in P.PRODUCTIONS)):
        held("each production is a block, said once", f"rows {blocks}: the three productions whole, in order; the "
             "launch's line its metadata alone; no answer composed over them")
    else:
        failures.append(f"  ✗ words unfolded              rc={worded.returncode} blocks={blocks} answered={len(answered)} "
                        f"metadata={metadata} {worded.stdout!r} {worded.stderr[-300:]!r}")
    return 0
