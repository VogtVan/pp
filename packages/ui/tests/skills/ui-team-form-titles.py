"""Scenario `ui-team-form-titles` -- the titles of the two zones of a form's side pane read as the titles of the post's
other zones (batch les-reglages-des-formulaires), on the bench's `pp-team` witness: `S` on `core-review` in three
themes -- the one the post opens in, the next and the one after it in its list (`t`) --, captured with their styles:
- `S`, its Documents (batch la-liste-des-documents): the title of the holes of the document chosen and the one of its
  text are bold, in another colour than their frame's, in each theme
- the three themes draw the frame in three colours: the titles were read in three looks
"""
from __future__ import annotations

import re

from tests.harness import support

F = support(__file__, "team_forms")
T, P = F.T, F.P

THEMES = (("opened", ""), ("next", "t,down,enter,"), ("further", "t,down,down,enter,"))
TITLES = ("holes", "text")     # `S`, Documents: the side pane says the holes and the text of a document


def _looks(raw: str, title: str) -> tuple[str, str] | None:
    """-> the SGR parameters the title `title` and the corner `╭` of its frame are drawn with, on the row holding both;
    None without that row."""
    for row in raw.split("\n"):
        bare = P.ANSI.sub("", row)
        if title not in bare or "╭" not in bare:
            continue
        current, corner, said = "", None, None
        for part in re.split(r"(\x1b\[[0-9;]*m)", row):
            found = P.SGR.fullmatch(part)
            if found:
                current = found.group(1)
                continue
            if corner is None and "╭" in part:
                corner = current
            if title in part:
                said = current
                break
        return (said, corner) if said is not None and corner is not None else None
    return None


def _bold(params: str) -> bool:
    return "1" in params.split(";")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-form-titles", F.script())
    corners = []
    for name, keys in THEMES:
        done = house.render("--render", "teams", *F.SIZE, "--press", f"{keys}S,{F.TO_SEASON_DOCUMENTS}", "--styles")
        looks = {title: _looks(done.raw, title) for title in TITLES}
        read = all(one is not None and _bold(one[0]) and one[0] != one[1] for one in looks.values())
        corners.append(next((one[1] for one in looks.values() if one is not None), None))
        if done.returncode == 0 and read:
            held(f"the titles of the side pane read, theme {name}", "; ".join(f"{title}: {one[0]} on a frame {one[1]}"
                                                                         for title, one in looks.items()))
        else:
            failures.append(f"  ✗ titles, theme {name:<12} rc={done.returncode} {looks} {done.stderr[-300:]!r}")
    if len(set(corners)) == len(THEMES) and None not in corners:
        held("three themes, three frames", f"{corners}")
    else:
        failures.append(f"  ✗ themes                      {corners}")
    return 0
