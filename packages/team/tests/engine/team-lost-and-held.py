"""Scenario `team-lost-and-held` -- 2 case(s) (batch le-tick, rework, pass A, team 0.12.0; split
out of `team-review` by les-scenarios-par-maison, 2026-10-07): a spawn lost, a run held.
- (e) the lost spawn [43], [44] (I1, I10e): under `launches: 2`, lq's first wake-up dies, then an
  intent forged without any launch: neither spends a launch nor the retry -- lq woken again, T1
  done, no `final`, no `launches-spent`
- (f) the held run [45] (I17): hd's run kept, its wake lock held by the bench, a note that makes hd
  due: no intent while held, no `run-busy`; released, the tick resumes THAT run, T1 done
"""
from __future__ import annotations

import os
import time

from tests.harness import holding, support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "lq": [{"sleep": 0.1, "body": "crash"},
               {"sleep": 0.1, "body": {"done": "after the lost spawn"}}],
        "hd": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which branch?"}}},
               {"sleep": 0.1, "body": {"done": "after the hold"}}]})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of

    # --- (e) the lost spawn [43], [44] -- I1, I10e -------------------------------------------------------
    h.declare("lost", "---\nagents: |\n  lq lq\nroot: lq\nlaunches: 2\nschedule: off\n---\nA spawn lost.\n")
    lost = h.call("team", "start", "lost", "--message", "do it", *h.harnessed)
    launched_lq = h.settled("lost", lambda found: bool(by_kind(found, "wake-launched", agent="lq")), timeout=30)
    pid_lq = next((one.get("pid") for one in by_kind(h.events("lost"), "wake-launched", agent="lq")), None)
    deadline = time.monotonic() + 30                  # the first wake-up dies (its script): no on-end
    while time.monotonic() < deadline and isinstance(pid_lq, int):
        try:
            os.kill(pid_lq, 0)
        except ProcessLookupError:
            break
        time.sleep(0.1)
    found_l = h.events("lost")
    do_l = next(one["id"] for one in by_kind(found_l, "post", verb="do"))
    T.forge_intents(h, "lost", "T1", "lq", ("lost-forged",), [do_l])   # a tick that died before its spawn

    def settled_l(found: list[dict]) -> bool:
        return bool((by_kind(found, "done", task="T1") or by_kind(found, "launches-spent")
                     or any(one.get("final") for one in by_kind(found, "wake-failed"))) and all_ended(found))

    h.tick_until("lost", settled_l)
    found_l = h.events("lost")
    fails_l = [(one.get("final"), one.get("reason")) for one in by_kind(found_l, "wake-failed")]
    launched_l = by_kind(found_l, "wake-launched", agent="lq")
    if (lost.returncode == 0 and launched_lq
            and fails_l == [(False, "wake-dead"), (False, "launch-missing")]
            and not by_kind(found_l, "launches-spent") and len(T.closings(found_l, "lq")) == 1
            and len(launched_l) == 2 and len(by_kind(found_l, "wake-intent")) == 3
            and result_of(found_l, "T1") == "after the lost spawn"):
        held("(e) a lost spawn costs nothing", "under launches 2 and one retry: lq dead once, then an intent "
             "without its spawn -- wake-dead and launch-missing, neither final; lq woken again, T1 done, "
             "no launches-spent -- I1, I10e")
    else:
        failures.append(f"  ✗ (e) the lost spawn          rc={lost.returncode} launched={launched_lq} fails={fails_l} "
                        f"spent={by_kind(found_l, 'launches-spent')} launches={len(launched_l)} "
                        f"result={result_of(found_l, 'T1')!r}")

    # --- (f) the held run [45] -- I17 -------------------------------------------------------------------
    h.declare("hold", "---\nagents: |\n  hd hd\nroot: hd\nschedule: off\n---\nA run held.\n")
    hold = h.call("team", "start", "hold", "--message", "begin", *h.harnessed)
    asked_hd = h.settled("hold", lambda found: bool(by_kind(found, "wake-ended", agent="hd")) and all_ended(found),
                         timeout=60)
    time.sleep(0.5)                                   # the on-end tick has left
    kept_hd = next((one.get("run") for one in by_kind(h.events("hold"), "wake-ended", agent="hd")), "")
    wake_hd = h.meta_of("hd") / ".sys" / "state" / f"session-{kept_hd}.wake.lock"
    with holding(wake_hd):                            # the answer kept, the release still to come
        nudged = h.call("team", "post", "hold", "--task", "T1", "--message", "go on")
        during = by_kind(h.events("hold"), "wake-intent", agent="hd")
    released = h.call("team", "tick", "hold")
    done_hd = h.settled("hold", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=60)
    found_h = h.events("hold")
    intents_hd = by_kind(found_h, "wake-intent", agent="hd")
    reasons_h = [str(one.get("reason")) for one in by_kind(found_h, "wake-failed")]
    if (hold.returncode == 0 and asked_hd and kept_hd and nudged.returncode == 0 and len(during) == 1
            and released.returncode == 0 and done_hd and len(intents_hd) == 2
            and intents_hd[1].get("run") == kept_hd and not any("run-busy" in one for one in reasons_h)
            and result_of(found_h, "T1") == "after the hold"):
        held("(f) a held run is busy", f"hd's run {kept_hd} under the bench's hold: the post wakes nobody, "
             "no run-busy; released, the tick resumes that run, T1 done -- I17")
    else:
        failures.append(f"  ✗ (f) the held run            rc={hold.returncode}/{nudged.returncode}/{released.returncode} "
                        f"asked={asked_hd} during={len(during)} intents={[(one['id'], one.get('run')) for one in intents_hd]} "
                        f"kept={kept_hd} reasons={reasons_h} done={done_hd} result={result_of(found_h, 'T1')!r}")
    return 0
