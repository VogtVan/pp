"""Scenario `team-launch-space` -- 5 case(s) (batch pp-mort-dans-pp-workers, s.1455, team 1.14.3): a launch is
PROVEN by what the house sees -- its wake lock held --, a pid means something in its process SPACE alone, and a
member's state is read on the season that plays. The facts replayed: T22 and T23 of pp-workers, launched from a
sandbox whose process space ended with the command (pid 14 twice, a flow of 17 lines without an end), said `running`
for 19 hours, then `wake-dead final`, then `dead` after the season's start. Every launch here is FORGED on a
disposable journal -- `wake-intent`, `wake-launched {space: pid:[1]}`, a flow opened by its tag and left without an
end, no wake lock held --; the one wake-up that plays is the witness's.
- (b) the face before any tick: a launch whose wake lock is free is no wake-up under way -- `tasks[T1].running` is
  `[]`, the member's `how` is `gone`, the team is `waiting [reap]`, the line counts `running 0`
- (e) the roster before any tick: the same launch leaves the team `waiting` in `team roster --json`, never `working`
- (c) a pid of another process space is never killed: `team stop --kill` on a launch born in `pid:[1]` whose pid
  names a process group of the bench's -- the group lives, no `wake-killed`, the stop says why
- (a) the reap of a launch that ended with its process space: `wake-failed {house: true}`, `launch-failed: … process
  space …`, never final under `retries: 0`, ONE notice of the team to the owner, nobody suspected; the same tick
  launches the member in the house -- `wake-launched` says the house's own space -- and T1 ends done
- (d) the season: a member whose last launch died for good says `dead`; after `team stop` and `team start` -- a season --, with
  nothing launched since, it says `kept` -- the run kept, the dead launch of the season before no state of this one
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

from tests.harness import support

T = support(__file__, "team")

ELSEWHERE = "pid:[1]"                              # a process space no bench plays in


def here() -> str | None:
    """-> the bench's own process space, as the tick names its own; None where the system names none."""
    try:
        return os.readlink("/proc/self/ns/pid")
    except OSError:
        return None


def forged(h, name: str, agent: str, run: str, pid, space: str | None) -> str:
    """A launch forged on the team's journal for its root's `do`: the intent, its `wake-launched` -- with the
    `space` it was born in when one is given --, and a flow opened by the tag that says no end. -> the tag."""
    found = h.events(name)
    last = max(one["id"] for one in found)
    do = next(one["id"] for one in T.by_kind(found, "post", verb="do"))
    tag = f"{agent}-T1-f0f0f0"
    with h.journal_of(name).open("a", encoding="utf-8") as handle:
        for offset, line in enumerate((
                {"kind": "wake-intent", "tag": tag, "agent": agent, "task": "T1", "run": None, "messages": [do]},
                {"kind": "wake-launched", "tag": tag, "agent": agent, "run": run, "pid": pid, "launch": 1,
                 **({"space": space} if space else {})}), 1):
            handle.write(json.dumps({"at": "2026-10-03T12:00:00+00:00", "id": last + offset, "team": name, **line}) + "\n")
    flow = T.flow_file(h, f"agents/{agent}", run)
    flow.parent.mkdir(parents=True, exist_ok=True)
    with flow.open("a", encoding="utf-8") as handle:                  # opened, conducted, and nothing after
        for one in ({"kind": "opened", "exchange": 1, "agent": f"agents/{agent}", "tag": tag},
                    {"kind": "conduction", "exchange": 1, "launch": 1, "chars": 10}):
            handle.write(json.dumps({"at": "2026-10-03T12:00:01+00:00", "run": run, **one}) + "\n")
    return tag


