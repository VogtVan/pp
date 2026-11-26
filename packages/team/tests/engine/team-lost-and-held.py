"""Scenario `team-lost-and-held` -- 4 case(s) (batch le-tick, rework, pass A, team 0.12.0; split
out of `team-review` by les-scenarios-par-maison, 2026-10-07): a spawn lost, a run held, a launch that raises.
- (e) the lost spawn [43], [44] (I1, I10e): under `launches: 2`, lq's first wake-up dies, then an
  intent forged without any launch: neither spends a launch nor the retry -- lq woken again, T1
  done, no `final`, no `launches-spent`
- (f) the held run [45] (I17): hd's run kept, its wake lock held by the bench, a note that makes hd
  due: no intent while held, no `run-busy`; released, the tick resumes THAT run, T1 done
- (g) a launch whose preparation RAISES (batch la-continuation-bornee-et-le-tick-releve, s.1357): a tick played in
  the bench's process under `schedule: 1h`, the launch raising the `PermissionError` of an `os.replace` onto a
  read-only directory once its intent is written -- `wake-failed {house: true}` with the exception's type in its
  reason, the house's notice to the owner, and the team's net stands: `timer-armed` once, a timer stands
- (h) a tick KILLED during a launch (batch le-minuteur-arme-au-debut-du-tick, s.1373): under `schedule: 5s`, the tick
  played by the console in a process group of its own, killed by SIGKILL of its group as soon as kl's `wake-intent` is
  written, before `wake-launched` -- the timer armed at the start of its round stands (its mark, `timer-armed`, its
  hour the team's step), and at that hour it ticks without any call: the killed intent reaped (`launch-missing`, or
  its launch read late), kl launched again, T1 done
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time

from tests.harness import holding, support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "lq": [{"sleep": 0.1, "body": "crash"},
               {"sleep": 0.1, "body": {"done": "after the lost spawn"}}],
        "hd": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which branch?"}}},
               {"sleep": 0.1, "body": {"done": "after the hold"}}],
        "rz": [{"sleep": 0.1, "body": {"done": "never launched"}}],
        "kl": [{"sleep": 3.0, "body": {"done": "after the killed tick"}},
               {"sleep": 0.1, "body": {"done": "after the killed tick"}}]})
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

    # --- (g) a launch whose preparation raises -----------------------------------------------------------------------
    h.declare("raise", "---\nagents: |\n  rz agents/rz\nroot: rz\nschedule: 1h\n---\nA launch that raises.\n")
    begun = h.call("team", "start", "raise", "--message", "begin", *h.harnessed, "--no-tick")
    team = h.module()
    locked = bench.temp() / "locked"
    locked.mkdir()
    moved = bench.temp() / "moved.tmp"
    moved.write_text("x", encoding="utf-8")
    locked.chmod(0o555)

    def raising(*args, **kwargs):
        os.replace(moved, locked / "target")         # what a launch's preparation may meet: a target it cannot replace
        raise AssertionError("os.replace onto a read-only directory did not refuse")

    kept_env = {key: os.environ.get(key) for key in h.env}
    os.environ.update(h.env)
    raised = None
    try:
        with team.replaced("launched", raising):
            root, conductor = team.house()
            team.ticked(root, conductor, "raise")
    except Exception as error:                        # noqa: BLE001 -- what the tick let out is the case's evidence
        raised = f"{type(error).__name__}: {error}"
    finally:
        for key, value in kept_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        locked.chmod(0o755)
    found_r = h.events("raise")
    fails_r = [(one.get("house"), one.get("final"), str(one.get("reason") or "").split(":")[:2])
               for one in by_kind(found_r, "wake-failed", agent="rz")]
    told_r = [one for one in by_kind(found_r, "post", verb="notice") if one.get("house") and one.get("to") == "house"]
    kinds_r = [one.get("kind") for one in found_r]
    standing_r = team.timer_standing(h.house, "raise")
    team.disarmed(h.house, "raise")                   # the timer of an hour leaves with the case
    if (begun.returncode == 0 and raised is None and fails_r == [(True, False, ["launch-failed", " PermissionError"])]
            and len(told_r) == 1 and kinds_r.count("timer-armed") == 1 and standing_r
            and not by_kind(found_r, "wake-launched")):
        held("(g) a launch that raises is said", "the launch's PermissionError after its intent: wake-failed house: true, "
             "launch-failed: PermissionError, the house's notice to the owner; the net stands: timer-armed once, a timer stands")
    else:
        failures.append(f"  ✗ (g) a launch that raises    rc={begun.returncode} raised={raised!r} fails={fails_r} "
                        f"told={len(told_r)} kinds={kinds_r} timer={standing_r} {begun.stderr[-200:]!r}")

    # --- (h) a tick killed during a launch -----------------------------------------------------------------------------
    h.declare("killed", "---\nagents: |\n  kl kl\nroot: kl\nschedule: 5s\n---\nA tick killed during a launch.\n")
    begun_k = h.call("team", "start", "killed", "--message", "begin", *h.harnessed, "--no-tick")
    console = [sys.executable, str(h.engine), "--instance", str(h.house), "team", "tick", "killed"]
    ticking = subprocess.Popen(console, cwd=h.ws, env={**os.environ, **h.env}, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, start_new_session=True)   # a group of its own
    killed_tag, raced = None, None
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline and ticking.poll() is None:
        intent = next(iter(by_kind(h.events("killed"), "wake-intent", agent="kl")), None)
        if intent is not None:
            os.killpg(ticking.pid, signal.SIGKILL)   # the tick and its console's children, mid-launch
            killed_tag = intent.get("tag")
            raced = bool(by_kind(h.events("killed"), "wake-launched", tag=killed_tag))
            break
        time.sleep(0.01)
    ticking.wait(timeout=10)
    time.sleep(1.5)                                   # whatever outlives the kill has written
    mark_k = h.records / "teams" / "killed" / "tick.timer"
    marked_k = json.loads(mark_k.read_text(encoding="utf-8")) if mark_k.is_file() else {}
    kinds_k = [one.get("kind") for one in h.events("killed")]
    begun_at = next((one.get("at") for one in by_kind(h.events("killed"), "team-started")), None)
    in_step = False
    if marked_k.get("due") and begun_at:
        lag = (T.datetime.fromisoformat(marked_k["due"]) - T.datetime.fromisoformat(begun_at).astimezone()
               .replace(tzinfo=None)).total_seconds()
        in_step = 0 < lag <= 5 + 30
    reaped_k = h.settled("killed", lambda found: bool(
        [one for one in found if one.get("tag") == killed_tag and one.get("kind") in ("wake-failed", "wake-launched")])
        and bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=40)
    found_k = h.events("killed")
    reaped_how = [(one.get("kind"), one.get("reason")) for one in found_k
                  if one.get("tag") == killed_tag and one.get("kind") in ("wake-failed", "wake-launched")]
    h.module().disarmed(h.house, "killed")             # whatever net stands leaves with the case
    if (begun_k.returncode == 0 and killed_tag and raced is False and marked_k.get("pid") and in_step
            and kinds_k.count("timer-armed") == 1 and reaped_k and len(by_kind(found_k, "wake-launched", agent="kl")) >= 1
            and result_of(found_k, "T1") == "after the killed tick"):
        held("(h) a killed tick leaves its timer", f"the tick killed by SIGKILL of its group after kl's wake-intent, before "
             f"wake-launched: the mark stands (due {marked_k.get('due')}), timer-armed once; at its hour the timer ticks: "
             f"{reaped_how}, kl launched again, T1 done")
    else:
        failures.append(f"  ✗ (h) a killed tick           rc={begun_k.returncode} tag={killed_tag} raced={raced} "
                        f"mark={marked_k} in_step={in_step} kinds={kinds_k} reaped={reaped_k} how={reaped_how} "
                        f"result={result_of(found_k, 'T1')!r}")
    return 0
