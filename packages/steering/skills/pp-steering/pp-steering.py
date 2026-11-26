#!/usr/bin/env python3
"""DETERMINISTIC keeper of the STEPS -- the work owed in this workspace.

THREE records of the instance's store (`conductor.store`, `.sys/records/records.db`), each
entry under its key:

  steps     key `<id>`, body `{name, at, work, comment, status, reason, labels, key, touched, closed,
            archived, recalled}}` -- a step is one unit of work owed. Its NAME (lowercase words joined by hyphens) and its WORK
            (the work, written to be understood alone) are fixed when it is added: no verb
            writes them again. Its COMMENT says what happened to it since, rewritten freely.
            Its status is `open`, `waiting` (its reason kept), `done` or `dropped` (its reason
            kept). `at` is its birth; `touched` moves with its comment and its status; `closed`
            is when `done` or `drop` closed it, empty while it is still to do; a step's AGE runs from
            its recall when it has one, from `touched` otherwise. A KEY,
            when the work has an address elsewhere, is a vector verified through the engine and
            unique at the record. `archived` is empty while the step is active.
  labels    key `<name>`, body `{note, order}` -- a label groups steps: `order` lists its steps' ids in
            the order wanted, `note` says why. A step carries zero, one or several labels;
            dissolving a label leaves its steps as they are.
  counters  key `s`, body `{value}` -- the step counter, never rewound.

Every move writes the step it touches -- and the labels and the counter it touches -- by `put`, in
ONE transaction of the store; `apply` plays all its moves in one. The reads reach the ACTIVE steps
(`archived` empty) by the index of `archived`, never walking the archived ones; `--archived` reads
one page of the store's bound, its total said at the foot.

The ID (`<member>.s.<n>`) is what every verb takes, short (`s.<n>`) for a step of the
instance's member; the NAME is what a step is called by when the principal reads it -- every
text rendering shows both, the id short, and the data (`--json`) the whole id. A name is unique among the steps
still to do (`open`, `waiting`): a closed step frees its name.

  pp-steering.py add <name> <work ...> [--label <l>]... [--key <family:slug>]
                    [--priority p1|p2|p3] [--level critical|high|medium|low]
                                               -> the priority and the level are LABELS, posed
                                                  after the others
  pp-steering.py comment <id> <text ...>          -> the comment rewritten (empty: none)
  pp-steering.py done <id>
  pp-steering.py drop <id> <reason ...>
  pp-steering.py wait <id> <reason ...>
  pp-steering.py open <id>                        -> back to work, the reason cleared
  pp-steering.py label <id> +<label>|-<label> ... -> labels added or taken off
  pp-steering.py priority <id> p1|p2|p3            -> the priority label posed, the step's other
                                                  priority label taken off
  pp-steering.py level <id> critical|high|medium|low
                                               -> the level label posed, the step's other level
                                                  label taken off
  pp-steering.py note <label> <text ...>          -> the label's note
  pp-steering.py order <label> <id> ...           -> those steps first, in that order
  pp-steering.py dissolve <label>                 -> the label leaves the record and its steps
  pp-steering.py list [--label <l>] [--status <s>]... [--key <family>]... [--older <n>d]
                    [--newer <n>d] [--since <date>] [--before <date>] [--all | --archived]
                    [--by label|age|status] [--sweep] [--json]
                                               -> the active steps still to do, the most
                                                  recently touched first; `--all` adds the
                                                  closed ones, `--status` keeps the statuses
                                                  named, `--key` the families of key named;
                                                  `--archived` shows one page of the archived
                                                  ones every filter keeps, the newest born first,
                                                  and says the total of that selection -- its
                                                  --json `{rows, total, bound}`;
                                                  `--older`/`--newer` read the age,
                                                  `--since`/`--before` the birth; `--by` groups
                                                  the lines; `--sweep` sweeps first and names
                                                  at the foot what it has just archived
  pp-steering.py board [--json]                   -> the counts, the last 7 days, the durations,
                                                  the least touched, each label with its
                                                  freshest steps
  pp-steering.py labels [--all | --archived] [--json]
                                               -> one line per label, its note and counts;
                                                  `--archived` counts one page of the archived
                                                  steps, the newest born first, its --json
                                                  `{rows, total, bound}`
  pp-steering.py apply -                          -> stdin, one move per line (done, drop, wait,
                                                  open, comment, label, recall, priority,
                                                  level): all written
                                                  at once, or nothing
  pp-steering.py view <verb> [args]               -> a reading alone: board, labels, list (no
                                                  --sweep), show, review -- the console verb
                                                  `./pp steering` plays it, without a run
  pp-steering.py show <id> [--json]               -> one step, whole
  pp-steering.py sweep                            -> archives the steps untouched for
                                                  `steering_life_days`, then the least
                                                  recently touched steps still to do past
                                                  `steering_active_max`; says each one
  pp-steering.py recall <id>                      -> an archived step back, its age restarted
  pp-steering.py review [--json]                  -> the active steps still to do, the least
                                                  recently touched first

Refusals -- exit 2, nothing written: step-invalid, step-unknown, status-invalid, name-invalid,
name-taken, budget, key-invalid, step-taken, label-unknown, step-active, apply-refused,
view-read-only, priority-invalid, level-invalid, state-malformed, state-unmigrated (a former
`steps.json` or `threads.json` stands and the store holds no counter yet: the house takes it
over first, the file is never read); a key the family's verifier refuses is relayed under the
engine's own code; a refusal of the store (busy, corrupt) under its own. The clock reads `PP_NOW`
(a date and time such as 2026-10-25T16:00:00+00:00) when it is set. No network, ever.

The conductor plays this skill: an agent reaches it as `./pp <key> -s pp-steering ...`.
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

STEPS, LABELS, COUNTERS = "steps", "labels", "counters"    # the keeper's records in the store
FORMER = ("steps.json", "threads.json")   # the files of the former forms: never read, their presence alone said
INDEXED = ("archived", "status", "name", "key")             # the fields of a step the store indexes
PRIORITIES = ("p1", "p2", "p3")                             # the priority labels the verb poses
LEVELS = ("critical", "high", "medium", "low")              # the level labels the verb poses
STEP_BUDGET_KEY, STEP_BUDGET_FALLBACK = "steering_step_budget", 100    # a work, a comment, a reason
NAME_MAX_KEY, NAME_MAX_FALLBACK = "steering_name_max", 60
NOTE_BUDGET_KEY, NOTE_BUDGET_FALLBACK = "steering_note_budget", 80     # a label's note
LIFE_KEY, LIFE_FALLBACK = "steering_life_days", 15            # the days a step stays active untouched
ACTIVE_MAX_KEY, ACTIVE_MAX_FALLBACK = "steering_active_max", 60   # the active steps still to do, at most
PER_LABEL_KEY, PER_LABEL_FALLBACK = "steering_board_per_label", 3   # the freshest steps the board shows per label
CLOCK = "PP_NOW"                 # an ISO instant the clock reads instead of the system's
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")   # kebab-case, the slugs' own grammar
VECTOR = re.compile(r"^[a-z][a-z0-9_-]*:\S+$")   # a key: `<family>:<slug>`, the bus's own grammar
FAMILY = re.compile(r"^[a-z][a-z0-9_-]*$")        # the family of a key, the part before its `:`
ID = re.compile(r"^\S+\.s\.[0-9]+$")             # a step id's SHAPE -- read for its shape alone
SHORT = re.compile(r"^s\.[0-9]+$")               # the short id of a step of the instance's member
DAYS = re.compile(r"^([0-9]+)d$")                 # an age: whole days
STATUSES = ("open", "waiting", "done", "dropped")
DUE = ("open", "waiting")        # the steps still to do: their names are unique
FIELDS = ("name", "at", "work", "comment", "status", "reason", "labels", "key", "touched", "closed", "archived",
          "recalled")
CLOSED = ("done", "dropped")     # the statuses that date `closed`
MOVES = ("done", "drop", "wait", "open", "comment", "label", "recall", "priority", "level")   # what `apply` plays
READS = ("board", "labels", "list", "show", "review")   # what `view` lets through


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
        refuse(getattr(raised, "code", "setting-invalid"), str(raised).split(" — ", 1)[-1])
    try:
        return int(found)
    except (TypeError, ValueError):
        refuse("setting-invalid", f"`{key}: {found}` is not a whole number")


# --- the record --------------------------------------------------------------------------

def store(root: Path):
    """-> the instance's store: the one way to its records."""
    return engine().store.of(root)


