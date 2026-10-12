"""Scenario `agent-exchanges` -- each response paired with the message it answers (batch
l-appariement-des-echanges, 2026-10-11), the witness harness playing:
- a conversation whose first message is stopped during the witness's pause (nothing kept), then two
  messages: `exchanges --json` says `null` for the first and the responses for the second and the third;
  the text says `(no response)` for the first
- records sharing seconds (a run of the witness, then lines a bench writes after them): a message that
  kept nothing, a response in the second of its own message, a response in the second of the next
  message -- each response at its message, the order of both records kept
- no record gains a field
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

from tests.harness import support

A = support(__file__, "agent")
HOLD = 10.0
SENT_FIELDS = {"at", "from", "to", "run", "message", "policy", "conducted"}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)

    def talk(mode: str, where: Path) -> subprocess.Popen:
        argv = [sys.executable, str(h.engine), "--instance", str(h.house), "agent", "chat", "agents/ag1",
                "--json", *h.harnessed_at(mode, where)]
        return subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, cwd=h.ws, env={**os.environ, **h.env})

    def command(kind: str, **fields) -> str:
        return json.dumps({"kind": kind, **fields}) + "\n"

    def until_kind(live, kind: str) -> list[dict]:
        seen = []
        while True:
            line = live.stdout.readline()
            if not line:
                return seen
            seen.append(json.loads(line))
            if seen[-1].get("kind") == kind:
                return seen

    def exchanges(key: str, *flags: str) -> subprocess.CompletedProcess:
        return h.call("agent", "exchanges", "agents/ag1", key, *flags)

    def objects(played: subprocess.CompletedProcess) -> list[dict]:
        return [json.loads(one) for one in played.stdout.splitlines() if one.strip()]

    # --- a message stopped before its launch ended, then two: each response at its message -----------
    known = set(h.keys())
    out = bench.temp() / "pa"
    live = talk("pause", out)
    live.stdin.write(command("message", text="un"))
    live.stdin.flush()
    opened = time.monotonic()
    while not h.read(".pid", out) and time.monotonic() - opened < HOLD:
        time.sleep(0.05)
    live.stdin.write(command("stop"))
    live.stdin.flush()
    first = until_kind(live, "verdict")
    key = next((one for one in h.keys() if one not in known), "")
    live.stdin.write(command("message", text="deux") + command("message", text="trois") + command("quit"))
    live.communicate(timeout=120)
    paired = objects(exchanges(key, "--json"))
    text = exchanges(key).stdout.splitlines()
    kept = [one for one in h.responses() if one.get("run") == key]
    if ([one.get("state") for one in first if one.get("kind") == "verdict"] == ["interrupted"]
            and len(kept) == 2 and [one.get("message") for one in paired] == ["un", "deux", "trois"]
            and [one.get("response") is None for one in paired] == [True, False, False]
            and [one.get("index") for one in paired] == [1, 2, 3]
            and len(text) == 3 and text[0].endswith("-> (no response)") and "(no response)" not in text[1]):
        held("an interrupted message keeps no response, the next ones keep theirs",
             f"run {key}: 3 messages, 2 responses kept; `un` null, `deux` and `trois` answered; the text says "
             "(no response) on the first line alone")
    else:
        failures.append(f"  ✗ interrupted then two      key={key} kept={len(kept)} "
                        f"paired={[(one.get('message'), one.get('response')) for one in paired]} text={text}")

    # --- shared seconds: the bench writes a run's lines after a real exchange ------------------------
    known = set(h.keys())
    made = h.wake("m1", "play")
    run = next((one for one in h.keys() if one not in known), "")
    template_sent = next((one for one in h.messages() if one.get("run") == run), {})
    template_kept = next((one for one in h.responses() if one.get("run") == run), {})

    def sent(at: str, message: str) -> dict:
        return {**template_sent, "at": at, "message": message}

    def answer(at: str, index: int, response: str) -> dict:
        return {**template_kept, "at": at, "index": index, "response": response}

    with (h.records / "messages.jsonl").open("a", encoding="utf-8") as messages, \
            (h.records / "responses.jsonl").open("a", encoding="utf-8") as responses:
        messages.write(json.dumps(sent("2099-01-01T00:00:10+00:00", "m2")) + "\n")     # kept nothing
        messages.write(json.dumps(sent("2099-01-01T00:00:20+00:00", "m3")) + "\n")
        responses.write(json.dumps(answer("2099-01-01T00:00:20+00:00", 2, "r3")) + "\n")   # its own second
        messages.write(json.dumps(sent("2099-01-01T00:00:30+00:00", "m4")) + "\n")
        responses.write(json.dumps(answer("2099-01-01T00:00:31+00:00", 3, "r4")) + "\n")
        messages.write(json.dumps(sent("2099-01-01T00:00:31+00:00", "m5")) + "\n")      # r4's second
        responses.write(json.dumps(answer("2099-01-01T00:00:40+00:00", 4, "r5")) + "\n")
    shared = objects(exchanges(run, "--json"))
    pairs = [(one.get("message"), one.get("response")) for one in shared]
    if (made.returncode == 0 and run and [one.get("message") for one in shared] == ["m1", "m2", "m3", "m4", "m5"]
            and shared[0].get("response") == template_kept.get("response")
            and pairs[1:] == [("m2", None), ("m3", "r3"), ("m4", "r4"), ("m5", "r5")]):
        held("shared seconds", f"run {run}: m2 kept nothing; r3 in m3's own second, r4 in m5's second -- each "
             "response at its message, the order of both records kept")
    else:
        failures.append(f"  ✗ shared seconds            rc={made.returncode} run={run} pairs={pairs}")

    # --- no record gains a field --------------------------------------------------------------------
    answered = {field for one in h.responses() for field in one}
    written = {field for one in h.messages() for field in one}
    if answered <= A.RECORD_FIELDS | {"conducted"} and written <= SENT_FIELDS:
        held("no record gains a field", f"responses {sorted(answered)}; messages {sorted(written)}")
    else:
        failures.append(f"  ✗ records                     responses={sorted(answered)} messages={sorted(written)}")
    return 0
