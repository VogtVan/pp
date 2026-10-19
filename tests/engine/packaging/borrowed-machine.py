"""Scenario `borrowed-machine` -- an instance under a machine borrows it, on one house that
carries a witness package whose script writes in the records of the instance it serves:
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
- an instance that borrows adopts a PROC of the house on offer (`+REVUE` in a `tools:` of its
  own): the catalog describes it with its contract under the house's `procs/`, `-s REVUE` opens
  the conducted frame, its laws join the registry (a code the borrower declares too is said
  doubled), its `mount:` sleeps; a name the borrower carries itself stays its own, and an instance
  carrying its own machine adopts nothing from the house
- the house's `procs/HOUSE.md` rides a borrower that MOUNTS it (`mounts: {turn.begin: HOUSE.md}`
  on its TURN overlay): its law in the block and in the registry; a borrower without the line
  sees nothing of it; a borrower's own document may CALL a proc of the house, the build accepts it
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

SCRIBE = "scribe"            # the witness package this scenario pins in its source
RECORD = "operations.jsonl"  # the record its script appends to, under `.sys/records/`


def _scribe(source) -> None:
    """Pins the witness package `scribe` in the source: one script skill, `pp-scribe register
    <text>`, that appends the text to its instance's record -- the instance found by the
    bootstrap every package that imports carries (`skills/_core.py`), copied as it stands."""
    home = source / "packages" / SCRIBE
    skill = home / "skills" / f"pp-{SCRIBE}"
    skill.mkdir(parents=True)
    (home / "package.yaml").write_text(
        f"name: {SCRIBE}\nversion: 0.0.1\ndescription: >-\n  A witness whose script writes in "
        "the records of the instance it serves.\nrequires: [kit]\n", encoding="utf-8")
    shutil.copy(next((source / "packages").glob("*/skills/_core.py")), home / "skills" / "_core.py")
    (skill / "SKILL.md").write_text(
        f"---\nname: pp-{SCRIBE}\ndescription: the scribe witness -- register appends a line\n---\n\n"
        f"pp-{SCRIBE}\n", encoding="utf-8")
    (skill / f"pp-{SCRIBE}.py").write_text(
        "import json, sys\nfrom pathlib import Path\n"
        "sys.path.insert(0, str(Path(__file__).resolve().parents[1]))\n"
        "from _core import home\n"
        "root = home(__file__)\n"
        "if root is None or sys.argv[1:2] != ['register']:\n    raise SystemExit(2)\n"
        "records = root / '.sys' / 'records'\n"
        "records.mkdir(parents=True, exist_ok=True)\n"
        f"with (records / {RECORD!r}).open('a', encoding='utf-8') as handle:\n"
        "    handle.write(json.dumps({'entry': ' '.join(sys.argv[2:])}) + '\\n')\n",
        encoding="utf-8")


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
    _scribe(source)
    ws = bench.temp() / "house"
    house = install.install(engine, ws / INSTANCE, [SCRIBE])
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
    rc, _, err = contributions.run_skill(agent, f"pp-{SCRIBE}", ["register", "a fact of the agent"])
    mine = agent / ".sys" / "records" / RECORD
    theirs = house / ".sys" / "records" / RECORD
    if (rc == 0 and mine.is_file() and "a fact of the agent" in mine.read_text(encoding="utf-8")
            and "a fact of the agent" not in (theirs.read_text(encoding="utf-8") if theirs.is_file() else "")):
        held("a script writes in the instance that borrows", f"pp-{SCRIBE}, a file of the house's vendor, "
             "launched for agents/a: the fact lands in agents/a's records, not the house's")
    else:
        failures.append(f"  ✗ the borrower's records      rc={rc} {err.strip()[-300:]!r}")

    # --- a neighbour keeps its home ----------------------------------------------------------------
    other_ws = bench.temp() / "neighbour"
    neighbour = install.install(engine, other_ws / INSTANCE, [SCRIBE])
    script = neighbour / ".sys" / "vendor" / f"{SCRIBE}@{instance.pins(neighbour)[SCRIBE]}" \
        / "skills" / f"pp-{SCRIBE}" / f"pp-{SCRIBE}.py"
    ran = subprocess.run([sys.executable, str(script), "register", "a fact of the neighbour"],
                         capture_output=True, text=True, cwd=other_ws,
                         env={**os.environ, "PP_HOME": str(agent)})
    kept = neighbour / ".sys" / "records" / RECORD
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

    # --- the house's procs, adopted on offer by an instance that borrows its machine ---------------------
    (house / "procs").mkdir(exist_ok=True)
    (house / "procs" / "REVUE.md").write_text(
        "---\nname: REVUE\nkind: proc\ndescription: the house review\nmount: boot.ready\n"
        "constraints.production: |\n  RV1  a finding names its line.\nproc: |\n  WORK\n---\n"
        "Read the diff.\n", encoding="utf-8")
    (house / "procs" / "HOUSE.md").write_text(
        "---\nname: HOUSE\nkind: doc\ndescription: the house's common ground\n"
        "constraints.behavior: |\n  HS1  the house speaks plainly.\n---\nThe house charter.\n",
        encoding="utf-8")
    cli(console, "-install", "agents/b", cwd=ws)
    offerer = ws / "agents" / "b" / INSTANCE
    (offerer / "procs").mkdir(exist_ok=True)
    (offerer / "procs" / "TURN.md").write_text("---\nname: TURN\ntools: |\n  +REVUE\n---\n",
                                               encoding="utf-8")
    contract = house / "procs" / "REVUE.md"
    catalog = compiling.render_tools(offerer)
    if (instance.adopted(offerer, "REVUE") == contract and f"**`REVUE`** (house)" in catalog
            and str(contract) in catalog and "- `REVUE`\n" not in catalog):
        held("a borrower adopts the house's proc on offer", "`+REVUE` at its TURN: the catalog lists it "
             "described, its contract in the house's procs/, no bare name left to the harness")
    else:
        failures.append(f"  ✗ house proc in the catalog   adopted={instance.adopted(offerer, 'REVUE')} "
                        f"{catalog[catalog.find('## Adopted'):][:300]!r}")
    first = cli(console, "--instance", str(offerer), "-new", cwd=ws / "agents" / "b")
    door = cli(console, "--instance", str(offerer), "-s", "REVUE", cwd=ws / "agents" / "b")
    if (first.returncode == 0 and "▸ REVUE" not in first.stdout and "HS1" not in first.stdout
            and door.returncode == 0
            and "▸ REVUE{" in door.stdout and "RV1" in door.stdout):
        held("the adopted proc is a door, never a mount", "the borrower's boot mounts nothing of the house "
             "(its `mount: boot.ready` sleeps); `-s REVUE` opens the conducted frame, RV1 in force")
    else:
        failures.append(f"  ✗ house proc played           rc={first.returncode}/{door.returncode} "
                        f"{door.stdout[-300:]!r} {door.stderr[-200:]!r}")
    (offerer / "procs" / "MINE.md").write_text(
        "---\nname: MINE\nkind: doc\nconstraints.production: |\n  RV1  the borrower's own law.\n---\n",
        encoding="utf-8")
    registry = compiling.render_registry(offerer)
    doubled = [one for one in compiling.lint(offerer) if one.startswith("constraint-doubled: `RV1`")]
    (offerer / "procs" / "MINE.md").unlink()
    if "`RV1`" in registry and doubled and "REVUE.md" in doubled[0]:
        held("the adopted proc's laws join the registry", "RV1 registered; the borrower's own RV1 is "
             "said doubled against the house's REVUE")
    else:
        failures.append(f"  ✗ house proc in the registry  doubled={doubled}")
    (offerer / "procs" / "REVUE.md").write_text(
        "---\nname: REVUE\nkind: proc\ndescription: the borrower's own\nproc: |\n  WORK\n---\n",
        encoding="utf-8")
    kept = instance.resolve(offerer, "REVUE.md")
    kept_catalog = compiling.render_tools(offerer)
    (offerer / "procs" / "REVUE.md").unlink()
    (own / "procs").mkdir(exist_ok=True)
    (own / "procs" / "TURN.md").write_text("---\nname: TURN\ntools: |\n  +REVUE\n---\n", encoding="utf-8")
    alone = compiling.render_tools(own)
    (own / "procs" / "TURN.md").unlink()
    if (kept == offerer / "procs" / "REVUE.md" and str(contract) not in kept_catalog
            and instance.adopted(own, "REVUE") is None and "- `REVUE`\n" in alone):
        held("a name the borrower carries stays its own; a machine of its own adopts nothing",
             "the borrower's REVUE.md is the base, the house unread; sub/own leaves `REVUE` to its harness")
    else:
        failures.append(f"  ✗ house proc out of reach     kept={kept} own={instance.adopted(own, 'REVUE')}")

    # --- the house's HOUSE.md, mounted by a borrower that names it; a CALL to the house builds ------------
    cli(console, "-install", "agents/c", cwd=ws)
    mounter = ws / "agents" / "c" / INSTANCE
    (mounter / "procs").mkdir(exist_ok=True)
    (mounter / "procs" / "TURN.md").write_text("---\nname: TURN\nmounts:\n  turn.begin: HOUSE.md\n---\n",
                                               encoding="utf-8")
    (mounter / "procs" / "CHAIN.md").write_text(
        "---\nname: CHAIN\nkind: proc\ndescription: calls the house review\nproc: |\n  CALL REVUE.md\n---\n",
        encoding="utf-8")
    built = None
    try:
        compiling.build_tools(mounter)
    except Exception as refusal:                      # the build judges the CALL to the house
        built = refusal
    hosted = cli(console, "--instance", str(mounter), "-new", cwd=ws / "agents" / "c")
    boot = hosted.stdout
    key = re.search(r"run ([0-9a-f]{6})", boot)
    while key and "a reading continues" in boot.rsplit("▶ ", 1)[-1]:      # the cut boot, drained
        boot += cli(console, "--instance", str(mounter), key.group(1), cwd=ws / "agents" / "c").stdout
    if (built is None and hosted.returncode == 0 and "HS1" in boot
            and "`HS1`" in compiling.render_registry(mounter)):
        held("a borrower mounts the house's HOUSE.md", "`mounts: {turn.begin: HOUSE.md}` at its TURN: "
             "HS1 in its block and its registry; its CALL to the house's REVUE builds")
    else:
        failures.append(f"  ✗ house mounted               built={built!r} rc={hosted.returncode} "
                        f"{boot[-300:]!r} {hosted.stderr[-200:]!r}")

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
