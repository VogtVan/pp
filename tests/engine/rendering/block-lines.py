"""Scenario `block-lines` -- the shape of a rendered output, on one house:
- the weld: every section opens on a blank line; the laws stand between a segment's readings
  and its INSTRUCTION; the tool's channel never fuses; the packages' state line sits under the output's heading, one cell per package
- the heading's hour: once per output, a later output a later hour, the keyless console too
- the closings of a run its principal conducts stand bare; after a judged proof the AWAIT
  stands bare too, no look-ahead
- a view cut under the cap says so by ONE fact line at its foot, the same text in both modes
- every instruction line ends on the name of its document in parentheses
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import replace
from datetime import timedelta

from conductor import render, rendering
from conductor.core import language, model
from conductor.execution import blocks
from tests.harness import cli

LAWFUL = ("---\nname: LAWFUL\nkind: doc\ndescription: a law mounted at the boot\n"
          "mount: boot.initialize\nconstraints.behavior: |\n  W1  the witness law sits next to the ask.\n---\n")
SWITCHES = (("alpha", ""), ("beta", "alpha"), ("gamma", "gamma"))

MARK = re.compile(r" · (\d\d):(\d\d):(\d\d) · \+(\d+):(\d\d):(\d\d)$")

VARIABLE = "PP_CONDUCTED_BY_PRINCIPAL"
CLOSED = "---\nname: CLOSED\nkind: proc\ndescription: a witness\nproc: |\n  WORK\n  WORK\n---\nwork\n"
PROVEN = ("---\nname: PROVEN\nkind: proc\ndescription: a witness under a law\n"
          "constraints.production: |\n  Z1  say it plainly\nproc: |\n  INFER\n  PROVE\n---\nsay\n")

KEY = re.compile(r"run ([0-9a-f]{6})")
OVERLAY = "---\nname: TURN\ntools: |\n  +SIDE\n---\n"
SIDE = ("---\nname: SIDE\nkind: proc\ndescription: a side door\noutput: any\n"
        "constraints.production: |\n  S1  say it plainly.\nproc: |\n  INFER\n---\n\nthe side door's brief\n")
NAMED = re.compile(r"^(WORK|INFER|PICK)\b.*\((\w+)\)$")

def _cell(name: str, cause: str) -> str:
    """-> the state a switch says of its package: on, off, or off with its cause."""
    if not cause:
        return f"{name} on"
    return f"{name} off" if cause == name else f"{name} off (<- {cause})"


def _cells(line: str) -> list[str]:
    """-> the cells of a packages' state line, its mark dropped."""
    return line.removeprefix(f"{model.Block.MARK} ").split(" · ")


def _marks(text: str) -> list[re.Match]:
    return [m for line in text.splitlines() if (m := MARK.search(line))]


def _closing(text: str) -> list[str]:
    lines = text.splitlines()
    at = max((i for i, one in enumerate(lines) if one.startswith("▶ ")), default=len(lines))
    return lines[at:]


def _led(call):
    """-> `call()` played under a run its principal conducts."""
    spot = os.environ.get(VARIABLE)
    os.environ[VARIABLE] = "true"
    try:
        return call()
    finally:
        if spot is None:
            os.environ.pop(VARIABLE, None)
        else:
            os.environ[VARIABLE] = spot


