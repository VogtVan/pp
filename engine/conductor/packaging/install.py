"""Behaviour: REPRODUCTION -- seeding an instance, and keeping its packages materialized.

The mechanism carries its own reproduction: no external generator writes an instance.
`install` seeds one from `template/instance/`; `sync` (re)materializes the pinned
packages under `vendor/` -- an instance carries EVERYTHING it runs on, the engine
included: cloned alone, backed up, restored, its procedural layer travels with it.
"""
from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from . import compiling, contributions, topology
from ..state import instance
from ..state.settings import SEEDS   # noqa: F401 -- the system's defaults are settings data; install seeds them
from ..core import language
from ..core.errors import Refusal
from ..core.model import Member

BASE = language.BASE           # every instance stands on it; installs are `kit + asked`
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


def _console_texts(meta: Path) -> list[tuple[str, str, bool]]:
    """-> (name, text, executable) for the two console scripts of `meta`'s member."""
    return [("pp", CONSOLE.format(meta=meta.name), True),
            ("pp.cmd", CONSOLE_CMD.format(meta=meta.name), False)]


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


def _single_user_bearer(roots: list[tuple[str, Path]]) -> None:
    """At most ONE requested package may carry user-level files -- two personas
    fighting over MEMBER.md is a conflict to refuse upfront, nothing written."""
    bearers = [name for name, root in roots if user_files(root)]
    if len(bearers) > 1:
        raise Refusal("user-packages-conflict",
                      f"{', '.join(bearers)} all install user-level files -- "
                      "one package of this kind at a time")


