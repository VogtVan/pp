"""Scenario `agent-chat-interrupted` -- an interrupted exchange is said to the LLM at the next message
(batch l-interruption-dite, 2026-10-09), the witness harness playing:
- pp on, in the conversation: `stop` during the `pause` witness, then `go on` -- the first prompt of the
  next wake-up opens on the interruption's head, then the message's head, the message, then pp's output;
  `opened.interrupted` is true; the message after it carries no such head, nor does any `conduction`
- pp off, the same conversation taken up by `chat --run <key>`: under `conduct off`, the prompt after the
  `stop` opens on the two heads and the message, nothing of pp
- from one process to another: a conversation interrupted then closed leaves the interruption in the
  MARK of its wake lock (`interrupted: true`); `run --run <key>` opens on the head and its verdict says
  `after an interruption`; the mark is cleared by that wake-up, the next one has neither
- no record gains a field: `responses.jsonl`, `messages.jsonl`, `sessions.jsonl` read after the cases
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
HEAD = A.HEAD
INTERRUPTED = "[interrupted by your principal]"
HOLD = 10.0
SENT_FIELDS = {"at", "from", "to", "run", "message", "policy", "conducted"}
SESSION_FIELDS = {"at", "agent", "run", "provider", "session"}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)

    def talk(mode: str, where: Path, *flags: str) -> subprocess.Popen:
        argv = [sys.executable, str(h.engine), "--instance", str(h.house), "agent", "chat", "agents/ag1",
                "--json", *flags, *h.harnessed_at(mode, where)]
        return subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, cwd=h.ws, env={**os.environ, **h.env})

    def command(kind: str, **fields) -> str:
        return json.dumps({"kind": kind, **fields}) + "\n"

    def events_of(out: str) -> list[dict]:
        return [json.loads(one) for one in out.splitlines() if one.strip()]

    def until_kind(live, kind: str) -> list[dict]:
        seen = []
        while True:
            line = live.stdout.readline()
            if not line:
                return seen
            seen.append(json.loads(line))
            if seen[-1].get("kind") == kind:
                return seen

    def stopped(live, where: Path, text: str) -> list[dict]:
        """`text` sent, then `stop` once the witness sleeps in its pause: the events up to the verdict."""
        live.stdin.write(command("message", text=text))
        live.stdin.flush()
        opened = time.monotonic()
        while not h.read(".pid", where) and time.monotonic() - opened < HOLD:
            time.sleep(0.05)
        live.stdin.write(command("stop"))
        live.stdin.flush()
        return until_kind(live, "verdict")

    def prompts(where: Path) -> dict[str, str]:
        return {one.name.split(".prompt.", 1)[1]: one.read_text(encoding="utf-8")
                for one in sorted(where.parent.glob(where.name + ".prompt.*"))}

    def first_with(where: Path, text: str) -> str:
        """-> the prompt the witness received that carries the message `text` under its head."""
        return next((one for one in prompts(where).values() if f"{HEAD}\n{text}" in one), "")

    def mark(key: str) -> dict:
        try:
            return json.loads(A.launcher(h.agent_meta, key).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    # --- pp on, in the conversation: the head once, before the message's, then pp's output -----------
    known = set(h.keys())
    out_a = bench.temp() / "ia"
    live = talk("pause", out_a)
    first = stopped(live, out_a, "think")
    key_a = next((one for one in h.keys() if one not in known), "")
    live.stdin.write(command("message", text="go on") + command("message", text="again") + command("quit"))
    out, err = live.communicate(timeout=120)
    later = events_of(out)
    flow = first + later
    openings = [one for one in flow if one.get("kind") == "opened"]
    verdicts = [one.get("state") for one in flow if one.get("kind") == "verdict"]
    resumed = first_with(out_a, "go on")
    after = first_with(out_a, "again")
    conductions = [str(one.get("text", "")) for one in flow if one.get("kind") == "conduction"]
    if (live.returncode == 0 and err == "" and key_a and verdicts == ["interrupted", "parked", "parked"]
            and resumed.startswith(f"{INTERRUPTED}\n{HEAD}\ngo on\n\n▌ pp · run {key_a}")
            and after.startswith(f"{HEAD}\nagain\n") and INTERRUPTED not in after
            and INTERRUPTED not in first_with(out_a, "think")
            and [one.get("interrupted") for one in openings] == [None, True, None]
            and conductions and not any(INTERRUPTED in one for one in conductions)):
        held("pp on: the interruption said once", f"run {key_a}: `go on` opens on {INTERRUPTED} then the message's "
             "head, the message and pp's output; opened.interrupted on that exchange alone; `again` and every "
             f"conduction without it ({len(conductions)} conductions)")
    else:
        failures.append(f"  ✗ pp on                       rc={live.returncode} err={err[-200:]!r} verdicts={verdicts} "
                        f"opened={[one.get('interrupted') for one in openings]} resumed={resumed[:160]!r} "
                        f"after={after[:80]!r} prompts={list(prompts(out_a))}")

    # --- pp off, the run taken up by another conversation: the two heads and the message alone ------
    known = set(h.keys())
    made = h.wake("first", "play")
    key_b = next((one for one in h.keys() if one not in known), "")
    out_b = bench.temp() / "ib"
    live = talk("pause", out_b, "--run", key_b)
    live.stdin.write(command("conduct", on=False))
    live.stdin.flush()
    first = stopped(live, out_b, "think")
    live.stdin.write(command("message", text="go on") + command("quit"))
    out, err = live.communicate(timeout=120)
    flow = first + events_of(out)
    verdicts = [one.get("state") for one in flow if one.get("kind") == "verdict"]
    openings = [one for one in flow if one.get("kind") == "opened"]
    bare = first_with(out_b, "go on")
    if (made.returncode == 0 and live.returncode == 0 and key_b and verdicts == ["interrupted", "unconducted"]
            and bare == f"{INTERRUPTED}\n{HEAD}\ngo on" and "▌ pp" not in bare
            and [one.get("interrupted") for one in openings] == [None, True]):
        held("pp off: the two heads and the message", f"run {key_b}: under conduct off the prompt after the stop is "
             f"{bare!r}, nothing of pp; opened.interrupted")
    else:
        failures.append(f"  ✗ pp off                      rc={made.returncode}/{live.returncode} err={err[-200:]!r} "
                        f"verdicts={verdicts} bare={bare!r} opened={[one.get('interrupted') for one in openings]}")

    # --- from one process to another: the mark keeps it, run --run says it, then it is gone ---------
    out_c = bench.temp() / "ic"
    live = talk("pause", out_c, "--run", key_b)
    first = stopped(live, out_c, "think")
    live.stdin.write(command("quit"))
    live.communicate(timeout=120)
    kept_mark = mark(key_b)
    out_d = bench.temp() / "id"
    taken = h.call("agent", "run", "agents/ag1", "--run", key_b, "--message", "go on", *h.harnessed_at("play", out_d))
    cleared = mark(key_b)
    again = h.call("agent", "run", "agents/ag1", "--run", key_b, "--message", "again", *h.harnessed_at("play", out_d))
    taken_up = first_with(out_d, "go on")
    if ([one.get("state") for one in first if one.get("kind") == "verdict"] == ["interrupted"]
            and kept_mark.get("interrupted") is True and "interrupted" not in cleared
            and taken.returncode == 0 and "· after an interruption" in taken.stderr
            and taken_up.startswith(f"{INTERRUPTED}\n{HEAD}\ngo on\n\n▌ pp · run {key_b}")
            and again.returncode == 0 and "after an interruption" not in again.stderr
            and first_with(out_d, "again").startswith(f"{HEAD}\nagain")):
        held("from one process to another, through the mark", f"run {key_b}: the closed conversation left the mark "
             f"{sorted(kept_mark)}; run --run opened on the head, its verdict `after an interruption`, the mark "
             "cleared; the next run --run without either")
    else:
        failures.append(f"  ✗ across processes            mark={kept_mark} cleared={cleared} rc={taken.returncode}/"
                        f"{again.returncode} taken={taken.stderr[-200:]!r} prompt={taken_up[:120]!r}")

    # --- no record gains a field --------------------------------------------------------------------
    answered = {field for one in h.responses() for field in one}
    sent = {field for one in h.messages() for field in one}
    opened_sessions = {field for one in h.sessions() for field in one}
    if answered <= A.RECORD_FIELDS | {"conducted"} and sent <= SENT_FIELDS and opened_sessions <= SESSION_FIELDS:
        held("no record gains a field", f"responses {sorted(answered)}; messages {sorted(sent)}; "
             f"sessions {sorted(opened_sessions)}")
    else:
        failures.append(f"  ✗ records                     responses={sorted(answered)} messages={sorted(sent)} "
                        f"sessions={sorted(opened_sessions)}")
    return 0
