"""memory -- the conversations the post keeps open from one opening to the next: the agent and
the run of each tab, in the METADATA the engine keeps for each package of the instance, read
and written through the engine's face alone (`metadata.of_package`, `metadata.update`) -- the
engine derives the package's space (`ui`) from this file's place in the vendor, so the post
names no space and no path. Outside an installed instance (the source itself) there is no
memory: `recall` gives nothing and `keep` keeps nothing. The theme the operator chose (`t`)
is kept there too: `theme` reads it, `keep_theme` writes it."""
from __future__ import annotations

import sys
from pathlib import Path

KEY = "open"
THEME = "theme"


def _face():
    """-> (the engine's `metadata` face, the instance this file serves, the post's space), or
    None outside an installed instance."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))     # skills/: the bootstrap
    try:
        from _core import core
        conductor = core(__file__)
    except (SystemExit, ImportError):
        return None
    try:
        meta, space = conductor.metadata.mine(__file__)
    except conductor.Refusal:
        return None
    return conductor.metadata, meta, space


def recall() -> list[tuple[str, str]]:
    """-> the (agent, run) of each conversation the post kept open, in their order."""
    found = _face()
    if found is None:
        return []
    face, meta, space = found
    kept = face.of_package(meta, space).get(KEY) or []
    return [(str(one["agent"]), str(one["run"])) for one in kept
            if isinstance(one, dict) and one.get("agent") and one.get("run")]


def keep(pairs: list[tuple[str, str]]) -> None:
    """The conversations open now, in their order, each pair once; none at all takes the key out
    (an emptied space leaves the metadata)."""
    found = _face()
    if found is None:
        return
    face = found[0]
    once = list(dict.fromkeys(pairs))              # a pair is kept once, at its first place
    face.update(__file__, {KEY: [{"agent": agent, "run": run} for agent, run in once] or None})


def forget(pairs: list[tuple[str, str]]) -> None:
    """The conversations of runs that no longer exist taken out of the memory, the others kept in their order."""
    gone = set(pairs)
    kept = recall()
    if any(one in gone for one in kept):
        keep([one for one in kept if one not in gone])


def theme() -> str:
    """-> the theme the post was left in, '' when none was chosen."""
    found = _face()
    if found is None:
        return ""
    face, meta, space = found
    return str(face.of_package(meta, space).get(THEME) or "")


def keep_theme(name: str) -> None:
    """The theme chosen, kept for the next opening of the post."""
    found = _face()
    if found is not None:
        found[0].update(__file__, {THEME: name})
