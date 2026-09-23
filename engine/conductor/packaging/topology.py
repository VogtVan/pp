"""packaging.topology -- the LINT of topology: every reference a package's document
or manifest carries resolves to its OWNER, and the build refuses, by name and
before anything is written, the ones the referrer's `requires` closure does not
cover.

A package extends the engine by declaring; what it declares may only name what
it requires. The owner of a target is the package whose root carries it, the
engine (the mechanical formats, the protocol's settings keys), or the instance
(its own documents, the documents a package PLACES there through `user/`, the
machine's `.sys` artifacts, the repository). The instance is the top of the
composition: its documents reference every pin and HOOK what they want.

Three refusals: `dependency-undeclared` (the owner is a package outside the
referrer's closure), `reference-unknown` (a CALL, a tool, an overlay's base, an
attach, a sink, a contribution's skill, a format or a key that resolves nowhere),
`socket-undeclared` (a package's proc HOOKs a socket its manifest does not
declare). A `serve:` token is judged on its closure alone -- its existence is
the run's matter (the repository, the artifacts still to build). The gate is
the contract's: `validate` plays `contributions.validate` first, then this pass.

The NAMES a package exposes are judged here too (the naming law of plan
pp-split, KPS31): the EXPLICIT kinds -- a console verb, a skill, a vector
family, a payload token (a settings key is the fragment's own gate) -- wear the
package's name, `<package>-<name>` (`pp-<package>` for a skill; the package's
name alone counts), the base package alone staying bare; a name wearing ANOTHER
package's prefix JOINS that package's thing and is a dependency like any other
(`dependency-undeclared` outside the closure); a name wearing nobody's refuses
`name-unprefixed`. The bare kinds -- procs and refs -- are resolved by the
engine and never prefixed: a document name is ONE base across the packages, and
two packages carrying it as a base refuse `name-ambiguous` (an overlay amends a
base under `overlays/`, by the source name -- that is the one same name allowed).
"""
from __future__ import annotations

import re
from pathlib import Path

from ..core import document as documents
from ..core import language, tokens
from ..core.errors import Refusal
from ..state import instance
from . import contributions

INSTANCE = "instance"      # the owner of everything the instance carries or places
ENGINE = "engine"          # the owner of the mechanical formats and the protocol's keys
TAG = re.compile(r"@([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]+)")
SETTINGS = "SETTINGS"
HOOK_LINE = re.compile(r"^\s*HOOK\s+(\S+)\s*$")
DOCUMENT_SPACES = ("overlays", "procs", "refs")            # where a package's document names resolve
OVERLAY_SPACES = ("overlays",)                            # a file there amends a BASE elsewhere
BASE_SPACES = ("procs", "refs")                            # where a package carries a BASE by its bare name
SKILL_LEAD = "pp-"                                         # every skill name opens so; the package follows


# --- the composition: roots, names, closures ---------------------------------------

def _roots(meta: Path, roots: list[Path] | None) -> dict[str, Path]:
    """-> package name -> root, in the requires topology."""
    found = {}
    for root in (instance.vendored(meta, switched=False) if roots is None else roots):
        try:
            found[str(instance.manifest_of(root)["name"])] = root
        except Refusal as refusal:
            if refusal.code != "package-unmanifested":
                raise
    return found


def closure(named: dict[str, Path], package: str) -> set[str]:
    """-> `package` and every package it requires, transitively, within `named` --
    a name the composition lacks is left out (the pins are read CLOSED upstream)."""
    seen: set[str] = set()
    stack = [package]
    while stack:
        one = stack.pop()
        if one in seen or one not in named:
            continue
        seen.add(one)
        for need in instance.manifest_of(named[one]).get("requires") or []:
            stack.append(str(need))
    return seen


# --- ownership: what a name resolves to, and whose it is ----------------------------

