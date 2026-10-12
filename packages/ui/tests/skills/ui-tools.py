"""Scenario `ui-tools` -- what the agent does during a launch, as lines of the transcript (plan ui, batch
les-appels-d-outils), on the bench's `pp-chat` witness replaying the flow of `agent chat --json`:
- a turn reads in the order of the flow: the message, `◇` the conduction of launch 1, `⚙` the call of pp (`pp`, its
  title, `✓`, the size of its result), ONE line of thought (`∴ … thinking ~188 tokens`, the last count), `⚙` the
  `Read` in error (`✗`), a `◀` line of the intermediate words, the line of the steps, the `◀` line of the agent, the
  answer, the verdict; the last words, the same text as the agent's, are not shown twice
- `enter` on the call of pp opens its input (indented) and its result WHOLE; on the `Read`, its error
- `c` hides `⚙`, `∴` and `◇`; the `◀` lines, the answer and the verdict stay
"""
from __future__ import annotations

import re

from tests.harness import support

P = support(__file__, "dialogue")

TURN = "h,i,enter,wait:waiting"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-tools", P.tools_script())
    render = post.render
    sent = ("ag1", "--render", "dialogue", "--size", "140x44")

    # --- the order of a turn with its calls ---------------------------------------------------------
    shown = render(*sent, "--press", "h,i,enter", "--wait", "waiting")
    text = shown.stdout
    rows = text.split("\n")

    def at(pattern: str) -> int:
        return next((n for n, row in enumerate(rows) if re.search(pattern, row)), -1)

    order = [at(r"▶ \d\d:\d\d:\d\d"),
             at(r"◇ \d\d:\d\d:\d\d · launch 1 · "),
             at(r"⚙ \d\d:\d\d:\d\d · launch 1 · pp · \./pp w00001 - · ✓ · \d+ chars"),
             at(r"∴ \d\d:\d\d:\d\d · launch 1 · thinking ~188 tokens"),
             at(r"⚙ \d\d:\d\d:\d\d · launch 1 · Read · /nowhere/file\.md · ✗ · \d+ chars"),
             at(r"◀ \d\d:\d\d:\d\d · launch 1 · \d+ chars · let me read the proof"),
             at(r"· \d\d:\d\d:\d\d · 3 step\(s\)"),
             at(r"◀ \d\d:\d\d:\d\d · launch 1 · 0\.01 USD · \d+ chars · the agent says one"),
             at(r"◇ \d\d:\d\d:\d\d · launch 2 · "),
             at(r"✓ parked")]
    agent_one = [row for row in rows if re.search(r"◀ .*launch 1 .*the agent says one", row)]
    if (shown.returncode == 0 and -1 not in order and order == sorted(order) and len(set(order)) == len(order)
            and text.count("∴") == 1 and "~50 tokens" not in text and len(agent_one) == 1
            and "tool-result" not in text and "words" not in text):
        held("a turn reads with its calls in the order of the flow", f"rows {order}: the message, ◇ launch 1, ⚙ pp ✓, "
             "∴ ~188 tokens (one line), ⚙ Read ✗, ◀ the words, the steps, ◀ the agent (its text once), ◇ launch 2, ✓ parked")
    else:
        failures.append(f"  ✗ order                       rc={shown.returncode} order={order} agent_one={agent_one} "
                        f"{text!r} {shown.stderr[-300:]!r}")

    # --- enter on a call opens its input and its result whole -------------------------------------------
    up = ",".join(["shift+tab"] * 8)                       # from the message line, up to the call of pp
    called = render(*sent, "--press", f"{TURN},{up},enter")
    read_up = ",".join(["shift+tab"] * 6)                  # up to the Read
    erred = render(*sent, "--press", f"{TURN},{read_up},enter")
    if (called.returncode == 0 and '"command": "./pp w00001 -"' in called.stdout and "proof taken" in called.stdout
            and "held 3 codes" in called.stdout and "[esc] close" in called.stdout
            and erred.returncode == 0 and '"file_path": "/nowhere/file.md"' in erred.stdout
            and "File does not exist." in erred.stdout):
        held("a call opens whole", "the call of pp: its input indented (\"command\") and its result on two lines; "
             "the Read: its input and its error")
    else:
        failures.append(f"  ✗ open                        rc={called.returncode}/{erred.returncode} {called.stdout!r} / "
                        f"{erred.stdout!r}")

    # --- c hides the calls and the thought with the conduction ----------------------------------------
    hidden = render(*sent, "--press", f"{TURN},escape,c")
    if (hidden.returncode == 0 and "⚙" not in hidden.stdout and "∴" not in hidden.stdout and "◇" not in hidden.stdout
            and "let me read the proof" in hidden.stdout and "launch 1 · 0.01 USD" in hidden.stdout
            and "the answer" in hidden.stdout and "✓ parked" in hidden.stdout):
        held("c hides the calls and the thought", "after c no ⚙, ∴ nor ◇; the words, the agent's lines, the answer "
             "and the verdict stay")
    else:
        failures.append(f"  ✗ c                           rc={hidden.returncode} {hidden.stdout!r}")
    return 0
