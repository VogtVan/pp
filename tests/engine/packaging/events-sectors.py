"""Scenario `events-sectors` -- the sector a latch carries, who may name one, and how the bus
arbitrates between sectors:
- the sector: a signal without `sector:` falls to the declared default, the engine's commons; a
  named sector serves its declarant alone; a collision refuses every read
- the arbitration: it ranks by declared priority, then by count, then by latch order; each sector
  serves under its own cap, the default sector leading
"""
from __future__ import annotations

from conductor import instance
from conductor import events as events_module


def _probe(bench, name: str, sectors: str, signals: str, settings: str = "") -> object:
    """-> the instance of a fresh environment carrying the `probe` package: its `sectors` and
    `signals` (YAML lines), the `zone` family checked by the `pp-zone` verifier."""
    made = bench.env(name).made
    root = made / ".sys" / "vendor" / "probe@0.0.1"
    root.mkdir(parents=True)
    (root / "package.yaml").write_text(
        "name: probe\nversion: 0.0.1\ndescription: a motor fixture\nrequires: []\n"
        "contributes:\n"
        "  events:\n"
        "    sectors:\n" + sectors +
        "    vectors:\n"
        "      zone: {verify: pp-zone}\n"
        "    signals:\n" + signals, encoding="utf-8")
    zone = root / "skills" / "pp-zone"            # the family's verifier: every slug is a node
    zone.mkdir(parents=True)
    (zone / "SKILL.md").write_text("---\nname: pp-zone\ndescription: the probe verifier\n---\n\npp-zone\n", encoding="utf-8")
    (zone / "pp-zone.py").write_text("#!/usr/bin/env python3\nimport sys\nsys.stdin.read()\nraise SystemExit(0)\n", encoding="utf-8")
    pins = instance.read(made)
    pins["packages"]["probe"] = "0.0.1"
    instance.write(made, pins)
    (made / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\nhistory_day: never\ninstructions_fusion: max\n"
        + settings + "---\n", encoding="utf-8")
    return made


def sectors(bench) -> None:
    """The latch learns its sector; a named sector serves its declarant alone."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    sct_made = _probe(bench, "sctw",
                      "      probe: {cap: 1, icon: 🧪}\n",
                      "      sectored: {door: PP-RULES, sector: probe}\n"
                      "      bare: {door: PP-MEMBER}\n"
                      "      astray: {door: PP-RULES, sector: elsewhere}\n")

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


def arbitration(bench) -> None:
    """The bus ranks the latches and serves each sector under its own cap."""
    held, failures = bench.held, bench.failures
    arb_made = _probe(bench, "arbw",
                      "      probe: {cap: 1}\n"
                      "      wide: {}\n",
                      "      arbone: {door: PP-RULES, priority: 1}\n"
                      "      arbtwo: {door: PP-RULES, priority: 2}\n"
                      "      gamma: {door: PP-RULES}\n"
                      "      delta: {door: PP-RULES}\n"
                      "      inhouse: {door: PP-RULES, sector: probe, priority: 1}\n"
                      "      inhouse2: {door: PP-MEMBER, sector: probe, priority: 2}\n"
                      "      broad: {door: PP-RULES, sector: wide}\n")

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
        held("each sector under its own cap", "0 mutes the default sector alone; a "
             "declared cap holds its sector; an unsaid one serves 2; the default sector leads "
             "the order")
    else:
        failures.append(f"  ✗ sector caps                 {[one['signal'] for one in arb_muted]} "
                        f"{[one['signal'] for one in arb_capped]} {len(arb_wide)} "
                        f"{[one['signal'] for one in arb_order]}")


def scenario(bench) -> int:
    sectors(bench)
    arbitration(bench)
    return 0
