"""Scenario `ui-agents-house` -- the Agents tab (plan ui), cut from `ui-agents` (rule 10), on the bench's
`pp-chat` witness:
- the overlay of the runs takes the width of a wide screen: at 200x50 its border spans 150 columns at least
  (batch les-retours-du-reel; the other overlays keep 100)
- the house heads the table when `list --json` says it (batch la-maison-et-ses-themes): named by its folder,
  `(house)`, the overlay of its runs titled the same; `./pp ui .` opens the conversation of the house
"""
from __future__ import annotations

import copy

from tests.harness import support

P = support(__file__, "dialogue")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-agents-house")
    render = post.render

    # --- the overlay of the runs, wide on a wide screen ---------------------------------------------
    wide = render("--render", "dialogue", "--size", "200x50", "--press", "2,enter")
    spans = [line.count("━") for line in wide.stdout.split("\n") if line.count("━") and "┏" in line]
    if wide.returncode == 0 and spans and max(spans) >= 150 and "runs of ag1" in wide.stdout:
        held("the overlay of the runs is wide", f"its border spans {max(spans)} columns at 200x50")
    else:
        failures.append(f"  ✗ wide runs overlay           rc={wide.returncode} spans={spans} {wide.stderr[-200:]!r}")

    # --- the house heads the table, `./pp ui .` opens its conversation ------------------------------------
    script = copy.deepcopy(P.SCRIPT)
    script["faces"]["list"].insert(0, {"agent": ".", "runs": 1, "running": 0, "responses": 1})
    script["faces"]["status"]["."] = [
        {"agent": ".", "run": "h00001", "name": "", "exchanges": 1, "state": "parked", "stack": "", "session": "h-1",
         "provider": P.PROVIDER, "cost_usd": 0.02, "launches": 1, "responses": 1, "first_message": "la maison",
         "first_at": "2026-10-09T09:00:00+00:00", "last_at": "2026-10-09T09:01:00+00:00"},
        {"agent": ".", "providers": [P.PROVIDER], "last": {"provider": P.PROVIDER, "policy": {}}}]
    script["agents"]["."] = P.script("h00002", "the house says")
    home = P.Post(bench, "ui-agents-house", script)
    label = f"{home.ws.name} (house)"
    table = home.render("--render", "agents", "--size", "120x30")
    rows = [line for line in table.stdout.split("\n") if "(house)" in line or "ag1" in line]
    titled = home.render("--render", "dialogue", "--size", "120x30", "--press", "2,enter")
    talked = home.render(".", "--render", "dialogue", "--size", "120x30", "--press", "h,i,enter", "--wait", "waiting")
    if (table.returncode == 0 and rows and label in rows[0] and titled.returncode == 0
            and f"runs of {label}" in titled.stdout and "h00001" in titled.stdout
            and talked.returncode == 0 and "the house says" in talked.stdout):
        held("the house heads the table", f"`{label}` first, its overlay titled `runs of {label}`; ./pp ui . talks with it")
    else:
        failures.append(f"  ✗ the house                   rc={table.returncode}/{titled.returncode}/{talked.returncode} "
                        f"rows={rows[:2]} {titled.stdout[-600:]!r} {talked.stderr[-200:]!r}")
    return 0
