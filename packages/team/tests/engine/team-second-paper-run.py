"""Scenario `team-second-paper-run` -- 2 case(s) (batch le-tick, rework, pass B, team 0.12.1, and
the rework of l-attente, I9; split out of `team-review` by les-scenarios-par-maison, 2026-10-07):
the second paper run under the member's run, `team-reframe.puml` up to the stop of T2.
- (l) the second paper run (`team-reframe.puml`; I7, I8, I11, I18): fm's T1 and T2 in its ONE run, one
  wake-up at a time, its question to the owner on T1, a delegation to fr1 on T2 and fr1's escalate,
  fm's escalate to the owner; fm's run forgotten by `-reset` when nothing runs; the owner's reply opens
  a new run on T1, told the history of T1 and T2; T1 done, the question never returned; T2 left open,
  nobody holds it; then (the rework of `l-attente`, I9) `team stop --task T2`: `stopped`, no stop post,
  no wake-up after -- the run played to its end
"""
from __future__ import annotations

import time

from conductor import persistence
from tests.harness import cli, support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "fm": {"T1": [{"sleep": 2.0, "body": {"ask": {"to": "house", "text": "scope?"}}},
                      {"sleep": 0.1, "body": {"done": "LGTM"}}],
               "T2": [{"sleep": 0.1, "body": {"do": ["fr1"]}},
                      {"sleep": 0.1, "body": {"escalate": "blocked by the build"}}]},
        "fr1": [{"sleep": 0.1, "body": {"escalate": "the PR does not build"}}]})
    by_kind, all_ended, asks_to, escalates_of, intents_on, result_of = (
        T.by_kind, T.all_ended, T.asks_to, T.escalates_of, T.intents_on, T.result_of)

    # --- (l) the second paper run under the member's run: team-reframe.puml up to the stop of T2 -- I7, I8, I11, I18
    h.declare("reframe", "---\nagents: |\n  fm fm\n  fr1 fr1\nreports: |\n  fr1 -> fm\nroot: fm\nschedule: off\n---\n"
                         "Review what is asked.\n")
    first_r = h.call("team", "start", "reframe", "--message", "review PR 42", *h.harnessed)
    second_r = h.call("team", "post", "reframe", "--to", "fm", "--message", "review PR 43")
    quiet_r = h.settled("reframe", lambda found: bool(asks_to(found, "fm", "house")) and bool(escalates_of(found, "fm"))
                        and all_ended(found), 90)
    found_r = h.events("reframe")
    ask_r = next((one["id"] for one in asks_to(found_r, "fm", "house")), -1)
    fm_t1 = intents_on(found_r, "fm", "T1")
    kept_r = next((one.get("run") for one in by_kind(found_r, "wake-launched", agent="fm")
                   if fm_t1 and one.get("tag") == fm_t1[0]["tag"]), "")
    forgot_r = None
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        forgot_r = cli(h.engine, "--instance", str(h.meta_of("fm")), "-reset", kept_r, cwd=h.ws, env=h.env)
        if forgot_r.returncode == 0 or "call-busy" not in forgot_r.stderr:
            break
        time.sleep(0.5)
    gone_r = bool(kept_r) and not persistence.slot_of(h.meta_of("fm"), kept_r).exists()
    replied_r = h.call("team", "post", "reframe", "--task", "T1", "--reply", str(ask_r), "--message", "the whole diff")
    done_r = h.settled("reframe", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    found_r = h.events("reframe")
    fm_t1, fm_t2 = intents_on(found_r, "fm", "T1"), intents_on(found_r, "fm", "T2")
    runs_r = {one["tag"]: one.get("run") for one in by_kind(found_r, "wake-launched")}
    ended_t1 = next((one["id"] for one in by_kind(found_r, "wake-ended", agent="fm")
                     if fm_t1 and one.get("tag") == fm_t1[0]["tag"]), 10 ** 9)
    status_r = h.call("team", "status", "reframe")
    reopened_r = next((one for one in h.prompts_of("fm") if "[history of T1 for fm]" in one), "")
    if (first_r.returncode == 0 and second_r.returncode == 0 and quiet_r and forgot_r is not None
            and forgot_r.returncode == 0 and gone_r and replied_r.returncode == 0 and done_r
            and len(fm_t2) == 2 and fm_t2[0]["id"] > ended_t1
            and {runs_r.get(one["tag"]) for one in fm_t2} == {kept_r} and fm_t2[0].get("run") == kept_r
            and by_kind(found_r, "delegation", **{"from": "fm"}) and escalates_of(found_r, "fr1")
            and [one.get("to") for one in escalates_of(found_r, "fm")] == ["house"]
            and len(fm_t1) == 2 and fm_t1[1].get("run") is None and runs_r.get(fm_t1[1]["tag"]) not in (None, kept_r)
            and "[history of T1 for fm]" in reopened_r and "[history of T2 for fm]" in reopened_r
            and not by_kind(found_r, "returned") and not by_kind(found_r, "wake-failed")
            and result_of(found_r, "T1") == "LGTM" and "T2 · open" in status_r.stdout):
        held("(l) the second paper run", f"fm's two tasks in its ONE run {kept_r}, one wake-up at a time (T2 woken "
             f"#{fm_t2[0]['id']} after T1's end #{ended_t1}); fr1 escalates up the edge, fm escalates T2 to the owner; "
             f"`-reset` forgets {kept_r}; the reply reopens T1 on a new run told the history of T1 and T2; T1 LGTM; "
             "the ask to the owner never returned; T2 left open, nobody holds it (stopped below) -- I7, I8, I11, I18")
    else:
        failures.append(f"  ✗ (l) the second paper run    {first_r.returncode}/{second_r.returncode}/"
                        f"{getattr(forgot_r, 'returncode', None)}/{replied_r.returncode} quiet={quiet_r} gone={gone_r} "
                        f"done={done_r} t1={[(one['id'], one.get('run')) for one in fm_t1]} "
                        f"t2={[(one['id'], one.get('run')) for one in fm_t2]} end_t1={ended_t1} "
                        f"returned={by_kind(found_r, 'returned')} failed={by_kind(found_r, 'wake-failed')} "
                        f"result={result_of(found_r, 'T1')!r} {status_r.stdout[-300:]!r}")

    # --- (l) closed: the stop of T2, a task nobody holds (s.602) -- I9 ---------------------------------------
    stopped_r = h.call("team", "stop", "reframe", "--task", "T2")
    time.sleep(1.0)
    found_r = h.events("reframe")
    stop_r = next(iter(by_kind(found_r, "stopped", task="T2")), {})
    stop_posts_r = [one for one in by_kind(found_r, "post", verb="stop") if one.get("task") == "T2"]
    after_r = [one for one in by_kind(found_r, "wake-intent") if one["id"] > stop_r.get("id", 0)]
    status_r2 = h.call("team", "status", "reframe")
    if (stopped_r.returncode == 0 and stop_r and stop_posts_r == [] and after_r == []
            and "nobody held it" in stopped_r.stdout and "T2 · stopped" in status_r2.stdout
            and "T1 · resolved" in status_r2.stdout):
        held("(l) closed: the stop of T2", f"T2, held by nobody (fm and fr1 terminal), stopped #{stop_r.get('id')}: "
             "no stop post, no wake-up after, `nobody held it`; the second paper run played to its end -- I9")
    else:
        failures.append(f"  ✗ (l) the stop of T2         rc={stopped_r.returncode} stopped={stop_r} posts={len(stop_posts_r)} "
                        f"after={[(one['agent'], one['task']) for one in after_r]} {stopped_r.stdout[-200:]!r} "
                        f"{status_r2.stdout[-300:]!r}")
    return 0
