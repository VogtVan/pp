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
  `-close` gives DESK back
- a space several segments offer (FORK, whose inner step stands under a law of its own): the block's
  `openable` says it once (`segment` null), `-open` bare opens it at the segment of the pending step (the last
  that offers it, traced `routed`), `-open` on a space already open refuses `space-open`, `-open <name>@<n>`
  opens it under the segment named, an `@<n>` past the output's segments refuses `address-stale`, and `-s`
  bare still asks for `-s <name>@<n>`
- the build refuses an OPEN to a document that resolves nowhere (`reference-unknown`) and to one that
  cycles (`open-unplayable`)
- at the console the agent's `-open` and `-close` answer one neutral line, and the principal's
  call serves what follows
- a space whose entry FUSES a welcome with its step (PORCH, WELCOME attached at its entry), opened by the
  principal while the root's last step is still due: the principal's `-open` answers one line and the output is
  HELD at the run, the principal's bare call serves it whole -- ONE segment, the welcome's step and the space's
  under the laws they share, the welcome's law in text, the root's step due said again --; the principal's `-close` holds the same way; after the agent's
  `-peek`, `@2` refuses `address-stale` and `@1`, the one segment that stands, plays
- the output's heading names the root
- the trace says the SPACES at every block (batch les-espaces-au-flux, beta.36): on GATE, which offers SPACE
  (openable) and LEAVER (it leaves to a successor) while INNER stands in the catalogue unoffered, the block's
  `spaces` says `open: []` and `openable: [{name: SPACE, segment: null}]` -- nothing out of the offer --; after
  `-open SPACE`, `open: [SPACE]` and SPACE out of `openable`
