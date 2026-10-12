"""Scenario `team-watch` -- 2 case(s) (batch le-suivi-de-l-equipe, 2026-10-01; split out of
`team-review` by les-scenarios-par-maison, 2026-10-07): a team followed from outside.
- `team watch --for 25 --json --heartbeat 1` started before `team start watched` (v -> v1 v2) follows the team on stderr:
  the journal's events as they arrive, the steps of each wake-up under way prefixed by its agent and
  run, `no event for <n>s`; the team ends as without a watch (4 wake-ups, done)
- a watch on a team at rest writes nothing: the journal's bytes and its directory unchanged after
  `watch --for 2`; `--until-done` leaves at once; `watch` without a name says the usage
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
        "v": [{"sleep": 0.2, "body": {"do": ["v1", "v2"]}}, {"sleep": 0.2, "body": {"done": "watched"}}],
        "v1": [{"sleep": 2.0, "body": {"done": True}}],
        "v2": [{"sleep": 2.0, "body": {"done": True}}]})
    all_ended = T.all_ended

    # --- watch follows a team from its start: the events, the steps, the quiet ----------------------
    h.declare("watched", "---\nagents: |\n  v v\n  v1 v1\n  v2 v2\nreports: |\n  v1 v2 -> v\nroot: v\n---\nWatched.\n")
    watch_err = bench.temp() / "watch.err"
    with watch_err.open("w", encoding="utf-8") as handle:
        watcher = subprocess.Popen([sys.executable, str(h.engine), "--instance", str(h.house), "team", "watch", "watched",
                                    "--for", "25", "--json", "--heartbeat", "1"],   # the bench's load: a window wide enough
                                   cwd=str(h.ws), env={**os.environ, **h.env}, stdout=subprocess.PIPE, stderr=handle, text=True)
    time.sleep(0.5)
    watched = h.call("team", "start", "watched", "--message", "watch me", *h.harnessed)
    done_w = h.settled("watched", lambda found: any(one.get("kind") == "done" for one in found) and all_ended(found), timeout=60)
    watcher_out, _ = watcher.communicate(timeout=60)
    seen = []
    for line in watch_err.read_text(encoding="utf-8").splitlines():
        try:
            seen.append(json.loads(line))
        except ValueError:
            seen.append({"unparsed": line})
    journal_events = [one.get("event") for one in seen if one.get("team") == "watched" and one.get("event") != "quiet"]
    steps = [(one.get("agent"), one.get("event")) for one in seen if one.get("agent") and "team" not in one]
    quiet = [one for one in seen if one.get("event") == "quiet"]
    found = h.events("watched")
    if (watched.returncode == 0 and done_w and watcher.returncode == 0 and watcher_out == ""
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
        failures.append(f"  ✗ watch                       rc={watched.returncode}/{watcher.returncode} done={done_w} "
                        f"out={watcher_out!r} events={journal_events} steps={steps} quiet={len(quiet)} "
                        f"{watch_err.read_text(encoding='utf-8')[-400:]!r} {watched.stderr[-200:]!r}")

    # --- a watch at rest writes nothing; --until-done leaves at once ------------------------------------
    journal = h.journal_of("watched")
    before_w = journal.read_bytes()
    locks_before = sorted(one.name for one in journal.parent.iterdir())
    started_at = time.monotonic()
    resting = h.call("team", "watch", "watched", "--for", "2")
    took_rest = time.monotonic() - started_at
    started_at = time.monotonic()
    until = h.call("team", "watch", "watched", "--until-done")       # watched is done: nothing open, nothing under way
    took_until = time.monotonic() - started_at
    nameless = h.call("team", "watch")
    if (resting.returncode == 0 and 1.5 <= took_rest < 4 and journal.read_bytes() == before_w
            and sorted(one.name for one in journal.parent.iterdir()) == locks_before
            and until.returncode == 0 and took_until < 1.0 and journal.read_bytes() == before_w
            and nameless.returncode == 2 and "usage" in (nameless.stderr + nameless.stdout).lower()):
        held("a watch at rest writes nothing", f"watch --for 2 took {took_rest:.1f}s, the journal's bytes and the "
             f"directory unchanged; --until-done on the done team left in {took_until:.2f}s; watch without a name: the usage")
    else:
        failures.append(f"  ✗ watch at rest               {resting.returncode}/{until.returncode}/{nameless.returncode} "
                        f"took={took_rest:.1f}/{took_until:.2f} same={journal.read_bytes() == before_w} "
                        f"{resting.stderr[-200:]!r} {until.stderr[-200:]!r}")
    return 0
