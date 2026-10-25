#!/usr/bin/env python3
"""DETERMINISTIC keeper of the STEPS -- the work owed in this workspace.

ONE record, `steps.json`:

  steps     `{<id>: {name, at, work, comment, status, reason, labels, key, touched, archived,
            recalled}}` -- a step is one unit of work owed. Its NAME (lowercase words joined by hyphens) and its WORK
            (the work, written to be understood alone) are fixed when it is added: no verb
            writes them again. Its COMMENT says what happened to it since, rewritten freely.
            Its status is `open`, `waiting` (its reason kept), `done` or `dropped` (its reason
            kept). `at` is its birth; `touched` moves with its comment and its status; a step's AGE runs from
            its recall when it has one, from `touched` otherwise. A KEY,
            when the work has an address elsewhere, is a vector verified through the engine and
            unique at the record. `archived` is empty while the step is active.
  labels    `{<name>: {note, order}}` -- a label groups steps: `order` lists its steps' ids in
            the order wanted, `note` says why. A step carries zero, one or several labels;
            dissolving a label leaves its steps as they are.
  counters  `{s}` -- the step counter, never rewound.

The ID (`<member>.s.<n>`) is what every verb takes; the NAME is what a step is called by
when the principal reads it -- every rendering shows both. A name is unique among the steps
still to do (`open`, `waiting`): a closed step frees its name.

  pp-steering.py add <name> <work ...> [--label <l>]... [--key <family:slug>]
  pp-steering.py comment <id> <text ...>          -> the comment rewritten (empty: none)
  pp-steering.py done <id>
  pp-steering.py drop <id> <reason ...>
  pp-steering.py wait <id> <reason ...>
  pp-steering.py open <id>                        -> back to work, the reason cleared
  pp-steering.py label <id> +<label>|-<label> ... -> labels added or taken off
  pp-steering.py note <label> <text ...>          -> the label's note
  pp-steering.py order <label> <id> ...           -> those steps first, in that order
  pp-steering.py dissolve <label>                 -> the label leaves the record and its steps
  pp-steering.py list [--label <l>] [--all | --archived] [--json]
                                               -> the active steps still to do, the most
                                                  recently touched first; `--all` adds the
                                                  closed ones; `--archived` shows the
                                                  archived ones
  pp-steering.py show <id> [--json]               -> one step, whole
  pp-steering.py sweep                            -> archives the steps untouched for
                                                  `steering_life_days`, then the least
                                                  recently touched steps still to do past
                                                  `steering_active_max`; says each one
  pp-steering.py recall <id>                      -> an archived step back, its age restarted
  pp-steering.py review [--json]                  -> the active steps still to do, the least
                                                  recently touched first

Refusals -- exit 2, nothing written: step-invalid, step-unknown, status-invalid, name-invalid,
name-taken, budget, key-invalid, step-taken, label-unknown, step-active, state-malformed,
state-unmigrated
(a `threads.json` of the thread model stands without `steps.json`: it is never read); a key
the family's verifier refuses is relayed under the engine's own code. Writes go through the
engine's one write regime: lock, read inside it, atomic replace. The clock reads `PP_NOW`
(a date and time such as 2026-10-25T16:00:00+00:00) when it is set. No network, ever.

The conductor plays this skill: an agent reaches it as `./pp <key> -s pp-steering ...`.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

STATE_NAME = "steps.json"
LEGACY_NAME = "threads.json"     # the record of the thread model: refused, never read
STEP_BUDGET_KEY, STEP_BUDGET_FALLBACK = "steering_step_budget", 100    # a work, a comment, a reason
NAME_MAX_KEY, NAME_MAX_FALLBACK = "steering_name_max", 60
NOTE_BUDGET_KEY, NOTE_BUDGET_FALLBACK = "steering_note_budget", 80     # a label's note
LIFE_KEY, LIFE_FALLBACK = "steering_life_days", 15            # the days a step stays active untouched
ACTIVE_MAX_KEY, ACTIVE_MAX_FALLBACK = "steering_active_max", 60   # the active steps still to do, at most
CLOCK = "PP_NOW"                 # an ISO instant the clock reads instead of the system's
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")   # kebab-case, the slugs' own grammar
VECTOR = re.compile(r"^[a-z][a-z0-9_-]*:\S+$")   # a key: `<family>:<slug>`, the bus's own grammar
ID = re.compile(r"^\S+\.s\.[0-9]+$")             # a step id's SHAPE -- read for its shape alone
STATUSES = ("open", "waiting", "done", "dropped")
DUE = ("open", "waiting")        # the steps still to do: their names are unique
FIELDS = ("name", "at", "work", "comment", "status", "reason", "labels", "key", "touched", "archived", "recalled")


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

def state_path(root: Path) -> Path:
    return root / ".sys" / "records" / STATE_NAME


def empty() -> dict:
    return {"counters": {"s": 0}, "steps": {}, "labels": {}}


def load(root: Path) -> dict:
    """-> the record, `{counters, steps, labels}` -- empty when there is none. One shape is
    read: anything else refuses `state-malformed`; a record of the thread model standing
    alone refuses `state-unmigrated`, so a workspace never starts again from an empty book
    without saying it."""
    path = state_path(root)
    if not path.is_file():
        if (path.parent / LEGACY_NAME).is_file():
            refuse("state-unmigrated", f"{LEGACY_NAME} stands without {STATE_NAME} -- the thread model is not "
                                       "read: the operator ports the record first")
        return empty()
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        refuse("state-malformed", f"{path} does not parse")
    if (not isinstance(record, dict) or set(record) != {"counters", "steps", "labels"}
            or not isinstance(record["counters"], dict) or set(record["counters"]) != {"s"}
            or not isinstance(record["counters"]["s"], int)
            or not isinstance(record["steps"], dict) or not isinstance(record["labels"], dict)):
        refuse("state-malformed", f"{path} is not the steps with their counter")
    for sid, step in record["steps"].items():
        if (not ID.fullmatch(sid) or not isinstance(step, dict) or set(step) != set(FIELDS)
                or step["status"] not in STATUSES or not step["name"] or not step["work"]
                or not isinstance(step["labels"], list)):
            refuse("state-malformed", f"step `{sid}` is not a step of this record")
    for name, label in record["labels"].items():
        if not isinstance(label, dict) or not isinstance(label.get("order"), list) \
                or any(sid not in record["steps"] for sid in label["order"]):
            refuse("state-malformed", f"label `{name}` lists a step the record does not hold")
    return record


def save(root: Path, record: dict) -> None:
    """Writes the whole record atomically -- the engine's one write regime."""
    engine().record.replace(state_path(root), json.dumps(record, ensure_ascii=False, indent=1) + "\n")


