"""Scenario `work` -- the pattern `steps/work`, played from its demonstration:
- a WORK is said to the principal: its line says `=> words`, the ask rides its block, and a WORK
  that ends the document closes the passage
- a production handed to the tool on a WORK bounces: nothing recorded, no repair, the same step;
  the trace's answer line says the channel `words`; the bare call moves on
- under the principal's conduction the same steps play, the closing bare
"""
from __future__ import annotations

from conductor.core import language
from conductor import render
from tests.harness import closing, demonstrated, plant, principal, titles, traced

DEMOS = ("ASK.md", "HANDOFF.md")
STRAY = "a summary nobody asked the tool for"


def _line(rendered: str, keyword: str) -> str:
    """-> the instruction line of `keyword` in a rendering, "" when absent."""
    return next((one for one in rendered.splitlines() if one.startswith(f"{keyword} ")), "")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("work", bare=True)
    found = demonstrated("steps", "work")
    if found != sorted(DEMOS):
        failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    plant(env, "steps", "work", DEMOS)

    # --- a WORK alone: said, then the passage is over --------------------------------------
    asking = env.conductor()
    asking.forget()
    alone = asking.start(asking.boot("ASK.md"))
    shown = render(alone) if alone is not None else ""
    if (alone is not None and alone.instruction.keyword == "WORK" and alone.wait
            and _line(shown, "WORK").split("  (")[0] == "WORK any => words"
            and "▌ NEXT INSTRUCTION CONTEXT — ASK" in titles(shown)
            and closing(shown)[0] == "▶ AWAIT"):
        held("a WORK is said to the principal", f"`{_line(shown, 'WORK')}`, its brief and the "
             "ask on the block, the passage over at its step")
    else:
        failures.append(f"  ✗ a WORK alone                {_line(shown, 'WORK')!r} "
                        f"{closing(shown)[:1]!r}")
    env.conductor(asking.run_id).forget()

    # --- a production handed to the tool bounces --------------------------------------------
    handing = env.conductor()
    handing.forget()
    opened = handing.start(handing.boot("HANDOFF.md"))
    key = handing.run_id
    bounced = env.conductor(key).submit(STRAY)
    answers = [one for one in traced(env, key) if one.get("kind") == "answer"]
    moved = env.conductor(key).forward("")
    if (opened is not None and opened.instruction.keyword == "WORK" and not opened.wait
            and bounced is not None and bounced.deviation and bounced.repair == 0
            and (bounced.position, bounced.instruction.keyword) == (1, "WORK")
            and answers and answers[-1].get("channel") == language.WORDS
            and answers[-1].get("given") == STRAY
            and moved is not None and moved.instruction.keyword == "INFER"
            and (moved.position, moved.total) == (2, 2)):
        held("a production handed on a WORK bounces", "the same step comes back with its "
             "DEVIATION, no repair counted, the answer line says `words`; the bare call "
             f"moves on to `{moved.stack}`")
    else:
        failures.append(f"  ✗ the bounce                  {bounced and bounced.deviation!r} "
                        f"{answers[-1:]!r} {moved and moved.stack!r}")
    env.conductor(key).forget()

    # --- the principal's conduction: the same steps, no closing line -----------------------
    led = env.conductor()
    led.forget()
    first = principal(lambda: led.start(led.boot("HANDOFF.md")))
    led_key = led.run_id
    then = principal(lambda: env.conductor(led_key).forward(""))
    over = principal(lambda: env.conductor(led_key).forward(""))
    agent = [closing(render(one)) for one in (opened, moved)]
    led_tails = [closing(render(one)) for one in (first, then, over)]
    if (first is not None and then is not None and over is not None
            and [(one.position, one.instruction.keyword) for one in (first, then)]
            == [(1, "WORK"), (2, "INFER")]
            and led_tails == [[], [], []]
            and any(key in line for line in agent[0]) and agent[1][0] == "▶ AWAIT"
            and not then.wait and over.wait):
        held("both conductions play the same steps", "WORK then INFER under the principal's "
             "conduction too; its outputs close on no line, and its last step waits for the "
             "principal's call before the passage ends")
    else:
        failures.append(f"  ✗ the principal's conduction  {led_tails!r} {agent!r}")
    env.conductor(led_key).forget()
    return 0
