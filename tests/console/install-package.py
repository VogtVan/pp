"""Scenario `install-package` -- 1 case(s), in the monolith's order:
- `install -package <name>` extends an EXISTING instance, no recreation
"""
from __future__ import annotations

import contextlib
import io
import tempfile
from pathlib import Path
from conductor import discovery, instance
from tests.harness import pin_step, PRODUCT_ENGINE
import pp as pp_cli


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    # --- `install -package <name>` extends an EXISTING instance, no recreation ---------
    from conductor import install as install_module                       # noqa: PLC0415
    product_engine = PRODUCT_ENGINE
    depot = Path(tempfile.mkdtemp())
    solo = install_module.install(product_engine, depot / "solo" / ".pp", [])
    pin_step(solo)
    solo_member = discovery.instance_member(solo / ".sys" / "engine" / "pp.py")
    added = install_module.add_package(solo_member, "daneel")
    pinned = instance.pins(solo)
    if (pinned.get("daneel") and added.is_dir()
            and added.name == f"daneel@{pinned['daneel']}"):
        held("install -package adds to an existing instance",
             "pinned, vendored, catalog recompiled -- no recreation")
    else:
        failures.append(f"  ✗ add_package                {pinned} {added}")
    expect("package-installed", lambda: install_module.add_package(solo_member, "daneel"))
    expect("package-unknown", lambda: install_module.add_package(solo_member, "nope"))

    err = io.StringIO()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
        ambiguous_rc = pp_cli.main(["-install", str(depot / "solo"), "-package", "daneel"])
    if ambiguous_rc == 2 and "install-ambiguous" in err.getvalue():
        held("install -package is exclusive", "a workspace or another flag alongside it refuses")
    else:
        failures.append(f"  ✗ install-ambiguous          rc={ambiguous_rc} {err.getvalue()!r}")
    return 0
