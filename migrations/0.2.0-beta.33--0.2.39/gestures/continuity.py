"""Continuity: the two records 0.2.0-beta.33 kept as JSON lines -- `operations.jsonl` (`{at, entry}`)
and `history.jsonl` (`{at, synthesis}`) -- taken over into the records `operations` and `history` of
the store of their instance, in file order, each entry keeping its date (the store writes it in its
own form, UTC to the microsecond), in ONE transaction per instance.

A last line that does not parse is a writer cut mid-line: skipped and said, as the old script did.
It has its own row in the counts, `<record>-torn`, so the table shows what was not taken over.
Any other line that does not parse refuses `records-unreadable`; a store record that already holds
entries refuses `records-taken`. Every instance is read and checked before the first is written.
Counted per instance and per record: the entries of the file, and the ones the store reads back
with their dates and bodies equal."""
from __future__ import annotations

import json
from pathlib import Path

import _common

from . import RECORDS, every

FILES = {"operations.jsonl": ("operations", "entry"), "history.jsonl": ("history", "synthesis")}
TORN = "{record}-torn"      # the row of the counts that says a torn last line skipped, beside its record's


def parsed(path: Path, field: str) -> tuple[list[dict], int]:
    """-> (the entries of a file, the torn last lines skipped); refuses `records-unreadable`."""
    raw = path.read_text(encoding="utf-8").splitlines()
    found, skipped = [], 0
    for number, line in enumerate(raw, 1):
        if not line.strip():
            continue
        try:
            one = json.loads(line)
            at, text = one["at"], one[field]
        except (ValueError, KeyError, TypeError):
            if number == len(raw):
                skipped += 1
                continue
            raise _common.Refused("records-unreadable", f"{path}: line {number} is not an entry -- nothing is "
                                                        "written; mend the file, then migrate again") from None
        found.append({"at": at, "body": {field: text}})
    return found, skipped


def gesture(house, engine) -> list[tuple]:
    planned = []
    for meta in house.instances:
        kept = engine.store.of(meta)
        files = []
        for name, (record, field) in FILES.items():
            path = meta / RECORDS / name
            if not path.is_file():
                continue
            entries, skipped = parsed(path, field)
            if kept.count(record):
                raise _common.Refused("records-taken", f"{meta}: the store record `{record}` already holds "
                                                       "entries -- the migration is played once")
            if skipped:
                print(f"migrate: continuity: {path.relative_to(house.root)} -- a torn last line skipped",
                      flush=True)
            files.append((record, entries, skipped))
        if files:
            planned.append((meta, kept, files))
    rows = []
    for meta, kept, files in planned:               # every instance checked before the first is written
        with kept.transaction() as session:
            for record, entries, _ in files:
                if entries:
                    session.extend(record, entries)
        for record, entries, skipped in files:
            stored = every(kept, record) if entries else []
            equal = sum(engine.store.moment(one["at"]) == back.at and one["body"] == back.body
                        for one, back in zip(entries, stored))
            rows.append((meta, record, len(entries), equal if len(stored) == len(entries) else len(stored)))
            if skipped:
                rows.append((meta, TORN.format(record=record), skipped, skipped))
    return rows
