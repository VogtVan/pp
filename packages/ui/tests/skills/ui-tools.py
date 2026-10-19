"""Scenario `ui-tools` -- what the agent does during a launch, as lines of the transcript (plan ui, batch
les-appels-d-outils), on the bench's `pp-chat` witness replaying the flow of `agent chat --json`:
- a turn reads in the order of the flow: the message, `◇` the conduction of launch 1, `⚙` the call of pp (`pp`, its
  title, `✓`, the size of its result), ONE line of thought (`∴ … thinking ~188 tokens`, the last count), `⚙` the
  `Read` in error (`✗`), the line of the steps, then each words of the launch as a block, once, then the `◀` line of
  the launch's end, the verdict
- `enter` on the call of pp opens its input (indented) and its result WHOLE; on the `Read`, its error
- `c` hides `∴` and `◇` and the steps, the calls stay; `b` hides the calls (batch les-bascules-du-dialogue), the
  conduction stays; `c,b` hides both; `b,b` brings the calls back; the words, the `◀` lines and the verdict stay
- the footer says each toggle's state: its `[c]` entry changes after `c`, its `[b]` entry after `b` and comes back
  after `b,b`
"""
from __future__ import annotations

import re

from tests.harness import support

P = support(__file__, "dialogue")

TURN = "i,h,i,enter,wait:waiting"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-tools", P.tools_script())
    render = post.render
    sent = ("ag1", "--render", "dialogue", "--size", "140x44")

    # --- the order of a turn with its calls ---------------------------------------------------------
    shown = render(*sent, "--press", "i,h,i,enter", "--wait", "waiting")
    text = shown.stdout
    rows = text.split("\n")

    def at(pattern: str) -> int:
        return next((n for n, row in enumerate(rows) if re.search(pattern, row)), -1)

    order = [at(r"▶ \d\d:\d\d:\d\d"),
             at(r"◇ \d\d:\d\d:\d\d · launch 1 · "),
             at(r"⚙ \d\d:\d\d:\d\d · launch 1 · pp · \./pp w00001 - · ✓ · \d+ chars"),
             at(r"∴ \d\d:\d\d:\d\d · launch 1 · thinking ~188 tokens"),
             at(r"⚙ \d\d:\d\d:\d\d · launch 1 · Read · /nowhere/file\.md · ✗ · \d+ chars"),
             at(r"· \d\d:\d\d:\d\d · 3 step\(s\)"),
             at(r"^\s*let me read the proof\s*$"),
             at(r"^\s*the agent says one\s*$"),
             at(r"◀ \d\d:\d\d:\d\d · launch 1 · 0\.01 USD\s*$"),
             at(r"◇ \d\d:\d\d:\d\d · launch 2 · "),
             at(r"✓ parked")]
    agent_one = [row for row in rows if "the agent says one" in row]
    if (shown.returncode == 0 and -1 not in order and order == sorted(order) and len(set(order)) == len(order)
            and text.count("∴") == 1 and "~50 tokens" not in text and len(agent_one) == 1
            and "tool-result" not in text and "words" not in text):
        held("a turn reads with its calls in the order of the flow", f"rows {order}: the message, ◇ launch 1, ⚙ pp ✓, "
             "∴ ~188 tokens (one line), ⚙ Read ✗, the steps, the two words (each once), ◀ the launch's end, ◇ launch 2, "
             "✓ parked")
    else:
        failures.append(f"  ✗ order                       rc={shown.returncode} order={order} agent_one={agent_one} "
                        f"{text!r} {shown.stderr[-300:]!r}")

    # --- enter on a call opens its input and its result whole -------------------------------------------
    up = ",".join(["shift+tab"] * 5)                       # from the message line, up to the call of pp
    called = render(*sent, "--press", f"{TURN},{up},enter")
    read_up = ",".join(["shift+tab"] * 3)                  # up to the Read (◀ 2 and ◀ 1 open nothing)
    erred = render(*sent, "--press", f"{TURN},{read_up},enter")
    if (called.returncode == 0 and '"command": "./pp w00001 -"' in called.stdout and "proof taken" in called.stdout
            and "held 3 codes" in called.stdout and "[esc]" in called.stdout
            and erred.returncode == 0 and '"file_path": "/nowhere/file.md"' in erred.stdout
            and "File does not exist." in erred.stdout):
        held("a call opens whole", "the call of pp: its input indented (\"command\") and its result on two lines; "
             "the Read: its input and its error")
    else:
        failures.append(f"  ✗ open                        rc={called.returncode}/{erred.returncode} {called.stdout!r} / "
                        f"{erred.stdout!r}")

    # --- c, b, both, b twice; the footer's entries follow the toggles --------------------------------------
    rest, c, b, cb, bb = (render(*sent, "--press", f"{TURN},escape" + keys) for keys in ("", ",c", ",b", ",c,b", ",b,b"))
    stays = ("let me read the proof", "launch 1 · 0.01 USD", "the agent says two", "✓ parked")
    if (all(one.returncode == 0 for one in (rest, c, b, cb, bb))
            and "⚙" in rest.stdout and "◇" in rest.stdout
            and not any(glyph in c.stdout for glyph in ("◇", "step(s)", "∴")) and "⚙" in c.stdout
            and all(word in c.stdout for word in stays)
            and "⚙" not in b.stdout and all(one in b.stdout for one in ("◇", "step(s)", "∴", *stays))
            and "⚙" not in cb.stdout and "◇" not in cb.stdout and "the agent says two" in cb.stdout
            and "⚙" in bb.stdout):
        held("c and b fold one class each", "c: no ◇, steps nor ∴, the ⚙ stay; b: no ⚙, the conduction stays; c,b: "
             "neither; b,b: the calls back; the words, the launches' lines and the verdict stay")
    else:
        failures.append(f"  ✗ toggles                     {c.stdout!r} / {b.stdout!r} / {cb.stdout[-800:]!r}")
    entries = {name: (P.entry_of(done.stdout, "c"), P.entry_of(done.stdout, "b"))
               for name, done in (("rest", rest), ("c", c), ("b", b), ("bb", bb))}
    if (all(one[0] and one[1] for one in entries.values())
            and entries["c"][0] != entries["rest"][0] and entries["c"][1] == entries["rest"][1]
            and entries["b"][1] != entries["rest"][1] and entries["b"][0] == entries["rest"][0]
            and entries["bb"] == entries["rest"]):
        held("the footer says each toggle's state", f"[c] changes after c alone, [b] after b alone and comes back "
             f"after b,b: {entries['rest']} -> c {entries['c'][0]!r}, b {entries['b'][1]!r}")
    else:
        failures.append(f"  ✗ footer states               {entries}")
    return 0
