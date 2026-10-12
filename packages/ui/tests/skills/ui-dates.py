"""Scenario `ui-dates` -- a datum of another day shows its date (plan ui, batch les-retours-du-reel-0-18), on the
bench's `pp-chat` witness whose faces are dated as the scenario plays -- a run of yesterday, a run of today:
- the table of the agents: an agent whose last run is of yesterday shows `DD/MM HH:MM`, one of today its hour alone
- the overlay of an agent's runs: the same, run by run
- a run of yesterday resumed: the heads of its history say `history #1  DD/MM HH:MM`
"""
from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone

from tests.harness import support

P = support(__file__, "dialogue")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)
    local, before = now.astimezone(), yesterday.astimezone()
    dated = before.strftime("%d/%m %H:%M" if before.year == local.year else "%d/%m/%Y %H:%M")
    hour = local.strftime("%H:%M:%S")

    script = copy.deepcopy(P.SCRIPT)
    ag1, ag2 = script["faces"]["status"]["ag1"], script["faces"]["status"]["ag2"]
    ag1[0]["first_at"] = ag1[0]["last_at"] = yesterday.isoformat()     # w00001, of yesterday
    ag1[1]["first_at"] = ag1[1]["last_at"] = now.isoformat()           # w00009, of today
    ag2[0]["first_at"] = ag2[0]["last_at"] = yesterday.isoformat()     # w00002, of yesterday
    for turn in script["faces"]["exchanges"]["ag1"]["w00001"]:
        turn["at"] = yesterday.isoformat()
    post = P.Post(bench, "ui-dates", script)
    render = post.render

    def row_of(text: str, name: str) -> str:
        return next((line for line in text.split("\n") if f" {name} " in f" {line} "), "")

    # --- the table of the agents ---------------------------------------------------------------------
    table = render("--render", "agents", "--size", "140x30")
    first, second = row_of(table.stdout, "ag1"), row_of(table.stdout, "ag2")
    if table.returncode == 0 and hour in first and dated not in first and dated in second and hour not in second:
        held("the table dates an agent of another day", f"ag1 (its last run today) says {hour}, "
             f"ag2 (its last run yesterday) says {dated}")
    else:
        failures.append(f"  ✗ table                       rc={table.returncode} ag1={first!r} ag2={second!r} "
                        f"{table.stderr[-300:]!r}")

    # --- the overlay of the runs --------------------------------------------------------------------
    runs = render("--render", "dialogue", "--size", "140x30", "--press", "2,enter")
    old, new = row_of(runs.stdout, "w00001"), row_of(runs.stdout, "w00009")
    if runs.returncode == 0 and dated in old and hour not in old and hour in new and dated not in new:
        held("the overlay of the runs dates a run of another day", f"w00001 says {dated}, w00009 says {hour}")
    else:
        failures.append(f"  ✗ runs overlay                rc={runs.returncode} w00001={old!r} w00009={new!r} "
                        f"{runs.stderr[-300:]!r}")

    # --- a run of yesterday resumed: its history dated ------------------------------------------------
    resumed = render("--render", "dialogue", "--size", "140x30", "--press", "2,enter,enter", "--wait", "waiting")
    heads = [line.strip() for line in resumed.stdout.split("\n") if "history #" in line]
    if resumed.returncode == 0 and heads and all(f"history #{n}  {dated}" in " ".join(heads) for n in (1, 2)):
        held("the history of a run of yesterday is dated", f"history #1  {dated} and history #2  {dated}")
    else:
        failures.append(f"  ✗ history                     rc={resumed.returncode} heads={heads} {resumed.stderr[-300:]!r}")
    return 0
