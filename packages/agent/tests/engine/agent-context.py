"""Scenario `agent-context` -- 5 case(s) (batch la-part-de-pp-dans-le-contexte, 2026-10-10): the flow of an
exchange counted by voice, and the context of a run approached from it.
- under the `stream` witness (per launch: words, 42 thinking tokens, a call of `./pp` and its result, a `Read` in
  error), `run` writes `flow` at its line of `responses.jsonl`: each voice in tokens as the engine estimates them
  (`principal` the head and the message, `conduction` pp's outputs, `pp_input`/`pp_result`, `tool_input`/
  `tool_result`, `words`, `thinking`), `calls` = launches + calls of tools
- `chat --json`: a conducted exchange then a bare one (`conduct off`: one launch, `conduction` 0) each write their
  `flow`
- `stats --json` says `context`: the voices summed and their total, `pp` {tokens, share, served} -- `served` the
  engine's `-stats` tokens, the gap measured --, `calls`, `reread`, `since` null; `window` and `used` null for a
  caller's command, the window of the run's model once its session's provider is one whose adapter declares it
  (`CONTEXT_WINDOWS`)
- `status --json` says each run's `context` reduced {tokens, used, pp}
- a run whose wake-up kept no response says `context: null` at both faces
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

from conductor import metrics
from tests.harness import support

A = support(__file__, "agent")
VOICES = ("principal", "conduction", "pp_input", "pp_result", "tool_input", "tool_result", "words", "thinking")


def objects(text: str) -> list[dict]:
    return [json.loads(one) for one in text.splitlines() if one.strip()]


def expected(h, where, session: str, launches: range, key: str, bare: bool = False) -> dict:
    """-> the flow the `stream` witness's launches carry, from the prompts it kept: the first prompt
    split at pp's output (the head and the message before it), the later ones pp's output alone."""
    tokens = metrics.tokens
    sums = {voice: 0 for voice in VOICES}
    sums["calls"] = 0
    for n in launches:
        prompt = h.read(f".prompt.{session}.{n}", where)
        at = len(prompt) if bare else (prompt.find("▌ pp · run ") if n == launches[0] else 0)
        sums["principal"] += tokens(prompt[:at])
        sums["conduction"] += tokens(prompt[at:]) if prompt[at:] else 0
        sums["pp_input"] += tokens(json.dumps({"command": f"./pp {key} -"}))
        sums["pp_result"] += tokens("ok")
        sums["tool_input"] += tokens(json.dumps({"file_path": "/nowhere"}))
        sums["tool_result"] += tokens("File does not exist.")
        sums["words"] += tokens("witness words")
        sums["thinking"] += 42
        sums["calls"] += 3
    return sums


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)

    # --- run: the flow of one exchange at its record line ------------------------------------------
    windowed_by = next((one for one in A.providers(h.house) if A.declared(h.house, one, "CONTEXT_WINDOWS")), "")
    model, window = next(iter((A.declared(h.house, windowed_by, "CONTEXT_WINDOWS") or {"m": None}).items()))
    played = h.wake("count me", "stream", "--model", model)
    key = h.keys()[0] if h.keys() else ""
    line = h.responses()[-1] if h.responses() else {}
    launches = line.get("launches") or 0
    want = expected(h, h.out, "w-1", range(1, launches + 1), key) if key else {}
    if played.returncode == 0 and key and launches >= 1 and line.get("flow") == want:
        held("run writes the flow of its exchange", f"run {key}, {launches} launch(es): {want}")
    else:
        failures.append(f"  ✗ run flow                    rc={played.returncode} key={key!r} got={line.get('flow')} "
                        f"want={want} {played.stderr[-300:]!r}")

    # --- chat --json: a conducted exchange, then a bare one ----------------------------------------
    where = bench.temp() / "chat"
    argv = [sys.executable, str(h.engine), "--instance", str(h.house), "agent", "chat", "agents/ag1", "--json",
            *h.harnessed_at("stream", where)]
    commands = "".join(json.dumps(one) + "\n" for one in (
        {"kind": "message", "text": "first"}, {"kind": "conduct", "on": False},
        {"kind": "message", "text": "bare one"}, {"kind": "quit"}))
    live = subprocess.run(argv, input=commands, capture_output=True, text=True, cwd=h.ws,
                          env={**os.environ, **h.env}, timeout=120)
    chat_key = next((one for one in h.keys() if one != key), "")
    talked = [one for one in h.responses() if one.get("run") == chat_key]
    if len(talked) == 2:
        conducted = talked[0].get("launches") or 0
        want_c = expected(h, where, "w-1", range(1, conducted + 1), chat_key)
        want_b = expected(h, where, "w-1", range(conducted + 1, conducted + 2), "", bare=True)
    else:
        want_c = want_b = {}
    if (live.returncode == 0 and len(talked) == 2 and talked[0].get("flow") == want_c
            and talked[1].get("conducted") is False and talked[1].get("flow") == want_b
            and want_b.get("conduction") == 0 and want_b.get("calls") == 3):
        held("chat writes the flow of each exchange, bare included", f"run {chat_key}: conducted {want_c}; "
             f"bare {want_b}")
    else:
        failures.append(f"  ✗ chat flow                   rc={live.returncode} {[one.get('flow') for one in talked]} "
                        f"want={want_c} / {want_b} {live.stderr[-300:]!r}")

    # --- stats --json: the context approached, pp's part, the engine's count beside -----------------
    measured = h.call("agent", "stats", "agents/ag1", key, "--json")
    face = objects(measured.stdout)[0] if measured.returncode == 0 and measured.stdout.strip() else {}
    context = face.get("context") or {}
    total = sum(want.get(voice, 0) for voice in VOICES)
    pp = want.get("conduction", 0) + want.get("pp_input", 0) + want.get("pp_result", 0)
    served = (face.get("conduction") or {}).get("tokens")
    if (measured.returncode == 0 and context.get("flow") == {**{v: want.get(v) for v in VOICES}, "total": total}
            and context.get("window") is None and context.get("used") is None
            and context.get("pp") == {"tokens": pp, "share": round(pp / total, 4), "served": served}
            and context.get("calls") == want.get("calls") and context.get("since") is None
            and context.get("reread") == want.get("calls", 0) * (total // 2) and isinstance(served, int)):
        held("stats --json says the context and pp's part", f"total {total} tokens, pp {pp} ({context['pp']['share']:.0%}), "
             f"served by the engine {served} (gap {pp - served:+d} = {(pp - served) / served:+.1%}), calls "
             f"{context['calls']}, reread {context['reread']}; no window for a caller's command")
    else:
        failures.append(f"  ✗ stats context               rc={measured.returncode} {context} total={total} pp={pp} "
                        f"served={served} {measured.stderr[-300:]!r}")

    with open(h.records / "sessions.jsonl", "a", encoding="utf-8") as sessions:   # the run's session made that provider's
        sessions.write(json.dumps({"at": A.now_iso(), "agent": "agents/ag1", "run": key, "provider": windowed_by,
                                   "session": "w-1"}) + "\n")
    windowed = objects(h.call("agent", "stats", "agents/ag1", key, "--json").stdout)
    seen = (windowed[0].get("context") or {}) if windowed else {}
    if window and seen.get("window") == window and seen.get("used") == round(total / window, 4):
        held("the window of the run's model", f"{model} under {windowed_by}: window {seen['window']}, used {seen['used']}")
    else:
        failures.append(f"  ✗ window                      {seen}")

    # --- status --json, and a run without a flow -----------------------------------------------------
    crashed = h.wake("no answer", "crash")
    dead = next((one for one in h.keys() if one not in (key, chat_key)), "")
    rows = {one["run"]: one for one in objects(h.call("agent", "status", "agents/ag1", "--json").stdout) if "run" in one}
    none = objects(h.call("agent", "stats", "agents/ag1", dead, "--json").stdout) if dead else []
    if (crashed.returncode != 0 and dead and rows.get(key, {}).get("context") == {
            "tokens": total, "used": round(total / 1_000_000, 4), "pp": round(pp / total, 4)}
            and isinstance((rows.get(chat_key, {}).get("context") or {}).get("tokens"), int)
            and (rows.get(chat_key, {}).get("context") or {}).get("used") is None
            and "context" in rows.get(dead, {}) and rows[dead]["context"] is None
            and none and "context" in none[0] and none[0]["context"] is None):
        held("status --json says each run's context; none without a flow", f"{key}: {rows[key]['context']}; "
             f"{chat_key}: {rows[chat_key]['context']}; {dead} (no response): null at status and stats")
    else:
        failures.append(f"  ✗ status context              {crashed.returncode} dead={dead!r} "
                        f"{ {k: v.get('context', 'ABSENT') for k, v in rows.items()} } {none}")
    return 0