def weld(bench, env) -> None:
    """The weld of the sections, the tool's channel, the packages' line."""
    held, failures = bench.held, bench.failures
    conductor = env.conductor()
    booted = render(conductor.resume(conductor.boot("BOOT.md")))
    marked = [one for one in booted.splitlines()
              if one.startswith((model.Block.MARK, model.Block.SIGNAL))]
    glued = marked[1:]        # the output's FIRST line has nothing above it to part from
    seams = [f"\n\n{one}" in booted for one in glued]
    if glued and all(seams):
        held("every section opens on a blank line",
             f"{len(glued)} marked lines, none welded to what stands above -- the "
             "INSTRUCTION and the closing come through the same weld as the rest")
    else:
        missing = [one for one, ok in zip(glued, seams) if not ok]
        failures.append(f"  ✗ la soudure                  {missing[:3]!r}")

    titles = [one for one in marked if one.startswith(f"{model.Block.MARK} ")]
    read = (f"{model.Block.MARK} INFORMATION —", f"{model.Block.MARK} NEXT INSTRUCTION CONTEXT —")
    laws = [k for k, one in enumerate(titles) if one == f"{model.Block.MARK} CONSTRAINTS"]
    asks = [k for k, one in enumerate(titles) if one == f"{model.Block.MARK} INSTRUCTION"]
    stranded = [k for k in laws
                if not any(j > k for j in asks)
                or any(one.startswith(read) for one in titles[k:min(j for j in asks if j > k)])]
    if laws and any(one.startswith(read) for one in titles[:laws[0]]) and not stranded:
        held("the laws sit next to the ask",
             f"{len(laws)} CONSTRAINTS section(s), each after its segment's readings and "
             "before its INSTRUCTION, no reading between -- rule and ask share a screen")
    else:
        failures.append(f"  ✗ l'ordre des sections         {titles!r}")

    to_tool = {one for one in language.YIELDING if one not in language.FREE}
    if (to_tool == {"PICK", "PROVE", "FIELD", "NEXT"} and "INFER" in language.FREE
            and "WORK" in language.FREE):
        held("the tool's channel never fuses",
             "the fusion takes FREE productions alone, and a channel reads `tool` for a "
             "PICK, a checkpoint, a described door's field, a leaving document's successor "
             "or a CONSUMED production -- "
             "exactly what it refuses to fuse: the closing's command always answers the "
             "LAST step rendered")
    else:
        failures.append(f"  ✗ le canal tool               {sorted(to_tool)!r}")

    cells = rendering.packages(SWITCHES)
    switched = replace(conductor.resume(conductor.boot("BOOT.md")), switches=SWITCHES[:2])
    lines = rendering.head(switched).splitlines()
    if (cells.startswith(f"{model.Block.MARK} ")
            and _cells(cells) == [_cell(*one) for one in SWITCHES]
            and rendering.packages(()) == ""
            and len(lines) == 2 and lines[0].startswith(f"{model.Block.MARK} pp · ")
            and lines[1].startswith(f"{model.Block.MARK} ")
            and _cells(lines[1]) == [_cell(*one) for one in SWITCHES[:2]]
            and f"{model.Block.MARK} pp · " not in lines[1]):
        held("the packages' state says itself",
             "one cell per package: `on` where it plays, `off` where a switch took it out, "
             "`off (<- <dependency>)` where its requirement did -- and the line sits UNDER the "
             "output's own heading, the two welded by a single newline: one heading, two lines; "
             "nothing to say, no line")
    else:
        failures.append(f"  ✗ l-etat-des-packages         {cells!r} {lines[-1:]!r}")


def clock(bench, env) -> None:
    """The heading's hour: read at the render, relative to the run's -new."""
    held, failures = bench.held, bench.failures
    real = blocks.clock
    conductor = env.conductor()
    frozen = {"after": timedelta(seconds=65)}
    blocks.clock = lambda: ((blocks._opened_at(conductor._log or "") or real()) + frozen["after"])
    try:
        text = render(conductor.resume(conductor.boot("BOOT.md")))
        opened = blocks._opened_at(conductor._log)
        first = text.splitlines()[0]
        marks = _marks(text)
        local = (opened + frozen["after"]).astimezone().strftime("%H:%M:%S")
        if (first.startswith("▌ pp · ") and len(marks) == 1 and MARK.search(first)
                and first.endswith(f" · {local} · +0:01:05")):
            held("the output's heading says the hour once", f"`{first[-24:]}` on the boot -- "
                 "the local hour and +0:01:05 since -new, the mark once")
        else:
            failures.append(f"  ✗ clock once                 {first!r} marks={len(marks)}")

        frozen["after"] = timedelta(hours=1, minutes=2, seconds=3)
        later = render(conductor.forward(""))
        later_first = later.splitlines()[0]
        peeked = conductor.peek()
        peek_text = render(peeked) if peeked else ""
        if (later_first.endswith(" · +1:02:03") and len(_marks(later)) == 1
                and peek_text.splitlines()[0].endswith(" · +1:02:03")):
            held("a later output says a later hour", "`+1:02:03` on the advance and on the peek")
        else:
            failures.append(f"  ✗ clock later                {later_first!r} {peek_text.splitlines()[:1]!r}")
    finally:
        blocks.clock = real

    shelf = env.cli()
    if shelf.returncode == 0 and len(_marks(shelf.stdout)) == 1:
        held("the keyless console shows the hour once", "it shows the pending block, the mark with it")
    else:
        failures.append(f"  ✗ keyless clock              rc={shelf.returncode} {shelf.stdout[:160]!r}")


