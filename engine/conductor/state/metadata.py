"""Behaviour: the repository's METADATA -- what a package knows about the repo it lives in.

A package writes facts under its OWN name, in its OWN repository, and reads them back;
the engine governs the metadata record and knows no key. That is the difference with the
settings: those are the operator's values, read-only for a package; these are the
package's own knowledge of this repository, written by it. The record is shared, so every
write goes through the one regime -- lock, read inside the lock, atomic replace.

The WRITE takes no repository and no package name: it DERIVES both from the file of the
caller, which lives at `<member>/<meta>/.sys/vendor/<package>@<version>/...`. Writing at
a neighbour, or in another package's section, is therefore not a forbidden move -- it is
one that cannot be written. Reading stays free and addressed: cross-reading is what makes
the shared state of neighbouring members converge, and a member may read what its
neighbours say of
themselves.

documentary: the namespace was a call convention until the operator's word of 2026-08-31
(`write(meta, package, facts)`), which let a caller write at a neighbour and in another
package's section alike -- an intention the code did not hold. `mine()` walks up from the
CALLER's own file, never from this module's, because a vendored file shared across
packages in one process would otherwise answer for every other. An emptied section is
REMOVED rather than kept as `{}`: what a package has not written leaves no trace.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import instance, record
from ..core.errors import Refusal

STORE = ".sys/records/metadata.json"
VENDOR = "vendor"


def path_of(meta: Path) -> Path:
    """-> where this instance keeps the metadata record."""
    return meta / STORE


def mine(start: Path | str) -> tuple[Path, str]:
    """-> the (instance, package) the CALLER belongs to, walked up from its own file to
    the machine whose bundle holds it (a copy under its vendor, or a house package it plays from
    its sources); the instance `PP_HOME` names when that instance
    BORROWS this machine (the engine launched the caller for it), the machine itself
    otherwise. A caller that is not a vendored package's file refuses: the record cannot
    name a section for someone it cannot situate."""
    import os
    walked = Path(start).resolve()
    for parent in walked.parents:
        if (parent / instance.MANIFEST).is_file():
            found = instance.bundle_at(parent, walked)
            if found is None:
                raise Refusal("not-a-package",
                              f"{walked} is in no bundle of {parent} -- the metadata record writes "
                              "for a package's file, and derives its section from it")
            under = found[0].split("@", 1)[0]
            named = os.environ.get("PP_HOME", "").strip()
            if named and instance.is_instance(Path(named)) and instance.borrowed(Path(named).resolve()) == parent:
                return Path(named).resolve(), under
            return parent, under
    raise Refusal("not-an-instance",
                  f"{walked} is under no installed instance -- there is nowhere to write")


def read(meta: Path) -> dict:
    """-> the whole record, one section per package name -- empty when nothing was written."""
    path = path_of(meta)
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8") or "{}")


def of_package(meta: Path, package: str) -> dict:
    """-> what `package` knows about that repository, or an empty section. Reading is
    free and addressed: any member may read any other's record."""
    return read(meta).get(package) or {}


def write(start: Path | str, facts: dict) -> dict:
    """Replaces the CALLER's own section with `facts`; every other section travels
    untouched. -> the section as it now stands."""
    return _hold(start, lambda _: dict(facts))


def update(start: Path | str, facts: dict) -> dict:
    """Merges `facts` into the CALLER's own section -- a key set to None is dropped.
    -> the section as it now stands."""
    def merged(section: dict) -> dict:
        for key, value in facts.items():
            if value is None:
                section.pop(key, None)
            else:
                section[key] = value
        return section
    return _hold(start, merged)


def _hold(start: Path | str, change) -> dict:
    """The critical section of the record: the caller situated, read inside the lock,
    one section changed, replaced atomically. An emptied section leaves the record."""
    meta, package = mine(start)
    path = path_of(meta)
    with record.held(path):
        kept = read(meta)
        section = change(dict(kept.get(package) or {}))
        if section:
            kept[package] = section
        else:
            kept.pop(package, None)
        record.replace(path, json.dumps(kept, ensure_ascii=False, indent=1) + "\n")
    return section
