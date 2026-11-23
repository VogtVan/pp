"""Scenario `team-log` -- 5 case(s): the readers of a journal -- `inbox`, `log`, `responses` and `result` -- on
a team the witness plays and on the journal team 0.32.2 wrote (`T.OLD_JOURNAL`). A team `desk` (lead root, rev
reporting to lead, `schedule: off`): lead asks the owner, a task T2 is posted and stopped (its `do` returned),
the owner marks the inbox seen, replies, lead delegates to rev, rev answers, lead concludes; a team `calm`
started with nothing waiting, a team `idle` never started, a team `old` whose journal is the old one.
- the inbox: `--json` gives the question with its text and the returned post, each with the `at` of its event;
  after `--seen` the question alone; after the reply and the conclusion, T1 done at its event's `at`; without a
  name, only the teams where something waits; `--seen --json`: the usage
- the log: `--json` gives one object per event, the object `watch --json` writes, the snapshot left out;
  `--task T1` and `--last 3` keep the ids the text keeps
- the responses: `--json` gives one object per `wake-ended`, its text the record's, its cost the event's;
  `--since`, `--agent`, `--task --last` keep the ids the text keeps; a team never started: `team-not-started`
- `log` renders the journal, one line per event: `--task T1` the events of T1 (its posts, its intents and
  their ends), `--last 3` the three last, bare all of them; nothing written
- `result` reads a resolved task's result: `"LGTM"` for the old T1, the last resolved without a task,
  `task-open` on a stopped or an open task, `team-unknown`; nothing written
The old journal's own cases are `team-log-old`'s.
"""
from __future__ import annotations

import json

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
    question = {"id": ask.get("id"), "verb": "ask", "from": "lead", "task": "T1", "text": "which PR?",
                "at": ask.get("at")}                          # each entry carries the moment of its event
    if (started.returncode == 0 and asked and all(one.returncode == 0 for one in calls) and done
            and box_1 == [{"team": "desk", "name": "desk", "questions": [question], "notices": [], "infos": [], "done": [],
                           "returned": [{"id": returned_post.get("id"), "verb": "do", "from": "house", "task": "T2",
                                         "text": "later", "at": returned_post.get("at")}]}]
            and box_2 == [{"team": "desk", "name": "desk", "questions": [question], "notices": [], "infos": [], "done": [],
                           "returned": []}]
            and box_3 is not None and len(box_3) == 1 and box_3[0]["questions"] == [] and box_3[0]["returned"] == []
            and [(one["task"], one["at"]) for one in box_3[0]["done"]]
            == [("T1", one.get("at")) for one in by_kind(h.events("desk"), "done", task="T1")]
            and ask.get("at") and returned_post.get("at")
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
    return 0
