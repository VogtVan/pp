"""What can be tuned without touching behaviour -- and WHERE: the instance's own
`SETTINGS.md`, the operator's VALUES in the product's SHAPE -- seeded at
install, re-shaped at every upgrade and doctor, no chosen value rewritten. The
conductor serves a replaceable BASE package; the PROTOCOL keys here are the
conductor's own, bare, documented once.

The constants here are the DEFAULTS: an instance with no `SETTINGS.md` (or a key
left out) plays exactly as before. A value that does not parse REFUSES -- a typo
silently falling back to a default would be a lie.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from ..core import document as documents
from . import instance
from ..core import language
from ..core.errors import Refusal

SEEDS = (("conduction_effort", "medium"),
         ("max_harness_tool_output", "25000"), ("proc_body_serve", "always"),
         ("work_repairs_allowed", "3"), ("instructions_fusion", "none"),
         ("verbatim_constraints", "true"), ("conduction", "strict"))
                        # the PROTOCOL's keys alone: a policy's key (the reflex,
                        # the records' cadence, the digest's anchor) lives at the
                        # fragment of the package that owns it, the kit's included
                        # the keys every synced SETTINGS front matter carries,
                        # each VALUED at the engine default the absent key played
                        # (operator word 2026-08-22: no key absent, none empty) --
                        # the TEMPLATE seeds the product defaults for NEW installs
                        # (effort medium), the sync of a LIVING instance arrives
                        # the behaviour it already had; a key the operator killed
                        # is no seed: a living instance that still carries it
                        # keeps it as an unowned stranger, the operator removes
                        # it (KPS14 -- the engine migrates nothing)

HARNESS_CAP = 25000    # characters ONE tool output may hold at the HOST -- the engine
                       # measures the block it is about to hand over and cuts it under
                       # this, the rest coming back on a bare call. A fact of the host,
                       # not of pp: Claude Code's VS Code extension persists a result
                       # past 30000, so 25000 leaves the framing its room; another
                       # harness has its own, and the instance declares it
PRINCIPAL_CAP = 200000 # the FLOOR of the cap in a run its principal conducts: the output goes
                       # to the harness on its standard input, no tool output of the host holds
                       # it, and one output is one launch -- no setting lowers it (`served_cap`)
REPAIRS_ALLOWED = 3    # deviations on one instruction, before the operator is handed back to
VERBATIM_CONSTRAINTS = True   # constraints re-emit in every block as their full text;
                              # False = the codes alone -- leaner, and less safe (the
                              # dead-letter risk); the economy is the opt-out
FUSION = 1             # yields rendered per output, the NO-SETTINGS fallback: 1 =
                       # "none" (one step per block -- an instance with no SETTINGS
                       # plays exactly as before); "max" (held 0) fuses the maximal
                       # certain stretch -- the TEMPLATE ships max; a document's own
                       # `fusion:` front-matter key caps ITS frame
WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
SERVE_NATURES = ("code", "reference", "architecture", "diagram", "contract", "map")
                        # the declared document natures a serve row may wear (its
                        # first token, `<nature>:`) -- declared, never inferred; a
                        # DECLARATION alone: every row serves, no regime holds one
MATERIAL_REPO = "repo"  # the MATERIALS a reading may name: `repo` is the repository around the
MATERIAL_WORK = "work"  # instance, tacit; `work` the launcher's, at the slot; any other name is
                        # the operator's, declared `material.<name>: <path>` at SETTINGS
CONDUCTION = "strict"   # where an output the AGENT's call renders goes, in a run its principal
CONDUCTIONS = ("strict", "hybrid")   # conducts: `strict` holds every one for the principal's call;
                        # `hybrid` answers in the tool result the one whose closing asks the
                        # agent a value (a proof, a field, a choice, a production a consumer
                        # takes), cut under the host's cap -- an output that moves the run on
                        # (a bare CONTINUE, a FINAL, a FREE step said to the chat) stays held.
                        # The LLM's mode reads none of it
CALL_LOCK_WAIT = 30     # seconds a keyed call WAITS for the run's call lock another call
                        # holds, before it refuses `call-busy` -- under the harness's own
                        # patience for one tool call
BODY_SERVE = "always"   # how a CALLed proc's BODY comes with: "always" (at every CALL --
                        # the brief re-read each time) or "once" (proven by its
                        # content like any reading: a body already proven in the run
                        # renders nothing) -- the effort presets it, light and medium to "once"
CONDUCTION_EFFORT = ""  # HOW LEAN the conducted blocks render: light | medium |
                        # full preset the weight knobs; `none` (explicit) or
                        # absent, the keys rule -- a key the effort does not name
                        # stays the operator's
EFFORTS = {             # the PROTOCOL's weight keys -- the engine's own; every
                        # package, the kit included, adds its keys to a level in
                        # its fragment's `effort:` block
    "light":  {"verbatim_constraints": False, "instructions_fusion": "max",
               "proc_body_serve": "once"},
    "medium": {"verbatim_constraints": False, "instructions_fusion": "max",
               "proc_body_serve": "once"},
    "full":   {"verbatim_constraints": True, "instructions_fusion": "none",
               "proc_body_serve": "always"},
}                       # a policy's weight key (the reflex, the records' cadence,
                        # the kit's capture of the prompt) is preset by its OWNER's
                        # fragment `effort:` block
DOCUMENT = "SETTINGS.md"


@dataclass(frozen=True)
class Settings:
    harness_cap: int = HARNESS_CAP
    repairs_allowed: int = REPAIRS_ALLOWED
    verbatim_constraints: bool = VERBATIM_CONSTRAINTS
    fusion: int = FUSION     # 0 = max
    effort: str = CONDUCTION_EFFORT
    body_serve: str = BODY_SERVE   # "always" | "once": whether a CALLed body proven
                                   # in this run comes with again
    call_lock_wait: int = CALL_LOCK_WAIT   # seconds a keyed call waits for the run's call lock
    conduction: str = CONDUCTION   # "strict" | "hybrid": whether an output asking the agent a value
                                   # comes back in its tool result (a run its principal conducts)
    sector_caps: tuple = ()   # the operator's `cap.<sector>` overrides, as pairs --
                              # a named sector's serve cap moves at SETTINGS, never in code
    switches: tuple = ()      # the packages SETTINGS switches off (`package.<name>: off`),
                              # sorted -- the ONE reader is instance.hard_off; off is not gone
    packages: tuple = ()      # the packages' own keys, parsed by their fragment's type,
                              # as (key, value) pairs -- `plan_…`: the prefix
                              # names the owner
    materials: tuple = ()     # the operator's MATERIALS, `material.<name>: <path>` as
                              # (name, path) pairs -- the trees a serve row may read from
                              # by `@<name>`; `repo` and `work` are the engine's, never here

    def of_package(self, key: str, default=None):
        """-> a package key's parsed value (`plan_implementation_care`), or default."""
        for name, value in self.packages:
            if name == key:
                return value
        return default


