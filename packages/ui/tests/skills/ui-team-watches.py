"""Scenario `ui-team-watches` -- ONE watch per team started, never one per task (plan ui, batch le-suivi-des-taches),
on the bench's `pp-team` witness, `core-review` and `ops` started, `veille` never:
- the Tasks tab, then the Teams tab, then the Tasks tab again and T3's thread opened by `enter`: the witness's journal
  says `watch core-review` and `watch ops` once each and no `watch <team> <task>` -- the two tabs and the thread share
  their team's watch
- the post's end ends each: `watch-end core-review`, `watch-end ops`, no witness left
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "teams")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-watches")

    # --- both tabs shown and a thread opened: one watch per team started ------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "130x40", "--press", "3,4,enter")
    watches = [one for one in house.journal_lines() if one.startswith("watch")]
    per_task = [one for one in watches if re.fullmatch(r"watch \S+ \S+", one)]
    if (done.returncode == 0 and watches.count("watch core-review") == 1 and watches.count("watch ops") == 1
            and not per_task and "watch veille" not in watches and "#41 " in done.stdout):
        held("one watch per team started, none per task", f"{[one for one in watches if not one.startswith('watch-end')]}"
             "; T3's thread shown in its overlay")
    else:
        failures.append(f"  ✗ watches                     rc={done.returncode} {watches} {done.stdout[-1500:]!r} "
                        f"{done.stderr[-400:]!r}")

    # --- the post's end ends each ---------------------------------------------------------------------
    ended = [one for one in watches if one.startswith("watch-end")]
    if sorted(ended) == ["watch-end core-review", "watch-end ops"] and not house.alive():
        held("the post's end ends each watch", f"{sorted(ended)}; no witness left")
    else:
        failures.append(f"  ✗ ended                       {watches} alive={house.alive()}")
    return 0
