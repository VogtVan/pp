"""Scenario `compile-arrival` -- 2 case(s) (batch les-ecrivains-partages, 2026-09-30):
- the receipts' lock held by another process: a compile of the catalog waits for it
- eight compiles at once: the receipts keep every artifact and parse, each reading is the
  one a single compile renders
"""
from __future__ import annotations

import subprocess
import sys

from conductor.packaging import compiling
from tests.harness import PRODUCT_ENGINE, holding, race

BUILD = """import sys
sys.path.insert(0, sys.argv[1])
from pathlib import Path
from conductor.packaging import compiling
meta = Path(sys.argv[2])
compiling.build_tools(meta)
compiling.build_system(meta)
print("built")
"""


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("arrival")
    made = env.made
    receipts = made / ".sys" / "receipts.yaml"
    build = bench.temp() / "build.py"
    build.write_text(BUILD, encoding="utf-8")
    root = str(PRODUCT_ENGINE.parent)

    # --- the receipts' lock held: a compile waits --------------------------------------------------
    with holding(receipts.with_name(receipts.name + ".lock")):
        proc = subprocess.Popen([sys.executable, str(build), root, str(made)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            proc.wait(timeout=2.0)
            early = True
        except subprocess.TimeoutExpired:
            early = False
    out, err = proc.communicate(timeout=30)
    if early:
        failures.append(f"a compile wrote its receipt while the receipts' lock was held (rc {proc.returncode})")
    elif proc.returncode or "built" not in out:
        failures.append(f"the compile after the release failed: rc {proc.returncode} -- {err.strip()[:160]}")
    else:
        held("a compile waits for the receipts' lock", "held 2s · then built")

    # --- eight compiles at once -----------------------------------------------------------------------
    results = race(build, [[root, str(made)] for _ in range(8)])
    import yaml
    kept = yaml.safe_load(receipts.read_text(encoding="utf-8")) or {}
    whole = [(made / ".sys" / name).read_text(encoding="utf-8") == render(made)
             for name, render in ((compiling.TOOLS, compiling.render_tools),
                                  (compiling.OUTPUT, compiling.render_formats))]
    if any(one.returncode for one in results):
        failures.append("a compile among eight failed: " + " | ".join(one.stderr.strip()[:80] for one in results if one.returncode))
    elif not {*compiling.CATALOGS, "system.md"} <= set(kept) or not all(whole):
        failures.append(f"eight compiles at once: receipts {sorted(kept)}, readings whole {whole}")
    else:
        held("eight compiles at once: every receipt kept, both readings whole", f"receipts {sorted(kept)}")
    return len(failures)
