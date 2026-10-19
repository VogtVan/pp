"""Behaviour: REPRODUCTION -- seeding an instance, and keeping its packages materialized.

The mechanism carries its own reproduction: no external generator writes an instance.
`install` seeds one in two layers -- the engine's own template (`template/instance/`:
SETTINGS, FORMATS, the shelf of procs), then the BASE's `user/` layer (the kit's
MEMBER.md), then one package's `user/` at most; `sync` (re)materializes the pinned
packages under `vendor/` -- an instance carries EVERYTHING it runs on, the engine
included: cloned alone, backed up, restored, its procedural layer travels with it.
"""
from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path

from . import compiling, contributions, topology
from ..state import instance
from ..state.settings import SEEDS   # noqa: F401 -- the system's defaults are settings data; install seeds them
from ..core import language
from ..core.errors import Refusal
from ..core.model import Member

USER = "user"                # a package's OPERATOR-SPACE files -- placed at the instance root

CONSOLE = """#!/bin/sh
# Procedural Prompting -- the conductor's console (machine file: rewritten by
# install, sync and doctor -- not yours to edit; the engine is the one voice).
here="$(cd "$(dirname "$0")" && pwd)"
exec uv run "$here/{meta}/.sys/engine/pp.py" "$@"
"""

CONSOLE_CMD = """@echo off
rem Procedural Prompting -- the conductor's console (machine file: rewritten by
rem install, sync and doctor -- not yours to edit; the engine is the one voice).
uv run "%~dp0{meta}\\.sys\\engine\\pp.py" %*
"""

BORROWED = """#!/bin/sh
# Procedural Prompting -- the conductor's console (machine file: rewritten by
# install, sync and doctor -- not yours to edit; the engine is the one voice).
here="$(cd "$(dirname "$0")" && pwd)"
exec uv run "$here/{engine}" --instance "$here/{meta}" "$@"
"""

BORROWED_CMD = """@echo off
rem Procedural Prompting -- the conductor's console (machine file: rewritten by
rem install, sync and doctor -- not yours to edit; the engine is the one voice).
uv run "%~dp0{engine}" --instance "%~dp0{meta}" %*
"""


def engine_invocation(meta: Path) -> str:
    """-> the engine a launcher of `meta`'s member runs, as the launcher spells it: by its
    path relative to the member's root -- the instance's own copy, or the machine it
    borrows -- what the adapters' permissions name as the repair path beside `./pp`."""
    machine = instance.borrowed(meta)
    if machine is None:
        return f"{meta.name}/{instance.SYS}/engine/pp.py"
    return Path(os.path.relpath(instance.engine_root(meta) / "pp.py", meta.parent)).as_posix()


def _console_texts(meta: Path) -> list[tuple[str, str, bool]]:
    """-> (name, text, executable) for the two console scripts of `meta`'s member: each
    runs the engine under the instance; an instance that borrows a machine runs the
    machine's engine by its relative path and addresses itself (`--instance`)."""
    if instance.borrowed(meta) is None:
        return [("pp", CONSOLE.format(meta=meta.name), True),
                ("pp.cmd", CONSOLE_CMD.format(meta=meta.name), False)]
    engine = engine_invocation(meta)
    return [("pp", BORROWED.format(meta=meta.name, engine=engine), True),
            ("pp.cmd", BORROWED_CMD.format(meta=meta.name, engine=engine.replace("/", "\\")), False)]


def foreign_console(root: Path, meta_name: str) -> list[str]:
    """-> console names standing at `root` that are NOT this machine's own text --
    a first install must refuse rather than clobber a stranger's file."""
    meta = root / meta_name
    return [name for name, text, _ in _console_texts(meta)
            if (root / name).is_file()
            and (root / name).read_text(encoding="utf-8") != text]


def console(meta: Path) -> list[Path]:
    """The operator's console at the member root -- MACHINE-OWNED: written at
    install, rewritten by sync and doctor (byte-stable; an edit does not survive,
    the blocks' channel repairs itself). -> the paths (re)written."""
    made = []
    for name, text, executable in _console_texts(meta):
        target = meta.parent / name
        if not target.is_file() or target.read_text(encoding="utf-8") != text:
            target.write_text(text, encoding="utf-8")
            made.append(target)
        if executable:
            target.chmod(0o755)
    return made


def user_files(root: Path) -> list[Path]:
    """-> the files a package proposes for the instance ROOT (the operator's space)."""
    home = root / USER
    return sorted(p for p in home.glob("*") if p.is_file()) if home.is_dir() else []


def _single_user_bearer(roots: list[tuple[str, Path]], base: str | None = None) -> None:
    """At most ONE requested package BESIDE the base may carry user-level files -- two
    personas fighting over MEMBER.md is a conflict to refuse upfront, nothing written.
    The base's own `user/` layer is the seat a persona replaces, never a rival."""
    bearers = [name for name, root in roots if name != base and user_files(root)]
    if len(bearers) > 1:
        raise Refusal("user-packages-conflict",
                      f"{', '.join(bearers)} all install user-level files -- "
                      "one package of this kind at a time")


def _seeded(meta: Path, source: Path, name: str) -> list[bytes]:
    """-> the bytes a root file `name` is SEEDED with: the engine's template, then the
    base's `user/` layer -- what a standing file may still equal without being edited."""
    found = []
    for path in (source / "template" / "instance" / name,
                 package_dir(source, instance.base_of(meta)) / USER / name):
        if path.is_file():
            found.append(path.read_bytes())
    return found


def _place_user(meta: Path, root: Path, source: Path, backup: bool) -> list[str]:
    """Places a package's user files at the instance root. A fresh install places the
    base's layer over the template seeds, then a package's over the base's, silently;
    later (backup=True), a PRISTINE file -- identical to the incoming copy or still a
    seed (the template's, the base's) -- is replaced silently, an EDITED one is saved
    to `<name>.old` first: the operator's work is never destroyed.
    -> the names that were backed up."""
    saved = []
    for item in user_files(root):
        target = meta / item.name
        incoming = item.read_bytes()
        if target.exists() and backup:
            standing = target.read_bytes()
            pristine = standing == incoming or standing in _seeded(meta, source, item.name)
            if not pristine:
                target.replace(target.with_name(target.name + ".old"))
                saved.append(item.name)
        target.write_bytes(incoming)
    return saved