def guarded(root: Path):
    """The record's critical section: every load-change-save plays inside it."""
    return engine().record.held(state_path(root))


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


def mint(root: Path, record: dict) -> str:
    record["counters"]["s"] += 1
    return f"{member_of(root)}.s.{record['counters']['s']}"


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


def name_free(record: dict, name: str, but: str | None = None) -> None:
    for sid, step in record["steps"].items():
        if sid != but and step["name"] == name and step["status"] in DUE:
            refuse("name-taken", f"`{name}` is {sid}, still to do -- a name is free again once its step is closed")


def step_of(record: dict, said: str) -> tuple[str, dict]:
    sid = said.lstrip("#")
    if not ID.fullmatch(sid):
        refuse("step-invalid", f"`{said}` -- a step is taken by its id, `<member>.s.<n>`")
    if sid not in record["steps"]:
        refuse("step-unknown", f"{sid} is no step of this record")
    return sid, record["steps"][sid]


def label_of(record: dict, name: str) -> dict:
    if name not in record["labels"]:
        refuse("label-unknown", f"`{name}` is no label of this record")
    return record["labels"][name]


def valid_key(root: Path, record: dict, key: str) -> str:
    """-> the key, once its grammar, its uniqueness at the record and its family's verifier
    agree -- the verifier's no relayed under the engine's own code."""
    if not VECTOR.fullmatch(key):
        refuse("key-invalid", f"`{key}` -- a key is a vector, `<family>:<slug>`")
    for sid, step in record["steps"].items():
        if step["key"] == key:
            refuse("step-taken", f"{key} is {sid} already -- one step per key")
    try:
        engine().events.verified(root, key)
    except Exception as raised:
        if type(raised).__name__ != "Refusal":
            raise
        refuse(getattr(raised, "code", "key-invalid"), str(raised).split(" — ", 1)[-1])
    return key


