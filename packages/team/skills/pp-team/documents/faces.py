"""The `documents` domain, layer `faces`: how a team's documents are put into words.

A definition belongs here when it composes what a member reads -- the text of a document the team serves, the turn's
overlay, the name of the members' sheet -- from what it is given, and gives it back without writing or printing it. It
reads nothing: the face of the declaration as it plays and the members' sheet, which read the season and the documents,
are acts (`documents/acts.py`), and a document's name is a rule (`documents/rules.py`), since a decision writes it.
"""
from __future__ import annotations

from pathlib import Path

from documents.model import ACT_FORMAT, DECIDER, IDLE, TURN_DOC


def team_document(name: str, documents: list[str], intention: str, served: list[str]) -> bytes:
    """-> `TEAM-<name>.md` of the team's directory: the HEAD this skill writes -- called at the kit's
    `turn.begin` of every exchange of the team's runs, its `SERVE` serves `served` (`served_of`: the document
    itself, the package's `TEAM_WORK.md`, then the team's other documents), each body read once and again when it changes; with entries, at
    its exit this skill's verb `entry` elects among them and the neutral successor -- then the BODY, the team's
    intention as `start` renders it from the template `TEAM.md` names, empty without one."""
    elected = (f"next: {' '.join([*documents, IDLE])}\ndecide: {DECIDER} {name}\n" if documents else "")
    lines = "".join(f"  {one}\n" for one in served)
    return (f"---\nproc: |\n  SERVE\nserve: |\n{lines}attach: turn.begin\n{elected}---\n" + intention).encode("utf-8")


def turn_overlay() -> bytes:
    """-> `TURN.md` of the team's directory: the overlay of the kit's turn, its `output:` the form of an act
    (`ACT_FORMAT`) and nothing else -- no law, no body. The directory is the root of documents of every run the
    team opens: the WORK line of each of their exchanges names that form."""
    return f"---\nname: {Path(TURN_DOC).stem}\noutput: {ACT_FORMAT}\n---\n".encode("utf-8")


def sheet_name(name: str) -> str:
    """-> the file name of the members' sheet: `TEAM-<name>-members.md`."""
    return f"TEAM-{name}-members.md"
