"""Scenario `open` -- the pattern `control-flow/open`, played from its demonstration:
- CALLER opens SPACE in the middle of its steps: SPACE is the root; its last step parks the run in
  the space (AWAIT), a message awaited, the exchange counted, the passage's mount gone and NOTES,
  mounted at SPACE's entry, kept; CALLER's tail never plays; the next message replays SPACE from its
  first step, CALLER where it stood
- `-close` leaves the space: CALLER resumes at the step after its OPEN in the same passage, the root
  CALLER again, the trace saying `closed`; its PROVE asks the space's law beside its own
- LOBBY offers DEEP: `-open DEEP` opens it on the parked LOBBY, DEEP opens INNER: the root is the
  deepest; `-close` gives DEEP back at the step after its OPEN, a second `-close` gives LOBBY back
  parked; at the console `-open DEEP` opens at LOBBY's pending WORK and `-close` gives it back
- `-close` with no space refuses `space-none`; `-open` on a proc that leaves to a successor refuses
  `open-unplayable`; a name the output does not offer is denied as `-s` denies it
- `-compacted` in a space re-serves it, the root still the space
- the build refuses an OPEN to a document that resolves nowhere (`reference-unknown`) and to one that
  cycles (`open-unplayable`)
- under the principal's conduction `-open` and `-close` answer one neutral line, and the principal's
  call serves what follows; the space parks the same way
- the output's heading names the root
"""
from __future__ import annotations

import json
import re

from conductor import Conductor, compiling, persistence, render
from tests.harness import PRINCIPAL, cli, closing, demonstrated, plant, principal, traced

DEMOS = ("CALLER.md", "DEEP.md", "INNER.md", "LOBBY.md", "NOTES.md", "SPACE.md")
KEY = re.compile(r"run ([0-9a-f]{6})")
LINE = "the topic: the release notes"
LEAVER = ("---\nname: LEAVER\nkind: proc\ndescription: leaves to a successor\nnext: INNER.md\n"
          "proc: |\n  WORK\n---\nleave\n")
HALL = ("---\nname: HALL\nkind: proc\ndescription: offers a proc that leaves\ntools: |\n  LEAVER\n"
        "proc: |\n  WORK\n---\nserve\n")
HOSTED = "---\nname: HOSTED\nkind: doc\ndescription: a reading of one passage\n---\n\none passage\n"


def _state(slot) -> dict:
    return json.loads(slot.read_text(encoding="utf-8")) if slot.is_file() else {}


def _mounted(slot) -> list[str]:
    return [one.get("doc", "") for one in persistence.mounted_of(slot)]


def _proof(*codes: str) -> str:
    return json.dumps([{"code": code, "evidence": "the line names it", "verdict": "ok"} for code in codes])


