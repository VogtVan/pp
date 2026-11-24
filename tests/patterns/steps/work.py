"""Scenario `work` -- the pattern `steps/work`, played from its demonstration:
- a WORK is said to the principal: its line says `=> terminal`, even alone; the ask rides its block, and a WORK
  that ends the document closes the passage once it is printed
- a WORK said on `terminal` is due to print: a production handed by the value call bounces -- the block
  that stands and its DEVIATION, nothing recorded, no repair, the print still due; its print call keeps
  the production as handed (an `answer` of channel `terminal` naming the document) and moves the run on
- a gesture between two productions loses nothing: TWOFOLD says its two WORKs and its INFER in one output;
  the first printed, a `-peek` shows the others still due and leaves them due; the last printed, nothing
  remains due
- the steps play on no closing line; the end of the passage closes on AWAIT with no call under it
"""
from __future__ import annotations

from conductor.core import messages
from conductor.core import language
from conductor import render
from conductor import Conductor
from tests.harness import closing, demonstrated, plant, titled, titles, traced

DEMOS = ("ASK.md", "HANDOFF.md", "TWOFOLD.md")
STRAY = "a summary nobody asked the tool for"
FUSED = "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: max\n---\n"


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

    # --- a WORK alone: said, printed, then the passage is over --------------------------------
    asking = env.conductor()
    asking.forget()
    alone = asking.start(asking.boot("ASK.md"))
    ask_key = asking.run_id
    shown = render(alone) if alone is not None else ""
    owed = env.conductor(ask_key).prints_due()
    said, over = env.conductor(ask_key).printed("ASK", "the work, done")
    ended = render(over) if over is not None else ""
    if (alone is not None and alone.instruction.keyword == "WORK" and not alone.wait
            and _line(shown, "WORK").split("  (")[0] == f"WORK any => {language.TERMINAL}"
            and titled(language.CONTEXT, "ASK") in titles(shown)
            and closing(shown) == [] and owed == ["ASK"]
            and said == "moved" and over is not None and over.wait
            and closing(ended) == [f"{messages.SIGNAL} {language.AWAIT}"]):
        held("a WORK is said to the principal", f"`{_line(shown, 'WORK')}`, its brief and the "
             "ask on the block, no closing; its print ends the passage on AWAIT")
    else:
        failures.append(f"  ✗ a WORK alone                {_line(shown, 'WORK')!r} "
                        f"{closing(shown)!r} owed={owed} {said} {closing(ended)!r}")
    env.conductor(ask_key).forget()

    # --- a production handed to the tool bounces --------------------------------------------
    handing = env.conductor()
    handing.forget()
    opened = handing.start(handing.boot("HANDOFF.md"))
    key = handing.run_id
    bounced = env.conductor(key).submit(STRAY)
    due = env.conductor(key).prints_due()
    stray = [one for one in traced(env, key) if one.get("kind") in ("answer", "stray")]
    said, moved = env.conductor(key).printed("HANDOFF", "the work, done")
    answers = [one for one in traced(env, key) if one.get("kind") == "answer"]
    if (opened is not None and opened.instruction.keyword == "WORK" and not opened.wait
            and bounced is not None and bounced.deviation and bounced.repair == 0
            and (bounced.position, bounced.instruction.keyword) == (1, "WORK")
            and due == ["HANDOFF"] and [one["kind"] for one in stray] == ["stray"]
            and answers and answers[-1].get("channel") == language.TERMINAL
            and answers[-1].get("document") == "HANDOFF" and answers[-1].get("given") == "the work, done"
            and said == "moved" and moved is not None and moved.instruction.keyword == "INFER"
            and (moved.position, moved.total) == (2, 2)):
        held("a WORK is due to print", "a production handed by the value call comes back with its "
             "DEVIATION, no repair counted, nothing recorded, the print still due; its print call keeps "
             f"it as handed and moves on to `{moved.stack}`")
    else:
        failures.append(f"  ✗ the print of a WORK         {bounced and bounced.deviation!r} due={due} "
                        f"{stray[-1:]!r} {said} {answers[-1:]!r} {moved and moved.stack!r}")
    env.conductor(key).forget()

    # --- the closings: a closing at the passage's end alone -----------------------------------
    led = env.conductor()
    led.forget()
    first = led.start(led.boot("HANDOFF.md"))
    led_key = led.run_id
    _, then = env.conductor(led_key).printed("HANDOFF", "the work, done")
    _, over = env.conductor(led_key).printed("HANDOFF", "the summary")
    led_tails = [closing(render(one)) if one is not None else None for one in (first, then, over)]
    if (first is not None and then is not None and over is not None
            and [(one.position, one.instruction.keyword) for one in (first, then)]
            == [(1, "WORK"), (2, "INFER")]
            and led_tails == [[], [], [f"{messages.SIGNAL} {language.AWAIT}"]]
            and not first.wait and not then.wait and over.wait):
        held("the steps close on no line", "WORK then INFER; each step closes on no line and its print "
             "moves the run on, and the passage ends on AWAIT with no call under it")
    else:
        failures.append(f"  ✗ the closings                {led_tails!r}")
    env.conductor(led_key).forget()

    # --- a gesture between two productions: the second still due, nothing lost --------------------
    fused = bench.env("work-fused", bare=True)
    fused.write("SETTINGS.md", FUSED)               # the certain stretch in one output
    plant(fused, "steps", "work", DEMOS)
    twofold = fused.conductor()
    twofold.forget()
    output = twofold.start(twofold.boot("TWOFOLD.md"))
    two_key = twofold.run_id
    lines = [one for one in render(output).splitlines() if one.startswith(("WORK ", "INFER "))] if output else []
    owed = fused.conductor(two_key).prints_due()
    first, _ = fused.conductor(two_key).printed("TWOFOLD", "part one")
    view = render(fused.conductor(two_key).peek())
    after_view = fused.conductor(two_key).prints_due()
    second, _ = fused.conductor(two_key).printed("TWOFOLD", "part two")
    third, _ = fused.conductor(two_key).printed("TWOFOLD", "the summary")
    left = fused.conductor(two_key).prints_due()
    kept = [one.get("given") for one in traced(fused, two_key)
            if one.get("kind") == "answer" and one.get("channel") == language.TERMINAL and one.get("document")]
    if (lines == [f"WORK any => {language.TERMINAL}  (TWOFOLD)"] * 2 + [f"INFER any => {language.TERMINAL}  (TWOFOLD)"]
            and owed == ["TWOFOLD"] * 3 and first == "more" and messages.PRINTED.get(first)
            and f"WORK any => {language.TERMINAL}  (TWOFOLD)" in view.splitlines()
            and after_view == ["TWOFOLD"] * 2 and second == "more" and third == "moved"
            and left == [] and kept == ["part one", "part two", "the summary"]):
        held("a gesture between two productions loses nothing", "TWOFOLD says its two WORKs and its INFER in "
             "one output; the first printed (`more`), a `-peek` shows the others still due and leaves them due; "
             f"the last printed (`{third}`): the three productions kept as handed, in order")
    else:
        failures.append(f"  ✗ the gesture between prints  lines={lines} owed={owed} first={first} "
                        f"after={after_view} second={second} third={third} left={left} kept={kept}")
    fused.conductor(two_key).forget()
    return 0
