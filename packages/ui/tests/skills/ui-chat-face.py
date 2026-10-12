"""Scenario `ui-chat-face` -- the face of a conversation (plan ui, batch la-face-du-flux), async:
- on the real `agent chat --json` and agent's witness harness, `Conversation` reads the flow in the contract's order under `asyncio.run` -- `ready` first, before any message, then `waiting` --, each event with its voice, and the transcript deduces the turns
- `stop()` during an exchange: the harness dies, the verdict says `interrupted`, the next message takes the standing run up
- on the bench's `pp-chat` witness: a kind nobody knows is kept as it is (the house's voice), a line that does not read is `unreadable`, the end is `ended`
- `Dialogue`: two threads, the background one counts what speaks as unread, the activation reads them, the title is the first message
- `close` ends the whole group (batch l-onglet-unique-par-run): the witness made deaf to `quit` and to the end of
  stdin, with a child of its own -- after `close(timeout=0.5)` neither lives
The witness harness of `agent` is BORROWED by its path (its `House`, its modes), never copied.
"""
from __future__ import annotations

import asyncio
import importlib
import json
import os
import shutil
import sys

from conductor import contributions
from tests.harness import SOURCE

SKILL = SOURCE / "packages" / "ui" / "skills" / "pp-ui"
WITNESS = SOURCE / "packages" / "ui" / "tests" / "witness" / "pp-chat"
HOLD = 20.0


class Reader:
    """One task consuming `events()`, the events kept in order; `until(kind)` waits for the
    next event of that kind (or `ended`) to arrive, without polling."""

    def __init__(self, conversation, ended: str) -> None:
        self.events: list = []
        self._ended = ended
        self._cursor = 0                                     # where the next `until` reads from
        self._came = asyncio.Event()
        self.task = asyncio.create_task(self._read(conversation))

    async def _read(self, conversation) -> None:
        async for event in conversation.events():
            self.events.append(event)
            self._came.set()

    async def until(self, kind: str, timeout: float) -> list:
        """-> the events not yet handed over, up to and including the first of `kind` (or
        `ended`) -- the events already read but not yet asked for come first --, or what came
        before `timeout` passed."""
        start = self._cursor
        deadline = asyncio.get_event_loop().time() + timeout
        while True:
            later = self.events[start:]
            hit = next((i for i, one in enumerate(later) if one.kind in (kind, self._ended)), None)
            if hit is not None:
                self._cursor = start + hit + 1
                return later[:hit + 1]
            left = deadline - asyncio.get_event_loop().time()
            if left <= 0 or self.task.done():
                self._cursor = len(self.events)
                return later
            self._came.clear()
            try:
                await asyncio.wait_for(self._came.wait(), left)
            except asyncio.TimeoutError:
                self._cursor = len(self.events)
                return self.events[start:]


