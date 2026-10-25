"""Scenario `formats` -- the pattern `outputs/formats`, played from its demonstration:
- `output:` names a form of the enumeration, the line carries the name, the formats reading teaches
  it; a form nobody declares, one declared twice and one without its mode refuse
- a consumed production is captured -- its closing hands it to the tool, an empty or broken value
  repairs, a valid one lands -- and a production nobody takes is said, no smell for the build
- the instance redeclares a form and wins over the engine's; the engine's forms reach the
  enumeration from its own table; a form at the mode `chat` is said to the principal and stands
  alone, a mode the dialect lacks refuses, the reading carries the forms alone, `said` is no form
  of the engine's; a package's form at `chat` is said with its mode
- the two readings: the build writes the skills' and the forms' readings, each with its receipt,
  neither carrying the other's sections; an imposed form keeps the engine's mode -- another refuses
  `format-mode-fixed`, nothing written, its own words pass
- an overlay changes `output:`; one naming a form nobody declares refuses at the build
- a proven production nobody takes speaks in the chat; the step a PICK elects from produces the
  engine's `list` whatever `output:` says -- a text, a list of objects and a twin repair, the list
  becomes the OPTIONS, the document's other steps keep its own form
The instance's form documents, the package and the overlays are placed at the test's time.
"""
from __future__ import annotations

import json

from conductor import compiling, reading, render
from conductor.core import language
from tests.harness import demonstrated, demos, plant, vendor

DRAWER, PATTERN = "outputs", "formats"
DEMO = demos(DRAWER, PATTERN)
DEMOS = ("ACT.md", "CHATTY.md", "FORMS.md", "FREE.md", "JUDGE.md", "LISTED.md", "LOST.md", "MISMODED.md",
         "OPENING.md", "OWNTABLE.md", "PACKAGED.md", "PRODUCER.md", "SHIP.md", "SPOKEN.md", "TORN.md",
         "TURN.nonesuch.md", "TURN.overlay.md", "TWICE.md", "UNKNOWN.md")
SPLIT = ("\n## The OUTPUT formats\n",)   # the one section the forms' reading carries, the skills' none
PACKAGE = "name: witness\nversion: 0.0.1\ndescription: a package that declares a form\nrequires: [kit]\n"


def _text(name: str) -> str:
    return (DEMO / name).read_text(encoding="utf-8")


def _declared(name: str) -> dict[str, tuple[str, str]]:
    """-> the forms the demonstration `name` declares: {form: (mode, definition)}."""
    found = {}
    for line in str(reading.read(DEMO / name).front.get("formats", "")).splitlines():
        parts = line.split(None, 2)
        if len(parts) == 3:
            found[parts[0]] = (parts[1], parts[2])
    return found


def _section(catalog: str, heading: str) -> str:
    return catalog.split(heading, 1)[1].split("\n## ", 1)[0] if heading in catalog else ""