def every(reader, record: str, **query) -> list:
    """-> every entry a query selects, in rank order, read in pages of the store's bound -- for a
    selection bounded by construction alone: the active steps, the labels."""
    found, cursor = [], None
    while True:
        page = reader.read(record, order="asc", **query, **({} if cursor is None else {"after": cursor}))
        found += page.rows
        if page.next is None:
            return found
        cursor = page.next["after"]


def checked(sid: str, step) -> dict:
    """-> the step as the store holds it, once its shape is a step's; `state-malformed` otherwise."""
    if (not isinstance(sid, str) or not ID.fullmatch(sid) or not isinstance(step, dict) or set(step) != set(FIELDS)
            or step["status"] not in STATUSES or not step["name"] or not step["work"]
            or not isinstance(step["labels"], list)):
        refuse("state-malformed", f"step `{sid}` is not a step of this record")
    return step


def migrated(root: Path, reader) -> None:
    """Refuses `state-unmigrated` when a file of a former form stands and the store holds no counter
    yet: a workspace never starts again from an empty book without saying it. The file is never read."""
    former = [name for name in FORMER if (root / ".sys" / "records" / name).is_file()]
    if former and reader.get(COUNTERS, "s") is None:
        refuse("state-unmigrated", f"{former[0]} stands and the store holds no step yet -- the former record "
                                   "is not read: the operator takes it over into the store first")


def pairs(entries) -> list[tuple[str, dict]]:
    return [(one.key, checked(one.key, one.body)) for one in entries]


def active(reader) -> list[tuple[str, dict]]:
    """-> the active steps -- `archived` empty --, reached by the index of `archived`."""
    return pairs(every(reader, STEPS, where={"archived": None}))


class Book:
    """The steps as ONE transaction of the store sees them: what a move reads, and the entries it
    writes -- the step it touches, its labels, the counter -- each by its key, nothing else."""

    def __init__(self, root: Path, session, now: str) -> None:
        self.root, self.session, self.now = root, session, now

    def indexed(self) -> None:
        """Gives the indexed fields their index, once: the first write of a book lays them."""
        for field in INDEXED:
            self.session.index(STEPS, field)

    def get(self, sid: str) -> dict | None:
        found = self.session.get(STEPS, sid)
        return None if found is None else checked(sid, found.body)

    def put(self, sid: str, step: dict) -> None:
        self.session.put(STEPS, sid, step, at=self.now)

    def label(self, name: str) -> dict | None:
        found = self.session.get(LABELS, name)
        return None if found is None else found.body

    def put_label(self, name: str, held: dict) -> None:
        self.session.put(LABELS, name, held, at=self.now)

    def named(self, name: str) -> list[tuple[str, dict]]:
        """-> the steps that wear `name`, by the index of `name`."""
        return pairs(every(self.session, STEPS, where={"name": name}))

    def mint(self) -> str:
        counter = self.session.get(COUNTERS, "s")
        value = (counter.body["value"] if counter else 0) + 1
        self.session.put(COUNTERS, "s", {"value": value}, at=self.now)
        return f"{member_of(self.root)}.s.{value}"


def written(root: Path, change, *args) -> None:
    """One move in one transaction of the store: read, changed, its entries written, then said."""
    print(booked(root, lambda book: change(root, book, *args)))


def booked(root: Path, play):
    """-> what `play(book)` returns, played inside ONE write transaction of the store; a refusal
    inside it undoes every write."""
    kept = store(root)
    migrated(root, kept)
    now = stamp()
    with kept.transaction() as session:
        book = Book(root, session, now)
        book.indexed()
        return play(book)