def user_clashes(meta: Path, name: str) -> list[str]:
    """-> the EDITED operator files `add_package(name)` would back up and replace."""
    declared = instance.read(meta)
    source = Path(declared.get("source", ""))
    if not source.is_dir():
        return []
    root = package_dir(source, name)
    clashes = []
    for item in user_files(root):
        target = meta / item.name
        if not target.exists():
            continue
        standing = target.read_bytes()
        if standing != item.read_bytes() and standing not in _seeded(meta, source, item.name):
            clashes.append(item.name)
    return clashes


def wired_providers(workspace: Path) -> list[str]:
    """-> the adapters this workspace was wired with, read from their artifacts --
    what a fresh sibling install should be wired with too. A cursor-only wiring is
    told by the shared card standing WITHOUT codex's own config."""
    found = []
    if (workspace / ".claude" / "skills" / "pp").is_dir():
        found.append("claude")
    if (workspace / ".codex").is_dir():
        found.append("codex")
    if (workspace / ".gemini").is_dir() or (workspace / "gemini-pp").exists():
        found.append("gemini")
    if (workspace / ".agents" / "skills" / "pp").is_dir() and ".codex" not in [
            p.name for p in workspace.iterdir() if p.is_dir()]:
        found.append("cursor")
    return found


def _projections_path(meta: Path) -> Path:
    return meta / instance.SYS / "projections.yaml"


def _projections(meta: Path) -> dict:
    """The provenance registry: surface path -> sha256 of the last PP projection.
    Machine-owned; what lets a refresh tell a pristine projection from an
    operator's edit without ever guessing."""
    path = _projections_path(meta)
    if not path.is_file():
        return {}
    import yaml
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


def _record_projection(meta: Path, target: Path, content: str) -> None:
    import hashlib, yaml
    registry = _projections(meta)
    registry[str(target)] = hashlib.sha256(content.encode("utf-8")).hexdigest()
    path = _projections_path(meta)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(registry, sort_keys=True), encoding="utf-8")


def card(meta: Path) -> str | None:
    """-> the card a HARNESS receives from the engine of the instance `meta` (`card_of`)."""
    return card_of(instance.engine_root(meta))


def card_of(engine: Path) -> str | None:
    """-> the card a HARNESS receives from the engine rooted at `engine`: its `refs/PP.md`
    followed by the body of its `system/SYSTEM.CONDUCT.md` -- the session a harness opens on
    its own is one the LLM conducts. One composition, read by every adapter's projection, by
    the verifier and by the boot's `card-drift`; None when the engine carries no card."""
    from .. import reading
    pp, conduct = engine / "refs" / "PP.md", engine / "system" / language.SYSTEM[1]
    if not pp.is_file():
        return None
    text = pp.read_text(encoding="utf-8").rstrip("\n") + "\n"
    if conduct.is_file():
        text += "\n" + reading.body_of(conduct.read_text(encoding="utf-8")).strip() + "\n"
    return text


def project(meta: Path, target: Path, content: str) -> str | None:
    """Writes or refreshes ONE projection of the agent contract with provenance:
    absent -> written; identical -> nothing; pristine (our last projection) ->
    refreshed in place; operator-edited -> left INTACT, the current projection
    arrives beside it as `<name>.candidate` and the drift is said.
    -> the message to print, None when nothing was owed."""
    import hashlib
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        _record_projection(meta, target, content)
        return str(target)
    standing = target.read_text(encoding="utf-8")
    if standing == content:
        return None
    recorded = _projections(meta).get(str(target))
    if recorded == hashlib.sha256(standing.encode("utf-8")).hexdigest():
        target.write_text(content, encoding="utf-8")
        _record_projection(meta, target, content)
        return f"{target} refreshed (pristine projection moved to the current contract)"
    candidate = target.with_name(target.name + ".candidate")
    candidate.write_text(content, encoding="utf-8")
    return (f"{target} was edited -- left intact; the current projection sits at "
            f"{candidate.name}: merge or replace at your own hand")


def merge_codex_config(meta: Path, config: Path, escaped_marble: str,
                       fresh_content: str) -> str | None:
    """The HARDENED codex merge: PP owns exactly TWO fields of an existing
    `config.toml` -- `developer_instructions` and the `PP_MARBLE` sentinel -- and
    splices ONLY the first, byte-preserving every other key (the sentinel line is
    part of the generated shape and never moved once present). The managed field
    must be OUR last projection (or absent) to move; an operator-edited value is
    never touched in place: the fresh projection arrives as `.candidate`, said.
    -> the message, None when the config is already current."""
    import hashlib
    import tomllib
    text = config.read_text(encoding="utf-8")
    probe = 'developer_instructions = """\n' + escaped_marble + '\n"""\n'
    try:
        target_value = tomllib.loads(probe)["developer_instructions"]
        parsed = tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        candidate = config.with_name(config.name + ".candidate")
        candidate.write_text(fresh_content, encoding="utf-8")
        return (f"{config} does not parse as TOML -- left intact; a full projection "
                f"sits at {candidate.name}")
    key = str(config) + "#developer_instructions"
    current = parsed.get("developer_instructions")
    if current == target_value:
        _record_projection(meta, Path(key), target_value)
        return None
    recorded = _projections(meta).get(key)
    ours = (recorded == hashlib.sha256(str(current).encode("utf-8")).hexdigest()
            if current is not None else True)
    import re as _re
    block = _re.compile(r'developer_instructions = """\n.*?\n"""\n', _re.DOTALL)
    spliced = None
    if current is None:
        spliced = probe + ("" if text.startswith("\n") else "\n") + text
    elif ours and block.search(text):
        spliced = block.sub(lambda _: probe, text, count=1)
    if spliced is not None:
        try:
            after = tomllib.loads(spliced)
        except tomllib.TOMLDecodeError:
            after = None
        foreign = {k: v for k, v in parsed.items() if k != "developer_instructions"}
        kept = ({k: v for k, v in after.items() if k != "developer_instructions"}
                if after is not None else None)
        if after is not None and kept == foreign \
                and after.get("developer_instructions") == target_value:
            config.write_text(spliced, encoding="utf-8")
            _record_projection(meta, Path(key), target_value)
            return (f"{config} refreshed -- developer_instructions moved to the "
                    "current contract, every other key byte-preserved")
    candidate = config.with_name(config.name + ".candidate")
    candidate.write_text(fresh_content, encoding="utf-8")
    return (f"{config} carries an edited or unrecognized developer_instructions -- "
            f"left intact; the current projection sits at {candidate.name}")


