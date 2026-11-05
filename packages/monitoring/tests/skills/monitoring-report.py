"""Scenario `monitoring-report` -- what `report` attributes, read from its rows -- 4 case(s):
- the served volume goes BY PACKAGE from the repo: a served body carries no provider line,
  yet NEXT belongs to steering and TURN/CAPABILITIES to kit -- no `?` row
- a `derive --fusion none` repo renders ONE output per step: the report says fusion=1,
  the time per STEP
- each interval goes to the FUNCTION of the block before it; a proof advancement stands
  apart, the tail closes on the turn-end stamp, the operator's wait never enters
- without a turn-end stamp the tail is UNKNOWN, never guessed
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from conductor.packaging import contributions

START = datetime(2026, 9, 2, 12, 0, tzinfo=timezone.utc)
BOOK = ("composition: kit steering\n\n## S1\n\n| id | gesture | expected |\n"
        "|---|---|---|\n| S1.01 | S1.01 hi | -- |\n| S1.02 | S1.02 bye | -- |\n")


def _trace(path: Path, events: list[tuple[int, dict]]) -> Path:
    lines = [json.dumps({"at": (START + timedelta(seconds=off)).isoformat(timespec="milliseconds"),
                         **data}, ensure_ascii=False) for off, data in events]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _rows(report: str, kind: str, unit: str) -> dict[str, float]:
    """-> label: figure of the report's `<kind>` rows (`  time     TURN/WORK   8.0 s`)."""
    pattern = re.compile(rf"^  {kind}\s+(.+?)(?:\s+x\d+)?\s+(-?\d+(?:\.\d+)?) {unit}\b")
    return {m.group(1): float(m.group(2))
            for m in map(pattern.match, report.splitlines()) if m}


def _regime(report: str) -> tuple[str, str] | None:
    found = re.search(r"fusion=(-?\d+), time is (.+)$", report, re.M)
    return (found.group(1), found.group(2)) if found else None


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("monitoring-report", ("steering", "monitoring"))
    made = env.made
    env.write("SETTINGS.md", env.read("SETTINGS.md")
              .replace("monitoring_capture: false", "monitoring_capture: true"))
    book = made.parent / "pb.md"
    book.write_text(BOOK, encoding="utf-8")
    record = made / ".sys" / "records" / "monitoring.json"

    # --- derive under fusion none, run, report ----------------------------------------
    target = made.parent / "derived-none"
    contributions.run_skill(made, "pp-monitoring", ["derive", str(target), "--fusion", "none"])
    derived = target / made.name
    fused_none = "instructions_fusion: none" in (derived / "SETTINGS.md").read_text(encoding="utf-8")
    contributions.run_skill(made, "pp-monitoring", ["setup", "res", str(derived), str(book)])
    rc, _, _ = contributions.run_skill(made, "pp-monitoring", ["run", "res"])
    rc2, rep, _ = contributions.run_skill(made, "pp-monitoring", ["report", "res"])
    packages = _rows(rep, "package", "c of payload")

    if (fused_none and rc == 0 and rc2 == 0
            and packages.get("steering", 0) > 0 and packages.get("kit", 0) > 0
            and not any(one.startswith("unattributed") for one in packages)):
        held("the volume is attributed by package from the repo",
             "NEXT to steering, the kit's own to kit -- no provider line needed, no `?`")
    else:
        failures.append(f"  ✗ per package                {packages}")

    if _regime(rep) == ("1", "per STEP"):
        held("the fusion regime is said, and none gives per-step time",
             "derive --fusion none -> the report says fusion=1, time is per STEP")
    else:
        failures.append(f"  ✗ fusion regime              {_regime(rep)!r}")

    # --- a hand-written trace: the time by function -----------------------------------
    # WORK at 0 -> 8 s of agent, a gesture inside -> INFER at 9 -> 3 s -> INFER at 12,
    # proven at 17 (5 s apart) -> the waiting block at 17 -> turn-end at 25 (the tail, 8 s)
    contributions.run_skill(made, "pp-monitoring", ["setup", "t", str(derived), str(book)])
    state = json.loads(record.read_text(encoding="utf-8"))
    state["t"]["last_trace"] = str(_trace(made / ".sys" / "records" / "hand.jsonl", [
        (0, {"kind": "new"}),
        (0, {"kind": "block", "stack": "BOOT ▸ TURN{2/4}", "command": "WORK", "wait": False,
             "weight": {"total": 400, "tokens": 100}}),
        (8, {"kind": "gesture", "name": "pp-steering"}),
        (9, {"kind": "block", "stack": "BOOT ▸ TURN ▸ NEXT{1/1}", "command": "INFER",
             "wait": False, "weight": {"total": 300, "tokens": 80}}),
        (9, {"kind": "provider", "name": "pp-steering", "token": "steering-threads",
             "package": "steering", "ms": 120}),
        (12, {"kind": "block", "stack": "BOOT ▸ TURN{5/6}", "command": "INFER",
              "wait": False, "weight": {"total": 200, "tokens": 50}}),
        (17, {"kind": "answer", "instruction": "PROVE "}),
        (17, {"kind": "block", "stack": "BOOT ▸ TURN{5/6}", "command": "", "wait": True}),
        (25, {"kind": "turn-end"}),
    ]))
    record.write_text(json.dumps(state), encoding="utf-8")
    _, out, err = contributions.run_skill(made, "pp-monitoring", ["report", "t"])
    times = _rows(out, "time", "s")
    engine = _rows(out, "provider", "ms")
    if (times.get("TURN/WORK") == 8.0 and times.get("NEXT/INFER") == 3.0
            and times.get("proof (dissociated)") == 5.0
            and times.get("tail (answer delivery)") == 8.0
            and "1 proof advancement" in out and "1 turn-end stamp(s)" in out
            and list(engine.values()) == [120.0]):
        held("the time is attributed by function, proof dissociated, tail on the stamp",
             "WORK 8s, INFER 3s, PROOF 5s apart (the engine marks it), the tail 8s, engine "
             "120ms; the operator's wait never enters")
    else:
        failures.append(f"  ✗ time table                 {times} {engine} {err[-60:]!r}")

    # --- no stamp: the tail is unknown ------------------------------------------------
    state["t"]["last_trace"] = str(_trace(made / ".sys" / "records" / "nostamp.jsonl", [
        (0, {"kind": "new"}),
        (0, {"kind": "block", "stack": "BOOT ▸ TURN{2/4}", "command": "WORK", "wait": False}),
        (5, {"kind": "block", "stack": "BOOT ▸ TURN{5/6}", "command": "", "wait": True}),
    ]))
    record.write_text(json.dumps(state), encoding="utf-8")
    _, out2, _ = contributions.run_skill(made, "pp-monitoring", ["report", "t"])
    if "the tail is UNKNOWN" in out2 and "tail (answer delivery)" not in _rows(out2, "time", "s"):
        held("no stamp, the tail is unknown", "report says the tail is unknown, never guesses it")
    else:
        failures.append(f"  ✗ unknown tail               {_rows(out2, 'time', 's')}")
    return len(failures)
