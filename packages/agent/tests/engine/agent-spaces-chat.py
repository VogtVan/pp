"""Scenario `agent-spaces-chat` -- the SPACES a principal opens and closes on a run (batch les-espaces-au-flux, agent
0.37.0): the commands `open` and `close` of `agent chat --json`, the verbs `agent open` and `agent close`, on a house
pinning `agent`, the run opened on the door HELLO (one WORK) with an overlay of TURN that offers the space ROOM at
every block (`--door`, `--documents`, as the campaign's root `space` lays them):
- open on a parked run, with its message (agent 1.0.1, s.1415): `{"kind": "open", "name": "ROOM", "text": "into the
  room"}` after the first exchange says `space {name: ROOM, open: true, pending: false, spaces}` -- `spaces.open`
  holding ROOM --, then ONE exchange of that message: one `opened`, the `principal` voice saying the text, a
  `conduction` and a `verdict` -- launched on ROOM's block, which parks the run in ROOM; the message is on record
- an open without a text (agent 1.0.34, batch les-espaces-sans-overlay) opens the space, then ONE exchange without a
  message, as `close` does: `space {name: ROOM, open: true}`, then a verdict, no `principal` voice between them;
  a `close` after it leaves the run as the first close did
- the space's welcome reaches the agent: ROOM's welcome (WELCOME, attached at its entry, under its law W1) fuses
  with ROOM's step; the exchange of the open's message serves both, the law in text, at its first launch
- close gives the block below: `{"kind": "close"}` says `space {name: ROOM, open: false}`, then the trace's last block
  says `spaces.open = []`
- a name not offered is refused: `{"kind": "open", "name": "NOBODY", "text": …}` says `refused` with the engine's code,
  nothing opened
- a command during an exchange plays after it: `message` then `open` written together -- the `space` object comes
  after the message's `verdict`, never before
- the verbs say the spaces: `agent open agents/ag1 <key> ROOM --json` says `{key, spaces, state}` with ROOM open and
  the run parked; `agent close agents/ag1 <key> --json` says `open: []`
- run-busy: under a conversation holding the run, `agent open` refuses `run-busy` and plays nothing
- a run taken up knows the spaces: `chat --run <key> --json` says `ready.spaces` with `open` and `openable`
- the verbs refuse before they launch: `agent open` without a key, without a name or with a message is refused
  with the usage, `agent close` on an unknown run `run-unknown`, `agent open` of a name not offered by the engine's
  code relayed -- nothing launched, nothing opened
- without `--json` the verbs say one line naming the run; `agent open` under a harness that dies after the gesture
  is refused, exit 2, no response kept; `agent close` under a harness that answers then dies says its line, keeps
  the response and exits 2
- an `open` said before any run of a conversation is refused `run-missing`, no run opened
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
INTO = "into the room"                                   # the message an open carries


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
    played, flow = talk(bench.temp() / "sa", command("message", text="hi") + command("open", name="ROOM", text=INTO)
                        + command("close") + command("open", name="NOBODY", text="nobody")
                        + command("open", name="ROOM") + command("close") + command("quit"),
                        "--door", "HELLO.md", "--documents", str(documents))
    key = fresh(known)
    kinds = [one.get("kind") for one in flow]
    spaces = [one for one in flow if one.get("kind") == "space"]
    verdicts = indexes(flow, "verdict")
    first_space = indexes(flow, "space")[:1]
    conduction_events = indexes(flow, "conduction")
    principals = indexes(flow, "principal")
    between = [one for i, one in enumerate(flow) if first_space and len(verdicts) >= 2
               and first_space[0] < i < verdicts[1]]
    said = [one.get("text") for one in between if one.get("kind") == "principal"]
    recorded = [one.get("message") for one in h.messages() if one.get("run") == key]
    if (played.returncode == 0 and key and len(spaces) >= 2
            and spaces[0].get("name") == "ROOM" and spaces[0].get("open") is True and spaces[0].get("pending") is False
            and (spaces[0].get("spaces") or {}).get("open") == ["ROOM"]
            and first_space and len(verdicts) >= 2 and verdicts[0] < first_space[0] < verdicts[1]
            and any(first_space[0] < one < verdicts[1] for one in conduction_events)
            and sum(1 for one in between if one.get("kind") == "opened") == 1 and said == [INTO]
            and INTO in recorded):
        held("open on a parked run, with its message", f"run {key}: space ROOM open with ROOM among the open spaces, "
             f"then ONE exchange: the principal says {said[0]!r}, a conduction, a verdict")
    else:
        failures.append(f"  ✗ open                        rc={played.returncode} key={key!r} kinds={kinds} spaces={spaces} "
                        f"verdicts={verdicts} principals={principals} said={said} recorded={recorded} "
                        f"err={played.stderr[-300:]!r}")
    unread = [one for one in flow if one.get("kind") == "refused" and one.get("code") == "command-unreadable"]
    bare = [i for i, one in enumerate(flow) if one.get("kind") == "space" and one.get("open") is True][1:2]
    after = [i for i in verdicts if bare and i > bare[0]][:1]
    voiced = [one for i, one in enumerate(flow) if bare and after and bare[0] < i < after[0]
              and one.get("kind") == "principal"]
    if (played.returncode == 0 and unread == [] and bare and flow[bare[0]].get("name") == "ROOM"
            and flow[bare[0]].get("pending") is False and after and voiced == []):
        held("an open without a text opens, then one exchange without a message", f"space ROOM open at {bare[0]}, "
             f"its verdict at {after[0]}, no principal voice between")
    else:
        failures.append(f"  ✗ open without a text         unread={unread} spaces={spaces} verdicts={verdicts}")
    served = [one.get("text", "") for i, one in enumerate(flow) if one.get("kind") == "conduction"
              and first_space and len(verdicts) >= 2 and first_space[0] < i < verdicts[1]]
    first = (served[:1] or [""])[0].splitlines()
    heads = [one for one in first if one.startswith("▌ ") and "{" in one]
    steps = [one.rsplit("(", 1)[-1].rstrip(")") for one in first
             if one.startswith(("INFER ", "WORK ")) and one.endswith(")")]
    if (served and len(heads) == 1 and "WELCOME{" in heads[0] and steps == ["WELCOME", "ROOM"]
            and "greet the principal" in served[0]):
        held("the space's welcome reaches the agent", "the exchange of the open's message serves the output the "
             f"open held: one segment, `{heads[0]}`, WELCOME's step then ROOM's, a line each, W1 in text, at its "
             "first launch")
    else:
        failures.append(f"  ✗ the welcome                 heads={heads} steps={steps} "
                        f"{[one for one in first if one.startswith(('INFER ', 'WORK '))]}")
    closed = [one for one in spaces if one.get("open") is False]
    final = last_block(key)
    if (played.returncode == 0 and closed and closed[0].get("name") == "ROOM" and len(verdicts) >= 3
            and (final.get("spaces") or {}).get("open") == [] and final.get("root") == "TURN"):
        held("close gives the block below", f"space ROOM open false, the last block's open [] and root TURN; "
             f"{len(verdicts)} verdicts")
    else:
        failures.append(f"  ✗ close                       closed={closed} final={ {k: final.get(k) for k in ('spaces', 'root', 'stack')} } "
                        f"verdicts={verdicts}")
    refused = [one for one in flow if one.get("kind") == "refused" and one.get("code") != "command-unreadable"]
    not_offered = refused[0].get("code") if refused else ""       # the engine's code for a name it does not offer
    if (played.returncode == 0 and len(refused) == 1 and refused[0].get("code")
            and "NOBODY" in str(refused[0].get("line", "")) and sum(1 for one in spaces if one.get("name") == "NOBODY") == 0):
        held("a name not offered is refused", f"refused {refused[0].get('code')!r}, nothing opened")
    else:
        failures.append(f"  ✗ not offered                 refused={refused} spaces={spaces}")

    # --- a command during an exchange plays after it ----------------------------------------------------------
    known = set(keys())
    played, flow = talk(bench.temp() / "sb", command("message", text="hi") + command("open", name="ROOM", text=INTO)
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

    # --- the verbs refuse before they launch ---------------------------------------------------------------------
    play, usage = h.harnessed_at("play", where), f"pp-agent: {A.skill().USAGE}"
    before_v = (h.counted(), (last_block(key).get("spaces") or {}).get("open"))
    unplayed = {"no key": h.call("agent", "open", "agents/ag1"), "no name": h.call("agent", "open", "agents/ag1", key),
                "a message": h.call("agent", "open", "agents/ag1", key, "ROOM", "--message", "x", *play),
                "an unknown run": h.call("agent", "close", "agents/ag1", "zzzzzz", *play),
                "a name not offered": h.call("agent", "open", "agents/ag1", key, "NOBODY", *play)}
    said_v = {what: one.stderr.strip() for what, one in unplayed.items()}
    known_v = set(keys())
    _, early = talk(bench.temp() / "se", command("open", name="ROOM", text="before any run") + command("quit"),
                    "--door", "HELLO.md", "--documents", str(documents))
    early_codes = [one.get("code") for one in early if one.get("kind") == "refused"]
    if (all(one.returncode == 2 and not one.stdout for one in unplayed.values())
            and [said_v[what] == usage for what in ("no key", "no name", "a message")] == [True] * 3
            and said_v["an unknown run"].startswith("pp-agent: run-unknown ")
            and not_offered and said_v["a name not offered"].startswith(f"pp-agent: {not_offered} ")
            and early_codes == ["run-missing"] and set(keys()) == known_v
            and (h.counted(), (last_block(key).get("spaces") or {}).get("open")) == before_v):
        bench.refusals += 5
        held("the verbs refuse before they launch", "agent open without a key, without a name, with a message: the "
             f"usage; agent close on an unknown run: run-unknown; agent open NOBODY: {not_offered}, the engine's "
             "refusal relayed; an open said before any run of a conversation: run-missing; nothing launched, "
             "nothing opened")
    else:
        failures.append(f"  ✗ the verbs refuse            rc={[one.returncode for one in unplayed.values()]} "
                        f"said={ {what: text[:90] for what, text in said_v.items()} } code={not_offered!r} "
                        f"early={early_codes} "
                        f"moved={(h.counted(), (last_block(key).get('spaces') or {}).get('open'))}/{before_v}")

    # --- without --json the verbs say one line; a launch that dies after the gesture is refused -------------------
    opened_t = h.call("agent", "open", "agents/ag1", key, "ROOM", *play)
    closed_t = h.call("agent", "close", "agents/ag1", key, *play)
    answered_v = h.counted()[0]
    died = h.call("agent", "open", "agents/ag1", key, "ROOM", *h.harnessed_at("crash", where))
    halved = h.call("agent", "close", "agents/ag1", key,           # a witness at its first launch: it answers, then dies
                    *h.harnessed_at("crash1", bench.temp() / "sf"))
    lines_t = [one.stdout.splitlines() for one in (opened_t, closed_t)]
    if (opened_t.returncode == 0 and closed_t.returncode == 0 and [len(one) for one in lines_t] == [1, 1]
            and all(key in one[0] and not one[0].startswith("{") for one in lines_t) and "ROOM" in lines_t[0][0]
            and died.returncode == 2 and not died.stdout and halved.returncode == 2
            and len(halved.stdout.splitlines()) == 1 and h.counted()[0] == answered_v + 1):
        held("the verbs say one line, a dead launch is refused", "agent open and agent close without --json: one "
             "line naming the run, ROOM at the open; agent open under a harness that dies: exit 2, no response "
             "kept; agent close under a harness that answers then dies: its line, its response kept, exit 2")
    else:
        failures.append(f"  ✗ the verbs' line             rc={opened_t.returncode}/{closed_t.returncode}/{died.returncode} "
                        f"lines={lines_t} {opened_t.stderr[-160:]!r} died={died.stderr[-200:]!r} "
                        f"halved={halved.returncode} {halved.stdout[:120]!r} {halved.stderr[-200:]!r} "
                        f"answered={h.counted()[0]}/{answered_v}")
    return 0
