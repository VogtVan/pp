"""Scenario `seeded-member` -- 5 case(s) (the cases of the root sectors that read the kit's
seeded MEMBER and its CAPABILITIES, moved here at le-tri-de-l-execution-et-du-packaging,
2026-10-06 -- each named with the scenario it comes from):
- tags resolve on a vanilla instance: M1 says `your name is AGENT`, M2 the kit's own character
  (`tests/engine/packaging/install.py`)
- CAPABILITIES' presentation is a constraint, not prose: C1, C2 and C3 ride the boot's block
  with the kit's own text, and `Deliver it in chat AS THE TABLE` is gone from its body
  (`install.py`)
- the unitary keeps INFER: CAPABILITIES asks ONE table -- one inference, no choice
  (`tests/engine/execution/work-free.py`)
- the catalog rides CAPABILITIES: tools.md served inside its frame, after the member's body
  and right above its ask; the member's offer keeps CAPABILITIES open at the TURN
  (`tests/engine/execution/sessions.py`)
- a member still equal to the kit's seeded file is pristine: `_place_user` swaps it without
  a `.old` (`tests/engine/packaging/user-tier.py`)
"""
from __future__ import annotations

from pathlib import Path

from conductor import render
from conductor import install as install_module
from tests.harness import PRODUCT_ENGINE


def _landed(env):
    """-> the boot's first STEP block: a long boot reading rides CONTINUEs first."""
    opener = env.conductor("t")
    opening = opener.resume(opener.boot("BOOT.md"))
    for _ in range(6):
        if opening.command:
            break
        opening = env.conductor("t").resume(env.conductor("t").boot("BOOT.md"))
    return opening


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("seeded")
    made = env.made
    opening = _landed(env)
    texts = {one.code: one.text for one in opening.constraints}

    # --- tags resolve on a vanilla instance ---------------------------------------------------
    if (texts.get("M1") == "your name is AGENT"
            and texts.get("M2") == "you must behave like this: cooperative, honest, helpful, and respectful"):
        held("tags resolve on a vanilla instance",
             "M1 and M2 both live by default, both resolved -- no `@...` literal")
    else:
        failures.append(f"  ✗ default M1/M2 tags         {texts.get('M1')!r} / {texts.get('M2')!r}")

    # --- CAPABILITIES' presentation rule is a constraint ------------------------------------------
    kit_caps_text = next((made / ".sys" / "vendor").glob("kit@*/procs/CAPABILITIES.md")).read_text(encoding="utf-8")
    if (all(texts.get(code) and texts[code] in kit_caps_text for code in ("C1", "C2", "C3"))
            and "Deliver it in chat AS THE TABLE" not in kit_caps_text):
        held("CAPABILITIES' presentation is a constraint", "C1, C2 and C3 carry what the body used "
             "to instruct, in the kit's own words; the body is a fact now")
    else:
        failures.append(f"  ✗ CAPABILITIES C1-C3         {[texts.get(code) for code in ('C1', 'C2', 'C3')]}")

    # --- the unitary keeps INFER --------------------------------------------------------------------
    if (opening.instruction.keyword == "INFER" and opening.output == "table"
            and not opening.options and opening.document == "CAPABILITIES"):
        held("the unitary keeps INFER", "CAPABILITIES asks ONE table -- one inference suffices, no choice")
    else:
        failures.append(f"  ✗ capabilities INFER          {opening.instruction!r} {opening.output!r}")

    # --- the catalog rides CAPABILITIES ------------------------------------------------------------------
    rendered = render(opening)
    turn_block = env.conductor("t").submit("")
    if ("NEXT INSTRUCTION CONTEXT — CAPABILITIES" in rendered
            and "INFORMATION — tools" in rendered and "INFORMATION — AGENT" in rendered
            and rendered.index("INFORMATION — AGENT") < rendered.index("INFORMATION — tools")
            < rendered.index("NEXT INSTRUCTION CONTEXT — CAPABILITIES")
            and turn_block.document == "TURN"
            and "CAPABILITIES" in [one.name for one in turn_block.tools]):
        held("the catalog rides CAPABILITIES",
             "tools.md serves inside the presenting frame, after the member's body and right "
             "above its ask; the member's offer keeps the door open at the TURN")
    else:
        failures.append(f"  ✗ catalog placement          {[one.name for one in turn_block.tools]} "
                        f"{rendered[:300]!r}")
    env.conductor("t").forget()

    # --- a member still equal to the kit's seeded file is pristine -------------------------------------
    persona_a = bench.temp() / "a"
    (persona_a / "user").mkdir(parents=True)
    (persona_a / "user" / "MEMBER.md").write_text("Persona A's member\n", encoding="utf-8")
    seated = bench.env("seatedws").made          # the kit's own member, as the install placed it
    src_root = install_module.product_root(PRODUCT_ENGINE)
    saved = install_module._place_user(seated, persona_a, src_root, backup=True)
    if (not saved and not (seated / "MEMBER.md.old").exists()
            and (seated / "MEMBER.md").read_text(encoding="utf-8") == "Persona A's member\n"):
        held("the kit's seeded member is pristine", "still the kit's file, it swaps for the "
             "persona's without a .old -- the operator never wrote it")
    else:
        failures.append(f"  ✗ seeded member pristine      saved={saved}")
    return 0
