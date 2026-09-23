"""Scenario `resolution` -- the affinage of the measure (plan pp-split, batch
l-affinage-de-la-resolution) -- 2 case(s):
- report attributes the served volume BY PACKAGE from the repo (a served body has no
  provider line, yet NEXT belongs to steering, TURN/CAPABILITIES to kit) -- no more "?"
- a `derive --fusion none` pass renders ONE output per step, so the time is per STEP and
  the report says the regime (fusion=1)
"""
from __future__ import annotations

import json

from conductor.packaging import contributions


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("resows", ("steering", "monitoring"))
    made = env.made
    env.write("SETTINGS.md", env.read("SETTINGS.md")
              .replace("monitoring_capture: false", "monitoring_capture: true"))
    book = made.parent / "pb.md"
    book.write_text("composition: kit steering\n\n## S1\n\n| id | gesture | expected |\n"
                    "|---|---|---|\n| S1.01 | S1.01 hi | -- |\n| S1.02 | S1.02 bye | -- |\n",
                    encoding="utf-8")

    # --- derive under fusion none, run, report ----------------------------------------
    target = made.parent / "derived-none"
    contributions.run_skill(made, "pp-monitoring", ["derive", str(target), "--fusion", "none"])
    meta2 = target / made.name
    fusion_line = "instructions_fusion: none" in (meta2 / "SETTINGS.md").read_text(encoding="utf-8")
    contributions.run_skill(made, "pp-monitoring", ["setup", "res", str(meta2), str(book)])
    rc, out, err = contributions.run_skill(made, "pp-monitoring", ["run", "res"])
    rc2, rep, _ = contributions.run_skill(made, "pp-monitoring", ["report", "res"])

    if (fusion_line and rc == 0 and rc2 == 0
            and "package  steering" in rep and "package  kit" in rep
            and "package  ?" not in rep):
        held("the volume is attributed by package from the repo",
             "NEXT to steering, the kit's own to kit -- no provider line needed, no `?`")
    else:
        failures.append(f"  ✗ per package                {rep[-260:]!r}")

    if "fusion=1, time is per STEP" in rep:
        held("the fusion regime is said, and none gives per-step time",
             "derive --fusion none -> the report says fusion=1, time is per STEP")
    else:
        failures.append(f"  ✗ fusion regime              {[ln for ln in rep.splitlines() if 'fusion' in ln]!r}")
    return len(failures)
