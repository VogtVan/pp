"""Scenario `team-relaunch` -- 4 case(s): the house's ONE relaunch entry on the Windows façade, the refusals said on
both façades, the entry that relaunches every team that needs its net, and the lines of an earlier version replaced;
every call carries `PP_CRONTAB` and `PP_RUNKEY`, never the machine's.
- (h) the Windows façade (`PP_SCHEDULER=nt`): `start` of two teams writes ONE value `pp-team-<12 hex of the house>` of
  the Run key, whose command plays `team tick --all`; the stop of one team keeps it while the other needs its net, a
  `post` keeps it, `delete --yes` of the last team that needs it removes it; no crontab line; `scheduler(system)` takes
  the system as a parameter
- (i) a refusal is said, the team starts: a Run key that cannot be written and a crontab that cannot be written --
  `start` rc 0, the reason on stderr, ONE notice of the team to the owner (`relaunch: true`, its `why`) through a
  `post` that tries again, the face `relaunch: false` with the reason, the timer armed all the same
- (j) the entry relaunches: the `@reboot` command played by hand on a house whose timers died ticks every team that
  needs its net -- a new timer armed for each (`timer-armed` again, a live pid at the mark) -- and leaves a team that
  needs none untouched (its journal unchanged)
- (k) the lines of an earlier version: a crontab holding the per-team lines of team 0.44 for this house, another
  house's line and a line of the user's own -- the lay leaves ONE line for this house, the other house's and the user's
  intact
"""
from __future__ import annotations

import os
import signal

import subprocess
import time

from tests.harness import support

T = support(__file__, "team")

CRASH_THEN_RECOVER = [{"sleep": 0.1, "body": "crash"}, {"sleep": 0.1, "body": {"re": "DO", "text": "recovered"}}]
RITUAL = "ceremonies: |\n  daily every weekday 09:30 with s -> s\n"


