"""Scenario `law-codes` -- a law said by its code:
- codes mode: a law's text renders at its FIRST emission of the run and its code at every
  re-emission; no registry is served and none is written; after `-compacted` the texts return
- a law redone by its code keeps the SECTION of its first emission, across the processes a
  routed frame's life spans: (a) LAPS, a described door routed from the WORK, renders
  `production:` with LP1 alone and the inherited behavior codes under `behavior:` at every lap,
  its proof line asking `[LP1]` alone, its heading counting the lap's own steps; (b) ROUTE ->
  STAGE -> LEFT: the successor's block shows no `production:` section
"""
from __future__ import annotations

import json
import re

from conductor import render
from tests.harness import cli

LAWFUL = """---
name: LAWFUL
kind: doc
description: a law in force for the whole exchange, mounted at the boot's socket
mount: boot.ready
constraints.behavior: |
  W4  the witness law says its text once, its code after.
---
"""
LATE = """---
name: LATE
kind: proc
description: a document the turn's end calls -- its law is new in its frame
attach: turn.end
output: any
constraints.behavior: |
  Y1  the late law is new in its frame.
proc: |
  INFER
---
late
"""
LEAN = ("---\nname: SETTINGS\nkind: doc\nverbatim_constraints: false\n"
        "max_harness_tool_output: 60000\n---\n")      # codes mode, a wide budget: never the default's cut

KEY = re.compile(r"run ([0-9a-f]{6})")
FUSED = "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: max\nmax_harness_tool_output: 200000\n---\n"   # every yield fused, one output
OVERLAY = "---\nname: TURN\ntools: |\n  +LAPS\n  +ROUTE\nconstraints.behavior: |\n  B1  act only within your own member.\n---\n"
LAPS = ("---\nname: LAPS\nkind: proc\ndescription: the described door\noutput: any\n"
        "field: |\n  The three names alpha, beta, gamma -- one lap each, in that order.\n"
        "constraints.production: |\n  LP1  the lap's line names its element and nothing else.\n"
        "proc: |\n  INFER\n---\n\nOne lap per element under `field`: say ONE line.\n")
ROUTE = "---\nname: ROUTE\nkind: proc\ndescription: the root\noutput: any\nproc: |\n  CALL STAGE.md\n---\n\nThe root.\n"
STAGE = ("---\nname: STAGE\nkind: proc\ndescription: the stage\noutput: any\nnext: LEFT.md RIGHT.md\n"
         "choose: |\n  LEFT when odd, RIGHT when even.\nproc: |\n  INFER\n---\n\nSay ONE line.\n")
LEFT = "---\nname: LEFT\nkind: proc\ndescription: the odd successor\noutput: any\nproc: |\n  INFER\n---\n\nSay LEFT.\n"
RIGHT = "---\nname: RIGHT\nkind: proc\ndescription: the even successor\noutput: any\nproc: |\n  INFER\n---\n\nSay RIGHT.\n"
PROOF = re.compile(r"^INFER proof \[([^\]]*)\]", re.M)     # the codes the proof line asks for
HEAD = re.compile(r"▸ LAPS\{([0-9-]+)/(\d+)\}")              # a lap's heading: its steps' range


def _section(text: str, title: str) -> list[str]:
    """-> the lines of the LAST `▌ <title>` section of `text`."""
    lines = text.splitlines()
    starts = [i for i, one in enumerate(lines) if one == f"▌ {title}"]
    if not starts:
        return []
    out = []
    for one in lines[starts[-1] + 1:]:
        if one.startswith(("▌ ", "▶ ")):
            break
        out.append(one)
    return out


def _opened(env) -> str:
    """-> the key of a run opened at the console."""
    opened = cli(env.engine, "-new", "go", cwd=env.root)
    return KEY.search(opened.stdout).group(1) if KEY.search(opened.stdout) else ""


