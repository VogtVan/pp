"""Scenario `events-arbitration` -- 2 case(s):
- the arbitration ranks by declared priority, then by count, then by latch order
- each sector serves under its own cap, the default sector leading

Migrated from the improvement package (batch les-signaux-et-les-compteurs): the
arbitration is the BUS's, and no policy owns it. The two cases that served a RUN
latch to a block left with the run-latch question (events-motors).
"""
from __future__ import annotations

from pathlib import Path
from conductor import Conductor, render, discovery, instance, persistence
from tests.harness import session_of
from conductor import events as events_module


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    # --- A3/L2 l-arbitrage: the service renders the arbitrated exact ------------------
    arb_made = bench.env("arbw").made
    arb_engine = arb_made / ".sys" / "engine" / "pp.py"
    arb_member = discovery.instance_member(arb_engine)
    arb_root = arb_made / ".sys" / "vendor" / "probe@0.0.1"
    arb_root.mkdir(parents=True)
    (arb_root / "package.yaml").write_text(
        "name: probe\nversion: 0.0.1\ndescription: a motor fixture\nrequires: []\n"
        "contributes:\n"
        "  events:\n"
        "    sectors:\n"
        "      probe: {cap: 1}\n"
        "      wide: {}\n"
        "    vectors:\n"
        "      zone: {verify: pp-zone}\n"
        "    signals:\n"
        "      arbone: {door: PP-RULES, priority: 1}\n"
        "      arbtwo: {door: PP-RULES, priority: 2}\n"
        "      gamma: {door: PP-RULES}\n"
        "      delta: {door: PP-RULES}\n"
        "      inhouse: {door: PP-RULES, sector: probe, priority: 1}\n"
        "      inhouse2: {door: PP-MEMBER, sector: probe, priority: 2}\n"
        "      broad: {door: PP-RULES, sector: wide}\n", encoding="utf-8")
    zone = arb_root / "skills" / "pp-zone"            # the family's verifier: every slug is a node
    zone.mkdir(parents=True)
    (zone / "SKILL.md").write_text("---\nname: pp-zone\ndescription: the probe verifier\n---\n\npp-zone\n", encoding="utf-8")
    (zone / "pp-zone.py").write_text("#!/usr/bin/env python3\nimport sys\nsys.stdin.read()\nraise SystemExit(0)\n", encoding="utf-8")
    arb_pins = instance.read(arb_made)
    arb_pins["packages"]["probe"] = "0.0.1"
    instance.write(arb_made, arb_pins)
    (arb_made / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\nhistory_day: never\ninstructions_fusion: max\n"
        "workspace_improvement_next_max: 1\n---\n", encoding="utf-8")
    (arb_made / "MEMBER.md").write_text(
        (arb_made / "MEMBER.md").read_text(encoding="utf-8")
        .rstrip() + "\nshaped by hand\n", encoding="utf-8")

    l_one = events_module.push(arb_made, "probe", "arbone", vector="zone:a")
    l_two = events_module.push(arb_made, "probe", "arbtwo", vector="zone:b")
    l_gamma = events_module.push(arb_made, "probe", "gamma", vector="zone:c")
    l_delta = events_module.push(arb_made, "probe", "delta", vector="zone:d")
    l_in = events_module.push(arb_made, "probe", "inhouse", vector="zone:e")
    l_in2 = events_module.push(arb_made, "probe", "inhouse2", vector="zone:f")
    l_broad = events_module.push(arb_made, "probe", "broad", vector="zone:g")

    full = events_module.emitted(arb_made, [l_gamma, l_two, l_one], setting_cap=2)
    risen = events_module.emitted(arb_made, [l_gamma, l_two], setting_cap=2)
    tied = events_module.emitted(arb_made, [l_delta, {**l_gamma, "n": 3}], setting_cap=2)
    if ([one["signal"] for one in full] == ["arbone", "arbtwo"]
            and [one["signal"] for one in risen] == ["arbtwo", "gamma"]
            and [one["signal"] for one in tied] == ["gamma", "delta"]):
        held("the arbitration ranks and caps", "priority first, the count breaks the "
             "tie, the overflow waits and rises as a place frees")
    else:
        failures.append(f"  ✗ arbitration order           {[one['signal'] for one in full]} "
                        f"{[one['signal'] for one in risen]} "
                        f"{[one['signal'] for one in tied]}")

    arb_muted = events_module.emitted(arb_made, [l_one, l_in], setting_cap=0)
    arb_capped = events_module.emitted(arb_made, [l_in2, l_in], setting_cap=2)
    arb_wide = events_module.emitted(arb_made, [l_broad, {**l_broad, "vector": "zone:h"}],
                                      setting_cap=0)
    arb_order = events_module.emitted(arb_made, [l_in, l_one], setting_cap=2)
    if ([one["signal"] for one in arb_muted] == ["inhouse"]
            and [one["signal"] for one in arb_capped] == ["inhouse"]
            and len(arb_wide) == 2
            and [one["signal"] for one in arb_order] == ["arbone", "inhouse"]):
        held("each sector under its own cap", "0 mutes improvement alone; a declared "
             "cap holds its sector; an unsaid one serves 2; improvement leads the order")
    else:
        failures.append(f"  ✗ sector caps                 {[one['signal'] for one in arb_muted]} "
                        f"{[one['signal'] for one in arb_capped]} {len(arb_wide)} "
                        f"{[one['signal'] for one in arb_order]}")

    return 0
