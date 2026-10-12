"""Scenario `agent-run` -- 12 case(s) (batches le-package-agent, 2026-09-27, its rework, 2026-10-03,
and its rework B, 2026-10-07: the wake-up its principal conducts; la-reprise-dans-la-session,
2026-09-27; le-result-a-la-sortie, 2026-09-27; split out of `agent-home` by
les-scenarios-par-maison, 2026-10-07): a house wakes its agent and conducts its run.
- a house wakes its agent, and CONDUCTS its run: `agent run agents/ag1 --message … --harness <witness>`
  answers 0; the house plays `-new "<message>"` itself under the principal's mark -- the trace opens on
  `new` with `conducted_by: principal`, then `prompt` --, the first prompt of the harness is the message
  under `[message from your principal]` then pp's whole output, the later prompts pp's outputs alone,
  and the house makes the run advance by its own marked calls (`advance` in the trace); the witness
  calls pp NEVER (its calls file is empty) -- `-stats <key>` counts its advances and no value; the
  response, the message and the session stand at the house's records with their fields, `launches`
  the launches of the wake-up (2 at any cap: the boot whole -- the floor of a principal's cap --, then the FINAL),
  `cost_usd` the sum of the launches, `session_cost_usd` the provider's cumul; stdout carries the
  response alone, the verdict line goes to stderr
- the agent's first prompt is the boot of the principal's mode: what the witness received after the
  head of the message equals a marked `-new` on an interactive twin of the same composition, the key
  and the clock masked
- `--run <key> --message-file <path>` reopens the run's session (`PP_AGENT_SESSION`): the house plays
  the marked `<key> "<message>"` itself (traced `prompt`), exchange 2, the same session; the cost of
  the resume is the difference of the cumuls (0.16 before, 0.22 after two launches: 0.06)
- n runs: a second `run` without `--run` opens a second run in a second session, `status`
  says both sessions, `--run <key>` resumes the one named (its exchange count alone moves)
- a standing run resumes where it stands: a witness that answers then crashes at its first launch leaves the run
  standing, its response kept with the error (`stopped`, exit 2); a message is owed to resume it
  (`message-missing` without one), then the house serves the standing block and takes the run to its
  frontier in the same exchange -- `standing resumed`, exchange 1, parked
- no identity, nothing kept: a harness that answers no session identity refuses
  `session-missing` and leaves the three records as they were; `--run` on its run refuses
  `session-missing` before any launch, its trace untouched
- the provider holds: `--run` on a run opened under `--harness` with `--provider <an adapter of the product>`
  refuses `provider-mismatch`; the run stays as it was -- its wake mark the same to the byte,
  `status` parked, `result` rc 0 (the corrective rework, 2026-10-04)
- mute and crash: a harness that answers nothing, or fails without a word at its first launch,
  records no response
- `responses` and `messages` read newest first, `--last n`, filtered by agent; `list`; no record
  ever says `handed`
- `--json` renders the response's record line, plus `session` and `state`, as one object
- a failure renders what it kept: a run left standing by a crash prints the response it kept on
  stdout before the refusal; a harness without identity prints nothing
"""
from __future__ import annotations

import json

from conductor import persistence
from tests.harness import cli, support