def stamp() -> str:
    """-> the instant, UTC, to the microsecond -- `PP_NOW` when it is set."""
    said = os.environ.get(CLOCK, "").strip()
    if said:
        try:
            moment = datetime.fromisoformat(said)
        except ValueError:
            refuse("clock-invalid", f"{CLOCK}={said} is no date and time such as 2026-10-25T16:00:00+00:00")
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=timezone.utc)
        return moment.astimezone(timezone.utc).isoformat(timespec="microseconds")
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def member_of(root: Path) -> str:
    """-> the workspace the instance lives in: what an id carries for its uniqueness alone."""
    return root.resolve().parent.name


# --- the checks --------------------------------------------------------------------------

def line_of(root: Path, words: str, what: str, key: str = STEP_BUDGET_KEY, fallback: int = STEP_BUDGET_FALLBACK) -> str:
    """-> the words as one line under its budget."""
    said = " ".join((words or "").split())
    cap = budget(root, key, fallback)
    if len(said) > cap:
        refuse("budget", f"{len(said)} chars -- {what} holds {cap}")
    return said


def valid_name(root: Path, name: str, what: str) -> str:
    cap = budget(root, NAME_MAX_KEY, NAME_MAX_FALLBACK)
    if not NAME.fullmatch(name) or len(name) > cap:
        refuse("name-invalid", f"`{name}` -- {what} is lowercase words joined by hyphens, {cap} chars at most")
    return name


def name_free(book: Book, name: str, but: str | None = None) -> None:
    for sid, step in book.named(name):
        if sid != but and step["status"] in DUE:
            refuse("name-taken", f"`{name}` is {sid}, still to do -- a name is free again once its step is closed")


def short(root: Path, sid: str) -> str:
    """-> `s.<n>` for a step of the instance's member, the whole id otherwise."""
    mine = f"{member_of(root)}.s."
    return "s." + sid[len(mine):] if sid.startswith(mine) else sid


def sid_of(root: Path, said: str) -> str:
    sid = said.lstrip("#")
    if SHORT.fullmatch(sid):
        sid = f"{member_of(root)}.{sid}"
    if not ID.fullmatch(sid):
        refuse("step-invalid", f"`{said}` -- a step is taken by its id, `s.<n>` or `<member>.s.<n>`")
    return sid


def step_of(root: Path, book, said: str) -> tuple[str, dict]:
    """-> (the id, the step) of an id said short or whole; `book` a Book or the store."""
    sid = sid_of(root, said)
    found = book.get(sid) if isinstance(book, Book) else book.get(STEPS, sid)
    if found is None:
        refuse("step-unknown", f"{sid} is no step of this record")
    return sid, found if isinstance(book, Book) else checked(sid, found.body)


def label_of(book: Book, name: str) -> dict:
    held = book.label(name)
    if held is None:
        refuse("label-unknown", f"`{name}` is no label of this record")
    return held


def key_held(reader, key: str) -> None:
    """Refuses `step-taken` when a step of the record holds the key already -- by the index of `key`."""
    page = reader.read(STEPS, last=1, where={"key": key})
    if page.rows:
        refuse("step-taken", f"{key} is {page.rows[0].key} already -- one step per key")


def valid_key(root: Path, key: str) -> str:
    """-> the key, once its grammar, its uniqueness at the record and its family's verifier
    agree -- the verifier's no relayed under the engine's own code. The add judges the uniqueness
    again inside its transaction."""
    if not VECTOR.fullmatch(key):
        refuse("key-invalid", f"`{key}` -- a key is a vector, `<family>:<slug>`")
    key_held(store(root), key)
    try:
        engine().events.verified(root, key)
    except Exception as raised:
        if type(raised).__name__ != "Refusal":
            raise
        refuse(getattr(raised, "code", "key-invalid"), str(raised).split(" — ", 1)[-1])
    return key


def labelled(book: Book, step: dict, sid: str, name: str) -> None:
    if name not in step["labels"]:
        step["labels"].append(name)
        held = book.label(name) or {"note": "", "order": []}
        held["order"].append(sid)
        book.put_label(name, held)


def unlabelled(book: Book, step: dict, sid: str, name: str) -> None:
    if name in step["labels"]:
        step["labels"].remove(name)
        held = book.label(name)
        if held is not None and sid in held["order"]:
            held["order"].remove(sid)
            book.put_label(name, held)


def classed(value: str | None, family: tuple, code: str) -> str | None:
    """-> a priority or a level, once it is one of its family; `code` refuses it otherwise."""
    if value is not None and value not in family:
        refuse(code, f"`{value}` -- one of {', '.join(family)}")
    return value


# --- the moves: each one changes the record it is given and says what it did -------------

def said_as(root: Path, verb: str, step: dict, sid: str) -> str:
    return f"pp-steering: {verb} -- {step['name']} [{short(root, sid)}]"


def commented(root: Path, book: Book, ident: str, text: str) -> str:
    sid, step = step_of(root, book, ident)
    step["comment"] = line_of(root, text, "a comment")
    step["touched"] = stamp()
    book.put(sid, step)
    return said_as(root, "commented", step, sid)


def moved(root: Path, book: Book, ident: str, status: str, reason: str | None = None) -> str:
    """A step changes status: `done` and `open` clear the reason, `wait` and `drop` keep theirs;
    `done` and `drop` date `closed`, `open` and `wait` empty it; a step opened again takes its
    name back, so no other step still to do may wear it."""
    sid, step = step_of(root, book, ident)
    if step["status"] == status:
        refuse("status-invalid", f"{short(root, sid)} is {status} already")
    if status in DUE and step["status"] not in DUE:
        name_free(book, step["name"], but=sid)
    why = ""
    if reason is not None:
        why = line_of(root, reason, "a reason")
        if not why:
            refuse("step-invalid", f"{status} takes its reason")
    now = stamp()
    step["status"], step["reason"], step["touched"] = status, why, now
    step["closed"] = now if status in CLOSED else None
    book.put(sid, step)
    return said_as(root, status, step, sid)


def relabelled(root: Path, book: Book, ident: str, changes: list[str]) -> str:
    sid, step = step_of(root, book, ident)
    for change in changes:
        sign, name = change[:1], change[1:]
        if sign not in "+-" or not sign:
            refuse("step-invalid", f"`{change}` -- a label change is `+<label>` or `-<label>`")
        valid_name(root, name, "a label")
        (labelled if sign == "+" else unlabelled)(book, step, sid, name)
    book.put(sid, step)
    return said_as(root, "labelled", step, sid)


