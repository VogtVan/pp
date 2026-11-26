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
- the context measured (batch le-contexte-mesure): each call the harness's adapter counts says `context` at the
  flow -- its tokens, its window and the part used, once per message -- and kept, never by `run`; the exchange's
  `flow` keeps the last as `context`; `stats` and `status --json` say the measure, `estimated` false; an exchange
  that measures nothing after it adds its flow, weighed by the adapter's constants, `estimated` true
- the voices counted: `run` and `chat` write `flow` at their line of `responses.jsonl`, each voice in tokens as
  the engine estimates them (`principal` the head and the message, `conduction` pp's outputs, `pp_input`/
  `pp_result`, `tool_input`/`tool_result`, `words`, `thinking`), `calls` = launches + calls of tools, a bare
  exchange `conduction` 0; `stats --json` says `context` -- the voices summed, `pp` {tokens, marble, share,
  served}, `calls`, `reread`, `since` null, `window` and `used` null for a caller's command, the window of the
  run's model once its session's provider declares one (`CONTEXT_WINDOWS`); `status --json` says each run's
  `context` reduced, `over` beside pp's share; a run whose wake-up kept no response says `context: null` at both faces
- pp's part OF THE CONTEXT (s.1208): its voices of the flow and the standing orders the launch carries (the
  marble, `.sys/system.md`, counted when the provider's adapter receipts it), weighed by the adapter's
  `FLOW_RATIO`, over the context's tokens -- never over the flow, whose thought the context may not keep: on a
  known flow (a heavy thought, a known marble) `context_of` says the part the context holds, `over` false; on a
  context measured smaller than that part, no share and `over` true -- never a share cut at the whole; at the
  face, the witness's measures covering pp, a share under one, the marble counted under a provider that carries
  it and none for a caller's command
- a run the engine cannot count (its slot stands, its trace is away): `stats --json` refuses `stats-unreadable`,
  nothing on stdout
