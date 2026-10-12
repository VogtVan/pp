"""Scenario `door-at-new` -- the engine opens the door the launcher names (plan agent,
batch le-rythme-et-les-entrees, 2026-10-01). `PP_DOOR` is read by `-new` alone:
- the named document, a proc of the instance, is OPENED as a CALL above the boot: the
  first output carries its heading, the trace says `door`
- an unknown name refuses `door-unknown` and the opening leaves nothing: no slot, no trace
- without the variable nothing changes: two kit throwaways with the same proc render
  byte-identical first blocks (the key apart) -- the door is the launcher's word alone
- the variable is ignored off `-new`: a keyed call under `PP_DOOR` stacks nothing
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from conductor import persistence
from tests.harness import cli

DAILY = """---
proc: |
  WORK
---
# DAILY

Say yesterday, today and blockers for this agent, then close the exchange.
"""

KEY = re.compile(r"run ([0-9a-f]{6})")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    envs = [bench.env(f"door-{n}") for n in (1, 2, 3)]
    for env in envs:
        env.write("procs/DAILY.md", DAILY)

    def opened(env, extra: dict | None = None):
        return cli(env.engine, "-new", cwd=env.root,
                   env=None if extra is None else {**os.environ, **extra})

    def traces(env) -> list:
        return sorted((env.made / ".sys" / "state").glob("session-*.jsonl"))

    def trace_kinds(env) -> list[str]:
        found = []
        for path in traces(env):
            for line in path.read_text(encoding="utf-8").splitlines():
                try:
                    found.append(json.loads(line))
                except ValueError:
                    pass
        return found

    # --- the door opens above the boot ---------------------------------------------------------
    doored = opened(envs[0], {"PP_DOOR": "DAILY.md"})
    key = KEY.search(doored.stdout).group(1) if KEY.search(doored.stdout) else ""
    door_lines = [one for one in trace_kinds(envs[0]) if one.get("kind") == "door"]
    if (doored.returncode == 0 and key and re.search(r"▸ DAILY", doored.stdout)
            and len(door_lines) == 1 and door_lines[0].get("document") == "DAILY.md"):
        held("the door opens above the boot", f"PP_DOOR=DAILY.md at -new: the first output carries "
             f"DAILY, the trace says door (run {key})")
    else:
        failures.append(f"  ✗ door at -new                rc={doored.returncode} key={key!r} "
                        f"door_lines={door_lines} {doored.stdout[-300:]!r} {doored.stderr[-200:]!r}")

    # --- an unknown door leaves nothing --------------------------------------------------------
    slots_before, traces_before = len(persistence.slots(envs[0].made)), len(traces(envs[0]))
    unknown = opened(envs[0], {"PP_DOOR": "NOWHERE.md"})
    if (unknown.returncode == 2 and "door-unknown" in unknown.stderr
            and len(persistence.slots(envs[0].made)) == slots_before
            and len(traces(envs[0])) == traces_before):
        held("an unknown door leaves nothing", "PP_DOOR=NOWHERE.md: door-unknown, exit 2, "
             "no slot and no trace beyond the standing run's")
    else:
        failures.append(f"  ✗ door unknown                rc={unknown.returncode} "
                        f"slots={len(persistence.slots(envs[0].made))}/{slots_before} "
                        f"{unknown.stderr[-200:]!r}")

    # --- without the variable nothing changes --------------------------------------------------
    plain2 = opened(envs[1])
    plain3 = opened(envs[2])
    key2 = KEY.search(plain2.stdout).group(1) if KEY.search(plain2.stdout) else "?"
    key3 = KEY.search(plain3.stdout).group(1) if KEY.search(plain3.stdout) else "!"
    lines2 = plain2.stdout.replace(key2, "KEY").replace(str(envs[1].root), "WS").splitlines()[1:]
    lines3 = plain3.stdout.replace(key3, "KEY").replace(str(envs[2].root), "WS").splitlines()[1:]
    if (plain2.returncode == 0 and plain3.returncode == 0 and lines2 and lines2 == lines3
            and not re.search(r"▸ DAILY", plain2.stdout)
            and not [one for one in trace_kinds(envs[1]) if one.get("kind") == "door"]):
        held("without the variable nothing changes", f"{len(lines2)} lines identical across two kit "
             "throwaways carrying the same proc, no door heading, no door trace line")
    else:
        drift = next((i for i, (a, b) in enumerate(zip(lines2, lines3)) if a != b), None)
        failures.append(f"  ✗ door absent                 rc={plain2.returncode}/{plain3.returncode} "
                        f"lines={len(lines2)}/{len(lines3)} drift={drift} "
                        f"{lines2[drift] if drift is not None and drift < len(lines2) else ''!r}")

    # --- the variable is ignored off -new -------------------------------------------------------
    keyed = cli(envs[1].engine, key2, cwd=envs[1].root, env={**os.environ, "PP_DOOR": "DAILY.md"})
    if (keyed.returncode in (0, 2)
            and not [one for one in trace_kinds(envs[1]) if one.get("kind") == "door"]):
        held("the variable is ignored off -new", "a keyed call under PP_DOOR stacks nothing: "
             "no door line in the trace")
    else:
        failures.append(f"  ✗ door off -new               rc={keyed.returncode} "
                        f"{keyed.stdout[-150:]!r} {keyed.stderr[-150:]!r}")
    return 0
