"""Scenario `team-log` -- 9 case(s): the readers of a journal -- `inbox`, `log`, `responses` and `result` -- on
a team the witness plays and on the journal team 0.32.2 wrote (`T.OLD_JOURNAL`). A team `desk` (lead root, rev
reporting to lead, `schedule: off`): lead asks the owner, a task T2 is posted and stopped (its `do` returned),
the owner marks the inbox seen, replies, lead delegates to rev, rev answers, lead concludes; a team `calm`
started with nothing waiting, a team `idle` never started, a team `old` whose journal is the old one.
- the inbox: `--json` gives the question with its text and the returned post; after `--seen` the question
  alone; after the reply and the conclusion, T1 done; without a name, only the teams where something waits;
  `--seen --json`: the usage
- the log: `--json` gives one object per event, the object `watch --json` writes, the snapshot left out;
  `--task T1` and `--last 3` keep the ids the text keeps
- the responses: `--json` gives one object per `wake-ended`, its text the record's, its cost the event's;
  `--since`, `--agent`, `--task --last` keep the ids the text keeps; a team never started: `team-not-started`
- `log` renders the journal, one line per event: `--task T1` the events of T1 (its posts, its intents and
  their ends), `--last 3` the three last, bare all of them; nothing written
- `result` reads a resolved task's result: `"LGTM"` for the old T1, the last resolved without a task,
  `task-open` on a stopped or an open task, `team-unknown`; nothing written
- (a) `log --json` on the old journal: no `delegation`, no `terminal`; every post a `do`, an `ask`, a `re` or a
  `notice`; r1's and r2's `done` to m are `re` to the `do` each received (`was: done`), m's `reply` a `re` to
  r2's ask (`was: reply`), r1's `escalate` to m a `re` to its `do` (`was: escalate`), m's `escalate` to the
  owner the team's `notice` about m
- (b) `log` on the old journal: its lines carry the ids `--json` carries -- no `delegation` nor `terminal`
  line, the notice #56 said
- (c) `watch --json`: two events of the old kinds appended while it watches -- the `delegation` is never said,
  the `done` is said `re`
- (d) `status --json`: the face of the old journal is read -- T1 resolved, T2 open, its members m, r1 and r2
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import threading
import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "lead": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which PR?"}}},
                 {"sleep": 0.1, "body": {"do": ["rev"]}}, {"sleep": 0.1, "body": {"done": "merged"}}],
        "rev": [{"sleep": 0.1, "body": {"done": "reviewed"}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    def faced(*args: str) -> tuple:
        played = h.call("team", *args)
        try:
            found = [json.loads(line) for line in played.stdout.splitlines() if line.strip()]
        except ValueError:
            found = None
        return played, found

    def ids(played) -> list[int]:
        return [int(line.split()[0].lstrip("#")) for line in played.stdout.splitlines() if line.startswith("#")]

    h.declare("desk", "---\nagents: |\n  lead agents/lead\n  rev agents/rev\nreports: |\n  rev -> lead\nroot: lead\n"
                      "schedule: off\n---\nMerge what is asked.\n")
    h.declare("calm", "---\nagents: |\n  c agents/c\nroot: c\nschedule: off\n---\nNothing to say.\n")
    h.declare("idle", "---\nagents: |\n  s agents/s\nroot: s\n---\nNever started.\n")
    h.declare("old", T.OLD_DECLARED)
    h.journal_of("old").parent.mkdir(parents=True, exist_ok=True)
    h.journal_of("old").write_text(T.OLD_JOURNAL, encoding="utf-8")

    # --- the teams play: desk asks the owner, a returned post, the inbox seen, the reply, the end ----------
    started = h.call("team", "start", "desk", "--message", "merge it", *h.harnessed)
    calls = [h.call("team", "start", "calm", "--message", "wait", "--no-tick")]
    asked = h.settled("desk", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), 60)
    ask = next((one for one in by_kind(h.events("desk"), "post", verb="ask")), {})
    calls += [h.call("team", "post", "desk", "--message", "later", "--no-tick"),
              h.call("team", "stop", "desk", "--task", "T2", "--no-tick")]
    _, box_1 = faced("inbox", "desk", "--json")
    calls.append(h.call("team", "inbox", "desk", "--seen"))
    _, box_2 = faced("inbox", "desk", "--json")
    calls.append(h.call("team", "post", "desk", "--task", "T1", "--reply", str(ask.get("id")), "--message", "PR 7"))
    done = h.settled("desk", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    _, box_3 = faced("inbox", "desk", "--json")
    every_rc, every = faced("inbox", "--json")
    mixed = h.call("team", "inbox", "desk", "--seen", "--json")
    returned = by_kind(h.events("desk"), "returned")
    returned_post = next((one for one in by_kind(h.events("desk"), "post") if returned
                          and one["id"] == returned[0].get("message")), {})

    # --- the inbox ---------------------------------------------------------------------------------------
    question = {"id": ask.get("id"), "verb": "ask", "from": "lead", "task": "T1", "text": "which PR?"}
    if (started.returncode == 0 and asked and all(one.returncode == 0 for one in calls) and done
            and box_1 == [{"team": "desk", "questions": [question], "notices": [], "done": [],
                           "returned": [{"id": returned_post.get("id"), "verb": "do", "from": "house", "task": "T2",
                                         "text": "later"}]}]
            and box_2 == [{"team": "desk", "questions": [question], "notices": [], "done": [], "returned": []}]
            and box_3 is not None and len(box_3) == 1 and box_3[0]["questions"] == [] and box_3[0]["returned"] == []
            and [one["task"] for one in box_3[0]["done"]] == ["T1"]
            and every_rc.returncode == 0 and sorted(one["team"] for one in every or []) == ["desk", "old"]
            and mixed.returncode == 2 and "usage" in mixed.stderr and mixed.stdout == ""):
        held("the inbox", f"the question #{ask.get('id')} with its text and the returned #{returned_post.get('id')}; "
             "after --seen the question alone; after the reply T1 done; without a name desk and old (calm waits for "
             "nothing, idle never started); --seen --json: the usage")
    else:
        failures.append(f"  ✗ the inbox                   rc={started.returncode}/{[c.returncode for c in calls]} "
                        f"asked={asked} done={done} box1={box_1} box2={box_2} box3={box_3} every={every} "
                        f"mixed={mixed.returncode}:{mixed.stderr[-120:]!r} {[c.stderr[-150:] for c in calls if c.returncode]}")

    # --- the log --json ------------------------------------------------------------------------------------
    snapped = h.call("team", "snapshot", "desk")
    journals = (h.journal_of("desk"), h.journal_of("old"))
    before_w = [one.read_bytes() for one in journals]       # what the readers below leave as it is
    events =[one for one in h.events("desk") if one.get("kind") != "snapshot"]
    shaped = [{"at": one.get("at"), "team": "desk", "event": one.get("kind"),
               **{key: value for key, value in one.items() if key not in ("at", "kind", "team")}} for one in events]
    whole_rc, whole = faced("log", "desk", "--json")
    task_rc, by_task = faced("log", "desk", "--task", "T1", "--json")
    tail_rc, tail = faced("log", "desk", "--last", "3", "--json")
    text_task, text_tail = h.call("team", "log", "desk", "--task", "T1"), h.call("team", "log", "desk", "--last", "3")
    if (snapped.returncode == 0 and whole_rc.returncode == 0 and whole == shaped and len(whole) > 20
            and not any(one.get("event") == "snapshot" for one in whole)
            and task_rc.returncode == 0 and [one["id"] for one in by_task or []] == ids(text_task) and ids(text_task)
            and tail_rc.returncode == 0 and [one["id"] for one in tail or []] == ids(text_tail) == [e["id"] for e in events[-3:]]):
        held("the log", f"{len(whole)} objects, each the event as watch --json writes it, the snapshot left out; "
             f"--task T1 {len(by_task)} and --last 3 keep the text's ids")
    else:
        failures.append(f"  ✗ the log                     rc={snapped.returncode}/{whole_rc.returncode}/{task_rc.returncode}/"
                        f"{tail_rc.returncode} same={whole == shaped} n={len(whole or [])}/{len(shaped)} "
                        f"task={[one.get('id') for one in by_task or []]}/{ids(text_task)} "
                        f"tail={[one.get('id') for one in tail or []]}/{ids(text_tail)} {whole_rc.stderr[-200:]!r}")

    # --- the responses -------------------------------------------------------------------------------------
    ends = by_kind(h.events("desk"), "wake-ended")
    all_rc, answers = faced("responses", "desk", "--json")
    first = ends[0]["id"] if ends else 0
    picks = {"since": (["--since", str(first)], None), "agent": (["--agent", "rev"], None),
             "task": (["--task", "T1", "--last", "1"], None)}
    for key, (args, _) in picks.items():
        picks[key] = (faced("responses", "desk", *args, "--json")[1], ids(h.call("team", "responses", "desk", *args)))
    unstarted = h.call("team", "responses", "idle", "--json")

    def kept(one: dict) -> str | None:
        flowed = h.call("agent", "flow", one.get("path"), one.get("run"), "--json", "--exchange", str(one.get("launch")))
        texts = [str(json.loads(line).get("text") or "").strip() for line in flowed.stdout.splitlines()
                 if line.strip() and json.loads(line).get("kind") == "words"]
        return "\n\n".join(text for text in texts if text) or None

    if (all_rc.returncode == 0 and answers is not None and [one["id"] for one in answers] == [e["id"] for e in ends]
            and len(answers) == 4 and all(one["response"] == kept(one) and one["response"] for one in answers)
            and all(set(one) == {"id", "member", "path", "task", "run", "launch", "at", "cost_usd", "response"}
                    for one in answers)
            and [one["cost_usd"] for one in answers] == [e.get("cost") for e in ends]
            and [one["member"] for one in answers] == [e.get("agent") for e in ends]
            and all([one["id"] for one in (found or [])] == text and text for found, text in picks.values())
            and unstarted.returncode == 2 and "team-not-started" in unstarted.stderr):
        held("the responses", f"{len(answers)} objects, each text the words of its launch at the flow, each cost the "
             f"event's; --since #{first}, "
             "--agent rev, --task T1 --last 1 keep the text's ids; idle: team-not-started")
    else:
        failures.append(f"  ✗ the responses               rc={all_rc.returncode} answers={answers} "
                        f"ends={[e['id'] for e in ends]} picks={picks} idle={unstarted.returncode}:{unstarted.stderr[-120:]!r}")

    # --- log renders the journal, by task and by tail -------------------------------------------------------
    everything = [one for one in h.events("desk") if one.get("kind") != "snapshot"]
    tags_t1 = {one.get("tag") for one in everything if one.get("kind") == "wake-intent" and one.get("task") == "T1"}
    ids_t1 = [one["id"] for one in everything if one.get("task") == "T1" or one.get("tag") in tags_t1]
    logged, tailed = text_task, text_tail                   # the text read above, on this same journal
    whole_log = h.call("team", "log", "desk")
    opening = [one["id"] for one in by_task or [] if one.get("event") == "post" and one.get("verb") == "do"
               and one.get("from") == "house" and one.get("to") == "lead" and one.get("task") == "T1"]
    if (logged.returncode == 0 and ids(logged) == ids_t1 and len(ids_t1) > 15
            and tailed.returncode == 0 and ids(tailed) == [one["id"] for one in everything[-3:]]
            and whole_log.returncode == 0 and ids(whole_log) == [one["id"] for one in everything]
            and [one.read_bytes() for one in journals] == before_w
            and len(opening) == 1 and opening[0] in ids(logged)):
        held("log renders the journal", f"--task T1: {len(ids_t1)} line(s) in order (the posts -- the opening #{opening[0]} "
             f"among them --, the intents and their ends); --last 3: the three last ids; bare: all {len(everything)}; "
             "nothing written")
    else:
        failures.append(f"  ✗ log                         {logged.returncode}/{tailed.returncode}/{whole_log.returncode} "
                        f"t1={ids(logged)}/{ids_t1} tail={ids(tailed)} opening={opening} "
                        f"written={[one.read_bytes() for one in journals] != before_w}")

    # --- result reads a resolved task's result ---------------------------------------------------------------
    got = h.call("team", "result", "old", "T1")
    last_resolved = [one for one in h.events("old") if one.get("kind") == "done"][-1]
    latest = h.call("team", "result", "old")
    stopped_r = h.call("team", "result", "desk", "T2")
    stopped_state = {one.get("id"): one.get("state") for one in h.face("desk").get("tasks") or []}.get("T2")
    nothing = h.call("team", "result", "nothing")
    opened_r = h.call("team", "result", "old", "T2")
    if (got.returncode == 0 and json.loads(got.stdout or "null") == "LGTM"
            and latest.returncode == 0 and json.loads(latest.stdout or "null") == last_resolved.get("result")
            and stopped_r.returncode == 2 and "task-open" in stopped_r.stderr and stopped_state == "stopped"
            and nothing.returncode == 2 and "team-unknown" in nothing.stderr
            and opened_r.returncode == 2 and "task-open" in opened_r.stderr
            and [one.read_bytes() for one in journals] == before_w):
        held("result reads a resolved task", f'old T1 -> "LGTM"; bare -> the last resolved ({last_resolved.get("task")}); '
             "desk T2 (stopped) -> task-open; nothing -> team-unknown; old T2 (open) -> task-open; nothing written")
    else:
        failures.append(f"  ✗ result                      {got.returncode}/{latest.returncode}/{stopped_r.returncode}/"
                        f"{nothing.returncode}/{opened_r.returncode} {got.stdout!r} {latest.stdout!r} "
                        f"T2={stopped_state} {stopped_r.stderr[-120:]!r} {opened_r.stderr[-120:]!r}")

    # --- (a) log --json on the old journal ---------------------------------------------------------------------
    played, said = faced("log", "old", "--json")
    said = said or []
    by_id = {one.get("id"): one for one in said}
    kinds = {one.get("event") for one in said}
    verbs = {one.get("verb") for one in said if one.get("event") == "post"}

    def seen(key: int) -> tuple:
        one = by_id.get(key) or {}
        return tuple(one.get(field) for field in ("verb", "re", "was", "from", "about"))

    wanted = {21: ("re", 7, "done", "r1", None), 23: ("re", 16, "reply", "m", None), 28: ("re", 9, "done", "r2", None),
              50: ("re", 41, "escalate", "r1", None), 56: ("notice", None, "escalate", "old", "m")}
    got_a = {key: seen(key) for key in wanted}
    if (played.returncode == 0 and not kinds & {"delegation", "terminal"} and verbs <= {"do", "ask", "re", "notice", "note", "stop"}
            and got_a == wanted and 8 not in by_id and 20 not in by_id):
        held("(a) log --json speaks the debt", f"no delegation, no terminal; posts {sorted(verbs)}; #21 #23 #28 #50 said re "
             "(was done, reply, done, escalate), #56 the team's notice about m")
    else:
        failures.append(f"  ✗ (a) log --json             rc={played.returncode} kinds={sorted(map(str, kinds))} "
                        f"verbs={sorted(map(str, verbs))} got={got_a}")

    # --- (b) log, the text: the ids --json carries, the dead events' ids absent ---------------------------------
    text = h.call("team", "log", "old")
    dead = {one["id"] for one in h.events("old") if one.get("kind") in ("delegation", "terminal")}
    if (text.returncode == 0 and ids(text) == [one.get("id") for one in said] and dead and not dead & set(ids(text))
            and 56 in ids(text)):
        held("(b) log speaks the debt", f"{len(ids(text))} lines, the ids of --json; no dead line ({sorted(dead)} absent); "
             "#56 said")
    else:
        failures.append(f"  ✗ (b) log                    rc={text.returncode} ids={ids(text)} json={[one.get('id') for one in said]} "
                        f"dead={sorted(dead)}")

    # --- (c) watch --json: the old kinds appended while it watches ---------------------------------------------
    watcher = subprocess.Popen([sys.executable, str(h.engine), "--instance", str(h.house), "team", "watch", "old", "--json",
                                "--heartbeat", "1", "--for", "15"], cwd=h.ws, env={**os.environ, **h.env},
                               stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, start_new_session=True)
    heard: list[str] = []
    reader = threading.Thread(target=lambda: heard.extend(iter(watcher.stderr.readline, "")), daemon=True)
    reader.start()
    deadline = time.monotonic() + 10
    while not heard and time.monotonic() < deadline:          # the first quiet beat: the watch follows the journal
        time.sleep(0.1)
    with h.journal_of("old").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"at": "2026-10-13T05:42:00+00:00", "id": 57, "kind": "delegation", "team": "old",
                                 "from": "m", "to": "r2", "task": "T2"}) + "\n")
        handle.write(json.dumps({"at": "2026-10-13T05:42:00+00:00", "id": 58, "kind": "post", "team": "old", "task": "T2",
                                 "from": "m", "to": "r2", "verb": "do", "text": "look"}) + "\n")
        handle.write(json.dumps({"at": "2026-10-13T05:42:01+00:00", "id": 59, "kind": "post", "team": "old", "task": "T2",
                                 "from": "r2", "to": "m", "verb": "done", "text": "looked"}) + "\n")

    def flow() -> list[dict]:
        found = []
        for one in list(heard):
            try:
                found.append(json.loads(one))
            except ValueError:
                pass
        return found

    deadline = time.monotonic() + 10
    while not any(one.get("id") == 59 for one in flow()) and time.monotonic() < deadline:
        time.sleep(0.1)
    os.killpg(watcher.pid, signal.SIGTERM)                    # read: the watch and what it launched end here
    watcher.wait(timeout=10)
    reader.join(timeout=5)
    ids_c = {one.get("id"): one for one in flow() if one.get("team") == "old"}
    if 57 not in ids_c and (ids_c.get(58) or {}).get("verb") == "do" and \
            ((ids_c.get(59) or {}).get("verb"), (ids_c.get(59) or {}).get("re"), (ids_c.get(59) or {}).get("was")) == ("re", 58, "done"):
        held("(c) watch --json speaks the debt", "the delegation #57 never said; #59 r2's done said re #58 (was done)")
    else:
        failures.append(f"  ✗ (c) watch --json           ids={sorted(map(str, ids_c))} #59={ids_c.get(59)} {''.join(heard)[-300:]!r}")

    # --- (d) status --json: the face of the old journal ---------------------------------------------------------
    face = h.face("old")
    tasks = {one.get("id"): one.get("state") for one in face.get("tasks") or []}
    members = {one.get("member") for one in face.get("members") or []}
    if tasks == {"T1": "resolved", "T2": "open"} and {"m", "r1", "r2"} <= members:
        held("(d) status --json reads the old journal", f"tasks {tasks}, members {sorted(members)}")
    else:
        failures.append(f"  ✗ (d) status --json          tasks={tasks} members={sorted(members)} face={str(face)[-300:]!r}")
    return 0
