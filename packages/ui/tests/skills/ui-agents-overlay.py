"""Scenario `ui-agents-overlay` -- the overlay of an agent's runs and what it stacks, on ONE post of the bench's `pp-chat`
witness whose script changes by `use()`:
- the overlay of the runs takes the width of a wide screen: at 200x50 its border spans 150 columns at least
- `s` in the overlay of an agent's runs stacks the statistics of the run under the cursor, in three sections: the run
  (its sums), pp (the engine's conduction: blocks, proofs, the seconds spent) and ctx (the context approached from the
  run's flow, pp's share of the flow with what the engine served beside, the voices, the reread) -- none of them for a
  run whose flow was never counted; the seconds pp spent read in `h min s`
- `s` on a conversation's tab: the same statistics, `stats ag1 w00001 --json` in the journal (once for the gauge after
  the verdict, once for `s`); the footer at rest offers `[s]` and no stop
- a datum of another day shows its date: the table of the agents and the overlay of the runs say `DD/MM HH:MM` for
  yesterday and the hour alone for today; the history of a run of yesterday dated
- the house heads the table when `list --json` says it, named by its folder, the overlay of its runs titled the same;
  `./pp ui .` opens the conversation of the house
"""
from __future__ import annotations

import copy
import re
from datetime import datetime, timedelta, timezone

from tests.harness import support

P = support(__file__, "dialogue")
SENT = "i,h,i,enter,wait:waiting,escape"


def row_of(text: str, name: str) -> str:
    return next((line for line in text.split("\n") if f" {name} " in f" {line} "), "")


