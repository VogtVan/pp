"""Scenario `proof-coverage` -- 5 case(s) (batch les-codes-non-nommes-refuses, 2026-10-04): every code
the proof line asks has an object in the proof; a code left unnamed is a named deviation.
- (a) three laws of production asked, a proof of two objects: REPAIR 1, the DEVIATION names the third
- (b) the proof of three objects passes: the FINAL renders
- (c) a behavior code named in addition does not deviate
- (d) the mini-proof over a repaired code passes without naming the others
- (e) nineteen laws of production asked (the p90 of the corpus): the complete proof passes, and the
  mass of the objects it adds over a proof leaving three unnamed is said
"""
from __future__ import annotations

import json

from conductor import Conductor, discovery, render
from tests.harness import document


def _doc(codes: list[str]) -> str:
    laws = "".join(f"  {code}  the law {code} holds\n" for code in codes)
    return ("---\nname: COVERED\nkind: proc\ndescription: a proven exchange\ncycle: true\n"
            f"constraints.production: |\n{laws}constraints.behavior: |\n  B9  speak plainly\n"
            "proc: |\n  INFER\n  FINAL\n---\nanswer the ask\n")


def _proof(codes: list[str], verdict: str = "n/a") -> str:
    return json.dumps([{"code": code, "evidence": "no bearing on this production", "verdict": verdict}
                       for code in codes])


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    home = discovery.member(bench.town(["coverer"]).siblings, "coverer")
    script = bench.town(["engine"])["engine"].engine

    def conductor() -> Conductor:
        return Conductor(home, script, "t")

    three = ["Z1", "Z2", "Z3"]
    doc = document(_doc(three), at=home.meta)

    # --- (a) a code left unnamed deviates, named --------------------------------------------------
    conductor().start(doc)
    asked = conductor().submit("")
    holed = conductor().submit(_proof(["Z1", "Z2"]))
    if (asked is not None and list(asked.judged) == three and holed is not None and holed.repair == 1
            and "Z3" in (holed.deviation or "") and "unnamed" in (holed.deviation or "")):
        held("(a) a code left unnamed deviates", f"the line asks {list(asked.judged)}, the proof names two: "
             f"REPAIR 1, the DEVIATION says `{holed.deviation}`")
    else:
        failures.append(f"  ✗ (a) the unnamed code        judged={asked and list(asked.judged)} "
                        f"repair={holed and holed.repair} {(holed.deviation if holed else '')!r}")
    conductor().forget()

    # --- (b) the complete proof passes ------------------------------------------------------------
    conductor().start(doc)
    conductor().submit("")
    whole = conductor().submit(_proof(three))
    if whole is not None and whole.wait and not whole.repair and not whole.deviation:
        held("(b) the complete proof passes", "three objects for three codes asked: the FINAL renders")
    else:
        failures.append(f"  ✗ (b) the complete proof      wait={whole and whole.wait} {(whole.deviation if whole else '')!r}")
    conductor().forget()

    # --- (c) a behavior code named in addition does not deviate -------------------------------------
    conductor().start(doc)
    conductor().submit("")
    extra = conductor().submit(_proof(three + ["B9"]))
    if extra is not None and extra.wait and not extra.deviation:
        held("(c) a behavior code in addition passes", "B9 named beside Z1-Z3: no deviation, the FINAL renders")
    else:
        failures.append(f"  ✗ (c) the behavior code       wait={extra and extra.wait} {(extra.deviation if extra else '')!r}")
    conductor().forget()

    # --- (d) the mini-proof names the repaired code alone -------------------------------------------
    conductor().start(doc)
    conductor().submit("")
    fixing = json.dumps([{"code": "Z1", "evidence": "a claim unrendered", "verdict": "fail", "fix": "render it"},
                         {"code": "Z2", "evidence": "held", "verdict": "ok"},
                         {"code": "Z3", "evidence": "no bearing", "verdict": "n/a"}])
    placed = conductor().submit(fixing)
    mini = conductor().submit(json.dumps([{"code": "Z1", "evidence": "rendered: grep -c 1", "verdict": "ok"}]))
    if (placed is not None and "IN PLACE" in (placed.deviation or "") and mini is not None and mini.wait
            and not mini.deviation):
        held("(d) the mini-proof covers the repaired code alone", "Z1 fixed in place, its mini-proof names Z1 "
             "alone: the FINAL renders")
    else:
        failures.append(f"  ✗ (d) the mini-proof          {(placed.deviation if placed else '')!r} "
                        f"wait={mini and mini.wait} {(mini.deviation if mini else '')!r}")
    conductor().forget()

    # --- (e) nineteen codes: the complete proof passes, its added mass said --------------------------
    many = [f"Y{n}" for n in range(1, 20)]
    big = document(_doc(many), at=home.meta)
    conductor().start(big)
    conductor().submit("")
    full_proof, short_proof = _proof(many), _proof(many[:16])
    passed = conductor().submit(full_proof)
    added = len(full_proof) - len(short_proof)
    if passed is not None and passed.wait and not passed.deviation:
        held("(e) nineteen codes, the complete proof passes", f"19 objects, {len(full_proof)} c; a proof leaving "
             f"three unnamed would be {len(short_proof)} c: the three explicit n/a cost {added} c "
             f"({added // 3} c an object)")
    else:
        failures.append(f"  ✗ (e) nineteen codes          wait={passed and passed.wait} {(passed.deviation if passed else '')!r}")
    conductor().forget()
    return len(failures)
