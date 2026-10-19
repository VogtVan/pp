"""Scenario `io-flow` -- how a production takes its form and travels:
- the outputs: OUTPUT is a NAME of the format enumeration, the catalog teaches it; an
  unknown, doubled or malformed format refuses; a consumed production is captured, typed,
  validated and seeds its callee; a CALL yields its callee's last production, across the
  pop; `any` is the wildcard, a mismatch refuses
- the formats: an instance redeclares a format and wins over the engine's; the mechanical
  forms reach the enumeration from the engine's own `FORMATS`
- the PICK's options: every malformed list REPAIRs with the miss named, never a crash; a
  number is an option; a list of strings renders its OPTIONS and weighs them; a list no
  capture judged refuses `options-invalid`, a PICK with no producer `options-empty`; the
  trace says the miss
- the answer channel: the trace's `answer` line carries the step's channel, a stray
  production on a response step says `response`
"""
from __future__ import annotations

from conductor import compiling, render
from conductor.core import language
from tests.harness import document, steady, support

run = support(__file__, "run")

# --- the outputs ----------------------------------------------------------------------------

VERDICT = "approve, revise or reject -- one word"      # the description FORMS gives `verdict`
FORMS = ("---\nname: FORMS\ndescription: local formats\nformats: |\n"
         f"  verdict  inline  {VERDICT}\n"
         "  json     stdin   one valid JSON value, nothing around it\n"
         "  line     inline  one line, plainly worded\n"
         "  table    stdin   a markdown table\n---\n")

# --- the formats ----------------------------------------------------------------------------

OWN_TABLE = "the operator's own table style"
OVERRIDE = ("---\nname: FORMATS\nkind: doc\ndescription: local overrides\nformats: |\n"
            f"  table  stdin  {OWN_TABLE}\n---\n")

# --- the PICK's options ---------------------------------------------------------------------

FLOOR = ("---\nname: X\nkind: proc\ndescription: judge\noutput: json\nproc: |\n"
         "  INFER\n  PICK verdict\n---\nelect\n")
CRASHING = [('[{"id": "approve"}, {"id": "reject"}]', "not a scalar"),
            ('[1, 2, 3]', ""),                       # numbers are scalars: no miss
            ('[["a"], ["b"]]', "not a scalar"),
            ('[null, "a"]', "not a scalar"),
            ('[true, false]', "not a scalar")]
SILENT = [('["", "a"]', "is empty"), ('["a", "a"]', "appears twice"),
          ('[]', "are empty"), ('"approve"', "not a JSON array"), ('{"a": 1}', "not a JSON array")]
WITNESS = ["approve", "reject"]

# --- the answer channel ---------------------------------------------------------------------

STRAY = "a table nobody asked the tool for"


def _sections(rendered: str) -> list[str]:
    """-> the headings and the closing arrow of a rendering, in order."""
    return [line for line in steady(rendered).splitlines() if line.startswith(("▌ ", "▶ "))]


def _section(rendered: str, heading: str) -> list[str]:
    """-> the lines under `heading` up to the next blank line."""
    lines = rendered.splitlines()
    if heading not in lines:
        return []
    body = lines[lines.index(heading) + 1:]
    return body[:body.index("")] if "" in body else body