def codes_mode(bench) -> None:
    """Under codes mode a law's text renders once per run, its code after; the ledger goes
    with the context."""
    held, failures = bench.held, bench.failures
    env = bench.env("lean")
    env.write("SETTINGS.md", LEAN)
    env.write("procs/LAWFUL.md", LAWFUL)
    env.write("procs/LATE.md", LATE)

    lean_rendered = render(env.conductor().resume(env.conductor().boot("BOOT.md")))
    w4_line = "W4  the witness law says its text once, its code after."
    w4_text = w4_line[len("W4  "):]
    second = render(env.conductor().submit(""))   # the next output: W4 re-emits, LATE's law is new
    written = any((env.made / ".sys" / name).is_file()
                  for name in ("constraints.md", "_constraints.md"))
    if ("INFORMATION — constraints" not in lean_rendered
            and w4_text in lean_rendered and not written
            and "\n" + w4_line not in second and "W4" in second
            and "Y1  the late law is new" in second):
        held("the first emission is verbatim, the re-emission its code",
             "no registry served, no file written; W4's text once at the boot, its code "
             "in the next output while the new frame's law says its text")
    else:
        failures.append(f"  ✗ first emission              {w4_text in lean_rendered} "
                        f"{written} {('W4' in second, w4_line in second)!r}")

    compacted = render(env.conductor().compacted())
    if w4_text in compacted and "INFORMATION — constraints" not in compacted:
        held("the ledger goes with the context",
             "after -compacted every law says its text again -- and still no registry")
    else:
        failures.append(f"  ✗ compacted texts             {w4_text in compacted}")
    env.conductor().forget()


def keep_section(bench) -> None:
    """A law redone by its code keeps the section of its first emission; a lap's heading
    counts the lap's own steps."""
    held, failures = bench.held, bench.failures
    env = bench.env("sections")
    env.write("SETTINGS.md", FUSED)
    env.write("procs/TURN.md", OVERLAY)
    for doc, text in (("LAPS", LAPS), ("ROUTE", ROUTE), ("STAGE", STAGE), ("LEFT", LEFT), ("RIGHT", RIGHT)):
        env.write(f"procs/{doc}.md", text)

    # --- (a) the laps keep their sections, each headed by its own steps ---------------------------
    key = _opened(env)
    cli(env.engine, key, "-s", "LAPS", cwd=env.root)
    lap1 = cli(env.engine, key, "-", cwd=env.root, stdin='["alpha", "beta", "gamma"]')
    proof = json.dumps([{"code": "LP1", "evidence": "alpha", "verdict": "ok"}])
    lap2 = cli(env.engine, key, "-", cwd=env.root, stdin=proof)
    lap3 = cli(env.engine, key, "-", cwd=env.root, stdin=proof)
    laps = [lap1.stdout, lap2.stdout, lap3.stdout]
    good = []
    for text in laps:
        constraints = "\n".join(_section(text, "CONSTRAINTS"))
        under = constraints.split("behavior:")[0] if "behavior:" in constraints else constraints
        good.append(constraints.startswith("production:") and "LP1" in under and "B1" not in under
                    and "behavior:" in constraints and "B1" in constraints.split("behavior:")[-1]
                    and PROOF.findall(text) == ["LP1"])
    if all(good) and all(one.returncode == 0 for one in (lap1, lap2, lap3)):
        held("(a) the laps keep their sections", "three laps: `production: [LP1]`, the inherited codes under "
             "`behavior:`, the proof line asks `[LP1]` alone")
    else:
        failures.append(f"  ✗ (a) the laps                good={good} "
                        f"{_section(laps[0], 'CONSTRAINTS')!r} proof={[PROOF.findall(t) for t in laps]}")

    heads = [HEAD.findall(text) for text in laps]
    if all(found and found[-1] == ("1-2", "2") for found in heads):
        held("the lap counter is stable", f"three laps headed {[found[-1] for found in heads]}")
    else:
        failures.append(f"  ✗ the counter                 {heads}")

    # --- (b) the successor has no production section ---------------------------------------------
    key = _opened(env)
    staged = cli(env.engine, key, "-s", "ROUTE", cwd=env.root)
    if "PICK next" not in staged.stdout:
        cli(env.engine, key, cwd=env.root)        # STAGE's line said: the bare call closes it, the PICK comes
    left = cli(env.engine, key, "LEFT.md", cwd=env.root)
    constraints = _section(left.stdout, "CONSTRAINTS")
    if left.returncode == 0 and "▸ LEFT" in left.stdout and "production:" not in constraints and "behavior:" in constraints:
        held("(b) the successor shows no production section", f"LEFT's block: {constraints}")
    else:
        failures.append(f"  ✗ (b) the successor           rc={left.returncode} {constraints!r} "
                        f"{left.stdout[-200:]!r}")


def scenario(bench) -> int:
    codes_mode(bench)
    keep_section(bench)
    return 0
