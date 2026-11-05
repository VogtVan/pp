"""Scenario `open` -- the pattern `control-flow/open`, played from its demonstration:
- CALLER opens SPACE in the middle of its steps: SPACE is the root; its last step parks the run in
  the space (AWAIT), a message awaited, the exchange counted, the passage's mount gone and NOTES,
  mounted at SPACE's entry, kept; CALLER's tail never plays; the next message replays SPACE from its
  first step, CALLER where it stood
- `-close` leaves the space: CALLER resumes at the step after its OPEN in the same passage, the root
  CALLER again, the trace saying `closed`; its PROVE asks the space's law beside its own
- LOBBY offers DEEP: `-open DEEP` opens it on the parked LOBBY, the trace saying `opened` with the
  name, DEEP opens INNER: the root is the deepest; `-close` gives DEEP back at the step after its OPEN, a second `-close` gives LOBBY back
  parked; at the console `-open DEEP` opens at LOBBY's pending WORK and `-close` gives it back
- `-close` with no space refuses `space-none`; `-open` on a proc that leaves to a successor refuses
  `open-unplayable`; a name the output does not offer is denied as `-s` denies it
- `-compacted` in a space re-serves it, the root still the space
- DESK opens LEDGER, whose last step calls REPORT: the passage ends when REPORT is done, the root
  LEDGER; the next message replays LEDGER from its first step, REPORT receiving the new production;
  `-close` gives DESK back -- under both conductions
- a space several segments offer: the block's `openable` says it once (`segment` null), `-open` bare
  opens it at the segment of the pending step (the last that offers it, traced `routed`), `-open` on a
  space already open refuses `space-open`, `-open <name>@<n>` opens it under the segment named, and `-s`
  bare still asks for `-s <name>@<n>` -- under both conductions
- the build refuses an OPEN to a document that resolves nowhere (`reference-unknown`) and to one that
  cycles (`open-unplayable`)
- under the principal's conduction `-open` and `-close` answer one neutral line, and the principal's
  call serves what follows; the space parks the same way
- the output's heading names the root
- the trace says the SPACES at every block (batch les-espaces-au-flux, beta.36): on GATE, which offers SPACE
  (openable) and LEAVER (it leaves to a successor) while INNER stands in the catalogue unoffered, the block's
  `spaces` says `open: []` and `openable: [{name: SPACE, segment: null}]` -- nothing out of the offer --; after
  `-open SPACE`, `open: [SPACE]` and SPACE out of `openable`
"""
from __future__ import annotations

import json
import re

from conductor import Conductor, compiling, persistence, render
from tests.harness import PRINCIPAL, cli, closing, demonstrated, plant, principal, traced

DEMOS = ("CALLER.md", "DEEP.md", "DESK.md", "INNER.md", "LEDGER.md", "LOBBY.md", "NOTES.md", "REPORT.md",
         "SPACE.md")
TAIL = ("DESK.md", "LEDGER.md", "REPORT.md")
KEY = re.compile(r"run ([0-9a-f]{6})")
LINE = "the topic: the release notes"
LEAVER = ("---\nname: LEAVER\nkind: proc\ndescription: leaves to a successor\nnext: INNER.md\n"
          "proc: |\n  WORK\n---\nleave\n")
HALL = ("---\nname: HALL\nkind: proc\ndescription: offers a proc that leaves\ntools: |\n  LEAVER\n"
        "proc: |\n  WORK\n---\nserve\n")
FORK = ("---\nname: FORK\nkind: proc\ndescription: speaks, calls an inner step, offering DEEP\n"
        "tools: |\n  DEEP\nproc: |\n  INFER\n  CALL FORKIN.md\n  INFER\n---\nfork\n")
FORKIN = "---\nname: FORKIN\nkind: proc\ndescription: the inner step\nproc: |\n  INFER\n---\ninner\n"
HOSTED = "---\nname: HOSTED\nkind: doc\ndescription: a reading of one passage\n---\n\none passage\n"
GATE = ("---\nname: GATE\nkind: proc\ndescription: offers a space and a proc that leaves\ntools: |\n  SPACE\n  LEAVER\n"
        "proc: |\n  WORK\n---\ngate\n")


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