def closing_notes(bench, env) -> None:
    """A run its principal conducts closes no output that owes no call: no closing line, no note."""
    held, failures = bench.held, bench.failures
    closed = env.write("CLOSED.md", CLOSED)
    proven = env.write("PROVEN.md", PROVEN)

    conductor = env.conductor()
    first = _led(lambda: conductor.start(closed))
    key = conductor.run_id
    env.conductor(key).submit("")                  # the second WORK: pending, its closing bare
    final = env.conductor(key).submit("")          # the frontier comes at the principal's call
    work_tail, final_tail = _closing(render(first)), _closing(render(final))
    if work_tail == [] and final_tail == []:
        held("the principal's outputs close on no line", "the pending WORK and the end of the passage end on "
             "their last section -- nothing tells the agent who calls next")
    else:
        failures.append(f"  ✗ bare closings                {work_tail} {final_tail}")

    env.conductor(key).forget()
    conductor = env.conductor()
    opened = _led(lambda: conductor.start(proven))
    key = conductor.run_id
    before = _closing(render(opened))
    proving = env.conductor(key).submit("")                     # the principal's advance: the proof block
    judged = env.conductor(key).submit(json.dumps([{"code": "Z1", "evidence": "a line", "verdict": "ok"}]))
    tail = _closing(render(judged))
    # the INFER stays pending until the principal's call: no closing line; the written PROVE
    # asks its proof; the end of the passage after it closes on no line either
    if (before == [] and proving.output == "proof" and tail == []):
        held("the end after a written proof closes on no line", "no closing on the INFER, the PROVE asked, "
             "none at the end")
    else:
        failures.append(f"  ✗ bare after proof             before={before} tail={tail}")


def view_fact(bench, env) -> None:
    """A view over the cap is clipped, and the clip is said by a fact at the foot -- one text, both modes."""
    held, failures = bench.held, bench.failures
    env.write("LONG.md", "---\nname: LONG\nkind: doc\n---\n\n" + "a long line of matter\n" * 12000 + "\n")
    # past the principal's floor too: the view is clipped in both modes, under each one's cap
    viewrun = env.write("VIEWRUN.md", "---\nname: VIEWRUN\nkind: proc\ndescription: a witness\nproc: |\n"
                                      "  SERVE LONG.md\n  WORK\n---\nread\n")
    env.write("SETTINGS.md", "---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: 2000\n---\n")
    views = {}
    for mode, led in (("llm", False), ("principal", True)):
        conductor = env.conductor()
        conductor.forget()
        block = _led(lambda: conductor.start(viewrun)) if led else conductor.start(viewrun)
        views[mode] = conductor.shown(block)
    feet = {mode: [one for one in text.splitlines() if one.startswith("   (")] for mode, text in views.items()}
    shapes = {mode: [re.sub(r"\d+", "N", one) for one in feet[mode]] for mode in feet}
    caps = {"llm": 2000, "principal": 200000}
    if (all(len(feet[mode]) == 1 for mode in feet) and shapes["llm"] == shapes["principal"]
            and all(len(text) <= caps[mode] for mode, text in views.items())
            and all(text.rstrip().splitlines()[-1] == feet[mode][0] for mode, text in views.items())
            and all("(this view" not in text for text in views.values())):
        held("a cut view says so by one fact at its foot", f"`{shapes['llm'][0].strip()}` closes the view in both "
             "modes, the same text (the count apart), nothing in the body says it")
    else:
        failures.append(f"  ✗ the view's fact             {feet} sizes={[len(t) for t in views.values()]}")


def instruction_names(bench, env) -> None:
    """Every instruction line of a fused output ends on the name of its document."""
    held, failures = bench.held, bench.failures
    env.write("procs/TURN.md", OVERLAY)
    env.write("procs/SIDE.md", SIDE)
    opened = cli(env.engine, "-new", "go", cwd=env.root)
    key = KEY.search(opened.stdout).group(1) if KEY.search(opened.stdout) else ""
    door = cli(env.engine, key, "-s", "SIDE", cwd=env.root)
    lines = [line for text in (opened.stdout, door.stdout) for line in text.splitlines()
             if line.startswith(("WORK ", "INFER ", "PICK ")) and "=>" in line]
    named = [NAMED.match(line) for line in lines]
    if (lines and all(named) and any(m.group(2) == "TURN" for m in named)
            and any(m.group(2) == "SIDE" for m in named)
            and any("INFER any => words  (SIDE)" == line for line in lines)):
        held("every instruction line names its document", f"{len(lines)} lines, e.g. {lines[:3]}")
    else:
        failures.append(f"  ✗ the lines                   {lines}")


def scenario(bench) -> int:
    env = bench.env("lines")
    env.write("procs/LAWFUL.md", LAWFUL)     # a law in force at the boot: its section has a place
    weld(bench, env)
    clock(bench, env)
    closing_notes(bench, env)
    instruction_names(bench, env)
    view_fact(bench, env)
    return 0
