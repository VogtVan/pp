#!/usr/bin/env python3
"""DETERMINISTIC keeper of the named threads -- the NEXT's cross-cutting entities.

TWO DICTIONARIES, both by id, at the member's record `threads.json`:

  steps     `{<id>: {owner, name, thread, text, status, key?, from?, reason?}}` -- a step is
            the UNIT of work: a record that never changes place. `thread` is the id of the
            thread it was born in, kept for good. Its NAME says the work -- with its key, the
            step's identity, changed on the operator's request alone (NEXT says when); its
            `text` is a COMPLEMENT the agent writes freely, empty allowed, under the step budget;
            its status is `open`, `done`, `redo` (delivered once, pointed again), `blocked`
            (waiting, its reason kept) or `dropped` (left, kept); the key, when the work has an
            address, is its vector (`plan-lot:<plan>/<phase>/<batch>`, `steering-thread:<thread
            id>`...), verified by the family's own verifier through the engine and UNIQUE at the
            dictionary -- a work is minted once; `from` names the step a copy crossed from (a
            step's id at another member).
  threads   `{<id>: {name, owner, steps, next, opened_at, worked_at, note?}}` -- a thread
            ORDERS steps: `steps` is the ORDERED list of the ids it holds, the whole of its
            order. The list says where a step stands, `thread` where it was born: `move` takes a
            step from one list to another, and one open thread at a time lists it. A thread
            lists ids of THIS dictionary alone: a record listing one it does not hold, or a
            BRAID (`braid: true`, a shape the model had before 0.6.0) is of a former shape
            (`state-legacy`). `next` is the suggested next move, a listed id. The name is the
            thread's identity, unique among the open threads; the id is the handle of every
            verb. `note` says the thread's why, then what to know now, under the note budget --
            written by `open --note` and `note`, never a date. `worked_at` is the date of the
            WORK: a step's status moved, a step added or reordered, the thread closed, opened or
            reopened -- never an amend, a note nor a rename.
  counters  `{s, f}` -- one counter per SERIES, never rewound.

An ID has NO semantics: `<member>.s.<n>` for a step, `<member>.f.<n>` for a thread -- the
member for the uniqueness across a confederation alone, never read to derive anything: the
OWNER says the member that minted the record. A copy born of a crossing keeps the source
thread's id and owner (the link across members) and lists steps minted here.

A closed thread leaves `threads` for `threads-closed.jsonl` -- the durable history, the
thread with its ids -- and its steps stay at the dictionary: a closed chain stays legible.
`threads-seen.json` holds, per run, what the run has SEEN: the snapshot `{thread id:
worked_at}` of the open threads as the table was last served to it, and the exchange it was
served at. The NEXT's provider (`status --due`) compares the data now with that snapshot
before serving: the table when the run boots, saw none, or a thread was added, closed or
worked since -- by this run, by another session, during a turn or between two -- and one
line otherwise; a table served is kept as seen. An amend or a rename moves no date and is
not a change of the table. This script is the records' ONLY writer; the agent drives the
calls, the operator's challenge wins through them.

  pp-steering.py open <name> [--note <text>]     -> a thread minted -- the ONE verb that takes a
                                                  NAME, since it gives it; its steps piped one
                                                  per line: `<name>`, `<name> | <text>`,
                                                  `<name> | <family:slug>`, `<name> |
                                                  <family:slug> | <text>`; the minted id said
                                                  back: every other verb takes it
  pp-steering.py attach <thread id> --as <name> [--key <family:slug>] [<text ...>]
                                               -> one step minted in that thread and listed;
                                                  the thread's id and the step's said back
  pp-steering.py attach <thread id> --from <step id> --owner <member> --name <name> [<text ...>]
                                               -> a step crossing from a neighbour: minted here
                                                  with its `from`, listed in the thread of that
                                                  id -- born under <name> and that owner when
                                                  none stands; a text over the budget is cut
                                                  to it and the cut said
  pp-steering.py amend <thread id> <step id> [--as <name>] [--key <family:slug>|-] [<text ...>]
                                               -> the text, the name or the key rewritten; the
                                                  name and the key are the step's IDENTITY,
                                                  changed on the operator's request alone (NEXT
                                                  says when); nothing here dates the thread
  pp-steering.py done <thread id> <step id>      -> delivered; every pointer on it moves on
  pp-steering.py block <thread id> <step id> <reason ...>
  pp-steering.py drop <thread id> <step id>      -> `dropped`, kept, out of the front
  pp-steering.py reorder <thread id> <step id> <rank>
  pp-steering.py move <thread id> <step id> <target thread id>
                                               -> the step leaves this thread's list for the end
                                                  of the target's, unchanged; both threads dated
  pp-steering.py renext <thread id> <step id>    -> the next move; a delivered step pointed
                                                  again REOPENS as `redo`
  pp-steering.py rename <thread id> <new>        -> the name changes, the id stays; nothing
                                                  dates the thread
  pp-steering.py note <thread id> <text ...>     -> the thread's note rewritten (empty: none);
                                                  nothing dates the thread
  pp-steering.py close <thread id>               -> leaves the state, written to history
  pp-steering.py reopen <thread id>              -> a closed thread comes back, its ids as they
                                                  were
  pp-steering.py status [<thread id>] [--all [--open]]
                                               -> the FRONT the NEXT pastes -- the table
                                                  `initiative | note | progress | age | next
                                                  action(s)` of the threads with a step to do,
                                                  the `⏸` line of the waiting steps, the `💤`
                                                  footer past the rows kept; no id shown -- or,
                                                  with `--all`, the LEDGER: ids, names, notes
                                                  and owners, the agent's view; `--open` keeps
                                                  the steps still to do (what the boot serves)
  pp-steering.py status --due                    -> what the NEXT's provider serves: the front when
                                                  the run that names this script (`PP_RUN`) boots,
                                                  saw no table, or a thread was added, closed or
                                                  worked since the table it last saw -- by any
                                                  hand, at any moment -- else the one line `thread
                                                  table not changed since the last turn`; the front
                                                  served is kept at `threads-seen.json` as seen,
                                                  and the runs whose slot is gone leave it
  pp-steering.py data [--bare]                   -> the member's OPEN threads as ONE JSON object
                                                  (version 3): ids, names, owners, notes,
                                                  stamps, counts, the id of the pointed step and
                                                  the steps still to do, each once in its thread
                                                  -- never a delivered or dropped one -- and
                                                  `closed`, the ids of the closed threads;
                                                  `--bare` without texts; read-only, what
                                                  another package reads
  pp-steering.py verify                          -> this package's VERIFIER, the engine's call:
                                                  `steering-thread:<thread id>` on stdin, rc 0
                                                  when an OPEN thread carries that id

Guards -- exit 2, nothing written: thread-taken, thread-unknown, thread-addressed-by-name,
step-invalid, step-unknown (an id the thread does not list), step-taken (a key already minted,
a source already crossed), step-crossed and thread-foreign (`move` of a step crossed from a
neighbour, or to or from a thread another member owns), key-invalid, name-invalid,
name-taken, budget, family-foreign, state-legacy (a record of a former shape -- a step
without its `thread` or its `name`, a thread without `worked_at`, a thread listing an id the
dictionary does not hold (at every read, and at `reopen` for a closure of the history), a
braid, the shapes before them: this version does not read it), thread-guarded (a GUARDIAN
another package declared on the family keeps the thread from closing -- the engine asks it,
this script relays its no); a key the
family's verifier refuses is relayed under the engine's own code. Writes go through the
engine's one write regime: lock, read inside it, atomic replace. No network, ever.

The conductor plays this skill: an agent reaches it as `./pp <key> -s pp-steering ...`,
and pp runs it with its own interpreter -- what the engine depends on, it may depend on.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

STATE_NAME = "threads.json"
HISTORY_NAME = "threads-closed.jsonl"
SEEN_NAME = "threads-seen.json"      # per run, the open threads as the table was LAST SERVED to it
NOT_CHANGED = "thread table not changed since the last turn"
STEP_BUDGET_KEY = "steering_step_budget"
STEP_BUDGET_FALLBACK = 100    # the fragment's value -- what plays when the line is missing
NAME_MAX_KEY = "steering_name_max"
NAME_MAX_FALLBACK = 60
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")   # kebab-case, the slugs' own grammar
VECTOR = re.compile(r"^[a-z][a-z0-9_-]*:\S+$")   # a key: `<family>:<slug>`, the bus's own grammar
DORMANT_KEY, DORMANT_FALLBACK = "steering_dormant_days", 7   # a thread untouched that long shows 💤
NOTE_BUDGET_KEY, NOTE_BUDGET_FALLBACK = "steering_note_budget", 80   # a thread's note: its why, then what to know now
NEXT_MAX_KEY, NEXT_MAX_FALLBACK = "steering_next_max", 3         # the next actions a row names before `…`
LINE_MAX_KEY, LINE_MAX_FALLBACK = "steering_line_max", 7         # the waiting steps the ⏸ line names before `+n`
FRONT_MIN_KEY, FRONT_MIN_FALLBACK = "steering_front_min", 5      # the rows the table keeps before anything folds
FAMILY = "steering-thread"      # the one vector family this package declares -- the only one it verifies
ID = re.compile(r"^\S+\.[sf]\.[0-9]+$")   # an id's SHAPE, `<member>.s.<n>` / `<member>.f.<n>` -- read for its shape alone, never for the member
STATUSES = ("open", "done", "redo", "blocked", "dropped")


def refuse(code: str, detail: str) -> None:
    sys.stderr.write(f"pp-steering: {code} -- {detail}\n")
    raise SystemExit(2)


def home() -> Path:
    """-> the instance this vendored copy belongs to -- the bootstrap's one walk."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from _core import home as walk                       # noqa: E402 -- the bootstrap
    found = walk(__file__)
    if found is None:
        refuse("not-an-instance", "not inside an installed instance -- nothing to write to")
    return found


