"""Scenario `agent-chat-tools` -- 4 case(s) (batch les-appels-au-flux, 2026-10-09; split out of `agent-chat-json`
by la-decoupe-d-agent-chat-json, 2026-10-09): the calls of a launch on the flow of `agent chat <path> --json`.
- under the `stream` witness (the witness's grammar) the flow says
  `tool` (the call of pp, `pp: true`, its `shell`), its `tool-result`, `thinking` {tokens}, a `Read` (`pp: false`)
  and its `tool-result` in error, `words` -- each with its `exchange` and `launch`, all before the `agent` of their
  launch and said before it ends (the witness's pause); under `--harness … --provider <its grammar>` the `stream-codex`
  witness is read in the grammar its mode declares (`MODE_GRAMMARS`: the answer, the session, a `tool` with its `shell`);
  a call the face refuses is
  a `step` `refusal` {events-malformed} and the exchange reaches its response; `run --json` on the `stream` witness
  says none of the four kinds and keeps the record's fields
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
    h = A.House(bench)
    keys, responses = h.keys, h.responses

    def talk(mode: str, where, *flags: str) -> subprocess.Popen:
        argv = [sys.executable, str(h.engine), "--instance", str(h.house), "agent", "chat", "agents/ag1",
                "--json", *flags, *h.harnessed_at(mode, where)]
        return subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, cwd=h.ws, env={**os.environ, **h.env})

    def events_of(out: str) -> list[dict]:
        found = []
        for line in out.splitlines():
            try:
                found.append(json.loads(line))
            except ValueError:
                found.append({"kind": "UNREADABLE", "line": line})
        return found

    def fresh(known: set) -> str:
        return next((one for one in keys() if one not in known), "")

    def command(kind: str, **fields) -> str:
        return json.dumps({"kind": kind, **fields}) + "\n"

    # --- tools: the calls of a launch ---------------------------------------------------------------
    CALLS = ("tool", "tool-result", "thinking", "words")
    known = set(keys())
    out_t = bench.temp() / "jt"
    live = talk("stream", out_t)
    out, err = live.communicate(command("message", text="tools") + command("quit"), timeout=120)
    key_t = fresh(known)
    told = events_of(out)
    calls = [one for one in told if one.get("kind") in CALLS]
    first = [one for one in calls if one.get("launch") == 1]
    agent_1 = next((at for at, one in enumerate(told) if one.get("kind") == "agent" and one.get("launch") == 1), -1)
    tools = [one for one in calls if one.get("kind") == "tool"]
    results = {one.get("id"): one for one in calls if one.get("kind") == "tool-result"}
    piped = next((one for one in tools if one.get("pp") is True), {})
    read = next((one for one in tools if one.get("name") == "Read"), {})
    if (live.returncode == 0 and err == "" and key_t and first and agent_1 > 0
            and all(told.index(one) < agent_1 for one in first)
            and max(str(one.get("at")) for one in first) < str(told[agent_1].get("at"))
            and all(one.get("exchange") == 1 and isinstance(one.get("launch"), int) for one in calls)
            and piped.get("shell") == f"./pp {key_t} -" and piped.get("name") == "Bash"
            and results.get(piped.get("id"), {}).get("error") is False
            and read.get("pp") is False and results.get(read.get("id"), {}).get("error") is True
            and any(one.get("kind") == "thinking" and one.get("tokens") == 42 for one in calls)
            and any(one.get("kind") == "words" and one.get("text") == "witness words" for one in calls)
            and not any(one.get("kind") == "step" and one.get("event") == "refusal" for one in told)
            and [one.get("response") for one in told if one.get("kind") == "response"] == ["witness answer: stream"]):
        held("the calls of a launch reach the flow while it plays", f"run {key_t}: {len(calls)} calls over "
             f"{len({one.get('launch') for one in calls})} launches; launch 1's {len(first)} before its agent and said "
             f"before it ended ({max(str(one.get('at')) for one in first)} < {told[agent_1].get('at')}); `{piped.get('shell')}` "
             "pp: true and its result; Read pp: false, its result in error; thinking 42 tokens; words")
    else:
        failures.append(f"  ✗ tools                       rc={live.returncode} err={err[-300:]!r} key={key_t} "
                        f"kinds={[one.get('kind') for one in told]} piped={piped} read={read}")

    known = set(keys())
    out_x = bench.temp() / "jx"
    live = talk("stream-codex", out_x)
    out, err = live.communicate(command("message", text="the other grammar") + command("quit"), timeout=120)
    key_x = fresh(known)
    told = events_of(out)
    answered = [one for one in told if one.get("kind") == "response"]
    shells = [one.get("shell") for one in told if one.get("kind") == "tool"]
    if (live.returncode == 0 and err == "" and key_x
            and [one.get("response") for one in answered] == ["witness answer: stream-codex"]
            and [one.get("session") for one in answered] == ["w-1"]
            and shells and all(one == f"./pp {key_x} -" for one in shells)
            and all(one.get("pp") is True for one in told if one.get("kind") == "tool")
            and any(one.get("kind") == "thinking" and one.get("text") == "witness reasoning" for one in told)
            and any(one.get("kind") == "tool-result" and one.get("content") == "ok" for one in told)):
        held("--provider names the grammar of a --harness", f"run {key_x}: read in {A.MODE_GRAMMARS['stream-codex']}'s grammar -- the answer of its "
             f"agent_message, the session of thread.started (w-1), {len(shells)} tool(s) `./pp {key_x} -` pp: true, "
             "their output, the reasoning")
    else:
        failures.append(f"  ✗ the other grammar           rc={live.returncode} err={err[-300:]!r} key={key_x} "
                        f"answered={answered} shells={shells} kinds={[one.get('kind') for one in told]}")

    out_m = bench.temp() / "jm"
    live = talk("stream-malformed", out_m)
    out, err = live.communicate(command("message", text="malformed") + command("quit"), timeout=120)
    told = events_of(out)
    malformed = [one for one in told if one.get("kind") == "step" and one.get("event") == "refusal"
                 and str(one.get("code", "")) == "events-malformed"]
    if (live.returncode == 0 and malformed
            and [one.get("response") for one in told if one.get("kind") == "response"] == ["witness answer: stream-malformed"]
            and [one.get("state") for one in told if one.get("kind") == "verdict"] == ["parked"]):
        held("a call the face refuses is a step, the exchange goes on", f"{len(malformed)} step refusal "
             "events-malformed; the response kept, the verdict parked")
    else:
        failures.append(f"  ✗ malformed                   rc={live.returncode} err={err[-300:]!r} "
                        f"steps={[one for one in told if one.get('kind') == 'step'][-4:]}")

    out_q = bench.temp() / "jq"
    ran = h.call("agent", "run", "agents/ag1", "--message", "quiet run", "--json", *h.harnessed_at("stream", out_q))
    said_steps = []
    for line in ran.stderr.splitlines():
        try:
            said_steps.append(json.loads(line))
        except ValueError:
            pass
    try:
        printed = json.loads(ran.stdout)
    except ValueError:
        printed = {}
    if (ran.returncode == 0 and said_steps and not any(one.get("event") in CALLS for one in said_steps)
            and not any(kind in ran.stderr for kind in ('"tool"', '"tool-result"', '"thinking"', '"words"'))
            and set(printed) - {"session", "state"} == A.RECORD_FIELDS
            and set(responses()[-1]) == A.RECORD_FIELDS and responses()[-1].get("response") == "witness answer: stream"):
        held("run says none of the calls", f"run --json on the stream witness: {len(said_steps)} steps on stderr, none "
             "of the four kinds; the record's fields unchanged, the response of the result line")
    else:
        failures.append(f"  ✗ run quiet                   rc={ran.returncode} stdout={ran.stdout[-200:]!r} "
                        f"stderr={ran.stderr[-300:]!r}")
    return 0
