"""Scenario `agent-flow` -- 3 case(s) (batch l-historisation-de-la-conduction, 2026-10-11): every exchange keeps, in
the file of its run under the house's records (`flows/<digest of the agent's path>/<key>.jsonl`), every event its flow
says -- and `agent flow` reads them back.
- kept as said: a `chat --json` of two messages on the `stream` witness, the second bare (`conduct off`): the lines of
  the run's flow file are the very objects stdout said for its exchanges, in their order -- the conversation's own
  events (`ready`, `waiting`, `conduct`, `closed`) left out; the bare exchange keeps `principal` and `agent`, no
  `conduction`
- a `run` keeps its voices: `conduction`, `tool`, `tool-result`, `thinking`, `words`, `agent`, then `response` and
  `verdict` -- and its stderr still says none of the voices
- the face: `agent flow <path> <key> --json` gives the lines as kept; `--exchange 2` those of the second exchange; the
  text one line per event; a key nobody knows `run-unknown`
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from tests.harness import support

A = support(__file__, "agent")
CONVERSATION = ("ready", "waiting", "conduct", "package", "policy", "refused", "closed")   # said, never kept
VOICES = ("conduction", "tool", "tool-result", "thinking", "words", "agent")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)

    def flow_file(key: str) -> Path:
        digest = hashlib.sha1("agents/ag1".encode("utf-8")).hexdigest()[:12]
        return h.records / "flows" / digest / f"{key}.jsonl"

    def kept(key: str) -> list[dict]:
        return A.lines(flow_file(key))

    def command(kind: str, **fields) -> str:
        return json.dumps({"kind": kind, **fields}) + "\n"

    # --- kept as said: a conversation, the second exchange bare ----------------------------------------------
    known = set(h.keys())
    live = subprocess.Popen([sys.executable, str(h.engine), "--instance", str(h.house), "agent", "chat", "agents/ag1",
                             "--json", *h.harnessed_at("stream", bench.temp() / "fc")], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=h.ws,
                            env={**os.environ, **h.env})
    out, err = live.communicate(command("message", text="one") + command("conduct", on=False)
                                + command("message", text="two") + command("quit"), timeout=120)
    key = next((one for one in h.keys() if one not in known), "")
    said = [json.loads(line) for line in out.splitlines() if line.strip()]
    exchanged = [one for one in said if one.get("kind") not in CONVERSATION]
    lines = kept(key) if key else []
    second = [one for one in lines if one.get("exchange") == 2]
    if (live.returncode == 0 and key and lines and lines == exchanged
            and {one.get("kind") for one in lines} >= {"opened", "principal", "conduction", "tool", "agent",
                                                         "response", "verdict"}
            and [one.get("kind") for one in second if one.get("kind") in ("principal", "agent")] == ["principal", "agent"]
            and not any(one.get("kind") == "conduction" for one in second)):
        held("the flow kept as said", f"run {key}: {len(lines)} lines, the very objects stdout said for its two "
             "exchanges; the bare one keeps principal and agent, no conduction")
    else:
        failures.append(f"  ✗ kept as said               rc={live.returncode} key={key!r} kept={len(lines)} "
                        f"said={len(exchanged)} first diff={next((i for i, (a, b) in enumerate(zip(lines, exchanged)) if a != b), None)} "
                        f"{err[-300:]!r}")

    # --- a run keeps its voices, its stderr unchanged ---------------------------------------------------------
    known = set(h.keys())
    ran = h.call("agent", "run", "agents/ag1", "--message", "run me", "--json", *h.harnessed_at("stream", bench.temp() / "fr"))
    run_key = next((one for one in h.keys() if one not in known), "")
    run_lines = kept(run_key) if run_key else []
    steps = []
    for line in ran.stderr.splitlines():
        try:
            steps.append(json.loads(line))
        except ValueError:
            pass
    kinds = [one.get("kind") for one in run_lines]
    if (ran.returncode == 0 and run_key and set(VOICES) <= set(kinds) and kinds[-2:] == ["response", "verdict"]
            and steps and not any(one.get("event") in VOICES for one in steps)):
        held("a run keeps its voices", f"run {run_key}: {len(run_lines)} lines -- {', '.join(VOICES)}, then response and "
             f"verdict; stderr {len(steps)} steps, none of the voices")
    else:
        failures.append(f"  ✗ run voices                  rc={ran.returncode} key={run_key!r} kinds={kinds} "
                        f"{ran.stderr[-300:]!r}")

    # --- the face ------------------------------------------------------------------------------------------
    as_json = h.call("agent", "flow", "agents/ag1", key, "--json")
    try:
        read = [json.loads(line) for line in as_json.stdout.splitlines() if line.strip()]
    except ValueError:
        read = []
    only_two = h.call("agent", "flow", "agents/ag1", key, "--exchange", "2", "--json")
    try:
        read_two = [json.loads(line) for line in only_two.stdout.splitlines() if line.strip()]
    except ValueError:
        read_two = []
    text = h.call("agent", "flow", "agents/ag1", key)
    unknown = h.call("agent", "flow", "agents/ag1", "zzzzzz")
    if (as_json.returncode == 0 and read == lines and only_two.returncode == 0 and read_two
            and read_two[0].get("kind") == "opened" and read_two[0].get("exchange") == 2
            and all(one in lines for one in read_two) and len(read_two) < len(lines)
            and text.returncode == 0 and len(text.stdout.strip().splitlines()) == len(lines)
            and unknown.returncode == 2 and "run-unknown" in unknown.stderr):
        bench.refusals += 1
        held("agent flow reads it back", f"--json {len(read)} lines as kept; --exchange 2 {len(read_two)} lines from its "
             f"opened; the text {len(lines)} lines; run-unknown")
    else:
        failures.append(f"  ✗ face                        {as_json.returncode}/{only_two.returncode}/{text.returncode}/"
                        f"{unknown.returncode} json={len(read)} two={len(read_two)} {as_json.stderr[-200:]!r} "
                        f"{unknown.stderr[-200:]!r}")
    return 0
