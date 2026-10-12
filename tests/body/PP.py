"""engine/refs/PP.md -- the card, the ENGINE's contract: the text it keeps -- the
conducted turn, the block section by section, the offers, the closings, written on the
word `principal`; and that the boot serves it."""
from __future__ import annotations

from tests.harness import SOURCE, kept_document

PHRASES = ("## Block anatomy", "An offer exists only while the output offering it is current",
           "routed from [n]", "do not investigate", "EVERY code the line asks",
           "work is free under displayed constraints", "in this exchange",
           "the pending block among them, no precedence",
           # what the heading says of the packages a run plays (l-interrupteur-de-package);
           # the switch itself is the LLM's to place: engine/system/SYSTEM.CONDUCT.md
           "off (<- <dependency>)",
           # the card relieved of what the orders and the glossary carry (la-carte-allegee):
           # it refers to the orders, declines the first golden rule at the chunk, and
           # promises nothing the engine denies
           "The standing orders above this card come first",
           "The regime is the standing orders' (§ Proof)",
           "[--blocks]",
           # the manual of a script: a package's skill wears its name, and called with no
           # argument pp mounts its contract instead of running it (le-manuel-des-skills)
           "Every package carries a skill of its own name, `pp-<package>`",
           "a script does not run: pp mounts its manual",
           # the two doors the engine describes, taught at the protocol and defined word by
           # word in the glossary (la-porte-decrite-au-kit)
           "A document leaving to several successors asks the same way (`PICK next`)",
           "a door described in prose asks its field ONCE",
           # the engine's own diagnostics have their place in the block's order
           # (le-diagnostic-au-bloc)
           "stands between DEVIATION and OPTIONS",
           # the run its principal conducts: no closing that moves it on carries a command
           # (le-canal-du-run)
           "In a run your principal conducts, a closing that moves the run on",
           # and what pp serves on the agent's call comes at the next prompt, whatever the
           # call -- a manual, a mount, a door, a peek (la-remise)
           "what pp serves on your call")
GONE = ("Hermetic",                      # the bench is not hermetic: the card no longer says so
        "UPPERCASE by convention", "hidden DRAFT", "One mark per direction",   # the glossary's
        "`pp off` opens a PARENTHESIS", "sloppy ok",                          # the orders' own
        # what the section gave back for the manual: said by the table of calls, by
        # « Repairs… » and by the engine's own deviation
        "Verbs are dash-prefixed", "your ask was not played", "outside a fusion",
        # the separator is the orders' rule, and the glossary says what an ephemeral is
        "its name, `---`", "(hidden draft, delivered by FINAL)",
        # the package switch moved to SYSTEM.CONDUCT.md: a run its principal conducts never reads it
        # (la-suspension-par-l-agent)
        "The principal also says which PACKAGES play", "-disable <pkg>")


def scenario(bench) -> int:
    text = kept_document(SOURCE / "engine", "PP").read_text(encoding="utf-8")
    for phrase in PHRASES:
        assert phrase in text, phrase
    for phrase in GONE:
        assert phrase not in text, phrase
    # the engine's contract names no base (le-marbre-et-la-carte-au-noyau) and its
    # renderer speaks the same word (le-mot-du-rendu): no `operator` left at all
    assert text.lower().count("operator") == 0
    assert "kit" not in text.lower()
    bench.held("the card says the protocol", "the block · the offers · the closings of value · "
               "the packages the run plays; the orders, the glossary and SYSTEM.CONDUCT.md not restated")

    conductor = bench.shared().conductor("body-card")
    rendered = conductor.resume(conductor.boot("BOOT.md"))
    standing = next((text for title, text in rendered.payloads if title.startswith("standing")), "")
    conductor.forget()
    assert "An offer exists only while the output offering it is current" in standing
    bench.held("the boot serves the card", "the standing orders carry it -- the first block reads it back")
    return 0
