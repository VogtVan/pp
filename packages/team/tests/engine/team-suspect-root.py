"""Scenario `team-suspect-root` -- 3 case(s) (batch le-detecteur-de-fautes, team 0.35.0: row 93 of the study § 19;
`team-sim-debt.py` J4): a ROOT fallen in passing takes its task back by itself.
- (a) tried on its opening: f dies twice on T1 -- the team's notice about it to its principal, T1 open; a tick within its interval
  wakes nobody and writes nothing; `PP_NOW` past the interval, the tick tries f by a relance on its opening
  (`relance: "tried"`), f answers it and T1 resolves -- no `team resume`
- (b) an opening during the interval LAUNCHES the suspect (batch les-echecs-du-tick, team 0.41.0; KET12): g dies twice
  on T1; the owner posts T2 to g during g's interval -- g is launched at that very tick on T2, its try (no notice
  « tried again », no answer in its place), it answers 't2 done' and repents: not suspected any more, T1 still open,
  held by the team's notice about g
- (c) `team resume --task` takes T1 back after the fall: resumed from `failed`, g is woken on the resume's note, answers
  T1 'revived'
- (d) a ceremony's facilitator falls for good (batch les-avis-et-la-relecture, s.984): the ceremony's task is the
  TEAM's, and the team's notice about the facilitator goes to the OWNER -- never to the team, whom nobody reads --;
  `inbox --json` lists it `awaits`, the face waits on `owner`
"""
from __future__ import annotations

import json

from tests.harness import support

T = support(__file__, "team")

