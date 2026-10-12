"""engine/system/SYSTEM.COMMON.md -- the standing orders of the ENGINE that hold in both
conduction modes: the text it keeps, written on the word `principal` and naming no base,
compiled first into both marbles and served at the boot; the engine's card closes the
engine's section, and the base's own precision follows it."""
from __future__ import annotations

import re

from tests.harness import SOURCE, body_of, kept_document

GOLDEN = ("**What pp serves, the principal asked for.**",
          "**The principal decides, pp sequences, you infer.**",
          "**A refusal is the principal's tool speaking.**",
          "**What pp writes, only pp writes.**",
          "**pp's machine is pp's alone.**",
          "**A non-ok is better than a sloppy ok.**")
PRECEDENCE = "where the `pp` card that follows says otherwise, these orders prevail"
VECTOR = "**vector**, **family** — the address of one piece of work a package tracks"
PRINCIPAL = "**principal** — the one a run answers to"
REFERRAL = "A technical word these orders or the card use is defined in the Glossary at the end of these orders."
GLOSSARY_WORDS = 60     # at least: the entries are read at the source, never listed here
DECLINED = ("Principles, not laws. Each says what the principal wants, why, and what you betray",
            "Never read or write anything under `.pp/.sys/` with your own tools",
            "an output you did not read is a decision you took in their place",
            "Read every pp output whole, in the tool result it lands in",
            "never pipe it (`|`), never send it to a file (`>`, `tee`)",
            "a choice taken in silence is taken from their hands",
            "it guards a state the principal wanted",
            "the script is the principal's hand and leaves a trace",
            "A verdict bought is a debt the principal pays",
            "the complete operating contract, under these standing orders",
            "they serve the principal's decisions, never override them",
            "the golden rule on proof applies",
            "The card's **“Proof”** binds here", "governed by **“Proof”**",
            # the engine's own diagnostics (le-diagnostic-au-bloc): what the agent does with
            # a DIAGNOSTIC section is the engine's layer to say, under any base
            "A `DIAGNOSTIC` section is pp telling you that something is wrong with the conduction itself",
            "a `critical` one comes before any work")
DIAGNOSTIC = "**diagnostic** — pp saying the conduction itself is at fault"
# the sentences that name the operator's chat turn moved to the kit's precision:
# the engine's layer never says who the principal is
GONE = ("operator", "sends a chat message", "pp off", "one final chat message", "the kit")


def scenario(bench) -> int:
    text = kept_document(SOURCE / "engine", "SYSTEM.COMMON").read_text(encoding="utf-8")
    for phrase in ("Conducted workspace", PRECEDENCE, "## Golden rules", "## Diagnostics"):
        assert phrase in text, phrase
    assert text.index("# Conducted workspace") < text.index(PRECEDENCE) < text.index("## Golden rules")
    bench.held("the marble opens on the conducted workspace and its precedence",
               "Conducted workspace · these orders prevail over the card · the diagnostics said")

    positions = [text.index(rule) for rule in GOLDEN]
    assert positions == sorted(positions), positions
    assert positions[-1] < text.index("## Procedural Prompting")
    for phrase in DECLINED:
        assert phrase in text, phrase
    assert text.count("sloppy ok") == 1 and "The protocol" not in text
    counted = re.search(r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"
                        r"\s+(principles|golden rules)", text, re.IGNORECASE)
    assert counted is None, counted
    golden = text[text.index("## Golden rules"):text.index("## Procedural Prompting")]
    assert "in the chat" not in golden and "harness itself saves" not in golden
    assert len(golden) <= 1800, len(golden)
    bench.held("the golden rules lead, in their order",
               "the principles under ## Golden rules, before the standing orders, never counted; "
               "each said once, no reference to an absent title")

    lowered = text.lower()
    for word in GONE:
        assert word not in lowered, word
    assert "principal" in lowered
    bench.held("the engine's layer names no base", "it says `the principal` and never who: no "
               "operator, no chat turn, no parenthesis word, no kit -- the base's precision says it")

    compiled = (bench.shared().made / ".sys" / "system.md").read_text(encoding="utf-8")
    common = (bench.shared().made / ".sys" / "system.common.md").read_text(encoding="utf-8")
    card_head = body_of(kept_document(SOURCE / "engine", "PP"))[:80]
    base_root = next((bench.shared().made / ".sys" / "vendor").glob("kit@*"))   # the base the
    precision = body_of(base_root / "system" / "SYSTEM.COMMON.md")[:60]          # environment stands on
    for marble in (compiled, common):
        assert "Conducted workspace" in marble
        assert marble.index(GOLDEN[0]) < marble.index(card_head) < marble.index(precision)
    bench.held("the marble compiles in sections",
               "both marbles carry the engine's orders, the card closing the engine's section, "
               "then the base's precision, on the shared environment")

    # the glossary (batch le-glossaire): the last section of the marble, one entry per word
    # of these orders, of the card or of the texts packages serve at the turn, each used at
    # the source; the opening refers to it
    assert REFERRAL in text and text.index(REFERRAL) < text.index("## Golden rules")
    glossary = text[text.index("## Glossary"):]
    assert text.index("## Diagnostics") < text.index("## Glossary") and "\n## " not in glossary[3:]
    card = kept_document(SOURCE / "engine", "PP").read_text(encoding="utf-8")
    served = "\n".join(one.read_text(encoding="utf-8")     # the texts packages serve at the turn
                       for folder in ("overlays", "procs", "system")
                       for one in sorted(list(SOURCE.glob(f"packages/*/{folder}/*.md"))
                                         + list(SOURCE.glob(f"bases/*/{folder}/*.md"))))
    assert VECTOR in glossary and "the id joins it" in glossary
    assert PRINCIPAL in glossary
    assert DIAGNOSTIC in glossary
    words = re.findall(r"\*\*([^*]+)\*\*", glossary)
    assert len(words) >= GLOSSARY_WORDS, len(words)
    for word in words:      # both ways: every entry names a word the orders, the card or a served text use
        used = re.compile(r"\b" + re.escape(word) + r"(s|es|ed|d)?\b", re.IGNORECASE)
        assert used.search(text) or used.search(card) or used.search(served), word
    for line in glossary[glossary.index("\n**") + 1:].splitlines():   # one entry per line,
        if not line.strip():                                           # a blank line between
            continue                                                   # two (each its own paragraph)
        assert line.startswith("**") and " — " in line, line
    # the bound GUARDS the growth, it is not a target (operator word 2026-09-22, the mass
    # relaxed): it leaves room for the words the phase's next batch brings
    assert len(glossary) <= 5600, len(glossary)
    assert compiled.index("## Glossary") < compiled.index(card_head)
    bench.held("the glossary closes the marble and precedes the card",
               f"{len(words)} words, each with its entry and used at the source, "
               f"{len(glossary)} chars; the opening refers to it; `principal` defined; "
               "compiled before the card")
    return 0