def refresh_projections(workspace: Path, meta: Path, source: Path) -> list[str]:
    """Re-runs every wired adapter over the workspace -- their artifacts now
    carry provenance, so a pristine projection follows the current contract and
    an edited one is preserved and diagnosed. -> what was done, one per line."""
    from . import contributions
    told = []
    for name in wired_providers(workspace):
        wire_path = source / "adapters" / name / "wire.py"
        if not wire_path.is_file():
            continue
        module = contributions.module_at(wire_path)
        told += [str(done) for done in module.wire(workspace.resolve(), meta)]
    return told


def product_root(script: Path) -> Path:
    """-> the product checkout an engine belongs to (`<product>/engine/pp.py`)."""
    return script.resolve().parent.parent


def package_dir(source: Path, name: str) -> Path:
    """-> where `name` lives in the product: a base under bases/ (the kit), a
    package under packages/ -- nothing at the root."""
    for candidate in (source / "bases" / name, source / "packages" / name):
        if (candidate / instance.PACKAGE_MANIFEST).is_file():
            return candidate
    raise Refusal("package-unknown", f"`{name}` -- no such package under {source}")


def closure(source: Path, names: list[str]) -> dict[str, str]:
    """-> the pins of `names` CLOSED over `requires` at the source: each requested
    package, then every prerequisite it pulls, at the version the source holds --
    the requested order first, the pulled ones after, in discovery order. A name
    the source lacks refuses `package-unknown`, a loop `package-cycle`, before any
    caller writes."""
    pins: dict[str, str] = {}
    walking: list[str] = []

    def pull(name: str) -> None:
        if name in pins:
            return
        if name in walking:
            raise Refusal("package-cycle",
                          f"`{name}` -- the requires loop: {' -> '.join(walking + [name])}")
        manifest = instance.manifest_of(package_dir(source, name))   # package-unknown here
        walking.append(name)
        for one in manifest.get("requires") or []:
            pull(str(one))
        walking.pop()
        pins[name] = str(manifest["version"])

    for name in names:
        pull(name)
    return {name: pins[name] for name in names if name in pins} | pins


def pulled(before: dict[str, str], after: dict[str, str]) -> list[str]:
    """-> the packages a closure ADDED beyond what was asked -- what the call says."""
    return [name for name in after if name not in before]


def target_roots(source: Path, pins: dict[str, str]) -> list[Path]:
    """-> the package roots of a composition READ AT THE SOURCE, in the requires
    topology -- what a call validates before the instance moves: the contract
    and the closure judged on the target, nothing written yet."""
    return instance.ordered({name: package_dir(source, name) for name in pins})


def install(script: Path, target: Path, packages: list[str], slug: str | None = None,
            doors: bool = True, base: str | None = None, borrow: bool = False) -> Path:
    """Seeds an instance at `target`: template, engine (a member carries everything),
    the pinned packages, their seeds, and the compiled catalog. Never overwrites.
    `base` names the package the instance STANDS on: given, the composition is
    `[base] + packages`, the target is judged with it (its contract: BOOT.md, TURN.md,
    a system fragment) and the manifest says `base:`; left out, the role's default
    (`language.BASE`) composes and the manifest stays as it always was. `borrow` seeds
    an instance that BORROWS the machine above `target` instead of carrying one
    (`_borrowing`): `packages` and `base` are then the machine's.

    `slug` is this member's identity -- kit's own, not a package's: given, it must be
    strict kebab-case; left out, it defaults to the workspace directory's name, kebabed."""
    source = product_root(script)
    meta = target.resolve()
    if instance.is_instance(meta):
        raise Refusal("instance-exists", f"{meta} already carries {instance.MANIFEST}")
    if slug is not None and not instance.valid_slug(slug):
        raise Refusal("slug-invalid",
                      f"`{slug}` -- a slug is lowercase, digits and single dashes only")
    taken = foreign_console(meta.parent, meta.name)
    if taken:
        raise Refusal("pp-name-taken",
                      f"{', '.join(taken)} already exist(s) at {meta.parent} and is not "
                      "the conductor's console -- move yours aside, nothing was written")
    if borrow:
        return _borrowing(meta, slug, doors)
    resolved_slug = slug or instance.kebab(meta.parent.name)
    standing = base or language.BASE
    wanted = [standing] + [name for name in packages if name != standing]
    pins = closure(source, wanted)                 # the prerequisites come with the install
    _single_user_bearer([(name, package_dir(source, name)) for name in pins], base=standing)
    topology.validate(meta, target_roots(source, pins),   # the target judged first --
                      template=source / "template" / "instance",   # its seeds its own,
                      base=standing)                              # its base said, not read
    meta.mkdir(parents=True, exist_ok=True)
    for item in sorted((source / "template" / "instance").iterdir()):
        _copy(item, meta / item.name, overwrite=False)
    (meta / "procs").mkdir(exist_ok=True)          # the user's own space
    from datetime import datetime, timezone
    declared = {"source": str(source), "slug": resolved_slug,
                "engine": source_version(source),
                "installed": datetime.now(timezone.utc).date().isoformat()}
    if base is not None:
        declared["base"] = base      # said only when named: a manifest of yesterday keeps its bytes
    declared["packages"] = pins
    instance.write(meta, declared)   # `installed:` -- the instance's birth date, on record
    _refresh(meta, source, pins)
    _seed(meta, source, pins)
    for name in [standing] + [one for one in pins if one != standing]:   # the BASE's user
        _place_user(meta, package_dir(source, name), source, backup=False)   # layer first,
        # over the template seeds; then the one package's, over the base's
    sync_settings(meta, source)   # the seeded SETTINGS composes with the packages'
                                  # fragments -- their groups and sections from day one
    if doors:
        _doors(meta)
    member_doc = meta / "MEMBER.md"
    if member_doc.is_file():
        declared = instance.read(meta)
        declared["member_seed"] = hashlib.sha256(member_doc.read_bytes()).hexdigest()
        instance.write(meta, declared)   # the seeded member's fingerprint -- bare detection
    console(meta)
    compiling.build_tools(meta)
    compiling.render_registry(meta)   # validates; writes nothing
    compiling.build_system(meta)
    return meta


def _source_of(machine: Path) -> Path:
    """-> the product checkout a machine was installed from -- `source-missing` when gone."""
    source = Path(instance.read(machine).get("source", ""))
    if not source.is_dir():
        raise Refusal("source-missing",
                      f"{machine / instance.MANIFEST} points at `{source}` -- not a directory")
    return source


