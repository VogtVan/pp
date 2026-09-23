"""Scenario `pick-options` -- 6 case(s) (batch le-pick-sur-des-objets, 2026-09-23):
- the five forms that crashed the renderer (objects, numbers, lists, null, booleans)
  each REPAIR with the miss named under DEVIATION -- never an exception
- the five forms passed in silence or misnamed (an empty element, a twin, an empty
  array, a scalar, an object) each repair too, the miss named
- a number is an option like another: `[1, 2]` renders `1` and `2`, `2` is taken
  verbatim, `3` misses with the options joined
- the witness at the byte: `["approve", "reject"]` renders the block and weighs what
  it weighed on beta.13
- a list no capture judged refuses `options-invalid` by name, the element said; `PICK x`
  alone still refuses `options-empty`
- the trace: the `answer` line, the `repair` line and the REPAIR block, counted
"""
from __future__ import annotations

import json

from conductor import render
from tests.harness import document, steady

FLOOR = ("---\nname: X\nkind: proc\ndescription: judge\noutput: json\nproc: |\n"
         "  INFER\n  PICK verdict\n---\nelect\n")
CRASHING = [('[{"id": "approve"}, {"id": "reject"}]', "not a scalar"),
            ('[1, 2, 3]', ""),                       # numbers are scalars: no miss (case 3)
            ('[["a"], ["b"]]', "not a scalar"),
            ('[null, "a"]', "not a scalar"),
            ('[true, false]', "not a scalar")]
SILENT = [('["", "a"]', "is empty"), ('["a", "a"]', "appears twice"),
          ('[]', "are empty"), ('"approve"', "not a JSON array"), ('{"a": 1}', "not a JSON array")]


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("pick-options")
    floor = document(FLOOR, at=env.made)

    def fresh():
        conductor = env.conductor("t")
        conductor.forget()
        conductor.start(floor)
        return conductor

    def trace() -> list[dict]:
        log = json.loads(env.session().read_text(encoding="utf-8"))["log"]
        lines = (env.made / ".sys" / "state" / log).read_text(encoding="utf-8").splitlines()
        return [json.loads(one) for one in lines if one.strip()]

    def repaired(answer: str, expected: str) -> bool:
        """-> the production MISSES: the document reopens at its INFER, the miss named."""
        fresh()
        block = env.conductor("t").submit(answer)
        return (block.instruction.keyword == "INFER" and block.repair == 1
                and expected in (block.deviation or "") and "OPTIONS" in (block.deviation or "")
                and "TypeError" not in render(block))

    # --- the five forms that crashed the renderer each repair, the miss named ---------
    seen = [repaired(answer, expected) for answer, expected in CRASHING if expected]
    if all(seen) and len(seen) == 4:
        held("a list of non-scalars repairs, never crashes",
             "objects, nested lists, null and booleans each reopen the document at REPAIR 1 -- "
             "the DEVIATION names the OPTIONS' element, the renderer never meets a dict")
    else:
        failures.append(f"  ✗ non-scalar options          {seen}")

    # --- the forms passed in silence or misnamed each repair too -----------------------
    seen = [repaired(answer, expected) for answer, expected in SILENT]
    if all(seen):
        held("the whole form is judged", "an empty element, a twin, an empty array, a scalar "
             "and an object each miss by name -- what beta.13 let through or misnamed")
    else:
        failures.append(f"  ✗ silent forms                {seen}")

    # --- a number is an option like another --------------------------------------------
    fresh()
    numbers = env.conductor("t").submit("[1, 2]")
    rendered = render(numbers)
    missed = env.conductor("t").submit("3")
    fresh(); env.conductor("t").submit("[1, 2]")
    taken = env.conductor("t").submit("2")
    if (list(numbers.options) == ["1", "2"] and "\n1\n2\n" in rendered
            and "`3` is not in OPTIONS (1, 2)" in (missed.deviation or "")
            and bench.over(taken)):
        held("a number is an option", "`[1, 2]` renders OPTIONS `1` and `2`; `2` is taken "
             "verbatim and closes the run, `3` misses with the options joined as text")
    else:
        failures.append(f"  ✗ numeric options             {list(numbers.options)!r} "
                        f"{missed.deviation!r} {taken and taken.end!r}")

    # --- the witness at the byte: the block and its weight of beta.13 ------------------
    fresh()
    witness = env.conductor("t").submit('["approve", "reject"]')
    weighed = next((one.get("weight", {}) for one in reversed(trace())
                    if one.get("kind") == "block" and one.get("command") == "PICK verdict"), {})
    expected = ("▌ DOC{2/2}\n\n▌ OPTIONS\napprove\nreject\n\n▌ INSTRUCTION\n"
                "PICK verdict options => tool\n\n▶ CONTINUE\n./pp t <your-choice>")
    if (steady(render(witness)).strip() == expected
            and (weighed.get("options"), weighed.get("instruction"), weighed.get("total"))
            == (15, 19, 149) and not witness.deviation):
        held("the witness stands at the byte", "a list of strings renders the block beta.13 "
             "rendered -- OPTIONS, the PICK line, the closing -- and weighs 149 c, 15 of options")
    else:
        failures.append(f"  ✗ witness                     {steady(render(witness))!r} {weighed!r}")

    # --- what no capture judged refuses by name; the document with no producer too ----
    (env.made / "procs").mkdir(exist_ok=True)
    (env.made / "procs" / "LISTER.md").write_text(
        "---\nname: LISTER\nkind: proc\ndescription: lists\noutput: json\nproc: |\n  INFER\n"
        "---\nlist\n", encoding="utf-8")
    (env.made / "procs" / "ELECTOR.md").write_text(
        "---\nname: ELECTOR\nkind: proc\ndescription: elects from its seed\ninput: json\n"
        "proc: |\n  PICK member\n---\nelect\n", encoding="utf-8")
    seeded = env.write("procs/SEEDED.md", "---\nname: SEEDED\nkind: proc\ndescription: chains\n"
                       "proc: |\n  CALL LISTER.md\n  CALL ELECTOR.md\n---\nx\n")
    conductor = env.conductor("s")
    conductor.forget()
    conductor.start(seeded)
    expect("options-invalid", lambda: env.conductor("s").submit('[{"id": "a"}]'))
    bare = env.write("procs/BARE.md",
                     "---\nname: BARE\nkind: proc\ndescription: bare\nproc: |\n  PICK x\n---\n")
    conductor = env.conductor("b")
    conductor.forget()
    expect("options-empty", lambda: conductor.start(bare))
    held("the guard refuses by name", "a list arrived by a seed, judged by no capture, refuses "
         "`options-invalid`; a PICK with no producer still refuses `options-empty`")

    # --- the trace: the answer, the repair, the REPAIR block ---------------------------
    fresh()
    env.conductor("t").submit('[{"id": "approve"}]')
    events = trace()
    kinds = [one.get("kind") for one in events]
    repair_block = next((one for one in events if one.get("kind") == "block"
                         and one.get("deviation")), None)
    if (kinds.count("answer") == 1 and kinds.count("repair") == 1 and repair_block is not None
            and "OPTIONS" in repair_block["deviation"]
            and repair_block.get("weight", {}).get("total", 0) > 0):
        held("the trace says the miss", "one `answer` line, one `repair` line, and the REPAIR "
             f"block weighed ({repair_block['weight']['total']} c) with its deviation")
    else:
        failures.append(f"  ✗ trace                       {kinds!r}")
    return 0
