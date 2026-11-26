"""Scenario `ui-team-menus` -- the menus of the Teams and Tasks tabs (cut out of `ui-team-layout`, batch
la-sequence-d-equipe-repliable, s.1920), on the bench's `pp-team` witness:
- the menu of the teams holds its columns: no horizontal scroll bar (`hbar`) within the menu of Teams, at 72x24 (its
  40 % cap), at the wide size and at 100x34
- the menus of Teams and Tasks are as wide, at 80x24 and at 100x34: one rule of the post gives them their width
- the folded menu of Teams holds the first team of the faces and its state; `]` the next team and its state
- the folded menu of Tasks holds a show and a team -- none of the faces' teams; `]` changes the show alone, `}` sets
  the team to the first team of the faces and leaves the show
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the palette's constants

REGION = re.compile(r"^(menu|fold|band|hbar) (\S+) x=(\d+) y=(\d+) w=(\d+) h=(\d+)$")
NARROW, WIDE = (60, 20), (80, 24)
FOLDED = re.compile(r"< (.*?) >")      # a folded menu's value, between its arrows


def _regions(text: str) -> list[tuple]:
    return [(m.group(1), m.group(2), *map(int, m.group(3, 4, 5, 6))) for m in map(REGION.match, text.splitlines()) if m]


def _lines(text: str) -> list[str]:
    return text.rstrip("\n").split("\n")


def _folded(text: str) -> list[str]:
    """-> the values of the folded menu: the row right under the bar of the tabs."""
    lines = _lines(text)
    bar = next((index for index, line in enumerate(lines) if line.count("━") >= len(lines[0]) - 2), None)
    return FOLDED.findall(lines[bar + 1]) if bar is not None and bar + 1 < len(lines) else []


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-menus")
    sep = P.palette_constant("SEP")
    teams = [one["team"] for one in T.BADGES]

    # --- the menu of the teams holds its columns: no horizontal scroll bar -------------------------------------
    widths = {}
    for width, height in ((72, 24), WIDE, (100, 34)):
        done = house.render("--render", "teams", "--size", f"{width}x{height}", "--regions")
        found = _regions(done.stdout)
        menu = [one for one in found if one[0] == "menu" and one[4] > 0]
        widths[(width, height)] = [one[4] for one in menu]
        edge = max((one[2] + one[4] for one in menu), default=0)
        bars = [one[1] for one in found if one[0] == "hbar" and one[2] < edge]
        if done.returncode == 0 and menu and not bars:
            held(f"teams at {width}x{height}: the menu holds its columns", f"menu w={menu[0][4]}, no hbar")
        else:
            failures.append(f"  ✗ teams hbar {width}x{height}       rc={done.returncode} menu={menu} hbar={bars} "
                            f"{done.stderr[-300:]!r}")

    # --- the menus of Teams and Tasks are as wide --------------------------------------------------------------
    for width, height in (WIDE, (100, 34)):
        done = house.render("--render", "tasks", "--size", f"{width}x{height}", "--regions")
        tasks = [one[4] for one in _regions(done.stdout) if one[0] == "menu" and one[4] > 0]
        beside = widths.get((width, height)) or []
        if done.returncode == 0 and len(tasks) == 1 and tasks == beside:
            held(f"the menus as wide at {width}x{height}", f"Tasks w={tasks[0]}, Teams w={beside[0]}")
        else:
            failures.append(f"  ✗ menus as wide {width}x{height}    rc={done.returncode} tasks={tasks} teams={beside} "
                            f"{done.stderr[-300:]!r}")

    # --- the folded menu of Teams: the team chosen and its state, `]` the next ---------------------------------
    size = f"{NARROW[0]}x{NARROW[1]}"
    for keys, badge in (("", T.BADGES[0]), ("right_square_bracket", T.BADGES[1])):
        done = house.render("--render", "teams", "--size", size, *(["--press", keys] if keys else []))
        said = _folded(done.stdout)
        if done.returncode == 0 and said == [f"{badge['team']}{sep}{badge['state']}"]:
            held(f"the folded menu of teams{' after ' + keys if keys else ''}", f"{badge['team']}, {badge['state']}")
        else:
            failures.append(f"  ✗ folded teams {keys:<20} rc={done.returncode} {said} {done.stdout[:900]!r} "
                            f"{done.stderr[-300:]!r}")

    # --- the folded menu of Tasks: a show and a team; `]` the show alone, `}` the team alone -------------------
    first = house.render("--render", "tasks", "--size", size)
    shown = _folded(first.stdout)
    if first.returncode == 0 and len(shown) == 2 and shown[1] not in teams:
        held("the folded menu of tasks", f"show {shown[0]!r}, team {shown[1]!r} -- none of {teams}")
    else:
        failures.append(f"  ✗ folded tasks                rc={first.returncode} {shown} {first.stdout[:900]!r} "
                        f"{first.stderr[-300:]!r}")
    for keys, wanted in (("right_square_bracket", lambda said: len(shown) == 2 and said[0] != shown[0]
                          and said[1] == shown[1]),
                         ("right_curly_bracket", lambda said: len(shown) == 2 and said[0] == shown[0]
                          and said[1] == teams[0])):
        done = house.render("--render", "tasks", "--size", size, "--press", keys)
        said = _folded(done.stdout)
        if done.returncode == 0 and len(said) == 2 and wanted(said):
            held(f"the folded menu of tasks after {keys}", f"{shown} -> {said}")
        else:
            failures.append(f"  ✗ folded tasks {keys:<20} rc={done.returncode} {shown} -> {said} "
                            f"{done.stdout[:900]!r} {done.stderr[-300:]!r}")
    return 0
