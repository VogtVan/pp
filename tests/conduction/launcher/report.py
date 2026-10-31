"""Scenario `launcher/report` -- 3 case(s) (plan moteur-0.2.0, phase le-banc-de-conduction, batches
la-campagne-au-banc and le-mode-reel, 2026-10-27/28; split from `launcher/plan` at le-secteur-conduction,
2026-10-29): the operator's bench and the report of the campaign's launcher, WITHOUT a real harness:
- (e) `prepare --root read-lines` builds ONE house on a throwaway path: the agent's cap at the host's,
  the kit's turn with `READ_LINES` offered to the WORK, `LINES.txt` laid, the run sheet written; a second
  `prepare` says `standing`
- (f) `runsheet` renders fourteen sections, one per root, each naming its house, its message and the two gestures
- (h) the REPORT of a campaign played under `model --repeat 2` on two roots (laps, review): four exchanges,
  `<name>#<k>` each, all parked; the bound said before the first launch and the cost after, both 0 USD;
  the report's means and p90 equal to the values of two identical repetitions; `report <date>` replays
  `coverage.json` and `report.json` byte for byte; the model wires nothing (no `.claude` at the agent)
"""
from __future__ import annotations

import json
import os
import re
import shutil

import yaml

from tests.harness import SOURCE, cli, support

C = support(__file__, "conduction")
KEY = re.compile(r"run ([0-9a-f]{6})")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- (e) the operator's bench: one house prepared ----------------------------------------------------------
    houses = bench.temp() / "houses"
    built = C.launcher("prepare", "--root", "read-lines", "--out", str(houses))
    again = C.launcher("prepare", "--root", "read-lines", "--out", str(houses))
    house = houses / "read-lines"
    agent = house / "agents" / "pat"
    settings = agent / ".pp" / "SETTINGS.md"
    capped = "max_harness_tool_output: 25000" in settings.read_text(encoding="utf-8") if settings.is_file() else False
    turn = agent / ".pp" / "procs" / "TURN.md"
    offered = "+READ_LINES" in turn.read_text(encoding="utf-8") if turn.is_file() else False
    if (built.returncode == 0 and "built" in built.stdout and again.returncode == 0 and "standing" in again.stdout
            and (agent / "LINES.txt").is_file() and (agent / ".pp" / "procs" / "READ_LINES.md").is_file()
            and (houses / "RUNSHEET.md").is_file() and capped and offered):
        held("(e) one house of the operator's bench", "prepared under a throwaway path, standing at the second "
             "call; the agent's cap at the host's, the turn with READ_LINES offered, LINES.txt laid, the run sheet written")
    else:
        failures.append(f"  ✗ (e) the house               rc={built.returncode}/{again.returncode} capped={capped} "
                        f"offered={offered} {built.stdout[-160:]!r} {built.stderr[-200:]!r}")

    # --- (f) the run sheet ---------------------------------------------------------------------------------------
    said = C.launcher("runsheet", "--out", str(houses))
    sections = [line for line in said.stdout.splitlines() if line.startswith("## ")]
    roots = len(C.ROOTS) + len(C.SITUATIONS)
    if (said.returncode == 0 and len(sections) == roots and said.stdout.count("- editor:") == roots
            and said.stdout.count("- post:") == roots and said.stdout.count("- message:") == roots):
        held("(f) the run sheet", f"{roots} sections, each with its house, its message, the editor and the post gestures")
    else:
        failures.append(f"  ✗ (f) the run sheet           rc={said.returncode} sections={len(sections)}")

    # --- (h) the report of a campaign under the model, repeated twice ------------------------------------------
    done, coverage, folder, house = C.played(bench, "--root", "laps", "--root", "review", "--channel", C.RELAYED,
                                             "--conduction", C.STRICT, "--repeat", "2")
    found = C.exchanges_of(coverage)
    names = {f"{root}-relayed-strict#{k}" for root in ("laps", "review") for k in (1, 2)}
    said = done.stdout.splitlines()
    before = (folder / "coverage.json").read_bytes() if (folder / "coverage.json").is_file() else b""
    first = C.report_of(folder)
    reported = C.launcher("report", folder.name, "--out", str(folder.parent))
    again = C.launcher("report", folder.name, "--out", str(folder.parent))
    report = C.report_of(folder)
    after = (folder / "coverage.json").read_bytes() if (folder / "coverage.json").is_file() else b""
    lines = report.get("exchanges", [])
    groups = report.get("aggregates", [])
    steady = all(one["cost_usd"]["mean"] == 0 and one["launches"]["p90"] == one["launches"]["mean"]
                 and one["n"] == 2 and one["parked"] == 2 for one in groups)
    launches = {(one["root"], one["repetition"]): one["launches"] for one in lines}
    same = all(launches.get((root, 1)) == launches.get((root, 2)) for root in ("laps", "review"))
    if (done.returncode == 0 and set(found) == names and C.all_parked(coverage)
            and said and "0 USD" in said[0] and "0 USD" in said[-1]
            and reported.returncode == 0 and again.returncode == 0 and (folder / "REPORT.md").is_file()
            and len(lines) == 4 and len(groups) == 2 and steady and same and first == report
            and before and before == after and not (house / "agents" / "pat" / ".claude").exists()):
        held("(h) the report of a repeated campaign", f"4 exchanges `<name>#<k>` parked at cost 0, the bound and the "
             f"cost said 0 USD; report.json 4 lines, 2 aggregates with mean = value and p90 = mean; coverage.json "
             f"rewritten byte for byte, a second report identical; nothing wired under the model; "
             + "; ".join(f"{root} {launches.get((root, 1))} launch(es)" for root in ("laps", "review")))
    else:
        failures.append(f"  ✗ (h) the report              rc={done.returncode}/{reported.returncode} {sorted(found)} "
                        f"lines={len(lines)} groups={len(groups)} steady={steady} same={same} "
                        f"bytes={before == after} {done.stderr[-200:]!r} {reported.stderr[-200:]!r}")
    return 0
