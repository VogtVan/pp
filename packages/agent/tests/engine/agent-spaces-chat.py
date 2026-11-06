"""Scenario `agent-spaces-chat` -- the SPACES a principal opens and closes on a run (batch les-espaces-au-flux, agent
0.37.0): the commands `open` and `close` of `agent chat --json`, the verbs `agent open` and `agent close`, on a house
pinning `agent`, the run opened on the door HELLO (one WORK) with an overlay of TURN that offers the space ROOM at
every block (`--door`, `--documents`, as the campaign's root `space` lays them):
- open on a parked run: `{"kind": "open", "name": "ROOM"}` after the first exchange says `space {name: ROOM, open:
  true, pending: false, spaces}` -- `spaces.open` holding ROOM --, then a `conduction` and a `verdict` without a
  `principal` voice -- an exchange without a message, launched on ROOM's block, which parks the run in ROOM (its
  trace's last block says the root ROOM)
- the space's welcome reaches the agent: ROOM's welcome (WELCOME, attached at its entry, under its law W1) fuses
  with ROOM's step; the exchange without a message serves both, the law in text, at its first launch
- close gives the block below: `{"kind": "close"}` says `space {name: ROOM, open: false}`, then the trace's last block
  says `spaces.open = []`
- a name not offered is refused: `{"kind": "open", "name": "NOBODY"}` says `refused` with the engine's code,
  nothing opened
- a command during an exchange plays after it: `message` then `open` written together -- the `space` object comes
  after the message's `verdict`, never before
- the verbs say the spaces: `agent open agents/ag1 <key> ROOM --json` says `{key, spaces, state}` with ROOM open and
  the run parked; `agent close agents/ag1 <key> --json` says `open: []`
- run-busy: under a conversation holding the run, `agent open` refuses `run-busy` and plays nothing
- a run taken up knows the spaces: `chat --run <key> --json` says `ready.spaces` with `open` and `openable`
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

from tests.harness import support

A = support(__file__, "agent")

HELLO = ("---\nname: HELLO\nkind: proc\noutput: any\ndescription: one WORK, offering the space ROOM\n"
         "tools: |\n  ROOM\nproc: |\n  WORK\n---\n\n# HELLO\n\nSay ONE line: « hello ».\n")
ROOM = ("---\nname: ROOM\nkind: proc\noutput: any\ndescription: a space the principal opens -- one INFER\n"
        "proc: |\n  INFER\n---\n\n# ROOM\n\nSay ONE line: « room ».\n")
WELCOME = ("---\nname: WELCOME\nkind: proc\ndescription: the welcome of ROOM, once at its entry\n"
           "attach: room.initialize\noutput: said\n"
           "constraints.behavior: |\n  W1  greet the principal by the name of the room\nproc: |\n  INFER\n---\n\n"
           "# WELCOME\n\nSay ONE line: « welcome ».\n")
TURN = "---\nname: TURN\ntools: |\n  +ROOM\n---\n"       # the overlay that offers ROOM at every block of the turn


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)
    documents = bench.temp() / "documents"
    documents.mkdir(exist_ok=True)
    (documents / "HELLO.md").write_text(HELLO, encoding="utf-8")
    (documents / "ROOM.md").write_text(ROOM, encoding="utf-8")
    (documents / "TURN.md").write_text(TURN, encoding="utf-8")
    (documents / "WELCOME.md").write_text(WELCOME, encoding="utf-8")
    keys = h.keys

    def talk(where, commands: str, *flags: str) -> tuple[subprocess.CompletedProcess, list[dict]]:
        """-> the conversation `agent chat agents/ag1 --json` fed `commands`, and the objects it wrote."""
        argv = [sys.executable, str(h.engine), "--instance", str(h.house), "agent", "chat", "agents/ag1",
                "--json", *flags, *h.harnessed_at("play", where)]
        played = subprocess.run(argv, input=commands, capture_output=True, text=True, cwd=h.ws,
                                env={**os.environ, **h.env}, timeout=180)
        found = []
        for line in played.stdout.splitlines():
            try:
                found.append(json.loads(line))
            except ValueError:
                found.append({"kind": "UNREADABLE", "line": line})
        return played, found

    def command(kind: str, **fields) -> str:
        return json.dumps({"kind": kind, **fields}) + "\n"

    def fresh(known: set) -> str:
        return next((one for one in keys() if one not in known), "")

    def last_block(key: str) -> dict:
        blocks = [one for one in h.trace(key) if one.get("kind") == "block"]
        return blocks[-1] if blocks else {}

    def indexes(flow: list[dict], kind: str) -> list[int]:
        return [i for i, one in enumerate(flow) if one.get("kind") == kind]

    # --- open on a parked run, close gives the block below, a name not offered is refused ---------------------
    known = set(keys())
    played, flow = talk(bench.temp() / "sa", command("message", text="hi") + command("open", name="ROOM")
                        + command("close") + command("open", name="NOBODY") + command("quit"),
                        "--door", "HELLO.md", "--documents", str(documents))
    key = fresh(known)
    kinds = [one.get("kind") for one in flow]
    spaces = [one for one in flow if one.get("kind") == "space"]
    verdicts = indexes(flow, "verdict")
    first_space = indexes(flow, "space")[:1]
    conductions = indexes(flow, "conduction")
    principals = indexes(flow, "principal")
    if (played.returncode == 0 and key and len(spaces) >= 2
            and spaces[0].get("name") == "ROOM" and spaces[0].get("open") is True and spaces[0].get("pending") is False
            and (spaces[0].get("spaces") or {}).get("open") == ["ROOM"]
            and first_space and len(verdicts) >= 2 and verdicts[0] < first_space[0] < verdicts[1]
            and any(first_space[0] < one < verdicts[1] for one in conductions)
            and not any(first_space[0] < one < verdicts[1] for one in principals)):
        held("open on a parked run", f"run {key}: space ROOM open with ROOM among the open spaces, then a conduction "
             "and a verdict without a principal's voice -- an exchange without a message")
    else:
        failures.append(f"  ✗ open                        rc={played.returncode} key={key!r} kinds={kinds} spaces={spaces} "
                        f"verdicts={verdicts} principals={principals} err={played.stderr[-300:]!r}")
    served = [one.get("text", "") for i, one in enumerate(flow) if one.get("kind") == "conduction"
              and first_space and len(verdicts) >= 2 and first_space[0] < i < verdicts[1]]
    if served and "WELCOME{" in served[0] and "ROOM{" in served[0] and "greet the principal" in served[0]:
        held("the space's welcome reaches the agent", "the exchange without a message serves the output the open "
             "held: WELCOME and ROOM, W1 in text, at its first launch")
    else:
        failures.append(f"  ✗ the welcome                 {[one for one in (served[:1] or [''])[0].splitlines() if one.startswith('▌ ')][:6]}")
    closed = [one for one in spaces if one.get("open") is False]
    final = last_block(key)
    if (played.returncode == 0 and closed and closed[0].get("name") == "ROOM" and len(verdicts) >= 3
            and (final.get("spaces") or {}).get("open") == [] and final.get("root") == "TURN"):
        held("close gives the block below", f"space ROOM open false, the last block's open [] and root TURN; "
             f"{len(verdicts)} verdicts")
    else:
        failures.append(f"  ✗ close                       closed={closed} final={ {k: final.get(k) for k in ('spaces', 'root', 'stack')} } "
                        f"verdicts={verdicts}")
    refused = [one for one in flow if one.get("kind") == "refused"]
    if (played.returncode == 0 and len(refused) == 1 and refused[0].get("code")
            and "NOBODY" in str(refused[0].get("line", "")) and sum(1 for one in spaces if one.get("name") == "NOBODY") == 0):
        held("a name not offered is refused", f"refused {refused[0].get('code')!r}, nothing opened")
    else:
        failures.append(f"  ✗ not offered                 refused={refused} spaces={spaces}")

    # --- a command during an exchange plays after it ----------------------------------------------------------
    known = set(keys())
    played, flow = talk(bench.temp() / "sb", command("message", text="hi") + command("open", name="ROOM")
                        + command("quit"), "--door", "HELLO.md", "--documents", str(documents))
    key_b = fresh(known)
    verdicts = indexes(flow, "verdict")
    applied = [i for i, one in enumerate(flow) if one.get("kind") == "space" and one.get("pending") is False]
    if played.returncode == 0 and key_b and verdicts and applied and verdicts[0] < applied[0] and len(verdicts) == 2:
        held("a command during an exchange plays after it", f"run {key_b}: the message's verdict at {verdicts[0]}, the "
             f"space applied at {applied[0]}, its own verdict after")
    else:
        failures.append(f"  ✗ during an exchange          rc={played.returncode} verdicts={verdicts} applied={applied} "
                        f"kinds={[one.get('kind') for one in flow]} err={played.stderr[-300:]!r}")

    # --- the verbs say the spaces, on a fresh run parked -----------------------------------------------------------
    known = set(keys())
    talk(bench.temp() / "sc0", command("message", text="hi") + command("quit"),
         "--door", "HELLO.md", "--documents", str(documents))
    key = fresh(known)
    where = bench.temp() / "sc"
    opened = h.call("agent", "open", "agents/ag1", key, "ROOM", "--json", *h.harnessed_at("play", where))
    try:
        told = json.loads(opened.stdout.strip().splitlines()[-1]) if opened.stdout.strip() else {}
    except ValueError:
        told = {}
    shut = h.call("agent", "close", "agents/ag1", key, "--json", *h.harnessed_at("play", where))
    try:
        told_close = json.loads(shut.stdout.strip().splitlines()[-1]) if shut.stdout.strip() else {}
    except ValueError:
        told_close = {}
    if (opened.returncode == 0 and told.get("key") == key and (told.get("spaces") or {}).get("open") == ["ROOM"]
            and told.get("state") == "parked" and shut.returncode == 0
            and (told_close.get("spaces") or {}).get("open") == [] and told_close.get("state") == "parked"):
        held("the verbs say the spaces", f"agent open: {told.get('spaces')}, parked; agent close: open []")
    else:
        failures.append(f"  ✗ the verbs                   rc={opened.returncode}/{shut.returncode} told={told} close={told_close} "
                        f"{opened.stderr[-300:]!r} {shut.stderr[-300:]!r}")

    # --- run-busy under a conversation; a run taken up says its spaces at ready ----------------------------------
    talking = subprocess.Popen([sys.executable, str(h.engine), "--instance", str(h.house), "agent", "chat", "agents/ag1",
                                "--run", key, "--json", *h.harnessed_at("play", bench.temp() / "sd")],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                               cwd=h.ws, env={**os.environ, **h.env})
    assert talking.stdout is not None and talking.stdin is not None
    ready_line = talking.stdout.readline()
    before_busy = (last_block(key).get("spaces") or {}).get("open")
    busy = h.call("agent", "open", "agents/ag1", key, "ROOM", *h.harnessed_at("play", where))
    talking.stdin.close()
    talking.wait(timeout=30)
    try:
        ready = json.loads(ready_line)
    except ValueError:
        ready = {}
    if (ready.get("kind") == "ready" and busy.returncode == 2 and "run-busy" in busy.stderr
            and (last_block(key).get("spaces") or {}).get("open") == before_busy):
        bench.refusals += 1
        held("run-busy under a conversation", "agent open refused run-busy, nothing opened")
    else:
        failures.append(f"  ✗ run-busy                    rc={busy.returncode} ready={ready.get('kind')} {busy.stderr[-300:]!r}")
    if ready.get("kind") == "ready" and set(ready.get("spaces") or {}) == {"open", "openable"} \
            and any(one.get("name") == "ROOM" for one in ready["spaces"]["openable"]):
        held("a run taken up says its spaces at ready", f"ready.spaces {ready.get('spaces')}")
    else:
        failures.append(f"  ✗ ready.spaces               ready={ready}")
    return 0
