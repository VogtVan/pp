"""Scenario `team-log-result` -- 2 case(s) (batch le-suivi-de-l-equipe, 2026-10-01; split out of
`team-review` by les-scenarios-par-maison, 2026-10-07): the journal and the results read back,
on the paper run replayed.
- `team log` renders the journal, one line per event: `--task T1` the events of T1 (its posts, its
  intents and their ends), `--last 3` the three last, bare all of them; nothing written
- `team result` reads a resolved task's result: `"LGTM"` for T1, the last resolved without a task,
  `task-open` on a stopped or open task, `team-unknown`
"""
from __future__ import annotations

import json

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench)
    T.paper_run(h)
    journal = h.journal_of("review")
    h.call("team", "post", "review", "--to", "r1", "--message", "look again", "--no-tick")   # T2, left open
    h.declare("halt", "---\nagents: |\n  s s\nroot: s\n---\nStopped before any wake-up.\n")
    h.call("team", "start", "halt", "--message", "hold", "--no-tick")
    h.call("team", "stop", "halt", "--task", "T1", "--no-tick")
    before_w = journal.read_bytes()

    # --- log renders the journal, by task and by tail ------------------------------------------------------
    everything = h.events()
    tags_t1 = {one.get("tag") for one in everything if one.get("kind") == "wake-intent" and one.get("task") == "T1"}
    ids_t1 = [one["id"] for one in everything if one.get("task") == "T1" or one.get("tag") in tags_t1]
    logged = h.call("team", "log", "review", "--task", "T1")
    tailed = h.call("team", "log", "review", "--last", "3")
    whole_log = h.call("team", "log", "review")

    def ids(played) -> list[int]:
        return [int(line.split()[0].lstrip("#")) for line in played.stdout.splitlines() if line.startswith("#")]

    if (logged.returncode == 0 and ids(logged) == ids_t1 and len(ids_t1) > 20
            and tailed.returncode == 0 and ids(tailed) == [one["id"] for one in everything[-3:]]
            and whole_log.returncode == 0 and ids(whole_log) == [one["id"] for one in everything]
            and journal.read_bytes() == before_w
            and any(" post do house -> m on T1" in line for line in logged.stdout.splitlines())):
        held("log renders the journal", f"--task T1: {len(ids_t1)} line(s) in order (the posts, the intents and their "
             f"ends); --last 3: the three last ids; bare: all {len(everything)}; nothing written")
    else:
        failures.append(f"  ✗ log                         {logged.returncode}/{tailed.returncode}/{whole_log.returncode} "
                        f"t1={ids(logged)[:6]}…/{len(ids_t1)} tail={ids(tailed)} {logged.stdout[:300]!r}")

    # --- result reads a resolved task's result ----------------------------------------------------------------
    got = h.call("team", "result", "review", "T1")
    last_resolved = [one for one in everything if one.get("kind") == "done"][-1]
    latest = h.call("team", "result", "review")
    halted_r = h.call("team", "result", "halt", "T1")
    nothing = h.call("team", "result", "nothing")
    opened_r = h.call("team", "result", "review", "T2")
    if (got.returncode == 0 and got.stdout == '"LGTM"\n'
            and latest.returncode == 0 and json.loads(latest.stdout) == last_resolved.get("result")
            and halted_r.returncode == 2 and "task-open" in halted_r.stderr and "stopped" in halted_r.stderr
            and nothing.returncode == 2 and "team-unknown" in nothing.stderr
            and opened_r.returncode == 2 and "task-open" in opened_r.stderr
            and journal.read_bytes() == before_w):
        held("result reads a resolved task", f'T1 -> "LGTM"; bare -> the last resolved ({last_resolved.get("task")}); '
             "halt T1 (stopped) -> task-open; nothing -> team-unknown; T2 (open) -> task-open; nothing written")
    else:
        failures.append(f"  ✗ result                      {got.returncode}/{latest.returncode}/{halted_r.returncode}/"
                        f"{nothing.returncode}/{opened_r.returncode} {got.stdout!r} {latest.stdout!r} "
                        f"{halted_r.stderr[-120:]!r} {opened_r.stderr[-120:]!r}")
    return 0
