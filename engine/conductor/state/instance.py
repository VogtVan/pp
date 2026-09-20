"""The INSTANCE: what a member's directory declares, and where its documents resolve.

An instance is a directory (its NAME is a parameter -- `.pp` is the CLI's default).
Its ROOT belongs to the operator: MEMBER.md, SETTINGS.md, FORMATS.md and `procs/`,
nothing else. THE MACHINE lives under `.sys/`: the engine, the manifest
(`instance.yaml` -- source and pins), the read-only bundles (`vendor/`), the data
records (`records/`), the run state (`state/`) and the compiled catalogs.
"""
from __future__ import annotations

import copy
import re
from pathlib import Path

import yaml

from ..core import language
from ..core.errors import Refusal
from ..core.model import INSTANCE_DIRECTORY as DIRECTORY   # the instance directory's name, said once

SYS = ".sys"                          # the machine's own directory, under the meta root
MANIFEST = ".sys/instance.yaml"       # marks a directory as an instance
PACKAGE_MANIFEST = "package.yaml"     # marks a directory as a package
VENDOR = ".sys/vendor"
RECORDS = ".sys/records"              # the records the packages seed and write
STATE = ".sys/state"                  # session.json · session-<UTC>.jsonl (the trace)
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def is_instance(meta: Path) -> bool:
    return (meta / MANIFEST).is_file()


def kebab(name: str) -> str:
    """-> `name` normalized to kebab-case: lowercase, runs of anything not alnum become
    one `-`, leading/trailing `-` trimmed."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def valid_slug(value: str) -> bool:
    """-> whether `value` is strict kebab-case (lowercase alnum runs, single dashes)."""
    return bool(SLUG_RE.fullmatch(value))


def slug(meta: Path) -> str:
    """-> this member's slug: declared in `instance.yaml` if it carries one, else derived
    from its workspace directory's name -- a targeted read, never wired into `Member`."""
    declared = str(read(meta).get("slug") or "") if is_instance(meta) else ""
    return declared or kebab(meta.parent.name)


_parsed: dict[str, tuple[bytes, object]] = {}
# the manifests this process has parsed, by path: the BYTES they were parsed from
# beside the value -- a deferred read, never a parallel truth (nothing to evict)


def _manifest(path: Path) -> object:
    """-> `path` parsed as YAML, once per STATE of the file. The bytes are read at
    every call and decide alone: identical bytes hand back the parse already made,
    a rewritten file is parsed again at the next call -- by the engine's own writer
    or by hand, in this process or another. A read costs microseconds, a parse
    milliseconds: a call resolving names reads its manifests dozens of times,
    and parses each once. The caller gets its own copy: the memo is never handed
    out, so a declaration a verb edits before writing back cannot leak into it."""
    # the bytes, not a stat signature: two same-size rewrites within one clock
    # tick (the bench does it) wear the same (mtime_ns, size) -- the content never lies
    raw = path.read_bytes()
    held = _parsed.get(str(path))
    if held is None or held[0] != raw:
        held = (raw, yaml.safe_load(raw.decode("utf-8")) or {})
        _parsed[str(path)] = held
    return copy.deepcopy(held[1])


def read(meta: Path) -> dict:
    """-> the instance's declaration. Missing = not an instance; malformed = a refusal."""
    path = meta / MANIFEST
    if not path.is_file():
        raise Refusal("instance-missing", f"{meta} carries no {MANIFEST}")
    loaded = _manifest(path)
    if not isinstance(loaded, dict):
        raise Refusal("instance-malformed", f"{path} is not a mapping")
    return loaded


def write(meta: Path, declared: dict) -> None:
    """Persists the instance's declaration -- the ONLY writer, so `source:`/`slug:`/
    `root:`/whatever else it carries never gets dropped by a partial rewrite."""
    (meta / MANIFEST).parent.mkdir(parents=True, exist_ok=True)
    (meta / MANIFEST).write_text(yaml.safe_dump(declared, sort_keys=False), encoding="utf-8")


def manifest_of(package_root: Path) -> dict:
    """-> a package's declaration -- name, version, description, requires."""
    path = package_root / PACKAGE_MANIFEST
    if not path.is_file():
        raise Refusal("package-unmanifested", f"{package_root} carries no {PACKAGE_MANIFEST}")
    loaded = _manifest(path)
    if not isinstance(loaded, dict):
        raise Refusal("package-unmanifested", f"{path} is not a mapping")
    for key in ("name", "version"):
        if not loaded.get(key):
            raise Refusal("package-unmanifested", f"{path} declares no `{key}`")
    return loaded


