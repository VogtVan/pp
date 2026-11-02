"""Scenario `call` -- the pattern `composition/call`, played from its demonstration:
- the callee's body comes first, as the context of its step; the caller's body rides as information
- the callee's laws stand over the caller's while its frame lives, and fall with it
- the heading says the path while the callee plays, the caller alone once it returns
- a CALL to a document that resolves nowhere refuses by name, nothing played
"""
from __future__ import annotations

from conductor import persistence, render
from tests.harness import codes, demonstrated, plant, titles

DEMOS = ("GATE.md", "LOST.md", "REVIEW.md")


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("call", bare=True)
    found = demonstrated("composition", "call")
    if found != sorted(DEMOS):
        failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    plant(env, "composition", "call", DEMOS)

    def key() -> str:
        return persistence.run_id_of(env.session())

    # --- the body first, then the frame --------------------------------------------------
    opener = env.conductor()
    opener.forget()
    entered = opener.start(opener.boot("GATE.md"))
    shown = titles(render(entered)) if entered is not None else []
    caller_info, callee_brief = "▌ INFORMATION — GATE", "▌ NEXT INSTRUCTION CONTEXT — REVIEW"
    if (entered is not None and entered.document == "REVIEW"
            and entered.instruction.keyword == "INFER"
            and caller_info in shown and callee_brief in shown
            and shown.index(caller_info) < shown.index(callee_brief)):
        held("the callee's body first", "REVIEW's body is the context of its step, GATE's body "
             "rides above it as information")
    else:
        failures.append(f"  ✗ body first                  {entered and entered.document!r} {shown!r}")

    # --- the laws stand over the caller's, the heading says the path ---------------------
    if (entered is not None and {"G1", "R1"} <= set(codes(entered))
            and entered.stack.startswith("GATE ▸ REVIEW{1/1}")):
        held("the callee's laws stand over the caller's", f"{codes(entered)} in force while "
             f"REVIEW plays, the heading `{entered.stack}`")
    else:
        failures.append(f"  ✗ laws and path in the callee {codes(entered)} {entered and entered.stack!r}")

    # --- the callee returns: its laws fall, the caller resumes ---------------------------
    back = env.conductor(key()).forward("")
    if (back is not None and back.document == "GATE" and back.instruction.keyword == "INFER"
            and "G1" in codes(back) and "R1" not in codes(back)
            and back.stack.startswith("GATE{2/2}")):
        held("the callee's laws fall with its frame", f"back at GATE: {codes(back)}, "
             f"the heading `{back.stack}`")
    else:
        failures.append(f"  ✗ the return                  {back and back.document!r} {codes(back)} "
                        f"{back and back.stack!r}")
    env.conductor(key()).forget()

    # --- a CALL that resolves nowhere refuses by name ------------------------------------
    lost = env.conductor()
    lost.forget()
    expect("document-missing", lambda: lost.start(lost.boot("LOST.md")))
    return 0
