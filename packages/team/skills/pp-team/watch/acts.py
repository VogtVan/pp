"""The `watch` domain, layer `acts`: a team followed as it moves.

A definition belongs here when it plays an effect of several steps for the watch: it reads a launch's flow through the
house's console in a thread of its own, or follows the journal and the wake-ups under way until the bound asked, reading
and never writing, and says each event of the journal on the standard error as a line or as JSON (`said_event`). It
may use the lower layers of any domain.

Each line read as the journal grows is decoded once into an event and kept beside the events of the state; the watch
reads it by its fields, and what it says is the line itself (`one.line`). The filter of `--task` reads the task and the
tag on the line, since an event of any kind may carry them. The lines the watch reads before it follows go through
`event_read` and then `read_on`: only the kinds whose body the reader reads are decoded.
"""
from __future__ import annotations

import json
import os
import queue
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

from house.model import Declined
from house.rules import agent_meta, journal_of
from house.store import engine_of, lines_of, now, refuse, tracing
from journal.model import Event
from watch.model import ACTIVITY_DRAIN, ACTIVITY_KINDS, ACTIVITY_RATE, DEFAULT_HEARTBEAT
from wake.rules import open_intents, opened_by, path_of_intent
from journal.faces import event_object, shown
from journal.replay import event_read, read_on, said_so_far
from journal.store import state_of
from watch.rules import quiescent, seconds_of
from watch.faces import activity_line, activity_of


class ActivityReader:
    """The FLOW of one launch the watch follows, read by `agent flow <path> <run> --json --from <rank> --follow`
    in a thread of its own -- the same call as the follower --: from the `opened` of the launch's exchange, found
    by its tag, the events that say what the harness does (`ACTIVITY_KINDS`) come out of `fresh()` as the fields
    of an `activity` object, at most `ACTIVITY_RATE` per second: past that, the latest is HELD and the ones it
    replaces are counted, said with `more` once the second turned or at `close()`; a `context` always passes.
    `done` once the stream ended on its own."""

    def __init__(self, engine: Path, root: Path, path: str, run: str, tag: str, start: int) -> None:
        self.tag, self.opened, self.done = tag, False, False
        self.window: float | None = None             # the instant the current second opened
        self.count = 0                               # the objects said in it
        self.held: dict | None = None                # the latest object past the rate, said when the second turns
        self.dropped = 0                             # the objects it replaced
        self._queue: queue.Queue = queue.Queue()
        self._process = subprocess.Popen([sys.executable, str(engine), "--instance", str(root), "agent", "flow", path, run,
                                          "--json", "--from", str(max(1, start)), "--follow"],
                                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                                         cwd=str(root.parent), env=dict(os.environ))
        self._thread = threading.Thread(target=self._read, daemon=True)
        self._thread.start()

    def _read(self) -> None:
        assert self._process.stdout is not None
        for line in self._process.stdout:
            if line.strip():
                try:
                    self._queue.put(json.loads(line))
                except ValueError:
                    continue
        self._queue.put(None)

    def fresh(self, now: float) -> list[dict]:
        """-> the activity objects to say now: those read since the last call, under the rate, and the held one
        once the second turned."""
        said: list[dict] = []
        while True:
            try:
                one = self._queue.get_nowait()
            except queue.Empty:
                break
            if one is None:
                self.done = True
                break
            kind = one.get("kind")
            if kind == "opened":                     # the launch's own exchange opens here; another closes it
                self.opened = opened_by(one, self.tag)
            elif self.opened and kind in ACTIVITY_KINDS:
                fields = activity_of(str(kind), one)
                said += [fields] if kind == "context" else self._bounded(fields, now)
        return said + self._turned(now)

    def _bounded(self, fields: dict, now: float) -> list[dict]:
        out = self._turned(now)
        if self.window is None or now - self.window >= 1.0:
            self.window, self.count = now, 0
        if self.count < ACTIVITY_RATE - 1:           # the last slot of the second is the held one's
            self.count += 1
            return out + [fields]
        if self.held is not None:
            self.dropped += 1
        self.held = fields
        return out

    def _turned(self, now: float) -> list[dict]:
        """-> the held object once the second turned: it opens the next one."""
        if self.held is None or (self.window is not None and now - self.window < 1.0):
            return []
        self.window, self.count = now, 1
        return [self._flushed()]

    def _flushed(self) -> dict:
        said = {**self.held, **({"more": self.dropped} if self.dropped else {})}
        self.held, self.dropped = None, 0
        return said

    def close(self) -> list[dict]:
        """The stream ended: the process ended when still alive, the held object said. -> what is left to say."""
        if self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._process.kill()
        return [self._flushed()] if self.held is not None else []


