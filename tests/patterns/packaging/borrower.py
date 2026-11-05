"""Scenario `borrower` -- the pattern `packaging/borrower`, played from its demonstration on one house:
- an instance born under the house by `-install` borrows its machine: no engine, no vendor, a manifest
  that declares no machine, found among the house's borrowers
- an instance that carried its own machine, its proc `KEPT` among its own files, is imported under the
  house: it borrows the house's machine, keeps its proc in its catalog and its birth date, and is found
  among the borrowers too
"""
from __future__ import annotations

from conductor import install, instance
from tests.harness import INSTANCE, demonstrated, demos

DRAWER, PATTERN = "packaging", "borrower"
DEMOS = ("KEPT.md",)


def _borrowing(meta, house) -> bool:
    """-> whether `meta` plays `house`'s machine and declares none of its own."""
    declared = instance.read(meta)
    return (not (meta / ".sys" / "engine").exists() and not (meta / ".sys" / "vendor").exists()
            and "source" not in declared and "packages" not in declared and instance.machine_of(meta) == house)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    if tuple(demonstrated(DRAWER, PATTERN)) != DEMOS:
        failures.append(f"  ✗ the demonstration           {demonstrated(DRAWER, PATTERN)!r} -- owed {DEMOS!r}")
        return 0
    env = bench.env("borrower")
    house = env.made

    # --- born under the house ----------------------------------------------------------------------
    born = install.install(env.engine, env.root / "agents" / "born" / INSTANCE, [], slug="born",
                           doors=False, borrow=True)
    if _borrowing(born, house) and born in instance.borrowers(house):
        held("an instance born under the house borrows its machine", "no engine, no vendor, no declared "
             "machine; listed among the house's borrowers")
    else:
        failures.append(f"  ✗ born                        {instance.read(born)} borrowers={instance.borrowers(house)}")

    # --- imported from its own machine -------------------------------------------------------------
    own = install.install(bench.engine(), bench.temp() / "own" / INSTANCE, [])
    (own / "procs" / "KEPT.md").write_text((demos(DRAWER, PATTERN) / "KEPT.md").read_text(encoding="utf-8"),
                                           encoding="utf-8")
    first = instance.read(own).get("installed")
    kept = env.root / "agents" / "kept" / INSTANCE
    install.imported(own, kept, "kept")
    found = instance.resolve(kept, "KEPT.md")
    if (_borrowing(kept, house) and kept in instance.borrowers(house) and found == kept / "procs" / "KEPT.md"
            and instance.read(kept).get("installed") == first and not own.exists()):
        held("an imported instance borrows the house's machine", f"its machine taken out, KEPT in its catalog, "
             f"born {first} as before; listed among the borrowers")
    else:
        failures.append(f"  ✗ imported                    {instance.read(kept)} KEPT={found} "
                        f"borrowers={instance.borrowers(house)} left={own.exists()}")
    return 0
