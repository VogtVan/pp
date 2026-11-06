"""Scenario `ui-spaces-turn` -- the row of the spaces when nothing may play (plan ui, batch les-boutons-des-espaces),
on the bench's `pp-chat` witness:
- nothing plays during a turn: a click on a button while `ag3`'s turn runs writes nothing on the witness's entry, the
  button takes no focus, the row stays
- a run without a space draws no row and leaves the message line where it stood (`ui-status-line`, `ui-turn`)
- the buttons stand out (batch les-trois-reprises): `--styles` gives `+ PLANS` a background the row's root label has
  not, and a bold label
"""
from __future__ import annotations

import re

from tests.harness import support

P = support(__file__, "dialogue")
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
SIZE = ("--size", "100x30")
TURN = "i,h,i,enter,wait:waiting"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-spaces-turn", P.spaces_script())
    render = post.render

    def sent() -> list[str]:
        return [one for one in post.journal_lines() if one.startswith("space ")]

    # --- nothing plays during a turn --------------------------------------------------------------------------
    post.clear_journal()
    busy = render("ag3", "--render", "dialogue", *SIZE, "--press",
                  "i,h,i,enter,wait:principal,click:#space-open-1:1:0,focus")
    focused = next((one for one in busy.stdout.split("\n") if one.startswith("focused ")), "")
    row_busy = P.spaces_row(busy.stdout)
    if busy.returncode == 0 and sent() == [] and "space-open-1" not in focused and "+ PLANS" in row_busy:
        held("nothing plays during a turn", f"the journal has no space; {focused.strip()!r}; {row_busy[:40]!r}")
    else:
        failures.append(f"  ✗ busy                        rc={busy.returncode} {sent()} {focused!r} {row_busy!r} "
                        f"{busy.stderr[-300:]!r}")

    # --- the buttons stand out ----------------------------------------------------------------------------------
    styled = render("ag1", "--render", "dialogue", *SIZE, "--styles", "--press", TURN)
    row = next((one for one in styled.stdout.split("\n") if "root TURN" in one and "+ PLANS" in one), "")
    segments = SEGMENT.findall(row)
    button = next((style for style, text in segments if "+ PLANS" in text), "")
    root = next((style for style, text in segments if "root TURN" in text), "")
    button_bg, root_bg = background_codes(button), background_codes(root)
    if (styled.returncode == 0 and row and button_bg and not button_bg & root_bg
            and "1" in button.split(";")):
        held("the buttons stand out", f"+ PLANS on {sorted(button_bg)}, bold; the root on {sorted(root_bg) or 'none'}")
    else:
        failures.append(f"  ✗ look                        rc={styled.returncode} row={bool(row)} button={button!r} "
                        f"root={root!r} {styled.stderr[-300:]!r}")

    # --- a run without a space draws no row -------------------------------------------------------------------
    post.use(P.SCRIPT)
    none = render("ag1", "--render", "dialogue", *SIZE, "--regions", "--press", TURN)
    zones = P.zones_of(none.stdout)
    if none.returncode == 0 and "spaces" not in zones and "message" in zones and not P.spaces_row(none.stdout):
        held("a run without a space draws no row", f"zones {sorted(zones)}")
    else:
        failures.append(f"  ✗ no row                      rc={none.returncode} {sorted(zones)} {none.stderr[-300:]!r}")
    return 0
