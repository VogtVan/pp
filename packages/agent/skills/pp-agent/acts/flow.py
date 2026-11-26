"""The flow of an exchange: its events said and kept, the harness followed while it plays, the voices summed."""
from __future__ import annotations

import json
import subprocess
import tempfile
import time
from pathlib import Path

from model.flow import Sums
from model.exchange import Final, Issue, Said
from model.words import ASIDE, FINAL, FLOW_VOICES, HAND_BACK
from rules.flow import pp_called
from rules.verdict import verdict_of
from store.clock import now
from store.records import flow_of

TERMINATE_WAIT = 5              # seconds an interrupted harness gets to end on SIGTERM before SIGKILL

CALLS = ("tool", "tool-result", "thinking", "words", ASIDE, FINAL, "context")   # what a launch does, read on the
# harness's output as it comes -- `words`, a production pp took; `aside`, a text the harness wrote that a call
# follows; `final`, the launch's last message, its text and its length; `context`, what one call sent the model,
# measured where the provider counts it
VOICES = ("opened", "principal", "conduction", "agent") + CALLS   # what a conversation's flow says beside the run's
# steps: the house opening a run, the principal's message, pp's output served to the harness, the harness's answer,
# and what the harness does during a launch -- a call of a tool, its result, a thought, words
FLOW = VOICES + ("ready", "response", "verdict", "waiting", "refused", "closed", "policy", "conduct", "package",
                 "space")   # every kind of the flow but `step`


def step_sayer(log, as_json: bool):
    """-> the `say` of a wake-up watched from stderr: every step of the run or of the house
    said by the engine's `log.said` -- one line each, text or JSON --, the VOICES of a
    conversation (what a flow alone renders) left unsaid."""
    def say(key: str, line: str, kind: str, fields: dict) -> None:
        if kind not in VOICES:
            log.said(key, line, kind, fields, as_json)
    return say


def event_of(key: str | None, kind: str, fields: dict) -> dict:
    """-> one event of a flow: `kind`, `at` and `run` first -- a voice or a house's word under its own kind,
    a step of the run or of the house under `step` with its `event`."""
    if kind in FLOW:
        return {"kind": kind, "at": now(), "run": key or None, **fields}
    return {"kind": "step", "at": now(), "run": key or None, "event": kind, **fields}


def event_sayer(stream):
    """-> the `say` of a conversation's FLOW: one JSON object per line on `stream` (`event_of`) -- a voice
    under its own kind (`opened`, `principal`, `conduction`, `agent`), a step of the run or of the house
    under `step` with its `event` and its fields, the grammar `run --json` says on stderr. Its `told`
    prints an event already built: the very object a keeper kept."""
    def told(event: dict) -> None:
        print(json.dumps(event, ensure_ascii=False), file=stream, flush=True)

    def say(key: str, line: str, kind: str, fields: dict) -> None:
        told(event_of(key, kind, fields))
    say.told = told
    return say


def keeper(root: Path, name: str, say):
    """-> `say` wrapped by the KEEPER of the run's flow: every event it receives -- voices and steps, before
    the caller chooses what to say of it -- appended to the run's flow file (`flow_of`), one JSON line each,
    then handed on: the very object to a flow's `told`, the words as they came to any other `say`. Its
    `recorded` keeps an event without saying it -- the end of an exchange `run` never says on stderr. One
    writer per run at a time: the one that holds its wake lock."""
    def kept(key: str | None, kind: str, fields: dict) -> dict:
        event = event_of(key, kind, fields)
        if key:
            path = flow_of(root, name, key)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        return event

    def wrapped(key: str, line: str, kind: str, fields: dict) -> None:
        event = kept(key, kind, fields)
        told = getattr(say, "told", None)
        if told is not None:
            told(event)
        else:
            say(key, line, kind, fields)
    wrapped.told = getattr(say, "told", None)
    wrapped.recorded = lambda key, kind, fields: kept(key, kind, fields) and None
    return wrapped


