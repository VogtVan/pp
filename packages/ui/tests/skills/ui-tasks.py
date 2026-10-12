"""Scenario `ui-tasks` -- the Tasks tab says what the teams do (plan ui, batch les-deux-onglets), on the bench's
`pp-team` witness replaying the faces of `team` for three declared teams -- `core-review` and `ops` started,
`veille` never:
- the tasks of every team started in ONE table, `running` by default: the name, else the start of the text cut at
  30 characters; the team, the holders, the progress counted on the face's delegations, the hour of the last event;
  the menu `SHOW` with what each filter keeps, `TEAM` with the teams started alone
- the filters: `for you` the tasks with a question or an end not seen, `all` every task, a team alone
- the band: the task under the cursor whole, then its last action -- its `last` event at rest (batch
  le-suivi-des-taches); `enter` opens its thread, its history read at `log --task`
- the readings: `status --json`, then one `status <name> --json` per team started, `veille` never read; `u` reads again
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "teams")


NAMES = ("review PR 88", "review PR 87", "daily 2026-10-10", "rotate the certificates", "weekly report")
ROW = re.compile(r"(" + "|".join(re.escape(one) for one in NAMES) + r")\S*(?: \S+)*?\s+(core-review|ops)\s+"
                 r"(open|stopped|resolved)\b")


def _rows(text: str) -> list[str]:
    """-> the rows of the table of the tasks: a task's name, its team, its state."""
    return [found.group(0) for found in map(ROW.search, text.split("\n")) if found]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks")

    # --- the tasks of every team, running by default -----------------------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "150x40")
    first = [one for one in house.journal_lines() if one.startswith("status")]
    journal = house.journal_lines()
    text = done.stdout
    rows = _rows(text)
    ops = next((one for one in done.stdout.split("\n") if "rotate the certificates" in one), "")
    counts = {show: bool(re.search(rf"{show}\s+{n}\b", text)) for show, n in
              (("running", 2), ("for you", 3), ("stopped", 1), ("resolved", 2), ("all", 5))}
    status = text.rstrip("\n").split("\n")[-1]
    if (done.returncode == 0 and len(rows) == 2 and any("review PR 88" in one and "core-review" in one for one in rows)
            and "rotate the certificates of th…" in ops and "ops" in ops and "sre, dba" in ops and "1/2" in ops
            and all(counts.values()) and "core-review" in text and "veille" not in text
            and "2/5 task(s)" in status):
        held("the tasks of every team, running by default", f"2 of 5 rows, ops' task named by its text cut "
             f"{ops.split('│')[0].strip()[:40]!r}, 1/2, counts {sorted(counts)}; {status.strip()[:60]!r}")
    else:
        failures.append(f"  ✗ every team                  rc={done.returncode} rows={rows} counts={counts} {status!r} "
                        f"{text[-2500:]!r} {done.stderr[-400:]!r}")

    # --- the filters -------------------------------------------------------------------------------
    for keys, expected, what in (("shift+tab,shift+tab,down", {"review PR 88", "daily 2026-10-10", "weekly report"},
                                  "for you"),
                                 ("shift+tab,shift+tab,down,down,down,down", {"review PR 88", "review PR 87",
                                                                             "daily 2026-10-10", "rotate the certificates",
                                                                             "weekly report"}, "all"),
                                 ("shift+tab,down", {"review PR 88"}, "a team alone")):
        done = house.render("--render", "tasks", "--size", "150x36", "--press", keys)
        rows = _rows(done.stdout)
        found = {name for name in NAMES if any(name in one for one in rows)}
        if done.returncode == 0 and found == expected and len(rows) == len(expected):
            held(f"the filter {what}", f"--press {keys}: {sorted(found)}")
        else:
            failures.append(f"  ✗ filter {what:<20} rc={done.returncode} {sorted(found)} {rows} "
                            f"{done.stdout[-1500:]!r} {done.stderr[-300:]!r}")

    # --- the band: the task whole, then its last action (the first render); enter its thread ----------
    flat = " ".join(text.split())
    house.clear_journal()
    thread = house.render("--render", "tasks", "--size", "150x40", "--press", "enter")
    if ("T3 · open · core-review" in flat and "holders lead, reviewer" in flat and "last: #47 wake-ended" in flat
            and "log core-review T3" not in journal and "log core-review T3" in house.journal_lines()
            and "#45 " in thread.stdout and "[open]" in thread.stdout):
        held("the band: the task whole, then its last action", "T3 · open · core-review, its holders, last: #47 "
             "wake-ended; enter: its history with #45 [open]")
    else:
        failures.append(f"  ✗ band                        {journal} {house.journal_lines()} {text[:4000]!r} "
                        f"{thread.stdout[-2000:]!r}")

    # --- the readings: the teams started alone (the first render), `u` again -------------------------
    house.clear_journal()
    again = house.render("--render", "tasks", "--size", "150x36", "--press", "u")
    second = [one for one in house.journal_lines() if one.startswith("status")]
    if (again.returncode == 0 and sorted(first) == ["status", "status core-review", "status ops"]
            and second.count("status") == 2 and "status veille" not in second):
        held("the readings: the teams started alone, u again", f"{sorted(first)}; after u {len(second)} readings")
    else:
        failures.append(f"  ✗ readings                    rc={again.returncode} {first} {second}")
    return 0
