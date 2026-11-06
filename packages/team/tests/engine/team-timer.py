"""Scenario `team-timer` -- 5 case(s): the TIMER is a team's net at every step of `schedule:` (team 0.44.0), and its
life and launch are chosen by system; every call carries `PP_CRONTAB` and `PP_RUNKEY`, never the machine's.
- (e) `schedule: 1s` and `schedule: 2m` with `timeout: 1` -- the root dies at its first launch (no `--on-end` for a
  dead harness), the start's tick armed a timer (`timer-armed {due}`), which ticks without any call: under 1s the
  member suspected one second and tried by a relance, under 2m the dead launch caught at its `timeout:` and retried;
  T1 done, `schedule-off`, the mark `tick.timer` gone, no timer process alive, the house's relaunch entry gone once neither needs it
- `schedule:` is declared: `2` is 120 s and lays the house's relaunch entry, `off` lays nothing more (`team-started.schedule`
  null, the face's `schedule` all null), `soon` refuses `team-invalid` (rc 2), nothing written
- (f) the grammar of `schedule:`: `2m` 120 s, `5` 300 s, `30s` 30 s, `90s` 90 s, `1h` 3 600 s, the house's one entry
  laid; `0s` and `2h30` refuse `team-invalid`, nothing written (batch les-equipes-au-poste: the hours)
- (g) the timer's life and launch by system (batch les-lancements-sous-windows, team 0.43.1): `alive(pid, "posix")` says
  a witness process alive, then dead once it ended; `alive(pid, "nt")` never calls `os.kill` (which ends the process
  under Windows) and gives the system's answer; `apart("nt")` a hidden console in its own group, no
  `DETACHED_PROCESS`; `apart("posix")` a session of its own
- (h) the timer knows itself by its token (batch le-minuteur-sous-windows, team 0.46.1): a timer spawned behind one more
  process -- `sh -c '<the console> team timer … --token <t> ; :'`, the mark naming the `sh`, as uv's launcher stands
  under Windows -- sleeps its second and ticks: the mark taken, the member woken, no `team timer` left; a timer whose
  mark carries another token leaves without ticking, the mark kept; `team timer` without `--token` is the usage
"""
from __future__ import annotations

import os
import signal
import sys

import subprocess
import time

from tests.harness import support

T = support(__file__, "team")

CRASH_THEN_RECOVER = [{"sleep": 0.1, "body": "crash"}, {"sleep": 0.1, "body": {"re": "DO", "text": "recovered"}}]
REFUSED = "access-denied"
RITUAL = "ceremonies: |\n  daily every weekday 09:30 with s -> s\n"


