"""Scenario `ui-team-layout` -- the Teams and Tasks tabs are a menu beside a pile of horizontal bands, every zone framed
and labelled (batch les-zones-cadrees), their menus folded into one line on a narrow screen, on the bench's `pp-team`
witness:
- the geometry, read by `--render <pane> --regions` at 60x20 and 80x24: every band of the centre of each tab at the
  same x and of the same width, under the menu's right edge -- on Teams the head, the members, the tasks of the member
  and their sequence; on Tasks the list, the summary of the task, its text and its sequence; under 70 columns the menu hidden and the folded line one row high, the bands at x 0
(each zone framed and labelled: `ui-zones-framed`; the menus holding their columns and folded: `ui-team-menus`)
- the sequence of the team expands as the frames of the Tasks tab (batch la-sequence-d-equipe-repliable, s.1920),
  at 130x40: its title closes on `palette.EXPAND`, which takes the look `palette.HOVER` under the mouse; a click on it
  leaves the sequence the one frame beside the menu, as high as the menu, its title closing on `palette.COLLAPSE`;
  `escape`, or a second click on the glyph, gives back the four bands of the centre
- the overlay `B`: its box heavy (`┏━┓`), each of its fields thin (`┌─┐`), no `tall` border left (`▔`)
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the frames of a capture; the palette's constants
B = support(__file__, "tasks_band")    # the glyphs of a frame that expands, the look under the mouse

REGION = re.compile(r"^(menu|fold|band|hbar) (\S+) x=(\d+) y=(\d+) w=(\d+) h=(\d+)$")
NARROW, WIDE = (60, 20), (80, 24)


def _regions(text: str) -> list[tuple]:
    return [(m.group(1), m.group(2), *map(int, m.group(3, 4, 5, 6))) for m in map(REGION.match, text.splitlines()) if m]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-layout")

    # --- the geometry, at a narrow and a wide size ---------------------------------------------------------------
    for pane, bands in (("teams", 4), ("tasks", 4)):      # Tasks: the list, the summary, the text, the sequence
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

    # --- the sequence of the team expands, as the frames of the Tasks tab ----------------------------------------
    size = ("--size", "130x40")
    plain = house.render("--render", "teams", *size, "--styles")
    rows = [P.ANSI.sub("", one) for one in plain.stdout.split("\n")]

    def edge(frame: tuple, text_rows: list[str]) -> str:
        x, y, w, _ = frame
        return text_rows[y][x:x + w] if y < len(text_rows) else ""

    glyphed = [one for one in P.frames_of(plain.stdout) if B.EXPAND and B.EXPAND in edge(one, rows)]
    sequence = max(glyphed, key=lambda one: one[1], default=None)        # the lowest frame with a glyph
    dx = edge(sequence, rows).find(B.EXPAND) if sequence else -1
    glyph = f"#teams-sequence:{max(dx, 0)}:0"
    over = house.render("--render", "teams", *size, "--styles", "--press", f"hover:{glyph}")
    wide = house.render("--render", "teams", *size, "--styles", "--press", f"click:{glyph}")
    looks = [B.look_at(done.stdout.split("\n")[sequence[1]], sequence[0] + dx) if sequence else frozenset()
             for done in (plain, over)]
    hovered = {B.SGR_OF.get(one, one) for one in (B.HOVER or "").split()}
    shown = [P.ANSI.sub("", one) for one in wide.stdout.split("\n")]
    frames = P.frames_of(wide.stdout)
    menu = next((one for one in frames if one[0] == 0), None)
    opened = [one for one in frames if one is not menu]
    backs = [[one[1] for one in _regions(done.stdout) if one[0] == "band"]
             for done in (house.render("--render", "teams", *size, "--regions", "--press", f"click:{glyph},escape"),
                          house.render("--render", "teams", *size, "--regions", "--press",
                                       f"click:{glyph},click:{glyph}"))]
    if (sequence and dx >= 0 and hovered and hovered <= looks[1] and not hovered <= looks[0] and menu
            and len(opened) == 1 and opened[0][1] == menu[1] and opened[0][3] == menu[3]
            and B.COLLAPSE in edge(opened[0], shown)
            and all(one == ["teams-top", "teams-members", "teams-strip", "teams-sequence"] for one in backs)):
        held("the sequence of the team expands", f"its glyph at {dx}, {sorted(looks[0])} -> under the mouse "
             f"{sorted(looks[1])}; a click: the one frame beside the menu {opened[0]}, folding glyph in its title; "
             f"escape and a second click: {backs[0]}")
    else:
        failures.append(f"  ✗ the sequence expands        frame={sequence} glyph at {dx} looks={looks} "
                        f"opened={opened} menu={menu} backs={backs} {shown[3:8]} {wide.stderr[-300:]!r}")

    # --- the overlay B: its box heavy, its fields thin ---------------------------------------------------------
    done = house.render("--render", "teams", "--size", "100x34", "--press", "B")
    text = done.stdout
    if done.returncode == 0 and "┏" in text and "┓" in text and text.count("┌") >= 3 and "▔" not in text:
        held("the overlay heavy, its fields thin", f"┏━┓ for its box, {text.count('┌')} fields in ┌─┐, no ▔ left")
    else:
        failures.append(f"  ✗ overlay B                   rc={done.returncode} ┌={text.count('┌')} ▔={text.count('▔')} "
                        f"{text!r} {done.stderr[-300:]!r}")

    return 0
