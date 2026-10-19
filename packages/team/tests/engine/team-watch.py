"""Scenario `team-watch` -- 4 case(s): a team followed from outside. Two teams on one house, `watched`
(v -> v1 v2) and `steps` (s -> s1 s2, T1 resolved, then T2 posted to s1); three watches started before
either team starts -- `--json --heartbeat 1` on `watched`, `--json` and text on `steps` --, each ended once
what its case reads is written.
- `team watch --json --heartbeat 1` started before `team start watched` follows the team on stderr: the
  journal's events as they arrive, the steps of each wake-up under way with its agent and run, `quiet`
  lines with their seconds; nothing on stdout; the team ends as without a watch (4 wake-ups, done)
- a watch on a team at rest writes nothing: the journal's bytes and its directory unchanged after
  `watch --for 2`; `--until-done` leaves at once; `watch` without a name refuses with the usage (exit 2)
- under `--json`, each step of a wake-up carries the `task`, the `tag` and the `index` of its `wake-intent`,
  field for field; the steps on T2 are s1's alone
- the text watch's lines of steps carry the agent, the run and the step, and no task, tag or index
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

# A text line of a step: `[HH:MM:SS] <agent> · <run> · <step>` -- the agent, the run, what the step is.
STEP_LINE = re.compile(r"^\[\d\d:\d\d:\d\d\] (s|s1|s2) · ([^ ·]+) · (.*)$")


def read_json(path) -> list[dict]:
    """-> the JSON lines a watch wrote, a line that is not JSON kept as `{"unparsed": line}`."""
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


def ended(watcher: subprocess.Popen) -> tuple[bool, str]:
    """Terminates a watch still running -> (whether it was running, what it wrote on stdout)."""
    running = watcher.poll() is None
    watcher.terminate()
    out, _ = watcher.communicate(timeout=30)
    return running, out


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "v": [{"sleep": 0.2, "body": {"do": ["v1", "v2"]}}, {"sleep": 0.2, "body": {"done": "watched"}}],
        "v1": [{"sleep": 2.0, "body": {"done": True}}],
        "v2": [{"sleep": 2.0, "body": {"done": True}}],
        "s": [{"sleep": 0.2, "body": {"do": ["s1", "s2"]}}, {"sleep": 0.2, "body": {"done": "first"}}],
        "s1": [{"sleep": 0.5, "body": {"done": True}}, {"sleep": 0.5, "body": {"done": "second"}}],
        "s2": [{"sleep": 0.5, "body": {"done": True}}]})
    all_ended = T.all_ended
    h.declare("watched", "---\nagents: |\n  v v\n  v1 v1\n  v2 v2\nreports: |\n  v1 v2 -> v\nroot: v\n---\nWatched.\n")
    h.declare("steps", "---\nagents: |\n  s s\n  s1 s1\n  s2 s2\nreports: |\n  s1 s2 -> s\nroot: s\n---\nSteps.\n")

    # --- the watches, started before the teams --------------------------------------------------------
    def watching(name: str, path, *flags: str) -> subprocess.Popen:
        with path.open("w", encoding="utf-8") as handle:
            return subprocess.Popen([sys.executable, str(h.engine), "--instance", str(h.house), "team", "watch", name,
                                     "--for", "60", *flags],                  # a bound past any wait: each is terminated
                                    cwd=str(h.ws), env={**os.environ, **h.env}, stdout=subprocess.PIPE, stderr=handle,
                                    text=True)
    watch_err = bench.temp() / "watch.err"
    files = {mode: bench.temp() / f"watch-{mode}.err" for mode in ("json", "text")}
    watcher = watching("watched", watch_err, "--json", "--heartbeat", "1")
    steppers = [watching("steps", files["json"], "--json", "--heartbeat", "5"),
                watching("steps", files["text"], "--heartbeat", "5")]
    # the watch of `watched` says its first `quiet` once its loop runs: the watches read before the teams start
    ready = waited(lambda: any(one.get("event") == "quiet" for one in read_json(watch_err)), timeout=15)
    time.sleep(0.3)
    watched = h.call("team", "start", "watched", "--message", "watch me", *h.harnessed)
    started = h.call("team", "start", "steps", "--message", "first", *h.harnessed)

    # --- watch follows a team from its start: the events, the steps, the quiet ----------------------
    done_w = h.settled("watched", lambda found: any(one.get("kind") == "done" for one in found) and all_ended(found),
                       timeout=60)

    def quiet_after_done() -> bool:
        seen = read_json(watch_err)
        at = next((n for n, one in enumerate(seen) if one.get("event") == "done"), None)
        return at is not None and any(one.get("event") == "quiet" for one in seen[at:])
    said_w = waited(quiet_after_done, timeout=20)
    running_w, watcher_out = ended(watcher)
    seen = read_json(watch_err)
    journal_events = [one.get("event") for one in seen if one.get("team") == "watched" and one.get("event") != "quiet"]
    steps = [(one.get("agent"), one.get("event")) for one in seen if one.get("agent") and "team" not in one]
    quiet = [one for one in seen if one.get("event") == "quiet"]
    found = h.events("watched")
    if (ready and watched.returncode == 0 and done_w and said_w and running_w and watcher_out == ""
            and not any("unparsed" in one for one in seen)
            and all({"at", "event"} <= set(one) for one in seen)
            and journal_events[:3] == ["team-started", "task", "post"]
            and "wake-intent" in journal_events and "wake-launched" in journal_events and "done" in journal_events
            and ("v1", "new") in steps and ("v2", "new") in steps and ("v", "block") in steps
            and steps.count(("v", "new")) == 1                       # v's second wake-up resumed its run: no second opening
            and all(one.get("run") for one in seen if one.get("agent") and "team" not in one)
            and quiet and all(one.get("seconds") for one in quiet)
            and any(one.get("kind") == "done" and one.get("result") == "watched" for one in found)
            and sum(1 for one in found if one.get("kind") == "wake-intent") == 4):
        held("watch follows a team from its start", f"{len(seen)} JSON line(s) on stderr: the journal's events "
             f"({len(journal_events)}), the steps of v, v1, v2 ({len(steps)}), {len(quiet)} quiet line(s); the team "
             "ended as without a watch: 4 wake-ups, done")
    else:
        failures.append(f"  ✗ watch                       rc={watched.returncode} ready={ready} done={done_w} "
                        f"said={said_w} running={running_w} out={watcher_out!r} events={journal_events} steps={steps} "
                        f"quiet={len(quiet)} {watch_err.read_text(encoding='utf-8')[-400:]!r} {watched.stderr[-200:]!r}")

    # --- a watch at rest writes nothing; --until-done leaves at once ------------------------------------
    journal = h.journal_of("watched")
    before_w = journal.read_bytes()
    locks_before = sorted(one.name for one in journal.parent.iterdir())
    started_at = time.monotonic()
    resting = h.call("team", "watch", "watched", "--for", "2")       # its subject is the natural end of `--for`
    took_rest = time.monotonic() - started_at
    started_at = time.monotonic()
    until = h.call("team", "watch", "watched", "--until-done")       # watched is done: nothing open, nothing under way
    took_until = time.monotonic() - started_at
    nameless = h.call("team", "watch")
    refusal = nameless.stderr.removeprefix("pp-team: ").split(" ", 1)[0].rstrip(":")   # the refusal's code word
    if (resting.returncode == 0 and 1.5 <= took_rest < 4 and journal.read_bytes() == before_w
            and sorted(one.name for one in journal.parent.iterdir()) == locks_before
            and until.returncode == 0 and took_until < 1.0 and journal.read_bytes() == before_w
            and nameless.returncode == 2 and nameless.stdout == "" and refusal == "usage"):
        held("a watch at rest writes nothing", f"watch --for 2 took {took_rest:.1f}s, the journal's bytes and the "
             f"directory unchanged; --until-done on the done team left in {took_until:.2f}s; watch without a name: the usage")
    else:
        failures.append(f"  ✗ watch at rest               {resting.returncode}/{until.returncode}/{nameless.returncode} "
                        f"took={took_rest:.1f}/{took_until:.2f} same={journal.read_bytes() == before_w} "
                        f"refusal={refusal!r} {resting.stderr[-200:]!r} {until.stderr[-200:]!r}")

    # --- each step under --json says its task, tag and index ------------------------------------------
    first = h.settled("steps", lambda found: any(one.get("kind") == "done" and one.get("task") == "T1" for one in found)
                      and all_ended(found), timeout=60)
    posted = h.call("team", "post", "steps", "--to", "s1", "--message", "second")
    second = h.settled("steps", lambda found: any(one.get("kind") == "done" and one.get("task") == "T2" for one in found)
                       and all_ended(found), timeout=60)
    done_t2 = next((one["id"] for one in T.by_kind(h.events("steps"), "done", task="T2")), None)

    def json_read() -> bool:                                         # T2's done said, and a step of T2 with it
        seen_s = read_json(files["json"])
        return (any(one.get("event") == "done" and one.get("task") == "T2" for one in seen_s)
                and any(one.get("agent") and "team" not in one and one.get("task") == "T2" for one in seen_s))

    def text_read() -> bool:                                         # the text watch has said T2's done event
        return any(f"steps · #{done_t2} done " in one for one in files["text"].read_text(encoding="utf-8").splitlines())
    read_s = waited(lambda: json_read() and text_read(), timeout=20)
    time.sleep(0.4)                                                  # the steps a loop of the watch writes after the event
    ends_s = [ended(one) for one in steppers]
    seen_s = [one for one in read_json(files["json"]) if "unparsed" not in one]
    found_s = h.events("steps")
    intents = {one["tag"]: one for one in T.by_kind(found_s, "wake-intent")}
    steps_s = [one for one in seen_s if one.get("agent") and "team" not in one]
    wrong = [one for one in steps_s if one.get("tag") not in intents
             or (one.get("task"), one.get("index")) != (intents[one["tag"]].get("task"), intents[one["tag"]].get("index"))
             or intents[one["tag"]].get("agent") != one.get("agent")]
    on_t2 = {one.get("agent") for one in steps_s if one.get("task") == "T2"}
    if (started.returncode == 0 and posted.returncode == 0 and first and second and read_s and steps_s and not wrong
            and all(running and out == "" for running, out in ends_s)
            and on_t2 == {"s1"} and {one.get("task") for one in steps_s} == {"T1", "T2"}):
        held("each step says its task, tag and index", f"{len(steps_s)} step(s) of {len(intents)} wake-up(s), each the "
             f"fields of its wake-intent; T2's steps s1's alone")
    else:
        failures.append(f"  ✗ steps                       rc={started.returncode}/{posted.returncode} first={first} "
                        f"second={second} read={read_s} ends={ends_s} steps={len(steps_s)} wrong={wrong[:3]} "
                        f"on_t2={on_t2} {files['json'].read_text(encoding='utf-8')[-600:]!r}")

    # --- the text of watch carries none of them -----------------------------------------------------
    runs = {one.get("run") for one in T.by_kind(found_s, "wake-launched")}
    marks = set(intents) | {one.get("task") for one in intents.values()}   # every tag and task of the journal
    text = files["text"].read_text(encoding="utf-8").splitlines()
    step_lines = [STEP_LINE.match(one) for one in text if STEP_LINE.match(one)]
    if (step_lines and all(one.group(2) in runs for one in step_lines)
            and not any(" · " in one.group(3) and one.group(3).split(" · ")[-1] != "parked" for one in step_lines)
            and not any(mark in re.split(r"[\s·]+", one.group(3)) for one in step_lines for mark in marks)):
        held("the text of watch says none of them", f"{len(step_lines)} line(s) of steps, as before")
    else:
        failures.append(f"  ✗ text                        {len(step_lines)} {[one.group(0) for one in step_lines[:3]]}")
    return 0