def labelled(record: dict, step: dict, sid: str, name: str) -> None:
    if name not in step["labels"]:
        step["labels"].append(name)
        record["labels"].setdefault(name, {"note": "", "order": []})["order"].append(sid)


def unlabelled(record: dict, step: dict, sid: str, name: str) -> None:
    if name in step["labels"]:
        step["labels"].remove(name)
        record["labels"][name]["order"].remove(sid)


# --- the verbs ---------------------------------------------------------------------------

def said_as(verb: str, step: dict, sid: str) -> None:
    print(f"pp-steering: {verb} -- {step['name']} [{sid}]")


def add(root: Path, name: str, work: str, labels: list[str], key: str | None) -> None:
    with guarded(root):
        record = load(root)
        valid_name(root, name, "a step name")
        name_free(record, name)
        work = line_of(root, work, "a step's work")
        if not work:
            refuse("step-invalid", "a step is added with its work -- what to do, where and why")
        for label in labels:
            valid_name(root, label, "a label")
        held = valid_key(root, record, key) if key is not None else None
        now = stamp()
        sid = mint(root, record)
        step = {"name": name, "at": now, "work": work, "comment": "", "status": "open", "reason": "",
                "labels": [], "key": held, "touched": now, "archived": None, "recalled": None}
        record["steps"][sid] = step
        for label in labels:
            labelled(record, step, sid, label)
        save(root, record)
    said_as("added", step, sid)


def comment(root: Path, ident: str, text: str) -> None:
    with guarded(root):
        record = load(root)
        sid, step = step_of(record, ident)
        step["comment"] = line_of(root, text, "a comment")
        step["touched"] = stamp()
        save(root, record)
    said_as("commented", step, sid)


def moved(root: Path, ident: str, status: str, reason: str | None = None) -> None:
    """A step changes status: `done` and `open` clear the reason, `wait` and `drop` keep theirs;
    a step opened again takes its name back, so no other step still to do may wear it."""
    with guarded(root):
        record = load(root)
        sid, step = step_of(record, ident)
        if step["status"] == status:
            refuse("status-invalid", f"{sid} is {status} already")
        if status in DUE and step["status"] not in DUE:
            name_free(record, step["name"], but=sid)
        why = ""
        if reason is not None:
            why = line_of(root, reason, "a reason")
            if not why:
                refuse("step-invalid", f"{status} takes its reason")
        step["status"], step["reason"], step["touched"] = status, why, stamp()
        save(root, record)
    said_as(status, step, sid)


def label(root: Path, ident: str, changes: list[str]) -> None:
    with guarded(root):
        record = load(root)
        sid, step = step_of(record, ident)
        for change in changes:
            sign, name = change[:1], change[1:]
            if sign not in "+-" or not sign:
                refuse("step-invalid", f"`{change}` -- a label change is `+<label>` or `-<label>`")
            valid_name(root, name, "a label")
            (labelled if sign == "+" else unlabelled)(record, step, sid, name)
        save(root, record)
    said_as("labelled", step, sid)


def note(root: Path, name: str, text: str) -> None:
    with guarded(root):
        record = load(root)
        label_of(record, name)["note"] = line_of(root, text, "a label's note", NOTE_BUDGET_KEY, NOTE_BUDGET_FALLBACK)
        save(root, record)
    print(f"pp-steering: noted -- {name}")


