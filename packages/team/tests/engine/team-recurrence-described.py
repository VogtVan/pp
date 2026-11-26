"""Scenario `team-recurrence-described` -- 5 case(s): a RECURRENCE carries its DESCRIPTION -- one sentence of what it
does, beside its short `--name` -- laid by `team post … --every … --description <text>` or by `team recurrence --task
T<n> --every … --description <text>`, said at `status --json`. One team under a frozen clock (`PP_NOW`), Monday
2026-10-05, nothing woken; the pose, the sounding and the faces are `team-recurrence`'s, the change of a description
`team-recurrence-changed`'s.
- (a) a recurrence described: `--description` of 201 characters or of two lines refuses `description-invalid`,
  `--description` without `--every` the usage, the journal byte-identical; `post --every … --description <text>`
  writes it in the `recurrence` event, `team recurrence --task T<n> --every … --description <text>` in its own, a
  recurrence posted without it says nothing in its event; `status --json` says `recurrences[].description`, `null`
  for the one without
The faces, the changes and the net of a recurrence that no wake-up plays, beside it -- nothing woken either:
- (b) the faces off the period: `weekday 09:30` (R1) and `4h` (R2) posted Monday -- `status --json` Monday 10:30 says R2
  `next_due` 10:00 itself and `due` true, its slot under way owing; Saturday R1 `due` false and `next_due` Monday
  2026-10-12T09:30; at a clock set back before the pose by more than a week, R1's `next_due` null
- (c) a duration said otherwise: R2 under `4h`, `--every 240m` refuses `recurrence-unchanged` -- the same seconds --,
  the journal byte-identical
- (d) off season: R1 paused, the season stopped -- `team recurrence R1 --now` refuses `season-stopped`, the journal
  byte-identical; `--message <new>` without `--no-tick` writes `recurrence-changed {text}` and its tick opens nothing;
  `team resume --recurrence R1` writes `recurrence-resumed` and opens nothing; on a team whose journal says a delete
  begun, `team resume --recurrence` refuses `team-deleting`, the journal byte-identical
- (e) the net of a paused recurrence: a team under `schedule: 5m`, nothing open, its one recurrence paused -- `team
  tick` at its hour opens nothing and arms no timer (no `timer-armed`, the face's `schedule.timer` false)
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")

MONDAY, PAIR = T.MONDAY, T.PAIR
SATURDAY = "2026-10-10T"
LATER = "2027-01-04T"                                  # a Monday ahead of the wall's clock: a timer armed would sleep
AT = "2026-11-03T21:00:00+00:00"
GONE = [{"kind": "team-started", "agents": {"ga": "agents/ga"}, "reports": [], "root": "ga", "principals": [],
         "owner": "house", "ceremonies": [], "launch": {}, "limits": {}, "schedule": None, "digest": "000000000000"},
        {"kind": "recurrence", "recurrence": "R1", "from": "house", "to": "ga", "text": "x",
         "when": {"kind": "weekday", "at": "09:30"}, "since": "2026-10-05T08:00:00", "context": None},
        {"kind": "recurrence-paused", "recurrence": "R1", "by": "house"},
        {"kind": "deleting", "by": "house"}]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})
    by_kind = T.by_kind
    # --- (a) a recurrence described -------------------------------------------------------------------------------
    h.declare("desc", PAIR.format(m="em", w="ew"))
    begun = h.call("team", "start", "desc", "--message", "go", "--no-tick", now=MONDAY + "07:50")
    described = "Reviews the open PRs every morning."
    post = lambda *rest: h.call("team", "post", "desc", "--message", "x", "--to", "ew", *rest, "--no-tick",
                                now=MONDAY + "08:00")
    before = h.journal_of("desc").read_bytes()
    refused = {"description-invalid": post("--every", "day 09:30", "--description", "x" * 201),
               "description-invalid ": post("--every", "day 09:30", "--description", "one line\nand another"),
               "usage": post("--description", described)}
    untouched = h.journal_of("desc").read_bytes() == before
    with_it = post("--every", "day 09:30", "--description", described)
    without = post("--every", "day 10:30")
    task = post("--name", "once")
    born = h.call("team", "recurrence", "desc", "--task", "T1", "--every", "day 12:00", "--description", "Its own.",
                  "--no-tick", now=MONDAY + "08:01")
    poses = {one.get("recurrence"): one for one in by_kind(h.events("desc"), "recurrence")}
    faced = {one.get("id"): one for one in h.face("desc", now=MONDAY + "08:02").get("recurrences") or []}
    if (begun.returncode == 0 and untouched
            and all(call.returncode == 2 and code.strip() in call.stderr for code, call in refused.items()
                    if code != "usage")
            and refused["usage"].returncode == 2 and "usage" in refused["usage"].stderr
            and all(call.returncode == 0 for call in (with_it, without, task, born))
            and (poses.get("R1") or {}).get("description") == described and "description" not in (poses.get("R2") or {"description": 0})
            and (poses.get("R3") or {}).get("description") == "Its own." and (poses.get("R3") or {}).get("task") == "T1"
            and [(faced.get(one) or {}).get("description", "?") for one in ("R1", "R2", "R3")] == [described, None, "Its own."]):
        held("(a) a recurrence described", "201 characters and two lines description-invalid, without --every the usage, "
             "the journal byte-identical; the post and the --task pose carry it in their event, the one without "
             "nothing; status --json says it, null without")
    else:
        failures.append(f"  ✗ (a) a recurrence described   rc={[call.returncode for call in (begun, with_it, without, task, born)]} "
                        f"untouched={untouched} refused={[(code, call.returncode, call.stderr.strip()[-90:]) for code, call in refused.items()]} "
                        f"poses={poses} faced={[(one, (faced.get(one) or {}).get('description', '?')) for one in ('R1', 'R2', 'R3')]} "
                        f"{(with_it.stderr or born.stderr).strip()[-160:]!r}")
    # --- (b) the faces off the period -----------------------------------------------------------------------------
    h.declare("wk", PAIR.format(m="km", w="kw"))
    wk = h.journal_of("wk")
    wk_calls = [h.call("team", "start", "wk", "--no-tick", now=MONDAY + "07:50"),
                h.call("team", "post", "wk", "--message", "weekly check", "--to", "kw", "--every", "weekday 09:30",
                       "--no-tick", now=MONDAY + "08:00"),
                h.call("team", "post", "wk", "--message", "watch the prices", "--to", "kw", "--every", "4h",
                       "--no-tick", now=MONDAY + "10:00")]
    of = lambda face, key: next((one for one in face.get("recurrences") or [] if one.get("id") == key), {})
    owing = of(h.face("wk", now=MONDAY + "10:30"), "R2")
    weekend = of(h.face("wk", now=SATURDAY + "10:00"), "R1")
    before_pose = of(h.face("wk", now="2026-09-20T10:00"), "R1")
    if (all(call.returncode == 0 for call in wk_calls) and owing.get("next_due") == MONDAY + "10:00"
            and owing.get("due") is True and weekend.get("due") is False and weekend.get("next_due") == "2026-10-12T09:30"
            and before_pose.get("id") == "R1" and before_pose.get("next_due") is None and before_pose.get("due") is False):
        held("(b) the faces off the period", f"R2 at 10:30, its slot owing: next_due {owing.get('next_due')}, due; "
             f"Saturday R1 due false, next_due {weekend.get('next_due')}; a clock set back before the pose: next_due null")
    else:
        failures.append(f"  ✗ (b) the faces off the period rc={[call.returncode for call in wk_calls]} owing={owing} "
                        f"weekend={weekend} before={before_pose} "
                        f"{next((call.stderr.strip()[-200:] for call in wk_calls if call.returncode), '')!r}")

    # --- (c) a duration said otherwise ------------------------------------------------------------------------------
    c_before = wk.read_bytes()
    same_form = h.call("team", "recurrence", "wk", "R2", "--every", "240m", "--no-tick", now=MONDAY + "10:40")
    if same_form.returncode == 2 and T.refusal_code(same_form.stderr) == "recurrence-unchanged" and wk.read_bytes() == c_before:
        held("(c) a duration said otherwise", "R2 under 4h: --every 240m refuses recurrence-unchanged, the journal "
             "byte-identical")
    else:
        failures.append(f"  ✗ (c) a duration said otherwise rc={same_form.returncode} "
                        f"code={T.refusal_code(same_form.stderr)!r} {same_form.stderr.strip()[-160:]!r}")

    # --- (d) off season ---------------------------------------------------------------------------------------------
    off_calls = [h.call("team", "pause", "wk", "--recurrence", "R1", now=MONDAY + "10:50"),
                 h.call("team", "stop", "wk", "--no-tick", now=MONDAY + "10:51")]
    d_before = wk.read_bytes()
    now_refused = h.call("team", "recurrence", "wk", "R1", "--now", "--no-tick", now=MONDAY + "10:52")
    d_same = wk.read_bytes() == d_before
    tasks_before = len(by_kind(h.events("wk"), "task"))
    off_calls += [h.call("team", "recurrence", "wk", "R1", "--message", "check the week", now=MONDAY + "10:53"),
                  h.call("team", "resume", "wk", "--recurrence", "R1", now=MONDAY + "10:54")]
    found = h.events("wk")
    h.declare("gone", PAIR.format(m="ga", w="gw"))
    h.written("gone", GONE, AT)
    gone_before = h.journal_of("gone").read_bytes()
    gone_refused = h.call("team", "resume", "gone", "--recurrence", "R1")
    gone_same = h.journal_of("gone").read_bytes() == gone_before
    changed = by_kind(found, "recurrence-changed")[-1:] or [{}]
    if (all(call.returncode == 0 for call in off_calls) and now_refused.returncode == 2
            and T.refusal_code(now_refused.stderr) == "season-stopped" and d_same
            and changed[0].get("text") == "check the week" and found[-1].get("kind") == "recurrence-resumed"
            and found[-1].get("recurrence") == "R1" and len(by_kind(found, "task")) == tasks_before
            and gone_refused.returncode == 2 and T.refusal_code(gone_refused.stderr) == "team-deleting" and gone_same):
        held("(d) off season", "R1 paused, the season stopped: --now refuses season-stopped, same bytes; the text "
             "changed with its tick, R1 resumed, nothing opened; a delete begun: resume --recurrence team-deleting")
    else:
        failures.append(f"  ✗ (d) off season              rc={[call.returncode for call in off_calls]} "
                        f"now={now_refused.returncode}/{T.refusal_code(now_refused.stderr)!r} same={d_same} "
                        f"changed={changed[0]} last={found[-1:]} tasks={tasks_before}/{len(by_kind(found, 'task'))} "
                        f"gone={gone_refused.returncode}/{T.refusal_code(gone_refused.stderr)!r}/{gone_same} "
                        f"{next((call.stderr.strip()[-200:] for call in off_calls if call.returncode), '')!r}")

    # --- (e) the net of a paused recurrence -------------------------------------------------------------------------
    h.declare("hush", "---\nagents: |\n  hm agents/hm\nroot: hm\nschedule: 5m\n---\nWater the plants.\n")
    hush_calls = [h.call("team", "start", "hush", "--no-tick", now=LATER + "08:00"),
                  h.call("team", "post", "hush", "--message", "water the plants", "--to", "hm", "--every",
                         "weekday 09:30", "--no-tick", now=LATER + "08:01"),
                  h.call("team", "pause", "hush", "--recurrence", "R1", now=LATER + "08:02"),
                  h.call("team", "tick", "hush", now=LATER + "09:31")]
    hush_found = h.events("hush")
    hush_face = h.face("hush", now=LATER + "09:32")
    h.off_season("hush", now=LATER + "09:33")
    if (all(call.returncode == 0 for call in hush_calls) and not by_kind(hush_found, "task")
            and not by_kind(hush_found, "timer-armed") and (hush_face.get("schedule") or {}).get("seconds") == 300
            and (hush_face.get("schedule") or {}).get("timer") is False):
        held("(e) the net of a paused recurrence", f"schedule 5m, R1 paused: the tick of 09:31 opens nothing, no timer "
             f"armed ({hush_face.get('schedule')})")
    else:
        failures.append(f"  ✗ (e) the net of a paused recurrence rc={[call.returncode for call in hush_calls]} "
                        f"found={[(one['id'], one['kind']) for one in hush_found]} schedule={hush_face.get('schedule')} "
                        f"{next((call.stderr.strip()[-200:] for call in hush_calls if call.returncode), '')!r}")
    return 0
