"""Scenario `team-routes` -- 3 case(s) (batch le-tick, rework, pass B: the routes and the answers,
team 0.12.1, agent 0.3.1; split out of `team-review` by les-scenarios-par-maison, 2026-10-07):
the witness names the cost of each answer; each case names the invariant of
`team-sim-reframe.py` it replays.
- (h) the edges [35] and the asks [62] (I11a restated): `eg1 eg2 ->
  eg`, `retries: 2`; eg delegates T1 to eg1, which answers `{"do": ["eg2"]}` -- `response-unreadable`
  naming the edge, retried --, then `{"ask": {"to": "eg2"}}`: ROUTED, eg2 woken by it, its reply cites the
  ask; eg1 answers `done`, eg closes T1
- (i) the post to a principal [36] (I11b): iq asks the owner on T1, the owner replies, iq answers done:
  no `returned` of the ask; `status` lists it in the owner's inbox, `team inbox` says T1 done
- (k) the answer before the timeout [46] (I16): `timeout: 1`; a wake-up launched long ago whose
  answer is kept on its run, its wake lock held by the bench: the tick writes `wake-ended` with its
  cost, never `wake-timeout`
"""
from __future__ import annotations

import json

from tests.harness import holding, support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "eg": [{"sleep": 0.1, "body": {"do": ["eg1"]}},
               {"sleep": 0.1, "body": {"done": "edges held"}}],
        "eg1": [{"sleep": 0.1, "body": {"do": ["eg2"]}},
                {"sleep": 0.1, "body": {"ask": {"to": "eg2", "text": "and you?"}}},
                {"sleep": 0.1, "body": {"done": True}}],
        "eg2": [{"sleep": 0.1, "body": {"reply": {"to": "eg1", "text": "mine is fine"}}}],
        "iq": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "scope?"}}},
               {"sleep": 0.1, "body": {"done": "answered"}}]})
    by_kind, all_ended, asks_to, result_of = T.by_kind, T.all_ended, T.asks_to, T.result_of

    # --- (h) the edges applied [35], an ask to any member [62] -- I11a restated ---------------------------
    h.declare("edges", "---\nagents: |\n  eg eg\n  eg1 eg1\n  eg2 eg2\nreports: |\n  eg1 eg2 -> eg\n"
                       "root: eg\nretries: 2\nschedule: off\n---\nDelegate along the edges.\n")
    edges = h.call("team", "start", "edges", "--message", "review PR 12", *h.harnessed)
    done_eg = h.settled("edges", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=60)
    found_e = h.events("edges")
    fails_e = [(one.get("final"), str(one.get("reason"))) for one in by_kind(found_e, "wake-failed", agent="eg1")]
    asked_e = asks_to(found_e, "eg1", "eg2")
    replies_e = [(one.get("from"), one.get("to"), one.get("reply")) for one in by_kind(found_e, "post", verb="reply")]
    if (edges.returncode == 0 and done_eg and len(fails_e) == 1 and not fails_e[0][0]
            and fails_e[0][1].startswith("response-unreadable") and "off the edges" in fails_e[0][1]
            and "eg2" in fails_e[0][1] and not by_kind(found_e, "delegation", **{"from": "eg1"})
            and len(asked_e) == 1 and len(by_kind(found_e, "wake-intent", agent="eg2")) == 1
            and replies_e == [("eg2", "eg1", asked_e[0]["id"])]
            and result_of(found_e, "T1") == "edges held"):
        held("(h) the edges applied, an ask to any member", "eg1's do to eg2 -- off the edges, eg2 reports to eg: "
             f"response-unreadable, retried; its ask to eg2 (#{asked_e[0]['id']}) routed, eg2 woken once, its reply "
             "cites the ask; T1 done -- I11a restated")
    else:
        failures.append(f"  ✗ (h) the edges and the asks    rc={edges.returncode} done={done_eg} fails={fails_e} "
                        f"asks={[one['id'] for one in asked_e]} replies={replies_e} "
                        f"eg2={len(by_kind(found_e, 'wake-intent', agent='eg2'))} result={result_of(found_e, 'T1')!r}")

    # --- (i) the post to a principal [36] -- I11b -----------------------------------------------------------
    h.declare("ownerq", "---\nagents: |\n  iq iq\nroot: iq\nschedule: off\n---\nAsk the owner.\n")
    ownerq = h.call("team", "start", "ownerq", "--message", "scope it", *h.harnessed)
    asked_iq = h.settled("ownerq", lambda found: bool(asks_to(found, "iq", "house")) and all_ended(found), timeout=60)
    ask_iq = next((one["id"] for one in asks_to(h.events("ownerq"), "iq", "house")), -1)
    replied_iq = h.call("team", "post", "ownerq", "--task", "T1", "--reply", str(ask_iq), "--message", "all of it")
    done_iq = h.settled("ownerq", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=60)
    found_i = h.events("ownerq")
    status_i = h.call("team", "status", "ownerq")
    inbox_i = h.call("team", "inbox", "ownerq")
    ask_line = next((line for line in status_i.stdout.splitlines() if line.strip().startswith(f"#{ask_iq} ask")), "")
    if (ownerq.returncode == 0 and asked_iq and replied_iq.returncode == 0 and done_iq
            and not [one for one in by_kind(found_i, "returned") if one.get("message") == ask_iq]
            and ask_line.strip() == f"#{ask_iq} ask from iq on T1"
            and inbox_i.returncode == 0 and "ownerq: T1 done" in inbox_i.stdout and "returned" not in inbox_i.stdout
            and result_of(found_i, "T1") == "answered"):
        held("(i) a post to the owner is never returned", f"iq's ask #{ask_iq} to the owner, the owner's reply, T1 "
             f"done: no returned; status says {ask_line.strip()!r}; the inbox says T1 done -- I11b")
    else:
        failures.append(f"  ✗ (i) the post to the owner    {ownerq.returncode}/{replied_iq.returncode} asked={asked_iq} "
                        f"done={done_iq} returned={by_kind(found_i, 'returned')} line={ask_line!r} "
                        f"inbox={inbox_i.stdout!r}")

    # --- (k) the answer before the timeout [46] -- I16 -------------------------------------------------------------
    h.declare("late", "---\nagents: |\n  kx kx\nroot: kx\ntimeout: 1\nretries: 0\nschedule: off\n---\nAnswer late.\n")
    late = h.call("team", "start", "late", "--message", "do it", *h.harnessed, "--no-tick")
    found_k = h.events("late")
    last_k = max(one["id"] for one in found_k)
    do_k = next(one["id"] for one in by_kind(found_k, "post", verb="do"))
    with h.journal_of("late").open("a", encoding="utf-8") as handle:   # a wake-up launched long ago
        for offset, line in enumerate((
                {"kind": "wake-intent", "tag": "late-kx", "agent": "kx", "task": "T1", "run": None, "index": 1,
                 "messages": [do_k]},
                {"kind": "wake-launched", "tag": "late-kx", "agent": "kx", "run": "abc123", "pid": None}), 1):
            handle.write(json.dumps({"at": "2026-10-03T12:00:00+00:00", "id": last_k + offset, "team": "late",
                                     **line}) + "\n")
    with (h.records / "responses.jsonl").open("a", encoding="utf-8") as handle:   # its answer, kept on its run
        handle.write(json.dumps({"at": "2026-10-03T12:00:05+00:00", "agent": "kx", "run": "abc123",
                                 "index": 1, "response": '{"done": true}', "cost_usd": 0.25, "denials": [],
                                 "error": None, "harness_rc": 0}) + "\n")
    with holding(h.meta_of("kx") / ".sys" / "state" / "session-abc123.wake.lock"):   # still releasing
        ticked_k = h.call("team", "tick", "late")
    found_k = h.events("late")
    fails_k = [(one.get("final"), str(one.get("reason")), one.get("cost")) for one in by_kind(found_k, "wake-failed")]
    ends_k = [one.get("cost") for one in by_kind(found_k, "wake-ended", tag="late-kx")]
    status_k = h.call("team", "status", "late")
    if (late.returncode == 0 and ticked_k.returncode == 0
            and fails_k == [] and ends_k == [0.25]
            and "cost 0.25 USD" in status_k.stdout):
        held("(k) a kept answer is never killed", "kx's answer kept on its run, its wake lock held past "
             "timeout 1: wake-ended with its cost 0.25, no wake-timeout -- I16")
    else:
        failures.append(f"  ✗ (k) the answer first       {late.returncode}/{ticked_k.returncode} fails={fails_k} ends={ends_k} "
                        f"{next((line for line in status_k.stdout.splitlines() if line.startswith('cost')), '')!r} "
                        f"{ticked_k.stderr[-200:]!r}")
    return 0