def engine():
    """-> the engine's face, reached through the vendored bootstrap."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from _core import core                                # noqa: E402 -- the bootstrap
    return core(__file__)


def budget(root: Path, key: str, fallback: int) -> int:
    """-> a budget of this package: the instance's EFFECTIVE value for the key -- the
    operator's line, the effort's preset over it, the fragment's default under it -- and
    a refusal when it is not a whole number."""
    face = engine().settings
    try:
        found = face.of(root).of_package(key, face.default_of(root, key) or fallback)
    except Exception as raised:            # the face refuses a TYPED value by its own name
        if type(raised).__name__ != "Refusal":
            raise
        detail = str(raised).split(" — ", 1)[-1]
        refuse(getattr(raised, "code", "setting-invalid"), detail)
    try:
        return int(found)
    except (TypeError, ValueError):
        refuse("setting-invalid", f"`{key}: {found}` is not a whole number")


def state_path(root: Path) -> Path:
    return root / ".sys" / "records" / STATE_NAME


def empty() -> dict:
    """-> a record with nothing in it: the two dictionaries and the counters at zero."""
    return {"counters": {"s": 0, "f": 0}, "threads": {}, "steps": {}}


def load(root: Path) -> dict:
    """-> the record, `{counters, threads, steps}` -- empty when there is none. ONE shape is
    read: a record of a former shape is refused, never guessed; a field this version does not
    know is left as it is."""
    path = state_path(root)
    if not path.is_file():
        return empty()
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        refuse("state-malformed", f"{path} does not parse -- the record is not mine to guess")
    legacy = "this version of steering does not read it"
    if (not isinstance(record, dict) or not all(isinstance(record.get(k), dict) for k in ("counters", "threads", "steps"))
            or not all(isinstance(record["counters"].get(s), int) for s in ("s", "f"))):
        refuse("state-legacy", f"the record is not the two dictionaries with their counters -- {legacy}")
    for tid, thread in record["threads"].items():
        if thread.get("braid"):
            refuse("state-legacy", f"thread `{tid}` is a braid -- the model has none since steering 0.6.0: close it "
                                   "with the version that opened it")
        if (not ID.fullmatch(tid) or not isinstance(thread, dict) or not thread.get("name") or not thread.get("owner")
                or not isinstance(thread.get("steps"), list) or not all(isinstance(s, str) and ID.fullmatch(s) for s in thread["steps"])
                or not thread.get("worked_at")):
            refuse("state-legacy", f"thread `{tid}` is not a record of the two dictionaries with its `worked_at` -- {legacy}")
    for sid, step in record["steps"].items():
        if (not ID.fullmatch(sid) or not isinstance(step, dict) or not step.get("owner") or step.get("status") not in STATUSES
                or not step.get("name") or not ID.fullmatch(str(step.get("thread", "")))):
            refuse("state-legacy", f"step `{sid}` is not a record of the two dictionaries with its `name` and its `thread` -- {legacy}")
    for tid, thread in record["threads"].items():
        for sid in thread["steps"]:
            if sid not in record["steps"]:
                refuse("state-legacy", f"thread `{tid}` lists {sid}, an id this dictionary does not hold -- a thread lists "
                                       f"the member's own steps alone; {legacy}")
    return record


def stamp() -> str:
    """-> the UTC instant, to the microsecond: two writes in one second still order."""
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def touched(thread: dict) -> None:
    """Every gesture on a thread's WORK stamps it: `worked_at` is the date of the work -- a step
    whose status moved, a step added or moved, the thread closed, opened or reopened -- what the
    render orders by, shows as the age and folds under. An amend of a text, a name or a key
    and a rename leave it where the work left it."""
    thread["worked_at"] = stamp()


def member_of(root: Path) -> str:
    """-> the member this record belongs to: the workspace the instance lives in -- what an
    OWNER field says, and what an id carries for its uniqueness alone."""
    return root.resolve().parent.name


def mint(root: Path, record: dict, series: str) -> str:
    """-> a fresh id of a series, `<member>.<series>.<n>`: the member's counter moves
    forward and never rewinds -- an id is never reused, never rewritten."""
    record["counters"][series] += 1
    return f"{member_of(root)}.{series}.{record['counters'][series]}"


def save(root: Path, record: dict) -> None:
    """Writes the whole record atomically -- the engine's one write regime."""
    engine().record.replace(state_path(root), json.dumps(record, ensure_ascii=False, indent=1) + "\n")


