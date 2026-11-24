"""The conversation as a flow: its commands read, the principal's words played between two exchanges, its loop."""
from __future__ import annotations

import json
import os
import sys
from dataclasses import replace
from pathlib import Path

from acts.exchange import exchange, reasoned
from acts.flow import event_sayer
from acts.launch import policy_of, set_policy, conducted
from acts.mounts import switched, replayer
from acts.refusal import ruled
from model.exchange import Issue
from model.policy import Asked
from rules.budget import budget_of
from rules.policy import grammar_of, provider_of, provider_named
from rules.refusals import refused_space
from rules.resume import verdict_of
from store.adapters import launcher_cap
from store.houses import wired_of, documents_asked, refusal_line
from store.records import spent_of, vectors_due
from store.refusal import refuse
from store.settings import cap_of, packages_of
from store.traces import spaces_of


def typed(stream):
    """-> the messages typed on `stream`, one per line: a line ending on a backslash goes on with
    the next -- the backslash taken out, the line break kept --; an empty message sends nothing."""
    parts: list[str] = []
    for line in stream:
        line = line.rstrip("\n")
        if line.endswith("\\"):
            parts.append(line[:-1] + "\n")
            continue
        parts.append(line)
        message, parts = "".join(parts), []
        if message.strip():
            yield message
    message = "".join(parts).rstrip("\n")
    if message.strip():
        yield message


def commanded(stream, busy, said=None):
    """-> the COMMANDS of a conversation's flow, read on `stream` by a thread of its own so that one
    arrives during an exchange too -- one JSON object per line: `{"kind": "message", "text": …}`
    yields `("message", text)`; `{"kind": "stop"}` raises SIGINT at this process while an exchange
    plays (`busy` set: the harness ends, the exchange is said `interrupted`) and does nothing
    otherwise; `{"kind": "set", …}` yields `("set", fields, line)` -- the policy of the next launches;
    `{"kind": "conduct", "on": …}` yields `("conduct", on, line)`; `{"kind": "package", "name": …,
    "on": …}` yields `("package", name, on, line)`;
    `{"kind": "open", "name": "<NAME[@n]>", "text": "<message>"}` yields `("open", name, text, line)` -- the space
    opened, then ONE exchange of that message; without `text`, or with an empty one, `text` is None: the space
    opened, then one exchange without a message, as `close` plays -- and
    `{"kind": "close"}` `("close", line)` -- the spaces of the run, played between two exchanges; one that comes during
    an exchange is said `pending` by `said` at once, when the caller gives it, and waits its turn in the queue --;
    `{"kind": "quit"}` ends the commands after the exchange under way; a line that does
    not read yields `("refused", "command-unreadable", line)`, a kind nobody knows
    `("refused", "command-unknown", line)`. The end of the stream ends the commands."""
    import queue
    import threading
    box: queue.Queue = queue.Queue()
    main = threading.main_thread().ident

    def reading() -> None:
        for raw in stream:
            line = raw.rstrip("\n")
            try:
                read = json.loads(line)
            except ValueError:
                box.put(("refused", "command-unreadable", line))
                continue
            kind = read.get("kind") if isinstance(read, dict) else None
            if kind == "message" and isinstance(read.get("text"), str):
                box.put(("message", read["text"]))
            elif kind == "set":
                box.put(("set", {key: value for key, value in read.items() if key != "kind"}, line))
            elif kind == "conduct" and isinstance(read.get("on"), bool):
                box.put(("conduct", read["on"], line))
            elif kind == "package" and isinstance(read.get("name"), str) and isinstance(read.get("on"), bool):
                box.put(("package", read["name"], read["on"], line))
            elif kind == "open" and isinstance(read.get("name"), str) and read["name"].strip():
                text = read.get("text") if isinstance(read.get("text"), str) and read["text"].strip() else None
                if busy.is_set() and said is not None:
                    said("space", {"name": read["name"].strip(), "open": True, "pending": True})
                box.put(("open", read["name"].strip(), text, line))
            elif kind == "close":
                if busy.is_set() and said is not None:
                    said("space", {"name": None, "open": False, "pending": True})
                box.put(("close", line))
            elif kind == "stop":
                if busy.is_set() and main is not None:   # to the MAIN thread, where the exchange waits on the harness
                    interrupting(main)
            elif kind == "quit":
                box.put(("quit",))
                break
            else:
                box.put(("refused", "command-unknown", line))
        box.put(None)

    threading.Thread(target=reading, daemon=True).start()
    while True:
        item = box.get()
        if item is None or item[0] == "quit":
            return
        yield item


