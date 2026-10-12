"""Scenario `ui-separators` -- every zone of the teams' tabs is set apart the same way, by a thin line (plan ui, batch
les-separateurs), on the bench's `pp-team` witness, at 80x24:
- Teams: a column of `│` between the menu and the centre, a row of `─` above the band `Members`
- Tasks: the `│` between the menu and the centre, a `─` above the band of the task chosen and above `Team` in the menu
- the footer: a row of `─` above its keys, on the Teams, Tasks and Agents tabs
- the header and the row of the tabs carry no new line: the header and the tabs plain, the tabs' bar in `━`
- the overlay `B`: its box heavy (`┏━┓`), each of its fields thin (`┌─┐`), no `tall` border left (`▔`)
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the footer's keys, read on any number of lines

RULE = re.compile(r"─{12,}")


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


def _column(lines: list[str], x: int) -> int:
    """-> how many rows of the body carry `│` at column x."""
    return sum(1 for line in lines[3:-4] if len(line) > x and line[x] == "│")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-separators")

    # --- Teams: the menu's column, the band Members, the footer, the header untouched --------------------
    done = house.render("--render", "teams", "--size", "80x24")
    lines = _lines(done.stdout)
    members = next((index for index, line in enumerate(lines) if "Members ·" in line), None)
    above = [lines[index][31:] for index in range(max(3, (members or 0) - 2), members or 0)]
    footer = _footer_rule(lines)
    header = (not re.search("[─│]", lines[0] + lines[1]) and lines[2].count("━") >= 78) if len(lines) > 3 else False
    if (done.returncode == 0 and _column(lines, 30) >= 8 and members and any(RULE.search(one) for one in above)
            and footer is not None and header):
        held("Teams set apart by thin lines", f"│ at column 30 on {_column(lines, 30)} rows, ─ above Members (row "
             f"{members}), ─ above the footer (row {footer}); the header and the tabs as they were")
    else:
        failures.append(f"  ✗ teams                       rc={done.returncode} column={_column(lines, 30)} members={members} "
                        f"above={above!r} footer={footer} header={header} {done.stdout!r} {done.stderr[-300:]!r}")

    # --- Tasks: the menu's column, Team in the menu, the band of the task chosen ---------------------------
    done = house.render("--render", "tasks", "--size", "80x24")
    lines = _lines(done.stdout)
    team = next((index for index, line in enumerate(lines) if re.match(r"\s*Team ·", line[:22])), None)
    footer = _footer_rule(lines)
    band = [index for index, line in enumerate(lines[3:footer or -4], 3) if RULE.search(line[23:])]
    if (done.returncode == 0 and _column(lines, 22) >= 8 and team and RULE.search(lines[team - 1][:22])
            and band and footer is not None):
        held("Tasks set apart by thin lines", f"│ at column 22 on {_column(lines, 22)} rows, ─ above Team (row {team}), "
             f"─ above the band (row {band[0]}), ─ above the footer (row {footer})")
    else:
        failures.append(f"  ✗ tasks                       rc={done.returncode} column={_column(lines, 22)} team={team} "
                        f"band={band} footer={footer} {done.stdout!r} {done.stderr[-300:]!r}")

    # --- the Agents tab: the footer set apart -----------------------------------------------------------
    done = house.render("--render", "agents", "--size", "80x24")
    footer = _footer_rule(_lines(done.stdout))
    if done.returncode == 0 and footer is not None:
        held("the Agents tab's footer set apart", f"─ at row {footer}, above the keys")
    else:
        failures.append(f"  ✗ agents                      rc={done.returncode} {done.stdout!r} {done.stderr[-300:]!r}")

    # --- the overlay B: its box heavy, its fields thin -------------------------------------------------
    done = house.render("--render", "teams", "--size", "100x34", "--press", "B")
    text = done.stdout
    if done.returncode == 0 and "┏" in text and "┓" in text and text.count("┌") >= 3 and "▔" not in text:
        held("the overlay heavy, its fields thin", f"┏━┓ for its box, {text.count('┌')} fields in ┌─┐, no ▔ left")
    else:
        failures.append(f"  ✗ overlay B                   rc={done.returncode} ┌={text.count('┌')} ▔={text.count('▔')} "
                        f"{text!r} {done.stderr[-300:]!r}")
    return 0