def tail(bench, env) -> None:
    """A space whose last step is a CALL: the root is the space, never its callee."""
    held, failures = bench.held, bench.failures
    plant(env, "control-flow", "open", TAIL)
    for led in (False, True):
        where = "principal" if led else "LLM"
        play = principal if led else (lambda call: call())
        desk = env.conductor()
        desk.forget()
        play(lambda: desk.start(desk.boot("DESK.md")))
        key = desk.run_id
        slot = persistence.slot_of(env.made, key)
        steps = []
        for given in ("", "the first ask", "the first report"):
            steps.append(play(lambda: env.conductor(key).submit(given)))
            if steps[-1] is not None and steps[-1].wait:
                break
        while steps[-1] is not None and not steps[-1].wait and len(steps) < 6:
            steps.append(play(lambda: env.conductor(key).forward("")))
        ended = steps[-1]
        again = play(lambda: env.conductor(key).submit("the second message"))
        report = play(lambda: env.conductor(key).submit("the second ask"))
        shown = render(report) if report is not None else ""
        back = play(lambda: env.conductor(key).close())
        if (ended is not None and ended.wait and ended.root == "LEDGER"
                and persistence.awaits(slot) == persistence.MESSAGE
                and again is not None and again.stack == "DESK ▸ LEDGER{1/2}" and again.root == "LEDGER"
                and report is not None and report.stack == "DESK ▸ LEDGER ▸ REPORT{1/1}"
                and "the second ask" in shown and "the first ask" not in shown
                and back is not None and back.root == "DESK"):
            held(f"a space that ends on a CALL replays itself ({where})", "REPORT done, the passage "
                 "parks in LEDGER; the next message serves LEDGER{1/2}, REPORT receives the second "
                 "ask; `-close` gives DESK back")
        else:
            failures.append(f"  ✗ the space's tail ({where})     {[(one.stack, one.root, one.wait) for one in steps if one]} "
                            f"again={again and (again.stack, again.root)!r} report={report and report.stack!r} "
                            f"second={'the second ask' in shown} back={back and back.root!r}")
        env.conductor(key).forget()


