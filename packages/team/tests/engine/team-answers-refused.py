"""Scenario `team-answers-refused` -- 6 case(s): the acts the tick refuses at the routing (their form right,
their sense wrong: `wake-refused`, a note to the member, the launch goes on), the `words` that are no act
(said: nothing written, nothing fails), and the failures it answers in the member's place; every team is
declared and started at once, then each is read in turn.
- (c) a `re` citing a message never delivered to the member: `wake-refused`, no answer posted on that id, a
  note to the member -- which launches it again: it answers the opening; no `wake-failed`
- (d) a `words` of another form (the old verb `done`) is SAID: nothing written of it, no failure; the act said
  after it in the same launch answers the opening
- a prose is said: no failure, the launch ends `wake-ended` and the run parks; the opening stays owed and the
  member is RELANCED on it (R12: a debt is due until its answer), answering at its third launch -- no notice,
  on two teams, `retries` 1 and 0 alike
- (f) a final failure answers in place: a worker dying past `retries:` gets the tick's answer to its `do`
  (`by: tick`), which launches its lead; a root dying past `retries:` never gets its opening answered -- the task
  stays open and its principal gets the team's notice about it
- (b) an ask to a name nobody declared: `wake-refused`, no ask posted, a note to the member; launched again by
  the note, it answers the opening
- (h) a `do` off the edges (`eg1 eg2 -> eg`, eg1 delegates to eg2): `wake-refused`, no delegation from eg1, a
  note; launched again by it, eg1's `ask` to eg2 is ROUTED, eg2 launched once by it, its answer cites the ask;
  eg closes T1
"""
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor

from tests.harness import support

T = support(__file__, "team")


def refusals_of(found: list[dict], agent: str) -> list[str]:
    """-> the reasons the tick refused the member's acts with, in order."""
    return [str(one.get("why")) for one in found if one.get("kind") == "wake-refused" and one.get("agent") == agent]


