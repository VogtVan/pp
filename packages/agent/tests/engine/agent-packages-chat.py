"""Scenario `agent-packages-chat` -- a `package` command of `agent chat <path> --json`, on a house pinning `agent`,
`steering` and `plan` (`plan` mounts `NEXT_MOVE` at `turn.end`; the end of the passage sweeps it, so a parked
run holds no mount); it never ends in `run-missing` nor `package-in-flight`:
- before the first message: `package {pending: true}` before any `opened`, then `pending: false` with `plan` off
  before the first `agent`; the run's trace says `switch`; nothing refused
- on a parked run: `pending: false` at once (the parked run holds no mount), the exchange after it plays `plan`
  off; the switch traced once
- a double switch on a parked run: both apply at once, `plan` back on; two switches traced
- a switch that is no flight: `package nowhere` is `refused` `package-unpinned` with the engine's `detail`
- the flag seeds the list: `chat --json --package plan=off` says `plan` in `ready.pending`, then `package
  {pending: false}` with `plan` off before the first `agent`
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

from tests.harness import support

A = support(__file__, "agent")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench, packages=("agent", "steering", "plan"))
    keys = h.keys

    def talk(where, commands: str, *flags: str) -> tuple[subprocess.CompletedProcess, list[dict]]:
        """-> the conversation `agent chat agents/ag1 --json` fed `commands`, and the objects it wrote."""
        argv = [sys.executable, str(h.engine), "--instance", str(h.house), "agent", "chat", "agents/ag1",
                "--json", *flags, *h.harnessed_at("play", where)]
        played = subprocess.run(argv, input=commands, capture_output=True, text=True, cwd=h.ws,
                                env={**os.environ, **h.env}, timeout=180)
        found = []
        for line in played.stdout.splitlines():
            try:
                found.append(json.loads(line))
            except ValueError:
                found.append({"kind": "UNREADABLE", "line": line})
        return played, found

    def command(kind: str, **fields) -> str:
        return json.dumps({"kind": kind, **fields}) + "\n"

    def switch(packages, name: str = "plan") -> object:
        return next((one.get("on") for one in packages or [] if one.get("name") == name), None)

    def switches(key: str) -> int:
        return len([one for one in h.trace(key) if one.get("kind") == "switch"]) if key else -1

    def fresh(known: set) -> str:
        return next((one for one in keys() if one not in known), "")

    # --- before the first message: the switch waits, then applies after the opening ---------------------------
    known = set(keys())
    played, flow = talk(bench.temp() / "pa", command("package", name="plan", on=False) + command("message", text="un")
                        + command("quit"))
    key_a = fresh(known)
    kinds = [one.get("kind") for one in flow]
    packages = [one for one in flow if one.get("kind") == "package"]
    first_agent = kinds.index("agent") if "agent" in kinds else len(kinds)
    opened_at = kinds.index("opened") if "opened" in kinds else len(kinds)
    applied = [i for i, one in enumerate(flow) if one.get("kind") == "package" and one.get("pending") is False]
    if (played.returncode == 0 and "refused" not in kinds and len(packages) == 2
            and packages[0].get("pending") is True and kinds.index("package") < opened_at
            and applied and applied[0] < first_agent and switch(packages[1].get("packages")) is False
            and switches(key_a) == 1):
        held("a switch before the first message waits, then applies", f"run {key_a}: package pending before opened, "
             f"then pending false (plan off) before the first agent; the trace says switch once; nothing refused")
    else:
        failures.append(f"  ✗ before the run              rc={played.returncode} kinds={kinds} packages={packages} "
                        f"switches={switches(key_a)} err={played.stderr[-300:]!r}")

    # --- on a parked run: the engine says in flight, the switch waits for the next message --------------
    known = set(keys())
    played, flow = talk(bench.temp() / "pb", command("message", text="un") + command("package", name="plan", on=False)
                        + command("message", text="deux") + command("quit"))
    key_b = fresh(known)
    kinds = [one.get("kind") for one in flow]
    packages = [one for one in flow if one.get("kind") == "package"]
    openings = [one for one in flow if one.get("kind") == "opened"]
    second = [i for i, one in enumerate(flow) if one.get("kind") == "principal" and one.get("exchange") == 2]
    launches_2 = [i for i, one in enumerate(flow) if one.get("kind") == "conduction" and one.get("exchange") == 2]
    applied = [i for i, one in enumerate(flow) if one.get("kind") == "package" and one.get("pending") is False]
    if (played.returncode == 0 and "refused" not in kinds and len(packages) == 1
            and packages[0].get("pending") is False and switch(packages[0].get("packages")) is False
            and applied and second and launches_2 and applied[0] < second[0] < launches_2[0]
            and switches(key_b) == 1
            and len(openings) == 2 and switch(openings[0].get("packages")) is True):
        held("a switch on a parked run applies at once", f"run {key_b}: the parked run holds no mount -- pending "
             "false at once, plan off before exchange 2 opens; switch traced once")
    else:
        failures.append(f"  ✗ parked                      rc={played.returncode} kinds={kinds} packages={packages} "
                        f"switches={switches(key_b)} err={played.stderr[-300:]!r}")

    # --- a double switch: the wait is cancelled, nothing played ------------------------------------------
    known = set(keys())
    played, flow = talk(bench.temp() / "pc", command("message", text="un") + command("package", name="plan", on=False)
                        + command("package", name="plan", on=True) + command("message", text="deux")
                        + command("quit"))
    key_c = fresh(known)
    packages = [one for one in flow if one.get("kind") == "package"]
    kinds = [one.get("kind") for one in flow]
    if (played.returncode == 0 and "refused" not in kinds and len(packages) == 2
            and packages[0].get("pending") is False and packages[1].get("pending") is False
            and switch(packages[1].get("packages")) is True and switches(key_c) == 2):
        held("a double switch on a parked run plays both", f"run {key_c}: off then on, each applied at once, "
             "plan on at the next message; two switches traced")
    else:
        failures.append(f"  ✗ double                      rc={played.returncode} packages={packages} "
                        f"switches={switches(key_c)} err={played.stderr[-300:]!r}")

    # --- a refusal that is no flight: refused with the engine's detail -------------------------------------
    played, flow = talk(bench.temp() / "pd", command("message", text="un") + command("package", name="nowhere", on=False)
                        + command("quit"))
    refused = [one for one in flow if one.get("kind") == "refused"]
    if (played.returncode == 0 and [one.get("code") for one in refused] == ["package-unpinned"]
            and "nowhere" in str(refused[0].get("detail", ""))
            and not any(one.get("kind") == "package" for one in flow)):
        held("a switch the engine refuses for another cause is refused with its detail",
             f"package-unpinned, detail {str(refused[0].get('detail'))[:60]!r}")
    else:
        failures.append(f"  ✗ unpinned                    rc={played.returncode} refused={refused} err={played.stderr[-300:]!r}")

    # --- the flag seeds the list: pending at ready, applied before the first launch ------------------------------
    known = set(keys())
    played, flow = talk(bench.temp() / "pe", command("message", text="un") + command("quit"), "--package", "plan=off")
    key_e = fresh(known)
    kinds = [one.get("kind") for one in flow]
    seeded = next((one for one in flow if one.get("kind") == "ready"), {})
    applied = [i for i, one in enumerate(flow) if one.get("kind") == "package" and one.get("pending") is False]
    first_agent = kinds.index("agent") if "agent" in kinds else len(kinds)
    if (played.returncode == 0 and seeded.get("pending") == [{"name": "plan", "on": False}] and applied
            and applied[0] < first_agent and switch(flow[applied[0]].get("packages")) is False
            and "refused" not in kinds and switches(key_e) == 1):
        held("the flag seeds the list", f"run {key_e}: ready says plan pending, then pending false with plan off "
             "before the first agent")
    else:
        failures.append(f"  ✗ seeded                      rc={played.returncode} ready={seeded.get('pending')} kinds={kinds} "
                        f"switches={switches(key_e)} err={played.stderr[-300:]!r}")

    return 0
