"""Scenario `upgrade-under-locks` -- 3 case(s) (batch le-verrou-de-reveil, 2026-09-30; rewritten by
le-verrou-de-la-machine, 2026-10-03):
- a pp process alive under the machine (the bench holds the machine's lock shared): `upgrade`
  with a move refuses `maintenance-busy`, the pins and the slot intact, the lock free after
- none alive: the same `upgrade` moves the pin, renews the run -- its slot a renewal mark, the
  files of its run gone (its call lock, its wake lock) --, sweeps the files of a run gone, and
  leaves the lock free
- a call lock and a wake lock held OUTSIDE any pp process do not hold the upgrade: it takes no
  run lock -- the pin moves, the run is renewed
"""
from __future__ import annotations

import re

from conductor import instance, persistence
from tests.harness import INSTANCE, bench_key, cli, holding
from conductor import install
from conductor.state import lock


def launcher(meta, key: str):
    """-> the launcher's file of the run `key` -- the `agent` package's published contract,
    `session-<key>.wake.lock` beside the slot; the engine names none."""
    return persistence.slot_of(meta, key).with_name(f"session-{key}.wake.lock")


def _bumped(manifest) -> str:
    """The kit's version at the source copy, raised by one on its last number -> the new version."""
    text = manifest.read_text(encoding="utf-8")
    found = re.search(r"^version: (\S+)$", text, re.M)
    assert found, text[:200]
    head, last = found.group(1).rsplit(".", 1)
    new = f"{head}.{int(last) + 1}"
    manifest.write_text(text.replace(f"version: {found.group(1)}", f"version: {new}", 1), encoding="utf-8")
    return new


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    engine = bench.source_with("kit-witness")          # a copy of the product: its versions may move
    source = engine.parent.parent
    ws = bench.temp() / "ws"
    made = install.install(engine, ws / INSTANCE, [])
    console = instance.engine_root(made) / "pp.py"
    opened = cli(console, "-new", cwd=ws)
    if opened.returncode:
        failures.append(f"-new failed: {opened.stderr.strip()[:200]}")
        return len(failures)
    key = bench_key(made)
    before = instance.pins(made)["kit"]
    target = _bumped(source / "bases" / "kit" / "package.yaml")
    orphan = launcher(made, "ffffff")
    orphan.touch()

    # --- a pp process alive under the machine: nothing moves ----------------------------------------
    with lock.serving(made):
        blocked = cli(console, "upgrade", cwd=ws)
    if (blocked.returncode == 2 and "maintenance-busy" in blocked.stderr
            and instance.pins(made)["kit"] == before and persistence.slot_of(made, key).is_file()
            and not lock.held(lock.maintenance_of(made))):
        held("a pp process alive: maintenance-busy, nothing moved", f"kit stays {before}, the slot of "
             f"{key} stands, the lock free after")
    else:
        failures.append(f"  ✗ process alive               rc={blocked.returncode} {blocked.stderr.strip()[-200:]!r} "
                        f"kit={instance.pins(made)['kit']}")

    # --- none alive: the upgrade moves the pin, forgets the run with its files, sweeps ----------------
    lock.call_of(made, key).touch()
    launcher(made, key).touch()
    moved = cli(console, "upgrade", cwd=ws)
    gone = (persistence.renewed(persistence.slot_of(made, key)) is not None and not launcher(made, key).exists()
            and not lock.call_of(made, key).exists() and not orphan.exists())
    if (moved.returncode == 0 and f"kit {before} -> {target}" in moved.stdout
            and instance.pins(made)["kit"] == target and gone and not lock.held(lock.maintenance_of(made))):
        held("none alive, the upgrade moves and sweeps", f"kit {before} -> {target}; the slot of {key} a renewal "
             "mark, its two lock files and the orphan wake lock file gone; the lock free")
    else:
        failures.append(f"  ✗ upgrade passes              rc={moved.returncode} {moved.stdout[-200:]!r} "
                        f"{moved.stderr[-200:]!r} gone={gone}")

    # --- run locks held outside any pp process: the upgrade takes none ---------------------------------
    cli(console, "-new", cwd=ws)
    key2 = bench_key(made)
    target2 = _bumped(source / "bases" / "kit" / "package.yaml")
    with holding(lock.call_of(made, key2)), holding(launcher(made, key2)):
        cut = cli(console, "upgrade", cwd=ws)
    if (cut.returncode == 0 and instance.pins(made)["kit"] == target2
            and persistence.renewed(persistence.slot_of(made, key2)) is not None):
        held("run locks held outside any pp process: the upgrade takes none", f"kit {target} -> {target2}, "
             f"the run {key2} renewed")
    else:
        failures.append(f"  ✗ no run lock taken           rc={cut.returncode} {cut.stderr.strip()[-200:]!r} "
                        f"kit={instance.pins(made)['kit']}")
    return len(failures)
