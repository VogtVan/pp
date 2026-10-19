"""Scenario `kit-boot` -- what the kit seeds and what its boot does:
- the seeded member: on a vanilla instance M1 and M2 ride the boot's block under behavior,
  their tags resolved by the member's own front, no law of production in force; a member
  still equal to the kit's seeded file is pristine -- `_place_user` swaps it without a `.old`
- CAPABILITIES: its presentation is a constraint -- C1, C2 and C3 ride the block as the
  document's front says them, its body carries none; it asks ONE table by INFER, no choice;
  `tools.md` serves inside its frame, after the member's body and right above its ask, and
  the member's offer keeps it open at the TURN
- the `capabilities` key: no effort presets it; at `false` the boot skips the catalog, at
  `true` it presents it
- `capture_prompt`: the kit presets it light=false, medium=true, full=true under
  `effective`; a FINAL under the key asks the principal's message in its call -- the bare
  call extended by an argument, waiting
- the template's shelf: a fresh install stays INERT -- the kit's MEMBER as its `user/`
  keeps it, T1-T4 alone in force on TURN, the shelf seeded `_`; renaming the overlay,
  pasting a format, uncommenting M3 each take hold
"""
from __future__ import annotations

import re

from conductor import compiling, instance, reading, render, settings
from conductor import install as install_module
from tests.harness import PRODUCT_ENGINE, SOURCE, body_of, kept_document, support

kit = support(__file__, "kit")

KIT = SOURCE / "bases" / "kit"
TAG = re.compile(r"@MEMBER\.(\w+)")
EFFORTS = ("light", "medium", "full")
PRESETS = {"light": False, "medium": True, "full": True}


def _member_laws() -> dict[str, str]:
    """-> the laws of the kit's member by code, each `@MEMBER.<field>` tag resolved by the
    member's own front -- what a vanilla boot renders."""
    member = reading.read(kept_document(KIT, "MEMBER"))
    return {one.code: TAG.sub(lambda tag: str(member.front[tag.group(1)]).strip(), one.text)
            for one in reading.constraints(member)}


