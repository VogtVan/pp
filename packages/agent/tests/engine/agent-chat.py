"""Scenario `agent-chat` -- a conversation with an agent, one run from a message to the next, and its resume:
- two messages, one run: `agent chat` reads its messages on stdin, one per line --
  `printf 'un\\ndeux\\n' | agent chat agents/ag1 --harness <witness>` plays two exchanges of the same
  run: two responses on stdout, two verdicts on stderr, exit 0; `responses.jsonl` two lines of that run
  (index 1 and 2), `messages.jsonl` two, `sessions.jsonl` one; the trace says both prompts, the witness's
  second prompt carries `deux` under the head
- the continuation: `un \\` then `deux` make ONE message of two lines, kept as typed at the record
- the lock is held: while the conversation lives, `agent run --run <key>` refuses `run-busy`; its stdin
  closed, the conversation exits 0, the lock is free and the same call plays; an empty stdin opens nothing
- an exchange is interrupted: a SIGINT to `pp-agent` (the console's child, found at /proc) while the witness
  pauses ends the harness (`alive(pid)` false), the run stands, stderr says `interrupted`; the next message
  takes the run up (`standing resumed`) to its AWAIT
- an exchange that fails says why and the conversation goes on: under `--launches 1` each message spends
  it (`launches-spent`, the response kept, the exchange standing -- the boot whole takes one launch, the
  AWAIT another), the second message resumes it standing; the `verdict` events of the run's flow say both
- the refusals: `--message`, `--message-file`, `--dry-run`, `--tag`, `--on-end`, `--new` refuse
  `flag-unsupported`, nothing opened; `--run <unknown>` refuses `run-unknown`
- the policy kept: on a house wired with TWO providers by their adapters' `wire()` (KEPT, the house's own,
  and OTHER), a run whose model was set to `m2` before its second message is resumed by `chat --run <key>`
  with the witness and no policy flag: `opened` says `{model: m2}`, the message's line at `messages.jsonl`
  carries it; `--model m3` on the resume prevails
- `harness-required`: a run opened under a caller's command, resumed without `--harness`
- the provider kept: the run's session line made KEPT's by the bench's hand, `chat --run <key>` with no
  flag opens the conversation (no `provider-ambiguous`), its `ready` says KEPT, and closes on `quit`,
  nothing launched; `run --run <key> --dry-run` composes the line `conductor.adapters.launch` composes for
  KEPT, the run's policy and session
- `provider-mismatch`: `--provider <OTHER>` on that run; `provider-unwired`: a session of a provider the
  house is not wired with
"""
from __future__ import annotations

import json
import os
import shlex
import signal
import subprocess
import sys
import time
from pathlib import Path

from conductor import adapters, install
from conductor.state import lock
from tests.harness import support

A = support(__file__, "agent")
HEAD = A.HEAD
HOLD = 10.0                      # seconds a case waits for the witness to show up, or to die


def scenario(bench) -> int:
    conversed(bench, A.House(bench))     # counts the runs and records of its house, case after case
    resumed(bench, A.House(bench))       # wired with a second provider, its run the house's first
    return 0


def flow_of(h, key: str) -> list[dict]:
    """-> the events of the run's flow file under the house's records, in order."""
    found = []
    for path in sorted((h.records / "flows").rglob(f"{key}.jsonl")) if key else []:
        found += A.lines(path)
    return found