def net_doc(extra: str = "") -> str:
    return f"---\nagents: |\n  s s\nroot: s\n{extra}---\nA net under one agent.\n"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={"f": CRASH_THEN_RECOVER, "g": CRASH_THEN_RECOVER})
    h2 = str(h.house.resolve())
    team = h.module()

    def table() -> list[str]:
        return h.crontab.read_text(encoding="utf-8").splitlines() if h.crontab.is_file() else []

    def house_lines() -> list[str]:
        return [one for one in table() if one.endswith(f"# pp-team {h2}")]

    def values() -> list[tuple[str, str]]:
        said = h.runkey.read_text(encoding="utf-8").splitlines() if h.runkey.is_file() else []
        return [tuple(one.split("\t", 1)) for one in said if "\t" in one]

    def kinds_of(name: str) -> list:
        return [one.get("kind") for one in h.events(name)]

    def notices_of(name: str) -> list[dict]:
        return [one for one in h.events(name) if one.get("kind") == "post" and one.get("relaunch")]

    for name in ("win", "refused", "cronless", "idle"):
        h.declare(name, net_doc())
    for name in ("winrit", "rebooted"):
        h.declare(name, net_doc(RITUAL))

    # --- (h) the Windows façade: one value of the Run key for the house -----------------------------------------
    h.env["PP_SCHEDULER"] = "nt"
    try:
        win1 = h.call("team", "start", "win", "--message", "on Windows", "--no-tick")
        laid_w = values()
        rit_w = h.call("team", "start", "winrit", "--no-tick")
        both_w = values()
        face_w = h.face("win")
        stop_w = h.call("team", "stop", "win", "--no-tick")
        kept_w = values()
        post_w = h.call("team", "post", "win", "--message", "again", "--no-tick")
        back_w = values()
        h.call("team", "stop", "win", "--no-tick")
        deleted_w = h.call("team", "delete", "winrit", "--yes")
        gone_w = values()
    finally:
        del h.env["PP_SCHEDULER"]
    name_w, command_w = laid_w[0] if len(laid_w) == 1 else ("", "")
    if (win1.returncode == 0 and len(laid_w) == 1 and name_w.startswith("pp-team-") and len(name_w) == len("pp-team-") + 12
            and command_w.endswith("team tick --all") and rit_w.returncode == 0 and both_w == laid_w
            and face_w.get("schedule", {}).get("relaunch") is True and house_lines() == []
            and stop_w.returncode == 0 and kept_w == laid_w and post_w.returncode == 0 and back_w == laid_w
            and deleted_w.returncode == 0 and gone_w == []
            and team.scheduler("nt") == "nt" and team.scheduler("posix") == "posix"):
        held("(h) the Windows façade", f"PP_SCHEDULER=nt: one value {name_w} of the Run key playing `team tick --all` for "
             "win and winrit; the stop of win kept it under winrit's ceremony, a post kept it, delete --yes of winrit "
             "removed it; no crontab line")
    else:
        failures.append(f"  ✗ (h) nt façade              {win1.returncode}/{rit_w.returncode}/{stop_w.returncode}/"
                        f"{post_w.returncode}/{deleted_w.returncode} laid={laid_w} both={both_w} kept={kept_w} "
                        f"back={back_w} gone={gone_w} face={face_w.get('schedule')!r} {win1.stderr[-200:]!r}")

    # --- (i) a refusal is said, the team starts ------------------------------------------------------------------
    keyless = bench.temp()                                     # a directory: the Run key's witness cannot be written
    h.env.update({"PP_SCHEDULER": "nt", "PP_RUNKEY": str(keyless)})
    try:
        refused = h.call("team", "start", "refused", "--message", "no key", *h.harnessed)
        face_r = h.face("refused")
        again_r = h.call("team", "post", "refused", "--message", "still no key", "--no-tick")
    finally:
        del h.env["PP_SCHEDULER"]
        h.env["PP_RUNKEY"] = str(h.runkey)
    nowhere = h.crontab
    h.env["PP_CRONTAB"] = str(bench.temp())                 # a directory: the crontab cannot be written
    try:
        cronless = h.call("team", "start", "cronless", "--message", "no cron", "--no-tick")
        face_c = h.face("cronless")
    finally:
        h.env["PP_CRONTAB"] = str(nowhere)
    told_r, told_c = notices_of("refused"), notices_of("cronless")
    why_r = told_r[0].get("why") if told_r else ""
    if (refused.returncode == 0 and why_r and why_r in refused.stderr and again_r.returncode == 0 and why_r in again_r.stderr
            and len(told_r) == 1 and told_r[0].get("verb") == "notice" and not told_r[0].get("about")
            and face_r.get("schedule", {}).get("relaunch") is False
            and face_r.get("schedule", {}).get("reason") == why_r and "timer-armed" in kinds_of("refused")
            and cronless.returncode == 0 and len(told_c) == 1 and face_c.get("schedule", {}).get("relaunch") is False
            and face_c.get("schedule", {}).get("reason") == told_c[0].get("why") and told_c[0].get("why")):
        held("(i) a refusal is said, the team starts", "nt with a Run key that cannot be written: start rc 0, the reason "
             "on stderr twice, ONE notice (relaunch, its why, no about), the face relaunch false with the reason, "
             "timer-armed; posix with an unwritable crontab: rc 0, one notice, the face says why")
    else:
        failures.append(f"  ✗ (i) the refusal            {refused.returncode}/{again_r.returncode}/{cronless.returncode} "
                        f"told={told_r}/{told_c} face={face_r.get('schedule')!r}/{face_c.get('schedule')!r} "
                        f"kinds={kinds_of('refused')} {refused.stderr[-200:]!r}")
    h.call("team", "stop", "refused", "--no-tick")
    h.call("team", "stop", "cronless", "--no-tick")

    # --- (j) the entry relaunches every team that needs its net ----------------------------------------------------
    first = h.call("team", "start", "rebooted", *h.harnessed, now="08:00")     # a ceremony: a deadline stands
    h.call("team", "start", "idle", "--message", "nothing", "--no-tick")
    h.call("team", "stop", "idle", "--no-tick")                                 # idle needs no net any more
    idle_before = kinds_of("idle")
    mark_j = h.records / "teams" / "rebooted" / "tick.timer"
    stood = team.json.loads(mark_j.read_text(encoding="utf-8")) if mark_j.is_file() else {}
    if stood.get("pid"):
        os.kill(int(stood["pid"]), signal.SIGKILL)          # the machine stopped: the timer died, its mark left behind
        time.sleep(0.3)
    line_j = house_lines()
    replayed = None
    if len(line_j) == 1:
        command_j = line_j[0].split(" ", 1)[1].split(" >/dev/null")[0]
        replayed = subprocess.run(["sh", "-c", command_j], capture_output=True, text=True, cwd=h.ws,
                                  env={**os.environ, **h.env, "PP_NOW": T.THURSDAY + "08:00"})
    after_j = team.json.loads(mark_j.read_text(encoding="utf-8")) if mark_j.is_file() else {}
    armed_j = kinds_of("rebooted").count("timer-armed")
    if (first.returncode == 0 and stood.get("pid") and len(line_j) == 1 and "team tick --all" in line_j[0]
            and replayed is not None and replayed.returncode == 0
            and armed_j == 2 and after_j.get("pid") not in (None, stood.get("pid")) and team.alive(int(after_j["pid"]))
            and kinds_of("idle") == idle_before):
        held("(j) the entry relaunches", "the timer killed, its mark stale: the house's @reboot command `team tick --all` "
             "played by hand ticked rebooted -- a new timer armed (timer-armed twice, a live pid) -- and left idle, "
             "which needs no net, untouched")
    else:
        failures.append(f"  ✗ (j) the relaunch           rc={first.returncode} stood={stood} line={line_j} "
                        f"replayed={replayed and (replayed.returncode, replayed.stderr[-200:])!r} armed={armed_j} "
                        f"after={after_j} idle={kinds_of('idle')}/{idle_before}")
    h.call("team", "delete", "rebooted", "--yes")

    # --- (k) the lines of an earlier version, replaced at the lay -------------------------------------------------
    earlier = [f"@reboot python pp.py --instance {h2} team tick win >/dev/null 2>&1 # pp-team {h2} win",
               f"@reboot python pp.py --instance {h2} team tick idle >/dev/null 2>&1 # pp-team {h2} idle",
               f"@reboot python pp.py --instance {h2}2 team tick --all >/dev/null 2>&1 # pp-team {h2}2",
               "0 3 * * * the user's own line"]
    h.crontab.write_text("\n".join(earlier) + "\n", encoding="utf-8")
    relaid = h.call("team", "post", "win", "--message", "back on Linux", "--no-tick")
    kept_k = table()
    if (relaid.returncode == 0 and len(house_lines()) == 1 and earlier[2] in kept_k and earlier[3] in kept_k
            and not any(one.endswith(f"# pp-team {h2} win") or one.endswith(f"# pp-team {h2} idle") for one in kept_k)):
        held("(k) the lines of an earlier version", "the per-team lines of this house replaced by its one line; the "
             "other house's line and the user's own kept")
    else:
        failures.append(f"  ✗ (k) the earlier lines       rc={relaid.returncode} table={kept_k} {relaid.stderr[-200:]!r}")
    return 0
