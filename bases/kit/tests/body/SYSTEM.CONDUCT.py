"""bases/kit/system/SYSTEM.CONDUCT.md -- the kit's conducted turn, for a run the LLM conducts
alone: the three steps, the call each block names, the parenthesis, the closings that make the
agent call pp -- compiled into `system.md` after the kit's `SYSTEM.COMMON.md`, absent from
`system.common.md`."""
from __future__ import annotations

from tests.harness import SOURCE, body_of, kept_document

PHRASES = ("## Conducted turn", "operator sends a chat message",
           "run the exact pp command shown",
           "follow pp instructions until told to stop",
           "otherwise wait for the next operator message",
           "`pp off` opens a parenthesis", "`pp on` closes it",
           "A parenthesis is never a closure",
           "as the standing orders' **“Parenthesis”** says",
           "* `CONTINUE`: call back now.", "* `END`: stop conduction.")
GONE = ("as the card's", "* `FINAL`")    # the parenthesis is the orders' section; FINAL is COMMON


def scenario(bench) -> int:
    path = kept_document(SOURCE / "bases" / "kit", "SYSTEM.CONDUCT")
    text = path.read_text(encoding="utf-8")
    for phrase in PHRASES:
        assert phrase in text, phrase
    for phrase in GONE:
        assert phrase not in text, phrase
    bench.held("the kit's turn stands in its CONDUCT", "the three steps, the parenthesis "
               "pointing at the standing orders, CONTINUE and END")

    made = bench.shared().made / ".sys"
    llm = (made / "system.md").read_text(encoding="utf-8")
    common = (made / "system.common.md").read_text(encoding="utf-8")
    head = body_of(path)[:60]
    precision = body_of(kept_document(SOURCE / "bases" / "kit", "SYSTEM.COMMON"))[:60]
    assert head in llm and llm.index(precision) < llm.index(head)
    lines = [line.strip() for line in body_of(path).splitlines() if len(line.strip()) >= 20]
    leaked = [line for line in lines if line in common]
    assert not leaked, leaked
    bench.held("the LLM's orders carry it, the principal's do not",
               f"system.md after the kit's COMMON; none of its {len(lines)} lines in system.common.md")
    return 0