def _document_homes(meta: Path, named: dict[str, Path], spaces=DOCUMENT_SPACES) -> list[tuple[Path, str]]:
    """-> (directory, owner) where a document NAME resolves, nearest first -- the
    instance's own space (the template that SEEDS it counts as its own: a fresh
    install judges before the seeding), then each package's spaces in the
    requires topology reversed (a client is nearer than its dependency, as
    `search_paths` walks)."""
    homes = [(meta, INSTANCE), (meta / "procs", INSTANCE), (meta / instance.SYS, INSTANCE)]
    if _TEMPLATE is not None:
        homes += [(_TEMPLATE, INSTANCE), (_TEMPLATE / "procs", INSTANCE)]
    for name, root in reversed(list(named.items())):
        homes += [(root / space, name) for space in spaces]
    # a package's `user/` documents are PLACED at the instance by the install:
    # their owner is the instance, whether the placing already happened or not
    homes += [(root / "user", INSTANCE) for root in named.values()]
    return homes


def _skill_owner(name: str, meta: Path, named: dict[str, Path]) -> str | None:
    """-> the owner of the skill contract `name` resolves to: the instance's own
    `skills/` first, then each package's (the order `skill_contract` walks)."""
    if (meta / "skills" / name / "SKILL.md").is_file():
        return INSTANCE
    for package, root in named.items():
        if (root / "skills" / name / "SKILL.md").is_file():
            return package
    return None


def _format_owners(read: list[tuple[Path, str, dict]]) -> dict[str, str]:
    """-> format name -> owner: the engine's builtins, then every `formats:` line a
    document of the composition declares (the instance's own space included)."""
    owners = {name: ENGINE for name in language.FORMATS}
    for _, owner, front in read:
        for line in str(front.get("formats") or "").splitlines():
            parts = line.split()
            if parts:
                owners.setdefault(parts[0], owner)
    return owners


def _key_owners(meta: Path, named: dict[str, Path]) -> dict[str, str]:
    """-> settings key -> owner: the protocol's keys (the engine), each package's
    fragment (`settings/SETTINGS.md`, read as data), the instance's own keys."""
    from ..state import settings
    owners = {key: ENGINE for key, _ in settings.SEEDS}
    for name, root in named.items():
        fragment = root / settings.FRAGMENT
        if fragment.is_file():
            front = _front(fragment) or {}
            for key in front:
                if key not in settings.META_KEYS:
                    owners.setdefault(str(key), name)
    own = meta / "SETTINGS.md"
    if own.is_file():
        for key in (_front(own) or {}):
            owners.setdefault(str(key), INSTANCE)
    return owners


def _socket_owners(named: dict[str, Path]) -> dict[str, str]:
    """-> socket -> the package declaring it under `contributes.sockets`."""
    owners = {}
    for name, root in named.items():
        declared = contributions.declared(instance.manifest_of(root))
        value = declared.get("sockets") or []
        names = value.split() if isinstance(value, str) else [str(one) for one in value]
        for socket in names:
            owners.setdefault(contributions.address(name, socket), name)
    return owners


# --- the documents of the composition, and what each one references ---------------

def _front(path: Path) -> dict | None:
    try:
        return documents.read(path).front
    except Refusal:
        return None            # a broken front matter is another gate's refusal


def _documents(meta: Path, named: dict[str, Path]) -> list[tuple[Path, str]]:
    """-> (path, owner) of every document the pass judges: EVERY document of the
    instance but the machine's own state, whatever directory carries it; each
    package's procs, overlays and skills. A package's `user/` and `refs/`
    carry no flow of their own; `_`-prefixed files are shelf ideas, never judged."""
    found = []
    if meta.is_dir():
        # the instance is the operator's side, whole: a directory it grows -- whoever
        # grew it -- is judged like the rest, and no package's name lives here
        found += [(path, INSTANCE) for path in sorted(meta.rglob("*.md"))
                  if path.relative_to(meta).parts[0] != instance.SYS]
    for name, root in named.items():
        for space in ("procs", "overlays"):
            found += [(path, name) for path in sorted((root / space).glob("*.md"))]
        found += [(path, name) for path in sorted((root / "skills").glob("*/SKILL.md"))]
    return [(path, owner) for path, owner in found if not path.name.startswith("_")]


