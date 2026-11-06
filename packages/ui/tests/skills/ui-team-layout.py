"""Scenario `ui-team-layout` -- the Teams and Tasks tabs are a menu beside a pile of horizontal bands, every zone framed
and labelled (batch les-zones-cadrees), their menus folded into one line on a narrow screen, on the bench's `pp-team`
witness:
- the geometry, read by `--render <pane> --regions` at 60x20 and 80x24: every band of the centre of each tab at the
  same x and of the same width, under the menu's right edge -- on Teams the head, the members, the tasks of the member
  and their sequence; under 70 columns the menu hidden and the folded line one row high, the bands at x 0
(each zone framed and labelled: `ui-zones-framed`)
- the overlay `B`: its box heavy (`┏━┓`), each of its fields thin (`┌─┐`), no `tall` border left (`▔`)
- the folded menu of Teams holds the first team of the faces and its state; `]` the next team and its state
- the folded menu of Tasks holds a show and a team -- none of the faces' teams; `]` changes the show alone, `}` sets
  the team to the first team of the faces and leaves the show
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the footer's keys, read on any number of lines; the palette's constants

REGION = re.compile(r"^(menu|fold|band) (\S+) x=(\d+) y=(\d+) w=(\d+) h=(\d+)$")
NARROW, WIDE = (60, 20), (80, 24)
FOLDED = re.compile(r"< (.*?) >")      # a folded menu's value, between its arrows


def _regions(text: str) -> list[tuple]:
    return [(m.group(1), m.group(2), *map(int, m.group(3, 4, 5, 6))) for m in map(REGION.match, text.splitlines()) if m]


def _lines(text: str) -> list[str]:
    return text.rstrip("\n").split("\n")


def _footer_rule(lines: list[str]) -> int | None:
    """-> the index of the row of `─` right above the footer's keys, or None."""
    keys = P.keys_rows("\n".join(lines))
    if not keys:
        return None
    first = next((index for index, line in enumerate(lines) if line.strip() == keys[0]), None)
    if first is None or first == 0:
        return None
    above = lines[first - 1].strip()
    return first - 1 if above and set(above) == {"─"} and len(above) >= len(lines[0]) - 2 else None


def _folded(text: str) -> list[str]:
    """-> the values of the folded menu: the row right under the bar of the tabs."""
    lines = _lines(text)
    bar = next((index for index, line in enumerate(lines) if line.count("━") >= len(lines[0]) - 2), None)
    return FOLDED.findall(lines[bar + 1]) if bar is not None and bar + 1 < len(lines) else []


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-layout")
    sep = P.palette_constant("SEP")
    teams = [one["team"] for one in T.BADGES]

    # --- the geometry, at a narrow and a wide size ---------------------------------------------------------------
    for pane, bands in (("teams", 4), ("tasks", 2)):
        for width, height in (NARROW, WIDE):
            done = house.render("--render", pane, "--size", f"{width}x{height}", "--regions")
            found = _regions(done.stdout)
            menu = [one for one in found if one[0] == "menu"]
            fold = [one for one in found if one[0] == "fold"]
            band = [one for one in found if one[0] == "band"]
            narrow = width < 70
            edge = max((one[2] + one[4] for one in menu), default=0)
            ok = (done.returncode == 0 and len(band) == bands and len({one[2] for one in band}) == 1
                  and len({one[4] for one in band}) == 1 and menu and fold)
            if ok and narrow:
                ok = all(one[4] == 0 for one in menu) and fold[0][5] == 1 and band[0][2] == 0 and band[0][4] == width
            elif ok:
                ok = all(one[4] > 0 for one in menu) and fold[0][5] == 0 and band[0][2] >= edge
            if ok:
                held(f"{pane} at {width}x{height}: a pile of bands", f"{len(band)} bands at x={band[0][2]} "
                     f"w={band[0][4]}; menu w={menu[0][4]}, fold h={fold[0][5]}")
            else:
                failures.append(f"  ✗ {pane} {width}x{height}          rc={done.returncode} {found} "
                                f"{done.stdout[-600:]!r} {done.stderr[-300:]!r}")

    # --- the overlay B: its box heavy, its fields thin ---------------------------------------------------------
    done = house.render("--render", "teams", "--size", "100x34", "--press", "B")
    text = done.stdout
    if done.returncode == 0 and "┏" in text and "┓" in text and text.count("┌") >= 3 and "▔" not in text:
        held("the overlay heavy, its fields thin", f"┏━┓ for its box, {text.count('┌')} fields in ┌─┐, no ▔ left")
    else:
        failures.append(f"  ✗ overlay B                   rc={done.returncode} ┌={text.count('┌')} ▔={text.count('▔')} "
                        f"{text!r} {done.stderr[-300:]!r}")

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
