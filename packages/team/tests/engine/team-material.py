"""Scenario `team-material` -- 1 case(s) (batch le-tick, rework, pass A, team 0.12.0; split out of
`team-review` by les-scenarios-par-maison, 2026-10-07): the material of a member.
- (g) the material of a member [54] (I13): `work: <a throwaway repository>`; T1 and T2 to wm, one
  wake-up at a time: ONE clone under `wm/work/<key>`, one line `open` then `pushed` at each wake-up at
  `workdirs.jsonl`, one branch `agent/wm/<key>` in the repository
"""
from __future__ import annotations

import subprocess
import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "wm": {"T1": [{"sleep": 2.0, "body": {"done": "first material"}}],
               "T2": [{"sleep": 2.0, "body": {"done": "second material"}}]}})
    by_kind, all_ended, intents_on = T.by_kind, T.all_ended, T.intents_on

    # --- (g) the material of a member [54] -- I13 ------------------------------------------------------
    target = bench.temp() / "target"
    subprocess.run(["git", "init", "-q", str(target)], check=True)
    (target / "README").write_text("the target\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(target), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(target), "-c", "user.name=bench", "-c", "user.email=bench@bench.local",
                    "commit", "-q", "-m", "the target"], check=True)
    h.declare("mat", f"---\nagents: |\n  wm wm\nroot: wm\nparallel: 2\nwork: {target}\nschedule: off\n---\n"
                     "One material per member.\n")
    mat = h.call("team", "start", "mat", "--message", "first change", *h.harnessed)
    mat2 = h.call("team", "post", "mat", "--to", "wm", "--message", "second change")
    done_m = h.settled("mat", lambda found: len(by_kind(found, "done")) == 2 and all_ended(found), timeout=90)
    time.sleep(0.5)
    found_m = h.events("mat")
    rows = [one for one in T.lines(h.records / "workdirs.jsonl") if one.get("agent") == "wm"]
    opened_m = {one.get("run") for one in rows if one.get("state") == "open"}
    pushed_m = {one.get("run") for one in rows if one.get("state") == "pushed"}
    branches = [word for word in subprocess.run(["git", "-C", str(target), "branch", "--list", "agent/wm/*"],
                                                capture_output=True, text=True).stdout.split()
                if word.startswith("agent/wm/")]
    clones = {one.name for one in (h.ws / "wm" / "work").iterdir() if one.is_dir()} if (h.ws / "wm" / "work").is_dir() else set()
    t2_wm = intents_on(found_m, "wm", "T2")
    t1_end = next((one["id"] for one in by_kind(found_m, "wake-ended", agent="wm")), 10 ** 9)
    opens_m = [one for one in rows if one.get("state") == "open"]
    if (mat.returncode == 0 and mat2.returncode == 0 and done_m and len(opens_m) == 1 and len(opened_m) == 1
            and opened_m == pushed_m and branches == [f"agent/wm/{run}" for run in opened_m] and clones == opened_m
            and t2_wm and t2_wm[0]["id"] > t1_end and t2_wm[0].get("run") in opened_m):
        held("(g) a material per member", f"wm on T1 then T2, one wake-up at a time: ONE clone {sorted(clones)}, "
             f"opened once then pushed at each wake-up at workdirs.jsonl, one branch agent/wm/<key> -- I13")
    else:
        failures.append(f"  ✗ (g) the material            {mat.returncode}/{mat2.returncode} done={done_m} rows="
                        f"{[(one.get('run'), one.get('state')) for one in rows]} branches={branches} clones={clones} "
                        f"t2={[one['id'] for one in t2_wm]} t1_end={t1_end} {mat.stderr[-200:]!r}")
    return 0
