"""Scenario `pick` -- the pattern `steps/pick`, played from its demonstration:
- the OPTIONS are the production before the PICK: rendered one per line above the PICK's line, the
  closing a CONTINUE that carries the call; they weigh what they print
- a value of the OPTIONS is taken verbatim and the passage goes on; a value outside repairs at the
  INFER, the value named, and the trace says the answer, the repair and the REPAIR block
- every list off the OPTIONS' form repairs, never crashes; a number is an option
- a PICK with nothing before it refuses `options-empty`; a list that reached it without being
  judged refuses `options-invalid`
"""
from __future__ import annotations

import json

from conductor import render
from conductor.core import language
from tests.harness import closing, demonstrated, plant, titles, traced

DEMOS = ("BALLOT.md", "CHOOSE.md", "ELECT.md", "SHORTLIST.md", "TRIAGE.md")
CANDIDATES = ["approve", "revise"]
OFF_FORM = ['[{"id": "approve"}, {"id": "reject"}]', '[["a"], ["b"]]', '[null, "a"]',
            '[true, false]', '["", "a"]', '["a", "a"]', '[]', '"approve"', '{"a": 1}']


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("pick", bare=True)
    found = demonstrated("steps", "pick")
    if found != sorted(DEMOS):
        failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    plant(env, "steps", "pick", DEMOS)

    def triage():
        conductor = env.conductor()
        conductor.forget()
        triage.asked = conductor.start(conductor.boot("TRIAGE.md"))
        return conductor.run_id

    # --- the OPTIONS, their line, their closing, their weight -------------------------------
    key = triage()
    listing = triage.asked
    offered = env.conductor(key).submit(json.dumps(CANDIDATES))
    shown = render(offered) if offered is not None else ""
    heads = titles(shown)
    order = [next((i for i, one in enumerate(heads) if one.startswith(head)), -1)
             for head in ("▌ OPTIONS", "▌ INSTRUCTION", "▶ CONTINUE")]
    weight = next((one.get("weight", {}) for one in reversed(traced(env, key))
                   if one.get("kind") == "block" and one.get("command", "").startswith("PICK")), {})
    tail = closing(shown)
    lines = shown.splitlines()
    listed = lines[lines.index("▌ OPTIONS") + 1:][:len(CANDIDATES)] if "▌ OPTIONS" in lines else []
    line = next((one for one in lines if one.startswith("PICK ")), "")
    if (offered is not None and list(offered.options) == CANDIDATES and listed == CANDIDATES
            and line.startswith("PICK candidate ") and "=> tool" in line
            and offered.instruction.keyword == "PICK" and offered.output == "options"
            and listing is not None and listing.output == language.LIST
            and -1 not in order and order == sorted(order)
            and tail[0] == "▶ CONTINUE" and any(key in line for line in tail)
            and weight.get("options") == sum(len(one) + 1 for one in CANDIDATES)
            and weight.get("instruction") == len(offered.command) + len(offered.output)
            and weight.get("total", 0) > weight["options"] + weight["instruction"]):
        held("the OPTIONS are the production before", f"TRIAGE lists in the engine's `list` without "
             f"a word of `output:`; {list(offered.options)} one per line "
             "above the PICK's line, a CONTINUE that carries the call, "
             f"{weight['options']} c and the line {weight['instruction']} c weighed for what "
             f"they print, of {weight['total']} c")
    else:
        failures.append(f"  ✗ the OPTIONS                 {heads!r} {tail[:2]!r} {weight!r}")

    # --- a value of the OPTIONS is taken; one outside repairs, named -------------------------
    missed = env.conductor(key).submit("reject")
    events = traced(env, key)
    kinds = [one.get("kind") for one in events]
    repaired = next((one for one in events if one.get("kind") == "block" and one.get("deviation")), {})
    env.conductor(key).submit(json.dumps(CANDIDATES))
    taken = env.conductor(key).submit("revise")
    answers = [one for one in traced(env, key) if one.get("kind") == "answer"]
    if (missed is not None and missed.repair == 1 and missed.instruction.keyword == "INFER"
            and "reject" in (missed.deviation or "")
            and kinds.count("repair") == 1 and repaired.get("weight", {}).get("total", 0) > 0
            and taken is not None and taken.wait
            and [one.get("channel") for one in answers[-2:]] == ["tool", "tool"]):
        held("a value is taken verbatim", "`revise` closes the passage; `reject` repairs at the "
             "INFER, named -- the trace says the answer, the repair and the REPAIR block weighed; "
             "the PICK's answer line says `tool`")
    else:
        failures.append(f"  ✗ the value                   {missed and missed.deviation!r} "
                        f"{kinds!r} {taken and taken.wait!r}")
    env.conductor(key).forget()

    # --- off the OPTIONS' form, each list repairs; a number is an option ---------------------
    misses = []
    for answer in OFF_FORM:
        miss = env.conductor(triage()).submit(answer)
        misses.append(miss is not None and miss.repair == 1 and miss.instruction.keyword == "INFER"
                      and "OPTIONS" in (miss.deviation or "") and "Traceback" not in render(miss))
    number_key = triage()
    listed = env.conductor(number_key).submit("[1, 2]")
    number = env.conductor(number_key).submit("2")
    if (all(misses) and listed is not None and list(listed.options) == ["1", "2"]
            and number is not None and number.wait):
        held("every list off the form repairs", f"{len(OFF_FORM)} forms each reopen the INFER "
             "with the OPTIONS named; `[1, 2]` offers `1` and `2`, `2` is taken")
    else:
        failures.append(f"  ✗ the forms                   {misses!r} {listed and list(listed.options)!r}")
    env.conductor(number_key).forget()

    # --- what has no list, or an unjudged one, refuses by name -------------------------------
    empty = env.conductor()
    empty.forget()
    expect("options-empty", lambda: empty.start(empty.boot("CHOOSE.md")))
    ballot = env.conductor()
    ballot.forget()
    ballot.start(ballot.boot("BALLOT.md"))
    expect("options-invalid", lambda: env.conductor(ballot.run_id).submit('[{"id": "a"}]'))
    held("the PICK refuses what it cannot elect from", "no production before it: "
         "`options-empty`; a list no capture judged: `options-invalid`")
    return 0
