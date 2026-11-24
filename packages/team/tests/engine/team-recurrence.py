"""Scenario `team-recurrence` -- 5 case(s): `team post <name> … --every "<when>"` lays a RECURRENCE on a task -- the
tick opens ONE occurrence per period, a task like any other --, `team stop <name> --recurrence R<n>` ends it, and the
faces say it. One team under a frozen clock (`PP_NOW`): Monday 2026-10-05, then Tuesday; the cases of an occurrence
held open and of the pause are `team-recurrence-held`'s.
- (a) judged before writing: `team-not-started`, `every-invalid` (`someday 09:30`, `weekday 9h`), `--every` with
  `--task` or `--reply` (the usage), `participant-unknown` -- rc 2, the journal byte-identical
- (b) the pose and the sounding: Monday 08:00 `post --to w --name revue --every "weekday 09:30"` writes `recurrence
  R1` and opens nothing; the tick of 09:31 opens ONE occurrence named `revue 2026-10-05 09:30` to w, its opening do
  -- its `task` and `do` events shaped as a posted task's, `recurrence` and `period` apart --; a tick at 10:00 opens
  nothing; Tuesday 09:31 a second occurrence; while R1 lives no `schedule-off` is written
- (e) the faces: `status --json` says `recurrences [{id, name, when, next_due, due, stopped, last}]` and
  `tasks[].recurrence` on each occurrence; `status` twice gives the same bytes; `log --json` says `recurrence`;
  after a `snapshot` the face says the same recurrences
- (f) the net: a live recurrence keeps the timer's deadline -- on Tuesday at noon `deadline_of` on that team's state is
  its next period (Wednesday 09:30) while nothing else is due, None once the recurrence is stopped
- (g) a recurrence by a duration (study § 21, row 121): `--every 30s`, `0h`, `4x`, `4` refuse `every-invalid`, the
  journal byte-identical, and a ceremony line `every 4h` still refuses `team-invalid` at `start`; Monday 10:00 `post
  --every 4h --no-tick`, then a tick at 10:00 opens ONE occurrence `veille 2026-10-05 10:00` (period
  `2026-10-05T10:00`); 13:59 nothing; 14:01 the slot of 14:00; 22:01, the slot of 18:00 missed, the slot of 22:00
  alone; `status --json` says `when {kind: interval, every: 4h, seconds: 14400}` and `next_due` Tuesday 02:00, which
  `deadline_of` follows
"""
from __future__ import annotations

import json
import os
from datetime import datetime

from tests.harness import support

T = support(__file__, "team")

