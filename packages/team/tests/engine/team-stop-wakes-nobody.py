"""Scenario `team-stop-wakes-nobody` -- 1 case(s) (batch l-equipe-au-reel, 2026-10-02, and the
rework of l-attente, I9; split out of `team-review` by les-scenarios-par-maison, 2026-10-07): a
team stopped when nobody can move.
- a stop wakes nobody: a root failed for good -- nobody holds T1 --, then `team stop` -- `stopped`,
  no stop post, `nobody held it`, no intent after it, `status` says `T1 · stopped`, and `team start`
  starts the team again (I9, the rework of `l-attente`); a root under way and its delegate at rest,
  then `team stop` -- `stopped` before its posts, the wake-up under way ends routed nowhere, no
  intent after it, no `waits` said on the stopped task; `watch --until-done` leaves
  at once on an open task where nothing runs and nothing is due
"""
from __future__ import annotations

import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "se": [{"sleep": 0.1, "body": "crash"},
               {"sleep": 0.1, "body": "crash"}],
        "sg": [{"sleep": 0.1, "body": {"do": ["sg1"]}},
               {"sleep": 4.0, "body": {"done": "late"}}],
        "sg1": [{"sleep": 0.1, "body": {"ask": {"to": "sg", "text": "which branch?"}}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    def intents_after(name: str, after: int) -> list[dict]:
        return [one for one in by_kind(h.events(name), "wake-intent") if one.get("id", 0) > after]

    # --- a stop wakes nobody; watch --until-done leaves when nothing can move ------------------------
    h.declare("halted", "---\nagents: |\n  se se\nroot: se\nschedule: off\n---\nStop me.\n")
    halted = h.call("team", "start", "halted", "--message", "say it", *h.harnessed)
    final_s = h.settled("halted", lambda found: bool(by_kind(found, "wake-failed", final=True)) and all_ended(found), timeout=60)
    time.sleep(0.5)
    begun_w = time.monotonic()
    until = h.call("team", "watch", "halted", "--until-done", "--for", "10")
    took_w = time.monotonic() - begun_w
    stopped_s = h.call("team", "stop", "halted", "--task", "T1")
    stop_event = next(iter(by_kind(h.events("halted"), "stopped", task="T1")), {})
    stop_id = stop_event.get("id", 0)                # no `stopped`: the case counts from the start, never vacuously
    time.sleep(1.5)
    after_s = intents_after("halted", stop_id)
    posts_s = by_kind(h.events("halted"), "post", verb="stop")
    status_s = next((one.get("state") for one in h.face("halted").get("tasks") or [] if one.get("id") == "T1"), None)
    h.declare("rest", "---\nagents: |\n  sg sg\n  sg1 sg1\nreports: |\n  sg1 -> sg\nroot: sg\n---\nStop under way.\n")
    rest = h.call("team", "start", "rest", "--message", "work slowly", *h.harnessed)
    asking = h.settled("rest", lambda found: len(by_kind(found, "wake-launched", agent="sg")) >= 2, timeout=60)
    stopped_g = h.call("team", "stop", "rest", "--task", "T1")
    found_g = h.events("rest")
    stop_g_event = next(iter(by_kind(found_g, "stopped", task="T1")), {})
    stop_g = stop_g_event.get("id", 0)
    posts_g = [one for one in by_kind(found_g, "post", verb="stop")]
    quiet_g = h.settled("rest", all_ended, timeout=30)
    time.sleep(1.0)
    found_g = h.events("rest")
    sg_face = next((one for one in h.face("rest").get("members") or [] if one.get("member") == "sg"), {})
    again_s = h.call("team", "start", "halted", "--message", "say it again", *h.harnessed)
    redone_s = h.settled("halted", lambda found: bool(by_kind(found, "done", task="T2")) and all_ended(found), timeout=60)
    if (halted.returncode == 0 and final_s and stopped_s.returncode == 0
            and stop_event.get("task") == "T1" and posts_s == [] and after_s == []
            and status_s == "stopped"
            and again_s.returncode == 0 and redone_s
            and until.returncode == 0 and took_w < 3.0
            and rest.returncode == 0 and asking and stopped_g.returncode == 0 and quiet_g
            and stop_g_event.get("task") == "T1" and posts_g and all(one["id"] > stop_g for one in posts_g)
            and intents_after("rest", stop_g) == []
            and len(by_kind(found_g, "wake-ended", agent="sg")) == 2 and not by_kind(found_g, "done")
            and sg_face.get("waits") == []):
        held("a stop wakes nobody", f"a root failed for good, nobody holds T1, then stop: stopped #{stop_id}, no stop "
             f"post, no intent after, the face's T1 stopped, team start again resolves T2; a root "
             f"under way and its delegate at rest, then stop: stopped #{stop_g} before its posts, the wake-up ends "
             f"routed nowhere, no intent after, sg waits on nobody; watch --until-done left in {took_w:.1f}s -- I9")
    else:
        failures.append(f"  ✗ stop without wake-up        {halted.returncode}/{stopped_s.returncode}/{rest.returncode}/"
                        f"{stopped_g.returncode}/{again_s.returncode} final={final_s} asking={asking} quiet={quiet_g} "
                        f"stopped={stop_event}/{stop_g_event} posts_s={len(posts_s)} redone={redone_s} "
                        f"after_s={[one['agent'] for one in after_s]} "
                        f"after_g={[one['agent'] for one in intents_after('rest', stop_g)]} "
                        f"{stopped_s.stdout[-160:]!r} {again_s.stderr[-160:]!r} "
                        f"watch={until.returncode}/{took_w:.1f}s sg={sg_face} T1={status_s} done={by_kind(found_g, 'done')}")
    return 0
