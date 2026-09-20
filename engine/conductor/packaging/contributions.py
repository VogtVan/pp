"""packaging.contributions -- the CONTRACT of contributions: what a package declares
under `contributes:` in its manifest, validated at the build, refused by name.

A package extends the engine by DECLARING, never by calling: the manifest says at
which point a contribution plays and the engine composes every package's
declarations in the requires topology. Two executors carry them all -- a
document played at a socket (`HOOK <socket>` in a proc, the contributor's
`attach:`), a skill run by the engine with its output rendered -- and the data
kinds (resources, events) are materialized, never executed. This module reads
and validates; the consumption of each kind arrives with its own batch of the
plan `pp-split` -- until then a declared contribution is a contract, not a
behavior.
"""
from __future__ import annotations

import re
from pathlib import Path

from ..core import language
from ..core.errors import Refusal
from ..state import instance

KEY = "contributes"            # the manifest section every contribution lives under
BASE = language.BASE           # the base package: its sockets ARE their address, no prefix

KINDS = {
    # kind: (the executor, the required fields, the optional fields)
    "sockets": ("none", (), ()),                                   # names a package's procs HOOK
    "cadences": ("document", ("name", "anchor", "record", "play", "at"), ("since",)),
    "checks": ("skill", ("signal",), ("predicate", "skill", "record", "anchor", "home")),
    "commands": ("skill", ("verb", "skill"), ("args",)),          # a console verb of the package
    "events": ("none", (), ("vectors", "signals", "sectors")),    # the bus's data
}
EXECUTORS = frozenset({"document", "skill", "none"})
# exactly TWO executors play a contribution (a document at a socket, a skill run);
# `none` marks the DATA kinds -- a third executor is a defect of this table, not a feature
PREDICATES = frozenset({"record-crossing", "fingerprint", "home-idle", "card-drift"})
SYSTEM_VERBS = frozenset({"acquit", "add", "doctor", "help", "remove", "repo",
                          "upgrade", "version"})
# the console's own bare verbs -- a package command never shadows one
SOCKET_RE = re.compile(r"^[a-z][a-z0-9]*(\.[a-z][a-z0-9]*)+$")   # `boot.ready`, `turn.begin`
VERB_RE = re.compile(r"^[a-z][a-z0-9-]*$")                     # a package's console verb
KEY_RE = re.compile(r"^[0-9a-f]{6}$")
# a run's key is six hex digits (`decade`, `facade` are keys): a verb of that form
# would race the run it shadows at the console, so the grammar refuses it at the build
HOOK_RE = re.compile(r"^\s*HOOK\s+(\S+)\s*$", re.MULTILINE)


def address(owner: str | None, written: str) -> str:
    """-> the ADDRESS of a socket. A proc writes `<proc>.<hook>` -- its own name, then the
    hook's -- and the PACKAGE qualifies it: `<pkg>.<proc>.<hook>`. The kit and the instance
    are the exception: what they write IS their address, two segments. The count therefore
    settles the reading, with no ambiguity to arbitrate: two segments name the kit (or the
    instance), three name another package.

    documentary: a hook name is free INSIDE its package; two packages may open the same one
    without meeting, because the address carries the package that opens it."""
    return written if owner in (None, BASE) else f"{owner}.{written}"


def owner_of(path: Path) -> str | None:
    """-> the NAME of the package a document belongs to, None at the instance -- what
    `address` needs to qualify what that document's proc HOOKs."""
    root = instance.package_of(path)
    if root is None:
        return None
    try:
        return str(instance.manifest_of(root).get("name") or "") or None
    except Refusal:
        return None


def declared(manifest: dict) -> dict:
    """-> the `contributes:` section of a manifest, `{}` when absent. A manifest
    without the section declares nothing -- today's packages are valid as they are."""
    section = manifest.get(KEY)
    if section is None:
        return {}
    if not isinstance(section, dict):
        raise Refusal("contribution-malformed", f"`{KEY}:` is not a mapping")
    return section


def _families_verified(name: str, section) -> None:
    """A vector family is a STRUCTURE: the prefix and the skill that verifies its slugs
    (`verify: <skill>`). A family declared without one refuses at the build by its name --
    the engine asks for the form alone, it names no package and no referential."""
    families = (section or {}).get("vectors") if isinstance(section, dict) else None
    for prefix, spec in (families or {}).items():
        workers = [str(spec.get(role) or "").strip() for role in ("verify", "guard")] if isinstance(spec, dict) else []
        if not any(workers):
            raise Refusal("family-unverified",
                          f"`{name}` declares `{prefix}:` without `verify:` -- a family names "
                          "the skill that verifies its slugs (verb `verify`, the vector on stdin); "
                          "a provider that only GUARDS another's family names `guard:` alone")


