"""The BUS of events: motors push signals, the bus does the base shaping --
validation against what the packages declare, counting, thresholds, latching,
standing entries, acquit, lifecycle. It knows no POLICY family, signal or sector
by name: every one comes from a package's `contributes.events` declaration --
beside the engine's OWN operational signals, BUILTIN below: the declarant is the
emitter (operator word 2026-08-26). A consumer (the reflex document of a policy package)
reads the crossed latches and does the non-deterministic sorting; nothing here
judges, nothing here runs on its own.

A vector's SLUG is verified by the package that owns its family: the declaration names
a skill (`verify:`), the bus runs it at every entry (push, stand) and at the service
(a latch whose vector no longer verifies drops) -- the engine holds no referential
(operator word 2026-09-03: declaration, description, verification -- the package's)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ..state import instance
from ..core.errors import Refusal

RECORD = "events.json"    # the bus's durable state: one counter per vector
STALE_DAYS = 30           # a counter silent this long dies -- the bus's own
                          # time cleanup; a dead NODE is the verifier's call
DIRECTIVES = ("::push", "::clear")   # what a script says to the bus, one line each
BUILTIN = {               # the engine's OWN operational events: emitted by the conductor
    "vectors": {},        # wherever it runs, so declared WITH it -- never a package's to
    "signals": {          # register; a policy's taxonomy stays at its package
        "refused": {"priority": 3, "sector": "protocol"},
        "serve-stale": {"priority": 3, "sector": "protocol"},
        "serve-shadowed": {"priority": 3, "sector": "protocol"},
        "repaired": {"priority": 4, "sector": "protocol"},
    },
    "sectors": {"protocol": {"icon": "🧭", "default": True}},
}                         # `protocol` is the COMMONS: any declarant may name it, and its
                          # `default` is the LAST RESORT -- one package default overrides it


def providers(meta: Path) -> dict:
    """-> every provider of events: the `contributes.events` section of each
    vendored package's manifest, by package name -- vectors (the families),
    signals, sectors. Data only: a provider never ships code."""
    from . import contributions
    found = {"engine": {key: dict(value) for key, value in BUILTIN.items()}}
    for one in contributions.composed(meta):
        if one["kind"] != "events":
            continue
        section = one.get("value") or {}
        if not isinstance(section, dict):
            raise Refusal("contribution-malformed", f"`{one['package']}` events: a mapping is owed")
        found[str(one["package"])] = {
            "vectors": dict(section.get("vectors") or {}),
            "signals": dict(section.get("signals") or {}),
            "sectors": dict(section.get("sectors") or {}),
        }
    return found


def families(meta: Path) -> dict:
    """-> the registered vector families: prefix -> {verify, source} and, when a
    provider guards the family, {guard, guard_source}. The registry MERGES what the
    providers declare on one prefix: the owner's `verify:` and ONE `guard:` -- the
    family's second worker, asked before a node retires -- declared by any provider,
    the owner included. Two providers naming the same worker refuse `family-collision`;
    a prefix nobody verifies refuses `family-unverified` -- the validation of the whole
    lives here, a manifest alone seeing only its own line.

    documentary: the guard came with batch le-gardien-declare (plan pp-split): a package
    that is not the owner of a family may keep its nodes from retiring while the
    package knows better -- the confederation holding a thread a neighbour still works."""
    merged: dict = {}
    for source, declared in providers(meta).items():
        for prefix, spec in declared["vectors"].items():
            entry = merged.setdefault(str(prefix), {})
            for worker, owner_key in (("verify", "source"), ("guard", "guard_source")):
                skill = str((spec or {}).get(worker) or "").strip()
                if not skill:
                    continue
                if entry.get(worker):
                    raise Refusal("family-collision",
                                  f"`{prefix}:` -- `{worker}:` is declared by `{entry[owner_key]}` "
                                  f"and `{source}`; a family has ONE {worker}")
                entry[worker] = skill
                entry[owner_key] = source
    for prefix, entry in merged.items():
        if not entry.get("verify"):
            raise Refusal("family-unverified",
                          f"`{prefix}:` is guarded by `{entry.get('guard_source')}` and verified by "
                          "nobody -- a family names the skill that verifies its slugs")
    return merged


def sectors(meta: Path) -> dict:
    """-> the declared sectors: name -> {**spec, source}. A NAMED sector belongs
    to its declarant -- two providers declaring one name refuse; ONE declarant
    marks the default: a signal without `sector:` falls there, whoever pushes."""
    merged = {}
    for source, declared in providers(meta).items():
        for name, spec in declared["sectors"].items():
            if str(name) in merged:
                raise Refusal("sector-collision",
                              f"`{name}` is declared by `{merged[str(name)]['source']}` "
                              f"and `{source}` -- a named sector belongs to ONE provider")
            merged[str(name)] = {**(spec or {}), "source": source}
    defaults = [name for name, spec in merged.items()
                if spec.get("default") is True and spec.get("source") != "engine"]
    if len(defaults) > 1:
        raise Refusal("sector-collision",
                      f"{', '.join(f'`{one}`' for one in defaults)} all declare `default: true` "
                      "-- ONE sector receives the signals that name none")
    return merged


def default_sector(meta: Path) -> str:
    """-> the sector a signal without `sector:` falls into -- the ONE a package
    declares `default: true`; none declared, the engine's builtin default (the
    `protocol` commons) receives them."""
    declared = sectors(meta)
    for name, spec in declared.items():
        if spec.get("default") is True and spec.get("source") != "engine":
            return name
    for name, spec in declared.items():
        if spec.get("default") is True:
            return name
    return ""


def threshold_of(meta: Path, spec: dict) -> int:
    """-> the bound a signal's `threshold:` names: a whole number, or a SETTINGS
    key referenced `@SETTINGS.<key>` -- the instance's value, else the key's
    default at its owner (the package fragment that declares it)."""
    from ..state import settings
    declared = str(spec.get("threshold", "")).strip()
    if declared.startswith("@SETTINGS."):
        declared = settings.referenced(meta, declared)   # the one resolver of a reference
    try:
        return int(declared)
    except ValueError:
        raise Refusal("threshold-invalid", f"`{declared}` is neither a whole number nor `@SETTINGS.<key>`")


def mark(declared: dict, sector: str) -> str:
    """-> the sector's declared icon -- the sector's own name when none is."""
    return str((declared.get(sector) or {}).get("icon") or sector)


def counters(meta: Path) -> dict:
    """-> the durable counters, `{vector: {count, last_at}}` -- {} when none stand."""
    path = meta / instance.RECORDS / RECORD
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return {}


def verified(meta: Path, vector: str) -> None:
    """The family's VERIFIER, run by the engine: the skill the declaration names, the
    verb `verify`, the whole vector on stdin, cwd the workspace -- rc 0 says valid, any
    other refuses `vector-unverified` with the skill's own reason. The engine knows no
    referential: the package that owns the family answers. -> None when valid.

    documentary: the ONE contract of verification -- the same call at the two entries
    (push, stand) and at the service (standing); a package's sink asks it BEFORE it
    counts, so a slug that never existed never accrues anywhere."""
    _worker(meta, vector, "verify", "verifier-missing", "vector-unverified")


def guarded(meta: Path, vector: str) -> None:
    """The family's GUARDIAN, run by the engine at the OWNER's ask before a node retires:
    the skill the registry names under `guard:`, the verb `guard`, the whole vector on
    stdin, cwd the workspace -- rc 0 says free, any other refuses `vector-guarded` with
    the guardian's own reason. No guardian declared: nothing plays, no subprocess -- a
    composition without one pays nothing. -> None when free.

    documentary: the same contract as `verified` (batch le-gardien-declare): the engine
    asks a declared worker and relays its no; the owner asks (a keeper's `close`), the
    engine never retires a node of its own."""
    _worker(meta, vector, "guard", "guardian-missing", "vector-guarded")


def _worker(meta: Path, vector: str, role: str, missing: str, refused: str) -> None:
    """ONE contract for the family's workers: the skill the registry names for `role`,
    played with `role` as its verb and the vector on stdin; a worker the family does not
    declare plays nothing (the guard is optional, the verifier never is)."""
    prefix = vector.split(":", 1)[0]
    spec = families(meta).get(prefix)
    if spec is None:
        raise Refusal("family-unknown",
                      f"`{prefix}:` is no registered vector family -- a provider "
                      "declares its families before its motors push on them")
    skill = str(spec.get(role) or "").strip()
    if not skill:
        return None
    contract = instance.skill_contract(meta, skill)
    script = contract.parent / f"{skill}.py" if contract else None
    if script is None or not script.is_file():
        raise Refusal(missing,
                      f"`{prefix}:` names `{skill}` as its {role} worker and no script skill "
                      "of that name is vendored in this instance")
    done = subprocess.run([sys.executable, str(script), role], input=vector,
                          capture_output=True, text=True, cwd=str(meta.parent))
    if done.returncode != 0:
        reason = (done.stderr.strip() or done.stdout.strip() or "refused").splitlines()[-1][-300:]
        raise Refusal(refused, f"`{vector}` -- {skill}: {reason}")


def _alive(meta: Path, vector: str) -> bool:
    """-> whether a held vector still verifies -- the service's broom."""
    if not vector:
        return True
    try:
        verified(meta, vector)
    except Refusal:
        return False
    return True


def gesture_signals(meta: Path, skill: str) -> list[tuple[str, str]]:
    """-> the signals declared AT a call (`at: call:<skill>`): the package's
    motor without a line of code -- the engine pushes when the call plays.
    (`at`, not `on`: YAML 1.1 reads a bare `on` key as a boolean.)"""
    found = []
    for source, declared in providers(meta).items():
        for signal, spec in declared["signals"].items():
            if str((spec or {}).get("at", "")).strip() == f"gesture:{skill}":
                found.append((source, str(signal)))
    return found


def _guarded(meta: Path):
    """The record's critical section: every load-modify-write of the counters
    plays inside it -- two sessions of one member never lose a push."""
    from ..state import record
    return record.held(meta / instance.RECORDS / RECORD)


def push(meta: Path, source: str, signal: str, vector: str = "",
         door: str = "", evidence: str = "") -> dict | None:
    """One motor's event, shaped. Validated against the registry -- an orphan push
    REFUSES, nothing written. A signal declaring `threshold:` counts its vector
    (a number, or `@SETTINGS.<key>` resolved at the instance); one without
    latches on the push itself. -> the latch entry when one crossed, None otherwise."""
    registry = providers(meta)
    declared = registry.get(source)
    if declared is None:
        raise Refusal("provider-unknown", f"`{source}` declares no `contributes.events`")
    spec = declared["signals"].get(signal)
    if spec is None:
        raise Refusal("signal-unknown", f"`{source}` declares no signal `{signal}`")
    spec = spec or {}
    if vector:
        verified(meta, vector)           # the family's own verifier, before anything counts
    declared_sectors = sectors(meta)   # a colliding declaration refuses every push
    fallback = default_sector(meta)
    sector = str(spec.get("sector", "")).strip() or fallback
    if not sector:
        raise Refusal("sector-unowned",
                      f"`{signal}` names no sector and no package declares a default one")
    if (sector != fallback
            and (declared_sectors.get(sector) or {}).get("source") not in (source, "engine")):
        raise Refusal("sector-unowned",
                      f"`{signal}` claims sector `{sector}` and `{source}` does not "
                      "declare it -- a named sector serves its declarant's signals alone, "
                      "the engine's commons excepted")
    entry = {"signal": signal, "source": source, "vector": vector,
             "door": str(spec.get("door", door) or door), "sector": sector, "n": 1}
    if "threshold" not in spec:
        return entry                          # a predicate: the push IS the crossing
    bound = threshold_of(meta, spec)
    with _guarded(meta):
        held = _prune(meta, counters(meta))
        now = datetime.now(timezone.utc)
        one = held.get(vector) or {"count": 0}
        one = {"count": int(one.get("count", 0)) + 1, "last_at": now.isoformat(timespec="seconds")}
        held[vector] = one
        _write(meta, held)
    if one["count"] >= bound:
        return {**entry, "n": one["count"]}
    return None


def standing(meta: Path, latched: list) -> list:
    """-> the latches still TRUE now -- the recomputation: a counting latch whose
    counter fell under its bound (or whose vector died) drops; a predicate latch
    stands for its session (its motor re-pushes, or it dies with the run)."""
    sectors(meta)   # a colliding declaration blocks the read too, named
    with _guarded(meta):
        held = _prune(meta, counters(meta))
        _write(meta, held)
    registry = providers(meta)
    kept = []
    for one in latched:
        declared = registry.get(one.get("source", "")) or {"signals": {}}
        spec = declared["signals"].get(one.get("signal", "")) or {}
        if "threshold" in spec:
            bound = threshold_of(meta, spec)
            count = int((held.get(one.get("vector", "")) or {}).get("count", 0))
            if count < bound:
                continue
        if not _alive(meta, str(one.get("vector", ""))):
            continue                     # its node is gone: the verifier says so, the latch drops
        kept.append(one)
    return kept


def emitted(meta: Path, latched: list, setting_cap: int = 2,
            sector_caps: dict | None = None) -> list:
    """-> the latches to SERVE, arbitrated: grouped by sector, each sector sorted
    by the signal's declared `priority:` (absent sorts last), then count, then
    latch order, and capped -- the DEFAULT sector by the instance's setting, a named
    sector by the operator's `cap.<sector>` setting when said, else its declared
    `cap:` (2 unsaid, 0 mute); the default sector serves first, then in pin order.
    A pure view: the overflow stays latched, unserved, and rises as the
    recomputation frees a place."""
    registry = providers(meta)
    declared = sectors(meta)
    fallback = default_sector(meta)     # the sector a package DECLARES default, never a name
    ranked = {}
    for at, one in enumerate(latched):
        spec = ((registry.get(one.get("source", "")) or {"signals": {}})
                ["signals"].get(one.get("signal", "")) or {})
        weight = (int(spec["priority"]) if str(spec.get("priority", "")).strip()
                  else float("inf"))
        sector = str(one.get("sector", "")) or fallback
        ranked.setdefault(sector, []).append((weight, -int(one.get("n", 1)), at, one))
    served = []
    for sector in [fallback] + [name for name in declared if name != fallback]:
        if sector not in ranked:
            continue
        cap = (setting_cap if sector == fallback
               else int((sector_caps or {}).get(
                   sector, (declared.get(sector) or {}).get("cap", 2))))
        served += [one for _, _, _, one in sorted(ranked[sector])[:max(cap, 0)]]
    return served


def acquit(meta: Path, vector: str) -> int:
    """The operator's GO on a treated vector: its counter AND every held entry
    speaking for it fall together -- a cause that has been answered stops asking.
    -> how many record keys fell; an unknown vector refuses, nothing written."""
    with _guarded(meta):
        held = counters(meta)
        # a vector wears two key shapes here -- its bare counter, and every standing
        # key whose tail names it; both fall together or the line comes back served
        doomed = [key for key in held if _vector_of(key) == vector]
        if not doomed:
            raise Refusal("vector-unknown",
                          f"`{vector}` holds no counter and no latch -- nothing to acquit")
        for key in doomed:
            del held[key]
        _write(meta, held)
    return len(doomed)


STANDING = "standing|"    # record keys of held entries: standing|<source>|<signal>|<vector>


def _vector_of(key: str) -> str:
    """-> the vector a record key speaks for -- its own name, or the tail of a
    standing key."""
    return key.split("|", 3)[3] if key.startswith(STANDING) else key


def _standing_spec(meta: Path, signal: str) -> tuple[str, dict]:
    """-> (source, spec) of the ONE provider declaring `signal` as standing --
    unknown, ambiguous or non-standing refuse by name."""
    owners = [(source, declared["signals"][signal] or {})
              for source, declared in providers(meta).items()
              if signal in declared["signals"]]
    if not owners:
        raise Refusal("signal-unknown", f"no provider declares a signal `{signal}`")
    if len(owners) > 1:
        raise Refusal("signal-ambiguous",
                      f"`{signal}` is declared by several providers -- one signal, one home")
    source, spec = owners[0]
    if not spec.get("standing"):
        raise Refusal("signal-not-standing",
                      f"`{signal}` does not declare `standing: true` -- only a held "
                      "signal takes a harvested push")
    return source, spec


def stand(meta: Path, signal: str, vector: str, text: str) -> dict:
    """A script's harvested push, held: ONE durable entry per (signal, vector) --
    the newest REPLACES the previous, so a delivery cleans its own push by
    pushing the next; `unstand` removes it, the stale and the sweep apply as to
    any counter. The event is captured at the moment the call made it true."""
    source, spec = _standing_spec(meta, signal)
    if vector:
        verified(meta, vector)           # the family's own verifier, before anything stands
    fallback = default_sector(meta)
    sector = str(spec.get("sector", "")).strip() or fallback
    declared_sectors = sectors(meta)
    if (sector != fallback
            and (declared_sectors.get(sector) or {}).get("source") != source):
        raise Refusal("sector-unowned",
                      f"`{signal}` claims sector `{sector}` and `{source}` does not declare it")
    with _guarded(meta):
        held = _prune(meta, counters(meta))
        entry = {"text": " ".join(text.split()),
                 "last_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        held[f"{STANDING}{source}|{signal}|{vector}"] = entry
        _write(meta, held)
    return entry


def unstand(meta: Path, signal: str, vector: str) -> bool:
    """The clearing push: the held entry falls -- closing a plan cleans its line."""
    source, _ = _standing_spec(meta, signal)
    with _guarded(meta):
        held = _prune(meta, counters(meta))
        dropped = held.pop(f"{STANDING}{source}|{signal}|{vector}", None) is not None
        _write(meta, held)
    return dropped


def standing_entries(meta: Path) -> list:
    """-> the held entries, latch-shaped for the serve -- they come with EVERY serve of
    any run until replaced, cleared, staled or swept; nothing here is per-run."""
    registry = providers(meta)
    found = []
    for key, entry in _prune(meta, counters(meta)).items():
        if not key.startswith(STANDING):
            continue
        _, source, signal, vector = key.split("|", 3)
        if not _alive(meta, vector):
            continue                     # its node is gone: the verifier says so, nothing served
        spec = ((registry.get(source) or {"signals": {}})["signals"].get(signal)) or {}
        found.append({"signal": signal, "source": source, "vector": vector,
                      "door": str(spec.get("door", "") or ""),
                      "sector": str(spec.get("sector", "")).strip() or default_sector(meta),
                      "n": 1, "text": str(entry.get("text", ""))})
    return found


def migrate_families(meta: Path) -> list[str]:
    """The bus's record follows the families' names (the naming law, KPS31): a key
    whose family the registry no longer knows is rewritten to the ONE registered family
    wearing it as its tail (`thread:x` -> `steering-thread:x`), standing keys included;
    none or several wearing it: the key stays and is said. Played at `upgrade`, the
    moment the families move with their packages. -> what moved, one line each;
    [] when nothing was to do -- a replay says nothing.

    documentary: the engine owns this record and knows every family the packages
    declare -- it is the one hand that can carry a latched vector across a rename
    without a referential of its own: the tail of a qualified family IS the old name."""
    registry = families(meta)
    with _guarded(meta):
        held = counters(meta)
        moved: dict[str, str] = {}
        told: list[str] = []
        left: list[str] = []
        for key in list(held):
            vector = _vector_of(key)
            family, colon, slug = vector.partition(":")
            if not colon or family in registry:
                continue
            wearing = [one for one in registry if one == family or one.endswith("-" + family)]
            if len(wearing) != 1:
                left.append(f"`{vector}` left as is -- {len(wearing) or 'no'} registered "
                            f"famil{'y wears' if len(wearing) == 1 else 'ies wear'} `{family}`")
                continue
            renamed = f"{wearing[0]}:{slug}"
            if key.startswith(STANDING):
                head = key.split("|", 3)[:3]
                moved[key] = "|".join(head + [renamed])
            else:
                moved[key] = renamed
        for old_key, new_key in moved.items():
            held[new_key] = held.pop(old_key)
            told.append(f"`{_vector_of(old_key)}` -> `{_vector_of(new_key)}`")
        if moved:
            _write(meta, held)
            told += left            # what the pass could not carry is said WITH the pass;
    return told                     # a replay that moves nothing says nothing (idempotent)


def _prune(meta: Path, held: dict) -> dict:
    """Life at the write: every counter dies after STALE_DAYS of silence. A vector whose
    node is gone dies at the SERVICE, by its family's verifier -- never here."""
    now = datetime.now(timezone.utc)
    kept = {}
    for vector, entry in held.items():
        try:
            last = datetime.fromisoformat(str(entry.get("last_at", "")))
        except ValueError:
            continue
        if now - last > timedelta(days=STALE_DAYS):
            continue
        kept[vector] = entry
    return kept


def _write(meta: Path, held: dict) -> None:
    path = meta / instance.RECORDS / RECORD
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(held, indent=2, ensure_ascii=False, sort_keys=True),
                         encoding="utf-8")
    os.replace(temporary, path)   # atomic: a torn counter would lie


def harvest(meta: Path, text: str) -> list[str]:
    """The ONE collector of what a script says to the bus: every `::push <signal>
    <vector> <text>` line stands its entry, every `::clear <signal> <vector>` line
    removes it -- the console's calls and the engine's sinks alike. -> the lines
    that were NOT directives, for whoever renders the rest. A malformed directive
    refuses by name, nothing standing."""
    rest = []
    for line in text.splitlines():
        parts = line.split(None, 3)
        if parts and parts[0] == "::push":
            if len(parts) < 4:
                raise Refusal("push-malformed",
                              f"`{line}` -- a push is `::push <signal> <vector> <text>`")
            try:
                stand(meta, parts[1], parts[2], parts[3])
            except Refusal as refusal:
                if refusal.code != "vector-unverified":
                    raise
                # the verifier said no: the producer hears it, the turn goes on
                rest.append(f"{parts[2]} refused -- {refusal}")
        elif parts and parts[0] == "::clear":
            if len(parts) != 3:
                raise Refusal("push-malformed", f"`{line}` -- a clear is `::clear <signal> <vector>`")
            unstand(meta, parts[1], parts[2])
        else:
            rest.append(line)
    return rest


def sink(meta: Path, skill: str, production: str) -> list[str]:
    """A document's production handed to its declared SINK: the skill runs in a
    subprocess with the production on stdin, and what it prints to the bus is
    harvested -- the same collector as a console call. -> the skill's other
    lines. A skill that refuses is said back, it never breaks the turn."""
    import subprocess
    import sys
    contract = instance.skill_contract(meta, skill)
    script = contract.parent / f"{skill}.py" if contract else None
    if script is None or not script.is_file():
        return [f"{skill} -- no script skill of that name in this instance"]
    done = subprocess.run([sys.executable, str(script)], input=production, capture_output=True,
                          text=True, cwd=str(meta.parent))
    if done.returncode != 0:
        return [f"{skill} refused ({done.returncode}): {done.stderr.strip()[-300:]}"]
    return harvest(meta, done.stdout)
