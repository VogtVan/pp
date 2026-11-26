"""Scenario `team-answers-refused` -- 9 case(s): the acts the tick refuses at the routing (their form right,
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
- (f2) a root a member delegated its task to, dying past `retries: 0` (a journal written by hand: the member's `do` on
  the root's task, a launch dead without a flow): the team's notice about it goes to THAT member, the tick answers the
  member's `do` in its place, and the member, woken by that answer, owes nothing: its `wake-intent` carries no beat
- (c2) a `re` that names a boolean (`{"re": true}`) is no message number: `wake-refused`, a note to the member, no
  failure; launched again by the note, it answers the opening
- (b) an ask to a name nobody declared: `wake-refused`, no ask posted, a note to the member; launched again by
  the note, it answers the opening
- (h) a `do` off the edges (`eg1 eg2 -> eg`, eg1 delegates to eg2): `wake-refused`, no delegation from eg1, a
  note; launched again by it, eg1's `ask` to eg2 is ROUTED, eg2 launched once by it, its answer cites the ask;
  eg closes T1
- (k) the acts found in a words of text: ONE production -- the print that hands it, the only words of its launch --
  carries two asks between sentences, routed both, in order; then `{"do": 5}`, an ask with a key too many, a `do`
  that still carries `await` -- a key of no form since team 1.14.0, named in the refusal -- and an object cut short
  on `"do"`, each refused in its order, each reason naming its own form -- `wake-refused`, a note to the member, nothing posted, no failure, the
  follower alive --; then an answer inside a ``` block after a sentence, which closes T1
"""
from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor

from tests.harness import support

T = support(__file__, "team")


def refusals_of(found: list[dict], agent: str) -> list[str]:
    """-> the reasons the tick refused the member's acts with, in order."""
    return [str(one.get("why")) for one in found if one.get("kind") == "wake-refused" and one.get("agent") == agent]


