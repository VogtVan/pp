"""Scenario `infer` -- the pattern `steps/infer`, played from its demonstration:
- the line names the form of the document: `any` without `output:`, the declared one otherwise
- a production nothing consumes is said to the principal (`=> terminal`, the last step too) and is due to
  print; the print of the last one closes the passage
- a production the next step consumes goes to the tool by its form's channel, the trace's answer
  line says it; a consumed empty production and one that breaks its form each repair at the INFER;
  a valid one seeds the next step, which sees it under `input`
"""
from __future__ import annotations

import json

from conductor import render
from conductor.core import language, messages
from tests.harness import closing, demonstrated, plant, traced

DEMOS = ("COUNT.md", "NOTE.md", "REPORT.md", "TALLY.md")


def _line(block) -> str:
    """-> the INFER line of a block's rendering, its document's name dropped."""
    rendered = render(block) if block is not None else ""
    return next((one.split("  (")[0] for one in rendered.splitlines()
                 if one.startswith("INFER ")), "")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("infer", bare=True)
    found = demonstrated("steps", "infer")
    if found != sorted(DEMOS):
        failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    plant(env, "steps", "infer", DEMOS)

    def opened(name: str):
        conductor = env.conductor()
        conductor.forget()
        return conductor.start(conductor.boot(name)), conductor.run_id

    # --- the form on the line, the production said ------------------------------------------
    note, note_key = opened("NOTE.md")
    env.conductor(note_key).forget()
    tally, tally_key = opened("TALLY.md")
    owed = env.conductor(tally_key).prints_due()
    said, over = env.conductor(tally_key).printed("TALLY", "| asked | delivered | remains |\n|---|---|---|\n| a | b | c |")
    ended = render(over) if over is not None else ""
    env.conductor(tally_key).forget()
    if (_line(note) == f"INFER any => {language.TERMINAL}" and not note.wait
            and _line(tally) == f"INFER table => {language.TERMINAL}" and tally.output == "table"
            and closing(render(tally)) == [] and owed == ["TALLY"]
            and said == "moved" and over is not None and over.wait
            and closing(ended) == [f"{messages.SIGNAL} {language.AWAIT}"]):
        held("the line names the form", f"`{_line(note)}` without `output:`, `{_line(tally)}` "
             "with `output: table`; said at its step, its print ends the passage on AWAIT")
    else:
        failures.append(f"  ✗ the form                    {_line(note)!r} {_line(tally)!r} "
                        f"{closing(render(tally))!r} owed={owed} {said} {closing(ended)!r}")

    # --- a consumed production: the tool's channel, judged at its capture -------------------
    count, key = opened("COUNT.md")
    empty = env.conductor(key).submit("")
    broken = env.conductor(key).submit("[not json")
    seeded = env.conductor(key).submit('["alpha", "beta"]')
    answers = [one for one in traced(env, key) if one.get("kind") == "answer"]
    if (_line(count) == f"INFER json => {language.TOOL_HEREDOC}" and not count.wait
            and not count.label and not count.next_call
            and empty is not None and empty.repair == 1 and empty.deviation
            and empty.instruction.keyword == "INFER" and empty.document == "COUNT"
            and broken is not None and broken.repair == 2 and broken.deviation
            and seeded is not None and seeded.document == "REPORT"
            and seeded.stack.startswith("COUNT ▸ REPORT")
            and json.loads(dict(seeded.payloads).get("input", "null")) == ["alpha", "beta"]
            and answers and answers[-1].get("channel") == language.TOOL_HEREDOC):
        held("a consumed production goes to pp", f"`{_line(count)}`; empty, it repairs "
             "(REPAIR 1), off its form, it repairs (REPAIR 2), whole, it seeds "
             f"`{seeded.stack}`, served under `input` -- the answer line says the heredoc channel")
    else:
        failures.append(f"  ✗ the consumed production     {_line(count)!r} "
                        f"{empty and empty.repair!r} {broken and broken.repair!r} "
                        f"{seeded and seeded.stack!r} {answers[-1:]!r}")
    env.conductor(key).forget()
    return 0
