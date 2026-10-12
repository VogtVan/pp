"""Scenario `agent-grammar` -- 4 case(s) (batch la-grammaire-par-defaut, 2026-10-11): the grammar a `--harness`
command's output is read in is always named by the caller -- `--provider` beside it; `pp-agent` names no provider.
- `run --harness <witness>` without `--provider` refuses `grammar-missing`, exit 2: no run opened, no record
- `chat --harness <witness>` without `--provider` refuses before any message is read: no run opened, no record
- `start --harness <witness>` without `--provider`: the child's refusal relayed, no run opened, no record
- the same `run` with `--provider <the witness's grammar>` plays: the response kept, the run parked
"""
from __future__ import annotations

from tests.harness import support

A = support(__file__, "agent")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)

    # --- run: a --harness alone refuses ---------------------------------------------------------------
    alone = h.call("agent", "run", "agents/ag1", "--message", "read me", "--harness", h.harness("play"))
    if alone.returncode == 2 and "grammar-missing" in alone.stderr and h.keys() == [] and h.counted() == (0, 0, 0):
        bench.refusals += 1
        held("run: a --harness without --provider refuses", "grammar-missing, exit 2, no run opened, no record")
    else:
        failures.append(f"  ✗ run grammar-missing         rc={alone.returncode} keys={h.keys()} records={h.counted()} "
                        f"{alone.stderr[-300:]!r}")

    # --- chat: refused before any message -------------------------------------------------------------
    talked = h.call("agent", "chat", "agents/ag1", "--harness", h.harness("play"), stdin="hi\n")
    if talked.returncode == 2 and "grammar-missing" in talked.stderr and h.keys() == [] and h.counted() == (0, 0, 0):
        bench.refusals += 1
        held("chat: a --harness without --provider refuses", "grammar-missing before any message, nothing opened")
    else:
        failures.append(f"  ✗ chat grammar-missing        rc={talked.returncode} keys={h.keys()} records={h.counted()} "
                        f"{talked.stderr[-300:]!r}")

    # --- start: the child's refusal relayed -----------------------------------------------------------
    started = h.call("agent", "start", "agents/ag1", "--message", "read me", "--harness", h.harness("play"))
    if (started.returncode == 2 and "grammar-missing" in started.stderr and started.stdout.strip() == ""
            and h.keys() == [] and h.counted() == (0, 0, 0)):
        bench.refusals += 1
        held("start: the refusal relayed", "grammar-missing on stderr, no report, nothing opened")
    else:
        failures.append(f"  ✗ start grammar-missing       rc={started.returncode} out={started.stdout[-120:]!r} "
                        f"keys={h.keys()} records={h.counted()} {started.stderr[-300:]!r}")

    # --- the grammar named: the exchange plays ---------------------------------------------------------
    named = h.wake("read me")
    kept = h.responses()
    if (named.returncode == 0 and len(h.keys()) == 1 and len(kept) == 1
            and kept[0].get("response") == "witness answer: play"):
        held("the grammar named beside the harness plays", f"run {h.keys()[0]}: the witness's answer kept, read in "
             f"the grammar its support declares")
    else:
        failures.append(f"  ✗ grammar named               rc={named.returncode} keys={h.keys()} "
                        f"responses={[one.get('response') for one in kept]} {named.stderr[-300:]!r}")
    return 0
