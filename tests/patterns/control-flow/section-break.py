"""Scenario `section-break` -- the pattern `control-flow/section-break`, played from its demonstration:
- under `instructions_fusion: max`, a `§` closes the output on a CONTINUE and the marked step opens the
  next call; a commented `# §` cuts nothing, the steps after it join the second output
- the break holds before a step that chains (a SERVE): the reading waits for the next call
- under the principal's conduction the same two outputs, the closing bare
"""
from __future__ import annotations

from conductor import render
from tests.harness import closing, demonstrated, plant, principal, titles

DEMOS = ("NOTES.md", "PACED.md", "READAHEAD.md")
FUSED = "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: max\n---\n"


def _lines(block) -> int:
    """-> the instruction lines a block renders."""
    return sum(1 for one in render(block).splitlines() if one.startswith(("INFER ", "WORK ")))


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("section-break", bare=True)
    found = demonstrated("control-flow", "section-break")
    if found != sorted(DEMOS):
        failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    plant(env, "control-flow", "section-break", DEMOS)
    env.write("SETTINGS.md", FUSED)

    def played(name: str, led: bool = False):
        conductor = env.conductor()
        conductor.forget()
        call = (lambda: conductor.start(conductor.boot(name)))
        first = principal(call) if led else call()
        key = conductor.run_id
        follow = (lambda: env.conductor(key).forward(""))
        second = principal(follow) if led else follow()
        return first, second, key

    # --- the cut, and the inert comment -----------------------------------------------------
    first, second, key = played("PACED.md")
    heads = [titles(render(one))[0] if one is not None else "" for one in (first, second)]
    if (first is not None and not first.wait and _lines(first) == 1
            and render(first).count("▌ INSTRUCTION") == 1
            and heads == ["▌ PACED{1/3}", "▌ PACED{2-3/3}"] and closing(render(first))[0] == "▶ CONTINUE"
            and second is not None and second.wait and _lines(second) == 2
            and render(second).count("▌ INSTRUCTION") == 1):
        held("a § cuts the output", f"`{heads[0]}` closes on CONTINUE under fusion max, "
             f"`{heads[1]}` opens the next call: the commented `# §` cuts nothing")
    else:
        failures.append(f"  ✗ the cut                     {heads!r} {first and _lines(first)}")
    env.conductor(key).forget()

    # --- before a step that chains, the reading waits ----------------------------------------
    first, second, key = played("READAHEAD.md")
    if (first is not None and "▌ INFORMATION — NOTES" not in render(first) and _lines(first) == 1
            and second is not None and "▌ INFORMATION — NOTES" in render(second)):
        held("the § holds before a SERVE", "the reading rides the next output, never the one the "
             "§ closed")
    else:
        failures.append(f"  ✗ before a SERVE              {first and render(first)[-160:]!r}")
    env.conductor(key).forget()

    # --- the principal's conduction: the same cut, the closing bare --------------------------
    first, second, key = played("PACED.md", led=True)
    if (first is not None and closing(render(first)) == ["▶ CONTINUE"]
            and (first.position, first.total) == (1, 3) and _lines(first) == 1
            and second is not None and titles(render(second))[0] == "▌ PACED{2-3/3}"):
        held("both conductions cut at the §", f"`{first.stack}` then `{titles(render(second))[0]}` under the "
             "principal's conduction, its CONTINUE bare")
    else:
        failures.append(f"  ✗ the principal's cut         {first and closing(render(first))!r} "
                        f"{second and second.stack!r}")
    env.conductor(key).forget()
    return 0
