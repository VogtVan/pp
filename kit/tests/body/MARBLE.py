"""kit/system/MARBLE.md -- the standing orders: the text it keeps, compiled into
every instance's system.md and served first at the boot."""
from __future__ import annotations

import re

from tests.harness import SOURCE, body_of, kept_document

GOLDEN = ("**What pp serves, the operator asked for.**",
          "**The operator decides, pp sequences, you infer.**",
          "**A refusal is the operator's tool speaking.**",
          "**What pp writes, only pp writes.**",
          "**pp's machine is pp's alone.**",
          "**A non-ok is better than a sloppy ok.**",
          "**Call pp before you think.**")
PRECEDENCE = "where the `pp` card that follows says otherwise, these orders prevail"
VECTOR = "**vector**, **family** — the address of one piece of work a package tracks"
REFERRAL = "A technical word these orders or the card use is defined in the Glossary at the end of these orders."
GLOSSARY_WORDS = 60     # at least: the entries are read at the source, never listed here
DECLINED = ("Principles, not laws. Each says what the operator wants, why, and what you betray",
            "Never read or write anything under `.pp/.sys/` with your own tools",
            "an output you did not read is a decision you took in their place",
            "Read every pp output whole, in the tool result it lands in",
            "never pipe it (`|`), never send it to a file (`>`, `tee`)",
            "a choice taken in silence is taken from their hands",
            "it guards a state the operator wanted",
            "the script is the operator's hand and leaves a trace",
            "A verdict bought is a debt the operator pays",
            "Work begun before the call is work against rules you have not read",
            "the complete operating contract, under these standing orders",
            "they serve the operator's decisions, never override them",
            "the golden rule on proof applies", "The golden rule on calling pp says when",
            "The card's **“Proof”** binds here", "governed by **“Proof”**",
            # the delivery names each draft (les-noms-a-la-livraison): the separator as the
            # operator wrote it, the names read on the closing
            "each draft opened by three lines — `---`, its name, `---` —",
            "the names being those the closing lists in parentheses, in its order")


def scenario(bench) -> int:
    text = kept_document(SOURCE / "kit", "MARBLE").read_text(encoding="utf-8")
    for phrase in ("Conducted workspace", PRECEDENCE, "## Golden rules",
                   "`CONTINUE`: call back now", "wait for the operator"):
        assert phrase in text, phrase
    assert text.index("# Conducted workspace") < text.index(PRECEDENCE) < text.index("## Golden rules")
    bench.held("the marble opens on the conducted workspace and its precedence",
               "Conducted workspace · these orders prevail over the card · the closings kept")

    positions = [text.index(rule) for rule in GOLDEN]
    assert positions == sorted(positions), positions
    assert positions[-1] < text.index("## Conducted turn")
    for phrase in DECLINED:
        assert phrase in text, phrase
    assert text.count("sloppy ok") == 1 and "The protocol" not in text
    counted = re.search(r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"
                        r"\s+(principles|golden rules)", text, re.IGNORECASE)
    assert counted is None, counted
    golden = text[text.index("## Golden rules"):text.index("## Conducted turn")]
    assert "in the chat" not in golden and "harness itself saves" not in golden
    assert len(golden) <= 1750, len(golden)
    bench.held("the golden rules lead, in their order",
               "the principles under ## Golden rules, before the standing orders, never counted; "
               "each said once, no reference to an absent title")

    compiled = (bench.shared().made / ".sys" / "system.md").read_text(encoding="utf-8")
    card_head = body_of(kept_document(SOURCE / "kit", "PP"))[:80]
    assert "Conducted workspace" in compiled
    assert compiled.index(GOLDEN[0]) < compiled.index(card_head)
    bench.held("the marble compiles into the instance",
               "system.md carries the golden rules ahead of the card on the shared environment")

    # the glossary (batch le-glossaire): the last section of the marble, one entry per word
    # of these orders, of the card or of the texts packages serve at the turn, each used at
    # the source; the opening refers to it
    assert REFERRAL in text and text.index(REFERRAL) < text.index("## Golden rules")
    glossary = text[text.index("## Glossary"):]
    assert text.index("## Mandatory pp use") < text.index("## Glossary") and "\n## " not in glossary[3:]
    card = kept_document(SOURCE / "kit", "PP").read_text(encoding="utf-8")
    served = "\n".join(one.read_text(encoding="utf-8")     # the texts packages serve at the turn
                       for folder in ("overlays", "procs")
                       for one in sorted(SOURCE.glob(f"packages/*/{folder}/*.md")))
    assert VECTOR in glossary and "the id joins it" in glossary
    words = re.findall(r"\*\*([^*]+)\*\*", glossary)
    assert len(words) >= GLOSSARY_WORDS, len(words)
    for word in words:      # both ways: every entry names a word the orders, the card or a served text use
        used = re.compile(r"\b" + re.escape(word) + r"(s|es|ed|d)?\b", re.IGNORECASE)
        assert used.search(text) or used.search(card) or used.search(served), word
    for line in glossary[glossary.index("\n**") + 1:].splitlines():   # one entry per line
        assert line.startswith("**") and " — " in line, line
    # the bound GUARDS the growth, it is not a target (operator word 2026-09-22, the mass
    # relaxed): it leaves room for the words the phase's next batch brings
    assert len(glossary) <= 5300, len(glossary)
    assert compiled.index("## Glossary") < compiled.index(card_head)
    bench.held("the glossary closes the marble and precedes the card",
               f"{len(words)} words, each with its entry and used at the source, "
               f"{len(glossary)} chars; the opening refers to it; compiled before the card")
    return 0
