"""Scenario `ui-turn-zone` -- the look of the turn zone of the message line (batch les-trois-reprises), on the bench's
`pp-chat` witness: `ag3`'s turn runs 2 s.
- the zone's background during a turn is not the alert's under `pp off` (`--styles`: the background code of the
  glyph's segment against the `pp OFF` mark's)
- the text of the zone is centred: on the middle row of the zone, as many blank columns on its left as on its right
  (one apart), the rows above and below blank (`--regions` for the zone, the plain capture for the text)
"""
from __future__ import annotations

import re

from tests.harness import support

P = support(__file__, "dialogue")
SIZE = ("--size", "120x30")
SPINNER = P.palette_constant("SPINNER")
SEGMENT = re.compile(r"\x1b\[([0-9;]*)m([^\x1b]*)")


def background_codes(style: str) -> set[str]:
    """-> the background codes of one SGR sequence, its parameters walked as the terminal reads them -- `48;2;r;g;b`,
    `48;5;n`, `40`-`47`, `100`-`107` --; a component of a 24-bit foreground is never mistaken for one."""
    found: set[str] = set()
    tokens = [one for one in style.split(";") if one != ""]
    at = 0
    while at < len(tokens):
        token = tokens[at]
        if token in ("38", "48") and at + 1 < len(tokens):
            width = 5 if tokens[at + 1] == "2" else 3 if tokens[at + 1] == "5" else 1
            if token == "48":
                found.add(";".join(tokens[at:at + width]))
            at += width
            continue
        if token.isdigit() and (40 <= int(token) <= 47 or 100 <= int(token) <= 107):
            found.add(token)
        at += 1
    return found


def backgrounds(styled: str, zone: tuple | None) -> set[str]:
    """-> the background codes of the segments that stand inside `zone` (x, y, w, h of a `--regions` capture) in a
    `--styles` capture of the same screen: what the zone is painted with, whatever its text."""
    found: set[str] = set()
    if not zone:
        return found
    x, y, w, h = zone
    for row in styled.split("\n")[y:y + h]:
        at = 0
        for style, piece in SEGMENT.findall(row):
            start, at = at, at + len(piece)
            if piece and start < x + w and at > x:
                found |= background_codes(style)
    return found


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-turn-zone")
    render = post.render
    turning = "i,h,i,enter,wait:principal"

    # --- the background of the zone is not the alert's ------------------------------------------------------
    during = render("ag3", "--render", "dialogue", *SIZE, "--styles", "--press", turning)
    during_at = render("ag3", "--render", "dialogue", *SIZE, "--regions", "--press", turning)
    off = "i,h,i,enter,wait:waiting,escape,o,wait:conduct"
    paused = render("ag1", "--render", "dialogue", *SIZE, "--styles", "--press", off)
    paused_at = render("ag1", "--render", "dialogue", *SIZE, "--regions", "--press", off)
    turn_bg = backgrounds(during.stdout, P.zones_of(during_at.stdout).get("turn"))
    alert_bg = backgrounds(paused.stdout, P.zones_of(paused_at.stdout).get("alert"))
    if (during.returncode == 0 and paused.returncode == 0 and turn_bg and alert_bg and not turn_bg & alert_bg):
        held("the zone's background is not the alert's", f"turn {sorted(turn_bg)}, pp OFF {sorted(alert_bg)}")
    else:
        failures.append(f"  ✗ background                  rc={during.returncode}/{paused.returncode} turn={turn_bg} "
                        f"alert={alert_bg} {during.stderr[-300:]!r}")

    # --- the text is centred in the zone --------------------------------------------------------------------
    regions = during_at
    plain = render("ag3", "--render", "dialogue", *SIZE, "--press", turning)
    zone = P.zones_of(regions.stdout).get("turn")
    rows = plain.stdout.split("\n")
    if zone and len(rows) > zone[1] + 2:
        x, y, w, _ = zone
        slices = [rows[y + n][x:x + w] if len(rows[y + n]) >= x else "" for n in range(3)]
        middle = slices[1]
        left, right = len(middle) - len(middle.lstrip()), len(middle) - len(middle.rstrip())
    else:
        slices, left, right = [], -1, -1
    if (regions.returncode == 0 and plain.returncode == 0 and zone and slices and re.search(rf"[{SPINNER}] \d+ s", slices[1])
            and not slices[0].strip() and not slices[2].strip() and abs(left - right) <= 1):
        held("the text is centred in the zone", f"{slices[1]!r}: {left} left, {right} right; the rows around blank")
    else:
        failures.append(f"  ✗ centred                     rc={regions.returncode}/{plain.returncode} zone={zone} "
                        f"{slices!r} left={left} right={right} {plain.stderr[-300:]!r}")
    return 0
