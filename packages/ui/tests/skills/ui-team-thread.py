"""Scenario `ui-team-thread` -- the thread of a task (plan ui, batches le-fil-de-la-tache, les-deux-onglets and
le-suivi-des-taches), on the Tasks tab and the bench's `pp-team` witness: T3's history at `log --task`, the team's ONE
watch pushing #44 again, then the post #48 and a step of `reviewer`'s wake-up -- each naming T3 -- and the
`wake-ended` #49, which names no task:
- `enter` on T3 (the first task running) opens its thread in an overlay: its history -- `[open]` on the ask #45 that
  `waiting.questions` counts --, then the live flow, #44 once, #48 after; `live:` says the step; the history read
  again at the overlay's first object brings #46, written meanwhile, in its place, and at #49 brings #49 -- no watch
  of a task, the team's alone
- `escape` closes the thread: the band of the task again, no watch of a task
- moving the cursor opens nothing: no history read without `enter`
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

POST_48 = T.event("09:13:00", "post", 48, task="T3", **{"from": "lead"}, to="reviewer", verb="reply", text="412 held")
ENDED_49 = T.event("09:14:00", "wake-ended", 49, tag="reviewer-T3-3", agent="reviewer", run="a01389", index=3, cost=0.02)
WATCH = [{"sleep": 1.0}, T.T3_LOG[3], {"sleep": 0.4}, POST_48, T.STEP, {"sleep": 0.3}, ENDED_49]
READS = T.T3_READS + [sorted(T.T3_READS[1] + [POST_48, ENDED_49], key=lambda one: one["id"])]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    script = T.script(watch={"core-review": WATCH})
    script["log"]["core-review/T3"] = READS
    house = T.Teams(bench, "ui-team-thread", script)

    # --- the history, then the live flow, without a hole or a twin ----------------------------------
    done = house.render("--render", "tasks", "--size", "130x40", "--press", "enter,wait:team:wake-ended")
    lines = done.stdout.split("\n")
    at = {number: [index for index, line in enumerate(lines) if f"#{number} " in line and "→" in line or
                   f"#{number} " in line and "wake-ended" in line] for number in (41, 44, 45, 46, 48, 49)}
    ask = next((line for line in lines if "#45 " in line and "→" in line), "")
    live = next((line for line in lines if "live:" in line), "")
    journal = house.journal_lines()
    if (done.returncode == 0 and all(at[one] for one in (41, 45, 48, 49)) and len(at[44]) == 1 and len(at[46]) == 1
            and at[45][0] < at[46][0] < at[48][0] < at[49][0] and "[open]" in ask and "reviewer" in live
            and "TURN{4/4}" in live and journal.count("log core-review T3") >= 2
            and "watch core-review T3" not in journal and journal.count("watch core-review") == 1
            and "watch-end core-review" in journal and not house.alive()):
        held("the thread of a task: its history, then its live flow", f"#44 once, #46 and #49 read again in their place, "
             f"#48 after #45 [open]; {live.strip()[:70]!r}; {journal.count('log core-review T3')} history readings, the "
             "team's one watch, ended with the post")
    else:
        failures.append(f"  ✗ thread                      rc={done.returncode} {at} {ask!r} {live!r} {journal} "
                        f"alive={house.alive()} {done.stdout[-1800:]!r} {done.stderr[-400:]!r}")

    # --- escape closes the thread ----------------------------------------------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "130x40", "--press", "enter,escape")
    watched = [one for one in house.journal_lines() if one.startswith("watch")]
    if (done.returncode == 0 and "#41 " not in done.stdout and "T3 · open · core-review" in " ".join(done.stdout.split())
            and not any(one.endswith(" T3") for one in watched)):
        held("escape closes the thread", f"{watched}; the band of T3 again")
    else:
        failures.append(f"  ✗ thread closed               rc={done.returncode} {watched} {done.stdout[-900:]!r}")

    # --- moving the cursor opens nothing ---------------------------------------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "130x40", "--press", "shift+tab,tab,down,up")
    logs = [one for one in house.journal_lines() if one.startswith("log ")]
    if done.returncode == 0 and logs == [] and not house.alive():
        held("moving the cursor opens nothing", "shift+tab, tab, down, up: no history read without enter")
    else:
        failures.append(f"  ✗ quick moves                 rc={done.returncode} {logs} alive={house.alive()}")
    return 0