def outputs(bench) -> None:
    """OUTPUT names a format; a consumed production is captured, validated, seeded and flows."""
    held, expect, over, failures = bench.held, bench.expect, bench.over, bench.failures
    io = bench.env("io", bare=True)
    meta = io.made

    def io_c():
        return io.conductor("t")

    # --- OUTPUT is a NAME of the enumeration -- pp dictates the form ------------------
    (meta / "FORMS.md").write_text(FORMS, encoding="utf-8")
    judged = io_c().start(document(
        "---\nname: X\nkind: proc\ndescription: judge\noutput: verdict\nproc: |\n"
        "  INFER\n---\njudge the draft\n", at=meta))
    io_rendered = render(judged)
    catalog_io = compiling.render_tools(meta)
    enumerated = compiling.format_enumeration(meta)
    if (judged.output == "verdict" and "▌ INSTRUCTION\nINFER verdict => response" in io_rendered
            and VERDICT not in io_rendered
            and "The OUTPUT formats" in catalog_io
            and enumerated.get("verdict", ())[:2] == ("inline", VERDICT)
            and VERDICT in catalog_io):
        held("OUTPUT is a name of the enumeration",
             "a doc declares, a doc names, the block carries the NAME -- the catalog teaches")
    else:
        failures.append(f"  ✗ OUTPUT name                 {judged.output!r} "
                        f"{io_rendered[:80]!r} {enumerated.get('verdict')!r}")

    expect("format-unknown", lambda: io_c().start(document(
        "---\nname: X\noutput: nope\nproc: |\n  INFER\n---\nx\n", at=meta)))
    (meta / "DOUBLE.md").write_text(
        "---\nname: DOUBLE\nformats: |\n  json  stdin  again\n---\n", encoding="utf-8")
    expect("format-doubled", lambda: io_c().start(document(
        "---\nname: X\nproc: |\n  INFER\n---\nx\n", at=meta)))
    (meta / "DOUBLE.md").write_text(
        "---\nname: DOUBLE\nformats: |\n  nomode  whatever it is\n---\n", encoding="utf-8")
    expect("format-malformed", lambda: io_c().start(document(
        "---\nname: X\nproc: |\n  INFER\n---\nx\n", at=meta)))
    (meta / "DOUBLE.md").unlink()

    # --- a consumed production is captured -- typed, validated, seeded ----------------
    (meta / "JSHIP.md").write_text(
        "---\nname: JSHIP\ndescription: takes a payload\ninput: json\nproc: |\n"
        "  HOOK shipped\n---\nship it\n", encoding="utf-8")
    producer = document(
        "---\nname: X\nkind: proc\ndescription: makes json\noutput: json\nproc: |\n"
        "  INFER\n  CALL JSHIP.md\n---\nproduce the payload\n", at=meta)
    asked_io = io_c().start(producer)
    if (" -   (" in asked_io.next_call and "stdin" in asked_io.next_call
            and "▶ CONTINUE" in render(asked_io)):
        held("a consumed production is captured", "the closing hands the mode: json travels on stdin")
    else:
        failures.append(f"  ✗ capture closing             {asked_io.next_call!r}")

    empty_miss = io_c().submit("")
    bad_json = io_c().submit("{oops")
    landed = io_c().submit('{"ok": 1}')
    if ("empty production" in empty_miss.deviation
            and "not one valid JSON value" in bad_json.deviation and "REPAIR" in render(bad_json)
            and over(landed)):
        held("the capture validates", "empty missed, bad json REPAIRed, one valid value lands -- PROVE's seed")
    else:
        failures.append(f"  ✗ capture validation          {empty_miss.deviation!r} / "
                        f"{bad_json.deviation!r} / {landed and landed.command!r}")

    (meta / "NAMED.md").write_text(
        "---\nname: NAMED\ndescription: opens on a line\ninput: line\nproc: |\n"
        "  HOOK landed\n---\ngo there\n", encoding="utf-8")
    seeder = document(
        "---\nname: X\nkind: proc\ndescription: names a member\noutput: line\nproc: |\n"
        "  INFER\n  CALL NAMED.md\n---\nname the member\n", at=meta)
    io_c().forget()
    seeded_ask = io_c().start(seeder)
    seeded_end = io_c().submit("io")
    if seeded_ask.next_call.endswith(" <output>") and over(seeded_end):
        held("the seed opens the callee", "a `line` travels inline; the callee opened on the caller's production")
    else:
        failures.append(f"  ✗ seed                        {seeded_ask.next_call!r} / "
                        f"{seeded_end and seeded_end.command!r}")

    io_c().forget()
    mismatch = document(
        "---\nname: X\nkind: proc\ndescription: wrong feed\noutput: table\nproc: |\n"
        "  INFER\n  CALL JSHIP.md\n---\nx\n", at=meta)
    expect("format-mismatch", lambda: io_c().start(mismatch))

    (meta / "LOST.md").write_text(
        "---\nname: LOST\nkind: proc\ndescription: speaks to the chat\noutput: json\nproc: |\n"
        "  INFER\n  SERVE TAGGED.md\n---\nx\n", encoding="utf-8")
    warned = compiling.lint(meta)
    if not any("forgotten" in one for one in warned):
        held("a chat production is no smell", "the channel is a rendered state -- "
             "the lint presumes no oversight")
    else:
        failures.append(f"  ✗ lint                        {warned!r}")
    (meta / "LOST.md").unlink()

    # --- the flow is UNIVERSAL: a CALL yields its callee's last production -------------
    (meta / "LISTER.md").write_text(
        "---\nname: LISTER\ndescription: lists\noutput: json\nproc: |\n  INFER\n---\n"
        "the siblings\n", encoding="utf-8")
    lister_caller = document(
        "---\nname: X\nkind: proc\ndescription: picks\nproc: |\n  CALL LISTER.md\n"
        "  PICK member\n---\nchoose\n", at=meta)
    io_c().forget()
    asked_list = io_c().start(lister_caller)
    flowed = io_c().submit('["io"]')
    if (asked_list.document == "LISTER" and list(flowed.options) == ["io"]
            and str(flowed.instruction) == "PICK member"):
        held("a CALL yields its callee's production",
             "LISTER's list feeds the caller's PICK")
    else:
        failures.append(f"  ✗ universal flow              {flowed.options!r}")
    io_c().forget()

    (meta / "MAKERJ.md").write_text(
        "---\nname: MAKERJ\ndescription: makes json\noutput: json\nproc: |\n  INFER\n"
        "---\nproduce\n", encoding="utf-8")
    chain = document(
        "---\nname: X\nkind: proc\ndescription: chains\nproc: |\n  CALL MAKERJ.md\n"
        "  CALL JSHIP.md\n---\nx\n", at=meta)
    boundary_ask = io_c().start(chain)
    boundary_end = io_c().submit('{"through": true}')
    if (" -   (" in boundary_ask.next_call and boundary_ask.document == "MAKERJ"
            and over(boundary_end)):
        held("consumption crosses the pop",
             "a callee's LAST INFER is consumed by its CALLER's continuation -- captured, flowed, shipped")
    else:
        failures.append(f"  ✗ boundary consumption        {boundary_ask.next_call!r} / "
                        f"{boundary_end and boundary_end.command!r}")
    io_c().forget()

    (meta / "ANYONE.md").write_text(
        "---\nname: ANYONE\ndescription: takes anything\ninput: any\nproc: |\n"
        "  HOOK taken\n---\nx\n", encoding="utf-8")
    (meta / "MAKERT.md").write_text(
        "---\nname: MAKERT\ndescription: makes a table\noutput: table\nproc: |\n  INFER\n"
        "---\nproduce\n", encoding="utf-8")
    tolerant = document(
        "---\nname: X\nkind: proc\ndescription: chains any\nproc: |\n  CALL MAKERT.md\n"
        "  CALL ANYONE.md\n---\nx\n", at=meta)
    any_ask = io_c().start(tolerant)
    strict = document(
        "---\nname: X\nkind: proc\ndescription: chains wrong\nproc: |\n  CALL MAKERT.md\n"
        "  CALL JSHIP.md\n---\nx\n", at=meta)
    if any_ask.document == "MAKERT" and "stdin" in any_ask.next_call:
        held("`any` is the wildcard", "a table producer feeds an `input: any` without a mismatch")
    else:
        failures.append(f"  ✗ any                         {any_ask.document!r}")
    io_c().forget()
    expect("format-mismatch", lambda: io_c().start(strict))


