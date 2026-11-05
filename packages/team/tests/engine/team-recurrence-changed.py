"""Scenario `team-recurrence-changed` -- 2 case(s): `team recurrence <name> R<n> --every "<when>"` CHANGES the hour of a
live recurrence -- one `recurrence-changed` event, its periods kept: a period is its date, counted once. One team under
a frozen clock (`PP_NOW`): Monday 2026-10-05, then Tuesday; the pose, the sounding and the faces are
`team-recurrence`'s, an occurrence held open and the pause `team-recurrence-held`'s.
- (h) the hour changed: Monday 08:00 `post --to w --every "weekday 09:30"`, the tick of 09:31 opens Monday's occurrence;
  at 10:00 `team-unknown`, `team-not-started`, `recurrence-unknown` (R9), `recurrence-stopped` (R2, stopped),
  `every-invalid` (`someday 14:00`), `recurrence-unchanged` (the when in force), the usage (no `--every`, a `--to`) --
  rc 2, the journal byte-identical; then `team recurrence rec R1 --every "weekday 14:00"` writes ONE
  `recurrence-changed {recurrence, when, since, by}`; `status --json` says the when 14:00, the since of the change and
  `next_due` Tuesday 14:00, `log --json` the event, `deadline_of` at Monday 15:00 Tuesday 14:00; the ticks of Monday
  14:01 (the date counted) and Tuesday 09:31 (the old hour) open nothing, Tuesday 14:01 opens Tuesday's occurrence
- (i) a change beside the ticks: Monday 09:31 one `team recurrence race R1 --every "weekday 09:00"` and three `team tick
  race` at the same instant: ONE `recurrence-changed`, at most one occurrence of 2026-10-05 -- the period judged again
  under the journal's lock, the ids one apart
"""
from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from tests.harness import support

T = support(__file__, "team")

