"""Scenario `ui-task-last` -- the LAST ACTION of the task under the cursor, followed without a thread opened (plan ui,
batch le-suivi-des-taches), on the bench's witnesses: `core-review`'s watch says two steps of `reviewer`'s wake-up on
T3 -- each naming its task, its run and its exchange, as the face says them --, `agent flow` replays its kept flow:
- the band of T3 says ONE line for `reviewer` (batch les-taches-vivantes): its last step (`live: reviewer · run
  a01389 · … TURN{4/4} · parked`), then the last call of a tool read from the flow of that exchange (`⚙ WebSearch ·
  "DDR4 spot"`, `flow agents/reviewer a01389 … --exchange 3` in the journal of `agent`); the step before is the
  thread's, no `before:` line
- a task no wake-up was seen on says its last event, as the face says it: ops' T1, `last: #9 wake-launched`
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

OPENED = {**T.STEP, "event": "opened", "stack": None, "wait": None}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-task-last", T.script(watch={"core-review": [{"sleep": 0.3}, OPENED, T.STEP]}))

    # --- the last step and the last call, on one line; no step before ------------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "160x40", "--wait", "team:block")
    text = done.stdout
    lives = [one.strip() for one in text.split("\n") if "live: " in one]
    flows = [one for one in house.chat_lines() if one.startswith("flow ")]
    if (done.returncode == 0 and len(lives) == 1 and "run a01389" in lives[0] and "TURN{4/4} · parked" in lives[0]
            and lives[0].endswith('⚙ WebSearch · "DDR4 spot"') and "before:" not in text
            and any("agents/reviewer a01389" in one and "--exchange 3" in one for one in flows)):
        held("the band says the last action of the task", f"{lives[0][:110]!r}; {flows}")
    else:
        failures.append(f"  ✗ last action                 rc={done.returncode} {lives} {flows} "
                        f"{text[-2000:]!r} {done.stderr[-400:]!r}")

    # --- a task at rest: its last event --------------------------------------------------------------
    rest = house.render("--render", "tasks", "--size", "150x40", "--press", "down")
    last = next((one.strip() for one in rest.stdout.split("\n") if "last:" in one), "")
    if rest.returncode == 0 and "#9 wake-launched" in last and "T1 · open · ops" in " ".join(rest.stdout.split()):
        held("a task at rest says its last event", last)
    else:
        failures.append(f"  ✗ at rest                     rc={rest.returncode} {last!r} {rest.stdout[-1500:]!r}")
    return 0