def formats(bench, env) -> None:
    """An instance's redeclaration wins over the engine's; the engine's forms reach the
    enumeration from `language.FORMATS`."""
    held, failures = bench.held, bench.failures
    installed = env.made / "FORMATS.md"
    seeded = installed.read_text(encoding="utf-8") if installed.is_file() else None

    installed.write_text(OVERRIDE, encoding="utf-8")
    shaped = compiling.format_enumeration(env.made)
    catalog_shaped = compiling.render_tools(env.made)
    if (shaped["table"][1] == OWN_TABLE
            and shaped["table"][2] == "FORMATS.md"
            and shaped["free"][1] == language.FORMATS["free"][1]
            and shaped["free"][2] == "engine"
            and OWN_TABLE in catalog_shaped):
        held("a format is yours to override",
             "the instance redeclares a DESCENDED name and wins -- instance over "
             "packages over engine, customizing is redeclaring at home")
    else:
        failures.append(f"  ✗ format override             {shaped.get('table')!r} / "
                        f"{shaped.get('free')!r}")
    if seeded is None:
        installed.unlink()
    else:
        installed.write_text(seeded, encoding="utf-8")

    installed_forms = compiling.format_enumeration(env.made)
    if (installed_forms["table"][1] == language.FORMATS["table"][1]
            and installed_forms["table"][2] == "engine"
            and installed_forms["free"][2] == "engine"
            and seeded is not None):
        held("the mechanical forms reach the enumeration from the engine",
             "table's rich shape rides language.FORMATS -- the installed FORMATS.md is the home of overrides")
    else:
        failures.append(f"  ✗ airy presentation           {installed_forms['table'][1][:60]!r} / "
                        f"{installed_forms['free'][1][:60]!r} seeded={seeded is not None}")


