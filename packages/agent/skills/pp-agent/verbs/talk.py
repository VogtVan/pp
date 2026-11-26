"""The verbs that talk to an agent: run, chat, open, close, start and its detached child, wait, result."""
from __future__ import annotations

import contextlib
import json
import os
import subprocess
import sys
import time
from dataclasses import replace
from pathlib import Path

from acts.chat import typed, flowing
from acts.exchange import exchange, reasoned
from acts.flow import flow_closed
from acts.launch import apart, unmeasured, policy_of, bounds_of, conducted, on_end
from acts.mounts import replayer
from acts.refusal import ruled
from faces.talk import (kept_object, logged_lines, outcome_line, spaced_line, spaced_object, started_object,
                        told_line)
from faces.text import harmless
from model.exchange import Response
from model.words import USAGE, WAIT_INTERVAL
from rules.passage import spoke
from rules.policy import provider_of
from rules.refusals import refused_space
from rules.resume import documents_judged, resumable, resumed_of
from rules.switches import asked_switches, seeded
from rules.verdict import verdict
from store.houses import house, wired_of, documents_asked, refusal_line
from store.locks import locks, held_mark, mark_of, launch_of, wake_log_of
from store.records import session_of_run, resume_of, run_was, answered_by, sent_to
from store.refusal import refuse
from store.settings import pinned_of, switches_played
from store.traces import standing_of, spaces_of, stack_of, documents_kept
from verbs.asked import asked_of, message_of, keyed, named_agent


def rendered(kept: Response, session: str, state: str, as_json: bool) -> None:
    """Prints on stdout what the call kept: the response's record line with its session and
    state (`--json`), or the response's text, `harmless`. Nothing when the harness gave no text."""
    if as_json:
        print(json.dumps(kept_object(kept, session, state), ensure_ascii=False))
    elif kept.response is not None:
        print(harmless(kept.response))


def run(rest: list[str]) -> int:
    root, conductor = house()
    name, meta, rest = named_agent(root, conductor, rest)
    asked = asked_of(rest)
    # judged before anything: a refusal leaves nothing
    switches = ruled(asked_switches, asked, str(meta), *pinned_of(conductor, meta))
    asked = replace(asked, package=tuple(value for _, _, value in switches))   # the dry run says the switches that play
    asked = ruled(resumed_of, asked.run, asked, *run_was(conductor, root, name, asked.run))
    waiting = seeded(switches, switches_played(conductor, meta, asked.run, None))
    issue, lease, keep = exchange(conductor, root, name, meta, asked, asked.run, message_of(asked), None,
                                  before=replayer(conductor, root, meta, waiting) if waiting else None,
                                  waiting=waiting)
    if issue.dry:
        return 0
    lock = locks(conductor)
    key, kept = issue.key, issue.kept
    if kept is None:                               # nothing kept: the lock given back, the reason said
        flow_closed(issue, keep, issue.reason)
        if lease is not None:
            lock.release(lease)
        refuse(issue.reason)
    flow_closed(issue, keep, reasoned(conductor, meta, key, issue))   # kept before the lock goes: one writer at a time
    said = issue.said
    lock.release(lease)                            # the records written: the wake-up is over
    if asked.on_end is not None:                # after the release: the command may reopen this run
        on_end(str(asked.on_end), root, name, key, said)
    rendered(kept, issue.account.session, said, asked.json)
    sys.stdout.flush()
    print(verdict(name, key, issue), file=sys.stderr)
    reason = reasoned(conductor, meta, key, issue)
    if reason is not None:
        refuse(reason)
    return 0