def flow_closed(issue: Issue, keep, reason: str | None) -> None:
    """Keeps the end of an exchange in its run's flow, by the keeper `exchange` handed back -- `response` when
    one was kept, then `verdict` -- without saying it: for `run`, `start` and the text of `chat`, whose stderr
    says the verdict its own way."""
    if keep is None or not issue.key:
        return
    if issue.kept is not None:
        keep.recorded(issue.key, "response", {**issue.kept.json(), "session": issue.account.session,
                                              "state": issue.said})
    keep.recorded(issue.key, "verdict", verdict_of(issue, reason))


def followed(trace, log, key: str, say, kept: list | None) -> int:
    """Reads what the run's trace gained: each event kept RAW in `kept` (when given), each step
    `say`d. -> the count of steps said."""
    fresh = trace.fresh()
    if kept is not None:
        kept.extend(fresh)
    steps = [one for one in map(log.step_of, fresh) if one is not None]
    for line, kind, fields in steps:
        say(key, line, kind, fields)
    return len(steps)


def waited(argv: list[str], cwd: Path, environment: dict, trace, key: str,
           beat: int, say, log, stdin: str = "", kept: list | None = None, heard=None) -> subprocess.CompletedProcess:
    """-> the harness's play, once it ends: the prompt written on its standard input and
    the input closed, its streams kept in files (never a pipe it could fill), and, while
    it plays, every 0.2 s: each COMPLETE line its standard output gained handed to `heard`
    (a line still being written waits for its end), and the run's trace followed by the engine's
    reader -- one step `say`d at a time, one more after every `beat` seconds without one, the events
    read kept raw in `kept`. Without a trace to follow (`--quiet`) the steps are not followed; with
    neither, it waits. The whole output is rendered at the end. The prompt rides stdin and never the
    line: an argument is bounded, a prompt is bounded by the model alone."""
    with tempfile.TemporaryDirectory() as scratch, tempfile.TemporaryFile() as err, \
            tempfile.TemporaryFile() as fed:
        fed.write(stdin.encode("utf-8"))               # a file, never a pipe: the harness reads at its pace
        fed.seek(0)
        written = Path(scratch) / "stdout"
        with open(written, "wb") as out, open(written, "rb") as reading:   # two handles: two offsets
            process = subprocess.Popen(argv, cwd=str(cwd), env=environment, stdin=fed, stdout=out, stderr=err)
            rest = b""

            def lines(last: bool = False) -> None:
                nonlocal rest
                rest += reading.read()
                *whole, rest = rest.split(b"\n")
                if last and rest:
                    whole, rest = whole + [rest], b""
                for one in whole:
                    heard(one.decode("utf-8", "replace"))

            try:
                if trace is None and heard is None:
                    process.wait()
                else:
                    still, beats = time.monotonic(), 0
                    while True:
                        ended = process.poll() is not None
                        if heard is not None:
                            lines()
                        if trace is not None:
                            steps = followed(trace, log, key, say, kept)
                            if steps:
                                still, beats = time.monotonic(), 0
                            elif time.monotonic() - still >= beat * (beats + 1):
                                beats += 1
                                say(key, f"no event for {beat * beats}s", "quiet", {"seconds": beat * beats})
                        if ended:
                            break
                        time.sleep(0.2)
                    if heard is not None:
                        lines(last=True)
            except KeyboardInterrupt:              # the launcher is interrupted: the harness goes with it, no orphan
                process.terminate()
                try:
                    process.wait(TERMINATE_WAIT)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                raise
            reading.seek(0)
            printed = reading.read()
        err.seek(0)
        return subprocess.CompletedProcess(argv, process.returncode, printed.decode("utf-8", "replace"),
                                           err.read().decode("utf-8", "replace"))


