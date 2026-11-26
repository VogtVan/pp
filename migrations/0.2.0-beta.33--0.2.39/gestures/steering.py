"""Steering: the record 0.2.0-beta.33 kept in `steps.json` -- `{counters: {s}, steps: {<id>: {twelve
fields}}, labels: {<name>: {note, order}}}` -- taken over into the store of its instance, the records
0.2.39 reads:

  steps     key = the step's id, body = its twelve fields as they stand, in the order of the ids
            (a step's rank is its birth), `at` = the latest of its stamps
  labels    key = the label's name, body = `{note, order}`, in the order of the file
  counters  key `s`, body `{value}`

with the indexes of `archived`, `status`, `name` and `key`, in ONE transaction per instance. Every
file is read and every store checked before the first instance is written: a file that does not
parse, or that is not a step record, refuses `steps-unreadable`; a store that already holds steps,
labels or a counter refuses `steps-taken` -- the migration is played once. Counted per instance:
the steps, the labels and the counter, in the file and in the store read back, ids and bodies
compared."""
from __future__ import annotations

import json
import re
from pathlib import Path

import _common

from . import RECORDS, every

FIELDS = {"name", "at", "work", "comment", "status", "reason", "labels", "key", "touched", "closed", "archived",
          "recalled"}
STAMPS = ("at", "touched", "closed", "archived", "recalled")
INDEXED = ("archived", "status", "name", "key")
ID = re.compile(r"^\S+\.s\.([0-9]+)$")


def parsed(path: Path) -> dict:
    """-> the step record of the file; refuses `steps-unreadable` otherwise."""
    def unreadable(why: str):
        return _common.Refused("steps-unreadable", f"{path}: {why} -- nothing is written; mend the file from the "
                                                   "backup or by hand, then migrate again")
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        raise unreadable("the file does not parse") from None
    if (not isinstance(record, dict) or set(record) != {"counters", "steps", "labels"}
            or not isinstance(record["counters"], dict) or not isinstance(record["counters"].get("s"), int)
            or not isinstance(record["steps"], dict) or not isinstance(record["labels"], dict)):
        raise unreadable("not the steps with their counter")
    for sid, step in record["steps"].items():
        if not ID.fullmatch(sid) or not isinstance(step, dict) or set(step) != FIELDS:
            raise unreadable(f"step `{sid}` is not a step")
    for name, label in record["labels"].items():
        if not isinstance(label, dict) or not isinstance(label.get("order"), list):
            raise unreadable(f"label `{name}` is not a label")
    return record


def gesture(house, engine) -> list[tuple]:
    planned = []
    for meta in house.instances:
        path = meta / RECORDS / "steps.json"
        if not path.is_file():
            continue
        record = parsed(path)
        kept = engine.store.of(meta)
        if kept.count("steps") or kept.count("labels") or kept.get("counters", "s") is not None:
            raise _common.Refused("steps-taken", f"{meta}: the store already holds steps -- the migration is "
                                                 "played once")
        planned.append((meta, kept, record))
    rows = []
    for meta, kept, record in planned:             # every instance checked before the first is written
        steps = sorted(record["steps"].items(), key=lambda pair: int(ID.fullmatch(pair[0]).group(1)))
        labels = list(record["labels"].items())
        counter = record["counters"]["s"]
        with kept.transaction() as session:
            for field in INDEXED:
                session.index("steps", field)
            if steps:
                session.extend("steps", [{"key": sid, "body": step,
                                          "at": max(step[one] for one in STAMPS if step[one])} for sid, step in steps])
            if labels:
                session.extend("labels", [{"key": name, "body": label} for name, label in labels])
            session.put("counters", "s", {"value": counter})
        stored, named = every(kept, "steps"), every(kept, "labels")
        value = kept.get("counters", "s").body["value"]
        equal = sum(one.key == sid and one.body == step for one, (sid, step) in zip(stored, steps))
        tagged = sum(one.key == name and one.body == label for one, (name, label) in zip(named, labels))
        rows += [(meta, "steps", len(steps), equal if len(stored) == len(steps) else len(stored)),
                 (meta, "labels", len(labels), tagged if len(named) == len(labels) else len(named)),
                 (meta, "counters", counter, value)]
    return rows