def spaced_verb(rest: list[str], opening: bool) -> int:
    """`agent open <path> <key> <NAME[@n]>` and `agent close <path> <key>`: the space opened or closed on the run by
    the principal, as the chat's commands do it out of a conversation -- the engine's `-open`/`-close` under the
    mark, then ONE exchange without a message: the launch serves the block the gesture left held (the space's
    first block, or the block below after a close) and plays the conduction until the run parks. Judged before
    anything: `run-unknown`, `run-busy` when a wake-up or a conversation holds the run; the engine's own refusal
    (`address-ambiguous`, `open-unplayable`, `space-none`, `offer-absent`) relayed, nothing launched. The flags of a
    launch after the key (the provider, the policy, `--harness`…); `--json`: ONE object `{key, run, spaces, state, launches,
    cost_usd}` -- `run` and `launches` as a response's record says them, so that a reader of records counts the wake-up."""
    root, conductor = house()
    name, meta, rest = named_agent(root, conductor, rest)
    if not rest or rest[0].startswith("--"):
        refuse(USAGE)
    key, rest = rest[0], rest[1:]
    space = None
    if opening:
        if not rest or rest[0].startswith("--"):
            refuse(USAGE)
        space, rest = rest[0], rest[1:]
    asked = asked_of(rest)
    if asked.message is not None or asked.message_file is not None or asked.run is not None or asked.vector:
        refuse(USAGE)
    if not conductor.persistence.slot_of(meta, key).is_file():
        refuse(f"run-unknown -- no run `{key}` at {name} (`./pp agent status {name}` lists them).")
    lock = locks(conductor)
    if lock.held(launch_of(meta, key)):
        refuse(f"run-busy -- a wake-up or a conversation holds run {key} of {name}: nothing opened nor closed.")
    asked = ruled(resumed_of, key, asked, *run_was(conductor, root, name, key))
    played = conducted(conductor, root, meta, key, *(["-open", space] if opening else ["-close"]))
    if played.returncode != 0:
        code, detail = refused_space(refusal_line(), played)
        refuse(f"{code} -- {detail or 'the engine refused'}; nothing launched.")
    issue, lease, keep = exchange(conductor, root, name, meta, asked, key, None, None, headless=True)
    if issue.kept is None:
        flow_closed(issue, keep, issue.reason)
        if lease is not None:
            lock.release(lease)
        refuse(issue.reason)
    flow_closed(issue, keep, reasoned(conductor, meta, key, issue))
    lock.release(lease)
    found = spaces_of(conductor, meta, key)
    state = standing_of(conductor, meta, key)
    if asked.json:
        print(json.dumps(spaced_object(key, found, state, issue.account.launches, issue.account.cost_usd),
                         ensure_ascii=False))
    else:
        print(spaced_line(name, key, space if opening else None, found, state))
    print(verdict(name, key, issue), file=sys.stderr)
    reason = reasoned(conductor, meta, key, issue)
    if reason is not None:
        refuse(reason)
    return 0


def open_verb(rest: list[str]) -> int:
    return spaced_verb(rest, True)


def close_verb(rest: list[str]) -> int:
    return spaced_verb(rest, False)