def order(root: Path, name: str, idents: list[str]) -> None:
    with guarded(root):
        record = load(root)
        held = label_of(record, name)
        first = []
        for ident in idents:
            sid, _ = step_of(record, ident)
            if sid not in held["order"]:
                refuse("step-invalid", f"{sid} does not carry the label `{name}`")
            first.append(sid)
        held["order"] = first + [sid for sid in held["order"] if sid not in first]
        save(root, record)
    print(f"pp-steering: ordered -- {name}")


def dissolve(root: Path, name: str) -> None:
    with guarded(root):
        record = load(root)
        label_of(record, name)
        for step in record["steps"].values():
            if name in step["labels"]:
                step["labels"].remove(name)
        del record["labels"][name]
        save(root, record)
    print(f"pp-steering: dissolved -- {name}")


# --- the archives ------------------------------------------------------------------------

def since(step: dict) -> str:
    """-> the instant a step's age is read from: its recall when it has one, its last touch
    otherwise."""
    return max(step["recalled"] or "", step["touched"])


def sweep(root: Path) -> None:
    """Archives every step not archived yet whose age passes `steering_life_days`, then the
    least recently touched steps still to do past `steering_active_max`; says each one.
    Only `archived` moves."""
    with guarded(root):
        record = load(root)
        now = stamp()
        moment = datetime.fromisoformat(now)
        life = timedelta(days=budget(root, LIFE_KEY, LIFE_FALLBACK))
        ceiling = budget(root, ACTIVE_MAX_KEY, ACTIVE_MAX_FALLBACK)
        archived = [(sid, step) for sid, step in record["steps"].items()
                    if step["archived"] is None and moment - datetime.fromisoformat(since(step)) > life]
        for _, step in archived:
            step["archived"] = now
        due = sorted(((sid, step) for sid, step in record["steps"].items()
                      if step["archived"] is None and step["status"] in DUE),
                     key=lambda pair: since(pair[1]), reverse=True)
        for _, step in due[ceiling:]:
            step["archived"] = now
        archived += due[ceiling:]
        if archived:
            save(root, record)
    if not archived:
        print("pp-steering: nothing to archive")
    for sid, step in archived:
        print(f"pp-steering: archived -- {step['name']} [{sid}] {ago(since(step), moment)}")


def recall(root: Path, ident: str) -> None:
    """An archived step comes back: `archived` emptied, `recalled` set now -- its age
    restarts. Only those two fields move."""
    with guarded(root):
        record = load(root)
        sid, step = step_of(record, ident)
        if step["archived"] is None:
            refuse("step-active", f"{sid} is not archived")
        step["archived"], step["recalled"] = None, stamp()
        save(root, record)
    said_as("recalled", step, sid)


# --- the renderings ----------------------------------------------------------------------

def ago(iso: str, now: datetime) -> str:
    """-> the time elapsed since a stamp, in the coarsest unit that still says it."""
    try:
        then = datetime.fromisoformat(iso)
    except (TypeError, ValueError):
        return str(iso)
    seconds = max(0, int((now - then).total_seconds()))
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


def as_data(sid: str, step: dict) -> dict:
    return {"id": sid, **step}


def chosen(record: dict, label_name: str | None, everything: bool, archived: bool = False) -> list[tuple[str, dict]]:
    """-> the active steps -- still to do, or all with `everything` -- or with `archived` the
    archived ones whatever their status; the most recently touched first, of one label when
    it is named."""
    found = [(sid, step) for sid, step in record["steps"].items()
             if (step["archived"] is not None if archived else step["archived"] is None)
             and (archived or everything or step["status"] in DUE)
             and (label_name is None or label_name in step["labels"])]
    return sorted(found, key=lambda pair: since(pair[1]), reverse=True)


def line(sid: str, step: dict, now: datetime) -> str:
    """-> one step on one line: its name and id, its status when not open with its reason,
    its labels, its key, its age, then its work."""
    parts = [f"{step['name']} [{sid}]"]
    if step["status"] != "open":
        parts.append(step["status"] + (f" ({step['reason']})" if step["reason"] else ""))
    parts += [f"#{name}" for name in step["labels"]]
    if step["key"]:
        parts.append(step["key"])
    parts.append(ago(since(step), now))
    return " · ".join(parts) + f" — {step['work']}"