def effective(front: dict, meta: Path | None = None) -> dict:
    """-> the front matter with the EFFORT's presets IN POWER: `conduction_effort`
    presets the weight knobs, and an absent key hands the operator's own the
    power. A package FRAGMENT (`meta` given) adds its own keys to a level. Every reader of
    SETTINGS front matter goes through here, the typed settings and the
    `@SETTINGS.<key>` guards alike. A key nobody declares any more is a MIGRATION of
    the operator's, flagged at the plan that renamed it -- pp carries no table of what
    a key used to be called."""
    found = fragments(meta) if meta is not None else ()
    merged = dict(front)
    effort = str(front.get("conduction_effort", "") or "").strip().lower()
    if effort and effort != "none":
        # `none` presets nothing: the weight keys rule -- the explicit
        # opt-out, so no key ever needs to stand empty
        if effort not in EFFORTS:
            raise Refusal("settings-invalid",
                          f"`conduction_effort: {effort}` -- `none` or one of: "
                          f"{', '.join(EFFORTS)}")
        merged.update(EFFORTS[effort])
        for one in found:
            for key, levels in one.effort.items():
                if effort in levels:
                    # a fragment's preset arrives parsed by ITS declared type -- an
                    # int where the key is a number -- as the engine's presets do
                    kind = one.types.get(key, "free")
                    merged[key] = typed(key, levels[effort], kind) if kind != "free" else levels[effort]
    return merged


