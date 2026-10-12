"""Scenario `traces` -- 12 case(s):
- an exchange runs from the prompt to the closing that waits: three exchanges, counted
- the intervals belong to the event that ends them: proof, script call, work, answer
- a reshow after a script call counts apart; a hole over thirty minutes is left out
- the mass and the tokens come from the trace's weights alone: a trace without them says none
- the values are counted by keyword: an answer whose channel goes to the tool is one, a bare
  close and a stray production are none
- a trace older than the answer's channel counts the value keywords alone, and says so
- the period's line says the averages per closed exchange, the table a `values` column
- the json hands the values per exchange and the averages of the period
- a rendered block writes its weight: the boot of a fresh environment carries it
- the measure discriminates: the block line itemizes its payloads by subject, and an
  engine-run provider leaves its named line with its duration
- a run its principal conducts: the `held` outputs and the principal's `advance` calls are
  counted per exchange and said on the period's line; a run the LLM conducts says nothing of them
- the held outputs by act: the json counts them by the act each hold names, a hold without an
  act a value; the period's line keeps its words
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
              "diagnostic": 0, "frame": 40, "total": 450, "tokens": 120}
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

    # --- the values, by keyword: what the agent hands the conduction -----------------------
    valued = Path(tempfile.mkdtemp(prefix="pp-traces-values-"))
    _write(valued / "session-20260827T100000Z.jsonl", [
        (0, {"kind": "new"}),
        (0, {"kind": "block", "stack": "TURN{1/3}", "command": "WORK", "wait": False}),
        (10, {"kind": "answer", "instruction": "PROVE ", "given": "[]", "channel": "tool (heredoc)"}),
        (11, {"kind": "answer", "instruction": "PICK member", "given": "ada", "channel": "tool"}),
        (12, {"kind": "answer", "instruction": "PICK member", "given": "bob", "channel": "tool"}),
        (13, {"kind": "answer", "instruction": "FIELD ", "given": "[1]", "channel": "tool (heredoc)"}),
        (14, {"kind": "answer", "instruction": "INFER ", "given": '["a"]', "channel": "tool (heredoc)"}),
        (15, {"kind": "answer", "instruction": "WORK ", "given": "", "channel": "ephemeral"}),
        (16, {"kind": "answer", "instruction": "INFER ", "given": "stray", "channel": "ephemeral"}),
        (17, {"kind": "chunk", "left": 0}),
        (18, {"kind": "block", "stack": "TURN{3/3}", "command": "", "wait": True}),
        (100, {"kind": "prompt", "text": "again"}),
        (100, {"kind": "block", "stack": "TURN{1/3}", "command": "WORK", "wait": False}),
        (110, {"kind": "block", "stack": "TURN{3/3}", "command": "", "wait": True}),
        (200, {"kind": "prompt", "text": "open"}),
        (200, {"kind": "block", "stack": "TURN{1/3}", "command": "WORK", "wait": False}),
    ], start)
    counted = traces.runs(valued)
    head = counted[0].exchanges[0] if counted and counted[0].exchanges else None
    if (head is not None and getattr(head, "values", None) == {"PROVE": 1, "PICK": 2, "FIELD": 1, "INFER": 1}
            and getattr(head, "unchanneled", None) == 0 and head.proofs == 1):
        held("the values are counted by keyword", "PROVE 1, PICK 2, FIELD 1, INFER 1 -- the bare "
             "WORK close and the stray production count none")
    else:
        failures.append(f"  ✗ values by keyword          {getattr(head, 'values', None)!r}")

    older = Path(tempfile.mkdtemp(prefix="pp-traces-older-"))
    _write(older / "session-20260827T110000Z.jsonl", [
        (0, {"kind": "new"}),
        (0, {"kind": "block", "stack": "TURN{1/2}", "command": "WORK", "wait": False}),
        (5, {"kind": "answer", "instruction": "PROVE ", "given": "[]"}),
        (6, {"kind": "answer", "instruction": "PICK member", "given": "ada"}),
        (7, {"kind": "answer", "instruction": "INFER ", "given": "a draft or a value"}),
        (8, {"kind": "block", "stack": "TURN{2/2}", "command": "", "wait": True}),
    ], start)
    old_runs = traces.runs(older)
    old_head = old_runs[0].exchanges[0] if old_runs and old_runs[0].exchanges else None
    old_said = traces.render(old_runs, None, None)
    if (old_head is not None and getattr(old_head, "values", None) == {"PROVE": 1, "PICK": 1}
            and getattr(old_head, "unchanneled", None) == 3
            and "3 answer(s) without their channel: their value keywords alone counted" in old_said):
        held("an older trace counts its value keywords", "PROVE 1, PICK 1 -- the channel-less INFER "
             "is not guessed, and the period's line says how many answers carried no channel")
    else:
        failures.append(f"  ✗ older trace                 {getattr(old_head, 'values', None)!r} "
                        f"{old_said.splitlines()[-2:]!r}")

    valued_said = traces.render(counted, None, None)
    valued_lines = valued_said.splitlines()
    if (any(line.startswith("| run | key | exchanges | blocks (+reshows) | tokens ≈ | mass | proofs |"
                            " values | repairs |") for line in valued_lines)
            and any(line.startswith("| 2026-08-27 10:00 | — | 3 (1 open) | 5 (+0) | — | — | 1 | 5 | 0 |")
                    for line in valued_lines)
            and "per closed exchange: 2.5 conduction call(s) (0.5 chunk(s)), 2.5 value(s) "
                "(PROVE 0.5, PICK 1.0, FIELD 0.5, INFER 0.5), 0.0 script call(s)" in valued_said):
        held("the averages per closed exchange", "5 values over the run in their column; 2.5 calls "
             "(0.5 chunk), 2.5 values per closed exchange -- the open one left out")
    else:
        failures.append(f"  ✗ per exchange line           {valued_lines[2:5]!r} {valued_lines[-1:]!r}")

    valued_json = json.loads(traces.render_json(counted, None, None))
    per = valued_json["period"].get("per_exchange") or {}
    if (valued_json["runs"][0]["detail"][0].get("values") == {"PROVE": 1, "PICK": 2, "FIELD": 1, "INFER": 1}
            and valued_json["period"].get("values") == {"PROVE": 1, "PICK": 2, "FIELD": 1, "INFER": 1}
            and per.get("closed") == 2 and per.get("calls") == 2.5 and per.get("chunks") == 0.5
            and per.get("values") == 2.5 and per.get("by_keyword", {}).get("PICK") == 1.0):
        held("the json carries the values", "per exchange and over the period, with the averages "
             "per closed exchange")
    else:
        failures.append(f"  ✗ values json                 {valued_json['period'].get('values')!r} {per!r}")

    # --- a run its principal conducts: the held outputs and the principal's calls -------------
    led = Path(tempfile.mkdtemp(prefix="pp-traces-led-"))
    _write(led / "session-20260827T120000Z.jsonl", [
        (0, {"kind": "new", "conducted_by": "principal"}),
        (0, {"kind": "block", "stack": "TURN{1/2}", "command": "WORK", "wait": False}),
        (5, {"kind": "advance", "held": False, "prompt": False}),
        (6, {"kind": "block", "stack": "TURN{2/2}", "command": "INFER", "wait": False}),
        (20, {"kind": "answer", "instruction": "PROVE ", "given": "[]", "channel": "tool (heredoc)"}),
        (20, {"kind": "block", "stack": "TURN{2/2}", "command": "", "wait": True}),
        (20, {"kind": "held", "weight": {"chars": 400, "tokens": 100}}),
        (30, {"kind": "advance", "held": True, "prompt": False}),       # the release, after the close
        (60, {"kind": "prompt", "text": "go"}),
        (60, {"kind": "block", "stack": "TURN{1/2}", "command": "WORK", "wait": False}),
        (60, {"kind": "advance", "held": False, "prompt": True}),
    ], start)
    led_runs = traces.runs(led)
    led_said = traces.render(led_runs, None, None)
    led_json = json.loads(traces.render_json(led_runs, None, None))
    first_led = led_runs[0].exchanges[0] if led_runs and led_runs[0].exchanges else None
    second_led = led_runs[0].exchanges[1] if led_runs and len(led_runs[0].exchanges) > 1 else None
    if (first_led is not None and first_led.held == 1 and first_led.advances == 2
            and second_led is not None and second_led.advances == 1 and second_led.held == 0
            and "1.0 held, 2.0 principal advance(s)" in led_said
            and led_json["period"].get("held") == 1 and led_json["period"].get("advances") == 3
            and (led_json["period"].get("per_exchange") or {}).get("advances") == 2.0
            and "held" not in rendered and "principal advance" not in rendered):
        held("the held outputs and the principal's advances are counted", "1 held, 2 advances on the closed "
             "exchange (the release after the close belongs to it), 1 on the open one; the period's line says "
             "them; a run the LLM conducts says nothing of them")
    else:
        failures.append(f"  ✗ held / advances            {first_led and first_led.as_dict()} "
                        f"{second_led and second_led.as_dict()} {led_said.splitlines()[-1:]!r}")

    # --- the held outputs by act ---------------------------------------------------------------
    acts = Path(tempfile.mkdtemp(prefix="pp-traces-acts-"))
    _write(acts / "session-20260827T130000Z.jsonl", [
        (0, {"kind": "new", "conducted_by": "principal"}),
        (0, {"kind": "block", "stack": "TURN{1/2}", "command": "WORK", "wait": False}),
        (5, {"kind": "held", "act": "mount", "weight": {"chars": 900, "tokens": 220}}),
        (6, {"kind": "advance", "held": True, "prompt": False}),
        (7, {"kind": "held", "act": "mount", "weight": {"chars": 900, "tokens": 220}}),
        (8, {"kind": "advance", "held": True, "prompt": False}),
        (20, {"kind": "held", "weight": {"chars": 400, "tokens": 100}}),
        (21, {"kind": "advance", "held": True, "prompt": False}),
        (22, {"kind": "block", "stack": "TURN{2/2}", "command": "", "wait": True}),
    ], start)
    by_act = traces.runs(acts)
    by_json = json.loads(traces.render_json(by_act, None, None))
    by_said = traces.render(by_act, None, None)
    if (by_json["period"].get("held") == 3 and by_json["period"].get("held_by") == {"mount": 2, "value": 1}
            and by_json["runs"][0]["detail"][0].get("held_by") == {"mount": 2, "value": 1}
            and "3.0 held, 3.0 principal advance(s)" in by_said and "mount" not in by_said):
        held("the held outputs by act", "2 mounts and 1 value held, by act in the json; the period's "
             "line says 3 held as before")
    else:
        failures.append(f"  ✗ held by act                 {by_json['period'].get('held_by')!r} "
                        f"{by_said.splitlines()[-1:]!r}")

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
                                             "diagnostic", "frame", "total", "tokens"}
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