def _borrowing(meta: Path, slug: str | None, doors: bool) -> Path:
    """Seeds at `meta` an instance that BORROWS the machine above it: the root seeded, a
    manifest that says who it is and nothing of a machine (its versions and its
    composition are the machine's, read there at every call), its records seeded, its
    SETTINGS composed, its console, its marble and catalog compiled -- no engine, no
    vendor. No machine above refuses `machine-missing` before anything is written."""
    machine = instance.machine_of(meta)
    source = _source_of(machine)
    meta.mkdir(parents=True, exist_ok=True)
    for item in sorted((source / "template" / "instance").iterdir()):
        _copy(item, meta / item.name, overwrite=False)
    (meta / "procs").mkdir(exist_ok=True)
    from datetime import datetime, timezone
    instance.write(meta, {"slug": slug or instance.kebab(meta.parent.name),
                          "installed": datetime.now(timezone.utc).date().isoformat()})
    pins = instance.pins(meta)
    standing = instance.base_of(meta)
    _seed(meta, source, pins)
    for name in [standing] + [one for one in pins if one != standing]:
        _place_user(meta, package_dir(source, name), source, backup=False)
    sync_settings(meta, source)
    if doors:
        _doors(meta)
    member_doc = meta / "MEMBER.md"
    if member_doc.is_file():
        declared = instance.read(meta)
        declared["member_seed"] = hashlib.sha256(member_doc.read_bytes()).hexdigest()
        instance.write(meta, declared)
    console(meta)
    compiling.build_tools(meta)
    compiling.render_registry(meta)   # validates; writes nothing
    compiling.build_system(meta)
    return meta


# ONE door for every harness (plan fixes1): the first call, and nothing to invoke before it --
# the standing orders the call serves carry the card; a skill or a command the harness
# registers stays the principal's own, never a second copy the agent reads first
DOOR = ("This workspace is conducted. Run now:\n"
        "```{shell}\n"
        "{console} -new\n"
        "```\n"
        "Then follow what it prints: the conductor's output names the next call.\n")
DOORS = {"CLAUDE.md": DOOR, "AGENTS.md": DOOR, "GEMINI.md": DOOR}


def door_call() -> tuple[str, str]:
    """-> the shell the door's block names, and the console call as THIS machine
    spells it (`.\\pp` under Windows). Both launchers are written at every install;
    the door is read where it was installed, so it names ONE call -- an agent reads
    the line that runs here, never a choice between two."""
    if os.name == "nt":
        return "powershell", ".\\pp"
    return "bash", "./pp"


def door(root: Path, name: str) -> Path | None:
    """ONE integration door at the member root, pointing that harness at the
    conductor. Written once, never overwritten -- the member's own file the moment
    it exists. -> the path when written, None when it already stood."""
    path = root / name
    if path.exists():
        return None
    shell, call = door_call()
    path.write_text(DOORS[name].format(shell=shell, console=call), encoding="utf-8")
    return path


def _doors(meta: Path) -> None:
    """The GENERIC doors of a bare install (no adapter flag): the two cross-vendor
    standards -- a flagged install lets each adapter write its own instead."""
    for name in ("CLAUDE.md", "AGENTS.md"):
        door(meta.parent, name)


def source_version(source: Path) -> str:
    """-> the VERSION the source checkout declares -- read off its file, never
    imported: the running engine may be an older vendored copy."""
    leaf = source / "engine" / "conductor" / "core" / "version.py"
    if leaf.is_file():
        for line in leaf.read_text(encoding="utf-8").splitlines():
            if line.startswith("VERSION"):
                return line.split('"')[1]
    return "unversioned"


def _delegate(meta: Path, copied: str, *verb: str) -> None:
    """The RELAY: the tail of a lifecycle call (seed, compile, projections) runs
    in the engine just COPIED, never in the module still loaded here -- the
    artifacts of pin N+1 are compiled by the code N+1. The old process copies,
    then hands over; a child that cannot finish refuses aloud."""
    import subprocess
    engine = instance.engine_root(meta) / "pp.py"
    child = subprocess.run(["uv", "run", str(engine), "--instance", str(meta), *verb],
                           capture_output=True, text=True)
    print(child.stdout, end="")
    if child.returncode != 0:
        detail = child.stderr.strip().splitlines()[-1] if child.stderr.strip() else "no detail"
        raise Refusal("delegation-failed",
                      f"the copied engine ({copied}) could not finish "
                      f"`{' '.join(verb)}` -- {detail}")


def _judged(meta: Path) -> None:
    """The composition judged BEFORE a maintenance verb writes or forgets anything --
    when every pinned bundle stands. A bare vendor (the repair from outside) has
    nothing to judge yet: its builds judge it once the bundles are back.

    documentary: a refusal that follows a write lies when it says nothing played;
    judging first is what keeps the runs, the console and the vendor where they
    were (le-sync-juge-avant-d-oublier)."""
    try:
        instance.vendored(meta, switched=False)      # every bundle stands, wherever it lives
    except Refusal as refusal:
        if refusal.code == "package-missing":
            return
        raise
    topology.validate(meta)


def sync(member: Member) -> list[Path]:
    """(Re)materializes the member's packages and engine at their pins -- idempotent,
    and at CONSTANT pins the standing runs stand: a run binds to bundle versions, and
    none moved (`upgrade` is the verb that voids them). A copied engine NEWER than the
    running one takes the tail over (`_delegate`). An instance that BORROWS a machine
    has nothing to materialize: its sync is its state's work alone (`_restate`)."""
    meta = member.meta
    machine = instance.borrowed(meta)
    if machine is not None:
        return _restate(member, machine)
    declared = instance.read(meta)
    source = Path(declared.get("source", ""))
    if not source.is_dir():
        raise Refusal("source-missing",
                      f"{meta / instance.MANIFEST} points at `{source}` -- not a directory")
    standing = instance.pins(meta)
    closed = closure(source, list(standing))     # a repair closes the pins too --
    pins = {one: standing.get(one, closed[one]) for one in closed}   # at CONSTANT versions
    if not pulled(standing, pins):
        _judged(meta)        # the closure already closed: judged before anything is written
    if pulled(standing, pins):
        declared["packages"] = pins              # the prerequisite a hand edit dropped
        instance.write(meta, declared)           # comes back with its bundle
    made = _refresh(meta, source, pins)
    if declared.get("engine") != source_version(source):
        declared["engine"] = source_version(source)     # the record follows the copy
        instance.write(meta, declared)
    from ..core.version import VERSION
    if source_version(source) != VERSION:
        _delegate(meta, source_version(source), "-sync", str(meta))
        return made
    _seed(meta, source, pins)
    console(meta)
    compiling.build_tools(meta)
    compiling.render_registry(meta)   # validates; writes nothing
    compiling.build_system(meta)
    for done in refresh_projections(member.path, meta, source):
        print(f"pp: {done}")
    return made


