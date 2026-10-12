"""Scenario `team-ring` -- 2 case(s) (batch la-sonnerie-a-la-main, 2026-10-10: decisions 69-70 of the phase,
team 0.19.0): `team ring <name> <ceremony>` rings a ceremony at hand, out of its hour, the clock frozen by
`PP_NOW`; each case names the invariant of `team-sim-reframe.py` it replays.
- (a) the refusals before any writing: `team-unknown`, `team-not-started`, `ceremony-unknown`,
  `principal-unknown`, the usage without a ceremony -- rc 2, the journal byte-identical; a quorum out of
  its range at `start` (`any 0`, `any 3` of two participants, `any x`) refuses `team-invalid`, no journal
- (b) a ring at hand, then the every at its hour (I15): at 08:00 `team ring gong daily` writes
  `ceremony-due {daily, manual-<its id>, by: house}`, ONE task to f with a `do` and a `delegation` to p1 and
  p2; a second ring while that task is open refuses `ceremony-open` and writes no ring; the participants
  answer, f resolves the task; the tick of 09:31 rings the daily's date, once
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")

GONG = ("---\nagents: |\n  f agents/f\n  p1 agents/p1\n  p2 agents/p2\nreports: |\n  p1 p2 -> f\nroot: f\n"
        "ceremonies: |\n  daily every weekday 09:30 with p1 p2 -> f\nschedule: off\n---\nRing on demand.\n")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "f": [{"sleep": 0.1, "body": {"done": "root"}}, {"sleep": 0.1, "body": {"done": "manual standup"}},
              {"sleep": 0.1, "body": {"done": "daily standup"}}],
        "p1": [{"sleep": 1.5, "body": {"done": True}}, {"sleep": 0.1, "body": {"done": True}}],
        "p2": [{"sleep": 0.2, "body": {"done": True}}, {"sleep": 0.1, "body": {"done": True}}]})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of

    # --- (a) judged before anything is written -------------------------------------------------------
    h.declare("never", GONG)
    h.declare("gong", GONG)
    started = h.call("team", "start", "gong", "--message", "open the day", *h.harnessed, now="07:50")
    root = h.settled("gong", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 45)
    before = h.journal_of("gong").read_bytes()
    refusals = {
        "team-unknown": h.call("team", "ring", "nope", "daily", now="07:55"),
        "team-not-started": h.call("team", "ring", "never", "daily", now="07:55"),
        "ceremony-unknown": h.call("team", "ring", "gong", "weekly", now="07:55"),
        "principal-unknown": h.call("team", "ring", "gong", "daily", "--as", "zz", now="07:55"),
        "usage": h.call("team", "ring", "gong", now="07:55")}
    untouched = h.journal_of("gong").read_bytes() == before
    bad = {}
    for name, tail in (("q0", "any 0"), ("q3", "any 3"), ("qx", "any x")):
        h.declare(name, GONG.replace("with p1 p2 -> f\n", f"with p1 p2 -> f {tail}\n"))
        bad[name] = h.call("team", "start", name, "--message", "x", "--no-tick", now="07:55")
    if (started.returncode == 0 and root and untouched
            and all(one.returncode == 2 and code in one.stderr for code, one in refusals.items())
            and all(one.returncode == 2 and "team-invalid" in one.stderr for one in bad.values())
            and not any(h.journal_of(name).exists() for name in bad)):
        held("(a) judged before writing", "team-unknown, team-not-started, ceremony-unknown, principal-unknown, the "
             "usage: rc 2, the journal byte-identical; any 0, any 3 of two, any x: team-invalid, no journal")
    else:
        failures.append(f"  ✗ (a) judged before writing    rc={started.returncode} root={root} untouched={untouched} "
                        f"{[(code, one.returncode, one.stderr.strip()[-120:]) for code, one in refusals.items()]} "
                        f"{[(name, one.returncode, one.stderr.strip()[-120:]) for name, one in bad.items()]}")

    # --- (b) a ring at hand, a second refused, then the every at its hour -- I15 -----------------------
    rung = h.call("team", "ring", "gong", "daily", now="08:00")
    found = h.events("gong")
    manual = next(iter(by_kind(found, "ceremony-due", ceremony="daily")), {})
    task = next((one for one in found if one.get("kind") == "task" and one.get("ceremony") == "daily"), {})
    dos = [one.get("to") for one in by_kind(found, "post", verb="do") if one.get("task") == task.get("task")]
    delegs = [one.get("to") for one in by_kind(found, "delegation") if one.get("task") == task.get("task")]
    again = h.call("team", "ring", "gong", "daily", now="08:01")
    single = len(by_kind(h.events("gong"), "ceremony-due")) == 1
    resolved = h.settled("gong", lambda found: bool(by_kind(found, "done", task=task.get("task")))
                         and all_ended(found), 45)
    dated = h.call("team", "tick", "gong", now="09:31")
    daily = h.settled("gong", lambda found: len(by_kind(found, "ceremony-due")) == 2
                      and len(by_kind(found, "done")) == 3 and all_ended(found), 45)
    found = h.events("gong")
    dues = by_kind(found, "ceremony-due")
    log = h.call("team", "log", "gong").stdout
    if (rung.returncode == 0 and manual.get("period") == f"manual-{manual.get('id')}" and manual.get("by") == "house"
            and task.get("to") == "f" and task.get("period") == manual.get("period")
            and sorted(dos) == ["p1", "p2"] and sorted(delegs) == ["p1", "p2"]
            and again.returncode == 2 and "ceremony-open" in again.stderr and single and resolved
            and result_of(found, task.get("task")) == "manual standup"
            and dated.returncode == 0 and daily and [one.get("period") for one in dues][1:] == ["2026-10-01"]
            and f"ceremony-due daily · {manual.get('period')} by house" in log):
        held("(b) a ring at hand, then the every", f"08:00: ceremony-due {manual.get('period')} by house, "
             f"{task.get('task')} to f, do + delegation to p1 and p2; a second ring ceremony-open; "
             "'manual standup'; 09:31 rings 2026-10-01, once -- I15")
    else:
        failures.append(f"  ✗ (b) a ring at hand           rc={rung.returncode}/{again.returncode}/{dated.returncode} "
                        f"manual={manual} task={task} dos={dos} delegs={delegs} single={single} resolved={resolved} "
                        f"daily={daily} dues={[(one.get('period'), one.get('by')) for one in dues]} "
                        f"{rung.stderr.strip()[-200:]!r} {again.stderr.strip()[-200:]!r}")
    return 0
