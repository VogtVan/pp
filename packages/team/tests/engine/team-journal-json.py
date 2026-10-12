"""Scenario `team-journal-json` -- 3 case(s) (batch le-journal-en-json of plan ui, 2026-10-10: team 0.21.0):
`log`, `responses` and `inbox` take `--json`, the faces a program reads; their text keeps its bytes. A
team `desk` (m root, r1 reporting to m, `schedule: off`): m asks the owner, a task T2 is posted and
stopped (its `do` returned), the owner marks the inbox seen, replies, m delegates to r1, r1 answers, m
concludes; a team `calm` started with nothing waiting, a team `idle` never started.
- the log: one object per event, the object `watch --json` writes (`event_object`), the snapshot left
  out; `--task T1` and `--last 3` keep the ids the text keeps
- the responses: one object per `wake-ended`, its text the record's, its cost the event's; `--since`,
  `--agent`, `--task --last` keep the ids the text keeps; a team never started: `team-not-started`
- the inbox: the question with its text and the returned post; after `--seen` the question alone; after
  the reply and the conclusion, T1 done; without a name, only the teams where something waits;
  `--seen --json`: the usage
"""
from __future__ import annotations

import json

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "m": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which PR?"}}},
              {"sleep": 0.1, "body": {"do": ["r1"]}}, {"sleep": 0.1, "body": {"done": "merged"}}],
        "r1": [{"sleep": 0.1, "body": {"done": "reviewed"}}]})
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

    h.declare("desk", "---\nagents: |\n  m agents/m\n  r1 agents/r1\nreports: |\n  r1 -> m\nroot: m\n"
                      "schedule: off\n---\nMerge what is asked.\n")
    h.declare("calm", "---\nagents: |\n  c agents/c\nroot: c\nschedule: off\n---\nNothing to say.\n")
    h.declare("idle", "---\nagents: |\n  s agents/s\nroot: s\n---\nNever started.\n")

    # --- the team plays: an ask to the owner, a returned post, the inbox seen, the reply, the end -------
    started = h.call("team", "start", "desk", "--message", "merge it", *h.harnessed)
    asked = h.settled("desk", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), 60)
    ask = next((one for one in by_kind(h.events("desk"), "post", verb="ask")), {})
    calls = [h.call("team", "start", "calm", "--message", "wait", "--no-tick"),
             h.call("team", "post", "desk", "--message", "later", "--no-tick"),
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

    # --- the inbox -------------------------------------------------------------------------------------
    question = {"id": ask.get("id"), "verb": "ask", "from": "m", "task": "T1", "text": "which PR?"}
    if (started.returncode == 0 and asked and all(one.returncode == 0 for one in calls) and done
            and box_1 == [{"team": "desk", "questions": [question], "done": [],
                           "returned": [{"id": returned_post.get("id"), "verb": "do", "from": "house", "task": "T2",
                                         "text": "later"}]}]
            and box_2 == [{"team": "desk", "questions": [question], "done": [], "returned": []}]
            and box_3 is not None and len(box_3) == 1 and box_3[0]["questions"] == [] and box_3[0]["returned"] == []
            and [one["task"] for one in box_3[0]["done"]] == ["T1"]
            and every_rc.returncode == 0 and [one["team"] for one in every or []] == ["desk"]
            and mixed.returncode == 2 and "usage" in mixed.stderr and mixed.stdout == ""):
        held("the inbox", f"the question #{ask.get('id')} with its text and the returned #{returned_post.get('id')}; "
             "after --seen the question alone; after the reply T1 done; without a name desk alone (calm waits for "
             "nothing); --seen --json: the usage")
    else:
        failures.append(f"  ✗ the inbox                   rc={started.returncode}/{[c.returncode for c in calls]} "
                        f"asked={asked} done={done} box1={box_1} box2={box_2} box3={box_3} every={every} "
                        f"mixed={mixed.returncode}:{mixed.stderr[-120:]!r} {[c.stderr[-150:] for c in calls if c.returncode]}")

    # --- the log ---------------------------------------------------------------------------------------
    snapped = h.call("team", "snapshot", "desk")
    events = [one for one in h.events("desk") if one.get("kind") != "snapshot"]
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

    # --- the responses ---------------------------------------------------------------------------------
    ends = by_kind(h.events("desk"), "wake-ended")
    record = T.lines(h.records / "responses.jsonl")
    all_rc, answers = faced("responses", "desk", "--json")
    first = ends[0]["id"] if ends else 0
    picks = {"since": (["--since", str(first)], None), "agent": (["--agent", "r1"], None),
             "task": (["--task", "T1", "--last", "1"], None)}
    for key, (args, _) in picks.items():
        picks[key] = (faced("responses", "desk", *args, "--json")[1], ids(h.call("team", "responses", "desk", *args)))
    unstarted = h.call("team", "responses", "idle", "--json")

    def kept(one: dict) -> str | None:
        return next((str(r.get("response") or "") for r in record if r.get("agent") == one.get("path")
                     and r.get("run") == one.get("run") and r.get("index") == one.get("index")), None)

    if (all_rc.returncode == 0 and answers is not None and [one["id"] for one in answers] == [e["id"] for e in ends]
            and len(answers) == 4 and all(one["response"] == kept(one) and one["response"] for one in answers)
            and all(set(one) == {"id", "member", "path", "task", "run", "index", "at", "cost_usd", "response"}
                    for one in answers)
            and [one["cost_usd"] for one in answers] == [e.get("cost") for e in ends]
            and [one["member"] for one in answers] == [e.get("agent") for e in ends]
            and all([one["id"] for one in (found or [])] == text and text for found, text in picks.values())
            and unstarted.returncode == 2 and "team-not-started" in unstarted.stderr):
        held("the responses", f"{len(answers)} objects, each text the record's, each cost the event's; --since #{first}, "
             "--agent r1, --task T1 --last 1 keep the text's ids; idle: team-not-started")
    else:
        failures.append(f"  ✗ the responses               rc={all_rc.returncode} answers={answers} "
                        f"ends={[e['id'] for e in ends]} picks={picks} idle={unstarted.returncode}:{unstarted.stderr[-120:]!r}")
    return 0
