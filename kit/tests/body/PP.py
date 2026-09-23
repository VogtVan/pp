"""kit/refs/PP.md -- the card: the text it keeps -- the conducted turn, the block
section by section, the offers, the closings; and that the boot serves it."""
from __future__ import annotations

from tests.harness import SOURCE, kept_document

PHRASES = ("When conduction applies", "This is the operator's intended rhythm",
           "## Block anatomy", "An offer exists only while the output offering it is current",
           "routed from [n]", "do not investigate", "the codes at risk",
           "work is free under displayed constraints", "in this exchange",
           "the block that STANDS and advances nothing",
           "the pending block among them, no precedence",
           # the package switch: the operator's word, the verb that places it, and what
           # the heading says of it (l-interrupteur-de-package)
           "The operator also says which PACKAGES play",
           "-disable <package>", "-enable <package>",
           "every package that REQUIRES it leaves with it",
           "`package.<name>: on|off` at SETTINGS",
           "off (<- <dependency>)",
           # the card relieved of what the orders and the glossary carry (la-carte-allegee):
           # it refers to the orders, declines the first golden rule at the chunk, and
           # promises nothing the engine denies
           "The standing orders above this card come first",
           "see the standing orders, § Mandatory pp use",
           "The regime is the standing orders' (§ Proof)",
           "Read each chunk whole, where it lands, before the bare call",
           "[--blocks]",
           # the manual of a script: a package's skill wears its name, and called with no
           # argument pp mounts its contract instead of running it (le-manuel-des-skills)
           "Every package carries a skill of its own name, `pp-<package>`",
           "a script does not run: pp mounts its manual",
           # the closing names the drafts it delivers; the rule stays the orders'
           # (les-noms-a-la-livraison)
           "qualified `ephemerals => chat (A · B)`, it names in parentheses the documents whose drafts it delivers",
           # the two doors the engine describes, taught at the protocol and defined word by
           # word in the glossary (la-porte-decrite-au-kit)
           "A document leaving to several successors asks the same way (`PICK next`)",
           "a door described in prose asks its field ONCE")
GONE = ("Hermetic",                      # the bench is not hermetic: the card no longer says so
        "UPPERCASE by convention", "hidden DRAFT", "One mark per direction",   # the glossary's
        "`pp off` opens a PARENTHESIS", "sloppy ok",                          # the orders' own
        # what the section gave back for the manual: said by the table of calls, by
        # « Repairs… » and by the engine's own deviation
        "Verbs are dash-prefixed", "your ask was not played", "outside a fusion",
        # the separator is the orders' rule, and the glossary says what an ephemeral is
        "its name, `---`", "(hidden draft, delivered by FINAL)")


def scenario(bench) -> int:
    text = kept_document(SOURCE / "kit", "PP").read_text(encoding="utf-8")
    for phrase in PHRASES:
        assert phrase in text, phrase
    for phrase in GONE:
        assert phrase not in text, phrase
    bench.held("the card says the protocol", "when conduction applies · the block · the offers · "
               "the closings · the packages the run plays; the orders and the glossary not restated")

    conductor = bench.shared().conductor("body-card")
    rendered = conductor.resume(conductor.boot("BOOT.md"))
    standing = next((text for title, text in rendered.payloads if title.startswith("standing")), "")
    conductor.forget()
    assert "When conduction applies" in standing
    bench.held("the boot serves the card", "the standing orders carry it -- the first block reads it back")
    return 0
