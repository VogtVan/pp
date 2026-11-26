"""Scenario `launcher/relayed` -- 3 case(s) (plan moteur-0.2.0, phase le-banc-de-conduction, batch
la-campagne-au-banc, 2026-10-27): the six patterns of the engine played under the modelled LLM, the house
conducting -- one launch per output pp holds for it, every block never served held, the values included:
- six exchanges on a throwaway house, every one parked at cost 0, no hole, no refusal; the coverage
  written (`coverage.json`, `COVERAGE.md`) with one line per exchange; the play writes no setting at
  the agent: its effort stands as seeded, no retired key at its SETTINGS
- the zones each root crosses are in the table: READ_LINES its door; LAPS its door, its laps, its
  proofs and the values judged; CYCLE its laps; ROUTE its successor (`next`); BEGIN its proof; REVIEW
  the door opened during the WORK -- and the house's conduction: `held-output` wherever an exchange
  took more than one launch, the principal's `advance` everywhere, `inline` on none of them: no root
  replays a block (a repair), and a lap of LAPS or CYCLE is a block never served, held
- the intention of the model plays: ROUTE's PICK is judged on LEFT, LAPS's field answers three
  elements, REVIEW's door is opened (the trace says `routed`); the measure (KM28) per root printed
"""
from __future__ import annotations

import json

from tests.harness import support

C = support(__file__, "conduction")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    done, coverage, folder, house = C.played(bench, *C.PATTERNS)
    found = C.exchanges_of(coverage)
    names = [f"{root}-relayed" for root in C.ROOTS]
    effort = C.setting_of(house, "agents/pat", "conduction_effort")
    retired = [key for key in C.RETIRED if C.setting_of(house, "agents/pat", key)]
    if done.returncode == 0 and set(found) == set(names) and C.all_parked(coverage) \
            and (folder / "COVERAGE.md").is_file() and effort == C.SEEDS["conduction_effort"] and not retired:
        held("six exchanges relayed, all parked", f"rc 0, {len(found)} exchanges at cost 0, no hole, no "
             f"refusal; {sum(one['launches'] for one in found.values())} launches, "
             f"{round(sum(one['seconds'] for one in found.values()), 1)} s; coverage written under {folder.name}; "
             f"the agent's effort as seeded ({effort}), no retired key at its SETTINGS")
    else:
        failures.append(f"  ✗ relayed                    rc={done.returncode} {sorted(found)} effort={effort!r} "
                        f"retired={retired} {done.stderr[-300:]!r} {done.stdout[-300:]!r}")
    missing = {root: C.crossed(found.get(f"{root}-relayed", {}), C.ZONES[root]) for root in C.ROOTS}
    no_hold = [name for name, one in found.items() if one["launches"] > 1 and not one["zones"].get("held-output")]
    no_advance = [name for name, one in found.items() if not one["zones"].get("advance")]
    inline = [name for name, one in found.items() if one["zones"].get("inline")]
    if not any(missing.values()) and not no_hold and not no_advance and not inline:
        held("the zones of each root, and the house's", "every root crosses its zones; held-output on every "
             "exchange of more than one launch, advance everywhere, inline nowhere; never crossed: "
             + ", ".join(coverage.get("never", [])))
    else:
        failures.append(f"  ✗ the zones                  missing={missing} no_hold={no_hold} no_advance={no_advance} "
                        f"inline={inline}")

    def answers(name: str, keyword: str) -> list[str]:
        path = folder / name / "trace.jsonl"
        if not path.is_file():
            return []
        return [str(json.loads(line).get("given")) for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip() and json.loads(line).get("kind") == "answer"
                and str(json.loads(line).get("instruction", "")).startswith(keyword)]

    picked = answers("route-relayed", "NEXT")
    field = answers("laps-relayed", "FIELD")
    elements = json.loads(field[0]) if field else []
    if (picked == ["LEFT.md"] and isinstance(elements, list) and len(elements) == 3
            and found.get("review-relayed", {}).get("zones", {}).get("door")):
        held("the intention of the model plays", "ROUTE picked LEFT, LAPS answered three elements, REVIEW opened "
             "its door; the measure: " + "; ".join(f"{root} {found[f'{root}-relayed']['launches']} launch(es) "
                                                    f"{found[f'{root}-relayed']['seconds']} s" for root in C.ROOTS
                                                    if f"{root}-relayed" in found))
    else:
        failures.append(f"  ✗ the intention              picked={picked} field={field} "
                        f"review={found.get('review-relayed', {}).get('zones')}")
    return 0