def base_of(meta: Path) -> str:
    """The BASE package's name at this instance -- the role the engine resolves the
    base by: `base:` in instance.yaml when an operator replaced the kit, the role's
    default (`language.BASE`) otherwise."""
    try:
        return read(meta).get("base") or language.BASE
    except Exception:                                        # an uninstalled meta
        return language.BASE


def pins(meta: Path) -> dict[str, str]:
    """-> {package name: pinned version} as the instance declares them."""
    declared = read(meta).get("packages") or {}
    if not isinstance(declared, dict):
        raise Refusal("instance-malformed", f"{meta / MANIFEST}: `packages` is not a mapping")
    return {str(name): str(version) for name, version in declared.items()}


def vendored(meta: Path, held: dict[str, str] | None = None,
             switched: bool = True) -> list[Path]:
    """-> the materialized package roots in the REQUIRES topology, dependencies
    first -- the foundation aggregates before its clients (system, catalogs);
    `search_paths` walks it REVERSED so a client's space is NEARER and its
    overlay amends its dependency's and wins. Ties keep the pin order (stable).
    A pin without its bundle refuses: a declared package that is not there
    would silently amputate the procedural layer. The composition is read
    CLOSED: a pin whose prerequisite is not pinned refuses too -- the topology
    never lies by omission. `held` reads a composition OTHER than the pinned
    one (a call validating its target before writing it).

    The SWITCHES apply here and nowhere else: a package switched off -- at
    SETTINGS (`package.<name>: off`) or for the run being played -- leaves the
    list with every package that requires it, so whatever reads the composition
    plays without them. `switched=False` reads the WHOLE composition: what
    installs, syncs and removes sees every pin, since off is not gone."""
    if not is_instance(meta):
        return []
    if held is None:
        held = pins(meta)
    roots = {}
    for name, version in held.items():
        root = meta / VENDOR / f"{name}@{version}"
        if not root.is_dir():
            raise Refusal("package-missing",
                          f"`{name}@{version}` is pinned but not under {meta / VENDOR} -- "
                          "run `./pp doctor`")
        roots[name] = root
    whole = ordered(roots)
    if not switched:
        return whole
    off = _off(meta, whole)
    return [root for root in whole if _name_of(root) not in off]


SWITCH_KEY = "package."     # the engine's name-keyed family at SETTINGS: `package.<name>: on|off`
_SOFT_OFF: dict[str, frozenset] = {}   # instance -> the packages the run being played
                                       # switched off; no run, no entry


def play_off(meta: Path, names) -> None:
    """The SOFT switches of the run being played at `meta`, set from its slot before
    anything reads the composition; an empty set plays every pin. One entry per
    instance: a process driving two instances keeps their plays apart."""
    held = frozenset(str(one) for one in names)
    if held:
        _SOFT_OFF[str(meta)] = held
    else:
        _SOFT_OFF.pop(str(meta), None)


def soft_off(meta: Path) -> frozenset:
    """-> the packages the run being played switched off, none outside a run."""
    return _SOFT_OFF.get(str(meta), frozenset())


def hard_off(meta: Path) -> frozenset[str]:
    """-> the packages the instance's SETTINGS switches off: `package.<name>: off`.
    `on` plays, an absent key plays; any other value refuses `settings-invalid`, and
    so does `off` on the base -- every instance stands on it."""
    from ..core.document import read as read_document      # local import: reading stays below instance for documents
    path = meta / "SETTINGS.md"
    if not path.is_file():
        return frozenset()
    found = set()
    for key, value in read_document(path).front.items():
        if not (isinstance(key, str) and key.startswith(SWITCH_KEY)):
            continue
        name = key[len(SWITCH_KEY):].strip()
        if isinstance(value, bool):          # YAML reads a bare on/off as a boolean
            said = "on" if value else "off"
        else:
            said = str(value if value is not None else "").strip().lower()
        if not name or said not in ("on", "off"):
            raise Refusal("settings-invalid",
                          f"`{key}: {value}` -- a package switch is `package.<name>: on|off`")
        if said == "off" and name == base_of(meta):
            raise Refusal("settings-invalid",
                          f"`{key}: off` -- `{name}` is the base of every instance, never switched off")
        if said == "off":
            found.add(name)
    return frozenset(found)


