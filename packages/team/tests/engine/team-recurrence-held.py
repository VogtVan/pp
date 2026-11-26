"""Scenario `team-recurrence-held` -- 4 case(s): a RECURRENCE (`team post … --every`) that cannot sound -- before
its pose, under a pause, while its occurrence before is still open, or already opened by another tick --, and its stop
while an occurrence is open. Three teams side by side in one house under a frozen clock (`PP_NOW`): Monday 2026-10-05, Tuesday, Wednesday; the pose, the
sounding and the faces are `team-recurrence`'s.
- (c) `since` and the pause: posted Monday 10:00, the recurrence does not sound that Monday; paused Monday 11:00, the
  tick of Tuesday 09:31 opens nothing; `team resume` Wednesday 10:00 opens Wednesday's occurrence -- never Tuesday's
- (d) an occurrence still open: Monday's, held behind a gate, is open on Tuesday at 09:31 -- `recurrence-skipped
  {open: T1}`, nothing opens; `team stop --recurrence R1` writes `recurrence-stopped`, T1 lives on and resolves once
  the gate opens; Wednesday 09:31 opens nothing; a second stop refuses `recurrence-stopped`, `R9` `recurrence-unknown`
- (g) two writers at once: four `team tick` of one team played at the same instant at Monday 09:31 open ONE occurrence
  -- the period judged again under the journal's lock, behind the tick's
- (h) a slot of a duration held (study § 21, row 121): `--every 1h` posted Monday 10:00, its first occurrence behind a
  gate; the tick of 11:01 writes `recurrence-skipped {period: 2026-10-05T11:00, open: T1}` and opens nothing; the gate
  open, T1 resolves; 12:01 opens the slot of 12:00
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from tests.harness import support

T = support(__file__, "team")

MONDAY, TUESDAY, WEDNESDAY, PAIR = T.MONDAY, T.TUESDAY, T.WEDNESDAY, T.PAIR


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})
    by_kind, all_ended = T.by_kind, T.all_ended
    for name, m, w in (("late", "lm", "lw"), ("slow", "sm", "sw"), ("twin", "tm", "tw")):
        h.declare(name, PAIR.format(m=m, w=w))
    h.declare("hold", PAIR.format(m="hm", w="hw"))
    hold_gate = bench.temp() / "hold-gate"               # (h) hw's first slot held open until its gate stands
    hold_started = h.call("team", "start", "hold", *T.gated(h, hold_gate, ("hw",)), now=MONDAY + "07:50")
    gate = bench.temp() / "slow-gate"                    # sw's first occurrence held open until the gate stands
    started = {name: h.call("team", "start", name, *(T.gated(h, gate, ("sw",)) if name == "slow" else h.harnessed),
                            now=MONDAY + "07:50") for name in ("late", "slow", "twin")}
    slow_posed = h.call("team", "post", "slow", "--message", "build the report", "--to", "sw", "--every", "day 09:30",
                        "--no-tick", now=MONDAY + "08:00")
    late_posed = h.call("team", "post", "late", "--message", "late", "--to", "lw", "--every", "day 09:30", "--no-tick",
                        now=MONDAY + "10:00")
    paused = h.call("team", "pause", "late", now=MONDAY + "11:00")
    twin_posed = h.call("team", "post", "twin", "--message", "count once", "--to", "tw", "--every", "day 09:30",
                        "--no-tick", now=MONDAY + "08:00")
    with ThreadPoolExecutor(4) as pool:                  # (g) four writers at the same instant
        twins = list(pool.map(lambda _: h.call("team", "tick", "twin", now=MONDAY + "09:31"), range(4)))
    monday = {name: h.call("team", "tick", name, now=MONDAY + ("10:05" if name == "late" else "09:31"))
              for name in ("slow", "late")}
    slow_open = h.settled("slow", lambda found: bool(by_kind(found, "wake-launched", agent="sw")), 30)

    # --- Tuesday ----------------------------------------------------------------------------------------------------
    tuesday = {name: h.call("team", "tick", name, now=TUESDAY + "09:31") for name in ("slow", "late")}
    skipped = by_kind(h.events("slow"), "recurrence-skipped")
    halted = h.call("team", "stop", "slow", "--recurrence", "R1", now=TUESDAY + "09:40")
    twice = h.call("team", "stop", "slow", "--recurrence", "R1", now=TUESDAY + "09:41")
    unknown = h.call("team", "stop", "slow", "--recurrence", "R9", now=TUESDAY + "09:41")
    t1_alive = (h.face("slow", now=TUESDAY + "09:42").get("tasks") or [{}])[0].get("state")
    gate.write_text("open", encoding="utf-8")
    slow_done = h.settled("slow", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 45)

    # --- (c) since and the pause -----------------------------------------------------------------------------------
    quiet = [one.get("period") for one in by_kind(h.events("late"), "task")]
    resumed = h.call("team", "resume", "late", now=WEDNESDAY + "10:00")
    late_done = h.settled("late", lambda found: bool(by_kind(found, "done")) and all_ended(found), 45)
    late_tasks = [one.get("period") for one in by_kind(h.events("late"), "task")]
    if (all(one.returncode == 0 for one in started.values()) and late_posed.returncode == 0
            and paused.returncode == 0 and monday["late"].returncode == 0
            and tuesday["late"].returncode == 0 and quiet == [] and resumed.returncode == 0 and late_done
            and late_tasks == ["2026-10-07"]):
        held("(c) since and the pause", "posted Monday 10:00: nothing that Monday; paused, nothing Tuesday; resumed "
             "Wednesday 10:00: Wednesday's occurrence alone")
    else:
        failures.append(f"  ✗ (c) since and the pause      rc={late_posed.returncode}/{paused.returncode}/"
                        f"{resumed.returncode} quiet={quiet} tasks={late_tasks} done={late_done} "
                        f"{late_posed.stderr.strip()[-200:]!r}")

    # --- (d) an occurrence still open ------------------------------------------------------------------------------
    wednesday = h.call("team", "tick", "slow", now=WEDNESDAY + "09:31")
    found = h.events("slow")
    stopped = by_kind(found, "recurrence-stopped")
    if (slow_posed.returncode == 0 and slow_open and tuesday["slow"].returncode == 0
            and [(one.get("period"), one.get("open")) for one in skipped] == [("2026-10-06", "T1")]
            and halted.returncode == 0 and [one.get("recurrence") for one in stopped] == ["R1"]
            and t1_alive == "open" and slow_done and wednesday.returncode == 0
            and [one.get("task") for one in by_kind(found, "task")] == ["T1"]
            and twice.returncode == 2 and "recurrence-stopped" in twice.stderr
            and unknown.returncode == 2 and "recurrence-unknown" in unknown.stderr):
        held("(d) an occurrence still open", "Tuesday: recurrence-skipped {open: T1}, nothing opens; the stop writes "
             "recurrence-stopped, T1 lives on and resolves; Wednesday nothing; recurrence-stopped, recurrence-unknown")
    else:
        failures.append(f"  ✗ (d) an occurrence still open  rc={slow_posed.returncode}/{halted.returncode}/"
                        f"{twice.returncode}/{unknown.returncode} open={slow_open} skipped={skipped} stopped={stopped} "
                        f"t1={t1_alive} done={slow_done} tasks={[one.get('task') for one in by_kind(found, 'task')]} "
                        f"{halted.stderr.strip()[-160:]!r}")

    # --- (g) two writers at once ------------------------------------------------------------------------------------
    twin_done = h.settled("twin", lambda found: bool(by_kind(found, "done")) and all_ended(found), 45)
    occurrences = [one.get("period") for one in by_kind(h.events("twin"), "task") if one.get("recurrence")]
    if (twin_posed.returncode == 0 and all(one.returncode == 0 for one in twins) and twin_done
            and occurrences == ["2026-10-05"]):
        held("(g) two writers at once", "four ticks at 09:31 at the same instant: one occurrence, 2026-10-05")
    else:
        failures.append(f"  ✗ (g) two writers at once      rc={twin_posed.returncode}/{[one.returncode for one in twins]} "
                        f"done={twin_done} occurrences={occurrences}")

    # --- (h) a slot of a duration held -------------------------------------------------------------------------------
    hold_posed = h.call("team", "post", "hold", "--message", "watch", "--to", "hw", "--every", "1h", "--no-tick",
                        now=MONDAY + "10:00")
    hold_first = h.call("team", "tick", "hold", now=MONDAY + "10:00")
    hold_open = h.settled("hold", lambda found: bool(by_kind(found, "wake-launched", agent="hw")), 30)
    hold_later = h.call("team", "tick", "hold", now=MONDAY + "11:01")
    hold_skipped = [(one.get("period"), one.get("open")) for one in by_kind(h.events("hold"), "recurrence-skipped")]
    hold_tasks = [one.get("task") for one in by_kind(h.events("hold"), "task")]
    hold_gate.write_text("open", encoding="utf-8")
    hold_done = h.settled("hold", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 45)
    hold_next = h.call("team", "tick", "hold", now=MONDAY + "12:01")
    hold_two = h.settled("hold", lambda found: len(by_kind(found, "done")) == 2 and all_ended(found), 45)
    hold_periods = [one.get("period") for one in by_kind(h.events("hold"), "task")]
    if (hold_started.returncode == 0 and all(call.returncode == 0 for call in (hold_posed, hold_first, hold_later, hold_next))
            and hold_open and hold_skipped == [("2026-10-05T11:00", "T1")] and hold_tasks == ["T1"] and hold_done
            and hold_two and hold_periods == ["2026-10-05T10:00", "2026-10-05T12:00"]):
        held("(h) a slot of a duration held", "11:01 recurrence-skipped {2026-10-05T11:00, open T1}, nothing opened; "
             "T1 resolved; 12:01 the 12:00 slot")
    else:
        failures.append(f"  ✗ (h) a slot of a duration held rc={[call.returncode for call in (hold_started, hold_posed, hold_first, hold_later, hold_next)]} "
                        f"open={hold_open} skipped={hold_skipped} tasks={hold_tasks} done={hold_done}/{hold_two} "
                        f"periods={hold_periods} {hold_posed.stderr.strip()[-160:]!r}")
    return 0