def interrupting(main: int, system: str = os.name) -> None:
    """Interrupts the MAIN thread `main` from another thread of this process: `KeyboardInterrupt` is raised there at
    its next instruction -- under Windows by `_thread.interrupt_main`, elsewhere by SIGINT sent to that thread."""
    if system == "nt":
        import _thread
        _thread.interrupt_main()
        return
    import signal
    signal.pthread_kill(main, signal.SIGINT)


def ready_of(conductor, root: Path, name: str, meta: Path, asked: Asked, key: str | None) -> dict:
    """-> what a conversation's flow says of its run before any message (`ready`): the agent, whether
    the run is taken up, the provider, the policy, the packages and the cap -- read by the functions
    `opened` reads them with -- the run's budget under a cap, whether the next exchanges are conducted, the switches waiting
    (`pending`, none at the start of a conversation), the root of documents (`documents`: the
    run's under `--run`, the one `--documents` names at an opening, None without) and the vectors the
    run mounts (`vectors`: the `--vector` given, else the set the run keeps, [] for none -- `vectors_due`).
    The run itself is the event's `run`: its key under `--run`, none at an opening."""
    persistence = conductor.persistence
    documents = (persistence.documents_of(persistence.slot_of(meta, key)) if key is not None
                 else documents_asked(root, asked)) or None
    policy = policy_of(conductor, asked)
    wired = wired_of(conductor, root)
    try:
        cap = launcher_cap(conductor, root, grammar_of(asked, ruled(provider_of, asked, wired)[1]), policy)
    except conductor.Refusal as refusal:
        refuse(str(refusal))
    budget = budget_of(policy, spent_of(root, name, key))
    return {"agent": name, "resumed": key is not None, "provider": ruled(provider_named, asked, wired),
            "policy": policy.json(), "packages": packages_of(conductor, meta, key),
            "spaces": spaces_of(conductor, meta, key) if key is not None else None,
            "cap": cap_of(conductor, meta, cap), "budget": budget.json() if budget is not None else None,
            "conducted": asked.conduct is not False, "pending": [], "documents": documents,
            "vectors": vectors_due(root, name, key, asked)}


def spacing(conductor, root: Path, meta: Path, key: str, item: tuple, say) -> dict | None:
    """ONE space opened or closed on the run, between two exchanges, by this script as the principal -- the engine's
    `-open <name>` or `-close` by the same path as `-enable` (`conducted`): accepted, the flow says `space {name, open,
    pending: false}` and -> the spaces the run's last block says; refused, the flow says `refused` with the engine's
    code and detail (`address-ambiguous`, `open-unplayable`, `space-none`, `offer-absent` for a name the output does
    not offer) and -> None. The output the gesture left held is the next exchange's: an open's message, when it has one, rides it;
    an open without one, and a close, launch without a message."""
    opening = item[0] == "open"
    name = item[1] if opening else ((spaces_of(conductor, meta, key) or {}).get("open") or [None])[-1]
    played = conducted(conductor, root, meta, key, *(["-open", item[1]] if opening else ["-close"]))
    if played.returncode != 0:
        code, detail = refused_space(refusal_line(), played)
        say(key, f"refused {code}", "refused", {"code": code, "line": item[-1], "detail": detail})
        return None
    found = spaces_of(conductor, meta, key) or {"open": [], "openable": []}
    say(key, f"space {name} {'open' if opening else 'closed'}", "space",
        {"name": name, "open": opening, "pending": False, "spaces": found})
    return found