def parked(bench, env) -> None:
    """The space is the root: it parks the run, replays on the message, the caller untouched."""
    held, failures = bench.held, bench.failures
    caller = env.conductor()
    caller.forget()
    first = caller.start(caller.boot("CALLER.md"))
    key = caller.run_id
    slot = persistence.slot_of(env.made, key)
    entered = env.conductor(key).submit("")                     # CALLER's WORK: OPEN SPACE plays
    env.conductor(key).mount([{"doc": "HOSTED.md", "body": True}])
    mid = (persistence.turns_of(slot), sorted(_mounted(slot)))
    worked = env.conductor(key).submit(LINE)                    # SPACE's INFER: its WORK, the last
    ended = env.conductor(key).forward("") if worked is not None and not worked.wait else worked
    frames = [frame.get("document", "").rsplit("/", 1)[-1]
              for frame in _state(slot).get("frames", [])]
    caller_steps = [one.get("done") for one in _state(slot)["frames"][0]["instructions"]]
    if (first is not None and first.root == "CALLER" and entered is not None
            and entered.stack == "CALLER ▸ SPACE{1/2}" and entered.root == "SPACE"
            and ended is not None and ended.wait and closing(render(ended))[0] == "▶ AWAIT"
            and ended.stack.startswith("CALLER ▸ SPACE{") and ended.root == "SPACE"
            and persistence.awaits(slot) == persistence.MESSAGE
            and mid[0] == 0 and "HOSTED.md" in mid[1] and "NOTES" in " ".join(mid[1])
            and persistence.turns_of(slot) == 1 and "HOSTED.md" not in _mounted(slot)
            and any("NOTES" in one for one in _mounted(slot))
            and frames == ["CALLER.md", "SPACE.md"] and caller_steps == [True, False, False, False]):
        held("the space parks the run", f"`{entered.stack}` the root SPACE; its last step parks on AWAIT "
             "in the space, a message awaited, the count 0 -> 1, HOSTED swept and NOTES held; CALLER's "
             "OPEN, INFER and PROVE still undone")
    else:
        failures.append(f"  ✗ the space parks             {entered and entered.stack!r} "
                        f"root={entered and entered.root!r} {ended and ended.stack!r} wait={ended and ended.wait} "
                        f"mid={mid} mounted={_mounted(slot)} frames={frames} caller={caller_steps}")

    again = env.conductor(key).submit("the next message")
    if (again is not None and again.stack == "CALLER ▸ SPACE{1/2}" and again.root == "SPACE"
            and persistence.awaits(slot) == persistence.PRODUCTION):
        held("the message replays the space", "the next message rewinds SPACE to its first step, "
             "CALLER where it stood")
    else:
        failures.append(f"  ✗ the replay                  {again and again.stack!r}")

    shown = render(again) if again is not None else ""
    if shown.splitlines()[0].startswith("▌ pp · ") and " · root SPACE" in shown.splitlines()[0]:
        held("the heading names the root", f"`{shown.splitlines()[0]}`")
    else:
        failures.append(f"  ✗ the heading                 {shown.splitlines()[:1]!r}")

    reserved = env.conductor(key).compacted()
    if reserved is not None and reserved.root == "SPACE" and reserved.stack == "CALLER ▸ SPACE{1/2}":
        held("a compaction re-serves the space", "`-compacted` in the space: the same step, the root SPACE")
    else:
        failures.append(f"  ✗ the compaction              {reserved and reserved.stack!r} {reserved and reserved.root!r}")

    # --- -close: the caller resumes after its OPEN, its PROVE asks the space's law -------------
    back = env.conductor(key).close()
    kinds = [one.get("kind") for one in traced(env, key)]
    asked = env.conductor(key).submit("") if back is not None else None   # the line is said, never handed
    if (back is not None and back.stack == "CALLER{3/4}" and back.root == "CALLER" and "closed" in kinds
            and asked is not None and asked.instruction.keyword == "PROVE"
            and {"S1", "C1"} <= set(asked.judged)):
        held("-close gives the caller back", f"`{back.stack}` in the same passage, the root CALLER, "
             f"`closed` traced; its PROVE asks {list(asked.judged)} -- the space's law with its own")
    else:
        failures.append(f"  ✗ the close                   {back and back.stack!r} {kinds[-3:]} "
                        f"{asked and asked.judged!r}")
    paid = env.conductor(key).submit(_proof(*(asked.judged if asked is not None else ())))
    if paid is not None and paid.wait and paid.root == "CALLER" and persistence.turns_of(slot) == 2:
        held("the caller's passage ends at its root", "proven, CALLER parks on AWAIT: two exchanges")
    else:
        failures.append(f"  ✗ the caller's end            {paid and paid.stack!r} turns={persistence.turns_of(slot)}")
    expect_none = env.conductor(key)
    bench.expect("space-none", lambda: expect_none.close())
    env.conductor(key).forget()


def nested(bench, env) -> None:
    """The agent opens DEEP, DEEP opens INNER: the deepest is the root; two closes give it all back."""
    held, failures = bench.held, bench.failures
    lobby = env.conductor()
    lobby.forget()
    lobby.start(lobby.boot("LOBBY.md"))
    key = lobby.run_id
    opened = env.conductor(key).open("DEEP", route=env.conductor(key).route("DEEP"))
    inner = env.conductor(key).submit("")                       # DEEP's WORK: OPEN INNER plays
    first = env.conductor(key).close()                          # INNER leaves: DEEP's last WORK
    last = env.conductor(key).close()                           # DEEP, parked, leaves: LOBBY's WORK
    if (opened is not None and opened.stack == "LOBBY ▸ DEEP{1/3}" and opened.root == "DEEP"
            and inner is not None and inner.stack == "LOBBY ▸ DEEP ▸ INNER{1/1}" and inner.root == "INNER"
            and first is not None and first.stack == "LOBBY ▸ DEEP{3/3}" and first.root == "DEEP"
            and first.wait
            and last is not None and last.stack == "LOBBY{2/2}" and last.root == "LOBBY" and last.wait):
        held("nested spaces, closed one by one", "`-open DEEP` on LOBBY parked, DEEP opens INNER: the root "
             "INNER; `-close` gives DEEP back at its last step, which ends the passage in DEEP; a second "
             "`-close` gives LOBBY back parked, as a door opened on a parked run leaves it (its total "
             "counts the injected OPEN)")
    else:
        failures.append(f"  ✗ nested spaces               {opened and opened.stack!r} {inner and inner.stack!r} "
                        f"{first and (first.stack, first.wait)!r} {last and (last.stack, last.wait, last.root, str(last.instruction))!r}")
    env.conductor(key).forget()

    env.write("procs/LEAVER.md", LEAVER)
    env.write("procs/HALL.md", HALL)
    hall = env.conductor()
    hall.forget()
    hall.start(hall.boot("HALL.md"))
    hall_key = hall.run_id
    bench.expect("open-unplayable", lambda: env.conductor(hall_key).open(
        "LEAVER", route=env.conductor(hall_key).route("LEAVER")))
    env.conductor(hall_key).forget()


