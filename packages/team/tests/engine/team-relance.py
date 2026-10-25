"""Scenario `team-relance` -- 4 case(s): a member that owes an answer and has nothing to receive is woken again -- a
RELANCE --, a member at the bottom of a wait is never, two members waiting on each other are, and `launches:` bounds the
relances; four teams play side by side on one house.
- (a) a debtor put off: worker-2's wake-up delivers its `do` and worker-1's `ask`; it answers the ask alone and puts
  its `do` off; the tick relances it (`relance: "owed"`, its debt in `messages`, the head opening on the module's
  RELANCED), it answers, and T1 resolves -- no principal's note; the supervisor, under its wait, and worker-1,
  waiting for its ask, are never relanced
- (b) a question to a principal is a wait: a root asks its principal and puts the opening off -- no relance, however
  many ticks; the principal's answer wakes it, and it closes the task
- (a) a cycle of waits: two peers ask each other and put every answer off -- p1 waits for p2's answer, p2 for p1's;
  the tick relances p1 on T1 (`relance: "cycle"`, its debts -- r's `do` and p2's ask -- in `messages`, its head
  opening on a line naming p2 in RELANCED's place), p1 answers, the answers run, and T1 resolves
- (b) `launches:` bounds a debtor that never answers: relanced until the task's launches are spent, then `launches-spent`
  on T1 and the team's notice to the owner on T1 -- nobody woken after
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "team")

PAIR = ("---\nagents: |\n  c agents/c\n  d agents/d\nreports: |\n  d -> c\nroot: c\nschedule: off\nlaunches: 3\n---\n"
        "Delegate, then conclude.\n")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        # t8: worker-2 answers the ask and puts its do off
        "supervisor": [{"sleep": 0.1, "body": {"do": {"worker-1": "part A; ask worker-2 for B's API",
                                                      "worker-2": "part B"}}},
                       {"sleep": 0.1, "body": {"re": "DO", "text": "T8 closed"}}],
        "worker-1": [{"sleep": 0.1, "body": {"ask": {"to": "worker-2", "text": "what is B's API?"}}},
                     {"sleep": 0.1, "body": {"re": "DO", "text": "part A done"}}],
        "worker-2": [{"sleep": 0.1, "body": {"re": "ASK from worker-1", "text": "B is gRPC"}},
                     {"sleep": 0.1, "body": {"re": "DO", "text": "part B done"}}],
        # q: a root that asks its principal
        "asker": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which branch?"}}},
                  {"sleep": 0.1, "body": {"re": "DO", "text": "merged on main"}}],
        # pair: two peers that ask each other and put everything off
        "r": [{"sleep": 0.1, "body": {"do": ["p1", "p2"]}},
              {"sleep": 0.1, "body": {"re": "DO", "text": "both halves in"}}],
        "p1": [{"sleep": 0.1, "body": {"ask": {"to": "p2", "text": "your schema?"}}},
               {"sleep": 0.1, "body": []},
               {"sleep": 0.1, "body": {"re": "ASK from p2", "text": "mine is v1"}},
               {"sleep": 0.1, "body": {"re": "DO", "text": "p1 done"}}],
        "p2": [{"sleep": 0.1, "body": {"ask": {"to": "p1", "text": "your schema?"}}},
               {"sleep": 0.1, "body": [{"re": "ASK from p1", "text": "mine is v2"}, {"re": "DO", "text": "p2 done"}]}],
        # mute: d never answers
        "c": [{"sleep": 0.1, "body": {"do": ["d"]}}],
        "d": [{"sleep": 0.1, "body": []}] * 6})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of
    ended = lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found)
    relanced = h.module().RELANCED

    # --- the four teams declared and started side by side ----------------------------------------------
    h.declare("t8", "---\nagents: |\n  supervisor agents/supervisor\n  worker-1 agents/worker-1\n"
                    "  worker-2 agents/worker-2\nreports: |\n  worker-1 worker-2 -> supervisor\nroot: supervisor\n"
                    "parallel: 1\nschedule: off\n---\nSplit the work, ask each other, report.\n")
    h.declare("q", "---\nagents: |\n  asker agents/asker\nroot: asker\nschedule: off\n---\nAsk when in doubt.\n")
    h.declare("pair", "---\nagents: |\n  r agents/r\n  p1 agents/p1\n  p2 agents/p2\nreports: |\n  p1 p2 -> r\nroot: r\n"
                      "parallel: 1\nschedule: off\n---\nAgree on a schema, then build.\n")
    h.declare("mute", PAIR)
    t8 = h.call("team", "start", "t8", "--message", "build the two halves", *h.harnessed)
    q = h.call("team", "start", "q", "--message", "merge the fix", *h.harnessed)
    pair = h.call("team", "start", "pair", "--message", "build both halves", *h.harnessed)
    mute = h.call("team", "start", "mute", "--message", "say something", *h.harnessed)

    # --- (a) a debtor put off is relanced; those who wait are not ----------------------------------------
    done_a = h.settled("t8", ended, timeout=30)
    found = h.events("t8")
    to_w2 = next((one["id"] for one in by_kind(found, "post", verb="do", **{"from": "supervisor"})
                  if one.get("to") == "worker-2"), None)
    w2 = T.intents_of(found, "worker-2")
    relances = [one for one in by_kind(found, "wake-intent") if one.get("relance")]
    w2_prompts = h.prompts_of("worker-2")
    if (t8.returncode == 0 and done_a and result_of(found, "T1") == "T8 closed" and len(w2) == 2
            and [(one.get("agent"), one.get("relance"), one.get("messages")) for one in relances]
            == [("worker-2", "owed", [to_w2])]
            and len(w2_prompts) == 2 and relanced in w2_prompts[1] and relanced not in w2_prompts[0]
            and not by_kind(found, "post", verb="note")):
        held("(a) T8 put off, relanced", f"worker-2 answers the ask and puts #{to_w2} off; relanced "
             f"(relance owed, messages [{to_w2}]), it answers: T1 'T8 closed', no note; the supervisor and "
             "worker-1, waiting, never relanced")
    else:
        failures.append(f"  ✗ (a) T8 put off, relanced    rc={t8.returncode} done={done_a} result={result_of(found, 'T1')!r} "
                        f"w2={len(w2)} relances={[(one.get('agent'), one.get('relance'), one.get('messages')) for one in relances]} "
                        f"heads={[relanced in one for one in w2_prompts]}\n{t8.stderr[-300:]}")

    # --- (b) a question to a principal is a wait -----------------------------------------------------------
    asked = h.settled("q", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), timeout=30)
    ticks = [h.call("team", "tick", "q") for _ in range(3)]
    before = len(T.intents_of(h.events("q"), "asker"))
    question = next((one["id"] for one in by_kind(h.events("q"), "post", verb="ask")), None)
    replied = h.call("team", "post", "q", "--task", "T1", "--reply", str(question), "--message", "main")
    done_b = h.settled("q", ended, timeout=30)
    found = h.events("q")
    if (q.returncode == 0 and asked and all(one.returncode == 0 for one in ticks) and before == 1
            and replied.returncode == 0 and done_b and result_of(found, "T1") == "merged on main"
            and len(T.intents_of(found, "asker")) == 2
            and not [one for one in by_kind(found, "wake-intent") if one.get("relance")]):
        held("(b) a question to a principal is a wait", f"asker asks house (#{question}) and puts the opening off: "
             "1 wake-up through 3 ticks, no relance; the reply wakes it, T1 'merged on main'")
    else:
        failures.append(f"  ✗ (b) a question is a wait     rc={q.returncode}/{replied.returncode} asked={asked} before={before} "
                        f"done={done_b} result={result_of(found, 'T1')!r} intents={len(T.intents_of(found, 'asker'))} "
                        f"relances={[one.get('relance') for one in by_kind(found, 'wake-intent') if one.get('relance')]}"
                        f"\n{replied.stderr[-200:]}")

    # --- (a) a cycle of waits is relanced -----------------------------------------------------------------
    done_c = h.settled("pair", ended, timeout=40)
    found = h.events("pair")
    asked_p1 = next((one["id"] for one in T.asks_to(found, "p2", "p1")), None)
    do_p1 = next((one["id"] for one in T.delegated(found, "r") if one.get("to") == "p1"), None)
    relances = [(one.get("agent"), one.get("relance"), one.get("task"), sorted(one.get("messages") or []))
                for one in by_kind(found, "wake-intent") if one.get("relance")]
    p1 = h.prompts_of("p1")
    # the line that opens a wake-up's head after `[team <team> · you are <member>]`: a relance's reason, else the inbox
    opening = lambda prompt: next(iter(re.findall(r"^\[team \S+ · you are \S+\]\n+(.*)$", prompt, re.M)), "")
    names_p2 = lambda prompt: bool(re.search(r"^\[.*\bp2\b.*\]$", opening(prompt)))
    if (pair.returncode == 0 and done_c and result_of(found, "T1") == "both halves in"
            and relances == [("p1", "cycle", "T1", sorted([do_p1, asked_p1]))] and len(p1) >= 3
            and names_p2(p1[2]) and opening(p1[2]) != relanced and not names_p2(p1[0])
            and not by_kind(found, "post", verb="note")):
        held("(a) a cycle of waits, relanced", f"p1 and p2 ask each other and put everything off; p1 relanced "
             f"{relances} -- r's do #{do_p1} and p2's ask #{asked_p1} its debts --, its head opens on a line naming "
             "p2; T1 'both halves in'")
    else:
        failures.append(f"  ✗ (a) a cycle of waits        rc={pair.returncode} done={done_c} result={result_of(found, 'T1')!r} "
                        f"relances={relances} do={do_p1} ask={asked_p1} heads={[names_p2(one) for one in p1]}"
                        f"\n{pair.stderr[-300:]}")

    # --- (b) launches: bounds the relances ----------------------------------------------------------------------
    spent = h.settled("mute", lambda found: bool(by_kind(found, "launches-spent")) and all_ended(found), 30)
    ticks = [h.call("team", "tick", "mute") for _ in range(2)]
    found = h.events("mute")
    d = T.intents_of(found, "d")
    gone = by_kind(found, "launches-spent")
    told = [one for one in by_kind(found, "post", verb="notice") if one.get("to") == "house"]
    if (mute.returncode == 0 and spent and all(one.returncode == 0 for one in ticks)
            and [one.get("relance") for one in d] == [None, "owed"]
            and [(one.get("task"), one.get("spent"), one.get("launches")) for one in gone] == [("T1", 3, 3)]
            and [(one.get("from"), one.get("task"), one.get("about"), one["id"]) for one in told]
            == [("mute", "T1", None, gone[0]["id"] + 1)]
            and len(by_kind(found, "wake-intent")) == 3 and not by_kind(found, "done")):
        held("(b) launches: bounds the relances", "d never answers: relanced once, the third launch of T1; then "
             "launches-spent on T1 (3 of 3) and the team's notice to house on T1, nobody woken through 2 more ticks")
    else:
        failures.append(f"  ✗ (b) launches: bounds relances  rc={mute.returncode} spent={spent} "
                        f"d={[one.get('relance') for one in d]} intents={len(by_kind(found, 'wake-intent'))} "
                        f"gone={[(one.get('task'), one.get('spent'), one.get('launches')) for one in gone]} "
                        f"told={[(one.get('from'), one.get('task'), one.get('about'), one['id']) for one in told]}")
    return 0