def watched(root: Path, conductor, name: str, asked: dict) -> int:
    """`team watch`: the journal and the traces of the wake-ups under way FOLLOWED -- read,
    never written, no lock taken -- until the bound asked, or Ctrl-C. Under `--json` each step of a
    wake-up says the `task`, the `tag` and the `launch` (its rank in the run) of the intent it follows.
    Beside the trace, the FLOW of each wake-up followed is read by its own `agent flow --follow`
    (`ActivityReader`, closed with the wake-up): what the harness does between two blocks is said as
    `activity` objects -- `{at, agent, run, event: activity, kind, task, tag, launch, …}` --, one line
    of text each without `--json`."""
    log = tracing(conductor)
    engine = engine_of(root, conductor)
    journal = journal_of(root, name)
    task = asked["task"]
    as_json = asked["json"]
    try:
        beat = int(seconds_of(asked, "heartbeat", 1) or DEFAULT_HEARTBEAT)
        bound = seconds_of(asked, "for", 0)
    except Declined as declining:
        refuse(str(declining))
    state = state_of(journal)
    tail = log.tail(journal, from_end=True)
    context = said_so_far()                                # what the journal said: the next events said in its words
    for line in lines_of(journal):
        one = event_read(line)
        if one.kind != "snapshot":
            read_on(context, one)
    follows: dict[str, tuple[str, str, object]] = {}      # tag -> (member, run, the run's reader)
    activities: dict[str, ActivityReader] = {}            # tag -> the reader of the launch's flow
    closing: dict[str, float] = {}                        # tag -> when its wake-up ended: its reader drains, then closes
    intents: dict[str, dict] = {str(tag): one for tag, one in state.wake.intents.items()}   # tag -> its wake-intent
    launches: dict[str, dict] = {str(tag): one for tag, one in state.wake.launched.items()}   # tag -> its wake-launched
    started = state.season.started
    members = dict((started.body.agents if started is not None else None) or {})          # name -> the agent's path
    paths = {tag: path_of_intent(state, one) for tag, one in state.wake.intents.items()}   # tag -> path
    tags_of_task: set[str] = {tag for tag, one in state.wake.intents.items() if one.body.task == task}
    for one in open_intents(state):                        # the wake-ups already under way: read on
        launch = state.wake.launched.get(one.body.tag)
        if launch is not None and launch.body.run and (task is None or one.body.tag in tags_of_task):
            follows[one.body.tag] = (one.body.agent, launch.body.run,
                                     log.follow(agent_meta(root, paths[one.body.tag]), launch.body.run, from_end=True))
            activities[one.body.tag] = ActivityReader(engine, root, paths[one.body.tag], str(launch.body.run),
                                                      one.body.tag, int(state.wake.flow.get(str(launch.body.run)) or 0) + 1)
    resumed: set[str] = {tag for tag, one in state.wake.intents.items() if one.body.run}
    opened, still, beats = time.monotonic(), time.monotonic(), 0
    try:
        while True:
            moved = False
            arrived = [Event.of(line) for line in tail.fresh()]   # the journal's new events, decoded once read
            for one in arrived:
                kind = one.kind
                said = read_on(context, one) if kind != "snapshot" else one.line   # what read_on says is the line read
                if kind == "team-started":
                    members = dict(one.body.agents or {})
                if kind == "wake-intent":
                    tag = one.body.tag
                    paths[str(tag)] = str(one.body.path or members.get(one.body.agent, one.body.agent))
                    intents[str(tag)] = one
                    if one.body.task == task:
                        tags_of_task.add(str(tag))
                    if one.body.run:                       # a run resumed: its trace read from its end
                        resumed.add(str(tag))
                if kind == "wake-launched":
                    launches[str(one.body.tag)] = one
                if task is not None and one.line.get("task") != task and one.line.get("tag") not in tags_of_task:
                    continue                               # any kind: the task or the tag its line carries, if any
                if said is not None:
                    said_event(name, said, as_json)
                    moved = True
                if kind == "wake-launched" and one.body.run and one.body.tag not in follows:
                    tag, body = one.body.tag, one.body
                    at = paths.get(str(tag)) or str(members.get(body.agent, body.agent))
                    follows[str(tag)] = (str(body.agent), str(body.run),
                                         log.follow(agent_meta(root, at), str(body.run),
                                                    from_end=str(tag) in resumed))
                    activities[str(tag)] = ActivityReader(engine, root, at, str(body.run), str(tag),
                                                          int(state.wake.flow.get(str(body.run)) or 0) + 1)
            for tag in list(follows):
                agent, run, reader = follows[tag]
                intent, launch = intents.get(tag), launches.get(tag)
                for line, kind, fields in filter(None, map(log.step_of, reader.fresh())):
                    if as_json:                             # the step said with the intent it follows
                        fields = {**fields, "task": intent.body.task if intent is not None else None, "tag": tag,
                                  "launch": launch.body.launch if launch is not None else None}
                    log.said(run, line, kind, fields, as_json, who=agent)
                    moved = True
            now_at = time.monotonic()
            for tag in list(activities):                    # the activity of each launch followed, under the rate
                reader = activities[tag]
                intent, launch = intents.get(tag), launches.get(tag)
                agent, run = (follows.get(tag) or (intent.body.agent if intent is not None else None,
                                                   launch.body.run if launch is not None else None))[:2]
                over = tag in closing and (reader.done or now_at - closing[tag] >= ACTIVITY_DRAIN)
                for fields in reader.fresh(now_at) + (reader.close() if over else []):
                    log.said(str(run), activity_line(fields), "activity",
                             {**fields, "task": intent.body.task if intent is not None else None, "tag": tag,
                              "launch": launch.body.launch if launch is not None else None}, as_json, who=str(agent))
                    moved = True
                if over:
                    del activities[tag], closing[tag]
            if arrived:                                     # a journal at rest is not read again: its state stands
                state = state_of(journal)
            for tag in list(follows):                       # a wake-up over leaves the watch; its flow drains, then closes
                if tag in state.wake.ended:
                    del follows[tag]
                    if tag in activities:
                        closing[tag] = time.monotonic()
            if moved:
                still, beats = time.monotonic(), 0
            elif time.monotonic() - still >= beat * (beats + 1):
                beats += 1
                if as_json:
                    said_event(name, {"at": now(), "kind": "quiet", "seconds": beat * beats}, True)
                else:
                    sys.stderr.write(f"[{datetime.now().strftime('%H:%M:%S')}] {name} · no event for {beat * beats}s\n")
                    sys.stderr.flush()
            if asked["until-done"] and state.season.started is not None and quiescent(state):
                break
            if bound is not None and time.monotonic() - opened >= bound:
                break
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    finally:
        for reader in activities.values():
            reader.close()
    return 0


def said_event(name: str, one: dict, as_json: bool) -> None:
    """One journal event on stderr, as `watch` says it: the line, or the JSON object;
    a `snapshot` is a reader's aid, not a team event, and is never said."""
    if one.get("kind") == "snapshot":
        return
    if as_json:
        text = json.dumps(event_object(name, one), ensure_ascii=False)
    else:
        text = f"[{datetime.now().strftime('%H:%M:%S')}] {name} · {shown(one)}"
    sys.stderr.write(text + "\n")
    sys.stderr.flush()