def conversed(bench, h) -> None:
    held, failures = bench.held, bench.failures
    keys, trace, responses, messages, sessions = h.keys, h.trace, h.responses, h.messages, h.sessions

    def converse(mode: str, where, *flags: str) -> subprocess.Popen:
        """`agent chat agents/ag1` under the witness in `mode`, its stdin a pipe the case writes."""
        argv = [sys.executable, str(h.engine), "--instance", str(h.house), "agent", "chat", "agents/ag1",
                *flags, *h.harnessed_at(mode, where)]
        return subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, cwd=h.ws, env={**os.environ, **h.env})

    def fresh(known: set) -> str:
        return next((one for one in keys() if one not in known), "")

    def of_run(key: str, record) -> list[dict]:
        return [one for one in record() if one.get("run") == key]

    def until(condition, bound: float = HOLD) -> bool:
        opened = time.monotonic()
        while time.monotonic() - opened < bound:
            if condition():
                return True
            time.sleep(0.05)
        return condition()

    def child_of(pid: int) -> int:
        """-> the pid of the one child of `pid` (the skill the console launched), 0 when none."""
        for one in Path("/proc").iterdir():
            if one.name.isdigit():
                try:
                    stat = (one / "stat").read_text(encoding="utf-8")
                except OSError:
                    continue
                if int(stat.rsplit(")", 1)[1].split()[1]) == pid:
                    return int(one.name)
        return 0

    # --- two messages, one run ---------------------------------------------------------------------
    out_a = bench.temp() / "pa"
    talk = converse("play", out_a)
    out, err = talk.communicate("un\ndeux\n", timeout=120)
    key = keys()[0] if keys() else ""
    prompts = [one.get("text") for one in trace(key) if one.get("kind") == "prompt"] if key else []
    kept, sent = of_run(key, responses), of_run(key, messages)
    if (talk.returncode == 0 and len(keys()) == 1 and out == "witness answer: play\nwitness answer: play\n"
            and f"pp-agent: agents/ag1 · run {key} · exchange 1 · parked · harness rc 0" in err
            and f"pp-agent: agents/ag1 · run {key} · exchange 2 · parked · harness rc 0" in err
            and prompts == ["un", "deux"]
            and [one.get("index") for one in kept] == [1, 2] and all(one.get("harness_rc") == 0 for one in kept)
            and set(kept[0]) == A.RECORD_FIELDS
            and [one.get("message") for one in sent] == ["un", "deux"] and len(sessions()) == 1
            and h.read(".prompt.w-1.2", out_a).startswith(f"{HEAD}\ndeux\n\n▌ pp · run {key}")):
        held("two messages, one run", f"run {key}: two exchanges parked, responses index 1 and 2, two messages, "
             "one session; the witness's second prompt opens on the second message under the head")
    else:
        failures.append(f"  ✗ two messages one run        rc={talk.returncode} keys={keys()} out={out!r} "
                        f"err={err[-400:]!r} prompts={prompts} kept={[(o.get('index'), o.get('harness_rc')) for o in kept]} "
                        f"sent={[o.get('message') for o in sent]} sessions={len(sessions())} "
                        f"p2={h.read('.prompt.w-1.2', out_a)[:60]!r}")

    # --- the continuation: a line ending on a backslash goes on ---------------------------------------
    known = set(keys())
    out_b = bench.temp() / "pb"
    talk = converse("play", out_b)
    out, err = talk.communicate("un \\\ndeux\n", timeout=120)
    key_b = fresh(known)
    sent_b = of_run(key_b, messages)
    if (talk.returncode == 0 and out == "witness answer: play\n" and len(sent_b) == 1
            and sent_b[0].get("message") == "un \ndeux"
            and h.read(".prompt.w-1.1", out_b).startswith(f"{HEAD}\nun \ndeux\n\n▌ pp · run {key_b}")):
        held("the continuation makes one message of two lines", "`un \\` then `deux`: one exchange, the record "
             "keeps 'un \\ndeux', the prompt carries it under the head")
    else:
        failures.append(f"  ✗ continuation                rc={talk.returncode} out={out!r} sent={[o.get('message') for o in sent_b]} "
                        f"p1={h.read('.prompt.w-1.1', out_b)[:60]!r} err={err[-200:]!r}")

    # --- the lock is held for the whole conversation; the end of stdin frees it -------------------------
    known = set(keys())
    out_c = bench.temp() / "pc"
    talk = converse("play", out_c, "--quiet")
    assert talk.stdin is not None and talk.stdout is not None
    talk.stdin.write("hello\n")
    talk.stdin.flush()
    first = talk.stdout.readline()
    key_c = fresh(known)
    launcher = A.launcher(h.agent_meta, key_c) if key_c else None
    during = bool(launcher) and lock.held(launcher)
    busy = h.call("agent", "run", "agents/ag1", "--run", key_c, "--message", "again", *h.harnessed("play"))
    out, err = talk.communicate(timeout=120)         # closes stdin: the end of the conversation
    after = bool(launcher) and launcher.exists() and not lock.held(launcher)
    again = h.call("agent", "run", "agents/ag1", "--run", key_c, "--message", "again", *h.harnessed("play"))
    empty = converse("play", bench.temp() / "pe")
    out_e, err_e = empty.communicate("", timeout=60)
    if (first == "witness answer: play\n" and during and busy.returncode == 2 and "run-busy" in busy.stderr
            and talk.returncode == 0 and out == "" and after
            and again.returncode == 0 and f"run {key_c} · exchange 2 · parked" in again.stderr
            and empty.returncode == 0 and out_e == "" and len(keys()) == len(known) + 1):
        held("the lock is held, the end of stdin frees it", f"run {key_c}: run-busy while the conversation lives; "
             "stdin closed -> exit 0, the lock present and free, the same resume plays (exchange 2); an empty "
             "stdin opens no run")
    else:
        failures.append(f"  ✗ lock held                   first={first!r} during={during} busy={busy.returncode} "
                        f"{busy.stderr[-160:]!r} rc={talk.returncode} after={after} again={again.returncode} "
                        f"{again.stderr[-200:]!r} empty={empty.returncode} keys={len(keys())}/{len(known)} err={err[-200:]!r}")

    # --- an exchange is interrupted: the harness ends, the run stands, the next message takes it up ------
    known = set(keys())
    out_d = bench.temp() / "pd"
    h.lawful()                       # the exchange owes a proof -- two launches -- so a SIGINT lands mid-exchange
    talk = converse("pause", out_d, "--quiet")
    assert talk.stdin is not None
    talk.stdin.write("think\n")
    talk.stdin.flush()
    shown = until(lambda: bool(h.read(".pid", out_d)))
    pid = int(h.read(".pid", out_d) or 0)
    skill = child_of(talk.pid)                     # pp-agent, the console's child: the SIGINT is its to handle
    if skill:
        os.kill(skill, signal.SIGINT)
    dead = until(lambda: not A.alive(pid)) if pid and skill else False
    time.sleep(0.3)
    chatting = talk.poll() is None
    key_d = fresh(known)
    still = bool(key_d) and lock.held(A.launcher(h.agent_meta, key_d))
    talk.stdin.write("go on\n")
    out, err = talk.communicate(timeout=120)         # flushes and closes stdin
    kept_d, sent_d = of_run(key_d, responses), of_run(key_d, messages)
    if (shown and pid and dead and chatting and still and talk.returncode == 0
            and "interrupted" in err and "standing resumed" in err
            and f"pp-agent: agents/ag1 · run {key_d} · exchange 1 · parked · harness rc 0" in err
            and kept_d and out == f"{A.composed(kept_d[-1])}\n" and "witness answer: pause" in out
            and [one.get("index") for one in kept_d] == [1] and [one.get("message") for one in sent_d] == ["think", "go on"]):
        held("an exchange is interrupted, the run stands, the next message takes it up",
             f"SIGINT while the witness (pid {pid}) paused: the harness dead, the conversation alive, the lock held, "
             "stderr says interrupted and nothing kept; 'go on' resumes the standing run to its AWAIT")
    else:
        failures.append(f"  ✗ interrupted                 shown={shown} pid={pid} dead={dead} chatting={chatting} still={still} "
                        f"rc={talk.returncode} out={out!r} kept={[o.get('index') for o in kept_d]} "
                        f"sent={[o.get('message') for o in sent_d]} err={err[-500:]!r}")

    # --- an exchange that fails says why, and the conversation goes on ----------------------------------
    known = set(keys())
    out_f = bench.temp() / "pf"
    talk = converse("play", out_f, "--launches", "1", "--quiet")
    out, err = talk.communicate("a\nb\n", timeout=120)
    key_f = fresh(known)
    kept_f = of_run(key_f, responses)
    verdicts = [one for one in flow_of(h, key_f) if one.get("kind") == "verdict"]
    said = [(one.get("exchange"), one.get("state"), one.get("harness_rc"), one.get("launches"),
             one.get("standing_resumed")) for one in verdicts]
    # an exchange takes two launches (the boot with the WORK, then the checkpoint): under `--launches 1` the first
    # never reaches its AWAIT (exchange 1 standing, the exchange under way), and the second message RESUMES it
    # standing -- its one launch judges the proof, the bare AWAIT launches nothing: parked. Its cost is the
    # witness's cumul at its second launch less its first (0.16 - 0.10)
    if (talk.returncode == 0 and err.count("pp-agent: launches-spent") == 1
            and said == [(1, "standing", 0, 1, False), (1, "parked", 0, 1, True)]
            and str(verdicts[0].get("reason") or "").startswith("launches-spent") and "reason" not in verdicts[1]
            and round(verdicts[1].get("cost_usd") or 0, 2) == 0.06 == round(kept_f[-1].get("cost_usd") or 0, 2)
            and err.count(f"pp-agent: agents/ag1 · run {key_f} · exchange 1 · ") == 2
            and out == "witness answer: play\nwitness answer: play\n"
            and [one.get("index") for one in kept_f] == [1, 2]
            and [one.get("launches") for one in kept_f] == [1, 1]):
        held("an exchange that fails says why, the conversation goes on", f"run {key_f}: launches-spent after 1 "
             "launch (the response kept, the exchange said standing), the second message resumed the standing "
             "exchange, its one launch judged the proof and the AWAIT launched nothing: parked, exit 0")
    else:
        failures.append(f"  ✗ failing exchange            rc={talk.returncode} out={out!r} kept={[(o.get('index'), o.get('launches')) for o in kept_f]} "
                        f"verdicts={verdicts} err={err[-500:]!r}")

    # --- the refusals -------------------------------------------------------------------------------
    before = len(keys())
    refused = {}
    for flags in (("--message", "x"), ("--message-file", "f"), ("--dry-run",), ("--tag", "t"),
                  ("--on-end", "true"), ("--new",)):
        played = h.call("agent", "chat", "agents/ag1", *flags, *h.harnessed("play"), stdin="hi\n")
        refused[flags[0]] = (played.returncode, "flag-unsupported" in played.stderr)
    unknown = h.call("agent", "chat", "agents/ag1", "--run", "zzzzzz", *h.harnessed("play"), stdin="hi\n")
    if (all(one == (2, True) for one in refused.values()) and unknown.returncode == 2 and "run-unknown" in unknown.stderr
            and len(keys()) == before):
        held("the refusals", f"{len(refused)} flags refuse flag-unsupported, --run <unknown> refuses run-unknown; "
             "no run opened")
    else:
        failures.append(f"  ✗ refusals                    {refused} unknown={unknown.returncode} {unknown.stderr[-160:]!r} "
                        f"keys={len(keys())}/{before}")