def clean_text(root: Path, text: str | None) -> str:
    """-> the step's text as one budgeted line: a COMPLEMENT to the name, empty allowed -- the
    wording stays the agent's duty, the name says the work."""
    step = " ".join((text or "").split())
    cap = budget(root, STEP_BUDGET_KEY, STEP_BUDGET_FALLBACK)
    if len(step) > cap:
        refuse("budget", f"{len(step)} chars -- a text is a complement to the step's name, the budget is {cap}")
    return step


def clean_note(root: Path, text: str | None) -> str:
    """-> a thread's note as one budgeted line: its why, then what to know now -- a table cell,
    so the budget keeps the front legible."""
    note = " ".join((text or "").split())
    cap = budget(root, NOTE_BUDGET_KEY, NOTE_BUDGET_FALLBACK)
    if len(note) > cap:
        refuse("budget", f"{len(note)} chars -- a thread's note says its why and what to know now, the budget is {cap}")
    return note


def cut_text(root: Path, text: str | None) -> tuple[str, int | None]:
    """-> (the text, the budget it was cut to or None): what a CROSSING keeps of a neighbour's
    sentence -- the whole stays readable at its source, the copy holds the budget's worth."""
    step = " ".join((text or "").split())
    cap = budget(root, STEP_BUDGET_KEY, STEP_BUDGET_FALLBACK)
    return (step[:cap], cap) if len(step) > cap else (step, None)


def valid_name(root: Path, name: str) -> str:
    cap = budget(root, NAME_MAX_KEY, NAME_MAX_FALLBACK)
    if not NAME.fullmatch(name) or len(name) > cap:
        refuse("name-invalid", f"`{name}` -- a thread name is kebab-case, {cap} chars at most")
    return name


def valid_step_name(root: Path, name: str) -> str:
    """-> the name a step wears, once its grammar agrees: kebab-case, the slugs' own, capped
    like a thread's. A step's TEXT is prose one rewrites; its NAME is what designates it."""
    cap = budget(root, NAME_MAX_KEY, NAME_MAX_FALLBACK)
    if not NAME.fullmatch(name) or len(name) > cap:
        refuse("name-invalid", f"`{name}` -- a step name is kebab-case, {cap} chars at most")
    return name


def name_free_in(record: dict, thread: dict, name: str, but: str | None = None) -> str:
    """-> the name, once no OTHER step of this thread wears it: a name designates one step of
    a chain, two threads may name two works alike, and the id stays the machine's identity."""
    for sid in thread["steps"]:
        if sid != but and record["steps"].get(sid, {}).get("name") == name:
            refuse("name-taken", f"`{name}` is {sid} already in this thread -- a name designates "
                                 "one step of the chain; amend it or name this one otherwise")
    return name


def valid_id(said: str) -> str:
    """-> an id as a verb receives it (`#` tolerated in front) -- its shape checked, nothing read in it."""
    said = said.lstrip("#")
    if not ID.fullmatch(said):
        refuse("step-invalid", f"`{said}` -- an id is `<member>.s.<n>` (a step) or `<member>.f.<n>` (a thread)")
    return said


def by_thread(record: dict, said: str) -> tuple[str, dict]:
    """-> (id, thread) of the open thread carrying an ID -- the handle of every verb that
    reads or writes one thread. A NAME refuses, naming the id it labels.

    documentary: a name is unique among the open threads of ONE member at ONE instant --
    the history may wear it, a neighbour may wear it, `rename` changes it; an id is minted
    once and never moves. So the address of a gesture is the id (batch la-mutation-par-id,
    operator word 2026-09-10); the name stays what the operator reads at the front."""
    thread = record["threads"].get(said)
    if thread is not None:
        return said, thread
    labelled = next((tid for tid, one in record["threads"].items() if one["name"] == said), None)
    if labelled is not None:
        refuse("thread-addressed-by-name", f"`{said}` is the NAME of {labelled} -- take a thread by its "
                                           "id (`status --all` says them); a name is a label, it changes")
    refuse("thread-unknown", f"`{said}` is no open thread -- a thread is taken by its id "
                             "`<member>.f.<n>`, read at `status --all`")


def name_free(record: dict, name: str, but: str | None = None) -> None:
    for tid, thread in record["threads"].items():
        if thread["name"] == name and tid != but:
            refuse("thread-taken", f"`{name}` already stands [{tid}] -- attach to it, or close it first")


def hosted(record: dict, name: str, thread: dict, said: str) -> tuple[str, dict]:
    """-> (id, step) of an id the thread LISTS -- a step of this dictionary, as `load` guarantees
    every listed id is."""
    sid = valid_id(said)
    if sid not in thread["steps"]:
        refuse("step-unknown", f"{sid} is not listed by {name} -- `status --all` says what stands")
    return sid, record["steps"][sid]


def hosts_of(record: dict, sid: str) -> list[str]:
    """-> the names of the open threads listing an id."""
    return [thread["name"] for thread in record["threads"].values() if sid in thread["steps"]]


def worked(record: dict, sid: str) -> None:
    """A step's status moved: the open thread listing it is dated."""
    for thread in record["threads"].values():
        if sid in thread["steps"]:
            touched(thread)


def valid_key(root: Path, record: dict, key: str, but: str | None = None) -> str:
    """-> the key, once its grammar, its uniqueness at the DICTIONARY and its family's
    verifier all agree -- one step per key: a work already keyed is found by its key, never
    minted again. The verifier is the engine's call, its no relayed under the engine's own
    code (family-unknown, vector-unverified, verifier-missing)."""
    if not VECTOR.fullmatch(key):
        refuse("key-invalid", f"`{key}` -- a key is a vector, `<family>:<slug>`")
    for sid, step in record["steps"].items():
        if step.get("key") == key and sid != but:
            where = ", ".join(hosts_of(record, sid)) or "no open thread"
            refuse("step-taken", f"{key} is {sid} already (listed by {where}) -- done, amend or renext it")
    try:
        engine().events.verified(root, key)
    except Exception as raised:            # the family's no, relayed with the engine's code
        if type(raised).__name__ != "Refusal":
            raise
        refuse(getattr(raised, "code", "key-invalid"), str(raised).split(" — ", 1)[-1])
    return key


def split_line(line: str) -> tuple[str, str | None, str]:
    """-> (name, key, text) of an `open` line -- `<name>`, `<name> | <text>`, `<name> |
    <family:slug>` and `<name> | <family:slug> | <text>`. The name opens the line because it is
    the step's identity; the text is a complement, absent allowed; a line without a name
    refuses at the birth, naming what it needs."""
    head, sep, tail = line.partition(" | ")
    if not sep:
        bare = line.strip()
        return (bare, None, "") if NAME.fullmatch(bare) else ("", None, line)
    name, rest = head.strip(), tail
    middle, sep2, tail2 = rest.partition(" | ")
    if sep2 and VECTOR.fullmatch(middle.strip()):
        return name, middle.strip(), tail2
    if not sep2 and VECTOR.fullmatch(rest.strip()):
        return name, rest.strip(), ""
    return name, None, rest


def first_open(record: dict, thread: dict, after: str | None = None) -> str | None:
    """-> the first listed id after `after` in chain order, else the first anywhere, whose
    step is open or reopened -- what a delivered pointer moves to; None when none remains."""
    ids = thread["steps"]
    start = ids.index(after) + 1 if after in ids else 0
    for sid in ids[start:] + ids[:start]:
        if record["steps"][sid]["status"] in ("open", "redo"):
            return sid
    return None


