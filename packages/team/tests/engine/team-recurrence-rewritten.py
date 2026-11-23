"""Scenario `team-recurrence-rewritten` -- 2 case(s): `team recurrence <name> R<n> --message <text>` REWRITES the text of a
live recurrence, and `team recurrence <name> --task T<n> --every "<when>"` lays a recurrence on a task that exists, the
task its last occurrence (study § 21, row 122). Two teams in one house under a frozen clock (`PP_NOW`): Monday
2026-10-05, then Tuesday; the hour, the limit and the form changed are `team-recurrence-changed`'s.
- (l) the text changed: Monday 08:00 `post --to tw --every "weekday 09:30"` with a text, Monday's occurrence opened at
  09:31; at 10:00 `--message ""` refuses `message-missing`, the journal byte-identical; `--message <new>` writes ONE
  `recurrence-changed {recurrence, text, by}` without `when` nor `since`, the same text again `recurrence-unchanged`;
  `status --json` says the new text; Tuesday's occurrence opens with it (its `task` and its `do`), Monday's keeps its own
- (m) a task made recurrent: T1 posted once to ow, held open behind a gate; at 08:05 `--task T9` (`task-unknown`),
  `R1 --task T1`, `--task T1` without `--every`, `--task T1 --message x` (the usage) and `--every someday` (`every-invalid`)
  refuse, the journal byte-identical; `--task T1 --every 1h` writes `recurrence {R1, task: T1, from, to, text, name}` --
  T1's member, text and name; the tick of 08:06 writes `recurrence-skipped {open: T1}`; T1 resolved, the tick of 09:06
  opens `veille 2026-10-05 09:05` with T1's text, its wake-up opening a NEW run; `status --json` says
  `recurrences[].task` T1, `log --json` the recurrence with its task; `--task` on that occurrence refuses `task-recurrent`
"""
from __future__ import annotations

import json

from tests.harness import support

T = support(__file__, "team")

