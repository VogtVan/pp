"""Scenario `agent-budget` -- 7 case(s) (batch le-plafond-du-run, 2026-10-11): `--max-budget-usd` is the CAP of a
run, held by the providers' abstraction alone -- every expectation a provider bears on is computed through the
engine's face (`conductor.adapters.load(...)`, its `SPELLS` and `COST`, `conductor.adapters.launch(...)`), never
from a provider's literal. The witness speaks the grammar of the adapter `--provider` names (its own when none).
- a run capped between two exchanges: under a cap of 0.15 the first exchange plays its two launches (0.16 spent:
  the second launch left with 0.05); the second refuses `budget-spent` before any launch, exit 2, no line added to
  `messages.jsonl` nor `responses.jsonl`; `status --json` says the run's budget 0.16 of 0.15
- a stop between two launches: under a cap of 0.10 the first launch plays (0.10), the second never leaves; the
  response of the first is kept as the run's first exchange, `status --json` says the run standing -- the first never
  reached its frontier -- and the refusal its reason `budget-spent`
- the remainder passed through the abstraction: for each adapter of the product whose `COST` measures, a dry run
  of the run that spent 0.16 under `--max-budget-usd 1` composes the line `conductor.adapters.launch` composes for
  the remainder 0.84 when the adapter spells `max_budget_usd`, without the key otherwise
- the response a cap stopped says it (agent 0.23.3): the line of `responses.jsonl` the stop between two launches
  kept carries `error: "budget-spent"` and `budget {cap, spent}`; the exchange that went past its cap at its last
  launch and arrived keeps `error` null and no `budget`
- a cap the run cannot measure refuses: under the grammar of an adapter whose `COST` is None, `--max-budget-usd`
  refuses `budget-unmeasured` before anything -- no run opened, no record
- a conversation: under a cap of 0.15 the second message is refused `budget-spent` (a verdict, no response), a
  `set` that raises the cap holds, the next message plays; `ready` says no cap, `opened` and `verdict` say
  `budget {cap, spent, left}`
- the faces: `status --json` and the `ready` of a resumed conversation say the run's `budget`
"""
from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys

from conductor import adapters
from tests.harness import support

