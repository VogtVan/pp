"""Scenario `consignation-through-the-console` -- 2 case(s):
- la-sequence: the PROTOCOL replayed call by call -- the work, a gesture, the closing
  call that opens OPERATIONS, the consignation -- and the line lands in the record
- le-geste-intercale: a gesture played between the block and the consignation leaves
  the offer alive, and the second line lands too

The subject is the SEQUENCE, so the calls go through the console: driven in process the
flow crosses several steps at once, and the lived turn is exactly what went unproven --
the defect this batch chased lived between two calls, never inside one.
"""
from __future__ import annotations

import json
import re

from tests.harness import session_of

WORK_STEP = "WORK any => ephemeral"      # the pending step an agent works from


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("consign", ("continuity",))
    made = env.made
    settings = made / "SETTINGS.md"
    settings.write_text(re.sub(r"^continuity_memory_frequency: .*$",
                               "continuity_memory_frequency: 1",
                               settings.read_text(encoding="utf-8"), flags=re.M), encoding="utf-8")
    record = made / ".sys" / "records" / "operations.jsonl"
    env.cli("-new")
    key = session_of(made).name[len("session-"):-len(".json")]

    def entries() -> list[dict]:
        return [json.loads(one) for one in record.read_text(encoding="utf-8").splitlines()
                if one.strip()]

    def to_work(bound: int = 12) -> bool:
        """Bare calls until a turn's WORK stands again, one turn having closed: where
        an agent starts working, and where the consignation becomes due."""
        closed = False
        for _ in range(bound):
            out = env.cli(key).stdout
            closed = closed or "FINAL" in out
            if closed and WORK_STEP in out:
                return True
        return False

    # --- la-sequence: the turn walked one call at a time ------------------------------
    reached = to_work()
    before = session_of(made).read_bytes()
    worked = env.cli(key, "-s", "pp-continuity", "recall", "last", "3")   # the agent's own work
    steady = session_of(made).read_bytes() == before
    opened = env.cli(key)                     # the call that closes the work
    consigned = env.cli(key, "-s", "pp-continuity", "register", "the turn answered")
    landed = entries()
    if (reached and worked.returncode == 0 and steady
            and "▸ OPERATIONS{1/1}" in opened.stdout and "pp-continuity" in opened.stdout
            and consigned.returncode == 0 and "consigned" in consigned.stdout
            and landed and landed[-1]["entry"] == "the turn answered"):
        held("the consignation lands in the lived sequence",
             "the work, a gesture that moves nothing, the closing call that opens "
             "OPERATIONS with `pp-continuity` offered, then the consignation -- the record "
             f"holds {len(landed)} line(s), the last one this turn's")
    else:
        failures.append(f"  ✗ la sequence                 work={reached}/{worked.returncode}/{steady} "
                        f"open={opened.stdout[:60]!r} consign={consigned.returncode} {len(landed)}")

    # --- le-geste-intercale: the offer survives what is played after it ---------------
    again = to_work()
    env.cli(key)                              # OPERATIONS opens again, the cadence is 1
    between = env.cli(key, "-s", "pp-continuity", "recall", "last", "1")  # played AFTER the block
    second = env.cli(key, "-s", "pp-continuity", "register", "the next turn answered")
    landed = entries()
    if (again and between.returncode == 0 and second.returncode == 0
            and "consigned" in second.stdout and landed[-1]["entry"] == "the next turn answered"):
        held("a gesture between the block and the consignation costs nothing",
             "the OPERATIONS offer is still there after a routed gesture, and the second "
             "line lands -- the order of the agent's calls no longer decides")
    else:
        failures.append(f"  ✗ le geste intercale          {again}/{between.returncode}/"
                        f"{second.returncode} {second.stdout[:80]!r}")
    return 0
