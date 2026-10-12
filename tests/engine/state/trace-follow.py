"""Scenario `trace-follow` -- 3 case(s) (plan agent, batch le-suivi-de-l-equipe, 2026-10-01):
the engine READS a run's trace for whoever follows a run -- `pp-agent run` for one wake-up,
`pp-team watch` for a team's -- once, at `conductor.state.log`.
- `follow` reads a trace from its start or from its end, renders the new lines alone at every
  call, finds the file through the slot once it exists, and holds a line still being written
  until its end
- `step_of` says a step's word: opened, the stack and `· parked`, answer, refused <code>,
  repair <doc>, skill <name>, compacted -- and nothing for a cut, a chunk or a weight
- `said` renders the text form `[HH:MM:SS] <key> · <line>`, the agent before the key when one
  is named, and the JSON form `{at, run, event, …}` with `agent` when one is named
"""
from __future__ import annotations

import io
import json
import re
import tempfile
from contextlib import redirect_stderr
from pathlib import Path

from conductor.state import log, persistence


def _event(path: Path, text: str) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    meta = Path(tempfile.mkdtemp(prefix="pp-follow-")) / ".pp"
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
    return 0