"""
from __future__ import annotations

import json
import re

from conductor.core import messages
from conductor import Conductor, compiling, persistence, render
from tests.harness import agents, cli, closing, demonstrated, plant, printed, stepped, traced

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
FORKIN = ("---\nname: FORKIN\nkind: proc\ndescription: the inner step, under a law of its own\n"
          "constraints.behavior: |\n  FK1  the inner step keeps to its own part\nproc: |\n  INFER\n---\ninner\n")
HOSTED = "---\nname: HOSTED\nkind: doc\ndescription: a reading of one passage\n---\n\none passage\n"
GATEWAY = ("---\nname: GATEWAY\nkind: proc\ndescription: offers the space PORCH\ntools: |\n  PORCH\n"
           "proc: |\n  WORK\n---\ngateway\n")
PORCH = ("---\nname: PORCH\nkind: proc\ndescription: a space whose welcome fuses with its step\ntools: |\n  LOOK\n"
         "proc: |\n  WORK\n---\nporch\n")
WELCOME = ("---\nname: WELCOME\nkind: proc\ndescription: the welcome of PORCH, once at its entry\n"
           "attach: porch.initialize\nformats: |\n  greeting  words  one line that greets\noutput: greeting\n"
           "constraints.behavior: |\n  W1  greet the principal by the name of the space\nproc: |\n  INFER\n---\nwelcome\n")
LOOK = "---\nname: LOOK\nkind: proc\ndescription: a look around\nproc: |\n  WORK\n---\nlook\n"
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
    entered = stepped(lambda: env.conductor(key))                # CALLER's WORK printed: OPEN SPACE plays
    env.conductor(key).mount([{"doc": "HOSTED.md", "body": True}])
    mid = (persistence.turns_of(slot), sorted(_mounted(slot)))
    worked = printed(env, key, LINE)                            # SPACE's INFER printed: its WORK, the last
    ended = stepped(lambda: env.conductor(key), "", by="forward") if worked is not None and not worked.wait else worked
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
    asked = stepped(lambda: env.conductor(key)) if back is not None else None   # the line is printed, never handed
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
    desk = env.conductor()
    desk.forget()
    desk.start(desk.boot("DESK.md"))
    key = desk.run_id
    slot = persistence.slot_of(env.made, key)
    steps = []
    for given in ("", "the first ask", "the first report"):
        steps.append(stepped(lambda: env.conductor(key), given))
        if steps[-1] is not None and steps[-1].wait:
            break
    while steps[-1] is not None and not steps[-1].wait and len(steps) < 6:
        steps.append(stepped(lambda: env.conductor(key), "", by="forward"))
    ended = steps[-1]
    again = env.conductor(key).submit("the second message")
    report = env.conductor(key).submit("the second ask")
    shown = render(report) if report is not None else ""
    back = env.conductor(key).close()
    if (ended is not None and ended.wait and ended.root == "LEDGER"
            and persistence.awaits(slot) == persistence.MESSAGE
            and again is not None and again.stack == "DESK ▸ LEDGER{1/2}" and again.root == "LEDGER"
            and report is not None and report.stack == "DESK ▸ LEDGER ▸ REPORT{1/1}"
            and "the second ask" in shown and "the first ask" not in shown
            and back is not None and back.root == "DESK"):
        held(f"a space that ends on a CALL replays itself", "REPORT done, the passage "
             "parks in LEDGER; the next message serves LEDGER{1/2}, REPORT receives the second "
             "ask; `-close` gives DESK back")
    else:
        failures.append(f"  ✗ the space's tail     {[(one.stack, one.root, one.wait) for one in steps if one]} "
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
    inner = stepped(lambda: env.conductor(key))                  # DEEP's WORK printed: OPEN INNER plays
    first = env.conductor(key).close()                          # INNER leaves: DEEP's last WORK
    deep_end = stepped(lambda: env.conductor(key), by="forward")   # the principal's call ends the passage in DEEP
    last = env.conductor(key).close()                           # DEEP, parked, leaves: LOBBY's WORK
    lobby_end = stepped(lambda: env.conductor(key), by="forward")  # the principal's call parks LOBBY
    if (opened is not None and opened.stack == "LOBBY ▸ DEEP{1/3}" and opened.root == "DEEP"
            and inner is not None and inner.stack == "LOBBY ▸ DEEP ▸ INNER{1/1}" and inner.root == "INNER"
            and first is not None and first.stack == "LOBBY ▸ DEEP{3/3}" and first.root == "DEEP"
            and not first.wait and deep_end is not None and deep_end.wait and deep_end.root == "DEEP"
            and last is not None and last.stack == "LOBBY{2/2}" and last.root == "LOBBY" and not last.wait
            and lobby_end is not None and lobby_end.wait and lobby_end.root == "LOBBY"
            and names == ["DEEP"]):
        held("nested spaces, closed one by one", "`-open DEEP` on LOBBY parked (traced `opened` with its name), "
             "DEEP opens INNER: the root "
             "INNER; `-close` gives DEEP back at its last step, whose term the principal's call gives -- the "
             "passage ends in DEEP; a second `-close` gives LOBBY back at its last step, as a door opened on a "
             "parked run leaves it (its total counts the injected OPEN), the principal's call parks it")
    else:
        failures.append(f"  ✗ nested spaces               {opened and opened.stack!r} opened={names} {inner and inner.stack!r} "
                        f"{first and (first.stack, first.wait)!r} {deep_end and (deep_end.stack, deep_end.wait)!r} "
                        f"{last and (last.stack, last.wait, last.root, str(last.instruction))!r} "
                        f"{lobby_end and (lobby_end.stack, lobby_end.wait)!r}")
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
    """The verbs at the console: the agent's `-open` and `-close` answer one neutral line, the principal's
    bare call serves what follows."""
    held, failures = bench.held, bench.failures
    out = cli(env.engine, "-new", cwd=env.root, env={"PP_DOOR": "LOBBY.md"})
    key = KEY.search(out.stdout).group(1) if KEY.search(out.stdout) else ""
    said = {act: messages.held(act) for act in messages.ACKNOWLEDGED}
    denied = cli(env.engine, key, "-open", "NOBODY", cwd=env.root)
    agent_open = cli(env.engine, key, "-open", "DEEP", cwd=env.root, env=agents(key))
    served_open = cli(env.engine, key, cwd=env.root)
    agent_close = cli(env.engine, key, "-close", cwd=env.root, env=agents(key))
    served_close = cli(env.engine, key, cwd=env.root)
    none = cli(env.engine, key, "-close", cwd=env.root, env=agents(key))
    if (key and denied.returncode == 2 and "DEVIATION" in denied.stdout
            and agent_open.returncode == 0 and agent_open.stdout.strip() == said["door"]
            and "DEEP{1/3}" in served_open.stdout and " · root DEEP" in served_open.stdout
            and agent_close.returncode == 0 and agent_close.stdout.strip() == said["closed"]
            and "LOBBY{" in served_close.stdout and " · root DEEP" not in served_close.stdout
            and none.returncode == 2 and "space-none" in none.stderr):
        held("the console opens and closes", f"`-open NOBODY` denied as `-s` denies it; the agent's `-open DEEP` "
             f"and `-close` answer `{agent_open.stdout.strip()}` then `{agent_close.stdout.strip()}`, the "
             "principal's bare call serves DEEP, then LOBBY; a second `-close` refuses space-none")
    else:
        failures.append(f"  ✗ the console                 key={key!r} {denied.returncode}/{agent_open.returncode}/"
                        f"{agent_close.returncode}/{none.returncode} {agent_open.stdout[-120:]!r} "
                        f"{agent_close.stdout[-120:]!r} {served_open.stdout[-200:]!r} {served_close.stdout[-200:]!r} "
                        f"{none.stderr[-120:]!r}")


def addressed(bench) -> None:
    """A space several segments offer: the block says it ONCE (`segment` null), the bare name opens it at the
    segment of the pending step (the last that offers it), a space already open refuses `space-open`, and the
    address opens it under the segment named; `-s` still asks for the address -- on a house with its
    settings, whose outputs fuse. Two runs: the offer leaves with the fused output, so the bare open and the
    addressed open each take a fresh one."""
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

    def fresh() -> tuple:
        """A new run on FORK, its boot's chunks taken by `-s DEEP` until the fused output stands: -> (key, that
        `-s DEEP` call)."""
        out = cli(env.engine, "-new", cwd=env.root, env={"PP_DOOR": "FORK.md"})
        key = KEY.search(out.stdout).group(1) if KEY.search(out.stdout) else ""
        door = cli(env.engine, key, "-s", "DEEP", cwd=env.root)
        for _ in range(20):
            if "chunk-pending" not in door.stdout:
                break
            door = cli(env.engine, key, "-s", "DEEP", cwd=env.root)
        return key, door


    def served(key: str) -> None:
        """A gesture of the principal holds its output: the principal's bare call serves it."""
        cli(env.engine, key, cwd=env.root)

    key, door = fresh()
    fused = owners(key)
    blocks = [one for one in traced(env, key) if one.get("kind") == "block"]
    said = [one for one in (blocks[-1].get("spaces") or {}).get("openable") or []
            if isinstance(one, dict) and one.get("name") == "DEEP"] if blocks else []
    if len(fused) >= 2 and said == [{"name": "DEEP", "segment": None}]:
        held(f"a name offered twice is said once", f"DEEP offered by segments {fused}, the block's "
             "openable says {name: DEEP, segment: null} once")
    else:
        failures.append(f"  ✗ the offer said once   owners={fused} openable={said}")
    bare = cli(env.engine, key, "-open", "DEEP", cwd=env.root)
    served(key)
    if (key and door.returncode == 2 and "address-ambiguous" in door.stderr and "-s DEEP@<n>" in door.stderr
            and bare.returncode == 0 and opened_names(key) == ["DEEP"] and fused and routed(key) == [fused[-1]]):
        held(f"the bare name opens at the pending step", "`-s DEEP`, offered by several segments, asks "
             f"for `-s DEEP@<n>`; `-open DEEP` opens the space, routed to segment {fused[-1]} (the last that "
             "offers it), traced `opened`")
    else:
        failures.append(f"  ✗ the bare open        key={key!r} {door.returncode}/{bare.returncode} "
                        f"{door.stderr[-120:]!r} {bare.stderr[-160:]!r} opened={opened_names(key)} "
                        f"routed={routed(key)} owners={fused}")
    again = cli(env.engine, key, "-open", "DEEP", cwd=env.root)
    if again.returncode == 2 and "space-open" in again.stderr and opened_names(key) == ["DEEP"]:
        held(f"a space already open refuses", "`-open DEEP` inside DEEP refuses space-open; one "
             "`opened` at the trace")
    else:
        failures.append(f"  ✗ the space reopened   {again.returncode} {again.stderr[-160:]!r} "
                        f"opened={opened_names(key)}")
    cli(env.engine, "-reset", key, cwd=env.root)

    key, _ = fresh()
    at = owners(key)
    past = len(persistence.segments_of(persistence.slot_of(env.made, key))) + 1
    beyond = cli(env.engine, key, "-open", f"DEEP@{past}", cwd=env.root)
    nothing = opened_names(key)
    addressed_open = cli(env.engine, key, "-open", f"DEEP@{at[0]}" if at else "DEEP@1", cwd=env.root)
    served(key)
    if (at and beyond.returncode == 2 and "address-stale" in beyond.stderr and nothing == []
            and addressed_open.returncode == 0 and opened_names(key) == ["DEEP"] and routed(key) == [at[0]]):
        held(f"the address opens under its segment", f"`-open DEEP@{past}`, past the output's "
             f"segments, refuses address-stale and opens nothing; `-open DEEP@{at[0]}` opens the space under "
             f"segment {at[0]}, traced `routed` there")
    else:
        failures.append(f"  ✗ the addressed open   {beyond.returncode}/{addressed_open.returncode} "
                        f"{addressed_open.stderr[-160:]!r} owners={at} opened={opened_names(key)} routed={routed(key)}")
    cli(env.engine, "-reset", key, cwd=env.root)


