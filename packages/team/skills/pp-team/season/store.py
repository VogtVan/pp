"""The `season` domain, layer `store`: where a season is read and written.

A definition belongs here when it reaches the system for a season and gives back what it read: it reads or writes
`SEASON.md`, finds the packages' manifests, the packages a member's run plays and those the team requires, reads the set
of a season, or reads the team's files to see whether they changed since the start. What reads and then judges a season
-- the season a start opens, the members' profiles, the gap to the last start, the flags written into `SEASON.md`, the
set a wake-up plays -- is an act (`season/acts.py`); a judgement that needs no system belongs to a rule.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from house.model import BORDER, decline
from house.rules import agent_meta, block, body_of, team_doc, team_root
from template.model import SEASON_DOC
from season.model import LAUNCH_FLAGS, PROFILE_LINE, SEASON_KEYS, SEASON_LIMITS


def season_text(path: Path, text: str | None = None) -> tuple[str, list[str] | None, str] | None:
    """-> (the text of SEASON.md, its lines when it opens on a front matter -- None otherwise --, its body: the whole
    text without a front matter) -- None without the file. `text`: what `declare` is about to write there, read
    in the file's place."""
    if text is None:
        if not path.is_file():
            return None
        text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != BORDER:
        return text, None, text.strip()
    return text, lines, body_of(text)


def season_word(directory: Path) -> str:
    """-> the owner's word of the season: the body of SEASON.md, "" without the file or its body."""
    read = season_text(directory / SEASON_DOC)
    return "" if read is None else read[2]


def season_front(conductor, path: Path, text: str | None = None) -> dict | None:
    """-> the front matter of SEASON.md -- the file, or `text` in its place --, read and judged by its keys
    (`SEASON_KEYS`) -- `{}` for a file without one,
    None without the file. DECLINES `season-invalid`: a front matter that never closes or that the engine cannot read,
    a key SEASON.md does not say."""
    read = season_text(path, text)
    if read is None:
        return None
    _, lines, _ = read
    front: dict = {}
    if lines is not None:
        end = next((at for at, line in enumerate(lines[1:], 1) if line.strip() == BORDER), None)
        if end is None:
            decline(f"season-invalid -- {path}: its front matter never closes.")
        try:
            front = conductor.reading.front_matter(lines[1:end])
        except conductor.Refusal as refusal:
            decline(f"season-invalid -- {path}: {refusal}")
    for key in front:
        if key not in SEASON_KEYS:
            decline(f"season-invalid -- {path}: `{key}:` -- {SEASON_DOC} says {', '.join(f'`{one}:`' for one in SEASON_KEYS)}.")
    return front


def season_written(root: Path, conductor, name: str, text: str | None = None) -> dict:
    """-> the season `teams/<name>/SEASON.md` writes -- the file, or `text` in its place --, in the form of `start`'s flags: `{launch: {key: value}, limits:
    {key: value}, packages: [<name>=on|off], profiles: {member: {key: value, packages: [...]}}, work}` -- empty
    without the file or its keys. `packages:` one `<name>=on|off` per line; `profiles:` one line per member, `<member>
    <key>=<value> ...`, the keys those of `PROFILE_LINE` and `package.<name>`. DECLINES `season-invalid`, nothing
    written: a line of another form, a name or a member said twice."""
    path = team_root(root, name) / SEASON_DOC
    front = season_front(conductor, path, text) or {}
    found: dict = {"launch": {key: str(front[key]) for key in LAUNCH_FLAGS if front.get(key) is not None},
                   "limits": {key: front[key] for key in SEASON_LIMITS if front.get(key) is not None},
                   "packages": [], "profiles": {},
                   "work": None if front.get("work") is None else str(front["work"])}
    switch = re.compile(r"[a-z0-9][a-z0-9_-]*=(on|off)")
    for line in block(front, "packages"):
        if not switch.fullmatch(line) or line.partition("=")[0] in [one.partition("=")[0] for one in found["packages"]]:
            decline(f"season-invalid -- {path}: packages: `{line}` -- one line per package, `<name>=on|off`, each once.")
        found["packages"].append(line)
    for line in block(front, "profiles"):
        member, *pairs = line.split()
        profile: dict = {}
        for pair in pairs:
            key, equal, value = pair.partition("=")
            package = key.removeprefix("package.") if key.startswith("package.") else None
            if (not equal or not value or (package is None and key not in PROFILE_LINE)
                    or (package is not None and not switch.fullmatch(f"{package}={value}")) or key in profile
                    or (package is not None and package in [one.partition("=")[0] for one in profile.get("packages", [])])):
                decline(f"season-invalid -- {path}: profiles: `{line}` -- `<member> <key>=<value> ...`, the keys "
                        f"{', '.join(PROFILE_LINE)} and package.<name> (on|off), each once.")
            if package is None:
                profile[key] = value
            else:
                profile.setdefault("packages", []).append(f"{package}={value}")
        if not pairs or member in found["profiles"]:
            decline(f"season-invalid -- {path}: profiles: `{line}` -- one line per member, said once, with one "
                    "`<key>=<value>` at least.")
        found["profiles"][member] = profile
    return found


