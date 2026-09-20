"""Scenario `flags` -- 2 case(s), in the monolith's order:
- flags cumulate without clobber: any order, the same surface
- la-carte-enseigne-la-vie-d-une-offre: play NAME while the step offers it
"""
from __future__ import annotations

import contextlib
import io
import tempfile
from pathlib import Path
from tests.harness import load_script, pin_step, PRODUCT_ENGINE, SOURCE, body_of, kept_document, reaches
from conductor import install as install_module


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    product_engine = PRODUCT_ENGINE
    # --- flags cumulate without clobber: any order, the same surface ------------------
    # (gemini sits out: its wire needs the binary and refuses upfront, proven elsewhere)
    cumul_adapters = install_module.product_root(product_engine) / "adapters"
    cumul_trees = []
    for order in (["claude", "codex", "cursor"], ["cursor", "codex", "claude"]):
        cumul_ws = Path(tempfile.mkdtemp()) / "cumul"
        with contextlib.redirect_stdout(io.StringIO()):
            cumul_made = install_module.install(product_engine, cumul_ws / ".pp", [])
            pin_step(cumul_made)
            for pname in order:
                load_script(cumul_adapters / pname / "wire.py").wire(cumul_ws, cumul_made)
        cumul_trees.append({str(p.relative_to(cumul_ws)): p.read_bytes()
                            for p in sorted(cumul_ws.rglob("*"))
                            if p.is_file() and ".pp" not in p.relative_to(cumul_ws).parts})
    if (cumul_trees[0] == cumul_trees[1]
            and ".agents/skills/pp/SKILL.md" in cumul_trees[0]
            and "GEMINI.md" in cumul_trees[0] and "claude-pp" in cumul_trees[0]
            and "pp" in cumul_trees[0]):
        held("flags cumulate without clobber",
             "claude+codex+cursor in either order -- byte-identical surface, one shared card")
    else:
        failures.append(f"  ✗ flag cumul                "
                        f"{sorted(set(cumul_trees[0]) ^ set(cumul_trees[1]))}")

    # --- la-carte-enseigne-la-vie-d-une-offre: play NAME while the step offers it ----
    wired_card = cumul_trees[0][".claude/skills/pp/SKILL.md"].decode("utf-8")
    if (reaches(wired_card, body_of(kept_document(SOURCE / "kit", "PP")))
            and "address-ambiguous" in wired_card):
        held("the card teaches the offer's lifetime",
             "an offer lives with its OUTPUT: numbered segments, pending-first "
             "resolution, the address on ambiguity, the routed door's note")
    else:
        failures.append("  ✗ card offer lifetime       the sentence is not taught")
    return 0
