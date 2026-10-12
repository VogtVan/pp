"""Scenario `agent-chat-mark` -- 4 case(s) (batch la-marque-du-verrou-du-chat, 2026-10-10): a conversation that
resumes a run MARKS its wake lock as soon as it takes it, before any message.
- after a wake-up, `chat --run <key>` waiting: the lock's mark says `held: "chat"`, the hour of the take (later than
  the wake-up's), the head of the run's last message, no `responses`; a neighbour's `run --dry-run` reads
  `since HH:MM « <head> »`
- the lock file gone before the take: the same line, never `since ? « ? »`
- a mark carrying `interrupted: true` keeps it through the take: the conversation's first message opens its prompt
  on `[interrupted by your principal]`
- a conversation resumed then closed without a message leaves its run `parked` at `status --json`, never `dead`
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime

from tests.harness import support

A = support(__file__, "agent")
INTERRUPTED = "[interrupted by your principal]"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)
    h.wake("first message of A", "play")
    key = h.keys()[0] if h.keys() else ""
    lock_file = A.launcher(h.agent_meta, key)

    def mark() -> dict:
        try:
            read = json.loads(lock_file.read_text(encoding="utf-8"))
            return read if isinstance(read, dict) else {}
        except (OSError, ValueError):
            return {}

    def taken(where) -> subprocess.Popen:
        """`chat --run <key> --json` launched and read up to its first `waiting`: the lock is taken."""
        argv = [sys.executable, str(h.engine), "--instance", str(h.house), "agent", "chat", "agents/ag1", "--json",
                "--run", key, *h.harnessed_at("play", where)]
        live = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, cwd=h.ws, env={**os.environ, **h.env})
        while True:
            line = live.stdout.readline()
            if not line or json.loads(line).get("kind") == "waiting":
                return live

    def closed(live, *commands: dict) -> None:
        live.communicate("".join(json.dumps(one) + "\n" for one in (*commands, {"kind": "quit"})), timeout=120)

    def neighbours() -> str:
        dry = h.wake("probe", "play", "--dry-run")
        return next((one for one in dry.stdout.splitlines() if one.startswith("[runs under way")), "")

    def line_of(seen: dict) -> str:
        local = datetime.fromisoformat(str(seen.get("at"))).astimezone().strftime("%H:%M") if seen.get("at") else "?"
        return f"[runs under way: {key} since {local} « first message of A »]"

    # --- after a wake-up: the take writes its own mark -----------------------------------------------
    before = mark()
    time.sleep(1.1)                                   # the hour of the take, one second at least after the wake-up's
    live = taken(bench.temp() / "m1")
    seen, read = mark(), neighbours()
    closed(live)
    if (key and seen.get("held") == "chat" and "responses" not in seen and seen.get("message") == "first message of A"
            and str(seen.get("at")) > str(before.get("at")) and read == line_of(seen)):
        held("the take marks the lock", f"run {key}: {seen}; the neighbour reads {read!r}")
    else:
        failures.append(f"  ✗ take                        before={before} seen={seen} read={read!r}")

    # --- the lock file gone before the take: still a mark, never `?` ----------------------------------
    lock_file.unlink(missing_ok=True)
    live = taken(bench.temp() / "m2")
    seen, read = mark(), neighbours()
    closed(live)
    if seen.get("held") == "chat" and read == line_of(seen) and "since ?" not in read:
        held("a lock file gone is marked at the take", f"{read!r}")
    else:
        failures.append(f"  ✗ gone                        seen={seen} read={read!r}")

    # --- an interruption kept through the take ------------------------------------------------------
    lock_file.write_text(json.dumps({"at": A.now_iso(), "message": "think", "responses": len(h.responses()),
                                     "interrupted": True}) + "\n", encoding="utf-8")   # the mark a `stop` leaves
    where = bench.temp() / "m3"
    live = taken(where)
    seen = mark()
    closed(live, {"kind": "message", "text": "go on"})
    prompt = next((p.read_text(encoding="utf-8") for p in sorted(where.parent.glob(where.name + ".prompt.*"))), "")
    if seen.get("interrupted") is True and "responses" not in seen and prompt.startswith(f"{INTERRUPTED}\n{A.HEAD}\ngo on"):
        held("the interruption crosses the take", f"the take's mark {sorted(seen)}; the first prompt opens on "
             f"{INTERRUPTED}")
    else:
        failures.append(f"  ✗ interrupted                 seen={seen} prompt={prompt[:120]!r}")

    # --- resumed then closed without a message: parked, never dead ----------------------------------
    live = taken(bench.temp() / "m4")
    closed(live)
    rows = {one["run"]: one for one in (json.loads(x) for x in h.call("agent", "status", "agents/ag1", "--json")
                                        .stdout.splitlines() if x.strip()) if "run" in one}
    if rows.get(key, {}).get("state") == "parked":
        held("a conversation closed without a message leaves its run parked", f"status --json: {key} parked")
    else:
        failures.append(f"  ✗ closed bare                 {rows.get(key)}")
    return 0
