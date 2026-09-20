"""Scenario `traces` -- 6 case(s):
- an exchange runs from the prompt to the closing that waits: three exchanges, counted
- the intervals belong to the event that ends them: proof, script call, work, answer
- a reshow after a script call counts apart; a hole over thirty minutes is left out
- the mass and the tokens come from the trace's weights alone: a trace without them says none
- a rendered block writes its weight: the boot of a fresh environment carries it
- the measure discriminates: the block line itemizes its payloads by subject, and an
  engine-run provider leaves its named line with its duration
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile

from conductor.state import traces, instance


def _write(path: Path, events: list[tuple[int, dict]], start: datetime) -> None:
    lines = []
    for offset, data in events:
        at = (start + timedelta(seconds=offset)).isoformat(timespec="milliseconds")
        lines.append(json.dumps({"at": at, **data}, ensure_ascii=False))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    state = Path(tempfile.mkdtemp(prefix="pp-traces-"))
    start = datetime(2026, 8, 26, 15, 0, tzinfo=timezone.utc)
    weight = {"constraints": 100, "payload": 300, "options": 0, "instruction": 10,
              "frame": 40, "total": 450, "tokens": 120}
    # --- run one: three exchanges -- a boot, a proof, a script call with its reshow, a hole
    _write(state / "session-20260826T150000Z.jsonl", [
        (0, {"kind": "new"}),
        (0, {"kind": "block", "stack": "BOOT", "command": "INFER", "wait": False, "weight": weight}),
        (10, {"kind": "block", "stack": "TURN{1/2}", "command": "WORK", "wait": False, "weight": weight}),
        (70, {"kind": "answer", "instruction": "PROVE ", "given": "[]",
              "weight": {"chars": 2, "tokens": 1}}),
        (72, {"kind": "block", "stack": "TURN{2/2}", "command": "", "wait": True, "weight": weight}),
        # exchange two: a prompt, a script call that reshows the block, a skip
        (300, {"kind": "prompt", "text": "go"}),
        (300, {"kind": "block", "stack": "TURN{1/2}", "command": "WORK", "wait": False, "weight": weight}),
        (330, {"kind": "gesture", "name": "pp-steering", "segment": 1, "frame": "TURN"}),
        (331, {"kind": "block", "stack": "TURN{1/2}", "command": "WORK", "wait": False, "weight": weight}),
        (345, {"kind": "block", "stack": "TURN{2/2}", "command": "", "wait": True, "weight": weight}),
        # exchange three: a hole -- forty minutes on one exchange, a repair and a refusal inside
        (400, {"kind": "prompt", "text": "encore"}),
        (400, {"kind": "block", "stack": "TURN{1/2}", "command": "WORK", "wait": False, "weight": weight}),
        (2000, {"kind": "refusal", "code": "address-stale", "detail": "x"}),
        (2400, {"kind": "answer", "instruction": "PROVE ", "given": "[]",
                "weight": {"chars": 2, "tokens": 1}}),
        (2401, {"kind": "repair", "instruction": "PROVE "}),
        (2800, {"kind": "block", "stack": "TURN{2/2}", "command": "", "wait": True, "weight": weight}),
    ], start)
    # --- run two: one exchange, no weight in the trace (an older engine wrote it)
    _write(state / "session-20260826T160000Z.jsonl", [
        (0, {"kind": "new"}),
        (0, {"kind": "block", "stack": "BOOT", "command": "INFER", "wait": False}),
        (20, {"kind": "block", "stack": "TURN{2/2}", "command": "", "wait": True}),
    ], start + timedelta(hours=1))
    (state / "session-abc123.json").write_text(json.dumps({"log": "session-20260826T160000Z.jsonl"}),
                                               encoding="utf-8")
    found = traces.runs(state)
    one, two = found[0], found[1]

    # --- three exchanges, from the prompt to the waiting closing --------------------
    if (len(found) == 2 and len(one.exchanges) == 3 and len(two.exchanges) == 1
            and [round(e.duration.total_seconds()) for e in one.exchanges] == [72, 45, 2400]
            and two.key == "abc123" and one.key == ""):
        held("an exchange runs prompt to closing", "3 + 1 exchanges, 72s / 45s / 2400s, the "
             "slot's key mapped to its trace")
    else:
        failures.append(f"  ✗ exchanges                  {[len(r.exchanges) for r in found]} "
                        f"{[round(e.duration.total_seconds()) for e in one.exchanges]} {two.key!r}")

    # --- the intervals belong to the event that ends them ---------------------------
    first = one.exchanges[0]
    if (first.proofs == 1 and round(first.seconds["proof"]) == 60
            and round(first.seconds["work"]) == 12 and first.blocks == 3 and first.reshows == 0):
        held("the intervals belong to their event", "60s of proof, 12s of work, 3 blocks")
    else:
        failures.append(f"  ✗ attribution                {first.as_dict()}")

    # --- a reshow apart, a hole left out ---------------------------------------------
    second, third = one.exchanges[1], one.exchanges[2]
    totals = traces.summary(found)
    if (second.reshows == 1 and second.blocks == 2 and second.gestures == 1
            and round(second.seconds["gesture"]) == 30
            and third.gap and third.repairs == 1 and third.refusals == 1
            and totals["gaps"] == 1 and round(totals["median"]) == 45
            and totals["exchanges"] == 4 and totals["reshows"] == 1):
        held("a reshow counts apart, a hole is left out", "reshow 1 · script call 30s · the 40-min "
             "exchange excluded from the durations, its repair and refusal counted")
    else:
        failures.append(f"  ✗ reshow / hole              {second.as_dict()} {third.as_dict()} "
                        f"{totals}")

    # --- the mass comes from the weights alone -----------------------------------------
    rendered = traces.render(found, None, None)
    payload = json.loads(traces.render_json(found, 7, None))
    if (first.mass == 3 * 450 and first.parts["payload"] == 900 and two.exchanges[0].mass is None
            and first.tokens == 3 * 120 and two.exchanges[0].tokens is None
            and first.given == {"chars": 2, "tokens": 1} and "tokens" not in first.parts
            and "| 2026-08-26 16:00 | abc123 | 1 | 2 (+0) | — | — |" in rendered
            and "| 2026-08-26 15:00 | — | 3 | 7 (+1) | 960 | 3 600 |" in rendered
            and payload["period"]["mass"] == 8 * 450 and payload["period"]["tokens"] == 8 * 120
            and payload["period"]["given"] == {"chars": 4, "tokens": 2}
            and payload["scope"]["days"] == 7):
        held("the mass and the tokens are the weights' sum", "1 350 chars / 360 tokens on the "
             "first exchange, — on a trace without weights, 3 600 / 960 over the period, the "
             "agent's answers 4 chars / 2 tokens, the table and the json agree")
    else:
        failures.append(f"  ✗ mass                       {first.mass} {two.exchanges[0].mass} "
                        f"{rendered.splitlines()[3:6]}")

    # --- a rendered block writes its weight ----------------------------------------------
    weighed_env = bench.env("weighed")
    made = weighed_env.made
    conductor = weighed_env.conductor()
    conductor.resume(conductor.boot("BOOT.md"))
    written = sorted((made / instance.STATE).glob("session-*.jsonl"))
    events = traces.read(written[-1]) if written else []
    blocks = [one for one in events if one.get("kind") == "block"]
    live = traces.runs(made / instance.STATE)
    itemized = [b for b in blocks if isinstance(b.get("payloads"), dict)]
    if (blocks and all(isinstance(b.get("weight"), dict) and b["weight"].get("total", 0) > 0
                       for b in blocks)
            and set(blocks[0]["weight"]) == {"constraints", "payload", "options", "instruction",
                                             "frame", "total", "tokens"}
            and all(b["weight"]["tokens"] > 0 for b in blocks)
            and live and live[0].exchanges and live[0].exchanges[0].mass
            and live[0].exchanges[0].mass == sum(b["weight"]["total"] for b in blocks)
            and itemized and all(sum(pair[0] for pair in b["payloads"].values())
                                 == b["weight"]["payload"] for b in itemized)):
        held("a rendered block writes its weight", f"{len(blocks)} block(s) weighed in the trace, "
             "the reader sums them")
    else:
        failures.append(f"  ✗ weight written             {[b.get('weight') for b in blocks][:2]}")

    # --- an engine-run provider leaves its named line --------------------------------
    provided_env = bench.env("provided", ("steering",))
    made2 = provided_env.made
    (made2 / "procs").mkdir(exist_ok=True)
    (made2 / "procs" / "TAKER.md").write_text(     # a consumer of steering's token:
        "---\nname: TAKER\nkind: proc\ndescription: consumes the threads\n"
        "payloads: steering-threads\nproc: |\n  INFER\n---\none line\n", encoding="utf-8")
    (made2 / "procs" / "OUTER.md").write_text(
        "---\nname: OUTER\nkind: proc\ndescription: calls the taker\nproc: |\n"
        "  CALL TAKER.md\n---\nouter\n", encoding="utf-8")
    provided = provided_env.conductor()
    provided.start(provided.boot("OUTER.md"))    # the CALL opens TAKER: its providers run
    written = sorted((made2 / instance.STATE).glob("session-*.jsonl"))
    events = traces.read(written[-1]) if written else []
    providers = [one for one in events if one.get("kind") == "provider"]
    if (providers and all(one.get("name") and "ms" in one for one in providers)
            and any(one.get("name") == "pp-steering" and one.get("token") == "steering-threads"
                    and one.get("package") == "steering" for one in providers)):
        held("a provider leaves its named line", "pp-steering ran for `steering-threads` on TAKER's "
             "opening, its package and duration on the line")
    else:
        failures.append(f"  ✗ provider line              {providers[:2]!r}")
    return 0