# --- the packages' fragments: data the engine composes, never code --------------------

FRAGMENT = Path("settings") / "SETTINGS.md"   # where a package declares its keys
TYPES = ("flag", "natural", "positive", "one_of", "piped", "free")
META_KEYS = ("name", "kind", "description", "package", "types", "effort")


@dataclass(frozen=True)
class Fragment:
    name: str                 # the package -- and the prefix every key wears
    defaults: tuple           # (key, default) pairs, the fragment's order
    types: dict               # key -> declared type (`flag`, `one_of[a|b]`, ...)
    effort: dict              # key -> {level: value} -- the fragment's own presets
    body: str                 # the package's SECTION of the SETTINGS body


def fragments(meta: Path) -> tuple:
    """-> every vendored package's settings fragment, in the REQUIRES topology
    (dependencies first): `<package>/settings/SETTINGS.md`, read as data. A
    package without one declares no setting. A key outside the package's
    prefix refuses: the prefix is the ownership."""
    from . import instance
    found = []
    base = instance.base_of(meta)      # the base's keys are bare -- the base by ROLE
    for root in instance.vendored(meta, switched=False):   # every pin: off is not gone
        path = root / FRAGMENT
        if not path.is_file():
            continue
        name = str(instance.manifest_of(root)["name"])
        document = documents.read(path)
        front = document.front
        defaults = []
        for key, value in front.items():
            if key in META_KEYS:
                continue
            if name != base and not str(key).startswith(f"{name}_"):
                # the BASE package alone declares its keys bare -- its procs
                # reference them by name; every package beyond prefixes
                raise Refusal("settings-fragment-invalid",
                              f"{path}: `{key}` -- a `{name}` key wears the `{name}_` prefix")
            defaults.append((str(key), _literal(value)))
        declared = {key for key, _ in defaults}
        types = {}
        for key, kind in _pairs(front.get("types")):
            if key not in declared:
                raise Refusal("settings-fragment-invalid",
                              f"{path}: `types` names `{key}`, no such key")
            if kind.split("[", 1)[0] not in TYPES:
                raise Refusal("settings-fragment-invalid",
                              f"{path}: `{key}` -- type `{kind}` is none of: {', '.join(TYPES)}")
            types[key] = kind
        effort = _levels(front.get("effort"), declared, path, EFFORTS)
        body = documents.body_of(path.read_text(encoding="utf-8"))
        found.append(Fragment(name, tuple(defaults), types, effort, body))
    return tuple(found)


