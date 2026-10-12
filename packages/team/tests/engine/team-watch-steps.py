"""Scenario `team-watch-steps` -- 2 case(s) (batch la-tache-des-pas of plan ui, 2026-10-11: team 0.28.0): under
`--json`, each step of a wake-up `team watch` writes says the `task`, the `tag` and the `index` of the intent of
the wake-up it follows; the text of `watch` says none of them. A team `v -> v1 v2` resolves T1, then T2 is posted
to `v1`; two watches, `--json` and text, started before `team start`.
- the steps of every wake-up carry the fields of their `wake-intent`, field for field; those of `v1`'s wake-up on
  T2 say `T2`
- the text watch's lines of steps carry neither `task` nor `tag`
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "v": [{"sleep": 0.2, "body": {"do": ["v1", "v2"]}}, {"sleep": 0.2, "body": {"done": "first"}}],
        "v1": [{"sleep": 0.5, "body": {"done": True}}, {"sleep": 0.5, "body": {"done": "second"}}],
        "v2": [{"sleep": 0.5, "body": {"done": True}}]})
    h.declare("steps", "---\nagents: |\n  v v\n  v1 v1\n  v2 v2\nreports: |\n  v1 v2 -> v\nroot: v\n---\nSteps.\n")
    files = {mode: bench.temp() / f"watch-{mode}.err" for mode in ("json", "text")}
    watchers = []
    for mode, path in files.items():
        with path.open("w", encoding="utf-8") as handle:
            watchers.append(subprocess.Popen(
                [sys.executable, str(h.engine), "--instance", str(h.house), "team", "watch", "steps", "--for", "25",
                 *(["--json"] if mode == "json" else []), "--heartbeat", "5"],
                cwd=str(h.ws), env={**os.environ, **h.env}, stdout=subprocess.PIPE, stderr=handle, text=True))
    time.sleep(0.5)
    started = h.call("team", "start", "steps", "--message", "first", *h.harnessed)
    first = h.settled("steps", lambda found: any(one.get("kind") == "done" and one.get("task") == "T1" for one in found)
                      and T.all_ended(found), timeout=60)
    posted = h.call("team", "post", "steps", "--to", "v1", "--message", "second")
    second = h.settled("steps", lambda found: any(one.get("kind") == "done" and one.get("task") == "T2" for one in found)
                       and T.all_ended(found), timeout=60)
    for one in watchers:
        one.terminate()
        one.communicate(timeout=30)
    seen = []
    for line in files["json"].read_text(encoding="utf-8").splitlines():
        try:
            seen.append(json.loads(line))
        except ValueError:
            pass
    intents = {one["tag"]: one for one in T.by_kind(h.events("steps"), "wake-intent")}
    steps = [one for one in seen if one.get("agent") and "team" not in one]
    wrong = [one for one in steps if one.get("tag") not in intents
             or (one.get("task"), one.get("index")) != (intents[one["tag"]].get("task"), intents[one["tag"]].get("index"))
             or intents[one["tag"]].get("agent") != one.get("agent")]
    on_t2 = {one.get("agent") for one in steps if one.get("task") == "T2"}
    if (started.returncode == 0 and posted.returncode == 0 and first and second and steps and not wrong
            and on_t2 == {"v1"} and {one.get("task") for one in steps} == {"T1", "T2"}):
        held("each step says its task, tag and index", f"{len(steps)} step(s) of {len(intents)} wake-up(s), each the "
             f"fields of its wake-intent; T2's steps v1's alone")
    else:
        failures.append(f"  ✗ steps                       rc={started.returncode}/{posted.returncode} first={first} "
                        f"second={second} steps={len(steps)} wrong={wrong[:3]} on_t2={on_t2} "
                        f"{files['json'].read_text(encoding='utf-8')[-600:]!r}")

    text = files["text"].read_text(encoding="utf-8").splitlines()
    step_lines = [one for one in text if any(f"] {agent} · " in one for agent in ("v", "v1", "v2"))]
    if step_lines and not any("task" in one or "tag" in one or "index" in one for one in step_lines):
        held("the text of watch says none of them", f"{len(step_lines)} line(s) of steps, as before")
    else:
        failures.append(f"  ✗ text                        {len(step_lines)} {step_lines[:3]}")
    return 0
