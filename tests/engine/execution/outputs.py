"""Scenario `outputs` -- 3 case(s), in the monolith's order:
- IO.1: OUTPUT is a NAME of the enumeration -- pp dictates the form
- IO.3: a consumed production is captured -- typed, validated, seeded
- the flow is UNIVERSAL: a CALL yields its callee's last production
"""
from __future__ import annotations

from conductor import Conductor, render, compiling, discovery
from tests.harness import document


def scenario(bench) -> int:
    held, expect, over, failures = bench.held, bench.expect, bench.over, bench.failures
    # --- the first environment: three instances side by side, `core` the home
    town = bench.town(["core", "perso", "sw7-hub"])
    siblings = town.siblings
    home = town["core"].member
    script = town["core"].engine
    (home.meta / "TAGGED.md").write_text("some corpus\n", encoding="utf-8")


    def conductor() -> Conductor:
        """A fresh object every time -- what survives must survive on disk, not in memory."""
        return Conductor(home, siblings, script, "t")


    # --- IO.1: OUTPUT is a NAME of the enumeration -- pp dictates the form ------------
    io_siblings = bench.town(["io"]).siblings
    io_home = discovery.member(io_siblings, "io")

    def io_c() -> Conductor:
        return Conductor(io_home, io_siblings, script, "t")

    (io_home.meta / "FORMS.md").write_text(
        "---\nname: FORMS\ndescription: local formats\nformats: |\n"
        "  verdict  inline  approve, revise or reject -- one word\n"
        "  json     stdin   one valid JSON value, nothing around it\n"
        "  line     inline  one line, plainly worded\n"
        "  table    stdin   a markdown table\n---\n", encoding="utf-8")
    judged = io_c().start(document(
        "---\nname: X\nkind: proc\ndescription: judge\noutput: verdict\nproc: |\n"
        "  INFER\n---\njudge the draft\n", at=io_home.meta))
    io_rendered = render(judged)
    catalog_io = compiling.render_tools(io_home.meta)
    if (judged.output == "verdict" and "▌ INSTRUCTION\nINFER verdict => chat" in io_rendered
            and "approve, revise" not in io_rendered
            and "The OUTPUT formats" in catalog_io
            and "`verdict`** (inline) — approve, revise or reject" in catalog_io):
        held("OUTPUT is a name of the enumeration",
             "a doc declares, a doc names, the block carries the NAME -- the catalog teaches")
    else:
        failures.append(f"  ✗ OUTPUT name                 {judged.output!r} "
                        f"{io_rendered[:80]!r}")

    expect("format-unknown", lambda: io_c().start(document(
        "---\nname: X\noutput: nope\nproc: |\n  INFER\n---\nx\n", at=io_home.meta)))
    (io_home.meta / "DOUBLE.md").write_text(
        "---\nname: DOUBLE\nformats: |\n  json  stdin  again\n---\n", encoding="utf-8")
    expect("format-doubled", lambda: io_c().start(document(
        "---\nname: X\nproc: |\n  INFER\n---\nx\n", at=io_home.meta)))
    (io_home.meta / "DOUBLE.md").write_text(
        "---\nname: DOUBLE\nformats: |\n  nomode  whatever it is\n---\n", encoding="utf-8")
    expect("format-malformed", lambda: io_c().start(document(
        "---\nname: X\nproc: |\n  INFER\n---\nx\n", at=io_home.meta)))
    (io_home.meta / "DOUBLE.md").unlink()

    # --- IO.3: a consumed production is captured -- typed, validated, seeded ----------
    (io_home.meta / "JSHIP.md").write_text(
        "---\nname: JSHIP\ndescription: takes a payload\ninput: json\nproc: |\n"
        "  HOOK shipped\n---\nship it\n", encoding="utf-8")
    producer = document(
        "---\nname: X\nkind: proc\ndescription: makes json\noutput: json\nproc: |\n"
        "  INFER\n  CALL JSHIP.md\n---\nproduce the payload\n", at=io_home.meta)
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

    (io_home.meta / "NAMED.md").write_text(
        "---\nname: NAMED\ndescription: opens on a line\ninput: line\nproc: |\n"
        "  HOOK landed\n---\ngo there\n", encoding="utf-8")
    seeder = document(
        "---\nname: X\nkind: proc\ndescription: names a member\noutput: line\nproc: |\n"
        "  INFER\n  CALL NAMED.md\n---\nname the member\n", at=io_home.meta)
    io_c().forget()
    seeded_ask = io_c().start(seeder)
    seeded_end = io_c().submit("io")
    if (seeded_ask.next_call.endswith(" <output>") and over(seeded_end)):
        held("the seed opens the callee", "a `line` travels inline; the callee opened on the caller's production")
    else:
        failures.append(f"  ✗ seed                        {seeded_ask.next_call!r} / "
                        f"{seeded_end and seeded_end.command!r}")

    io_c().forget()
    mismatch = document(
        "---\nname: X\nkind: proc\ndescription: wrong feed\noutput: table\nproc: |\n"
        "  INFER\n  CALL JSHIP.md\n---\nx\n", at=io_home.meta)
    expect("format-mismatch", lambda: io_c().start(mismatch))

    (io_home.meta / "LOST.md").write_text(
        "---\nname: LOST\nkind: proc\ndescription: speaks to the chat\noutput: json\nproc: |\n"
        "  INFER\n  SERVE TAGGED.md\n---\nx\n", encoding="utf-8")
    warned = compiling.lint(io_home.meta)
    if not any("forgotten" in one for one in warned):
        held("a chat production is no smell", "the channel is a rendered state now -- "
             "the lint stopped presuming an oversight")
    else:
        failures.append(f"  ✗ lint                        {warned!r}")
    (io_home.meta / "LOST.md").unlink()

    # --- the flow is UNIVERSAL: a CALL yields its callee's last production -------------
    (io_home.meta / "LISTER.md").write_text(
        "---\nname: LISTER\ndescription: lists\noutput: json\nproc: |\n  INFER\n---\n"
        "the siblings\n", encoding="utf-8")
    lister_caller = document(
        "---\nname: X\nkind: proc\ndescription: picks\nproc: |\n  CALL LISTER.md\n"
        "  PICK member\n---\nchoose\n", at=io_home.meta)
    io_c().forget()
    asked_list = io_c().start(lister_caller)
    flowed = io_c().submit('["io"]')
    if (asked_list.document == "LISTER" and list(flowed.options) == ["io"]
            and str(flowed.instruction) == "PICK member"):
        held("a CALL yields its callee's production",
             "the doc-name vestige is dead -- LISTER's list feeds the caller's PICK")
    else:
        failures.append(f"  ✗ universal flow              {flowed.options!r}")
    io_c().forget()

    (io_home.meta / "MAKERJ.md").write_text(
        "---\nname: MAKERJ\ndescription: makes json\noutput: json\nproc: |\n  INFER\n"
        "---\nproduce\n", encoding="utf-8")
    chain = document(
        "---\nname: X\nkind: proc\ndescription: chains\nproc: |\n  CALL MAKERJ.md\n"
        "  CALL JSHIP.md\n---\nx\n", at=io_home.meta)
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

    (io_home.meta / "ANYONE.md").write_text(
        "---\nname: ANYONE\ndescription: takes anything\ninput: any\nproc: |\n"
        "  HOOK taken\n---\nx\n", encoding="utf-8")
    (io_home.meta / "MAKERT.md").write_text(
        "---\nname: MAKERT\ndescription: makes a table\noutput: table\nproc: |\n  INFER\n"
        "---\nproduce\n", encoding="utf-8")
    tolerant = document(
        "---\nname: X\nkind: proc\ndescription: chains any\nproc: |\n  CALL MAKERT.md\n"
        "  CALL ANYONE.md\n---\nx\n", at=io_home.meta)
    any_ask = io_c().start(tolerant)
    strict = document(
        "---\nname: X\nkind: proc\ndescription: chains wrong\nproc: |\n  CALL MAKERT.md\n"
        "  CALL JSHIP.md\n---\nx\n", at=io_home.meta)
    if any_ask.document == "MAKERT" and "stdin" in any_ask.next_call:
        held("`any` is the wildcard", "a table producer feeds an `input: any` without a mismatch")
    else:
        failures.append(f"  ✗ any                         {any_ask.document!r}")
    io_c().forget()
    expect("format-mismatch", lambda: io_c().start(strict))
    return 0
