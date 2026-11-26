"""Scenario `team-timer-relayed` -- 2 case(s) (batch la-continuation-bornee-et-le-tick-releve, s.1357; split out of
`team-timer` to keep each under its target): a TIMER survives its failed tick; every call carries `PP_CRONTAB` and
`PP_RUNKEY`, never the machine's.
- (i) under `schedule: 1s`, TEAM.md taken away, the timer's tick refuses `team-unknown` -- the failed timer arms the
  next at the step, which fails in turn and arms the next: a timer stands, and the owner gets ONE notice of the season
  (`timer: true`, no `about`, the tick's stderr in its `why`) for both failures; TEAM.md back, the next timer's tick
  wakes the member, T1 done, `schedule-off`, no timer left
- (ii) the tick's lock held: the same failed tick on another team while the bench holds its `tick.lock` -- the timer
  takes its mark and its tick refuses `team-unknown`; the relay, which takes the lock without waiting, arms nothing and
  tells nobody: no mark, no `team timer` left, the journal the same to the byte
"""
from __future__ import annotations

import subprocess
import time

from tests.harness import holding, support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={"fl": [{"sleep": 0.1, "body": {"done": "after the failed ticks"}}]})
    by_kind, all_ended = T.by_kind, T.all_ended
    team = h.module()

    h.declare("failing", "---\nagents: |\n  fl agents/fl\nroot: fl\nschedule: 1s\n---\nA tick that fails.\n")
    begun = h.call("team", "start", "failing", "--message", "tick me", *h.harnessed, "--no-tick")
    declared = h.teams / "failing" / "TEAM.md"
    away = declared.with_name("TEAM.md.away")
    declared.rename(away)                              # the console's tick refuses team-unknown
    first = h.timer_spawned("failing", "0123456789abcdef", "0123456789abcdef", sleep=0)
    try:
        first.wait(timeout=20)
    except subprocess.TimeoutExpired:
        first.kill()
    log = h.records / "teams" / "failing" / "follow.log"
    said = lambda: log.read_text(encoding="utf-8").count("team-unknown") if log.is_file() else 0
    deadline = time.monotonic() + 15                   # the timer it armed fails in turn: said in its log
    while time.monotonic() < deadline and said() < 1:
        time.sleep(0.1)
    failed_ticks = 1 + said()
    standing = team.timer_standing(h.house, "failing")
    notices = [one for one in h.events("failing") if one.get("kind") == "post" and one.get("timer")]
    away.rename(declared)
    over = bool(standing) and h.settled("failing", lambda found: bool(by_kind(found, "done", task="T1"))
                                        and bool(by_kind(found, "schedule-off")) and all_ended(found), 30)
    gone = h.timer_gone("failing")
    if (begun.returncode == 0 and failed_ticks >= 2 and standing
            and [(one.get("verb"), one.get("to"), one.get("about")) for one in notices] == [("notice", "house", None)]
            and "team-unknown" in str(notices[0].get("why")) and over and gone):
        held("(i) a timer survives its failed tick", f"{failed_ticks} timer ticks refused team-unknown: each armed the next at "
             "the step, a timer stands, ONE notice to house (timer, no about, the stderr its why); TEAM.md back: T1 done, "
             "schedule-off, no timer left")
    else:
        failures.append(f"  ✗ (i) a timer survives        rc={begun.returncode} failed={failed_ticks} timer={standing} "
                        f"notices={[(one.get('verb'), one.get('to'), one.get('about'), one.get('why')) for one in notices]} "
                        f"over={over} gone={gone} kinds={[one.get('kind') for one in h.events('failing')]}")

    # --- (ii) the tick's lock held: the relay leaves it to the tick that holds it ---------------------------------------
    h.declare("locked", "---\nagents: |\n  lk agents/lk\nroot: lk\nschedule: 1s\n---\nA tick that fails, held.\n")
    begun_ii = h.call("team", "start", "locked", "--message", "tick me", *h.harnessed, "--no-tick")
    declared_ii = h.teams / "locked" / "TEAM.md"
    away_ii = declared_ii.with_name("TEAM.md.away")
    declared_ii.rename(away_ii)
    journal_ii = h.journal_of("locked")
    before_ii = journal_ii.read_bytes()
    mark_ii = h.records / "teams" / "locked" / "tick.timer"
    with holding(journal_ii.parent / "tick.lock"):
        timer_ii = h.timer_spawned("locked", "fedcba9876543210", "fedcba9876543210", sleep=0)
        try:
            timer_ii.wait(timeout=20)
            ended_ii = True                                # the timer ended on its own, the lock still held
        except subprocess.TimeoutExpired:
            timer_ii.kill()
            timer_ii.wait()                                # reaped before anything is read: killed, not ended
            ended_ii = False
        marked_ii = mark_ii.exists()
    away_ii.rename(declared_ii)
    same_ii = journal_ii.read_bytes() == before_ii
    gone_ii = h.timer_gone("locked")
    if begun_ii.returncode == 0 and ended_ii and not marked_ii and same_ii and gone_ii:
        held("(ii) the tick's lock held", "the timer took its mark, its tick refused team-unknown, the relay found the "
             "lock held: no mark, no timer left, the journal the same to the byte")
    else:
        failures.append(f"  ✗ (ii) the lock held          rc={begun_ii.returncode} ended={ended_ii} marked={marked_ii} "
                        f"same={same_ii} gone={gone_ii} {begun_ii.stderr[-200:]!r}")
    return 0
