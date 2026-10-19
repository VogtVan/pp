"""Scenario `team-answers` -- 4 case(s): an answer is a list of `do`, `ask` and `{"re": <id>}`; each `do` or
`ask` delivered to a member opens one debt, settled by its first answer. Four teams run side by side in one
house, each under its own names; each case waits for its team, then reads its journal.
- (a) T8 crossed under `parallel: 1`: worker-2's wake-up delivers its `do` AND worker-1's `ask`; it answers
  a list -- its own `ask` to worker-1 and the answer to worker-1's ask --, then answers its `do` at its next
  wake-up; the supervisor answers the task's opening and T1 resolves, no principal's note
- (b) a second answer to the same message: posted `info`, it settles nothing -- the lead stays held until
  the other delegate answers, and is woken once for the two answers
- (e) the root decides: a delegate's answer to its `do` never resolves the task; the root's answer to the
  opening does, its text the result; an `ask` posted by a wake-up ending after the close opens no debt --
  the next wake-up of the member it was posted to, on another task, owes nothing but that task's opening
- (a) two members ask each other: `help-1 help-2 -> chief`; chief delegates T1 to both; each asks the
  other, each answers the ask it received, then each answers its `do`; chief closes T1 -- no `wake-failed`,
  each ask posted between the two helpers, each answer citing the ask it answers
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "team")


def owed_ids(prompt: str, owed: str) -> set[int]:
    """-> the ids of the messages a head marks as owed (`#<id> ... -- <owed>`), wherever the head lists them."""
    return {int(one.group(1)) for one in re.finditer(rf"^#(\d+) [A-Z]+\b.* -- {re.escape(owed)}", prompt, re.M)}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        # (a) T8: the supervisor delegates two halves that need each other
        "supervisor": [{"sleep": 0.1, "body": {"do": {"worker-1": "part A; ask worker-2 for B's API",
                                                      "worker-2": "part B; ask worker-1 for A's API"}}},
                       {"sleep": 0.1, "body": {"re": "DO", "text": "T8 closed"}}],
        "worker-1": [{"sleep": 0.1, "body": {"ask": {"to": "worker-2", "text": "what is B's API?"}}},
                     {"sleep": 0.1, "body": [{"re": "ASK from worker-2", "text": "A is REST"},
                                             {"re": "DO", "text": "part A done"}]}],
        "worker-2": [{"sleep": 0.1, "body": [{"ask": {"to": "worker-1", "text": "what is A's API?"}},
                                             {"re": "ASK from worker-1", "text": "B is gRPC"}]},
                     {"sleep": 0.1, "body": {"re": "DO", "text": "part B done"}}],
        # (b) a1 answers its do twice in one answer; a2 answers late
        "lead": [{"sleep": 0.1, "body": {"do": ["a1", "a2"]}},
                 {"sleep": 0.1, "body": {"re": "DO", "text": "both in"}}],
        "a1": [{"sleep": 0.1, "body": [{"re": "DO", "text": "first"}, {"re": "DO", "text": "and more"}]}],
        "a2": [{"sleep": 1.5, "body": {"re": "DO", "text": "late"}}],
        # (e) the root decides; a slow delegate asks after the close
        "boss": {"T1": [{"sleep": 0.1, "body": {"do": ["fast", "slow"], "await": {"any": 1}}},
                        {"sleep": 0.1, "body": {"re": "DO", "text": "boss closes"}}]},
        "fast": {"T1": [{"sleep": 0.1, "body": {"re": "DO", "text": "fast done"}}],
                 "T2": [{"sleep": 0.1, "body": {"re": "DO", "text": "T2 done"}}]},
        "slow": {"T1": [{"sleep": 3.0, "body": {"ask": {"to": "fast", "text": "too late?"}}}]},
        # (a) two helpers ask each other, answer, then close
        "chief": [{"sleep": 0.1, "body": {"do": ["help-1", "help-2"]}},
                  {"sleep": 0.1, "body": {"done": "T19 closed"}}],
        "help-1": [{"sleep": 0.2, "body": {"ask": {"to": "help-2", "text": "which half is yours?"}}},
                   {"sleep": 0.1, "body": {"reply": {"to": "help-2", "text": "the tests"}}},
                   {"sleep": 0.1, "body": {"done": "help-1 done"}}],
        "help-2": [{"sleep": 0.4, "body": {"ask": {"to": "help-1", "text": "and yours?"}}},
                   {"sleep": 0.1, "body": {"reply": {"to": "help-1", "text": "the code"}}},
                   {"sleep": 0.1, "body": {"done": "help-2 done"}}]})
    by_kind, all_ended, result_of, asks_to = T.by_kind, T.all_ended, T.result_of, T.asks_to
    ended = lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found)
    owed_mark = h.module().OWED

    # --- every team declared and started before the first wait: they run side by side ----------------------
    h.declare("t8", "---\nagents: |\n  supervisor agents/supervisor\n  worker-1 agents/worker-1\n"
                    "  worker-2 agents/worker-2\nreports: |\n  worker-1 worker-2 -> supervisor\nroot: supervisor\n"
                    "parallel: 1\nschedule: off\n---\nSplit the work, ask each other, report.\n")
    h.declare("twice", "---\nagents: |\n  lead agents/lead\n  a1 agents/a1\n  a2 agents/a2\nreports: |\n"
                       "  a1 a2 -> lead\nroot: lead\nschedule: off\n---\nDelegate and gather.\n")
    h.declare("root", "---\nagents: |\n  boss agents/boss\n  fast agents/fast\n  slow agents/slow\nreports: |\n"
                      "  fast slow -> boss\nroot: boss\nschedule: off\n---\nThe boss closes.\n")
    h.declare("pair", "---\nagents: |\n  chief agents/chief\n  help-1 agents/aide\n  help-2 agents/aide\nreports: |\n"
                      "  help-1 help-2 -> chief\nroot: chief\nschedule: off\n---\nSplit the work and agree.\n")
    t8 = h.call("team", "start", "t8", "--message", "build the two halves", *h.harnessed)
    twice = h.call("team", "start", "twice", "--message", "gather two answers", *h.harnessed)
    rooted = h.call("team", "start", "root", "--message", "close it", *h.harnessed)
    pair = h.call("team", "start", "pair", "--message", "T19: split the change", *h.harnessed)

    # --- (a) several messages, one answer each -----------------------------------------------------------
    done_a = h.settled("t8", ended, timeout=90)
    found = h.events("t8")
    dos = {one["to"]: one["id"] for one in by_kind(found, "post", verb="do", **{"from": "supervisor"})}
    ask12 = asks_to(found, "worker-1", "worker-2")
    ask21 = asks_to(found, "worker-2", "worker-1")
    w2 = T.intents_of(found, "worker-2")
    first_w2 = w2[0]["messages"] if w2 else []
    w2_tag = w2[0]["tag"] if w2 else None
    w2_end = next((one["id"] for one in by_kind(found, "wake-ended", tag=w2_tag)), None)
    answers = by_kind(found, "post", verb="re")
    after_w2 = [(one.get("from"), one.get("re")) for one in found
                if one.get("kind") == "post" and w2_end is not None and w2_end < one["id"]
                and one["id"] <= w2_end + 2]
    w2_do_answer = [one for one in answers if one.get("from") == "worker-2" and one.get("re") == dos.get("worker-2")]
    opening = next((one["id"] for one in by_kind(found, "post", verb="do", **{"from": "house"})), None)
    notes = by_kind(found, "post", verb="note")
    if (t8.returncode == 0 and done_a and ask12 and ask21 and sorted(first_w2) == sorted([dos.get("worker-2"), ask12[0]["id"]])
            and after_w2 == [("worker-2", None), ("worker-2", ask12[0]["id"])]
            and len(w2) == 2 and len(w2_do_answer) == 1 and w2_do_answer[0]["id"] > w2_end
            and any(one.get("from") == "supervisor" and one.get("re") == opening for one in answers)
            and result_of(found, "T1") == "T8 closed" and not notes and not by_kind(found, "wake-failed")):
        held("(a) T8, one answer per message", f"worker-2's first wake-up delivers #{dos['worker-2']} DO and "
             f"#{ask12[0]['id']} ASK: it answers its own ask and the answer to #{ask12[0]['id']} in one list, then "
             f"#{dos['worker-2']} at its next wake-up; the supervisor answers the opening #{opening}: T1 closed, "
             "no note, no failure")
    else:
        failures.append(f"  ✗ (a) T8, one answer per message  rc={t8.returncode} done={done_a} dos={dos} "
                        f"asks={[one['id'] for one in ask12]}/{[one['id'] for one in ask21]} first_w2={first_w2} "
                        f"after_w2={after_w2} w2={len(w2)} answers={[(one.get('from'), one.get('re')) for one in answers]} "
                        f"result={result_of(found, 'T1')!r} fails={[one.get('reason') for one in by_kind(found, 'wake-failed')]}"
                        f"\n{t8.stderr[-300:]}")

    # --- (b) a debt settled once: the second answer is information -----------------------------------------
    done_b = h.settled("twice", ended, timeout=60)
    found = h.events("twice")
    to_a1 = next((one["id"] for one in by_kind(found, "post", verb="do", **{"from": "lead", "to": "a1"})), None)
    a1_answers = [(one.get("re"), bool(one.get("info"))) for one in by_kind(found, "post", verb="re", **{"from": "a1"})]
    a2_answer = next((one["id"] for one in by_kind(found, "post", verb="re", **{"from": "a2"})), 10 ** 9)
    lead_wakes = T.intents_of(found, "lead")
    if (twice.returncode == 0 and done_b and a1_answers == [(to_a1, False), (to_a1, True)]
            and len(lead_wakes) == 2 and lead_wakes[1]["id"] > a2_answer
            and result_of(found, "T1") == "both in"):
        held("(b) a debt settled once", f"a1 answers #{to_a1} twice in one answer: the first settles it, the "
             "second is posted info; lead stays held until a2 answers, woken once for both")
    else:
        failures.append(f"  ✗ (b) a debt settled once         rc={twice.returncode} done={done_b} a1={a1_answers} "
                        f"lead={[one['id'] for one in lead_wakes]} a2={a2_answer} result={result_of(found, 'T1')!r}")

    # --- (e) the root decides; nothing owed after the close ------------------------------------------------------
    closed = h.settled("root", ended, timeout=60)
    found = h.events("root")
    fast_answer = next((one["id"] for one in by_kind(found, "post", verb="re", **{"from": "fast"})), None)
    done_e = next((one["id"] for one in by_kind(found, "done", task="T1")), None)
    late = asks_to(found, "slow", "fast")
    posted = h.call("team", "post", "root", "--to", "fast", "--message", "now this")
    done_t2 = h.settled("root", lambda found: bool(by_kind(found, "done", task="T2")) and all_ended(found), timeout=60)
    found_t2 = h.events("root")
    opening_t2 = next((one["id"] for one in by_kind(found_t2, "post", verb="do", task="T2", to="fast")), None)
    prompts = h.prompts_of("fast")
    owed_t2 = owed_ids(prompts[-1], owed_mark) if prompts else {"?"}
    boss_answer = [one for one in by_kind(found_t2, "post", verb="re", **{"from": "boss"})]
    if (rooted.returncode == 0 and closed and fast_answer is not None and done_e is not None
            and boss_answer and boss_answer[0]["id"] < done_e and fast_answer < boss_answer[0]["id"]
            and result_of(found, "T1") == "boss closes" and late and late[0]["id"] > done_e
            and posted.returncode == 0 and done_t2 and len(prompts) == 2 and opening_t2 is not None
            and owed_t2 == {opening_t2} and f"#{late[0]['id']}" not in prompts[-1]):
        held("(e) the root decides", f"fast answers its do (#{fast_answer}), T1 stays open; boss answers the opening "
             f"(#{boss_answer[0]['id']}): done T1 'boss closes'; slow's ask #{late[0]['id']} posted after the close "
             f"opens no debt -- fast's next wake-up, on T2, owes #{opening_t2} alone")
    else:
        failures.append(f"  ✗ (e) the root decides           rc={rooted.returncode}/{posted.returncode} closed={closed} "
                        f"fast={fast_answer} boss={[one['id'] for one in boss_answer]} done={done_e} "
                        f"late={[one['id'] for one in late]} t2={done_t2} prompts={len(prompts)} "
                        f"owed={sorted(owed_t2, key=str)} opening_t2={opening_t2} result={result_of(found, 'T1')!r}")

    # --- (a) two helpers ask each other, answer, then close ---------------------------------------------
    done_p = h.settled("pair", ended, timeout=90)
    found = h.events("pair")
    fails = [(one.get("agent"), str(one.get("reason"))) for one in by_kind(found, "wake-failed")]
    ask_12, ask_21 = asks_to(found, "help-1", "help-2"), asks_to(found, "help-2", "help-1")
    asked = {one["id"] for one in ask_12 + ask_21}
    replies = [(one.get("from"), one.get("to"), one.get("re")) for one in by_kind(found, "post", verb="re")
               if one.get("re") in asked]
    owed = {("help-1", "help-2", ask_21[0]["id"] if ask_21 else None),
            ("help-2", "help-1", ask_12[0]["id"] if ask_12 else None)}
    if (pair.returncode == 0 and done_p and fails == [] and len(ask_12) == 1 and len(ask_21) == 1
            and set(replies) == owed and len(replies) == 2
            and len(T.closings(found, "help-1")) == 1 and len(T.closings(found, "help-2")) == 1
            and result_of(found, "T1") == "T19 closed"):
        held("(a) two members ask each other", f"help-1 asks help-2 (#{ask_12[0]['id']}), help-2 asks help-1 "
             f"(#{ask_21[0]['id']}), each answers the ask it received (re), each answers its do; T1 closed by chief, "
             "no wake-failed")
    else:
        failures.append(f"  ✗ (a) two members ask each other  rc={pair.returncode} done={done_p} fails={fails} "
                        f"asks={len(ask_12)}/{len(ask_21)} replies={replies} owed={sorted(owed, key=str)} "
                        f"result={result_of(found, 'T1')!r}")
    return 0