def references(path: Path, front: dict) -> list[tuple[str, str]]:
    """-> (kind, name) for every reference a document's front matter carries:
    `call` (CALL lines, `@Doc.field` tags on a document), `serve` (SERVE lines and
    `serve:` rows, ranges and natures stripped), `tool` (offers; `-name` removals
    skipped, `+name` marked `offer+`), `hook` (HOOK lines), `attach`, `sink`,
    `format` (output:/input:), `key` (`@SETTINGS.<key>` tags)."""
    found: list[tuple[str, str]] = []
    proc = str(front.get("proc") or "")
    for line in proc.splitlines():
        words = line.split()
        if not words:
            continue
        if words[0] == "CALL" and len(words) > 1:
            found.append(("call", words[1]))
        elif words[0] == "HOOK" and len(words) > 1:
            found.append(("hook", words[1]))
        elif words[0] == "SERVE" and len(words) > 1:
            found.append(("serve", tokens.parse(tokens.split_row(line)[1])[0]))
    for token in str(front.get("tools") or "").split():
        if token.startswith("-"):
            continue
        found.append(("offer+" if token.startswith("+") else "tool", token.lstrip("+")))
    for row in str(front.get("serve") or "").splitlines():
        for token in tokens.split_row(row):
            if token.endswith(":"):
                continue           # the nature of the row, not a document
            found.append(("serve", tokens.parse(token)[0]))
    for socket in str(front.get("attach") or "").split():
        found.append(("attach", socket))
    for socket in str(front.get("mount") or "").split():
        found.append(("mount", socket))
    if front.get("sink"):
        found.append(("sink", str(front["sink"]).strip()))
    for key in ("output", "input"):
        if front.get(key):
            found.append(("format", str(front[key]).strip()))
    for name in str(front.get("next") or "").split():
        found.append(("call", name))     # a successor is CALLed: judged as one
    tagged = " ".join([proc, str(front.get("when") or ""), str(front.get("exec") or ""),
                       str(front.get("decide") or "")])
    for match in TAG.finditer(tagged):
        document, field = match.group(1), match.group(2)
        found.append(("key", field) if document == SETTINGS else ("call", f"{document}.md"))
    return found


def _judge_exec(owner: str, where: str, path: Path, front: dict, meta: Path,
                named: dict[str, Path]) -> None:
    """The `exec:` of a document: played by the OWNER's own skill -- `pp-<package>`, which
    the package must carry (`reference-unknown`); a document of the instance names one of
    the instance's own skills first. A document the engine neither CALLs nor mounts -- a
    skill contract, a ref, a package document with neither `proc:` nor `mount:` -- refuses
    `exec-unplayable`: its exec would never play."""
    declared = str(front.get("exec") or "").split()
    if not declared:
        return
    if owner == INSTANCE:
        if not (meta / "skills" / declared[0] / "SKILL.md").is_file():
            raise Refusal("reference-unknown",
                          f"`{owner}` {where}: exec `{declared[0]}` names no skill under the "
                          "instance's own `skills/` -- a document of the instance plays its "
                          "own skill, named first")
        return
    playable = (path.parent.name in OVERLAY_SPACES
                or path.parent.name == "procs" and (front.get("proc") or front.get("mount")))
    if not playable:
        raise Refusal("exec-unplayable",
                      f"`{owner}` {where}: `exec:` on a document the engine neither CALLs nor "
                      "mounts -- an exec plays at a CALL, a mount or a lap")
    skill = f"{SKILL_LEAD}{owner}"
    if _skill_owner(skill, meta, named) != owner:
        raise Refusal("reference-unknown",
                      f"`{owner}` {where}: `exec: {' '.join(declared)}` plays `{skill}` and "
                      f"`{owner}` carries no such skill")


def _judge_field(owner: str, where: str, path: Path, front: dict) -> None:
    """The `field:` of a DESCRIBED door: prose, never empty (`field-empty`); alone --
    `cycle:` and `field:` together refuse `cycle-and-field`, one iterator per door; on a
    document the engine CALLs as a proc, or its step would never play
    (`field-unplayable`)."""
    if "field" not in front:
        return
    if not str(front.get("field") or "").strip():
        raise Refusal("field-empty",
                      f"`{owner}` {where}: `field:` declares nothing -- the prose of what the "
                      "cycle turns on, said to the agent")
    if front.get("cycle"):
        raise Refusal("cycle-and-field",
                      f"`{owner}` {where} declares `cycle:` and `field:` together -- keep one: "
                      "`cycle: <token>` asks a provider, `field:` asks the agent")
    if not (path.parent.name == "procs" and front.get("proc")):
        raise Refusal("field-unplayable",
                      f"`{owner}` {where}: `field:` on a document the engine never CALLs as a "
                      "proc -- the field's step would never play")


