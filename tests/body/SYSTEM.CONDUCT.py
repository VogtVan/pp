"""engine/system/SYSTEM.CONDUCT.md -- how the agent makes the run advance when it conducts
the run itself: the text it keeps, moved whole out of the engine's common orders and the
card (batch le-document-de-la-conduction; the package switch, batch la-suspension-par-l-agent), compiled after the engine's common orders and
before the card into the standing orders of a run the LLM conducts, and absent from the
standing orders of a run its principal conducts."""
from __future__ import annotations

from tests.harness import SOURCE, body_of, kept_document

# the sentences the document took, each whole -- from the marble, then from the card
MOVED = ("**Call pp before you think.** The laws in force exist only once served",
         "Work begun before the call is work against rules you have not read",
         "Governing rule: the conversation's first command is `./pp -new`",
         "## Mandatory pp use", "The golden rule on calling pp says when",
         "* `CONTINUE`: call back now.",
         "how the drafts are delivered is the base's own section",
         "When conduction applies: principal speaks", "This is the principal's intended rhythm",
         "`CONTINUE`: call exactly what is shown **now**",
         "then call nothing until the principal's own next message",
         "`=> response` (say it, then call with the key alone)",
         "The first call of **every conversation** is `./pp -new`, never bare",
         "./pp <key>                   # ADVANCE",
         "Every answer is conducted: the first call is `-new`",
         "see the standing orders, § Mandatory pp use",
         "Read each chunk whole, where it lands, before the bare call",
         "FINAL may request `<the principal's next message>`",
         "### Host compaction", "the block that STANDS and advances nothing",
         "**chunk** — a piece of an output too long for the harness's **cap**; the bare call serves the next piece.",
         "**closing** — the last line of a block: CONTINUE (call now)",
         "**parenthesis** — a stretch the principal suspends conduction for",
         "**compaction** — the harness summarizing the conversation",
         # the package switch, from the card (la-suspension-par-l-agent): the LLM conducting the
         # run places the principal's word; a run its principal conducts never reads it
         "./pp <key> -disable <pkg>    # one package out of THIS run's play; -enable puts it back",
         "The principal also says which PACKAGES play",
         "every package that REQUIRES it leaves with it",
         "`package.<name>: on|off` at SETTINGS")


def scenario(bench) -> int:
    text = kept_document(SOURCE / "engine", "SYSTEM.CONDUCT").read_text(encoding="utf-8")
    marble = kept_document(SOURCE / "engine", "SYSTEM.COMMON").read_text(encoding="utf-8")
    card = kept_document(SOURCE / "engine", "PP").read_text(encoding="utf-8")
    for phrase in MOVED:
        assert phrase in text, phrase
        assert phrase not in marble and phrase not in card, phrase
    bench.held("the document keeps what it took", f"{len(MOVED)} sentences of the marble and the "
               "card, each whole here and gone from where it was")

    made = bench.shared().made / ".sys"
    llm = (made / "system.md").read_text(encoding="utf-8")
    principal = (made / "system.common.md").read_text(encoding="utf-8")
    body = body_of(kept_document(SOURCE / "engine", "SYSTEM.CONDUCT"))
    head = body_of(kept_document(SOURCE / "engine", "PP"))[:80]
    assert body[:80] in llm and llm.index(body[:80]) < llm.index(head)
    assert body[:80] not in principal and "When conduction applies" not in principal
    bench.held("the LLM's orders carry it, the principal's do not",
               "system.md compiles it before the card; system.common.md does not carry it")

    conductor = bench.shared().conductor("body-advancing")
    rendered = conductor.resume(conductor.boot("BOOT.md"))
    standing = next((text for title, text in rendered.payloads if title.startswith("standing")), "")
    conductor.forget()
    assert "When conduction applies" in standing
    bench.held("the boot serves it", "a run the LLM conducts reads it among its standing orders")
    return 0