def _restate(member: Member, machine: Path) -> list[Path]:
    """The STATE's work of an instance that borrows `machine`, at the machine's versions:
    its SETTINGS composed, its records seeded, its console, its catalog and marble
    compiled -- the machine never written. A machine whose engine is newer than the
    running one takes it over (`_delegate`)."""
    meta = member.meta
    source = _source_of(machine)
    from ..core.version import VERSION
    if source_version(source) != VERSION:
        _delegate(meta, source_version(source), "-sync", str(meta))
        return []
    sync_settings(meta, source)
    _seed(meta, source, instance.pins(meta))
    console(meta)
    compiling.build_tools(meta)
    compiling.render_registry(meta)   # validates; writes nothing
    compiling.build_system(meta)
    return []


def _owned(meta: Path, verb: str) -> None:
    """A verb of the MACHINE played in an instance that borrows one refuses
    `machine-borrowed`, naming the machine where it plays."""
    machine = instance.borrowed(meta)
    if machine is not None:
        raise Refusal("machine-borrowed",
                      f"{meta} borrows the machine of {machine} -- `{verb}` plays there "
                      f"(`{machine.parent / 'pp'} {verb}`), and reaches this instance from there")


def _named(meta: Path, borrower: Path) -> str:
    """-> a borrowing instance said from its machine: its workspace relative to the machine's."""
    return borrower.parent.relative_to(meta.parent).as_posix()


def _restated(meta: Path, borrowers: list[Path]) -> list[str]:
    """The state's work of every instance that borrows `meta`'s machine. -> one line each."""
    from ..state import discovery
    told = []
    for one in borrowers:
        sync(discovery.member_at(one))
        told.append(f"{_named(meta, one)} restated")
    return told


def upgrade(member: Member) -> list[str]:
    """Moves every pin to the version the source holds NOW, then re-materializes
    (standing runs are RENEWED -- a run's state binds to bundle versions, its key does not:
    the slot becomes a renewal mark, and the next call on the key reopens the run under
    it). -> the moves, told
    one per line; [] when already current, and then NOTHING was touched. The verb
    plays under the machine's maintenance lock held EXCLUSIVE (`lock.maintaining`,
    taken by the console before anything is read): no pp process lives under the
    machine meanwhile -- no call, no opening, no launcher -- so no run lock is taken.
    Played at a MACHINE, the verb DESCENDS: every instance that borrows it
    (`instance.borrowers`) gets its state's work, and the runs of the machine and of
    every borrower are renewed, the files of their own but the slot gone; the files of a
    run already gone are swept."""
    meta = member.meta
    _owned(meta, "upgrade")
    borrowers = instance.borrowers(meta)
    declared = instance.read(meta)
    source = Path(declared.get("source", ""))
    if not source.is_dir():
        raise Refusal("source-missing",
                      f"{meta / instance.MANIFEST} points at `{source}` -- not a directory")
    return _moved(member, declared, source, borrowers)


def _moved(member: Member, declared: dict, source: Path, borrowers: list[Path]) -> list[str]:
    """The upgrade proper: the moves computed, then the machine rewritten, the borrowers'
    state worked, and every run of the machine and its borrowers renewed -- its slot a
    renewal mark (`persistence.renew`), `renewed` in its trace; a reservation no opening
    took is dropped."""
    meta = member.meta
    from datetime import datetime, timezone
    from ..state import log, persistence
    pins = instance.pins(meta)
    held = closure(source, list(pins))           # the versions the source holds, CLOSED:
    topology.validate(meta, target_roots(source, held))   # a new version may require
    moves = [(name, pins[name], held[name]) for name in pins if pins[name] != held[name]]
    added = pulled(pins, held)                   # a package that was not pinned yet
    recorded, at_source = declared.get("engine", "unversioned"), source_version(source)
    if recorded != at_source:
        moves.append(("engine", recorded, at_source))    # the engine is a component too
    if not moves and not added:
        return []
    standing = [slot for one in [meta] + borrowers for slot in persistence.slots(one)]
    for one in added:                            # the bundles first, the manifest after
        _materialize(meta, source, one, held[one])
    declared["packages"] = held
    instance.write(meta, declared)
    sync(member)
    restated = _restated(meta, borrowers)
    moved_from = {name: old for name, old, _ in moves}
    moved_to = {name: new for name, _, new in moves}
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    renewed = 0
    for slot in standing:            # a saved run binds to bundle VERSIONS: across an update its
        if persistence.reserved(slot):           # state is void, its KEY is not -- the slot
            persistence.dropped(slot)            # becomes a renewal mark; a reservation no
            continue                             # opening took holds no run
        try:
            persistence.renew(slot, moved_from, moved_to, at)
        except (OSError, ValueError):
            persistence.dropped(slot)            # a slot no reader can parse holds no run either
            continue
        trace = persistence.trace_of(slot)
        if trace:                                # the update that renews a run says so IN its trace
            log.record(slot.parent / trace, "renewed", **{"from": moved_from, "to": moved_to})
        renewed += 1
    for one in [meta] + borrowers:
        _swept(one)
    told = [f"{name} {old} -> {new}" for name, old, new in moves]
    told += [f"{name} pinned at {held[name]} (required)" for name in added]
    told += sync_settings(meta, source)
    from . import events             # the bus's record follows the families' names: a
    told += [f"bus: {line}" for line in events.migrate_families(meta)]   # latched vector
                                     # crosses a rename by the tail of its qualified family
    told += restated
    if renewed:
        told.append(f"{renewed} run(s) renewed by the update -- each reopens under its key "
                    "at its next call")
    return told


def _unlinked(path: Path) -> None:
    """Removes a file of a run gone -- kept where the platform refuses to remove an open
    file (Windows): a free lock file is held by nobody."""
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass


def _swept(meta: Path) -> None:
    """Removes the files of the runs that are gone -- a launcher killed before `-new`, a
    slot forgotten by hand: every `session-<key>.*` whose slot stands no more (the traces
    stay: the history of a run outlives it). Played under the exclusive, where no process
    holds one."""
    from ..state import persistence
    state = meta / persistence.DIRECTORY
    if not state.is_dir():
        return
    for path in sorted(state.glob("session-*.*")):
        key = path.name.removeprefix("session-").split(".", 1)[0]
        if path.suffix == ".jsonl" or persistence.slot_of(meta, key).exists():
            continue
        _unlinked(path)


SEPARATOR = "# ---- {name} ----"   # the composer's own group marks in the front matter


def sync_settings(meta: Path, source: Path | None = None) -> list[str]:
    """The operator's SETTINGS follows the engine at every upgrade and doctor:
    the file is COMPOSED -- the engine's fragment (the install template) then
    every vendored package's fragment in the REQUIRES topology, each a group
    of keys in the front matter (marked `# ---- <package> ----`) and a named
    SECTION of the body (Engine, Kit, Plan…) -- and keeps the OPERATOR'S
    VALUES: a known key at the operator's value (a missing one arrives at the
    default it silently played, an EMPTY one fills the same way), a RETIRED
    key migrates along its chain of successors (engine's and fragments') and
    stays as a commented RECEIPT at the tail beside every comment the operator
    wrote, a key no fragment owns travels under `# ---- unowned ----` (a
    package unpinned loses nothing), `cap.<sector>` travels with the engine. The
    documentation is the product's, the values alone are the operator's.
    Idempotent. Without a source template the front matter migrates in
    place and the body stands. -> the moves, one line each."""
    from ..state import settings as tuning
    path = meta / "SETTINGS.md"
    if not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return []
    end = next((i for i, l in enumerate(lines[1:], 1) if l.strip() == "---"), None)
    if end is None:
        return []
    found = tuning.fragments(meta)
    told: list[str] = []
    values: dict[str, str] = {}          # the operator's keys, raw values, in order
    comments: list[str] = []             # every comment line -- receipts included
    skeleton = ("name", "kind", "description")
    import re
    mark = re.compile(r"^# ---- [a-z0-9_-]+ ----$")   # the composer's own marks, any
    i = 1                                             # package's -- a gone one's too
    while i < end:
        line = lines[i]
        bare = line.strip()
        if bare.startswith("#"):
            if not mark.match(bare):     # the composer's marks regenerate, never travel
                comments.append(line if line.endswith("\n") else line + "\n")
            i += 1
            continue
        key = line.split(":", 1)[0].strip() if ":" in line and line[:1] not in (" ", "\t") else ""
        if not key:
            i += 1
            continue
        value = line.split(":", 1)[1].strip()
        if key in skeleton:
            i += 1
            while i < end and lines[i][:1] in (" ", "\t"):
                i += 1
            continue
        seeded = dict(SEEDS).get(key, "") or _fragment_default(found, key)
        if not value and seeded:
            value = seeded
            told.append(f"SETTINGS: `{key}: {seeded}` filled (was empty)")
        values[key] = value
        i += 1
    for key, default in SEEDS:
        if key not in values:
            values[key] = default
            told.append(f"SETTINGS: `{key}` added ({default})")
    for one in found:
        for key, default in one.defaults:
            if key not in values:
                values[key] = default
                told.append(f"SETTINGS: `{key}` added ({default}, {one.name})")
    # the package SWITCHES: one `package.<name>` per pin beyond the base, seeded `on`,
    # the operator's value kept, the key of an unpinned package dropped (off is not gone,
    # gone is gone) -- the engine's family, no fragment owns it
    switches = [f"package.{name}" for name in instance.pins(meta) if name != instance.base_of(meta)]
    for key in switches:
        if key not in values:
            values[key] = "on"
            told.append(f"SETTINGS: `{key}` added (on)")
    for key in [one for one in values if one.startswith(instance.SWITCH_KEY) and one not in switches]:
        del values[key]
        told.append(f"SETTINGS: `{key}` dropped (unpinned)")
    template = (source / "template" / "instance" / "SETTINGS.md") if source else None
    if template is not None and template.is_file():
        shaped = template.read_text(encoding="utf-8").splitlines(keepends=True)
        shaped_end = next((i for i, l in enumerate(shaped[1:], 1) if l.strip() == "---"), None)
    else:
        shaped, shaped_end = None, None
    if shaped is None or shaped_end is None:
        fresh = [f"{key}: {value}\n" for key, value in values.items()]
        rebuilt = [lines[0]] + fresh + comments + lines[end:]
    else:
        fresh = []
        placed = set()
        j = 1
        while j < shaped_end:
            line = shaped[j]
            key = line.split(":", 1)[0].strip() if ":" in line and line[:1] not in (" ", "\t", "#") else ""
            if key and key not in skeleton:
                fresh.append(f"{key}: {values.get(key, line.split(':', 1)[1].strip())}\n")
                if key not in values:
                    told.append(f"SETTINGS: `{key}` added (template)")
                placed.add(key)
            else:
                fresh.append(line)         # name, kind, description -- the template's
            j += 1
        for key, value in values.items():
            if key.startswith(("cap.", "material.")) and key not in placed:
                fresh.append(f"{key}: {value}\n")    # a sector cap travels with the engine
                placed.add(key)
        if switches:
            fresh.append(SEPARATOR.format(name="packages") + "\n")
            for key in switches:
                fresh.append(f"{key}: {values[key]}\n")
                placed.add(key)
        for one in found:
            fresh.append(SEPARATOR.format(name=one.name) + "\n")
            for key, _ in one.defaults:
                fresh.append(f"{key}: {values[key]}\n")
                placed.add(key)
        strangers = [key for key in values if key not in placed]
        if strangers:
            fresh.append(SEPARATOR.format(name="unowned") + "\n")
            for key in strangers:
                fresh.append(f"{key}: {values[key]}\n")
        body = shaped[shaped_end:]
        for one in found:
            body = body + ["\n"] + one.body.splitlines(keepends=True)
            if not one.body.endswith("\n"):
                body.append("\n")
        rebuilt = [shaped[0]] + fresh + comments + body
        if "".join(lines[end:]) != "".join(body):
            told.append("SETTINGS: body composed from the fragments")
    if "".join(rebuilt) == "".join(lines):
        return []
    if not told:
        told.append("SETTINGS: shaped as the template (keys ordered by section)")
    temporary = path.with_suffix(".tmp")
    temporary.write_text("".join(rebuilt), encoding="utf-8")
    import os
    os.replace(temporary, path)
    return told