def chat(rest: list[str]) -> int:
    """`agent chat`: a CONVERSATION at the foreground, conducted by the house -- the messages read on
    stdin one per line (`typed`), each an `exchange` of ONE run, held with its session and its wake
    lock from a message to the next: the first message opens the run (`--run <key>` resumes one),
    every later one resumes it. After each exchange the response goes to stdout and the verdict to
    stderr, as `run` says them; an exchange that ends badly says why on stderr and the conversation
    goes on, the run standing for the next message. A SIGINT during an exchange ends the harness and
    is said `interrupted`; one while waiting for a message, or the end of stdin, closes the
    conversation: the lock released, exit 0, the run resumable by `--run <key>`.
    Under `--json` the conversation is a FLOW: commands on stdin (`commanded`), events on stdout --
    one JSON object per line, each naming its voice by its `kind` (`event_sayer`: `opened`,
    `principal`, `conduction`, `agent`, `step`; here `ready`, `response`, `verdict`, `waiting`,
    `refused`, `closed`) --, stderr silent from the first command on."""
    root, conductor = house()
    name, meta, rest = named_agent(root, conductor, rest)
    asked = asked_of(rest)
    # the conversation's waiting list, seeded below
    switches = ruled(asked_switches, asked, str(meta), *pinned_of(conductor, meta))
    for flag in ("message", "message-file", "tag", "on-end"):
        if getattr(asked, flag.replace("-", "_")) is not None:
            refuse(f"flag-unsupported -- `--{flag}` has no meaning under chat: the messages are the lines of stdin, "
                   "a tag and an on-end belong to one wake-up.")
    for flag in ("dry-run", "new", "detached"):
        if getattr(asked, flag.replace("-", "_")):
            refuse(f"flag-unsupported -- `--{flag}` has no meaning under chat: a dry run is `run --dry-run`, "
                   "the first message opens the run.")
    persistence = conductor.persistence
    key = asked.run
    opening = key is None
    if asked.door is not None and not opening:
        refuse("door-on-resume -- a door opens a run's FIRST exchange; a resume continues the conversation.")
    if not opening and persistence.slot_of(meta, key).is_file():
        ruled(documents_judged, key, *documents_kept(conductor, meta, key, documents_asked(root, asked)))
    lock = locks(conductor)
    asked = ruled(resumed_of, key, asked, *run_was(conductor, root, name, key))   # a resume keeps what the run was
    head, provider = ruled(provider_of, asked, wired_of(conductor, root))   # judged before any message is read
    refused = unmeasured(conductor, root, asked, policy_of(conductor, asked))
    if refused is not None:
        refuse(refused)
    bounds_of(asked)
    lease = None
    if not opening:
        if not persistence.slot_of(meta, key).is_file():
            refuse(f"run-unknown -- no run `{key}` at {meta}.")
        ruled(resumable, key, str(meta), *resume_of(conductor, root, meta, name, key), provider)
        lease = lock.try_(launch_of(meta, key))
        if lease is None:
            refuse(f"run-busy -- a wake-up plays run {key}: one wake-up at a time on a run.")
        sent = sent_to(root, name, key)
        held_mark(lease, str(sent[-1].message or "") if sent else "")
    waiting = seeded(switches, switches_played(conductor, meta, key, None))
    if asked.json:
        return flowing(conductor, root, name, meta, asked, key, lease, lock, waiting)
    before = replayer(conductor, root, meta, waiting)
    try:
        for message in typed(sys.stdin):
            issue, lease, keep = exchange(conductor, root, name, meta, asked, key, message, lease, before=before,
                                          waiting=waiting)
            if key is None and issue.key is not None:
                asked = replace(asked, door=None)  # the door played at the opening: the exchanges after carry none
            key = issue.key
            flow_closed(issue, keep, issue.reason if issue.kept is None else reasoned(conductor, meta, key, issue))
            if issue.kept is None:                 # nothing kept: said, the run standing for the next message
                print(told_line(issue.reason), file=sys.stderr)
                sys.stderr.flush()
                continue
            rendered(issue.kept, issue.account.session, issue.said, False)
            sys.stdout.flush()
            print(verdict(name, key, issue), file=sys.stderr)
            reason = reasoned(conductor, meta, key, issue)
            if reason is not None:
                print(told_line(reason), file=sys.stderr)
            sys.stderr.flush()
    except KeyboardInterrupt:                      # while waiting for a message: the conversation closes
        pass
    finally:
        if lease is not None:
            lock.release(lease)
    return 0


def outcome(conductor, root: Path, name: str, meta: Path, key: str, lock) -> int:
    """Renders the last response of the run `key` as `run` does, when the last launch left
    one: the text on stdout, the verdict on stderr, 0 when the run parked with a response;
    `wake-dead` when the launch ended without a response (the wake log's tail said)."""
    persistence = conductor.persistence
    mark = mark_of(lock, meta, key)
    answered = answered_by(root, name, key)
    launched = mark.responses
    if launched is not None and len(answered) <= launched:
        log = wake_log_of(lock, meta, key)
        tail = log.read_text(encoding="utf-8").strip().splitlines()[-5:] if log.is_file() else []
        for line in logged_lines(tail):
            print(line, file=sys.stderr)
        refuse(f"wake-dead -- the wake-up of run {key} ended without a response.")
    if not answered:
        refuse(f"result-missing -- run {key} has no response recorded.")
    kept = answered[-1]
    slot = persistence.slot_of(meta, key)
    state, stack = (standing_of(conductor, meta, key), stack_of(conductor, meta, key)) if slot.is_file() else ("standing", "")
    exchanges = persistence.turns_of(slot) if slot.is_file() else 0
    known = session_of_run(root, name, key)
    session = known.session if known is not None else ""
    arrived = kept.harness_rc == 0 and state == "parked" and spoke(kept)
    said = "parked" if arrived else ("stopped" if kept.harness_rc else "standing")
    rendered(kept, str(session), said, False)
    sys.stdout.flush()
    print(outcome_line(name, key, exchanges, said, kept), file=sys.stderr)
    return 0 if arrived else 2


