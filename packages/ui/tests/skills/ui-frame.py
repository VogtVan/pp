"""Scenario `ui-frame` -- the frame of the post at any size, on ONE house pinning `ui` -- rendered on its own faces
(no agent, no team) or on the bench's `pp-chat` witness:
- at 80x24 and at 200x50 the frame holds: the header naming the house on the first line, the tabs on the second with
  their bar across the width, the footer at the bottom -- its keys on as many lines as the width asks, the remedy, the
  status --, the pane's text between
- the tabs come in the order of their digits 1 · 2 · 3; `--press 2` shows the Agents tab, `--press 3` the Teams tab --
  each a text of its own, not the dialogue's, with the keys line without its own digit
- the least size is 40x8: below it `size-invalid`, at it eight full lines
- `U` opens the gesture of maintenance: the command it plays shown (`./pp upgrade`) and the post's opening after it
  (`./pp ui`); `enter`, on this throwaway house: the console plays `upgrade`, then the post again, which says what the
  verb answered and takes its `then` out -- once: the post played again asks no more
- `--press` without a key refuses `press-invalid`
- at 60x24 every key of a conversation reads whole -- `[q]` and `[i]` among them --, on more than one line, no key cut
  in its middle; at 240x50 the keys stand on one line
- `[U]` stands among the keys of every tab: the dialogue, the agents, the teams, the tasks
"""
from __future__ import annotations

import re

from conductor import metadata
from tests.harness import cli, support

P = support(__file__, "dialogue")      # the footer's keys, read on any number of lines

BAR = "━"
TABS = re.compile(r"1·\S+.*2·\S+.*3·\S+")
ITEM = re.compile(r"^\[[^\]]+\] \S.*$")          # one key: `[key] label`, whole


def _frame(stdout: str) -> list[str]:
    return stdout.rstrip("\n").split("\n")


def _holds(lines: list[str], width: int, height: int, house: str) -> str:
    """-> "" when the frame holds at (width, height), else what fails."""
    if len(lines) != height:
        return f"{len(lines)} lines, not {height}"
    if max(len(one) for one in lines) > width:
        return f"a line wider than {width}"
    if house not in lines[0]:
        return f"header: {lines[0]!r}"
    if not TABS.search(lines[1]):
        return f"tabs: {lines[1]!r}"
    if lines[2].count(BAR) < width - 2:
        return f"the bar spans {lines[2].count(BAR)} of {width}"
    if not P.entry_of("\n".join(lines), "q"):
        return f"keys line: {P.keys_of(chr(10).join(lines))!r}"
    if " · " not in lines[-1] or not lines[-1].strip().endswith(tuple("0123456789")):
        return f"status line: {lines[-1]!r}"
    return ""


