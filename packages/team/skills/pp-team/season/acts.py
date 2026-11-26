"""The `season` domain, layer `acts`: a season read, then judged.

A definition belongs here when it chains a store's reading and a rule's judgement for a season: the season a `start`
opens, in the form `team-started` keeps (`season_opened`); the team's packages and the members' profiles judged before
any write (`profiles_judged`); what a new `start` would change of the season (`season_gap`); the values the start's
flags give, written into `SEASON.md` (`season_flagged`); the set a member's wake-up plays (`season_played`), and the
face of the launch it gets (`launch_face`). Only verbs and other acts call it. A paused team taken back, which plays a
tick, is a verb (`unpause`, `season/verbs.py`), and the season's flags of a `declare --season` are judged by
`declaration/acts.py`. It may use the lower layers of any domain.
"""
from __future__ import annotations

from pathlib import Path

from house.model import decline
from house.store import placed
from season.model import LAUNCH_FLAGS, LAUNCH_KEYS, PROFILE_KEYS, SEASON_LIMITS, SEASON_PENDING
from template.rules import values_written
from season.rules import profile_of, season_changes, season_of, season_switches, set_of, switches_composed
from season.store import manifests_named, season_set, season_written


def season_opened(root: Path, conductor, name: str, team: dict, asked: dict, packages: list, profiles: dict,
                  text: str | None = None) -> dict:
    """-> the season a `start` opens, in the form `team-started` keeps -- `{launch, season, packages, profiles, work}`:
    SEASON.md's values (`season_written`; `text` read in the file's place) each covered by the start's flag for the same key -- a team's flag its key,
    a member's flag its profile's key, a `--package` its name --, then judged whole by the season's judges: a
    `--harness` without its `--provider` (`grammar-missing`), the limits (`season_of`), the packages and the profiles
    (`profiles_judged`); the packages written as the whole SET (`season_set`). DECLINES, nothing written."""
    written = season_written(root, conductor, name, text)
    limits = {**written["limits"], **{key: asked[key] for key in SEASON_LIMITS if asked.get(key) is not None}}
    launch = {**written["launch"], **{key: asked[key] for key in LAUNCH_FLAGS if asked.get(key) is not None}}
    launch = {key: launch[key] for key in ("harness", "provider", "model", "permissions", "effort") if key in launch}
    if launch.get("harness") is not None and launch.get("provider") is None:   # every wake-up would refuse it
        decline("grammar-missing -- `--harness` runs a caller's command at every wake-up: name the grammar its "
                "output is read in with `--provider <name>` beside it -- the provider whose adapter reads it.")
    season = season_of({key: limits.get(key) for key in SEASON_LIMITS})
    composed_packages = [f"{key}={value}" for key, value in switches_composed(written["packages"], packages).items()]
    composed_profiles: dict = {member: dict(profile) for member, profile in written["profiles"].items()}
    for member, flagged in profiles.items():
        profile = composed_profiles.setdefault(member, {})
        for key, value in flagged.items():
            if key == "packages":
                profile["packages"] = [f"{one}={state}" for one, state in
                                       switches_composed(profile.get("packages") or [], value).items()]
            else:
                if not str(value).strip() or any(one.isspace() for one in str(value)):
                    decline(f"season-invalid -- `--member {member} --{key} {value}`: a profile's value is one word.")
                profile[key] = value
    profiles_judged(root, conductor, team, composed_packages, composed_profiles)
    whole = season_set(root, conductor, switches_composed(composed_packages))
    for profile in composed_profiles.values():
        if profile.get("packages"):
            profile["packages"] = season_set(root, conductor, switches_composed(whole, profile["packages"]))
    return {"launch": launch, "season": season, "packages": whole, "profiles": composed_profiles,
            "work": written["work"]}