def switched_off(meta: Path, held: dict[str, str] | None = None) -> dict[str, str]:
    """-> {package: cause} for every pinned package the run does NOT play: the hard
    switches of SETTINGS and the soft ones of the run, closed over their DEPENDENTS --
    a package whose `requires` names an off package is off too, its cause that
    package; a switched package is its own cause; the base never leaves."""
    return _off(meta, vendored(meta, held, switched=False))


def _off(meta: Path, whole: list[Path]) -> dict[str, str]:
    """The one pass, dependencies first: a root switched off by name, or requiring a
    root already off, is off -- `whole` is the ordered composition."""
    named = hard_off(meta) | soft_off(meta)
    base = base_of(meta)
    off: dict[str, str] = {}
    for root in whole:
        name = _name_of(root)
        if name == base:
            continue
        if name in named:
            off[name] = name
            continue
        try:
            needs = manifest_of(root).get("requires") or []
        except Refusal:
            needs = []
        cause = next((str(one) for one in needs if str(one) in off), None)
        if cause is not None:
            off[name] = cause
    return off


def _name_of(root: Path) -> str:
    """-> a vendored root's package name: its manifest's, else the `<name>@` of its directory."""
    return _named(root) or root.name.split("@")[0]


def ordered(roots: dict[str, Path]) -> list[Path]:
    """-> `roots` (name -> package root) in the REQUIRES topology, dependencies
    first, ties in the given order. A prerequisite missing from `roots` refuses
    `package-required` -- never filtered in silence -- and a loop refuses
    `package-cycle`."""
    def needs_of(name: str) -> list[str]:
        try:
            declared = manifest_of(roots[name]).get("requires") or []
        except Refusal:
            declared = []          # an unmanifested bundle sorts as a leaf
        absent = [one for one in declared if one not in roots]
        if absent:
            # the silent filter is gone: a declared prerequisite that is not
            # pinned makes the composition a lie -- the call is named instead
            raise Refusal("package-required",
                          f"`{name}` requires `{absent[0]}`, which is not pinned -- "
                          f"`./pp add {absent[0]}` closes the composition (or `./pp doctor`)")
        return list(declared)

    needs = {name: needs_of(name) for name in roots}

    def depth(name: str, walked: tuple = ()) -> int:
        if name in walked:
            raise Refusal("package-cycle",
                          f"`{name}` -- the requires of the pinned packages loop")
        return 1 + max((depth(one, walked + (name,)) for one in needs[name]), default=-1)

    ranked = sorted(roots, key=depth)          # stable: ties keep the pin order
    return [roots[name] for name in ranked]


def search_paths(meta: Path) -> list[Path]:
    """Where a document name resolves, in order: the instance's own space first (the
    user can always add), then the machine's compiled catalogs (servable by name),
    then every vendored package's OVERLAYS -- the packages' own overlay space,
    interposed so a same-name file there is always NEARER than any package base
    (it can never become the base, and the user's space still applies last) --
    then the packages' procs, then their refs. The packages walk the REQUIRES
    topology reversed: a client's space is NEARER than its dependency's, so its
    overlay applies after and wins -- never the pin order."""
    paths = [meta, meta / "procs", meta / SYS]
    packages = list(reversed(vendored(meta)))
    paths += [root / "overlays" for root in packages]
    paths += [root / "procs" for root in packages]
    paths += [root / "refs" for root in packages]
    return [path for path in paths if path.is_dir()] or [meta]


def chain(meta: Path, name: str) -> list[Path]:
    """-> every hit of `name` across the search paths, nearest space first."""
    return [base / name for base in search_paths(meta) if (base / name).is_file()]


def resolve(meta: Path, name: str) -> Path:
    """-> the BASE document: the deepest hit -- a same-name file in a nearer space is an
    OVERLAY of it (deltas on its sections), never a shadow. Plain meta path when no hit
    (so the caller's refusal names the canonical location)."""
    hits = chain(meta, name)
    return hits[-1] if hits else meta / name


def overlays_of(meta: Path, name: str) -> list[Path]:
    """-> the overlays of `name`, deepest first -- the nearest space applies LAST (wins)."""
    return list(reversed(chain(meta, name)[:-1]))


def attached(meta: Path, hook: str) -> tuple[str, ...]:
    """-> the NAMES of every document declaring `attach: <hook>` -- the contributors a
    HOOK CALLS. Order and scan are `_declaring`'s."""
    return _declaring(meta, hook, "attach")