def _judge_next(owner: str, where: str, path: Path, front: dict, meta: Path,
                named: dict[str, Path]) -> None:
    """The successors of a document (`next:`): on a proc the engine CALLs, or the
    transition would never play (`next-unplayable`); two names or more want ONE
    decider -- `choose:` (the agent) or `decide:` (the owner's skill, which must exist:
    `reference-unknown`) -- none refuses `next-undecided`, both `choose-and-decide`;
    a decider with fewer than two names has nothing to decide (`decision-idle`)."""
    names = str(front.get("next") or "").split()
    prose = str(front.get("choose") or "").strip()
    words = str(front.get("decide") or "").split()
    decider = "choose" if prose else "decide" if words else ""
    if not names:
        if decider:
            raise Refusal("decision-idle",
                          f"`{owner}` {where}: `{decider}:` with no `next:` -- nothing to decide")
        return
    if not (path.parent.name == "procs" and front.get("proc")):
        raise Refusal("next-unplayable",
                      f"`{owner}` {where}: `next:` on a document the engine never CALLs as a "
                      "proc -- a successor follows a document that leaves")
    if prose and words:
        raise Refusal("choose-and-decide",
                      f"`{owner}` {where} declares `choose:` and `decide:` together -- keep one: "
                      "`choose:` asks the agent, `decide:` asks a skill")
    if len(names) < 2 and decider:
        raise Refusal("decision-idle",
                      f"`{owner}` {where}: `{decider}:` under a `next:` of one name -- nothing "
                      "to decide, the one successor follows")
    if len(names) >= 2 and not decider:
        raise Refusal("next-undecided",
                      f"`{owner}` {where}: `next:` names {len(names)} successors and no decider "
                      "-- `choose:` (the prose) or `decide:` (a skill) says which")
    if not words:
        return
    if owner == INSTANCE:
        if not (meta / "skills" / words[0] / "SKILL.md").is_file():
            raise Refusal("reference-unknown",
                          f"`{owner}` {where}: decide `{words[0]}` names no skill under the "
                          "instance's own `skills/` -- a document of the instance plays its "
                          "own skill, named first")
        return
    skill = f"{SKILL_LEAD}{owner}"
    if _skill_owner(skill, meta, named) != owner:
        raise Refusal("reference-unknown",
                      f"`{owner}` {where}: `decide: {' '.join(words)}` plays `{skill}` and "
                      f"`{owner}` carries no such skill")


def _judge_graph(read: list[tuple[Path, str, dict]]) -> None:
    """The GRAPH of successors over the whole composition: the `next:` of every proc
    makes the edges between base documents; a loop refuses `next-cycle` with its
    parts named (the gesture of `order-cycle`, on documents), and an edge whose two
    ends declare a format refuses `format-mismatch` when the upstream `output:` and
    the downstream `input:` differ -- the check the run cannot make on an injected
    CALL. An accepted graph cannot loop: the run verifies nothing."""
    fronts: dict[str, dict] = {}
    for path, _owner, front in read:
        if path.parent.name == "procs":
            fronts[path.name] = front       # the later home wins, as a CALL resolves
    edges = {name: str(front.get("next") or "").split()
             for name, front in fronts.items() if front.get("next")}
    for name, targets in edges.items():
        out = str(fronts[name].get("output") or "").strip()
        for target in targets:
            into = str(fronts.get(target, {}).get("input") or "").strip()
            if out and into and "any" not in (out, into) and out != into:
                raise Refusal("format-mismatch",
                              f"`{name}` produces `{out}` -- its successor `{target}` needs `{into}`")
    state: dict[str, int] = {}

    def visit(node: str, trail: list[str]) -> None:
        state[node] = 1
        trail.append(node)
        for target in edges.get(node, ()):
            if state.get(target) == 1:
                loop = trail[trail.index(target):] + [target]
                raise Refusal("next-cycle",
                              f"`{' -> '.join(loop)}` -- the successors loop; a graph of "
                              "transitions is acyclic, a repetition is a node's own (`cycle:`, `field:`)")
            if state.get(target) is None:
                visit(target, trail)
        trail.pop()
        state[node] = 2

    for node in edges:
        if state.get(node) is None:
            visit(node, [])


