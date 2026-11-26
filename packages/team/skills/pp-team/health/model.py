"""The `health` domain, layer `model`: what a team's health is, held as plain values.

A definition belongs here when it is data about how the team watches its members and does nothing -- the bounds of the
silence that makes a member suspected, or a type that carries one of them. Nothing here reads the disk, the clock or the
environment.

It also holds `Silence`, the body of the health's one kind of event, in the tuple `HEALTH_BODIES` that
`journal/model.py` reads to decode the journal. A silence of an old journal wrote its count under the key `exchanges`:
when the line has no `passages`, the body reads `exchanges` as `passages`, and the key stays in the line as it was read.

And it holds the health's part of the team's state, typed: `health`, a dictionary per member, and `silences`, the
`silence` events read, or after a snapshot the dictionaries it kept.
"""
from __future__ import annotations

from dataclasses import dataclass

from house.model import Body, Part

DEFAULT_SILENCE = 3                              # silent passages in a row that make a member suspected, unless TEAM.md says


@dataclass(frozen=True, eq=False)
class Silence(Body):
    """`silence`: a member said nothing for `passages` passages in a row on a task -- a fall of the detector. A journal
    of before counts them under `exchanges`: read here when `passages` is not there, the key left in the line."""
    KIND = "silence"
    agent: str | None = None
    task: str | None = None
    passages: int | None = None

    @classmethod
    def of(cls, line: dict) -> "Silence":
        if "passages" not in line and "exchanges" in line:   # a silence of before: its count under its old name
            return super().of({**line, "passages": line["exchanges"]})
        return super().of(line)


HEALTH_BODIES: tuple = (Silence,)   # the bodies of this domain's kinds: `journal/model.py` reads them


@dataclass(frozen=True, eq=False)
class HealthPart(Part):
    """The part `health` of the team's state -- the health of the members and the silences that fell."""
    health: dict[str, dict]           # member -> {falls, repents, at, cause, id}: its falls and its last one
    silences: list["Event"]           # the `silence` events read; a snapshot's, the dictionaries it kept
