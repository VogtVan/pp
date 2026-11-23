"""Scenario `agent-vector-unserved` -- the bare call that serves the first prompt of an exchange FAILS once the
vectors are mounted under the hold, on the house of `agent-vector` (`Vectored` of the support module):
- (a) a run stands with its output left open (a mount refused once the message opened the exchange); the slot's
  open output is damaged by the test, so that the engine's bare call fails; `--run <key>` with a vector mounts it
  under the hold, then the bare call fails: rc 2, nothing launched -- and the run is left as a gesture refused
  after the message leaves it: the message's line at `messages.jsonl`, a `refused` event in the run's flow,
  `agent status --json` saying the run standing, never `dead`; neither the mount refused nor the bare call
  that failed rendered a block
- (b) the damage undone, `--run <key>` with the vector takes the run up: one output, each step's line once
"""
from __future__ import annotations

import json

from conductor import persistence
from tests.harness import support

A = support(__file__, "agent")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    v = A.Vectored(bench)
    h, keys, fresh, flow, resume = v.h, v.h.keys, v.fresh, v.flow, v.resume

    known = set(keys())
    plain = h.wake("un", "play", "--documents", str(v.shared))
    key = fresh(known)
    own = f"agent-run:./{key}"                             # verified by pp-agent, which no block of TURN offers
    stopped = resume(key, "deux", "--vector", own)
    slot = persistence.slot_of(h.agent_meta, key)
    state = json.loads(slot.read_text(encoding="utf-8")) if key else {}
    left = bool((state.get("held") or {}).get("open"))
    if left:                                               # a reading no output can be assembled from
        state["held"]["payloads"] = list(state["held"].get("payloads", [])) + [[0]]
        slot.write_text(json.dumps(state), encoding="utf-8")
    launches, refused_before = len(h.responses()), len([one for one in flow(key) if one.get("kind") == "refused"])
    failed = resume(key, "trois", "--vector", v.vector)
    sent = [one for one in h.messages() if one.get("run") == key and one.get("message") == "trois"]
    said = [one for one in flow(key) if one.get("kind") == "refused"]
    joined = [one for one in h.trace(key) if one.get("kind") == "held" and one.get("act") == "mount" and one.get("open")]
    face = h.face(key).get("state")
    rendered = [one for one in (v.exchanges_traced(key) or [[]])[-1] if one.get("kind") == "block"]
    if (plain.returncode == 0 and key and v.refused(stopped, "offer-absent") and left and not rendered
            and failed is not None and failed.returncode == 2 and len(joined) == 1
            and len(h.responses()) == launches and len(sent) == 1
            and len(said) == refused_before + 1 and str(said[-1].get("detail") or "")
            and said[-1].get("code") == "first-prompt-unserved"
            and face not in (None, "dead")):
        held("(a) a first prompt unserved leaves the run on record", f"run {key}: the vector mounted under the hold, "
             "the bare call failed -- rc 2, nothing launched, no block rendered since the message; the message's "
             f"line at messages.jsonl, a refused event in the flow, the run {face} at agent status, never dead")
    else:
        failures.append(f"  ✗ (a) a first prompt unserved   rc={plain.returncode}/{stopped.returncode if stopped else None}/"
                        f"{failed.returncode if failed else None} key={key!r} left={left} joined={len(joined)} "
                        f"rendered={len(rendered)} "
                        f"responses={launches}/{len(h.responses())} sent={len(sent)} "
                        f"refused={refused_before}/{len(said)} code={(said[-1:] or [{}])[0].get('code')!r} state={face!r} "
                        f"held={sorted((json.loads(slot.read_text(encoding='utf-8')).get('held') or {})) if key else None} "
                        f"{(failed.stderr[-300:] if failed else '')!r}")

    # --- (b) the damage undone: the next wake-up renders the exchange once ----------------------------------
    state = json.loads(slot.read_text(encoding="utf-8")) if key else {}
    if state.get("held"):                                  # the open output as the calls left it
        state["held"]["payloads"] = [one for one in state["held"].get("payloads", []) if one != [0]]
        slot.write_text(json.dumps(state), encoding="utf-8")
    seen = v.prompts()
    taken = resume(key, "quatre", "--vector", v.vector)
    prompt = v.first_prompt(seen, v.prompts())
    head = [v.before_answer(one) for one in v.exchanges_traced(key)[-1:]]
    after = [v.blocks_after_mounts(one) for one in head]
    if (taken is not None and taken.returncode == 0 and v.once(prompt)
            and [v.blocks_before_mounts(one) for one in head] == [0]
            and [between for between, _ in after] == [0] and all(behind >= 1 for _, behind in after)
            and not (json.loads(slot.read_text(encoding="utf-8")).get("held") or {})):
        held("(b) the run taken up renders once", f"run {key}: `--run` with the vector -- no block before the "
             "last mount, one output after it, each step's line once, nothing held at the run")
    else:
        failures.append(f"  ✗ (b) the run taken up          rc={taken.returncode if taken else None} "
                        f"once={v.once(prompt)} after={after} {(taken.stderr[-300:] if taken else '')!r}")
    return 0
