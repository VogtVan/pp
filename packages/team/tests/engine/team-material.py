"""Scenario `team-material` -- 2 case(s) (batch le-tick, rework, pass A, team 0.12.0; split out of
`team-review` by les-scenarios-par-maison, 2026-10-07): the material of a member.
- (g) the material of a member [54] (I13): `work: <a throwaway repository>`; T1 and T2 to wm, one
  wake-up at a time: ONE clone under `wm/work/<key>`, one line `open` then `pushed` at each wake-up at
  `workdirs.jsonl`, one branch `agent/wm/<key>` in the repository
- (h) the `work:` held (T7, I13): wh stands on T1 (its entry says two acts cut by a `§`) when T2 reaches it --
  under `work:` the tick keeps T2 until wh parks: wh is relaunched on T1 with nothing new, parks, then launched
  on T2; without `work:` (wf) T2 rides the head of the standing run's next launch, before any park
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
               "T2": [{"sleep": 2.0, "body": {"done": "second material"}}]},
        "wh": {"T1": [{"sleep": 0.3, "body": "prose"}, {"sleep": 0.1, "body": {"done": "T1 held"}}],
               "T2": [{"sleep": 0.1, "body": {"done": "T2 after the park"}}]},
        "wf": {"T1": [{"sleep": 0.3, "body": "prose"}, {"sleep": 0.1, "body": {"done": "T1 free"}}],
               "T2": [{"sleep": 0.1, "body": {"done": "T2 at the head"}}]}})
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
    

    # --- (h) the work: held for a standing run -- T7, I13 ------------------------------------------------------
    target2 = bench.temp() / "target2"
    subprocess.run(["git", "init", "-q", str(target2)], check=True)
    (target2 / "README").write_text("the second target\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(target2), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(target2), "-c", "user.name=bench", "-c", "user.email=bench@bench.local",
                    "commit", "-q", "-m", "the second target"], check=True)
    h.declare("held", f"---\nagents: |\n  wh agents/wh\nroot: wh\nparallel: 2\nwork: {target2}\nentries: |\n  do -> ACTS.md\n"
                      "schedule: off\n---\nStand, then take the next task.\n")
    h.declare("free", "---\nagents: |\n  wf agents/wf\nroot: wf\nparallel: 2\nentries: |\n  do -> ACTS.md\n"
                      "schedule: off\n---\nStand, then take the next task.\n")
    for name in ("held", "free"):
        (h.teams / name / "ACTS.md").write_text("---\nproc: |\n  INFER\n  §\n  INFER\noutput: team-act\n---\n# ACTS\n\nSay one act at each step.\n", encoding="utf-8")
    held_t = h.call("team", "start", "held", "--message", "first", *h.harnessed, "--no-tick")
    held_t2 = h.call("team", "post", "held", "--to", "wh", "--message", "second", "--no-tick")
    free_t = h.call("team", "start", "free", "--message", "first", *h.harnessed, "--no-tick")
    free_t2 = h.call("team", "post", "free", "--to", "wf", "--message", "second", "--no-tick")
    h.call("team", "tick", "held")
    h.call("team", "tick", "free")
    done_h = h.settled("held", lambda found: len(by_kind(found, "done")) == 2 and all_ended(found), timeout=120)
    done_f = h.settled("free", lambda found: len(by_kind(found, "done")) == 2 and all_ended(found), timeout=120)
    found_h, found_f = h.events("held"), h.events("free")
    order_h = [(one.get("task"), one.get("messages")) for one in by_kind(found_h, "wake-intent", agent="wh")]
    order_f = [one.get("task") for one in by_kind(found_f, "wake-intent", agent="wf")]
    parked_h = next((one["id"] for one in by_kind(found_h, "wake-ended", agent="wh") if one.get("state") == "parked"), 10 ** 9)
    parked_f = next((one["id"] for one in by_kind(found_f, "wake-ended", agent="wf") if one.get("state") == "parked"), 10 ** 9)
    t2_h = intents_on(found_h, "wh", "T2")
    t2_f = intents_on(found_f, "wf", "T2")
    if (held_t.returncode == 0 and held_t2.returncode == 0 and free_t.returncode == 0 and free_t2.returncode == 0
            and done_h and done_f and [task for task, _ in order_h[:3]] == ["T1", "T1", "T2"] and order_h[1][1] == []
            and t2_h and t2_h[0]["id"] > parked_h
            and order_f[:2] == ["T1", "T2"] and t2_f and t2_f[0]["id"] < parked_f
            and len(T.runs_launched(found_h, "wh")) == 1 and len(T.runs_launched(found_f, "wf")) == 1):
        held("(h) the work: held", f"wh under work: stands on T1, relaunched with nothing new, parks (#{parked_h}), then "
             f"T2 (#{t2_h[0]['id']}); wf without work: T2 at the head of its standing run's launch 2 (#{t2_f[0]['id']}) "
             f"before any park (#{parked_f}) -- T7, I13")
    else:
        failures.append(f"  ✗ (h) the work: held          {held_t.returncode}/{held_t2.returncode}/{free_t.returncode}/"
                        f"{free_t2.returncode} done={done_h}/{done_f} held={order_h} parked_h={parked_h} "
                        f"free={order_f} parked_f={parked_f} {held_t.stderr[-160:]!r}")
    return 0
