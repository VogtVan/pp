"""packages/agent/skills/pp-agent -- the house's console verb, as the operator drives it
(batch le-package-agent, 2026-09-27; its rework, 2026-10-03): `./pp help` lists `agent` with its
package and its `add`; `./pp agent` without a verb says the usage in one line, exit 2; `status` on a
path no agent stands at refuses `agent-unknown`; `agent add ag1` gives birth to the agent at `ag1`; the policy travels as data -- `run --model --max-budget-usd --provider <an adapter that spells both>
--dry-run` says the line the face composes, and a cap under an adapter whose `COST` is None refuses
`budget-unmeasured`, nothing launched, no run opened; `start` without a message relays
`message-missing` in one line, nothing launched; `purge` without a key nor a date says the usage,
which names it.
"""
from __future__ import annotations

import shlex

from conductor import adapters, contributions, instance, persistence
from tests.harness import INSTANCE, SOURCE, cli

A = contributions.module_at(SOURCE / "packages" / "agent" / "tests" / "engine" / "_agent.py")   # `harnessing`


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("agent-house", packages=("agent",))
    ws = env.made.parent
    def call(*args: str):
        return cli(env.engine, *args, cwd=ws)

    # --- the console carries the verb ------------------------------------------------------
    helped = call("help")
    bare = call("agent")
    agent_line = next((one for one in helped.stdout.splitlines() if "./pp agent" in one), "")
    if (helped.returncode == 0 and "(agent)" in agent_line and "`add <path>`" in agent_line
            and bare.returncode == 2 and "usage" in (bare.stderr + bare.stdout).lower()
            and len((bare.stderr + bare.stdout).strip().splitlines()) == 1):
        held("the console carries the verb", "./pp help lists `./pp agent (agent) …` with `add <path>`; "
             "a bare `./pp agent` says the usage in one line, exit 2")
    else:
        failures.append(f"  ✗ console verb                {helped.returncode}/{bare.returncode} "
                        f"{helped.stdout[-200:]!r} {bare.stderr[-200:]!r}")

    # --- an unknown agent refuses by name ---------------------------------------------------
    nobody = call("agent", "status", "nobody")
    if nobody.returncode == 2 and "agent-unknown" in nobody.stderr:
        held("agent-unknown", "status on a name no agent wears refuses by name")
    else:
        failures.append(f"  ✗ agent-unknown               rc={nobody.returncode} {nobody.stderr[-160:]!r}")

    # --- the policy travels as data, to the face ----------------------------------------------
    born = call("agent", "add", "ag1")               # born at its path: it borrows the house's machine
    agent_meta = ws / "ag1" / INSTANCE
    spelled = A.spelling(env.made, "model", "max_budget_usd")   # chosen by what its adapter declares
    dry = call("agent", "run", "ag1", "--provider", spelled, "--model", "m",
               "--max-budget-usd", "0.5", "--dry-run")
    product = adapters.product_of(env.made) / "adapters"
    unmeasured = next((one.name for one in sorted(product.iterdir()) if (one / "wire.py").is_file()
                       and getattr(adapters.load(one.name, env.made), "COST", "absent") is None), "")
    refused = call("agent", "run", "ag1", "--provider", unmeasured, "--max-budget-usd", "0.5", "--dry-run")
    budgeted = shlex.join(adapters.launch(spelled, ws / "ag1", agent_meta, "x", wiring=ws,
                                          marble=agent_meta / ".sys" / "system.common.md",
                                          policy={"model": "m", "max_budget_usd": 0.5})[0])
    if (born.returncode == 0 and instance.is_instance(agent_meta)
            and dry.returncode == 0 and budgeted in dry.stdout.splitlines() and not persistence.slots(agent_meta)
            and unmeasured and refused.returncode == 2 and "budget-unmeasured" in refused.stderr
            and unmeasured in refused.stderr):
        held("the policy travels as data", "--dry-run: the line the face composes for the policy; a cap under "
             f"{unmeasured} (COST None) refuses budget-unmeasured; no run opened")
    else:
        failures.append(f"  ✗ policy as data              {born.returncode}/{dry.returncode}/{refused.returncode} "
                        f"{born.stderr[-160:]!r} {dry.stdout[-200:]!r} {refused.stderr[-160:]!r}")

    # --- list names the agents of the house ----------------------------------------------------
    listed = call("agent", "list")
    if listed.returncode == 0 and "ag1 · 0 run(s)" in listed.stdout:
        held("list names the agents", listed.stdout.strip().splitlines()[0])
    else:
        failures.append(f"  ✗ list                        rc={listed.returncode} {listed.stdout[-160:]!r}")

    # --- start without a message: the child's refusal relayed in one line, nothing launched --------
    bare_start = call("agent", "start", "ag1", *A.harnessing("true"))
    if (bare_start.returncode == 2 and "message-missing" in bare_start.stderr and bare_start.stdout == ""
            and len(bare_start.stderr.strip().splitlines()) == 1 and not persistence.slots(agent_meta)):
        held("start without a message refuses message-missing", "one line on stderr, no report, no run")
    else:
        failures.append(f"  ✗ start refusal               rc={bare_start.returncode} {bare_start.stdout!r} "
                        f"{bare_start.stderr[-200:]!r}")

    # --- upgrade is no verb of pp-agent: the usage, in one line --------------------------------------
    extra = call("agent", "upgrade")
    if (extra.returncode == 2 and "usage" in extra.stderr.lower() and extra.stdout == ""
            and len(extra.stderr.strip().splitlines()) == 1):
        held("upgrade is no verb: the usage", "one line on stderr, exit 2, nothing touched -- the house's `./pp upgrade` reaches its agents")
    else:
        failures.append(f"  ✗ upgrade usage               rc={extra.returncode} {extra.stdout!r} "
                        f"{extra.stderr[-200:]!r}")

    # --- prune wants the agent and the run's key: without the key, the usage in one line ---------------
    bare_prune = call("agent", "prune", "ag1")
    if (bare_prune.returncode == 2 and "usage" in bare_prune.stderr.lower() and bare_prune.stdout == ""
            and len(bare_prune.stderr.strip().splitlines()) == 1):
        held("prune without a key says the usage", "one line on stderr, exit 2, nothing touched")
    else:
        failures.append(f"  ✗ prune usage                 rc={bare_prune.returncode} {bare_prune.stdout!r} "
                        f"{bare_prune.stderr[-200:]!r}")

    # --- purge wants a key or a date: without either, the usage in one line, which names the verb --------
    bare_purge = call("agent", "purge", "ag1")
    if (bare_purge.returncode == 2 and "usage" in bare_purge.stderr.lower() and "purge <path>" in bare_purge.stderr
            and bare_purge.stdout == "" and len(bare_purge.stderr.strip().splitlines()) == 1):
        held("purge without a key nor a date says the usage", "one line on stderr naming `purge`, exit 2, nothing touched")
    else:
        failures.append(f"  ✗ purge usage                 rc={bare_purge.returncode} {bare_purge.stdout!r} "
                        f"{bare_purge.stderr[-200:]!r}")
    return 0