def notes_to(found: list[dict], agent: str) -> list[dict]:
    """-> the infos the team posted to the member (an act refused, said to it)."""
    return [one for one in found if one.get("kind") == "post" and one.get("verb") == "info" and one.get("to") == agent]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        # (c) a re to a message never delivered, then the answer
        "x1": [{"sleep": 0.1, "body": {"re": 9999, "text": "?"}},
               {"sleep": 0.1, "body": {"re": "DO", "text": "fine"}}],
        # (c2) a re naming a boolean, then the answer
        "x4": [{"sleep": 0.1, "body": {"re": True, "text": "?"}},
               {"sleep": 0.1, "body": {"re": "DO", "text": "fine"}}],
        # (f2) the member woken by the tick's answer in its root's place: it says nothing
        "hub": [{"sleep": 0.1, "body": []}],
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
        "eg2": [{"sleep": 0.1, "body": {"reply": {"to": "eg1", "text": "mine is fine"}}}],
        # (k) acts inside ONE words of text: two asks, four broken forms, then the answer in a ``` block
        "y": [{"sleep": 0.1, "words": [
            {"wrap": ["Two questions: ", {"ask": {"to": "house", "text": "q1"}}, " then ",
                      {"ask": {"to": "house", "text": "q2"}}, ".\n",
                      '{"do": 5}\n',
                      '{"ask": {"to": "house", "text": "q3"}, "extra": 1}\n',
                      '{"do": ["y"], "await": {"any": 1}}\n',
                      'Cut short: {"do": {"zz": "half\n',
                      "Here is my answer.\n```json\n", {"re": "DO", "text": "found"}, "\n```"]}]}]})
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
    h.declare("forms", "---\nagents: |\n  y agents/y\nroot: y\nretries: 1\nschedule: off\n---\nSay it in words.\n")
    h.declare("flag", "---\nagents: |\n  x4 agents/x4\nroot: x4\nretries: 1\nschedule: off\n---\nAnswer.\n")
    h.declare("relay", "---\nagents: |\n  leaf agents/leaf\n  hub agents/hub\nreports: |\n  hub -> leaf\nroot: leaf\n"
                       "retries: 0\nschedule: off\n---\nThe root may die.\n")
    relay = h.call("team", "start", "relay", "--message", "hold it", "--no-tick", *h.harnessed)
    found_rl = h.events("relay")                        # by hand: hub's do to leaf on T1, leaf's launch dead, no flow
    opening_rl = next((one["id"] for one in T.by_kind(found_rl, "post", verb="do")), None)
    last_rl = max((one["id"] for one in found_rl), default=0)
    with h.journal_of("relay").open("a", encoding="utf-8") as handle:
        for offset, one in enumerate((
                {"kind": "post", "task": "T1", "from": "hub", "to": "leaf", "verb": "do", "text": "half of it"},
                {"kind": "wake-intent", "tag": "leaf-T1-dead00", "agent": "leaf", "path": "agents/leaf", "task": "T1",
                 "run": None, "index": 1, "messages": [opening_rl, last_rl + 1]},
                {"kind": "wake-launched", "tag": "leaf-T1-dead00", "agent": "leaf", "run": "gone00", "launch": 1}), 1):
            handle.write(json.dumps({"at": "2026-11-23T10:00:00+00:00", "id": last_rl + offset, "team": "relay", **one}) + "\n")
    openings = {"edges": "review PR 12", "dies": "try it", "frail": "try it", "alone": "do it",   # the longest
                "never": "answer me", "verbs": "answer me", "prosy": "say something", "prosy0": "say something",
                "forms": "answer me", "flag": "answer me"}
    with ThreadPoolExecutor(max_workers=len(openings)) as pool:     # chain first, every start at once
        calls = {name: pool.submit(h.call, "team", "start", name, "--message", text, *h.harnessed)
                 for name, text in openings.items()}
    started = {name: one.result() for name, one in calls.items()}

    # --- one wait for all: the dead wake-ups fire no on-end, their teams are ticked ----------------------------
    awaited = {"never": ended, "verbs": ended, "prosy": said_once, "prosy0": said_once,   # the prose teams: three launches
               "dies": ended, "frail": final_failed, "alone": ended, "edges": ended, "forms": ended, "flag": ended,
               "relay": lambda found: bool(T.notices_about(found, "leaf")) and bool(T.intents_of(found, "hub"))
               and all_ended(found)}
    ticked = {"dies", "frail", "relay"}
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

    # --- (k) the acts found in a words of text ---------------------------------------------------------------
    forms, done_k = started["forms"], reached["forms"]
    found_k = h.events("forms")
    routed_k = [one.get("words") for one in by_kind(found_k, "wake-routed", agent="y")]
    refused_k = [(one.get("words"), str(one.get("why"))) for one in by_kind(found_k, "wake-refused", agent="y")]
    asked_k = [one.get("text") for one in by_kind(found_k, "post", verb="ask", **{"from": "y"})]
    notes_k = notes_to(found_k, "y")
    rank_k = [int(one["rank"]) for one in T.lines(h.out / "y.prints") if '{"ask"' in one["text"]]   # its print
    marks = ("5", "extra", "await", "zz")      # what each broken form carries, in its order in the words
    whys = [why for _, why in refused_k]
    in_order = len(whys) == len(marks) and all(
        mark in why and not any(other in why for other in marks[1:] if other != mark) for mark, why in zip(marks, whys))
    if (forms.returncode == 0 and done_k and len(rank_k) == 1 and routed_k == rank_k * 3
            and [one for one, _ in refused_k] == rank_k * 4
            and in_order
            and asked_k == ["q1", "q2"] and len(notes_k) == 4 and not by_kind(found_k, "wake-failed")
            and not by_kind(found_k, "post", verb="do", **{"from": "y"}) and result_of(found_k, "T1") == "found"):
        held("(k) the acts found in a words of text", f"one words (the print of rank {rank_k}): two asks between "
             "sentences routed in order; a do of no member, a key too many, a do that carries `await` -- the key "
             "named -- and an object cut short refused in that order with a note each, nothing posted, no failure; the answer "
             "in a ``` block closes T1")
    else:
        failures.append(f"  ✗ (k) the acts in a words       rc={forms.returncode} done={done_k} routed={routed_k} "
                        f"refused={refused_k} asks={asked_k} notes={len(notes_k)} rank={rank_k} "
                        f"fails={by_kind(found_k, 'wake-failed')} result={result_of(found_k, 'T1')!r}")

    # --- (f2) a root a member delegated to: the notice to that member ------------------------------------------
    found_rl = h.events("relay")
    told_rl = T.notices_about(found_rl, "leaf")
    in_place_rl = [one for one in by_kind(found_rl, "post", verb="re", **{"from": "leaf"}) if one.get("by") == "tick"]
    hub_rl = T.intents_of(found_rl, "hub")
    if (relay.returncode == 0 and reached["relay"] and opening_rl is not None
            and [(one.get("reason"), one.get("final")) for one in by_kind(found_rl, "wake-failed", agent="leaf")]
            == [("wake-dead", True)]
            and [(one.get("to"), one.get("task")) for one in told_rl] == [("hub", "T1")]
            and [(one.get("re"), one.get("to")) for one in in_place_rl] == [(last_rl + 1, "hub")]
            and len(hub_rl) == 1 and "beat" not in hub_rl[0] and hub_rl[0].get("continued") is False
            and hub_rl[0].get("messages") == [in_place_rl[0]["id"], told_rl[0]["id"]] and not by_kind(found_rl, "done")):
        held("(f2) a root a member delegated to", f"leaf, root of T1, dies for good with hub's do #{last_rl + 1} on it: the "
             f"team's notice about leaf to hub, the tick's answer to #{last_rl + 1} in its place; hub woken by both owes "
             "nothing: its wake-intent without a beat; T1 open")
    else:
        failures.append(f"  ✗ (f2) a root delegated to       rc={relay.returncode} reached={reached['relay']} "
                        f"told={[(one.get('to'), one.get('task')) for one in told_rl]} "
                        f"in_place={[(one.get('re'), one.get('to')) for one in in_place_rl]} hub={hub_rl} "
                        f"journal={[T.shape(one) + ((one.get('reason'), one.get('final')) if one.get('kind') == 'wake-failed' else ()) for one in found_rl]} "
                        f"{relay.stderr[-200:]!r}")

    # --- (c2) a re naming a boolean -------------------------------------------------------------------------------
    flag, done_c2 = started["flag"], reached["flag"]
    found_c2 = h.events("flag")
    refused_c2, notes_c2 = refusals_of(found_c2, "x4"), notes_to(found_c2, "x4")
    if (flag.returncode == 0 and done_c2 and len(refused_c2) == 1 and len(notes_c2) == 1
            and not [one for one in by_kind(found_c2, "post", verb="re") if one.get("from") == "x4" and one.get("re") is True]
            and not by_kind(found_c2, "wake-failed") and len(by_kind(found_c2, "wake-intent", agent="x4")) == 2
            and result_of(found_c2, "T1") == "fine"):
        held("(c2) a re naming a boolean", "x4's {re: true}: wake-refused, nothing posted on it, a note to x4, no failure; "
             "launched again by the note, x4 answers the opening")
    else:
        failures.append(f"  ✗ (c2) a re naming a boolean     rc={flag.returncode} done={done_c2} refused={refused_c2} "
                        f"notes={len(notes_c2)} fails={by_kind(found_c2, 'wake-failed')} "
                        f"intents={len(by_kind(found_c2, 'wake-intent', agent='x4'))} result={result_of(found_c2, 'T1')!r}")
    return 0
