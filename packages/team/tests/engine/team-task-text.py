"""Scenario `team-task-text` -- 3 case(s) (batch le-texte-des-taches of plan ui, 2026-10-11: team 0.27.0):
`team status <name> --json` says each task's `text` -- the text of its `task` event -- and its `last`
`{id, kind, at}`, the last event of the task as `team log --task` keeps them (`of_task`): an event that
names it, or a launch, an end or a failure of an intent it opened. A team `crew` (m root, r1 reporting to
m, `daily every weekday 09:30 with r1 -> m`), the clock frozen by `PP_NOW` on Thursday 2026-10-01.
- the text and the last: T1 at its start says the message of `start` and its `do` post as `last`; once
  resolved, its `last` is still the last object `log --json --task T1` gives, its wake-ups among them
- the snapshot: T2 opened, `team snapshot`, then every task's `text` and `last` as before; a note on T2
  after it moves T2's `last` to that note, T1's stays
- the ring: a daily rung at hand -- its task says the ring's consigne as `text`, the task event's, and
  its `last` is the last object of its log
"""
from __future__ import annotations

import json

from tests.harness import cli, support

T = support(__file__, "team")

CREW = ("---\nagents: |\n  m agents/m\n  r1 agents/r1\nreports: |\n  r1 -> m\nroot: m\n"
        "ceremonies: |\n  daily every weekday 09:30 with r1 -> m\n---\nShip together.\n")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "m": [{"sleep": 0.1, "body": {"do": ["r1"]}}, {"sleep": 0.1, "body": {"done": "shipped"}}],
        "r1": [{"sleep": 0.1, "body": {"done": True}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    def objects(*args: str, when: str) -> list[dict]:
        played = cli(h.engine, "--instance", str(h.house), "team", *args, cwd=h.ws, env={**h.env, "PP_NOW": when})
        try:
            return [json.loads(line) for line in played.stdout.splitlines() if line.strip()]
        except ValueError:
            return []

    def tasks(when: str) -> dict:
        found = objects("status", "crew", "--json", when=when)
        return {one.get("id"): one for one in (found[0] if found else {}).get("tasks") or []}

    def logged_last(task: str, when: str) -> dict | None:
        found = objects("log", "crew", "--json", "--task", task, when=when)
        return {"id": found[-1].get("id"), "kind": found[-1].get("event"), "at": found[-1].get("at")} if found else None

    h.declare("crew", CREW)

    # --- the text and the last ---------------------------------------------------------------------
    started = h.call("team", "start", "crew", "--message", "ship the release notes", *h.harnessed, "--no-tick",
                     now="09:10")
    first = tasks("2026-10-01T09:10").get("T1") or {}
    first_log = logged_last("T1", "2026-10-01T09:10")
    ticked = h.call("team", "tick", "crew", now="09:15")
    done = h.settled("crew", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    after = tasks("2026-10-01T09:20").get("T1") or {}
    after_log = logged_last("T1", "2026-10-01T09:20")
    kinds = [one.get("event") for one in objects("log", "crew", "--json", "--task", "T1", when="2026-10-01T09:20")]
    if (started.returncode == 0 and first.get("text") == "ship the release notes" and first_log is not None
            and first.get("last") == first_log and first_log["kind"] == "post"
            and ticked.returncode == 0 and done and after.get("state") == "resolved"
            and after.get("text") == "ship the release notes" and after.get("last") == after_log
            and "wake-ended" in kinds and after_log["id"] > first_log["id"]):
        held("the text and the last", f"T1 says its message; last #{first_log['id']} post at its start, "
             f"#{after_log['id']} {after_log['kind']} once resolved -- the log's last each time")
    else:
        failures.append(f"  ✗ the text and the last       rc={started.returncode}/{ticked.returncode} done={done} "
                        f"first={first} first_log={first_log} after={after} after_log={after_log} kinds={kinds} "
                        f"{started.stderr[-200:]!r}")

    # --- the snapshot ------------------------------------------------------------------------------
    opened = h.call("team", "post", "crew", "--message", "draft the changelog", "--no-tick", now="09:25")
    before = tasks("2026-10-01T09:26")
    snapped = h.call("team", "snapshot", "crew", now="09:27")
    kept = tasks("2026-10-01T09:28")
    noted = h.call("team", "post", "crew", "--task", "T2", "--message", "mind the dates", "--no-tick", now="09:29")
    note_id = max((e["id"] for e in by_kind(h.events("crew"), "post", task="T2")), default=-1)
    moved = tasks("2026-10-01T09:29")
    same = {key: (one.get("text"), one.get("last")) for key, one in before.items()} == \
        {key: (one.get("text"), one.get("last")) for key, one in kept.items()}
    if (opened.returncode == 0 and snapped.returncode == 0 and noted.returncode == 0 and same
            and (before.get("T2") or {}).get("text") == "draft the changelog"
            and ((moved.get("T2") or {}).get("last") or {}).get("id") == note_id
            and (moved.get("T2") or {}).get("last") == logged_last("T2", "2026-10-01T09:29")
            and (moved.get("T1") or {}).get("last") == (before.get("T1") or {}).get("last")):
        held("the snapshot", f"T1 and T2 the same text and last across it; the note #{note_id} on T2 after it "
             "is T2's last, T1's unmoved")
    else:
        failures.append(f"  ✗ the snapshot                rc={opened.returncode}/{snapped.returncode}/{noted.returncode} "
                        f"same={same} before={before} kept={kept} moved={moved} note={note_id} "
                        f"{snapped.stderr[-200:]!r}")

    # --- the ring ----------------------------------------------------------------------------------
    rung = h.call("team", "ring", "crew", "daily", "--no-tick", now="09:31")
    found = h.events("crew")
    ring_event = next((e for e in reversed(found) if e.get("kind") == "task" and e.get("ceremony") == "daily"), {})
    ring_task = tasks("2026-10-01T09:32").get(ring_event.get("task")) or {}
    if (rung.returncode == 0 and ring_event and ring_task.get("text") == ring_event.get("text")
            and ring_task.get("text") and ring_task.get("name") == ring_event.get("name")
            and ring_task.get("last") == logged_last(ring_event["task"], "2026-10-01T09:32")):
        held("the ring", f"{ring_event['task']} « {ring_task.get('name')} » says its consigne "
             f"({len(ring_task['text'])} chars), its last the log's")
    else:
        failures.append(f"  ✗ the ring                    rc={rung.returncode} event={ring_event} task={ring_task} "
                        f"{rung.stderr[-200:]!r}")
    return 0
