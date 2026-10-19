"""Scenario `team-answers-refused` -- 6 case(s): the answers the tick refuses to route, and the failures it
answers in the member's place; every team is declared and started at once, then each is read in turn.
- (c) a `re` citing a message never delivered to the member: a `wake-failed response-unreadable`, not final, no
  answer posted on that id; the retry answers the opening
- (d) an old verb (`done`): a `wake-failed response-unreadable`, not final, no post of that verb; the retry
  answers the opening
- a prose answer is a dead wake-up: `wake-failed response-unreadable`, retried `retries` times (1, then 0 on a
  second team), then `final` and the team's notice about the root to the owner -- its opening never answered in
  its place
- (f) a final failure answers in place: a worker failing past `retries:` gets the tick's answer to its `do`
  (`by: tick`), which wakes its lead; a root failing past `retries:` never gets its opening answered -- the task
  stays open and its principal gets the team's notice about it
- (b) an ask to a name nobody declared: a `wake-failed response-unreadable`, not final, no ask posted; the retry
  answers the opening
- (h) a `do` off the edges (`eg1 eg2 -> eg`, eg1 delegates to eg2): a `wake-failed response-unreadable`, not
  final, no delegation from eg1; then eg1's `ask` to eg2 is ROUTED, eg2 woken once by it, its answer cites the
  ask; eg closes T1
"""
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor

from tests.harness import support

T = support(__file__, "team")

UNREADABLE = "response-unreadable"


