"""Scenario `time-attribution` -- the agent TIME by function (plan pp-split, batch
la-mesure-de-l-effort) -- 2 case(s):
- report attributes each interval to the FUNCTION of the block that precedes it, closes
  the tail on a turn-end stamp, and holds the operator's wait (a prompt) out
- without a turn-end stamp the tail is said UNKNOWN, never guessed
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from conductor.packaging import contributions

START = datetime(2026, 9, 2, 12, 0, tzinfo=timezone.utc)


def _trace(path: Path, events: list[tuple[int, dict]]) -> None:
    lines = [json.dumps({"at": (START + timedelta(seconds=off)).isoformat(timespec="milliseconds"),
                         **data}, ensure_ascii=False) for off, data in events]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _declare(env, name, meta_str, book):
    contributions.run_skill(env.made, "pp-monitoring", ["setup", name, meta_str, str(book)])


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("timews", ("monitoring",))
    made = env.made
    # a minimal declared analysis, then we overwrite its last_trace by hand -- the trace is
    # the datum report reads; the drive is proven elsewhere
    book = made.parent / "pb.md"
    book.write_text("composition: kit\n\n## S1\n\n| id | gesture | expected |\n|---|---|---|\n"
                    "| S1.01 | S1.01 hi | -- |\n", encoding="utf-8")
    contributions.run_skill(made, "pp-monitoring", ["setup", "t", str(made), str(book)])

    trace = made / ".sys" / "records" / "hand.jsonl"
    # WORK block at 0s -> agent thinks 8s -> a gesture at 8 (its own interval) -> INFER block
    # at 9 -> agent 3s -> the FINAL (waiting) block at 12 -> turn-end at 20 (answer delivery 8s)
    _trace(trace, [
        (0, {"kind": "new"}),
        (0, {"kind": "block", "stack": "BOOT ▸ TURN{2/4}", "command": "WORK", "wait": False,
             "weight": {"total": 400, "tokens": 100}}),
        (8, {"kind": "gesture", "name": "pp-steering"}),
        (9, {"kind": "block", "stack": "BOOT ▸ TURN ▸ NEXT{1/1}", "command": "INFER",
             "wait": False, "weight": {"total": 300, "tokens": 80}}),
        (9, {"kind": "provider", "name": "pp-steering", "token": "steering-threads", "package": "steering", "ms": 120}),
        (12, {"kind": "block", "stack": "BOOT ▸ TURN{5/6}", "command": "INFER",
              "wait": False, "weight": {"total": 200, "tokens": 50}}),
        (17, {"kind": "answer", "instruction": "PROVE "}),  # 5s proving -- dissociated
        (17, {"kind": "block", "stack": "BOOT ▸ TURN{5/6}", "command": "", "wait": True}),
        (25, {"kind": "turn-end"}),
    ])
    state = json.loads((made / ".sys" / "records" / "monitoring.json").read_text(encoding="utf-8"))
    state["t"]["last_trace"] = str(trace)
    (made / ".sys" / "records" / "monitoring.json").write_text(json.dumps(state), encoding="utf-8")

    _, out, err = contributions.run_skill(made, "pp-monitoring", ["report", "t"])
    if ("agent time by function" in out and "TURN/WORK" in out and "NEXT/INFER" in out
            and "tail (answer delivery)" in out and "8.0 s" in out
            and "proof (dissociated)" in out and "5.0 s" in out and "1 proof advancement" in out
            and "1 turn-end stamp(s)" in out and "120.0 ms" in out):
        held("the time is attributed by function, proof dissociated, tail on the stamp",
             "WORK 8s, INFER 3s, PROOF 5s apart (the engine marks it), the tail 8s, engine "
             "120ms; the operator's wait never enters")
    else:
        failures.append(f"  ✗ time table                 {out[-260:]!r} {err[-60:]!r}")

    # --- no stamp: the tail is unknown ------------------------------------------------
    trace2 = made / ".sys" / "records" / "nostamp.jsonl"
    _trace(trace2, [
        (0, {"kind": "new"}),
        (0, {"kind": "block", "stack": "BOOT ▸ TURN{2/4}", "command": "WORK", "wait": False}),
        (5, {"kind": "block", "stack": "BOOT ▸ TURN{5/6}", "command": "", "wait": True}),
    ])
    state["t"]["last_trace"] = str(trace2)
    (made / ".sys" / "records" / "monitoring.json").write_text(json.dumps(state), encoding="utf-8")
    _, out2, _ = contributions.run_skill(made, "pp-monitoring", ["report", "t"])
    if "the tail is UNKNOWN" in out2:
        held("no stamp, the tail is unknown", "report says the tail is unknown, never guesses it")
    else:
        failures.append(f"  ✗ unknown tail               {out2[-160:]!r}")
    return len(failures)
