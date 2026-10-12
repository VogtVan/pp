"""Scenario `borrowed-machine` -- 10 case(s) (batch la-machine-en-remontant, 2026-10-03; batch
le-package-agent, its rework, 2026-10-03):
- an instance born by `-install <dir>` at a machine's console, `<dir>` under it, BORROWS the
  machine: its `.sys/` carries neither `engine/` nor `vendor/`, its manifest no engine, no
  packages, no source; its readers answer the machine's engine and bundles
- the borrowing instance opens a run by its own launcher, the machine untouched
- a script the engine launches for the borrowing instance writes in ITS records, not the
  machine's (`PP_HOME` names the instance that borrows the script's machine)
- a neighbour keeps its home: a script of an instance carrying its own machine, launched under
  a `PP_HOME` naming another instance, writes in its own records
- `doctor` and `upgrade` played in the borrowing instance refuse `machine-borrowed`, nothing
  written, the machine's fingerprint the same
- an instance with no machine under it nor above refuses `machine-missing`
- `-own` gives an instance under a machine its own copy of the machine
- `-install a/c/x` stays generic: a borrower two levels down, outside `agents/`, with its doors
- a pp process alive at a borrowing instance (the machine held shared through it) makes the
  machine's `upgrade` refuse `maintenance-busy`, nothing moved
- the machine's `upgrade` DESCENDS: it names the borrowing instance it found, renews its runs,
  recompiles it at the new version, and leaves alone a subtree carrying its own machine and a
  hidden directory
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys

import yaml

from conductor import compiling, contributions, instance, persistence
from conductor.state import lock
from conductor import install
from tests.harness import INSTANCE, bench_key, cli


def _fingerprint(meta) -> str:
    """-> one hash over every file of the machine (`.sys/engine/`, `.sys/vendor/`), names and bytes."""
    digest = hashlib.sha256()
    for home in (meta / ".sys" / "engine", meta / ".sys" / "vendor"):
        for path in sorted(home.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                digest.update(str(path.relative_to(meta)).encode("utf-8"))
                digest.update(path.read_bytes())
    return digest.hexdigest()


def _bumped(manifest) -> str:
    """The package's version at the source copy, raised by one on its last number -> the new version."""
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
    ws = bench.temp() / "house"
    house = install.install(engine, ws / INSTANCE, ["continuity"])
    console = house / ".sys" / "engine" / "pp.py"
    before = _fingerprint(house)

    # --- the birth under a machine: the instance borrows it -------------------------------------
    born = cli(console, "-install", "agents/a", cwd=ws)
    agent = ws / "agents" / "a" / INSTANCE
    manifest = agent / ".sys" / "instance.yaml"
    declared = (yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}) if manifest.is_file() else {}
    machine_free = not (agent / ".sys" / "engine").exists() and not (agent / ".sys" / "vendor").exists()
    if (born.returncode == 0 and machine_free
            and not {"engine", "packages", "source"} & set(declared)
            and instance.engine_root(agent) == house / ".sys" / "engine"
            and [root.name for root in instance.vendored(agent)] == [root.name for root in instance.vendored(house)]):
        held("an instance born under a machine borrows it", "agents/a/.pp/.sys without engine/ nor "
             f"vendor/, its manifest {sorted(declared)}; its engine and its bundles are the house's")
    else:
        failures.append(f"  ✗ birth by borrowing          rc={born.returncode} {born.stderr.strip()[-300:]!r} "
                        f"machine_free={machine_free} declared={sorted(declared)}")
        return len(failures)

    # --- a run by its own launcher, the machine untouched ----------------------------------------
    launcher = ws / "agents" / "a" / "pp"
    opened = subprocess.run(["sh", str(launcher), "-new"], capture_output=True, text=True,
                            cwd=ws / "agents" / "a")
    key = bench_key(agent) if persistence.slots(agent) else None
    if (opened.returncode == 0 and key is not None and not persistence.slots(house)
            and _fingerprint(house) == before):
        held("the borrowing instance opens its run", f"run {key} in agents/a/.pp/.sys/state by its launcher; "
             "the house holds no run, its machine the same to the byte")
    else:
        failures.append(f"  ✗ run by the launcher         rc={opened.returncode} {opened.stderr.strip()[-300:]!r} "
                        f"key={key}")

    # --- a script launched for the borrowing instance writes in ITS records ----------------------
    rc, _, err = contributions.run_skill(agent, "pp-continuity", ["register", "a fact of the agent"])
    mine = agent / ".sys" / "records" / "operations.jsonl"
    theirs = house / ".sys" / "records" / "operations.jsonl"
    if (rc == 0 and mine.is_file() and "a fact of the agent" in mine.read_text(encoding="utf-8")
            and "a fact of the agent" not in (theirs.read_text(encoding="utf-8") if theirs.is_file() else "")):
        held("a script writes in the instance that borrows", "pp-continuity, a file of the house's vendor, "
             "launched for agents/a: the fact lands in agents/a's operations, not the house's")
    else:
        failures.append(f"  ✗ the borrower's records      rc={rc} {err.strip()[-300:]!r}")

    # --- a neighbour keeps its home ----------------------------------------------------------------
    other_ws = bench.temp() / "neighbour"
    neighbour = install.install(engine, other_ws / INSTANCE, ["continuity"])
    script = neighbour / ".sys" / "vendor" / f"continuity@{instance.pins(neighbour)['continuity']}" \
        / "skills" / "pp-continuity" / "pp-continuity.py"
    ran = subprocess.run([sys.executable, str(script), "register", "a fact of the neighbour"],
                         capture_output=True, text=True, cwd=other_ws,
                         env={**os.environ, "PP_HOME": str(agent)})
    kept = neighbour / ".sys" / "records" / "operations.jsonl"
    if (ran.returncode == 0 and kept.is_file() and "a fact of the neighbour" in kept.read_text(encoding="utf-8")
            and "a fact of the neighbour" not in mine.read_text(encoding="utf-8")):
        held("a neighbour keeps its home", "its own script, launched under PP_HOME naming agents/a: the fact "
             "lands in the neighbour's records -- agents/a borrows another machine")
    else:
        failures.append(f"  ✗ the neighbour               rc={ran.returncode} {ran.stderr.strip()[-300:]!r}")

    # --- the machine's verbs refuse in the borrowing instance ----------------------------------------
    said = {}
    for verb in ("doctor", "upgrade"):
        done = cli(console, "--instance", str(agent), verb, cwd=ws / "agents" / "a")
        said[verb] = done.returncode == 2 and "machine-borrowed" in done.stderr and str(house) in done.stderr
    if all(said.values()) and _fingerprint(house) == before:
        held("doctor and upgrade refuse in the borrowing instance", "machine-borrowed, naming the house; "
             "the machine the same to the byte")
    else:
        failures.append(f"  ✗ machine-borrowed            {said}")

    # --- no machine under nor above: machine-missing ----------------------------------------------------
    stray = bench.temp() / "stray" / "a"
    shutil.copytree(ws / "agents" / "a", stray, ignore=shutil.ignore_patterns("state"))
    lost = cli(console, "--instance", str(stray / INSTANCE), "-new", cwd=stray)
    if lost.returncode == 2 and "machine-missing" in lost.stderr:
        held("no machine above: machine-missing", "agents/a copied out of the house refuses by its name")
    else:
        failures.append(f"  ✗ machine-missing             rc={lost.returncode} {lost.stderr.strip()[-300:]!r}")

    # --- -own: a copy of the machine under a machine ----------------------------------------------------
    owned = cli(console, "-install", "sub/own", "-own", cwd=ws)
    own = ws / "sub" / "own" / INSTANCE
    if owned.returncode == 0 and (own / ".sys" / "engine").is_dir() and (own / ".sys" / "vendor").is_dir():
        held("-own copies the machine", "sub/own/.pp carries its own engine/ and vendor/ under the house")
    else:
        failures.append(f"  ✗ -own                        rc={owned.returncode} {owned.stderr.strip()[-300:]!r}")

    # --- -install stays generic: a borrower two levels down, outside agents/, with its doors -------------
    deep = cli(console, "-install", "a/c/x", cwd=ws)
    deep_meta = ws / "a" / "c" / "x" / INSTANCE
    deep_doors = sorted(one.name for one in (ws / "a" / "c" / "x").iterdir()
                        if one.name in ("CLAUDE.md", "AGENTS.md")) if deep_meta.parent.is_dir() else []
    if (deep.returncode == 0 and instance.is_instance(deep_meta)
            and not (deep_meta / ".sys" / "engine").exists() and not (deep_meta / ".sys" / "vendor").exists()
            and instance.engine_root(deep_meta) == house / ".sys" / "engine"
            and deep_doors == ["AGENTS.md", "CLAUDE.md"] and deep_meta in instance.borrowers(house)):
        held("-install stays generic two levels down", "a/c/x/.pp borrows the house's machine, its doors "
             "AGENTS.md and CLAUDE.md beside it; the descent finds it")
    else:
        failures.append(f"  ✗ generic install, deep       rc={deep.returncode} {deep.stderr.strip()[-300:]!r} "
                        f"doors={deep_doors}")

    # a hidden directory holding a borrowing-shaped instance: the descent never looks there
    hidden = ws / ".hidden" / "x" / INSTANCE
    (hidden / ".sys").mkdir(parents=True)
    (hidden / ".sys" / "instance.yaml").write_text("slug: x\n", encoding="utf-8")
    own_pins = dict(instance.pins(own))

    # --- a pp process alive at the borrowing instance: the machine's upgrade refuses ----------------------
    stale = compiling.receipts(agent)["system.md"]["inputs"]
    target = _bumped(source / "bases" / "kit" / "package.yaml")
    was = instance.pins(house)["kit"]
    with lock.serving(agent):                     # the bench, a pp process of the borrower
        busy = cli(console, "upgrade", cwd=ws)
    if (busy.returncode == 2 and "maintenance-busy" in busy.stderr
            and instance.pins(house)["kit"] == was):
        held("a pp process at a borrower: maintenance-busy", f"the house's upgrade refused; the kit stays {was}")
    else:
        failures.append(f"  ✗ maintenance-busy, borrower  rc={busy.returncode} {busy.stderr.strip()[-300:]!r}")

    # --- released: the upgrade descends -------------------------------------------------------------------
    moved = cli(console, "upgrade", cwd=ws)
    fresh = compiling.receipts(agent)["system.md"]["inputs"]
    compiled = fresh != stale and fresh == compiling.receipt_inputs(agent)
    if (moved.returncode == 0 and f"kit {was} -> {target}" in moved.stdout and "agents/a" in moved.stdout
            and persistence.slots(agent)
            and all(persistence.renewed(one) is not None for one in persistence.slots(agent)) and compiled
            and instance.pins(own) == own_pins and not (hidden / ".sys" / "tools.md").exists()):
        held("the machine's upgrade descends", f"kit {was} -> {target}; agents/a named, its run renewed, "
             "recompiled at the new version; sub/own (its own machine) and .hidden left alone")
    else:
        failures.append(f"  ✗ the descent                 rc={moved.returncode} {moved.stdout[-300:]!r} "
                        f"{moved.stderr[-300:]!r} slots={persistence.slots(agent)} compiled={compiled}")
    return len(failures)