def pointers_off(record: dict, sid: str) -> None:
    """Every open thread pointing at a step just delivered, blocked or dropped moves its
    pointer on -- a step lives in every thread that lists it, once."""
    for thread in record["threads"].values():
        if thread.get("next") == sid:
            thread["next"] = first_open(record, thread, after=sid)
            touched(thread)


def guarded(root: Path):
    """The record's critical section -- every load-modify-save plays inside it: two
    sessions of one member never lose a call. The regime lives at the engine
    (`conductor.record`): one primitive for every shared record of the product."""
    return engine().record.held(state_path(root))


def born(name: str, owner: str) -> dict:
    now = stamp()
    return {"name": name, "owner": owner, "steps": [], "next": None, "opened_at": now, "worked_at": now}


def open_thread(root: Path, name: str, piped: str, note: str | None = None) -> None:
    """A thread is minted with its steps: a named line mints a step of this dictionary, born
    in this thread (`thread`). `--note` gives it its note at once."""
    with guarded(root):
        record = load(root)
        name_free(record, valid_name(root, name))
        tid = mint(root, record, "f")
        thread = born(name, member_of(root))
        if note:
            thread["note"] = clean_note(root, note)
        for line in piped.splitlines():
            line = line.strip()
            if not line:
                continue
            if ID.fullmatch(line):
                refuse("step-invalid", f"`{line}` -- a thread mints its own steps: a line is `<name>`, `<name> | <text>` "
                                       "or `<name> | <family:slug> [| <text>]`")
            # `step_name`, jamais `name` : le nom du FIL est le paramètre de cette fonction,
            # et l'écraser ici ferait dire au rendu le nom du dernier pas.
            step_name, key, text = split_line(line)
            if not step_name:
                refuse("step-invalid", f"`{line[:60]}` -- a step line is `<name>`, `<name> | <text>` or "
                                       "`<name> | <family:slug> [| <text>]`: every step wears a name, the text is a complement")
            sid = mint(root, record, "s")
            step = {"owner": member_of(root), "name": name_free_in(record, thread, valid_step_name(root, step_name)),
                    "thread": tid, "text": clean_text(root, text), "status": "open"}
            if key is not None:
                step["key"] = valid_key(root, record, key)
            record["steps"][sid] = step
            thread["steps"].append(sid)
        if not thread["steps"]:
            refuse("step-invalid", "a thread opens WITH its steps -- pipe them, one per line")
        thread["next"] = first_open(record, thread) or thread["steps"][0]
        record["threads"][tid] = thread
        save(root, record)
    print(f"pp-steering: opened -- {name} [{tid}], {len(thread['steps'])} step(s), next {thread['next']}")


def attach(root: Path, ident: str, text: str, name: str | None = None, key: str | None = None,
           source: str | None = None, owner: str | None = None, born_as: str | None = None) -> None:
    """Mints one step here and lists it in the thread of that ID. A step CROSSING from a
    neighbour (`--from <step id> --owner <member> --name <name>`) lands in the thread of that
    id whatever its name here; when none stands, the copy is BORN under that id, that owner
    and `--name` -- the one birth that inherits an id instead of minting it. The keeper
    derives nothing: the id, the source and the owner are read by the caller at the
    neighbour's record, and the name is the one the neighbour gave.

    Every step wears a NAME (`--as <name>`): it is its identity, the text a complement -- empty
    allowed, cut to the budget for a crossing, refused over it for an own step. The step is born
    in the thread it is attached to (`thread`), for good."""
    if not name:
        refuse("step-invalid", "attach <thread id> --as <name> [<text ...>] -- a step wears a name: "
                               "kebab-case, its identity, while its text is a complement")
    with guarded(root):
        record = load(root)
        if source is not None:
            if not owner:
                refuse("step-invalid", "--from takes --owner <member>: what the neighbour's record says")
            source, ident = valid_id(source), valid_id(ident)
            thread = record["threads"].get(ident)
            if thread is None:
                if not born_as:
                    refuse("step-invalid", f"no thread carries {ident} here -- `--name <name>` births the copy")
                name_free(record, valid_name(root, born_as))
                thread = born(born_as, owner.strip())
                record["threads"][ident] = thread
            tid = ident
            if any(record["steps"].get(sid, {}).get("from") == source for sid in thread["steps"]):
                refuse("step-taken", f"{source} already crossed into {thread['name']} -- a source crosses once")
        else:
            tid, thread = by_thread(record, ident)
        sid = mint(root, record, "s")
        said, cut_at = cut_text(root, text) if source is not None else (clean_text(root, text), None)
        step = {"owner": member_of(root), "name": name_free_in(record, thread, valid_step_name(root, name)),
                "thread": tid, "text": said, "status": "open"}
        if key is not None:
            step["key"] = valid_key(root, record, key)
        if source is not None:
            step["from"] = source
        record["steps"][sid] = step
        thread["steps"].append(sid)
        if thread["next"] is None:
            thread["next"] = sid                  # a chain all delivered points at what arrives
        touched(thread)
        save(root, record)
    print(f"pp-steering: attached -- {thread['name']} [{tid}] {sid}" + (f" (text cut to {cut_at} c)" if cut_at else ""))


def amend(root: Path, ident: str, said: str, text: str | None, key: str | None = None,
          name: str | None = None) -> None:
    """Changes a step's name, its text, its key, or any of them: `--as <name>` renames it (the
    grammar, free in its thread), `--key <vector>` poses or changes the key (the family's
    verifier, the unicity at the dictionary), `--key -` removes it. The name and the key are
    the step's IDENTITY: NEXT says they change on the operator's request alone; its id never
    moves. No amend dates the thread: `worked_at` is the work's, not the wording's.

    documentary: `worked_at` is the date of the thread's WORK, and the front orders by it. A
    naming or rewording pass over a whole record would otherwise restamp every thread in a
    minute and wipe the order the operator reads (operator words 2026-09-11 and 2026-09-15)."""
    if text is None and key is None and name is None:
        refuse("step-invalid", "amend <thread id> <step id> [--as <name>] [--key <family:slug>|-] "
                               "[<text ...>] -- a name, a text, a key, or several")
    with guarded(root):
        record = load(root)
        tid, thread = by_thread(record, ident)
        sid, step = hosted(record, thread['name'], thread, said)
        if name is not None:
            step["name"] = name_free_in(record, thread, valid_step_name(root, name), but=sid)
        if text is not None:
            step["text"] = clean_text(root, text)
        if key == "-":
            step.pop("key", None)
        elif key is not None and key != step.get("key"):
            step["key"] = valid_key(root, record, key, but=sid)
        save(root, record)
    print(f"pp-steering: amended -- {thread['name']} {sid}")


def done(root: Path, ident: str, said: str) -> None:
    """Delivers a step, once for every thread that lists it: its status, and every pointer
    on it -- moved to the next open step in each thread's order, None once every step is
    delivered."""
    with guarded(root):
        record = load(root)
        tid, thread = by_thread(record, ident)
        sid, step = hosted(record, thread['name'], thread, said)
        step["status"] = "done"
        step.pop("reason", None)
        pointers_off(record, sid)
        worked(record, sid)
        save(root, record)
    following = f"next {thread['next']}" if thread["next"] is not None else "every step delivered"
    print(f"pp-steering: done -- {thread['name']} {sid}, {following}")


