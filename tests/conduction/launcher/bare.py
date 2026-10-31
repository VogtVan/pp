"""Scenario `launcher/bare` -- 3 case(s) (plan moteur-0.2.0, phase le-banc-de-conduction, batch
la-campagne-au-banc, 2026-10-27): the six patterns of the engine played under the modelled LLM on the
BARE channel -- the harness launched by hand on the agent's workspace, the model calls pp itself
(`./pp -new` under `PP_DOCUMENTS` and `PP_DOOR`), one launch for the whole exchange:
- six exchanges on a throwaway house, every one parked at cost 0, one launch each, no hole, no
  refusal; the harness's lines kept (`harness.jsonl`), the coverage written
- the zones each root crosses are in the table, and the channel's own: no `held-output`, no
  `advance` (nobody conducts but the model), the boot cut under the host's cap (`chunk`) and served
  by the model's own bare calls, the bare call where BEGIN's words precede the WORK's
- the model's first call is `./pp -new` on every exchange, and the run it opened is the one the
  coverage names
"""
from __future__ import annotations

import json

from tests.harness import support

C = support(__file__, "conduction")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    done, coverage, folder, _house = C.played(bench, *C.PATTERNS, "--channel", C.BARE)
    found = C.exchanges_of(coverage)
    names = [f"{root}-bare" for root in C.ROOTS]
    if (done.returncode == 0 and set(found) == set(names) and C.all_parked(coverage)
            and all(one["launches"] == 1 for one in found.values())
            and all((folder / name / "harness.jsonl").is_file() for name in names)):
        held("six exchanges bare, all parked", f"rc 0, {len(found)} exchanges at cost 0, one launch each, no hole, "
             f"no refusal; {round(sum(one['seconds'] for one in found.values()), 1)} s; harness.jsonl kept")
    else:
        failures.append(f"  ✗ bare                       rc={done.returncode} {sorted(found)} "
                        f"{done.stderr[-300:]!r} {done.stdout[-300:]!r}")
    missing = {root: C.crossed(found.get(f"{root}-bare", {}), C.ZONES[root]) for root in C.ROOTS}
    conducted = [name for name, one in found.items() if one["zones"].get("held-output") or one["zones"].get("advance")]
    no_chunk = [name for name, one in found.items() if not one["zones"].get("chunk")]
    begin = found.get("begin-bare", {}).get("zones", {}).get("bare-call")
    if not any(missing.values()) and not conducted and not no_chunk and begin:
        held("the zones of each root, and the channel's", "every root crosses its zones; no held-output, no "
             "advance; the boot cut in chunks everywhere, BEGIN's bare call; never crossed: "
             + ", ".join(coverage.get("never", [])))
    else:
        failures.append(f"  ✗ the zones                  missing={missing} conducted={conducted} no_chunk={no_chunk} "
                        f"begin={begin}")

    def first_call(name: str) -> str:
        path = folder / name / "harness.jsonl"
        if not path.is_file():
            return ""
        for line in path.read_text(encoding="utf-8").splitlines():
            one = json.loads(line)
            if one.get("kind") == "tool":
                return str(one.get("shell") or "")
        return ""

    firsts = {name: first_call(name) for name in names}
    if all(one.endswith("pp -new") for one in firsts.values()) and all(found[name]["run"] for name in names):
        held("the model opens the run itself", "`./pp -new` the first call of every exchange, the run opened named "
             "by the coverage: " + ", ".join(f"{name} {found[name]['run']}" for name in names))
    else:
        failures.append(f"  ✗ the opening                {firsts} {[found[n]['run'] for n in names]}")
    return 0
