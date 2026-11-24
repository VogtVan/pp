"""_tasks_band -- what the scenarios of the band of a task on the Tasks tab share (rule 10): the sizes and keys of their
renders, where the parts of the pane stand (`regions_of`) and what a capture shows in a region (`rows_in`), the labels
of the frames (`titles_of`), the glyph that expands a frame -- and the case each frame that expands proves
(`expands`): a click on its glyph expands it over its place, the other frames hidden, the glyph turned to the one
that folds; the same click folds it back, the regions as they were --, the filters the list expanded keeps beside it
(`filters_kept`), and the look the glyph takes under the mouse (`glyph_hovered`)."""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "teams")
P = D = support(__file__, "dialogue")


def glyph(name: str) -> str | None:
    """-> the glyph `name` of the palette; None when the palette has none."""
    try:
        return P.palette_constant(name)
    except KeyError:
        return None


EXPAND, COLLAPSE = glyph("EXPAND"), glyph("COLLAPSE")              # the glyph of a frame, folded and expanded
HOVER = glyph("HOVER")                                               # the look of a glyph under the mouse
SGR_OF = {"bold": "1", "dim": "2", "italic": "3", "underline": "4", "blink": "5", "reverse": "7", "strike": "9"}

WIDE, SHORT, NARROW, TALL = ("--size", "130x40"), ("--size", "130x28"), ("--size", "80x40"), ("--size", "130x60")
EVERY = "shift+tab,shift+tab,down,down,down,down,down,down"         # SHOW `all`
RESOLVED = "shift+tab,shift+tab,down,down,down,down,tab,tab,down"   # SHOW `resolved`, the cursor on ops' T2
ID_ROW = re.compile(r"^T\d+\s{2,}")                                  # a row of the table: a task's id, then its cells
TITLE = re.compile(r"─ (sequence|result|text)(?: \S)? ─")             # the label of a frame, in its top edge, its glyph
SHOWN = ("tasks-menu", "tasks-show", "tasks-team", "tasks-list", "tasks-detail", "tasks-text", "tasks-sequence")


def regions_of(text: str) -> dict[str, tuple[int, int, int, int]]:
    """-> where each named part of the pane stands, `(x, y, w, h)` by its id -- the last line that names it."""
    found = {}
    for one in text.split("\n"):
        words = one.split()
        if len(words) == 6 and words[0] in ("menu", "band", "inner", "framed"):
            found[words[1]] = tuple(int(word.split("=")[1]) for word in words[2:])
    return found


def rows_in(text: str, region: tuple[int, int, int, int]) -> list[str]:
    """-> the rows of a capture a region covers, cut to its columns."""
    x, y, w, h = region
    return [one[x:x + w] for one in text.split("\n")[y:y + h]]


def titles_of(text: str) -> list[str]:
    """-> the labels of the frames of the band a capture shows, top to bottom."""
    return [found.group(1) for found in map(TITLE.search, text.split("\n")) if found]


def look_at(row: str, column: int) -> frozenset:
    """-> the SGR parameters a styled row draws its PLAIN column `column` with -- those set since the last reset."""
    at, seen, look = 0, 0, set()
    while at < len(row):
        found = D.SGR.match(row, at)
        if found:
            words = found.group(1).split(";")
            while words:
                word = words.pop(0)
                if word in ("", "0"):
                    look = set()
                elif word in ("38", "48"):                         # a colour: its own parameters taken out
                    look.add(word)
                    del words[:{"5": 2, "2": 4}.get(words[0] if words else "", 0)]
                else:
                    look.add(word)
            at = found.end()
            continue
        found = D.ANSI.match(row, at)
        if found:
            at = found.end()
            continue
        if seen == column:
            return frozenset(look)
        at += 1
        seen += 1
    return frozenset()


def _house(bench, name: str):
    return T.Teams(bench, name, T.script(states={"core-review": [T.CORE_BAND], "ops": [T.OPS]}))


