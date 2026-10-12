"""Scenario `team-pause-ceremony` -- 1 case(s) (batch la-pause-de-l-equipe, 2026-10-12: row 83 of the study § 18,
team 0.32.0): a ceremony whose hour falls while the team is PAUSED, the clock frozen by `PP_NOW`; each case names
the invariant of `team-sim-reframe.py` it replays.
- (a) resumed the same day (I24, I15): paused at 08:00, the tick of 09:31 rings nothing; a ring at hand at 09:40
  writes its task and wakes nobody (the verb says it); `team resume` at 10:00 rings the day's period -- its hour
  passed, never rung -- and wakes the participants of both rings
The next day is `team-pause-next-day`'s (rule 10).
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")

GONG = ("---\nagents: |\n  f agents/f\n  p1 agents/p1\n  p2 agents/p2\nreports: |\n  p1 p2 -> f\nroot: f\n"
        "ceremonies: |\n  daily every weekday 09:30 with p1 p2 -> f\nschedule: off\n---\nRing on demand.\n")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={"f": [{"sleep": 0.1, "body": {"done": "ok"}}] * 6,
                               "p1": [{"sleep": 0.1, "body": {"done": True}}] * 6,
                               "p2": [{"sleep": 0.1, "body": {"done": True}}] * 6})
    by_kind, all_ended = T.by_kind, T.all_ended

    # --- (a) resumed the same day: the day's period rung at the resume -- I24, I15 --------------------
    h.declare("gong", GONG)
    started = h.call("team", "start", "gong", "--message", "open the day", *h.harnessed, now="07:50")
    opened = h.settled("gong", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 45)
    paused = h.call("team", "pause", "gong", now="08:00")
    silent = h.call("team", "tick", "gong", now="09:31")
    rung = h.call("team", "ring", "gong", "daily", now="09:40")
    found = h.events("gong")
    mark = next((one["id"] for one in by_kind(found, "paused")), 10 ** 9)
    held_back = [one for one in found if one["id"] > mark]
    resumed = h.call("team", "resume", "gong", now="10:00")
    settled = h.settled("gong", lambda found: len(by_kind(found, "done")) >= 3 and all_ended(found), 60)
    found = h.events("gong")
    periods = [one.get("period") for one in by_kind(found, "ceremony-due")]
    lift = next((one["id"] for one in by_kind(found, "unpaused")), 10 ** 9)
    woken = sorted({one.get("agent") for one in by_kind(found, "wake-intent") if one["id"] > lift})
    if (started.returncode == 0 and opened and paused.returncode == 0 and silent.returncode == 0 and rung.returncode == 0
            and resumed.returncode == 0 and settled
            and not by_kind(held_back, "wake-intent")
            and [str(one.get("period")).startswith("manual-") for one in by_kind(held_back, "ceremony-due")] == [True]
            and "paused: nobody woken until team resume" in rung.stdout
            and len(periods) == 2 and periods[1] == "2026-10-01"
            and woken == ["f", "p1", "p2"]):
        held("(a) resumed the same day", f"no ring at 09:31 under the pause; the ring at hand waits; the resume "
             f"at 10:00 rings {periods[1]}, then wakes {woken} -- I24, I15")
    else:
        failures.append(f"  ✗ (a) resumed the same day     rc={started.returncode}/{paused.returncode}/{silent.returncode}/"
                        f"{rung.returncode}/{resumed.returncode} opened={opened} settled={settled} periods={periods} "
                        f"held_back={[(one['id'], one['kind']) for one in held_back]} woken={woken} "
                        f"{rung.stdout.strip()[-160:]!r} {paused.stderr.strip()[-160:]!r}")
    return 0
