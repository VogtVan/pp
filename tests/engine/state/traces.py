"""Scenario `traces` -- what a run's trace holds, how it is named, read, followed and counted:
- the costs of the runs, read from their traces:
  - an exchange runs from the prompt to the closing that waits: three exchanges, counted
  - the intervals belong to the event that ends them: proof, script call, work, answer
  - a reshow after a script call counts apart; a hole over thirty minutes is left out
  - the mass and the tokens come from the trace's weights alone: a trace without them says none
  - the values are counted by keyword: an answer whose channel goes to the tool is one, a bare
    close and a stray production are none
  - a trace older than the answer's channel counts the value keywords alone, and says so
  - the period's averages per closed exchange, the table a `values` column
  - the json hands the values per exchange and the averages of the period
  - a run its principal conducts: the `held` outputs and the principal's `advance` calls are
    counted per exchange and said on the period's line; a run the LLM conducts says nothing of them
  - the held outputs by act: the json counts them by the act each hold names, a hold without an
    act a value; the period's line keeps its words
  - a rendered block writes its weight: the boot of a fresh environment carries it, the block line
    itemizes its payloads by subject
  - the inline outputs of `conduction: hybrid` are counted and said; a provider, a sink and an
    `exec` the engine played count as script calls, their time as gesture
  - an engine-run provider leaves its named line with its package and its duration
- the naming: two `-new` in one second write a trace each, named by its key, both counted
- the following, at `conductor.state.log`:
  - `follow` reads a trace from its start or from its end, renders the new lines alone at every
    call, finds the file through the slot once it exists, and holds a line still being written
    until its end
  - `step_of` says a step's word: opened, the stack and `· parked`, answer, refused <code>,
    repair <doc>, skill <name>, compacted -- and nothing for a cut, a chunk or a weight
  - `said` renders the text form `[HH:MM:SS] <key> · <line>`, the agent before the key when one
    is named, and the JSON form `{at, run, event, …}` with `agent` when one is named
- the token estimate:
  - it holds against the reference encoding: four synthetic texts of one nature each, their
    o200k counts recorded, the exact counts and the tolerance measured
  - it is a pure function of the standard library: empty, a word, a run of spaces, an accented
    word against an ascii one, a punctuation run
"""
from __future__ import annotations

import io
import json
import re
from contextlib import redirect_stderr
from datetime import datetime, timedelta, timezone
from pathlib import Path

from conductor.state import instance, log, metrics, persistence, traces
from tests.harness import cli

# the witness provider package, pinned by hand in the instance's vendor
PROBE = "probe"
PROBE_TOKEN = "probe-lines"
PROBE_SKILL = "pp-probe"
PROBE_MANIFEST = f"name: {PROBE}\nversion: 0.0.1\ndescription: a witness package\nrequires: [kit]\n"
PROBE_PROVIDER = (f"---\nname: PROBE\nkind: doc\ndescription: a witness provider\nprovides: {PROBE_TOKEN}\n"
                  f"with: {PROBE_SKILL}\n---\n\nPROBE provides\n")
PROBE_CODE = "#!/usr/bin/env python3\nprint('the probe says one line')\n"

# the token estimate's witnesses: GENERATED here, byte for byte the texts measured with tiktoken
# (o200k_base) outside the engine -- no phrase of any kept document, no fixture file to keep in step
FR = ("La rivière longe le village avant de rejoindre la plaine ; les jardins descendent jusqu'à l'eau, "
      "et chaque maison garde une barque amarrée sous les saules. Le matin, la brume efface les collines, "
      "puis le soleil rend aux toits leur couleur d'ardoise. ")
EN = ("The archive keeps one folder per year, and every folder holds the letters in the order they arrived; "
      "a reader who wants the reply must find the next folder, because the copies were never filed with "
      "their originals. ")
CODE = ("def merge(left: list[int], right: list[int]) -> list[int]:\n    out: list[int] = []\n    i = j = 0\n"
        "    while i < len(left) and j < len(right):\n        if left[i] <= right[j]:\n            out.append(left[i]); i += 1\n"
        "        else:\n            out.append(right[j]); j += 1\n    return out + left[i:] + right[j:]\n\n")
