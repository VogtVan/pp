"""bases/kit/procs/BOOT.md -- the text it keeps: the root laws a boot puts on screen and
the formats it teaches. Read at the source; B1 and B5 proven in force on the shared
environment (never mutated). B4 is gone (batch la-suspension-par-l-agent, on the operator's
word): the call before every answer is the LLM's own rule, `SYSTEM.CONDUCT` § Advancing, and a
run its principal conducts never reads it."""
from __future__ import annotations

from tests.harness import SOURCE, kept_document


def scenario(bench) -> int:
    text = kept_document(SOURCE / "bases" / "kit", "BOOT").read_text(encoding="utf-8")
    laws = {
        "B1 says the action scope as action": ("act only within your own member",
                                               "the operator's ask is always in scope"),
        "B5 opens one door at a time": ("open ONE door at a time, only on the operator's GO",),
    }
    for label, phrases in laws.items():
        assert all(phrase in text for phrase in phrases), label
        bench.held(label, " · ".join(phrases)[:70])
    assert "nothing outside your own member" not in text
    assert "B4" not in text and "precede every answer with a tool call" not in text
    bench.held("B4 is gone", "the call before every answer lives at SYSTEM.CONDUCT § Advancing alone")
    bench.held("B1 words positively", "no list of nevers -- the old phrasing is gone")
    # the formats-teach-their-shape case died with BOOT's formats block (batch
    # la-descente-du-kit): the mechanical forms live at language.FORMATS now.

    conductor = bench.shared().conductor("body-boot")
    rendered = conductor.resume(conductor.boot("BOOT.md"))
    codes = {one.code for one in rendered.constraints}
    assert {"B1", "B5"} <= codes and "B4" not in codes
    conductor.forget()
    bench.held("the root laws reach the boot block", "B1, B5 in force on the shared environment, no B4")
    return 0