def classified(root: Path, book: Book, ident: str, value: str, family: tuple, code: str) -> str:
    """The priority or the level of a step: the other labels of its family taken off the step, its
    own posed -- the labels of the other families, and the labels themselves, left as they are."""
    classed(value, family, code)
    sid, step = step_of(root, book, ident)
    for other in family:
        if other != value:
            unlabelled(book, step, sid, other)
    labelled(book, step, sid, value)
    book.put(sid, step)
    return said_as(root, "labelled", step, sid)


def noted(root: Path, book: Book, name: str, text: str) -> str:
    held = label_of(book, name)
    held["note"] = line_of(root, text, "a label's note", NOTE_BUDGET_KEY, NOTE_BUDGET_FALLBACK)
    book.put_label(name, held)
    return f"pp-steering: noted -- {name}"


def ordered(root: Path, book: Book, name: str, idents: list[str]) -> str:
    held = label_of(book, name)
    first = []
    for ident in idents:
        sid, _ = step_of(root, book, ident)
        if sid not in held["order"]:
            refuse("step-invalid", f"{short(root, sid)} does not carry the label `{name}`")
        first.append(sid)
    held["order"] = first + [sid for sid in held["order"] if sid not in first]
    book.put_label(name, held)
    return f"pp-steering: ordered -- {name}"


def dissolved(root: Path, book: Book, name: str) -> str:
    """The label leaves the record and each step its order lists -- the steps that carry it."""
    held = label_of(book, name)
    for sid in held["order"]:
        step = book.get(sid)
        if step is not None and name in step["labels"]:
            step["labels"].remove(name)
            book.put(sid, step)
    book.session.remove(LABELS, key=name)
    return f"pp-steering: dissolved -- {name}"


def recalled(root: Path, book: Book, ident: str) -> str:
    """An archived step comes back: `archived` emptied, `recalled` set now -- its age
    restarts. Only those two fields move."""
    sid, step = step_of(root, book, ident)
    if step["archived"] is None:
        refuse("step-active", f"{short(root, sid)} is not archived")
    step["archived"], step["recalled"] = None, stamp()
    book.put(sid, step)
    return said_as(root, "recalled", step, sid)


def add(root: Path, name: str, work: str, labels: list[str], key: str | None, priority: str | None = None,
        level: str | None = None) -> None:
    """A step born: its id minted at the counter and the step, its labels and the counter written in
    ONE transaction; the priority and the level posed as labels after the others."""
    valid_name(root, name, "a step name")
    work = line_of(root, work, "a step's work")
    if not work:
        refuse("step-invalid", "a step is added with its work -- what to do, where and why")
    for label in labels:
        valid_name(root, label, "a label")
    classed(priority, PRIORITIES, "priority-invalid")
    classed(level, LEVELS, "level-invalid")
    migrated(root, store(root))
    held = valid_key(root, key) if key is not None else None

    def born(book: Book) -> tuple[str, dict]:
        name_free(book, name)
        if held is not None:
            key_held(book.session, held)
        now = stamp()
        sid = book.mint()
        step = {"name": name, "at": now, "work": work, "comment": "", "status": "open", "reason": "",
                "labels": [], "key": held, "touched": now, "closed": None, "archived": None, "recalled": None}
        for label in [*labels, *(one for one in (priority, level) if one is not None)]:
            labelled(book, step, sid, label)
        book.put(sid, step)
        return sid, step

    sid, step = booked(root, born)
    print(said_as(root, "added", step, sid))


def move_of(root: Path, book: Book, words: list[str]) -> str:
    """One move of a batch, `<verb> <id> [words]`, played in the batch's transaction."""
    verb, rest = words[0], words[1:]
    if verb not in MOVES or not rest:
        refuse("step-invalid", f"`{' '.join(words)}` -- a move is `<verb> <id> [words]`, the verb one of "
                               f"{', '.join(MOVES)}")
    if verb in ("done", "open", "recall") and len(rest) != 1:
        refuse("step-invalid", f"`{' '.join(words)}` -- {verb} takes the id alone")
    if verb in ("priority", "level") and len(rest) != 2:
        refuse("step-invalid", f"`{' '.join(words)}` -- {verb} takes the id and its value")
    if verb == "comment":
        return commented(root, book, rest[0], " ".join(rest[1:]))
    if verb == "label":
        return relabelled(root, book, rest[0], rest[1:])
    if verb == "recall":
        return recalled(root, book, rest[0])
    if verb == "priority":
        return classified(root, book, rest[0], rest[1], PRIORITIES, "priority-invalid")
    if verb == "level":
        return classified(root, book, rest[0], rest[1], LEVELS, "level-invalid")
    status = {"done": "done", "open": "open", "drop": "dropped", "wait": "waiting"}[verb]
    return moved(root, book, rest[0], status, " ".join(rest[1:]) if verb in ("drop", "wait") else None)


def apply(root: Path, text: str) -> None:
    """A batch of moves, one per line: each judged in order in ONE transaction; the first refusal
    refuses the batch and undoes it, nothing written; else one line per move."""
    def batch(book: Book) -> list[str]:
        said = []
        for number, raw in enumerate(text.splitlines(), 1):
            words = raw.split()
            if not words:
                continue
            try:
                said.append(move_of(root, book, words))
            except SystemExit:
                refuse("apply-refused", f"line {number} `{raw.strip()}` refused -- nothing written")
        return said

    said = booked(root, batch) if text.strip() else []
    print("\n".join(said) if said else "pp-steering: nothing to apply")


# --- the archives ------------------------------------------------------------------------

def since(step: dict) -> str:
    """-> the instant a step's age is read from: its recall when it has one, its last touch
    otherwise."""
    return max(step["recalled"] or "", step["touched"])


