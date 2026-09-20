"""Scenario `codes-mode` -- 2 case(s):
- le-registre-aux-codes: under codes mode a law's text renders at its FIRST emission of
  the run and its code at every re-emission; no registry is served and none is written
- the ledger goes with the context: after `-compacted` the texts return
"""
from __future__ import annotations

from pathlib import Path
from conductor import Conductor, render, discovery
from tests.harness import SOURCE, kept_document


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    lean_made = bench.env("lean").made
    lean_member = discovery.instance_member(lean_made / ".sys" / "engine" / "pp.py")
    (lean_made / "SETTINGS.md").write_text(   # the bench rule survives the rewrite:
        "---\nname: SETTINGS\nkind: doc\nverbatim_constraints: false\n"   # a wide budget,
        "max_harness_tool_output: 60000\n---\n", encoding="utf-8")   # never the default's cut
    def lean_c() -> Conductor:
        return Conductor(lean_member, discovery.siblings_around(lean_member),
                         lean_made / ".sys" / "engine" / "pp.py")

    # --- the first emission is verbatim; no registry served, none written -------------
    lean_rendered = render(lean_c().resume(lean_c().boot("BOOT.md")))
    b4_line = next(one.strip() for one in kept_document(SOURCE / "kit", "BOOT")
                   .read_text(encoding="utf-8").splitlines() if one.strip().startswith("B4  "))
    b4_text = b4_line[len("B4  "):]        # the law as the document says it, read at run time
    second = render(lean_c().submit(""))   # the next output: B-laws re-emit, T-laws are new
    written = any((lean_made / ".sys" / name).is_file()
                  for name in ("constraints.md", "_constraints.md"))
    if ("INFORMATION — constraints" not in lean_rendered
            and b4_text in lean_rendered and not written
            and "\n" + b4_line not in second and "B4" in second
            and "T1  an approval names" in second):
        held("the first emission is verbatim, the re-emission its code",
             "no registry served, no file written; B4's text once at the boot, its code "
             "in the next output while the new frame's laws say their text")
    else:
        failures.append(f"  ✗ first emission              {b4_text in lean_rendered} "
                        f"{written} {('B4' in second, b4_line in second)!r}")

    # --- the ledger goes with the context: -compacted brings the texts back -----------
    compacted = render(lean_c().compacted())
    if b4_text in compacted and "INFORMATION — constraints" not in compacted:
        held("the ledger goes with the context",
             "after -compacted every law says its text again -- and still no registry")
    else:
        failures.append(f"  ✗ compacted texts             {b4_text in compacted}")
    lean_c().forget()
    return 0