- after a compaction (the slot's `boot` at an exchange) `stats --json` counts the flow of the responses that follow
  it, and says the first of them at `since`
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import conductor
from conductor import metrics, persistence
from tests.harness import support

A = support(__file__, "agent")
ASIDE = A.skill().ASIDE                               # the kind of a text the harness wrote that a call follows
CALLS = ("tool", "tool-result", "thinking", "words", ASIDE, "context")
CONVERSATION = ("ready", "waiting", "conduct", "package", "policy", "refused", "closed")   # said, never kept
SPOKEN = ("conduction", "tool", "tool-result", "thinking", "words", "context", "agent")               # the voices a run keeps
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
        sums["words"] += tokens("witness words")       # its aside; its last message is no voice
        sums["thinking"] += 42
        sums["calls"] += 3
    if not bare and launches[0] == 1:                  # the prints the conduction asked of the run's opening, which the
        sums["words"] += len(h.dues(key, 1)) * tokens(A.PRINTED)   # witness handed: counted among the words, the
                                                       # first out of the input of the console's
        sums["pp_input"] -= min(tokens(A.PRINTED), tokens(json.dumps({"command": f"./pp {key} -"})))   # call it came by
    sums["context"] = 100000 * launches[-1] + 302      # what the witness's last call of the exchange sent the model
    return sums


def sent(launch: int) -> list[int]:
    """-> the contexts the `stream` witness's calls of its launch of that rank say, once per message."""
    return [100000 * launch + 100 * k + 2 for k in (1, 2, 3)]


def weighed(flow: dict, ratio: float, kept: float) -> float:
    """-> what an exchange's flow adds to a context, weighed as an adapter's constants say."""
    thinking = flow.get("thinking", 0)
    return ratio * (sum(flow.get(voice, 0) for voice in COUNTED) - thinking) + kept * thinking


KNOWN = {"principal": 400, "conduction": 30000, "pp_input": 1000, "pp_result": 3000, "tool_input": 2000,
         "tool_result": 20000, "words": 4000, "thinking": 120000, "calls": 20}   # pp's voices 34000, the thought heavy
MODEL = {"window": 1_000_000, "base": 90000, "ratio": 1.5, "kept": 0.0, "marble": 8000}
# written by hand: 90000 + 1.5 x (180400 - 120000) = 180600 tokens of context; pp 1.5 x (34000 + 8000) = 63000 of them,
# the marble 1.5 x 8000 = 12000; 63000 / 180600 = 0.3488 -- of the flow it would be 34000 / 180400 = 0.1885
UNDER = {"tokens": 63000, "marble": 12000, "share": 0.3488, "over": False, "served": 33000}
# the same flow on a context MEASURED at 20000 tokens: pp's 63000 pass it -- no share, the overflow said
OVER = {"tokens": 63000, "marble": 12000, "share": None, "over": True, "served": 33000}


def known_flow(bench, h) -> None:
    """pp's part of a context on a KNOWN flow, read by `context_of` itself and compared with values written by hand:
    a thought heavier than the rest of the flow, which the adapter's context keeps none of, and a known marble -- the
    share is the part of the context, never the part of the flow; the same flow on a measured context smaller than
    pp's part says the overflow, never a share cut at the whole."""
    held, failures = bench.held, bench.failures
    agent = h.module()
    found = agent.context_of([agent.Response(index=1, flow=agent.Sums.of(KNOWN))], agent.Scale(**MODEL), 33000)
    found = found.json() if found is not None else None
    if found is not None and found.get("tokens") == 180600 and found.get("pp") == UNDER:
        held("pp's part is a part of the context", f"a thought of {KNOWN['thinking']} tokens kept none, a marble of "
             f"{MODEL['marble']}: pp {UNDER['tokens']} of 180600 tokens, {UNDER['share']:.2%} of the context (of the "
             "flow it would be 18.85%)")
    else:
        failures.append(f"  ✗ pp's part of the context    found={found and found.get('pp')} tokens="
                        f"{found and found.get('tokens')} owed={UNDER} at 180600")
    beyond = agent.context_of([agent.Response(index=1, flow=agent.Sums.of({**KNOWN, "context": 20000}))], agent.Scale(**MODEL),
                              33000)
    beyond = beyond.json() if beyond is not None else None
    if beyond is not None and beyond.get("tokens") == 20000 and beyond.get("pp") == OVER:
        held("pp's part beyond the context is said", f"a context measured at 20000 tokens under pp's "
             f"{OVER['tokens']}: share None, over true")
    else:
        failures.append(f"  ✗ pp's part beyond the context found={beyond and beyond.get('pp')} tokens="
                        f"{beyond and beyond.get('tokens')} owed={OVER} at 20000")


SHARE_STEP = 0.0001        # the last digit a face says of a share: one ten-thousandth


def under_one(pp: object, tokens: object, marbled: bool) -> bool:
    """Whether a face's `pp` says a part UNDER the whole of its context: `over` false, a share between 0 and 1 that
    is its `tokens` over the context's to a ten-thousandth, and a marble -- counted under a provider that carries
    one, none otherwise. The face rounds the part and the share each on its own: the share it says may stand one
    step of its last digit away from the share of the part it says."""
    if not isinstance(pp, dict) or not isinstance(tokens, int) or tokens <= 0:
        return False
    share, marble = pp.get("share"), pp.get("marble")
    return (pp.get("over") is False and isinstance(share, float) and 0 < share < 1
            and abs(share - pp.get("tokens", 0) / tokens) <= SHARE_STEP and isinstance(marble, int)
            and (marble > 0 if marbled else marble == 0))


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)
    known_flow(bench, h)
    h.lawful()          # every exchange owes a proof, fused under the WORK: one launch, the AWAIT held after it

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
    first = first[:max((at for at, one in enumerate(first) if one.get("kind") != "words"), default=-1) + 1]   # the last
    # message is said when the launch ends: what stands before it is said while the launch plays
    agent_1 = next((at for at, one in enumerate(told) if one.get("kind") == "agent" and one.get("exchange") == 1
                    and one.get("launch") == 1), -1)
    tools = [one for one in calls if one.get("kind") == "tool"]
    results = {one.get("id"): one for one in calls if one.get("kind") == "tool-result"}
    piped = next((one for one in tools if one.get("pp") is True), {})
    read = next((one for one in tools if one.get("name") == "Read"), {})
    answered = [one for one in told if one.get("kind") == "response"]
    launched = list(dict.fromkeys((one.get("exchange"), one.get("launch")) for one in calls))   # the session's launches
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
            and any(one.get("kind") == ASIDE and one.get("text") == "witness words" for one in calls)
            and any(one.get("kind") == "words" and one.get("text") == A.PRINTED for one in first)
            and [[one.get("tokens") for one in calls if one.get("kind") == "context"
                  and (one.get("exchange"), one.get("launch")) == launch] for launch in launched]
            == [sent(rank) for rank in range(1, len(launched) + 1)]
            and all(one.get("window") is None and one.get("used") is None
                    for one in calls if one.get("kind") == "context")
            and not any(one.get("kind") == "step" and one.get("event") == "refusal" for one in told)
            and [one.get("response") for one in answered] == [A.composed(one) for one in answered]
            and not any(A.answer_of("stream") in str(one.get("response")) for one in answered)):
        held("the calls of a launch reach the flow while it plays", f"run {chat_key}: {len(calls)} calls over "
             f"{len({(one.get('exchange'), one.get('launch')) for one in calls})} launches of 2 exchanges; exchange 1 "
             f"launch 1's {len(first)} before its agent and said before it ended ({max(str(one.get('at')) for one in first)} "
             f"< {told[agent_1].get('at')}); `{piped.get('shell')}` pp: true and its result; Read pp: false, its result in "
             "error; thinking 42 tokens; an aside, the words of the production handed; the context of each call once per message, no window for a caller's "
             "command")
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
            and len(answered_x) == 1 and A.answer_of("stream-codex") not in str(answered_x[0].get("response"))
            and [one.get("session") for one in answered_x] == ["w-1"]
            and shells and all(one == f"./pp {key_x} -" for one in shells)
            and all(one.get("pp") is True for one in said_x if one.get("kind") == "tool")
            and any(one.get("kind") == "thinking" and one.get("text") == "witness reasoning" for one in said_x)
            and any(one.get("kind") == "tool-result" and one.get("content") == "ok" for one in said_x)):
        held("--provider names the grammar of a --harness", f"run {key_x}: read in {A.MODE_GRAMMARS['stream-codex']}'s "
             f"grammar -- its agent_message the last message, no words; the session of thread.started (w-1), {len(shells)} tool(s) "
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
    dues_g = h.dues(key_g) if key_g else []          # the prints the conduction asked
    if (gem.returncode == 0 and gem.stderr == "" and key_g and len(answered_g) == 1
            and answered_g[0].get("response") == A.composed(answered_g[0])
            and "stream-gemini" not in str(answered_g[0].get("response"))
            and [one.get("session") for one in answered_g] == ["w-1"]
            and launches_g and dues_g and len(words_g) == len(dues_g) and len(lines_g) == len(dues_g)
            and [one.get("text") for one in words_g] == [A.PRINTED] * len(dues_g)
            and [one.get("chars") for one in kept_g[-1].get("finals") or []] == [len("stream-gemini")] * launches_g
            and [one.get("text") for one in said_g if one.get("kind") == ASIDE] == [A.ANSWER] * launches_g
            and not any("delta" in one for one in words_g)
            and kept_g[-1].get("words") and all(one.get("text") for one in kept_g[-1]["words"])):
        held("gemini's pieces make one text", f"run {key_g}, {launches_g} launch(es): two pieces then a tool = one "
             f"aside `witness answer: `, then the last message `stream-gemini`, its text and its length -- {len(words_g)} words, "
             f"the {len(dues_g)} productions due handed, {len(lines_g)} lines kept, none carries delta; the response their composition")
    else:
        failures.append(f"  ✗ gemini pieces               rc={gem.returncode} err={gem.stderr[-300:]!r} key={key_g} "
                        f"launches={launches_g} dues={dues_g} words={[one.get('text') for one in words_g]} lines={len(lines_g)} "
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
            and A.answer_of("stream-malformed") not in str([one.get("response") for one in answered_m])
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
            and not any(kind in ran.stderr for kind in ('"tool"', '"tool-result"', '"thinking"', '"words"', '"context"'))
            and set(printed) - {"session", "state"} == A.RECORD_FIELDS
            and set(last) == A.RECORD_FIELDS
            and last.get("response") == A.composed(last)
            and A.answer_of("stream") not in str(last.get("response"))):
        held("run says none of the calls", f"run --json on the stream witness: {len(steps)} steps on stderr, none "
             "of the five kinds; the record's fields unchanged, the response composed of the words")
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
            and under_one(context.get("pp"), context.get("tokens"), False)
            and (context.get("pp") or {}).get("tokens") == pp and (context.get("pp") or {}).get("served") == served
            and context.get("calls") == want.get("calls") and context.get("since") is None
            and context.get("reread") == want.get("calls", 0) * (total // 2) and isinstance(served, int)
            and context.get("tokens") == want.get("context") and context.get("estimated") is False
            and context.get("measured") == {"tokens": want.get("context"), "index": last.get("index")}):
        held("stats --json says the context and pp's part", f"total {total} tokens, pp {pp} ({context['pp']['share']:.0%} "
             "of the context, no marble for a caller's command), "
             f"served by the engine {served} (gap {pp - served:+d} = {(pp - served) / served:+.1%}), calls "
             f"{context['calls']}, reread {context['reread']}; no window for a caller's command; the context "
             f"measured at the last call, {context['tokens']} tokens")
    else:
        failures.append(f"  ✗ stats context               rc={measured.returncode} {context} total={total} pp={pp} "
                        f"served={served} {measured.stderr[-300:]!r}")

    with open(h.records / "sessions.jsonl", "a", encoding="utf-8") as sessions:   # the run's session made that provider's
        sessions.write(json.dumps({"at": A.now_iso(), "agent": "agents/ag1", "run": key, "provider": windowed_by,
                                   "session": "w-1"}) + "\n")
    windowed = objects(h.call("agent", "stats", "agents/ag1", key, "--json").stdout)
    seen = (windowed[0].get("context") or {}) if windowed else {}
    if window and seen.get("window") == window and seen.get("used") == round(want.get("context", 0) / window, 4):
        held("the window of the run's model", f"{model} under {windowed_by}: window {seen['window']}, used {seen['used']}")
    else:
        failures.append(f"  ✗ window                      {seen}")

    ratio = A.declared(h.house, windowed_by, "FLOW_RATIO", 1.0)
    known = set(h.keys())
    crashed = h.wake("no answer", "crash")
    dead = fresh(known)
    rows = {one["run"]: one for one in objects(h.call("agent", "status", "agents/ag1", "--json").stdout) if "run" in one}
    none = objects(h.call("agent", "stats", "agents/ag1", dead, "--json").stdout) if dead else []
    if (crashed.returncode != 0 and dead and rows.get(key, {}).get("context") == {
            "tokens": want.get("context"), "used": round(want.get("context", 0) / window, 4),
            "pp": rows.get(key, {}).get("context", {}).get("pp"), "over": False, "estimated": False}
            and 0 < (rows.get(key, {}).get("context", {}).get("pp") or 0) < 1
            and isinstance((rows.get(chat_key, {}).get("context") or {}).get("tokens"), int)
            and (rows.get(chat_key, {}).get("context") or {}).get("used") is None
            and "context" in rows.get(dead, {}) and rows[dead]["context"] is None
            and none and "context" in none[0] and none[0]["context"] is None):
        held("status --json says each run's context; none without a flow", f"{key}: {rows[key]['context']}; "
             f"{chat_key}: {rows[chat_key]['context']}; {dead} (no response): null at status and stats")
    else:
        failures.append(f"  ✗ status context              {crashed.returncode} dead={dead!r} "
                        f"{ {k: v.get('context', 'ABSENT') for k, v in rows.items()} } {none}")

    # --- after a measure, an exchange that measures nothing: the measure plus its flow, weighed -------------
    with open(h.records / "sessions.jsonl", "a", encoding="utf-8") as sessions:   # back to a caller's command
        sessions.write(json.dumps({"at": A.now_iso(), "agent": "agents/ag1", "run": key, "provider": None,
                                   "session": "w-1"}) + "\n")
    after = h.call("agent", "run", "agents/ag1", "--run", key, "--message", "unmeasured", "--json", "--model", model,
                   *h.harnessed_at("play", where_r))
    with open(h.records / "sessions.jsonl", "a", encoding="utf-8") as sessions:
        sessions.write(json.dumps({"at": A.now_iso(), "agent": "agents/ag1", "run": key, "provider": windowed_by,
                                   "session": "w-1"}) + "\n")
    later = [one for one in h.responses() if one.get("run") == key]
    keeps = A.declared(h.house, windowed_by, "THINKING_KEPT", 1.0)
    face_after = objects(h.call("agent", "stats", "agents/ag1", key, "--json").stdout)
    estimate = (face_after[0].get("context") or {}) if face_after else {}
    owed = round(want.get("context", 0) + weighed(later[-1].get("flow") or {}, ratio, keeps)) if len(later) == 2 else None
    skill = h.module()
    scale = skill.model_of(conductor, h.house, "agents/ag1", key)   # what the skill judges the run's context with
    declared = skill.Scale(window=window, base=A.declared(h.house, windowed_by, "CONTEXT_BASE", 0), ratio=ratio,
                           kept=keeps, marble=scale.marble)
    if (after.returncode == 0 and len(later) == 2 and "context" not in (later[-1].get("flow") or {"context": 0})
            and estimate.get("estimated") is True and estimate.get("tokens") == owed
            and estimate.get("measured") == {"tokens": want.get("context"), "index": later[0].get("index")}
            and estimate.get("used") == round(owed / window, 4)
            and under_one(estimate.get("pp"), estimate.get("tokens"), True)
            and scale == declared and scale != skill.Scale(window=window, marble=scale.marble)
            and (estimate.get("pp") or {}).get("marble") == round(ratio * scale.marble)):
        held("an exchange without a measure adds its flow to the last measure", f"{want.get('context')} measured, "
             f"then {owed} estimated under {windowed_by}'s constants (ratio {ratio}, thinking kept {keeps}); pp's "
             f"part of it, the marble its launch carries counted: {estimate['pp']}; the run's context is judged "
             f"with the window, the base, the ratio and the part kept its adapter declares, and its marble")
    else:
        failures.append(f"  ✗ estimate after a measure    rc={after.returncode} {estimate} owed={owed} scale={scale} "
                        f"{[one.get('flow') for one in later]} {after.stderr[-300:]!r}")

    # --- a run the engine cannot count: stats --json refuses, the records untouched ------------------------------
    slot = persistence.slot_of(h.agent_meta, key)
    trace = slot.parent / persistence.trace_of(slot)
    records_s = h.counted()
    trace.rename(trace.with_name(trace.name + ".away"))     # the slot stands, the engine finds no trace of the run
    untraced = h.call("agent", "stats", "agents/ag1", key, "--json")
    trace.with_name(trace.name + ".away").rename(trace)
    again = objects(h.call("agent", "stats", "agents/ag1", key, "--json").stdout)
    if (untraced.returncode == 2 and "stats-unreadable" in untraced.stderr and not untraced.stdout
            and h.counted() == records_s and again == face_after):
        held("stats --json refuses a run the engine cannot count", f"run {key}, its trace away: stats-unreadable, "
             "exit 2, nothing on stdout; the trace back, the same object as before")
    else:
        failures.append(f"  ✗ stats-unreadable            rc={untraced.returncode} {untraced.stdout[:120]!r} "
                        f"{untraced.stderr.strip()[-200:]!r} same={again == face_after}")

    # --- after a compaction the context counts from the response that follows it ----------------------------------
    whole = slot.read_bytes()
    slot.write_text(json.dumps({**json.loads(whole), "boot": 1}), encoding="utf-8")   # a compaction declared at exchange 1
    compacted = objects(h.call("agent", "stats", "agents/ag1", key, "--json").stdout)
    slot.write_bytes(whole)
    mine = [one for one in h.responses() if one.get("run") == key]
    counted_c = (compacted[0].get("context") or {}) if compacted else {}
    voices = A.skill().FLOW_VOICES
    after_c = sum(int((one.get("flow") or {}).get(voice) or 0) for one in mine[1:] for voice in voices)
    if (len(mine) >= 2 and counted_c.get("since") == int(mine[0].get("index") or 1) + 1
            and (counted_c.get("flow") or {}).get("total") == after_c
            and after_c < (face_after[0].get("context") or {}).get("flow", {}).get("total", 0)):
        held("after a compaction the context counts what follows", f"run {key}, its slot's boot at exchange 1: "
             f"stats --json counts the flow since response {counted_c.get('since')} ({after_c} tokens), no more "
             "the whole run's")
    else:
        failures.append(f"  ✗ context after a compaction  {counted_c.get('since')!r} {(counted_c.get('flow') or {}).get('total')!r} "
                        f"owed={after_c} indexes={[one.get('index') for one in mine]} "
                        f"whole={(face_after[0].get('context') or {}).get('flow') if face_after else None}")
    return 0
