"""Scenario `borrowed-machine` -- an instance under a machine borrows it, on one house that
carries a witness package whose script writes in the records of the instance it serves:
- an instance born by `-install <dir>` at a machine's console, `<dir>` under it, BORROWS the
  machine: its `.sys/` carries neither `engine/` nor `vendor/`, its manifest no engine, no
  packages, no source; its readers answer the machine's engine and bundles
- the borrowing instance opens a run by its own launcher, the machine untouched
- `version` played in the borrowing instance says the machine's source and engine; `-stats <key>`
  played at the house finds the borrower's run and names where it lives; a key known nowhere
  refuses `run-unknown`
- a script the engine launches for the borrowing instance writes in ITS records, not the
  machine's (`PP_HOME` names the instance that borrows the script's machine)
- a neighbour keeps its home: a script of an instance carrying its own machine, launched under
  a `PP_HOME` naming another instance, writes in its own records
- `doctor` and `upgrade` played in the borrowing instance refuse `machine-borrowed`, nothing
  written, the machine's fingerprint the same
- an instance with no machine under it nor above refuses `machine-missing`
- `-own` gives an instance under a machine its own copy of the machine
- a borrower offered a proc of the house that carries a name of its own keeps its own, the lint
  warning `house-shadowed`, and an instance carrying its own machine adopts nothing from the
  house (the adoption itself is the pattern `composition/adoption`)
- the house's `procs/HOUSE.md` rides a borrower that IMPORTS it (`imports: HOUSE.md` on its
  TURN overlay): its law in the block and in the registry, its offer REVUE; at the park the
  principal opens REVUE; a borrower without the line sees nothing of it; a borrower's own document
  may CALL a proc of the house, the build accepts it
- the registry follows the imports of what the borrower adopts: HOUSE imports CODEX, CX1 is registered
- a bare name HOUSE's `serve:` names resolves as the house resolves it -- its instance and its machine, then
  its workspace --, never in the borrower's instance nor at its root
- a path HOUSE's `serve:` names that the house reads in its machine's copy (`engine/patterns/...`) is
  served at the borrower from that copy
- a path HOUSE's `serve:` names reads the house's workspace: the house's file served where the
  borrower holds one of the same path, a file the house lacks not served -- the block says so,
  nothing read at the borrower --; a document of a package reads the borrower's file as before
- a borrower's document serves `engine/patterns/...` from the machine's `.sys/`, the same bytes as
  at the house; an instance carrying its own machine resolves through the same list as before
- `-install a/c/x` stays generic: a borrower two levels down, outside `agents/`, no door beside it
- a pp process alive at a borrowing instance (the machine held shared through it) makes the
  machine's `upgrade` refuse `maintenance-busy`, nothing moved
- the machine's `upgrade` DESCENDS: it names the borrowing instance it found, renews its runs,
  recompiles it at the new version, and leaves alone a subtree carrying its own machine, a
  hidden directory, and a CLONE of an instance -- its manifest declares a source and packages,
  the machine its git ignores is absent: no borrower, nor anything beneath it
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys

import yaml

from conductor import Conductor, compiling, contributions, discovery, instance, persistence, store
from conductor.state import lock
from conductor import install
from tests.harness import INSTANCE, bench_key, cli, na_proof, stepped

SCRIBE = "scribe"            # the witness package this scenario pins in its source
RECORD = "operations"        # the record of the store its script appends to
NOTE = "notes/note.md"       # one path in the house's workspace and in a borrower's
HOUSE_NOTE = "The house's own note, read where the house lives."
AGENT_NOTE = "The borrower's own note, a file of the same path."
AGENT_ONLY = "A note the borrower alone holds."
SHELF = "notes/shelf.md"     # a path HOUSE reads from a tree it names, the house holding one too
SHELF_NOTE = "The shelf's note, read from the tree the row names."
HOUSE_SHELF = "The house's copy of the shelf's note, never read."
CLONE_NOTE = "The clone's note, the run's own tree."
MACHINE_ROW = "engine/patterns/packaging/house-ground/README.md"   # a path the house reads in its machine's copy
LEXICON = "LEXICON.md"       # a bare name in the house's procs and in the borrower's
HOUSE_LEXICON = "HOUSE-LEXICON: the house's own, as the house resolves the name."
AGENT_LEXICON = "AGENT-LEXICON: the borrower's own, never read for the house."
GLOSS = "GLOSS.md"           # a bare name a harness home answers, at the house's root and at the borrower's
HOUSE_GLOSS = "HOUSE-GLOSS: the skill of the house's harness home."
AGENT_GLOSS = "AGENT-GLOSS: the skill of the borrower's harness home, never read for the house."
GUIDE = "GUIDE.md"           # a bare name at the root of the house's workspace and of the borrower's
HOUSE_GUIDE = "HOUSE-GUIDE: the house's guide, read where the house lives."
AGENT_GUIDE = "AGENT-GUIDE: the borrower's own guide, never read for the house."


def _scribe(source) -> None:
    """Pins the witness package `scribe` in the source: one script skill, `pp-scribe register
    <text>`, that appends the text to its instance's record through the store -- the instance and
    the engine found by the bootstrap every package that imports carries (`skills/_core.py`),
    copied as it stands."""
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
    (home / "procs").mkdir()
    (home / "procs" / "SCRIBED.md").write_text(
        f"---\nname: SCRIBED\nkind: doc\ndescription: a document of the package that reads a path\n"
        f"serve: |\n  {NOTE}\n---\n\nThe scribe's reading.\n", encoding="utf-8")
    (skill / f"pp-{SCRIBE}.py").write_text(
        "import sys\nfrom pathlib import Path\n"
        "sys.path.insert(0, str(Path(__file__).resolve().parents[1]))\n"
        "from _core import core, home\n"
        "root = home(__file__)\n"
        "if root is None or sys.argv[1:2] != ['register']:\n    raise SystemExit(2)\n"
        f"core(__file__).store.of(root).append({RECORD!r}, {{'entry': ' '.join(sys.argv[2:])}})\n",
        encoding="utf-8")


def _holds(meta, text: str) -> int:
    """-> how many entries of the record at `meta`'s store carry `text`."""
    return store.of(meta).count(RECORD, where={"entry": text})


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

    # --- version at the borrower, -stats at the house ----------------------------------------------
    told = cli(console, "--instance", str(agent), "version", cwd=ws / "agents" / "a")
    stats = cli(console, "-stats", key, cwd=ws) if key else None
    nowhere = cli(console, "-stats", "abcdef", cwd=ws)
    house_source = str(instance.read(house).get("source", ""))
    if (told.returncode == 0 and f"source {house_source}" in told.stdout and "source ?" not in told.stdout
            and stats is not None and stats.returncode == 0 and key in stats.stdout
            and "agents/a" in stats.stdout and "0 run(s)" not in stats.stdout
            and nowhere.returncode == 2 and "run-unknown" in nowhere.stderr):
        held("the borrower reads its machine; the house reads its borrowers", f"`version` in agents/a says "
             f"the house's source; `-stats {key}` at the house finds the run under agents/a; a key known "
             "nowhere refuses run-unknown")
    else:
        failures.append(f"  ✗ version / -stats            {told.stdout[:160]!r} "
                        f"{stats and stats.stdout[-200:]!r} {nowhere.returncode} {nowhere.stderr[-120:]!r}")

    # --- a script launched for the borrowing instance writes in ITS records ----------------------
    rc, _, err = contributions.run_skill(agent, f"pp-{SCRIBE}", ["register", "a fact of the agent"])
    if (rc == 0 and _holds(agent, "a fact of the agent") == 1 and _holds(house, "a fact of the agent") == 0):
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
    if (ran.returncode == 0 and _holds(neighbour, "a fact of the neighbour") == 1
            and _holds(agent, "a fact of the neighbour") == 0):
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

    # --- the house's procs, offered to a borrower: a name of its own hides the house's -----------------
    (house / "procs").mkdir(exist_ok=True)
    (house / "procs" / "REVUE.md").write_text(
        "---\nname: REVUE\nkind: proc\ndescription: the house review\nmount: boot.initialize\n"
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
    (offerer / "procs" / "REVUE.md").write_text(
        "---\nname: REVUE\nkind: proc\ndescription: the borrower's own\nproc: |\n  WORK\n---\n",
        encoding="utf-8")
    kept = instance.resolve(offerer, "REVUE.md")
    kept_catalog = compiling.render_tools(offerer)
    shadowing = [one for one in compiling.lint(offerer) if one.startswith("house-shadowed")]
    (offerer / "procs" / "REVUE.md").unlink()
    unshadowed = [one for one in compiling.lint(offerer) if one.startswith("house-shadowed")]
    if len(shadowing) == 1 and "REVUE.md" in shadowing[0] and str(contract) in shadowing[0] and not unshadowed:
        held("a borrower's document that hides the house's warns", "its procs/REVUE.md: `house-shadowed` "
             "names both files; removed, the lint says nothing")
    else:
        failures.append(f"  ✗ house-shadowed              {shadowing} / {unshadowed}")
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
    (mounter / "procs" / "TURN.md").write_text("---\nname: TURN\nimports: |\n  HOUSE.md\n  SCRIBED.md\n---\n",
                                               encoding="utf-8")
    (house / "procs" / "HOUSE.md").write_text(
        "---\nname: HOUSE\nkind: doc\ndescription: the house's common ground\n"
        "constraints.behavior: |\n  HS1  the house speaks plainly.\ntools: |\n  +REVUE\n"
        f"materials: |\n  shelf: {ws / 'shelf'}\n"
        "imports: |\n  CODEX.md\n"
        f"serve: |\n  {NOTE}\n  notes/mine.md\n  {SHELF} @shelf\n  {GUIDE}\n  {MACHINE_ROW}\n  {LEXICON}\n  {GLOSS}\n---\nThe house charter.\n",
        encoding="utf-8")
    for root, text in ((ws, HOUSE_GLOSS), (ws / "agents" / "c", AGENT_GLOSS)):
        home = root / instance.HARNESS_HOMES[0] / "GLOSS"
        home.mkdir(parents=True, exist_ok=True)
        (home / "SKILL.md").write_text(f"---\nname: GLOSS\ndescription: a gloss\n---\n{text}\n", encoding="utf-8")
    for meta, text in ((house, HOUSE_LEXICON), (mounter, AGENT_LEXICON)):
        (meta / "procs" / LEXICON).write_text(
            f"---\nname: LEXICON\nkind: doc\ndescription: a lexicon\n---\n{text}\n", encoding="utf-8")
    (house / "procs" / "CODEX.md").write_text(
        "---\nname: CODEX\nkind: doc\ndescription: what HOUSE imports in its turn\n"
        "constraints.behavior: |\n  CX1  the codex is cited by its article.\n---\nThe codex.\n", encoding="utf-8")
    for root, files in ((ws, {NOTE: HOUSE_NOTE, SHELF: HOUSE_SHELF, GUIDE: HOUSE_GUIDE}),
                        (ws / "shelf", {SHELF: SHELF_NOTE}),
                        (ws / "agents" / "c" / "clone", {NOTE: CLONE_NOTE}),
                        (ws / "agents" / "c", {NOTE: AGENT_NOTE, "notes/mine.md": AGENT_ONLY, GUIDE: AGENT_GUIDE})):
        for relpath, text in files.items():
            (root / relpath).parent.mkdir(parents=True, exist_ok=True)
            (root / relpath).write_text(text + "\n", encoding="utf-8")
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
    last = boot
    for _ in range(8):                                                     # the cut boot, drained
        if not key or "a reading continues" not in last.rsplit("▶", 1)[-1]:
            break
        last = cli(console, "--instance", str(mounter), key.group(1), cwd=ws / "agents" / "c").stdout
        boot += last
    if (built is None and hosted.returncode == 0 and "HS1" in boot
            and "`HS1`" in compiling.render_registry(mounter)):
        held("a borrower imports the house's HOUSE.md", "`imports: HOUSE.md` at its TURN: "
             "HS1 in its block and its registry; its CALL to the house's REVUE builds")
    else:
        failures.append(f"  ✗ house imported              built={built!r} rc={hosted.returncode} "
                        f"{boot[-300:]!r} {hosted.stderr[-200:]!r}")
    if (HOUSE_NOTE in boot and AGENT_NOTE in boot and AGENT_ONLY not in boot
            and "(not served" in boot and "notes/mine.md" in boot):
        held("a house document reads the house", f"HOUSE's `{NOTE}` served from the house's workspace where "
             "agents/c holds its own; notes/mine.md, which the house lacks, not served and said; the package's "
             f"SCRIBED reads agents/c's `{NOTE}` as before")
    else:
        failures.append(f"  ✗ the house's reading        house={HOUSE_NOTE in boot} agent={AGENT_NOTE in boot} "
                        f"mine={AGENT_ONLY in boot} said={'(not served' in boot}")
    if HOUSE_LEXICON in boot and AGENT_LEXICON not in boot:
        held("a bare name resolves as the house resolves it", f"`{LEXICON}` in the house's procs and in the "
             "borrower's: HOUSE serves the house's")
    else:
        failures.append(f"  ✗ the house's name            house={HOUSE_LEXICON in boot} agent={AGENT_LEXICON in boot}")
    if HOUSE_GLOSS in boot and AGENT_GLOSS not in boot:
        held("a harness skill of the house, as the house finds it", f"`{GLOSS}` in the house's harness home and "
             "the borrower's: HOUSE serves the house's")
    else:
        failures.append(f"  ✗ the house's harness skill   house={HOUSE_GLOSS in boot} agent={AGENT_GLOSS in boot}")
    machine_text = (house / ".sys" / MACHINE_ROW).read_text(encoding="utf-8").strip()
    if machine_text in boot and f"(not served: `{MACHINE_ROW}`" not in boot:
        held("a row the house reads in its machine", f"HOUSE's `{MACHINE_ROW}`, which the house reads in the "
             "machine's copy when it plays HOUSE, served at the borrower from that copy")
    else:
        failures.append(f"  ✗ the machine's row           served={machine_text in boot} "
                        f"said={f'(not served: `{MACHINE_ROW}`' in boot}")
    if HOUSE_GUIDE in boot and AGENT_GUIDE not in boot:
        held("a bare name of the house reads the house", f"HOUSE's `{GUIDE}`: the house's file served, the "
             "borrower's of the same name at its root never read")
    else:
        failures.append(f"  ✗ the bare name              house={HOUSE_GUIDE in boot} agent={AGENT_GUIDE in boot}")
    registry = compiling.render_registry(mounter)
    if "`CX1`" in registry and "`HS1`" in registry and "CX1" in boot:
        held("the registry follows the house's imports", "HOUSE imports CODEX: CX1 in the borrower's registry "
             "beside HS1, and in its block")
    else:
        failures.append(f"  ✗ the transitive registry    CX1 registry={'`CX1`' in registry} block={'CX1' in boot}")
    if SHELF_NOTE in boot and HOUSE_SHELF not in boot:
        held("a named tree keeps the upper hand", f"HOUSE's `{SHELF} @shelf` reads the tree shelf, never the "
             "house's file of the same path")
    else:
        failures.append(f"  ✗ the named tree             shelf={SHELF_NOTE in boot} house={HOUSE_SHELF in boot}")
    cloned = cli(console, "--instance", str(mounter), "-new", cwd=ws / "agents" / "c", env={"PP_WORKDIR": "clone"})
    clone_boot, clone_key = cloned.stdout, re.search(r"run ([0-9a-f]{6})", cloned.stdout)
    for _ in range(8):                                                     # the cut boot, drained
        if not clone_key or "a reading continues" not in clone_boot.rsplit("▶", 1)[-1]:
            break
        clone_boot += cli(console, "--instance", str(mounter), clone_key.group(1), cwd=ws / "agents" / "c").stdout
    if cloned.returncode == 0 and HOUSE_NOTE in clone_boot and CLONE_NOTE in clone_boot and AGENT_NOTE not in clone_boot:
        held("the house before the clone", f"a run given the tree clone: HOUSE's bare `{NOTE}` still read at the "
             "house; the package's SCRIBED reads the clone")
    else:
        failures.append(f"  ✗ the house before the clone  rc={cloned.returncode} house={HOUSE_NOTE in clone_boot} "
                        f"clone={CLONE_NOTE in clone_boot} agent={AGENT_NOTE in clone_boot} {cloned.stderr[-200:]!r}")
    if key:
        member = discovery.member_at(mounter)
        run = key.group(1)
        parked = None
        block = Conductor(member, console, run).peek()
        for _ in range(12):                          # bounded: a run that stops moving fails the case
            if block is None or block.wait:
                parked = block
                break
            block = stepped(lambda: Conductor(member, console, run), na_proof(block) if block.judged else "")
        door = cli(console, "--instance", str(mounter), run, "-s", "REVUE", cwd=ws / "agents" / "c")
        if (parked is not None and "REVUE" in [one.name for one in parked.tools]
                and door.returncode == 0 and "▸ REVUE{" in door.stdout and "RV1" in door.stdout):
            held("the house's offer stands at the park", "REVUE, HOUSE's offer, among the parked block's "
                 "tools; the principal's `-s REVUE` opens its frame, RV1 in force")
        else:
            failures.append(f"  ✗ the offer at the park       parked={parked and parked.wait} "
                            f"tools={parked and [one.name for one in parked.tools]} rc={door.returncode} "
                            f"{door.stdout[-200:]!r} {door.stderr[-200:]!r}")

    # --- the machine's patterns, served to a borrower; a machine of its own resolves as it did -------------
    pattern = "engine/patterns/packaging/proc-folders/README.md"
    cli(console, "-install", "agents/d", cwd=ws)
    reader = ws / "agents" / "d" / INSTANCE
    (reader / "procs").mkdir(exist_ok=True)
    (reader / "procs" / "TURN.md").write_text("---\nname: TURN\nimports: |\n  PATTERN.md\n---\n",
                                              encoding="utf-8")
    (reader / "procs" / "PATTERN.md").write_text(
        f"---\nname: PATTERN\nkind: doc\ndescription: a pattern of the machine\nserve: |\n  {pattern}\n---\n",
        encoding="utf-8")
    home_text = (house / ".sys" / pattern).read_bytes().decode("utf-8")
    opened = cli(console, "--instance", str(reader), "-new", cwd=ws / "agents" / "d")
    boot = opened.stdout
    key = re.search(r"run ([0-9a-f]{6})", boot)
    last = boot
    for _ in range(8):                                                     # the cut boot, drained
        if not key or "a reading continues" not in last.rsplit("▶", 1)[-1]:
            break
        last = cli(console, "--instance", str(reader), key.group(1), cwd=ws / "agents" / "d").stdout
        boot += last
    carried = {meta: [meta, meta / "procs", meta / ".sys"]                 # the list before the borrow
                     + [root / sub for sub in ("overlays", "procs", "refs")
                        for root in reversed(instance.vendored(meta))]
               for meta in (house, own)}
    carried = {meta: [one for one in paths if one.is_dir()] for meta, paths in carried.items()}
    paths = instance.search_paths(reader)
    if (opened.returncode == 0 and home_text.strip() in boot
            and instance.resolve(reader, pattern).read_bytes() == (house / ".sys" / pattern).read_bytes()
            and paths[paths.index(reader / ".sys") + 1] == house / ".sys"
            and all(instance.search_paths(meta) == carried[meta] for meta in carried)):
        held("a borrower serves the machine's patterns", f"{pattern} rendered at agents/d as at the house, "
             "byte for byte; the house and sub/own resolve through the same list as before")
    else:
        failures.append(f"  ✗ the machine's patterns      rc={opened.returncode} served={home_text.strip() in boot} "
                        f"paths={[str(one) for one in paths[:4]]} {opened.stderr[-200:]!r}")

    # --- the nearest compiled document wins: the borrower's catalogues, served once ----------------------
    served = {name: boot.count(title) for name, title in (("tools.md", "# The TOOLS of this instance"),
                                                         ("output.md", "# The FORMATS of this instance"))}
    own_catalogs = {name: instance.chain(reader, name) for name in served}
    if (served == {"tools.md": 1, "output.md": 1}
            and all(hits == [reader / ".sys" / name] for name, hits in own_catalogs.items())
            and instance.chain(reader, pattern) == [house / ".sys" / pattern] and home_text.strip() in boot):
        held("the nearest compiled document wins", "agents/d's boot serves tools.md and output.md once, "
             "its own .sys alone in their chain; the machine's .sys still answers the pattern")
    else:
        failures.append(f"  ✗ the nearest compiled        served={served} "
                        f"chain={ {name: [str(one) for one in hits] for name, hits in own_catalogs.items()} }")

    # --- -install stays generic: a borrower two levels down, outside agents/, no door beside it ---------
    deep = cli(console, "-install", "a/c/x", cwd=ws)
    deep_meta = ws / "a" / "c" / "x" / INSTANCE
    deep_standing = sorted(one.name for one in (ws / "a" / "c" / "x").iterdir()
                        if one.name in ("CLAUDE.md", "AGENTS.md", "GEMINI.md")) if deep_meta.parent.is_dir() else []
    if (deep.returncode == 0 and instance.is_instance(deep_meta)
            and not (deep_meta / ".sys" / "engine").exists() and not (deep_meta / ".sys" / "vendor").exists()
            and instance.engine_root(deep_meta) == house / ".sys" / "engine"
            and deep_standing == [] and deep_meta in instance.borrowers(house)):
        held("-install stays generic two levels down", "a/c/x/.pp borrows the house's machine, no door "
             "beside it; the descent finds it")
    else:
        failures.append(f"  ✗ generic install, deep       rc={deep.returncode} {deep.stderr.strip()[-300:]!r} "
                        f"standing={deep_standing}")

    # a hidden directory holding a borrowing-shaped instance: the descent never looks there
    hidden = ws / ".hidden" / "x" / INSTANCE
    (hidden / ".sys").mkdir(parents=True)
    (hidden / ".sys" / "instance.yaml").write_text("slug: x\n", encoding="utf-8")
    own_pins = dict(instance.pins(own))

    # a CLONE of an instance carrying its own machine: its tracked files alone (the machine is
    # ignored by its git), under the house -- it declares its own machine, it borrows nothing
    clone = ws / "work" / "target" / INSTANCE
    shutil.copytree(neighbour, clone, ignore=lambda here, names: [one for one in names
                                                                   if one in ("engine", "vendor", "state")])
    beneath = ws / "work" / "target" / "agents" / "z" / INSTANCE
    (beneath / ".sys").mkdir(parents=True)
    (beneath / ".sys" / "instance.yaml").write_text("slug: z\n", encoding="utf-8")
    cloned = {path: path.read_bytes() for path in sorted(clone.parent.rglob("*")) if path.is_file()}
    descended = instance.borrowers(house)
    if clone not in descended and beneath not in descended and deep_meta in descended:
        held("a clone is no borrower", "work/target/.pp declares its source and its packages: the "
             "descent passes it by, and what lies beneath it belongs to it")
    else:
        failures.append(f"  ✗ clone as a borrower         {[str(one) for one in descended]}")

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
            and instance.pins(own) == own_pins and not (hidden / ".sys" / "tools.md").exists()
            and {path: path.read_bytes() for path in sorted(clone.parent.rglob("*")) if path.is_file()} == cloned):
        held("the machine's upgrade descends", f"kit {was} -> {target}; agents/a named, its run renewed, "
             "recompiled at the new version; sub/own (its own machine), .hidden and the clone left alone")
    else:
        failures.append(f"  ✗ the descent                 rc={moved.returncode} {moved.stdout[-300:]!r} "
                        f"{moved.stderr[-300:]!r} slots={persistence.slots(agent)} compiled={compiled}")
    return len(failures)
