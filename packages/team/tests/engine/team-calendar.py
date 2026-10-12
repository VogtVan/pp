"""Scenario `team-calendar` -- 6 case(s) (batch le-calendrier, 2026-10-01; split out of
`team-review` by les-scenarios-par-maison, 2026-10-07): every call of the house carries
`PP_CRONTAB`, a throwaway file standing for the operating system's calendar -- never the
machine's.
- `team start` lays ONE line per team: `*/5 * * * * <python> <engine> --instance <house> team tick
  sched … # pp-team <house> sched`, the interpreter and the engine by absolute path; a second team
  adds its own; a season of the standing team (team 0.31.0, no `--message`) doubles nothing
- the line leaves and returns with the tasks: `stop` (nothing open) removes it, a `post` that opens
  a task lays it again, `stop --task` of one task among two keeps it, the last `stop` removes it
- two starts at once lose no line: the table is read and rewritten whole under the house's
  calendar lock (`state/crontab.lock`), so a race of two teams keeps both lines
- the tick removes it at `schedule-off`: a team that ended under the witness has no line, a team
  whose task stays open keeps one; a declared ceremony keeps it through a `stop`
- `schedule:` is declared: `2` lays `*/2`, `off` lays nothing (`team-started.schedule` null, `status`
  says `schedule · off`), `soon` refuses `team-invalid` naming the key, nothing written
- `status` says `schedule · every 5 min · laid`, then `absent` after the stop; the table unchanged by it
"""
from __future__ import annotations

import sys

from tests.harness import race, support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench)
    h2 = str(h.house.resolve())

    def table() -> list[str]:
        return h.crontab.read_text(encoding="utf-8").splitlines() if h.crontab.is_file() else []

    def lines_for(name: str) -> list[str]:
        return [one for one in table() if one.endswith(f"# pp-team {h2} {name}")]

    def net_doc(extra: str = "") -> str:
        return f"---\nagents: |\n  s s\nroot: s\n{extra}---\nA net under one agent.\n"

    # --- team start lays one line per team, found by its mark -------------------------------------
    h.declare("sched", net_doc())
    h.declare("sched2", net_doc())
    laid1 = h.call("team", "start", "sched", "--message", "hold the net", "--no-tick")
    one_line = lines_for("sched")
    laid2 = h.call("team", "start", "sched2", "--message", "hold it too", "--no-tick")
    again2 = h.call("team", "start", "sched", "--no-tick")
    words = one_line[0].split() if one_line else [""] * 7
    if (laid1.returncode == 0 and "schedule not laid" not in laid1.stderr and len(one_line) == 1
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
                        f"sched={one_line} sched2={lines_for('sched2')} {laid1.stderr[-200:]!r}")

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
    h.declare("sched3", net_doc())
    h.declare("sched4", net_doc())
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

    # --- the tick removes at schedule-off; a declared ceremony keeps the line ------------------------
    h.declare("ended", net_doc())                     # one agent, done at its first wake-up: the team ends
    h.declare("kept", net_doc())                      # started without a tick: its task stays open
    ended = h.call("team", "start", "ended", "--message", "end it", *h.harnessed)
    over = h.settled("ended", lambda found: any(one.get("kind") == "schedule-off" for one in found), timeout=60)
    kept = h.call("team", "start", "kept", "--message", "keep it", "--no-tick")
    h.declare("ritual", "---\nagents: |\n  s s\nroot: s\nceremonies: |\n  daily every weekday 09:30 with s -> s\n"
                        "---\nKeep the rhythm.\n")
    ritual1 = h.call("team", "start", "ritual", "--message", "first beat", "--no-tick")
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
    h.declare("every2", net_doc("schedule: 2\n"))
    h.declare("offteam", net_doc("schedule: off\n"))
    h.declare("soonteam", net_doc("schedule: soon\n"))
    fast = h.call("team", "start", "every2", "--message", "quick net", "--no-tick")
    off = h.call("team", "start", "offteam", "--message", "no net", "--no-tick")
    soon = h.call("team", "start", "soonteam", "--message", "bad net", "--no-tick")
    fast_started = next((one for one in h.events("every2") if one.get("kind") == "team-started"), {})
    off_started = next((one for one in h.events("offteam") if one.get("kind") == "team-started"), {})
    status_off = h.call("team", "status", "offteam")
    if (fast.returncode == 0 and len(lines_for("every2")) == 1 and lines_for("every2")[0].startswith("*/2 * * * * ")
            and fast_started.get("schedule") == 2
            and off.returncode == 0 and lines_for("offteam") == []
            and "schedule" in off_started and off_started.get("schedule") is None
            and status_off.returncode == 0 and "schedule · off" in status_off.stdout
            and soon.returncode == 2 and "team-invalid" in soon.stderr and "schedule" in soon.stderr
            and not h.journal_of("soonteam").exists() and lines_for("soonteam") == []):
        held("schedule: declares the interval", "2 lays */2 and team-started.schedule 2; off lays nothing, "
             "schedule null, status says `schedule · off`; soon refuses team-invalid naming the key, nothing written")
    else:
        failures.append(f"  ✗ schedule key                {fast.returncode}/{off.returncode}/{soon.returncode} "
                        f"every2={lines_for('every2')} started={fast_started.get('schedule')!r}/{off_started.get('schedule')!r} "
                        f"{status_off.stdout[-200:]!r} {soon.stderr[-200:]!r}")

    # --- status says the schedule, read in the calendar ---------------------------------------------
    before_t = table()
    status_s2 = h.call("team", "status", "sched2")
    same_t = table() == before_t
    stopped_s2 = h.call("team", "stop", "sched2", "--no-tick")
    status_s2b = h.call("team", "status", "sched2")
    if (status_s2.returncode == 0 and "schedule · every 5 min · laid" in status_s2.stdout and same_t
            and stopped_s2.returncode == 0 and lines_for("sched2") == []
            and status_s2b.returncode == 0 and "schedule · every 5 min · absent" in status_s2b.stdout):
        held("status reads the schedule in the calendar", "sched2: `schedule · every 5 min · laid`, the table "
             "unchanged by a status; after the stop: `absent`")
    else:
        failures.append(f"  ✗ schedule status             {status_s2.returncode}/{stopped_s2.returncode}/"
                        f"{status_s2b.returncode} same={same_t} {status_s2.stdout[-200:]!r} {status_s2b.stdout[-200:]!r}")
    return 0
