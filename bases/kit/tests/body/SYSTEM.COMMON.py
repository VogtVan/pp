"""bases/kit/system/SYSTEM.COMMON.md -- the kit's precision of the standing orders in both
conduction modes: who the principal is here (the operator, in the chat) and how the FINAL is
delivered -- compiled after the engine's section, whose card closes it, into `system.md` and
`system.common.md`; no sentence of it tells the agent to call pp or to run a command."""
from __future__ import annotations

from tests.harness import SOURCE, body_of, kept_document

PHRASES = ("the principal is the operator", "## The delivery",
           "as ONE `=> response`: your final chat message",
           "each draft opened by three lines — `---`, its name, `---` —",
           "the names being those the closing lists in parentheses, in its order",
           "then wait for the operator")
# the conducted turn is the kit's CONDUCT, said to a run the LLM conducts alone
GONE = ("operator sends a chat message", "run the exact pp command shown",
        "Call it again only when instructed", "`pp off` opens a parenthesis",
        "call back now", "stop conduction", "-peek")
MASS = 1100      # a guard, not a target: 25 % above the 887 bytes the file weighs


def scenario(bench) -> int:
    path = kept_document(SOURCE / "bases" / "kit", "SYSTEM.COMMON")
    text = path.read_text(encoding="utf-8")
    for phrase in PHRASES:
        assert phrase in text, phrase
    for phrase in GONE:
        assert phrase not in text, phrase
    assert " call" not in body_of(path).lower(), "a sentence says to call"
    assert "## Glossary" not in text and "## Golden rules" not in text
    engine = body_of(kept_document(SOURCE / "engine", "SYSTEM.COMMON"))
    repeated = [line.strip() for line in body_of(path).splitlines()
                if len(line.strip()) > 40 and line.strip() in engine]
    assert not repeated, repeated
    mass = len(path.read_bytes())
    assert mass <= MASS, mass
    bench.held("the kit says who the principal is and how FINAL delivers, nothing more",
               f"the operator in the chat, the delivery; no call, no command -- {mass} bytes "
               f"under {MASS:,}, no line of the engine's orders repeated")

    made = bench.shared().made / ".sys"
    head = body_of(path)[:60]
    for name in ("system.md", "system.common.md"):
        compiled = (made / name).read_text(encoding="utf-8")
        assert head in compiled, name
        assert compiled.index("## Runs and calls") < compiled.index(head), name
    bench.held("the precision compiles after the engine's section",
               "system.md and system.common.md on the shared environment: the card, then the kit")
    return 0
