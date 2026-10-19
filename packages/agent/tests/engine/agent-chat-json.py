"""Scenario `agent-chat-json` -- the flow of a conversation: `agent chat <path> --json` reads commands on stdin
and says events on stdout, one JSON object per line, each event naming its VOICE by its `kind`:
- the flow: `message`, `message`, `quit` on stdin -> every line of stdout is a JSON object with `kind`, `at` and
  `run`; `ready`, `waiting` then `opened` first -- `opened.cap` says the agent's `max_harness_tool_output` (`set`)
  and the cap its outputs are cut under (`applied`, raised to the floor of a principal's cap); each exchange says
  `principal`, then `conduction` and `agent` per launch, `response`, `verdict`, `waiting`; `closed` ends it,
  exit 0, stderr empty
- the three voices never mix: `principal.text` is the message as sent, every `conduction.text` opens on pp's
  heading and carries neither the head nor the message, every `agent` its cost and no text; `response` is the
  record's line plus `session` and `state`
- `quit` closes: `closed`, exit 0, the lock free, `run --run <key>` plays after
- a command that does not read, or a `kind` nobody knows: `refused` (`command-unreadable`, `command-unknown`), the
  conversation goes on
- `--quiet`: no `step` event, the voices and the house's events still said; the agent at the cap `add` writes
  (200000), `opened.cap` says it unraised
- `set`: `opened` says the provider and the policy of the opening; a `set` of the model, then of the permission
  regime, is said by `policy` and the next message's line at `messages.jsonl` carries both; `provider`, an empty
  model and a key nobody knows are `refused` (`provider-fixed`, `policy-invalid`, `policy-unknown`) and the policy
  holds; on a run of a provider whose adapter does not spell `permissions` (the first adapter whose `SPELLS` lacks
  it), its `set` refuses `policy-unsupported` before any launch
- `conduct`: before the run, `run-missing`; `conduct off` makes the next exchange BARE -- one launch, the message
  under its head and nothing of pp, no call of pp meanwhile, `verdict unconducted`, both record lines
  `conducted: false`, the run still parked; `conduct on` brings the conduction back
- `package`: `opened` says the packages the run plays; on a run no turn holds, `package` plays the engine's switch
  under the mark at once (the trace says `switch`), answers with the packages and `pending: false`, and the next
  conducted prompt carries `<name> off`; a name the engine refuses for another cause than a flight comes back
  `refused` with its code and detail (the waits of a switch are `agent-packages-chat`')
- conduction's blocks: every `conduction` says `chars` (the length of its text) and `blocks` -- `{stack, command,
  wait}` of each block the trace wrote since the conduction before: the first one the boot's (a stack opening on
  `BOOT`), the first of a resumed exchange its own block (in the conversation, and under `chat --run <key>`); under
  `--quiet` `chars` alone
- `ready`: before any message, the flow says the run -- at an opening `run` null, the provider, the policy of the
  flags, the packages, the cap, `conducted`, and no run opened; under `chat --run <key>` the run, `resumed`, its
  last policy and the packages its `opened` said
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from conductor.state import lock
from tests.harness import support

A = support(__file__, "agent")
HEAD = A.HEAD
VOICES = ("principal", "conduction", "agent")
HOUSE = ("opened", "response", "verdict", "waiting", "refused", "closed")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)
    h.lawful()          # the exchanges owe a proof: two launches, the boot with the WORK then the frontier
    keys, responses = h.keys, h.responses

    def talk(mode: str, where, *flags: str) -> subprocess.Popen:
        argv = [sys.executable, str(h.engine), "--instance", str(h.house), "agent", "chat", "agents/ag1",
                "--json", *flags, *h.harnessed_at(mode, where)]
        return subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, cwd=h.ws, env={**os.environ, **h.env})

    def events_of(out: str) -> list[dict]:
        found = []
        for line in out.splitlines():
            try:
                found.append(json.loads(line))
            except ValueError:
                found.append({"kind": "UNREADABLE", "line": line})
        return found

    def fresh(known: set) -> str:
        return next((one for one in keys() if one not in known), "")

    def command(kind: str, **fields) -> str:
        return json.dumps({"kind": kind, **fields}) + "\n"

    # --- the flow: two messages and a quit, every line an event with its voice ----------------------
    out_a = bench.temp() / "ja"
    live = talk("play", out_a)
    out, err = live.communicate(command("message", text="bonjour-principal") + command("message", text="suite")
                                + command("quit"), timeout=120)
    key = keys()[0] if keys() else ""
    events = events_of(out)
    found_cap = A.CAP_LINE.search((h.agent_meta / "SETTINGS.md").read_text(encoding="utf-8"))
    agent_cap = int(found_cap.group(0).split(":")[1]) if found_cap else -1
    opened_cap = next((one.get("cap") for one in events if one.get("kind") == "opened"), None)
    kinds = [one.get("kind") for one in events]
    well_formed = all(one.get("kind") != "UNREADABLE" and "at" in one and "run" in one for one in events)
    first_exchange = kinds[:kinds.index("response")] if "response" in kinds else []
    if (live.returncode == 0 and err == "" and well_formed and kinds[:3] == ["ready", "waiting", "opened"] and kinds[-1] == "closed"
            and kinds.count("principal") == 2 and kinds.count("conduction") == 3 and kinds.count("agent") == 3
            and kinds.count("response") == 2 and kinds.count("verdict") == 2 and kinds.count("waiting") >= 2
            and first_exchange.count("conduction") == 2 and first_exchange.count("agent") == 2
            and opened_cap == {"set": agent_cap, "applied": max(agent_cap, 200000)}
            and first_exchange.index("principal") < first_exchange.index("conduction") < first_exchange.index("agent")
            and all(one.get("run") == key for one in events if one.get("kind") not in ("waiting", "ready") or one.get("run"))
            and all(one.get("state") == "parked" for one in events if one.get("kind") == "verdict")):
        held("the flow says every event with its voice", f"run {key}: {len(events)} events, all JSON with kind/at/run; "
             f"ready, waiting then opened first (cap {opened_cap}), 2 principal, 3 conduction and 3 agent (2 + 1 launches: the boot "
             "with the WORK then the checkpoint; then the WORK with its checkpoint fused -- the bare FINAL launches nothing), 2 response, 2 verdict parked, "
             "closed last; stderr empty, exit 0")
    else:
        failures.append(f"  ✗ the flow                    rc={live.returncode} err={err[-300:]!r} well_formed={well_formed} "
                        f"kinds={kinds} first={first_exchange} cap={opened_cap} set={agent_cap}")

    # --- the three voices never mix -------------------------------------------------------------------
    principals = [one for one in events if one.get("kind") == "principal"]
    conductions = [one for one in events if one.get("kind") == "conduction"]
    agents = [one for one in events if one.get("kind") == "agent"]
    answers = [one for one in events if one.get("kind") == "response"]
    kept = responses()
    stripped = [{k: v for k, v in one.items() if k not in ("kind", "session", "state")} for one in answers]
    if (principals and principals[0].get("text") == "bonjour-principal" and principals[0].get("exchange") == 1
            and conductions and all(str(one.get("text", "")).startswith(f"▌ pp · run {key}") for one in conductions)
            and all(HEAD not in one["text"] and "bonjour-principal" not in one["text"] for one in conductions)
            and [one.get("launch") for one in conductions[:2]] == [1, 2]
            and agents and not any("text" in one for one in agents)
            and all(isinstance(one.get("cost_usd"), (int, float)) for one in agents)
            and len(kept) == 2 and stripped == kept and all(one.get("state") == "parked" for one in answers)):
        held("the three voices never mix", "principal = the message as sent (exchange 1); every conduction opens on "
             "pp's heading, no head, no message, launches 1-2; every agent event its cost, no text (the text "
             "is the words); response = the record's line plus session and state")
    else:
        failures.append(f"  ✗ voices                      principals={[o.get('text') for o in principals]} "
                        f"conductions={[str(o.get('text', ''))[:40] for o in conductions]} "
                        f"agents={[o.get('text') for o in agents]} stripped==kept={stripped == kept}")

    # --- quit closes: the lock free, a resume plays after ---------------------------------------------
    known = set(keys())
    out_d = bench.temp() / "jd"
    live = talk("play", out_d)
    out, err = live.communicate(command("message", text="one") + command("quit"), timeout=120)
    key_d = fresh(known)
    launcher = A.launcher(h.agent_meta, key_d) if key_d else None
    free = bool(launcher) and launcher.exists() and not lock.held(launcher)
    again = h.call("agent", "run", "agents/ag1", "--run", key_d, "--message", "again", *h.harnessed("play"))
    if (live.returncode == 0 and events_of(out)[-1].get("kind") == "closed" and free
            and again.returncode == 0 and f"run {key_d} · exchange 2 · parked" in again.stderr):
        held("quit closes, the lock is free", f"run {key_d}: closed, exit 0, the lock present and free, "
             "run --run plays exchange 2")
    else:
        failures.append(f"  ✗ quit                        rc={live.returncode} last={events_of(out)[-1:]} free={free} "
                        f"again={again.returncode} {again.stderr[-160:]!r}")

    # --- a command that does not read, a kind nobody knows: refused, the conversation goes on ---------
    known = set(keys())
    out_e = bench.temp() / "je"
    live = talk("play", out_e)
    out, err = live.communicate("not json\n" + command("dance") + command("message", text="still here") + command("quit"),
                                timeout=120)
    refused = [one for one in events_of(out) if one.get("kind") == "refused"]
    kinds = [one.get("kind") for one in events_of(out)]
    if (live.returncode == 0 and [one.get("code") for one in refused] == ["command-unreadable", "command-unknown"]
            and refused[0].get("line") == "not json" and kinds.count("principal") == 1 and kinds[-1] == "closed"
            and fresh(known)):
        held("a bad command is refused, the conversation goes on", "command-unreadable then command-unknown, "
             "the message after them played, closed")
    else:
        failures.append(f"  ✗ refused                     rc={live.returncode} refused={refused} kinds={kinds}")

    # --- --quiet: no step, the voices and the house's events still said ---------------------------------
    out_f = bench.temp() / "jf"
    settings_md = h.agent_meta / "SETTINGS.md"
    before = settings_md.read_text(encoding="utf-8")
    settings_md.write_text(A.CAP_LINE.sub("max_harness_tool_output: 200000", before, 1), encoding="utf-8")
    live = talk("play", out_f, "--quiet")
    out, err = live.communicate(command("message", text="hush") + command("quit"), timeout=120)
    settings_md.write_text(before, encoding="utf-8")
    quiet_events = events_of(out)
    kinds = [one.get("kind") for one in quiet_events]
    quiet_cap = next((one.get("cap") for one in quiet_events if one.get("kind") == "opened"), None)
    if (live.returncode == 0 and "step" not in kinds and kinds.count("conduction") == 2 and kinds.count("agent") == 2
            and all(one in kinds for one in ("opened", "principal", "response", "verdict", "waiting", "closed"))
            and quiet_cap == {"set": 200000, "applied": 200000}):
        held("--quiet silences the steps alone", f"{len(kinds)} events, no step; conduction x2, agent x2, "
             f"the house's events present; at the cap add writes, opened says {quiet_cap}")
    else:
        failures.append(f"  ✗ quiet                       rc={live.returncode} kinds={kinds} cap={quiet_cap} err={err[-200:]!r}")
    # --- set: the policy of the next launches, judged, said; the refused ones change nothing ------------
    known = set(keys())
    out_g = bench.temp() / "jg"
    live = talk("play", out_g, "--model", "m1")
    out, err = live.communicate(command("message", text="first") + command("set", model="m2")
                                + command("set", provider="x") + command("set", permissions="strict")
                                + command("set", model="") + command("set", dance=1)
                                + command("message", text="second") + command("quit"), timeout=120)
    key_g = fresh(known)
    flow = events_of(out)
    openings = [one for one in flow if one.get("kind") == "opened"]
    policies = [one for one in flow if one.get("kind") == "policy"]
    refused = [one.get("code") for one in flow if one.get("kind") == "refused"]
    sent = [one.get("policy") for one in h.messages() if one.get("run") == key_g]
    if (live.returncode == 0 and err == "" and key_g and len(openings) == 2
            and openings[0].get("provider") == "harness" and openings[0].get("policy") == {"model": "m1"}
            and openings[1].get("policy") == {"model": "m2", "permissions": "strict"}
            and len(policies) == 2 and policies[0].get("provider") == "harness" and policies[0].get("policy") == {"model": "m2"}
            and policies[1].get("policy") == {"model": "m2", "permissions": "strict"}
            and refused == ["provider-fixed", "policy-invalid", "policy-unknown"]
            and sent == [{"model": "m1"}, {"model": "m2", "permissions": "strict"}]):
        held("set changes the next launch's policy", f"run {key_g}: opened says harness and {{model: m1}}; the sets "
             f"said by policy {{model: m2}} then {{model: m2, permissions: strict}}; messages.jsonl {sent}; "
             "provider-fixed, policy-invalid and policy-unknown refused, the policy held")
    else:
        failures.append(f"  ✗ set                         rc={live.returncode} err={err[-200:]!r} openings={openings} "
                        f"policies={policies} refused={refused} sent={sent}")

    # --- ready: the run said before any message, at an opening and at a resume --------------------------
    known = set(keys())
    out_s = bench.temp() / "js"
    live = talk("play", out_s, "--model", "m1")
    out, err = live.communicate(command("quit"), timeout=60)
    start = events_of(out)
    ready = start[0] if start else {}
    resumed = talk("play", bench.temp() / "jt", "--run", key_g)
    out_t, err_t = resumed.communicate(command("quit"), timeout=60)
    taken = events_of(out_t)
    ready_t = taken[0] if taken else {}
    if (live.returncode == 0 and err == "" and [one.get("kind") for one in start] == ["ready", "waiting", "closed"]
            and ready.get("run") is None and ready.get("agent") == "agents/ag1" and ready.get("resumed") is False
            and ready.get("provider") == "harness" and ready.get("policy") == {"model": "m1"}
            and ready.get("packages") == [{"name": "agent", "on": True}] and ready.get("conducted") is True
            and ready.get("cap") == opened_cap and set(keys()) == known
            and resumed.returncode == 0 and err_t == "" and [one.get("kind") for one in taken][:2] == ["ready", "waiting"]
            and ready_t.get("run") == key_g and ready_t.get("resumed") is True
            and ready_t.get("policy") == {"model": "m2", "permissions": "strict"}
            and ready_t.get("packages") == openings[-1].get("packages")):
        held("ready says the run before any message", f"an opening: ready (run null, harness, {{model: m1}}, packages "
             f"{ready.get('packages')}, cap {ready.get('cap')}, conducted) then waiting, no run opened; chat --run {key_g}: "
             f"ready says the run, resumed, its last policy {ready_t.get('policy')} and the packages its opened said")
    else:
        failures.append(f"  ✗ ready                       rc={live.returncode}/{resumed.returncode} err={(err + err_t)[-200:]!r} "
                        f"start={start} taken={taken[:2]}")
    # --- set of the regime on a provider that does not spell it: policy-unsupported, nothing launched ------
    unregimed = A.lacking(h.house, "permissions")   # an adapter that spells no regime
    known = set(keys())
    argv = [sys.executable, str(h.engine), "--instance", str(h.house), "agent", "chat", "agents/ag1", "--json",
            "--provider", unregimed]
    unspelled = subprocess.run(argv, input=command("set", permissions="strict") + command("quit"), capture_output=True,
                               text=True, cwd=h.ws, env={**os.environ, **h.env}, timeout=60)
    flow_u = events_of(unspelled.stdout)
    if (unregimed and unspelled.returncode == 0 and [one.get("code") for one in flow_u if one.get("kind") == "refused"] == ["policy-unsupported"]
            and not any(one.get("kind") == "policy" for one in flow_u) and set(keys()) == known):
        held("a regime the provider does not spell refuses at the set", f"{unregimed}: policy-unsupported, no policy said, "
             "no run opened, closed")
    else:
        failures.append(f"  ✗ unspelled                   rc={unspelled.returncode} {[o.get('kind') for o in flow_u]} "
                        f"{flow_u[-3:]} {unspelled.stderr[-200:]!r}")

    # --- conduct: run-missing before the run, a bare exchange, the conduction back ---------------------
    def until_kind(stream, kind: str) -> list[dict]:
        seen = []
        while True:
            line = stream.readline()
            if not line:
                return seen
            seen.append(json.loads(line))
            if seen[-1].get("kind") == kind:
                return seen

    known = set(keys())
    out_h = bench.temp() / "jh"
    live = talk("play", out_h)
    assert live.stdin is not None and live.stdout is not None
    live.stdin.write(command("conduct", on=False) + command("message", text="first"))
    live.stdin.flush()
    first_part = until_kind(live.stdout, "verdict")
    calls_before = len(h.calls(out_h))
    opened_key = fresh(known)
    trace_before = len(h.trace(opened_key)) if opened_key else -1
    live.stdin.write(command("conduct", on=False) + command("message", text="bare one"))
    live.stdin.flush()
    bare_part = until_kind(live.stdout, "verdict")
    calls_after = len(h.calls(out_h))
    trace_after = len(h.trace(opened_key)) if opened_key else -2
    live.stdin.write(command("conduct", on=True) + command("message", text="again") + command("quit"))
    out, err = live.communicate(timeout=120)
    last_part = events_of(out)
    key_h = fresh(known)
    prompts = sorted(Path(str(out_h) + ".prompt.w-1.3").parent.glob(Path(str(out_h)).name + ".prompt.*"))
    bare_prompt = Path(str(out_h) + ".prompt.w-1.3").read_text(encoding="utf-8") if Path(str(out_h) + ".prompt.w-1.3").is_file() else ""
    sent_h = [one.get("conducted") for one in h.messages() if one.get("run") == key_h]
    kept_h = [one.get("conducted") for one in responses() if one.get("run") == key_h]
    bare_kinds = [one.get("kind") for one in bare_part]
    verdicts = [one for one in first_part + bare_part + last_part if one.get("kind") == "verdict"]
    status_h = [one for one in events_of(h.call("agent", "status", "agents/ag1", "--json").stdout) if one.get("run") == key_h]
    early = [one.get("code") for one in first_part if one.get("kind") == "refused"]
    if (live.returncode == 0 and err == "" and early == ["run-missing"]
            and [one.get("on") for one in bare_part + last_part if one.get("kind") == "conduct"] == [False, True]
            and "conduction" not in bare_kinds and "step" not in bare_kinds
            and [one.get("state") for one in verdicts] == ["parked", "unconducted", "parked"]
            and verdicts[1].get("launches") == 1 and calls_after == calls_before and trace_after == trace_before >= 1
            and "▌ pp · run" not in bare_prompt and "bare one" in bare_prompt and HEAD in bare_prompt
            and any(one.get("kind") == "opened" and one.get("conducted") is False for one in bare_part)
            and [one.get("kind") for one in last_part].count("conduction") >= 1
            and sent_h == [None, False, None] and kept_h == [None, False, None]
            and status_h and status_h[0].get("state") == "parked"):
        held("conduct off makes a bare exchange, on brings the conduction back", f"run {key_h}: run-missing before the "
             f"run; the bare exchange: one launch, no conduction nor step, no call of pp (the run's trace {trace_before} "
             f"lines before and after, the witness's calls {calls_before} and {calls_after}), its prompt the message under its head alone, verdict unconducted, both record lines conducted false; "
             "the run parked; after conduct on, the conduction is back and the verdict parked")
    else:
        failures.append(f"  ✗ conduct                     rc={live.returncode} err={err[-200:]!r} first={first_part[:1]} "
                        f"bare={bare_kinds} verdicts={[o.get('state') for o in verdicts]} calls={calls_before}/{calls_after} trace={trace_before}/{trace_after} "
                        f"prompt={bare_prompt[:120]!r} sent={sent_h} kept={kept_h} status={status_h[:1]} prompts={[p.name for p in prompts]}")

    # --- package: the run's packages, the engine's switch under the mark, the refusal relayed ----------
    known = set(keys())
    out_i = bench.temp() / "ji"
    live = talk("play", out_i)
    out, err = live.communicate(command("message", text="first") + command("package", name="agent", on=False)
                                + command("package", name="nowhere", on=False)
                                + command("message", text="second") + command("quit"), timeout=120)
    key_i = fresh(known)
    flow = events_of(out)
    openings = [one for one in flow if one.get("kind") == "opened"]
    switched = [one for one in flow if one.get("kind") == "package"]
    refused = [one.get("code") for one in flow if one.get("kind") == "refused"]
    details = [one.get("detail") for one in flow if one.get("kind") == "refused"]
    later = [one for one in flow[flow.index(switched[0]):] if one.get("kind") == "conduction"] if switched else []
    switches = [one for one in h.trace(key_i) if one.get("kind") == "switch"] if key_i else []
    if (live.returncode == 0 and err == "" and openings and openings[0].get("packages") == [{"name": "agent", "on": True}]
            and len(switched) == 1 and switched[0].get("name") == "agent" and switched[0].get("on") is False
            and switched[0].get("packages") == [{"name": "agent", "on": False}] and switched[0].get("pending") is False
            and refused == ["package-unpinned"] and details and "nowhere" in str(details[0]) and len(switches) == 1
            and later and "agent off" in str(later[0].get("text", "")).split("\n")[1]
            and openings[-1].get("packages") == [{"name": "agent", "on": False}]):
        held("package switches the run's package under the mark", f"run {key_i}: opened says [agent on]; package agent off "
             "answers [agent off], the trace says switch once, the next conducted prompt's state line says `agent off`; "
             "nowhere refused package-unpinned with the engine's detail")
    else:
        failures.append(f"  ✗ package                     rc={live.returncode} err={err[-200:]!r} openings={[o.get('packages') for o in openings]} "
                        f"switched={switched} refused={refused} switches={len(switches)} later={[str(o.get('text',''))[:120] for o in later[:1]]}")
    if "step" in [one.get("kind") for one in events]:
        held("steps are said without --quiet", f"{[one.get('kind') for one in events].count('step')} step events in "
             "the first conversation")
    else:
        failures.append("  ✗ steps                       no step event in the first conversation")

    # --- conduction: its blocks, read from the trace since the conduction before ----------------------
    def stacks(one: dict) -> list[str]:
        return [str(block.get("stack", "")) for block in one.get("blocks") or [] if isinstance(block, dict)]

    second = [one for one in events if one.get("kind") == "conduction" and one.get("exchange") == 2]
    quiet_conductions = [one for one in quiet_events if one.get("kind") == "conduction"]
    shaped = all(isinstance(one.get("blocks"), list) and one.get("chars") == len(str(one.get("text", "")))
                 and all({"stack", "command", "wait"} <= set(block) for block in one["blocks"])
                 for one in conductions)
    known = set(keys())
    out_r = bench.temp() / "jr"
    live = talk("play", out_r, "--run", key)
    out, err = live.communicate(command("message", text="again") + command("quit"), timeout=120)
    taken_up = [one for one in events_of(out) if one.get("kind") == "conduction"]
    if (conductions and shaped and any(one.startswith("BOOT") for one in stacks(conductions[0]))
            and second and stacks(second[0])
            and quiet_conductions and all("blocks" not in one and "left" not in one
                                          and one.get("chars") == len(str(one.get("text", "")))
                                          for one in quiet_conductions)
            and live.returncode == 0 and taken_up and stacks(taken_up[0]) and fresh(known) == ""):
        held("conduction says the blocks it serves", f"first {stacks(conductions[0])}; the second exchange's first "
             f"{stacks(second[0])}; chat --run {key}: {stacks(taken_up[0])}; chars == len(text) everywhere; "
             "under --quiet chars alone")
    else:
        failures.append(f"  ✗ blocks                      shaped={shaped} first={[stacks(o) for o in conductions[:2]]} "
                        f"second={[stacks(o) for o in second[:1]]} quiet={[sorted(o) for o in quiet_conductions[:1]]} "
                        f"run rc={live.returncode} taken_up={[stacks(o) for o in taken_up[:1]]} err={err[-200:]!r}")

    return 0
