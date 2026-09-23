"""Scenario `ranged-serve` -- 1 case(s):
- le-serve-par-lignes: a ranged token serves its lines, one grammar

Migrated from the improvement package (batch le-reflexe-et-son-sink): the
grammar of a serve token is the ENGINE's, and no policy owns it.
"""
from __future__ import annotations

from conductor import Refusal, reading


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    made = bench.env("rngw").made
    ranged_doc = made / "notes-banc.py"
    ranged_doc.write_text("ligne un\nligne deux\nligne trois\nligne quatre\nligne cinq\n",
                          encoding="utf-8")
    bare = reading.ranged("procs/TURN.md")
    named, cut = reading.ranged("notes-banc.py[2-3,5-9]")
    sliced_text, sliced_hash = reading.sliced(ranged_doc, cut)
    same_text, same_hash = reading.sliced(ranged_doc, cut)
    torn = []
    for bad in ("d.md[3-2]", "d.md[0-4]", "d.md[2-5,4-9]", "d.md[9-12,2-4]", "d.md[a-b]"):
        try:
            reading.ranged(bad)
        except Refusal as refusal:
            torn.append(refusal.code)
    if (bare == ("procs/TURN.md", ()) and named == "notes-banc.py"
            and cut == ((2, 3), (5, 9))
            and sliced_text == "ligne deux\nligne trois\nligne cinq\n"
            and sliced_text == same_text and sliced_hash == same_hash and len(sliced_hash) == 6
            and torn == ["serve-range-malformed"] * 5):
        held("a ranged token serves its lines", "the writer's grammar verbatim, the selection "
             "hashed, a bound past the end serves what stands, a bare token untouched -- and "
             "no EOS hold on a code file")
    else:
        failures.append(f"  ✗ ranged serve              {bare}/{named}/{cut}/{sliced_text!r}/{torn}")
    ranged_doc.unlink()
    return 0
