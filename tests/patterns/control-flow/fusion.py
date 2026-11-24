"""Scenario `fusion` -- the pattern `control-flow/fusion`, played from its demonstration:
- `instructions_fusion: max` renders the certain stretch in one output: one INSTRUCTION title, one
  line per step, the heading's range `{1-3/3}`, each step said on `terminal` traced `print-due`, on no
  closing line; the principal's call after them ends the passage on AWAIT
- a number caps the stretch: two steps on no closing line, the rest on the principal's next call
- a document's own `fusion: none` outranks the instance's `max`: one step per output
- the scope makes the segment: two steps of two documents under the same laws read in ONE segment, a line
  each naming its document; a second document under a law of its own opens a second segment
- `tools_in_scope`: two documents of the same laws, the second with an offer of its own -- one segment whose
  TOOLS is the union of the offers under `false`, the default; two segments under `true`
- the proof is a value like any other: under a said step of another document of the same laws it joins the
  segment and closes the output, its codes on its line; a line and its proof of one document stay in one
  output the same way
"""
from __future__ import annotations

from conductor.core import messages
from conductor import render
from conductor.core import language
from tests.harness import closing, demonstrated, plant, stepped, titled, titles, traced

DEMOS = ("APART.md", "CHECKED.md", "DUET.md", "GEARED.md", "LEFT.md", "RIGHT.md", "RULED.md", "SOLO.md",
         "STEPPED.md", "TOOLED.md", "TRIO.md")
TUNED = "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: {}\n---\n"
SCOPED = "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: max\ntools_in_scope: {}\n---\n"
MARK = f"{messages.MARK} "


def _lines(block) -> int:
    """-> the instruction lines a block renders."""
    return sum(1 for one in render(block).splitlines() if one.startswith("INFER "))


def _segments(shown: str) -> list[str]:
    """-> the headings of a rendering's segments: its marked lines that open no section of the engine's list."""
    return [one for one in titles(shown)
            if one.startswith(MARK) and not language.section_of(one.removeprefix(MARK))[0]]


def _asked(shown: str) -> list[str]:
    """-> the document each step line of a rendering names, in order."""
    return [one.rsplit("(", 1)[-1].rstrip(")") for one in shown.splitlines()
            if one.startswith(("INFER ", "WORK ", "PICK ")) and one.endswith(")")]


def _under(shown: str, title: str) -> list[str]:
    """-> the lines of every section `title` of a rendering."""
    lines, found, inside = shown.splitlines(), [], False
    for one in lines:
        if one.startswith((MARK, "▶ ")):
            inside = one == title
        elif inside and one.strip():
            found.append(one)
    return found


