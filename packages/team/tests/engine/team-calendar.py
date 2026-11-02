"""Scenario `team-calendar` -- 8 case(s): every call of the house carries `PP_CRONTAB` and `PP_RUNKEY`, throwaway
files standing for the system's session starts -- never the machine's; the house's ONE relaunch entry is its teams' way
back after a restart, laid and removed with their nets (the timer: `team-timer`; the Windows façade and the refusals:
`team-relaunch`); a season may open without a task.
- `team start` lays the house's ONE entry: `@reboot <python> <engine> --instance <house> team tick --all … # pp-team
  <house>`, the interpreter and the engine by absolute path, the face's `schedule` `{seconds: 300, timer: false,
  relaunch: true, reason: null}` under `--no-tick`; a second team lays nothing more; a season doubles nothing
- the entry leaves only when no team of the house needs its net: the stop of one team keeps it while another's task is
  open, posts and `stop --task` keep it, the stop of the last team removes it
- two starts at once leave one line; a `start` and a `stop` of two teams at once, three rounds, never take the net of
  the team that needs it: the need judged and the line removed under `state/relaunch.lock` (KRU6)
- the tick removes it at `schedule-off` when no other team needs it; a declared ceremony keeps it through a `stop`, and
  `delete` of that team removes it
- `status --json` reads the entry: `relaunch: true` while it stands, the table unchanged by a status; `false` after
- (a) a start without `--message` on a team never started: rc 0, `team-started` alone in the journal, the face says
  `state: idle` with no task, a tick after it writes nothing
- (b) no ceremony declared, no other team in need: the house holds no entry after (a)
- (c) a ceremony declared: the entry is laid at a start without a task (the clock frozen before its hour), nothing rung
- no periodic line is ever written to the crontab witness (KFM17)
"""
from __future__ import annotations

import sys

from tests.harness import race, support

T = support(__file__, "team")

IDLE = "---\nagents: |\n  r agents/r\n  w agents/w\nreports: |\n  w -> r\nroot: r\nschedule: 2\n---\nMerge together.\n"
DAILY = ("---\nagents: |\n  r agents/r\n  w agents/w\nreports: |\n  w -> r\nroot: r\nschedule: 2\nceremonies: |\n"
         "  daily every weekday 09:30 with w -> r\n---\nMeet daily.\n")
RITUAL = "ceremonies: |\n  daily every weekday 09:30 with s -> s\n"


