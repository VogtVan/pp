"""Scenario `agent-chat-resume` -- a resume keeps what the run was (batch les-retours-du-reel,
2026-10-08), on a house wired with TWO providers by their adapters' `wire()` (KEPT, the house's own, and
OTHER), the witness harness playing:
- the policy: a run whose model was set to `m2` before its second message is resumed by
  `chat --run <key>` with the witness and no policy flag: `opened` says `{model: m2}`, and the
  message's line at `messages.jsonl` carries it; `--model m3` on the resume prevails
- `harness-required`: a run opened under a caller's command, resumed without `--harness`
- the provider: the run's session line made KEPT's by the bench's hand, `chat --run <key>` with no
  flag opens the conversation (no `provider-ambiguous`), its `ready` says KEPT, and closes on `quit`, nothing launched;
  `run --run <key> --dry-run` composes the line `conductor.adapters.launch` composes for KEPT, the run's policy and session
- `provider-mismatch`: `--provider <OTHER>` on that run; `provider-unwired`: a session of a provider the house
  is not wired with
"""
from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys

from conductor import adapters, install
from tests.harness import support

A = support(__file__, "agent")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)
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
        return 0

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
    resumed = chat("--run", key, stdin=command("quit"))
    kinds = [one.get("kind") for one in events(resumed)]
    dry = h.call("agent", "run", "agents/ag1", "--run", key, "--message", "five", "--dry-run")
    last = (h.messages() or [{}])[-1].get("policy") or None
    line = shlex.join(adapters.launch(kept_p, h.agent_ws, h.agent_meta, "x", wiring=h.ws, policy=last,
                                      marble=h.agent_meta / ".sys" / "system.common.md",
                                      session=str(session.get("session")))[0]) if kept_p else ""
    if (resumed.returncode == 0 and resumed.stderr == "" and kinds == ["ready", "waiting", "closed"]
            and kept_p and other_p and events(resumed)[0].get("provider") == kept_p
            and dry.returncode == 0 and line in dry.stdout.splitlines() and last == {"model": "m3"}):
        held("a resume keeps the run's provider", f"no provider-ambiguous on a house wired {kept_p} + {other_p}: "
             f"{kinds}, ready says {kept_p}, rc 0; --dry-run composes the {kept_p} line for the run's policy {last} and its "
             f"session {session.get('session')}")
    else:
        failures.append(f"  ✗ the provider                rc={resumed.returncode} {resumed.stderr[-200:]!r} {kinds} "
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
    return 0