A = support(__file__, "agent")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)
    h.lawful()          # the exchanges owe a proof: two launches, the boot with the WORK then the frontier (plan fixes1)
    keys, counted = h.keys, h.counted

    def fresh(known: set) -> str:
        return next((one for one in keys() if one not in known), "")

    def run(*flags: str, mode: str = "play") -> subprocess.CompletedProcess:
        return h.call("agent", "run", "agents/ag1", *flags, *h.harnessed(mode))

    def budget(cap: float, spent: float) -> dict:
        return {"cap": cap, "spent": round(spent, 6), "left": round(cap - spent, 6)}

    # --- a run capped between two exchanges -------------------------------------------------------------
    known = set(keys())
    first = run("--message", "un", "--max-budget-usd", "0.15")
    key_a = fresh(known)
    recorded = counted()
    second = run("--run", key_a, "--message", "deux")
    if (first.returncode == 0 and key_a and h.face(key_a).get("budget") == budget(0.15, 0.16)
            and second.returncode == 2 and "budget-spent" in second.stderr and counted() == recorded):
        held("a run capped between two exchanges", f"run {key_a}: the first exchange spent 0.16 (two launches) under a cap of 0.15; "
             "the second refuses budget-spent before any launch, nothing recorded")
    else:
        failures.append(f"  ✗ capped run                  {first.returncode}/{second.returncode} key={key_a!r} "
                        f"{first.stderr[-240:]!r} {second.stderr[-240:]!r} {recorded}/{counted()}")

    # --- a stop between two launches ----------------------------------------------------------------------
    known = set(keys())
    stopped = run("--message", "un", "--max-budget-usd", "0.10")
    key_b = fresh(known)
    kept = h.responses()[-1] if h.responses() else {}
    if (stopped.returncode == 2 and key_b and "budget-spent" in stopped.stderr and kept.get("run") == key_b
            and kept.get("launches") == 1 and kept.get("response") and kept.get("index") == 1
            and h.face(key_b).get("state") == "standing"):
        held("a stop between two launches", f"run {key_b}: one launch under a cap of 0.10, its response kept, the run "
             "standing, the reason budget-spent")
    else:
        failures.append(f"  ✗ stop between launches       rc={stopped.returncode} key={key_b!r} kept={kept} "
                        f"{stopped.stderr[-300:]!r}")

    # --- the response a cap stopped says it -----------------------------------------------------------------
    arrived = next((one for one in h.responses() if one.get("run") == key_a), {})
    if (kept.get("error") == "budget-spent" and kept.get("budget") == {"cap": 0.10, "spent": 0.10}
            and arrived and arrived.get("error") is None and "budget" not in arrived):
        held("the response a cap stopped says it", f"run {key_b}: error budget-spent, budget {kept.get('budget')}; "
             f"run {key_a}, arrived past its cap, error null and no budget")
    else:
        failures.append(f"  ✗ stopped response            kept={ {k: kept.get(k) for k in ('error', 'budget')} } "
                        f"arrived={ {k: arrived.get(k, 'absent') for k in ('error', 'budget')} }")

    # --- the remainder passed through the abstraction --------------------------------------------------------
    product = adapters.product_of(h.house) / "adapters"
    named = sorted(one.name for one in product.iterdir() if (one / "wire.py").is_file())
    costs = {one: getattr(adapters.load(one, h.house), "COST", "absent") for one in named}
    measured = [one for one in named if costs[one] in ("session", "launch")]
    composed, recorded = {}, counted()[:2]
    for provider in measured:
        with (h.records / "sessions.jsonl").open("a", encoding="utf-8") as handle:   # a session no model makes here
            handle.write(json.dumps({"at": "2026-10-11T00:00:00+00:00", "agent": "agents/ag1", "run": key_a,
                                     "provider": provider, "session": "S"}) + "\n")
        spells = getattr(adapters.load(provider, h.house), "SPELLS", ())
        policy = {"max_budget_usd": 0.84} if "max_budget_usd" in spells else {}
        argv = adapters.launch(provider, h.agent_ws, h.agent_meta, "x", marble=h.agent_meta / ".sys" / "system.common.md",
                               wiring=h.ws, policy=policy, session="S")[0]
        dry = h.call("agent", "run", "agents/ag1", "--run", key_a, "--provider", provider, "--max-budget-usd", "1",
                     "--message", "later", "--dry-run")
        composed[provider] = (dry.returncode, shlex.join(argv) in dry.stdout.splitlines(), dry.stderr[-200:])
    if measured and all(rc == 0 and found for rc, found, _ in composed.values()) and counted()[:2] == recorded:
        held("the remainder is passed through the abstraction", f"{', '.join(measured)}: the dry run composes the line "
             "conductor.adapters.launch composes for the remainder 0.84 -- the key dropped where the adapter spells none")
    else:
        failures.append(f"  ✗ remainder                   costs={costs} {composed} {recorded}/{counted()[:2]}")

    # --- a cap the run cannot measure refuses ------------------------------------------------------------------
    unmeasured = [one for one in named if costs[one] is None]
    known, recorded = set(keys()), counted()
    refused = h.call("agent", "run", "agents/ag1", "--max-budget-usd", "1", "--message", "x",
                     *A.harnessing(h.harness("play"), unmeasured[0])) if unmeasured else None
    if (refused is not None and refused.returncode == 2 and "budget-unmeasured" in refused.stderr
            and set(keys()) == known and counted() == recorded):
        held("a cap the run cannot measure refuses", f"{unmeasured[0]} (COST None): budget-unmeasured before "
             "anything -- no run opened, no record")
    else:
        failures.append(f"  ✗ unmeasured                  {unmeasured} "
                        f"{(refused.returncode, refused.stderr[-240:]) if refused else None}")

    # --- a conversation: refused, raised, played ------------------------------------------------------------
    def talk(where, commands: str, *flags: str) -> tuple[subprocess.CompletedProcess, list[dict]]:
        argv = [sys.executable, str(h.engine), "--instance", str(h.house), "agent", "chat", "agents/ag1", *flags,
                "--json", *h.harnessed_at("play", where)]
        played = subprocess.run(argv, input=commands, capture_output=True, text=True, cwd=h.ws,
                                env={**os.environ, **h.env}, timeout=180)
        found = []
        for line in played.stdout.splitlines():
            try:
                found.append(json.loads(line))
            except ValueError:
                found.append({"kind": "UNREADABLE", "line": line})
        return played, found

    def command(kind: str, **fields) -> str:
        return json.dumps({"kind": kind, **fields}) + "\n"

    known = set(keys())
    played, flow = talk(bench.temp() / "chat", command("set", max_budget_usd=0.15) + command("message", text="un")
                        + command("message", text="deux") + command("set", max_budget_usd=1)
                        + command("message", text="trois") + command("quit"))
    key_c = fresh(known)
    kinds = [one.get("kind") for one in flow]
    ready = next((one for one in flow if one.get("kind") == "ready"), {})
    opened = [one.get("budget") for one in flow if one.get("kind") == "opened"]
    verdicts = [one for one in flow if one.get("kind") == "verdict"]
    responses = [one for one in flow if one.get("kind") == "response"]
    if (played.returncode == 0 and "budget" in ready and ready["budget"] is None
            and opened == [budget(0.15, 0), budget(1.0, 0.16)]
            and len(verdicts) == 3 and str(verdicts[1].get("reason", "")).startswith("budget-spent")
            and verdicts[1].get("kept") is False and len(responses) == 2
            and verdicts[0].get("budget") == budget(0.15, 0.16) and verdicts[2].get("budget") == budget(1.0, 0.19)):
        held("a conversation is refused, raised, played", f"run {key_c}: the second message refused budget-spent, "
             "a set raises the cap to 1, the third plays; opened and verdict say {cap, spent, left}")
    else:
        failures.append(f"  ✗ conversation                rc={played.returncode} kinds={kinds} ready={ready.get('budget', 'absent')} "
                        f"opened={opened} verdicts={[(one.get('budget'), one.get('reason')) for one in verdicts]} "
                        f"err={played.stderr[-200:]!r}")

    # --- the faces: status --json, the ready of a resumed conversation ---------------------------------------------
    faced = h.call("agent", "status", "agents/ag1", "--json")
    rows = {}
    for line in faced.stdout.splitlines():
        try:
            one = json.loads(line)
        except ValueError:
            continue
        if one.get("run"):
            rows[one["run"]] = one.get("budget", "absent")
    played, flow = talk(bench.temp() / "again", command("quit"), "--run", key_c)
    ready = next((one for one in flow if one.get("kind") == "ready"), {})
    if (faced.returncode == 0 and rows.get(key_c) == budget(1.0, 0.19) and rows.get(key_b) == budget(0.10, 0.10)
            and played.returncode == 0 and ready.get("budget") == budget(1.0, 0.19)):
        held("the faces say the budget", f"status --json: run {key_c} {rows.get(key_c)}, run {key_b} {rows.get(key_b)}; "
             "the ready of a resumed conversation says the same")
    else:
        failures.append(f"  ✗ faces                       rc={faced.returncode}/{played.returncode} rows={rows} "
                        f"ready={ready.get('budget', 'absent')} err={played.stderr[-200:]!r}")
    return 0
