"""Scenario `seed` -- the pattern `packaging/seed`, played from its demonstration:
- a package's `seed/` lands under the instance's records at the install, byte for byte
- the records are the instance's: once edited, an `add` of another package, a sync and an upgrade at
  constant pins leave them byte for byte, and a `remove` of their package leaves them standing
- a package without `seed/` writes no record
- `seed` is a folder, never a contribution: `contributes: resources` refuses
  `contribution-kind-unknown`, nothing written
"""
from __future__ import annotations

from conductor import install, instance
from tests.harness import PATTERNS, support

DRAWER, PATTERN = "packaging", "seed"
HOME = PATTERNS / DRAWER / PATTERN
OWED = {"manifests": ["declared.yaml", "ledger.yaml", "plain.yaml"],
        "seeds": ["ledger"]}
packaging = support(__file__, "source")


def _laid() -> dict:
    return {folder: sorted(path.name for path in (HOME / folder).glob("*")) for folder in OWED}


def _records(made) -> dict[str, bytes]:
    home = made / instance.RECORDS
    return {path.name: path.read_bytes() for path in sorted(home.iterdir())} if home.is_dir() else {}


def seeded(bench, root) -> None:
    """Placed once at the install, then the instance's own."""
    held, failures = bench.held, bench.failures
    seeds = {path.name: path.read_bytes() for path in sorted((HOME / "seeds" / "ledger").iterdir())}
    made, member = packaging.installed(bench, root, "kept", ["ledger"])
    if _records(made) == seeds:
        held("the seed lands at the install", f"{', '.join(seeds)} under the records, byte for byte")
    else:
        failures.append(f"  ✗ seeded                       {sorted(_records(made))} -- owed {sorted(seeds)}")
        return
    first = next(iter(seeds))
    record = made / instance.RECORDS / first
    record.write_bytes(record.read_bytes() + b'{"entry": "the instance\'s own"}\n')
    edited = _records(made)
    install.add_package(member, "plain")
    after_add = _records(made)
    install.sync(member)
    after_sync = _records(made)
    told = install.upgrade(member)
    after_upgrade = _records(made)
    if after_add == edited and after_sync == edited and told == [] and after_upgrade == edited:
        held("the records are the instance's", "edited, they stay byte for byte through an add of "
             "another package, a sync and an upgrade at constant pins")
    else:
        failures.append(f"  ✗ records kept                 add={after_add == edited} sync={after_sync == edited} "
                        f"upgrade={told} {after_upgrade == edited}")
    told = install.remove_package(member, "ledger")
    vendor = {path.name for path in (made / instance.VENDOR).iterdir()}
    if ("ledger" not in instance.pins(made) and "ledger@0.0.1" not in vendor
            and any("removed" in line for line in told) and _records(made) == edited):
        held("remove leaves the records", "ledger unpinned, its bundle gone, the removal said; its "
             "record standing as the instance left it")
    else:
        failures.append(f"  ✗ remove                       {instance.pins(made)} {sorted(_records(made))}")


def unseeded(bench, root) -> None:
    """No `seed/`, no record; a seed declared as a contribution refuses."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    made, _ = packaging.installed(bench, root, "plain", ["plain"])
    if _records(made) == {}:
        held("no seed, no record", "plain installed: nothing under the records")
    else:
        failures.append(f"  ✗ plain                        {sorted(_records(made))}")
    target = bench.temp() / "declared" / ".pp"
    expect("contribution-kind-unknown",
           lambda: install.install(root / "engine" / "pp.py", target, ["declared"]))
    if not target.exists():
        held("a declared seed writes nothing", "`contributes: resources` refused before the "
             "instance's directory exists")
    else:
        failures.append(f"  ✗ declared wrote               {sorted(p.name for p in target.iterdir())}")


def scenario(bench) -> int:
    failures = bench.failures
    laid = _laid()
    if laid != OWED:
        failures.append(f"  ✗ the demonstration           {laid!r} -- owed {OWED!r}")
        return 0
    root = packaging.source(bench, {name: packaging.parts(PATTERN, name)
                                    for name in ("declared", "ledger", "plain")})
    seeded(bench, root)
    unseeded(bench, root)
    return 0