def flowing(conductor, root: Path, name: str, meta: Path, asked: Asked, key: str | None, lease, lock,
            waiting: dict | None = None) -> int:
    """The conversation as a FLOW (`chat --json`): `ready` first, the run as judged before any message
    (`ready_of`), then `waiting`; the commands read by `commanded`, each `message`
    one `exchange` whose steps and voices `event_sayer` says on stdout; after it, `response` (the
    record's line plus `session` and `state`) when one was kept, `verdict` (the verdict as data,
    its `reason` when the exchange did not end well), then `waiting`; a `set` that holds is said by
    `policy` (the provider and the policy of the next launch), one that does not by `refused`;
    `conduct` and `package` are played by `switched`, a switch the run cannot take yet waiting in the
    conversation's list until a launch plays it (`replayer`); `open` plays the space (`spacing`) then ONE exchange of
    its message -- without one, an exchange without a message --, on the output the gesture held; `close` the space,
    then one exchange without a message; a bad
    command is `refused` and the flow goes on; `quit`, the end of stdin or a SIGINT while waiting closes it: `closed`,
    the lock released, exit 0."""
    import threading
    say = event_sayer(sys.stdout)
    busy = threading.Event()
    waiting = {} if waiting is None else waiting   # the switches asked and not yet played: {name: (on, line)}
    before = replayer(conductor, root, meta, waiting, say)
    def reported(issue: Issue, told) -> None:
        """What the flow says once an exchange ended: the response kept, the verdict, then `waiting`."""
        told = told or say                         # the exchange's keeper: kept in the flow, and said
        if issue.kept is not None:
            told(issue.key, "", "response", {**issue.kept.json(), "session": issue.account.session, "state": issue.said})
            reason = reasoned(conductor, meta, issue.key, issue)
        else:
            reason = issue.reason
        told(issue.key, "", "verdict", verdict_of(issue, reason))
        say(issue.key, "", "waiting", {})

    try:
        ready = ready_of(conductor, root, name, meta, asked, key)
        ready["pending"] = [{"name": one, "on": on} for one, (on, _) in waiting.items()]   # `--package`, seeded
        say(key or "", "", "ready", ready)
        say(key or "", "", "waiting", {})
        for item in commanded(sys.stdin, busy, lambda kind, fields: say(key or "", "", kind, fields)):
            if item[0] == "refused":
                say(key or "", "", "refused", {"code": item[1], "line": item[2]})
                continue
            if item[0] in ("conduct", "package"):
                asked = switched(conductor, root, meta, asked, key, item, say, waiting)
                continue
            if item[0] in ("open", "close"):
                if key is None:
                    say("", "", "refused", {"code": "run-missing", "line": item[-1]})
                    continue
                spaced = spacing(conductor, root, meta, key, item, say)
                if spaced is None:
                    continue
                text = item[2] if item[0] == "open" else None   # an open's message, if any: ONE exchange with it
                busy.set()
                try:
                    issue, lease, told = exchange(conductor, root, name, meta, asked, key, text, lease, say=say,
                                                  before=before, waiting=waiting, headless=text is None)
                finally:
                    busy.clear()
                reported(issue, told)
                key = issue.key
                continue
            if item[0] == "set":
                asked, code = set_policy(conductor, root, asked, item[1])
                if code is not None:
                    say(key or "", "", "refused", {"code": code, "line": item[2]})
                else:
                    say(key or "", "", "policy", {"provider": ruled(provider_named, asked, wired_of(conductor, root)),
                                                  "policy": policy_of(conductor, asked).json()})
                continue
            busy.set()
            try:
                issue, lease, told = exchange(conductor, root, name, meta, asked, key, item[1], lease, say=say,
                                              before=before, waiting=waiting)
            finally:
                busy.clear()
            if key is None and issue.key is not None:
                asked = replace(asked, door=None)  # the door played at the opening: the exchanges after carry none
            reported(issue, told)
            key = issue.key
    except KeyboardInterrupt:                      # while waiting for a command: the conversation closes
        pass
    finally:
        if lease is not None:
            lock.release(lease)
        say(key or "", "", "closed", {})
    return 0