def contributions(manifest: dict) -> list[dict]:
    """-> every contribution of `manifest` as one flat entry each: `{kind, package,
    ...fields}` -- the data kinds (`sockets`, `resources`, `events`) become one entry
    carrying their value. The shape is validated here: an unknown kind, a list where
    a mapping is owed or a missing field refuses by name, nothing composed."""
    name = str(manifest.get("name") or "?")
    found = []
    for kind, value in declared(manifest).items():
        if kind not in KINDS:
            raise Refusal("contribution-kind-unknown",
                          f"`{name}` declares `{KEY}.{kind}` -- the kinds are "
                          f"{', '.join(sorted(KINDS))}")
        executor, required, optional = KINDS[kind]
        if executor == "none":
            if kind == "events":
                _families_verified(name, value)
            found.append({"kind": kind, "package": name, "value": value})
            continue
        if not isinstance(value, list):
            raise Refusal("contribution-malformed",
                          f"`{name}` {KEY}.{kind}: a list of entries is owed")
        for entry in value:
            if not isinstance(entry, dict):
                raise Refusal("contribution-malformed",
                              f"`{name}` {KEY}.{kind}: an entry is a mapping")
            missing = [field for field in required if not entry.get(field)]
            if missing:
                raise Refusal("contribution-malformed",
                              f"`{name}` {KEY}.{kind}: `{missing[0]}` is owed")
            strangers = [field for field in entry if field not in required + optional]
            if strangers:
                raise Refusal("contribution-malformed",
                              f"`{name}` {KEY}.{kind}: `{strangers[0]}` is no field of it")
            found.append({"kind": kind, "package": name, **entry})
    return found


def _hooked(meta: Path, roots: list[Path]) -> set[str]:
    """-> the socket ADDRESSES that EXIST: every `HOOK <name>` a proc of the composition
    plays, qualified by the package that opens it (the kit's BOOT hooks `boot.ready`,
    a package's SHIP proc hooks `<pkg>.ship.done`), plus the instance's own procs.

    documentary: the same name twice in one proc REFUSES -- a socket names one place in
    the flow, and two would be indistinguishable to every contributor."""
    sockets = set()
    homes: list[tuple[str | None, Path]] = [(None, meta), (None, meta / "procs")]
    homes += [(_root_name(root), root / "procs") for root in roots]
    for owner, home in homes:
        if not home.is_dir():
            continue
        for path in home.glob("*.md"):
            if path.name.startswith("_"):
                continue                        # a `_` file is never scanned, nowhere
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            written = HOOK_RE.findall(text)
            for name in written:
                if written.count(name) > 1:
                    raise Refusal("socket-doubled",
                                  f"`{path.name}` HOOKs `{name}` twice -- a socket names ONE "
                                  "place in the flow")
            sockets.update(address(owner, name) for name in written)
    return sockets


def _root_name(root: Path) -> str | None:
    """-> the package name a vendored root carries, None when it manifests nothing."""
    try:
        return str(instance.manifest_of(root).get("name") or "") or None
    except Refusal:
        return None


def composed(meta: Path, roots: list[Path] | None = None) -> list[dict]:
    """-> every contribution of the instance's packages in the REQUIRES topology
    (dependencies first), each package's entries in declaration order -- the order
    every consumer plays them in. Validated on the way: what `validate` refuses,
    this refuses too. `roots` reads a composition OTHER than the vendored one --
    the target a call validates BEFORE writing it."""
    found = []
    for root in (instance.vendored(meta) if roots is None else roots):
        try:
            manifest = instance.manifest_of(root)
        except Refusal as refusal:
            if refusal.code != "package-unmanifested":
                raise
            continue            # an unmanifested bundle declares nothing -- the
        found += contributions(manifest)   # same leaf `vendored` sorts it as
    return found