ROWS = "\n".join(f"| item-{n} | {n*137:,} | {'yes' if n % 3 else 'no'} | {n * 0.75:.2f} |" for n in range(1, 25))
TABLE = "| name | count | kept | ratio |\n|---|---:|:---:|---:|\n" + ROWS + "\n"
OBJECTS = [{"id": f"r{n:03d}", "label": f"row {n}", "score": round(n / 7, 3), "tags": ["alpha", "beta"][: n % 3]}
           for n in range(40)]
TEXTS = {
    "prose_fr": FR * 12,
    "prose_en": EN * 14,
    "code_and_table": CODE * 6 + TABLE,
    "json_objects": json.dumps(OBJECTS, ensure_ascii=False, indent=1),
}
# the reference counts (tiktoken o200k_base) and the estimator's exact ones
TRUTH = {"prose_fr": 745, "prose_en": 589, "code_and_table": 956, "json_objects": 1530}
EXACT = {"prose_fr": 697, "prose_en": 603, "code_and_table": 1002, "json_objects": 1450}
TOLERANCE = 0.10      # the measured drift of one nature alone stays under 7 %; 10 % is the bound


def _write(path: Path, events: list[tuple[int, dict]], start: datetime) -> None:
    lines = []
    for offset, data in events:
        at = (start + timedelta(seconds=offset)).isoformat(timespec="milliseconds")
        lines.append(json.dumps({"at": at, **data}, ensure_ascii=False))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _cells(rendered: str, first: str) -> list[str]:
    """-> the cells of the table row whose first cell is `first`, [] when none."""
    for line in rendered.splitlines():
        if line.startswith("|"):
            cells = [one.strip() for one in line.strip().strip("|").split("|")]
            if cells and cells[0] == first:
                return cells
    return []


def _event(path: Path, text: str) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text)


def _vendor_probe(made: Path) -> None:
    """The witness provider package pinned at `made`, as an install vendors one: its manifest,
    its provider document, its skill beside its SKILL.md, the instance's pins naming it."""
    root = made / ".sys" / "vendor" / f"{PROBE}@0.0.1"
    (root / "procs").mkdir(parents=True, exist_ok=True)
    (root / "package.yaml").write_text(PROBE_MANIFEST, encoding="utf-8")
    (root / "procs" / "PROBE.md").write_text(PROBE_PROVIDER, encoding="utf-8")
    home = root / "skills" / PROBE_SKILL
    home.mkdir(parents=True, exist_ok=True)
    (home / "SKILL.md").write_text(f"---\nname: {PROBE_SKILL}\ndescription: a witness\n---\n\n{PROBE_SKILL}\n",
                                   encoding="utf-8")
    (home / f"{PROBE_SKILL}.py").write_text(PROBE_CODE, encoding="utf-8")
    pinned = instance.read(made)
    pinned["packages"][PROBE] = "0.0.1"
    instance.write(made, pinned)


