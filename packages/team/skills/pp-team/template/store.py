"""The `template` domain, layer `store`: where the templates are found and read, and nothing judged.

A definition belongs here when it reaches the system for a template and gives back what it read: the templates listed
under the house and the package, never read; a template's front matter read by the engine; the packages the house
pins; a template's text; the text a verb is handed, from a file or the standard input; a document's kind; the teams
that use a document. What a template is worth belongs to a rule, and an act chains the reading and the judgement. It
imports no rule and no face. This module also holds the path of the package's own templates.
"""
from __future__ import annotations

import sys
from pathlib import Path

from house.model import TEAMS, TEAM_DOC
from house.rules import block
from house.store import ENTRY
from template.model import PRESET_KEYS, SEASON_DOC, TEMPLATES_PLACE

TEMPLATES = Path(ENTRY).resolve().parents[2] / "templates"   # the package's templates, `<directory>/<name>.md`


# --- the templates: a TEAM.md to start from ------------------------------------------------

def templates_listed(root: Path) -> list[tuple[str, Path]]:
    """-> every `<directory>/<name>.md` under `<house>/.pp/teams/templates/`, then under the package's `templates/`,
    each place sorted, with its origin (`house`, `package`): listed, never read."""
    listed: list[tuple[str, Path]] = []
    for origin, place in (("house", root / "teams" / "templates"), ("package", TEMPLATES)):
        if place.is_dir():
            listed += [(origin, path) for path in sorted(place.glob("*/*.md"))]
    return listed


def template_front(conductor, path: Path) -> tuple[dict, object]:
    """-> (the front matter of a template's file as the engine reads it, None) -- ({}, the engine's `Refusal`) when it
    cannot read it."""
    try:
        return conductor.reading.read(path).front, None
    except conductor.Refusal as refusal:
        return {}, refusal


def pins_of(conductor, root: Path) -> set[str]:
    """-> the packages the house pins."""
    return set(conductor.instance.pins(root))


def template_text(path: Path) -> str:
    """-> the text of a template's file, as it stands."""
    return path.read_text(encoding="utf-8")


# --- a house's documents: their source read, created, replaced, deleted ---------------------------

def text_handed(given: str) -> str | None:
    """-> the text `--body-file <given>` hands over, read in BYTES and decoded as UTF-8, its line endings as they are:
    standard input's for `-`, the file's otherwise; None when no such file stands."""
    if given == "-":
        return sys.stdin.buffer.read().decode("utf-8")
    path = Path(given)
    return path.read_bytes().decode("utf-8") if path.is_file() else None


def document_kind(conductor, path: Path) -> str:
    """-> `preset` when the file's front matter carries one of `PRESET_KEYS`, `document` otherwise -- a front matter
    the engine cannot read included: its source is still read, replaced or deleted."""
    try:
        front = conductor.reading.read(path).front
    except conductor.Refusal:
        return "document"
    return "preset" if any(key in front for key in PRESET_KEYS) else "document"


def document_users(root: Path, conductor, name: str) -> list[str]:
    """-> who NAMES the house's document `name` on a line of `documents:`, one `<who> <file> <key>` each, the key
    between backquotes: every `TEAM.md` and `SEASON.md` of the house's teams, read without judging the team, and every
    preset of the house. A file whose front matter the engine cannot read names nothing."""
    files = []
    home = root.parent / TEAMS
    if home.is_dir():
        for directory in sorted(one for one in home.iterdir() if one.is_dir()):
            files += [(directory.name, directory / one) for one in (TEAM_DOC, SEASON_DOC)]
    shelf = root / TEMPLATES_PLACE
    if shelf.is_dir():
        files += [(f"{path.parent.name}/{path.stem}", path) for path in sorted(shelf.glob("*/*.md"))]
    found = []
    for who, path in files:
        if not path.is_file():
            continue
        try:
            front = conductor.reading.read(path).front
        except conductor.Refusal:
            continue
        for line in block(front, "documents"):
            key, *documents = line.split()
            if name in documents:
                found.append(f"{who} {path.relative_to(root.parent) if path.is_relative_to(root.parent) else path} "
                             f"`{key}`")
    return found