def code_of(reason) -> str:
    """-> the CODE of a `wake-failed` reason: what precedes its explanation (`<code>: <why>`)."""
    return str(reason).split(":", 1)[0]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        # (c) a re to a message never delivered, then the answer
        "x1": [{"sleep": 0.1, "body": {"re": 9999, "text": "?"}},
               {"sleep": 0.1, "body": {"re": "DO", "text": "fine"}}],
        # (d) an old verb, written as such, then the answer
        "x2": [{"sleep": 0.1, "body": [{"done": "old"}]},
               {"sleep": 0.1, "body": {"re": "DO", "text": "new"}}],
        # a prose answer, retries 1 then 0
        "q": [{"sleep": 0.1, "body": "prose"}, {"sleep": 0.1, "body": "prose"}],
        "q0": [{"sleep": 0.1, "body": "prose"}, {"sleep": 0.1, "body": "prose"}],
        # (f) a worker that dies, a root that dies
        "keeper": [{"sleep": 0.1, "body": {"do": ["dier"]}},
                   {"sleep": 0.1, "body": {"re": "DO", "text": "salvaged"}}],
        "dier": [{"sleep": 0.1, "body": "crash"}, {"sleep": 0.1, "body": "crash"}],
        "fragile": [{"sleep": 0.1, "body": "crash"}, {"sleep": 0.1, "body": "crash"}],
        # (b) an ask to a name nobody declared, then the answer
        "x3": [{"sleep": 0.1, "body": {"ask": {"to": "zz", "text": "anyone?"}}},
               {"sleep": 0.1, "body": {"done": "alone"}}],
        # (h) a do off the edges, then an ask to any member
        "eg": [{"sleep": 0.1, "body": {"do": ["eg1"]}},
               {"sleep": 0.1, "body": {"done": "edges held"}}],
        "eg1": [{"sleep": 0.1, "body": {"do": ["eg2"]}},
                {"sleep": 0.1, "body": {"ask": {"to": "eg2", "text": "and you?"}}},
                {"sleep": 0.1, "body": {"done": True}}],
        "eg2": [{"sleep": 0.1, "body": {"reply": {"to": "eg1", "text": "mine is fine"}}}]})
    by_kind, all_ended, asks_to, result_of = T.by_kind, T.all_ended, T.asks_to, T.result_of
    ended = lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found)
    final_failed = lambda found: any(one.get("final") for one in by_kind(found, "wake-failed")) and all_ended(found)

    # --- every team declared and started before the first wait ------------------------------------------------
    h.declare("never", "---\nagents: |\n  x1 agents/x1\nroot: x1\nretries: 1\nschedule: off\n---\nAnswer.\n")
    h.declare("verbs", "---\nagents: |\n  x2 agents/x2\nroot: x2\nretries: 1\nschedule: off\n---\nAnswer.\n")
    h.declare("prosy", "---\nagents: |\n  q q\nroot: q\nretries: 1\n---\nAnswer in JSON.\n")
    h.declare("prosy0", "---\nagents: |\n  q0 q0\nroot: q0\nretries: 0\n---\nAnswer in JSON.\n")
    h.declare("dies", "---\nagents: |\n  keeper agents/keeper\n  dier agents/dier\nreports: |\n  dier -> keeper\n"
                      "root: keeper\nretries: 1\nschedule: off\n---\nThe worker may die.\n")
    h.declare("frail", "---\nagents: |\n  fragile agents/fragile\nroot: fragile\nretries: 1\nschedule: off\n---\n"
                       "The root may die.\n")
    h.declare("alone", "---\nagents: |\n  x3 agents/x3\nroot: x3\nretries: 1\nschedule: off\n---\nWork alone.\n")
    h.declare("edges", "---\nagents: |\n  eg eg\n  eg1 eg1\n  eg2 eg2\nreports: |\n  eg1 eg2 -> eg\n"
                       "root: eg\nretries: 2\nschedule: off\n---\nDelegate along the edges.\n")
    openings = {"edges": "review PR 12", "dies": "try it", "frail": "try it", "alone": "do it",   # the longest
                "never": "answer me", "verbs": "answer me", "prosy": "say something", "prosy0": "say something"}
    with ThreadPoolExecutor(max_workers=len(openings)) as pool:     # chain first, every start at once
        calls = {name: pool.submit(h.call, "team", "start", name, "--message", text, *h.harnessed)
                 for name, text in openings.items()}
    started = {name: one.result() for name, one in calls.items()}

    # --- one wait for all: the dead wake-ups fire no on-end, their teams are ticked ----------------------------
    awaited = {"never": ended, "verbs": ended, "prosy": final_failed, "prosy0": final_failed,
               "dies": ended, "frail": final_failed, "alone": ended, "edges": ended}
    ticked = {"dies", "frail"}
    reached: dict[str, bool] = {name: False for name in awaited}
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        for name, predicate in awaited.items():
            reached[name] = reached[name] or predicate(h.events(name))
        if all(reached.values()):
            break
        for name in sorted(ticked):
            if not reached[name]:
                h.call("team", "tick", name)
        time.sleep(0.3)
    time.sleep(0.5)                                     # the last on-end tick writes after the response

    # --- (c) a re to a message never delivered ------------------------------------------------------------------
    never, done_c = started["never"], reached["never"]
    found = h.events("never")
    fails_c = [(one.get("final"), code_of(one.get("reason"))) for one in by_kind(found, "wake-failed")]
    cited_c = [one for one in by_kind(found, "post", verb="re") if one.get("re") == 9999]
    if (never.returncode == 0 and done_c and fails_c == [(False, UNREADABLE)] and not cited_c
            and result_of(found, "T1") == "fine"):
        held("(c) a re to a message never delivered", f"{fails_c[0][1]}, not final, no re posted on #9999, retried; "
             "the retry answers the opening")
    else:
        failures.append(f"  ✗ (c) a re never delivered       rc={never.returncode} done={done_c} fails={fails_c} "
                        f"cited={cited_c} result={result_of(found, 'T1')!r}")

    # --- (d) an old verb ------------------------------------------------------------------------------------------
    verbs, done_d = started["verbs"], reached["verbs"]
    found = h.events("verbs")
    fails_d = [(one.get("final"), code_of(one.get("reason"))) for one in by_kind(found, "wake-failed")]
    if (verbs.returncode == 0 and done_d and fails_d == [(False, UNREADABLE)]
            and not by_kind(found, "post", verb="done") and result_of(found, "T1") == "new"):
        held("(d) an old verb", f"{fails_d[0][1]}, not final, no done posted, retried; the retry answers the opening")
    else:
        failures.append(f"  ✗ (d) an old verb                rc={verbs.returncode} done={done_d} fails={fails_d} "
                        f"done_posts={by_kind(found, 'post', verb='done')} result={result_of(found, 'T1')!r}")

    # --- a prose answer is a dead wake-up: retried `retries` times, then final ----------------------
    prosy, prosy0 = started["prosy"], started["prosy0"]
    final_p, final_p0 = reached["prosy"], reached["prosy0"]
    found_p = h.events("prosy")
    found_p0 = h.events("prosy0")
    fails_p = [(one.get("final"), one.get("reason")) for one in by_kind(found_p, "wake-failed")]
    fails_p0 = [(one.get("final"), one.get("reason")) for one in by_kind(found_p0, "wake-failed")]
    tail_p = [(one.get("kind"), one.get("verb"), one.get("to")) for one in found_p[-3:]]
    if (prosy.returncode == 0 and prosy0.returncode == 0 and final_p and final_p0
            and fails_p == [(False, UNREADABLE), (True, UNREADABLE)]
            and fails_p0 == [(True, UNREADABLE)]
            and ("post", "notice", "house") in tail_p and not by_kind(found_p, "post", verb="re")):
        held("a prose answer is a dead wake-up", "retries 1: response-unreadable, then final + the notice about q -> house, "
             "its opening never answered in its place; retries 0: final at the first")
    else:
        failures.append(f"  ✗ prose                       {prosy.returncode}/{prosy0.returncode} {final_p}/{final_p0} "
                        f"{fails_p} {fails_p0} {tail_p} {prosy.stderr[-200:]!r}")

    # --- (f) a final failure answers in place, never the opening ---------------------------------------------
    dies, fragile = started["dies"], started["frail"]
    found = h.events("dies")
    to_dier = next((one["id"] for one in by_kind(found, "post", verb="do", **{"from": "keeper"})), None)
    in_place = by_kind(found, "post", verb="re", **{"from": "dier"})
    finals = [one for one in by_kind(found, "wake-failed", agent="dier") if one.get("final")]
    found_r = h.events("frail")
    opening_r = next((one["id"] for one in by_kind(found_r, "post", verb="do")), None)
    told = T.notices_about(found_r, "fragile")
    if (dies.returncode == 0 and len(finals) == 1 and len(in_place) == 1 and in_place[0].get("re") == to_dier
            and in_place[0].get("to") == "keeper" and in_place[0].get("by") == "tick"
            and not by_kind(found, "post", verb="notice") and result_of(found, "T1") == "salvaged"
            and fragile.returncode == 0 and not by_kind(found_r, "post", verb="re") and not by_kind(found_r, "done")
            and len(told) == 1 and told[0].get("to") == "house" and opening_r is not None):
        held("(f) a final failure answers in place", f"dier dies twice: the tick answers its do #{to_dier} in its place "
             f"({in_place[0]['text']!r}), keeper woken answers the opening: 'salvaged'; fragile, the root, dies twice: "
             f"its opening #{opening_r} never answered, T1 open, the team's notice to house")
    else:
        failures.append(f"  ✗ (f) a final failure in place   rc={dies.returncode}/{fragile.returncode} finals={len(finals)} "
                        f"in_place={[(one.get('re'), one.get('to'), one.get('by')) for one in in_place]} do={to_dier} "
                        f"notices={[(one.get('from'), one.get('to')) for one in by_kind(found, 'post', verb='notice')]} "
                        f"result={result_of(found, 'T1')!r} root_re={len(by_kind(found_r, 'post', verb='re'))} "
                        f"root_done={len(by_kind(found_r, 'done'))} told={[one.get('to') for one in told]} "
                        f"journal={[T.shape(one) + ((one.get('reason'), one.get('final')) if one.get('kind') == 'wake-failed' else ()) for one in found_r]}")

    # --- (b) an ask to a name nobody declared stays unreadable ---------------------------------
    alone, done_b = started["alone"], reached["alone"]
    found_b = h.events("alone")
    fails_b = [(one.get("final"), code_of(one.get("reason"))) for one in by_kind(found_b, "wake-failed", agent="x3")]
    if (alone.returncode == 0 and done_b and fails_b == [(False, UNREADABLE)]
            and not by_kind(found_b, "post", verb="ask") and not by_kind(found_b, "post", to="zz")
            and result_of(found_b, "T1") == "alone"):
        held("(b) an ask to nobody", f"x3's ask to zz: {fails_b[0][1]}, not final, no ask posted, retried; "
             "the retry answers done")
    else:
        failures.append(f"  ✗ (b) an ask to nobody            rc={alone.returncode} done={done_b} fails={fails_b} "
                        f"asks={by_kind(found_b, 'post', verb='ask')} result={result_of(found_b, 'T1')!r}")

    # --- (h) the edges applied, an ask to any member ---------------------------------------------------------
    edges, done_eg = started["edges"], reached["edges"]
    found_e = h.events("edges")
    fails_e = [(one.get("final"), code_of(one.get("reason"))) for one in by_kind(found_e, "wake-failed", agent="eg1")]
    asked_e = asks_to(found_e, "eg1", "eg2")
    replies_e = [(one.get("from"), one.get("to"), one.get("re")) for one in by_kind(found_e, "post", verb="re")
                 if one.get("from") == "eg2"]
    if (edges.returncode == 0 and done_eg and fails_e == [(False, UNREADABLE)]
            and not T.delegated(found_e, frm="eg1")
            and len(asked_e) == 1 and len(by_kind(found_e, "wake-intent", agent="eg2")) == 1
            and replies_e == [("eg2", "eg1", asked_e[0]["id"])]
            and result_of(found_e, "T1") == "edges held"):
        held("(h) the edges applied, an ask to any member", "eg1's do to eg2 -- off the edges, eg2 reports to eg: "
             f"response-unreadable, no delegation from eg1, retried; its ask to eg2 (#{asked_e[0]['id']}) routed, "
             "eg2 woken once, its answer cites the ask; T1 done")
    else:
        failures.append(f"  ✗ (h) the edges and the asks    rc={edges.returncode} done={done_eg} fails={fails_e} "
                        f"delegated={T.delegated(found_e, frm='eg1')} asks={[one['id'] for one in asked_e]} "
                        f"replies={replies_e} eg2={len(by_kind(found_e, 'wake-intent', agent='eg2'))} "
                        f"result={result_of(found_e, 'T1')!r}")
    return 0