def console(bench, env) -> None:
    """The verbs at the console, under both conductions."""
    held, failures = bench.held, bench.failures
    out = cli(env.engine, "-new", cwd=env.root, env={"PP_DOOR": "LOBBY.md"})
    key = KEY.search(out.stdout).group(1) if KEY.search(out.stdout) else ""
    denied = cli(env.engine, key, "-open", "NOBODY", cwd=env.root)
    opened = cli(env.engine, key, "-open", "DEEP", cwd=env.root)
    closed = cli(env.engine, key, "-close", cwd=env.root)
    none = cli(env.engine, key, "-close", cwd=env.root)
    if (key and denied.returncode == 2 and "DEVIATION" in denied.stdout
            and opened.returncode == 0 and "DEEP{1/3}" in opened.stdout and " · root DEEP" in opened.stdout
            and closed.returncode == 0 and "▸ LOBBY{" in closed.stdout and " · root DEEP" not in closed.stdout
            and none.returncode == 2 and "space-none" in none.stderr):
        held("the console opens and closes", "`-open NOBODY` denied as `-s` denies it, `-open DEEP` and "
             "`-close` answer their blocks in the LLM's mode, a second `-close` refuses space-none")
    else:
        failures.append(f"  ✗ the console                 key={key!r} {denied.returncode}/{opened.returncode}/"
                        f"{closed.returncode}/{none.returncode} {opened.stderr[-200:]!r} {none.stderr[-120:]!r}")

    led = cli(env.engine, "-new", cwd=env.root, env={"PP_DOOR": "LOBBY.md", PRINCIPAL: "true"})
    led_key = KEY.search(led.stdout).group(1) if KEY.search(led.stdout) else ""
    said = {act: "pp: " + line for act, line in Conductor.HELD_SAID.items()}
    agent_open = cli(env.engine, led_key, "-open", "DEEP", cwd=env.root)
    served_open = cli(env.engine, led_key, cwd=env.root, env={PRINCIPAL: "true"})
    agent_close = cli(env.engine, led_key, "-close", cwd=env.root)
    served_close = cli(env.engine, led_key, cwd=env.root, env={PRINCIPAL: "true"})
    if (led_key and agent_open.returncode == 0 and agent_open.stdout.strip() == said["door"]
            and "DEEP{1/3}" in served_open.stdout
            and agent_close.returncode == 0 and agent_close.stdout.strip() == said["closed"]
            and "LOBBY{" in served_close.stdout):
        held("under the principal, one neutral line each", f"`{agent_open.stdout.strip()}` then "
             f"`{agent_close.stdout.strip()}`; the principal's bare call serves DEEP, then LOBBY")
    else:
        failures.append(f"  ✗ the principal's verbs       {agent_open.stdout[-120:]!r} {agent_close.stdout[-120:]!r} "
                        f"{served_open.stdout[-200:]!r} {served_close.stdout[-200:]!r}")

    caller = env.conductor()
    caller.forget()
    steps = [principal(lambda: caller.start(caller.boot("CALLER.md")))]
    led_run = caller.run_id
    for _ in range(4):
        steps.append(principal(lambda: env.conductor(led_run).forward("")))
        if steps[-1] is not None and steps[-1].wait:
            break
    slot = persistence.slot_of(env.made, led_run)
    if (steps[-1] is not None and steps[-1].wait and steps[-1].root == "SPACE"
            and persistence.awaits(slot) == persistence.MESSAGE and persistence.turns_of(slot) == 1):
        held("the principal's space parks the same way", f"{[one.stack for one in steps if one]} -- "
             "AWAIT in SPACE, one exchange")
    else:
        failures.append(f"  ✗ the principal's space       {[(one.stack, one.wait) for one in steps if one]}")
    env.conductor(led_run).forget()


def build(bench) -> None:
    """The build refuses an OPEN it could never play."""
    lint = bench.env("open-lint", bare=True)
    lint.write("procs/LOST.md", "---\nname: LOST\nkind: proc\ndescription: opens nowhere\n"
                                "proc: |\n  OPEN NOWHERE.md\n---\nlost\n")
    bench.expect("reference-unknown", lambda: compiling.build_tools(lint.made))
    (lint.made / "procs" / "LOST.md").unlink()
    lint.write("procs/ROUND.md", "---\nname: ROUND\nkind: proc\ndescription: cycles\ncycle: round\n"
                                 "proc: |\n  WORK\n---\nround\n")
    lint.write("procs/OPENER.md", "---\nname: OPENER\nkind: proc\ndescription: opens a cycle\n"
                                  "proc: |\n  OPEN ROUND.md\n---\nopen\n")
    bench.expect("open-unplayable", lambda: compiling.build_tools(lint.made))


def scenario(bench) -> int:
    failures = bench.failures
    found = demonstrated("control-flow", "open")
    if found != sorted(DEMOS):
        failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    env = bench.env("open", bare=True)
    plant(env, "control-flow", "open", DEMOS)
    env.write("HOSTED.md", HOSTED)
    parked(bench, env)
    nested(bench, env)
    console(bench, env)
    build(bench)
    return 0
