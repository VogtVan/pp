"""Scenario `frontier-asks` -- 1 case(s) (batch la-base-temoin-du-banc, 2026-10-06; the case
of `tests/engine/rendering/principal-word.py` the kit keeps, since `capture_prompt` is the
kit's own key):
- a FINAL under `capture_prompt` asks for `<the principal's next message>` and its note says
  `once the principal replies` -- the engine's word, never `operator`
"""
from __future__ import annotations

from conductor import render


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("word", pin=False)
    made = env.made
    (made / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\ncapture_prompt: true\n---\n", encoding="utf-8")
    (made / "ASK.md").write_text(
        "---\nname: ASK\nkind: proc\ndescription: one step then the frontier\n"
        "proc: |\n  WORK\n  FINAL\n---\nsay it\n", encoding="utf-8")
    asked = env.conductor("t")
    block = asked.start(made / "ASK.md")
    text = render(block)
    closing = "\n".join(text.rstrip().splitlines()[-3:])   # the closing alone
    if ("<the principal's next message>" in block.next_call
            and "(once the principal replies" in closing
            and "operator" not in closing.lower()):
        held("the frontier asks for the principal", "`./pp <key> <the principal's next "
             "message>` and the note `once the principal replies` -- no operator rendered")
    else:
        failures.append(f"  ✗ frontier word               {block.next_call!r} "
                        f"{text.splitlines()[-2:]!r}")
    env.conductor("t").forget()
    return 0
