"""Scenario `section-break` -- the pattern `control-flow/section-break`, played from its demonstration:
- under `instructions_fusion: max`, a `§` closes the output, on no closing line, and the marked step
  opens the next call, the trace saying `section` once with that step; a commented `# §` cuts nothing, the steps
  after it join the second output
- the break holds before a step that chains (a SERVE): the reading waits for the next call
"""
from __future__ import annotations

from conductor import render
from conductor.core import language
from tests.harness import closing, demonstrated, plant, stepped, titled, titles, traced

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

    def played(name: str):
        conductor = env.conductor()
        conductor.forget()
        first = conductor.start(conductor.boot(name))
        key = conductor.run_id
        second = stepped(lambda: env.conductor(key), "", by="forward")   # the prints due, then the call
        return first, second, key

    # --- the cut, and the inert comment -----------------------------------------------------
    first, second, key = played("PACED.md")
    heads = [titles(render(one))[0] if one is not None else "" for one in (first, second)]
    sections = [str(one.get("instruction")).strip() for one in traced(env, key) if one.get("kind") == "section"]
    if (first is not None and not first.wait and _lines(first) == 1 and sections == ["INFER"]
            and titles(render(first)).count(titled(language.INSTRUCTION)) == 1
            and heads == ["▌ PACED{1/3}", "▌ PACED{2-3/3}"] and closing(render(first)) == []
            and second is not None and not second.wait and _lines(second) == 2
            and titles(render(second)).count(titled(language.INSTRUCTION)) == 1):
        held("a § cuts the output", f"`{heads[0]}` ends on no closing line under fusion max, "
             f"`{heads[1]}` opens the next call, its last step standing for the principal's call, `section` traced "
             "once with the INFER it opens: the "
             "commented `# §` cuts nothing")
    else:
        failures.append(f"  ✗ the cut                     {heads!r} {first and _lines(first)} sections={sections} "
                        f"second={second and (second.wait, _lines(second), titles(render(second)))!r} first={first and closing(render(first))!r}")
    env.conductor(key).forget()

    # --- before a step that chains, the reading waits ----------------------------------------
    first, second, key = played("READAHEAD.md")
    if (first is not None and titled(language.INFORMATION, "NOTES.md") not in titles(render(first)) and _lines(first) == 1
            and second is not None and titled(language.INFORMATION, "NOTES.md") in titles(render(second))):
        held("the § holds before a SERVE", "the reading rides the next output, never the one the "
             "§ closed")
    else:
        failures.append(f"  ✗ before a SERVE              {first and render(first)[-160:]!r}")
    env.conductor(key).forget()

    return 0
