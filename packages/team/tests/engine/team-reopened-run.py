"""Scenario `team-reopened-run` -- 1 case(s) (batch le-tick, rework, pass A, team 0.12.0; split out
of `team-review` by les-scenarios-par-maison, 2026-10-07): a member's run forgotten by `-reset`,
reopened by the owner's reply.
- (d) the reopened run [33] (I7, I1): u asks the owner on T1, then on T2, in its one run; `-reset` at
  u forgets that run (an upgrade renews a run under its key); `post --reply` on T1: the tick opens a
  NEW run whose head carries `[history of T1 for u]` and `[history of T2 for u]` (each do, each ask),
  then the inbox (the reply) -- the team's intention served by pp in the new run's output, once,
  never in the message (rework le-rythme-et-les-entrees, team 0.17.0); T1 done, no `run-unknown`
  anywhere
"""
from __future__ import annotations

import time

from conductor import persistence
from tests.harness import cli, support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "u": {"T1": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which branch?"}}},
                     {"sleep": 0.1, "body": {"done": "merged"}}],
              "T2": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which tag?"}}},
                     {"sleep": 0.1, "body": {"done": "tagged"}}]}})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of

    # --- (d) a forgotten run reopened, told every open task [33] -- I7, I1 ----------------------------
    h.declare("up", "---\nagents: |\n  u u\nroot: u\nschedule: off\n---\nMerge what is asked.\n")
    up = h.call("team", "start", "up", "--message", "merge PR 11", *h.harnessed)
    asked_u1 = h.settled("up", lambda found: bool(by_kind(found, "wake-ended", agent="u")) and all_ended(found), 60)
    up2 = h.call("team", "post", "up", "--to", "u", "--message", "tag release 2")
    asked_u = asked_u1 and h.settled("up", lambda found: len(by_kind(found, "wake-ended", agent="u")) == 2
                                     and all_ended(found), 60)
    found_u = h.events("up")
    kept_u = next((one.get("run") for one in reversed(by_kind(found_u, "wake-ended", agent="u"))), "")
    ask_u = next((one["id"] for one in by_kind(found_u, "post", verb="ask") if one.get("task") == "T1"), -1)
    slot_u = persistence.slot_of(h.meta_of("u"), kept_u) if kept_u else h.ws
    forgot = None
    deadline = time.monotonic() + 30                  # the last on-end tick may still be leaving
    while time.monotonic() < deadline:
        forgot = cli(h.engine, "--instance", str(h.meta_of("u")), "-reset", kept_u, cwd=h.ws, env=h.env)
        if forgot.returncode == 0 or "call-busy" not in forgot.stderr:
            break
        time.sleep(0.5)
    gone = kept_u != "" and not slot_u.exists()
    replied = h.call("team", "post", "up", "--task", "T1", "--reply", str(ask_u), "--message", "main")
    done_u = h.settled("up", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 45)
    found_u = h.events("up")
    intents_u = by_kind(found_u, "wake-intent", agent="u")
    runs_u = {one["tag"]: one.get("run") for one in by_kind(found_u, "wake-launched", agent="u")}
    reasons_u = [str(one.get("reason")) for one in by_kind(found_u, "wake-failed")]
    reopened = next((one for one in h.prompts_of("u") if "[history of T1 for u]" in one), "")
    history_at, inbox_at = reopened.find("[history of T1 for u]"), reopened.find("[inbox]")
    second_at = reopened.find("[history of T2 for u]")
    output_at = reopened.find("▌ pp · run")
    intention_at = reopened.find("Merge what is asked.")
    reopening = [one for one in intents_u if one.get("run") is None][1:]
    if (up.returncode == 0 and up2.returncode == 0 and asked_u and forgot is not None and forgot.returncode == 0
            and gone and replied.returncode == 0 and done_u and len(intents_u) == 3 and len(reopening) == 1
            and runs_u.get(reopening[0]["tag"]) not in (None, kept_u)
            and not any("run-unknown" in one for one in reasons_u)
            and 0 <= history_at < second_at < inbox_at < output_at < intention_at
            and reopened.count("Merge what is asked.") == 1
            and "INFORMATION — TEAM.md" in reopened[output_at:intention_at]
            and "do from house: merge PR 11" in reopened[history_at:second_at]
            and "ask to house: which branch?" in reopened[history_at:second_at]
            and "do from house: tag release 2" in reopened[second_at:inbox_at]
            and "ask to house: which tag?" in reopened[second_at:inbox_at]
            and "reply from house on T1: main" in reopened[inbox_at:]
            and result_of(found_u, "T1") == "merged"):
        held("(d) a forgotten run is reopened, told every open task", f"u holds T1 and T2 in its run {kept_u}, "
             "forgotten by `-reset`; the reply opens a new run whose head carries [history of T1 for u] (the do, "
             "its ask), then [history of T2 for u] (the do, its ask), then the inbox (the reply); the intention "
             "served once in pp's output; T1 merged, no run-unknown -- I7, I1")
    else:
        failures.append(f"  ✗ (d) the reopened run         rc={up.returncode}/{up2.returncode}/"
                        f"{getattr(forgot, 'returncode', None)}/{replied.returncode} asked={asked_u} gone={gone} "
                        f"done={done_u} intents={[(one['id'], one.get('task'), one.get('run')) for one in intents_u]} "
                        f"reasons={reasons_u} at={history_at}/{second_at}/{inbox_at}/{output_at}/{intention_at} "
                        f"{getattr(forgot, 'stderr', '')[-200:]!r} {reopened[:600]!r}")
    return 0
