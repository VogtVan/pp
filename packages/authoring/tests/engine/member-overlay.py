"""Scenario `member-overlay` -- 2 case(s):
- PP-MEMBER served bare carries no word of federation: the door is generic
- an overlay on PP-MEMBER (here the instance's own) appends its section at the end of the
  served body -- the anchor a package like federation uses to hand its prose back
"""
from __future__ import annotations

import re

from conductor import render
from tests.harness import SOURCE, kept_document

FEDERAL = re.compile(r"federat|confederat|admin|sibling", re.I)


def _opened(env) -> str:
    """-> the door's own brief as the block renders it: the NEXT INSTRUCTION CONTEXT section
    alone (the cheatsheet served beside it quotes block marks of its own)."""
    conductor = env.conductor()
    conductor.start(conductor.boot("BOOT.md"))
    conductor.submit("")
    text = render(conductor.play("PP-MEMBER"))
    conductor.forget()
    marker = "▌ NEXT INSTRUCTION CONTEXT — PP-MEMBER"
    return marker + text.split(marker, 1)[1].split("\n▌ ", 1)[0] if marker in text else ""


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("member-bare", packages=("authoring",))
    bare = _opened(env)
    text = kept_document(SOURCE / "packages" / "authoring", "PP-MEMBER").read_text(encoding="utf-8")
    last_heading = [line[3:] for line in text.splitlines() if line.startswith("## ")][-1]   # read at run time
    if "NEXT INSTRUCTION CONTEXT — PP-MEMBER" in bare and last_heading in bare \
            and not FEDERAL.search(bare):
        held("PP-MEMBER served bare is generic", "the door's body reaches the block without a "
             "word of federation")
    else:
        failures.append(f"  ✗ member bare                {FEDERAL.findall(bare)[:4]} {bare[:120]!r}")

    (env.made / "procs").mkdir(exist_ok=True)
    (env.made / "procs" / "PP-MEMBER.md").write_text(
        "---\nname: PP-MEMBER\n---\n\n## The confederation -- handed back by an overlay\n\n"
        "When sibling members stand, the admin is determined here.\n", encoding="utf-8")
    body = _opened(env)
    if ("handed back by an overlay" in body
            and body.index(last_heading) < body.index("handed back by an overlay")
            and "sibling members" in body):
        held("an overlay appends its section at the end", "the instance's overlay on PP-MEMBER "
             "rides after the base body -- federation's anchor")
    else:
        failures.append(f"  ✗ member overlay             {body[-300:]!r}")
    return 0
