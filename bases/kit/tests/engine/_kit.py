"""Support module of `bases/kit/tests/engine/` (rule 10): what the kit hosts share -- the
kit's boot played up to its first step, a run driven to its frontier. Never collected; a
host loads it by `support(__file__, "kit")`.
"""
from __future__ import annotations

from conductor import render
from tests.harness import na_proof


def boot(env) -> list:
    """-> every output of the kit's boot up to its first step, in order -- a long boot
    reading rides CONTINUEs first, a fused boot may arrive in pieces; the last output is
    the landed step."""
    opener = env.conductor("t")
    seen = [opener.resume(opener.boot("BOOT.md"))]
    for _ in range(6):
        if seen[-1].command:
            break
        seen.append(env.conductor("t").resume(env.conductor("t").boot("BOOT.md")))
    return seen


def drive(env, opening, cap: int = 8) -> list:
    """-> the blocks from `opening` to the frontier: a production is said in the chat (a
    bare submit), a checkpoint takes the bench's n/a proof."""
    seen = [opening]
    while seen[-1] is not None and "▶ FINAL" not in render(seen[-1]) and len(seen) < cap:
        last = seen[-1]
        seen.append(env.conductor("t").submit(na_proof(last) if "INFER proof" in render(last) else ""))
    return [one for one in seen if one is not None]