def _literal(value) -> str:
    """-> a default as the file spells it: YAML reads `true` as a bool, the
    composer writes it back lowercase -- never Python's `True`."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _pairs(block) -> list:
    """-> the (first token, rest) pairs of a piped-style block, one per line."""
    out = []
    for line in str(block or "").splitlines():
        parts = line.split(None, 1)
        if len(parts) == 2:
            out.append((parts[0].strip(), parts[1].strip()))
        elif parts:
            out.append((parts[0].strip(), ""))
    return out


def _levels(block, declared: set, path: Path, vocabulary: dict) -> dict:
    """-> key -> {level: value} from a `key  light=3 medium=3 full=1` block."""
    found = {}
    for key, rest in _pairs(block):
        if key not in declared:
            raise Refusal("settings-fragment-invalid",
                          f"{path}: a preset names `{key}`, no such key")
        levels = {}
        for token in rest.split():
            if "=" not in token:
                raise Refusal("settings-fragment-invalid",
                              f"{path}: `{key}` preset `{token}` -- `<level>=<value>` expected")
            level, value = token.split("=", 1)
            if level not in vocabulary:
                raise Refusal("settings-fragment-invalid",
                              f"{path}: `{key}` preset names `{level}` -- one of: "
                              f"{', '.join(vocabulary)}")
            levels[level] = value
        found[key] = levels
    return found






def referenced(meta: Path, reference: str) -> str:
    """-> the value a `@SETTINGS.<key>` reference names: the instance's own value
    (the profile's presets applied), else the key's default at its owner -- the
    system's seeds or the fragment of the package that declares it. The ONE
    resolver every declaration referencing a setting goes through (a threshold
    of the bus, the anchor of a cadence). An unknown key refuses."""
    if not reference.startswith("@SETTINGS."):
        raise Refusal("reference-invalid", f"`{reference}` -- a reference is `@SETTINGS.<key>`")
    key = reference[len("@SETTINGS."):]
    from .. import reading
    path = instance.resolve(meta, "SETTINGS.md")
    front = reading.read(path).front if path.is_file() else {}
    front = effective(front, meta)
    value = str(front.get(key, "")).strip() or default_of(meta, key)
    if not value:
        raise Refusal("setting-unknown",
                      f"`{reference}` -- no SETTINGS key `{key}` exists, no fragment declares it")
    return value


def default_of(meta: Path, key: str) -> str:
    """-> the default `key` plays when the instance left it out -- the SYSTEM's
    (the install seeds, one table) or the owning fragment's; "" when no one
    owns it. What a `^ @SETTINGS.<key>` guard reads on an absent key."""
    seeded = dict(SEEDS).get(key, "")
    if seeded:
        return seeded
    for one in fragments(meta):
        for name, default in one.defaults:
            if name == key:
                return default
    return ""


def typed(key: str, raw, kind: str):
    """-> `raw` parsed by its fragment type -- a value that does not parse refuses,
    package keys included: a typo silently falling back would be a lie."""
    base, _, inner = kind.partition("[")
    inner = inner.rstrip("]")
    if base == "flag":
        if isinstance(raw, bool):
            return raw
        named = str(raw).strip().lower()
        if named not in ("true", "false"):
            raise Refusal("settings-invalid", f"`{key}: {raw}` -- `true` or `false`")
        return named == "true"
    if base in ("natural", "positive"):
        try:
            value = int(raw)
        except (TypeError, ValueError):
            raise Refusal("settings-invalid", f"`{key}: {raw}` -- not a number")
        floor = 1 if base == "positive" else 0
        if value < floor:
            raise Refusal("settings-invalid", f"`{key}: {value}` -- below {floor}")
        return value
    words = [one.strip() for one in inner.split("|") if one.strip()]
    named = str(raw).strip().lower()
    if base == "one_of":
        if named not in words:
            raise Refusal("settings-invalid",
                          f"`{key}: {raw}` -- one of: {', '.join(words)}")
        return named
    if base == "piped":
        tokens = [one.strip() for one in named.split("|") if one.strip()]
        if not tokens or len(set(tokens)) != len(tokens) \
                or any(one not in words for one in tokens):
            raise Refusal("settings-invalid",
                          f"`{key}: {raw}` -- tokens piped from: {', '.join(words)}")
        return " | ".join(tokens)
    return str(raw).strip()


def package_values(front: dict, found) -> tuple:
    """-> every fragment key as (key, parsed) -- the instance's value, else the
    fragment's default -- validated by the declared type."""
    pairs = []
    for one in found:
        for key, default in one.defaults:
            raw = front.get(key, default)
            kind = one.types.get(key, "free")
            pairs.append((key, typed(key, raw, kind)))
    return tuple(pairs)


def of(meta: Path) -> Settings:
    """-> the instance's tuning: `SETTINGS.md`'s front matter over the defaults."""
    path = meta / DOCUMENT
    if not path.is_file():
        return Settings()
    found = fragments(meta)
    front = effective(documents.read(path).front, meta)
    return Settings(
        packages=package_values(front, found),
        harness_cap=_positive(front, "max_harness_tool_output", HARNESS_CAP),
        repairs_allowed=_positive(front, "work_repairs_allowed", REPAIRS_ALLOWED),
        verbatim_constraints=_flag(front, "verbatim_constraints", VERBATIM_CONSTRAINTS),
        fusion=fusion_of(front.get("instructions_fusion"), key="instructions_fusion"),
        effort=str(front.get("conduction_effort", "") or "").strip().lower(),
        body_serve=_one_of(front, "proc_body_serve", BODY_SERVE, ("always", "once")),
        call_lock_wait=_positive(front, "call_lock_wait", CALL_LOCK_WAIT),
        conduction=_one_of(front, "conduction", CONDUCTION, CONDUCTIONS),
        sector_caps=_sector_caps(front),
        switches=tuple(sorted(instance.hard_off(meta))),
        materials=_materials(front),
    )


def write(meta: Path, key: str, value) -> str:
    """Writes ONE value of the instance's `SETTINGS.md` -- the face a script calls when
    it poses a setting, so that no script opens the file itself. The key is one the
    instance KNOWS (a protocol seed, a pinned fragment's default, a `package.<name>`
    switch, a `cap.<sector>`, a `material.<name>`); the first top-level `<key>:` line
    of the front matter is rewritten in place, an absent one added before the closing
    `---`, every other byte kept. Written by a temporary and one rename, then JUDGED by
    `of()` on the file written: what the reading refuses, the writing refuses, the bytes
    restored. -> the previous raw value, "" when the line was absent."""
    path = meta / DOCUMENT
    if not path.is_file():
        raise Refusal("settings-invalid", f"{path} is missing -- no settings to write into")
    if not _known(meta, key):
        raise Refusal("settings-invalid", f"`{key}` -- no fragment of this instance owns that key")
    before = path.read_text(encoding="utf-8")
    lines = before.splitlines(keepends=True)
    end = next((i for i, l in enumerate(lines[1:], 1) if l.strip() == "---"), None) \
        if lines and lines[0].strip() == "---" else None
    if end is None:
        raise Refusal("settings-invalid", f"{path} carries no front matter to write a key into")
    said = str(value).strip()
    previous = ""
    for i in range(1, end):
        line = lines[i]
        if line[:1] in (" ", "\t", "#") or ":" not in line:
            continue
        if line.split(":", 1)[0].strip() == key:
            previous = line.split(":", 1)[1].strip()
            lines[i] = f"{key}: {said}\n"
            break
    else:
        lines.insert(end, f"{key}: {said}\n")
    _replace(path, "".join(lines))
    try:
        of(meta)
    except Refusal:
        _replace(path, before)
        raise
    return previous


def _known(meta: Path, key: str) -> bool:
    """-> whether the instance knows `key`: a protocol seed, a default of a pinned
    fragment, a switch of a pinned package, a sector cap or a material (their names
    judged by `of()`)."""
    if key in dict(SEEDS) or key.startswith(("cap.", "material.")):
        return True
    if key.startswith(instance.SWITCH_KEY):
        return key[len(instance.SWITCH_KEY):].strip() in instance.pins(meta)
    return any(name == key for one in fragments(meta) for name, _ in one.defaults)


def _replace(path: Path, text: str) -> None:
    """One atomic write: a temporary beside the file, then one rename."""
    temporary = path.with_suffix(".tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def _sector_caps(front: dict) -> tuple:
    """-> the `cap.<sector>` overrides as (name, cap) pairs -- the operator's hand
    on a named sector's serve cap; 0 mutes the sector, the manifest's default
    holds where no key is said."""
    found = []
    for key in front:
        if isinstance(key, str) and key.startswith("cap."):
            name = key[4:].strip()
            if not name:
                raise Refusal("settings-invalid", f"`{key}` names no sector")
            found.append((name, _natural(front, key, 0)))
    return tuple(found)


def _materials(front: dict) -> tuple:
    """-> the `material.<name>` declarations as (name, path) pairs -- the operator's
    catalogue of the trees a reading may name. A name must be given and must not be
    one of the engine's own (`repo`, `work`); the value is a path, relative to the
    workspace or absolute, judged on disk at the reading, never here: a worktree may
    leave and come back without SETTINGS refusing every call meanwhile."""
    found = []
    for key in front:
        if isinstance(key, str) and key.startswith("material."):
            name = key[len("material."):].strip()
            if not name:
                raise Refusal("settings-invalid", f"`{key}` names no material")
            if name in (MATERIAL_REPO, MATERIAL_WORK):
                raise Refusal("settings-invalid",
                              f"`{key}` -- `{name}` is the engine's: `repo` is the repository, "
                              "`work` the launcher's material")
            value = str(front.get(key) or "").strip()
            if not value:
                raise Refusal("settings-invalid",
                              f"`{key}` -- a path, relative to the workspace or absolute")
            found.append((name, value))
    return tuple(found)


def served_cap(cap: int, principal: bool) -> int:
    """-> the cap an output is cut under: in a run its principal conducts, the larger of the
    instance's `max_harness_tool_output` and `PRINCIPAL_CAP`; in the LLM's mode the setting
    as it stands. A cap of 0 or less cuts nothing, in either mode."""
    if cap <= 0 or not principal:
        return cap
    return max(cap, PRINCIPAL_CAP)


def _positive(front: dict, key: str, default: int) -> int:
    if key not in front:
        return default
    try:
        value = int(front[key])
    except ValueError:
        raise Refusal("settings-invalid", f"`{key}: {front[key]}` -- not a number")
    if value <= 0:
        raise Refusal("settings-invalid", f"`{key}: {value}` -- a budget below 1 plays nothing")
    return value


def _natural(front: dict, key: str, default: int) -> int:
    """A count that admits 0 -- zero is a deliberate mute, never a typo."""
    if key not in front:
        return default
    try:
        value = int(front[key])
    except ValueError:
        raise Refusal("settings-invalid", f"`{key}: {front[key]}` -- not a number")
    if value < 0:
        raise Refusal("settings-invalid", f"`{key}: {value}` -- a negative count means nothing")
    return value


def fusion_of(declared, key: str = "fusion") -> int:
    """The fusion cap -- `none` (1), `max` (0, unlimited) or a whole number >= 1.
    Shared with the per-document override (`fusion:`), which parses the same
    dialect; the SETTINGS key spells `instructions_fusion`."""
    if declared is None:
        return FUSION
    named = str(declared).strip().lower()
    if named == "none":
        return 1
    if named == "max":
        return 0
    try:
        value = int(named)
    except ValueError:
        raise Refusal("settings-invalid",
                      f"`{key}: {declared}` -- `none`, `max` or a whole number >= 1")
    if value < 1:
        raise Refusal("settings-invalid",
                      f"`{key}: {value}` -- below 1 renders nothing; `none` is the floor")
    return value



def _flag(front: dict, key: str, default: bool) -> bool:
    if key not in front:
        return default
    if isinstance(front[key], bool):
        return front[key]
    declared = str(front[key]).strip().lower()
    if declared not in ("true", "false"):
        raise Refusal("settings-invalid", f"`{key}: {front[key]}` -- `true` or `false`")
    return declared == "true"


def _one_of(front: dict, key: str, default: str, allowed: tuple[str, ...]) -> str:
    if key not in front:
        return default
    declared = str(front[key]).strip().lower()
    if declared not in allowed:
        raise Refusal("settings-invalid",
                      f"`{key}: {front[key]}` -- one of: {', '.join(allowed)}")
    return declared