def welcomed(bench) -> None:
    """A space whose entry fuses a welcome with its step, opened by the principal while the root's last step is still
    due: the output is held for the principal's bare call, served whole; the view and the address agree after a
    `-peek`."""
    held, failures = bench.held, bench.failures
    env = bench.env("open-welcomed", pin=False)
    for name, text in (("GATEWAY", GATEWAY), ("PORCH", PORCH), ("WELCOME", WELCOME), ("LOOK", LOOK)):
        env.write(f"procs/{name}.md", text)
    said = {act: messages.held(act, principal=True) for act in messages.ACKNOWLEDGED}

    def numbered(text: str) -> list[str]:
        return re.findall(r"^▌ \[(\d+)\] ", text, re.M)

    def asked(text: str) -> list[str]:
        """-> the document each step line of a rendering names, in order."""
        return [one.rsplit("(", 1)[-1].rstrip(")") for one in text.splitlines()
                if one.startswith(("INFER ", "WORK ")) and one.endswith(")")]

    def fused(text: str) -> bool:
        """One segment, unnumbered, that says the welcome's step then the space's, then the root's step
        still due to print said again."""
        return (numbered(text) == [] and asked(text) == ["WELCOME", "PORCH", "TURN"]
                and sum(1 for one in text.splitlines() if one.startswith("▌ ") and "WELCOME{" in one) == 1)

    def prints_owed(run: str) -> None:
        """The agent's prints of the exchange, each by its print call, the root's last step left standing:
        the door that offers the space stays in the output while the principal opens it."""
        for document in [one for one in (env.conductor(run).prints_due() if run else []) if one != "TURN"]:
            cli(env.engine, run, "-print", document, "-", cwd=env.root, stdin=f"{document} said")

    led = cli(env.engine, "-new", cwd=env.root, env={"PP_DOOR": "GATEWAY.md"})
    key = KEY.search(led.stdout).group(1) if KEY.search(led.stdout) else ""
    slot = persistence.slot_of(env.made, key)
    prints_owed(key)
    opened = cli(env.engine, key, "-open", "PORCH", cwd=env.root)
    kept = persistence.held_of(slot) if key else {}
    served = cli(env.engine, key, cwd=env.root)
    if (key and opened.returncode == 0 and opened.stdout.strip() == said["door"] and kept
            and fused(served.stdout) and "greet the principal" in served.stdout):
        held("the principal's open holds the welcome", f"`{opened.stdout.strip()}`, the output held "
             f"({kept.get('chars')} c); the bare call serves one segment, WELCOME's step then PORCH's, W1 in text, "
             "TURN's step due said again")
    else:
        failures.append(f"  ✗ the principal's open held    key={key!r} rc={opened.returncode} "
                        f"said={opened.stdout.strip()[:80]!r} held={bool(kept)} segments={numbered(served.stdout)} "
                        f"asked={asked(served.stdout)} {opened.stderr[-160:]!r}")
    peeked = cli(env.engine, key, "-peek", cwd=env.root, env=agents(key))
    stale = cli(env.engine, key, "-s", "LOOK@2", cwd=env.root, env=agents(key))
    at_one = cli(env.engine, key, "-s", "LOOK@1", cwd=env.root, env=agents(key))
    if (numbered(peeked.stdout) == [] and stale.returncode == 2 and "address-stale" in stale.stderr
            and at_one.returncode == 0):
        held("the address counts the segments that stand", "after the agent's `-peek` (no numbered segment), "
             "`-s LOOK@2` refuses address-stale and `-s LOOK@1` plays")
    else:
        failures.append(f"  ✗ the view and the address      peek={numbered(peeked.stdout)} stale={stale.returncode} "
                        f"{stale.stderr[-120:]!r} at_one={at_one.returncode} {at_one.stderr[-120:]!r}")
    cli(env.engine, key, cwd=env.root)                 # the principal serves what LOOK left held
    closed = cli(env.engine, key, "-close", cwd=env.root)
    kept_close = persistence.held_of(slot) if key else {}
    back = cli(env.engine, key, cwd=env.root)
    if closed.returncode == 0 and closed.stdout.strip() == said["closed"] and kept_close and "root TURN" in back.stdout.splitlines()[0]:
        held("the principal's close holds the same way", f"`{closed.stdout.strip()}`, the bare call serves the root below")
    else:
        failures.append(f"  ✗ the principal's close held   rc={closed.returncode} said={closed.stdout.strip()[:80]!r} "
                        f"held={bool(kept_close)} back={back.stdout[:160]!r}")
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
    welcomed(bench)
    build(bench)
    return 0