def net_doc(extra: str = "") -> str:
    return f"---\nagents: |\n  s s\nroot: s\n{extra}---\nA net under one agent.\n"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={"f": CRASH_THEN_RECOVER, "g": CRASH_THEN_RECOVER})
    h2 = str(h.house.resolve())
    by_kind, all_ended = T.by_kind, T.all_ended
    team = h.module()

    def table() -> list[str]:
        return h.crontab.read_text(encoding="utf-8").splitlines() if h.crontab.is_file() else []

    def house_lines() -> list[str]:
        return [one for one in table() if one.endswith(f"# pp-team {h2}")]

    def kinds_of(name: str) -> list:
        return [one.get("kind") for one in h.events(name)]

    def notices_of(name: str) -> list[dict]:
        return [one for one in h.events(name) if one.get("kind") == "post" and one.get("relaunch")]

    def timer_gone(name: str) -> bool:
        mark = h.records / "teams" / name / "tick.timer"
        gone_at = time.monotonic() + 10                # the tick that follows the end disarms the timer: the mark leaves
        while time.monotonic() < gone_at and mark.exists():
            time.sleep(0.2)
        alive = subprocess.run(["pgrep", "-f", f"timer {name} --sleep"], capture_output=True, text=True).stdout.strip()
        return not mark.exists() and not alive

    h.declare("quick", "---\nagents: |\n  f agents/f\nroot: f\nretries: 0\nschedule: 1s\n---\nThe net under the minute.\n")
    h.declare("slow", "---\nagents: |\n  g agents/g\nroot: g\nretries: 1\ntimeout: 1\nschedule: 2m\n---\n"
                      "The net at two minutes.\n")
    for name, value in (("twomin", "2m"), ("bare", "5"), ("thirty", "30s"), ("ninety", "90s"), ("hour", "1h"),
                        ("zero", "0s"), ("twohalf", "2h30")):
        h.declare(name, net_doc(f"schedule: {value}\n"))
    h.declare("every2", net_doc("schedule: 2\n"))
    h.declare("offteam", net_doc("schedule: off\n"))
    h.declare("soonteam", net_doc("schedule: soon\n"))
    quick = h.call("team", "start", "quick", "--message", "catch me", *h.harnessed)
    slow = h.call("team", "start", "slow", "--message", "catch me later", *h.harnessed)

    # --- (e) the timer at every step ----------------------------------------------------------------------------
    caught = {}
    for name, member, launch, step, tries in (("quick", "f", quick, 1, [None, "tried"]), ("slow", "g", slow, 120, [None, None])):
        begun = next((one for one in h.events(name) if one.get("kind") == "team-started"), {})
        over_t = h.settled(name, lambda found, name=name: bool(by_kind(found, "done", task="T1"))
                           and bool(by_kind(found, "schedule-off")) and all_ended(found), timeout=40)
        found_t = h.events(name)
        failed = [one for one in found_t if one.get("kind") == "wake-failed" and one.get("agent") == member]
        parts = {"rc": launch.returncode == 0, "step": begun.get("schedule") == step and begun.get("unit") == "s",
                 "over": over_t, "armed": "timer-armed" in [one.get("kind") for one in found_t], "failed": len(failed) == 1,
                 "tries": [one.get("relance") for one in T.intents_of(found_t, member)] == tries,
                 "result": T.result_of(found_t, "T1") == "recovered", "gone": timer_gone(name)}
        caught[name] = all(parts.values()) or {one for one, ok in parts.items() if not ok}
    entry_gone = h.settled("slow", lambda found: house_lines() == [], timeout=20)
    if all(one is True for one in caught.values()) and entry_gone:
        held("(e) the timer at every step", "1s: the dead launch reaped, the root tried by the timer's ticks; 2m with "
             "timeout 1: the dead launch caught at its timeout and retried -- no call, T1 'recovered', schedule-off, "
             "the entry, the mark and the process gone")
    else:
        failures.append(f"  ✗ (e) the timer              {caught} entry_gone={entry_gone} quick={kinds_of('quick')} slow={kinds_of('slow')} "
                        f"{quick.stderr[-160:]!r} {slow.stderr[-160:]!r}")

    fast = h.call("team", "start", "every2", "--message", "quick net", "--no-tick")
    off = h.call("team", "start", "offteam", "--message", "no net", "--no-tick")
    soon = h.call("team", "start", "soonteam", "--message", "bad net", "--no-tick")

    # --- schedule: declares the step, off and a bad value ------------------------------------------
    fast_started = next((one for one in h.events("every2") if one.get("kind") == "team-started"), {})
    off_started = next((one for one in h.events("offteam") if one.get("kind") == "team-started"), {})
    off_face = h.face("offteam")
    if (fast.returncode == 0 and len(house_lines()) == 1
            and fast_started.get("schedule") == 120 and fast_started.get("unit") == "s"
            and off.returncode == 0
            and "schedule" in off_started and off_started.get("schedule") is None
            and off_face.get("schedule") == {"seconds": None, "timer": None, "relaunch": None, "reason": None}
            and soon.returncode == 2 and "team-invalid" in soon.stderr
            and not h.journal_of("soonteam").exists() and len(house_lines()) == 1):
        held("schedule: declares the step", "2 is 120 s (unit s) and lays the house's entry; off lays nothing more, schedule null, "
             "the face's schedule all null; soon refuses team-invalid, nothing written")
    else:
        failures.append(f"  ✗ schedule key                {fast.returncode}/{off.returncode}/{soon.returncode} "
                        f"lines={house_lines()} started={fast_started.get('schedule')!r}/{off_started.get('schedule')!r} "
                        f"face={off_face.get('schedule')!r} {soon.stderr[-200:]!r}")

    # --- (f) the grammar of schedule: -----------------------------------------------------------------------------
    grammar = {name: h.call("team", "start", name, "--message", "x", "--no-tick")
               for name in ("twomin", "bare", "thirty", "ninety", "hour", "zero", "twohalf")}
    kept_g = {name: next((one.get("schedule") for one in h.events(name) if one.get("kind") == "team-started"), "∅")
              for name in grammar}
    read = ("twomin", "bare", "thirty", "ninety", "hour")
    if (all(grammar[name].returncode == 0 for name in read) and len(house_lines()) == 1
            and [kept_g[name] for name in read] == [120, 300, 30, 90, 3600]
            and all(grammar[name].returncode == 2 and "team-invalid" in grammar[name].stderr
                    and not h.journal_of(name).exists() for name in ("zero", "twohalf"))):
        held("(f) the grammar of schedule:", "2m 120 s, 5 300 s, 30s 30 s, 90s 90 s, 1h 3600 s, the house's one entry laid; "
             "0s and 2h30 refuse team-invalid")
    else:
        failures.append(f"  ✗ (f) the grammar            rc={[(name, one.returncode) for name, one in grammar.items()]} "
                        f"kept={kept_g} {grammar['zero'].stderr[-120:]!r} {grammar['twohalf'].stderr[-120:]!r}")

    # --- (g) the timer's life and launch by system -----------------------------------------------------------------
    witness = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    lived = team.alive(witness.pid, "posix")
    witness.kill()
    witness.wait()
    dead = team.alive(witness.pid, "posix")
    signalled, asked = [], []
    kill, system = team.os.kill, team.asked_alive
    team.os.kill = lambda pid, sig: signalled.append((pid, sig))
    team.asked_alive = lambda pid: asked.append(pid) or pid == 4242
    try:
        windows = (team.alive(4242, "nt"), team.alive(4343, "nt"))
    finally:
        team.os.kill, team.asked_alive = kill, system
    hidden, own = team.apart("nt"), team.apart("posix")
    flags = hidden.get("creationflags", 0)
    if (lived and not dead and windows == (True, False) and asked == [4242, 4343] and not signalled
            and set(hidden) == {"creationflags"} and flags & 0x08000000 and flags & 0x00000200 and not flags & 0x00000008
            and own == {"start_new_session": True}):
        held("(g) the timer's life and launch by system", "posix: the witness alive, then dead; nt: the system asked "
             "twice, os.kill never called; apart(nt) CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP without DETACHED_PROCESS, "
             "apart(posix) start_new_session")
    else:
        failures.append(f"  ✗ (g) by system              posix={lived}/{dead} nt={windows} asked={asked} signalled={signalled} "
                        f"apart={hidden}/{own}")

    # --- (h) the timer knows itself by its token ------------------------------------------------------------------
    for name in ("behind", "replaced"):
        h.declare(name, f"---\nagents: |\n  {name[0]}m agents/{name[0]}m\nroot: {name[0]}m\nschedule: off\n---\nOne task.\n")
        h.call("team", "start", name, "--message", "tick me", *h.harnessed, "--no-tick")
    console = f"{sys.executable} {h.engine} --instance {h.house}"

    def spawned(name: str, token: str, marked: str) -> subprocess.Popen:
        """A timer behind one more process, its mark naming that process and carrying `marked`."""
        due = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time() + 1))
        shell = subprocess.Popen(["sh", "-c", f"{console} team timer {name} --sleep 1 --due {due} --token {token} ; :"],
                                 cwd=h.ws, env={**os.environ, **h.env}, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
        mark = h.records / "teams" / name / "tick.timer"
        mark.write_text(team.json.dumps({"pid": shell.pid, "due": due, "token": marked}), encoding="utf-8")
        return shell

    shells = {"behind": spawned("behind", "a1b2c3d4e5f60718", "a1b2c3d4e5f60718"),
              "replaced": spawned("replaced", "a1b2c3d4e5f60718", "ffffffffffffffff")}
    ends = {}
    for name, shell in shells.items():
        try:
            ends[name] = shell.wait(timeout=20)
        except subprocess.TimeoutExpired:
            shell.kill()
            ends[name] = None
    behind_mark = (h.records / "teams" / "behind" / "tick.timer").exists()
    replaced_mark = team.json.loads((h.records / "teams" / "replaced" / "tick.timer").read_text(encoding="utf-8"))
    woken = {name: bool(by_kind(h.events(name), "wake-intent")) for name in shells}
    settled_h = h.settled("behind", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 30)
    left = subprocess.run(["pgrep", "-f", "timer (behind|replaced) --sleep"], capture_output=True, text=True).stdout.strip()
    bare = h.call("team", "timer", "behind", "--sleep", "1", "--due", "2026-10-01T09:00:00")
    if (ends == {"behind": 0, "replaced": 0} and not behind_mark and woken == {"behind": True, "replaced": False}
            and settled_h and replaced_mark.get("token") == "ffffffffffffffff" and not left
            and bare.returncode == 2):
        held("(h) the timer knows itself by its token", "behind a sh the mark names: slept, ticked -- the mark taken, bm "
             "woken, T1 done, no team timer left; another token at the mark: left without ticking, the mark kept; "
             "no --token: the usage")
    else:
        failures.append(f"  ✗ (h) the token              ends={ends} mark={behind_mark} replaced={replaced_mark} "
                        f"woken={woken} settled={settled_h} left={left!r} bare={bare.returncode} {bare.stderr[-160:]!r}")
    return 0
