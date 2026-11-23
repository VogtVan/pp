"""_team_stats -- what the scenarios of the stats of a team's seasons share (rule 10): the size of their renders, where
a frame stands in a capture and what its top edge and its rows hold (`framed`, `beside`, `offset`, `inside`, `title`),
the look of a cell and of a word (`looks`, `look`, `in_reverse`, `first`, `plain_fg`), the zones of the dashboard
drawn inside it and laid out by `--regions` (`zones_in`, `laid`, `apart`), the bands a `--regions` capture names
(`regions`) -- read by the structure of the render, never a text of the post."""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "teams")
D = support(__file__, "dialogue")
B = support(__file__, "tasks_band")   # the look of a glyph under the mouse

SEASON_ZONES = {"board-yield", "board-task-cost", "board-roles", "board-time", "board-principal", "board-context",
                "board-losses"}       # the zones of a season's dashboard, by their widgets
FRAMED = re.compile(r"^framed (\S+) x=(\d+) y=(\d+) w=(\d+) h=(\d+)$")

SIZE = ("--size", "160x44")        # the dashboard of a season whole in its frame
REGION = re.compile(r"^(band) (\S+) x=(\d+) y=(\d+) w=(\d+) h=(\d+)$")


def regions(text: str) -> dict[str, list[tuple]]:
    found: dict[str, list[tuple]] = {}
    for m in map(REGION.match, text.splitlines()):
        if m:
            found.setdefault(m.group(1), []).append((m.group(2), *map(int, m.group(3, 4, 5, 6))))
    return found


def rows(text: str) -> list[str]:
    return [D.ANSI.sub("", one) for one in text.rstrip("\n").split("\n")]


def offset(text: str, frame: tuple | None, word: str) -> int | None:
    """-> the offset of `word` in the top edge of `frame`, from the frame's left, as a click on it takes it."""
    if frame is None:
        return None
    drawn = rows(text)
    row = drawn[frame[2]] if frame[2] < len(drawn) else ""
    at = row.find(word, frame[1])
    return None if at < 0 or at >= frame[1] + frame[3] else at - frame[1]


def inside(text: str, frame: tuple | None) -> list[str]:
    """-> the rows of `frame`'s content, its edges left out."""
    if frame is None:
        return []
    _, x, y, w, h = frame
    return [row[x + 1:x + w - 1].strip() for row in rows(text)[y + 1:y + h - 1]]


CSI = re.compile(r"\x1b\[([0-9;]*)([A-Za-z])")


def codes(params: str) -> tuple[frozenset, str | None]:
    """-> the attributes an SGR sets -- `1` bold, `7` reverse -- and its foreground, `r;g;b`."""
    tokens, found, fg, at = params.split(";"), set(), None, 0
    while at < len(tokens):
        one = tokens[at]
        if one in ("38", "48") and at + 1 < len(tokens):
            width = 5 if tokens[at + 1] == "2" else 3
            if one == "38":
                fg = ";".join(tokens[at + 2:at + width])
            at += width
            continue
        found.add(one)
        at += 1
    return frozenset(found), fg


def looks(text: str) -> list[list[tuple]]:
    """-> the look of each cell of a `--styles` capture, row by row: its attributes and its foreground."""
    rows = []
    for row in text.rstrip("\n").split("\n"):
        cells, now, at = [], (frozenset(), None), 0
        for m in CSI.finditer(row):
            cells += [now] * len(row[at:m.start()])
            if m.group(2) == "m":
                now = (frozenset(), None) if m.group(1) in ("", "0") else codes(m.group(1))
            at = m.end()
        rows.append(cells + [now] * len(row[at:]))
    return rows


def first(text: str, frame: tuple, index: int) -> tuple | None:
    """-> the look of the first cell written of the content row `index` of `frame`, None for a blank row."""
    _, x, y, w, h = frame
    inner = rows(text)[y + 1 + index][x + 1:x + w - 1]
    if not inner.strip():
        return None
    return looks(text)[y + 1 + index][x + 1 + len(inner) - len(inner.lstrip())]


def in_reverse(text: str, frame: tuple | None, word: str) -> bool:
    """-> whether `word` stands in reverse in the top edge of `frame`."""
    at = offset(text, frame, word)
    return at is not None and "7" in looks(text)[frame[2]][frame[1] + at][0]


def plain_fg(text: str, frame: tuple) -> str | None:
    """-> the foreground most rows of `frame` start in: the look of a row written plain."""
    found = [one[1] for one in (first(text, frame, at) for at in range(frame[4] - 2)) if one and "1" not in one[0]]
    return max(set(found), key=found.count) if found else None


def frames(text: str) -> list[tuple]:
    return [("", *one) for one in D.frames_of(text)]


def within(inner: tuple, outer: tuple | None) -> bool:
    """-> whether the frame `inner` stands strictly inside the frame `outer`."""
    return (outer is not None and inner != outer and inner[1] > outer[1] and inner[2] > outer[2]
            and inner[1] + inner[3] < outer[1] + outer[3] and inner[2] + inner[4] < outer[2] + outer[4])


def zones_in(text: str, board: tuple | None) -> list[tuple]:
    """-> the frames drawn inside the dashboard: its zones, top to bottom."""
    return [one for one in frames(text) if within(one, board)]


def laid(text: str) -> dict[str, tuple]:
    """-> the framed zones of the dashboard a `--regions` capture lays out, by their widget's id: `("", x, y, w, h)`."""
    return {m.group(1): ("", *map(int, m.group(2, 3, 4, 5))) for m in map(FRAMED.match, text.splitlines())
            if m and m.group(1).startswith("board-")}


def apart(zones: list[tuple]) -> bool:
    """-> whether every two zones stand apart, a blank cell at least between them."""
    def gap(a, b):
        return (b[1] - (a[1] + a[3]) >= 1 or a[1] - (b[1] + b[3]) >= 1
                or b[2] - (a[2] + a[4]) >= 1 or a[2] - (b[2] + b[4]) >= 1)
    return all(gap(a, b) for at, a in enumerate(zones) for b in zones[at + 1:])


def look(text: str, frame: tuple | None, word: str) -> frozenset | None:
    """-> the attributes the first cell of `word` in the top edge of `frame` is drawn with."""
    at = offset(text, frame, word)
    return None if at is None else looks(text)[frame[2]][frame[1] + at][0]


HOVERED = frozenset(B.SGR_OF.get(one, one) for one in (B.HOVER or "").split())   # the SGR of `palette.HOVER`


def framed(text: str, word: str) -> tuple | None:
    """-> the round frame whose top edge holds `word`, `(word, x, y, w, h)`, None without one."""
    drawn = rows(text)
    return next((one for one in frames(text) if word in drawn[one[2]][one[1]:one[1] + one[3]]), None)


def beside(text: str, frame: tuple | None) -> tuple | None:
    """-> the frame on the left of `frame`, on its row: the head beside the summary."""
    if frame is None:
        return None
    return next((one for one in frames(text) if one[2] == frame[2] and one[1] + one[3] <= frame[1]
                 and one[1] > 0), None)


def title(text: str, frame: tuple | None) -> str:
    return "" if frame is None else rows(text)[frame[2]][frame[1]:frame[1] + frame[3]]