def _body(lines: list[str]) -> str:
    return " ".join("\n".join(lines[3:-3]).split())


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-frame")
    ws, engine = post.ws, post.engine

    def render(*args: str):
        """The post on the house's own faces: no agent, no team."""
        return post.render("--render", *args, witnessed=False)

    # --- the frame holds at two sizes: the same bones, the body between ---------------------
    bodies = {}
    for width, height in ((80, 24), (200, 50)):
        done = render("frame", "--size", f"{width}x{height}")
        lines = _frame(done.stdout)
        gap = _holds(lines, width, height, ws.name) if done.returncode == 0 else f"rc {done.returncode}"
        bodies[width] = _body(lines)
        if not gap and bodies[width] and P.entry_of(done.stdout, "U"):
            held(f"the frame holds at {width}x{height}", "header, tabs and their bar, the empty dialogue's text, "
                 "the footer's three lines")
        else:
            failures.append(f"  ✗ frame {width}x{height}            {gap or 'pane text or [U] missing'} "
                            f"{done.stdout[:200]!r} {done.stderr[-200:]!r}")

    # --- a pressed digit switches the tab: its own text, the keys line without its digit ---------
    tabs = {}
    for digit, key in (("2", "agents"), ("3", "teams")):
        done = render("frame", "--size", "80x24", "--press", digit)
        lines = _frame(done.stdout)
        tabs[key] = body = _body(lines)
        others = [one for one in "123" if one != digit]
        keys = P.keys_of("\n".join(lines))
        if (done.returncode == 0 and body and body != bodies[80] and P.entry_of(done.stdout, "U")
                and f"[{digit}]" not in keys and all(f"[{one}]" in keys for one in others)):
            held(f"--press {digit} shows the {key} tab", f"a text of its own, the keys line {keys.strip()!r}")
        else:
            failures.append(f"  ✗ press {digit}                      rc={done.returncode} {keys!r} "
                            f"{body[:160]!r} {done.stderr[-200:]!r}")
    if tabs.get("agents") and tabs.get("agents") == tabs.get("teams"):
        failures.append(f"  ✗ tabs alike                  {tabs}")

    # --- the least size: refused below, eight full lines at it ------------------------------------
    below = [render("frame", "--size", one) for one in ("39x8", "40x7")]
    least = render("frame", "--size", "40x8")
    lines = _frame(least.stdout)
    if (all(one.returncode == 2 and "size-invalid" in one.stderr and one.stdout == "" for one in below)
            and least.returncode == 0 and len(lines) == 8 and lines[0].strip()
            and "1·" in lines[1] and P.entry_of("\n".join(lines), "q")):
        held("40x8 is the least size", "39x8 and 40x7 refuse size-invalid; at 40x8 the eight lines "
             "carry the header, the tabs and the footer")
    else:
        failures.append(f"  ✗ least size                  {[one.returncode for one in below]} "
                        f"rc={least.returncode} lines={len(lines)} {least.stdout!r}")

    # --- U: the gesture of maintenance, its commands shown; enter asks the console ------------------------
    shown = render("frame", "--size", "120x30", "--press", "U")
    asked = render("frame", "--size", "120x30", "--press", "U,enter")   # played again, U,enter asks no more
    then = metadata.of_package(post.made, "ui").get("then")
    said = P.status_of(asked.stdout)                  # the verb that played and its exit, on the status line
    if (shown.returncode == 0 and "./pp upgrade" in shown.stdout and "./pp ui" in shown.stdout
            and asked.returncode == 0 and "upgrade" in said and re.search(r"\b0\b", said)
            and P.remedy_of(asked.stdout) and then is None):
        held("U asks the console for a maintenance verb", f"the overlay shows ./pp upgrade then ./pp ui; enter: the "
             f"console played upgrade, then the post again, which says it ({said[:60]!r}), its then taken out, and asks no more")
    else:
        failures.append(f"  ✗ maintenance gesture          rc={shown.returncode}/{asked.returncode} then={then!r} "
                        f"{said!r} {shown.stdout[-1200:]!r} {asked.stdout[-1200:]!r} {asked.stderr[-300:]!r}")
    empty = cli(engine, "ui", "--render", "frame", "--press", ",", cwd=ws)
    if empty.returncode == 2 and "press-invalid" in empty.stderr and empty.stdout == "":
        held("--press without a key refuses", "press-invalid, one line, rc 2")
    else:
        failures.append(f"  ✗ press-invalid               rc={empty.returncode} {empty.stderr[-160:]!r}")

    # --- the keys of a conversation at 60 and 240 columns -------------------------------------------------
    narrow = post.render("ag1", "--render", "dialogue", "--size", "60x24")
    wide = post.render("ag1", "--render", "dialogue", "--size", "240x50")
    rows_n, rows_w = P.keys_rows(narrow.stdout), P.keys_rows(wide.stdout)
    items = [one for row in rows_n for one in row.split(" · ")]
    if (narrow.returncode == 0 and wide.returncode == 0 and len(rows_n) > 1 and len(rows_w) == 1
            and P.entry_of(narrow.stdout, "q") and P.entry_of(narrow.stdout, "i") and all(ITEM.match(one) for one in items)
            and all(len(row) <= 58 for row in rows_n)):
        held("the footer grows at 60 columns", f"{len(rows_n)} lines of keys at 60x24, every key whole "
             f"({len(items)} keys, [q] and [i] among them); one line at 240x50")
    else:
        failures.append(f"  ✗ footer width                rc={narrow.returncode}/{wide.returncode} {rows_n} {rows_w} "
                        f"{narrow.stdout[-900:]!r} {narrow.stderr[-300:]!r}")

    # --- `U` at the foot of every tab: the dialogue's, the agents' and the teams' above; the tasks' ---------
    tasks = post.render("ag1", "--render", "tasks", "--size", "240x50")
    if tasks.returncode == 0 and P.entry_of(tasks.stdout, "U") and P.entry_of(wide.stdout, "U"):
        held("U stands at the foot of every tab", "[U] among the keys of the dialogue, the agents, the teams and the tasks")
    else:
        failures.append(f"  ✗ U at the foot               {P.keys_of(tasks.stdout)!r} {P.keys_of(wide.stdout)!r}")
    return 0
