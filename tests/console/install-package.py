"""Scenario `install-package` -- 1 case(s), in the monolith's order:
- `install -package <name>` extends an EXISTING instance, no recreation
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from conductor import discovery, instance
from tests.harness import cli, pin_step


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    # --- `install -package <name>` extends an EXISTING instance, no recreation ---------
    from conductor import install as install_module                       # noqa: PLC0415
    product_engine = bench.engine()
    depot = Path(tempfile.mkdtemp())
    solo = install_module.install(product_engine, depot / "solo" / ".pp", [])
    pin_step(solo)
    solo_member = discovery.instance_member(solo / ".sys" / "engine" / "pp.py")
    added = install_module.add_package(solo_member, "wit")
    pinned = instance.pins(solo)
    if (pinned.get("wit") and added.is_dir()
            and added.name == f"wit@{pinned['wit']}"):
        held("install -package adds to an existing instance",
             "pinned, vendored, catalog recompiled -- no recreation")
    else:
        failures.append(f"  ✗ add_package                {pinned} {added}")
    expect("package-installed", lambda: install_module.add_package(solo_member, "wit"))
    expect("package-unknown", lambda: install_module.add_package(solo_member, "nope"))

    ambiguous = cli(product_engine, "-install", str(depot / "solo"), "-package", "wit")
    ambiguous_rc = ambiguous.returncode
    if ambiguous_rc == 2 and "install-ambiguous" in ambiguous.stderr:
        held("install -package is exclusive", "a workspace or another flag alongside it refuses")
    else:
        failures.append(f"  ✗ install-ambiguous          rc={ambiguous_rc} {ambiguous.stderr!r}")
    return 0