async def _until(condition, bound: float = HOLD) -> bool:
    deadline = asyncio.get_event_loop().time() + bound
    while asyncio.get_event_loop().time() < deadline:
        if condition():
            return True
        await asyncio.sleep(0.05)
    return condition()


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    sys.path.insert(0, str(SKILL))
    chat = importlib.import_module("faces.chat")
    dialogue = importlib.import_module("model.dialogue")
    A = contributions.module_at(SOURCE / "packages" / "agent" / "tests" / "engine" / "_agent.py")
    h = A.House(bench)
    ENDED = dialogue.ENDED

    # --- the real verb: two messages and a quit, the flow in the contract's order ----------------
    async def real() -> tuple:
        out_a = bench.temp() / "face-a"
        conv = await chat.Conversation(str(h.ws), "agents/ag1",
                                       flags=[*h.harnessed_at("play", out_a)]).open()
        reader = Reader(conv, ENDED)
        await reader.until("waiting", 30)
        await conv.send("un")
        await reader.until("waiting", 120)
        await conv.send("deux")
        await reader.until("waiting", 120)
        await conv.quit()
        await reader.until(ENDED, 30)
        rc = await conv.close()
        await reader.task
        return conv, reader.events, rc

    conv, events, rc = asyncio.run(real())
    transcript = dialogue.Transcript()
    for one in events:
        transcript.add(one)
    kinds = [one.kind for one in events]
    first = kinds[kinds.index("principal"):kinds.index("response")] if "response" in kinds else []
    turns = transcript.turns
    if (kinds[:3] == ["ready", "waiting", "opened"] and kinds.count("principal") == 2 and kinds.count("conduction") == 4
            and kinds.count("agent") == 4 and kinds.count("response") == 2 and kinds.count("verdict") == 2
            and first.count("conduction") == 2 and first.count("agent") == 2
            and "closed" in kinds and kinds[-1] == ENDED and events[-1].fields.get("rc") == 0 and rc == 0
            and conv.ended and not conv.alive
            and all(one.at and one.run for one in events if not one.own and one.kind not in ("ready", "waiting"))
            and len(turns) == 2 and [t.message for t in turns] == ["un", "deux"]
            and [len(t.launches) for t in turns] == [4, 4] and all(t.state == "parked" for t in turns)
            and transcript.current is None):
        held("the face reads the flow in order, async", f"{len(events)} events under asyncio.run: ready, waiting, opened, "
             "then per exchange principal, conduction and agent per launch (2 then 2: the boot whole), response, verdict parked, "
             "waiting; closed, ended rc 0; two turns deduced with their launches and verdicts")
    else:
        failures.append(f"  ✗ the flow                    rc={rc} kinds={kinds} turns={[(t.message, len(t.launches), t.state) for t in turns]} "
                        f"stderr={events[-1].fields.get('stderr', '')[-200:] if events else ''!r}")

    principals = [one for one in events if one.kind == "principal"]
    conductions = [one for one in events if one.kind == "conduction"]
    agents = [one for one in events if one.kind == "agent"]
    if (principals and principals[0].fields.get("text") == "un" and principals[0].voice == "principal"
            and conductions and all(str(one.fields.get("text", "")).startswith("▌ pp · run") for one in conductions)
            and all(one.voice == "conduction" for one in conductions)
            and agents and all(one.fields.get("text") == "witness answer: play" for one in agents)
            and all(isinstance(one.fields.get("cost_usd"), (int, float)) for one in agents)
            and conv.command[0] == str(h.ws / "pp")
            and conv.command[1:5] == ["agent", "chat", "agents/ag1", "--json"] and "--harness" in conv.command):
        held("the three voices and the command", "principal = the message, conduction opens on pp's heading, "
             "agent = the witness's answer with its cost; the command is `<house>/pp agent chat agents/ag1 --json …`")
    else:
        failures.append(f"  ✗ voices                      {[o.fields.get('text') for o in principals]} "
                        f"{[str(o.fields.get('text', ''))[:30] for o in conductions]} "
                        f"{[o.fields.get('text') for o in agents]} {conv.command[:5]}")

    # --- stop during an exchange: the harness dies, interrupted, the standing run taken up -----------
    async def stopped() -> tuple:
        out_b = bench.temp() / "face-b"
        paused = await chat.Conversation(str(h.ws), "agents/ag1",
                                         flags=[*h.harnessed_at("pause", out_b), "--quiet"]).open()
        reader = Reader(paused, ENDED)
        await reader.until("waiting", 30)
        await paused.send("think")
        shown = await _until(lambda: bool(h.read(".pid", out_b)))
        pid = int(h.read(".pid", out_b) or 0)
        await paused.stop()
        seen = await reader.until("verdict", 60)
        dead = await _until(lambda: not A.alive(pid)) if pid else False
        await reader.until("waiting", 30)
        await paused.send("go on")
        later = await reader.until("verdict", 120)
        await reader.until("waiting", 30)
        rc_b = await paused.close()
        await reader.task
        return shown, dead, seen, later, rc_b

    shown, dead, seen, later, rc_b = asyncio.run(stopped())
    verdicts = [one for one in seen + later if one.kind == "verdict"]
    opened = [one for one in later if one.kind == "opened"]
    if (shown and dead and len(verdicts) == 2 and verdicts[0].fields.get("state") == "interrupted"
            and verdicts[1].fields.get("state") == "parked" and opened and opened[0].fields.get("standing") is True
            and rc_b == 0):
        held("stop interrupts, the next message resumes", "the pause witness killed, verdict interrupted, "
             "then opened.standing and a verdict parked; close -> rc 0")
    else:
        failures.append(f"  ✗ stop                        shown={shown} dead={dead} "
                        f"verdicts={[o.fields.get('state') for o in verdicts]} opened={[o.fields for o in opened]} rc={rc_b}")

    # --- the bench's witness: what the real verb never says -------------------------------------
    faces = bench.temp() / "faces"
    faces.mkdir(exist_ok=True)
    shutil.copy(WITNESS, faces / "agent")
    (faces / "agent").chmod(0o755)
    script = bench.temp() / "chat-script.json"
    script.write_text(
        '{"exchanges": [[{"kind": "opened", "agent": "agents/ag1", "exchange": 1}, '
        '{"kind": "principal", "exchange": 1, "text": "hi"}, {"kind": "wobble", "x": 1}, {"raw": "not json"}, '
        '{"kind": "verdict", "exchange": 1, "state": "parked", "launches": 1}, {"kind": "waiting"}]]}',
        encoding="utf-8")

    async def witnessed_flow() -> tuple:
        witnessed = await chat.Conversation(str(h.ws), "agents/ag1").open()
        reader = Reader(witnessed, ENDED)
        await reader.until("waiting", 10)
        await witnessed.send("hi")
        await reader.until("waiting", 10)
        await witnessed._write({"kind": "dance"})            # a command nobody knows: the flow refuses and goes on
        await reader.until("refused", 10)
        await witnessed.quit()
        await reader.until(ENDED, 10)
        rc_c = await witnessed.close()
        await reader.task
        return witnessed, reader.events, rc_c

    os.environ["PP_UI_FACES"] = str(faces)
    os.environ["PP_UI_CHAT_SCRIPT"] = str(script)
    try:
        witnessed, got, rc_c = asyncio.run(witnessed_flow())
    finally:
        del os.environ["PP_UI_FACES"]
        del os.environ["PP_UI_CHAT_SCRIPT"]
    kinds_c = [one.kind for one in got]
    wobble = next((one for one in got if one.kind == "wobble"), None)
    unreadable = next((one for one in got if one.kind == "unreadable"), None)
    if (witnessed.command[0] == str(faces / "agent") and kinds_c[0] == "waiting"
            and wobble is not None and wobble.voice == "house" and wobble.fields == {"x": 1}
            and unreadable is not None and unreadable.fields == {"line": "not json"} and unreadable.own
            and "refused" in kinds_c and kinds_c[-2:] == ["closed", ENDED] and got[-1].fields.get("rc") == 0 and rc_c == 0):
        held("the witness says what the real verb never does", "a kind nobody knows kept as it is (the house's "
             "voice), a line that does not read -> unreadable, a bad command -> refused, closed then ended rc 0")
    else:
        failures.append(f"  ✗ witness                     {kinds_c} {wobble} {unreadable} rc={rc_c} {witnessed.command[:2]}")

    # --- the dialogue: two threads, the unread of the background one, the title ----------------------
    Event, Thread, Dialogue = dialogue.Event, dialogue.Thread, dialogue.Dialogue
    post = Dialogue()
    a = post.open(Thread("ag1"))
    b = post.open(Thread("ag2"))
    for one in got:                                           # the witness's flow lands on the background thread
        post.take(b, one)
    before = list(post.lines())
    unread_b = post.threads[b].unread
    active_a = post.active == a
    post.activate(b)
    after = list(post.lines())
    post.take(a, Event.read('{"kind": "verdict", "at": "2026-10-08T09:00:04+00:00", "run": "k1", "exchange": 1, "state": "parked"}'))
    closed = post.close(a)
    if (active_a and unread_b == 3 and before[b] == "ag2 · run w00001 · ended rc 0 · " + got[-2].at[11:19] + " · 3 unread · hi"
            and post.threads[0].unread == 0 and after[b].endswith(" · hi") and "unread" not in after[b]
            and post.threads[0].title == "hi" and post.active == 0 and closed.agent == "ag1"
            and closed.unread == 1 and closed.state == "parked" and closed.line == "ag1 · run k1 · parked · 09:00:04 · 1 unread"):
        held("the dialogue counts the unread of a background thread", "the first thread opened is active; on the "
             "second, the witness's flow counts 3 unread (the verdict, the refusal, the end), the title is `hi`; "
             "activation reads them; closing the first leaves the second active")
    else:
        failures.append(f"  ✗ dialogue                    active_a={active_a} unread={unread_b} before={before} after={after} "
                        f"closed={closed.line!r} active={post.active}")

    # --- close ends the whole group: a witness deaf to quit, and its child ----------------------------
    pids = bench.temp() / "deaf.pids"
    deaf_script = bench.temp() / "deaf-script.json"
    deaf_script.write_text(json.dumps({"deaf": str(pids)}), encoding="utf-8")

    async def deaf() -> tuple:
        heard = await chat.Conversation(str(h.ws), "agents/ag1").open()
        reader = Reader(heard, ENDED)
        await reader.until("waiting", 10)
        written = await _until(lambda: pids.is_file() and len(pids.read_text().split()) == 2, 10)
        rc_d = await heard.close(timeout=0.5)
        return written, rc_d

    os.environ["PP_UI_FACES"] = str(faces)
    os.environ["PP_UI_CHAT_SCRIPT"] = str(deaf_script)
    try:
        written, rc_d = asyncio.run(deaf())
    finally:
        del os.environ["PP_UI_FACES"]
        del os.environ["PP_UI_CHAT_SCRIPT"]
    parent, child = (int(one) for one in pids.read_text().split()) if written else (0, 0)
    gone = asyncio.run(_until(lambda: not A.alive(parent) and not A.alive(child), 5)) if written else False
    if written and gone:
        held("close ends the whole group", f"the deaf witness (pid {parent}) and its child (pid {child}) both gone after "
             f"close(timeout=0.5), rc {rc_d}")
    else:
        failures.append(f"  ✗ close the group             written={written} parent={parent} alive={A.alive(parent) if parent else None} "
                        f"child={child} alive={A.alive(child) if child else None} rc={rc_d}")
    return 0
