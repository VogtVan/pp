"""Scenario `events-sectors` -- the sector a latch carries, and who may name one:
- a signal without `sector:` falls to the declared default, the engine's commons
- a named sector serves its declarant alone; a collision refuses every read

Migrated from the improvement package (batch les-signaux-et-les-compteurs). The
case that served a RUN latch to a block left with the run-latch question.
"""
from __future__ import annotations

from pathlib import Path
from conductor import Conductor, render, discovery, instance, persistence
from tests.harness import session_of
from conductor import events as events_module


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    # --- A3/L1 le-champ-sector: the latch learns its sector --------------------------
    sct_made = bench.env("sctw").made
    sct_engine = sct_made / ".sys" / "engine" / "pp.py"
    sct_member = discovery.instance_member(sct_engine)
    sct_root = sct_made / ".sys" / "vendor" / "probe@0.0.1"
    sct_root.mkdir(parents=True)
    (sct_root / "package.yaml").write_text(
        "name: probe\nversion: 0.0.1\ndescription: a motor fixture\nrequires: []\n"
        "contributes:\n"
        "  events:\n"
        "    sectors:\n"
        "      probe: {cap: 1, icon: 🧪}\n"
        "    vectors:\n"
        "      zone: {verify: pp-zone}\n"
        "    signals:\n"
        "      sectored: {door: PP-RULES, sector: probe}\n"
        "      bare: {door: PP-MEMBER}\n"
        "      astray: {door: PP-RULES, sector: elsewhere}\n", encoding="utf-8")
    zone = sct_root / "skills" / "pp-zone"            # the family's verifier: every slug is a node
    zone.mkdir(parents=True)
    (zone / "SKILL.md").write_text("---\nname: pp-zone\ndescription: the probe verifier\n---\n\npp-zone\n", encoding="utf-8")
    (zone / "pp-zone.py").write_text("#!/usr/bin/env python3\nimport sys\nsys.stdin.read()\nraise SystemExit(0)\n", encoding="utf-8")
    sct_pins = instance.read(sct_made)
    sct_pins["packages"]["probe"] = "0.0.1"
    instance.write(sct_made, sct_pins)
    (sct_made / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\nhistory_day: never\ninstructions_fusion: max\n---\n",
        encoding="utf-8")
    (sct_made / "MEMBER.md").write_text(
        (sct_made / "MEMBER.md").read_text(encoding="utf-8")
        .rstrip() + "\nshaped by hand\n", encoding="utf-8")

    sct_registry = events_module.sectors(sct_made)
    default_latch = events_module.push(sct_made, "probe", "bare", vector="zone:atelier")
    own_latch = events_module.push(sct_made, "probe", "sectored", vector="zone:forge")
    if (sct_registry.get("probe", {}).get("source") == "probe"
            and sct_registry["probe"].get("cap") == 1
            and default_latch is not None and default_latch["sector"] == "protocol"
            and own_latch is not None and own_latch["sector"] == "probe"):
        held("the latch learns its sector", "a signal without `sector:` falls to the "
             "DECLARED default -- the engine's `protocol` commons when no package declares one; one naming its provider's own sector carries it")
    else:
        failures.append(f"  ✗ sector field                {sct_registry} "
                        f"{default_latch}/{own_latch}")
    expect("sector-unowned", lambda: events_module.push(sct_made, "probe", "astray"))

    rival_root = sct_made / ".sys" / "vendor" / "rival@0.0.1"
    rival_root.mkdir(parents=True)
    (rival_root / "package.yaml").write_text(
        "name: rival\nversion: 0.0.1\ndescription: a colliding fixture\nrequires: []\n"
        "contributes:\n"
        "  events:\n"
        "    sectors:\n"
        "      probe: {cap: 2}\n"
        "    signals:\n"
        "      echo: {door: PP-RULES, sector: probe}\n", encoding="utf-8")
    sct_pins = instance.read(sct_made)
    sct_pins["packages"]["rival"] = "0.0.1"
    instance.write(sct_made, sct_pins)
    expect("sector-collision", lambda: events_module.sectors(sct_made))
    expect("sector-collision", lambda: events_module.push(
        sct_made, "probe", "bare", vector="zone:atelier"))
    expect("sector-collision", lambda: events_module.standing(sct_made, [dict(own_latch)]))
    (rival_root / "package.yaml").write_text(
        "name: rival\nversion: 0.0.1\ndescription: a colliding fixture\nrequires: []\n"
        "contributes:\n"
        "  events:\n"
        "    sectors:\n"
        "      rival: {}\n"
        "    signals:\n"
        "      echo: {door: PP-RULES, sector: probe}\n", encoding="utf-8")
    expect("sector-unowned", lambda: events_module.push(sct_made, "rival", "echo"))
    if events_module.standing(sct_made, [dict(own_latch)]):
        held("a named sector serves its declarant alone", "the collision refuses the "
             "registry read, push and standing alike; resolved, the foreign claim "
             "still refuses while the owner's latch stands")
    else:
        failures.append("  ✗ sector ownership            the owner's latch fell")
    return 0
