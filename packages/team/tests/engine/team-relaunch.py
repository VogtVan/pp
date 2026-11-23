"""Scenario `team-relaunch` -- 5 case(s): the house's ONE relaunch entry on the Windows façade, the refusals said on
both façades, the entry that relaunches every team that needs its net, the lines of an earlier version replaced, and
the two entries of the posix façade under WSL; every call carries `PP_CRONTAB` and `PP_RUNKEY`, never the machine's.
- (h) the Windows façade (`PP_SCHEDULER=nt`): `start` of two teams writes ONE value `pp-team-<12 hex of the house>` of
  the Run key, whose command plays `team tick --all --entry` -- the value of an earlier version, without `--entry`,
  replaced -- and keeps the PATH of the laying process at `state/relaunch.path`; the stop of one team keeps it while
  the other needs its net, the next `start` of the stopped one keeps it, `delete --yes` of the last team that needs it removes it and the kept
  PATH; no crontab line; `scheduler(system)` takes the system as a parameter
- (i) a refusal is said, the team starts: a Run key that cannot be written and a crontab that cannot be written --
  `start` rc 0, the reason on stderr, ONE notice of the team to the owner (`relaunch: true`, its `why`) through a
  `post` that tries again, the face `relaunch: false` with the reason, the timer armed all the same
- (j) the entry relaunches: the `@reboot` command played by hand on a house whose timers died ticks every team that
  needs its net -- a new timer armed for each (`timer-armed` again, a live pid at the mark) -- and leaves a team that
  needs none untouched (its journal unchanged); a team whose harness is a BARE name found only on the PATH of the
  `start` is launched by the `@reboot` command played under `PATH=/usr/bin:/bin` (`wake-launched`, the witness woken,
  no `harness-missing`): the entry takes up the PATH kept at the lay
- (k) the lines of an earlier version: a crontab holding the per-team lines of team 0.44 and the `team tick --all`
  line of team 1.14.3 for this house, another house's line and a line of the user's own -- the lay leaves ONE line for
  this house, playing `team tick --all --entry`, the other house's and the user's intact, the PATH kept
- (l) the posix façade under WSL (`PP_SCHEDULER=posix`, `WSL_DISTRO_NAME=Bench`): `start` writes the `@reboot` line AND
  the value `pp-team-<12 hex>` of the Run key, whose command opens on `wsl.exe -d Bench --exec` and ends on
  `team tick --all --entry`; the stop of the last team that needs its net removes both; without `WSL_DISTRO_NAME`, the line
  alone, no value of the Run key
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

    kept_path = h.house / ".sys" / "state" / "relaunch.path"

    def kept() -> str | None:
        return kept_path.read_text(encoding="utf-8") if kept_path.is_file() else None

    def kinds_of(name: str) -> list:
        return [one.get("kind") for one in h.events(name)]

    def notices_of(name: str) -> list[dict]:
        return [one for one in h.events(name) if one.get("kind") == "post" and one.get("relaunch")]

    for name in ("win", "refused", "cronless", "idle", "wsl", "plain", "bare"):
        h.declare(name, net_doc())
    for name in ("winrit", "rebooted"):
        h.declare(name, net_doc(RITUAL))

    # --- (h) the Windows façade: one value of the Run key for the house -----------------------------------------
    h.env["PP_SCHEDULER"] = "nt"
    earlier_w = f"{team.value_name(h.house.resolve())}\t\"pp\" team tick --all"     # the value of team 1.14.3
    h.runkey.write_text(earlier_w + "\n", encoding="utf-8")
    try:
        win1 = h.call("team", "start", "win", "--message", "on Windows", "--no-tick")
        laid_w = values()
        kept_w1 = kept()
        rit_w = h.call("team", "start", "winrit", "--no-tick")
        both_w = values()
        face_w = h.face("win")
        stop_w = h.call("team", "stop", "win", "--no-tick")
        kept_w = values()
        post_w = h.call("team", "start", "win", "--message", "again", "--no-tick")   # the next season
        back_w = values()
        h.call("team", "stop", "win", "--no-tick")
        deleted_w = h.call("team", "delete", "winrit", "--yes")
        gone_w = values()
        kept_w2 = kept()
    finally:
        del h.env["PP_SCHEDULER"]
    name_w, command_w = laid_w[0] if len(laid_w) == 1 else ("", "")
    if (win1.returncode == 0 and len(laid_w) == 1 and name_w.startswith("pp-team-") and len(name_w) == len("pp-team-") + 12
            and command_w.endswith("team tick --all --entry") and kept_w1 == os.environ["PATH"]
            and kept_w2 is None and rit_w.returncode == 0 and both_w == laid_w
            and face_w.get("schedule", {}).get("relaunch") is True and house_lines() == []
            and stop_w.returncode == 0 and kept_w == laid_w and post_w.returncode == 0 and back_w == laid_w
            and deleted_w.returncode == 0 and gone_w == []
            and team.scheduler("nt") == "nt" and team.scheduler("posix") == "posix"):
        held("(h) the Windows façade", f"PP_SCHEDULER=nt: one value {name_w} of the Run key playing `team tick --all "
             "--entry` for win and winrit, the value of 1.14.3 replaced, the PATH kept at state/relaunch.path; the stop "
             "of win kept it under winrit's ceremony, a post kept it, delete --yes of winrit removed it and the kept "
             "PATH; no crontab line")
    else:
        failures.append(f"  ✗ (h) nt façade              {win1.returncode}/{rit_w.returncode}/{stop_w.returncode}/"
                        f"{post_w.returncode}/{deleted_w.returncode} laid={laid_w} both={both_w} kept={kept_w} "
                        f"back={back_w} gone={gone_w} kept={kept_w1 is not None}/{kept_w2 is not None} "
                        f"face={face_w.get('schedule')!r} {win1.stderr[-200:]!r}")

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
    shelf = bench.temp()                                  # the harness by a BARE name, on the PATH of the start alone
    bare_name = "pp-bench-harness"
    (shelf / bare_name).write_text(f"#!/bin/sh\nexec {h.harness} \"$@\"\n", encoding="utf-8")
    (shelf / bare_name).chmod(0o755)
    h.env["PATH"] = f"{shelf}{os.pathsep}{os.environ['PATH']}"
    try:
        bare = h.call("team", "start", "bare", "--message", "by a bare name", "--harness", bare_name,
                      *h.harnessed[2:], "--no-tick")
    finally:
        del h.env["PATH"]
    line_b, kept_b = house_lines(), kept()                # read at the lay: the team's end removes both
    played_b = None
    if len(line_b) == 1:
        command_b = line_b[0].split(" ", 1)[1].split(" >/dev/null")[0]
        played_b = subprocess.run(["env", "PATH=/usr/bin:/bin", "sh", "-c", command_b], capture_output=True, text=True,
                                  cwd=h.ws, env={**os.environ, **h.env})
    gone_b = ("wake-failed", "wake-refused", "wake-dead")
    h.settled("bare", lambda found: any(one.get("kind") in ("wake-ended", *gone_b) for one in found), 30)
    kinds_b = kinds_of("bare")
    missing_b = [one for one in h.events("bare") if "harness-missing" in team.json.dumps(one)]
    if (bare.returncode == 0 and len(line_b) == 1 and played_b is not None and played_b.returncode == 0
            and "wake-launched" in kinds_b and "wake-ended" in kinds_b and not set(gone_b) & set(kinds_b)
            and not missing_b
            and kept_b is not None and str(shelf) in kept_b.split(os.pathsep)):
        held("(j) the entry takes up the kept PATH", f"the harness `{bare_name}` found on the PATH of the start alone: "
             "the @reboot command played under PATH=/usr/bin:/bin launched the member (wake-launched then wake-ended, nothing failed, "
             "refused or dead, no harness-missing)")
    else:
        failures.append(f"  ✗ (j) the kept PATH          rc={bare.returncode} line={line_b} "
                        f"played={played_b and (played_b.returncode, played_b.stderr[-300:])!r} kinds={kinds_b} "
                        f"missing={missing_b[-1:]} kept={kept_b!r}")
    h.call("team", "stop", "bare", "--no-tick")

    # --- (k) the lines of an earlier version, replaced at the lay -------------------------------------------------
    earlier = [f"@reboot python pp.py --instance {h2} team tick win >/dev/null 2>&1 # pp-team {h2} win",
               f"@reboot python pp.py --instance {h2} team tick idle >/dev/null 2>&1 # pp-team {h2} idle",
               f"@reboot python pp.py --instance {h2} team tick --all >/dev/null 2>&1 # pp-team {h2}",
               f"@reboot python pp.py --instance {h2}2 team tick --all >/dev/null 2>&1 # pp-team {h2}2",
               "0 3 * * * the user's own line"]
    h.crontab.write_text("\n".join(earlier) + "\n", encoding="utf-8")
    relaid = h.call("team", "start", "win", "--message", "back on Linux", "--no-tick")
    kept_k = table()
    if (relaid.returncode == 0 and len(house_lines()) == 1 and earlier[3] in kept_k and earlier[4] in kept_k
            and earlier[2] not in kept_k and "team tick --all --entry " in house_lines()[0]
            and kept() == os.environ["PATH"]
            and not any(one.endswith(f"# pp-team {h2} win") or one.endswith(f"# pp-team {h2} idle") for one in kept_k)):
        held("(k) the lines of an earlier version", "the per-team lines of 0.44 and the line of 1.14.3 of this house "
             "replaced by its one line playing `team tick --all --entry`, the PATH kept; the other house's line and "
             "the user's own kept")
    else:
        failures.append(f"  ✗ (k) the earlier lines       rc={relaid.returncode} table={kept_k} {relaid.stderr[-200:]!r}")

    # --- (l) the posix façade under WSL: the crontab's line and the Run key's value --------------------------------
    h.call("team", "stop", "win", "--no-tick")                                  # no team of the house needs its net
    before_l = (house_lines(), values())
    h.env.update({"PP_SCHEDULER": "posix", "WSL_DISTRO_NAME": "Bench"})
    try:
        wsl = h.call("team", "start", "wsl", "--message", "under WSL", "--no-tick")
        lines_l, values_l = house_lines(), values()
        face_l = h.face("wsl")
        stop_l = h.call("team", "stop", "wsl", "--no-tick")
        gone_l = (house_lines(), values())
        gone_kept = kept()
        h.env["WSL_DISTRO_NAME"] = ""                                           # outside WSL: the variable unset
        plain = h.call("team", "start", "plain", "--message", "on Linux", "--no-tick")
        lines_p, values_p = house_lines(), values()
        h.call("team", "stop", "plain", "--no-tick")
    finally:
        del h.env["PP_SCHEDULER"], h.env["WSL_DISTRO_NAME"]
    name_l, command_l = values_l[0] if len(values_l) == 1 else ("", "")
    if (before_l == ([], []) and wsl.returncode == 0 and len(lines_l) == 1 and lines_l[0].startswith("@reboot ")
            and "team tick --all --entry " in lines_l[0] and name_l.startswith("pp-team-")
            and len(name_l) == len("pp-team-") + 12 and command_l.startswith("wsl.exe -d Bench --exec ")
            and command_l.endswith("team tick --all --entry") and h2 in command_l
            and face_l.get("schedule", {}).get("relaunch") is True
            and stop_l.returncode == 0 and gone_l == ([], []) and gone_kept is None
            and plain.returncode == 0 and len(lines_p) == 1 and values_p == []):
        held("(l) the posix façade under WSL", f"WSL_DISTRO_NAME=Bench: start laid the @reboot line and the value "
             f"{name_l} `{command_l[:24]}… team tick --all --entry`; the stop of the last team removed both and "
             "the kept PATH; without "
             "WSL_DISTRO_NAME the line alone, no value")
    else:
        failures.append(f"  ✗ (l) WSL                    {wsl.returncode}/{stop_l.returncode}/{plain.returncode} "
                        f"before={before_l} lines={lines_l} values={values_l} face={face_l.get('schedule')!r} "
                        f"gone={gone_l}/{gone_kept is not None} plain={lines_p}/{values_p} {wsl.stderr[-200:]!r}")
    return 0
