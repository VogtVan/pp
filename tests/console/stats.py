"""Scenario `stats` -- 5 case(s):
- `-stats` is keyless inspection: the table renders, no run opens, nothing advances
- `-stats -json` hands the same figures to a tool; a bad argument refuses at the usage
- `-stats --blocks` renders what each OUTPUT carried, and `-stats` bare is untouched by it
- a key of six DIGITS names its run, never a number of days
- a CLOSED run keeps its key: the trace says which run it is
"""
from __future__ import annotations

import json

from conductor.state import instance


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("statsws")
    state = env.made / instance.STATE
    # a run under way, so the traces carry something
    conductor = env.conductor()
    conductor.resume(conductor.boot("BOOT.md"))
    slots_before = sorted(p.name for p in state.glob("session-*.json"))
    traces_before = sorted(p.name for p in state.glob("session-*.jsonl"))

    # --- keyless inspection: the table, nothing opened ----------------------------------
    told = env.cli("-stats")
    slots_after = sorted(p.name for p in state.glob("session-*.json"))
    traces_after = sorted(p.name for p in state.glob("session-*.jsonl"))
    lines = told.stdout.splitlines()
    if (told.returncode == 0 and lines and lines[0].startswith("**pp -- what the runs cost")
            and any(line.startswith("| run | key |") for line in lines)
            and any(line.startswith("| 20") for line in lines)
            and slots_after == slots_before and traces_after == traces_before):
        held("-stats is keyless inspection", "the table renders, no slot and no trace appear")
    else:
        failures.append(f"  ✗ stats table                rc={told.returncode} {lines[:4]} "
                        f"{told.stderr[-200:]}")

    # --- the json form, and the usage on a bad argument -------------------------------------
    as_json = env.cli("-stats", "7", "-json")
    bad = env.cli("-stats", "yesterday")
    try:
        payload = json.loads(as_json.stdout)
    except ValueError:
        payload = None
    if (as_json.returncode == 0 and payload and payload["scope"]["days"] == 7
            and payload["period"]["runs"] >= 1 and payload["runs"][0]["exchanges"]
            and bad.returncode != 0 and "days or a run's key" in (bad.stderr + bad.stdout)):
        held("-stats -json hands the figures", "scope, runs and the period; a bad argument "
             "answers the usage")
    else:
        failures.append(f"  ✗ stats json                 rc={as_json.returncode} "
                        f"{as_json.stdout[:120]!r} bad rc={bad.returncode}")
    # --- `--blocks`: what each output carried, the bare form untouched ------------------
    per_block = env.cli("-stats", "--blocks")
    as_rows = env.cli("-stats", "--blocks", "-json")
    bare_again = env.cli("-stats")
    block_lines = per_block.stdout.splitlines()
    try:
        ledger = json.loads(as_rows.stdout)
    except ValueError:
        ledger = None
    served = [line for one in (ledger or {}).get("blocks", []) for line in one["served"]]
    if (per_block.returncode == 0 and block_lines
            and block_lines[0].startswith("**pp -- what the blocks carried")
            and any(line.startswith("| # | subject | state | origin") for line in block_lines)
            and ledger and served
            and all({"subject", "state", "origin", "chars"} <= set(line) for line in served)
            and bare_again.stdout == told.stdout):
        held("-stats --blocks renders what the outputs carried",
             f"one table per block ({len(ledger['blocks'])} of them, {len(served)} line(s) "
             "served), the json carrying the same ledger -- and `-stats` bare renders exactly "
             "what it rendered before the flag existed")
    else:
        failures.append(f"  ✗ stats blocks               rc={per_block.returncode} "
                        f"{block_lines[:3]} served={len(served)}")
    # --- a key of six DIGITS names its run, never a number of days ---------------------
    # the key is FORGED, never drawn: a run whose key is all digits comes up 6% of the
    # time ((10/16)^6), and a bench that waits for a draw is no bench
    digits = "123456"
    standing = next(state.glob("session-*.json"))
    log_name = json.loads(standing.read_text(encoding="utf-8"))["log"]
    standing.rename(state / f"session-{digits}.json")
    opened_line, *rest_of_trace = (state / log_name).read_text(encoding="utf-8").splitlines()
    forged = {**json.loads(opened_line), "run": digits}      # the trace says the same key
    (state / log_name).write_text("\n".join([json.dumps(forged), *rest_of_trace]) + "\n",
                                  encoding="utf-8")
    keyed = env.cli("-stats", digits)
    keyed_lines = keyed.stdout.splitlines()
    by_days = env.cli("-stats", "7")
    if (keyed.returncode == 0 and keyed_lines
            and keyed_lines[0] == f"**pp -- what the runs cost, run {digits}**"
            and sum(1 for line in keyed_lines if line.startswith("| 20")) == 1
            and by_days.stdout.splitlines()[0].endswith("the last 7 day(s)**")):
        held("a key of digits names its run", f"`-stats {digits}` renders THAT run and its "
             "one line, while `-stats 7` still reads a number of days -- the form of a key "
             "is read before a count")
    else:
        failures.append(f"  ✗ stats digit key            rc={keyed.returncode} "
                        f"{keyed_lines[:2]}")

    # --- a CLOSED run keeps its key: the trace says which run it is --------------------
    opened = json.loads((state / log_name).read_text(encoding="utf-8").splitlines()[0])
    (state / f"session-{digits}.json").unlink()          # the slot dies, the trace stays
    closed = env.cli("-stats", digits)
    closed_lines = closed.stdout.splitlines()
    if (opened.get("run") and closed.returncode == 0
            and closed_lines[0] == f"**pp -- what the runs cost, run {digits}**"
            and sum(1 for line in closed_lines if line.startswith("| 20")) == 1
            and any(f"| {digits} |" in line for line in closed_lines)):
        held("a closed run keeps its key", "the trace's first line says which run it is, so "
             "`-stats <key>` finds a run whose slot is gone -- and the key column fills")
    else:
        failures.append(f"  ✗ stats closed run           rc={closed.returncode} "
                        f"opened={opened} {closed_lines[:2]}")
    return 0
