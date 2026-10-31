"""Scenario `model-bare` -- 3 case(s) (plan moteur-0.2.0, phase le-banc-de-conduction, batch
l-adaptateur-model, 2026-10-27): the modelled LLM on the BARE channel -- the model calls pp itself,
one launch for the whole exchange:
- launched by hand on a throwaway instance, as the editor's extension launches a model (the message
  on stdin, the root and the door in its environment, no output of pp in the prompt): its first call is
  `./pp -new`, the run it opened is the LLM's and ends parked, its words said, its result line at cost 0
  with its session; no repair
- the `bare-call` variant on that channel: on an instance whose member carries a law of production the
  model types the bare call where the proof is due -- the engine repairs (the empty answer), the model
  conforms, the run ends parked; the trace counts the repair
- `agent chat --json --provider model`: a conducted exchange, then `conduct off` and a second message:
  the second record says `conducted: false`, its flow carries the model's own `./pp -new` as a tool
  call of pp, and the agent holds TWO runs -- the chat's and the one the model opened, parked
"""
from __future__ import annotations

import json

from conductor import persistence
from tests.harness import support

M = support(__file__, "model")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    def result_of(events: list[dict]) -> dict:
        return next((one for one in reversed(events) if one.get("kind") == "result"), {})

    def tools_of(events: list[dict]) -> list[str]:
        return [str(one.get("shell") or "") for one in events if one.get("kind") == "tool"]

    def stats_of(env, key: str) -> dict:
        played = env.cli("-stats", key, "-json")
        try:
            return (json.loads(played.stdout).get("runs") or [{}])[0]
        except ValueError:
            return {}

    # --- the extension's way: the model opens the run ----------------------------------------------------
    env = bench.env("bare")
    (played, seconds) = M.timed(lambda: M.harnessed(env.root, "read the four lines",
                                                    documents=M.DOCS / "read-lines", door="READ_LINES.md"))
    done, events = played
    result = result_of(events)
    slots = persistence.slots(env.made)
    key = persistence.run_id_of(slots[0]) if slots else ""
    words = [one for one in events if one.get("kind") == "words"]
    if (done.returncode == 0 and len(slots) == 1 and tools_of(events)[:1] == [f"{M.harness_module().CONSOLE} -new"]
            and persistence.awaits(slots[0]) == persistence.MESSAGE
            and persistence.mode_of(slots[0]) != persistence.PRINCIPAL
            and result.get("cost_usd") == 0.0 and result.get("error") is None
            and str(result.get("session", "")).startswith("model-") and words
            and stats_of(env, key).get("repairs") == 0):
        held("the model opens and conducts the run itself", f"run {key}: opened by `./pp -new`, the LLM's mode, "
             f"{len(tools_of(events))} call(s), {len(words)} words, parked, 0 repair; cost 0, session "
             f"{result.get('session')}; {seconds} s")
    else:
        failures.append(f"  ✗ bare channel               rc={done.returncode} slots={len(slots)} tools={tools_of(events)} "
                        f"result={result} awaits={persistence.awaits(slots[0]) if slots else None} "
                        f"{done.stderr[-300:]!r}")

    # --- bare-call on the bare channel: an advance, a repair, then conform -------------------------------
    lawful = bench.env("bare-law")
    lawful.write_member(front="constraints.production: |\n  L1  the answer lands\n")
    missed, missed_events = M.harnessed(lawful.root, "hello", variant="bare-call")
    missed_slots = persistence.slots(lawful.made)
    missed_key = persistence.run_id_of(missed_slots[0]) if missed_slots else ""
    counted = stats_of(lawful, missed_key) if missed_key else {}
    thought = [one.get("text") for one in missed_events if one.get("kind") == "thinking"]
    if (missed.returncode == 0 and len(missed_slots) == 1 and persistence.awaits(missed_slots[0]) == persistence.MESSAGE
            and result_of(missed_events).get("missed") is True and "miss bare-call" in thought
            and isinstance(counted.get("repairs"), int) and counted["repairs"] >= 1
            and any(call.rstrip() == f"{M.harness_module().CONSOLE} {missed_key}" for call in tools_of(missed_events))):
        held("bare-call advances and is repaired on the bare channel", f"run {missed_key}: the bare call typed where "
             f"the proof was due, {counted['repairs']} repair counted, the passage ended parked")
    else:
        failures.append(f"  ✗ bare-call bare              rc={missed.returncode} awaits="
                        f"{persistence.awaits(missed_slots[0]) if missed_slots else None} stats={counted} "
                        f"thought={thought} tools={tools_of(missed_events)}")

    # --- agent chat under conduct off: the model opens a run of its own ----------------------------------------
    h = M.House(bench)
    commands = "\n".join(json.dumps(one) for one in ({"kind": "message", "text": "one"}, {"kind": "conduct", "on": False},
                                                     {"kind": "message", "text": "two"}, {"kind": "quit"})) + "\n"
    chat = h.call("agent", "chat", "agents/ag1", "--provider", M.PROVIDER, "--json", stdin=commands)
    told = M.objects(chat.stdout)
    answered = [one for one in told if one.get("kind") == "response"]
    records = h.responses()
    keys = h.keys("ag1")
    chat_key = answered[0].get("run") if answered else ""
    flow = h.flow(chat_key) if chat_key else []
    opened = [one for one in flow if one.get("kind") == "tool" and one.get("exchange") == 2
              and str(one.get("shell", "")).endswith("-new")]
    stray = [key for key in keys if key != chat_key]
    if (chat.returncode == 0 and len(answered) == 2 and len(records) == 2
            and records[0].get("conducted", True) is not False and records[1].get("conducted") is False
            and opened and opened[0].get("pp") is True and len(keys) == 2 and stray
            and h.awaits("ag1", stray[0]) == persistence.MESSAGE and h.awaits("ag1", chat_key) == persistence.MESSAGE):
        held("conduct off: the model opens a run of its own", f"chat run {chat_key} conducted then bare; the bare "
             f"exchange's flow says `./pp -new` as a call of pp; the stray run {stray[0]} parked")
    else:
        failures.append(f"  ✗ conduct off                rc={chat.returncode} answered={len(answered)} records="
                        f"{[one.get('conducted') for one in records]} keys={keys} opened={opened[:1]} "
                        f"{chat.stderr[-300:]!r}")
    return 0