def block(root: Path, ident: str, said: str, reason: str) -> None:
    """A step waits: `blocked`, its reason kept at the step; every pointer on it moves on.
    `done` or `renext` release it."""
    with guarded(root):
        record = load(root)
        tid, thread = by_thread(record, ident)
        sid, step = hosted(record, thread['name'], thread, said)
        step["status"] = "blocked"
        step["reason"] = clean_text(root, reason)
        pointers_off(record, sid)
        worked(record, sid)
        save(root, record)
    print(f"pp-steering: blocked -- {thread['name']} {sid}")


def drop(root: Path, ident: str, said: str) -> None:
    """A step leaves the work: `dropped`, kept at the dictionary (a step that crossed must
    stay consumed), out of the counts and the front, read at `--all`; every pointer on it
    moves on."""
    with guarded(root):
        record = load(root)
        tid, thread = by_thread(record, ident)
        sid, step = hosted(record, thread['name'], thread, said)
        step["status"] = "dropped"
        step.pop("reason", None)
        pointers_off(record, sid)
        worked(record, sid)
        save(root, record)
    print(f"pp-steering: dropped -- {thread['name']} {sid}")


def reorder(root: Path, ident: str, said: str, rank: str) -> None:
    with guarded(root):
        record = load(root)
        tid, thread = by_thread(record, ident)
        sid, _ = hosted(record, thread['name'], thread, said)
        count = len(thread["steps"])
        if not (rank.isdigit() and 1 <= int(rank) <= count):
            refuse("step-invalid", f"ranks are 1..{count}")
        thread["steps"].remove(sid)
        thread["steps"].insert(int(rank) - 1, sid)
        touched(thread)
        save(root, record)
    print(f"pp-steering: reordered -- {thread['name']} {sid} -> rank {rank}")


def move(root: Path, ident: str, said: str, target: str) -> None:
    """A step changes thread: its id leaves this thread's list for the end of the target's, and
    the step itself does not change -- `thread` keeps where it was born. The source's pointer
    moves on when it named the step; the target's takes it when it was empty and the step is to
    do; both threads are dated. A step crossed from a neighbour, and a thread another member
    owns, keep the link federation reads: they do not move."""
    with guarded(root):
        record = load(root)
        tid, thread = by_thread(record, ident)
        if target.lstrip("#") == tid:
            refuse("step-invalid", f"{tid} is the thread the step stands in -- name another thread")
        to_id, to = by_thread(record, target.lstrip("#"))
        sid, step = hosted(record, thread["name"], thread, said)
        if step.get("from"):
            refuse("step-crossed", f"{sid} crossed from {step['from']} -- it stays where the crossing landed it")
        me = member_of(root)
        for one_id, one in ((tid, thread), (to_id, to)):
            if one["owner"] != me:
                refuse("thread-foreign", f"{one['name']} [{one_id}] belongs to {one['owner']} -- a move stays among this "
                                         "member's own threads")
        name_free_in(record, to, step["name"])
        at = thread["steps"].index(sid)
        thread["steps"].remove(sid)
        if thread["next"] == sid:
            rest = thread["steps"][at:] + thread["steps"][:at]
            thread["next"] = next((one for one in rest if record["steps"][one]["status"] in ("open", "redo")), None)
        to["steps"].append(sid)
        if to["next"] is None and step["status"] in ("open", "redo"):
            to["next"] = sid
        touched(thread)
        touched(to)
        save(root, record)
    print(f"pp-steering: moved -- {sid} {step['name']} : {thread['name']} -> {to['name']} [{to_id}]")


def renext(root: Path, ident: str, said: str) -> None:
    """Points a listed id as the next move. A DELIVERED step of this dictionary pointed again
    REOPENS: its status passes to `redo` -- the work comes back, the step keeps its id, its
    key and its place; a blocked or dropped one is released.

    documentary: a work that comes back finds its step (the key is unique at the
    dictionary) and points it; reopening is the pointer's own meaning, no verb of its own
    (batch le-rendu-des-fils, arbitrage 8)."""
    with guarded(root):
        record = load(root)
        tid, thread = by_thread(record, ident)
        sid, step = hosted(record, thread['name'], thread, said)
        reopened = step["status"] == "done"
        released = step["status"] in ("blocked", "dropped")
        if reopened:
            step["status"] = "redo"
        elif released:
            step["status"] = "open"
            step.pop("reason", None)
        thread["next"] = sid
        touched(thread)
        if reopened or released:
            worked(record, sid)
        save(root, record)
    print(f"pp-steering: next -- {thread['name']} -> {sid}" + (" (reopened)" if reopened else " (released)" if released else ""))


def set_note(root: Path, ident: str, text: str) -> None:
    """The thread's NOTE -- its why, then what to know now -- rewritten. Like a rename, it is no
    work: `worked_at` does not move."""
    with guarded(root):
        record = load(root)
        tid, thread = by_thread(record, ident)
        note = clean_note(root, text)
        if note:
            thread["note"] = note
        else:
            thread.pop("note", None)
        save(root, record)
    print(f"pp-steering: noted -- {thread['name']} [{tid}]")


def rename(root: Path, ident: str, new: str) -> None:
    """The thread's name is its IDENTITY: NEXT says it changes on the operator's request alone;
    the id stays, and the date of the work does not move."""
    with guarded(root):
        record = load(root)
        tid, thread = by_thread(record, ident)
        was = thread["name"]
        name_free(record, valid_name(root, new), but=tid)
        thread["name"] = new
        save(root, record)
    print(f"pp-steering: renamed -- {was} -> {new} [{tid}]")


def held_back(root: Path, tid: str) -> None:
    """The family's GUARDIAN, asked through the engine before a thread retires -- this
    package names no other: the registry says who guards `steering-thread:`, the engine runs
    it; no guardian declared, nothing plays. A no is said back as `thread-guarded`."""
    try:
        engine().events.guarded(root, f"{FAMILY}:{tid}")
    except Exception as raised:            # the guardian's no, relayed with its reason
        if type(raised).__name__ != "Refusal":
            raise
        refuse("thread-guarded", str(raised).split(" — ", 1)[-1])


def retire(root: Path, record: dict, tid: str, closed_as: str) -> dict:
    """The thread leaves the open threads for the history -- the thread with its id, its ids and
    `closed_as` (`delivered` or `dropped`); the steps stay at the dictionary. -> the entry written."""
    thread = record["threads"].pop(tid)
    touched(thread)                               # a closure is work: the entry carries its date
    entry = {"id": tid}
    entry.update({key: value for key, value in thread.items() if key != "next"})
    entry["closed_at"] = stamp()
    entry["closed_as"] = closed_as
    with (state_path(root).parent / HISTORY_NAME).open("a", encoding="utf-8") as history:
        history.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def close(root: Path, ident: str) -> None:
    """The lifecycle's end: the thread leaves the state, its history is appended -- the
    thread with its ids, the steps staying at the dictionary, so a closed chain is readable
    whole and never comes back of itself. The family's guardian, when one is declared, is
    asked first: a thread a neighbour still works stays. `closed_as` says what the closure
    delivered: `delivered` when every listed step is done or dropped and at least one is
    listed, `dropped` otherwise -- a thread listing nothing delivers nothing."""
    tid, _ = by_thread(load(root), ident)
    held_back(root, tid)
    with guarded(root):
        record = load(root)
        tid, thread = by_thread(record, ident)
        mine = [record["steps"][sid] for sid in thread["steps"]]
        entry = retire(root, record, tid, "delivered" if mine and all(one["status"] in ("done", "dropped") for one in mine) else "dropped")
        save(root, record)
    print(f"pp-steering: closed -- {thread['name']} [{tid}], {len(entry['steps'])} id(s) to the history")