def _place_user(meta: Path, root: Path, source: Path, backup: bool) -> list[str]:
    """Places a package's user files at the instance root. A fresh install replaces
    the template seeds silently; later (backup=True), a PRISTINE file -- identical to
    the incoming copy or still the template seed -- is replaced silently, an EDITED
    one is saved to `<name>.old` first: the operator's work is never destroyed.
    -> the names that were backed up."""
    saved = []
    for item in user_files(root):
        target = meta / item.name
        incoming = item.read_bytes()
        if target.exists() and backup:
            standing = target.read_bytes()
            template = source / "template" / "instance" / item.name
            pristine = (standing == incoming
                        or (template.is_file() and standing == template.read_bytes()))
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
        template = source / "template" / "instance" / item.name
        if standing != item.read_bytes() and not (
                template.is_file() and standing == template.read_bytes()):
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
    import importlib.util
    told = []
    for name in wired_providers(workspace):
        wire_path = source / "adapters" / name / "wire.py"
        if not wire_path.is_file():
            continue
        spec = importlib.util.spec_from_file_location(f"wire_{name}", wire_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        told += [str(done) for done in module.wire(workspace.resolve(), meta)]
    return told


def product_root(script: Path) -> Path:
    """-> the product checkout an engine belongs to (`<product>/engine/pp.py`)."""
    return script.resolve().parent.parent


def package_dir(source: Path, name: str) -> Path:
    """-> where `name` lives in the product: the kit at the root, the rest under packages/."""
    for candidate in (source / name, source / "packages" / name):
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
            doors: bool = True) -> Path:
    """Seeds an instance at `target`: template, engine (a member carries everything),
    the pinned packages, their seeds, and the compiled catalog. Never overwrites.

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
    resolved_slug = slug or instance.kebab(meta.parent.name)
    wanted = [BASE] + [name for name in packages if name != BASE]
    pins = closure(source, wanted)                 # the prerequisites come with the install
    _single_user_bearer([(name, package_dir(source, name)) for name in pins])
    topology.validate(meta, target_roots(source, pins),   # the target judged first --
                      template=source / "template" / "instance")   # its seeds its own
    meta.mkdir(parents=True, exist_ok=True)
    for item in sorted((source / "template" / "instance").iterdir()):
        _copy(item, meta / item.name, overwrite=False)
    (meta / "procs").mkdir(exist_ok=True)          # the user's own space
    from datetime import datetime, timezone
    instance.write(meta, {"source": str(source), "slug": resolved_slug,
                          "engine": source_version(source),
                          "installed": datetime.now(timezone.utc).date().isoformat(),
                          "packages": pins})   # `installed:` -- the instance's birth date, on record
    _refresh(meta, source, pins)
    _seed(meta, source, pins)
    for name in pins:      # a fresh instance: the package's user files replace the
        _place_user(meta, package_dir(source, name), source, backup=False)   # template seeds
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


SKILL_DOOR = ("This workspace is conducted. **Use the `pp` skill** your harness lists —\n"
              "it is the operator-registered card of the conductor: what the tool is,\n"
              "what it never does, and the protocol for following its blocks.\n")
DOORS = {
    "CLAUDE.md": SKILL_DOOR,
    "AGENTS.md": SKILL_DOOR,
    "GEMINI.md": ("This workspace is conducted. **Run the `/pp` command** — it serves the\n"
                  "operator-registered card of the conductor: what the tool is, what it\n"
                  "never does, and the protocol for following its blocks.\n"),
}


def door(root: Path, name: str) -> Path | None:
    """ONE integration door at the member root, pointing that harness at the
    conductor. Written once, never overwritten -- the member's own file the moment
    it exists. -> the path when written, None when it already stood."""
    path = root / name
    if path.exists():
        return None
    path.write_text(DOORS[name], encoding="utf-8")
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
    engine = meta / instance.SYS / "engine" / "pp.py"
    child = subprocess.run(["uv", "run", str(engine), *verb],
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
    vendor = meta / instance.VENDOR
    if all((vendor / f"{name}@{version}").is_dir()
           for name, version in instance.pins(meta).items()):
        topology.validate(meta)


def sync(member: Member) -> list[Path]:
    """(Re)materializes the member's packages and engine at their pins -- idempotent,
    and at CONSTANT pins the standing runs stand: a run binds to bundle versions, and
    none moved (`upgrade` is the verb that voids them). A copied engine NEWER than the
    running one takes the tail over (`_delegate`)."""
    meta = member.meta
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
    from ..core.version import VERSION
    if source_version(source) != VERSION:
        _delegate(meta, source_version(source), "-sync", str(meta))
        return made
    if declared.get("engine") != source_version(source):
        declared["engine"] = source_version(source)     # the record follows the copy
        instance.write(meta, declared)
    _seed(meta, source, pins)
    console(meta)
    compiling.build_tools(meta)
    compiling.render_registry(meta)   # validates; writes nothing
    compiling.build_system(meta)
    for done in refresh_projections(member.path, meta, source):
        print(f"pp: {done}")
    return made


def upgrade(member: Member) -> list[str]:
    """Moves every pin to the version the source holds NOW, then re-materializes
    (standing runs close -- a run binds to bundle versions). -> the moves, told
    one per line; [] when already current, and then NOTHING was touched."""
    meta = member.meta
    declared = instance.read(meta)
    source = Path(declared.get("source", ""))
    if not source.is_dir():
        raise Refusal("source-missing",
                      f"{meta / instance.MANIFEST} points at `{source}` -- not a directory")
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
    from ..state import persistence
    runs = len(persistence.slots(meta))
    for one in added:                            # the bundles first, the manifest after
        _materialize(meta, source, one, held[one])
    declared["packages"] = held
    instance.write(meta, declared)
    sync(member)
    from ..state import log   # a saved run binds to bundle VERSIONS: across an update
    for slot in persistence.slots(meta):    # they are void -- state, not data
        standing = persistence.trace_of(slot)
        if standing:                        # the update that voids a run says so IN its trace
            log.record(slot.parent / standing, "sync")
        persistence.forget(slot)
    told = [f"{name} {old} -> {new}" for name, old, new in moves]
    told += [f"{name} pinned at {held[name]} (required)" for name in added]
    told += sync_settings(meta, source)
    from . import events             # the bus's record follows the families' names: a
    told += [f"bus: {line}" for line in events.migrate_families(meta)]   # latched vector
                                     # crosses a rename by the tail of its qualified family
    if runs:
        told.append(f"{runs} run(s) closed by the update")
    return told


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
            if key.startswith("cap.") and key not in placed:
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
    Standing runs stand: same versions, same contract (`upgrade` is the void)."""
    meta = member.meta
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
    made = [_materialize(meta, source, name, version) for name, version in current.items()]
    made += sync_settings(meta, source)   # the OLD engine runs an upgrade, so the
                                  # settings sync arrives one upgrade late by construction
                                  # -- doctor, running the NEW engine, heals in place
    engine = source / "engine"
    if engine.resolve() != (meta / instance.SYS / "engine").resolve():
        made.append(_copy(engine, meta / instance.SYS / "engine", overwrite=True))
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
    if declared.get("engine") != source_version(source):
        declared["engine"] = source_version(source)
        instance.write(meta, declared)
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
    for name in ("system.md", "tools.md"):
        if not (meta / instance.SYS / name).is_file():
            continue
        receipt = held.get(name) or {}
        if receipt.get("engine") != VERSION:
            told.append(f"receipt {name}: STALE -- compiled by "
                        f"{receipt.get('engine') or 'an engine that left no receipt'}")
        elif name == "system.md" and receipt.get("inputs") != inputs:
            told.append(f"receipt {name}: STALE -- the vendor inputs moved since the compile")
        elif name == "tools.md" and receipt.get("catalog") != compiling.catalog_inputs(meta):
            told.append(f"receipt {name}: STALE -- the catalog inputs moved since the compile")
        else:
            told.append(f"receipt {name}: current ({VERSION})")
    canon = next((root / "refs" / "PP.md" for root in instance.vendored(meta, switched=False)
                  if root.name.startswith(f"{instance.base_of(meta)}@")
                  and (root / "refs" / "PP.md").is_file()), None)
    if canon is not None:
        contract = canon.read_text(encoding="utf-8")
        for card in (member.path / ".claude" / "skills" / "pp" / "SKILL.md",
                     member.path / ".agents" / "skills" / "pp" / "SKILL.md"):
            if card.is_file():
                state = ("current" if card.read_text(encoding="utf-8") == contract
                         else "DRIFTED -- edited or old; the fresh projection is written "
                              "(or is owed) as its `.candidate`")
                told.append(f"card {card.relative_to(member.path)}: {state}")
    return told


