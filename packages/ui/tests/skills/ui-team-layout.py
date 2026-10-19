"""Scenario `ui-team-layout` -- the Teams and Tasks tabs are a menu beside a pile of horizontal bands, every zone set
apart by a thin line, their menus folded into one line on a narrow screen, on the bench's `pp-team` witness:
- the geometry, read by `--render <pane> --regions` at 60x20 and 80x24: every band of the centre of each tab at the
  same x and of the same width, under the menu's right edge; under 70 columns the menu hidden and the folded line one
  row high, the bands at x 0
- Teams at 80x24: a column of `│` at the menu's right edge, a row of `─` atop the band of the members, a row of `─`
  above the footer's keys; the header and the row of the tabs carry no thin line, the tabs' bar in `━`
- Tasks at 80x24: the `│` at the menu's right edge, a `─` atop the band of the task chosen and between the two menus,
  a `─` above the footer's keys
- the Agents tab: a row of `─` above the footer's keys
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


def _ruled(line: str, x: int, w: int) -> bool:
    """-> whether the row holds a thin rule from column x over w columns."""
    part = line[x:x + w]
    return len(part) == w and set(part) == {"─"}


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

    # --- the geometry, at a narrow and a wide size; the wide regions kept for the thin lines ------------------
    wide = {}
    for pane, bands in (("teams", 3), ("tasks", 3)):
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
                wide[pane] = (menu[0], {one[1]: one for one in band})
            if ok:
                held(f"{pane} at {width}x{height}: a pile of bands", f"{len(band)} bands at x={band[0][2]} "
                     f"w={band[0][4]}; menu w={menu[0][4]}, fold h={fold[0][5]}")
            else:
                failures.append(f"  ✗ {pane} {width}x{height}          rc={done.returncode} {found} "
                                f"{done.stdout[-600:]!r} {done.stderr[-300:]!r}")

    def column(lines: list[str], menu: tuple) -> int:
        """-> how many rows of the menu carry `│` at its right edge."""
        x = menu[2] + menu[4]
        return sum(1 for line in lines[menu[3]:menu[3] + menu[5]] if len(line) > x and line[x] == "│")

    # --- Teams: the menu's column, the band of the members, the footer, the header untouched -----------------
    done = house.render("--render", "teams", "--size", f"{WIDE[0]}x{WIDE[1]}")
    lines = _lines(done.stdout)
    menu, bands = wide.get("teams", (None, {}))
    title = bands.get("teams-members-title")
    footer = _footer_rule(lines)
    header = (not re.search("[─│]", lines[0] + lines[1]) and lines[2].count("━") >= WIDE[0] - 2) if len(lines) > 3 else False
    rule = bool(title) and len(lines) > title[3] and _ruled(lines[title[3]], title[2], title[4])
    if (done.returncode == 0 and menu and column(lines, menu) == menu[5] and rule and footer is not None and header):
        held("Teams set apart by thin lines", f"│ at column {menu[2] + menu[4]} on {column(lines, menu)} rows, ─ atop "
             f"the members (row {title[3]}), ─ above the footer (row {footer}); the header and the tabs as they were")
    else:
        failures.append(f"  ✗ teams                       rc={done.returncode} menu={menu} title={title} rule={rule} "
                        f"footer={footer} header={header} {done.stdout!r} {done.stderr[-300:]!r}")

    # --- Tasks: the menu's column, the rule between its menus, the band of the task chosen -------------------
    done = house.render("--render", "tasks", "--size", f"{WIDE[0]}x{WIDE[1]}")
    lines = _lines(done.stdout)
    menu, bands = wide.get("tasks", (None, {}))
    band = bands.get("tasks-band")
    footer = _footer_rule(lines)
    inner = [index for index in range(menu[3] + 1, menu[3] + menu[5]) if index < len(lines)
             and _ruled(lines[index], menu[2], menu[4])] if menu else []
    rule = bool(band) and len(lines) > band[3] and _ruled(lines[band[3]], band[2], band[4])
    if done.returncode == 0 and menu and column(lines, menu) == menu[5] and inner and rule and footer is not None:
        held("Tasks set apart by thin lines", f"│ at column {menu[2] + menu[4]} on {column(lines, menu)} rows, ─ between "
             f"the menus (row {inner[0]}), ─ atop the band (row {band[3]}), ─ above the footer (row {footer})")
    else:
        failures.append(f"  ✗ tasks                       rc={done.returncode} menu={menu} band={band} inner={inner} "
                        f"rule={rule} footer={footer} {done.stdout!r} {done.stderr[-300:]!r}")

    # --- the Agents tab: the footer set apart ------------------------------------------------------------------
    done = house.render("--render", "agents", "--size", f"{WIDE[0]}x{WIDE[1]}")
    footer = _footer_rule(_lines(done.stdout))
    if done.returncode == 0 and footer is not None:
        held("the Agents tab's footer set apart", f"─ at row {footer}, above the keys")
    else:
        failures.append(f"  ✗ agents                      rc={done.returncode} {done.stdout!r} {done.stderr[-300:]!r}")

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