def swept(root: Path) -> tuple[list[tuple[str, dict]], datetime]:
    """Archives every active step whose age passes `steering_life_days`, then the least recently
    touched steps still to do past `steering_active_max` -- the active steps read by the index,
    the archived ones written alone. Only `archived` moves. -> (the steps archived, the instant)."""
    life = timedelta(days=budget(root, LIFE_KEY, LIFE_FALLBACK))
    ceiling = budget(root, ACTIVE_MAX_KEY, ACTIVE_MAX_FALLBACK)
    now = stamp()
    moment = datetime.fromisoformat(now)

    def archiving(book: Book) -> list[tuple[str, dict]]:
        found = active(book.session)
        archived = [(sid, step) for sid, step in found if moment - datetime.fromisoformat(since(step)) > life]
        old = {sid for sid, _ in archived}
        due = sorted(((sid, step) for sid, step in found if sid not in old and step["status"] in DUE),
                     key=lambda pair: since(pair[1]), reverse=True)
        archived += due[ceiling:]
        for sid, step in archived:
            step["archived"] = now
            book.put(sid, step)
        return archived

    return booked(root, archiving), moment


def sweep(root: Path) -> None:
    archived, moment = swept(root)
    if not archived:
        print("pp-steering: nothing to archive")
    for sid, step in archived:
        print(f"pp-steering: archived -- {step['name']} [{short(root, sid)}] {ago(since(step), moment)}")


# --- the renderings ----------------------------------------------------------------------

def lasting(seconds: float) -> str:
    """-> a duration in the coarsest unit that still says it."""
    seconds = max(0, int(seconds))
    minutes, hours, days = seconds // 60, seconds // 3600, seconds // 86400
    if minutes < 1:
        return "now"
    if hours < 1:
        return f"{minutes} min"
    if days < 1:
        return f"{hours}h {minutes % 60} min" if minutes % 60 else f"{hours}h"
    if days < 7:
        return f"{days} day" + ("s" if days > 1 else "")
    if days < 30:
        weeks = days // 7
        return f"{weeks} week" + ("s" if weeks > 1 else "")
    if days < 365:
        months = days // 30
        return f"~{months} month" + ("s" if months > 1 else "")
    return f"~{days / 365:.1f} years"


def ago(iso: str, now: datetime) -> str:
    """-> the time elapsed since a stamp."""
    try:
        then = datetime.fromisoformat(iso)
    except (TypeError, ValueError):
        return str(iso)
    return lasting((now - then).total_seconds())


def as_data(sid: str, step: dict) -> dict:
    return {"id": sid, **step}


def age_of(step: dict, now: datetime) -> float:
    return (now - datetime.fromisoformat(since(step))).total_seconds()


def chosen(found: list, label_name: str | None, everything: bool,
           statuses: tuple = ()) -> list[tuple[str, dict]]:
    """-> of the active steps read, those still to do, all with `everything`, or of the `statuses`
    named; the most recently touched first, of one label when it is named. (The archived page keeps
    the order of its walk, the newest born first: it is not chosen here.)"""
    kept = statuses or (STATUSES if everything else DUE)
    found = [(sid, step) for sid, step in found
             if step["status"] in kept and (label_name is None or label_name in step["labels"])]
    return sorted(found, key=lambda pair: since(pair[1]), reverse=True)


def archives(root: Path, keep=lambda sid, step: True, plain: bool = False) -> tuple[list[tuple[str, dict]], int, int, bool]:
    """-> (a page of the archived steps the `keep` judges -- every filter of the reading --, the newest
    born first, at most the store's bound; the steps of that selection in all; the bound; whether the
    page is cut). The store is walked from its newest entry, page by page. A `plain` reading -- no filter
    at all -- stops at the bound and counts its total by the indexes (every step less the active ones);
    a filtered one walks on to the oldest entry to count its selection (its cost is s.1925)."""
    kept = store(root)
    bound = kept.limit()
    found, total, cursor = [], 0, None
    while True:
        page = kept.read(STEPS, **({} if cursor is None else {"before": cursor}))
        for sid, step in reversed(pairs(page.rows)):
            if step["archived"] is not None and keep(sid, step):
                total += 1
                if len(found) < bound:
                    found.append((sid, step))
        if page.next is None or (plain and len(found) == bound):
            break
        cursor = page.next["before"]
    if plain:
        total = kept.count(STEPS) - kept.count(STEPS, where={"archived": None})
    return found, total, bound, total > len(found)


def read_steps(root: Path, everything: bool, archived: bool, label_name=None, statuses: tuple = (),
               keep=None) -> tuple[list, dict | None]:
    """-> (the steps a reading chooses, None -- or, for the archived scope, its page: `{total, bound,
    foot}`, the foot the line that says a page cut by the bound, None when nothing is cut). The archived
    page holds the steps every filter keeps -- `keep`, when given, judging the others than status and
    label --, the newest born first, the order its walk takes."""
    if not archived:
        return chosen(active(store(root)), label_name, everything, statuses), None
    wanted = statuses or STATUSES
    plain = not statuses and label_name is None and keep is None
    page, total, bound, cut = archives(root, lambda sid, step: step["status"] in wanted
                                       and (label_name is None or label_name in step["labels"])
                                       and (keep is None or keep(sid, step)), plain)
    foot = f"pp-steering: {len(page)} archived steps shown of {total} -- the bound {bound}" if cut else None
    return page, {"total": total, "bound": bound, "foot": foot}


def paged(rows: list, page: dict | None) -> str:
    """-> the --json of a reading: its rows alone, or for the archived scope `{rows, total, bound}`."""
    if page is None:
        return json.dumps(rows, ensure_ascii=False)
    return json.dumps({"rows": rows, "total": page["total"], "bound": page["bound"]}, ensure_ascii=False)


def line(root: Path, sid: str, step: dict, now: datetime) -> str:
    """-> one step on one line: its name and short id, its status when not open with its
    reason, its labels, its key, its age, then its work."""
    parts = [f"{step['name']} [{short(root, sid)}]"]
    if step["status"] != "open":
        parts.append(step["status"] + (f" ({step['reason']})" if step["reason"] else ""))
    parts += [f"#{name}" for name in step["labels"]]
    if step["key"]:
        parts.append(step["key"])
    parts.append(ago(since(step), now))
    return " · ".join(parts) + f" — {step['work']}"


