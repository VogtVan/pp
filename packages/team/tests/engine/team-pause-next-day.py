"""Scenario `team-pause-next-day` -- 1 case(s) (batch la-pause-de-l-equipe, 2026-10-12: row 83 of the study § 18,
team 0.32.0): a ceremony whose hour falls while the team is PAUSED, the clock frozen by `PP_NOW`; each case names
the invariant of `team-sim-reframe.py` it replays.
- resumed the next day (I24), cut from `team-pause-ceremony` (rule 10): paused on Thursday at 08:00 and
  resumed on Friday at 09:00, Thursday's period is never rung; the tick of Friday 09:31 rings Friday's
"""
from __future__ import annotations

from tests.harness import cli, support

T = support(__file__, "team")

GONG = ("---\nagents: |\n  f agents/f\n  p1 agents/p1\n  p2 agents/p2\nreports: |\n  p1 p2 -> f\nroot: f\n"
        "ceremonies: |\n  daily every weekday 09:30 with p1 p2 -> f\nschedule: off\n---\nRing on demand.\n")
FRIDAY = "2026-10-02T"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={"f": [{"sleep": 0.1, "body": {"done": "ok"}}] * 6,
                               "p1": [{"sleep": 0.1, "body": {"done": True}}] * 6,
                               "p2": [{"sleep": 0.1, "body": {"done": True}}] * 6})
    by_kind, all_ended = T.by_kind, T.all_ended

    def on_friday(*args: str, at: str):
        return cli(h.engine, "--instance", str(h.house), *args, cwd=h.ws, env={**h.env, "PP_NOW": FRIDAY + at})

    # --- resumed the next day: Thursday's period never rung -- I24 ----------------------------------
    h.declare("bell", GONG)
    started = h.call("team", "start", "bell", "--message", "open the day", *h.harnessed, now="07:50")
    opened = h.settled("bell", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 45)
    paused = h.call("team", "pause", "bell", now="08:00")
    thursday = h.call("team", "tick", "bell", now="18:00")
    resumed = on_friday("team", "resume", "bell", at="09:00")
    early = [one.get("period") for one in by_kind(h.events("bell"), "ceremony-due")]
    friday = on_friday("team", "tick", "bell", at="09:31")
    settled = h.settled("bell", lambda found: len(by_kind(found, "done")) >= 2 and all_ended(found), 60)
    periods = [one.get("period") for one in by_kind(h.events("bell"), "ceremony-due")]
    if (started.returncode == 0 and opened and paused.returncode == 0 and thursday.returncode == 0
            and resumed.returncode == 0 and friday.returncode == 0 and settled
            and early == [] and periods == ["2026-10-02"]):
        held("resumed the next day", "Thursday's period never rung, Friday's at 09:31 -- I24")
    else:
        failures.append(f"  ✗ resumed the next day     rc={started.returncode}/{paused.returncode}/{thursday.returncode}/"
                        f"{resumed.returncode}/{friday.returncode} opened={opened} settled={settled} early={early} "
                        f"periods={periods} {resumed.stderr.strip()[-160:]!r}")
    return 0