def reopen(root: Path, ident: str) -> None:
    """A closed thread comes back from the history BY ITS ID: its name, its owner and its
    ids as at the closure -- the steps never left the dictionary -- the pointer on the first
    open step, `worked_at` now; the history entry stays and says `reopened_at`. The name it
    wore must be free: another thread may have taken it while this one slept. A closure
    listing an id this dictionary does not hold is of a former shape: refused
    -- the history is read here alone, so this is where it is judged."""
    with guarded(root):
        record = load(root)
        if ident in record["threads"]:
            refuse("thread-taken", f"[{ident}] already stands open as `{record['threads'][ident]['name']}`")
        graves = state_path(root).parent / HISTORY_NAME
        lines = graves.read_text(encoding="utf-8").splitlines() if graves.is_file() else []
        at = next((i for i in range(len(lines) - 1, -1, -1)
                   if lines[i].strip() and json.loads(lines[i]).get("id") == ident), None)
        if at is None:
            refuse("thread-unknown", f"`{ident}` is no closed thread -- the history holds no thread of that id")
        entry = json.loads(lines[at])
        if entry.get("braid"):
            refuse("state-legacy", f"closure `{ident}` is a braid -- the model has none since steering 0.6.0")
        strangers = [sid for sid in entry.get("steps", []) if sid not in record["steps"]]
        if strangers:
            refuse("state-legacy", f"closure `{ident}` lists {strangers[0]}, an id this dictionary does not hold -- "
                                   "this version of steering does not read it")
        name_free(record, str(entry.get("name", "")))
        thread = {key: value for key, value in entry.items()
                  if key not in ("id", "closed_at", "closed_as", "reopened_at")}
        thread["next"] = first_open(record, thread)
        touched(thread)
        record["threads"][entry["id"]] = thread
        entry["reopened_at"] = stamp()
        lines[at] = json.dumps(entry, ensure_ascii=False)
        engine().record.replace(graves, "\n".join(lines) + "\n")
        save(root, record)
    print(f"pp-steering: reopened -- {thread['name']} [{entry['id']}], {len(thread['steps'])} id(s)")


def fenced(text: str) -> str:
    """-> the text as inline code -- double fences when the text itself carries a backtick."""
    return f"`` {text} ``" if "`" in text else f"`{text}`"


def ago(iso: str, now: datetime) -> str:
    """-> the time elapsed since a stamp, in the coarsest unit that still says it: `now`
    under a minute, `12 min` under an hour, `1h 35 min` under a day, `> 1 day` under two,
    `3 days` under a week, `2 weeks` under a month, `~3 months` under a year, `~1.4 years`.

    documentary: a date asks the reader to compute; the elapsed time is what steering
    reads at a glance (operator word 2026-09-06, batch le-rendu-des-fils reopened)."""
    try:
        then = datetime.fromisoformat(iso)
    except ValueError:
        return iso
    seconds = max(0, int((now - then).total_seconds()))
    minutes, hours, days = seconds // 60, seconds // 3600, seconds // 86400
    if minutes < 1:
        return "now"
    if hours < 1:
        return f"{minutes} min"
    if days < 1:
        return f"{hours}h {minutes % 60} min" if minutes % 60 else f"{hours}h"
    if days < 2:
        return "> 1 day"
    if days < 7:
        return f"{days} days"
    if days < 30:
        weeks = days // 7
        return f"{weeks} week" + ("s" if weeks > 1 else "")
    if days < 365:
        months = days // 30
        return f"~{months} month" + ("s" if months > 1 else "")
    return f"~{days / 365:.1f} years"


def mark_of(step: dict) -> str:
    """-> the step's mark: `🔄` reopened · `⛔` waiting · `📥` crossed in, awaiting the GO ·
    `✉️` addressed to a neighbour, awaiting its answer · nothing for a plain open step."""
    if step["status"] == "redo":
        return "🔄"
    if step["status"] == "blocked":
        return "⛔"
    if step.get("from"):
        return "📥"
    if str(step.get("text", "")).startswith("@"):
        return "✉️"
    return ""


def freshest(threads: dict) -> list:
    """-> (id, thread) pairs, the last worked first, ties by name."""
    return sorted(sorted(threads.items(), key=lambda pair: pair[1]["name"]),
                  key=lambda pair: pair[1].get("worked_at", ""), reverse=True)


def rendered(tid: str, thread: dict, record: dict, open_only: bool = False) -> str:
    """-> one thread's LEDGER block, the agent's view: `~ <name> [<id>] (<owner>)` and the note
    after `—` when it has one, then every listed id -- `✓` delivered, `->` the next move, `🔄`
    reopened, `⛔` waiting, `🗑️` dropped, blank open -- with its NAME, its text, then its reason in
    parentheses for a waiting step, and its key. `open_only` keeps the steps still to do (`open`,
    `redo`, `blocked`): the form the boot serves, where a delivered step says nothing the session
    needs."""
    note = f" — {thread['note']}" if thread.get("note") else ""
    lines = [f"~ {thread['name']} [{tid}] ({thread['owner']}){note}"]
    for sid in thread["steps"]:
        step = record["steps"][sid]
        if open_only and step["status"] not in ("open", "redo", "blocked"):
            continue
        mark = ("✓ " if step["status"] == "done" else "->" if sid == thread["next"]
                else {"redo": "🔄", "blocked": "⛔", "dropped": "🗑️"}.get(step["status"], "  "))
        waiting = step.get("reason") if step["status"] == "blocked" else None
        said = f"{step['text']} ({waiting})" if waiting and step.get("text") else (waiting or step.get("text"))
        text = f" — {said}" if said else ""
        key = f"   [{step['key']}]" if step.get("key") else ""
        lines.append(f" {mark} {sid} {step['name']}{text}{key}")
    return "\n".join(lines)


