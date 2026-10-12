"""Scenario `codes-mode` -- 2 case(s):
- le-registre-aux-codes: under codes mode a law's text renders at its FIRST emission of
  the run and its code at every re-emission; no registry is served and none is written
- the ledger goes with the context: after `-compacted` the texts return
The laws are the witness's own, written at run time: one mounted at the boot's socket
for the whole exchange, one on a document the turn's end CALLs -- a new frame.
"""
from __future__ import annotations

from conductor import Conductor, render, discovery

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


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    lean_made = bench.env("lean").made
    lean_member = discovery.instance_member(lean_made / ".sys" / "engine" / "pp.py")
    (lean_made / "SETTINGS.md").write_text(   # the bench rule survives the rewrite:
        "---\nname: SETTINGS\nkind: doc\nverbatim_constraints: false\n"   # a wide budget,
        "max_harness_tool_output: 60000\n---\n", encoding="utf-8")   # never the default's cut
    (lean_made / "procs" / "LAWFUL.md").write_text(LAWFUL, encoding="utf-8")
    (lean_made / "procs" / "LATE.md").write_text(LATE, encoding="utf-8")
    def lean_c() -> Conductor:
        return Conductor(lean_member, lean_made / ".sys" / "engine" / "pp.py")

    # --- the first emission is verbatim; no registry served, none written -------------
    lean_rendered = render(lean_c().resume(lean_c().boot("BOOT.md")))
    w4_line = "W4  the witness law says its text once, its code after."
    w4_text = w4_line[len("W4  "):]
    second = render(lean_c().submit(""))   # the next output: W4 re-emits, LATE's law is new
    written = any((lean_made / ".sys" / name).is_file()
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

    # --- the ledger goes with the context: -compacted brings the texts back -----------
    compacted = render(lean_c().compacted())
    if w4_text in compacted and "INFORMATION — constraints" not in compacted:
        held("the ledger goes with the context",
             "after -compacted every law says its text again -- and still no registry")
    else:
        failures.append(f"  ✗ compacted texts             {w4_text in compacted}")
    lean_c().forget()
    return 0