def _set(made, value: str) -> None:
    """Write `capabilities: <value>` and `conduction_effort: medium` into the instance's
    SETTINGS front -- the operator's edit, under the effort the template seeds."""
    path = made / "SETTINGS.md"
    text = path.read_text(encoding="utf-8")
    if re.search(r"(?m)^conduction_effort:", text):
        text = re.sub(r"(?m)^conduction_effort:.*$", "conduction_effort: medium", text)
    else:
        text = text.replace("---\n", "---\nconduction_effort: medium\n", 1)
    if re.search(r"(?m)^capabilities:", text):
        text = re.sub(r"(?m)^capabilities:.*$", f"capabilities: {value}", text)
    else:
        text = text.replace("---\n", f"---\ncapabilities: {value}\n", 1)
    path.write_text(text, encoding="utf-8")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- the seeded member on a vanilla boot -------------------------------------------
    env = bench.env("seeded")
    made = env.made
    opening = kit.boot(env)[-1]
    texts = {one.code: one.text for one in opening.constraints}
    laws = _member_laws()
    if (laws.get("M1") and laws.get("M2") and texts.get("M1") == laws["M1"]
            and texts.get("M2") == laws["M2"] and "@" not in texts["M1"] + texts["M2"]):
        held("tags resolve on a vanilla instance",
             "M1 and M2 both live by default, both resolved -- no `@...` literal")
    else:
        failures.append(f"  ✗ default M1/M2 tags         {texts.get('M1')!r} / {texts.get('M2')!r}")

    sections = {one.code: one.section for one in opening.constraints}
    if (sections.get("M1") == "behavior" and sections.get("M2") == "behavior"
            and "production" not in sections.values()):
        held("the identity is behavior on a vanilla instance",
             "M1 and M2 under behavior on the boot block, no production law in force")
    else:
        failures.append(f"  ✗ identity sections          {sections}")

    # --- CAPABILITIES -------------------------------------------------------------------
    caps = next((made / ".sys" / "vendor").glob("kit@*/procs/CAPABILITIES.md"))
    caps_laws = {one.code: one.text for one in reading.constraints(reading.read(caps))}
    caps_body = body_of(caps)
    if all(texts.get(code) and texts[code] == caps_laws.get(code) and texts[code] not in caps_body
           for code in ("C1", "C2", "C3")):
        held("CAPABILITIES' presentation is a constraint", "C1, C2 and C3 ride the block as the "
             "kit's front says them; the body carries none of them")
    else:
        failures.append(f"  ✗ CAPABILITIES C1-C3         {[texts.get(code) for code in ('C1', 'C2', 'C3')]}")

    if (opening.instruction.keyword == "INFER" and opening.output == "table"
            and not opening.options and opening.document == "CAPABILITIES"):
        held("the unitary keeps INFER", "CAPABILITIES asks ONE table -- one inference suffices, no choice")
    else:
        failures.append(f"  ✗ capabilities INFER          {opening.instruction!r} {opening.output!r}")

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

    # --- the seeded member is pristine: a fresh install ----------------------------------
    persona_a = bench.temp() / "a"
    (persona_a / "user").mkdir(parents=True)
    (persona_a / "user" / "MEMBER.md").write_text("Persona A's member\n", encoding="utf-8")
    seated = bench.env("seated").made          # the kit's own member, as the install placed it
    src_root = install_module.product_root(PRODUCT_ENGINE)
    saved = install_module._place_user(seated, persona_a, src_root, backup=True)
    if (not saved and not (seated / "MEMBER.md.old").exists()
            and (seated / "MEMBER.md").read_text(encoding="utf-8") == "Persona A's member\n"):
        held("the kit's seeded member is pristine", "still the kit's file, it swaps for the "
             "persona's without a .old -- the operator never wrote it")
    else:
        failures.append(f"  ✗ seeded member pristine      saved={saved}")

    # --- the effort presets: SETTINGS rewritten whole, read under `effective` -------------
    efforts = bench.env("efforts").made
    seen = {}
    for level in EFFORTS:
        (efforts / "SETTINGS.md").write_text(
            f"---\nname: SETTINGS\nkind: doc\nconduction_effort: {level}\ncapabilities: false\n---\n",
            encoding="utf-8")
        merged = settings.effective(reading.read(efforts / "SETTINGS.md").front, efforts)
        seen[level] = merged.get("capabilities")
    if seen == {level: False for level in EFFORTS}:
        held("no effort presets capabilities", "the written false holds under light, medium and full")
    else:
        failures.append(f"  ✗ capabilities by effort      {seen!r}")

    seen = {}
    for level in PRESETS:
        (efforts / "SETTINGS.md").write_text(
            f"---\nname: SETTINGS\nkind: doc\nconduction_effort: {level}\n---\n", encoding="utf-8")
        merged = settings.effective(reading.read(efforts / "SETTINGS.md").front, efforts)
        seen[level] = merged.get("capture_prompt")
    if seen == PRESETS:
        held("the kit presets capture_prompt by effort", "light leaves the prompt alone, "
             "medium and full capture it -- the kit's fragment, read under `effective`")
    else:
        failures.append(f"  ✗ capture_prompt presets      {seen!r}")

    # --- the `capabilities` key on the boot -----------------------------------------------
    off = bench.env("caps-off")
    _set(off.made, "false")
    shown = "\n".join(render(one) for one in kit.boot(off))
    if "NEXT INSTRUCTION CONTEXT — CAPABILITIES" not in shown and "INFORMATION — tools" not in shown:
        held("capabilities false skips the catalog", "the boot's output asks no table and serves no tools.md")
    else:
        failures.append(f"  ✗ capabilities false          step={'NEXT INSTRUCTION CONTEXT — CAPABILITIES' in shown} "
                        f"tools={'INFORMATION — tools' in shown}")

    on = bench.env("caps-on")
    _set(on.made, "true")
    shown = "\n".join(render(one) for one in kit.boot(on))
    if "NEXT INSTRUCTION CONTEXT — CAPABILITIES" in shown and "INFORMATION — tools" in shown:
        held("capabilities true presents the catalog", "CAPABILITIES plays, tools.md served in its frame")
    else:
        failures.append(f"  ✗ capabilities true           tools={'INFORMATION — tools' in shown}")

    # --- the frontier's call, with and without `capture_prompt` ---------------------------
    frontier = bench.env("frontier", pin=False)
    calls = {}
    for captured in (True, False):
        (frontier.made / "SETTINGS.md").write_text(
            f"---\nname: SETTINGS\nkind: doc\ncapture_prompt: {str(captured).lower()}\n---\n",
            encoding="utf-8")
        (frontier.made / "ASK.md").write_text(
            "---\nname: ASK\nkind: proc\ndescription: one step then the frontier\n"
            "proc: |\n  WORK\n  FINAL\n---\nsay it\n", encoding="utf-8")
        key = "c" if captured else "b"
        block = frontier.conductor(key).start(frontier.made / "ASK.md")
        calls[captured] = (block.next_call.replace(f" {key}", " <key>", 1), block.wait)
        frontier.conductor(key).forget()
    (asked, asked_wait), (bare, bare_wait) = calls[True], calls[False]
    if asked.startswith(bare + " ") and asked_wait and bare_wait:
        held("the frontier's call under capture_prompt", "the call extends the bare call by "
             "the principal's message and waits; without the key, the bare call")
    else:
        failures.append(f"  ✗ frontier call               {calls!r}")

    # --- the template's shelf: a fresh install stays inert, then armed --------------------
    shelf_made = bench.env("shelf").made
    shelf_member = (shelf_made / "MEMBER.md").read_text(encoding="utf-8")
    shelf_formats = (shelf_made / "FORMATS.md").read_text(encoding="utf-8")
    shelf_enum = compiling.format_enumeration(shelf_made)
    shelf_turn = next((shelf_made / ".sys" / "vendor").glob("kit@*/procs/TURN.md"))
    inert_laws, _ = compiling.effective(shelf_made, reading.read(shelf_turn))
    shelf_names = {name for name, _, _ in compiling.entries(shelf_made)}
    shelf_served = reading.body_of(reading.served(shelf_made / "MEMBER.md")[0])
    if (shelf_member == kept_document(KIT, "MEMBER").read_text(encoding="utf-8") and "# M3 " in shelf_member
            and "uncomment" not in shelf_served and "M3" not in shelf_served
            and shelf_formats == kept_document(SOURCE / "template", "FORMATS").read_text(encoding="utf-8")
            and (shelf_made / "procs" / "_TURN.md").is_file()
            and (shelf_made / "procs" / "_BOOTNOTE.md").is_file()
            and "theme" not in shelf_enum and "brief" not in shelf_enum
            and [one.code for one in inert_laws] == ["T1", "T2", "T3", "T4"]
            and not any(one.startswith("_") or one == "BOOTNOTE" for one in shelf_names)
            and not instance.attached(shelf_made, "boot.ready")):
        held("the template opens doors, inert", "preferences in readme:, the SERVED body pure, "
             "the shelf seeded `_` -- nothing in force, cataloged or attached")
    else:
        failures.append(f"  ✗ template inert            {sorted(shelf_enum)} / "
                        f"{[c.code for c in inert_laws]} / {sorted(shelf_names)}")

    (shelf_made / "procs" / "_TURN.md").rename(shelf_made / "procs" / "TURN.md")
    armed_laws, _ = compiling.effective(shelf_made, reading.read(shelf_turn))
    (shelf_made / "FORMATS.md").write_text(
        "---\nname: FORMATS\nkind: doc\nformats: |\n"
        "  table  stdin   the HOUSE table style\n"
        "  theme  stdin   a one-line theme statement, then themed sections\n---\n",
        encoding="utf-8")
    armed_enum = compiling.format_enumeration(shelf_made)
    (shelf_made / "MEMBER.md").write_text(
        shelf_member.replace("  # M3 ", "  M3 ", 1), encoding="utf-8")
    kit_member = instance.resolve(shelf_made, "MEMBER.md")
    armed_member_laws, _ = compiling.effective(shelf_made, reading.read(kit_member))
    (shelf_made / "procs" / "_BOOTNOTE.md").rename(shelf_made / "procs" / "BOOTNOTE.md")
    if ([one.code for one in armed_laws] == ["T1", "T2", "T3", "T6"]
            and armed_enum["table"][1] == "the HOUSE table style"
            and "theme" in armed_enum and "brief" not in armed_enum
            and any(one.code == "M3" for one in armed_member_laws)
            and instance.attached(shelf_made, "boot.ready") == ("BOOTNOTE.md",)):
        held("renaming, uncommenting and pasting arm the doors", "the overlay merges, the house "
             "table supersedes the kit's, uncommented M3 enters the laws, the note attaches")
    else:
        failures.append(f"  ✗ arming                    {[c.code for c in armed_laws]} / "
                        f"{armed_enum.get('table')!r} / {[c.code for c in armed_member_laws]}")
    return 0
