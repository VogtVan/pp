"""Scenario `proc` -- the pattern `steps/proc`, played from its demonstration:
- a conducted document plays its `proc:` one step at a time, its body the context of its first step
- the heading counts the steps; the last one done, the passage is over
- every document that cannot be read as a procedure refuses by the code it names, nothing played
"""
from __future__ import annotations

from conductor import render
from tests.harness import demonstrated, demos, plant, titles

PLAYED = ("STEPS.md",)
REFUSING = {"BARECALL.md": "instruction-malformed", "CROWDED.md": "instruction-malformed",
            "DANCE.md": "unknown-keyword",
            "PROSE.md": "procedure-undeclared", "UNCLOSED.md": "front-matter-unterminated",
            "UNFRAMED.md": "front-matter-missing"}


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("proc", bare=True)
    found = demonstrated("steps", "proc")
    if found != sorted(PLAYED + tuple(REFUSING)):
        failures.append(f"  ✗ the demonstration           {found!r} -- owed "
                        f"{sorted(PLAYED + tuple(REFUSING))!r}")
        return 0
    plant(env, "steps", "proc", PLAYED)

    # --- one step at a time, the body first -------------------------------------------------
    opener = env.conductor()
    opener.forget()
    first = opener.start(opener.boot("STEPS.md"))
    key = opener.run_id
    second = env.conductor(key).forward("")
    if (first is not None and first.instruction.keyword == "INFER"
            and (first.position, first.total) == (1, 2) and not first.wait
            and "▌ NEXT INSTRUCTION CONTEXT — STEPS" in titles(render(first))
            and second is not None and second.instruction.keyword == "WORK"
            and (second.position, second.total) == (2, 2) and second.wait
            and second.stack.startswith("STEPS{2/2}")):
        held("a proc plays one step at a time", f"`{first.stack}` then `{second.stack}`: the "
             "body is the context of the first step, the last step closes the passage")
    else:
        failures.append(f"  ✗ step by step                {first and first.stack!r} "
                        f"{second and second.stack!r} {second and second.wait!r}")
    env.conductor(key).forget()

    # --- what cannot be read as a procedure refuses by name --------------------------------
    for name, code in sorted(REFUSING.items()):
        refused = env.conductor()
        refused.forget()
        expect(code, lambda r=refused, n=name: r.start(demos("steps", "proc") / n))
    held("every reading refusal names its code", f"{len(REFUSING)} documents, "
         f"{len(set(REFUSING.values()))} codes, nothing played")
    return 0
