"""Scenario `ui-footer` -- the footer that holds at any width and the budget of a run (plan ui, batch
le-pied-et-les-overlays), on the bench's `pp-chat` witness:
- at 60x24 every key of the chat reads whole -- `[q] quit` and `[i] write` among them --, on more than one line,
  no key cut in its middle; at 200x50 the keys stand on one line
- the status line of a conversation says the budget of its run, `budget 0.42/2.00 USD` and a bar of ten cells, read
  from `budget {cap, spent, left}` of `ready`, `opened` and `verdict`; the colour says its state -- green, yellow past
  80 %, bold red at 100 % (`--styles`); a run without a cap says `—`
"""
from __future__ import annotations

import re

from tests.harness import support

P = support(__file__, "dialogue")
TURN = "h,i,enter,wait:waiting"
ITEM = re.compile(r"^\[[^\]]+\] \S.*$")          # one key: `[key] label`, whole


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- the keys at 60 and 200 columns ------------------------------------------------------------------
    post = P.Post(bench, "ui-footer")
    narrow = post.render("ag1", "--render", "dialogue", "--size", "60x24")
    wide = post.render("ag1", "--render", "dialogue", "--size", "200x50")
    rows_n, rows_w = P.keys_rows(narrow.stdout), P.keys_rows(wide.stdout)
    keys = P.keys_of(narrow.stdout)
    items = [one for row in rows_n for one in row.split(" · ")]
    if (narrow.returncode == 0 and wide.returncode == 0 and len(rows_n) > 1 and len(rows_w) == 1
            and "[q] quit" in keys and "[i] write" in keys and all(ITEM.match(one) for one in items)
            and all(len(row) <= 58 for row in rows_n)):
        held("the footer grows at 60 columns", f"{len(rows_n)} lines of keys at 60x24, every key whole "
             f"({len(items)} keys, [q] quit and [i] write among them); one line at 200x50")
    else:
        failures.append(f"  ✗ footer width                rc={narrow.returncode}/{wide.returncode} {rows_n} {rows_w} "
                        f"{narrow.stdout[-900:]!r} {narrow.stderr[-300:]!r}")

    # --- the budget of the run on the status line ----------------------------------------------------------
    spent = P.Post(bench, "ui-footer-budget", P.budget_script([0.42, 1.7, 2.0]))
    first = spent.render("ag1", "--render", "dialogue", "--size", "160x30", "--press", TURN, "--styles")
    second = spent.render("ag1", "--render", "dialogue", "--size", "160x30", "--press", f"{TURN},{TURN}", "--styles")
    third = spent.render("ag1", "--render", "dialogue", "--size", "160x30", "--press", f"{TURN},{TURN},{TURN}",
                         "--styles")
    plain = [P.ANSI.sub("", one.stdout).rstrip("\n").split("\n")[-1] for one in (first, second, third)]
    looks = [P.styles_of(one.stdout, pattern) for one, pattern in
             ((first, r"budget 0\.42/2\.00 USD"), (second, r"budget 1\.70/2\.00 USD"), (third, r"budget 2\.00/2\.00 USD"))]
    bars = [re.search(r"budget [\d.]+/2\.00 USD ([▰▱]{10})", line) for line in plain]
    bold = any("1" in code.split(";")[:1] for code in looks[2])
    if (all(one.returncode == 0 for one in (first, second, third)) and all(bars)
            and [bar.group(1).count("▰") for bar in bars] == [2, 9, 10]
            and len({looks[0], looks[1], looks[2]}) == 3 and bold):
        held("the status says the budget of the run", f"{[bar.group(0) for bar in bars]}; three looks, the last "
             "one bold")
    else:
        failures.append(f"  ✗ budget                      {plain} {[sorted(one) for one in looks]} "
                        f"{first.stderr[-300:]!r}")
    free = P.Post(bench, "ui-footer-free", P.budget_script([0.42], cap=None))
    shown = free.render("ag1", "--render", "dialogue", "--size", "160x30", "--press", TURN)
    status = shown.stdout.rstrip("\n").split("\n")[-1]
    if shown.returncode == 0 and "budget" not in status and "prov · m1 · — · —" in status:
        held("a run without a cap says —", status.strip()[:100])
    else:
        failures.append(f"  ✗ no cap                      rc={shown.returncode} {status!r} {shown.stderr[-300:]!r}")
    return 0