def _manifest_references(manifest: dict) -> list[tuple[str, str]]:
    """-> (kind, name) for what a manifest's contributions name outside itself:
    the sockets of cadences and payloads (`socket`), the documents of cadences
    (`call`), the skills of payloads, checks and commands (`skill`)."""
    found = []
    for entry in contributions.contributions(manifest):
        kind = entry["kind"]
        if kind == "cadences":
            found += [("socket", str(entry["at"])), ("call", str(entry["play"]))]
        elif kind == "payloads":
            found.append(("skill", str(entry["skill"])))
            if entry.get("at"):
                found.append(("socket", str(entry["at"])))
        elif kind in ("checks", "commands") and entry.get("skill"):
            found.append(("skill", str(entry["skill"])))
    return found


# --- the names a package exposes ---------------------------------------------------

def _prefixed(name: str, package: str, lead: str = "") -> bool:
    """-> whether `name` wears `package`'s prefix: `<lead><package>` alone, or
    `<lead><package>-…` -- the one form the naming law admits for a package's own."""
    own = f"{lead}{package}"
    return name == own or name.startswith(own + "-")


def _wearer(name: str, named: dict[str, Path], lead: str = "") -> str | None:
    """-> the package whose prefix `name` wears -- the longest match, so `plan-x` is
    `plan-x`'s before `plan`'s -- or None when it wears nobody's."""
    hits = [package for package in named if _prefixed(name, package, lead)]
    return max(hits, key=len) if hits else None


def _base_bare_names(named: dict[str, Path], read: list[tuple[Path, str, dict]], base: str) -> set[str]:
    """-> the families and tokens the BASE package declares bare -- joinable by every
    package (the base is in every closure) without a prefix, since it wears none."""
    found: set[str] = set()
    root = named.get(base)
    if root is None:
        return found
    for entry in contributions.contributions(instance.manifest_of(root)):
        if entry["kind"] == "events":
            found.update(str(family) for family in ((entry.get("value") or {}).get("vectors") or {}))
    for _, owner, front in read:
        if owner == base:
            found.update(str(front.get("provides") or "").split())
    return found


def _naming(meta: Path, named: dict[str, Path], closures: dict[str, set[str]],
            read: list[tuple[Path, str, dict]], base: str) -> None:
    """The naming gate (KPS31): every EXPLICIT public name of a package -- verb, skill,
    family, token -- wears the package's name; a name wearing another package's is a
    JOIN and that package sits in the closure; the base package stays bare, and its
    bare families and tokens are everybody's to join. A proc or a ref is a BASE by its
    bare name, ONE across the packages -- `name-ambiguous` otherwise. Nothing written."""
    joinable = _base_bare_names(named, read, base)

    def refuse(owner: str, where: str, kind: str, name: str, form: str) -> None:
        raise Refusal("name-unprefixed",
                      f"`{owner}` {where}: {kind} `{name}` wears no package's name -- {form}")

    def judge(owner: str, where: str, kind: str, name: str, form: str, lead: str = "") -> None:
        if _prefixed(name, owner, lead) or name in joinable:
            return
        wearer = _wearer(name, named, lead)
        if wearer is None or wearer == base:
            refuse(owner, where, kind, name, form)
        if wearer not in closures[owner]:
            raise Refusal("dependency-undeclared",
                          f"`{owner}` {where}: {kind} `{name}` joins `{wearer}`'s and `{owner}` "
                          f"does not require it (requires: {sorted(closures[owner] - {owner}) or 'nothing'})")

    for package, root in named.items():
        if package == base:
            continue                                   # the base is bare by rule
        for entry in contributions.contributions(instance.manifest_of(root)):
            if entry["kind"] == "commands":
                verb = str(entry["verb"])
                if not _prefixed(verb, package):
                    refuse(package, "package.yaml", "verb", verb,
                           f"a console verb is `{package}-<verb>` (or `{package}` alone)")
            elif entry["kind"] == "events":
                for family in ((entry.get("value") or {}).get("vectors") or {}):
                    judge(package, "package.yaml", "family", str(family),
                          f"a vector family is `{package}-<family>:` (or `{package}:`); another "
                          "package's is joined under ITS prefix")
        for contract in sorted((root / "skills").glob("*/SKILL.md")):
            stem = contract.parent.name
            if not _prefixed(stem, package, SKILL_LEAD):
                refuse(package, f"skills/{stem}", "skill", stem,
                       f"a skill is `{SKILL_LEAD}{package}` (or `{SKILL_LEAD}{package}-<name>`)")
    for path, owner, front in read:
        if owner in (INSTANCE, base):
            continue                                   # the instance is the top, the base is bare
        where = str(path.relative_to(named[owner]))
        for key in ("provides", "payloads"):
            for token in str(front.get(key) or "").split():
                judge(owner, where, "token", token,
                      f"a payload token is `{owner}-<token>` (or `{owner}` alone); another "
                      "package's is named under ITS prefix")
    bases: dict[tuple[str, str], str] = {}
    for package, root in named.items():
        for space in BASE_SPACES:
            for path in sorted((root / space).glob("*.md")):
                if path.name.startswith("_"):
                    continue
                held = bases.setdefault((space, path.name), package)
                if held != package:
                    raise Refusal("name-ambiguous",
                                  f"`{path.name}` is carried under `{space}/` by `{held}` and "
                                  f"`{package}` -- a base is ONE document across the packages; "
                                  "a package amends another's under `overlays/`, by the source name")


