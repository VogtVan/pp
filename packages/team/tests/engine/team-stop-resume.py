"""Scenario `team-stop-resume` -- 4 case(s): `team stop` ends a task without interrupting the wake-up under way, and
`team resume <name> --task <id>` takes a stopped task back. Five teams run side by side in one house, each under its
own names; each case waits for its team, then reads its journal, its face and the heads its members were shown.
- (a) the refusals of a resume, judged before anything is written: `team-unknown`, `team-not-started`,
  `task-unknown`, `task-resolved`, `task-not-blocked` (an open task nobody failed on), `principal-unknown`, and
  without `--task` `team-not-paused` -- rc 2 each, by their code, every journal byte-identical
- a stop reaches its holders alone: g delegates to g1, g1 answers, g asks the owner; `team stop --task T1` posts
  one stop, to g -- g1, which has answered, holds nothing --; nobody is woken after it; the face says T1 stopped
- a stop does not interrupt, and routes nowhere: h delegates to h1, which sleeps; a note is laid while h waits,
  then `team stop --task T1` while h1's wake-up runs: a stop post to h and to h1, the note returned to the owner;
  h1's wake-up ends after the stop, not killed, and its answer is routed nowhere; nobody is woken for the stop,
  even by a later tick; the face says T1 stopped
- (b) a stopped task taken back: `team resume --message` writes `resumed {task, by, from: [stopped]}` (in the
  journal and in `team log --json`), then a note to h and to h1 -- the holders at the stop --; h1 is woken in its
  own run with that note in its head, answers, h is woken in its own run and resolves T1; the returned note
  stays returned and reaches no head; the face says T1 resolved, resumed by that event
"""
from __future__ import annotations

import json
import re

from tests.harness import support

T = support(__file__, "team")

# A message head as the witness reads it: `#<id> <KIND>[ #<re>] from <who> on <task>[ -- you owe ...]`.
HEAD = re.compile(r"^#(\d+) ([A-Z]+)(?: #(\d+))? from (\S+) on (\S+?)( -- you owe an answer(, and your answer to it "
                  r"closes \S+)?)?$", re.M)
REFUSED = re.compile(r"^pp-team: (\S+) --", re.M)


def heads(prompt: str) -> list[tuple[int, str, str, str]]:
    """-> the messages a head shows: (id, KIND, from, task) each."""
    return [(int(one.group(1)), one.group(2), one.group(4), one.group(5)) for one in HEAD.finditer(prompt)]


def code_of(played) -> str:
    """-> the code a refusal names on stderr, '' when none."""
    found = REFUSED.search(played.stderr)
    return found.group(1) if found else ""