def remove_package(member: Member, name: str) -> list[str]:
    """Retires ONE package from an ALREADY-SEEDED instance -- the inverse of `add`,
    the same transaction read backwards: the target composition is judged first
    (nothing pinned may still require it, the contract must still hold), then
    the manifest lets it go, then its bundle leaves; the records stay -- they are
    the instance's data -- and the package's settings keys carry on as `unowned`
    in the recomposed SETTINGS, so a later `add` finds the operator's values.
    -> what was done, told one per line."""
    meta = member.meta
    declared = instance.read(meta)
    source = Path(declared.get("source", ""))
    if not source.is_dir():
        raise Refusal("source-missing",
                      f"{meta / instance.MANIFEST} points at `{source}` -- not a directory")
    pins = instance.pins(meta)
    if name == BASE:
        raise Refusal("package-base", f"`{BASE}` is the base of every instance -- never removed")
    if name not in pins:
        raise Refusal("package-unpinned", f"`{name}` is not pinned here -- nothing to remove")
    dependents = []
    for other, version in pins.items():
        if other == name:
            continue
        try:
            requires = instance.manifest_of(meta / instance.VENDOR / f"{other}@{version}").get("requires") or []
        except Refusal:
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
    return told


def add_package(member: Member, name: str) -> Path:
    """Adds `name` to an ALREADY-SEEDED instance -- `install` without recreating it.
    Pins it, materializes its bundle, seeds it, recompiles the catalog."""
    meta = member.meta
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
            posed.append(_materialize(meta, source, one, version))
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
    made = meta / instance.VENDOR / f"{name}@{target[name]}"
    console(meta)
    compiling.build_tools(meta)
    compiling.render_registry(meta)   # validates; writes nothing
    compiling.build_system(meta)
    for done in refresh_projections(member.path, meta, source):
        print(f"pp: {done}")
    return made


def _materialize(meta: Path, source: Path, name: str, version: str) -> Path:
    """Copies `name`'s bundle at its pinned `version` into `meta`'s vendor -- the one
    package-materializing call `install`/`sync`/`add_package` all share."""
    root = package_dir(source, name)
    held = instance.manifest_of(root)["version"]
    if held != version:
        raise Refusal("package-missing",
                      f"`{name}@{version}` is pinned but the source holds {held} -- "
                      "the source moved on; `upgrade` follows it")
    return _copy(root, meta / instance.VENDOR / f"{name}@{version}", overwrite=True)


def _refresh(meta: Path, source: Path, pins: dict[str, str]) -> list[Path]:
    made = [_materialize(meta, source, name, version) for name, version in pins.items()]
    engine = source / "engine"
    if engine.resolve() != (meta / instance.SYS / "engine").resolve():
        made.append(_copy(engine, meta / instance.SYS / "engine", overwrite=True))
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
    staging = target.with_name(target.name + ".staging")   # the copy happens OFF-STAGE:
    if staging.exists():                                   # the swap window shrinks to a rename
        shutil.rmtree(staging)
    shutil.copytree(item, staging, ignore=shutil.ignore_patterns("__pycache__", "tests"))   # a bundle carries no bench
    if target.exists():
        shutil.rmtree(target)
    staging.rename(target)
    return target
