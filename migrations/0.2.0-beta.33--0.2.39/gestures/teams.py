"""The teams: at 0.2.0-beta.33, `team new` wrote the team's intention -- its template's text, its
holes filled -- into `teams/<name>/TEAM-<name>.md`, beside a `TEAM.md` whose body it left empty. At
0.2.39 that document is the one `team start` renders, and the owner's word is the body of `TEAM.md`:
a `TEAM-<name>.md` no start rendered refuses the start (`intention-misplaced`).

The body of `TEAM-<name>.md`, word for word, becomes the body of an empty `TEAM.md`; the front of
`TEAM.md` stays as written, its keys still read at 0.2.39. No template is deduced. `TEAM-<name>.md`
itself leaves at the cleanup. A `TEAM.md` whose body is already written and differs refuses the
gesture (`team-intention`): the owner settles which text is theirs. Every team is read before the
first is written. Counted per team: the lines of the intention, and the ones the body of `TEAM.md`
holds after."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

import _common

from . import joined, replace, split


def document(team: Path) -> Path:
    return team / f"TEAM-{team.name}.md"


def intention(team: Path) -> str | None:
    """-> the intention `TEAM-<name>.md` holds, its own front left out; None without the file."""
    path = document(team)
    if not path.is_file():
        return None
    front, body = split(path.read_text(encoding="utf-8"))
    return body.strip()


def body(team: Path) -> tuple[list[str] | None, str]:
    return split((team / "TEAM.md").read_text(encoding="utf-8"))


def moved(team: Path) -> bool:
    """-> whether the body of `TEAM.md` holds the intention of `TEAM-<name>.md`, word for word."""
    said = intention(team)
    return said is not None and body(team)[1].strip() == said


def lines(text: str) -> list[str]:
    return [line for line in text.split("\n") if line.strip()]


def gesture(house, engine) -> list[tuple]:
    planned = []
    for team in house.teams:
        said = intention(team)
        if said is None:
            continue
        front, written = body(team)
        if written.strip() and written.strip() != said:
            raise _common.Refused("team-intention", f"{team / 'TEAM.md'}: its body is written and differs from "
                                                    f"{document(team).name} -- keep one text in the body of "
                                                    "TEAM.md, delete the other file, then migrate again")
        planned.append((team, front, written, said))
    rows = []
    for team, front, written, said in planned:     # every team read before the first is written
        if not written.strip() and said:
            text = (joined(front, "\n" + said + "\n") if front is not None else said + "\n")
            replace(team / "TEAM.md", text)
        after = body(team)[1]
        rows.append((team, "team-intention", len(lines(said)), sum((Counter(lines(said)) & Counter(lines(after))).values())))
    return rows
