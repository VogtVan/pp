"""Scenario `kit-boot` -- what the kit seeds and what its boot does:
- the seeded member: on a vanilla instance M1 and M2 ride the boot's block under behavior,
  their tags resolved by the member's own front, no law of production in force; a member
  still equal to the kit's seeded file is pristine -- `_place_user` swaps it without a `.old`
- the member's presentation: the boot's first step is MEMBER's own INFER, its laws (M3
  among them) riding the block as the member's front says them
- CAPABILITIES: its catalog is a constraint -- every law of its front rides its block as the
  front says it, its body carries none; it asks ONE table by INFER, no choice, after MEMBER's;
  the BOOT serves the two readings, `tools.md` then `output.md`, before the member's body (the
  brief of its INFER),
  CAPABILITIES' frame serves nothing, and the member's offer keeps it open at the TURN;
  `-compacted` serves the two readings again; the
  kit's TURN declares the `said` FORM (the three lines a said production opens on), the
  formats served at the boot carry it with its mode, the forms their only section;
  an overlay of TURN in the instance redefines the form, and a proc may name it
- the second exchange: the member's laws (B and M) hold on the TURN's block, once each, and
  neither MEMBER's body, the catalog nor CAPABILITIES replay
- the member rewritten mid-passage (its `# SERVE` uncommented, as the member craft writes it):
  the passage ends on the steps it played, the next message reseats MEMBER -- the steps of its
  proc, every one before `CALL TURN.md` done --, traced `reseated`, and neither BOOT, MEMBER's
  body, the catalog nor CAPABILITIES replay
- the `capabilities` key: no effort presets it; at `false` the boot serves the two readings
  and asks no table, at `true` the two readings and the table
- `capture_prompt`: no effort presets it, the written value holds under light, medium and
  full
- the template's shelf: a fresh install stays INERT -- the kit's MEMBER as its `user/`
  keeps it, T1-T4 alone in force on TURN, the shelf seeded `_`; renaming the overlay,
  pasting a format, uncommenting the member's first commented law each take hold
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from conductor.core import messages
from conductor import compiling, instance, persistence, reading, render, settings
from conductor.core import language
from conductor import install as install_module
from tests.harness import (PRODUCT_ENGINE, SOURCE, body_of, document, kept_document, na_proof, stepped,
                           support)

kit = support(__file__, "kit")

KIT = SOURCE / "bases" / "kit"
TAG = re.compile(r"@MEMBER\.(\w+)")
TOOLS, FORMS = (messages.titled(language.INFORMATION, name) for name in compiling.CATALOGS)
EFFORTS = ("light", "medium", "full")
SHELVED = re.compile(r"(?m)^  # ([A-Z]+\d+)  ")     # a law the member's front keeps commented


def _member_steps(path) -> list[str]:
    """-> the keywords of a member's proc, its commented lines out -- the steps a passage plays."""
    lines = str(reading.read(path).front.get("proc", "")).splitlines()
    return [one.split()[0] for one in lines if one.strip() and not one.lstrip().startswith("#")]


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
    if (opening.document == "MEMBER" and opening.instruction.keyword == "INFER" and not opening.options
            and all(texts.get(code) == text for code, text in laws.items())):
        held("the member presents itself first", f"the boot's first step is MEMBER's INFER, "
             f"{', '.join(laws)} riding its block as the member's front says them")
    else:
        failures.append(f"  ✗ member presentation        {opening.document!r} {opening.instruction!r} "
                        f"{sorted(texts)}")
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
    rendered = render(opening)
    caps_block = stepped(lambda: env.conductor("t"))
    caps_texts = {one.code: one.text for one in caps_block.constraints}
    if caps_laws and all(caps_texts.get(code) == text and text not in caps_body
                         for code, text in caps_laws.items()):
        held("CAPABILITIES' catalog is a constraint", f"{', '.join(caps_laws)} riding the block as the "
             "kit's front says them; the body carries none of them")
    else:
        failures.append(f"  ✗ CAPABILITIES laws          {sorted(caps_laws)} / {sorted(caps_texts)}")

    if (caps_block.instruction.keyword == "INFER" and caps_block.output == "table"
            and not caps_block.options and caps_block.document == "CAPABILITIES"):
        held("the unitary keeps INFER", "CAPABILITIES asks ONE table -- one inference suffices, no choice")
    else:
        failures.append(f"  ✗ capabilities INFER          {caps_block.instruction!r} {caps_block.output!r}")

    turn_block = stepped(lambda: env.conductor("t"))
    brief = messages.titled(language.CONTEXT, str(reading.read(kept_document(KIT, "MEMBER")).front["name"]))
    if (messages.titled(language.CONTEXT, "CAPABILITIES") in render(caps_block)
            and all(title in rendered for title in (TOOLS, FORMS, brief))
            and rendered.index(TOOLS) < rendered.index(FORMS) < rendered.index(brief)
            and "serve" not in reading.read(caps).front
            and turn_block.document == "TURN"
            and "CAPABILITIES" in [one.name for one in turn_block.tools]):
        held("the boot serves the two readings",
             "tools.md then output.md, served by the BOOT before the member's body, the brief of its INFER; CAPABILITIES "
             "serves nothing; the member's offer keeps the door open at the TURN")
    else:
        failures.append(f"  ✗ readings placement         {turn_block.document!r} {[one.name for one in turn_block.tools]} "
                        f"{[line for line in rendered.splitlines() if line.startswith('▌ ')]!r}")
    back = render(env.conductor("t").compacted())
    if TOOLS in back and FORMS in back:
        held("a compaction serves the two readings again", "-compacted at the TURN re-serves "
             "tools.md and output.md from the BOOT that stands")
    else:
        failures.append(f"  ✗ readings after compaction  {back[:300]!r}")
    said = compiling.format_enumeration(made).get(language.SAID)
    if (said is not None and said[0] == language.WORDS and "TURN" in said[2]
            and f"**`{language.SAID}`** ({language.listing(language.SAID, language.WORDS)}) — {said[1]}" in rendered
            and compiling.render_formats(made).count("\n## ") == 1
            and language.WORDS not in compiling.format_enumeration(made)):
        held("the kit declares the said form",
             "`said  words  …` on the kit's TURN: the formats served at the boot carry it with its "
             "mode, the forms the reading's only section; no form is named `response`")
    else:
        failures.append(f"  ✗ said form                  {said!r}")
    own = "the house's own opening"
    env.write("procs/TURN.md", f"---\nname: TURN\nformats: |\n  {language.SAID}  {language.WORDS}  {own}\n---\n")
    redefined = compiling.format_enumeration(made).get(language.SAID)
    named = env.conductor("f").start(document(
        f"---\nname: SAY\nkind: proc\ndescription: the kit's form named\noutput: {language.SAID}\n"
        "proc: |\n  INFER\n---\nsay\n", at=made))
    if (redefined is not None and redefined[1] == own and "TURN" in redefined[2]
            and redefined[2] != said[2]
            and named.output == language.SAID and language.said(named.channel)):
        held("an overlay of TURN redefines the said form",
             "the instance's `procs/TURN.md` redeclares `said` and wins over the kit's; "
             "`output: said` names the form like any other, its channel one of a said production")
    else:
        failures.append(f"  ✗ said redefined             {redefined!r} {named.output!r}")
    env.conductor("f").forget()
    (made / "procs" / "TURN.md").unlink()
    env.conductor("t").forget()

    # --- the second exchange: the member's laws hold, nothing of the boot replays ---------
    second = bench.env("second-exchange")
    opener = second.conductor("s")
    block = opener.start(opener.boot("BOOT.md"))
    for _ in range(12):
        if block is None or block.wait:
            break
        block = stepped(lambda: second.conductor("s"), na_proof(block) if block.judged else "")
    again = second.conductor("s").submit("the operator's second message")
    codes = [one.code for one in again.constraints]
    served = [subject for subject, _ in again.payloads]
    shown = render(again)
    if (again.document == "TURN" and all(codes.count(code) == 1 for code in ("B2", "B3", "M1", "M2"))
            and "MEMBER" not in served and TOOLS not in shown and FORMS not in shown
            and messages.titled(language.CONTEXT, "CAPABILITIES") not in shown):
        held("the member's laws hold at the second exchange", "B2, B3, M1 and M2 once each on the "
             "TURN's block of the second exchange; neither MEMBER's body, the catalog nor CAPABILITIES replay")
    else:
        failures.append(f"  ✗ second exchange            document={again.document} codes={codes} served={served}")
    second.conductor("s").forget()

    # --- the member rewritten mid-passage: reseated at the next message, nothing replayed --
    rewritten = bench.env("rewritten-member")
    key = "m"
    opener = rewritten.conductor(key)
    block = opener.start(opener.boot("BOOT.md"))
    member = rewritten.made / "MEMBER.md"
    seated = _member_steps(member)                   # the steps the kit's member plays, SERVE commented
    member.write_text(member.read_text(encoding="utf-8").replace("  # SERVE\n", "  SERVE\n", 1),
                      encoding="utf-8")
    for _ in range(12):
        if block is None or block.wait:
            break
        block = stepped(lambda: rewritten.conductor(key), na_proof(block) if block.judged else "")
    again = rewritten.conductor(key).submit("the operator's second message")
    slot = persistence.slot_of(rewritten.made, key)
    frames = json.loads(slot.read_text(encoding="utf-8"))["frames"]
    steps = [(one["keyword"], one.get("done")) for one in frames[1]["instructions"]]
    last = str(frames[1]["instructions"][-1].get("argument", "")).split()
    lines = [json.loads(line) for line in (slot.parent / persistence.trace_of(slot))
             .read_text(encoding="utf-8").splitlines() if line.strip()]
    reseated = [one.get("document") for one in lines if one.get("kind") == "reseated"]
    shown = render(again) if again is not None else ""
    if (block is not None and block.wait and again is not None and again.document == "TURN"
            and "SERVE" not in seated and [keyword for keyword, _ in steps] == ["SERVE"] + seated
            and steps[-1][0] == "CALL" and last and Path(last[0]).stem == "TURN"
            and [done for _, done in steps] == [True] * (len(steps) - 1) + [False]
            and reseated == ["MEMBER"] and "MEMBER" not in [subject for subject, _ in again.payloads]
            and TOOLS not in shown and FORMS not in shown
            and messages.titled(language.CONTEXT, "CAPABILITIES") not in shown):
        held("the member rewritten mid-passage", "the passage parks on its own steps; "
             f"the next message reseats MEMBER on {', '.join(keyword for keyword, _ in steps)} -- all done "
             "but CALL TURN -- traced `reseated`, and the TURN plays with nothing of the boot replayed")
    else:
        failures.append(f"  ✗ member rewritten           wait={block and block.wait} "
                        f"{again and again.document!r} steps={steps} last={last} reseated={reseated}")
    rewritten.conductor(key).forget()
    member.write_text(member.read_text(encoding="utf-8").replace("  SERVE\n", "  # SERVE\n", 1),
                      encoding="utf-8")

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
    for level in EFFORTS:
        (efforts / "SETTINGS.md").write_text(
            f"---\nname: SETTINGS\nkind: doc\nconduction_effort: {level}\ncapture_prompt: true\n---\n",
            encoding="utf-8")
        merged = settings.effective(reading.read(efforts / "SETTINGS.md").front, efforts)
        seen[level] = merged.get("capture_prompt")
    if seen == {level: True for level in EFFORTS}:
        held("no effort presets capture_prompt", "the written true holds under light, medium and full "
             "-- the kit's fragment presets nothing, read under `effective`")
    else:
        failures.append(f"  ✗ capture_prompt presets      {seen!r}")

    # --- the `capabilities` key on the boot: the readings always, the table at `true` ----
    shown = {}
    for value in ("false", "true"):
        house = bench.env(f"caps-{value}")
        _set(house.made, value)
        text = "\n".join(render(one) for one in kit.boot(house))
        shown[value] = (TOOLS in text, FORMS in text,
                        messages.titled(language.CONTEXT, "CAPABILITIES") in text)
    if shown["false"] == (True, True, False) and shown["true"] == (True, True, True):
        held("capabilities rules the table alone", "at false the boot serves tools.md and "
             "output.md and asks no table, at true the two and the table")
    else:
        failures.append(f"  ✗ capabilities               {shown!r}")

    # --- the template's shelf: a fresh install stays inert, then armed --------------------
    shelf_made = bench.env("shelf").made
    shelf_member = (shelf_made / "MEMBER.md").read_text(encoding="utf-8")
    shelf_formats = (shelf_made / "FORMATS.md").read_text(encoding="utf-8")
    shelf_enum = compiling.format_enumeration(shelf_made)
    shelf_turn = next((shelf_made / ".sys" / "vendor").glob("kit@*/procs/TURN.md"))
    inert_laws, _ = compiling.effective(shelf_made, reading.read(shelf_turn))
    shelf_names = {name for name, _, _ in compiling.entries(shelf_made)}
    shelf_served = reading.body_of(reading.served(shelf_made / "MEMBER.md")[0])
    shelved = SHELVED.search(shelf_member)
    shelved = shelved.group(1) if shelved else ""
    if (shelf_member == kept_document(KIT, "MEMBER").read_text(encoding="utf-8") and shelved
            and "uncomment" not in shelf_served and shelved not in shelf_served
            and shelf_formats == kept_document(SOURCE / "template", "FORMATS").read_text(encoding="utf-8")
            and (shelf_made / "procs" / "_TURN.md").is_file()
            and (shelf_made / "procs" / "_BOOTNOTE.md").is_file()
            and "theme" not in shelf_enum and "brief" not in shelf_enum
            and [one.code for one in inert_laws] == ["T1", "T2", "T3", "T4"]
            and not any(one.startswith("_") or one == "BOOTNOTE" for one in shelf_names)
            and not instance.attached(shelf_made, "boot.initialize")):
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
        shelf_member.replace(f"  # {shelved} ", f"  {shelved} ", 1), encoding="utf-8")
    kit_member = instance.resolve(shelf_made, "MEMBER.md")
    armed_member_laws, _ = compiling.effective(shelf_made, reading.read(kit_member))
    (shelf_made / "procs" / "_BOOTNOTE.md").rename(shelf_made / "procs" / "BOOTNOTE.md")
    if ([one.code for one in armed_laws] == ["T1", "T2", "T3", "T6"]
            and armed_enum["table"][1] == "the HOUSE table style"
            and "theme" in armed_enum and "brief" not in armed_enum
            and shelved and any(one.code == shelved for one in armed_member_laws)
            and instance.attached(shelf_made, "boot.initialize") == ("BOOTNOTE.md",)):
        held("renaming, uncommenting and pasting arm the doors", "the overlay merges, the house "
             f"table supersedes the kit's, uncommented {shelved} enters the laws, the note attaches")
    else:
        failures.append(f"  ✗ arming                    {[c.code for c in armed_laws]} / "
                        f"{armed_enum.get('table')!r} / {[c.code for c in armed_member_laws]}")
    return 0