def _fragment_default(found, key: str) -> str:
    for one in found:
        for name, default in one.defaults:
            if name == key:
                return default
    return ""


def doctor(member: Member) -> list[str]:
    """The operator's repair, at CONSTANT pins: re-materializes bundles and engine,
    re-seeds, recompiles, rewrites the console -- and says what it did. A copied
    engine NEWER than the running one takes the repair over (`_delegate`); the
    pass closes on the VERIFIER: every receipt and card, checked and named.
    Standing runs stand: same versions, same contract (`upgrade` is the void). Played
    at a MACHINE, the repair DESCENDS: every instance that borrows it gets its state's
    work, at the same versions."""
    meta = member.meta
    _owned(meta, "doctor")
    declared = instance.read(meta)
    source = Path(declared.get("source", ""))
    if not source.is_dir():
        raise Refusal("source-missing",
                      f"{meta / instance.MANIFEST} points at `{source}` -- not a directory")
    _judged(meta)
    pins = instance.pins(meta)
    current = {name: version for name, version in pins.items()
               if instance.manifest_of(package_dir(source, name))["version"] == version}
    outrun = {name: version for name, version in pins.items() if name not in current}
    made: list = [_materialize(meta, source, name, version) for name, version in current.items()]
    made += sync_settings(meta, source)   # the OLD engine runs an upgrade, so the
                                  # settings sync arrives one upgrade late by construction
                                  # -- doctor, running the NEW engine, heals in place
    copied = _engine_copy(meta, source)
    if copied is not None:
        made.append(copied)
    if declared.get("engine") != source_version(source):
        declared["engine"] = source_version(source)     # the record names the copy
        instance.write(meta, declared)
    from ..core.version import VERSION
    if source_version(source) != VERSION:
        _delegate(meta, source_version(source), "doctor")
        return [f"repair delegated to the copied engine ({source_version(source)})"]
    vendor = meta / instance.VENDOR
    if vendor.is_dir():        # an OUTRUN bundle is kept, never swept: it is the
        keep = {f"{name}@{version}" for name, version in pins.items()}   # instance's copy
        for stale in vendor.iterdir():
            if stale.name not in keep:
                shutil.rmtree(stale)
    _seed(meta, source, current)
    made += console(meta)
    compiling.render_registry(meta)   # validates; writes nothing
    made += [built for built in (compiling.build_tools(meta),
                                 compiling.build_system(meta)) if built]
    told = [f"{one} rewritten" for one in made]
    told += refresh_projections(member.path, meta, source)
    for name, version in outrun.items():
        held = instance.manifest_of(package_dir(source, name))["version"]
        told.append(f"{name}@{version} kept as vendored -- the source holds {held}; "
                    "`upgrade` moves you there")
    told += verify(member)
    told += _restated(meta, instance.borrowers(meta))
    return told


def verify(member: Member) -> list[str]:
    """The invariants of the standing instance, checked and NAMED -- the doctor's
    closing statement: build receipts against the running engine and inputs, wired
    cards against the current contract. Statements, not repairs: a wrong one names
    what rights it."""
    meta = member.meta
    from ..core.version import VERSION
    held = compiling.receipts(meta)
    inputs = compiling.receipt_inputs(meta)
    told = []
    for name in (*compiling.MARBLES.values(), "tools.md"):
        if not (meta / instance.SYS / name).is_file():
            continue
        receipt = held.get(name) or {}
        if receipt.get("engine") != VERSION:
            told.append(f"receipt {name}: STALE -- compiled by "
                        f"{receipt.get('engine') or 'an engine that left no receipt'}")
        elif name in compiling.MARBLES.values() and receipt.get("inputs") != inputs:
            told.append(f"receipt {name}: STALE -- the vendor inputs moved since the compile")
        elif name == "tools.md" and receipt.get("catalog") != compiling.catalog_inputs(meta):
            told.append(f"receipt {name}: STALE -- the catalog inputs moved since the compile")
        else:
            told.append(f"receipt {name}: current ({VERSION})")
    contract = card(meta)    # the card a harness receives, as every projection writes it
    if contract is not None:
        for wired in (member.path / ".claude" / "skills" / "pp" / "SKILL.md",
                      member.path / ".agents" / "skills" / "pp" / "SKILL.md"):
            if wired.is_file():
                state = ("current" if wired.read_text(encoding="utf-8") == contract
                         else "DRIFTED -- edited or old; the fresh projection is written "
                              "(or is owed) as its `.candidate`")
                told.append(f"card {wired.relative_to(member.path)}: {state}")
    return told


def remove_package(member: Member, name: str) -> list[str]:
    """Retires ONE package from an ALREADY-SEEDED instance -- the inverse of `add`,
    the same transaction read backwards: the target composition is judged first
    (nothing pinned may still require it, the contract must still hold), then
    the manifest lets it go, then its bundle leaves; the records stay -- they are
    the instance's data -- and the package's settings keys carry on as `unowned`
    in the recomposed SETTINGS, so a later `add` finds the operator's values. Played at
    a machine, every instance that borrows it gets its state's work.
    -> what was done, told one per line."""
    meta = member.meta
    _owned(meta, "remove")
    declared = instance.read(meta)
    source = Path(declared.get("source", ""))
    if not source.is_dir():
        raise Refusal("source-missing",
                      f"{meta / instance.MANIFEST} points at `{source}` -- not a directory")
    pins = instance.pins(meta)
    if name == instance.base_of(meta):
        raise Refusal("package-base", f"`{name}` is the base of this instance -- never removed")
    if name not in pins:
        raise Refusal("package-unpinned", f"`{name}` is not pinned here -- nothing to remove")
    dependents = []
    roots = {root.name.split("@")[0]: root for root in instance.vendored(meta, switched=False)}
    for other, version in pins.items():
        if other == name:
            continue
        try:
            requires = instance.manifest_of(roots[other]).get("requires") or []
        except (Refusal, KeyError):
            requires = []
        if name in requires:
            dependents.append(other)
    if dependents:
        raise Refusal("package-required-by",
                      f"`{name}` is required by {', '.join(f'`{one}`' for one in dependents)} -- "
                      "remove them first, one by one")
    target = {one: version for one, version in pins.items() if one != name}
    topology.validate(meta, target_roots(source, target))   # the contract still holds
    declared["packages"] = target
    instance.write(meta, declared)               # the manifest FIRST: the pin lets go...
    root = meta / instance.VENDOR / f"{name}@{pins[name]}"
    shutil.rmtree(root, ignore_errors=True)      # ...then the bundle leaves
    told = [f"{name}@{pins[name]} removed -- the records stay, the keys remain as unowned"]
    told += sync_settings(meta, source)
    console(meta)
    compiling.build_tools(meta)
    compiling.render_registry(meta)   # validates; writes nothing
    compiling.build_system(meta)
    for done in refresh_projections(member.path, meta, source):
        told.append(done)
    told += _restated(meta, instance.borrowers(meta))
    return told