def listing(root: Path, label_name: str | None, everything: bool, archived: bool, as_json: bool) -> str:
    record = load(root)
    found = chosen(record, label_name, everything, archived)
    if as_json:
        return json.dumps([as_data(sid, step) for sid, step in found], ensure_ascii=False)
    if not found:
        return "pp-steering: no step"
    now = datetime.fromisoformat(stamp())
    return "\n".join(line(sid, step, now) for sid, step in found)


def showing(root: Path, ident: str, as_json: bool) -> str:
    record = load(root)
    sid, step = step_of(record, ident)
    if as_json:
        return json.dumps(as_data(sid, step), ensure_ascii=False)
    now = datetime.fromisoformat(stamp())
    rows = [line(sid, step, now)]
    if step["comment"]:
        rows.append(f"  comment: {step['comment']}")
    rows.append(f"  born {step['at']} · touched {step['touched']}"
                + (f" · archived {step['archived']}" if step["archived"] else ""))
    return "\n".join(rows)


def reviewing(root: Path, as_json: bool) -> str:
    """-> the active steps still to do, the least recently touched first -- what the agent
    judges: done elsewhere, still relevant, or to drop. A line says whether the step has a
    comment."""
    found = list(reversed(chosen(load(root), None, False)))
    if as_json:
        return json.dumps([as_data(sid, step) for sid, step in found], ensure_ascii=False)
    if not found:
        return "pp-steering: no step"
    now = datetime.fromisoformat(stamp())
    return "\n".join(line(sid, step, now) + ("" if step["comment"] else " · no comment") for sid, step in found)


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


def main(argv: list[str]) -> int:
    verbs = ("add", "comment", "done", "drop", "wait", "open", "label", "note", "order", "dissolve", "list", "show",
             "sweep", "recall", "review")
    if not argv or argv[0] not in verbs:
        sys.stderr.write(__doc__)
        return 2
    verb, rest = argv[0], argv[1:]
    root = home()
    if verb == "add":
        rest, labels = flagged(rest, "--label")
        rest, keys = flagged(rest, "--key")
        if len(rest) < 1 or len(keys) > 1:
            refuse("step-invalid", "add <name> <work ...> [--label <l>]... [--key <family:slug>]")
        add(root, rest[0], " ".join(rest[1:]), labels, keys[0] if keys else None)
    elif verb == "comment" and rest:
        comment(root, rest[0], " ".join(rest[1:]))
    elif verb in ("done", "open") and len(rest) == 1:
        moved(root, rest[0], verb)
    elif verb in ("drop", "wait") and rest:
        moved(root, rest[0], "dropped" if verb == "drop" else "waiting", " ".join(rest[1:]))
    elif verb == "label" and len(rest) >= 2:
        label(root, rest[0], rest[1:])
    elif verb == "note" and rest:
        note(root, rest[0], " ".join(rest[1:]))
    elif verb == "order" and len(rest) >= 2:
        order(root, rest[0], rest[1:])
    elif verb == "dissolve" and len(rest) == 1:
        dissolve(root, rest[0])
    elif verb == "list":
        rest, labels = flagged(rest, "--label")
        rest, everything = switched(rest, "--all")
        rest, archived = switched(rest, "--archived")
        rest, as_json = switched(rest, "--json")
        if rest or len(labels) > 1 or (everything and archived):
            refuse("step-invalid", "list [--label <l>] [--all | --archived] [--json]")
        print(listing(root, labels[0] if labels else None, everything, archived, as_json))
    elif verb == "sweep" and not rest:
        sweep(root)
    elif verb == "recall" and len(rest) == 1:
        recall(root, rest[0])
    elif verb == "review" and rest in ([], ["--json"]):
        print(reviewing(root, bool(rest)))
    elif verb == "show":
        rest, as_json = switched(rest, "--json")
        if len(rest) != 1:
            refuse("step-invalid", "show <id> [--json]")
        print(showing(root, rest[0], as_json))
    else:
        refuse("step-invalid", f"`{' '.join(argv)}` -- the call does not fit `{verb}` (the usage: the script alone)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
