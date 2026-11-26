"""What the agent's settings, the run's switches and the families it plays say, read at the engine's faces."""
from __future__ import annotations

from pathlib import Path

from model.refusal import VectorRefused
from model.vector import Mount
from model.words import EMPTIED


def switches_played(conductor, meta: Path, key: str | None, waiting: dict | None) -> dict:
    """-> the switches the run plays at this wake-up, `{package: "on"|"off"}`: its own (the slot's), then the
    ones this wake-up asks and has not played yet -- what the engine's faces read the composition under."""
    persistence = conductor.persistence
    switches = dict(persistence.switches_of(persistence.slot_of(meta, key))) if key is not None else {}
    switches.update({name: "on" if on else "off" for name, (on, _) in (waiting or {}).items()})
    return switches


def mounts_of(conductor, meta: Path, key: str | None, waiting: dict | None, vectors: list[str]) -> list[Mount]:
    """-> what the launcher plays for each vector, its `Mount`: the script the family's manifest
    names as its verifier, read at the engine's face (`events.families`) among the families the run PLAYS --
    its own switches, then the ones this wake-up asks, over SETTINGS. This script knows no family and no
    package: a family answers `mount <id>` by the script that verifies it. Judged before anything is opened
    or played, each raising `VectorRefused` with its cause: a vector that is not `<family>:<id>`
    (`vector-invalid`), a family no package the run plays declares (`family-unknown`), a registry the engine
    refuses (its own code)."""
    if not vectors:
        return []
    instance = conductor.instance
    instance.play_switches(meta, switches_played(conductor, meta, key, waiting))
    try:
        families = conductor.events.families(meta)
    except conductor.Refusal as refusal:
        raise VectorRefused(refusal.code, ", ".join(vectors), str(refusal).split(" — ", 1)[-1]) from refusal
    finally:
        instance.play_switches(meta, {})
    found = []
    for vector in vectors:
        family, colon, ident = vector.partition(":")
        if not colon or not family.strip() or not ident.strip() or vector != vector.strip():
            raise VectorRefused("vector-invalid", vector, f"`--vector {vector}`: the form is <family>:<id>, "
                                                          f"or `{EMPTIED}` alone to keep none")
        script = str((families.get(family) or {}).get("verify") or "")
        if not script:
            raise VectorRefused("family-unknown", vector,
                                f"`{family}:` is no vector family this run plays: no package it plays declares it")
        found.append(Mount(vector=vector, script=script, ident=ident))
    return found


def call_wait(conductor, root: Path) -> float:
    """-> `call_lock_wait` as the house's settings say it, 30 s without them."""
    try:
        return float(conductor.settings.of(root).call_lock_wait)
    except Exception:                                   # no settings to read: the engine's seed
        return 30.0


def known_setting(conductor, meta: Path, key: str) -> bool:
    """-> whether the instance knows `key`: a `package.<name>` switch of a package it pins, or a key
    a pinned fragment declares."""
    switch = conductor.instance.SWITCH_KEY
    if key.startswith(switch):
        return key[len(switch):] in conductor.instance.pins(meta)
    return any(name == key for one in conductor.settings.fragments(meta) for name, _ in one.defaults)


def cap_of(conductor, meta: Path, cap: int | None = None) -> dict:
    """-> the cap the run's outputs are cut under: `set` the agent's `max_harness_tool_output`,
    `applied` what the engine serves this run -- the house conducts it, so the cap the house names on
    its calls (`cap`, `launcher_cap`) holds, else the floor of a principal's cap
    (`settings.served_cap`, the engine's one rule)."""
    face = conductor.settings
    harness_cap = face.of(meta).harness_cap
    return {"set": harness_cap, "applied": face.served_cap(harness_cap, True, cap)}


def packages_of(conductor, meta: Path, key: str | None) -> list[dict]:
    """-> the packages the agent's instance pins beyond its base, each `{name, on}` as the run
    plays it: the run's own switches over the switches of SETTINGS, their dependents with them --
    read on the engine's faces, the run's slot set into the play for the reading and taken out
    after; without a run, as the switches of SETTINGS alone say them."""
    instance, persistence = conductor.instance, conductor.persistence
    instance.play_switches(meta, persistence.switches_of(persistence.slot_of(meta, key)) if key is not None else {})
    try:
        off = instance.switched_off(meta)
    finally:
        instance.play_switches(meta, {})
    base = instance.base_of(meta)
    return [{"name": name, "on": name not in off} for name in instance.pins(meta) if name != base]


def worded(conductor, meta: Path, key: str | None, name: str) -> str | None:
    """-> the word the run's own switches hold on `name` (`on`, `off`), None when the run holds none on it -- then
    the agent's SETTINGS decide, and a switch asked is WRITTEN at the run, so that the run's word stands whatever
    SETTINGS says later; no run, None."""
    if key is None:
        return None
    persistence = conductor.persistence
    return persistence.switches_of(persistence.slot_of(meta, key)).get(name)


def pinned_of(conductor, meta: Path) -> tuple[str, set[str]]:
    """-> (the base of the agent's instance, the names of the packages it pins beyond it)."""
    return conductor.instance.base_of(meta), {one["name"] for one in packages_of(conductor, meta, None)}