def notes_to(found: list[dict], agent: str) -> list[dict]:
    """-> the notes the team posted to the member (an act refused, said to it)."""
    return [one for one in found if one.get("kind") == "post" and one.get("verb") == "note" and one.get("to") == agent]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        # (c) a re to a message never delivered, then the answer
        "x1": [{"sleep": 0.1, "body": {"re": 9999, "text": "?"}},
               {"sleep": 0.1, "body": {"re": "DO", "text": "fine"}}],
        # (d) an old verb, written as such -- said --, then the answer in the same launch
        "x2": [{"sleep": 0.1, "words": [[{"done": "old"}], {"re": "DO", "text": "new"}]}],
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
    said_once = lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found)

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
    awaited = {"never": ended, "verbs": ended, "prosy": said_once, "prosy0": said_once,   # the prose teams: three launches
               "dies": ended, "frail": final_failed, "alone": ended, "edges": ended}
    ticked = {"dies", "frail"}
    reached: dict[str, bool] = {name: False for name in awaited}
    deadline = time.monotonic() + 90
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
    refused_c, notes_c = refusals_of(found, "x1"), notes_to(found, "x1")
    cited_c = [one for one in by_kind(found, "post", verb="re") if one.get("re") == 9999]
    if (never.returncode == 0 and done_c and len(refused_c) == 1 and "9999" in refused_c[0] and not cited_c
            and len(notes_c) == 1 and not by_kind(found, "wake-failed")
            and len(by_kind(found, "wake-intent", agent="x1")) == 2 and result_of(found, "T1") == "fine"):
        held("(c) a re to a message never delivered", f"wake-refused ({refused_c[0][:40]}…), no re posted on #9999, "
             "a note to x1, no failure; launched again by the note, x1 answers the opening")
    else:
        failures.append(f"  ✗ (c) a re never delivered       rc={never.returncode} done={done_c} refused={refused_c} "
                        f"notes={len(notes_c)} cited={cited_c} fails={by_kind(found, 'wake-failed')} "
                        f"intents={len(by_kind(found, 'wake-intent', agent='x1'))} result={result_of(found, 'T1')!r}")

    # --- (d) an old verb ------------------------------------------------------------------------------------------
    verbs, done_d = started["verbs"], reached["verbs"]
    found = h.events("verbs")
    routed_d = [one.get("words") for one in by_kind(found, "wake-routed", agent="x2")]
    if (verbs.returncode == 0 and done_d and not by_kind(found, "wake-failed") and not by_kind(found, "wake-refused")
            and not by_kind(found, "post", verb="done") and routed_d == [2]
            and len(by_kind(found, "wake-intent", agent="x2")) == 1 and result_of(found, "T1") == "new"):
        held("(d) an old verb is said", "a words of another form: nothing written, no failure, no refusal; the act said "
             "after it in the same launch (words 2) answers the opening")
    else:
        failures.append(f"  ✗ (d) an old verb                rc={verbs.returncode} done={done_d} routed={routed_d} "
                        f"fails={by_kind(found, 'wake-failed')} refused={by_kind(found, 'wake-refused')} "
                        f"done_posts={by_kind(found, 'post', verb='done')} result={result_of(found, 'T1')!r}")

    # --- a prose answer is a dead wake-up: retried `retries` times, then final ----------------------
    prosy, prosy0 = started["prosy"], started["prosy0"]
    said_p, said_p0 = reached["prosy"], reached["prosy0"]
    found_p = h.events("prosy")
    found_p0 = h.events("prosy0")
    ends_p = [(one.get("state"), one.get("launch")) for one in by_kind(found_p, "wake-ended", agent="q")]
    ends_p0 = [(one.get("state"), one.get("launch")) for one in by_kind(found_p0, "wake-ended", agent="q0")]
    relanced_p = [one.get("relance") for one in by_kind(found_p, "wake-intent", agent="q")]
    relanced_p0 = [one.get("relance") for one in by_kind(found_p0, "wake-intent", agent="q0")]
    routed_p = [(one.get("launch"), one.get("words")) for one in by_kind(found_p, "wake-routed")]
    if (prosy.returncode == 0 and prosy0.returncode == 0 and said_p and said_p0
            and ends_p == [("parked", 1), ("parked", 2), ("parked", 3)] and ends_p0 == [("parked", 1), ("parked", 2), ("parked", 3)]
            and relanced_p == [None, "owed", "owed"] and relanced_p0 == [None, "owed", "owed"]
            and not by_kind(found_p, "wake-failed") and not by_kind(found_p0, "wake-failed")
            and routed_p == [(3, 1)] and not by_kind(found_p, "post", verb="notice")
            and not by_kind(found_p, "wake-refused") and len({one.get("run") for one in by_kind(found_p, "wake-launched")}) == 1):
        held("a prose is said", "retries 1 and 0 alike: two launches of prose end wake-ended parked, no act routed, "
             "no failure, no refusal, no notice; the opening stays owed and q is relanced on it twice, in its one "
             "run, and answers at its third launch")
    else:
        failures.append(f"  ✗ prose                       {prosy.returncode}/{prosy0.returncode} {said_p}/{said_p0} "
                        f"ends={ends_p}/{ends_p0} relanced={relanced_p}/{relanced_p0} fails={by_kind(found_p, 'wake-failed')} "
                        f"routed={routed_p} notices={by_kind(found_p, 'post', verb='notice')} "
                        f"refused={by_kind(found_p, 'wake-refused')} {prosy.stderr[-200:]!r}")

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
    refused_b, notes_b = refusals_of(found_b, "x3"), notes_to(found_b, "x3")
    if (alone.returncode == 0 and done_b and len(refused_b) == 1 and "zz" in refused_b[0] and len(notes_b) == 1
            and not by_kind(found_b, "wake-failed")
            and not by_kind(found_b, "post", verb="ask") and not by_kind(found_b, "post", to="zz")
            and result_of(found_b, "T1") == "alone"):
        held("(b) an ask to nobody", f"x3's ask to zz: wake-refused, no ask posted, a note to x3, no failure; "
             "launched again by the note, x3 answers done")
    else:
        failures.append(f"  ✗ (b) an ask to nobody            rc={alone.returncode} done={done_b} refused={refused_b} "
                        f"notes={len(notes_b)} fails={by_kind(found_b, 'wake-failed')} "
                        f"asks={by_kind(found_b, 'post', verb='ask')} result={result_of(found_b, 'T1')!r}")

    # --- (h) the edges applied, an ask to any member ---------------------------------------------------------
    edges, done_eg = started["edges"], reached["edges"]
    found_e = h.events("edges")
    refused_e, notes_e = refusals_of(found_e, "eg1"), notes_to(found_e, "eg1")
    asked_e = asks_to(found_e, "eg1", "eg2")
    replies_e = [(one.get("from"), one.get("to"), one.get("re")) for one in by_kind(found_e, "post", verb="re")
                 if one.get("from") == "eg2"]
    if (edges.returncode == 0 and done_eg and len(refused_e) == 1 and "edges" in refused_e[0] and len(notes_e) == 1
            and not by_kind(found_e, "wake-failed") and not T.delegated(found_e, frm="eg1")
            and len(asked_e) == 1 and len(by_kind(found_e, "wake-intent", agent="eg2")) == 1
            and replies_e == [("eg2", "eg1", asked_e[0]["id"])]
            and result_of(found_e, "T1") == "edges held"):
        held("(h) the edges applied, an ask to any member", "eg1's do to eg2 -- off the edges, eg2 reports to eg: "
             f"wake-refused, no delegation from eg1, a note; launched again, its ask to eg2 (#{asked_e[0]['id']}) "
             "routed, eg2 launched once, its answer cites the ask; T1 done")
    else:
        failures.append(f"  ✗ (h) the edges and the asks    rc={edges.returncode} done={done_eg} refused={refused_e} "
                        f"notes={len(notes_e)} fails={by_kind(found_e, 'wake-failed')} "
                        f"delegated={T.delegated(found_e, frm='eg1')} asks={[one['id'] for one in asked_e]} "
                        f"replies={replies_e} eg2={len(by_kind(found_e, 'wake-intent', agent='eg2'))} "
                        f"result={result_of(found_e, 'T1')!r}")
    return 0