def instant(said: str) -> datetime:
    """-> a date or a date and time as an instant, UTC when it says no zone."""
    try:
        moment = datetime.fromisoformat(said)
    except ValueError:
        refuse("step-invalid", f"`{said}` -- a date is written like 2026-10-25 or 2026-10-25T16:00:00+00:00")
    return moment if moment.tzinfo else moment.replace(tzinfo=timezone.utc)


def days_of(said: str) -> int:
    found = DAYS.fullmatch(said)
    if not found:
        refuse("step-invalid", f"`{said}` -- an age is whole days, `<n>d`")
    return int(found.group(1))


def filtered(found: list, now: datetime, older: str | None, newer: str | None, after: str | None,
             before: str | None, families: tuple = ()) -> list:
    """-> the steps whose age and birth hold the bounds given, and whose key is of one of the
    families named when any is: the key's family alone is read, never the step's words."""
    if families:
        found = [pair for pair in found if pair[1]["key"] and pair[1]["key"].split(":", 1)[0] in families]
    if older is not None:
        floor = days_of(older) * 86400
        found = [pair for pair in found if age_of(pair[1], now) > floor]
    if newer is not None:
        ceiling = days_of(newer) * 86400
        found = [pair for pair in found if age_of(pair[1], now) <= ceiling]
    if after is not None:
        start = instant(after)
        found = [pair for pair in found if datetime.fromisoformat(pair[1]["at"]) >= start]
    if before is not None:
        end = instant(before)
        found = [pair for pair in found if datetime.fromisoformat(pair[1]["at"]) < end]
    return found


def slices(root: Path) -> list[tuple[str, float, float]]:
    """-> the slices of age, `(name, from, to)` in days; the last ones read `steering_life_days`."""
    bounds = sorted({1, 3, 7, budget(root, LIFE_KEY, LIFE_FALLBACK)})
    named = [("<1d", 0, bounds[0])]
    named += [(f"{low}-{high}d", low, high) for low, high in zip(bounds, bounds[1:])]
    return named + [(f">{bounds[-1]}d", bounds[-1], math.inf)]


def grouped(root: Path, found: list, by: str, now: datetime) -> list[tuple[str | None, list]]:
    """-> the steps in groups of one field: each label (a step under each of its labels, the
    unlabelled last), each status, each slice of age -- the empty groups left out."""
    if by == "label":
        names = sorted({name for _, step in found for name in step["labels"]})
        groups = [(name, [pair for pair in found if name in pair[1]["labels"]]) for name in names]
        groups.append((None, [pair for pair in found if not pair[1]["labels"]]))
    elif by == "status":
        groups = [(status, [pair for pair in found if pair[1]["status"] == status]) for status in STATUSES]
    else:
        groups = [(name, [pair for pair in found if low * 86400 <= age_of(pair[1], now) < high * 86400])
                  for name, low, high in slices(root)]
    return [(name, pairs) for name, pairs in groups if pairs]


def listing(root: Path, label_name: str | None, everything: bool, archived: bool, as_json: bool,
            statuses: tuple = (), older=None, newer=None, after=None, before=None, by=None,
            foot: list | None = None, families: tuple = ()) -> str:
    now = datetime.fromisoformat(stamp())
    judged = families or any(one is not None for one in (older, newer, after, before))
    keep = (lambda sid, step: bool(filtered([(sid, step)], now, older, newer, after, before, families))) if judged else None
    read, page = read_steps(root, everything, archived, label_name, statuses, keep)
    found = read if archived else filtered(read, now, older, newer, after, before, families)
    if by is not None:
        groups = grouped(root, found, by, now)
        if as_json:
            return paged([{"group": name, "count": len(pairs), "steps": [as_data(sid, step) for sid, step in pairs]}
                          for name, pairs in groups], page)
        rows = []
        for name, pairs in groups:
            rows.append(f"▸ {name if name is not None else '(no label)'} ({len(pairs)})")
            rows += [line(root, sid, step, now) for sid, step in pairs]
    else:
        if as_json:
            return paged([as_data(sid, step) for sid, step in found], page)
        rows = [line(root, sid, step, now) for sid, step in found]
    if foot:
        rows.append(f"archived now: {len(foot)} -- " + ", ".join(f"{step['name']} [{short(root, sid)}]"
                                                              for sid, step in foot))
    if page and page["foot"]:
        rows.append(page["foot"])
    return "\n".join(rows) if rows else "pp-steering: no step"


def showing(root: Path, ident: str, as_json: bool) -> str:
    sid, step = step_of(root, store(root), ident)
    if as_json:
        return json.dumps(as_data(sid, step), ensure_ascii=False)
    now = datetime.fromisoformat(stamp())
    rows = [line(root, sid, step, now)]
    if step["comment"]:
        rows.append(f"  comment: {step['comment']}")
    rows.append(f"  born {step['at']} · touched {step['touched']}"
                + (f" · closed {step['closed']}" if step["closed"] else "")
                + (f" · archived {step['archived']}" if step["archived"] else ""))
    return "\n".join(rows)


def reviewing(root: Path, as_json: bool) -> str:
    """-> the active steps still to do, the least recently touched first -- what the agent
    judges: done elsewhere, still relevant, or to drop. A line says whether the step has a
    comment."""
    found = list(reversed(chosen(active(store(root)), None, False)))
    if as_json:
        return json.dumps([as_data(sid, step) for sid, step in found], ensure_ascii=False)
    if not found:
        return "pp-steering: no step"
    now = datetime.fromisoformat(stamp())
    return "\n".join(line(root, sid, step, now) + ("" if step["comment"] else " · no comment") for sid, step in found)


def spread(values: list[float]) -> dict:
    """-> `{count, median, p90, max}` in whole seconds, by the nearest rank; None without values."""
    ranked = sorted(values)
    if not ranked:
        return {"count": 0, "median": None, "p90": None, "max": None}
    rank = lambda share: int(ranked[max(0, math.ceil(share * len(ranked)) - 1)])
    return {"count": len(ranked), "median": rank(0.5), "p90": rank(0.9), "max": int(ranked[-1])}


