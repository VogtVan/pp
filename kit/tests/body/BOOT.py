"""kit/procs/BOOT.md -- the text it keeps: the root laws a boot puts on screen and
the formats it teaches. Read at the source; B1 and B5 proven in force on the shared
environment (never mutated)."""
from __future__ import annotations

from tests.harness import SOURCE, kept_document


def scenario(bench) -> int:
    text = kept_document(SOURCE / "kit", "BOOT").read_text(encoding="utf-8")
    laws = {
        "B1 says the action scope as action": ("act only within your own member",
                                               "the operator's ask is always in scope"),
        "B4 re-arms the call at every block": ("B4  precede every answer with a tool call",
                                               "the operator requires it"),
        "B5 opens one door at a time": ("open ONE door at a time, only on the operator's GO",),
    }
    for label, phrases in laws.items():
        assert all(phrase in text for phrase in phrases), label
        bench.held(label, " · ".join(phrases)[:70])
    assert "nothing outside your own member" not in text
    bench.held("B1 words positively", "no list of nevers -- the old phrasing is gone")
    # the formats-teach-their-shape case died with BOOT's formats block (batch
    # la-descente-du-kit): the mechanical forms live at language.FORMATS now.

    conductor = bench.shared().conductor("body-boot")
    rendered = conductor.resume(conductor.boot("BOOT.md"))
    codes = {one.code for one in rendered.constraints}
    assert {"B1", "B4", "B5"} <= codes
    conductor.forget()
    bench.held("the root laws reach the boot block", "B1, B4, B5 in force on the shared environment")
    return 0