MONDAY, TUESDAY, WEDNESDAY, PAIR = T.MONDAY, T.TUESDAY, T.WEDNESDAY, T.PAIR


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})
    by_kind, all_ended = T.by_kind, T.all_ended
    for name, m, w in (("rec", "m", "w"), ("never", "nm", "nw"), ("dur", "dm", "dw")):
        h.declare(name, PAIR.format(m=m, w=w))
    h.declare("cer", PAIR.format(m="cm", w="cw").replace("schedule: off\n",
                                                           "schedule: off\nceremonies: |\n  check every 4h with cw -> cm\n"))
    started = h.call("team", "start", "rec", *h.harnessed, now=MONDAY + "07:50")
    # --- (a) judged before writing -------------------------------------------------------------------------------
    before = h.journal_of("rec").read_bytes()
    refused = {
        "team-not-started": h.call("team", "post", "never", "--message", "x", "--every", "day 09:30", now=MONDAY + "07:55"),
        "every-invalid": h.call("team", "post", "rec", "--message", "x", "--every", "someday 09:30", now=MONDAY + "07:55"),
        "every-invalid ": h.call("team", "post", "rec", "--message", "x", "--every", "weekday 9h", now=MONDAY + "07:55"),
        "usage": h.call("team", "post", "rec", "--message", "x", "--task", "T1", "--every", "day 09:30",
                        now=MONDAY + "07:55"),
        "usage ": h.call("team", "post", "rec", "--message", "x", "--reply", "3", "--every", "day 09:30",
                         now=MONDAY + "07:55"),
        "participant-unknown": h.call("team", "post", "rec", "--message", "x", "--to", "zz", "--every", "day 09:30",
                                      now=MONDAY + "07:55")}
    untouched = h.journal_of("rec").read_bytes() == before
    if (started.returncode == 0 and untouched
            and all(one.returncode == 2 and code.strip() in one.stderr for code, one in refused.items())):
        held("(a) judged before writing", "team-not-started, every-invalid twice, --every with --task or --reply (the "
             "usage), participant-unknown: rc 2, the journal byte-identical")
    else:
        failures.append(f"  ✗ (a) judged before writing    started={started.returncode} "
                        f"untouched={untouched} "
                        f"{[(code, one.returncode, one.stderr.strip()[-120:]) for code, one in refused.items()]}")

    # --- the poses, then the ticks of Monday and Tuesday --------------------------------------------------------------
    posed = h.call("team", "post", "rec", "--message", "revois les PR", "--to", "w", "--name", "revue",
                   "--every", "weekday 09:30", "--no-tick", now=MONDAY + "08:00")
    plain = h.call("team", "post", "rec", "--message", "a task posted once", "--to", "w", "--name", "once", "--no-tick",
                   now=MONDAY + "08:01")
    at_pose = by_kind(h.events("rec"), "task")
    monday = h.call("team", "tick", "rec", now=MONDAY + "09:31")
    rec_first = h.settled("rec", lambda found: len(by_kind(found, "done")) == 2 and all_ended(found), 45)
    again = h.call("team", "tick", "rec", now=MONDAY + "10:00")
    monday_tasks = by_kind(h.events("rec"), "task")
    tuesday = h.call("team", "tick", "rec", now=TUESDAY + "09:31")
    rec_second = h.settled("rec", lambda found: len(by_kind(found, "done")) == 3 and all_ended(found), 45)

    # --- (b) the pose and the sounding ------------------------------------------------------------------------------
    found = h.events("rec")
    posed_event = next(iter(by_kind(found, "recurrence")), {})
    occurrences = [one for one in by_kind(found, "task") if one.get("recurrence")]
    once = next((one for one in by_kind(found, "task") if one.get("name") == "once"), {})
    first = occurrences[0] if occurrences else {}
    do_of = lambda task: next((one for one in by_kind(found, "post", verb="do") if one.get("task") == task), {})
    same_task = set(first) - {"recurrence", "period"} == set(once) and {key: first.get(key) for key in ("from", "to")} \
        == {key: once.get(key) for key in ("from", "to")}
    same_do = set(do_of(first.get("task"))) == set(do_of(once.get("task"))) and bool(do_of(first.get("task")))
    if (posed.returncode == 0 and plain.returncode == 0 and monday.returncode == 0 and tuesday.returncode == 0
            and posed_event.get("recurrence") == "R1"
            and posed_event.get("to") == "w" and posed_event.get("when") == {"kind": "weekday", "at": "09:30"}
            and [one.get("name") for one in at_pose] == ["once"] and rec_first and again.returncode == 0
            and [one.get("name") for one in monday_tasks if one.get("recurrence")] == ["revue 2026-10-05 09:30"]
            and rec_second and [(one.get("name"), one.get("period"), one.get("to")) for one in occurrences]
            == [("revue 2026-10-05 09:30", "2026-10-05", "w"), ("revue 2026-10-06 09:30", "2026-10-06", "w")]
            and same_task and same_do and not by_kind(found, "schedule-off")):
        held("(b) the pose and the sounding", f"R1 posed, nothing open; 09:31 {first.get('task')} `{first.get('name')}` "
             "to w with its do, shaped as a posted task's; 10:00 nothing; Tuesday a second; no schedule-off")
    else:
        failures.append(f"  ✗ (b) the pose and the sounding  rc={posed.returncode}/{plain.returncode}/{again.returncode} "
                        f"posed={posed_event} at_pose={[one.get('name') for one in at_pose]} first={rec_first} "
                        f"second={rec_second} occurrences={[(one.get('name'), one.get('period')) for one in occurrences]} "
                        f"same={same_task}/{same_do} off={bool(by_kind(found, 'schedule-off'))} "
                        f"{posed.stderr.strip()[-200:]!r}")

    # --- (e) the faces ---------------------------------------------------------------------------------------------
    face = h.face("rec", now=TUESDAY + "12:00")
    said = [h.call("team", "status", "rec", now=TUESDAY + "12:00").stdout for _ in range(2)]
    logged = [json.loads(line) for line in h.call("team", "log", "rec", "--json", now=TUESDAY + "12:00").stdout
              .splitlines() if line.strip()]
    snap = h.call("team", "snapshot", "rec", now=TUESDAY + "12:01")
    after = h.face("rec", now=TUESDAY + "12:00")
    recurrences = face.get("recurrences") or [{}]
    one = recurrences[0]
    marks = {task.get("id"): task.get("recurrence") for task in face.get("tasks") or []}
    if (one.get("id") == "R1" and one.get("name") == "revue" and one.get("to") == "w"
            and one.get("when") == {"kind": "weekday", "at": "09:30"} and one.get("next_due") == "2026-10-07T09:30"
            and one.get("due") is False and one.get("stopped") is None
            and (one.get("last") or {}).get("period") == "2026-10-06" and (one.get("last") or {}).get("state") == "resolved"
            and sorted(task for task, mark in marks.items() if mark == "R1") == [one_["task"] for one_ in occurrences]
            and all(mark is None for task, mark in marks.items() if task == once.get("task"))
            and said[0] == said[1] and "R1" in said[0]
            and [entry.get("recurrence") for entry in logged if entry.get("event") == "recurrence"] == ["R1"]
            and snap.returncode == 0 and after.get("recurrences") == face.get("recurrences")):
        held("(e) the faces", f"recurrences[0] R1 next_due {one.get('next_due')}, last {one.get('last')}; "
             "tasks[].recurrence on each occurrence; status twice the same bytes; log --json; kept by a snapshot")
    else:
        failures.append(f"  ✗ (e) the faces               recurrences={face.get('recurrences')} marks={marks} "
                        f"same={said[0] == said[1]} logged={[entry.get('event') for entry in logged][-6:]} "
                        f"snap={snap.returncode} after={after.get('recurrences')}")

    # --- (f) the net: the timer's deadline --------------------------------------------------------------------------
    module = h.module()
    os.environ[module.NOW] = TUESDAY + "12:00"
    clock = datetime.fromisoformat(TUESDAY + "12:00")
    try:
        live = module.deadline_of(module.state_of(h.journal_of("rec")), clock, 300)
        halt = h.call("team", "stop", "rec", "--recurrence", "R1", "--no-tick", now=TUESDAY + "12:05")
        gone = module.deadline_of(module.state_of(h.journal_of("rec")), clock, 300)
        netless = module.netless(module.state_of(h.journal_of("rec")))
    finally:
        os.environ.pop(module.NOW, None)
    if live == datetime.fromisoformat(WEDNESDAY + "09:30") and halt.returncode == 0 and gone is None and netless:
        held("(f) the net", f"a live recurrence: the deadline {live:%a %H:%M}; stopped: none, and nothing open: "
             "netless")
    else:
        failures.append(f"  ✗ (f) the net                 live={live} gone={gone} netless={netless} "
                        f"rc={halt.returncode} {halt.stderr.strip()[-160:]!r}")

    # --- (g) a recurrence by a duration ------------------------------------------------------------------------------
    dur_started = h.call("team", "start", "dur", *h.harnessed, now=MONDAY + "07:50")
    before = h.journal_of("dur").read_bytes()
    every = lambda value: h.call("team", "post", "dur", "--message", "x", "--to", "dw", "--every", value,
                                 now=MONDAY + "09:55")
    refused = [every(value) for value in ("30s", "0h", "4x", "4")]
    ceremony = h.call("team", "start", "cer", *h.harnessed, now=MONDAY + "09:55")
    untouched = h.journal_of("dur").read_bytes() == before
    posed = h.call("team", "post", "dur", "--message", "veille les prix", "--to", "dw", "--name", "veille",
                   "--every", "4h", "--no-tick", now=MONDAY + "10:00")
    first = h.call("team", "tick", "dur", now=MONDAY + "10:00")
    one = h.settled("dur", lambda found: len(by_kind(found, "done")) == 1 and all_ended(found), 45)
    early = h.call("team", "tick", "dur", now=MONDAY + "13:59")
    after_early = [one_.get("period") for one_ in by_kind(h.events("dur"), "task")]
    second = h.call("team", "tick", "dur", now=MONDAY + "14:01")
    two = h.settled("dur", lambda found: len(by_kind(found, "done")) == 2 and all_ended(found), 45)
    late = h.call("team", "tick", "dur", now=MONDAY + "22:01")
    three = h.settled("dur", lambda found: len(by_kind(found, "done")) == 3 and all_ended(found), 45)
    face = h.face("dur", now=MONDAY + "22:30")
    r1 = (face.get("recurrences") or [{}])[0]
    os.environ[module.NOW] = MONDAY + "22:30"
    try:
        deadline = module.deadline_of(module.state_of(h.journal_of("dur")), datetime.fromisoformat(MONDAY + "22:30"),
                                      6 * 3600)
    finally:
        os.environ.pop(module.NOW, None)
    occurrences = [(one_.get("name"), one_.get("period")) for one_ in by_kind(h.events("dur"), "task")]
    if (dur_started.returncode == 0 and untouched
            and all(call.returncode == 2 and "every-invalid" in call.stderr for call in refused)
            and ceremony.returncode == 2 and "team-invalid" in ceremony.stderr
            and all(call.returncode == 0 for call in (posed, first, early, second, late)) and one and two and three
            and after_early == ["2026-10-05T10:00"]
            and occurrences == [("veille 2026-10-05 10:00", "2026-10-05T10:00"),
                                ("veille 2026-10-05 14:00", "2026-10-05T14:00"),
                                ("veille 2026-10-05 22:00", "2026-10-05T22:00")]
            and r1.get("when") == {"kind": "interval", "every": "4h", "seconds": 14400}
            and r1.get("next_due") == TUESDAY + "02:00" and deadline == datetime.fromisoformat(TUESDAY + "02:00")):
        held("(g) a recurrence by a duration", "30s, 0h, 4x, 4 every-invalid, a ceremony every 4h team-invalid; 10:00 "
             "its first slot at the pose, 13:59 nothing, 14:01 the 14:00 slot, 22:01 the 22:00 slot alone (18:00 missed); "
             f"when {r1.get('when')}, next_due {r1.get('next_due')}, the deadline {deadline:%a %H:%M}")
    else:
        failures.append(f"  ✗ (g) a recurrence by a duration rc={[call.returncode for call in (dur_started, posed, first, early, second, late)]} "
                        f"untouched={untouched} refused={[(call.returncode, call.stderr.strip()[-80:]) for call in refused]} "
                        f"ceremony={ceremony.returncode} {ceremony.stderr.strip()[-80:]!r} settled={one}/{two}/{three} "
                        f"early={after_early} occurrences={occurrences} r1={r1} deadline={deadline} "
                        f"{posed.stderr.strip()[-160:]!r}")
    return 0
