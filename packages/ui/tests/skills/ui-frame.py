"""Scenario `ui-frame` -- the frame of the post at any size (plan ui, batch la-charpente-et-la-palette):
- at 80x24 and at 200x50 the frame holds: the header on the first line, the tabs on the second with their bar across the width, the footer at the bottom -- its keys on as many lines as the width asks, the remedy, the status --, the pane's text between
- the tabs come in the order Dialogue · Agents · Teams; `--press 2` shows the Agents tab (its table, the word of a house without agents), `--press 3` the Teams tab (its column, the word of a house without a team) -- each with the keys line without its own digit
- the least size is 40x8: below it `size-invalid`, at it eight full lines
"""
from __future__ import annotations

from tests.harness import cli, support

P = support(__file__, "dialogue")      # the footer's keys, read on any number of lines

BAR = "━"


def _frame(stdout: str) -> list[str]:
    return stdout.rstrip("\n").split("\n")


def _holds(lines: list[str], width: int, height: int, house: str) -> str:
    """-> "" when the frame holds at (width, height), else what fails."""
    if len(lines) != height:
        return f"{len(lines)} lines, not {height}"
    if max(len(one) for one in lines) > width:
        return f"a line wider than {width}"
    if not (lines[0].startswith(f" pp · {house}") and house in lines[0]):
        return f"header: {lines[0]!r}"
    if not ("1·Dialogue" in lines[1] and "2·Agents" in lines[1] and "3·Teams" in lines[1]
            and lines[1].index("1·Dialogue") < lines[1].index("2·Agents") < lines[1].index("3·Teams")):
        return f"tabs: {lines[1]!r}"
    if lines[2].count(BAR) < width - 2:
        return f"the bar spans {lines[2].count(BAR)} of {width}"
    if "[q] quit" not in P.keys_of("\n".join(lines)):
        return f"keys line: {P.keys_of(chr(10).join(lines))!r}"
    if " · " not in lines[-1] or not lines[-1].strip().endswith(tuple("0123456789")):
        return f"status line: {lines[-1]!r}"
    return ""


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("ui-frame", packages=("ui",))
    ws, engine = env.made.parent, env.engine

    def render(*args: str):
        return cli(engine, "ui", "--render", *args, cwd=ws)

    # --- the frame holds at two sizes: the same bones, the body between ---------------------
    for width, height in ((80, 24), (200, 50)):
        done = render("frame", "--size", f"{width}x{height}")
        lines = _frame(done.stdout)
        gap = _holds(lines, width, height, ws.name) if done.returncode == 0 else f"rc {done.returncode}"
        body = "\n".join(lines[3:-3])
        if not gap and "name an agent to talk to" in " ".join(body.split()):
            held(f"the frame holds at {width}x{height}", "header, tabs and their bar, the empty dialogue "
                 "saying how to name an agent, the footer's three lines")
        else:
            failures.append(f"  ✗ frame {width}x{height}            {gap or 'pane text missing'} "
                            f"{done.stdout[:200]!r} {done.stderr[-200:]!r}")

    # --- a pressed digit switches the tab: its text, the keys line without its digit ---------
    for digit, key, said in (("2", "agents", ("last state", "no agent in this house yet")),
                             ("3", "teams", ("Teams ·", "no team declared"))):
        done = render("frame", "--size", "80x24", "--press", digit)
        lines = _frame(done.stdout)
        body = " ".join("\n".join(lines[3:-3]).split())
        others = [one for one in "123" if one != digit]
        keys = P.keys_of("\n".join(lines))
        if (done.returncode == 0 and all(one in body for one in said)
                and f"[{digit}]" not in keys and all(f"[{one}]" in keys for one in others)):
            held(f"--press {digit} shows the {key} tab", f"its text, the keys line {keys.strip()!r}")
        else:
            failures.append(f"  ✗ press {digit}                      rc={done.returncode} {keys!r} "
                            f"{body[:160]!r} {done.stderr[-200:]!r}")

    # --- the least size: refused below, eight full lines at it ------------------------------------
    below = [render("frame", "--size", one) for one in ("39x8", "40x7")]
    least = render("frame", "--size", "40x8")
    lines = _frame(least.stdout)
    if (all(one.returncode == 2 and "size-invalid" in one.stderr and one.stdout == "" for one in below)
            and least.returncode == 0 and len(lines) == 8 and "pp ·" in lines[0]
            and "1·Dialogue" in lines[1] and "[q] quit" in P.keys_of("\n".join(lines))):
        held("40x8 is the least size", "39x8 and 40x7 refuse size-invalid; at 40x8 the eight lines "
             "carry the header, the tabs and the footer")
    else:
        failures.append(f"  ✗ least size                  {[one.returncode for one in below]} "
                        f"rc={least.returncode} lines={len(lines)} {least.stdout!r}")
    empty = cli(engine, "ui", "--render", "frame", "--press", ",", cwd=ws)
    if empty.returncode == 2 and "press-invalid" in empty.stderr and empty.stdout == "":
        held("--press without a key refuses", "press-invalid, one line, rc 2")
    else:
        failures.append(f"  ✗ press-invalid               rc={empty.returncode} {empty.stderr[-160:]!r}")
    return 0