def mounting(meta: Path, hook: str) -> tuple[str, ...]:
    """-> the NAMES of every document declaring `mount: <hook>` -- the contributors a
    HOOK MOUNTS instead of calling: each one enters the view at the socket, its laws
    in force and its matter served, and it asks the agent nothing. Same scan and same
    order as `attached`: one socket, one list of contributors."""
    return _declaring(meta, hook, "mount")


def _declaring(meta: Path, hook: str, key: str) -> tuple[str, ...]:
    """-> the NAMES of every document whose front matter `key` names `hook` -- what a
    HOOK expands into, in `documents`' own order."""
    found: list[str] = []
    for name, _path, _package, front in documents(meta):
        if hook in str(front.get(key, "")).split() and name not in found:
            found.append(name)
    return tuple(found)


def documents(meta: Path) -> list[tuple[str, Path, str | None, dict]]:
    """-> (name, path, owning package, front matter) for every DECLARING document of the
    composition, in the REQUIRES topology of their homes (a dependency's before its
    clients', the instance's own space last) and by name within one home -- the one
    order every reader of what documents declare plays. The scan is live: dropping a
    proc in `procs/` is enough.

    documentary: what a document declares -- its socket, the token it provides, the skill
    that serves it -- is read HERE and nowhere else, so a new declaration costs its key
    and no second walk."""
    from ..core.document import read as read_document      # local import: reading stays below instance for documents
    found: list[tuple[str, Path, str | None, dict]] = []
    seen: set[str] = set()
    homes: list[tuple[str | None, Path]] = [(_named(root), root / "procs") for root in vendored(meta)]
    homes += [(None, meta / "procs"), (None, meta)]
    for package, base in homes:
        if not base.is_dir():
            continue
        for path in sorted(base.glob("*.md")):
            if path.name.startswith("_") or path.name in seen:
                continue       # a `_` file is a working file: never scanned, nowhere
            try:
                document = read_document(path)
            except Exception:
                continue       # no front matter, or malformed: it declares nothing
            seen.add(path.name)
            found.append((path.name, path, package, document.front))
    return found


def _named(root: Path) -> str | None:
    """-> the package name a vendored root manifests, None when it manifests nothing."""
    try:
        return str(manifest_of(root).get("name") or "") or None
    except Exception:
        return None


ORDER_RELATIONS = ("before", "after")   # what a preference may say, and nothing else


def preferences(meta: Path, name: str, hook: str) -> list[tuple[str, str]]:
    """-> the ORDER preferences the contributor `name` declares for `hook` -- the
    `order:` block of its own front matter, one line per pair, `<hook> before|after
    <package>`. The peer is named by its PACKAGE, never by a socket nor a path.

    documentary: the preference lives where the guard lives -- at the CONTRIBUTOR, in the
    same front matter as `when:` -- because the socket knows nothing of the packages that
    reach it, and an order is a condition of the same kind as a guard."""
    return preferences_of(resolve(meta, name), hook, name)


def preferences_of(path: Path, hook: str, said: str | None = None) -> list[tuple[str, str]]:
    """-> the ORDER preferences the FILE at `path` declares for `hook`, read at that file
    and no other: a contributor's are read at its resolved base, the declarants of
    several `exec:` on one document each at their own file -- the base and every
    overlay. `said` names the file in a refusal."""
    from ..core.document import read as read_document      # local import: reading stays below instance
    try:
        document = read_document(path)
    except Exception:
        return []                  # unreadable: it declares nothing, like an absent `attach:`
    found = []
    for line in str(document.front.get("order", "")).splitlines():
        words = line.split()
        if not words:
            continue
        if len(words) != 3 or words[1] not in ORDER_RELATIONS:
            raise Refusal("order-invalid",
                          f"`{line.strip()}` at {said or path.name} -- an order is "
                          "`<hook> before|after <package>`")
        if words[0] == hook:
            found.append((words[1], words[2]))
    return found


def ordering(meta: Path, hook: str, names: list[str]) -> list[str]:
    """-> the contributors of `hook`, DERIVED order first, re-ordered by the preferences
    each one declares. The derived order is the default and survives everything a
    preference does not constrain -- the sort is stable, so a composition that declares
    nothing renders exactly as before. A preference toward a package the composition
    lacks is INERT: a preference is no dependency and never becomes one. Two
    contributors that each want to come first refuse `order-cycle`, both named.

    documentary: this is what replaces an accident -- until now the order of a socket fell
    out of the requires topology and, between equals, out of the pin order of the
    instance; a client that PRODUCES what its dependency renders had no way to say so."""
    if len(names) < 2:
        return list(names)
    homes = {str(root): i for i, root in enumerate(vendored(meta))}
    owner, home = {}, {}
    for one in names:
        try:
            root = package_of(resolve(meta, one))
        except Exception:
            root = None
        # the HOME decides the derived rank -- where a contributor was DECLARED (a manifest
        # `hooks:` or its own `attach:`) decides nothing: one list, one order
        owner[one], home[one] = _home_of(homes, root)
    return _ordered(hook, names, owner, home, lambda one: preferences(meta, one, hook))


