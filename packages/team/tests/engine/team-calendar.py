"""Scenario `team-calendar` -- 13 case(s): every call of the house carries `PP_CRONTAB`, a throwaway file
standing for the operating system's calendar -- never the machine's; a season may open without a task.
- `team start` lays ONE line per team: `*/5 * * * * <python> <engine> --instance <house> team tick sched … #
  pp-team <house> sched`, the interpreter and the engine by absolute path, the face's `schedule.laid` true; a
  second team adds its own; a season of the standing team (no `--message`) doubles nothing
- the line leaves and returns with the tasks: `stop` (nothing open) removes it, a `post` that opens a task lays
  it again, `stop --task` of one task among two keeps it, the last `stop` removes it
- two starts at once lose no line: the table is read and rewritten whole under the house's calendar lock
  (`state/crontab.lock`), so a race of two teams keeps both lines
- the tick removes it at `schedule-off`: a team that ends under the witness has no line, a team whose task
  stays open keeps one; a declared ceremony keeps it through a `stop`
- `schedule:` is declared: `2` lays `*/2`, `off` lays nothing (`team-started.schedule` null, the face's
  `schedule` `{minutes: null, laid: null}`), `soon` refuses `team-invalid` (rc 2), nothing written
- `status --json` reads the schedule in the calendar: `{minutes: 5, laid: true}`, then `laid: false` after the
  stop; the table unchanged by a status
- (a) a start without `--message` on a team never started: rc 0, `team-started` alone in the journal, the face
  says `state: idle` with no task, a tick after it writes nothing
- (b) no ceremony declared: the calendar holds no line of the team after (a)
- (c) a ceremony declared: the line is laid at a start without a task (the clock frozen before its hour)
- (d) the first task comes from a post: `post --message` opens T1, lays the line, wakes the root in its run, and
  the root's answer resolves T1
- (e) the TIMER under the minute (batch les-echecs-du-tick, team 0.41.0): `schedule: 1s` -- `team-started.schedule` 1,
  `unit: s`, no cron line ever; the root dies at its first launch (no `--on-end` for a dead harness), the start's tick
  armed a timer (`timer-armed {due}`), which ticks without any call: the failure reaped, the member suspected one
  second, tried by a relance at the next timer, T1 done, `schedule-off`; the mark `tick.timer` gone, no timer process
  alive, `PP_CRONTAB` without a line of the team
- (f) the grammar of `schedule:`: `2m` lays `*/2` (120 s), `5` lays `*/5` (300 s), `30s` lays no line (30 s), `0s` and
  `90s` refuse `team-invalid` (a second at least; whole minutes at the minute and above), nothing written
- (g) the timer's life and launch by system (batch les-lancements-sous-windows, team 0.43.1): `alive(pid, "posix")` says
  a witness process alive, then dead once it ended; `alive(pid, "nt")` never calls `os.kill` (which ends the process
  under Windows) and gives the system's answer; `apart("nt")` a hidden console in its own group, no
  `DETACHED_PROCESS`; `apart("posix")` a session of its own
"""
from __future__ import annotations

import sys

import subprocess
import time

from tests.harness import race, support

T = support(__file__, "team")

IDLE = "---\nagents: |\n  r agents/r\n  w agents/w\nreports: |\n  w -> r\nroot: r\nschedule: 2\n---\nMerge together.\n"
DAILY = ("---\nagents: |\n  r agents/r\n  w agents/w\nreports: |\n  w -> r\nroot: r\nschedule: 2\nceremonies: |\n"
         "  daily every weekday 09:30 with w -> r\n---\nMeet daily.\n")


