"""Scenario `team-watch-activity` -- 2 case(s) (batch ui/le-poste-vivant/la-sequence-vivante, team 0.50.0): the watch
relays the ACTIVITY of the wake-ups it follows -- what the harness does between two blocks, read from the run's flow
by `agent flow --follow`, one object `event: activity` per `tool`, `tool-result`, `thinking`, `words`, `context`.
- (a) the watch relays the activity: a wake-up of `a` on T1 calls four tools -- one answered by 10 kB, one in error --,
  thinks, then answers; `watch --json` says one `activity` per call, per result, for the thought, the words and the
  calls measured, each with the `task`, the `tag` and the `launch` of the wake-up it follows, a result by its size and
  never its content, no text longer than `ACTIVITY_TEXT`; the text watch says one line per activity
- (b) the relay is bounded: fifty calls in a burst give at most `ACTIVITY_RATE` objects per second, the surplus folded
  into the last one said (`more`), every event accounted for; the `context` objects always pass
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time

from tests.harness import support

T = support(__file__, "team")

BIG = "x" * 10240                         # a result of 10 kB: said by its size, never its content
CALLS = [{"name": "Read", "input": {"file_path": "pp.py"}, "result": "def main", "sleep": 1.0},
         {"name": "Bash", "input": {"command": "ls"}, "result": BIG, "sleep": 1.0},
         {"name": "Grep", "input": {"pattern": "watch"}, "result": "nothing", "error": True, "sleep": 1.0},
         {"name": "Write", "input": {"file_path": "a.md", "content": "y" * 300}, "result": "written", "sleep": 1.0}]
ACTIVITY_LINE = re.compile(r"^\[\d\d:\d\d:\d\d\] a · (\S+) · (tool|result|thinking|words|context)\b(.*)$")


def constant(path, name: str) -> int:
    """-> the value of an integer constant of the script at `path`, read from its source."""
    found = re.search(rf"^{name} = (\d+)", path.read_text(encoding="utf-8"), re.M)
    return int(found.group(1)) if found else -1


def read_json(path) -> list[dict]:
    seen = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            seen.append(json.loads(line))
        except ValueError:
            seen.append({"unparsed": line})
    return seen


def waited(predicate, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.1)
    return False


def ended(watcher: subprocess.Popen) -> str:
    watcher.terminate()
    out, _ = watcher.communicate(timeout=30)
    return out


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "a": [{"sleep": 0.2, "calls": CALLS, "thought": "the price first, then the rest", "body": {"done": "read"}}],
        "b": [{"sleep": 0.2, "calls": [{"name": "Read", "input": {"file_path": f"f{n}.py"}, "result": "ok"}
                                       for n in range(50)], "body": {"done": "burst"}}]})
    rate, chars = constant(h.team_module(), "ACTIVITY_RATE"), constant(h.team_module(), "ACTIVITY_TEXT")
    h.declare("acts", "---\nagents: |\n  a a\nroot: a\nschedule: off\n---\nActs.\n")
    h.declare("burst", "---\nagents: |\n  b b\nroot: b\nschedule: off\n---\nBurst.\n")

    def watching(name: str, path, *flags: str) -> subprocess.Popen:
        with path.open("w", encoding="utf-8") as handle:
            return subprocess.Popen([sys.executable, str(h.engine), "--instance", str(h.house), "team", "watch", name,
                                     "--for", "60", *flags], cwd=str(h.ws), env={**os.environ, **h.env},
                                    stdout=subprocess.PIPE, stderr=handle, text=True)
    files = {name: bench.temp() / f"watch-{name}.err" for name in ("acts", "text", "burst")}
    watchers = [watching("acts", files["acts"], "--json", "--heartbeat", "1"), watching("acts", files["text"]),
                watching("burst", files["burst"], "--json", "--heartbeat", "1")]
    ready = waited(lambda: any(one.get("event") == "quiet" for one in read_json(files["acts"]))
                   and any(one.get("event") == "quiet" for one in read_json(files["burst"])), timeout=15)
    started = h.call("team", "start", "acts", "--message", "read the PR", *h.harnessed)
    burst = h.call("team", "start", "burst", "--message", "burst", *h.harnessed)
    done_a = h.settled("acts", lambda found: any(one.get("kind") == "done" for one in found) and T.all_ended(found),
                       timeout=60)
    done_b = h.settled("burst", lambda found: any(one.get("kind") == "done" for one in found) and T.all_ended(found),
                       timeout=60)
    said_a = waited(lambda: any(one.get("event") == "done" for one in read_json(files["acts"]))
                    and any(one.get("event") == "quiet" for one in read_json(files["acts"])[-1:]), timeout=20)
    said_b = waited(lambda: any(one.get("event") == "done" for one in read_json(files["burst"]))
                    and any(one.get("event") == "quiet" for one in read_json(files["burst"])[-1:]), timeout=20)
    outs = [ended(one) for one in watchers]

    # --- (a) the watch relays the activity --------------------------------------------------------------------------
    seen = read_json(files["acts"])
    found = h.events("acts")
    intents = {one["tag"]: one for one in T.by_kind(found, "wake-intent")}
    launches = {one["tag"]: one for one in T.by_kind(found, "wake-launched")}
    acts = [one for one in seen if one.get("event") == "activity"]
    kinds = {}
    for one in acts:
        kinds[one.get("kind")] = kinds.get(one.get("kind"), 0) + 1
    wrong = [one for one in acts if one.get("tag") not in intents or one.get("task") != "T1" or one.get("agent") != "a"
             or one.get("launch") != (launches.get(one.get("tag")) or {}).get("launch")
             or one.get("run") != (launches.get(one.get("tag")) or {}).get("run")]
    results = [one for one in acts if one.get("kind") == "tool-result"]
    tools = [one for one in acts if one.get("kind") == "tool"]
    big = [one for one in results if int(one.get("size") or 0) >= len(BIG)]
    long = [one for one in acts if any(isinstance(value, str) and len(value) > chars for value in one.values())]
    text_lines = [ACTIVITY_LINE.match(one) for one in files["text"].read_text(encoding="utf-8").splitlines()]
    text_lines = [one for one in text_lines if one]
    if (ready and started.returncode == 0 and done_a and said_a and outs[0] == "" and outs[1] == ""
            and not any("unparsed" in one for one in seen) and not wrong
            and kinds.get("tool") == 4 and kinds.get("tool-result") == 4 and kinds.get("thinking") == 1
            and kinds.get("words", 0) >= 1 and kinds.get("context", 0) >= 4
            and [one.get("name") for one in tools] == [one["name"] for one in CALLS]
            and all(one.get("title") for one in tools)
            and not any("content" in one for one in results) and len(big) == 1
            and [bool(one.get("error")) for one in results] == [bool(one.get("error")) for one in CALLS]
            and not long and all({"at", "agent", "run", "event", "kind", "task", "tag", "launch"} <= set(one) for one in acts)
            and len(text_lines) >= len(acts) - 2 and {one.group(2) for one in text_lines} >= {"tool", "result", "thinking", "context"}):
        held("(a) the watch relays the activity", f"{len(acts)} activity object(s): {kinds}; each the task, tag, launch "
             f"and run of its wake-up; the 10 kB result by its size, no content; no text over {chars}; "
             f"{len(text_lines)} text line(s)")
    else:
        failures.append(f"  ✗ (a) relays the activity     rc={started.returncode} ready={ready} done={done_a} "
                        f"said={said_a} outs={outs[:2]!r} kinds={kinds} wrong={wrong[:2]} big={len(big)} long={len(long)} "
                        f"results={[(one.get('size'), one.get('error')) for one in results]} "
                        f"tools={[one.get('name') for one in tools]} text={len(text_lines)} "
                        f"{files['acts'].read_text(encoding='utf-8')[-600:]!r}")

    # --- (b) the relay is bounded -----------------------------------------------------------------------------------
    seen = read_json(files["burst"])
    acts = [one for one in seen if one.get("event") == "activity"]
    bounded = [one for one in acts if one.get("kind") != "context"]
    contexts = [one for one in acts if one.get("kind") == "context"]
    by_second: dict[str, int] = {}
    for one in bounded:
        by_second[str(one.get("at"))] = by_second.get(str(one.get("at")), 0) + 1
    accounted = len(bounded) + sum(int(one.get("more") or 0) for one in bounded)
    expected = 50 * 2 + 1                                 # fifty calls, their results, the words of the answer
    if (burst.returncode == 0 and done_b and said_b and outs[2] == "" and bounded and contexts
            and max(by_second.values()) <= rate and len(bounded) < expected // 2
            and bounded[-1].get("more") and accounted == expected and len(contexts) == 50):
        held("(b) the relay is bounded", f"{expected} events of the burst: {len(bounded)} object(s) said, at most "
             f"{max(by_second.values())} in one second (rate {rate}), the last with more {bounded[-1].get('more')}, "
             f"all accounted for; {len(contexts)} context object(s) passed")
    else:
        failures.append(f"  ✗ (b) bounded                 rc={burst.returncode} done={done_b} said={said_b} "
                        f"out={outs[2]!r} said={len(bounded)} per_second={by_second} last={bounded[-1:] } "
                        f"accounted={accounted}/{expected} contexts={len(contexts)} "
                        f"{files['burst'].read_text(encoding='utf-8')[-400:]!r}")
    return 0
