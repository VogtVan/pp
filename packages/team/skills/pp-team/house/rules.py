"""The `house` domain, layer `rules`: what the house works out from the values it is given.

A definition belongs here when it computes its answer from its arguments alone: a path of the house, of a team or of an
agent put together from the house's root, a form judged, whether a path is an agent's path, a block of a front matter
and the body after it, a duration read from its text. It reads no disk, no clock and no environment, prints nothing and
never ends the call, and imports no store: what needs the system belongs to `store` -- whether a launch was born in
another process space is read there (`foreign`). A rule has one of two shapes: a question (a state in, a value out) or a
decision (a state in, the events to write or a refusal out).
"""
from __future__ import annotations

from pathlib import Path

from house.model import BORDER, HOUR, HOUSE, JOURNAL, MINUTE, TEAMS, TEAM_DOC


def team_doc(root: Path, name: str) -> Path:
    return root.parent / TEAMS / name / TEAM_DOC


def team_root(root: Path, name: str) -> Path:
    """-> the team's directory: its TEAM.md, its entries, its documents -- the root of documents of
    every run the team opens."""
    return root.parent / TEAMS / name


def journal_of(root: Path, name: str) -> Path:
    return root / ".sys" / "records" / TEAMS / name / JOURNAL


def record_of(root: Path, name: str) -> Path:
    """-> one of the house's records -- written by pp-agent, read here."""
    return root / ".sys" / "records" / name


def agent_meta(root: Path, path: str) -> Path:
    """-> where the agent `path` stands: an agent IS its path under the house, slugs joined by
    `/` (`m`, `squad/r9`), its instance directory named as the house's own; `.` (`HOUSE`) is the
    house itself. The path is judged at the declaration (`path_valid`)."""
    if path == HOUSE:
        return root
    return root.parent.joinpath(*path.split("/")) / root.name


def vector_formed(value) -> bool:
    """-> whether a VECTOR is formed: a text `<family>:<id>`, both sides said, no blank in it. What it names, the
    team never reads: the vector is an opaque string the launcher alone resolves."""
    if not isinstance(value, str) or any(one.isspace() for one in value):
        return False
    family, colon, ident = value.partition(":")
    return bool(family and colon and ident)


# --- the declaration: TEAM.md read whole ---------------------------------------------------

def block(front: dict, key: str) -> list[str]:
    """-> the non-empty lines of a `key: |` block, stripped; nothing for an absent key."""
    return [line.strip() for line in str(front.get(key, "")).splitlines() if line.strip()]


def body_of(text: str) -> str:
    """-> the text after the front matter."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != BORDER:
        return ""
    end = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == BORDER), None)
    return "\n".join(lines[end + 1:]).strip() if end is not None else ""


def seconds_of_duration(value) -> int | None:
    """-> the SECONDS a declaration's duration says -- `10s`, `2m`, `1h`, or a bare whole number of MINUTES (the form
    of before: `schedule: 5`) --, None for a form this contract cannot read or a duration under a second."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value * MINUTE if value >= 1 else None
    text = str(value).strip()
    unit = 1 if text.endswith("s") else MINUTE if text.endswith("m") else HOUR if text.endswith("h") else None
    digits = text[:-1] if unit is not None else text
    if not digits.isdigit() or int(digits) < 1:
        return None
    return int(digits) * (unit or MINUTE)


def path_valid(conductor, path: str) -> bool:
    """-> whether `path` is an agent's path: `.` (`HOUSE`) alone, or slugs joined by `/` -- no `.`
    nor `..` segment, no leading `/`, no empty segment."""
    return path == HOUSE or (bool(path) and all(conductor.instance.valid_slug(one) for one in path.split("/")))