def board_of(root: Path, now: datetime) -> tuple[dict, dict]:
    """-> (the board, the steps it names), read from the fields: the counts by status -- the active
    steps read by the index of `archived`, the archived ones counted by the index of `status` --;
    the last 7 days, from the steps the store saw written since; the durations to closure of every
    step closed, archived included, read in bounded pages by the index of `status`, and the ages of
    those still to do; the least touched, the labels and their
    freshest steps, the unlabelled."""
    kept = store(root)
    current = active(kept)
    week = now - timedelta(days=7)
    lately = pairs(every(kept, STEPS, since=week.isoformat()))     # every stamp of the week is a write of it
    within = lambda stamp_: stamp_ is not None and datetime.fromisoformat(stamp_) >= week
    due = sorted(((sid, step) for sid, step in current if step["status"] in DUE),
                 key=lambda pair: since(pair[1]), reverse=True)
    per = budget(root, PER_LABEL_KEY, PER_LABEL_FALLBACK)

    def share(pairs_: list) -> dict:
        return {"open": sum(1 for _, step in pairs_ if step["status"] == "open"),
                "waiting": sum(1 for _, step in pairs_ if step["status"] == "waiting"),
                "recent": [sid for sid, _ in pairs_[:per]]}

    names = {name for _, step in due for name in step["labels"]}
    held = sorted((entry for entry in (kept.get(LABELS, name) for name in names) if entry is not None),
                  key=lambda entry: entry.seq)                     # the labels in their order of birth
    labels = []
    for entry in held:
        mine = [pair for pair in due if entry.key in pair[1]["labels"]]
        labels.append({"name": entry.key, "note": entry.body.get("note", ""), **share(mine),
                       "touched": since(mine[0][1])})
    labels.sort(key=lambda one: one["touched"], reverse=True)
    labels = [{key: one[key] for key in ("name", "note", "open", "waiting", "touched", "recent")} for one in labels]
    counts = {}
    for status in STATUSES:
        here = sum(1 for _, step in current if step["status"] == status)
        counts[status] = {"active": here, "archived": kept.count(STEPS, where={"status": status}) - here}
    return {
        "counts": counts,
        "week": {"born": sum(1 for _, step in lately if within(step["at"])),
                 "done": sum(1 for _, step in lately if step["status"] == "done" and within(step["closed"])),
                 "dropped": sum(1 for _, step in lately if step["status"] == "dropped" and within(step["closed"])),
                 "archived": sum(1 for _, step in lately if within(step["archived"])),
                 "recalled": sum(1 for _, step in lately if within(step["recalled"]))},
        "resolution": spread([(datetime.fromisoformat(step["closed"]) - datetime.fromisoformat(step["at"])).total_seconds()
                              for status in CLOSED for _, step in pairs(every(kept, STEPS, where={"status": status}))
                              if step["closed"]]),
        "age": spread([age_of(step, now) for _, step in due]),
        "least_touched": [sid for sid, _ in reversed(due)][:5],
        "labels": labels,
        "unlabelled": share([pair for pair in due if not pair[1]["labels"]]),
    }, dict(current)


def boarding(root: Path, as_json: bool) -> str:
    now = datetime.fromisoformat(stamp())
    seen, steps = board_of(root, now)
    if as_json:
        return json.dumps(seen, ensure_ascii=False)
    named = lambda sid: f"{steps[sid]['name']} [{short(root, sid)}]"
    span = lambda one: ("--" if not one["count"] else
                        f"median {lasting(one['median'])} · p90 {lasting(one['p90'])} · max {lasting(one['max'])}"
                        f" ({one['count']})")
    counts = " · ".join(f"{status} {one['active']}" + (f" (+{one['archived']} archived)" if one["archived"] else "")
                        for status, one in seen["counts"].items())
    week = seen["week"]
    rows = [f"steps: {counts}",
            f"last 7 days: {week['born']} born · {week['done']} done · {week['dropped']} dropped · "
            f"{week['archived']} archived · {week['recalled']} recalled",
            f"to closure: {span(seen['resolution'])}",
            f"age of the steps to do: {span(seen['age'])}",
            "least touched: " + (", ".join(named(sid) for sid in seen["least_touched"]) or "--")]
    for one in seen["labels"]:
        rows.append(f"#{one['name']} · {one['open']} open · {one['waiting']} waiting · "
                    f"{ago(one['touched'], now)}" + (f" — {one['note']}" if one["note"] else ""))
        rows += [f"  {named(sid)}" for sid in one["recent"]]
    loose = seen["unlabelled"]
    if loose["open"] or loose["waiting"]:
        rows.append(f"(no label) · {loose['open']} open · {loose['waiting']} waiting")
        rows += [f"  {named(sid)}" for sid in loose["recent"]]
    return "\n".join(rows)


def labelling(root: Path, everything: bool, archived: bool, as_json: bool) -> str:
    """-> one entry per label: its note, its counts by status among the steps of the scope,
    the least and the most recently touched of them; the archived scope reads one page of them."""
    found, page = read_steps(root, everything, archived)
    entries = []
    for entry in every(store(root), LABELS):
        name, held = entry.key, entry.body
        mine = [step for _, step in found if name in step["labels"]]
        touched = sorted(since(step) for step in mine)
        entries.append({"name": name, "note": held.get("note", ""),
                        **{status: sum(1 for step in mine if step["status"] == status) for status in STATUSES},
                        "oldest": touched[0] if touched else None, "latest": touched[-1] if touched else None})
    entries.sort(key=lambda one: one["latest"] or "", reverse=True)
    if as_json:
        return paged(entries, page)
    if not entries:
        return "pp-steering: no label"
    now = datetime.fromisoformat(stamp())
    return "\n".join([f"#{one['name']} · " + " · ".join(f"{one[status]} {status}" for status in STATUSES if one[status])
                     + (f" · {ago(one['latest'], now)}" if one["latest"] else "")
                     + (f" — {one['note']}" if one["note"] else "") for one in entries] + ([page["foot"]] if page and page["foot"] else []))


# --- the console -------------------------------------------------------------------------