def member(face: dict, name: str) -> dict:
    return next((one for one in face.get("members") or [] if one.get("member") == name), {})


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={"s": [{"sleep": 0.1, "body": {"done": "played in the house"}}]})
    by_kind = T.by_kind
    alone = "---\nagents: |\n  {m} agents/{m}\nroot: {m}\nretries: 0\nschedule: off\n---\nAnswer.\n"
    for name, root in (("sand", "s"), ("kil", "k"), ("sea", "d")):
        h.declare(name, alone.format(m=root))
        h.call("team", "start", name, "--message", "do it", *h.harnessed, "--no-tick")
    sleeper = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"], start_new_session=True)
    try:
        tag_s = forged(h, "sand", "s", "0f0f0f", 14, ELSEWHERE)
        forged(h, "kil", "k", "1f1f1f", sleeper.pid, ELSEWHERE)     # its pid names a group of the bench's
        forged(h, "sea", "d", "d0d0d0", None, None)

        # --- (b) the face before any tick: a launch nobody holds is no wake-up under way ---------------------
        face_b = h.face("sand")
        running_b = next((one.get("running") for one in face_b.get("tasks") or [] if one.get("id") == "T1"), None)
        line_b = next((one for one in h.face() if one.get("team") == "sand"), {})
        if (running_b == [] and member(face_b, "s").get("how") == "gone" and face_b.get("state") == "waiting"
                and face_b.get("waiting_on") == ["reap"] and line_b.get("running") == 0
                and line_b.get("state") == "waiting"):
            held("(b) a launch whose wake lock is free is no wake-up under way",
                 "tasks[T1].running [], s gone, the team waiting [reap], the line running 0")
        else:
            failures.append(f"  ✗ (b) unproven launch on the face  running={running_b} how={member(face_b, 's').get('how')} "
                            f"state={face_b.get('state')} {face_b.get('waiting_on')} line={line_b.get('running')} "
                            f"{line_b.get('state')}")

        # --- (e) the roster before any tick: the same launch is no work under way ------------------------------
        roster_e = h.call("team", "roster", "--json")
        try:
            row_e = next((one for one in json.loads(roster_e.stdout).get("teams") or [] if one.get("team") == "sand"), {})
        except ValueError:
            row_e = {}
        if roster_e.returncode == 0 and row_e.get("state") == "waiting":
            held("(e) the roster says waiting of a team whose launch nobody holds",
                 f"team roster --json: sand {row_e.get('state')}")
        else:
            failures.append(f"  ✗ (e) unproven launch on the roster  rc={roster_e.returncode} state={row_e.get('state')} "
                            f"{roster_e.stderr[-200:]!r}")

        # --- (c) a pid of another process space is never killed ---------------------------------------------
        stopped = h.call("team", "stop", "kil", "--task", "T1", "--kill")
        alive = sleeper.poll() is None
        killed_c = by_kind(h.events("kil"), "wake-killed")
        line_c = next((one.strip() for one in stopped.stdout.splitlines()
                       if ELSEWHERE in one and str(sleeper.pid) in one.split()), None)
        if stopped.returncode == 0 and alive and not killed_c and line_c:
            held("(c) a pid of another process space is never killed",
                 f"stop --kill left the group {sleeper.pid} alive, no wake-killed: {line_c}")
        else:
            failures.append(f"  ✗ (c) foreign pid killed       rc={stopped.returncode} alive={alive} "
                            f"killed={[(one.get('pid'), one.get('run')) for one in killed_c]} out={stopped.stdout.strip()[-200:]!r}")
    finally:
        if sleeper.poll() is None:
            sleeper.kill()
        sleeper.wait()

    # --- (a) the reap of a launch that ended with its process space: the house's failure, then a launch here ----
    ticked_a = h.call("team", "tick", "sand")
    done_a = h.settled("sand", lambda found: bool(by_kind(found, "done")) and T.all_ended(found), timeout=60)
    found_a = h.events("sand")
    fails_a = [(one.get("final"), one.get("house"), str(one.get("reason")), one.get("space"))
               for one in by_kind(found_a, "wake-failed")]
    notices_a = [one for one in by_kind(found_a, "post", verb="notice")]
    launches_a = by_kind(found_a, "wake-launched", agent="s")
    if (ticked_a.returncode == 0 and done_a and len(fails_a) == 1 and fails_a[0][:2] == (False, True)
            and fails_a[0][2].startswith("launch-failed:") and fails_a[0][3] == ELSEWHERE
            and len(notices_a) == 1 and notices_a[0].get("house") and not notices_a[0].get("about")
            and len(launches_a) == 2 and launches_a[1].get("space") == here() and launches_a[1].get("run") != "0f0f0f"
            and T.result_of(found_a, "T1") == "played in the house"
            and not (member(h.face("sand"), "s").get("health") or {}).get("falls")):
        held("(a) a launch that ended with its process space is the house's failure",
             f"wake-failed house, not final under retries 0 ({fails_a[0][2][:70]}…), one notice to the owner, s "
             f"launched again in {launches_a[1].get('space')} (run {launches_a[1].get('run')}), T1 done")
    else:
        failures.append(f"  ✗ (a) reap of a foreign launch  rc={ticked_a.returncode} done={done_a} fails={fails_a} "
                        f"notices={[(one.get('house'), one.get('about'), one.get('text')) for one in notices_a]} "
                        f"launches={[(one.get('run'), one.get('space')) for one in launches_a]} tag={tag_s} "
                        f"{ticked_a.stderr[-200:]!r}")

    # --- (d) the season: a launch dead in the season before is no state of this one -------------------------------
    ticked_d = h.call("team", "tick", "sea")
    fails_d = [(one.get("final"), str(one.get("reason"))) for one in by_kind(h.events("sea"), "wake-failed")]
    before_d = member(h.face("sea"), "d")
    h.call("team", "stop", "sea", "--no-tick")
    season = h.call("team", "start", "sea", *h.harnessed, "--no-tick")
    face_d = h.face("sea")
    after_d = member(face_d, "d")
    if (ticked_d.returncode == 0 and fails_d == [(True, "wake-dead")] and before_d.get("how") == "dead"
            and season.returncode == 0 and (face_d.get("season") or {}).get("n") == 2
            and after_d.get("how") == "kept" and after_d.get("run") == "d0d0d0"
            and len(by_kind(h.events("sea"), "wake-intent")) == 1):
        held("(d) a launch dead in the season before is no state of this one",
             "d dead after its final wake-dead; a season, nothing launched since: run d0d0d0 kept, how kept")
    else:
        failures.append(f"  ✗ (d) dead after a season        rc={ticked_d.returncode} fails={fails_d} "
                        f"before={before_d.get('how')} season={season.returncode}:{season.stderr[-160:]!r} "
                        f"n={(face_d.get('season') or {}).get('n')} after={after_d.get('run')} {after_d.get('how')}")
    return 0