def task_state(face: dict, task: str) -> dict:
    """-> the face's object of one task, {} when absent."""
    return next((one for one in face.get("tasks") or [] if one.get("id") == task), {})


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        # the stop and the resume: h delegates to h1, which sleeps through the stop -- long enough for the post and the
        # stop to land inside its wake-up under a loaded machine; the other cases play meanwhile
        "h": [{"sleep": 0.2, "body": {"do": ["h1"]}}, {"sleep": 0.1, "body": {"done": "resumed"}}],
        "h1": [{"sleep": 5.0, "body": {"done": True}}, {"sleep": 0.1, "body": {"done": True}}],
        # the refusals: a task resolved at once
        "d": [{"sleep": 0.1, "body": {"done": "finished"}}],
        # the holders: g1 answers, g asks the owner and holds T1 alone
        "g": [{"sleep": 0.1, "body": {"do": ["g1"]}}, {"sleep": 0.1, "body": {"escalate": "blocked by the build"}}],
        "g1": [{"sleep": 0.1, "body": {"done": True}}]})
    by_kind, all_ended = T.by_kind, T.all_ended
    go_on = "go on"

    # --- every team declared and started before the first wait: they run side by side ----------------------
    h.declare("never", "---\nagents: |\n  n agents/n\nroot: n\nschedule: off\n---\nNever started.\n")
    h.declare("idle", "---\nagents: |\n  i agents/i\nroot: i\nschedule: off\n---\nOne task, still due.\n")
    h.declare("over", "---\nagents: |\n  d agents/d\nroot: d\nschedule: off\n---\nDone at once.\n")
    h.declare("halt", "---\nagents: |\n  h agents/h\n  h1 agents/h1\nreports: |\n  h1 -> h\nroot: h\n"
                      "schedule: off\n---\nHalt, then go on.\n")
    h.declare("hold", "---\nagents: |\n  g agents/g\n  g1 agents/g1\nreports: |\n  g1 -> g\nroot: g\n"
                      "schedule: off\n---\nHeld by the root alone.\n")
    idle = h.call("team", "start", "idle", "--message", "later", *h.harnessed, "--no-tick")
    over = h.call("team", "start", "over", "--message", "finish", *h.harnessed)
    started = h.call("team", "start", "halt", "--message", "review slowly", *h.harnessed)
    holding = h.call("team", "start", "hold", "--message", "fix the build", *h.harnessed)

    # --- the stop laid while h1's wake-up runs: first, its window is h1's sleep ------------------------------
    running = h.settled("halt", lambda found: bool(by_kind(found, "wake-launched", agent="h1")), 60)
    noted = h.call("team", "post", "halt", "--task", "T1", "--message", "while you wait", "--no-tick")
    # no tick: a note wakes a waiting member -- this one stays undelivered until the stop
    stopped = h.call("team", "stop", "halt", "--task", "T1")

    # --- (a) judged before anything is written -------------------------------------------------------
    finished = h.settled("over", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 45)
    journals = {name: h.journal_of(name) for name in ("idle", "over")}
    before = {name: path.read_bytes() for name, path in journals.items()}
    refusals = {
        "team-unknown": h.call("team", "resume", "nope", "--task", "T1"),
        "team-not-started": h.call("team", "resume", "never", "--task", "T1"),
        "task-unknown": h.call("team", "resume", "idle", "--task", "T9"),
        "task-resolved": h.call("team", "resume", "over", "--task", "T1"),
        "task-not-blocked": h.call("team", "resume", "idle", "--task", "T1"),
        "principal-unknown": h.call("team", "resume", "idle", "--task", "T1", "--as", "zz"),
        "team-not-paused": h.call("team", "resume", "idle")}
    untouched = all(path.read_bytes() == before[name] for name, path in journals.items())
    if (idle.returncode == 0 and over.returncode == 0 and finished and untouched
            and all(one.returncode == 2 and code_of(one) == code for code, one in refusals.items())):
        held("(a) judged before writing", "team-unknown, team-not-started, task-unknown, task-resolved, "
             "task-not-blocked, principal-unknown, team-not-paused: rc 2 each, by their code, both journals "
             "byte-identical")
    else:
        failures.append(f"  ✗ (a) judged before writing    rc={idle.returncode}/{over.returncode} finished={finished} "
                        f"untouched={untouched} "
                        f"{[(code, one.returncode, code_of(one), one.stderr.strip()[-120:]) for code, one in refusals.items()]}")

    # --- a stop reaches its holders alone -------------------------------------------------------------
    asked_g = h.settled("hold", lambda found: bool(T.asks_to(found, "g", "house")) and all_ended(found), 60)
    stopped_g = h.call("team", "stop", "hold", "--task", "T1")
    barrier_g = h.call("team", "tick", "hold")
    found_g = h.events("hold")
    stop_g = next(iter(by_kind(found_g, "stopped", task="T1")), {})
    stops_g = [(one.get("from"), one.get("to")) for one in by_kind(found_g, "post", verb="stop")]
    after_g = [one for one in by_kind(found_g, "wake-intent") if one["id"] > stop_g.get("id", 10 ** 9)]
    face_g = task_state(h.face("hold"), "T1")
    if (holding.returncode == 0 and asked_g and stopped_g.returncode == 0 and barrier_g.returncode == 0 and stop_g
            and len(T.closings(found_g, "g1")) == 1 and stops_g == [("house", "g")] and after_g == []
            and face_g.get("state") == "stopped"):
        held("a stop reaches its holders alone", f"g1 answered, g asked the owner: stop #{stop_g['id']} posts one "
             f"stop, to g; nobody woken after it; the face: T1 {face_g.get('state')}")
    else:
        failures.append(f"  ✗ stop to the holders         {holding.returncode}/{stopped_g.returncode}/{barrier_g.returncode} "
                        f"asked={asked_g} stop={stop_g} stops={stops_g} closings={T.closings(found_g, 'g1')} "
                        f"after={[(one['agent'], one.get('task')) for one in after_g]} face={face_g} "
                        f"{stopped_g.stderr[-200:]!r}")

    # --- a stop does not interrupt, and routes nowhere ----------------------------------------------
    quiet = h.settled("halt", lambda found: len(by_kind(found, "wake-ended", agent="h1")) >= 1 and all_ended(found), 60)
    barrier = h.call("team", "tick", "halt")       # whatever h1's end would route, a tick has had its chance
    found = h.events("halt")
    face_stopped = task_state(h.face("halt"), "T1")
    stops = by_kind(found, "post", verb="stop")
    stop_event = next(iter(by_kind(found, "stopped", task="T1")), {})
    note_h = by_kind(found, "post", verb="note")
    returned_h = by_kind(found, "returned")
    first_end = next(iter(by_kind(found, "wake-ended", agent="h1")), {})
    routed_after = [one for one in found if one.get("id", 0) > first_end.get("id", 10 ** 9)
                    and (one.get("kind") == "done"
                         or (one.get("kind") == "post" and one.get("from") in ("h", "h1")))]
    second = {agent: by_kind(found, "wake-intent", agent=agent)[1:] for agent in ("h", "h1")}
    runs = {member: T.runs_launched(found, member) for member in ("h", "h1")}
    if (started.returncode == 0 and running and noted.returncode == 0 and stopped.returncode == 0 and quiet
            and barrier.returncode == 0
            and sorted(one["to"] for one in stops) == ["h", "h1"] and all(one.get("from") == "house" for one in stops)
            and len(note_h) == 1
            and [(one.get("message"), one.get("to")) for one in returned_h] == [(note_h[0]["id"], "house")]
            and stop_event and first_end and stop_event["id"] < first_end["id"] and not by_kind(found, "wake-killed")
            and routed_after == []
            and all(second[agent] == [] for agent in ("h", "h1"))
            and len(by_kind(found, "wake-ended")) == 2 and not by_kind(found, "wake-failed")
            and face_stopped.get("state") == "stopped"):
        held("a stop does not interrupt, and routes nowhere", f"stop #{stop_event['id']} to h and h1 while h1 ran "
             f"(its end #{first_end['id']}, not killed), the note returned to house; h1's answer routed nowhere; nobody "
             f"woken for the stop, even by a later tick; the face: T1 {face_stopped.get('state')}")
    else:
        failures.append(f"  ✗ stop                        {started.returncode}/{noted.returncode}/{stopped.returncode}/"
                        f"{barrier.returncode} running={running} quiet={quiet} stop={stop_event.get('id')} "
                        f"end={first_end.get('id')} stops={[(one['to'], one['id']) for one in stops]} "
                        f"returned={[(one.get('message'), one.get('to')) for one in returned_h]} routed_after={routed_after} "
                        f"second={ {a: [one.get('messages') for one in s] for a, s in second.items()} } "
                        f"face={face_stopped} {stopped.stderr[-200:]!r}")

    # --- (b) a stopped task taken back: the holders noted, each in its run ------------------------------
    resumed = h.call("team", "resume", "halt", "--task", "T1", "--message", go_on)
    done = h.settled("halt", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    found = h.events("halt")
    resumes = by_kind(found, "resumed")
    mark = resumes[0]["id"] if resumes else 10 ** 9
    logged = [json.loads(line) for line in h.call("team", "log", "halt", "--json").stdout.splitlines()
              if line.strip().startswith("{")]
    logged_resumes = [(one.get("id"), one.get("task"), one.get("by"), one.get("from")) for one in logged
                      if one.get("event") == "resumed"]
    notes = {one.get("to"): one for one in by_kind(found, "post", verb="note") if one["id"] > mark}
    after = {member: {one.get("run") for one in by_kind(found, "wake-launched", agent=member) if one["id"] > mark}
             for member in ("h", "h1")}
    prompts = {member: h.prompts_of(member) for member in ("h", "h1")}
    revived = heads(prompts["h1"][-1]) if len(prompts["h1"]) >= 2 else []
    returned = [one.get("message") for one in returned_h]
    shown = {one[0] for member in ("h", "h1") for prompt in prompts[member] for one in heads(prompt)}
    face_done = task_state(h.face("halt"), "T1")
    if (resumed.returncode == 0 and done
            and [(one.get("task"), one.get("by"), one.get("from")) for one in resumes] == [("T1", "house", ["stopped"])]
            and logged_resumes == [(mark, "T1", "house", ["stopped"])]
            and sorted(notes) == ["h", "h1"]
            and all(one.get("from") == "house" and one.get("task") == "T1" and one.get("text") == go_on
                    for one in notes.values())
            and after["h1"] and after["h1"] <= runs["h1"] and after["h"] and after["h"] <= runs["h"]
            and (notes["h1"]["id"], "NOTE", "house", "T1") in revived
            and len(returned) == 1 and not set(returned) & shown
            and [one.get("message") for one in by_kind(found, "returned")] == returned
            and T.result_of(found, "T1") == "resumed"
            and face_done.get("state") == "resolved" and face_done.get("resumed") == mark):
        held("(b) a stopped task taken back", f"resumed #{mark} from [stopped] (journal and log), a note to h and h1; "
             f"h1 woken in run {sorted(after['h1'])[0]} (its own) with note #{notes['h1']['id']} in its head, h in "
             f"{sorted(after['h'])[0]}; T1 resolved 'resumed'; the returned note #{returned[0]} in no head")
    else:
        failures.append(f"  ✗ (b) a stopped task taken back rc={resumed.returncode} done={done} "
                        f"{resumed.stderr.strip()[-200:]!r} resumes={resumes} logged={logged_resumes} "
                        f"notes={ {to: (one['id'], one.get('from'), one.get('text')) for to, one in notes.items()} } "
                        f"runs={runs} after={after} returned={returned} shown={sorted(shown)} revived={revived} "
                        f"result={T.result_of(found, 'T1')!r} face={face_done}")
    return 0
