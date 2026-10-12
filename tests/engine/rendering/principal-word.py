"""Scenario `principal-word` -- what the engine renders says `the principal`, never
`operator` (plan agent, batch le-mot-du-rendu): the engine's layer speaks its own word,
the base says who the principal is.
- the frontier's ask for the principal's next message is the kit's (`capture_prompt` is its
  key): `bases/kit/tests/engine/frontier-asks.py` keeps it
- the END section reports to the principal
- the exhausted repair bound hands back to the principal
- the doors an install writes name the principal-registered card
- no message literal of the rendering, the closing, the language, the deviation or the
  install says `operator` -- the messages lint's own reader, re-used
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from conductor import render, install
from conductor.core import deviation
from conductor.core.errors import Refusal
from conductor.core.model import Instruction
from tests.harness import PRODUCT_ENGINE
from tests.engine.core.messages import literals

RENDERED = ("rendering/render.py", "execution/blocks.py", "core/language.py",
            "core/deviation.py", "packaging/install.py")


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("word", pin=False)
    made = env.made
    (made / "SETTINGS.md").write_text(          # the engine's own tuning, no pin
        "---\nname: SETTINGS\nkind: doc\n---\n", encoding="utf-8")

    # --- the END reports to the principal --------------------------------------------
    (made / "OVER.md").write_text(
        "---\nname: OVER\nkind: proc\ndescription: one step, no cycle\n"
        "proc: |\n  INFER\n---\nsay it once\n", encoding="utf-8")
    over = env.conductor("e")
    over.start(made / "OVER.md")
    ended = env.conductor("e").submit("")     # a chat production is said there: the bare call closes
    ended_text = render(ended) if ended is not None else ""
    if ("▌ END" in ended_text and "report to the principal" in ended_text
            and "operator" not in ended_text.lower()):
        held("the END reports to the principal", "the conduction is over -- report to the "
             "principal; do not call the tool again")
    else:
        failures.append(f"  ✗ END word                    {ended_text[-200:]!r}")

    # --- the exhausted bound hands back to the principal -------------------------------
    instruction = Instruction(keyword="INFER", argument="")
    deviation.register(instruction, 1)
    try:
        deviation.register(instruction, 1)
        failures.append("  ✗ repair bound                accepted a second miss over a bound of 1")
    except Refusal as refusal:
        if refusal.code == "repair-exhausted" and "the principal has to look at it" in str(refusal):
            held("the exhausted bound hands back to the principal",
                 "`repair-exhausted` -- the principal has to look at it")
        else:
            failures.append(f"  ✗ repair bound word           {refusal!r}")

    # --- the doors name the principal-registered card -------------------------------------
    root = Path(tempfile.mkdtemp(prefix="pp-doors-")) / "ws"
    root.mkdir()
    written = [install.door(root, name) for name in ("CLAUDE.md", "AGENTS.md", "GEMINI.md")]
    doors = [path.read_text(encoding="utf-8") for path in written if path]
    if (len(doors) == 3 and all("principal-registered card" in one for one in doors)
            and not any("operator" in one for one in doors)):
        held("the doors name the principal-registered card", "CLAUDE.md, AGENTS.md and "
             "GEMINI.md written by the install say the card's own word")
    else:
        failures.append(f"  ✗ doors word                  {[one[:80] for one in doors]!r}")

    # --- no rendered message of the engine says operator ---------------------------------
    engine = PRODUCT_ENGINE.parent / "conductor"
    said = [(name, line, text) for name in RENDERED
            for line, text in literals(engine / name) if "operator" in text.lower()]
    if not said:
        held("no rendered message says operator", f"{len(RENDERED)} modules read by the messages "
             "lint's own reader: the closing, the note, the END, the bound, the doors")
    else:
        failures.append(f"  ✗ operator rendered           {said[:4]!r}")
    return 0