def _glyph_at(house, size: tuple[str, str], frame: str) -> tuple[dict, int]:
    """-> the regions of the pane at `size`, and the offset of the glyph in the top edge of `frame` (-1 without)."""
    start = regions_of(house.render("--render", "tasks", *size, "--regions").stdout)
    edge = rows_in(house.render("--render", "tasks", *size).stdout, start[frame])[0] if frame in start else ""
    return start, (edge.find(EXPAND) if EXPAND else -1)


def _apart(one: tuple[int, int, int, int], other: tuple[int, int, int, int]) -> bool:
    """-> whether two regions share no cell."""
    return (one[0] + one[2] <= other[0] or other[0] + other[2] <= one[0]
            or one[1] + one[3] <= other[1] or other[1] + other[3] <= one[1])


def task_rows(text: str, region: tuple[int, int, int, int]) -> list[str]:
    """-> the rows of tasks a capture shows in a region, the sides of a frame stripped."""
    return [one.strip(" │") for one in rows_in(text, region) if ID_ROW.match(one.strip(" │"))]


def filters_kept(bench) -> int:
    """The case of the filters beside the list expanded, at 130x60 (s.1459): a click on the list's glyph expands it,
    the menu of the filters `SHOW` and `TEAM` still shown, neither over the list; `SHOW` changed from the keys while
    the list stays expanded reads its rows again -- its frame still expanded."""
    held, failures = bench.held, bench.failures
    house = _house(bench, "ui-tasks-band-filters")
    start, dx = _glyph_at(house, TALL, "tasks-list")
    click = f"click:#tasks-list:{max(dx, 0)}:0"
    resolved = "shift+tab,shift+tab,down,down,down,down"                # SHOW `resolved`, from the list focused
    grown = regions_of(house.render("--render", "tasks", *TALL, "--press", click, "--regions").stdout)
    changed = regions_of(house.render("--render", "tasks", *TALL, "--press", f"{click},{resolved}",
                                      "--regions").stdout)
    before = house.render("--render", "tasks", *TALL, "--press", click).stdout
    after = house.render("--render", "tasks", *TALL, "--press", f"{click},{resolved}").stdout
    listed = grown.get("tasks-list", (0, 0, 0, 0))
    menus = {one: grown.get(one, (0, 0, 0, 0)) for one in ("tasks-show", "tasks-team")}
    shown = all(area[2] and area[3] and _apart(area, listed) for area in menus.values())
    rows, rows_after = task_rows(before, listed), task_rows(after, changed.get("tasks-list", listed))
    if (dx >= 0 and listed[3] > start["tasks-list"][3] and shown and changed.get("tasks-list") == listed
            and rows_after and rows_after != rows):
        held("the filters stay beside the list expanded, SHOW reads it again",
             f"list {listed}, show {menus['tasks-show']}, team {menus['tasks-team']}; "
             f"{len(rows)} rows -> {len(rows_after)} rows")
    else:
        failures.append(f"  ✗ filters kept         glyph at {dx}; list {start.get('tasks-list')} -> {listed}, "
                        f"show/team {menus} (shown apart: {shown}); after SHOW {changed.get('tasks-list')}; "
                        f"rows {rows} -> {rows_after}")
    return 0


def glyph_hovered(bench) -> int:
    """The case of the glyph under the mouse (s.1460), at 130x40: the mouse on the cell of the list's glyph draws it
    with `palette.HOVER` added to its look; the mouse gone to another widget gives its look back."""
    held, failures = bench.held, bench.failures
    house = _house(bench, "ui-tasks-band-hover")
    start, dx = _glyph_at(house, WIDE, "tasks-list")
    x, y = start["tasks-list"][0] + max(dx, 0), start["tasks-list"][1]
    on = f"hover:#tasks-list:{max(dx, 0)}:0"
    looks = [look_at(house.render("--render", "tasks", *WIDE, "--styles", *press).raw.split("\n")[y], x)
             for press in ((), ("--press", on), ("--press", f"{on},hover:#tasks-show:2:1"))]
    wanted = {SGR_OF.get(one, one) for one in (HOVER or "").split()}
    rest, over, out = looks
    if dx >= 0 and HOVER and wanted <= over and not wanted <= rest and out == rest:
        held("the glyph of the list shines under the mouse", f"{sorted(rest)} -> {sorted(over)} -> {sorted(out)}")
    else:
        failures.append(f"  ✗ glyph hovered       glyph at {dx}, HOVER {HOVER!r} (SGR {sorted(wanted)}); look "
                        f"{sorted(rest)} -> under the mouse {sorted(over)} -> out {sorted(out)}")
    return 0