MONDAY, TUESDAY, PAIR = T.MONDAY, T.TUESDAY, T.PAIR


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})
    by_kind, all_ended = T.by_kind, T.all_ended
    for name, m, w in (("text", "tm", "tw"), ("orig", "om", "ow")):
        h.declare(name, PAIR.format(m=m, w=w))
    gate = bench.temp() / "orig-gate"                    # ow's T1 held open until the gate stands
    started = h.call("team", "start", "text", *h.harnessed, now=MONDAY + "07:50")
    orig_started = h.call("team", "start", "orig", *T.gated(h, gate, ("ow",)), now=MONDAY + "07:50")
    posed = h.call("team", "post", "text", "--message", "revois les PR", "--to", "tw", "--every", "weekday 09:30",
                   "--no-tick", now=MONDAY + "08:00")
    once = h.call("team", "post", "orig", "--message", "watch the prices", "--to", "ow", "--name", "veille",
                  now=MONDAY + "08:00")
    monday = h.call("team", "tick", "text", now=MONDAY + "09:31")
    held_open = h.settled("orig", lambda found: bool(by_kind(found, "wake-launched", agent="ow")), 30)

    # --- (m) judged before writing, then the pose on T1 still open --------------------------------------------------
    before = h.journal_of("orig").read_bytes()
    made = lambda *rest: h.call("team", "recurrence", "orig", *rest, now=MONDAY + "08:05")
    refused = {"task-unknown": made("--task", "T9", "--every", "1h"),
               "every-invalid": made("--task", "T1", "--every", "someday"),
               "usage": made("R1", "--task", "T1", "--every", "1h"),
               "usage ": made("--task", "T1"),
               "usage  ": made("--task", "T1", "--every", "1h", "--message", "x")}
    orig_untouched = h.journal_of("orig").read_bytes() == before
    laid = made("--task", "T1", "--every", "1h", "--no-tick")
    skip_tick = h.call("team", "tick", "orig", now=MONDAY + "08:06")
    skipped = [(one.get("recurrence"), one.get("open")) for one in by_kind(h.events("orig"), "recurrence-skipped")]
    gate.write_text("open", encoding="utf-8")
    origin_done = h.settled("orig", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 45)
    sounded = h.call("team", "tick", "orig", now=MONDAY + "09:06")
    second = h.settled("orig", lambda found: bool(by_kind(found, "done", task="T2")) and all_ended(found), 45)

    # --- (l) the text changed ---------------------------------------------------------------------------------------
    first = h.settled("text", lambda found: len(by_kind(found, "done")) == 1 and all_ended(found), 45)
    before = h.journal_of("text").read_bytes()
    empty = h.call("team", "recurrence", "text", "R1", "--message", "", now=MONDAY + "10:00")
    untouched = h.journal_of("text").read_bytes() == before
    rewritten = h.call("team", "recurrence", "text", "R1", "--message", "revois les PR et les issues", "--no-tick",
                       now=MONDAY + "10:00")
    again = h.call("team", "recurrence", "text", "R1", "--message", "revois les PR et les issues", now=MONDAY + "10:01")
    face = (h.face("text", now=MONDAY + "10:02").get("recurrences") or [{}])[0]
    tuesday = h.call("team", "tick", "text", now=TUESDAY + "09:31")
    later = h.settled("text", lambda found: len(by_kind(found, "done")) == 2 and all_ended(found), 45)
    found = h.events("text")
    changes = by_kind(found, "recurrence-changed")
    opened = [(one.get("period"), one.get("text")) for one in by_kind(found, "task")]
    dos = [one.get("text") for one in by_kind(found, "post", verb="do")]
    if (all(call.returncode == 0 for call in (started, posed, monday, rewritten, tuesday)) and first and later
            and empty.returncode == 2 and "message-missing" in empty.stderr and untouched
            and again.returncode == 2 and "recurrence-unchanged" in again.stderr
            and len(changes) == 1 and changes[0].get("text") == "revois les PR et les issues"
            and "when" not in changes[0] and "since" not in changes[0] and changes[0].get("by")
            and face.get("text") == "revois les PR et les issues"
            and opened == [("2026-10-05", "revois les PR"), ("2026-10-06", "revois les PR et les issues")]
            and dos == ["revois les PR", "revois les PR et les issues"]):
        held("(l) the text changed", "message-missing, the journal byte-identical; one recurrence-changed {text}, "
             "recurrence-unchanged after it; Tuesday's occurrence and its do carry the new text, Monday's its own")
    else:
        failures.append(f"  ✗ (l) the text changed        rc={[call.returncode for call in (started, posed, monday, empty, rewritten, again, tuesday)]} "
                        f"first={first} later={later} untouched={untouched} changes={changes} face={face.get('text')!r} "
                        f"opened={opened} dos={dos} {rewritten.stderr.strip()[-200:]!r}")

    # --- (m) the faces and the occurrence ---------------------------------------------------------------------------
    found = h.events("orig")
    laid_event = next(iter(by_kind(found, "recurrence")), {})
    tasks = {one["task"]: one for one in by_kind(found, "task")}
    occurrence = tasks.get("T2", {})
    intents = {one.get("task"): one for one in by_kind(found, "wake-intent", agent="ow")}
    runs = {one.get("tag"): one.get("run") for one in by_kind(found, "wake-launched", agent="ow")}
    origin_run = runs.get((intents.get("T1") or {}).get("tag"))
    occurrence_run = runs.get((intents.get("T2") or {}).get("tag"))
    recurrent = h.call("team", "recurrence", "orig", "--task", "T2", "--every", "1h", now=MONDAY + "09:30")
    orig_face = (h.face("orig", now=MONDAY + "09:30").get("recurrences") or [{}])[0]
    logged = [json.loads(line) for line in h.call("team", "log", "orig", "--json", now=MONDAY + "09:30").stdout
              .splitlines() if line.strip()]
    if (orig_started.returncode == 0 and once.returncode == 0 and held_open and orig_untouched
            and all(call.returncode == 2 and code.strip() in call.stderr for code, call in refused.items()
                    if not code.startswith("usage"))
            and all(call.returncode == 2 and call.stderr.strip() == refused["usage"].stderr.strip()
                    for code, call in refused.items() if code.startswith("usage"))
            and laid.returncode == 0 and skip_tick.returncode == 0 and sounded.returncode == 0
            and {key: laid_event.get(key) for key in ("recurrence", "task", "to", "text", "name")}
            == {"recurrence": "R1", "task": "T1", "to": "ow", "text": "watch the prices", "name": "veille"}
            and laid_event.get("from") and skipped[:1] == [("R1", "T1")] and origin_done and second
            and occurrence.get("recurrence") == "R1" and occurrence.get("text") == "watch the prices"
            and occurrence.get("name") == "veille 2026-10-05 09:05"
            and (intents.get("T2") or {}).get("run") is None and occurrence_run and origin_run
            and occurrence_run != origin_run
            and recurrent.returncode == 2 and "task-recurrent" in recurrent.stderr
            and orig_face.get("task") == "T1" and orig_face.get("text") == "watch the prices"
            and [entry.get("task") for entry in logged if entry.get("event") == "recurrence"] == ["T1"]):
        held("(m) a task made recurrent", f"five refusals, the journal byte-identical; R1 laid on T1; 08:06 skipped "
             f"while T1 is open; 09:06 `{occurrence.get('name')}` with T1's text in a new run ({occurrence_run} after "
             f"{origin_run}); the face's task T1; task-recurrent on the occurrence")
    else:
        failures.append(f"  ✗ (m) a task made recurrent   rc={[orig_started.returncode, once.returncode, laid.returncode, skip_tick.returncode, sounded.returncode, recurrent.returncode]} "
                        f"open={held_open} untouched={orig_untouched} "
                        f"refused={[(code, call.returncode, call.stderr.strip()[-90:]) for code, call in refused.items()]} "
                        f"laid={laid_event} skipped={skipped} done={origin_done}/{second} occurrence={occurrence} "
                        f"runs={origin_run}/{occurrence_run} face={orig_face} {laid.stderr.strip()[-200:]!r}")
    return 0