# --- the gate ----------------------------------------------------------------------

_TEMPLATE: Path | None = None     # the instance template a fresh install seeds from, while it judges


def validate(meta: Path, roots: list[Path] | None = None, template: Path | None = None) -> list[dict]:
    """The contract's gate, WHOLE: the manifests judged by `contributions.validate`,
    then every reference of every document and manifest resolved to its owner --
    `dependency-undeclared`, `reference-unknown`, `socket-undeclared` by name,
    the names a package exposes judged on the way (`name-unprefixed`,
    `name-ambiguous`), nothing written. -> the composed contributions when everything holds.
    `template` is the instance template a FRESH install seeds from: judged before
    the seeding, its documents (MEMBER.md, FORMATS.md) are the instance's own."""
    global _TEMPLATE
    _TEMPLATE = template
    try:
        return _validate(meta, roots)
    finally:
        _TEMPLATE = None


def _validate(meta: Path, roots: list[Path] | None) -> list[dict]:
    composed = contributions.validate(meta, roots)
    named = _roots(meta, roots)
    closures = {name: closure(named, name) for name in named}
    closures[INSTANCE] = set(named)
    read = [(path, owner, front) for path, owner in _documents(meta, named)
            if (front := _front(path)) is not None]     # one read per document
    formats = _format_owners(read)
    keys = _key_owners(meta, named)
    sockets = _socket_owners(named)
    seen: dict[str, str] = {}
    for package, root in named.items():
        # one owner per skill NAME: `skill_contract` takes the first hit, so two packages
        # carrying one name would make which of them serves a `with:` an accident of order
        for contract in sorted((root / "skills").glob("*/SKILL.md")):
            stem = contract.parent.name
            if stem in seen:
                raise Refusal("skill-taken",
                              f"`{stem}` is carried by `{seen[stem]}` and `{package}` -- "
                              "one owner per skill name")
            seen[stem] = package
    homes = _document_homes(meta, named)
    owners: dict[tuple[str, tuple], str | None] = {}

    def document_owner(name: str, spaces=DOCUMENT_SPACES) -> str | None:
        # resolved once per name: a CALL repeated across the composition stats once
        key = (name, spaces)
        if key not in owners:
            hits = [owner for home, owner in (homes if spaces == DOCUMENT_SPACES
                                              else _document_homes(meta, named, spaces))
                    if (home / name).is_file()]
            owners[key] = hits[-1] if hits else None
        return owners[key]

    def tool_owner(name: str) -> str | None:
        owner = document_owner(f"{name}.md", ("procs",))
        return owner if owner is not None else _skill_owner(name, meta, named)

    def judge(owner: str, where: str, kind: str, name: str, target: str | None) -> None:
        if target is None:
            raise Refusal("reference-unknown",
                          f"`{owner}` {where}: {kind} `{name}` resolves nowhere in the composition")
        if target in (INSTANCE, ENGINE, owner) or target in closures[owner]:
            return
        raise Refusal("dependency-undeclared",
                      f"`{owner}` {where}: {kind} `{name}` belongs to `{target}` and `{owner}` "
                      f"does not require it (requires: {sorted(closures[owner] - {owner}) or 'nothing'})")

    for path, owner, front in read:
        where = str(path.relative_to(named[owner])) if owner != INSTANCE else str(path.relative_to(meta))
        if owner != INSTANCE and path.parent.name in OVERLAY_SPACES:
            judge(owner, where, "overlay of", path.name, document_owner(path.name, ("procs",)))
        _judge_exec(owner, where, path, front, meta, named)
        _judge_field(owner, where, path, front)
        _judge_next(owner, where, path, front, meta, named)
        provides = str(front.get("provides") or "").split()
        said = str(front.get("with") or "").split()
        if provides and not said:
            raise Refusal("contribution-malformed",
                          f"`{owner}` {where} provides `{provides[0]}` and declares no "
                          "`with:` -- a provider names the skill that serves its token")
        if said and not provides:
            raise Refusal("contribution-malformed",
                          f"`{owner}` {where} declares `with: {said[0]}` and provides no "
                          "token -- a `with:` serves a `provides:`")
        if said:
            home = _skill_owner(said[0], meta, named)
            if home is None:
                raise Refusal("reference-unknown",
                              f"`{owner}` {where}: with `{said[0]}` resolves nowhere in the composition")
            if home != owner:
                # a package declares what it OWNS: borrowing a neighbour's tool would
                # make the neighbour's absence a silent hole in this one's contribution
                raise Refusal("with-foreign",
                              f"`{owner}` {where}: `with: {said[0]}` names a skill of "
                              f"`{home}` -- a document serves its token with a skill of its own package")
        if front.get("attach") and front.get("mount"):
            # the two entry verbs are EXCLUSIVE: the author chooses knowingly, and a
            # document that declared both would be called AND hosted at the same socket
            raise Refusal("attach-and-mount",
                          f"`{owner}` {where} declares `attach:` and `mount:` together -- keep "
                          "one: `attach:` calls the document at its socket, `mount:` enters it")
        for kind, name in references(path, front):
            if kind == "call":
                judge(owner, where, "CALL", name, document_owner(name))
            elif kind == "serve":
                if "/" in name:
                    continue       # a path serves the repository: the instance's matter
                target = document_owner(name)
                if target is not None:
                    judge(owner, where, "SERVE", name, target)
            elif kind == "tool":
                target = tool_owner(name)
                if owner == INSTANCE and target is None:
                    continue       # the instance may offer what its harness carries
                judge(owner, where, "offer", name, target)
            elif kind == "offer+":
                target = tool_owner(name)
                if target is not None:
                    judge(owner, where, "offer", name, target)
            elif kind == "hook":
                # the proc writes `<proc>.<hook>` and the manifest declares the same pair:
                # the comparison happens INSIDE the package, the address serves those outside
                if owner != INSTANCE and sockets.get(contributions.address(owner, name)) != owner:
                    raise Refusal("socket-undeclared",
                                  f"`{owner}` {where}: HOOK `{name}` -- the manifest declares no "
                                  "such socket (contributes.sockets)")
            elif kind in ("attach", "mount"):
                judge(owner, where, kind, name, sockets.get(name) if owner != INSTANCE else INSTANCE)
            elif kind == "sink":
                judge(owner, where, "sink", name, _skill_owner(name, meta, named))
            elif kind == "format":
                judge(owner, where, "format", name, formats.get(name))
            elif kind == "key":
                judge(owner, where, "key", name, keys.get(name))
    for owner, root in named.items():
        for kind, name in _manifest_references(instance.manifest_of(root)):
            if kind == "socket":
                judge(owner, "package.yaml", "socket", name, sockets.get(name))
            elif kind == "call":
                judge(owner, "package.yaml", "document", name, document_owner(name))
            elif kind == "skill":
                judge(owner, "package.yaml", "skill", name, _skill_owner(name, meta, named))
        for path in sorted((root / "refs").glob("*.md")):
            # a ref carries no flow and is judged for nothing else -- an `exec:` there
            # would never play, and the build says so
            front = None if path.name.startswith("_") else _front(path)
            if front is not None:
                _judge_exec(owner, str(path.relative_to(root)), path, front, meta, named)
    _judge_graph(read)                                             # the edges held: the graph
    _naming(meta, named, closures, read, instance.base_of(meta))   # the references held: now
    return composed                                                # the names a package exposes (KPS31)