def enumeration(bench) -> None:
    """`output:` names a form; the refusals; the capture; the production nobody takes."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("formats", bare=True)
    plant(env, DRAWER, PATTERN, ("FORMS.md", "JUDGE.md", "PRODUCER.md", "SHIP.md", "UNKNOWN.md"))

    def c():
        return env.conductor("t")

    def opened(name: str):
        c().forget()
        return c().start(env.made / "procs" / name)

    verdict = _declared("FORMS.md")["verdict"]
    judged = opened("JUDGE.md")
    shown = render(judged)
    taught = compiling.render_formats(env.made)
    if (judged.output == "verdict" and "▌ INSTRUCTION\nINFER verdict => response" in shown
            and verdict[1] not in shown and SPLIT[0].strip() in taught
            and compiling.format_enumeration(env.made).get("verdict", ())[:2] == verdict and verdict[1] in taught):
        held("output: names a form of the enumeration", "FORMS declares `verdict`, JUDGE names it, the line "
             "carries the name, the formats reading teaches it")
    else:
        failures.append(f"  ✗ the name                    {judged.output!r} {shown[:80]!r}")
    expect("format-unknown", lambda: opened("UNKNOWN.md"))
    plant(env, DRAWER, PATTERN, ("TWICE.md",))
    expect("format-doubled", lambda: opened("JUDGE.md"))
    (env.made / "procs" / "TWICE.md").unlink()
    plant(env, DRAWER, PATTERN, ("TORN.md",))
    expect("format-malformed", lambda: opened("JUDGE.md"))
    (env.made / "procs" / "TORN.md").unlink()

    asked = opened("PRODUCER.md")
    if " -   (" in asked.next_call and "stdin" in asked.next_call and "▶ CONTINUE" in render(asked):
        held("a consumed production is captured", "the closing hands the mode: json travels on stdin")
    else:
        failures.append(f"  ✗ the capture closing         {asked.next_call!r}")
    empty = c().submit("")
    broken = c().submit("{oops")
    landed = c().submit('{"ok": 1}')
    if ("empty production" in empty.deviation and "not one valid JSON value" in broken.deviation
            and "REPAIR" in render(broken) and landed is not None and landed.wait):
        held("the capture validates", "an empty value missed, a broken JSON repaired, a valid one lands")
    else:
        failures.append(f"  ✗ the validation              {empty.deviation!r} {broken.deviation!r}")
    c().forget()

    plant(env, DRAWER, PATTERN, ("LOST.md",))
    if not any("forgotten" in one for one in compiling.lint(env.made)):
        held("a production nobody takes is no smell", "LOST's JSON is said to the principal; the build "
             "presumes no oversight")
    else:
        failures.append("  ✗ the lint")


def instance_forms(bench) -> None:
    """The instance's forms over the engine's; the forms said to the chat; a package's form."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("formats-instance")
    installed = env.made / "FORMATS.md"
    seeded = installed.read_text(encoding="utf-8") if installed.is_file() else None

    installed.write_text(_text("OWNTABLE.md"), encoding="utf-8")
    shaped = compiling.format_enumeration(env.made)
    own = _declared("OWNTABLE.md")["table"][1]
    if (shaped["table"][1] == own and shaped["table"][2] == "FORMATS.md"
            and shaped["free"][1] == language.FORMATS["free"][1] and shaped["free"][2] == "engine"
            and own in compiling.render_formats(env.made)):
        held("the instance's form wins", "FORMATS.md redeclares `table` and wins; `free` stays the engine's")
    else:
        failures.append(f"  ✗ the override                {shaped.get('table')!r}")
    if seeded is None:
        installed.unlink()
    else:
        installed.write_text(seeded, encoding="utf-8")
    standing = compiling.format_enumeration(env.made)
    if (standing["table"][1] == language.FORMATS["table"][1] and standing["table"][2] == "engine"
            and standing["free"][2] == "engine" and seeded is not None):
        held("the engine's forms reach the enumeration", "without the redeclaration, `table` and `free` are "
             "the engine's own")
    else:
        failures.append(f"  ✗ the engine's forms          {standing['table'][2]!r} seeded={seeded is not None}")

    installed.write_text(_text("SPOKEN.md"), encoding="utf-8")
    spoken = _declared("SPOKEN.md")
    said_forms = compiling.format_enumeration(env.made)
    catalog = compiling.render_formats(env.made)
    plant(env, DRAWER, PATTERN, ("ACT.md",))
    act = env.conductor("chan").start(env.made / "procs" / "ACT.md")
    if (said_forms.get("act") == (language.CHAT, spoken["act"][1], "FORMATS.md")
            and said_forms.get(language.SAID) == (language.CHAT, spoken[language.SAID][1], "FORMATS.md")
            and f"**`act`** ({language.CHAT}) — {spoken['act'][1]}" in catalog
            and catalog.count("\n## ") == len(SPLIT)
            and act.output == "act" and act.channel == language.RESPONSE):
        held("a chat form stands alone", "`act` enters the enumeration with its mode `chat`, ACT names it, the "
             "line says `=> response`; the reading carries the forms alone")
    else:
        failures.append(f"  ✗ the chat form               {said_forms.get('act')!r} {act.output!r}")
    env.conductor("chan").forget()
    installed.write_text(_text("MISMODED.md"), encoding="utf-8")
    expect("format-malformed", lambda: compiling.format_enumeration(env.made))
    if seeded is None:
        installed.unlink()
    else:
        installed.write_text(seeded, encoding="utf-8")
    if language.SAID not in compiling.format_enumeration(env.made):
        plant(env, DRAWER, PATTERN, ("OPENING.md",))
        expect("reference-unknown", lambda: env.conductor("chan").start(env.made / "procs" / "OPENING.md"))
        held("said is no form of the engine's", "under the witness base `output: said` is unknown: the "
             "opening of a said production is the base's to declare")
        (env.made / "procs" / "OPENING.md").unlink()
    else:
        failures.append("  ✗ the said form               the witness base or the engine declares `said`")


