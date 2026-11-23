"""Scenario `root` -- the pattern `control-flow/root`, played from its demonstration:
- mid-passage the run waits for a production: a text handed there bounces, nothing traced as a
  message, no repair
- across a `§` the exchange count stands and a mount lives; the root's last step done, the run parks
  on AWAIT, waits for a message, the count moves and the mount is gone
- the next message rewinds the root to its first step under the same key, traced `prompt`
- a message opens a run: the trace says `new`, `prompt`, then the block
- a root whose last step is its first block stands on it for the principal's call, which parks the
  run, the exchange counted; a bare call on the parked run rewinds the root and the passage plays
  again, counted again
- the same passage read on its closings: the last step waits for the principal's call, then the run
  parks -- the end of the passage closed on AWAIT with no call -- and the message reopens it
- the last step stays said: each output ends on its step, which keeps `=> terminal` and asks no last
  message; the root at its end renders no step and gets no line
- the root rewritten mid-passage: the passage ends on the steps it played, and the next message
  rewinds the root on its new steps, traced `reseated`
"""
from __future__ import annotations

from conductor.core import messages
from conductor import persistence, render
from conductor.core import language
from tests.harness import closing, demonstrated, plant, stepped, traced

DEMOS = ("FLOOR.md", "HOSTED.md", "LINEAR.md")
NEXT = "the operator's next message"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("root", bare=True)
    found = demonstrated("control-flow", "root")
    if found != sorted(DEMOS):
        failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    plant(env, "control-flow", "root", DEMOS)

    # --- mid-passage: a production is awaited, a text bounces ---------------------------------
    floor = env.conductor()
    floor.forget()
    first = floor.start(floor.boot("FLOOR.md"))
    key = floor.run_id
    slot = persistence.slot_of(env.made, key)
    waiting = persistence.awaits(slot)
    mid_view = env.conductor(key).peek()
    strayed = env.conductor(key).submit(NEXT)
    kinds = [one.get("kind") for one in traced(env, key)]
    if (first is not None and not first.wait and waiting == persistence.PRODUCTION
            and mid_view is not None and not mid_view.wait
            and strayed is not None and (strayed.deviation or "").strip() and strayed.repair == 0
            and (strayed.position, strayed.total) == (first.position, first.total)
            and "prompt" not in kinds):
        held("mid-passage a text bounces", "the run waits for a production and -peek renders the "
             "pending step; the text comes back under a DEVIATION, no repair, no `prompt` traced")
    else:
        failures.append(f"  ✗ mid-passage                 {waiting!r} {strayed and strayed.deviation!r} {kinds}")

    # --- across the §: the count stands, the mount lives; then the passage ends ---------------
    env.conductor(key).mount([{"doc": "HOSTED.md", "body": True}])
    mid_turns, mid_mounts = persistence.turns_of(slot), persistence.mounted_of(slot)
    stepped(lambda: env.conductor(key), "", by="forward")           # the INFER said: the WORK stands
    ended = stepped(lambda: env.conductor(key), "", by="forward")   # the principal's call ends the passage
    end_turns, end_mounts = persistence.turns_of(slot), persistence.mounted_of(slot)
    parked_view = env.conductor(key).peek()
    if (mid_turns == 0 and mid_mounts and ended is not None and ended.wait
            and closing(render(ended))[0] == "▶ AWAIT" and persistence.awaits(slot) == persistence.MESSAGE
            and end_turns == 1 and not end_mounts
            and parked_view is not None and parked_view.wait
            and closing(render(parked_view))[0] == "▶ AWAIT"):
        held("the passage ends with the root", f"across the § the count stands at {mid_turns} and the "
             f"mount lives; the last step done, AWAIT (-peek renders it), a message awaited, the count "
             f"at {end_turns}, the mount gone")
    else:
        failures.append(f"  ✗ the end of the passage      turns={mid_turns}->{end_turns} "
                        f"mounts={len(mid_mounts)}->{len(end_mounts)} {ended and ended.wait!r}")

    # --- the next message rewinds the root ----------------------------------------------------
    reopened = env.conductor(key).submit(NEXT)
    prompted = [one.get("text") for one in traced(env, key) if one.get("kind") == "prompt"]
    if (reopened is not None and reopened.document == "FLOOR" and (reopened.position, reopened.total) == (1, 2)
            and not reopened.wait and prompted == [NEXT] and persistence.run_id_of(slot) == key):
        held("the message rewinds the root", f"`{reopened.stack}` again under run {key}, the text "
             "traced `prompt`")
    else:
        failures.append(f"  ✗ the rewind                  {reopened and reopened.stack!r} {prompted!r}")
    env.conductor(key).forget()

    # --- a message opens a run ----------------------------------------------------------------
    opener = env.conductor()
    opener.forget()
    opened = opener.start(opener.boot("FLOOR.md"), NEXT)
    events = traced(env, opener.run_id)
    kinds = [one.get("kind") for one in events]
    if (opened is not None and opened.document == "FLOOR" and kinds[:2] == ["new", "prompt"]
            and events[1].get("text") == NEXT and "block" in kinds):
        held("a message opens a run", "the trace says `new`, `prompt` with the text, then the block")
    else:
        failures.append(f"  ✗ the opening message         {kinds[:4]}")
    env.conductor(opener.run_id).forget()

    # --- a root whose last step is its first block parks on it, and replays on a bare call ----
    env.write("READ.md", "some reading\n")
    linear = env.conductor()
    linear.forget()
    shown = linear.start(env.made / "procs" / "LINEAR.md")
    lin_key = linear.run_id
    lin_slot = persistence.slot_of(env.made, lin_key)
    paused = stepped(lambda: env.conductor(lin_key), "", by="forward")     # the principal's call parks it
    turns_parked = persistence.turns_of(lin_slot)
    again = env.conductor(lin_key).resume(env.made / "procs" / "LINEAR.md")
    replayed = stepped(lambda: env.conductor(lin_key), "", by="forward")
    turns_replayed = persistence.turns_of(lin_slot)
    if (shown is not None and not shown.wait and shown.instruction.keyword == "INFER"
            and paused is not None and paused.wait and turns_parked == 1
            and again is not None and again.instruction.keyword == "INFER"
            and replayed is not None and replayed.wait and turns_replayed == 2):
        held("a one-step root parks and replays", "LINEAR's block stands for the principal's call, which parks "
             "the run (AWAIT), the exchange counted; a bare call rewinds the root, the passage plays again: "
             "two passages, two exchanges")
    else:
        failures.append(f"  ✗ the linear root             {shown and shown.wait} / {paused and paused.wait} / "
                        f"{turns_parked} / {again and again.stack!r} / {replayed and replayed.wait} / {turns_replayed}")
    env.conductor(lin_key).forget()

    # --- the same passage on its closings, held at its last step --------------------------
    led = env.conductor()
    led.forget()
    led_first = led.start(led.boot("FLOOR.md"))
    led_key = led.run_id
    led_last = stepped(lambda: env.conductor(led_key), "", by="forward")
    led_end = stepped(lambda: env.conductor(led_key), "", by="forward")
    led_again = env.conductor(led_key).submit(NEXT)
    if (led_first is not None and closing(render(led_first)) == []
            and led_last is not None and (led_last.position, led_last.total) == (2, 2) and not led_last.wait
            and closing(render(led_last)) == []
            and led_end is not None and led_end.wait
            and closing(render(led_end)) == [f"{messages.SIGNAL} {language.AWAIT}"]
            and led_again is not None and (led_again.position, led_again.total) == (1, 2)):
        held("the passage ends at the root on its closings", "the "
             "last step waits for the principal's call on no closing line, then the end closes on AWAIT with no "
             "call under it; the message rewinds the root")
    else:
        failures.append(f"  ✗ the principal's passage     {led_last and led_last.stack!r} "
                        f"{led_end and closing(render(led_end))!r} {led_again and led_again.stack!r} "
                        f"first={led_first and closing(render(led_first))!r} last_wait={led_last and led_last.wait} "
                        f"end_wait={led_end and led_end.wait}")
    env.conductor(led_key).forget()

    # --- the last step stays said: `=> terminal`, no last message asked --------------------------
    said, last = f"=> {language.TERMINAL}  (", f"=> {language.RESPONSE}  ("
    by_led = {"break": led_first, "last": led_last}
    off = [name for name, one in by_led.items()
           if one is None or one.response or render(one).count(said) != 1 or last in render(one)]
    at_end = render(led_end) if led_end is not None else ""
    if (not off and led_end is not None and not led_end.response and said not in at_end and last not in at_end
            and shown is not None and not shown.response and render(shown).count(said) == 1
            and last not in render(shown)):
        held("an output that ends what the agent does keeps its step said",
             "each of FLOOR's two outputs ends on its step, which stays `terminal` and asks no last message; the "
             "root at its end renders no step and gets no line; LINEAR's one step stays `terminal` too")
    else:
        failures.append(f"  ✗ the last step said          off={off} end={led_end and led_end.response!r} "
                        f"linear={shown and shown.response!r}")

    # --- the root rewritten mid-passage: its passage ends as it began, the next one is new ------
    floor = env.made / "procs" / "FLOOR.md"
    kept = floor.read_text(encoding="utf-8")
    grown = env.conductor()
    grown.forget()
    block = grown.start(floor)
    grown_key = grown.run_id
    floor.write_text(kept.replace("  WORK\n", "  WORK\n  INFER\n", 1), encoding="utf-8")
    for _ in range(6):
        if block is None or block.wait:
            break
        block = stepped(lambda: env.conductor(grown_key))
    renewed = env.conductor(grown_key).submit(NEXT)
    said = [one.get("document") for one in traced(env, grown_key) if one.get("kind") == "reseated"]
    if (block is not None and block.wait and block.total == 2
            and renewed is not None and (renewed.position, renewed.total) == (1, 3) and said == ["FLOOR"]):
        held("a root rewritten mid-passage", "its passage parks on the two steps it began with; the "
             "next message rewinds it on its three new steps, traced `reseated`")
    else:
        failures.append(f"  ✗ the rewritten root          {block and (block.stack, block.wait)!r} "
                        f"{renewed and renewed.stack!r} {said!r}")
    env.conductor(grown_key).forget()
    floor.write_text(kept, encoding="utf-8")
    return 0