DEATH = {"sleep": 0.1, "body": "crash"}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "f": {"T1": [DEATH, DEATH, {"sleep": 0.1, "body": {"re": "DO", "text": "recovered"}}]},
        "g": {"T1": [DEATH, DEATH, {"sleep": 0.1, "body": {"re": "DO", "text": "revived"}}],
              "T2": [{"sleep": 0.1, "body": {"re": "DO on T2", "text": "t2 done"}}]}})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of
    fallen = lambda member: lambda found: bool(T.finals_of(found, member)) and all_ended(found)

    # --- (a) a root tried on its opening, past its interval ----------------------------------------------------
    h.declare("frail", "---\nagents: |\n  f agents/f\nroot: f\nretries: 1\nschedule: off\n---\nThe root may fall.\n")
    started = h.call("team", "start", "frail", "--message", "try it", *h.harnessed)
    h.tick_until("frail", fallen("f"), timeout=40)
    before = h.events("frail")
    quiet = h.call("team", "tick", "frail")
    unmoved = len(h.events("frail")) == len(before)
    first = T.finals_of(before, "f")
    later = T.local_after(first[0]["at"], 6).isoformat(timespec="seconds") if first else None
    h.tick_until("frail", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=40, now=later)
    found = h.events("frail")
    tries = [one for one in T.intents_of(found, "f") if one.get("relance")]
    escalated = T.notices_about(found, "f")
    if (started.returncode == 0 and len(first) == 1 and quiet.returncode == 0 and unmoved
            and [one.get("relance") for one in tries] == ["tried"] and len(escalated) == 1
            and not by_kind(found, "resumed") and result_of(found, "T1") == "recovered"):
        held("(a) a root tried on its opening", "f fell on T1 (one notice about it); a tick within its interval writes nothing; "
             "past it the tick tries f by a relance on the opening (tried), f answers: T1 'recovered', no resume")
    else:
        failures.append(f"  ✗ (a) a root tried             rc={started.returncode}/{quiet.returncode} finals={len(first)} "
                        f"unmoved={unmoved} tries={[one.get('relance') for one in tries]} notices={len(escalated)} "
                        f"result={result_of(found, 'T1')!r} "
                        f"journal={[T.shape(one) + ((one.get('reason'), one.get('final')) if one.get('kind') == 'wake-failed' else ()) for one in found]}")

    # --- (b) an opening to a suspected root: the principal's word launches it, its try --------------------------
    h.declare("frail2", "---\nagents: |\n  g agents/g\nroot: g\nretries: 1\nschedule: off\n---\nThe root may fall.\n")
    started = h.call("team", "start", "frail2", "--message", "try it", *h.harnessed)
    h.tick_until("frail2", fallen("g"), timeout=40)
    fell = T.finals_of(h.events("frail2"), "g")
    posted = h.call("team", "post", "frail2", "--message", "another one")
    at_post = h.events("frail2")
    launched_at_post = T.intents_on(at_post, "g", "T2")
    h.tick_until("frail2", lambda found: bool(by_kind(found, "done", task="T2")) and all_ended(found), timeout=40)
    found = h.events("frail2")
    opening = next((one["id"] for one in by_kind(found, "post", verb="do") if one.get("task") == "T2"), None)
    told = [one for one in by_kind(found, "post", verb="notice") if one.get("task") == "T2"]
    in_place = [one for one in by_kind(found, "post", verb="re", **{"from": "g"}) if one.get("by") == "tick"]
    health = next((one.get("health") for one in h.face("frail2").get("members") or [] if one.get("member") == "g"), None) or {}
    if (started.returncode == 0 and posted.returncode == 0 and len(fell) == 1 and len(launched_at_post) == 1
            and launched_at_post[0].get("messages") == [opening] and not told and not in_place
            and result_of(found, "T2") == "t2 done" and health.get("suspected") is False and health.get("repents") == 1
            and not by_kind(found, "done", task="T1") and not by_kind(found, "resumed")):
        held("(b) an opening to a suspected root launches it", f"T2's opening #{opening} reaches g within its interval: g "
             "launched at the post's tick (its try), no notice, nothing answered in its place; T2 't2 done', g repented; "
             "T1 open")
    else:
        failures.append(f"  ✗ (b) an opening to a suspected rc={started.returncode}/{posted.returncode} finals={len(fell)} "
                        f"launched={[one.get('messages') for one in launched_at_post]} opening={opening} told={len(told)} "
                        f"in_place={len(in_place)} T2={result_of(found, 'T2')!r} health={health} "
                        f"T1_done={bool(by_kind(found, 'done', task='T1'))}")

    # --- (c) team resume --task takes T1 back after the fall ---------------------------------------------------------
    resumed = h.call("team", "resume", "frail2", "--task", "T1", "--message", "try again")
    h.tick_until("frail2", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=40)
    found = h.events("frail2")
    taken = next((one.get("from") for one in by_kind(found, "resumed")), None)
    if resumed.returncode == 0 and taken == ["failed"] and result_of(found, "T1") == "revived":
        held("(c) team resume takes T1 back", "resumed from failed: g woken on the note, T1 'revived'")
    else:
        failures.append(f"  ✗ (c) resume takes T1 back    rc={resumed.returncode} from={taken} T1={result_of(found, 'T1')!r} "
                        f"{resumed.stderr.strip()[-200:]!r}")

    # --- (d) a ceremony's facilitator falls for good: the owner is told, not the team -------------------------------
    h.scripted(fac={"T1": [DEATH]}, par={"T1": [{"sleep": 0.1, "body": {"re": "DO", "text": "took part"}}]})
    h.declare("rite", "---\nagents: |\n  fac agents/fac\n  par agents/par\nreports: |\n  par -> fac\nroot: fac\n"
                      "retries: 0\nschedule: off\nceremonies: |\n  daily every mon 09:30 with par -> fac\n---\n"
                      "The facilitator may fall.\n")
    started = h.call("team", "start", "rite", *h.harnessed)
    rung = h.call("team", "ring", "rite", "daily")
    h.tick_until("rite", fallen("fac"), timeout=40)
    found = h.events("rite")
    rite = next((one for one in by_kind(found, "task") if one.get("ceremony")), {})
    told = T.notices_about(found, "fac")
    boxed = h.call("team", "inbox", "rite", "--json")
    box = next((json.loads(line) for line in boxed.stdout.splitlines() if line.strip()), {})
    notices = [one for one in box.get("notices") or [] if one.get("about") == "fac"]
    owner = h.face("rite").get("owner")
    if (started.returncode == 0 and rung.returncode == 0 and rite.get("from") == "rite" and len(told) == 1
            and told[0].get("to") == owner and told[0].get("task") == rite.get("task")
            and len(notices) == 1 and notices[0].get("awaits") is True and notices[0].get("task") == rite.get("task")
            and "owner" in (h.face("rite").get("waiting_on") or [])):
        held("(d) a fallen facilitator: the owner told", f"the ceremony's task {rite.get('task')} is the team's; fac fell for "
             f"good: one notice about fac to {owner} (#{told[0]['id']}), in the owner's inbox (awaits), the face waits on owner")
    else:
        failures.append(f"  ✗ (d) a fallen facilitator      rc={started.returncode}/{rung.returncode} task={rite.get('task')} "
                        f"from={rite.get('from')} told={[(one.get('to'), one.get('task')) for one in told]} "
                        f"inbox={notices} waiting_on={h.face('rite').get('waiting_on')} "
                        f"finals={len(T.finals_of(found, 'fac'))} {boxed.stderr[-120:]!r}")
    return 0
