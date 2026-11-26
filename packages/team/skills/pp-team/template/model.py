"""The `template` domain, layer `model`: what a team template is, held as plain values.

A definition belongs here when it is data about the templates and does nothing: the flags of the verbs that read or
write a template, the keys of a template's front matter, the forms a team template can take, the shape of a hole
`{name}` in its text, the key of a `documents:` line every member receives, or a type that carries one of them. Nothing
here reads the disk, the clock or the environment.

It holds two CARRIERS, frozen classes that keep no dictionary and are read by their attributes: `Template`, a preset as
its file says it, judged, born in `template_of` (`template/store.py`); and `Shape`, the team a preset's form makes of
its members, born in `formed` (`template/rules.py`). Each `json()` gives the dictionary it was born as, its keys in
their order. `Template` keeps the field `values`, the name of its key.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from house.model import TEAMS, Typed

TEMPLATES_FLAGS = {"json": False, "render": True, "value": True, "team": True,   # `templates`, and its dry render
                   "season": False, "text-file": True}
DOCUMENT_FLAGS = {"new": False, "body-file": True, "delete": False, "json": False}   # `document`: one action at most
TEMPLATES_PLACE = Path(TEAMS) / "templates"      # under the house's instance: the house's templates, read first
DOCUMENT_SKELETON = ("---\ndescription: what this document tells the members, in one sentence\n---\n# {name}\n\n"
                     "Write here what the members must know or do.\n")
#                                                 what `team document --new` writes: a document, no preset key
TEMPLATE_KEYS = ("description", "requires", "values")   # a document's own keys: never rendered
PRESET_KEYS = ("documents", "form", "members")   # the keys that make a template a PRESET, never a document
TEAM_KEYS = ("form", "members", "reports")      # the keys that make a preset a TEAM's: TEAM.md names it, SEASON.md never
SEASON_DOC = "SEASON.md"                         # in the team's directory: the season's values, the owner's file
BUILT_IN = "team"                                # the one value no template declares: the team's name
HOLE = re.compile(r"\{\{|\}\}|\{([a-z0-9]+(?:-[a-z0-9]+)*)\}")   # a hole `{<name>}`, or a brace written twice
FORM_NAMES = ("star", "chain", "one", "tree")    # the forms `formed` plays, a team template's `form:`
SQUADS = 2                                       # the squad leads of a `tree` its template does not count
PLACES = {None: ("root", "others", "last"), "star": ("root", "others", "last"),   # the places each form has, what
          "chain": ("root", "others", "last"), "one": ("root", "last"),             # a preset's `roles:` line names
          "tree": ("root", "others", "squads", "workers", "last")}
ALL = "all"                                      # the key of a `documents:` line every member receives


@dataclass(frozen=True, eq=False)
class Template(Typed):
    """ONE preset as its file says it, judged: born in `template_of` (`template/store.py`), where its front matter is
    read, and read by its attributes. `json()`: the dictionary it was born as, its keys in their order. `values` is
    declared by `field()`, which changes nothing since no base gives the class a method of that name."""
    template: str
    origin: str
    path: Path
    values: list = field()                 # [{name, description, default}]
    documents: list                        # [(key, [document, ...])]
    description: str
    form: str | None
    team: bool
    members: list
    root: object                           # the front matter's `root:` as it stands, None without it
    reports: list
    roles: list
    daily_intention: str
    limits: dict
    schedule: object                       # the front matter's `schedule:` as it stands, None without it
    intention: str

    def json(self) -> dict:
        return {"template": self.template, "origin": self.origin, "path": self.path, "values": self.values,
                "documents": self.documents, "description": self.description, "form": self.form, "team": self.team,
                "members": self.members, "root": self.root, "reports": self.reports, "roles": self.roles,
                "daily_intention": self.daily_intention, "limits": self.limits, "schedule": self.schedule,
                "intention": self.intention}


@dataclass(frozen=True, eq=False)
class Shape(Typed):
    """The team a preset's FORM makes of its members: born in `formed` (`template/rules.py`) -- the members in their
    order, the root, the edges, the daily (None without one), the holes the intention fills and the members of each
    place. `json()`: the dictionary it was born as."""
    members: list
    root: str | None
    reports: list                          # the edges, `a b -> c`
    ceremony: str | None                   # the daily's line, None without one
    holes: dict
    places: dict

    def json(self) -> dict:
        return {"members": self.members, "root": self.root, "reports": self.reports, "ceremony": self.ceremony,
                "holes": self.holes, "places": self.places}
