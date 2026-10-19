"""Scenario `block-lines` -- the shape of a rendered output, on one house:
- the weld: every section opens on a blank line; a law says its section; the tool's channel never
  fuses; the packages' state line sits under the output's heading, one cell per package
- the heading's hour: once per output, a later output a later hour, the keyless console too
- the closings of a run its principal conducts stand bare; after a judged proof the look-ahead
  says « proof given »
- every instruction line ends on the name of its document in parentheses
- a proc that declares no `output:` yields `any`, never `free`
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
          "mount: boot.ready\nconstraints.behavior: |\n  W1  the witness law says its section.\n---\n")
SWITCHES = (("alpha", ""), ("beta", "alpha"), ("gamma", "gamma"))

MARK = re.compile(r" · (\d\d):(\d\d):(\d\d) · \+(\d+):(\d\d):(\d\d)$")

VARIABLE = "PP_CONDUCTED_BY_PRINCIPAL"
CLOSED = "---\nname: CLOSED\nkind: proc\ndescription: a witness\nproc: |\n  WORK\n  WORK\n  FINAL\n---\nwork\n"
PROVEN = ("---\nname: PROVEN\nkind: proc\ndescription: a witness under a law\n"
          "constraints.production: |\n  Z1  say it plainly\nproc: |\n  INFER\n  FINAL\n---\nsay\n")

KEY = re.compile(r"run ([0-9a-f]{6})")
OVERLAY = "---\nname: TURN\ntools: |\n  +SIDE\n---\n"
SIDE = ("---\nname: SIDE\nkind: proc\ndescription: a side door\noutput: any\n"
        "constraints.production: |\n  S1  say it plainly.\nproc: |\n  INFER\n---\n\nthe side door's brief\n")
NAMED = re.compile(r"^(WORK|INFER|PICK)\b.*\((\w+)\)$")

FORMLESS = ("---\nname: FORMLESS\nkind: proc\ndescription: a witness without a form\n"
            "proc: |\n  WORK\n  INFER\n---\n\nwork\n")


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
    """The weld of the sections, the label of a law, the tool's channel, the packages' line."""
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

    sections = [one.split(model.Block.MARK)[0].strip().splitlines()
                for one in booted.split(f"{model.Block.MARK} CONSTRAINTS")[1:]]
    labelled = [one[0] for one in sections if one]
    if labelled and all(one.startswith(("production:", "behavior:")) for one in labelled):
        held("a rendered law says its section",
             f"{len(labelled)} CONSTRAINTS section(s), each opening on its group's label "
             "whether or not the other stands: the agent reads what the checkpoint will "
             "ask for, never guesses it")
    else:
        failures.append(f"  ✗ la section dite             {labelled[:3]!r}")

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
    """The closings of a run its principal conducts carry no note that redoes the standing orders."""
    held, failures = bench.held, bench.failures
    closed = env.write("CLOSED.md", CLOSED)
    proven = env.write("PROVEN.md", PROVEN)

    conductor = env.conductor()
    first = _led(lambda: conductor.start(closed))
    key = conductor.run_id
    env.conductor(key).submit("")                  # the second WORK: pending, its closing bare
    final = env.conductor(key).submit("")          # the frontier comes at the principal's call
    work_tail, final_tail = _closing(render(first)), _closing(render(final))
    if (work_tail == ["▶ CONTINUE"] and final_tail[0] == "▶ FINAL"
            and all("message" not in line and "./pp" not in line for line in final_tail[1:])):
        held("the principal's closings stand bare", f"CONTINUE alone; FINAL {final_tail[1:]} -- no sentence "
             "tells the agent what the standing orders already say")
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
    # the INFER stays pending until the principal's call: its closing is bare, the look-ahead
    # belongs to the frontier the proof gates
    if (before == ["▶ CONTINUE"] and proving.output == "proof"
            and tail[0] == "▶ FINAL" and any("proof given" in line for line in tail[1:])):
        held("the frontier after a proof says « proof given »", f"{before} then {tail[1:]}")
    else:
        failures.append(f"  ✗ proof given                  before={before} tail={tail}")


def output_default(bench, env) -> None:
    """A proc that declares no `output:` yields the untyped form."""
    held, failures = bench.held, bench.failures
    formless = env.write("FORMLESS.md", FORMLESS)
    conductor = env.conductor()
    first = render(conductor.start(formless))
    second = render(env.conductor(conductor.run_id).submit(""))
    lines = [line for text in (first, second) for line in text.splitlines()
             if line.startswith(("WORK ", "INFER ")) and "=>" in line]
    if lines and all(" any => " in line for line in lines):
        held("a form-less proc yields `any`", f"{lines}")
    else:
        failures.append(f"  ✗ the default                 {lines}")


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
            and any("INFER any => response  (SIDE)" == line for line in lines)):
        held("every instruction line names its document", f"{len(lines)} lines, e.g. {lines[:3]}")
    else:
        failures.append(f"  ✗ the lines                   {lines}")


def scenario(bench) -> int:
    env = bench.env("lines")
    env.write("procs/LAWFUL.md", LAWFUL)     # a law in force for the exchange: its section is a subject
    weld(bench, env)
    clock(bench, env)
    closing_notes(bench, env)
    output_default(bench, env)
    instruction_names(bench, env)
    return 0
