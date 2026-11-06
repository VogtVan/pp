"""Scenario `launcher/hybrid-launches` -- 1 case (plan moteur-0.2.0, phase le-banc-de-conduction, batch
la-campagne-au-banc, 2026-10-27; split from `launcher/hybrid` at le-secteur-conduction, 2026-10-29): LAPS
under `conduction: hybrid` takes FEWER launches than under `strict` -- LAPS played hybrid on a throwaway
house, then strict on the same standing house, `exchanges.json` read on both.
"""
from __future__ import annotations

import json

from tests.harness import support

C = support(__file__, "conduction")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    done, _coverage, folder, house = C.played(bench, "--root", "laps", "--channel", C.RELAYED, "--conduction", C.HYBRID)
    out = folder.parent
    again = C.launcher("play", "--provider", C.PROVIDER, "--out", str(out), "--house", str(house),
                       "--root", "laps", "--channel", C.RELAYED, "--conduction", C.STRICT)
    folders = sorted(one for one in out.iterdir() if one.is_dir())
    strict_folder = folders[-1] / "laps-relayed-strict"

    def launches_of(path):
        if not path.is_file():
            return None
        lines = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        return lines[-1].get("launches") if lines else None

    strict = launches_of(strict_folder / "exchanges.json")
    hybrid = launches_of(folder / "laps-relayed-hybrid" / "exchanges.json")
    if done.returncode == 0 and again.returncode == 0 and isinstance(strict, int) and isinstance(hybrid, int) and hybrid < strict:
        held("hybrid takes fewer launches than strict on LAPS", f"strict {strict} launches, hybrid {hybrid}, "
             "read from exchanges.json")
    else:
        failures.append(f"  ✗ laps strict/hybrid         rc={done.returncode}/{again.returncode} strict={strict} hybrid={hybrid} "
                        f"{again.stderr[-200:]!r}")
    return 0
