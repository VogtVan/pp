"""Scenario `agent-chat-voices` -- the voices of an exchange: what its flow says, keeps and counts:
- the calls of a launch: under the `stream` witness `agent chat <path> --json` says `tool` (the call of pp,
  `pp: true`, its `shell`), its `tool-result`, `thinking` {tokens}, a `Read` (`pp: false`) and its `tool-result`
  in error, `words` -- each with its `exchange` and `launch`, all before the `agent` of their launch and said
  before it ends (the witness's pause); `--harness … --provider <its grammar>` reads the `stream-codex` witness
  in the grammar its mode declares (`MODE_GRAMMARS`); a call the face refuses is a `step` `refusal`
  {events-malformed} and the exchange reaches its response; `run --json` says none of the four kinds and keeps
  the record's fields
- the flow kept: every exchange keeps, in the file of its run (`flows/<digest of the agent's path>/<key>.jsonl`),
  the very objects its flow says -- the conversation's own events left out, a bare exchange (`conduct off`)
  keeping `principal` and `agent` without `conduction`; a `run` keeps its voices, its stderr says none of them;
  `agent flow <path> <key>` reads them back (`--json`, `--exchange`, the text), a key nobody knows `run-unknown`
- the voices counted: `run` and `chat` write `flow` at their line of `responses.jsonl`, each voice in tokens as
  the engine estimates them (`principal` the head and the message, `conduction` pp's outputs, `pp_input`/
  `pp_result`, `tool_input`/`tool_result`, `words`, `thinking`), `calls` = launches + calls of tools, a bare
  exchange `conduction` 0; `stats --json` says `context` -- the voices summed, `pp` {tokens, share, served},
  `calls`, `reread`, `since` null, `window` and `used` null for a caller's command, the window of the run's
  model once its session's provider declares one (`CONTEXT_WINDOWS`); `status --json` says each run's
  `context` reduced; a run whose wake-up kept no response says `context: null` at both faces
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from conductor import metrics
from tests.harness import support

A = support(__file__, "agent")
CALLS = ("tool", "tool-result", "thinking", "words")
CONVERSATION = ("ready", "waiting", "conduct", "package", "policy", "refused", "closed")   # said, never kept
SPOKEN = ("conduction", "tool", "tool-result", "thinking", "words", "agent")               # the voices a run keeps
COUNTED = ("principal", "conduction", "pp_input", "pp_result", "tool_input", "tool_result", "words", "thinking")


def objects(text: str) -> list[dict]:
    found = []
    for line in text.splitlines():
        if line.strip():
            try:
                found.append(json.loads(line))
            except ValueError:
                found.append({"kind": "UNREADABLE", "line": line})
    return found


def steps_of(stderr: str) -> list[dict]:
    """-> the JSON steps a `run --json` says on stderr, its other lines left out."""
    found = []
    for line in stderr.splitlines():
        try:
            found.append(json.loads(line))
        except ValueError:
            pass
    return found


def command(kind: str, **fields) -> str:
    return json.dumps({"kind": kind, **fields}) + "\n"


def expected(h, where, session: str, launches: range, key: str, bare: bool = False) -> dict:
    """-> the flow the `stream` witness's launches carry, from the prompts it kept: the first prompt
    split at pp's output (the head and the message before it), the later ones pp's output alone."""
    tokens = metrics.tokens
    sums = {voice: 0 for voice in COUNTED}
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
        sums["words"] += tokens("witness words") + tokens("witness answer: stream")   # its two texts
        sums["thinking"] += 42
        sums["calls"] += 3
    return sums


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)
    h.lawful()          # every exchange owes a proof: two launches, the boot with the WORK then the AWAIT

    def fresh(known: set) -> str:
        return next((one for one in h.keys() if one not in known), "")

    def talk(mode: str, where: Path, *commands: str) -> tuple[subprocess.CompletedProcess, str]:
        """`agent chat agents/ag1 --json` under the witness in `mode`, fed `commands` -> (what it played, its run)."""
        known = set(h.keys())
        argv = [sys.executable, str(h.engine), "--instance", str(h.house), "agent", "chat", "agents/ag1",
                "--json", *h.harnessed_at(mode, where)]
        played = subprocess.run(argv, input="".join(commands), capture_output=True, text=True, cwd=h.ws,
                                env={**os.environ, **h.env}, timeout=120)
        return played, fresh(known)

    def kept(key: str) -> list[dict]:
        digest = hashlib.sha1("agents/ag1".encode("utf-8")).hexdigest()[:12]
        return A.lines(h.records / "flows" / digest / f"{key}.jsonl")

    # One conversation of two exchanges, the second bare, feeds the calls of a launch, the flow kept, its face
    # and the chat's count; one `run --json` on a windowed model feeds the run's silence, its kept voices, its
    # count and the context faces. The `stream-codex` and `stream-malformed` witnesses talk on their own.

    # --- the conversation: a conducted exchange, then a bare one --------------------------------------------
    where_c = bench.temp() / "conversation"
    chat, chat_key = talk("stream", where_c, command("message", text="one"), command("conduct", on=False),
                          command("message", text="two"), command("quit"))
    told = objects(chat.stdout)

    # --- the calls of a launch reach the flow while it plays -----------------------------------------------
    calls = [one for one in told if one.get("kind") in CALLS]
    opened_at, exchange_of = None, []          # each call beside the exchange its flow opened last
    for one in told:
        if one.get("kind") == "opened":
            opened_at = one.get("exchange")
        elif one.get("kind") in CALLS:
            exchange_of.append((one.get("exchange"), opened_at))
    first = [one for one in calls if one.get("exchange") == 1 and one.get("launch") == 1]
    agent_1 = next((at for at, one in enumerate(told) if one.get("kind") == "agent" and one.get("exchange") == 1
                    and one.get("launch") == 1), -1)
    tools = [one for one in calls if one.get("kind") == "tool"]
    results = {one.get("id"): one for one in calls if one.get("kind") == "tool-result"}
    piped = next((one for one in tools if one.get("pp") is True), {})
    read = next((one for one in tools if one.get("name") == "Read"), {})
    answered = [one for one in told if one.get("kind") == "response"]
    if (chat.returncode == 0 and chat.stderr == "" and chat_key and first and agent_1 > 0
            and all(told.index(one) < agent_1 for one in first)
            and max(str(one.get("at")) for one in first) < str(told[agent_1].get("at"))
            and {exchange for exchange, _ in exchange_of} == {1, 2}
            and all(exchange == opened for exchange, opened in exchange_of)
            and all(isinstance(one.get("launch"), int) for one in calls)
            and piped.get("shell") == f"./pp {chat_key} -" and piped.get("name") == "Bash"
            and results.get(piped.get("id"), {}).get("error") is False
            and read.get("pp") is False and results.get(read.get("id"), {}).get("error") is True
            and any(one.get("kind") == "thinking" and one.get("tokens") == 42 for one in calls)
            and any(one.get("kind") == "words" and one.get("text") == "witness words" for one in calls)
            and not any(one.get("kind") == "step" and one.get("event") == "refusal" for one in told)
            and [one.get("response") for one in answered] == [A.composed(one) for one in answered]
            and all("witness answer: stream" in str(one.get("response")) for one in answered)):
        held("the calls of a launch reach the flow while it plays", f"run {chat_key}: {len(calls)} calls over "
             f"{len({(one.get('exchange'), one.get('launch')) for one in calls})} launches of 2 exchanges; exchange 1 "
             f"launch 1's {len(first)} before its agent and said before it ended ({max(str(one.get('at')) for one in first)} "
             f"< {told[agent_1].get('at')}); `{piped.get('shell')}` pp: true and its result; Read pp: false, its result in "
             "error; thinking 42 tokens; words")
    else:
        failures.append(f"  ✗ tools                       rc={chat.returncode} err={chat.stderr[-300:]!r} key={chat_key} "
                        f"kinds={[(one.get('kind'), one.get('exchange'), one.get('launch')) for one in told]} "
                        f"piped={piped} read={read}")

    # --- another grammar, named beside the harness ---------------------------------------------------------
    codex, key_x = talk("stream-codex", bench.temp() / "codex", command("message", text="the other grammar"),
                        command("quit"))
    said_x = objects(codex.stdout)
    answered_x = [one for one in said_x if one.get("kind") == "response"]
    shells = [one.get("shell") for one in said_x if one.get("kind") == "tool"]
    if (codex.returncode == 0 and codex.stderr == "" and key_x
            and [one.get("response") for one in answered_x] == [A.composed(one) for one in answered_x]
            and len(answered_x) == 1 and "witness answer: stream-codex" in str(answered_x[0].get("response"))
            and [one.get("session") for one in answered_x] == ["w-1"]
            and shells and all(one == f"./pp {key_x} -" for one in shells)
            and all(one.get("pp") is True for one in said_x if one.get("kind") == "tool")
            and any(one.get("kind") == "thinking" and one.get("text") == "witness reasoning" for one in said_x)
            and any(one.get("kind") == "tool-result" and one.get("content") == "ok" for one in said_x)):
        held("--provider names the grammar of a --harness", f"run {key_x}: read in {A.MODE_GRAMMARS['stream-codex']}'s "
             f"grammar -- the words of its agent_message, the session of thread.started (w-1), {len(shells)} tool(s) "
             f"`./pp {key_x} -` pp: true, their output, the reasoning")
    else:
        failures.append(f"  ✗ the other grammar           rc={codex.returncode} err={codex.stderr[-300:]!r} key={key_x} "
                        f"answered={answered_x} shells={shells} kinds={[one.get('kind') for one in said_x]}")

    # --- gemini's pieces: one words at the flow, one line at the file, the response whole -------------------
    gem, key_g = talk("stream-gemini", bench.temp() / "gemini", command("message", text="in pieces"), command("quit"))
    said_g = objects(gem.stdout)
    answered_g = [one for one in said_g if one.get("kind") == "response"]
    words_g = [one for one in said_g if one.get("kind") == "words"]
    lines_g = [one for one in (kept(key_g) if key_g else []) if one.get("kind") == "words"]
    kept_g = [one for one in h.responses() if one.get("run") == key_g]
    launches_g = kept_g[-1].get("launches") if kept_g else 0
    if (gem.returncode == 0 and gem.stderr == "" and key_g and len(answered_g) == 1
            and answered_g[0].get("response") == A.composed(answered_g[0])
            and str(answered_g[0].get("response")).endswith("stream-gemini")
            and [one.get("session") for one in answered_g] == ["w-1"]
            and launches_g and len(words_g) == 2 * launches_g and len(lines_g) == 2 * launches_g
            and [one.get("text") for one in words_g[:2]] == ["witness answer: ", "stream-gemini"]
            and not any("delta" in one for one in words_g)
            and kept_g[-1].get("words") and all(one.get("text") for one in kept_g[-1]["words"])):
        held("gemini's pieces make one words", f"run {key_g}, {launches_g} launch(es): two pieces then a tool = one "
             f"words `witness answer: `, then `stream-gemini` -- {len(words_g)} words said, {len(lines_g)} lines kept, "
             "none carries delta; the response their composition")
    else:
        failures.append(f"  ✗ gemini pieces               rc={gem.returncode} err={gem.stderr[-300:]!r} key={key_g} "
                        f"launches={launches_g} words={[one.get('text') for one in words_g]} lines={len(lines_g)} "
                        f"delta={[one.get('delta') for one in words_g]} answered={answered_g[:1]}")

    # --- a call the face refuses ---------------------------------------------------------------------------
    malformed_chat, _ = talk("stream-malformed", bench.temp() / "malformed", command("message", text="malformed"),
                             command("quit"))
    said_m = objects(malformed_chat.stdout)
    answered_m = [one for one in said_m if one.get("kind") == "response"]
    malformed = [one for one in said_m if one.get("kind") == "step" and one.get("event") == "refusal"
                 and str(one.get("code", "")) == "events-malformed"]
    if (malformed_chat.returncode == 0 and malformed
            and [one.get("response") for one in answered_m] == [A.composed(one) for one in answered_m]
            and "witness answer: stream-malformed" in str([one.get("response") for one in answered_m])
            and [one.get("state") for one in said_m if one.get("kind") == "verdict"] == ["parked"]):
        held("a call the face refuses is a step, the exchange goes on", f"{len(malformed)} step refusal "
             "events-malformed; the response kept, the verdict parked")
    else:
        failures.append(f"  ✗ malformed                   rc={malformed_chat.returncode} "
                        f"err={malformed_chat.stderr[-300:]!r} "
                        f"steps={[one for one in said_m if one.get('kind') == 'step'][-4:]}")

    # --- the run: `run --json` on the `stream` witness, its model one whose window an adapter declares -----
    windowed_by = next((one for one in A.providers(h.house) if A.declared(h.house, one, "CONTEXT_WINDOWS")), "")
    model, window = next(iter((A.declared(h.house, windowed_by, "CONTEXT_WINDOWS") or {"m": None}).items()))
    where_r = bench.temp() / "run"
    known = set(h.keys())
    ran = h.call("agent", "run", "agents/ag1", "--message", "run me", "--json", "--model", model,
                 *h.harnessed_at("stream", where_r))
    key = fresh(known)
    steps = steps_of(ran.stderr)
    try:
        printed = json.loads(ran.stdout)
    except ValueError:
        printed = {}
    last = h.responses()[-1] if h.responses() else {}
    if (ran.returncode == 0 and steps and not any(one.get("event") in CALLS for one in steps)
            and not any(kind in ran.stderr for kind in ('"tool"', '"tool-result"', '"thinking"', '"words"'))
            and set(printed) - {"session", "state"} == A.RECORD_FIELDS
            and set(last) == A.RECORD_FIELDS
            and last.get("response") == A.composed(last)
            and "witness answer: stream" in str(last.get("response"))):
        held("run says none of the calls", f"run --json on the stream witness: {len(steps)} steps on stderr, none "
             "of the four kinds; the record's fields unchanged, the response composed of the words")
    else:
        failures.append(f"  ✗ run quiet                   rc={ran.returncode} stdout={ran.stdout[-200:]!r} "
                        f"stderr={ran.stderr[-300:]!r}")

    # --- the flow kept as said -----------------------------------------------------------------------------
    exchanged = [one for one in told if one.get("kind") not in CONVERSATION]
    lines = kept(chat_key) if chat_key else []
    second = [one for one in lines if one.get("exchange") == 2]
    if (chat.returncode == 0 and chat_key and lines and lines == exchanged
            and {one.get("kind") for one in lines} >= {"opened", "principal", "conduction", "tool", "agent",
                                                         "response", "verdict"}
            and [one.get("kind") for one in second if one.get("kind") in ("principal", "agent")] == ["principal", "agent"]
            and not any(one.get("kind") == "conduction" for one in second)):
        held("the flow kept as said", f"run {chat_key}: {len(lines)} lines, the very objects stdout said for its two "
             "exchanges; the bare one keeps principal and agent, no conduction")
    else:
        failures.append(f"  ✗ kept as said               rc={chat.returncode} key={chat_key!r} kept={len(lines)} "
                        f"said={len(exchanged)} first diff={next((i for i, (a, b) in enumerate(zip(lines, exchanged)) if a != b), None)} "
                        f"{chat.stderr[-300:]!r}")

    run_lines = kept(key) if key else []
    kinds = [one.get("kind") for one in run_lines]
    if (ran.returncode == 0 and key and set(SPOKEN) <= set(kinds) and kinds[-2:] == ["response", "verdict"]
            and steps and not any(one.get("event") in SPOKEN for one in steps)):
        held("a run keeps its voices", f"run {key}: {len(run_lines)} lines -- {', '.join(SPOKEN)}, then response and "
             f"verdict; stderr {len(steps)} steps, none of the voices")
    else:
        failures.append(f"  ✗ run voices                  rc={ran.returncode} key={key!r} kinds={kinds} "
                        f"{ran.stderr[-300:]!r}")

    as_json = h.call("agent", "flow", "agents/ag1", chat_key, "--json")
    read_all = objects(as_json.stdout)
    only_two = h.call("agent", "flow", "agents/ag1", chat_key, "--exchange", "2", "--json")
    read_two = objects(only_two.stdout)
    text = h.call("agent", "flow", "agents/ag1", chat_key)
    unknown = h.call("agent", "flow", "agents/ag1", "zzzzzz")
    if (as_json.returncode == 0 and read_all == lines and only_two.returncode == 0 and read_two
            and read_two[0].get("kind") == "opened" and read_two[0].get("exchange") == 2
            and all(one in lines for one in read_two) and len(read_two) < len(lines)
            and text.returncode == 0 and len(text.stdout.strip().splitlines()) == len(lines)
            and unknown.returncode == 2 and "run-unknown" in unknown.stderr):
        bench.refusals += 1
        held("agent flow reads it back", f"--json {len(read_all)} lines as kept; --exchange 2 {len(read_two)} lines "
             f"from its opened; the text {len(lines)} lines; run-unknown")
    else:
        failures.append(f"  ✗ face                        {as_json.returncode}/{only_two.returncode}/{text.returncode}/"
                        f"{unknown.returncode} json={len(read_all)} two={len(read_two)} {as_json.stderr[-200:]!r} "
                        f"{unknown.stderr[-200:]!r}")

    # --- the voices counted ---------------------------------------------------------------------------------
    launches = last.get("launches") or 0
    want = expected(h, where_r, "w-1", range(1, launches + 1), key) if key else {}
    if ran.returncode == 0 and key and last.get("run") == key and launches >= 1 and last.get("flow") == want:
        held("run writes the flow of its exchange", f"run {key}, {launches} launch(es): {want}")
    else:
        failures.append(f"  ✗ run flow                    rc={ran.returncode} key={key!r} got={last.get('flow')} "
                        f"want={want} {ran.stderr[-300:]!r}")

    talked = [one for one in h.responses() if one.get("run") == chat_key]
    if len(talked) == 2:
        conducted = talked[0].get("launches") or 0
        want_c = expected(h, where_c, "w-1", range(1, conducted + 1), chat_key)
        want_b = expected(h, where_c, "w-1", range(conducted + 1, conducted + 2), "", bare=True)
    else:
        want_c = want_b = {}
    if (chat.returncode == 0 and len(talked) == 2 and talked[0].get("flow") == want_c
            and talked[1].get("conducted") is False and talked[1].get("flow") == want_b
            and want_b.get("conduction") == 0 and want_b.get("calls") == 3):
        held("chat writes the flow of each exchange, bare included", f"run {chat_key}: conducted {want_c}; "
             f"bare {want_b}")
    else:
        failures.append(f"  ✗ chat flow                   rc={chat.returncode} {[one.get('flow') for one in talked]} "
                        f"want={want_c} / {want_b} {chat.stderr[-300:]!r}")

    measured = h.call("agent", "stats", "agents/ag1", key, "--json")
    face = objects(measured.stdout)[0] if measured.returncode == 0 and measured.stdout.strip() else {}
    context = face.get("context") or {}
    total = sum(want.get(voice, 0) for voice in COUNTED)
    pp = want.get("conduction", 0) + want.get("pp_input", 0) + want.get("pp_result", 0)
    served = (face.get("conduction") or {}).get("tokens")
    if (measured.returncode == 0 and context.get("flow") == {**{v: want.get(v) for v in COUNTED}, "total": total}
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

    known = set(h.keys())
    crashed = h.wake("no answer", "crash")
    dead = fresh(known)
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
