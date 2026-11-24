"""Scenario `team-continuation-model` -- 1 case(s): a changed model alone waits for the park of a standing run (s.1569);
cut from `team-continuation` by rule 10, beside its (d) and (e).
- (f) a season that changes the MODEL alone of a member whose run stands renews it at the wake-up after its park: sn's
  first launch, under m1, holds at a gate; the season stopped, a new one gives sn `--model m2`, same provider, and T1
  is resumed; the gate opens, sn says
  its first act and stands; its next launch CONTINUES that run -- same key, no history at its head --, asks the owner
  and parks; the `info` of T1's resume, waiting for that park, wakes it: `run-renewed {why: model, was.model m1,
  now.model m2}` written after the park, a NEW run under m2 whose head opens on T1's history, continued then under
  m2, whose act answers the opening:
  T1 done -- no launch failed
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "team")

ACTS = "---\nproc: |\n  INFER\n  §\n  INFER\noutput: team-act\n---\n# ACTS\n\nSay one act at each step.\n"
HISTORY = re.compile(r"^\[history of (\S+) for (\S+)\]$", re.M)   # the head of a new run's history (team-reset)
OPENING = 3                                      # the start's `do`, after `team-started` and `task`


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    gate = bench.temp() / "sn.gate"                      # sn's first launch waits for it
    h = T.House(bench, script={
        # sn holds at a gate under m1 and stands; its continuation asks the owner and parks; the answer opens a new run
        # under m2, which stands on its first act and answers the opening in its continuation
        "sn": [{"words": [{"gate": str(gate)}, {"info": {"to": "house", "text": "the first act"}}]},
               {"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which branch?"}}},
               {"sleep": 0.1, "body": {"info": {"to": "house", "text": "renewed"}}},
               {"sleep": 0.1, "body": {"re": OPENING, "text": "T1 under m2"}}]})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of
    h.declare("still", "---\nagents: |\n  sn agents/n\nroot: sn\nentries: |\n  do -> ACTS.md\nschedule: off\n---\n"
                       "Act, ask, then answer.\n")
    (h.teams / "still" / "ACTS.md").write_text(ACTS, encoding="utf-8")
    still = h.call("team", "start", "still", "--message", "act, ask, answer", *h.harnessed, "--member", "sn", "--model", "m1")
    held_f = h.settled("still", lambda found: bool(by_kind(found, "wake-launched", agent="sn")), 20)
    h.off_season("still")                                # the season stopped: T1 with it, sn's launch under way
    season = h.call("team", "start", "still", "--no-tick", "--member", "sn", "--model", "m2")
    h.call("team", "resume", "still", "--task", "T1", "--no-tick")
    gate.write_text("open", encoding="utf-8")

    # --- (f) a changed model alone renews a standing run at the wake-up after its park ---------------------------
    asked = h.settled("still", lambda found: bool(by_kind(found, "post", verb="ask", to="house")) and all_ended(found)
                      or bool(by_kind(found, "wake-failed", agent="sn")), 30)
    done = h.settled("still", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found)
                     or len(by_kind(found, "wake-failed", agent="sn")) >= 2, 30)
    found = h.events("still")
    launched = {one.get("tag"): one for one in by_kind(found, "wake-launched")}
    intents = T.intents_of(found, "sn")
    sn = [(one.get("run"), (launched.get(one.get("tag")) or {}).get("run"),
           (launched.get(one.get("tag")) or {}).get("model"),
           (launched.get(one.get("tag")) or {}).get("provider")) for one in intents]
    ended = by_kind(found, "wake-ended", agent="sn")
    renewed = by_kind(found, "run-renewed")
    one = renewed[0] if renewed else {}
    heads = [HISTORY.findall(prompt.split("▌ pp · run", 1)[0]) for prompt in h.prompts_of("sn")]
    opening = next((one["id"] for one in by_kind(found, "post", verb="do", task="T1")), None)
    if (still.returncode == 0 and season.returncode == 0 and held_f and asked and done and opening == OPENING
            and len(sn) == 4
            and sn[0][0] is None and sn[0][2:] == ("m1", "claude") and sn[0][1]
            and sn[1][:2] == (sn[0][1], sn[0][1])
            and sn[2][0] is None and sn[2][2:] == ("m2", "claude") and sn[2][1] and sn[2][1] != sn[0][1]
            and sn[3] == (sn[2][1], sn[2][1], "m2", "claude")
            and [end.get("state") for end in ended][:4] == ["standing", "parked", "standing", "parked"]
            and not by_kind(found, "wake-failed") and len(renewed) == 1 and one.get("why") == "model"
            and one.get("member") == "sn" and one.get("task") == "T1" and one.get("run") == sn[0][1]
            and one.get("was") == {"model": "m1", "provider": "claude"}
            and one.get("now") == {"model": "m2", "provider": "claude"}
            and ended[1]["id"] < one.get("id", 0) < intents[2]["id"]
            and heads[:4] == [[], [], [("T1", "sn")], []] and result_of(found, "T1") == "T1 under m2"):
        held("(f) a changed model alone waits for the park", f"sn stands in {sn[0][1]} opened under m1; the season gives "
             f"it m2: its continuation keeps {sn[1][1]} and parks (#{ended[1]['id']}); the resume's info renews it after the "
             f"park (run-renewed #{one.get('id')}, model m1 -> m2), a new run {sn[2][1]} under m2 told T1's history, "
             "continued under m2, its answer closing T1; no launch failed")
    else:
        failures.append(f"  ✗ (f) a changed model alone      rc={still.returncode}/{season.returncode} held={held_f} "
                        f"asked={asked} done={done} opening={opening} "
                        f"intents={sn} ends={[(end['id'], end.get('state')) for end in ended]} renewed={renewed} "
                        f"intent_ids={[intent['id'] for intent in intents]} heads={heads} "
                        f"failed={[(fail.get('reason'), fail.get('why')) for fail in by_kind(found, 'wake-failed')]} "
                        f"result={result_of(found, 'T1')!r} {(still.stderr + season.stderr)[-200:]!r}")
    return 0