def nested(bench, env) -> None:
    """The agent opens DEEP, DEEP opens INNER: the deepest is the root; two closes give it all back."""
    held, failures = bench.held, bench.failures
    lobby = env.conductor()
    lobby.forget()
    lobby.start(lobby.boot("LOBBY.md"))
    key = lobby.run_id
    opened = env.conductor(key).open("DEEP", route=env.conductor(key).route("DEEP"))
    names = [one.get("name") for one in traced(env, key) if one.get("kind") == "opened"]
    inner = env.conductor(key).submit("")                       # DEEP's WORK: OPEN INNER plays
    first = env.conductor(key).close()                          # INNER leaves: DEEP's last WORK
    last = env.conductor(key).close()                           # DEEP, parked, leaves: LOBBY's WORK
    if (opened is not None and opened.stack == "LOBBY ▸ DEEP{1/3}" and opened.root == "DEEP"
            and inner is not None and inner.stack == "LOBBY ▸ DEEP ▸ INNER{1/1}" and inner.root == "INNER"
            and first is not None and first.stack == "LOBBY ▸ DEEP{3/3}" and first.root == "DEEP"
            and first.wait
            and last is not None and last.stack == "LOBBY{2/2}" and last.root == "LOBBY" and last.wait
            and names == ["DEEP"]):
        held("nested spaces, closed one by one", "`-open DEEP` on LOBBY parked (traced `opened` with its name), "
             "DEEP opens INNER: the root "
             "INNER; `-close` gives DEEP back at its last step, which ends the passage in DEEP; a second "
             "`-close` gives LOBBY back parked, as a door opened on a parked run leaves it (its total "
             "counts the injected OPEN)")
    else:
        failures.append(f"  ✗ nested spaces               {opened and opened.stack!r} opened={names} {inner and inner.stack!r} "
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
        failures.append(f"  ✗ the principal's space       {[(one.stack, one.wait) for one in steps if one]} "
                        f"root={steps[-1] and steps[-1].root!r} awaits={persistence.awaits(slot)!r} turns={persistence.turns_of(slot)}")
    env.conductor(led_run).forget()


def addressed(bench) -> None:
    """A space several segments offer: the block says it ONCE (`segment` null), the bare name opens it at the
    segment of the pending step (the last that offers it), a space already open refuses `space-open`, and the
    address opens it under the segment named; `-s` still asks for the address -- under both conductions, on a
    house with its settings, whose outputs fuse. Two runs per conduction: the offer leaves with the fused
    output, so the bare open and the addressed open each take a fresh one."""
    held, failures = bench.held, bench.failures
    env = bench.env("open-addressed", pin=False)
    plant(env, "control-flow", "open", DEMOS)
    env.write("procs/FORK.md", FORK)
    env.write("procs/FORKIN.md", FORKIN)

    def owners(key: str) -> list[int]:
        """The ordinals of the current output's segments that offer DEEP, as the engine keeps them."""
        return [int(one["ordinal"]) for one in persistence.segments_of(persistence.slot_of(env.made, key))
                if "DEEP" in one.get("tools", [])]

    def routed(key: str) -> list:
        return [one.get("segment") for one in traced(env, key) if one.get("kind") == "routed"]

    def opened_names(key: str) -> list:
        return [one.get("name") for one in traced(env, key) if one.get("kind") == "opened"]

    def fresh(mark: dict) -> tuple:
        """A new run on FORK, its boot's chunks taken by `-s DEEP` until the fused output stands: -> (key, that
        `-s DEEP` call)."""
        out = cli(env.engine, "-new", cwd=env.root, env={"PP_DOOR": "FORK.md", **mark})
        key = KEY.search(out.stdout).group(1) if KEY.search(out.stdout) else ""
        door = cli(env.engine, key, "-s", "DEEP", cwd=env.root)
        for _ in range(20):
            if "chunk-pending" not in door.stdout:
                break
            door = cli(env.engine, key, "-s", "DEEP", cwd=env.root)
        return key, door

    for led in (False, True):
        mark = {PRINCIPAL: "true"} if led else {}
        where = "principal" if led else "LLM"

        def served(key: str) -> None:
            """Under the principal a gesture holds its output: the principal's bare call serves it."""
            if led:
                cli(env.engine, key, cwd=env.root, env={PRINCIPAL: "true"})

        key, door = fresh(mark)
        fused = owners(key)
        blocks = [one for one in traced(env, key) if one.get("kind") == "block"]
        said = [one for one in (blocks[-1].get("spaces") or {}).get("openable") or []
                if isinstance(one, dict) and one.get("name") == "DEEP"] if blocks else []
        if len(fused) >= 2 and said == [{"name": "DEEP", "segment": None}]:
            held(f"a name offered twice is said once ({where})", f"DEEP offered by segments {fused}, the block's "
                 "openable says {name: DEEP, segment: null} once")
        else:
            failures.append(f"  ✗ the offer said once ({where})   owners={fused} openable={said}")
        bare = cli(env.engine, key, "-open", "DEEP", cwd=env.root)
        served(key)
        if (key and door.returncode == 2 and "address-ambiguous" in door.stderr and "-s DEEP@<n>" in door.stderr
                and bare.returncode == 0 and opened_names(key) == ["DEEP"] and fused and routed(key) == [fused[-1]]):
            held(f"the bare name opens at the pending step ({where})", "`-s DEEP`, offered by several segments, asks "
                 f"for `-s DEEP@<n>`; `-open DEEP` opens the space, routed to segment {fused[-1]} (the last that "
                 "offers it), traced `opened`")
        else:
            failures.append(f"  ✗ the bare open ({where})        key={key!r} {door.returncode}/{bare.returncode} "
                            f"{door.stderr[-120:]!r} {bare.stderr[-160:]!r} opened={opened_names(key)} "
                            f"routed={routed(key)} owners={fused}")
        again = cli(env.engine, key, "-open", "DEEP", cwd=env.root)
        if again.returncode == 2 and "space-open" in again.stderr and opened_names(key) == ["DEEP"]:
            held(f"a space already open refuses ({where})", "`-open DEEP` inside DEEP refuses space-open; one "
                 "`opened` at the trace")
        else:
            failures.append(f"  ✗ the space reopened ({where})   {again.returncode} {again.stderr[-160:]!r} "
                            f"opened={opened_names(key)}")
        cli(env.engine, "-reset", key, cwd=env.root)

        key, _ = fresh(mark)
        at = owners(key)
        addressed_open = cli(env.engine, key, "-open", f"DEEP@{at[0]}" if at else "DEEP@1", cwd=env.root)
        served(key)
        if at and addressed_open.returncode == 0 and opened_names(key) == ["DEEP"] and routed(key) == [at[0]]:
            held(f"the address opens under its segment ({where})", f"`-open DEEP@{at[0]}` opens the space under "
                 f"segment {at[0]}, traced `routed` there")
        else:
            failures.append(f"  ✗ the addressed open ({where})   {addressed_open.returncode} "
                            f"{addressed_open.stderr[-160:]!r} owners={at} opened={opened_names(key)} routed={routed(key)}")
        cli(env.engine, "-reset", key, cwd=env.root)


def spaces_said(bench, env) -> None:
    """The trace says the spaces: what is open, what the offer lets open -- nothing out of the offer."""
    held, failures = bench.held, bench.failures
    env.write("procs/GATE.md", GATE)
    gate = env.conductor()
    gate.forget()
    gate.start(gate.boot("GATE.md"))
    key = gate.run_id

    def last_spaces() -> dict | None:
        blocks = [one for one in traced(env, key) if one.get("kind") == "block"]
        return blocks[-1].get("spaces") if blocks else None
    before = last_spaces()
    env.conductor(key).open("SPACE", route=env.conductor(key).route("SPACE"))
    after = last_spaces()
    names = sorted(one.get("name") for one in (before or {}).get("openable") or [] if isinstance(one, dict))
    left = [one.get("name") for one in (after or {}).get("openable") or [] if isinstance(one, dict)]
    if (before == {"open": [], "openable": [{"name": "SPACE", "segment": None}]}
            and after is not None and after.get("open") == ["SPACE"] and "SPACE" not in left
            and "INNER" not in names and "LEAVER" not in names):
        held("the trace says the spaces", "GATE's block: open [], openable SPACE alone (LEAVER leaves, INNER is "
             "not offered); after -open SPACE: open [SPACE], SPACE no longer openable")
    else:
        failures.append(f"  ✗ the spaces at the trace     before={before} after={after}")
    env.conductor(key).forget()


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
    plant(env, "control-flow", "open", tuple(one for one in DEMOS if one not in TAIL))
    env.write("HOSTED.md", HOSTED)
    parked(bench, env)
    nested(bench, env)
    spaces_said(bench, env)
    console(bench, env)
    tail(bench, env)
    addressed(bench)
    build(bench)
    return 0
