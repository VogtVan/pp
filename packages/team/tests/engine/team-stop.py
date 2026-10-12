"""Scenario `team-stop` -- 1 case(s) (batch l-attente, 2026-10-01; split out of `team-review`
by les-scenarios-par-maison, 2026-10-07): a stop that does not interrupt.
- a stop does not interrupt: h delegates to h1, which sleeps 3 s; a note posted while h waits, then
  `team stop halt --task T1` -- a stop to h and to h1, the note returned to the owner, h1's running
  wake-up ends and is routed nowhere, nobody woken for the stop (team 0.10.0), nothing routed
"""
from __future__ import annotations

import os
import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "h": [{"sleep": 0.2, "body": {"do": ["h1"]}}, {"sleep": 0.1, "body": {"done": "stopped"}}],
        "h1": [{"sleep": 3.0, "body": {"done": True}}, {"sleep": 0.1, "body": {"done": True}}]})

    by_kind, lines, all_ended = T.by_kind, T.lines, T.all_ended

    # --- a stop does not interrupt, and routes nowhere ----------------------------------------------
    h.declare("halt", "---\nagents: |\n  h h\n  h1 h1\nreports: |\n  h1 -> h\nroot: h\n---\nHalt on demand.\n")
    halted = h.call("team", "start", "halt", "--message", "review slowly", *h.harnessed)
    running = h.settled("halt", lambda found: bool(by_kind(found, "wake-launched", agent="h1")), timeout=60)
    noted_h = h.call("team", "post", "halt", "--task", "T1", "--message", "while you wait")
    stopped_h = h.call("team", "stop", "halt", "--task", "T1")
    quiet_h = h.settled("halt", lambda found: len(by_kind(found, "wake-ended", agent="h1")) >= 1 and all_ended(found))
    time.sleep(1.0)
    found = h.events("halt")
    stops = by_kind(found, "post", verb="stop")
    note_h = by_kind(found, "post", verb="note")
    returned_h = by_kind(found, "returned")
    first_end = next(iter(by_kind(found, "wake-ended", agent="h1")), {})
    routed_after = [one for one in found if one.get("id", 0) > first_end.get("id", 10 ** 9)
                    and (one.get("kind") in ("terminal", "delegation", "done")
                         or (one.get("kind") == "post" and one.get("from") in ("h", "h1")))]
    second = {agent: by_kind(found, "wake-intent", agent=agent)[1:] for agent in ("h", "h1")}
    status_h = h.call("team", "status", "halt")
    if (halted.returncode == 0 and running and noted_h.returncode == 0 and stopped_h.returncode == 0 and quiet_h
            and sorted(one["to"] for one in stops) == ["h", "h1"] and all(one.get("from") == "house" for one in stops)
            and len(note_h) == 1 and [(one.get("message"), one.get("to")) for one in returned_h] == [(note_h[0]["id"], "house")]
            and first_end and routed_after == []
            and all(second[agent] == [] for agent in ("h", "h1"))
            and len(by_kind(found, "wake-ended")) == 2 and not by_kind(found, "wake-failed")
            and "T1 · stopped" in status_h.stdout):
        held("a stop does not interrupt, and routes nowhere", f"stop to h and h1, the note returned to house; h1's running "
             f"wake-up ended and was routed nowhere; nobody woken for the stop; {len(found)} events")
    else:
        failures.append(f"  ✗ stop                        {halted.returncode}/{noted_h.returncode}/{stopped_h.returncode} "
                        f"running={running} quiet={quiet_h} stops={[(one['to'], one['id']) for one in stops]} "
                        f"returned={[(one.get('message'), one.get('to')) for one in returned_h]} routed_after={routed_after} "
                        f"second={ {a: [one.get('messages') for one in s] for a, s in second.items()} } {stopped_h.stderr[-200:]!r}")

    return 0