def net_doc(extra: str = "") -> str:
    return f"---\nagents: |\n  s s\nroot: s\n{extra}---\nA net under one agent.\n"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={"r": [{"sleep": 0.1, "body": {"done": "merged"}}],
                               "f": [{"sleep": 0.1, "body": "crash"}, {"sleep": 0.1, "body": {"re": "DO", "text": "recovered"}}]})
    h2 = str(h.house.resolve())
    by_kind, all_ended = T.by_kind, T.all_ended

    def table() -> list[str]:
        return h.crontab.read_text(encoding="utf-8").splitlines() if h.crontab.is_file() else []

    def lines_for(name: str) -> list[str]:
        return [one for one in table() if one.endswith(f"# pp-team {h2} {name}")]

    def kinds_of(name: str) -> list:
        return [one.get("kind") for one in h.events(name)]

    for name in ("sched", "sched2", "sched3", "sched4", "ended", "kept"):
        h.declare(name, net_doc())
    h.declare("quick", "---\nagents: |\n  f agents/f\nroot: f\nretries: 0\nschedule: 1s\n---\nThe net under the minute.\n")
    for name, value in (("twomin", "2m"), ("thirty", "30s"), ("zero", "0s"), ("ninety", "90s")):
        h.declare(name, net_doc(f"schedule: {value}\n"))
    h.declare("ritual", "---\nagents: |\n  s s\nroot: s\nceremonies: |\n  daily every weekday 09:30 with s -> s\n"
                        "---\nKeep the rhythm.\n")
    h.declare("every2", net_doc("schedule: 2\n"))
    h.declare("offteam", net_doc("schedule: off\n"))
    h.declare("soonteam", net_doc("schedule: soon\n"))
    h.declare("idle", IDLE)
    h.declare("daily", DAILY)

    # --- team start lays one line per team, found by its mark -------------------------------------
    laid1 = h.call("team", "start", "sched", "--message", "hold the net", "--no-tick")
    one_line = lines_for("sched")
    face1 = h.face("sched")
    laid2 = h.call("team", "start", "sched2", "--message", "hold it too", "--no-tick")
    again2 = h.call("team", "start", "sched", "--no-tick")
    words = one_line[0].split() if one_line else [""] * 7
    if (laid1.returncode == 0 and face1.get("schedule") == {"seconds": 300, "minutes": 5, "laid": True} and len(one_line) == 1
            and one_line[0].startswith("*/5 * * * * ")
            and words[5] == sys.executable and words[6].startswith("/") and words[6].endswith("pp.py")
            and f"--instance {h2} team tick sched >/dev/null 2>&1" in one_line[0]
            and laid2.returncode == 0 and len(lines_for("sched2")) == 1
            and again2.returncode == 0
            and lines_for("sched") == one_line):
        held("team start lays one line per team", f"sched: */5, the interpreter and the engine absolute, "
             f"the mark `# pp-team <house> sched`; sched2 adds its own; a season of sched doubles nothing "
             f"({len(table())} line(s) in the table)")
    else:
        failures.append(f"  ✗ schedule laid               {laid1.returncode}/{laid2.returncode}/{again2.returncode} "
                        f"face={face1.get('schedule')!r} sched={one_line} sched2={lines_for('sched2')} "
                        f"{laid1.stderr[-200:]!r}")

    # --- the line leaves and returns with the tasks ------------------------------------------------
    gone1 = h.call("team", "stop", "sched", "--no-tick")
    after_stop = lines_for("sched")
    back = h.call("team", "post", "sched", "--message", "again", "--no-tick")                 # T2
    after_back = lines_for("sched")
    more = h.call("team", "post", "sched", "--message", "and more", "--no-tick")              # T3
    partial = h.call("team", "stop", "sched", "--task", "T2", "--no-tick")
    after_partial = lines_for("sched")
    final_stop = h.call("team", "stop", "sched", "--no-tick")
    if (gone1.returncode == 0 and after_stop == [] and len(lines_for("sched2")) == 1
            and back.returncode == 0 and len(after_back) == 1
            and more.returncode == 0 and partial.returncode == 0 and len(after_partial) == 1
            and final_stop.returncode == 0 and lines_for("sched") == []):
        held("the line leaves and returns with the tasks", "stop sched: its line gone, sched2's intact; a post "
             "lays it again (T2); stop --task T2 with T3 open keeps it; the last stop removes it")
    else:
        failures.append(f"  ✗ schedule follows tasks      {gone1.returncode}/{back.returncode}/{more.returncode}/"
                        f"{partial.returncode}/{final_stop.returncode} stop={after_stop} back={after_back} "
                        f"partial={after_partial} end={lines_for('sched')} {final_stop.stderr[-200:]!r}")

    # --- two starts at once lose no line: the calendar under the house's lock ----------------------
    raced_s = race(h.engine, [["--instance", str(h.house), "team", "start", "sched3", "--message", "x", "--no-tick"],
                              ["--instance", str(h.house), "team", "start", "sched4", "--message", "x", "--no-tick"]],
                   cwd=h.ws, env=h.env)
    if (all(one.returncode == 0 for one in raced_s)
            and len(lines_for("sched3")) == 1 and len(lines_for("sched4")) == 1):
        held("two starts at once lose no line", "sched3 and sched4 started in a race: both lines in the table, "
             "each laid under state/crontab.lock")
    else:
        failures.append(f"  ✗ schedule race               {[one.returncode for one in raced_s]} "
                        f"sched3={lines_for('sched3')} sched4={lines_for('sched4')} "
                        f"{[one.stderr[-120:] for one in raced_s]!r}")

    # --- the remaining teams start before any wait -------------------------------------------------
    ended = h.call("team", "start", "ended", "--message", "end it", *h.harnessed)   # done at its first wake-up
    kept = h.call("team", "start", "kept", "--message", "keep it", "--no-tick")       # its task stays open
    ritual1 = h.call("team", "start", "ritual", "--message", "first beat", "--no-tick")
    fast = h.call("team", "start", "every2", "--message", "quick net", "--no-tick")
    off = h.call("team", "start", "offteam", "--message", "no net", "--no-tick")
    soon = h.call("team", "start", "soonteam", "--message", "bad net", "--no-tick")
    started = h.call("team", "start", "idle", *h.harnessed)                         # a season without a task
    after_start = kinds_of("idle")
    state = h.face("idle")
    ticked = h.call("team", "tick", "idle")
    after_tick = kinds_of("idle")
    rung = h.call("team", "start", "daily", *h.harnessed, now="08:00")              # before the ceremony's hour
    daily_kinds = kinds_of("daily")
    daily_lines = lines_for("daily")

    # --- the tick removes at schedule-off; a declared ceremony keeps the line ------------------------
    over = h.settled("ended", lambda found: any(one.get("kind") == "schedule-off" for one in found)
                     and lines_for("ended") == [], timeout=60)
    ritual2 = h.call("team", "stop", "ritual", "--no-tick")
    if (ended.returncode == 0 and over and lines_for("ended") == [] and kept.returncode == 0 and len(lines_for("kept")) == 1
            and ritual1.returncode == 0 and ritual2.returncode == 0 and len(lines_for("ritual")) == 1):
        held("the tick removes at schedule-off, a ceremony keeps", "ended (done under the witness) without a line, "
             "kept (its task open) keeps one; ritual stopped under its ceremony keeps its line")
    else:
        failures.append(f"  ✗ schedule at schedule-off    {ended.returncode}/{kept.returncode}/{ritual1.returncode}/{ritual2.returncode} "
                        f"over={over} ended={lines_for('ended')} kept={lines_for('kept')} "
                        f"ritual={lines_for('ritual')} {ritual2.stderr[-200:]!r}")

    # --- schedule: declares the interval, off and a bad value --------------------------------------
    fast_started = next((one for one in h.events("every2") if one.get("kind") == "team-started"), {})
    off_started = next((one for one in h.events("offteam") if one.get("kind") == "team-started"), {})
    off_face = h.face("offteam")
    if (fast.returncode == 0 and len(lines_for("every2")) == 1 and lines_for("every2")[0].startswith("*/2 * * * * ")
            and fast_started.get("schedule") == 120 and fast_started.get("unit") == "s"
            and off.returncode == 0 and lines_for("offteam") == []
            and "schedule" in off_started and off_started.get("schedule") is None
            and off_face.get("schedule") == {"seconds": None, "minutes": None, "laid": None}
            and soon.returncode == 2 and "team-invalid" in soon.stderr
            and not h.journal_of("soonteam").exists() and lines_for("soonteam") == []):
        held("schedule: declares the interval", "2 lays */2 and team-started.schedule 120 (unit s); off lays nothing, "
             "schedule null, the face's schedule {seconds: null, minutes: null, laid: null}; soon refuses team-invalid, nothing written")
    else:
        failures.append(f"  ✗ schedule key                {fast.returncode}/{off.returncode}/{soon.returncode} "
                        f"every2={lines_for('every2')} started={fast_started.get('schedule')!r}/{off_started.get('schedule')!r} "
                        f"face={off_face.get('schedule')!r} {soon.stderr[-200:]!r}")

    # --- status says the schedule, read in the calendar ---------------------------------------------
    before_t = table()
    face_s2 = h.face("sched2")
    same_t = table() == before_t
    stopped_s2 = h.call("team", "stop", "sched2", "--no-tick")
    face_s2b = h.face("sched2")
    if (face_s2.get("schedule") == {"seconds": 300, "minutes": 5, "laid": True} and same_t
            and stopped_s2.returncode == 0 and lines_for("sched2") == []
            and face_s2b.get("schedule") == {"seconds": 300, "minutes": 5, "laid": False}):
        held("status reads the schedule in the calendar", "sched2: schedule {seconds: 300, minutes: 5, laid: true}, the table "
             "unchanged by a status; after the stop: laid false")
    else:
        failures.append(f"  ✗ schedule status             {stopped_s2.returncode} same={same_t} "
                        f"{face_s2.get('schedule')!r} {face_s2b.get('schedule')!r}")

    # --- (a) a season without a task
    if (started.returncode == 0 and after_start == ["team-started"] and state.get("tasks") == []
            and state.get("state") == "idle" and state.get("waiting_on") == [] and ticked.returncode == 0
            and after_tick == after_start):
        held("(a) a season without a task", "rc 0, team-started alone, state idle, a tick writes nothing -- KSST1")
    else:
        failures.append(f"  ✗ (a) a season without a task rc={started.returncode} kinds={after_start} "
                        f"state={state.get('state')} tasks={state.get('tasks')!r} tick={ticked.returncode} "
                        f"after={after_tick} {started.stderr.strip()[-160:]!r}")

    # --- (b) no ceremony: no calendar line
    if started.returncode == 0 and lines_for("idle") == []:
        held("(b) no ceremony, no line", "the calendar holds no line of the team after a start without a task")
    else:
        failures.append(f"  ✗ (b) no ceremony, no line   rc={started.returncode} lines={lines_for('idle')}")

    # --- (c) a ceremony declared: the line laid at the start
    if rung.returncode == 0 and daily_kinds == ["team-started"] and len(daily_lines) == 1:
        held("(c) a ceremony keeps the line", "laid at a start without a task, nothing rung before its hour")
    else:
        failures.append(f"  ✗ (c) a ceremony's line      rc={rung.returncode} kinds={daily_kinds} lines={daily_lines} "
                        f"{rung.stderr.strip()[-160:]!r}")

    # --- (e) the timer under the minute -------------------------------------------------------------------------
    quick = h.call("team", "start", "quick", "--message", "catch me", *h.harnessed)
    quick_started = next((one for one in h.events("quick") if one.get("kind") == "team-started"), {})
    over_q = h.settled("quick", lambda found: bool(by_kind(found, "done", task="T1")) and bool(by_kind(found, "schedule-off"))
                       and all_ended(found), timeout=40)
    mark_q = h.records / "teams" / "quick" / "tick.timer"
    gone_at = time.monotonic() + 10                   # the tick that follows the end disarms the timer: the mark leaves
    while time.monotonic() < gone_at and mark_q.exists():
        time.sleep(0.2)
    found_q = h.events("quick")
    kinds_q = [one.get("kind") for one in found_q]
    tries_q = [one.get("relance") for one in T.intents_of(found_q, "f")]
    timers_q = subprocess.run(["pgrep", "-f", f"team timer quick"], capture_output=True, text=True).stdout.strip()
    if (quick.returncode == 0 and quick_started.get("schedule") == 1 and quick_started.get("unit") == "s"
            and lines_for("quick") == [] and over_q and "timer-armed" in kinds_q
            and len(T.finals_of(found_q, "f")) == 1 and tries_q == [None, "tried"]
            and T.result_of(found_q, "T1") == "recovered" and not mark_q.exists() and not timers_q):
        held("(e) the timer under the minute", "schedule 1s: no cron line, timer-armed, the dead launch reaped and the "
             "root tried by the timer's ticks without a call, T1 'recovered', schedule-off, the mark and the process gone")
    else:
        failures.append(f"  ✗ (e) the timer              rc={quick.returncode} started={quick_started.get('schedule')!r}/"
                        f"{quick_started.get('unit')!r} lines={lines_for('quick')} over={over_q} kinds={kinds_q} tries={tries_q} "
                        f"result={T.result_of(found_q, 'T1')!r} mark={mark_q.exists()} timers={timers_q!r} {quick.stderr[-200:]!r}")

    # --- (f) the grammar of schedule: -----------------------------------------------------------------------------
    grammar = {name: h.call("team", "start", name, "--message", "x", "--no-tick") for name in ("twomin", "thirty", "zero", "ninety")}
    kept_g = {name: next((one.get("schedule") for one in h.events(name) if one.get("kind") == "team-started"), "∅")
              for name in grammar}
    if (grammar["twomin"].returncode == 0 and lines_for("twomin")[:1] and lines_for("twomin")[0].startswith("*/2 * * * * ")
            and kept_g["twomin"] == 120
            and grammar["thirty"].returncode == 0 and lines_for("thirty") == [] and kept_g["thirty"] == 30
            and all(grammar[name].returncode == 2 and "team-invalid" in grammar[name].stderr and not h.journal_of(name).exists()
                    and lines_for(name) == [] for name in ("zero", "ninety"))):
        held("(f) the grammar of schedule:", "2m lays */2 (120 s), 30s lays no line (30 s), 0s and 90s refuse team-invalid")
    else:
        failures.append(f"  ✗ (f) the grammar            rc={[(name, one.returncode) for name, one in grammar.items()]} kept={kept_g} "
                        f"twomin={lines_for('twomin')} thirty={lines_for('thirty')} "
                        f"{grammar['zero'].stderr[-120:]!r} {grammar['ninety'].stderr[-120:]!r}")

    # --- (g) the timer's life and launch by system -----------------------------------------------------------------
    team = h.module()
    witness = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    lived = team.alive(witness.pid, "posix")
    witness.kill()
    witness.wait()
    ended = team.alive(witness.pid, "posix")
    signalled, asked = [], []
    kill, system = team.os.kill, team.asked_alive
    team.os.kill = lambda pid, sig: signalled.append((pid, sig))
    team.asked_alive = lambda pid: asked.append(pid) or pid == 4242
    try:
        windows = (team.alive(4242, "nt"), team.alive(4343, "nt"))
    finally:
        team.os.kill, team.asked_alive = kill, system
    hidden, own = team.apart("nt"), team.apart("posix")
    flags = hidden.get("creationflags", 0)
    if (lived and not ended and windows == (True, False) and asked == [4242, 4343] and not signalled
            and set(hidden) == {"creationflags"} and flags & 0x08000000 and flags & 0x00000200 and not flags & 0x00000008
            and own == {"start_new_session": True}):
        held("(g) the timer's life and launch by system", "posix: the witness alive, then dead; nt: the system asked "
             "twice, os.kill never called; apart(nt) CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP without DETACHED_PROCESS, "
             "apart(posix) start_new_session")
    else:
        failures.append(f"  ✗ (g) by system              posix={lived}/{ended} nt={windows} asked={asked} signalled={signalled} "
                        f"apart={hidden}/{own}")

    # --- (d) the first task comes from a post ------------------------------------------------------------------
    posted = h.call("team", "post", "idle", "--message", "merge PR 7")
    laid = lines_for("idle")
    done = h.settled("idle", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    found = h.events("idle")
    opened = by_kind(found, "task", task="T1")
    if (posted.returncode == 0 and len(laid) == 1 and opened and done and T.result_of(found, "T1") == "merged"
            and len(by_kind(found, "wake-intent", agent="r")) == 1):
        held("(d) the first task comes from a post", "T1 opened, the line laid by the post, r woken once, T1 done")
    else:
        failures.append(f"  ✗ (d) the first post         rc={posted.returncode} laid={laid} opened={bool(opened)} "
                        f"done={done} result={T.result_of(found, 'T1')!r} {posted.stderr.strip()[-160:]!r}")
    return 0
