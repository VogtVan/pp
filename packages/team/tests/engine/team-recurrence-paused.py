"""Scenario `team-recurrence-paused` -- 2 case(s): ONE recurrence suspended and taken back (`team pause|resume <team>
--recurrence R<n>`) while its team plays on, under a frozen clock (`PP_NOW`): Monday 2026-10-05 to Thursday; the pose,
the sounding and the faces are `team-recurrence`'s, the team's own pause `team-recurrence-held`'s.
- (i) one recurrence paused: `weekday 09:30` (R1) posted Monday 08:00 beside `weekday 08:15` (R2), whose
  Monday occurrence T1 is held open behind a gate; `team pause --recurrence` R1 and R2 at 08:30 write
  `recurrence-paused` and leave T1 open; `deadline_of` is not armed on them; Tuesday and Wednesday 09:31 open nothing
  and skip nothing; `status --json` says `paused {by, at, id}`, `next_due` null, `due` false, the text the pause's id;
  `team recurrence R1 --message` passes and R1 stays paused; `team stop --recurrence R2` stops a paused one;
  `recurrence-unknown`, `recurrence-paused`, `recurrence-stopped`, the usage and, once resumed, `recurrence-live`
  refuse rc 2, the journal the same bytes; `team resume --recurrence R1` Wednesday 10:00 writes `recurrence-resumed
  {recurrence, by, since}` and opens nothing -- neither Tuesday nor Wednesday caught up --; Thursday 09:31 opens
  Thursday's occurrence with the new text; `log --json` carries both events
- (ii) one recurrence launched now: `weekday 09:30` (R1) to a gated member, `weekday 23:00` (R2), R3 stopped, posted
  Monday 08:00; `team recurrence soon R1 --now` at 08:15 opens T1 -- a `task` with `recurrence` and `now`, no `period`
  -- and its `do`; R1's `when`, `since`, `next_due`, `due`, `paused` read the same before and after; `team-unknown`,
  `team-not-started`, `recurrence-unknown`, `recurrence-stopped`, the usage (`--now` beside `--every`) and, T1 open,
  `recurrence-open` refuse rc 2, the journal the same bytes; the tick of 09:31 writes `recurrence-skipped {open: T1}`;
  R2 paused launches T2 and stays paused; T1 and T2 done, Tuesday 09:31 opens Tuesday's occurrence of R1
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta

from tests.harness import support

T = support(__file__, "team")

MONDAY, TUESDAY, WEDNESDAY, PAIR = T.MONDAY, T.TUESDAY, T.WEDNESDAY, T.PAIR
THURSDAY = "2026-10-08T"                             # the day after the week's resume


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})
    by_kind, all_ended = T.by_kind, T.all_ended
    h.declare("rest", PAIR.format(m="rm", w="rw"))

    # --- (i) one recurrence paused ----------------------------------------------------------------------------------
    rest_gate = bench.temp() / "rest-gate"               # rw's occurrence of R2 held open until its gate stands
    rest = h.journal_of("rest")
    rest_calls = [h.call("team", "start", "rest", *T.gated(h, rest_gate, ("rw",)), now=MONDAY + "07:50"),
                  h.call("team", "post", "rest", "--message", "sweep the inbox", "--to", "rm", "--every",
                         "weekday 09:30", "--no-tick", now=MONDAY + "08:00"),
                  h.call("team", "post", "rest", "--message", "carry on", "--to", "rw", "--every", "weekday 08:15",
                         "--no-tick", now=MONDAY + "08:00"),
                  h.call("team", "tick", "rest", now=MONDAY + "08:16"),
                  h.call("team", "pause", "rest", "--recurrence", "R1", now=MONDAY + "08:30"),
                  h.call("team", "pause", "rest", "--recurrence", "R2", now=MONDAY + "08:30")]
    rest_open = [one.get("state") for one in h.face("rest", now=MONDAY + "08:31").get("tasks") or []]
    module = h.module()
    clock, step = datetime.fromisoformat(MONDAY + "08:31"), 3 * 86400
    os.environ[module.NOW] = MONDAY + "08:31"
    try:
        rest_deadline = module.deadline_of(module.state_of(rest), clock, step)
    finally:
        os.environ.pop(module.NOW, None)
    rest_calls.append(h.call("team", "tick", "rest", now=TUESDAY + "09:31"))
    rest_face = h.face("rest", now=TUESDAY + "09:45")
    rest_text = h.call("team", "status", "rest", now=TUESDAY + "09:45").stdout.splitlines()
    rest_calls += [h.call("team", "recurrence", "rest", "R1", "--message", "sweep the inbox twice", "--no-tick",
                          now=TUESDAY + "10:00"),
                   h.call("team", "stop", "rest", "--recurrence", "R2", "--no-tick", now=TUESDAY + "10:05")]
    rest_kept = h.face("rest", now=TUESDAY + "10:06")
    rest_before = rest.read_bytes()
    rest_refused = {code: h.call("team", *args, now=TUESDAY + "10:10") for code, args in (
        ("recurrence-unknown", ("pause", "rest", "--recurrence", "R9")),
        ("recurrence-paused", ("pause", "rest", "--recurrence", "R1")),
        ("recurrence-stopped", ("pause", "rest", "--recurrence", "R2")),
        ("usage", ("resume", "rest", "--recurrence", "R1", "--task", "T1")))}
    rest_same = rest.read_bytes() == rest_before
    rest_calls += [h.call("team", "tick", "rest", now=WEDNESDAY + "09:31"),
                   h.call("team", "resume", "rest", "--recurrence", "R1", now=WEDNESDAY + "10:00")]
    rest_quiet = [(one.get("recurrence"), one.get("period")) for one in by_kind(h.events("rest"), "task")]
    rest_before = rest.read_bytes()
    rest_refused["recurrence-live"] = h.call("team", "resume", "rest", "--recurrence", "R1", now=WEDNESDAY + "10:05")
    rest_same = rest_same and rest.read_bytes() == rest_before
    rest_calls.append(h.call("team", "tick", "rest", now=THURSDAY + "09:31"))
    rest_logged = [json.loads(line) for line in h.call("team", "log", "rest", "--json", now=THURSDAY + "09:32").stdout
                   .splitlines() if line.strip()]
    rest_gate.write_text("open", encoding="utf-8")
    rest_done = h.settled("rest", lambda found: len(by_kind(found, "done")) == 2 and all_ended(found), 45)
    found = h.events("rest")
    paused_r1 = by_kind(found, "recurrence-paused", recurrence="R1")
    resumed_r1 = by_kind(found, "recurrence-resumed")
    pause_id = paused_r1[0].get("id") if paused_r1 else None
    face_r1 = next((one for one in rest_face.get("recurrences") or [] if one.get("id") == "R1"), {})
    kept_r1 = next((one for one in rest_kept.get("recurrences") or [] if one.get("id") == "R1"), {})
    line_r1 = next((line for line in rest_text if line.startswith("R1")), "")
    occurrences = [(one.get("recurrence"), one.get("period"), one.get("text")) for one in by_kind(found, "task")]
    if (all(call.returncode == 0 for call in rest_calls) and rest_open == ["open"]
            and [one.get("recurrence") for one in by_kind(found, "recurrence-paused")] == ["R1", "R2"]
            and not by_kind(found, "stopped") and rest_deadline in (None, clock + timedelta(seconds=step))
            and not by_kind(found, "recurrence-skipped")
            and set(face_r1.get("paused") or {}) == {"by", "at", "id"} and face_r1["paused"]["id"] == pause_id
            and face_r1.get("next_due") is None and face_r1.get("due") is False
            and f"#{pause_id}" in line_r1 and "next" not in line_r1
            and kept_r1.get("paused") == face_r1.get("paused") and kept_r1.get("text") == "sweep the inbox twice"
            and [one.get("recurrence") for one in by_kind(found, "recurrence-stopped")] == ["R2"]
            and all(call.returncode == 2 and code in call.stderr for code, call in rest_refused.items()) and rest_same
            and rest_quiet == [("R2", "2026-10-05")]
            and [(one.get("recurrence"), one.get("by"), str(one.get("since"))[:16]) for one in resumed_r1]
            == [("R1", paused_r1[0].get("by"), WEDNESDAY + "10:00")]
            and occurrences == [("R2", "2026-10-05", "carry on"), ("R1", "2026-10-08", "sweep the inbox twice")]
            and [entry.get("event") for entry in rest_logged if entry.get("event", "").startswith("recurrence-")]
            == ["recurrence-paused", "recurrence-paused", "recurrence-changed", "recurrence-stopped",
                "recurrence-resumed"] and rest_done):
        held("(i) one recurrence paused", f"paused #{pause_id}: T1 open, no deadline, Tuesday and Wednesday nothing; "
             "paused {by, at, id}, next_due null, due false; changed and still paused; refusals rc 2, same bytes; "
             "resumed Wednesday 10:00, nothing caught up; Thursday's occurrence with the new text")
    else:
        failures.append(f"  ✗ (i) one recurrence paused  rc={[call.returncode for call in rest_calls]} open={rest_open} "
                        f"deadline={rest_deadline} face={face_r1} kept={kept_r1.get('paused')} line={line_r1!r} "
                        f"refused={ {code: call.returncode for code, call in rest_refused.items()} } same={rest_same} "
                        f"quiet={rest_quiet} resumed={resumed_r1} occurrences={occurrences} done={rest_done} "
                        f"{next((call.stderr.strip()[-200:] for call in rest_calls if call.returncode), '')!r}")

    # --- (ii) one recurrence launched now ---------------------------------------------------------------------------
    h.declare("soon", PAIR.format(m="sm", w="sw"))
    h.declare("idle", PAIR.format(m="im", w="iw"))
    soon_gate = bench.temp() / "soon-gate"               # sw's launched occurrence held open until its gate stands
    soon = h.journal_of("soon")

    def planned(face: dict, key: str) -> dict:
        one = next((line for line in face.get("recurrences") or [] if line.get("id") == key), {})
        return {field: one.get(field) for field in ("when", "since", "next_due", "due", "paused", "stopped")}
    soon_calls = [h.call("team", "start", "soon", *T.gated(h, soon_gate, ("sw",)), now=MONDAY + "07:50")]
    soon_calls += [h.call("team", "post", "soon", "--message", text, "--to", to, "--every", every, "--no-tick",
                          now=MONDAY + "08:00")
                   for text, to, every in (("check the gateway", "sw", "weekday 09:30"),
                                           ("count the night", "sm", "weekday 23:00"),
                                           ("gone", "sm", "weekday 22:00"))]
    soon_calls.append(h.call("team", "stop", "soon", "--recurrence", "R3", "--no-tick", now=MONDAY + "08:01"))
    plan_before = planned(h.face("soon", now=MONDAY + "08:20"), "R1")
    soon_before = soon.read_bytes()
    soon_refused = {code: h.call("team", "recurrence", *args, now=MONDAY + "08:10") for code, args in (
        ("team-unknown", ("ghost", "R1", "--now")),
        ("team-not-started", ("idle", "R1", "--now")),
        ("recurrence-unknown", ("soon", "R9", "--now")),
        ("recurrence-stopped", ("soon", "R3", "--now")),
        ("usage", ("soon", "R1", "--now", "--every", "weekday 10:00")))}
    soon_same = soon.read_bytes() == soon_before
    launched = h.call("team", "recurrence", "soon", "R1", "--now", "--no-tick", now=MONDAY + "08:15")
    soon_face = h.face("soon", now=MONDAY + "08:20")
    plan_after = planned(soon_face, "R1")
    last_r1 = next((line.get("last") for line in soon_face.get("recurrences") or [] if line.get("id") == "R1"), None)
    soon_before = soon.read_bytes()
    soon_refused["recurrence-open"] = h.call("team", "recurrence", "soon", "R1", "--now", now=MONDAY + "08:25")
    soon_same = soon_same and soon.read_bytes() == soon_before
    soon_calls += [h.call("team", "tick", "soon", now=MONDAY + "09:31"),
                   h.call("team", "pause", "soon", "--recurrence", "R2", now=MONDAY + "09:40")]
    sleep_before = planned(h.face("soon", now=MONDAY + "09:50"), "R2")
    sleeping = h.call("team", "recurrence", "soon", "R2", "--now", "--no-tick", now=MONDAY + "09:45")
    sleep_after = planned(h.face("soon", now=MONDAY + "09:50"), "R2")
    soon_gate.write_text("open", encoding="utf-8")
    soon_calls.append(h.call("team", "tick", "soon", now=MONDAY + "10:00"))
    soon_closed = h.settled("soon", lambda found: {"T1", "T2"} <= {one.get("task") for one in by_kind(found, "done")}
                            and all_ended(found), 45)
    soon_calls.append(h.call("team", "tick", "soon", now=TUESDAY + "09:31"))
    soon_done = h.settled("soon", lambda found: len(by_kind(found, "done")) == 3 and all_ended(found), 45)
    found = h.events("soon")
    opened = [(one.get("task"), one.get("recurrence"), one.get("now"), one.get("period"), one.get("to"))
              for one in by_kind(found, "task")]
    first_do = [(one.get("to"), one.get("text")) for one in by_kind(found, "post", task="T1", verb="do")]
    skipped = [(one.get("recurrence"), one.get("period"), one.get("open")) for one in by_kind(found, "recurrence-skipped")]
    if (all(call.returncode == 0 for call in soon_calls) and launched.returncode == 0 and sleeping.returncode == 0
            and plan_before == plan_after and plan_before.get("next_due") == MONDAY + "09:30"
            and last_r1 == {"period": None, "task": "T1", "state": "open"}
            and all(call.returncode == 2 and code in call.stderr for code, call in soon_refused.items()) and soon_same
            and opened == [("T1", "R1", True, None, "sw"), ("T2", "R2", True, None, "sm"),
                           ("T3", "R1", None, "2026-10-06", "sw")]
            and all("period" not in one for one in by_kind(found, "task", task="T1"))
            and first_do == [("sw", "check the gateway")]
            and skipped == [("R1", "2026-10-05", "T1")]
            and sleep_before == sleep_after and sleep_after.get("paused") and sleep_after.get("next_due") is None
            and soon_closed and soon_done):
        held("(ii) one recurrence launched now", f"T1 now, no period; R1 planned the same {plan_after}; refusals rc 2, "
             "same bytes; Monday skipped while T1 open; R2 launched paused and still paused; Tuesday's occurrence T3")
    else:
        failures.append(f"  ✗ (ii) launched now  rc={[call.returncode for call in soon_calls]} "
                        f"launched={launched.returncode} {launched.stderr.strip()[-200:]!r} "
                        f"plans={plan_before} {plan_after} last={last_r1} "
                        f"refused={ {code: call.returncode for code, call in soon_refused.items()} } same={soon_same} "
                        f"opened={opened} do={first_do} skipped={skipped} sleep={sleep_before} {sleep_after} "
                        f"closed={soon_closed} done={soon_done}")
    return 0
