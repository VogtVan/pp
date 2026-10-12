"""Scenario `ui-real-agents-stats` -- the Agents tab on the REAL faces of `agent` (plan ui, batch
le-reel-du-poste-recadre; cut from `ui-real-agents` by le-poids-et-la-purge, rule 10), a real run of two exchanges
made first at the post, the model set to `m2` between them:
- `s` stacks the statistics of the real run: blocks and mass from the engine's `-stats`
- `n` opens the overlay of a new run prefilled with what the agent last played: the model `m2`
"""
from __future__ import annotations

import re

from tests.harness import support

R = support(__file__, "real")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = R.RealPost(bench, "ui-real-agents-stats")
    made = post.talk()
    runs = post.status_json()
    if made.returncode != 0 or len(runs) != 1 or len(post.responses()) != 2:
        failures.append(f"  ✗ real run                    rc={made.returncode} runs={runs} {made.stderr[-300:]!r}")
        return 0

    # --- s: the statistics of the real run ------------------------------------------------------------
    measured = post.render("--render", "dialogue", "--size", "120x40", "--press", "2,down,enter,s", "--wait", "waiting:2")
    blocks, mass = re.search(r"blocks\s+(\d+)", measured.stdout), re.search(r"mass\s+(\d+)", measured.stdout)
    if measured.returncode == 0 and blocks and int(blocks.group(1)) >= 1 and mass and int(mass.group(1)) >= 1:
        held("s reads the real statistics", f"blocks {blocks.group(1)}, mass {mass.group(1)} from -stats")
    else:
        failures.append(f"  ✗ real stats                  {measured.stdout!r} {measured.stderr[-300:]!r}")

    # --- n: the overlay of a new run, prefilled with what the agent last played ------------------------
    last = post.last_policy()
    fresh = post.render("--render", "agents", "--size", "120x40", "--press", "down,n", "--wait", "none:1.5")
    if (fresh.returncode == 0 and (last.get("policy") or {}).get("model") == "m2" and "a new run of" in fresh.stdout
            and "m2" in fresh.stdout):
        held("n opens the overlay with the last real policy", f"status --json last {last}; the overlay says m2")
    else:
        failures.append(f"  ✗ real n                      last={last} {fresh.stdout!r} {fresh.stderr[-300:]!r}")
    return 0
