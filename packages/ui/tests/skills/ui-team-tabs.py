"""Scenario `ui-team-tabs` -- the Teams and Tasks tabs are a menu beside a pile of horizontal bands (plan ui, batch
les-deux-onglets), on the bench's `pp-team` witness:
- the geometry, read by `--render <pane> --regions` at 60x20, 80x24 and 200x50: every band of the centre of each
  tab at the same x and of the same width, under the menu's right edge; under 70 columns the menu hidden and the
  folded line one row high, the bands at x 0
- the folded menus: `team: < core-review · working >` -- the team and its state (batch l-etat-et-les-gestes) --,
  `]` the next team; `show: < running > · team: < all >`, `]` the next
  `SHOW`, `}` the next `TEAM`
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "teams")
REGION = re.compile(r"^(menu|fold|band) (\S+) x=(\d+) y=(\d+) w=(\d+) h=(\d+)$")


def _regions(text: str) -> list[tuple]:
    return [(m.group(1), m.group(2), *map(int, m.group(3, 4, 5, 6))) for m in map(REGION.match, text.splitlines()) if m]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-tabs")

    # --- the geometry ------------------------------------------------------------------------------
    for pane, bands in (("teams", 3), ("tasks", 3)):
        for width, height in ((60, 20), (80, 24), (200, 50)):
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

    # --- the folded menus --------------------------------------------------------------------------
    for pane, keys, said in (("teams", "", "team: < core-review · working >"),
                             ("teams", "right_square_bracket", "team: < ops · working >"),
                             ("tasks", "", "show: < running > · team: < all >"),
                             ("tasks", "right_square_bracket", "show: < for you > · team: < all >"),
                             ("tasks", "right_curly_bracket", "show: < running > · team: < core-review >")):
        done = house.render("--render", pane, "--size", "60x20", *(["--press", keys] if keys else []))
        if done.returncode == 0 and said in done.stdout:
            held(f"the folded menu of {pane}{' after ' + keys if keys else ''}", said)
        else:
            failures.append(f"  ✗ folded {pane} {keys:<20} rc={done.returncode} {said!r} {done.stdout[:900]!r} "
                            f"{done.stderr[-300:]!r}")
    return 0