def readings(bench) -> None:
    """The two readings; a package's chat form; an imposed form's fixed mode."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    made = bench.env("formats-readings").made
    vendor(made, "witness", PACKAGE, {"PACKAGED": _text("PACKAGED.md")})
    built = compiling.build_tools(made)
    forms = made / ".sys" / compiling.OUTPUT
    tools_text = built.read_text(encoding="utf-8") if built.is_file() else ""
    forms_text = forms.read_text(encoding="utf-8") if forms.is_file() else ""
    receipts = compiling.receipts(made)
    if (not any(heading in tools_text for heading in SPLIT)
            and all(heading in forms_text for heading in SPLIT) and forms_text.count("\n## ") == len(SPLIT)
            and forms_text == compiling.render_formats(made)
            and all(name in receipts for name in compiling.CATALOGS)):
        held("the build writes the two readings", "the skills' reading without the forms, the forms' reading "
             "with the forms alone, each with its receipt")
    else:
        failures.append(f"  ✗ the two readings            {[h in tools_text for h in SPLIT]} {sorted(receipts)}")
    packaged = _declared("PACKAGED.md")["act"][1]
    catalog = compiling.render_formats(made)
    if (f"**`act`** ({language.CHAT}) — {packaged}" in _section(catalog, SPLIT[0])
            and catalog.count("\n## ") == len(SPLIT)):
        held("a package's chat form is said with its mode", "`act (chat)` under the forms, the reading "
             "carrying no other section")
    else:
        failures.append("  ✗ the package's form")

    stamp = built.read_bytes(), forms.read_bytes()
    doc = made / ".sys" / "vendor" / "witness@0.0.1" / "procs" / "PACKAGED.md"
    for name in language.IMPOSED:
        moved = next(mode for mode in language.MODES if mode != language.FORMATS[name][0])
        doc.write_text(f"---\nname: PACKAGED\nkind: doc\ndescription: an imposed form moved\nformats: |\n"
                       f"  {name}  {moved}  another way\n---\n\nmoved\n", encoding="utf-8")
        expect("format-mode-fixed", lambda: compiling.build_tools(made))
    if (built.read_bytes(), forms.read_bytes()) == stamp:
        held("a refused build writes neither reading", f"{len(language.IMPOSED)} imposed forms moved, each "
             "refused: both readings byte-identical")
    else:
        failures.append("  ✗ a reading changed under a refusal")
    own = "the witness's own words for a choice"
    doc.write_text(f"---\nname: PACKAGED\nkind: doc\ndescription: an imposed form reworded\nformats: |\n"
                   f"  options  {language.FORMATS['options'][0]}  {own}\n---\n\nreworded\n", encoding="utf-8")
    if compiling.format_enumeration(made)["options"][:2] == (language.FORMATS["options"][0], own):
        held("an imposed form takes its own words", "`options` redeclared at the engine's mode: the words the "
             "package's, the mode the engine's")
    else:
        failures.append(f"  ✗ the imposed reworded        {compiling.format_enumeration(made)['options']!r}")


def overlaid(bench) -> None:
    """An overlay changes `output:`; one naming a form nobody declares refuses at the build."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("formats-overlay")
    overlay = env.write("procs/TURN.md", _text("TURN.overlay.md"))
    runner = env.conductor("ovl")
    worked = runner.start(runner.boot("BOOT.md"))
    hops = 0
    while worked is not None and str(worked.instruction).strip() != "WORK" and not worked.wait and hops < 4:
        worked = env.conductor("ovl").forward("")
        hops += 1
    env.conductor("ovl").forget()
    if worked is not None and str(worked.instruction).strip() == "WORK" and worked.output == "line":
        held("an overlay changes output:", "the TURN overlay writes `output: line`: the base's WORK asks a line")
    else:
        failures.append(f"  ✗ the overlaid output         {worked and worked.output!r}")
    overlay.write_text(_text("TURN.nonesuch.md"), encoding="utf-8")
    expect("reference-unknown", lambda: compiling.build_tools(env.made))
    overlay.unlink()
    compiling.build_tools(env.made)


def channels(bench) -> None:
    """A proven production nobody takes speaks in the chat; the list before a PICK."""
    held, failures = bench.held, bench.failures
    env = bench.env("formats-channels", bare=True)
    plant(env, DRAWER, PATTERN, ("CHATTY.md", "FREE.md", "LISTED.md"))

    def c():
        return env.conductor("t")

    def opened(name: str):
        c().forget()
        return c().start(env.made / "procs" / name)

    chat = opened("CHATTY.md")
    if "stdin" not in chat.next_call and chat.command == "INFER":
        held("a proven production nobody takes speaks in the chat", "the closing is the keyed call alone: the "
             "checkpoint comes after it")
    else:
        failures.append(f"  ✗ the chat closing            {chat.next_call!r}")
    asked = opened("LISTED.md")
    shown = render(asked)
    misses = []
    for wrong in ("io and ep", '[{"name": "io"}]', '["io", "io"]'):
        back = c().submit(wrong)
        misses.append(back is not None and back.repair >= 1 and bool(back.deviation) and back.output == language.LIST)
    picked = c().submit(json.dumps(["io", 2]))
    first = opened("FREE.md")
    chosen = c().submit(json.dumps(["io"]))
    last = c().submit("io")
    c().forget()
    if (asked.output == language.LIST and f"INFER {language.LIST} => tool (heredoc)" in shown and all(misses)
            and picked is not None and list(picked.options) == ["io", "2"] and first.output == language.LIST
            and chosen is not None and list(chosen.options) == ["io"] and last is not None and last.output == "free"):
        held("the step a PICK elects from produces the list", "LISTED's INFER says `list => tool (heredoc)`; a "
             "text, a list of objects and a twin repair; the list becomes the OPTIONS; FREE lists for that step "
             "and writes `free` after the PICK")
    else:
        failures.append(f"  ✗ the list                    {asked.output!r} {misses} {last and last.output!r}")


def scenario(bench) -> int:
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        bench.failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    enumeration(bench)
    instance_forms(bench)
    readings(bench)
    overlaid(bench)
    channels(bench)
    return 0
