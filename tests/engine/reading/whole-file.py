"""Scenario `whole-file` -- 1 case(s) (plan pp-split, phase le-noyau-generique, batch
la-fin-du-marqueur):
- a row without a range serves ANY text file whole -- code included -- and the hash proves
  what was served; the one refusal `served()` keeps is `document-missing` (a row on a gone
  document degrades softly -- mount.py)
"""
from __future__ import annotations

from conductor import Conductor, discovery, reading
from tests.harness import document


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures

    whole_siblings = bench.town(["whole"]).siblings
    whole_member = discovery.member(whole_siblings, "whole")
    script = whole_member.meta / ".sys" / "engine" / "pp.py"
    code = "def served_whole():\n    return 1\n\n\nclass Bare:\n    pass\n"
    (whole_member.meta / "TOOL.py").write_text(code, encoding="utf-8")
    whole_doc = document("---\nname: X\nserve: |\n  code: TOOL.py\nproc: |\n  SERVE\n  INFER\n---\n",
                         at=whole_member.meta)
    whole_c = Conductor(whole_member, whole_siblings, script, "t")
    whole_c.forget()
    block = whole_c.start(whole_doc)
    served = dict(block.payloads).get("TOOL.py", "")
    whole_hash = reading.served(whole_member.meta / "TOOL.py")[1]
    sliced_hash = reading.sliced(whole_member.meta / "TOOL.py", ((1, 2),))[1]
    if served.strip() == code.strip() and whole_hash != sliced_hash:
        held("a text file serves whole", "a code file named without a range rides entire, "
             "its hash taken on what was served -- the slice hashes otherwise")
    else:
        failures.append(f"  ✗ whole file                 {block.command!r} {served[-60:]!r}")

    expect("document-missing", lambda: reading.served(whole_member.meta / "NOWHERE.md"))
    return 0
