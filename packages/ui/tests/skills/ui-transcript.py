"""Scenario `ui-transcript` -- the transcript of a conversation as LINES of events (plan ui, batch
les-lignes-d-evenement), on the bench's `pp-chat` witness:
- a turn reads in the order the flow said it: the message, then per launch the conduction's line (`◇`, the launch,
  the block it serves, `parked` on a waiting one, its size), the line of its steps (counted by kind), the agent's
  line (`◀`, the launch, its cost, its words); then the answer as markdown -- the table drawn, the code on its own
  line -- and the verdict; no fold, no line of pp's output in the transcript
- `enter` on a conduction's line opens it WHOLE in an overlay: its 80 lines, each folded to the width, the last one
  read after `end`; `escape` brings the transcript back with the focus on the line (`enter` opens it again)
- the line of a launch's steps is bold yellow on a refusal; opened, it lists the steps one per line, the refusal among them
- `c` hides the lines of conduction and of steps, the agent's lines, the answer and the verdict stay, the footer
  says hidden; `c` again brings them back
- `ctrl+a` then `ctrl+c` copies the transcript, and in the overlay its whole text: the status says `copied n chars`
"""
from __future__ import annotations

import re

from tests.harness import support

P = support(__file__, "dialogue")

TURN = "h,i,enter,wait:waiting"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-transcript", P.long_script())
    render = post.render
    sent = ("ag1", "--render", "dialogue", "--size", "120x40")

    # --- the order of a turn: per launch its conduction, its steps, the agent; the answer, the verdict ------
    shown = render(*sent, "--press", "h,i,enter", "--wait", "waiting")
    text = shown.stdout
    rows = text.split("\n")

    def at(pattern: str) -> int:
        return next((n for n, row in enumerate(rows) if re.search(pattern, row)), -1)

    order = [at(r"▶ \d\d:\d\d:\d\d"),
             at(r"◇ \d\d:\d\d:\d\d · launch 1 · BOOT ▸ MEMBER ▸ TURN\{2/4\} \+1 · \d+ chars"),
             at(r"· \d\d:\d\d:\d\d · 3 step\(s\) · launch ×1 · refusal ×1 · repair ×1"),
             at(r"◀ \d\d:\d\d:\d\d · launch 1 · 0\.01 USD · \d+ chars · the agent says one"),
             at(r"◇ \d\d:\d\d:\d\d · launch 2 · BOOT ▸ MEMBER ▸ TURN\{4/4\} \+1 · parked · [\d.]+k chars"),
             at(r"· \d\d:\d\d:\d\d · 1 step\(s\) · block ×1"),
             at(r"◀ \d\d:\d\d:\d\d · launch 2 · 0\.02 USD · \d+ chars · the agent says two"),
             at(r"◀ \d\d:\d\d:\d\d · the answer"),
             at(r"✓ parked")]
    if (shown.returncode == 0 and -1 not in order and order == sorted(order) and len(set(order)) == len(order)
            and "▌ pp · run" not in text and "line 80" not in text and "▸ conduction" not in text
            and "[c] conduction: shown" in text):
        held("a turn reads in the order of the flow", f"rows {order}: the message, ◇ launch 1 (TURN{{2/4}} +1), "
             "3 step(s), ◀ launch 1, ◇ launch 2 (TURN{4/4} +1 · parked), 1 step(s), ◀ launch 2, the answer, ✓ parked; "
             "no fold, no line of pp's output")
    else:
        failures.append(f"  ✗ order                       rc={shown.returncode} order={order} {text!r} {shown.stderr[-300:]!r}")

    # --- the answer is markdown --------------------------------------------------------------------
    md = P.Post(bench, "ui-transcript-md", P.markdown_script()).render(*sent, "--press", "h,i,enter",
                                                                         "--wait", "waiting")
    if (md.returncode == 0 and re.search(r"[│┃].*step.*[│┃].*state", md.stdout) and re.search(r"[─━]{3}", md.stdout)
            and re.search(r"^\W*print\(\"hello\"\)", md.stdout, re.M)):
        held("the answer reads as markdown", "the table drawn (step | state), print(\"hello\") on its line")
    else:
        failures.append(f"  ✗ markdown                    rc={md.returncode} {md.stdout!r} {md.stderr[-300:]!r}")

    # --- enter on the second conduction opens it whole; end reads its last line; escape comes back ---------
    to_second = f"{TURN},shift+tab,shift+tab,shift+tab"         # from the message line: ◀ 2, its steps, ◇ 2
    opened = render(*sent, "--press", f"{to_second},enter")
    ended = render(*sent, "--press", f"{to_second},enter,end")
    back = render(*sent, "--press", f"{to_second},enter,end,escape")
    again = render(*sent, "--press", f"{to_second},enter,end,escape,enter")
    wrapped = [row for row in ended.stdout.split("\n") if "a reading served whole" in row and "line " not in row]
    if (opened.returncode == 0 and "line 01 of the output" in opened.stdout and "launch 2 · BOOT" in opened.stdout
            and "[esc] close" in opened.stdout
            and ended.returncode == 0 and "line 80 -- the end of the output" in ended.stdout and wrapped
            and back.returncode == 0 and "line 80" not in back.stdout and "✓ parked" in back.stdout
            and again.returncode == 0 and "line 01 of the output" in again.stdout):
        held("a conduction opens whole", "enter: the overlay titled `launch 2 · BOOT…`, line 01 on top; end: line 80 "
             f"read, {len(wrapped)} row(s) of folded text; escape: the transcript back; enter again: the same overlay")
    else:
        failures.append(f"  ✗ overlay                     rc={opened.returncode}/{ended.returncode}/{back.returncode} "
                        f"{opened.stdout!r} / {ended.stdout!r} / {back.stdout[:300]!r} / {again.stdout[:300]!r}")

    # --- the steps of launch 1: opened, one per line, the refusal among them --------------------------
    steps = render(*sent, "--press", f"{to_second},shift+tab,shift+tab,enter")
    if (steps.returncode == 0 and re.search(r"launch  launch=1 chars=1200", steps.stdout)
            and "refusal  code=budget" in steps.stdout and "repair  n=1" in steps.stdout):
        held("the steps of a launch open one per line", "launch, refusal code=budget, repair n=1")
    else:
        failures.append(f"  ✗ steps                       rc={steps.returncode} {steps.stdout!r} {steps.stderr[-300:]!r}")

    # --- c hides the lines of conduction and of steps, c brings them back ---------------------------------
    hidden = render(*sent, "--press", f"{TURN},escape,c")
    shown_again = render(*sent, "--press", f"{TURN},escape,c,c")
    if (hidden.returncode == 0 and "◇" not in hidden.stdout and "step(s)" not in hidden.stdout
            and "launch 1 · 0.01 USD" in hidden.stdout and "the answer" in hidden.stdout and "✓ parked" in hidden.stdout
            and "[c] conduction: hidden" in hidden.stdout
            and shown_again.returncode == 0 and shown_again.stdout.count("◇") == 2
            and "3 step(s)" in shown_again.stdout and "[c] conduction: shown" in shown_again.stdout):
        held("c hides the conduction and the steps", "after c no ◇ nor step(s), the agent's lines, the answer and the "
             "verdict stay, the footer says hidden; after c again both ◇ and the steps are back")
    else:
        failures.append(f"  ✗ c                           rc={hidden.returncode} {hidden.stdout!r} / {shown_again.stdout!r}")

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
    return 0