def pick_options(bench, env) -> None:
    """The PICK judges the whole form of its options and refuses what no capture judged."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    floor = document(FLOOR, at=env.made)

    def fresh():
        conductor = env.conductor("t")
        conductor.forget()
        conductor.start(floor)
        return conductor

    def trace() -> list[dict]:
        return run.trace(env, "t")

    def repaired(answer: str, expected: str) -> bool:
        """-> the production MISSES: the document reopens at its INFER, the miss named."""
        fresh()
        block = env.conductor("t").submit(answer)
        return (block.instruction.keyword == "INFER" and block.repair == 1
                and expected in (block.deviation or "") and "OPTIONS" in (block.deviation or "")
                and "TypeError" not in render(block))

    # --- the forms a renderer cannot print each repair, the miss named -----------------
    seen = [repaired(answer, expected) for answer, expected in CRASHING if expected]
    if all(seen) and len(seen) == 4:
        held("a list of non-scalars repairs, never crashes",
             "objects, nested lists, null and booleans each reopen the document at REPAIR 1 -- "
             "the DEVIATION names the OPTIONS' element, the renderer never meets a dict")
    else:
        failures.append(f"  ✗ non-scalar options          {seen}")

    # --- the malformed whole forms each repair too -------------------------------------
    seen = [repaired(answer, expected) for answer, expected in SILENT]
    if all(seen):
        held("the whole form is judged", "an empty element, a twin, an empty array, a scalar "
             "and an object each miss by name")
    else:
        failures.append(f"  ✗ silent forms                {seen}")

    # --- a number is an option like another --------------------------------------------
    fresh()
    numbers = env.conductor("t").submit("[1, 2]")
    rendered = render(numbers)
    missed = env.conductor("t").submit("3")
    fresh()
    env.conductor("t").submit("[1, 2]")
    taken = env.conductor("t").submit("2")
    if (list(numbers.options) == ["1", "2"] and _section(rendered, "▌ OPTIONS") == ["1", "2"]
            and "`3` is not in OPTIONS (1, 2)" in (missed.deviation or "")
            and bench.over(taken)):
        held("a number is an option", "`[1, 2]` renders OPTIONS `1` and `2`; `2` is taken "
             "verbatim and closes the run, `3` misses with the options joined as text")
    else:
        failures.append(f"  ✗ numeric options             {list(numbers.options)!r} "
                        f"{missed.deviation!r} {taken and taken.end!r}")

    # --- the witness: its OPTIONS, its PICK line, its closing, and their weights --------
    fresh()
    witness = env.conductor("t").submit(f'["{WITNESS[0]}", "{WITNESS[1]}"]')
    shown = render(witness)
    weighed = next((one.get("weight", {}) for one in reversed(trace())
                    if one.get("kind") == "block" and one.get("command") == "PICK verdict"), {})
    heads = _sections(shown)
    order = [next((i for i, one in enumerate(heads) if one.startswith(head)), -1)
             for head in ("▌ DOC", "▌ OPTIONS", "▌ INSTRUCTION", "▶ CONTINUE")]
    instruction = _section(shown, "▌ INSTRUCTION")
    if (list(witness.options) == WITNESS and _section(shown, "▌ OPTIONS") == WITNESS
            and -1 not in order and order == sorted(order)
            and instruction and instruction[0].startswith("PICK verdict ")
            and "=> tool" in instruction[0]
            and weighed.get("options") == sum(len(one) + 1 for one in WITNESS)
            and weighed.get("instruction") == len(witness.command) + len(witness.output)
            and weighed.get("total", 0) > weighed["options"] + weighed["instruction"]
            and not witness.deviation):
        held("the witness stands at the byte", "a list of strings renders its OPTIONS one per "
             "line, the PICK line and the closing, in order -- the options and the instruction "
             f"weigh what they print ({weighed['options']} c, {weighed['instruction']} c of "
             f"{weighed['total']} c)")
    else:
        failures.append(f"  ✗ witness                     {heads!r} {instruction!r} {weighed!r}")

    # --- what no capture judged refuses by name; the document with no producer too ----
    env.write("procs/LISTER.md",
              "---\nname: LISTER\nkind: proc\ndescription: lists\noutput: json\nproc: |\n  INFER\n"
              "---\nlist\n")
    env.write("procs/ELECTOR.md",
              "---\nname: ELECTOR\nkind: proc\ndescription: elects from its seed\ninput: json\n"
              "proc: |\n  PICK member\n---\nelect\n")
    seeded = env.write("procs/SEEDED.md", "---\nname: SEEDED\nkind: proc\ndescription: chains\n"
                       "proc: |\n  CALL LISTER.md\n  CALL ELECTOR.md\n---\nx\n")
    conductor = env.conductor("s")
    conductor.forget()
    conductor.start(seeded)
    expect("options-invalid", lambda: env.conductor("s").submit('[{"id": "a"}]'))
    bare = env.write("procs/BARE.md",
                     "---\nname: BARE\nkind: proc\ndescription: bare\nproc: |\n  PICK x\n---\n")
    conductor = env.conductor("b")
    conductor.forget()
    expect("options-empty", lambda: conductor.start(bare))
    held("the guard refuses by name", "a list arrived by a seed, judged by no capture, refuses "
         "`options-invalid`; a PICK with no producer still refuses `options-empty`")

    # --- the trace: the answer, the repair, the REPAIR block ---------------------------
    fresh()
    env.conductor("t").submit('[{"id": "approve"}]')
    events = trace()
    kinds = [one.get("kind") for one in events]
    repair_block = next((one for one in events if one.get("kind") == "block"
                         and one.get("deviation")), None)
    if (kinds.count("answer") == 1 and kinds.count("repair") == 1 and repair_block is not None
            and "OPTIONS" in repair_block["deviation"]
            and repair_block.get("weight", {}).get("total", 0) > 0):
        held("the trace says the miss", "one `answer` line, one `repair` line, and the REPAIR "
             f"block weighed ({repair_block['weight']['total']} c) with its deviation")
    else:
        failures.append(f"  ✗ trace                       {kinds!r}")


def answer_channel(bench) -> None:
    """The trace's `answer` line carries the step's channel."""
    held, failures = bench.held, bench.failures
    env = bench.env("answer-channel")

    def answers(key: str) -> list[dict]:
        return [one for one in run.trace(env, key) if one.get("kind") == "answer"]

    # --- a consumed production and the PICK that takes it ---------------------------
    env.write("procs/CHOOSER.md",
              "---\nname: CHOOSER\nkind: proc\ndescription: lists, then picks\noutput: json\n"
              "proc: |\n  INFER\n  PICK member\n---\nlist the members, then pick one\n")
    chooser = env.conductor("c")
    chooser.start(chooser.boot("CHOOSER.md"))
    env.conductor("c").submit('["ada", "bob"]')
    env.conductor("c").submit("ada")
    told = [(one.get("instruction", "").split(" ")[0], one.get("channel")) for one in answers("c")]
    if told == [("INFER", "tool (heredoc)"), ("PICK", "tool")]:
        held("the answer line carries its channel", "the consumed INFER `tool (heredoc)`, the "
             "PICK `tool` -- derived where the block derives it, nothing else moves")
    else:
        failures.append(f"  ✗ consumed channel            {told!r}")

    # --- a stray production on a response step (the turn's WORK, `=> response`) ---------
    stray = env.conductor("s")
    opening = stray.resume(stray.boot("BOOT.md"))
    bounced = env.conductor("s").submit(STRAY)
    lines = answers("s")
    if (opening.instruction.keyword == "WORK" and lines
            and lines[-1].get("channel") == "response"
            and lines[-1].get("given") == STRAY
            and bounced.deviation and bounced.instruction.keyword == "WORK"):
        held("a stray production says its channel", "the response step's answer line reads "
             "`response` -- the soft catch bounces it, the reader counts no value")
    else:
        failures.append(f"  ✗ stray channel               {[(l.get('instruction'), l.get('channel')) for l in lines]!r} "
                        f"{bounced and bounced.deviation!r}")


def scenario(bench) -> int:
    outputs(bench)
    flow = bench.env("pick-options")
    formats(bench, flow)
    pick_options(bench, flow)
    answer_channel(bench)
    return 0