def net_doc(extra: str = "") -> str:
    return f"---\nagents: |\n  s s\nroot: s\n{extra}---\nA net under one agent.\n"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={"r": [{"sleep": 0.1, "body": {"done": "merged"}}]})
    h2 = str(h.house.resolve())

    def table() -> list[str]:
        return h.crontab.read_text(encoding="utf-8").splitlines() if h.crontab.is_file() else []

    def house_lines() -> list[str]:
        return [one for one in table() if one.endswith(f"# pp-team {h2}")]

    def kinds_of(name: str) -> list:
        return [one.get("kind") for one in h.events(name)]

    def call(*args: str) -> list[str]:
        return ["--instance", str(h.house), *args]

    for name in ("sched", "sched2", "sched3", "sched4", "sched5", "ended", "kept"):
        h.declare(name, net_doc())
    h.declare("ritual", net_doc(RITUAL))
    h.declare("idle", IDLE)
    h.declare("daily", DAILY)

    # --- team start lays the house's one entry ----------------------------------------------------------------------
    laid1 = h.call("team", "start", "sched", "--message", "hold the net", "--no-tick")
    one_line = house_lines()
    face1 = h.face("sched")
    laid2 = h.call("team", "start", "sched2", "--message", "hold it too", "--no-tick")
    again2 = h.call("team", "start", "sched", "--no-tick")
    words = one_line[0].split() if one_line else [""] * 3
    if (laid1.returncode == 0 and len(one_line) == 1
            and face1.get("schedule") == {"seconds": 300, "timer": False, "relaunch": True, "reason": None}
            and words[0] == "@reboot" and words[1] == sys.executable and words[2].startswith("/")
            and words[2].endswith("pp.py") and f"--instance {h2} team tick --all >/dev/null 2>&1" in one_line[0]
            and laid2.returncode == 0 and again2.returncode == 0 and house_lines() == one_line and len(table()) == 1):
        held("team start lays the house's one entry", "sched: @reboot, the interpreter and the engine absolute, "
             "`team tick --all`, the mark `# pp-team <house>`; sched2 and a season of sched add nothing")
    else:
        failures.append(f"  ✗ relaunch laid              {laid1.returncode}/{laid2.returncode}/{again2.returncode} "
                        f"face={face1.get('schedule')!r} table={table()} {laid1.stderr[-200:]!r}")

    # --- the entry leaves only when no team needs it ---------------------------------------------------------------
    stop1 = h.call("team", "stop", "sched", "--no-tick")
    after_stop = house_lines()
    back = h.call("team", "post", "sched", "--message", "again", "--no-tick")                 # T2
    more = h.call("team", "post", "sched", "--message", "and more", "--no-tick")              # T3
    partial = h.call("team", "stop", "sched", "--task", "T2", "--no-tick")
    after_partial = house_lines()
    stop_sched = h.call("team", "stop", "sched", "--no-tick")
    after_sched = house_lines()
    stop_last = h.call("team", "stop", "sched2", "--no-tick")
    if (stop1.returncode == 0 and after_stop == one_line and back.returncode == 0 and more.returncode == 0
            and partial.returncode == 0 and after_partial == one_line and stop_sched.returncode == 0
            and after_sched == one_line and stop_last.returncode == 0 and house_lines() == []):
        held("the entry leaves only when no team needs it", "stop sched kept it under sched2's open task; posts and "
             "stop --task kept it; the stop of sched2, the last team in need, removed it")
    else:
        failures.append(f"  ✗ relaunch follows the need  {stop1.returncode}/{back.returncode}/{partial.returncode}/"
                        f"{stop_sched.returncode}/{stop_last.returncode} stop={after_stop} partial={after_partial} "
                        f"sched={after_sched} end={house_lines()} {stop_last.stderr[-200:]!r}")

    # --- two starts at once, then a start and a stop at once: the need judged under the lock -----------------------
    raced_s = race(h.engine, [call("team", "start", "sched3", "--message", "x", "--no-tick"),
                              call("team", "start", "sched4", "--message", "x", "--no-tick")], cwd=h.ws, env=h.env)
    two_starts = house_lines()
    h.call("team", "stop", "sched4", "--no-tick")
    rounds = []
    for stopping, opening in (("sched3", "sched5"), ("sched5", "sched3"), ("sched3", "sched5")):
        verb = ["team", "start", opening, "--message", "x", "--no-tick"] if not h.journal_of(opening).exists() \
            else ["team", "post", opening, "--message", "x", "--no-tick"]
        raced = race(h.engine, [call("team", "stop", stopping, "--no-tick"), call(*verb)], cwd=h.ws, env=h.env)
        rounds.append((all(one.returncode == 0 for one in raced), len(house_lines())))
    if (all(one.returncode == 0 for one in raced_s) and len(two_starts) == 1 and rounds == [(True, 1)] * 3):
        held("the need judged under the lock", "two starts at once: one line; a stop of one team and the start or post "
             "of another at once, three rounds: the line stands each time -- state/relaunch.lock (KRU6)")
    else:
        failures.append(f"  ✗ relaunch races             {[one.returncode for one in raced_s]} starts={two_starts} "
                        f"rounds={rounds} {[one.stderr[-120:] for one in raced_s]!r}")
    h.call("team", "stop", "sched5", "--no-tick")

    # --- the tick removes at schedule-off when nobody needs it; a ceremony keeps; delete removes ----------------------
    ended = h.call("team", "start", "ended", "--message", "end it", *h.harnessed)   # done at its first wake-up
    over = h.settled("ended", lambda found: any(one.get("kind") == "schedule-off" for one in found)
                     and house_lines() == [], timeout=60)
    kept = h.call("team", "start", "kept", "--message", "keep it", "--no-tick")
    ritual1 = h.call("team", "start", "ritual", "--message", "first beat", "--no-tick")
    ritual2 = h.call("team", "stop", "ritual", "--no-tick")
    kept_stop = h.call("team", "stop", "kept", "--no-tick")
    under_ritual = house_lines()
    before_t = table()
    face_r = h.face("ritual")
    same_t = table() == before_t
    gone_r = h.call("team", "delete", "ritual", "--yes")
    face_k = h.face("kept")
    if (ended.returncode == 0 and over and kept.returncode == 0 and ritual1.returncode == 0 and ritual2.returncode == 0
            and kept_stop.returncode == 0 and len(under_ritual) == 1 and face_r.get("schedule", {}).get("relaunch") is True
            and same_t and gone_r.returncode == 0 and house_lines() == []
            and face_k.get("schedule") == {"seconds": 300, "timer": False, "relaunch": False, "reason": None}):
        held("schedule-off, a ceremony, delete", "ended done under the witness: its schedule-off removed the line, nobody "
             "else in need; kept and ritual stopped: ritual's ceremony keeps it, the face says relaunch true, the table "
             "unchanged by a status; delete ritual removed it, the face of kept says relaunch false, no reason")
    else:
        failures.append(f"  ✗ relaunch at schedule-off   {ended.returncode}/{kept.returncode}/{ritual1.returncode}/"
                        f"{ritual2.returncode}/{gone_r.returncode} over={over} ritual={under_ritual} "
                        f"face={face_r.get('schedule')!r}/{face_k.get('schedule')!r} same={same_t} {gone_r.stderr[-200:]!r}")

    # --- (a) a season without a task ------------------------------------------------------------------------------
    started = h.call("team", "start", "idle", *h.harnessed)
    after_start = kinds_of("idle")
    state = h.face("idle")
    ticked = h.call("team", "tick", "idle")
    after_tick = kinds_of("idle")
    if (started.returncode == 0 and after_start == ["team-started"] and state.get("tasks") == []
            and state.get("state") == "idle" and state.get("waiting_on") == [] and ticked.returncode == 0
            and after_tick == after_start):
        held("(a) a season without a task", "rc 0, team-started alone, state idle, a tick writes nothing -- KSST1")
    else:
        failures.append(f"  ✗ (a) a season without a task rc={started.returncode} kinds={after_start} "
                        f"state={state.get('state')} tasks={state.get('tasks')!r} tick={ticked.returncode} "
                        f"after={after_tick} {started.stderr.strip()[-160:]!r}")

    # --- (b) no ceremony, nobody in need: no entry ------------------------------------------------------------------
    if started.returncode == 0 and house_lines() == []:
        held("(b) no ceremony, no entry", "the house holds no entry after a start without a task, no team in need")
    else:
        failures.append(f"  ✗ (b) no ceremony, no entry  rc={started.returncode} lines={house_lines()}")

    # --- (c) a ceremony declared: the entry laid at the start -------------------------------------------------------
    rung = h.call("team", "start", "daily", "--no-tick", now="08:00")               # before the ceremony's hour
    if rung.returncode == 0 and kinds_of("daily") == ["team-started"] and len(house_lines()) == 1:
        held("(c) a ceremony keeps the entry", "laid at a start without a task, nothing rung before its hour")
    else:
        failures.append(f"  ✗ (c) a ceremony's entry     rc={rung.returncode} kinds={kinds_of('daily')} "
                        f"lines={house_lines()} {rung.stderr.strip()[-160:]!r}")

    # --- no periodic line, ever (KFM17) ----------------------------------------------------------------------------
    periodic = [one for one in table() if not one.startswith("@reboot ")]
    if not periodic:
        held("no periodic line, ever", f"{len(table())} line(s) left in the crontab witness, every one @reboot")
    else:
        failures.append(f"  ✗ a periodic line            {periodic}")
    return 0