def wait(rest: list[str]) -> int:
    """`agent wait <path> <key> [--timeout <seconds>]`: waits for the run's wake lock to be
    free -- looked at, never taken -- then renders the outcome; `wait-timeout` past the bound."""
    root, conductor = house()
    name, key, rest = keyed(rest)
    name, meta, _ = named_agent(root, conductor, [name])
    bound = None
    if rest[:1] == ["--timeout"] and len(rest) == 2:
        try:
            bound = float(rest[1])
        except ValueError:
            refuse(f"`{rest[1]}` is not a number of seconds.")
    elif rest:
        refuse(USAGE)
    lock = locks(conductor)
    deadline = None if bound is None else time.monotonic() + bound
    while lock.held(launch_of(meta, key)):
        if deadline is not None and time.monotonic() >= deadline:
            refuse(f"wait-timeout -- a wake-up still plays run {key} after {bound:g}s.")
        time.sleep(WAIT_INTERVAL)
    return outcome(conductor, root, name, meta, key, lock)


def result(rest: list[str]) -> int:
    """`agent result <path> <key>`: the run's last response at once -- `wake-running` while a
    wake-up plays and has not answered yet, `wake-dead` or `result-missing` otherwise."""
    root, conductor = house()
    name, key, rest = keyed(rest)
    if rest:
        refuse(USAGE)
    name, meta, _ = named_agent(root, conductor, [name])
    lock = locks(conductor)
    if lock.held(launch_of(meta, key)):
        launched = mark_of(lock, meta, key).responses
        if launched is None or len(answered_by(root, name, key)) <= launched:
            refuse(f"wake-running -- a wake-up plays run {key}: `agent wait {name} {key}` waits for it.")
    return outcome(conductor, root, name, meta, key, lock)


def detached(rest: list[str]) -> int:
    """The child of `agent start`, `run … --detached`: it outlives the console that launched
    its parent, so it holds the machine's maintenance lock SHARED itself, for its whole life
    -- under a maintenance it refuses `maintenance-in-progress` before anything is touched."""
    root, conductor = house()
    with contextlib.ExitStack() as stack:
        try:
            stack.enter_context(locks(conductor).serving(root))
        except conductor.Refusal as refusal:
            refuse(str(refusal))
        return run(rest)


REPORT_WAIT = 20                # seconds `start` gives its child to report {key, pid}


def start(rest: list[str], entry: Path) -> int:
    """`agent start`: the wake-up DETACHED -- the child is `run … --detached`, the process
    that lives with the harness and holds the wake lock; it reports `{key, pid}` on its
    stdout once the lock is held, and the parent prints that line and returns. A refusal
    the child says before its report reaches the parent on stderr and is relayed. `entry` is
    the script the child is launched by: the skill's own."""
    if not rest or rest[0].startswith("--"):
        refuse(USAGE)
    asked = asked_of(rest[1:])                     # judged here too: the usage says itself once
    for flag in ("json", "dry-run"):
        if getattr(asked, flag.replace("-", "_")):
            refuse(f"flag-unsupported -- `--{flag}` has no meaning under start: the report is JSON already, "
                   "a dry run is `run --dry-run`.")
    argv = [sys.executable, str(entry), "run", *rest, "--detached"]
    given = None if asked.message_file == "-" else subprocess.DEVNULL   # `-`: the message is the caller's input
    child = subprocess.Popen(argv, stdin=given, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                             cwd=os.getcwd(), env=dict(os.environ), **apart())
    assert child.stdout is not None and child.stderr is not None
    import threading
    box: dict = {}

    def reading() -> None:
        box["line"] = child.stdout.readline()

    reader = threading.Thread(target=reading, daemon=True)
    reader.start()
    reader.join(REPORT_WAIT)
    line = str(box.get("line", "")).strip()
    if not line:
        if child.poll() is None:                   # no report in time: the child is not ours to keep
            child.kill()
        said = child.stderr.read().strip() if reader.is_alive() is False else ""
        refuse(said.removeprefix("pp-agent: ") if said else
               f"start-timeout -- the wake-up reported nothing in {REPORT_WAIT}s")
    try:
        report = json.loads(line)
    except ValueError:
        refuse(f"start-garbled -- the wake-up reported `{line[:80]}`")
    print(json.dumps(started_object(report.get("key"), report.get("pid"))))
    return 0
