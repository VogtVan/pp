"""Scenario `awaits` -- what a saved run WAITS for, read by the one face a launcher reads it with,
`persistence.awaits(slot)`:
- a slot whose root is exhausted says `message`; a slot with a step pending says `production`; no
  slot at all says `production`
- a renewal mark -- no frames, what the run waited for kept apart -- says what it kept, never
  `production` for lack of frames
- the face reads no conduction mode: a run the LLM conducts and a run its principal conducts, both
  fresh, say the same await -- the one `awaits_of` says of their state
"""
from __future__ import annotations

import json

from conductor.state import persistence
from tests.harness import cli


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    face = getattr(persistence, "awaits", None)
    if face is None:
        failures.append("  ✗ the face                   persistence.awaits is absent")
        return 0
    state = bench.temp()
    parked = state / "session-aaaaaa.json"
    pending = state / "session-bbbbbb.json"
    marked = state / "session-cccccc.json"
    missing = state / "session-dddddd.json"
    parked.write_text(json.dumps({"frames": [{"instructions": [{"done": True}]}], "turns": 1}), encoding="utf-8")
    pending.write_text(json.dumps({"frames": [{"instructions": [{"done": True}, {"done": False}]}]}), encoding="utf-8")
    marked.write_text(json.dumps({"renewed": {"at": "2026-10-23T00:00:00+00:00", "from": {}, "to": {}},
                                  "log": None, "turns": 2, "off": [], "awaits": persistence.MESSAGE}), encoding="utf-8")

    # --- the slot's frames say the await; no slot says production -------------------------------------
    said = [face(parked), face(pending), face(missing)]
    if said == [persistence.MESSAGE, persistence.PRODUCTION, persistence.PRODUCTION]:
        held("the slot says its await", "root exhausted: message; a step pending: production; no slot: production")
    else:
        failures.append(f"  ✗ slot                        {said!r}")

    # --- a renewal mark says what it kept -----------------------------------------------------------
    kept = face(marked)
    if kept == persistence.MESSAGE and persistence.awaits_of(json.loads(marked.read_text(encoding="utf-8"))) == persistence.PRODUCTION:
        held("a renewal mark says what it kept", "the mark has no frames (awaits_of would say production); the "
             "face says the message it waited for")
    else:
        failures.append(f"  ✗ renewal mark                {kept!r}")

    # --- the two conductions: the face reads no mode ------------------------------------------------
    env = bench.env("awaits")
    llm = env.cli("-new")
    principal = cli(env.engine, "-new", cwd=env.root, env={"PP_CONDUCTED_BY_PRINCIPAL": "true"})
    slots = persistence.slots(env.made)
    modes = sorted(persistence.mode_of(one) for one in slots)
    awaited = {persistence.mode_of(one) or "llm": face(one) for one in slots}
    agreed = {persistence.mode_of(one) or "llm": persistence.awaits_of(json.loads(one.read_text(encoding="utf-8")))
              for one in slots}
    if (llm.returncode == 0 and principal.returncode == 0 and len(slots) == 2 and modes == ["", persistence.PRINCIPAL]
            and awaited == agreed and len(set(awaited.values())) == 1):
        held("the face reads no conduction mode", f"an LLM-conducted run and a principal-conducted run, both fresh: "
             f"{awaited} -- the same await, the one awaits_of says of each state")
    else:
        failures.append(f"  ✗ two conductions             rc={llm.returncode},{principal.returncode} modes={modes} "
                        f"awaited={awaited} agreed={agreed}")
    return 0