def hearer(conductor, meta: Path, grammar: str, key: str, say, exchange_no: int, launch: int, flow=None,
           window: int | None = None, captures=None):
    """-> the `heard` of ONE launch: each line of the harness's output read by the engine's READER of
    the adapter of `grammar` (`conductor.adapters.reader`: the pieces a host streams come out as whole
    texts), each event in the common schema said under its own kind with `exchange` and `launch` -- a
    `tool` also says `pp`, whether its `shell` calls the agent's console (`./pp`, or the console by its
    absolute path), a `context` its `window` -- the window of the launch's model, None unknown -- and the part
    of it `used` -- and counted by `flow` when one is given. A text of the harness is HELD until the launch
    says what follows it: a `tool` makes it an `aside`, a text written between two calls, kept apart; the end
    of the launch makes it the last message, said as `final`: its `text`, its blanks stripped, and `chars`, the
    length of that text -- the hand-back mark alone counts none and carries no `text`, blanks alone an empty
    one. At the result of a call of the console ONE
    production pp took and no result rendered yet -- the oldest the run's trace holds (`captures`) -- is said as
    `words`, as the trace holds it: a capture stands where its call ended, whenever the house reads that result,
    and leaves the input of that call in the flow's sums (`Flow.handed`). A line the face refuses (`events-malformed`)
    is said as a `refusal` step and the reading goes on: a call badly told does not end a launch.
    `heard.end()` is owed once the launch is over: the texts the reader still holds are read, every capture
    no result brought is said, then the last message. `heard.cut()` is owed to a launch interrupted: the
    captures no result brought and the texts held are said the same way -- a text no call follows is a last
    message --, what the reader holds in pieces left unread."""
    console = str(conductor.adapters.console_of(meta.parent))
    reading = conductor.adapters.reader(grammar, meta)
    held: list[dict] = []           # the texts of the harness nothing followed yet
    piped: set[str] = set()         # the calls of the console under way, by their id

    def said(kind: str, one: dict) -> None:
        if flow is not None:
            flow.heard(kind, one)
        say(key, "", kind, {"exchange": exchange_no, "launch": launch, **one})

    def released(kind: str) -> None:
        for one in held:
            said(kind, one)
        held.clear()

    def finished() -> None:
        # the texts no call followed are the launch's last message: its text and its length; the hand-back mark
        # alone says nothing
        if not held:
            return
        text = "\n\n".join(one for one in (str(each.get("text") or "").strip() for each in held) if one)
        held.clear()
        said(FINAL, {"chars": 0} if text == HAND_BACK else {"chars": len(text), "text": text})

    def captured(call: str | None = None) -> None:
        # a print call hands one production: its result brings one capture, the oldest; the end brings the rest
        for text in (captures(None if call is None else 1) if captures is not None else ()):
            if flow is not None and call is not None:
                flow.handed(call, text)
            said("words", {"text": text})

    def told(found: list[dict]) -> None:
        for one in found:
            kind = one.pop("kind")
            if kind == "words":
                held.append(one)
                continue
            if kind == "tool":
                one["pp"] = pp_called(one.get("shell"), console)
                if one["pp"]:
                    piped.add(str(one.get("id")))
                released(ASIDE)
            if kind == "context":
                one.update(window=window, used=round(one["tokens"] / window, 4) if window else None)
            said(kind, one)
            if kind == "tool-result" and str(one.get("id")) in piped:
                captured(str(one.get("id")))

    def heard(line: str) -> None:
        try:
            found = reading.heard(line)
        except conductor.Refusal as refusal:
            say(key, f"refused {refusal.code}", "refusal", {"code": refusal.code, "detail": str(refusal)})
            return
        told(found)

    def cut() -> None:
        captured()
        finished()

    def end() -> None:
        told(reading.end())
        cut()
    heard.end, heard.cut = end, cut
    return heard