def packages_at(root: Path, conductor, path: str, run: str | None = None, season: dict | None = None) -> dict:
    """-> `{born, packages [{name, on}]}` for the agent at `path`: born, the packages its instance pins beyond its
    base as `run` plays them -- the run's own switches over its SETTINGS, their dependents with them, read on the
    engine's faces as `agent status` reads them, the run's slot set into the play for the reading and taken out
    after; without a run, the `season`'s set (`season_played`: what its next opening gets, every pin named) --; not
    born yet, the house's pins beyond its base under the season's set."""
    instance, persistence, meta = conductor.instance, conductor.persistence, agent_meta(root, path)
    season = dict(season or {})
    if not instance.is_instance(meta):
        base = instance.base_of(root)
        return {"born": False, "packages": [{"name": name, "on": season.get(name, "on") == "on"}
                                            for name in instance.pins(root) if name != base]}
    slot = persistence.slot_of(meta, run) if run else None
    instance.play_switches(meta, persistence.switches_of(slot) if slot is not None and slot.is_file() else season)
    try:
        off = instance.switched_off(meta)
    finally:
        instance.play_switches(meta, {})
    base = instance.base_of(meta)
    return {"born": True, "packages": [{"name": name, "on": name not in off}
                                       for name in instance.pins(meta) if name != base]}


def manifests_named(root: Path, conductor) -> dict[str, Path]:
    """-> {package name: its vendored root} over the house's WHOLE composition, switched off included."""
    named: dict = {}
    for package_root in conductor.instance.vendored(root, switched=False):
        try:
            named[str(conductor.instance.manifest_of(package_root)["name"])] = package_root
        except conductor.Refusal:
            continue
    return named


def required_by_team(root: Path, conductor) -> set[str]:
    """-> `team` and every package it requires, transitively, as the house's manifests say them
    (`topology.closure`)."""
    return conductor.topology.closure(manifests_named(root, conductor), "team")


def season_set(root: Path, conductor, switches: dict[str, str]) -> list[str]:
    """-> the SET of a member's packages a season gives, `[<name>=on|off, ...]`: one per pin of the house beyond its
    base, in the pins' order -- `on` when `switches` switches it on or the team requires it (`required_by_team`),
    `off` otherwise. The one rule of a season's packages: `start` writes it, and a journal of before, whose list
    names some pins alone, is read under it -- a pin it does not name is off. The member's SETTINGS plays no part."""
    instance = conductor.instance
    base, needed = instance.base_of(root), required_by_team(root, conductor)
    return [f"{name}={switches.get(name) or ('on' if name in needed else 'off')}"
            for name in instance.pins(root) if name != base]


def changed_since_start(root: Path, name: str, started: dict) -> bool:
    """-> whether `TEAM.md` differs from the `digest` its start kept, or `SEASON.md` from the digest its start kept
    (`team-started.season-digest`) -- a SEASON.md that said no documents nor values at the start counts once it says
    some (`template:`, `documents:` or `values:`)."""
    if bool(started.body.digest) and (
            hashlib.sha256(team_doc(root, name).read_bytes()).hexdigest()[:12] != started.body.digest):
        return True
    kept = started.body.season_digest
    season = team_root(root, name) / SEASON_DOC
    read = season_text(season)
    if read is None:
        return kept is not None
    now = hashlib.sha256(season.read_bytes()).hexdigest()[:12]
    lines = read[1] or []
    end = next((at for at, line in enumerate(lines[1:], 1) if line.strip() == BORDER), len(lines))
    head = "\n".join(lines[1:end])
    return now != kept and (kept is not None or re.search(r"^(template|documents|values):", head, re.M) is not None)