def exec_order(meta: Path, files: list[Path]) -> list[Path]:
    """-> the DECLARANTS of `exec:` on one document -- its base file and the overlays of
    its name -- in the order their exec play: the derived order of their homes (the
    requires topology, the instance's own file last), re-ordered by the preferences each
    file declares under `order:` with the word `exec` in the socket's place. The rule of
    a socket's contributors, read at each declarant's OWN file."""
    if len(files) < 2:
        return list(files)
    homes = {str(root): i for i, root in enumerate(vendored(meta))}
    owner, home = {}, {}
    for one in files:
        owner[one], home[one] = _home_of(homes, package_of(one))
    return _ordered("exec", files, owner, home, lambda one: preferences_of(one, "exec"))


def _home_of(homes: dict[str, int], root: Path | None) -> tuple[str, int]:
    """-> (the owning package's name, its rank in the topology) of a package root; the
    instance owns nothing by name and ranks last."""
    if root is None:
        return "", len(homes)
    return str(manifest_of(root)["name"]), homes.get(str(root), len(homes))


def _ordered(hook: str, items: list, owner: dict, home: dict, preferences_of_item) -> list:
    """The ONE ordering: `items` sorted by their home's rank (stable), then re-ordered by
    the `before|after <package>` preferences each item declares -- a peer no item's owner
    wears is inert; a loop refuses `order-cycle`, both parties named."""
    items = sorted(items, key=lambda one: home[one])      # stable: a home keeps its own order
    edges = {one: set() for one in items}        # item -> the items that must follow it
    for one in items:
        for relation, peer in preferences_of_item(one):
            for other in items:
                if other == one or owner.get(other) != peer:
                    continue        # an unknown peer names nobody: the preference is inert
                (edges[one] if relation == "before" else edges[other]).add(
                    other if relation == "before" else one)
    rank = {one: i for i, one in enumerate(items)}
    waiting = {one: sum(1 for src in items if one in edges[src]) for one in items}
    ready = sorted((one for one in items if not waiting[one]), key=rank.get)
    out = []
    while ready:
        one = ready.pop(0)
        out.append(one)
        for other in sorted(edges[one], key=rank.get):
            waiting[other] -= 1
            if not waiting[other]:
                ready.append(other)
        ready.sort(key=rank.get)
    if len(out) != len(items):
        stuck = sorted((one for one in items if one not in out), key=rank.get)
        said = [getattr(one, "name", one) for one in stuck]
        raise Refusal("order-cycle",
                      f"`{said[0]}` and `{said[1] if len(said) > 1 else said[0]}` "
                      f"at `{hook}` -- their order preferences loop")
    return out


def package_of(path: Path) -> Path | None:
    """-> the package root `path` belongs to (the nearest ancestor carrying a manifest)."""
    for ancestor in path.parents:
        if (ancestor / PACKAGE_MANIFEST).is_file():
            return ancestor
    return None


HARNESS_HOMES = (".claude/skills", ".agents/skills", ".cursor/skills")
# the STANDARD skill directories of the workspace's harnesses -- where an OFFERED
# name may resolve (adoption); pp never sweeps them: the offer is the consent


def skill_contract(meta: Path, stem: str) -> Path | None:
    """-> the SKILL.md contract `stem` names in this instance -- its own `skills/`
    first, then each vendored package's."""
    for home in [meta] + vendored(meta):
        contract = home / "skills" / stem / "SKILL.md"
        if contract.is_file():
            return contract
    return None


def adopted(meta: Path, stem: str) -> Path | None:
    """-> the harness-home contract `stem` resolves to, or None. ADOPTION ON OFFER:
    callers consult this only for a name a `tools:` declares (or an authored CALL
    asks for) -- an unoffered copy stays invisible: the indifference invariant
    guards the sweep, the offer is the consent to read THIS one skill."""
    for home in HARNESS_HOMES:
        contract = meta.parent / home / stem / "SKILL.md"
        if contract.is_file():
            return contract
    return None