def resumed(bench, h) -> None:
    held, failures = bench.held, bench.failures
    for name in A.providers(h.house):                                  # a second wiring beside the house's own
        if name not in install.wired_providers(h.ws):
            A.wired(h.ws, h.house, name)
            if len(install.wired_providers(h.ws)) >= 2:
                break
    kept_p, other_p = (install.wired_providers(h.ws) + ["", ""])[:2]
    unwired = next((one for one in A.providers(h.house) if one not in install.wired_providers(h.ws)), "")
    out = bench.temp() / "jr"
    witness = h.harness_at("play", out)

    def command(kind: str, **fields) -> str:
        return json.dumps({"kind": kind, **fields}) + "\n"

    def chat(*flags: str, stdin: str = "") -> subprocess.CompletedProcess:
        argv = [sys.executable, str(h.engine), "--instance", str(h.house), "agent", "chat", "agents/ag1", "--json", *flags]
        return subprocess.run(argv, input=stdin, capture_output=True, text=True, cwd=h.ws,
                              env={**os.environ, **h.env}, timeout=120)

    def events(played) -> list[dict]:
        return [json.loads(one) for one in played.stdout.splitlines() if one.strip()]

    def opened(played) -> dict:
        return next((one for one in events(played) if one.get("kind") == "opened"), {})

    # --- a run made at the witness: m1, then m2 set before its second message --------------------
    made = chat(*A.harnessing(witness), "--model", "m1", stdin=command("message", text="one")
                + command("set", model="m2") + command("message", text="two") + command("quit"))
    key = h.keys()[0] if h.keys() else ""
    if made.returncode != 0 or not key:
        failures.append(f"  ✗ the run                     rc={made.returncode} {made.stderr[-300:]!r}")
        return

    # --- the policy kept: no flag takes the run's; a flag prevails ---------------------------------
    kept = chat("--run", key, *A.harnessing(witness), stdin=command("message", text="three") + command("quit"))
    named = chat("--run", key, *A.harnessing(witness), "--model", "m3", stdin=command("message", text="four")
                 + command("quit"))
    sent = [one.get("policy") for one in h.messages() if one.get("run") == key]
    if (kept.returncode == 0 and opened(kept).get("policy") == {"model": "m2"}
            and named.returncode == 0 and opened(named).get("policy") == {"model": "m3"}
            and sent == [{"model": "m1"}, {"model": "m2"}, {"model": "m2"}, {"model": "m3"}]):
        held("a resume keeps the run's policy", f"run {key}: resumed with no flag, opened says {{model: m2}}; "
             f"--model m3 prevails; messages.jsonl {sent}")
    else:
        failures.append(f"  ✗ the policy                  rc={kept.returncode}/{named.returncode} "
                        f"{opened(kept).get('policy')} {opened(named).get('policy')} sent={sent} {kept.stderr[-200:]!r}")

    # --- a caller's command is needed again ---------------------------------------------------------
    bare = chat("--run", key, stdin=command("quit"))
    if bare.returncode == 2 and "harness-required" in bare.stderr:
        held("a run of a caller's command asks it again", bare.stderr.strip()[:90])
    else:
        failures.append(f"  ✗ harness-required            rc={bare.returncode} {bare.stderr[-200:]!r}")

    # --- the provider kept: the session made KEPT's by the bench's hand -------------------------------
    session = A.lines(h.records / "sessions.jsonl")[-1]
    with (h.records / "sessions.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({**session, "provider": kept_p}) + "\n")
    taken = chat("--run", key, stdin=command("quit"))
    kinds = [one.get("kind") for one in events(taken)]
    dry = h.call("agent", "run", "agents/ag1", "--run", key, "--message", "five", "--dry-run")
    last = (h.messages() or [{}])[-1].get("policy") or None
    line = shlex.join(adapters.launch(kept_p, h.agent_ws, h.agent_meta, "x", wiring=h.ws, policy=last,
                                      marble=h.agent_meta / ".sys" / "system.common.md",
                                      session=str(session.get("session")))[0]) if kept_p else ""
    if (taken.returncode == 0 and taken.stderr == "" and kinds == ["ready", "waiting", "closed"]
            and kept_p and other_p and events(taken)[0].get("provider") == kept_p
            and dry.returncode == 0 and line in dry.stdout.splitlines() and last == {"model": "m3"}):
        held("a resume keeps the run's provider", f"no provider-ambiguous on a house wired {kept_p} + {other_p}: "
             f"{kinds}, ready says {kept_p}, rc 0; --dry-run composes the {kept_p} line for the run's policy {last} and its "
             f"session {session.get('session')}")
    else:
        failures.append(f"  ✗ the provider                rc={taken.returncode} {taken.stderr[-200:]!r} {kinds} "
                        f"dry rc={dry.returncode} {dry.stdout[-300:]!r} {dry.stderr[-200:]!r}")

    # --- a provider named that is not the run's; a provider no longer wired -----------------------------
    mismatched = chat("--run", key, "--provider", other_p, stdin=command("quit"))
    with (h.records / "sessions.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({**session, "provider": unwired}) + "\n")
    gone = chat("--run", key, stdin=command("quit"))
    if (unwired and mismatched.returncode == 2 and "provider-mismatch" in mismatched.stderr
            and gone.returncode == 2 and "provider-unwired" in gone.stderr):
        held("a resume refuses another provider, or one unwired", f"{mismatched.stderr.strip()[:60]!r}; "
             f"{gone.stderr.strip()[:70]!r}")
    else:
        failures.append(f"  ✗ the refusals                {mismatched.returncode} {mismatched.stderr[-160:]!r} / "
                        f"{gone.returncode} {gone.stderr[-160:]!r}")
