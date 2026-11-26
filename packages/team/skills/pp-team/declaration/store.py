"""The `declaration` domain, layer `store`: where a declaration is read, and nothing judged.

A definition belongs here when it reads a declaration from the system and gives back what it read: the front matter of
`TEAM.md` or of a text given, read by the engine; that front matter and the bytes of the file or of the text, which the
act `team_played` hands to the rule that judges the team; a candidate text from a file or the standard input. A front
matter the engine cannot read is declined; a `--text-file` that is no file ends the call with a refusal. What a
declaration is worth -- a name shown, a description, the team, the changes of `declare` -- belongs to a rule, and the
reading and the judgement are chained by an act. It imports no rule and no face.
"""
from __future__ import annotations

import sys
from pathlib import Path

from house.model import decline
from house.store import refuse


def front_read(conductor, path: Path, text: str | None = None) -> dict:
    """-> the front matter of a `TEAM.md`, its ONE reading: the file standing at `path`, or `text`, what `declare` is
    about to write there. DECLINES `team-invalid` for a front matter the engine cannot read; a file that is not there
    raises OSError."""
    try:
        if text is None:
            return conductor.reading.read(path).front
        lines = text.splitlines()
        start, end = conductor.sections.front_span(lines)
        return conductor.reading.front_matter(lines[start:end])
    except conductor.Refusal as refusal:
        decline(f"team-invalid -- {path}: {refusal}")


def team_read(conductor, path: Path, text: str | None = None) -> tuple[dict, bytes]:
    """-> (the front matter of a `TEAM.md`, its bytes): the file standing at `path`, or `text`, what `declare` is
    about to write there -- the front matter read first (`front_read`). DECLINES `team-invalid` for a front matter the
    engine cannot read; a file that is not there raises OSError."""
    front = front_read(conductor, path, text)
    return front, path.read_bytes() if text is None else text.encode("utf-8")


def candidate_read(asked: dict) -> str | None:
    """-> the CANDIDATE text `--text-file` names -- `-` the standard input, else a file --, None without the flag.
    Refuses `team-invalid` for a path that is no file."""
    if asked["text-file"] is None:
        return None
    if asked["text-file"] == "-":
        return sys.stdin.read()
    own = Path(asked["text-file"])
    if not own.is_file():
        refuse(f"team-invalid -- `--text-file {own}`: no such file.")
    return own.read_text(encoding="utf-8")