def scope_cases(bench, env) -> None:
    """The scope makes the segment; the setting `tools_in_scope`; the proof and its rule."""
    held, failures = bench.held, bench.failures

    def opened(name: str):
        conductor = env.conductor()
        conductor.forget()
        block = conductor.start(conductor.boot(name))
        return (render(block) if block is not None else ""), conductor.run_id

    # --- the same laws: one segment; a law of its own: a second segment ------------------------
    env.write("SETTINGS.md", TUNED.format("max"))
    same, key = opened("DUET.md")
    env.conductor(key).forget()
    apart, key = opened("APART.md")
    env.conductor(key).forget()
    ruled = [one for one in _under(apart, titled(language.CONSTRAINTS)) if one.startswith("FU2 ")]
    if (len(_segments(same)) == 1 and _asked(same) == ["LEFT", "RIGHT"]
            and len(_segments(apart)) == 2 and _asked(apart) == ["LEFT", "RULED"] and len(ruled) == 1):
        held("the scope makes the segment", f"DUET: LEFT's step and RIGHT's under `{_segments(same)[0]}`, one "
             "segment, a line each; APART: RULED opens a second segment, FU2 said there once")
    else:
        failures.append(f"  ✗ the scope and the segment   same={_segments(same)} {_asked(same)} "
                        f"apart={_segments(apart)} {_asked(apart)} ruled={len(ruled)}")

    # --- tools_in_scope: the offers join the scope under `true` alone ---------------------------
    shown = {}
    for value in ("false", "true"):
        env.write("SETTINGS.md", SCOPED.format(value))
        shown[value], key = opened("GEARED.md")
        env.conductor(key).forget()
    env.write("SETTINGS.md", TUNED.format("max"))
    default, key = opened("GEARED.md")
    env.conductor(key).forget()
    offered = _under(shown["false"], titled(language.TOOLS))
    if (len(_segments(shown["false"])) == 1 and len(_segments(default)) == 1
            and titles(shown["false"]).count(titled(language.TOOLS)) == 1
            and len(offered) == 1 and "TRIO" in offered[0].strip("[]").split()
            and _asked(shown["false"]) == ["LEFT", "TOOLED"]
            and len(_segments(shown["true"])) == 2 and _asked(shown["true"]) == ["LEFT", "TOOLED"]):
        held("tools_in_scope decides whether an offer opens a segment", "GEARED under `false` and without the "
             "key: one segment, its TOOLS the union of the offers, TRIO there once; under `true`: two segments")
    else:
        failures.append(f"  ✗ tools_in_scope              false={_segments(shown['false'])} offered={offered} "
                        f"default={_segments(default)} true={_segments(shown['true'])}")

    # --- the proof: a value like any other, the last step of the output ---------------------------
    first, key = opened("CHECKED.md")
    env.conductor(key).forget()
    solo, key = opened("SOLO.md")
    env.conductor(key).forget()
    checked = [one for one in first.splitlines() if one.startswith("INFER proof [FU1]")]
    proved = [one for one in solo.splitlines() if one.startswith("INFER proof [FU1]")]
    if (len(_segments(first)) == 1 and _asked(first) == ["CHECKED", "LEFT", "CHECKED"] and len(checked) == 1
            and closing(first)[:1] != ["▶ CONTINUE"]
            and len(_segments(solo)) == 1 and _asked(solo) == ["SOLO", "SOLO"] and len(proved) == 1):
        held("a proof closes the output it joins", "CHECKED: its line, LEFT's and the proof FU1 in one output, "
             "one segment, no CONTINUE; SOLO: the line and its proof in one output, one segment, FU1 on the "
             "proof's line")
    else:
        failures.append(f"  ✗ the proof joins the output  first={_segments(first)} {_asked(first)} "
                        f"{closing(first)[:1]} checked={len(checked)} "
                        f"solo={_segments(solo)} {_asked(solo)} proved={len(proved)}")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("fusion", bare=True)
    found = demonstrated("control-flow", "fusion")
    if found != sorted(DEMOS):
        failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    plant(env, "control-flow", "fusion", DEMOS)

    def opened(name: str):
        conductor = env.conductor()
        conductor.forget()
        return conductor.start(conductor.boot(name)), conductor.run_id

    # --- max: the certain stretch in one output ----------------------------------------------
    env.write("SETTINGS.md", TUNED.format("max"))
    fused, key = opened("TRIO.md")
    shown = render(fused) if fused is not None else ""
    due = [one.get("kind") for one in traced(env, key)].count("print-due")
    said = sum(1 for one in shown.splitlines() if one.startswith("INFER ") and f"=> {language.TERMINAL}  (" in one)
    ended = stepped(lambda: env.conductor(key), "", by="forward")    # the principal's call ends the passage
    if (fused is not None and not fused.wait and _lines(fused) == 3
            and titles(shown).count(titled(language.INSTRUCTION)) == 1 and titles(shown)[0] == "▌ TRIO{1-3/3}"
            and shown.count("▌ TRIO") == 1 and shown.count("▌ pp · run ") == 1 and said and due == said
            and closing(shown) == []
            and ended is not None and ended.wait and closing(render(ended))[:1] == ["▶ AWAIT"]):
        held("max renders the certain stretch", f"three steps under one INSTRUCTION title, "
             f"the heading `{titles(shown)[0]}`, the {said} said on `terminal` traced `print-due`, on no closing "
             "line; the principal's call after them ends the passage on AWAIT")
    else:
        failures.append(f"  ✗ fusion max                  {titles(shown)[:1]!r} {_lines(fused)} due={due} said={said} "
                        f"wait={fused and fused.wait} closing={closing(shown)!r} ended={ended and closing(render(ended))!r}")
    env.conductor(key).forget()

    # --- a number caps it ---------------------------------------------------------------------
    env.write("SETTINGS.md", TUNED.format("2"))
    capped, key = opened("TRIO.md")
    rest = stepped(lambda: env.conductor(key), "", by="forward")
    if (capped is not None and not capped.wait and _lines(capped) == 2
            and titles(render(capped)).count(titled(language.INSTRUCTION)) == 1
            and closing(render(capped)) == []
            and rest is not None and _lines(rest) == 1 and (rest.position, rest.total) == (3, 3)):
        held("a number caps the stretch", "two steps this output, on no closing line; the principal's call "
             "hands the third to the next output")
    else:
        failures.append(f"  ✗ fusion 2                    {capped and _lines(capped)} closing={capped and closing(render(capped))!r} "
                        f"{rest and (rest.stack, rest.wait)!r}")
    env.conductor(key).forget()

    # --- the document's own pace wins --------------------------------------------------------
    env.write("SETTINGS.md", TUNED.format("max"))
    paced, key = opened("STEPPED.md")
    then = stepped(lambda: env.conductor(key), "", by="forward")
    if (paced is not None and not paced.wait and _lines(paced) == 1
            and then is not None and _lines(then) == 1 and (then.position, then.total) == (2, 2)):
        held("a document pins its own fusion", "`fusion: none` in its front matter: one step per "
             "output under the instance's max")
    else:
        failures.append(f"  ✗ the document's pace         {paced and _lines(paced)} {then and then.stack!r}")
    env.conductor(key).forget()
    scope_cases(bench, env)
    return 0