def counted(text: str) -> list[str]:
    """-> what the statistics of `w00001` say of the faces' figures, by their fields: those missing."""
    wanted = (r"blocks\s+9\b", r"proofs\s+2\b", r"work\s+10\.5\b", r"~17%", r"\b1M\b", r"~33%", r"~56k", r"~54k",
              r"reread\s+~3\.6M", r"tool_result\s+~100k")
    return [one for one in wanted if not re.search(one, text)]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-agents-overlay")
    render = post.render

    # --- the overlay of the runs, wide on a wide screen ---------------------------------------------
    wide = render("--render", "dialogue", "--size", "200x50", "--press", "2,enter")
    spans = [line.count("━") for line in wide.stdout.split("\n") if line.count("━") and "┏" in line]
    title_w = P.title_of(wide.stdout)
    if wide.returncode == 0 and spans and max(spans) >= 150 and title_w[:1] and "ag1" in title_w[0]:
        held("the overlay of the runs is wide", f"its border spans {max(spans)} columns at 200x50")
    else:
        failures.append(f"  ✗ wide runs overlay           rc={wide.returncode} spans={spans} {wide.stderr[-200:]!r}")

    # --- s in the overlay: the statistics stacked over it; the durations in h min s ----------------------------
    measured = render("--render", "dialogue", "--size", "120x50", "--press", "2,enter,s", "--wait", "waiting:1")
    flowless = render("--render", "dialogue", "--size", "120x50", "--press", "2,enter,down,s", "--wait", "waiting:1")
    missing = counted(measured.stdout)
    if (measured.returncode == 0 and not missing and flowless.returncode == 0
            and not re.search(r"~17%|reread\s+~", flowless.stdout)):
        held("s stacks the statistics over the overlay", "run, pp (blocks 9, proofs 2, spent work 10.5 s) and ctx "
             "(~17% of 1M tokens, pp ~33% of the flow, reread ~3.6M); none of the flow's for a run without one")
    else:
        failures.append(f"  ✗ stats                       rc={measured.returncode}/{flowless.returncode} missing={missing} "
                        f"{measured.stdout!r} {flowless.stdout[-800:]!r} {measured.stderr[-300:]!r}")
    spent = next((line.strip() for line in flowless.stdout.split("\n") if "spent" in line), "")
    if ("work 1 h 02 min 05 s" in spent and "proof 5 min 03 s" in spent and "answer 12.3 s" in spent):
        held("the durations read in h min s", spent[:90])
    else:
        failures.append(f"  ✗ durations                   {spent!r}")

    # --- s on a conversation: its run's statistics; the footer --------------------------------------------
    post.clear_journal()
    stats = render("ag1", "--render", "dialogue", "--size", "160x50", "--press", f"{SENT},s", "--wait", "none:1.5")
    said = [one for one in post.journal_lines() if one.startswith("stats ")]
    s_case = (stats.returncode == 0 and not counted(stats.stdout) and said == ["stats ag1 w00001 --json"] * 2)
    s_seen = f"{said} {counted(stats.stdout)} {stats.stderr[-300:]!r}"

    # --- a datum of another day: the table, the overlay of the runs, the history ----------------------------
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
    post.use(script)
    table = render("--render", "agents", "--size", "140x30")
    first, second = row_of(table.stdout, "ag1"), row_of(table.stdout, "ag2")
    if table.returncode == 0 and hour in first and dated not in first and dated in second and hour not in second:
        held("the table dates an agent of another day", f"ag1 (its last run today) says {hour}, "
             f"ag2 (its last run yesterday) says {dated}")
    else:
        failures.append(f"  ✗ table                       rc={table.returncode} ag1={first!r} ag2={second!r} "
                        f"{table.stderr[-300:]!r}")
    runs = render("--render", "dialogue", "--size", "140x30", "--press", "2,enter")
    old, new = row_of(runs.stdout, "w00001"), row_of(runs.stdout, "w00009")
    if runs.returncode == 0 and dated in old and hour not in old and hour in new and dated not in new:
        held("the overlay of the runs dates a run of another day", f"w00001 says {dated}, w00009 says {hour}")
    else:
        failures.append(f"  ✗ runs overlay                rc={runs.returncode} w00001={old!r} w00009={new!r} "
                        f"{runs.stderr[-300:]!r}")
    resumed = render("--render", "dialogue", "--size", "140x30", "--press", "2,enter,enter", "--wait", "waiting")
    if resumed.returncode == 0 and resumed.stdout.count(dated) >= 2:
        held("the history of a run of yesterday is dated", f"its two exchanges headed {dated}")
    else:
        failures.append(f"  ✗ history                     rc={resumed.returncode} {resumed.stdout[-900:]!r} "
                        f"{resumed.stderr[-300:]!r}")
    if (s_case and resumed.returncode == 0                       # the tab of a run resumed, at rest: its footer
            and P.entry_of(resumed.stdout, "s") and not P.entry_of(resumed.stdout, "ctrl+g")):
        held("s shows the run's statistics from its tab", "the journal says stats ag1 w00001 twice (the gauge, then s); "
             "the faces' figures in the overlay; the footer at rest offers [s] and nothing of a stop")
    else:
        failures.append(f"  ✗ s from a tab               {s_seen} {P.keys_of(resumed.stdout)!r}")

    # --- the house heads the table, `./pp ui .` opens its conversation ------------------------------------
    script = copy.deepcopy(P.SCRIPT)
    script["faces"]["list"].insert(0, {"agent": ".", "runs": 1, "running": 0, "responses": 1})
    script["faces"]["status"]["."] = [
        {"agent": ".", "run": "h00001", "name": "", "exchanges": 1, "state": "parked", "stack": "", "session": "h-1",
         "provider": P.PROVIDER, "cost_usd": 0.02, "launches": 1, "responses": 1, "first_message": "la maison",
         "first_at": "2026-10-09T09:00:00+00:00", "last_at": "2026-10-09T09:01:00+00:00"},
        {"agent": ".", "providers": [P.PROVIDER], "last": {"provider": P.PROVIDER, "policy": {}}}]
    script["agents"]["."] = P.script("h00002", "the house says")
    post.use(script)
    house = post.ws.name
    table_h = render("--render", "agents", "--size", "120x30")
    rows = [line for line in table_h.stdout.split("\n") if house in line or "ag1" in line]
    titled = render("--render", "dialogue", "--size", "120x30", "--press", "2,enter")
    title_h = P.title_of(titled.stdout)
    talked = render(".", "--render", "dialogue", "--size", "120x30", "--press", "i,h,i,enter", "--wait", "waiting")
    if (table_h.returncode == 0 and rows and house in rows[0] and titled.returncode == 0 and title_h[:1]
            and house in title_h[0] and "h00001" in titled.stdout
            and talked.returncode == 0 and "the house says" in talked.stdout):
        held("the house heads the table", f"`{house}` first, its overlay titled by it; ./pp ui . talks with it")
    else:
        failures.append(f"  ✗ the house                   rc={table_h.returncode}/{titled.returncode}/{talked.returncode} "
                        f"rows={rows[:2]} {titled.stdout[-600:]!r} {talked.stderr[-200:]!r}")
    return 0
