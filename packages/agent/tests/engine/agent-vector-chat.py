"""Scenario `agent-vector-chat` -- the vectors a CONVERSATION names (`agent chat --vector`), mounted by the launcher at
every exchange as a wake-up's are, on the house of `agent-vector` (`Vectored` of the support module: `agent`
and `plan` pinned, a root of documents holding a shared plan whose batch carries a law):
- a conversation takes the flag as a wake-up does: `chat --vector` mounts the batch before its first message and
  again before its second, each `opened` saying the vector; `chat --run <key>` says the kept set in its `ready` and,
  without the flag, mounts it at its exchange, the law asked at its proof; `--vector <other>` replaces it,
  `--vector -` empties it (`ready.vectors` empty, no law on the exchange's block)
- a vector refused in a conversation closes it: rc 2, `vector-refused` first with its cause, nothing launched -- at a
  resume the run as it was, at an opening the run opened and never launched
"""
from __future__ import annotations

import json

from tests.harness import support

A = support(__file__, "agent")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    v = A.Vectored(bench)
    h, keys, counted, fresh = v.h, v.h.keys, v.h.counted, v.fresh
    shared, code, law_text, asks = v.shared, v.code, v.law_text, v.asks
    vector, phase, ghost_vector = v.vector, v.phase, v.ghost_vector
    prompts, flow, mounts = v.prompts, v.flow, v.mounts
    refused, opened_vectors, turns = v.refused, v.opened_vectors, v.turns

    # --- a conversation takes the flag: mounted at every exchange, kept, replaced, emptied ---------------------
    def chat(*flags: str, stdin: str):
        return h.call("agent", "chat", "agents/ag1", *flags, *h.harnessed("play"), stdin=stdin)

    def events(played) -> list[dict]:
        return [json.loads(line) for line in (played.stdout.splitlines() if played else []) if line.startswith("{")]

    def new_prompts(before: dict) -> list[str]:
        return [text for name, text in prompts().items() if name not in before]

    quit_ = json.dumps({"kind": "quit"}) + "\n"
    known, seen = set(keys()), prompts()
    talked = chat("--documents", str(shared), "--vector", vector, stdin="un\ndeux\n")
    key_c = fresh(known)
    mounted_talk = mounts(key_c)
    asked_twice = len([one for one in new_prompts(seen) if asks.search(one)])
    lawful = any(f"{code}  {law_text}" in one for one in new_prompts(seen))
    ready_kept = (events(chat("--run", key_c, "--json", stdin=quit_)) or [{}])[0] if key_c else {}
    seen = prompts()
    resumed = chat("--run", key_c, stdin="reprise\n") if key_c else None
    resumed_asks, mounted_resumed = any(asks.search(one) for one in new_prompts(seen)), mounts(key_c)
    seen = prompts()
    swapped = chat("--run", key_c, "--vector", phase, stdin="trois\n") if key_c else None
    swapped_asks = any(asks.search(one) for one in new_prompts(seen))
    kept_swap, mounted_swap = opened_vectors(key_c)[-1:], mounts(key_c)
    seen = prompts()
    emptied = chat("--run", key_c, "--vector", "-", "--json",
                   stdin=json.dumps({"kind": "message", "text": "quatre"}) + "\n" + quit_) if key_c else None
    ready_empty = (events(emptied) or [{}])[0]
    emptied_law = any(code in one for one in new_prompts(seen))
    if (talked.returncode == 0 and key_c and lawful and asked_twice >= 2 and mounted_talk == 2
            and opened_vectors(key_c)[:2] == [[vector], [vector]]
            and ready_kept.get("kind") == "ready" and ready_kept.get("vectors") == [vector]
            and resumed is not None and resumed.returncode == 0 and resumed_asks and mounted_resumed == 3
            and swapped is not None and swapped.returncode == 0 and kept_swap == [[phase]] and mounted_swap == 3
            and not swapped_asks
            and emptied is not None and emptied.returncode == 0 and ready_empty.get("vectors") == []
            and opened_vectors(key_c)[-1:] == [None] and not emptied_law):
        held("(j) a conversation mounts its vectors", f"run {key_c}: `chat --vector {vector}` -- the law {code} on the "
             f"first exchange's block, asked at the proof of both exchanges, the batch mounted twice; `chat --run "
             f"{key_c}` says ready.vectors {ready_kept.get('vectors')} and, without the flag, mounts the kept set -- "
             f"the batch mounted a third time, {code} asked at that exchange's proof; `--vector {phase}` replaces the set, "
             "`--vector -` empties it -- ready.vectors [], no law on the exchange")
    else:
        failures.append(f"  ✗ (j) the conversation       rc={talked.returncode}/{swapped.returncode if swapped else None}/"
                        f"{emptied.returncode if emptied else None} key={key_c!r} law={lawful} asked={asked_twice} "
                        f"mounts={mounted_talk}/{mounts(key_c)} opened={opened_vectors(key_c)} ready={ready_kept.get('vectors')}/"
                        f"{ready_empty.get('vectors')} swap={kept_swap}/{mounted_swap}/{swapped_asks} "
                        f"emptied_law={emptied_law} resumed={resumed.returncode if resumed else None}/{resumed_asks}/"
                        f"{mounted_resumed} {talked.stderr[-300:]!r}")

    # --- a vector refused in a conversation closes it -------------------------------------------------------
    before_counts, before_turns = counted(), turns(key_c)
    ghosted = chat("--run", key_c, "--vector", ghost_vector, stdin="cinq\n") if key_c else None
    said = [one for one in flow(key_c) if one.get("kind") == "refused"]
    known = set(keys())
    opening = chat("--documents", str(shared), "--vector", ghost_vector, stdin="six\n")
    key_g = fresh(known)
    if (refused(ghosted, "path-unknown") and said and said[-1].get("code") == "vector-refused"
            and said[-1].get("vector") == ghost_vector and turns(key_c) == before_turns
            and refused(opening, "path-unknown") and key_g
            and counted() == before_counts):
        held("(k) a vector refused closes the conversation", f"`chat --run {key_c} --vector {ghost_vector}`: rc 2, "
             f"`vector-refused` path-unknown, the flow's `refused` names it, the run as it was; at an opening run "
             f"{key_g} opened and never launched -- nothing recorded")
    else:
        failures.append(f"  ✗ (k) refused in a chat       rc={ghosted.returncode if ghosted else None}/{opening.returncode} "
                        f"said={said[-1:]} turns={before_turns}/{turns(key_c)} key={key_g!r} "
                        f"counts={before_counts}/{counted()} {(ghosted.stderr[-200:] if ghosted else '')!r} "
                        f"{opening.stderr[-200:]!r}")
    return 0
