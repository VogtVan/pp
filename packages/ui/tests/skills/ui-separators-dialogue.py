"""Scenario `ui-separators-dialogue` -- the dialogue set apart by the same thin line, in a dark and a light theme (plan ui, batch les-separateurs), on the bench's witness of `agent`, at 80x24:
- a conversation at rest: a row of `─` between the transcript and the message line, the message line in `┌─┐`, a row
  of `─` above the footer
- under `textual-dark` and `textual-light` the same rows, each drawn in a look of its theme -- not the look of the
  status line, and not the same in the two themes (`--styles`)
"""
from __future__ import annotations

import re

from tests.harness import support

P = support(__file__, "dialogue")

RULE = r"^\s*─{60,}\s*$"
STATUS = r"· pp on ·"


def _look(row: str) -> frozenset:
    """-> the styles (SGR sequences) one raw row of a `--styles` capture is drawn with."""
    return frozenset(P.SGR.findall(row)) - {"0", ""}


def _rules(lines: list[str]) -> list[int]:
    return [index for index, line in enumerate(lines) if re.match(RULE, line)]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-separators-dialogue")

    # --- a conversation at rest, in each theme ----------------------------------------------------------
    looks = {}
    for theme in ("textual-dark", "textual-light"):
        P.keep_theme(post.made, theme)
        done = post.render("ag1", "--render", "dialogue", "--size", "80x24", "--styles", keep=True)
        raw = done.stdout.rstrip("\n").split("\n")
        lines = [P.ANSI.sub("", one) for one in raw]
        rules = _rules(lines)
        box = next((index for index, line in enumerate(lines) if "┌" in line and index > 3), None)
        keys = P.keys_rows("\n".join(lines))
        first_keys = next((index for index, line in enumerate(lines) if keys and line.strip() == keys[0]), None)
        looks[theme] = (_look(raw[rules[-1]]) if rules else frozenset(),
                        _look(next((one for one, said in zip(raw, lines) if re.search(STATUS, said)), "")))
        if (done.returncode == 0 and box is not None and box - 1 in rules and first_keys is not None
                and first_keys - 1 in rules):
            held(f"the dialogue set apart under {theme}", f"─ above the message line (row {box - 1}) drawn in ┌─┐, "
                 f"─ above the footer (row {first_keys - 1})")
        else:
            failures.append(f"  ✗ dialogue {theme:<18} rc={done.returncode} rules={rules} box={box} keys={first_keys} "
                            f"{lines!r} {done.stderr[-300:]!r}")
    dark, light = looks["textual-dark"], looks["textual-light"]
    if dark[0] and light[0] and dark[0] != dark[1] and light[0] != light[1] and dark[0] != light[0]:
        held("the line in each theme's look", f"dark {sorted(dark[0])} against its status {sorted(dark[1])}; "
             f"light {sorted(light[0])} against {sorted(light[1])}")
    else:
        failures.append(f"  ✗ looks                       {looks!r}")

    return 0
