"""Scenario `sections` -- 3 case(s):
- a document declares its laws in two sections: production then behavior, each law
  carrying its section; a bare `constraints:` refuses by name -- the migration is a tool
- an overlay's deltas add in the section of their key and remove by code alone
- a law round-trips the wire: the section rides a routed snapshot, an older line reads
  as production
"""
from __future__ import annotations

from pathlib import Path
import tempfile

from conductor import reading
from conductor.core.model import Constraint


def _doc(text: str) -> Path:
    home = Path(tempfile.mkdtemp(prefix="pp-sections-"))
    path = home / "LAWS.md"
    path.write_text(text, encoding="utf-8")
    return path


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures

    # --- two sections, production first; the bare key still reads, as production --------
    both = reading.read(_doc(
        "---\nname: LAWS\nconstraints.production: |\n  P1  the file ends on a newline\n"
        "constraints.behavior: |\n  H1  say what you do before you do it\n"
        "  # H2  a comment stays inert\n---\nx\n"))
    laws = reading.constraints(both)
    expect("constraints-unsectioned", lambda: reading.constraints(reading.read(_doc(
        "---\nname: LAWS\nconstraints: |\n  B1  the old regime\n---\nx\n"))))
    if [(one.code, one.section) for one in laws] == [("P1", "production"), ("H1", "behavior")]:
        held("two sections, the bare key refuses", "P1 production, H1 behavior, the comment "
             "inert; a bare `constraints:` refuses `constraints-unsectioned`")
    else:
        failures.append(f"  ✗ sections read              {laws}")
    expect("constraint-malformed", lambda: reading.constraints(reading.read(_doc(
        "---\nname: LAWS\nconstraints.behavior: |\n  nocode\n---\nx\n"))))

    # --- the overlay dialect carries the section ------------------------------------------
    deltas = reading.constraint_deltas(reading.read(_doc(
        "---\nname: TURN\nconstraints.production: |\n  +Q1  a fact rendered\n"
        "constraints.behavior: |\n  -T4\n  W1  a way of doing\n---\n")))
    if deltas == [("+", "Q1", "a fact rendered", "production"), ("-", "T4", "", ""),
                  ("+", "W1", "a way of doing", "behavior")]:
        held("the overlay deltas carry their section", "+Q1 production, -T4 by code alone, "
             "W1 behavior")
    else:
        failures.append(f"  ✗ overlay deltas             {deltas}")

    # --- the wire round-trip -----------------------------------------------------------------
    law = Constraint(code="H1", text="say it", section="behavior")
    older = Constraint.parse("P9  an older snapshot line")
    if (Constraint.parse(law.wire()) == law and law.wire() == "behavior:H1  say it"
            and str(law) == "H1  say it" and older.section == "production"
            and Constraint.parse(Constraint(code="P1", text="t").wire())
            == Constraint(code="P1", text="t")):
        held("a law round-trips the wire", "the section rides the snapshot as a prefix; a "
             "bare line reads as production")
    else:
        failures.append(f"  ✗ wire                       {law.wire()!r} {older}")
    return 0