A = support(__file__, "agent")
HEAD, RECORD_FIELDS = A.HEAD, A.RECORD_FIELDS


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)
    twin_ws, twin = h.twin()
    read, keys, trace, calls, counted = h.read, h.keys, h.trace, h.calls, h.counted
    responses, messages, sessions = h.responses, h.messages, h.sessions

    # --- a house wakes its agent and conducts its run (a) -----------------------------------------
    woken = h.wake("first ask")
    key = keys()[0] if keys() else ""
    first, sent, opened = responses(), messages(), sessions()
    events = trace(key) if key else []
    kinds = [one["kind"] for one in events]
    advances = [one for one in events if one.get("kind") == "advance"]
    first_prompt = read(".prompt.w-1.1")
    counted_stats = h.stats(key) if key else {}
    if (woken.returncode == 0 and len(keys()) == 1
            and kinds[:2] == ["new", "prompt"] and events[0].get("conducted_by") == "principal"
            and events[1].get("text") == "first ask" and len(advances) >= 1
            and all(one.get("held") is False for one in advances)
            and f"pp-agent: agents/ag1 · run {key} · exchange 1 · parked · harness rc 0 · 0.16 USD · 2 launch(es)" in woken.stderr
            and woken.stdout == "witness answer: play\n"
            and first_prompt.startswith(f"{HEAD}\nfirst ask\n\n▌ pp · run {key}")
            and read(".prompt.w-1.2").startswith("▌ pp · run ")
            and "▶ FINAL" in read(".prompt.w-1.2") and not read(".prompt.w-1.3")
            and calls() == []
            and h.read(".cwd") and (bench.temp() / "x").parent and __import__("pathlib").Path(read(".cwd")).resolve() == h.agent_ws.resolve()
            and len(first) == 1 and first[0]["agent"] == "agents/ag1" and first[0]["run"] == key
            and first[0]["index"] == 1 and first[0]["response"] == "witness answer: play"
            and first[0]["cost_usd"] == 0.16 and first[0]["session_cost_usd"] == 0.16 and first[0]["launches"] == 2
            and first[0]["denials"] == [] and first[0]["harness_rc"] == 0 and first[0]["error"] is None
            and set(first[0]) == RECORD_FIELDS
            and len(sent) == 1 and sent[0]["from"] == "house" and sent[0]["to"] == "agents/ag1"
            and sent[0]["run"] == key and sent[0]["message"] == "first ask" and sent[0]["policy"] == {}
            and set(sent[0]) == {"at", "from", "to", "run", "message", "policy"}
            and len(opened) == 1 and set(opened[0]) == {"at", "agent", "run", "provider", "session"}
            and opened[0]["agent"] == "agents/ag1" and opened[0]["run"] == key
            and opened[0]["provider"] is None and opened[0]["session"] == "w-1"
            and counted_stats.get("advances") == len(advances) and counted_stats.get("values") == {}
            and counted_stats.get("held") == 0):
        held("a house wakes its agent and conducts its run", f"the house played -new under the mark (new: "
             f"conducted_by principal, prompt 'first ask'), {len(advances)} marked advance(s); the witness called pp "
             "0 times; 2 launches (the boot whole at the floor of a principal's cap, then the FINAL), cost 0.10/0.16 "
             f"-> 0.16; rc 0, parked; -stats: {counted_stats.get('advances')} advance(s), no value, 0 held")
    else:
        failures.append(f"  ✗ agent run                   rc={woken.returncode} {woken.stdout[-200:]!r} "
                        f"{woken.stderr[-400:]!r} kinds={kinds[:4]} advances={len(advances)} "
                        f"first_prompt={first_prompt[:80]!r} calls={calls()} "
                        f"responses={first} messages={sent} sessions={opened} stats={ {k: counted_stats.get(k) for k in ('advances', 'values', 'held')} }")

    # --- the agent's first prompt is the boot of the principal's mode (b) --------------------------
    twin_boot = cli(h.engine, "--instance", str(twin), "-new", "first ask", cwd=twin_ws,
                    env={"PP_CONDUCTED_BY_PRINCIPAL": "true"}).stdout
    twin_key = persistence.run_id_of(persistence.slots(twin)[0]) if persistence.slots(twin) else ""
    agent_lines = A.after_head(first_prompt).replace(key, "KEY").splitlines()[1:]
    twin_lines = twin_boot.replace(twin_key, "KEY").splitlines()[1:]
    if agent_lines and agent_lines == twin_lines:
        held("the agent's first prompt is the boot of the principal's mode", f"{len(agent_lines)} lines identical to "
             "a marked -new on an interactive twin, after the head of the message; the key and the clock masked")
    else:
        drift = next((i for i, (a, b) in enumerate(zip(agent_lines, twin_lines)) if a != b), None)
        failures.append(f"  ✗ first prompt                lines={len(agent_lines)}/{len(twin_lines)} drift={drift} "
                        f"{agent_lines[drift] if drift is not None and drift < len(agent_lines) else ''!r}")

    # --- --run <key> --message-file reopens the session, the house plays the marked call (c) -------
    letter = bench.temp() / "letter.txt"
    letter.write_text("from a file\nsecond line\n", encoding="utf-8")
    resumed = h.call("agent", "run", "agents/ag1", "--run", key, "--message-file", str(letter),
                     *h.harnessed("play"))
    prompts = [one for one in trace(key) if one.get("kind") == "prompt"]
    second = responses()[1] if len(responses()) > 1 else {}
    if (resumed.returncode == 0 and f"run {key} · exchange 2 · parked" in resumed.stderr
            and read(".session") == "w-1" and read(".prompt.w-1.3").startswith(f"{HEAD}\nfrom a file\nsecond line\n\n▌ pp · run {key}")
            and len(prompts) == 2 and prompts[1].get("text") == "from a file\nsecond line"
            and len(responses()) == 2 and second.get("index") == 2
            and second.get("launches") == 2 and second.get("session_cost_usd") == 0.22 and second.get("cost_usd") == 0.06
            and messages()[1]["message"] == "from a file\nsecond line" and messages()[1]["run"] == key
            and len(sessions()) == 1 and calls() == []):
        held("the resume reopens the recorded session", "PP_AGENT_SESSION=w-1, the house played the marked "
             "`<key> <message>` (traced prompt), the file's content under the head: exchange 2, no second session "
             "line; 2 launches at 0.19 and 0.22: the resume cost 0.06, the session's cumul 0.22")
    else:
        failures.append(f"  ✗ resume in session           rc={resumed.returncode} {resumed.stdout[-160:]!r} "
                        f"{resumed.stderr[-300:]!r} session={read('.session')!r} prompts={len(prompts)} "
                        f"second={second} prompt3={read('.prompt.w-1.3')[:60]!r} calls={calls()}")

    # --- n runs -------------------------------------------------------------------------------
    second_run = h.wake("second run")
    key2 = next((one for one in keys() if one != key), "")
    status = h.call("agent", "status", "agents/ag1")
    named = h.call("agent", "run", "agents/ag1", "--run", key2, "--message", "again", *h.harnessed("play"))
    turns = {one: persistence.turns_of(persistence.slot_of(h.agent_meta, one)) for one in keys()}
    if (second_run.returncode == 0 and len(keys()) == 2 and f"run {key2} · exchange 1 · parked" in second_run.stderr
            and status.returncode == 0
            and f"run {key} · 2 exchange(s) · parked at FINAL · session w-1 (harness)" in status.stdout
            and f"run {key2} · 1 exchange(s) · parked at FINAL · session w-2 (harness)" in status.stdout
            and named.returncode == 0 and read(".session") == "w-2" and turns == {key: 2, key2: 2}):
        held("n runs of one agent", "a second run opens in a second session, status says both sessions, "
             "--run <key> resumes the one named -- the other's count stays")
    else:
        failures.append(f"  ✗ n runs                      {second_run.returncode}/{status.returncode}/{named.returncode} "
                        f"keys={keys()} turns={turns} {status.stdout[-240:]!r} {named.stderr[-160:]!r}")

    # --- a standing run resumes where it stands (d) -------------------------------------------------
    known = set(keys())
    cut = h.wake("stop here", "crash1")
    key3 = next((one for one in keys() if one not in known), "")
    kept3 = [one for one in responses() if one.get("run") == key3]
    bare = h.call("agent", "run", "agents/ag1", "--run", key3, *h.harnessed("play"))
    going = h.call("agent", "run", "agents/ag1", "--run", key3, "--message", "go on", *h.harnessed("play"))
    kinds3 = [one["kind"] for one in trace(key3)] if key3 else []
    gone_on = [one for one in responses() if one.get("run") == key3]
    if (cut.returncode == 2 and "harness rc 1" in cut.stderr and "stopped" in cut.stderr and cut.stdout == "witness answer: crash1\n"
            and len(kept3) == 1 and kept3[0].get("harness_rc") == 1 and kept3[0].get("launches") == 1
            and str(kept3[0].get("error", "")).startswith("harness rc 1")
            and bare.returncode == 2 and "message-missing" in bare.stderr
            and going.returncode == 0 and f"run {key3} · exchange 1 · parked" in going.stderr
            and "standing resumed" in going.stderr
            and read(".session") == "w-3" and read().startswith("▌ pp · run ") and "▶ FINAL" in read()
            and "compacted" not in kinds3 and len(gone_on) == 2 and gone_on[1].get("index") == 2):
        held("a standing run resumes where it stands", "a crash after the first answer leaves the run standing, its "
             "response kept with the error (stopped, exit 2); a message is owed (message-missing without); the "
             "house served the standing block and took the run to its frontier: standing resumed, exchange 1")
    else:
        failures.append(f"  ✗ standing run                {cut.returncode}/{bare.returncode}/{going.returncode} "
                        f"kinds={kinds3[-4:]} kept={kept3} {cut.stderr[-200:]!r} {bare.stderr[-120:]!r} "
                        f"{going.stderr[-300:]!r} last={read()[:60]!r}")

    # --- no identity, nothing kept ---------------------------------------------------------------
    counts = counted()
    known = set(keys())
    anon = h.wake("who am I", "anon")
    key4 = next((one for one in keys() if one not in known), "")
    kept = counted()
    before = len(trace(key4)) if key4 else -1
    again4 = h.call("agent", "run", "agents/ag1", "--run", key4, "--message", "x", *h.harnessed("play"))
    if (anon.returncode == 2 and "session-missing" in anon.stderr and kept == (counts[0], counts[1] + 1, counts[2])
            and key4 and again4.returncode == 2 and "session-missing" in again4.stderr
            and len(trace(key4)) == before and counted() == kept):
        held("no identity, nothing kept but the message", "session-missing: the message sent stands, no "
             "response, no session; --run on that run refuses before any launch, its trace and the records untouched")
    else:
        failures.append(f"  ✗ no identity                 {anon.returncode}/{again4.returncode} counts={counts} "
                        f"kept={kept} key4={key4!r} {anon.stderr[-160:]!r} {again4.stderr[-160:]!r}")
    counts = counted()

    # --- the provider holds ------------------------------------------------------------------------
    mark_before = A.launcher(h.agent_meta, key).read_bytes() if A.launcher(h.agent_meta, key).is_file() else b""
    named = A.providers(h.house)[0]
    other = h.call("agent", "run", "agents/ag1", "--run", key, "--message", "x", "--provider", named)
    mark_after = A.launcher(h.agent_meta, key).read_bytes() if A.launcher(h.agent_meta, key).is_file() else b""
    still_line = h.status_line(key)
    last_said = h.call("agent", "result", "agents/ag1", key)
    if other.returncode == 2 and "provider-mismatch" in other.stderr and counted() == counts:
        held("the provider holds", f"a run opened under --harness refuses --provider {named}: provider-mismatch")
    else:
        failures.append(f"  ✗ provider mismatch           rc={other.returncode} {other.stderr[-200:]!r}")
    if (mark_before and mark_after == mark_before and "dead" not in still_line and "parked at FINAL" in still_line
            and last_said.returncode == 0):
        held("a refused resume leaves the run as it was", f"the wake mark of {key} the same to the byte after "
             f"provider-mismatch; status {still_line!r}; result rc 0")
    else:
        failures.append(f"  ✗ refused resume, mark        same={mark_after == mark_before} status={still_line!r} "
                        f"result={last_said.returncode} {last_said.stderr[-160:]!r}")

    # --- mute and crash: nothing kept -------------------------------------------------------------
    mute = h.wake("mute", "mute")
    crash = h.wake("crash", "crash")
    if (mute.returncode == 2 and "session-missing" in mute.stderr
            and crash.returncode == 2 and "harness rc 1" in crash.stderr and "boom" in crash.stderr
            and counted() == (counts[0], counts[1] + 2, counts[2])
            and [one["message"] for one in messages()[-2:]] == ["mute", "crash"]):
        held("mute and crash keep the message alone", "a harness that answers nothing: session-missing; one that "
             "fails without a word at its first launch: harness rc 1 -- the message sent stands, no response, no session")
    else:
        failures.append(f"  ✗ mute/crash                  {mute.returncode}/{crash.returncode} "
                        f"{mute.stderr[-120:]!r} {crash.stderr[-120:]!r}")

    # --- responses, messages, list ---------------------------------------------------------------
    answered = h.call("agent", "responses", "agents/ag1", "--last", "2")
    letters = h.call("agent", "messages", "--last", "1")
    listed = h.call("agent", "list")
    newest = responses()[-1]["at"] if responses() else "?"
    mine = len([one for one in responses() if one.get("agent") == "agents/ag1"])
    if (answered.returncode == 0 and answered.stdout.count("agents/ag1 · run") == 2
            and newest in answered.stdout.splitlines()[0]
            and letters.returncode == 0 and "house -> agents/ag1" in letters.stdout and "crash" in letters.stdout
            and letters.stdout.count("house -> agents/ag1") == 1
            and listed.returncode == 0 and f"agents/ag1 · {len(keys())} run(s) · 0 running · {mine} response(s)" in listed.stdout
            and not any("handed" in one for one in responses())):
        held("responses, messages, list", f"newest first, --last n, the agent named; list counts {len(keys())} runs "
             f"and {mine} responses; no record says handed")
    else:
        failures.append(f"  ✗ readings                    {answered.returncode}/{letters.returncode}/{listed.returncode} "
                        f"{answered.stdout[:160]!r} {letters.stdout[:120]!r} {listed.stdout[:120]!r}")

    # --- --json renders the record line --------------------------------------------------------------
    rendered = h.wake("as json", "play", "--json")
    try:
        obj = json.loads(rendered.stdout) if rendered.stdout.count("\n") == 1 else None
    except ValueError:
        obj = None
    line = responses()[-1] if responses() else {}
    if (rendered.returncode == 0 and isinstance(obj, dict)
            and {k: v for k, v in obj.items() if k not in ("session", "state")} == line
            and obj.get("state") == "parked" and obj.get("session") == sessions()[-1]["session"]
            and "pp-agent: agents/ag1 · run" in rendered.stderr):
        held("--json renders the record line", "one object on stdout: the responses.jsonl line plus "
             "session and state parked; the verdict on stderr")
    else:
        failures.append(f"  ✗ json                        rc={rendered.returncode} {rendered.stdout[-240:]!r} "
                        f"{rendered.stderr[-160:]!r}")

    # --- a failure renders what it kept ----------------------------------------------------------------
    cut2 = h.wake("stop again", "crash2")
    anon2 = h.wake("who", "anon")
    if (cut2.returncode == 2 and "harness rc 1" in cut2.stderr and cut2.stdout == "witness answer: crash2\n"
            and anon2.returncode == 2 and "session-missing" in anon2.stderr and anon2.stdout == ""):
        held("a failure renders what it kept", "a run left standing by a crash prints the response it kept, "
             "then refuses on stderr, exit 2; no identity: nothing kept, nothing printed")
    else:
        failures.append(f"  ✗ failure renders             {cut2.returncode}/{anon2.returncode} "
                        f"{cut2.stdout!r} {anon2.stdout!r} {cut2.stderr[-200:]!r}")
    return 0
