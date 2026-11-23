"""Scenario `awaits` -- what a saved run WAITS for, read by the one face a launcher reads it with,
`persistence.awaits(slot)`:
- a slot whose root is exhausted says `message`; a slot with a step pending says `production`; no
  slot at all says `production`
- a renewal mark -- no frames, what the run waited for kept apart -- says what it kept, never
  `production` for lack of frames
- a fresh run says the await `awaits_of` says of its state
"""
from __future__ import annotations

import json

from conductor.state import persistence


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

    # --- a fresh run: the face says what awaits_of says of its state --------------------------------
    env = bench.env("awaits")
    opened = env.cli("-new")
    slots = persistence.slots(env.made)
    awaited = [face(one) for one in slots]
    agreed = [persistence.awaits_of(json.loads(one.read_text(encoding="utf-8"))) for one in slots]
    if opened.returncode == 0 and len(slots) == 1 and awaited == agreed:
        held("the face says the state's await", f"a fresh run: {awaited} -- the one awaits_of says of its state")
    else:
        failures.append(f"  ✗ the fresh run               rc={opened.returncode} awaited={awaited} agreed={agreed}")
    return 0
