"""Scenario `member-turn` -- 1 case(s), in the monolith's order:
- MEMBER calls TURN (not BOOT): its constraints hold through the WHOLE turn
"""
from __future__ import annotations

from pathlib import Path
from conductor import Conductor, discovery, persistence
from tests.harness import session_of


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    # --- MEMBER calls TURN (not BOOT): its constraints hold through the WHOLE turn -------
    persona_made = bench.env("persona").made
    persona = persona_made.parent
    persona_engine = persona_made / ".sys" / "engine" / "pp.py"
    persona_member = discovery.instance_member(persona_engine)
    persona_member_doc = persona_made / "MEMBER.md"
    persona_member_doc.write_text(
        "---\nname: Sextant\ncharacter: >-\n  curt, dry wit\nconstraints.behavior: |\n"
        "  M1  your name is @MEMBER.name\n  M2  you must behave like this: @MEMBER.character\n"
        "proc: |\n  CALL CAPABILITIES.md\n  CALL TURN.md\n---\nA terse crew member.\n",
        encoding="utf-8")

    def persona_conductor() -> Conductor:
        return Conductor(persona_member, discovery.siblings_around(persona_member), persona_engine, "t")

    def persona_boot():
        c = persona_conductor()
        return c.resume(c.boot("BOOT.md"))

    persona_opening = persona_boot()
    texts = {c.code: c.text for c in persona_opening.constraints} if persona_opening else {}
    if (texts.get("M1") == "your name is Sextant"
            and texts.get("M2") == "you must behave like this: curt, dry wit"):
        held("a tag resolves to another document's own front matter",
             "@MEMBER.name / @MEMBER.character, both live at the first cession, both resolved")
    else:
        failures.append(f"  ✗ persona tags               {texts}")

    persistence.forget(session_of(persona_member.meta))
    persona_member_doc.write_text(
        "---\nname: Compass\nconstraints.behavior: |\n  M1  @NOPE.name knows nothing\nproc: |\n"
        "  CALL CAPABILITIES.md\n  CALL TURN.md\n---\nA terse crew member.\n",
        encoding="utf-8")
    expect("tag-unresolved", persona_boot)

    persistence.forget(session_of(persona_member.meta))
    persona_member_doc.write_text(
        "---\nname: Compass\nconstraints.behavior: |\n  M1  your character is @MEMBER.character\nproc: |\n"
        "  CALL CAPABILITIES.md\n  CALL TURN.md\n---\nA terse crew member.\n",
        encoding="utf-8")
    expect("tag-unresolved", persona_boot)
    persistence.forget(session_of(persona_member.meta))
    return 0
