"""Scenario `end-turn` -- the turn-end stamp (plan pp-split, batch le-stamp-turn-end) -- 2 case(s):
- without a run trace `-et` refuses no-run by name, nothing written
- `-et` poses ONE turn-end line on the most recently written run trace and stays INERT:
  the -peek before and after render the same block
"""
from __future__ import annotations

import json
import re

from conductor.state import instance

CLOCK = re.compile(r"\d{2}:\d{2}:\d{2}")


def _still(shown: str) -> str:
    """The block without its clocked heading -- inertness is judged on the content."""
    return "\n".join(line for line in shown.splitlines() if not CLOCK.search(line))


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("etws")

    bare = env.cli("-et")
    if bare.returncode == 2 and "no-run" in bare.stderr:
        held("no run, no stamp", "no-run named, nothing written")
    else:
        failures.append(f"  ✗ no-run                     rc={bare.returncode} {bare.stderr[-80:]!r}")

    env.cli("-new")
    before = env.cli("-peek").stdout
    stamped = env.cli("-et")
    after = env.cli("-peek").stdout
    traces = sorted((env.made / instance.STATE).glob("session-*.jsonl"))
    last = json.loads(traces[-1].read_text(encoding="utf-8").splitlines()[-1]) if traces else {}
    if (stamped.returncode == 0 and "turn-end" in stamped.stdout
            and last.get("kind") == "turn-end" and _still(before) == _still(after)):
        held("the stamp lands and the verb is inert",
             "one turn-end line on the freshest trace; the -peek before and after agree")
    else:
        failures.append(f"  ✗ stamp                      rc={stamped.returncode} "
                        f"{last.get('kind')!r} same={before == after}")
    return len(failures)