def costs(bench) -> None:
    """The costs of the runs, read from synthetic traces and from a booted environment."""
    held, failures = bench.held, bench.failures
    state = bench.temp()
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
        (330, {"kind": "gesture", "name": "pp-wit", "segment": 1, "frame": "TURN"}),
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
    older_row = _cells(rendered, "2026-08-26 16:00")
    weighed_row = _cells(rendered, "2026-08-26 15:00")
    if (first.mass == 3 * 450 and first.parts["payload"] == 900 and two.exchanges[0].mass is None
            and first.tokens == 3 * 120 and two.exchanges[0].tokens is None
            and first.given == {"chars": 2, "tokens": 1} and "tokens" not in first.parts
            and older_row[1:6] == ["abc123", "1", "2 (+0)", "—", "—"]
            and weighed_row[1:6] == ["—", "3", "7 (+1)", "960", "3 600"]
            and payload["period"]["mass"] == 8 * 450 and payload["period"]["tokens"] == 8 * 120
            and payload["period"]["given"] == {"chars": 4, "tokens": 2}
            and payload["scope"]["days"] == 7):
        held("the mass and the tokens are the weights' sum", "1 350 chars / 360 tokens on the "
             "first exchange, — on a trace without weights, 3 600 / 960 over the period, the "
             "agent's answers 4 chars / 2 tokens, the table and the json agree")
    else:
        failures.append(f"  ✗ mass                       {first.mass} {two.exchanges[0].mass} "
                        f"{older_row} {weighed_row}")

    # --- the values, by keyword: what the agent hands the conduction -----------------------
    valued = bench.temp()
    _write(valued / "session-20260827T100000Z.jsonl", [
        (0, {"kind": "new"}),
        (0, {"kind": "block", "stack": "TURN{1/3}", "command": "WORK", "wait": False}),
        (10, {"kind": "answer", "instruction": "PROVE ", "given": "[]", "channel": "tool (heredoc)"}),
        (11, {"kind": "answer", "instruction": "PICK member", "given": "ada", "channel": "tool"}),
        (12, {"kind": "answer", "instruction": "PICK member", "given": "bob", "channel": "tool"}),
        (13, {"kind": "answer", "instruction": "FIELD ", "given": "[1]", "channel": "tool (heredoc)"}),
        (14, {"kind": "answer", "instruction": "INFER ", "given": '["a"]', "channel": "tool (heredoc)"}),
        (15, {"kind": "answer", "instruction": "WORK ", "given": "", "channel": "response"}),
        (16, {"kind": "answer", "instruction": "INFER ", "given": "stray", "channel": "response"}),
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

    older = bench.temp()
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
    old_said = traces.render(old_runs, None, None).splitlines()
    old_json = json.loads(traces.render_json(old_runs, None, None))
    if (old_head is not None and getattr(old_head, "values", None) == {"PROVE": 1, "PICK": 1}
            and getattr(old_head, "unchanneled", None) == 3
            and old_json["period"].get("unchanneled") == 3
            and old_json["runs"][0]["detail"][0].get("unchanneled") == 3
            and "; 3 answer(s) " in old_said[-1]):
        held("an older trace counts its value keywords", "PROVE 1, PICK 1 -- the channel-less INFER "
             "is not guessed, and the period's line says how many answers carried no channel")
    else:
        failures.append(f"  ✗ older trace                 {getattr(old_head, 'values', None)!r} "
                        f"{old_json['period'].get('unchanneled')!r} {old_said[-1:]!r}")

    valued_said = traces.render(counted, None, None)
    valued_json = json.loads(traces.render_json(counted, None, None))
    per = valued_json["period"].get("per_exchange") or {}
    header = _cells(valued_said, "run")
    valued_row = _cells(valued_said, "2026-08-27 10:00")
    columns = dict(zip(header, valued_row))
    if (header[:9] == ["run", "key", "exchanges", "blocks (+reshows)", "tokens ≈", "mass", "proofs",
                       "values", "repairs"]
            and [columns.get(name) for name in header[1:9]] == ["—", "3 (1 open)", "5 (+0)", "—", "—", "1",
                                                                "5", "0"]
            and per.get("closed") == 2 and per.get("calls") == 2.5 and per.get("chunks") == 0.5
            and per.get("values") == 2.5 and per.get("gestures") == 0.0
            and per.get("by_keyword") == {"PROVE": 0.5, "PICK": 1.0, "FIELD": 0.5, "INFER": 0.5}
            and valued_said.splitlines()[-1].startswith("per closed exchange: 2.5 ")):
        held("the averages per closed exchange", "5 values over the run in their column; 2.5 calls "
             "(0.5 chunk), 2.5 values per closed exchange -- the open one left out")
    else:
        failures.append(f"  ✗ per exchange line           {columns!r} {per!r}")

    if (valued_json["runs"][0]["detail"][0].get("values") == {"PROVE": 1, "PICK": 2, "FIELD": 1, "INFER": 1}
            and valued_json["period"].get("values") == {"PROVE": 1, "PICK": 2, "FIELD": 1, "INFER": 1}
            and per.get("closed") == 2 and per.get("calls") == 2.5 and per.get("chunks") == 0.5
            and per.get("values") == 2.5 and per.get("by_keyword", {}).get("PICK") == 1.0):
        held("the json carries the values", "per exchange and over the period, with the averages "
             "per closed exchange")
    else:
        failures.append(f"  ✗ values json                 {valued_json['period'].get('values')!r} {per!r}")

    # --- a run its principal conducts: the held outputs and the principal's calls -------------
    led = bench.temp()
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
    acts = bench.temp()
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

    # --- the inline outputs of a hybrid conduction, the scripts the engine played ----------
    mixed = bench.temp()
    _write(mixed / "session-20260827T130000Z.jsonl", [
        (0, {"kind": "new", "conducted_by": "principal"}),
        (0, {"kind": "block", "stack": "TURN{1/2}", "command": "WORK", "wait": False}),
        (2, {"kind": "exec", "skill": "pp-wit", "verb": "stamp", "document": "TURN"}),
        (4, {"kind": "block", "stack": "TURN ▸ LAPS{1/1}", "command": "INFER", "wait": False}),
        (5, {"kind": "inline", "act": "door", "weight": {"chars": 300, "tokens": 80}}),
        (8, {"kind": "provider", "name": "pp-wit", "token": "wit-items", "package": "wit", "ms": 3}),
        (9, {"kind": "answer", "instruction": "FIELD ", "given": "[]", "channel": "tool (heredoc)"}),
        (9, {"kind": "block", "stack": "TURN ▸ LAPS{1/1}", "command": "INFER", "wait": False}),
        (9, {"kind": "inline", "act": "value", "weight": {"chars": 300, "tokens": 80}}),
        (12, {"kind": "sink", "skill": "pp-wit", "said": 10}),
        (20, {"kind": "answer", "instruction": "PROVE ", "given": "[]", "channel": "tool (heredoc)"}),
        (20, {"kind": "block", "stack": "TURN{2/2}", "command": "", "wait": True}),
        (20, {"kind": "held", "weight": {"chars": 400, "tokens": 100}}),
        (30, {"kind": "advance", "held": True, "prompt": False}),
    ], start)
    mixed_runs = traces.runs(mixed)
    mixed_said = traces.render(mixed_runs, None, None)
    mixed_json = json.loads(traces.render_json(mixed_runs, None, None))
    mixed_led = mixed_runs[0].exchanges[0] if mixed_runs and mixed_runs[0].exchanges else None
    if (mixed_led is not None and mixed_led.inline == 2 and mixed_led.held == 1 and mixed_led.gestures == 3
            and mixed_led.execs == 1 and round(mixed_led.seconds["gesture"], 1) == 8.0
            and mixed_json["period"].get("inline") == 2 and mixed_json["period"].get("gestures") == 3
            and "2.0 inline" in mixed_said and "3.0 script call(s)" in mixed_said
            and "inline" not in rendered):
        held("the inline outputs and the engine's scripts are counted", "2 inline (door, value), 1 held; an exec, a "
             "provider and a sink make 3 script calls and 8 s of gesture; the period's line says them; a run "
             "the LLM conducts says no inline")
    else:
        failures.append(f"  ✗ inline / scripts            {mixed_led and mixed_led.as_dict()} "
                        f"{mixed_said.splitlines()[-1:]!r}")

    # --- an engine-run provider leaves its named line --------------------------------
    provided_env = bench.env("provided")
    made2 = provided_env.made
    _vendor_probe(made2)
    (made2 / "procs").mkdir(exist_ok=True)
    (made2 / "procs" / "TAKER.md").write_text(     # a consumer of the probe's token
        "---\nname: TAKER\nkind: proc\ndescription: consumes the lines\n"
        f"payloads: {PROBE_TOKEN}\nproc: |\n  INFER\n---\none line\n", encoding="utf-8")
    (made2 / "procs" / "OUTER.md").write_text(
        "---\nname: OUTER\nkind: proc\ndescription: calls the taker\nproc: |\n"
        "  CALL TAKER.md\n---\nouter\n", encoding="utf-8")
    provided = provided_env.conductor()
    provided.start(provided.boot("OUTER.md"))    # the CALL opens TAKER: its providers run
    written = sorted((made2 / instance.STATE).glob("session-*.jsonl"))
    events = traces.read(written[-1]) if written else []
    providers = [one for one in events if one.get("kind") == "provider"]
    if (providers and all(one.get("name") and "ms" in one for one in providers)
            and any(one.get("name") == PROBE_SKILL and one.get("token") == PROBE_TOKEN
                    and one.get("package") == PROBE for one in providers)):
        held("a provider leaves its named line", f"{PROBE_SKILL} ran for `{PROBE_TOKEN}` on TAKER's "
             "opening, its package and duration on the line")
    else:
        failures.append(f"  ✗ provider line              {providers[:2]!r}")


def naming(bench) -> None:
    """Two `-new` in one second: a trace each, named by its key, both counted."""
    held, failures = bench.held, bench.failures
    env = bench.env("named")
    first = cli(env.engine, "-new", cwd=env.root)
    second = cli(env.engine, "-new", cwd=env.root)
    keys = [m.group(1) if (m := re.search(r"run ([0-9a-f]{6})", one.stdout)) else "?" for one in (first, second)]
    state = env.made / instance.STATE
    named = {one.name for one in state.glob("session-*.jsonl")}
    a = [one for one in named if one.endswith(f"-{keys[0]}.jsonl")]
    b = [one for one in named if one.endswith(f"-{keys[1]}.jsonl")]
    stats = env.cli("-stats", "1")
    if first.returncode or second.returncode:
        failures.append(f"-new failed: {first.stderr.strip()} {second.stderr.strip()}")
    elif len(a) != 1 or len(b) != 1 or keys[0] == keys[1]:
        failures.append(f"traces named by key: {sorted(named)} keys={keys}")
    elif keys[0] not in stats.stdout or keys[1] not in stats.stdout:
        failures.append(f"-stats does not count both runs: {stats.stdout[:200]}")
    elif traces._stamp_of(state / a[0]) == Path(a[0]).stem:
        failures.append(f"_stamp_of could not read the hour of {a[0]}")
    else:
        held("two -new in one second: a trace each, named by its key, both counted",
             f"{a[0]} · {b[0]}")


def following(bench) -> None:
    """The engine READS a run's trace for whoever follows a run, once, at `conductor.state.log`."""
    held, failures = bench.held, bench.failures
    meta = bench.temp() / ".pp"
    state = meta / ".sys" / "state"
    state.mkdir(parents=True)
    key = "ab12cd"
    slot = persistence.slot_of(meta, key)
    trace = state / f"session-20261001T200000Z-{key}.jsonl"

    # --- follow: from the start, from the end, the new lines alone, a torn line held --------------
    early = log.follow(meta, key)                       # the slot does not exist yet
    none_yet = early.fresh()
    slot.write_text(json.dumps({"log": trace.name}), encoding="utf-8")
    _event(trace, json.dumps({"kind": "new"}) + "\n")
    _event(trace, json.dumps({"kind": "block", "stack": "BOOT{1/2}", "wait": False}) + "\n")
    first = early.fresh()
    again = early.fresh()
    late = log.follow(meta, key, from_end=True)        # from the end: the two lines above are past
    _event(trace, json.dumps({"kind": "answer"}) + "\n")
    _event(trace, '{"kind": "block", "stack": "TURN')   # a line still being written
    torn = late.fresh()
    _event(trace, '{2/2}", "wait": true}\n')
    whole = late.fresh()
    if (none_yet == [] and [one.get("kind") for one in first] == ["new", "block"] and again == []
            and [one.get("kind") for one in torn] == ["answer"]
            and [(one.get("kind"), one.get("stack"), one.get("wait")) for one in whole] == [("block", "TURN{2/2}", True)]
            and late.fresh() == []):
        held("follow reads the new lines alone", "nothing before the slot; new + block once; from the end "
             "the answer alone; a torn line held until its end, then the parked block")
    else:
        failures.append(f"  ✗ follow                      none={none_yet} first={first} again={again} torn={torn} "
                        f"whole={whole}")

    # --- step_of: the word of a step ----------------------------------------------------------------
    words = [log.step_of(one) for one in (
        {"kind": "new"}, {"kind": "block", "stack": "TURN{2/4}", "wait": False},
        {"kind": "block", "stack": "TURN{4/4}", "wait": True}, {"kind": "answer"},
        {"kind": "refusal", "code": "call-busy"}, {"kind": "repair", "document": "TURN"},
        {"kind": "repair-in-place"}, {"kind": "gesture", "name": "pp-plan"}, {"kind": "compacted"},
        {"kind": "cut"}, {"kind": "chunk"}, {"kind": "weight"})]
    said_words = [one[0] if one else None for one in words]
    if said_words == ["opened", "TURN{2/4}", "TURN{4/4} · parked", "answer", "refused call-busy", "repair TURN",
                      "repair in place", "skill pp-plan", "compacted", None, None, None] \
            and words[2][1] == "block" and words[2][2] == {"stack": "TURN{4/4}", "wait": True} \
            and words[4][2] == {"code": "call-busy"}:
        held("step_of says the word of a step", "opened, the stack, · parked, answer, refused, repair, skill, "
             "compacted; nothing for a cut, a chunk, a weight")
    else:
        failures.append(f"  ✗ step_of                     {said_words}")

    # --- said: the text form and the JSON form, with or without an agent -------------------------------
    out = io.StringIO()
    with redirect_stderr(out):
        log.said(key, "opened", "new", {}, False)
        log.said(key, "TURN{2/4}", "block", {"stack": "TURN{2/4}", "wait": False}, False, who="m")
        log.said(key, "opened", "new", {}, True)
        log.said(key, "no event for 3s", "quiet", {"seconds": 3}, True, who="m")
    lines = out.getvalue().splitlines()
    objects = [json.loads(one) for one in lines[2:]] if len(lines) == 4 else []
    stamp = re.compile(r"^\[\d\d:\d\d:\d\d\] ")
    if (len(lines) == 4 and stamp.match(lines[0]) and lines[0].endswith(f"] {key} · opened")
            and lines[1].endswith(f"] m · {key} · TURN{{2/4}}")
            and objects and objects[0].get("run") == key and objects[0].get("event") == "new"
            and "agent" not in objects[0] and "at" in objects[0]
            and objects[1] == {**objects[1], "run": key, "event": "quiet", "seconds": 3, "agent": "m"}):
        held("said renders both forms", "text: [HH:MM:SS] <key> · <line>, the agent before the key; JSON: "
             "{at, run, event, …} with agent when named")
    else:
        failures.append(f"  ✗ said                        {lines!r}")


def tokens(bench) -> None:
    """The token estimate: against the reference encoding, and its rules."""
    held, failures = bench.held, bench.failures

    # --- the estimate against the reference --------------------------------------------
    counted = {name: metrics.tokens(text) for name, text in TEXTS.items()}
    within = {name: abs(counted[name] - TRUTH[name]) / TRUTH[name] for name in TEXTS}
    if counted == EXACT and all(drift <= TOLERANCE for drift in within.values()):
        held("the estimate holds against o200k", ", ".join(
            f"{name} {counted[name]}/{TRUTH[name]} ({within[name] * 100:+.1f} %)".replace("+", "")
            for name in TEXTS))
    else:
        failures.append(f"  ✗ tokens estimate            {counted} vs exact {EXACT}, truth {TRUTH}")

    # --- a pure function of the standard library ------------------------------------------
    if (metrics.tokens("") == 0 and metrics.tokens("hello") == 1 and metrics.tokens("   ") == 1
            and metrics.tokens("épaisseurs") > metrics.tokens("thickness")
            and metrics.tokens("réveillées") > metrics.tokens("awakened")
            and metrics.tokens("::::") == 2 and metrics.tokens("a b") == 2
            and metrics.tokens("12345") == 2):
        held("the estimator's rules", "empty 0, a word 1, spaces 1, an accented word splits "
             "sooner, punctuation by pairs, digits by threes")
    else:
        failures.append("  ✗ tokens rules               " + str([metrics.tokens(s) for s in
                        ("", "hello", "   ", "épaisseurs", "thickness", "réveillées", "awakened",
                         "::::", "a b", "12345")]))


def scenario(bench) -> int:
    costs(bench)
    naming(bench)
    following(bench)
    tokens(bench)
    return 0