def expands(bench, key: str, over: str) -> int:
    """The case of the frame `key` (`sequence`, `text`, `list`) on T7 of `core-review` -- `result` on ops' T2,
    resolved, whose band shows its result in the frame of the sequence (s.1517) --, at 130x40: a click on its glyph
    expands it over the whole centre (`over` `centre`) -- the menu of the filters kept beside it (s.1459) -- or the
    whole place under the list (`below`), the other frames hidden -- the menu, and the list under `below`, kept --,
    `COLLAPSE` in its title; a second click gives back the regions it found."""
    held, failures = bench.held, bench.failures
    house = _house(bench, f"ui-tasks-band-{key}")
    frame = f"tasks-{key}"
    band = "tasks-result" if key == "result" else "tasks-sequence"     # the frame below: the result or the sequence
    zones = tuple(band if one == "tasks-sequence" else one for one in SHOWN)
    before = {"sequence": "tab,", "result": f"{RESOLVED},tab,"}.get(key, "")   # a click focuses the sequence or
                                                                       # the result: so does `tab`
    reach = ("--press", before[:-1]) if before else ()                # the band as the click finds it
    wide = house.render("--render", "tasks", *WIDE, *(reach if key == "result" else ()))
    start = regions_of(house.render("--render", "tasks", *WIDE, *reach, "--regions").stdout)
    left, top, width = start["tasks-list"][:3]
    bottom = start[band][1] + start[band][3]
    below = top + start["tasks-list"][3]                               # the first row under the list
    region = (left, top, width, bottom - top) if over == "centre" else (left, below, width, bottom - below)
    edge = rows_in(wide.stdout, start[frame])[0] if frame in start else ""
    dx = edge.find(EXPAND) if EXPAND else -1
    click = f"click:#{frame}:{max(dx, 0)}:0"
    once, twice = (house.render("--render", "tasks", *WIDE, "--press", keys, "--regions")
                   for keys in (before + click, f"{before}{click},{click}"))
    drawn = house.render("--render", "tasks", *WIDE, "--press", before + click)
    grown, back = regions_of(once.stdout), regions_of(twice.stdout)
    kept = zones[:4] if over == "below" else zones[:3]                  # the menu stays; the text leaves the list too
    others = [one for one in zones if one != frame and one not in kept and grown.get(one, (0, 0, 0, 0))[2:] != (0, 0)]
    top_row = rows_in(drawn.stdout, grown[frame])[0] if frame in grown else ""
    if (dx >= 0 and grown.get(frame) == region and not others and all(grown.get(one) == start[one] for one in kept)
            and COLLAPSE and COLLAPSE in top_row and EXPAND not in top_row
            and {one: back.get(one) for one in zones} == {one: start[one] for one in zones}):
        held(f"the glyph of the {key} expands and folds its frame", f"{start[frame]} -> {grown[frame]}, "
             f"the others hidden, {COLLAPSE} in its title; folded back: {back[frame]}")
    else:
        failures.append(f"  ✗ expand {key:<20} glyph at {dx} in {edge!r}; {start.get(frame)} -> {grown.get(frame)} "
                        f"(wanted {region}), still shown {others}; title {top_row!r}; "
                        f"back {[(one, back.get(one)) for one in zones]}")
    return 0