def flagged(rest: list[str], flag: str) -> tuple[list[str], list[str]]:
    """-> (rest without every `flag value`, the values in order)."""
    kept, values = [], []
    words = iter(rest)
    for word in words:
        if word == flag:
            value = next(words, None)
            if value is None:
                refuse("step-invalid", f"{flag} takes a value")
            values.append(value)
        else:
            kept.append(word)
    return kept, values


def switched(rest: list[str], flag: str) -> tuple[list[str], bool]:
    return [word for word in rest if word != flag], flag in rest


def one_of(values: list[str], flag: str) -> str | None:
    if len(values) > 1:
        refuse("step-invalid", f"{flag} is given once")
    return values[0] if values else None


LIST_USAGE = ("list [--label <l>] [--status <s>]... [--key <family>]... [--older <n>d] [--newer <n>d] [--since <date>] "
              "[--before <date>] [--all | --archived] [--by label|age|status] [--sweep] [--json]")


def listed(root: Path, rest: list[str]) -> str:
    rest, labels = flagged(rest, "--label")
    rest, statuses = flagged(rest, "--status")
    rest, families = flagged(rest, "--key")
    rest, older = flagged(rest, "--older")
    rest, newer = flagged(rest, "--newer")
    rest, after = flagged(rest, "--since")
    rest, before = flagged(rest, "--before")
    rest, by = flagged(rest, "--by")
    rest, everything = switched(rest, "--all")
    rest, archived = switched(rest, "--archived")
    rest, sweeping = switched(rest, "--sweep")
    rest, as_json = switched(rest, "--json")
    by_ = one_of(by, "--by")
    if (rest or (everything and archived) or any(one not in STATUSES for one in statuses)
            or not all(FAMILY.match(one) for one in families) or by_ not in (None, "label", "age", "status")):
        refuse("step-invalid", LIST_USAGE)
    foot = swept(root)[0] if sweeping else None
    return listing(root, one_of(labels, "--label"), everything, archived, as_json, tuple(statuses),
                   one_of(older, "--older"), one_of(newer, "--newer"), one_of(after, "--since"),
                   one_of(before, "--before"), by_, foot, tuple(families))


def main(argv: list[str]) -> int:
    verbs = ("add", "comment", "done", "drop", "wait", "open", "label", "note", "order", "dissolve", "list", "show",
             "sweep", "recall", "review", "board", "labels", "apply", "view", "priority", "level")
    if not argv or argv[0] not in verbs:
        sys.stderr.write(__doc__)
        return 2
    verb, rest = argv[0], argv[1:]
    if verb == "view":
        if not rest or rest[0] not in READS or (rest[0] == "list" and "--sweep" in rest):
            refuse("view-read-only", f"`{' '.join(rest)}` -- the console reads the steps: "
                                     f"{', '.join(READS)} (list without --sweep); a move is played in a run")
        return main(rest)
    root = home()
    migrated(root, store(root))
    if verb == "add":
        rest, labels = flagged(rest, "--label")
        rest, keys = flagged(rest, "--key")
        rest, priorities = flagged(rest, "--priority")
        rest, levels = flagged(rest, "--level")
        if len(rest) < 1 or len(keys) > 1 or len(priorities) > 1 or len(levels) > 1:
            refuse("step-invalid", "add <name> <work ...> [--label <l>]... [--key <family:slug>] "
                                   "[--priority p1|p2|p3] [--level critical|high|medium|low]")
        add(root, rest[0], " ".join(rest[1:]), labels, keys[0] if keys else None, one_of(priorities, "--priority"),
            one_of(levels, "--level"))
    elif verb == "comment" and rest:
        written(root, commented, rest[0], " ".join(rest[1:]))
    elif verb in ("done", "open") and len(rest) == 1:
        written(root, moved, rest[0], verb)
    elif verb in ("drop", "wait") and rest:
        written(root, moved, rest[0], "dropped" if verb == "drop" else "waiting", " ".join(rest[1:]))
    elif verb == "label" and len(rest) >= 2:
        written(root, relabelled, rest[0], rest[1:])
    elif verb == "note" and rest:
        written(root, noted, rest[0], " ".join(rest[1:]))
    elif verb == "order" and len(rest) >= 2:
        written(root, ordered, rest[0], rest[1:])
    elif verb == "dissolve" and len(rest) == 1:
        written(root, dissolved, rest[0])
    elif verb == "list":
        print(listed(root, rest))
    elif verb == "sweep" and not rest:
        sweep(root)
    elif verb == "recall" and len(rest) == 1:
        written(root, recalled, rest[0])
    elif verb == "priority" and len(rest) == 2:
        written(root, classified, rest[0], rest[1], PRIORITIES, "priority-invalid")
    elif verb == "level" and len(rest) == 2:
        written(root, classified, rest[0], rest[1], LEVELS, "level-invalid")
    elif verb == "review" and rest in ([], ["--json"]):
        print(reviewing(root, bool(rest)))
    elif verb == "show":
        rest, as_json = switched(rest, "--json")
        if len(rest) != 1:
            refuse("step-invalid", "show <id> [--json]")
        print(showing(root, rest[0], as_json))
    elif verb == "board" and rest in ([], ["--json"]):
        print(boarding(root, bool(rest)))
    elif verb == "labels":
        rest, everything = switched(rest, "--all")
        rest, archived = switched(rest, "--archived")
        rest, as_json = switched(rest, "--json")
        if rest or (everything and archived):
            refuse("step-invalid", "labels [--all | --archived] [--json]")
        print(labelling(root, everything, archived, as_json))
    elif verb == "apply" and rest == ["-"]:
        apply(root, engine().reading.piped())
    else:
        refuse("step-invalid", f"`{' '.join(argv)}` -- the call does not fit `{verb}` (the usage: the script alone)")
    return 0


def caught(argv: list[str]) -> int:
    """-> `main`'s code; a refusal of the store (busy, corrupt) said by its own name, exit 2."""
    try:
        return main(argv)
    except Exception as raised:            # the engine refuses by its own name
        if type(raised).__name__ != "Refusal":
            raise
        refuse(getattr(raised, "code", "store-failed"), str(raised).split(" — ", 1)[-1])


if __name__ == "__main__":
    raise SystemExit(caught(sys.argv[1:]))
