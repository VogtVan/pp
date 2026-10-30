"""Scenario `root` -- the pattern `control-flow/root`, played from its demonstration:
- mid-passage the run waits for a production: a text handed there bounces, nothing traced as a
  message, no repair
- across a `§` the exchange count stands and a mount lives; the root's last step done, the run parks
  on AWAIT, waits for a message, the count moves and the mount is gone
- the next message rewinds the root to its first step under the same key, traced `prompt`
- a message opens a run: the trace says `new`, `prompt`, then the block
- a root whose last step is its first block parks on that block, the exchange counted; a bare call
  on the parked run rewinds the root and the passage plays again, counted again
- under the principal's conduction the same passage: the last step waits for the principal's call,
  then the run parks and the message reopens it
"""
from __future__ import annotations

from conductor import persistence, render
from tests.harness import closing, demonstrated, plant, principal, traced

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
    ended = env.conductor(key).forward("")
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
    paused = linear.start(env.made / "procs" / "LINEAR.md")
    lin_key = linear.run_id
    lin_slot = persistence.slot_of(env.made, lin_key)
    turns_parked = persistence.turns_of(lin_slot)
    replayed = env.conductor(lin_key).resume(env.made / "procs" / "LINEAR.md")
    turns_replayed = persistence.turns_of(lin_slot)
    if (paused is not None and paused.wait and paused.instruction.keyword == "INFER" and turns_parked == 1
            and replayed is not None and replayed.wait and replayed.instruction.keyword == "INFER"
            and turns_replayed == 2):
        held("a one-step root parks and replays", "LINEAR's block parks the run (AWAIT), the exchange counted; "
             "a bare call rewinds the root, the passage plays again: two passages, two exchanges")
    else:
        failures.append(f"  ✗ the linear root             {paused and paused.wait} / {turns_parked} / "
                        f"{replayed and replayed.wait} / {turns_replayed}")
    env.conductor(lin_key).forget()

    # --- the principal's conduction: the same passage, held at its last step ------------------
    led = env.conductor()
    led.forget()
    led_first = principal(lambda: led.start(led.boot("FLOOR.md")))
    led_key = led.run_id
    led_last = principal(lambda: env.conductor(led_key).forward(""))
    led_end = principal(lambda: env.conductor(led_key).forward(""))
    led_again = principal(lambda: env.conductor(led_key).submit(NEXT))
    if (led_first is not None and closing(render(led_first)) == []
            and led_last is not None and (led_last.position, led_last.total) == (2, 2) and not led_last.wait
            and led_end is not None and led_end.wait and closing(render(led_end)) == []
            and led_again is not None and (led_again.position, led_again.total) == (1, 2)):
        held("both conductions end the passage at the root", "under the principal's conduction the "
             "last step waits for the principal's call, then the end, on no closing line; the message rewinds the root")
    else:
        failures.append(f"  ✗ the principal's passage     {led_last and led_last.stack!r} "
                        f"{led_end and closing(render(led_end))!r} {led_again and led_again.stack!r} "
                        f"first={led_first and closing(render(led_first))!r} last_wait={led_last and led_last.wait} "
                        f"end_wait={led_end and led_end.wait}")
    env.conductor(led_key).forget()
    return 0
