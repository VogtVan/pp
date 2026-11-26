"""Scenario `ui-tasks` -- the Tasks tab says what the teams do, on the bench's `pp-team` witness replaying the faces of
`team` for three declared teams -- `core-review` and `ops` started, `veille` never (`_tasks`); its other cases are `ui-
tasks-filters`, `ui-tasks-recent`, `ui-tasks-stats`, `ui-tasks-launched`, `ui-tasks-list-place` and `ui-tasks-guards`'s:
- the tasks of every team started in ONE table, the most recently born first, `recent` by default: the id before the
  name, else the start of the text, cut to `TASK_CELL` cells; the team, the state, the holders, the moment the task was
  born; the menu counting what each filter keeps; the tasks shown over every task on the status line; the cells read
  by the name of their column; the band says the face's cost
- the band: the task under the cursor -- its id, its state, its team, its holders, its text whole --, then its
  sequence, its thread read once at `log`; `enter` opens its thread, its history read at `log` again
- the readings: `status --json`, then one `status <name> --json` per team started, `veille` never read; `u` reads again
"""
from __future__ import annotations

import re

from tests.harness import support

S = support(__file__, "tasks")
T, P = S.T, S.P


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks")

    # --- the tasks of every team, the open ones by default; `u` reads again ----------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "150x41", "--press", "u")   # the band whole above the footer's keys
    journal = house.journal_lines()
    text = done.stdout
    menu, centre = T.sides_of(text)
    rows = S.rows_of(text)
    by_state = {state: sum(1 for _, one in S.TASKS if one["state"] == state) for state in ("open", "stopped", "resolved")}
    counts = [by_state["open"], by_state["open"], len(S.for_you()), by_state["stopped"], by_state["resolved"], 0,
              len(S.TASKS)]                                          # `recurring`: the witness lays no recurrence
    born = [name for _, one in sorted(S.TASKS, key=lambda pair: pair[1]["at"], reverse=True) if one["state"] == "open"
            for name in S.NAMES if name in (one.get("name") or one["text"])]
    menu_counts = [int(found.group(1)) for found in (re.search(r"(\d+)\s*$", one) for one in menu) if found]
    core = T.cells_by_name(centre, "id", "T3")
    ops_task = T.OPS["tasks"][0]
    ops = T.cells_by_name(centre, "id", ops_task["id"], "ops")
    status, band = P.status_of(text), S.band_of(text)
    if (done.returncode == 0 and len(rows) == by_state["open"] and menu_counts[:7] == counts
            and [name for row in rows for name in S.NAMES if name in row] == born
            and core.get("at") == S.moment(S.T3["at"]) and ops.get("at") == S.moment(ops_task["at"])
            and [core.get(one) for one in ("id", "task", "team", "state")] == ["T3", S.T3["name"], "core-review", S.T3["state"]]
            and set(re.findall(r"[\w-]+", core.get("holder", ""))) == set(S.T3["holders"])
            and isinstance(S.CELL, int) and ops.get("id") == ops_task["id"]
            and ops.get("task", "").startswith(ops_task["text"][:S.CELL - 1])
            and len(ops.get("task", "")) == S.CELL and ops.get("task") != ops_task["text"]
            and [ops.get("team"), ops.get("state")] == ["ops", ops_task["state"]]
            and set(re.findall(r"[\w-]+", ops.get("holder", ""))) == set(ops_task["holders"])
            and "veille" not in text and f"{by_state['open']}/{len(S.TASKS)}" in status):
        held("the tasks of every team, recent by default, the newest first", f"{len(rows)} of {len(S.TASKS)} rows "
             f"{born}: {core.get('id')} {core.get('task')} born {core.get('at')}, {ops.get('id')} {ops.get('task')} cut at {S.CELL}, "
             f"the menu counts {counts}")
    else:
        failures.append(f"  ✗ every team                  rc={done.returncode} rows={rows} menu={menu_counts} {core} "
                        f"{ops} {status!r} {text[-2500:]!r} {done.stderr[-400:]!r}")

    # --- the readings: the teams started alone, `u` again (the first render) -----------------------------
    readings = [one for one in journal if one.startswith("status")]
    if (set(readings) == {"status", "status core-review", "status ops"} and readings.count("status") == 2
            and all(readings.count(f"status {team}") == 2 for team in S.TEAMS)):
        held("the readings: the teams started alone, u again", f"{sorted(set(readings))}; after u {len(readings)} "
             "readings")
    else:
        failures.append(f"  ✗ readings                    {journal}")

    # --- the cost of a task, a named task's text whole in the band (the first render) --------------------
    if any(S.T3["text"] in row for row in band) and any(f"{S.T3['cost']:.2f}" in row for row in band):
        held("the cost of a task, a named task's text whole", f"the band says T3's cost {S.T3['cost']:.2f} and its "
             "text whole")
    else:
        failures.append(f"  ✗ cost and text               t3={core} ops={ops} {band}")

    # --- the band: the task whole, then its sequence (the first render); `enter` its thread ----------
    house.clear_journal()
    thread = house.render("--render", "tasks", "--size", "150x40", "--press", "enter")
    title, rows = P.title_of(thread.stdout), P.overlay_rows(thread.stdout)
    asked = next(one for one in T.T3_LOG if one.get("verb") == "ask")
    first = next(one for one in T.T3_LOG if one["event"] == "post")
    if (band and all(one in band[0] for one in ("T3", S.T3["state"], "core-review"))
            and any(all(one in row for one in S.T3["holders"]) for row in band[1:])
            and any(row.startswith(f"#{first['id']} {first['verb']} ") for row in band)
            and journal.count("log core-review T3") == 1 and house.journal_lines().count("log core-review T3") == 2
            and title and all(one in title[0] for one in ("core-review", "T3", S.T3["name"]))
            and any(f"#{asked['id']}" in row and asked["text"] in row for row in rows)
            and all(any(f"#{one['id']}" in row for row in rows) for one in T.T3_LOG)):
        held("the band: the task whole, then its sequence", f"{band[0]!r}, its holders; the row #{first['id']}; enter: "
             f"{title[0]!r}, #{T.T3_LOG[0]['id']} to #{T.T3_LOG[-1]['id']}, the question #{asked['id']} with its text")
    else:
        failures.append(f"  ✗ band                        {band} {house.journal_lines()} {title} {rows} "
                        f"{thread.stderr[-400:]!r}")
    return 0
