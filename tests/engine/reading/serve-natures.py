"""Scenario `serve-natures` -- 1 case(s), in the monolith's order:
- the nature is a DECLARATION: a natured line serves like a bare one, titled by its token --
  no regime holds a row (les-cles-mortes, 2026-09-05: `document_serve` is gone)
"""
from __future__ import annotations

from conductor import Conductor, discovery
from tests.harness import document


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- the nature is a DECLARATION: both lines serve, each under its own token
    natured_home = bench.town(["natured"]).siblings
    natured_member = discovery.member(natured_home, "natured")
    script = natured_member.meta / ".sys" / "engine" / "pp.py"
    (natured_member.meta / "REF.md").write_text("ref\n", encoding="utf-8")
    (natured_member.meta / "CODE.md").write_text("code\n", encoding="utf-8")
    natured_doc = document("---\nname: X\nserve: |\n  reference: REF.md\n  code: CODE.md\nproc: |\n"
                           "  SERVE\n  INFER\n---\n", at=natured_member.meta)
    natured_c = Conductor(natured_member, natured_home, script, "t")
    natured_c.forget()
    natured_block = natured_c.start(natured_doc)
    served = dict(natured_block.payloads)
    if [n for n, _ in natured_block.payloads] == ["REF.md", "CODE.md"] \
            and served["REF.md"].strip() == "ref" and served["CODE.md"].strip() == "code":
        held("the nature is a declaration", "reference: and code: both serve, titled by their "
             "token -- a nature says what a reading is, it never holds one back")
    else:
        failures.append(f"  ✗ nature declares           {natured_block.payloads}")
    natured_c.forget()
    return 0
