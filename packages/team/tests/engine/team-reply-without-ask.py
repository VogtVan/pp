"""Scenario `team-reply-without-ask` -- 2 case(s) (batch le-tick, rework of 2026-10-09: decision 63 of
the phase, team 0.16.0): a `reply` answers an `ask` alone.
- (a) a reply nobody asked for: a1 answers `reply` to the `do` lead sent it -- `wake-failed
  response-unreadable` (reply answers no ask), retried; no `reply` post in the journal; lead woken
  twice only (its opening, then its delegate's `done`); T1 closed
- (b) the contract says it: the CONTRACT of `pp-team.py` says that a `do` received closes by `done` and
  that a `reply` answers an `ask` alone
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "lead": [{"sleep": 0.1, "body": {"do": ["a1"]}},
                 {"sleep": 0.1, "body": {"done": "closed"}}],
        "a1": [{"sleep": 0.1, "body": {"reply": {"to": "lead", "text": "fini"}}},
               {"sleep": 0.1, "body": {"done": "the work"}}]})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of

    # --- (a) a reply that answers no ask --------------------------------------------------------------
    h.declare("solo", "---\nagents: |\n  lead agents/lead\n  a1 agents/a1\nreports: |\n  a1 -> lead\n"
                      "root: lead\nretries: 1\nschedule: off\n---\nDelegate and close.\n")
    solo = h.call("team", "start", "solo", "--message", "close the change", *h.harnessed)
    done = h.settled("solo", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=60)
    found = h.events("solo")
    fails = [(one.get("final"), str(one.get("reason"))) for one in by_kind(found, "wake-failed", agent="a1")]
    if (solo.returncode == 0 and done and len(fails) == 1 and not fails[0][0]
            and fails[0][1].startswith("response-unreadable") and "reply answers no ask" in fails[0][1]
            and not by_kind(found, "post", verb="reply") and len(T.intents_of(found, "lead")) == 2
            and result_of(found, "T1") == "closed"):
        held("(a) a reply nobody asked for", f"a1's reply to lead's do: {fails[0][1]!r}, retried; no reply "
             "posted, lead woken at its opening and at a1's done alone; T1 closed")
    else:
        failures.append(f"  ✗ (a) a reply nobody asked for  rc={solo.returncode} done={done} fails={fails} "
                        f"replies={len(by_kind(found, 'post', verb='reply'))} lead={len(T.intents_of(found, 'lead'))} "
                        f"result={result_of(found, 'T1')!r}")

    # --- (b) the contract says it ---------------------------------------------------------------------
    module = h.team_module().read_text(encoding="utf-8")
    contract = module[module.find("CONTRACT = ("):module.find("USAGE = (")]
    closes, answers = 'a "do" you receive closes by "done"', 'a "reply" answers only an "ask" you received'
    if closes in contract and answers in contract:
        held("(b) the contract", "the CONTRACT says that a do received closes by done and that a reply answers an ask")
    else:
        failures.append(f"  ✗ (b) the contract               {contract[:600]!r}")
    return 0
