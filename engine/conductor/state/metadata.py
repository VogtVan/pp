"""Behaviour: the repository's METADATA -- what a package knows about the repo it lives in.

A package writes facts under its OWN name, in its OWN repository, and reads them back;
the engine governs the store and knows no key. That is the difference with the settings:
those are the operator's values, read-only for a package; these are the package's own
knowledge of this repository, written by it. The store is a shared record, so every
write goes through the one regime -- lock, read inside the lock, atomic replace.

The WRITE takes no repository and no package name: it DERIVES both from the file of the
caller, which lives at `<member>/<meta>/.sys/vendor/<package>@<version>/...`. Writing at
a neighbour, or in another package's space, is therefore not a forbidden move -- it is
one that cannot be written. Reading stays free and addressed: cross-reading is what makes
the shared state of neighbouring members converge, and a member may read what its
neighbours say of
themselves.

documentary: the namespace was a call convention until the operator's word of 2026-08-31
(`write(meta, package, facts)`), which let a caller write at a neighbour and in another
package's space alike -- an intention the code did not hold. `mine()` walks up from the
CALLER's own file, never from this module's, because a vendored file shared across
packages in one process would otherwise answer for every other. An emptied space is
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
    """-> where this instance keeps the store."""
    return meta / STORE


def mine(start: Path | str) -> tuple[Path, str]:
    """-> the (instance, package) the CALLER belongs to, walked up from its own file.
    A caller that is not a vendored package's file refuses: the store cannot name a
    space for someone it cannot situate."""
    walked = Path(start).resolve()
    for parent in walked.parents:
        if (parent / instance.MANIFEST).is_file():
            try:
                under = walked.relative_to(parent / instance.VENDOR).parts[0]
            except ValueError:
                raise Refusal("not-a-package",
                              f"{walked} is not under {parent / instance.VENDOR} -- the store "
                              "writes for a vendored package, and derives its space from it")
            return parent, under.split("@", 1)[0]
    raise Refusal("not-an-instance",
                  f"{walked} is under no installed instance -- there is nowhere to write")


def read(meta: Path) -> dict:
    """-> the whole store, one space per package name -- empty when nothing was written."""
    path = path_of(meta)
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8") or "{}")


def of_package(meta: Path, package: str) -> dict:
    """-> what `package` knows about that repository, or an empty space. Reading is
    free and addressed: any member may read any other's store."""
    return read(meta).get(package) or {}


def write(start: Path | str, facts: dict) -> dict:
    """Replaces the CALLER's own space with `facts`; every other space travels
    untouched. -> the space as it now stands."""
    return _hold(start, lambda _: dict(facts))


def update(start: Path | str, facts: dict) -> dict:
    """Merges `facts` into the CALLER's own space -- a key set to None is dropped.
    -> the space as it now stands."""
    def merged(space: dict) -> dict:
        for key, value in facts.items():
            if value is None:
                space.pop(key, None)
            else:
                space[key] = value
        return space
    return _hold(start, merged)


def _hold(start: Path | str, change) -> dict:
    """The critical section of the store: the caller situated, read inside the lock,
    one space changed, replaced atomically. An emptied space leaves the store."""
    meta, package = mine(start)
    path = path_of(meta)
    with record.held(path):
        store = read(meta)
        space = change(dict(store.get(package) or {}))
        if space:
            store[package] = space
        else:
            store.pop(package, None)
        record.replace(path, json.dumps(store, ensure_ascii=False, indent=1) + "\n")
    return space