MONDAY, TUESDAY, PAIR = T.MONDAY, T.TUESDAY, T.PAIR


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})
    by_kind, all_ended = T.by_kind, T.all_ended
    for name, m, w in (("rec", "m", "w"), ("never", "nm", "nw"), ("race", "rm", "rw")):
        h.declare(name, PAIR.format(m=m, w=w))
    started = h.call("team", "start", "rec", *h.harnessed, now=MONDAY + "07:50")
    race_started = h.call("team", "start", "race", *h.harnessed, now=MONDAY + "07:50")
    race_posed = h.call("team", "post", "race", "--message", "x", "--to", "rw", "--every", "weekday 09:30", "--no-tick",
                        now=MONDAY + "08:00")
    posed = h.call("team", "post", "rec", "--message", "revois les PR", "--to", "w", "--name", "revue",
                   "--every", "weekday 09:30", "--no-tick", now=MONDAY + "08:00")
    other = h.call("team", "post", "rec", "--message", "x", "--to", "w", "--every", "day 12:00", "--no-tick",
                   now=MONDAY + "08:01")
    halted = h.call("team", "stop", "rec", "--recurrence", "R2", "--no-tick", now=MONDAY + "08:02")
    monday = h.call("team", "tick", "rec", now=MONDAY + "09:31")
    first = h.settled("rec", lambda found: len(by_kind(found, "done")) == 1 and all_ended(found), 45)

    # --- judged before writing ----------------------------------------------------------------------------------
    before = h.journal_of("rec").read_bytes()
    change = lambda team, *rest: h.call("team", "recurrence", team, *rest, now=MONDAY + "10:00")
    refused = {
        "team-unknown": change("nobody", "R1", "--every", "weekday 14:00"),
        "team-not-started": change("never", "R1", "--every", "weekday 14:00"),
        "recurrence-unknown": change("rec", "R9", "--every", "weekday 14:00"),
        "recurrence-stopped": change("rec", "R2", "--every", "weekday 14:00"),
        "every-invalid": change("rec", "R1", "--every", "someday 14:00"),
        "recurrence-unchanged": change("rec", "R1", "--every", "weekday 09:30"),
        "usage": change("rec", "R1"),
        "usage ": change("rec", "R1", "--every", "weekday 14:00", "--to", "m")}
    untouched = h.journal_of("rec").read_bytes() == before
    usage = refused["usage"].stderr.strip()

    # --- the change, the faces, the ticks -----------------------------------------------------------------------
    changed = change("rec", "R1", "--every", "weekday 14:00", "--no-tick")
    face = h.face("rec", now=MONDAY + "15:00")
    logged = [json.loads(line) for line in h.call("team", "log", "rec", "--json", now=MONDAY + "15:00").stdout
              .splitlines() if line.strip()]
    module = h.module()
    os.environ[module.NOW] = MONDAY + "15:00"
    try:
        deadline = module.deadline_of(module.state_of(h.journal_of("rec")), datetime.fromisoformat(MONDAY + "15:00"),
                                      300)
    finally:
        os.environ.pop(module.NOW, None)
    late = h.call("team", "tick", "rec", now=MONDAY + "14:01")
    old_hour = h.call("team", "tick", "rec", now=TUESDAY + "09:31")
    quiet = [one.get("period") for one in by_kind(h.events("rec"), "task")]
    tuesday = h.call("team", "tick", "rec", now=TUESDAY + "14:01")
    second = h.settled("rec", lambda found: len(by_kind(found, "done")) == 2 and all_ended(found), 45)
    found = h.events("rec")
    events = by_kind(found, "recurrence-changed")
    event = events[0] if events else {}
    one = next((entry for entry in face.get("recurrences") or [] if entry.get("id") == "R1"), {})
    occurrences = [(task.get("name"), task.get("period")) for task in by_kind(found, "task")]
    if (all(call.returncode == 0 for call in (started, posed, other, halted, monday, changed, late, old_hour, tuesday))
            and first and untouched
            and all(call.returncode == 2 and code.strip() in call.stderr for code, call in refused.items()
                    if not code.startswith("usage"))
            and refused["usage "].returncode == 2 and refused["usage "].stderr.strip() == usage and usage
            and len(events) == 1 and event.get("recurrence") == "R1"
            and event.get("when") == {"kind": "weekday", "at": "14:00"}
            and event.get("since") == MONDAY + "10:00:00" and event.get("by")
            and one.get("when") == {"kind": "weekday", "at": "14:00"} and one.get("since") == MONDAY + "10:00:00"
            and one.get("next_due") == TUESDAY + "14:00" and one.get("stopped") is None
            and [entry.get("recurrence") for entry in logged if entry.get("event") == "recurrence-changed"] == ["R1"]
            and deadline == datetime.fromisoformat(TUESDAY + "14:00")
            and quiet == ["2026-10-05"] and second
            and occurrences == [("revue 2026-10-05 09:30", "2026-10-05"), ("revue 2026-10-06 14:00", "2026-10-06")]):
        held("(h) the hour changed", "eight refusals, the journal byte-identical; one recurrence-changed R1 14:00; the "
             f"face next_due {one.get('next_due')}, the deadline {deadline:%a %H:%M}; Monday 14:01 and Tuesday 09:31 "
             "nothing; Tuesday 14:01 its occurrence")
    else:
        failures.append(f"  ✗ (h) the hour changed         rc={[call.returncode for call in (started, posed, other, halted, monday, changed, late, old_hour, tuesday)]} "
                        f"first={first} untouched={untouched} "
                        f"refused={[(code, call.returncode, call.stderr.strip()[-90:]) for code, call in refused.items()]} "
                        f"events={events} face={one} deadline={deadline} quiet={quiet} second={second} "
                        f"occurrences={occurrences} {changed.stderr.strip()[-200:]!r}")

    # --- (i) a change beside the ticks ------------------------------------------------------------------------------
    plays = [("recurrence", "race", "R1", "--every", "weekday 09:00", "--no-tick")] + [("tick", "race")] * 3
    with ThreadPoolExecutor(4) as pool:
        raced = list(pool.map(lambda args: h.call("team", *args, now=MONDAY + "09:31"), plays))
    race_done = h.settled("race", lambda found: all_ended(found), 45)
    found = h.events("race")
    ids = [int(one.get("id") or 0) for one in found]
    monday_occurrences = [one for one in by_kind(found, "task") if one.get("period") == "2026-10-05"]
    if (race_started.returncode == 0 and race_posed.returncode == 0 and all(call.returncode == 0 for call in raced)
            and race_done and len(by_kind(found, "recurrence-changed")) == 1 and len(monday_occurrences) <= 1
            and ids == list(range(1, len(ids) + 1))):
        held("(i) a change beside the ticks", f"one recurrence-changed, {len(monday_occurrences)} occurrence of "
             "2026-10-05, the journal's ids one apart")
    else:
        failures.append(f"  ✗ (i) a change beside the ticks rc={[call.returncode for call in raced]} done={race_done} "
                        f"changed={by_kind(found, 'recurrence-changed')} monday={monday_occurrences} ids={ids} "
                        f"{raced[0].stderr.strip()[-200:]!r}")
    return 0
