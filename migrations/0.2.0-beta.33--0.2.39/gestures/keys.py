"""The keys of the plans' work: the families `plan-lot` and `plan-phase` of 0.2.0-beta.33 became the
one family `plan` (`plan:<address>`, at every depth). They live in two files of an instance: the
key of a step in `steps.json`, rewritten BEFORE steering takes the file over into the store, and
the held lines of the bus (`events.json`), whose text ends on the vector of the node they name.

A step whose new key is already another step's refuses the gesture (`key-taken`): a key is unique
at the record. Every instance is read before the first file is written. Counted per instance: the
old keys found and the ones rewritten."""
from __future__ import annotations

import json
import re
from pathlib import Path

import _common

from . import RECORDS, replace

OLD = re.compile(r"\bplan-(?:lot|phase):")
NEW = "plan:"


def rewritten(value):
    """-> the JSON value with every old key of a string rewritten, keys of objects included."""
    if isinstance(value, str):
        return OLD.sub(NEW, value)
    if isinstance(value, list):
        return [rewritten(one) for one in value]
    if isinstance(value, dict):
        return {rewritten(key): rewritten(one) for key, one in value.items()}
    return value


def steps_of(meta: Path) -> tuple[dict | None, int, int]:
    """-> the step record with its keys rewritten (None without a file to rewrite), the old keys
    found, the keys rewritten; `key-taken` when a new key is another step's."""
    path = meta / RECORDS / "steps.json"
    if not path.is_file():
        return None, 0, 0
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
        steps = record["steps"]
        held = {step.get("key") for step in steps.values() if step.get("key")}
    except (ValueError, KeyError, TypeError, AttributeError):
        return None, 0, 0                          # steering says what it cannot read
    found = done = 0
    for sid, step in steps.items():
        key = step.get("key") or ""
        if not OLD.match(key):
            continue
        found += 1
        anew = OLD.sub(NEW, key, count=1)
        if anew in held:
            raise _common.Refused("key-taken", f"{meta}: step {sid} -- `{key}` cannot become `{anew}`, the key "
                                               "of another step")
        held.discard(key)
        held.add(anew)
        step["key"] = anew
        done += 1
    return (record if found else None), found, done


def bus_of(meta: Path) -> tuple[str | None, int, int]:
    """-> the bus with its old keys rewritten (None when nothing to rewrite), the held lines that carry
    one, the lines rewritten."""
    path = meta / RECORDS / "events.json"
    if not path.is_file():
        return None, 0, 0
    text = path.read_text(encoding="utf-8")
    try:
        bus = json.loads(text)
    except ValueError:
        raise _common.Refused("bus-unreadable", f"{path} does not parse") from None
    lines = [[key, value] for key, value in bus.items() if OLD.search(json.dumps([key, value]))] if isinstance(bus, dict) else []
    if not lines:
        return None, 0, 0
    done = sum(not OLD.search(json.dumps(rewritten(line))) for line in lines)
    return json.dumps(rewritten(bus), indent=2, ensure_ascii=False) + "\n", len(lines), done


def gesture(house, engine) -> list[tuple]:
    planned = [(meta, steps_of(meta), bus_of(meta)) for meta in house.instances]
    rows = []
    for meta, (record, found, done), (bus, lines, cleaned) in planned:
        if record is not None:
            replace(meta / RECORDS / "steps.json", json.dumps(record, ensure_ascii=False, indent=1) + "\n")
        if bus is not None:
            replace(meta / RECORDS / "events.json", bus)
        if found or lines:
            rows += [(meta, "step-keys", found, done), (meta, "bus-lines", lines, cleaned)]
    return rows
