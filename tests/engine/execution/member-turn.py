"""Scenario `member-turn` -- 1 case(s):
- a tag resolves to another document's own front matter: `@MEMBER.name` and
  `@MEMBER.character` read the member's keys; a document nobody has, or a key the member
  does not carry, refuses `tag-unresolved` at the boot
(that the kit's MEMBER calls TURN and holds its laws through the whole turn is the kit's
text: `bases/kit/tests/engine/identity-in-behavior.py`)
"""
from __future__ import annotations

from conductor import persistence
from tests.harness import session_of


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("persona")

    def persona_boot():
        c = env.conductor("t")
        return c.resume(c.boot("BOOT.md"))

    env.write_member("character: >-\n  curt, dry wit\nconstraints.behavior: |\n"
                     "  M1  your name is @MEMBER.name\n  M2  you must behave like this: @MEMBER.character\n",
                     body="A terse crew member.", name="Sextant")
    persona_opening = persona_boot()
    texts = {c.code: c.text for c in persona_opening.constraints} if persona_opening else {}
    if (texts.get("M1") == "your name is Sextant"
            and texts.get("M2") == "you must behave like this: curt, dry wit"):
        held("a tag resolves to another document's own front matter",
             "@MEMBER.name / @MEMBER.character, both live at the first cession, both resolved")
    else:
        failures.append(f"  ✗ persona tags               {texts}")

    persistence.forget(session_of(env.made))
    env.write_member("constraints.behavior: |\n  M1  @NOPE.name knows nothing\n",
                     body="A terse crew member.", name="Compass")
    expect("tag-unresolved", persona_boot)

    persistence.forget(session_of(env.made))
    env.write_member("constraints.behavior: |\n  M1  your character is @MEMBER.character\n",
                     body="A terse crew member.", name="Compass")
    expect("tag-unresolved", persona_boot)
    persistence.forget(session_of(env.made))
    return 0
