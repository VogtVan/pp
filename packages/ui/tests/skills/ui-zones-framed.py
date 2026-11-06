"""Scenario `ui-zones-framed` -- every zone of the post framed and labelled (batch les-zones-cadrees), by the one rule of
the palette, on the bench's `pp-team` witness:
- AMPLE, at 120x40 (70 columns and 30 rows at least): each zone of Teams (the menu `Teams`, the head of the team,
  `Members`, `Tasks of <member>`, `Sequence`), of Tasks (`Show`, `Team`, `Tasks`, the band of the task chosen) and of
  Agents (`Agents`) in a round frame, its corners `╭` `╮` on its top row and its label in that row
- COMPACT, at 80x24 (under 30 rows): each zone shown carries its label in a thin line on its top row, no corner, no row
  of its own for a title
- both sizes: a row of `─` above the footer's keys; the header and the row of the tabs carry no thin line, the tabs'
  bar in `━`
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the footer's keys

ZONE = re.compile(r"^framed (\S+) x=(\d+) y=(\d+) w=(\d+) h=(\d+)$")
TEAMS = ["Teams", T.CORE["team"], "Members", f"Tasks of {T.CORE['members'][0]['member']}", "Sequence"]
TASKS = ["Show", "Team", "Tasks", "T3"]


def _lines(text: str) -> list[str]:
    return text.rstrip("\n").split("\n")


def _footer_rule(lines: list[str]) -> int | None:
    """-> the index of the row of `─` right above the footer's keys, or None."""
    keys = P.keys_rows("\n".join(lines))
    first = next((index for index, line in enumerate(lines) if keys and line.strip() == keys[0]), None)
    above = lines[first - 1].strip() if first else ""
    return first - 1 if above and set(above) == {"─"} else None


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-zones-framed")
    for size, ample in (("120x40", True), ("80x24", False)):
        for pane, labels in (("teams", TEAMS), ("tasks", TASKS), ("agents", ["Agents"])):
            regions = house.render("--render", pane, "--size", size, "--regions")
            lines = _lines(house.render("--render", pane, "--size", size).raw)     # the frames themselves: raw
            footer = _footer_rule(lines)
            tops = {}                                    # the top row of each zone in sight, by the label it carries
            for name, x, y, w, h in [(m.group(1), *map(int, m.group(2, 3, 4, 5)))
                                     for m in map(ZONE.match, regions.stdout.splitlines()) if m]:
                if footer is None or y >= footer:
                    continue                             # laid out under the footer: out of sight
                row = lines[y][x:x + w] if y < len(lines) else ""
                said = next((label for label in labels if label in row), None)
                tops[said or name] = row
            edged = {label: (row.strip()[:1] == "╭" and row.strip()[-1:] == "╮") if ample
                     else (row.strip()[:1] == "─" and "╭" not in row) for label, row in tops.items()}
            plain = not re.search("[─│]", lines[0] + lines[1]) and lines[2].count("━") >= len(lines[0]) - 2
            whole = sorted(tops) == sorted(labels) if ample else set(tops) <= set(labels)
            if regions.returncode == 0 and tops and whole and all(edged.values()) and footer is not None and plain:
                held(f"{pane} framed at {size}", f"{'round frames' if ample else 'thin lines'} labelled {sorted(tops)}; "
                     "the footer set apart, the header and the tabs as they were")
            else:
                failures.append(f"  ✗ {pane} framed {size:<12} {tops} {edged} {chr(10).join(lines)!r}")
    return 0
