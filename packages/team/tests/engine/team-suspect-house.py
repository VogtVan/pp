"""Scenario `team-suspect-house` -- 2 case(s) (batch les-echecs-du-tick, team 0.41.0; KET11, KET13; study § 21, rows
107 and 109): what the failure detector never reads, and the bound on what it reads.
- (a) a house failure is no fall: the member `w` plays under a profile whose provider the house is not wired with --
  `agent start` refuses before any harness, without its report -- twice in a row (the start's tick, then one tick):
  two `wake-failed {house: true, final: false}`, no retry spent, `w` not suspected (`health` null), its `do` back in its
  inbox each time, ONE notice of the team to the owner (`house`, no `about`: the face waits on nobody); a new season
  without the profile lifts the cause: the next tick launches `w`, which answers, T1 done
- (b) the interval is bounded: under `schedule: 5s` and `suspect-max: 20s`, `c2` dies for good at every task
  (`retries: 0`): its tries are due 5, 10, 20 then 20 seconds after each final failure -- the fourth bounded --, read
  at the face (`health.tried_at`, to the second) and at the module's `within` 21 s after the fourth failure, where
  40 s would still hold it
"""
from __future__ import annotations

from datetime import timedelta

from tests.harness import support

T = support(__file__, "team")

DEATH = {"sleep": 0.1, "body": "crash"}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "r": {"T1": [{"sleep": 0.1, "body": {"do": ["w"]}}, {"sleep": 0.1, "body": {"re": "DO", "text": "t1 done"}}]},
        "w": {"T1": [{"sleep": 0.1, "body": {"re": "DO", "text": "my part"}}]},
        "c1": {task: [{"sleep": 0.1, "body": {"do": ["c2"]}}, {"sleep": 0.1, "body": {"re": "DO", "text": f"{task} done"}}]
               for task in ("T1", "T2", "T3", "T4")},
        "c2": {task: [DEATH] for task in ("T1", "T2", "T3", "T4")}})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of

    # --- (a) a house failure is no fall ------------------------------------------------------------------------
    h.declare("hf", "---\nagents: |\n  r agents/r\n  w agents/w\nreports: |\n  w -> r\nroot: r\nretries: 1\nschedule: off\n---\n"
                    "The house may refuse.\n")
    started = h.call("team", "start", "hf", "--message", "build it", *h.harnessed, "--member", "w", "--provider", "nowhere")
    h.settled("hf", lambda found: bool(by_kind(found, "wake-failed", agent="w")) and all_ended(found), timeout=30)
    again = h.call("team", "tick", "hf")                      # every tick launches w again: refused again
    h.settled("hf", all_ended, timeout=10)
    found = h.events("hf")
    refused = sorted({(one.get("house"), one.get("final"), str(one.get("reason"))[:14]) for one in by_kind(found, "wake-failed", agent="w")})
    refusals = len(by_kind(found, "wake-failed", agent="w"))
    notices = [one for one in by_kind(found, "post", verb="notice") if one.get("house")]
    face = h.face("hf")
    w_face = next((one for one in face.get("members") or [] if one.get("member") == "w"), {})
    do_w = next((one["id"] for one in by_kind(found, "post", verb="do", to="w")), None)
    pending = [one.get("id") for one in w_face.get("pending") or []]
    lifted = h.call("team", "start", "hf", *h.harnessed)
    h.settled("hf", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=40)
    after = h.events("hf")
    if (started.returncode == 0 and again.returncode == 0 and refused == [(True, False, "launch-failed:")] and refusals >= 2
            and len(notices) == 1 and notices[0].get("to") == "house" and notices[0].get("about") is None
            and "w" in notices[0].get("text", "") and w_face.get("health") is None and w_face.get("how") == "refused"
            and pending == [do_w] and "owner" not in (face.get("waiting_on") or []) and "suspected" not in (face.get("waiting_on") or [])
            and lifted.returncode == 0 and len(T.intents_on(after, "w", "T1")) == refusals + 1
            and len(by_kind(after, "wake-launched", agent="w")) == 1 and result_of(after, "T1") == "t1 done"):
        held("(a) a house failure is no fall", f"w refused {refusals} times before any harness: wake-failed {{house, "
             "final false}} each time, no suspicion, its do back in its inbox, one notice to the owner; the cause lifted "
             "by a season, w launched once, T1 't1 done'")
    else:
        failures.append(f"  ✗ (a) a house failure         rc={started.returncode}/{again.returncode}/{lifted.returncode} "
                        f"refused={refused}x{refusals} notices={[(one.get('to'), one.get('about'), one.get('text')) for one in notices]} "
                        f"health={w_face.get('health')} how={w_face.get('how')} pending={pending} do={do_w} "
                        f"waiting_on={face.get('waiting_on')} intents={len(T.intents_on(after, 'w', 'T1'))} "
                        f"launched={len(by_kind(after, 'wake-launched', agent='w'))} result={result_of(after, 'T1')!r} "
                        f"{started.stderr[-160:]!r} {lifted.stderr[-160:]!r}")

    # --- (b) the interval is bounded ----------------------------------------------------------------------------
    h.declare("cap", "---\nagents: |\n  c1 agents/c1\n  c2 agents/c2\nreports: |\n  c2 -> c1\nroot: c1\nretries: 0\n"
                     "schedule: 5s\nsuspect-max: 20s\n---\nThe interval is bounded.\n")
    closed = lambda task: lambda found: bool(by_kind(found, "done", task=task)) and all_ended(found)
    started_c = h.call("team", "start", "cap", "--message", "first", *h.harnessed)
    h.settled("cap", closed("T1"), timeout=40)
    tried_at, gaps = [], []
    for n, task in enumerate(("T2", "T3", "T4"), 2):
        fell = T.finals_of(h.events("cap"), "c2")
        last = fell[-1]["at"] if fell else None
        gap = min(5 * 2 ** (n - 2), 20)
        gaps.append(gap)
        tried_at.append(next(((one.get("health") or {}).get("tried_at") for one in h.face("cap").get("members") or []
                              if one.get("member") == "c2"), None))
        now = T.local_after(last, seconds=gap + 1).isoformat(timespec="seconds") if last else None
        h.call("team", "post", "cap", "--message", task.lower(), now=now)
        h.tick_until("cap", closed(task), timeout=40, now=now)
    fell = T.finals_of(h.events("cap"), "c2")
    final_at = fell[-1]["at"] if fell else None
    tried_at.append(next(((one.get("health") or {}).get("tried_at") for one in h.face("cap").get("members") or []
                          if one.get("member") == "c2"), None))
    expected = [T.local_after(one["at"], seconds=gap).strftime("%Y-%m-%dT%H:%M:%S") for one, gap in zip(fell, (5, 10, 20, 20))]
    found = h.events("cap")
    module = h.module()
    state = module.state_of(h.journal_of("cap"))
    unbounded = T.local_after(final_at, seconds=40) if final_at else None
    within_40 = module.within(state, "c2", unbounded - timedelta(seconds=19)) if unbounded else None
    if (started_c.returncode == 0 and len(fell) == 4 and tried_at == expected and gaps == [5, 10, 20] and within_40 is False
            and all(one.get("final") for one in by_kind(found, "wake-failed", agent="c2"))):
        held("(b) the interval is bounded", f"c2's tries due {tried_at[0][-8:]}, {tried_at[1][-8:]}, {tried_at[2][-8:]}, "
             f"{tried_at[3][-8:]}: 5, 10, 20 then 20 s (suspect-max 20s); 21 s after the fourth fall c2 is no longer "
             "within its interval")
    else:
        failures.append(f"  ✗ (b) the interval is bounded rc={started_c.returncode} finals={len(fell)} tried_at={tried_at} "
                        f"expected={expected} within_40={within_40} "
                        f"journal={[T.shape(one) + ((one.get('reason'), one.get('final')) if one.get('kind') == 'wake-failed' else ()) for one in found][-12:]}")
    return 0