def bar(done_n: int, total: int) -> str:
    """-> five cells `▰▱`, filled at the ratio delivered / total rounded to the nearest cell."""
    filled = (10 * done_n // total + 1) // 2 if total else 0
    return "▰" * filled + "▱" * (5 - filled)


def actions_of(record: dict, thread: dict, cap: int) -> tuple[str, bool]:
    """-> (the row's next actions, whether the thread has any): the pointed step first, then
    the following steps still to do (`open`, `redo`) in the thread's order, each name between
    backticks with its mark, `cap` of them at most and `…` when more remain."""
    ids = thread["steps"]
    start = ids.index(thread["next"]) if thread.get("next") in ids else 0
    live = [sid for sid in ids[start:] + ids[:start] if record["steps"][sid]["status"] in ("open", "redo")]
    said = " · ".join(f"{fenced(record['steps'][sid]['name'])}{mark_of(record['steps'][sid])}" for sid in live[:cap])
    return said + (" …" if len(live) > cap else ""), bool(live)


def cell(text: str) -> str:
    """-> text safe inside a markdown table cell: a pipe would open a column."""
    return text.replace("|", "\\|")


def setting(root: Path, key: str, fallback: int) -> int:
    """-> an integer setting for a RENDER: an invalid value renders with the fallback, never refuses."""
    try:
        return budget(root, key, fallback)
    except SystemExit:
        return fallback


def front(root: Path, record: dict, threads: dict | None = None, now: datetime | None = None) -> str:
    """-> the threads as the NEXT pastes them -- the USER-FACING view, no id in it:

    - the TABLE `initiative | note | progress | age | next action(s)`, freshest first: one row
      per open thread with a step still to do (`open`, `redo`) -- a thread whose remaining steps
      all wait has no row, its steps stand at the ⏸ line; the note or `—`; a five-cell bar with
      delivered/total and the reopened count; the age of its work; up to `steering_next_max`
      next actions, then `…`;
    - the `⏸` line, when any step waits: `fil › step (reason)`, up to `steering_line_max`, then `+n`;
    - the `💤` footer: a thread with no work for `steering_dormant_days` days folds there, with its
      pointed step and its age -- but only past the `steering_front_min` freshest rows, so the
      table is never empty while threads stand (operator word 2026-09-19).

    documentary: the operator reads the work of the moment at a glance -- what each thread is for
    (its note), what comes next (up to three actions), what waits and why; an id has no meaning
    for the operator, the agent reads them at the ledger."""
    me = member_of(root)
    now = now or datetime.now(timezone.utc)
    threads = record["threads"] if threads is None else threads
    dormant_days = setting(root, DORMANT_KEY, DORMANT_FALLBACK)
    next_max = max(1, setting(root, NEXT_MAX_KEY, NEXT_MAX_FALLBACK))
    line_max = max(1, setting(root, LINE_MAX_KEY, LINE_MAX_FALLBACK))
    front_min = max(0, setting(root, FRONT_MIN_KEY, FRONT_MIN_FALLBACK))
    rows, folded, waiting = [], [], []
    for tid, thread in freshest(threads):
        mine = [s for s in (record["steps"][sid] for sid in thread["steps"])
                if s["status"] != "dropped"]      # a dropped step is out of the front
        waiting += [f"{thread['name']} › {fenced(s['name'])}" + (f" ({s['reason']})" if s.get("reason") else "")
                    for s in mine if s["status"] == "blocked"]
        actions, live = actions_of(record, thread, next_max)
        if not live:
            continue                              # nothing to do here now: its waiting steps say it at ⏸
        done_n = sum(1 for s in mine if s["status"] == "done")
        redo_n = sum(1 for s in mine if s["status"] == "redo")
        flags = "🔗" if thread["owner"] != me else ""
        name = f"{flags}{' ' if flags else ''}{thread['name']}"
        age = ago(thread.get("worked_at", ""), now)
        try:
            asleep = (now - datetime.fromisoformat(thread.get("worked_at", ""))).days >= dormant_days
        except ValueError:
            asleep = False
        if asleep and len(rows) >= front_min:
            first = actions.split(" · ")[0].rstrip(" …")
            folded.append(f"{name} {first} ({age})")
            continue
        progress = f"{bar(done_n, len(mine))} {done_n}/{len(mine)}" + (f" 🔄{redo_n}" if redo_n else "")
        rows.append(f"| {name} | {cell(thread.get('note') or '—')} | {progress} | {age} | {actions} |")
    parts = []
    if rows:
        parts.append("\n".join(["| initiative | note | progress | age | next action(s) |",
                                 "|---|---|---|---|---|", *rows]))
    tail = []
    if waiting:
        tail.append("⏸ " + " · ".join(waiting[:line_max]) + (f" · +{len(waiting) - line_max}" if len(waiting) > line_max else ""))
    if folded:
        tail.append("💤 " + " · ".join(folded))
    if tail:
        parts.append("\n".join(tail))
    return "\n\n".join(parts)


def status(root: Path, ident: str | None, everything: bool = False, due_only: bool = False,
           open_only: bool = False) -> str:
    """-> the render: the front (table and footer) the NEXT pastes, or with `everything` the
    whole ledger, one block per open thread -- both freshest first. One thread is taken by
    its ID, like every verb that writes; the name it wears is what the front then shows. With
    `due_only` -- the NEXT's provider -- the front only when the table is due to the run that
    asks, else the one line saying it did not change; the front served under the flag is
    what the run has SEEN: its snapshot is kept for the next comparison."""
    record = load(root)
    threads = record["threads"]
    if ident is not None:
        tid, thread = by_thread(record, ident)
        threads = {tid: thread}
    if not threads:
        return "pp-steering: no open thread"
    run = run_context(root) if due_only else None
    if due_only and not due(record, run, load_seen(root).get(run.key) if run else None):
        return NOT_CHANGED
    if due_only and run is not None:
        seen_now(root, run, record)
    if everything:
        return "\n\n".join(rendered(tid, thread, record, open_only) for tid, thread in freshest(threads))
    return front(root, record, None if ident is None else threads)


def seen_path(root: Path) -> Path:
    return root / ".sys" / "records" / SEEN_NAME


def load_seen(root: Path) -> dict:
    """-> what each run has seen: `{<run key>: {"exchange": n, "threads": {<thread id>:
    worked_at}}}`, the open threads as the table was last served to the run and the exchange
    it was served at -- empty when there is none or the file does not parse: a snapshot lost
    costs one table, never a refusal."""
    path = seen_path(root)
    if not path.is_file():
        return {}
    try:
        seen = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return {}
    return seen if isinstance(seen, dict) else {}


def snapshot(record: dict) -> dict:
    """-> `{<thread id>: worked_at}` of the open threads: what the table is made of. A thread
    added (an id more), closed (an id less) or worked (a date moved -- a step's status, a step
    added, reordered, pointed, listed) changes it; an amend or a rename does not."""
    return {tid: thread.get("worked_at") for tid, thread in record["threads"].items()}


def run_context(root: Path):
    """-> the run the engine named to this process (`PP_RUN`), None when none does -- a gesture
    played by hand, a script the bench runs."""
    try:
        return engine().context.current(root)
    except Exception as raised:
        if type(raised).__name__ == "Refusal" and getattr(raised, "code", "") in ("context-no-run", "run-unknown"):
            return None
        raise


def due(record: dict, run, seen: dict | None) -> bool:
    """-> whether the table is due to the run that asks: no run names the script, the run boots
    (its first exchange, or a compaction declared this exchange), it has seen no table, the
    table was served to it at THIS exchange already (one exchange sees one table, whatever
    the number of renderings), or the open threads differ from the table it last saw -- a
    thread added, closed or worked since, by this run or by any other hand, during a turn or
    between two: what is compared is the data now against the table last served, never the
    turn's beginning."""
    if run is None or run.is_boot():
        return True
    if not isinstance(seen, dict) or not isinstance(seen.get("threads"), dict):
        return True
    return seen.get("exchange") == run.exchange() or seen["threads"] != snapshot(record)


def seen_now(root: Path, run, record: dict) -> None:
    """The table is being served to the run: its snapshot and the exchange are kept as what
    the run has SEEN, and the runs whose slot is gone are forgotten. Nothing is written when
    the record already says it."""
    with engine().record.held(seen_path(root)):
        seen = load_seen(root)
        kept = {key: one for key, one in seen.items()
                if key != run.key and engine().persistence.slot_of(root, key).exists()}
        kept[run.key] = {"exchange": run.exchange(), "threads": snapshot(record)}
        if kept != seen:
            engine().record.replace(seen_path(root), json.dumps(kept, ensure_ascii=False, indent=1) + "\n")


DATA_VERSION = 3   # the schema `data` prints -- a reader of another version refuses it by this number


def closed_ids(root: Path, record: dict) -> list[str]:
    """-> the ids of the threads the history holds and that are not open now, in the
    history's order, once each."""
    graves = state_path(root).parent / HISTORY_NAME
    seen: list[str] = []
    for line in (graves.read_text(encoding="utf-8").splitlines() if graves.is_file() else []):
        if not line.strip():
            continue
        try:
            ident = json.loads(line).get("id")
        except ValueError:
            continue
        if ident and ident not in record["threads"] and ident not in seen:
            seen.append(ident)
    return seen


def data(root: Path, bare: bool = False) -> dict:
    """-> the member's OPEN threads as data, the public surface another package reads instead of
    the record: each thread's id, name, owner, note, stamps, counts, the id of its pointed
    step, and its steps still to do -- `open`, `redo`, `blocked` -- in the thread's order, each
    served ONCE, in its thread; a delivered or dropped step is never in it; and `closed`, the ids
    of the threads the history holds. `bare` drops every text and reason: the form a renderer
    reads when it needs states and names alone. READ-ONLY, no lock, like `verify`: the script
    of a member answers for that member, wherever it is run from."""
    record = load(root)

    def step_of(sid: str) -> dict:
        step = record["steps"][sid]
        said = {"id": sid, "name": step.get("name"), "status": step["status"]}
        if not bare:
            said["text"] = step["text"]
        said.update({field: step[field] for field in ("key", "from") if step.get(field)})
        if not bare and step.get("reason"):
            said["reason"] = step["reason"]
        return said

    threads = []
    for tid, thread in freshest(record["threads"]):
        held = [record["steps"][sid] for sid in thread["steps"]]
        counts = {status: sum(1 for step in held if step["status"] == status)
                  for status in ("done", "redo", "open", "blocked")}
        threads.append({"id": tid, "name": thread["name"], "owner": thread["owner"],
                        **({"note": thread["note"]} if thread.get("note") and not bare else {}),
                        "opened_at": thread.get("opened_at"), "worked_at": thread.get("worked_at"),
                        "counts": counts,
                        "next": thread.get("next") or None,
                        "steps": [step_of(sid) for sid in thread["steps"]
                                  if record["steps"][sid]["status"] in ("open", "redo", "blocked")]})
    return {"version": DATA_VERSION, "member": member_of(root), "threads": threads,
            "closed": closed_ids(root, record)}


def verify(root: Path, vector: str) -> None:
    """This package's VERIFIER, the engine's call at every entry and service of the bus:
    a `steering-thread:<thread id>` vector is valid when an OPEN thread of the record carries
    that id. A closed thread is no node any more -- its held line drops at the service, the
    verifier being the broom; a family this package does not declare is not its to judge.
    READ-ONLY, no lock: exit 2 says no, nothing written."""
    prefix, _, ident = vector.strip().partition(":")
    if prefix != FAMILY:
        refuse("family-foreign", f"`{prefix}:` is not a family steering declares ({FAMILY}); "
                                 "its owner verifies it")
    if not ident or ident not in load(root)["threads"]:
        refuse("thread-unknown", f"`{ident}` is no open thread -- a vector points at the id of a "
                                 "thread the record holds open (`status --all` says it), never at one "
                                 "closed or never opened")


def flagged(rest: list[str], flag: str) -> tuple[list[str], str | None]:
    """-> (rest without `flag value`, the value; None when absent)."""
    if flag not in rest:
        return rest, None
    at = rest.index(flag)
    if at + 1 >= len(rest):
        refuse("step-invalid", f"{flag} takes a value")
    return rest[:at] + rest[at + 2:], rest[at + 1]


def main(argv: list[str]) -> int:
    if not argv:
        sys.stderr.write(__doc__)
        return 2
    verb, rest = argv[0], argv[1:]
    root = home()
    if verb == "verify" and not rest:
        verify(root, sys.stdin.read())          # read-only: the engine asks, the record answers
    elif verb == "open" and rest:
        rest, note = flagged(rest, "--note")
        if len(rest) != 1:
            refuse("step-invalid", "open <name> [--note <text>] -- the steps piped, one per line")
        open_thread(root, rest[0], sys.stdin.read(), note)
    elif verb == "note" and len(rest) >= 2:
        set_note(root, rest[0], " ".join(rest[1:]))
    elif verb == "attach" and len(rest) >= 1:
        rest, as_name = flagged(rest, "--as")
        rest, key = flagged(rest, "--key")
        rest, source = flagged(rest, "--from")
        rest, owner = flagged(rest, "--owner")
        rest, born_as = flagged(rest, "--name")
        if len(rest) < 1:
            refuse("step-invalid", "attach <thread id> --as <name> [--key <family:slug>] "
                                   "[--from <step id> --owner <member> --name <thread name>] [<text ...>]")
        attach(root, rest[0], " ".join(rest[1:]), as_name, key, source, owner, born_as)
    elif verb == "amend" and len(rest) >= 2:
        rest, as_name = flagged(rest, "--as")
        rest, key = flagged(rest, "--key")
        if len(rest) < 2:
            refuse("step-invalid", "amend <thread id> <step id> [--as <name>] [--key <family:slug>|-] [<text ...>]")
        amend(root, rest[0], rest[1], " ".join(rest[2:]) if len(rest) > 2 else None, key, as_name)
    elif verb == "block" and len(rest) >= 3:
        block(root, rest[0], rest[1], " ".join(rest[2:]))
    elif verb == "drop" and len(rest) == 2:
        drop(root, rest[0], rest[1])
    elif verb == "reopen" and len(rest) == 1:
        reopen(root, rest[0])
    elif verb == "done" and len(rest) == 2:
        done(root, rest[0], rest[1])
    elif verb == "move" and len(rest) == 3:
        move(root, rest[0], rest[1], rest[2])
    elif verb == "reorder" and len(rest) == 3:
        reorder(root, rest[0], rest[1], rest[2])
    elif verb == "renext" and len(rest) == 2:
        renext(root, rest[0], rest[1])
    elif verb == "rename" and len(rest) == 2:
        rename(root, rest[0], rest[1])
    elif verb == "close" and len(rest) == 1:
        close(root, rest[0])
    elif verb == "data" and rest in ([], ["--bare"]):
        print(json.dumps(data(root, bare=bool(rest)), ensure_ascii=False))
    elif (verb == "status" and len(rest) <= 4 and len([r for r in rest if r not in ("--all", "--due", "--open")]) <= 1
          and ("--open" not in rest or "--all" in rest)):
        taken = [r for r in rest if r not in ("--all", "--due", "--open")]
        print(status(root, taken[0] if taken else None, everything="--all" in rest, due_only="--due" in rest,
                     open_only="--open" in rest))
    else:
        sys.stderr.write(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