class Flow:
    """What the flow of ONE exchange carries, summed by voice in tokens -- the engine's estimate
    (`conductor.metrics.tokens`, the rule of `-stats`): `principal` what a prompt carries beside pp's
    output (the head, the message), `conduction` pp's output served, `pp_input` and `pp_result` the
    calls of the agent's console and their results (paired by `id`) -- a production a call handed left out of
    its input: it is counted once, among the words --, `tool_input` and `tool_result`
    the other tools', `words` the model's text -- the productions pp took, kept in `words`, and its asides,
    summed and not kept --, `thinking` its thought (its text estimated, or the tokens the host counts); the last
    message of each launch is no voice: its text and its length are kept, in `finals`; `calls` the calls to
    the model -- one per launch, one more per call of a tool; `context`, present once a call was measured,
    what the last measured call sent the model, as its provider counts it. `sums` is what the record keeps;
    `sent` what every measured call sent the model, each message once by its id, None while no call was measured."""

    def __init__(self, tokens) -> None:
        self.tokens = tokens
        self.sums = {voice: 0 for voice in FLOW_VOICES}
        self.sums["calls"] = 0
        self.piped: dict[str, int] = {}  # the calls of the console by their id: what their input still counts
        self.launches = 0
        self.words: list[Said] = []      # every `words` of the exchange, `{launch, text}`, in order -- a production
                                         # pp took: the matter `response` is composed of (`composed`)
        self.finals: list[Final] = []    # the last message of each launch that said one: its length, its text
        self.measured: dict[str, int] = {}  # the measured calls by their message's id: what each sent the model

    def summed(self) -> Sums:
        """-> the sums as they stand, frozen: what a record keeps of the exchange's flow."""
        return Sums(**self.sums)

    def sent(self) -> int | None:
        """-> the tokens the exchange's calls sent the model, summed: one count per message, None unmeasured."""
        return sum(self.measured.values()) if self.measured else None

    def launch(self, prompt: str, output: str) -> None:
        """A launch on `prompt`, whose tail is pp's `output` (empty for a bare exchange)."""
        self.sums["calls"] += 1
        self.launches += 1
        self.sums["conduction"] += self.tokens(output) if output else 0
        self.sums["principal"] += self.tokens(prompt[:len(prompt) - len(output)])

    def handed(self, call: str, text: str) -> None:
        """A production the console's call `call` handed, as the trace holds it: its tokens leave the input of
        that call -- no more than the call still counts --, the `words` that say it count them."""
        taken = min(self.tokens(text), self.piped.get(call, 0))
        self.piped[call] = self.piped.get(call, 0) - taken
        self.sums["pp_input"] -= taken

    def heard(self, kind: str, one: dict) -> None:
        """One event of the launch as its hearer says it (`pp` already said on a `tool`): a `words` -- a
        production as the trace holds it -- kept under its launch, its text untouched; an `aside` summed with the
        model's text and kept nowhere; a `final`, the launch's last message, kept with its length and its text --
        none for the hand-back mark alone."""
        if kind == "tool":
            self.sums["calls"] += 1
            size = self.tokens(json.dumps(one.get("input") or {}, ensure_ascii=False))
            if one.get("pp"):
                self.piped[str(one.get("id"))] = size
                self.sums["pp_input"] += size
            else:
                self.sums["tool_input"] += size
        elif kind == "tool-result":
            voice = "pp_result" if str(one.get("id")) in self.piped else "tool_result"
            self.sums[voice] += self.tokens(str(one.get("content") or ""))
        elif kind == "thinking":
            counted = one.get("tokens")
            self.sums["thinking"] += counted if isinstance(counted, int) else self.tokens(str(one.get("text") or ""))
        elif kind in ("words", ASIDE):
            text = str(one.get("text") or "")
            self.sums["words"] += self.tokens(text)
            if kind == "words":
                self.words.append(Said(launch=self.launches, text=text))
        elif kind == FINAL:
            self.finals.append(Final(launch=self.launches, chars=int(one.get("chars") or 0), text=one.get("text")))
        elif kind == "context":
            self.sums["context"] = one["tokens"]
            self.measured[str(one.get("id") or f"#{len(self.measured)}")] = int(one["tokens"])