def add_package(member: Member, name: str) -> Path:
    """Adds `name` to an ALREADY-SEEDED instance -- `install` without recreating it.
    Pins it, materializes its bundle, seeds it, recompiles the catalog. Played at a
    machine, every instance that borrows it gets its state's work."""
    meta = member.meta
    _owned(meta, "add")
    declared = instance.read(meta)
    source = Path(declared.get("source", ""))
    if not source.is_dir():
        raise Refusal("source-missing",
                      f"{meta / instance.MANIFEST} points at `{source}` -- not a directory")
    pins = instance.pins(meta)
    if name in pins:
        raise Refusal("package-installed", f"`{name}` is already pinned at {pins[name]}")
    closed = closure(source, list(pins) + [name])          # closed: the prerequisites too
    target = {one: pins.get(one, closed[one]) for one in closed}   # a standing pin keeps its version
    topology.validate(meta, target_roots(source, target))  # judged at the source first
    fresh = {one: target[one] for one in pulled(pins, target)}  # what this call pins
    made = meta
    posed: list[Path] = []
    try:
        for one, version in fresh.items():      # the bundles arrive BEFORE the manifest
            stood = (instance.bundle_home(meta) / f"{one}@{version}").is_dir()
            made_at = _materialize(meta, source, one, version)
            if not stood:
                posed.append(made_at)          # a version already standing stays
    except Refusal:
        for root in posed:                       # a refusal leaves the instance as it was
            shutil.rmtree(root, ignore_errors=True)
        raise
    declared["packages"] = target
    instance.write(meta, declared)               # the manifest, written LAST
    _seed(meta, source, fresh)
    for one in fresh:
        for saved in _place_user(meta, package_dir(source, one), source, backup=True):
            print(f"pp: {saved} replaced -- your previous file is at {saved}.old")
    extra = [one for one in fresh if one != name]
    if extra:
        print(f"pp: add {name} -- pins {', '.join(extra)} (required)")
    for done in sync_settings(meta, source):     # the package's keys enter the SETTINGS --
        print(f"pp: {done}")                     # an unowned value of theirs comes home
    made = instance.bundle_home(meta) / f"{name}@{target[name]}"   # where it now lives
    console(meta)
    compiling.build_tools(meta)
    compiling.render_registry(meta)   # validates; writes nothing
    compiling.build_system(meta)
    for done in refresh_projections(member.path, meta, source):
        print(f"pp: {done}")
    for done in _restated(meta, instance.borrowers(meta)):
        print(f"pp: {done}")
    return made


def _materialize(meta: Path, source: Path, name: str, version: str) -> Path:
    """Copies `name`'s bundle at its pinned `version` under `meta`'s vendor -- the one
    package-materializing call install, `add`, `sync`, `upgrade` and `doctor` share,
    copied again at every call."""
    root = package_dir(source, name)
    held = instance.manifest_of(root)["version"]
    if held != version:
        raise Refusal("package-missing",
                      f"`{name}@{version}` is pinned but the source holds {held} -- "
                      "the source moved on; `upgrade` follows it")
    target = instance.bundle_home(meta) / f"{name}@{version}"
    return _copy(root, target, overwrite=True)


def _engine_copy(meta: Path, source: Path) -> Path | None:
    """Copies the source's engine under the instance, again at every call. -> the copy,
    None when the source IS the instance's engine."""
    engine = source / "engine"
    if engine.resolve() != (meta / instance.SYS / "engine").resolve():
        return _copy(engine, meta / instance.SYS / "engine", overwrite=True)
    return None


def _refresh(meta: Path, source: Path, pins: dict[str, str]) -> list[Path]:
    copied = _engine_copy(meta, source)          # the engine first: the instance carries
    made = [_materialize(meta, source, name, version)   # its machine before its bundles
            for name, version in pins.items()]           # are placed there
    if copied is not None:
        made.append(copied)
    vendor = meta / instance.VENDOR
    if vendor.is_dir():          # a bundle nothing pins is litter -- vendor is machine-owned
        keep = {f"{name}@{version}" for name, version in pins.items()}
        for stale in vendor.iterdir():
            if stale.name not in keep:
                shutil.rmtree(stale)
    return made


def _seed(meta: Path, source: Path, pins: dict[str, str]) -> None:
    """A package may SEED the instance (the kit ships its empty records) -- files arrive
    once, under the records home, and are never clobbered: the instance's data belongs
    to the instance."""
    records = meta / instance.RECORDS
    for name in pins:
        seed = package_dir(source, name) / "seed"
        if not seed.is_dir():
            continue
        records.mkdir(parents=True, exist_ok=True)
        for item in sorted(seed.iterdir()):
            _copy(item, records / item.name, overwrite=False)


def _copy(item: Path, target: Path, overwrite: bool) -> Path:
    if target.exists() and not overwrite:
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    if not item.is_dir():
        if target.exists():
            target.unlink()
        shutil.copy2(item, target)
        return target
    staging = target.with_name(target.name + ".staging")   # the copy happens OFF-STAGE, then
    if staging.exists():                                   # the EXCHANGE: the standing tree
        shutil.rmtree(staging)                             # steps aside, the copy steps in --
    shutil.copytree(item, staging, ignore=shutil.ignore_patterns("__pycache__", "tests"))   # a bundle carries no bench
    old = target.with_name(target.name + ".old")           # two renames, and the target is
    if old.exists():                                       # absent for the instant between
        shutil.rmtree(old)                                 # them alone, never for a copy's time
    if target.exists():
        target.rename(old)
    staging.rename(target)
    if old.exists():
        shutil.rmtree(old)
    return target
