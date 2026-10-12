"""Scenario `agent-faces-packages` -- 2 case(s) (batch les-packages-de-l-agent, 2026-10-12, agent 0.24.1): the last
object of `agent status <path> --json` says the PACKAGES the agent's instance pins beyond its base, `{name, on}` as its
SETTINGS switch them -- the face the post reads before it opens a run -- on a house pinning `agent`, `steering` and
`plan`:
- the face says what an opening says: `packages` of the last object equals `packages` of `ready` of a `chat --json`
  on the agent, every package on; nothing else of the object moves
- a switch of SETTINGS: `package.plan: off` written to the agent's `SETTINGS.md` (the operator's edit) -- the face says
  `plan` off, and so does the `ready` of a new conversation
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

from tests.harness import support

A = support(__file__, "agent")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench, packages=("agent", "steering", "plan"))

    def tail() -> dict:
        found = [json.loads(line) for line in h.call("agent", "status", "agents/ag1", "--json").stdout.splitlines()
                 if line.strip()]
        return found[-1] if found else {}

    def ready() -> dict:
        argv = [sys.executable, str(h.engine), "--instance", str(h.house), "agent", "chat", "agents/ag1",
                "--json", *h.harnessed_at("play", bench.temp() / "r")]
        played = subprocess.run(argv, input=json.dumps({"kind": "quit"}) + "\n", capture_output=True, text=True,
                                cwd=h.ws, env={**os.environ, **h.env}, timeout=120)
        flow = [json.loads(line) for line in played.stdout.splitlines() if line.strip().startswith("{")]
        return next((one for one in flow if one.get("kind") == "ready"), {})

    # --- the face says what an opening says ------------------------------------------------------------------
    face, opening = tail(), ready()
    every_on = [{"name": "steering", "on": True}, {"name": "plan", "on": True}]
    if (set(face) == {"agent", "providers", "last", "weight", "packages"}
            and sorted(face.get("packages") or [], key=lambda one: one["name"])
            == sorted(every_on + [{"name": "agent", "on": True}], key=lambda one: one["name"])
            and face.get("packages") == opening.get("packages")):
        held("the face says what an opening says", f"packages {face['packages']} = ready's")
    else:
        failures.append(f"  ✗ the face                     face={face} ready={opening.get('packages')}")

    # --- a switch of SETTINGS --------------------------------------------------------------------------------
    settings = h.agent_meta / "SETTINGS.md"
    text = settings.read_text(encoding="utf-8")
    switched = re.sub(r"^package\.plan: on$", "package.plan: off", text, count=1, flags=re.M)
    settings.write_text(switched, encoding="utf-8")
    face, opening = tail(), ready()
    plan = next((one.get("on") for one in face.get("packages") or [] if one.get("name") == "plan"), None)
    if switched != text and plan is False and face.get("packages") == opening.get("packages"):
        held("a switch of SETTINGS", f"plan off at the face and at a new conversation's ready: {face['packages']}")
    else:
        failures.append(f"  ✗ a switch                     edited={switched != text} face={face.get('packages')} "
                        f"ready={opening.get('packages')}")
    return 0
