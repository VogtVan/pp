"""Scenario `version` -- 1 case(s), in the monolith's order:
- le-kit-bump: the product has ONE version, recorded, told, compared
"""
from __future__ import annotations

from pathlib import Path
from conductor import Refusal, discovery, instance
from tests.harness import PRODUCT_ENGINE
from conductor import install as install_module


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    product_engine = PRODUCT_ENGINE
    # --- le-kit-bump: the product has ONE version, recorded, told, compared ----------
    from conductor import VERSION as ENGINE_VERSION                        # noqa: PLC0415
    ver_made = bench.env("verws").made
    ver_engine = ver_made / ".sys" / "engine" / "pp.py"
    ver_member = discovery.instance_member(ver_engine)
    pyproject = (install_module.product_root(product_engine) / "pyproject.toml").read_text(encoding="utf-8")
    if (instance.read(ver_made).get("engine") == ENGINE_VERSION
            and f'version = "{ENGINE_VERSION}"' in pyproject
            and install_module.source_version(install_module.product_root(product_engine))
            == ENGINE_VERSION):
        held("one version, one truth", "the constant, pyproject and the fresh instance's "
             "record all say the same thing")
    else:
        failures.append(f"  ✗ version record            {instance.read(ver_made).get('engine')!r}")

    # an engine drift alone is a move: upgrade says it and refreshes
    ver_leaf = ver_made / ".sys" / "engine" / "conductor" / "core" / "version.py"
    ver_leaf.write_text(ver_leaf.read_text(encoding="utf-8")
                        .replace(ENGINE_VERSION, "0.1.0-alpha.0"), encoding="utf-8")
    stale = instance.read(ver_made); stale["engine"] = "0.1.0-alpha.0"
    instance.write(ver_made, stale)
    up_engine_told = install_module.upgrade(ver_member)
    refreshed_leaf = ver_leaf.read_text(encoding="utf-8")
    if (any(one.startswith("engine 0.1.0-alpha.0 -> ") for one in up_engine_told)
            and ENGINE_VERSION in refreshed_leaf
            and instance.read(ver_made).get("engine") == ENGINE_VERSION):
        held("upgrade moves the engine too", "a drifted copy is a move like any pin -- "
             "told, refreshed, recorded")
    else:
        failures.append(f"  ✗ engine move               {up_engine_told!r}")

    # doctor keeps an outrun pin and says the gesture; the refusal guides too
    cur_kit = instance.pins(ver_made)["kit"]
    (ver_made / ".sys" / "vendor" / f"kit@{cur_kit}").rename(
        ver_made / ".sys" / "vendor" / "kit@0.0.9-past")
    outrun = instance.read(ver_made)
    outrun["packages"] = {**instance.pins(ver_made), "kit": "0.0.9-past"}
    instance.write(ver_made, outrun)
    doc_told = install_module.doctor(ver_member)
    try:
        install_module.sync(ver_member)
        guided = ""
    except Refusal as refusal:
        guided = str(refusal)
    if (any("kit@0.0.9-past kept as vendored" in one
            and "`upgrade` moves you there" in one for one in doc_told)
            and (ver_made / ".sys" / "vendor" / "kit@0.0.9-past").is_dir()
            and "`upgrade` follows it" in guided):
        held("doctor keeps what the source outran", "the repair stays useful -- the stale "
             "bundle stands, the way forward is named; the refusal guides the same way")
    else:
        failures.append(f"  ✗ doctor partial            {doc_told!r} / {guided!r}")
    return 0