def validate(meta: Path, roots: list[Path] | None = None) -> list[dict]:
    """The contract's GATE, played at the build: every manifest's section is read,
    the sockets named must exist (a HOOK in the composition or a `sockets`
    declaration), a verb or a socket claimed twice refuses, a document hooking
    the socket it HOOKs itself refuses as a cycle -- by name, before anything is
    written. -> the composed contributions when everything holds. `roots` judges
    a composition OTHER than the vendored one: the target of add, upgrade or
    remove, read at the source before the instance moves."""
    if roots is None:
        roots = instance.vendored(meta)
    found = composed(meta, roots)
    sockets = _hooked(meta, roots)
    for entry in found:
        if entry["kind"] != "sockets":
            continue
        for socket in _names(entry["value"], entry["package"], "sockets"):
            if not SOCKET_RE.match(socket) or socket.count(".") != 1:
                raise Refusal("contribution-malformed",
                              f"`{entry['package']}` sockets: `{socket}` -- a declaration is "
                              "`<proc>.<hook>`, lowercase; the package qualifies it itself")
            sockets.add(address(entry["package"], socket))
    verbs: dict[str, str] = {}
    for entry in found:
        kind = entry["kind"]
        if kind == "cadences":
            socket = entry["at"]
            if socket not in sockets:
                raise Refusal("socket-unknown",
                              f"`{entry['package']}` {kind}: `{socket}` -- no proc of the "
                              "composition HOOKs it and no package declares it")
        if kind == "checks":
            predicate = entry.get("predicate")
            if predicate and predicate not in PREDICATES:
                raise Refusal("contribution-malformed",
                              f"`{entry['package']}` checks: `{predicate}` -- the predicates "
                              f"are {', '.join(sorted(PREDICATES))}")
            if not predicate and not entry.get("skill"):
                raise Refusal("contribution-malformed",
                              f"`{entry['package']}` checks `{entry['signal']}`: a predicate "
                              "or a skill is owed")
        if kind == "commands":
            verb = str(entry["verb"])
            if verb in SYSTEM_VERBS:
                raise Refusal("command-taken",
                              f"`{entry['package']}` commands: `{verb}` is a verb of the "
                              "console -- a package never shadows one")
            if not VERB_RE.match(verb) or KEY_RE.match(verb):
                raise Refusal("contribution-malformed",
                              f"`{entry['package']}` commands: `{verb}` -- a verb is "
                              "lowercase kebab, and never six hex digits (a run's key)")
            if verb in verbs:
                raise Refusal("command-taken",
                              f"`{verb}` is declared by `{verbs[verb]}` and "
                              f"`{entry['package']}` -- one owner per verb")
            if _script(meta, roots, str(entry["skill"])) is None:
                raise Refusal("command-skill-unknown",
                              f"`{entry['package']}` commands: `{verb}` -> `{entry['skill']}` "
                              "is no script skill of the composition -- a console verb "
                              "runs a script (a proc needs a run)")
            verbs[verb] = entry["package"]
    return found

def providers(meta: Path, token: str) -> list[dict]:
    """-> the DOCUMENTS that provide `token` -- `provides: <token>` at their front matter,
    the skill and its arguments read from their `with: <skill> <args>` -- in the requires
    topology. Each is a skill the engine runs, its output rendered as the INFORMATION
    section the token names; several providers of one token render one contiguous section.

    documentary: a provider is DATA, exactly as a manifest entry was -- it serves its
    token whether or not its own document is in flight, so no order is owed between the
    document that provides and the one that consumes."""
    found = []
    for name, _path, package, front in instance.documents(meta):
        if token not in str(front.get("provides", "")).split():
            continue
        said = str(front.get("with", "")).split()
        if not said:
            raise Refusal("contribution-malformed",
                          f"`{name}` provides `{token}` and declares no `with:` -- a "
                          "provider names the skill that serves its token")
        found.append({"package": package, "document": name,
                      "token": token, "skill": said[0], "args": said[1:]})
    return found


def commands(meta: Path) -> list[dict]:
    """-> the `commands:` entries of the composition, in the requires topology then
    declaration order -- the order the console's help lists them in."""
    return [one for one in composed(meta) if one["kind"] == "commands"]


def command(meta: Path, verb: str) -> dict | None:
    """-> the command entry `verb` names, or None: the console resolves a bare
    first token here AFTER its own verbs and BEFORE the run's key -- one owner
    per verb, settled at the build."""
    return next((one for one in commands(meta) if str(one["verb"]) == verb), None)


def _script(meta: Path, roots: list[Path], skill: str) -> Path | None:
    """-> the script `skill` resolves to across `[meta] + roots` -- the instance's
    own `skills/` first, then the composition's packages, the FIRST contract found
    deciding (the same order `instance.skill_contract` walks at the run) -- or None
    when no contract stands or the one found carries no script beside it."""
    for home in [meta] + list(roots):
        contract = home / "skills" / skill / "SKILL.md"
        if contract.is_file():
            script = contract.parent / f"{skill}.py"
            return script if script.is_file() else None
    return None


def run_skill(meta: Path, skill: str, args: list[str]) -> tuple[int, str, str]:
    """Runs a package's script skill in a SUBPROCESS -- the interpreter running the
    engine, the script resolved by its contract (`skills/<name>/<name>.py`), the
    member's root as working directory -- and -> (rc, stdout, stderr). The
    engine never imports a package's code: the skill is a program it plays."""
    import subprocess
    import sys
    contract = instance.skill_contract(meta, skill)
    script = contract.parent / f"{skill}.py" if contract else None
    if script is None or not script.is_file():
        return 2, "", f"`{skill}` -- no script skill of that name in this instance"
    done = subprocess.run([sys.executable, str(script), *[str(one) for one in args]],
                          capture_output=True, text=True, cwd=str(meta.parent))
    return done.returncode, done.stdout, done.stderr


def _names(value, package: str, kind: str) -> list[str]:
    if isinstance(value, str):
        return value.split()
    if isinstance(value, list) and all(isinstance(one, str) for one in value):
        return value
    raise Refusal("contribution-malformed", f"`{package}` {kind}: a list of names is owed")

