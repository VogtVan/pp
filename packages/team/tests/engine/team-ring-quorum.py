"""Scenario `team-ring-quorum` -- 1 case(s) (batch la-sonnerie-a-la-main, 2026-10-10: decision 70 of the phase,
team 0.19.0): a ceremony line ending on `any <n>` closes the facilitator's wait at the n-th terminal
answer; it replays I14 of `team-sim-reframe.py` on the wait a ring writes.
- (q) a quorum of 2 of 3 (I14): `daily every weekday 09:30 with r1 r2 r3 -> f any 2`; the tick of 09:31
  rings -- `wait {f, any 2, to r1 r2 r3}` after the three delegations --; r1 and r2 answer quickly, r3
  slowly; f is woken after the second terminal answer and before r3's, its head names r1's and r2's
  `done` and not r3's; f resolves the daily while r3 still plays
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "f": [{"sleep": 0.1, "body": {"done": "root"}}, {"sleep": 0.1, "body": {"done": "quorum standup"}}],
        "r1": [{"sleep": 0.2, "body": {"done": True}}],
        "r2": [{"sleep": 0.6, "body": {"done": True}}],
        "r3": [{"sleep": 5.0, "body": {"done": True}}]})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of

    # --- (q) a quorum of 2 of 3 -- I14 ----------------------------------------------------------------
    h.declare("quorum", "---\nagents: |\n  f agents/f\n  r1 agents/r1\n  r2 agents/r2\n  r3 agents/r3\n"
                        "reports: |\n  r1 r2 r3 -> f\nroot: f\n"
                        "ceremonies: |\n  daily every weekday 09:30 with r1 r2 r3 -> f any 2\n"
                        "schedule: off\n---\nTwo voices suffice.\n")
    started = h.call("team", "start", "quorum", "--message", "open the day", *h.harnessed, now="09:10")
    root = h.settled("quorum", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 45)
    declared = next(iter(by_kind(h.events("quorum"), "team-started")), {}).get("ceremonies") or [{}]
    rung = h.call("team", "tick", "quorum", now="09:31")
    resolved = h.settled("quorum", lambda found: bool(by_kind(found, "done", task="T2")), 45)
    found = h.events("quorum")
    waits = [(one.get("agent"), one.get("task"), one.get("any"), sorted(one.get("to") or []))
             for one in by_kind(found, "wait")]
    last_deleg = max((one["id"] for one in by_kind(found, "delegation") if one.get("task") == "T2"), default=10 ** 9)
    wait_id = next((one["id"] for one in by_kind(found, "wait")), -1)
    f_on_t2 = next((one for one in by_kind(found, "wake-intent", agent="f") if one.get("task") == "T2"), {})
    ends = {one.get("agent"): one["id"] for one in by_kind(found, "wake-ended")}
    r3_end = ends.get("r3", 10 ** 9)
    head = h.prompts_of("f")[-1] if len(h.prompts_of("f")) >= 2 else ""
    done = h.settled("quorum", all_ended, 45)
    if (started.returncode == 0 and root and declared[0].get("quorum") == 2 and rung.returncode == 0 and resolved
            and waits == [("f", "T2", 2, ["r1", "r2", "r3"])] and wait_id > last_deleg
            and f_on_t2 and f_on_t2["id"] < r3_end
            and "done from r1" in head and "done from r2" in head and "done from r3" not in head
            and result_of(found, "T2") == "quorum standup" and done):
        held("(q) a quorum of 2 of 3", f"wait {{f, any 2}} #{wait_id} after the delegations; f woken #{f_on_t2['id']} "
             f"before r3's end #{r3_end}, its head with r1's and r2's done; T2 'quorum standup' -- I14")
    else:
        failures.append(f"  ✗ (q) a quorum of 2 of 3       rc={started.returncode}/{rung.returncode} root={root} "
                        f"declared={declared} resolved={resolved} waits={waits} wait={wait_id}/{last_deleg} "
                        f"f={f_on_t2.get('id')} r3={r3_end} done={done} {started.stderr.strip()[-200:]!r} "
                        f"{head[-300:]!r}")
    return 0
