"""Scenario `fusion` -- the pattern `control-flow/fusion`, played from its demonstration:
- `instructions_fusion: max` renders the certain stretch in one output: one INSTRUCTION title, one
  line per step, the heading's range `{1-3/3}`, each step traced `batched`
- a number caps the stretch: two steps, a CONTINUE, the rest on the next call
- a document's own `fusion: none` outranks the instance's `max`: one step per output
"""
from __future__ import annotations

from conductor import render
from tests.harness import closing, demonstrated, plant, titles, traced

DEMOS = ("STEPPED.md", "TRIO.md")
TUNED = "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: {}\n---\n"


def _lines(block) -> int:
    """-> the instruction lines a block renders."""
    return sum(1 for one in render(block).splitlines() if one.startswith("INFER "))


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("fusion", bare=True)
    found = demonstrated("control-flow", "fusion")
    if found != sorted(DEMOS):
        failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    plant(env, "control-flow", "fusion", DEMOS)

    def opened(name: str):
        conductor = env.conductor()
        conductor.forget()
        return conductor.start(conductor.boot(name)), conductor.run_id

    # --- max: the certain stretch in one output ----------------------------------------------
    env.write("SETTINGS.md", TUNED.format("max"))
    fused, key = opened("TRIO.md")
    shown = render(fused) if fused is not None else ""
    batched = [one.get("kind") for one in traced(env, key)].count("batched")
    if (fused is not None and fused.wait and _lines(fused) == 3
            and shown.count("▌ INSTRUCTION") == 1 and titles(shown)[0] == "▌ TRIO{1-3/3}"
            and shown.count("▌ TRIO") == 1 and shown.count("▌ pp · run ") == 1 and batched == 3
            and closing(shown)[0] == "▶ AWAIT"):
        held("max renders the certain stretch", f"three steps under one INSTRUCTION title, "
             f"the heading `{titles(shown)[0]}`, {batched} steps traced `batched`, the AWAIT after them")
    else:
        failures.append(f"  ✗ fusion max                  {titles(shown)[:1]!r} {_lines(fused)} {batched}")
    env.conductor(key).forget()

    # --- a number caps it ---------------------------------------------------------------------
    env.write("SETTINGS.md", TUNED.format("2"))
    capped, key = opened("TRIO.md")
    rest = env.conductor(key).forward("")
    if (capped is not None and not capped.wait and _lines(capped) == 2
            and render(capped).count("▌ INSTRUCTION") == 1
            and closing(render(capped))[0] == "▶ CONTINUE"
            and rest is not None and rest.wait and _lines(rest) == 1):
        held("a number caps the stretch", "two steps this output, the CONTINUE hands the third "
             "to the next call")
    else:
        failures.append(f"  ✗ fusion 2                    {capped and _lines(capped)} {rest and rest.wait}")
    env.conductor(key).forget()

    # --- the document's own pace wins --------------------------------------------------------
    env.write("SETTINGS.md", TUNED.format("max"))
    stepped, key = opened("STEPPED.md")
    then = env.conductor(key).forward("")
    if (stepped is not None and not stepped.wait and _lines(stepped) == 1
            and then is not None and _lines(then) == 1 and (then.position, then.total) == (2, 2)):
        held("a document pins its own fusion", "`fusion: none` in its front matter: one step per "
             "output under the instance's max")
    else:
        failures.append(f"  ✗ the document's pace         {stepped and _lines(stepped)} {then and then.stack!r}")
    env.conductor(key).forget()
    return 0