def profiles_judged(root: Path, conductor, team: dict, packages: list, profiles: dict) -> None:
    """Judges the team's packages and the members' profiles before any write: a member nobody declared
    (`participant-unknown`), a switch off its form (`package-invalid`), a package the team needs switched off
    (`package-required` -- `team` and what it requires), a package the house does not pin switched on
    (`package-unpinned`), a package switched on whose requirement the season's SET -- the team's switches covered by
    the member's, every other pin off unless the team requires it (`season_set`) -- switches off
    (`package-dependency`). A package the house does not pin, switched off, asks nothing: it leaves the set."""
    if not packages and not profiles:
        return
    named = manifests_named(root, conductor)
    needed = conductor.topology.closure(named, "team")
    pinned = set(conductor.instance.pins(root))

    def judged(values: list, whom: str) -> None:
        for value in values or []:
            package, _, state = str(value).partition("=")
            if not package or state not in ("on", "off"):
                decline(f"package-invalid -- `--package {value}` for {whom}: the form is <name>=on or <name>=off.")
            if state == "off" and package in needed:
                decline(f"package-required -- `{package}` cannot be switched off for {whom}: the team needs it "
                       f"({', '.join(sorted(needed))}).")
            if package not in pinned and state == "on":
                decline(f"package-unpinned -- `{package}` is not pinned by the house: the packages it pins are "
                       f"{', '.join(sorted(pinned))}.")

    def dependent(composed: dict, whom: str) -> None:
        off = {name for name, state in composed.items() if state == "off"}
        for name, state in composed.items():
            if state != "on":
                continue
            lacking = sorted((conductor.topology.closure(named, name) - {name}) & off)
            if lacking:
                decline(f"package-dependency -- `{name}=on` for {whom} needs {', '.join(lacking)}, which the season "
                       "switches off: a package never plays without what it requires.")

    judged(packages, "the team")
    dependent(set_of(season_set(root, conductor, switches_composed(packages))), "the team")
    for member, profile in profiles.items():
        if member not in team.agents:
            decline(f"participant-unknown -- `--member {member}` names a member nobody declared.")
        if profile.get("silence") is not None:
            if not str(profile["silence"]).isdigit() or int(profile["silence"]) < 1:
                decline(f"team-invalid -- `--member {member} --silence {profile['silence']}`: a whole number of 1 or more.")
            profile["silence"] = int(profile["silence"])
        judged(profile.get("packages") or [], member)
        dependent(set_of(season_set(root, conductor, switches_composed(packages, profile.get("packages") or []))),
                  member)


def season_gap(root: Path, conductor, started: dict, opened: dict) -> list[dict]:
    """-> what a new `start` without a flag would change of the season: `{key, started, declared}` per key of
    `SEASON_PENDING` that SEASON.md now opens otherwise than `team-started` kept it -- the kept side read as it plays:
    the launch's keys a launch passes (`LAUNCH_FLAGS`), the packages and each profile's as the whole set
    `season_played` reads a journal's lists with, a journal of before included."""
    launch = {key: value for key, value in (started.body.launch or {}).items()
              if key in LAUNCH_FLAGS and value is not None}
    profiles = {member: {**profile, **({"packages": season_played(root, conductor, started, member)}
                                       if profile.get("packages") else {})}
                for member, profile in (started.body.profiles or {}).items()}
    kept = {"launch": launch, "season": started.line.get("season") or {},   # the line: the season as SEASON.md said it
            "packages": season_played(root, conductor, started), "profiles": profiles,
            "work": started.body.work}
    return [{"key": key, "started": kept[key], "declared": opened[key]} for key in SEASON_PENDING
            if kept[key] != opened[key]]


def season_flagged(conductor, path: Path, asked: dict, packages: list, profiles: dict) -> bool:
    """Writes into SEASON.md the values the start's FLAGS give, key by key (`season_changes`, `values_written`), every
    other key, line and token and the body at their bytes; the file is born when a flag gives a value and it stands
    not, with those keys alone. -> whether a flag gave a value. Called after every judge and before `team-started`."""
    changes = season_changes(asked, packages, profiles)
    if not changes:
        return False
    text = path.read_bytes().decode("utf-8") if path.is_file() else ""   # its line endings as they are
    placed(path, values_written(conductor, text, changes).encode("utf-8"))
    return True


def season_played(root: Path, conductor, started: dict, member: str | None = None) -> list[str]:
    """-> the set a member's wake-up plays: the season's lists at `team-started` (`season_switches`) read under the
    rule of the set (`season_set`) -- the journal's set itself, every pin of a journal of before named."""
    return season_set(root, conductor, season_switches(started, member))


def launch_face(root: Path, conductor, started: dict, member: str | None = None) -> dict:
    """-> what the next wake-up gets of the launch `team start` kept: each key, `null` when absent -- never
    `max_budget_usd`, a per-wake cap an older journal may keep and the tick never passes --, and `packages`, the
    season's SET as `<name>=on|off`, one per pin (`season_played`): the team's; for a member, what its profile
    replaces, and the set its wake-up plays."""
    kept = started.body.launch or {}
    profile = profile_of(started, member)
    face = {key: kept.get(key) for key in LAUNCH_KEYS}
    face.update({key: profile[key] for key in PROFILE_KEYS if profile.get(key) is not None})
    face["packages"] = season_played(root, conductor, started, member)
    return face
