"""The `journal` domain, layer `store`: where the journal is read and written.

A definition belongs here when it reaches the journal on disk: it reads its lines from the last snapshot on, replays the
state a judge reads, or writes events under the journal's lock after it reads the team's declaration again. The lines of
a record read whole are read by `lines_of`, a tool of the whole skill in `house/store.py`. This module is the one writer
of a team's journal: every other module hands its events to it as typed bodies, and it writes the keys each body's
`json()` gives, in the order its writer gave them. What it wrote, it
gives back as EVENTS: each line written is decoded by `Event.of`, as a line read from the journal is, so the caller of a
writer reads the same values the state keeps. It imports the fold of its own domain (`journal/replay.py`): reading the
journal is reading its lines and folding them. The state a face reads, with the launches nobody holds, is read by
`journal/acts.py`.

The journal `.sys/records/teams/<name>/journal.jsonl` is APPEND-ONLY and the skill is its only writer: `{at, id, kind,
team, ...}`, the id the previous one + 1, read and written under the record's lock. A reader skips a last line still
being written; a line that does not parse anywhere else refuses by its name.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from house.rules import team_doc
from house.store import lines_of, now, refuse
from journal.model import Event
from journal.replay import replay


# --- the journal: the team's one truth ----------------------------------------------------

def tailed(path: Path) -> list[dict]:
    """-> the journal's events FROM its last `snapshot` line on (found by a text scan and
    verified by a parse), or all of them when none stands -- the read a state needs: the
    lines before the snapshot are never parsed."""
    if not path.is_file():
        return []
    raw = path.read_text(encoding="utf-8")
    at = raw.rfind('"kind": "snapshot"')
    while at >= 0:
        start = raw.rfind("\n", 0, at) + 1
        end = raw.find("\n", at)
        try:
            candidate = json.loads(raw[start:] if end < 0 else raw[start:end])
        except ValueError:
            candidate = None
        if isinstance(candidate, dict) and candidate.get("kind") == "snapshot":
            found = []
            lines = raw[start:].splitlines()
            for number, line in enumerate(lines, 1):
                if not line.strip():
                    continue
                try:
                    found.append(json.loads(line))
                except ValueError:
                    if number == len(lines):
                        continue
                    refuse(f"line {number} of the journal's tail is not a record -- this script is "
                           "the only writer, the file is not for hand edits.")
            return found
        at = raw.rfind('"kind": "snapshot"', 0, at)   # the match was a text's: scan on
    return lines_of(path)


def state_of(path: Path) -> dict:
    """-> the team's state, read from the last snapshot on: what every judge and every
    status reads -- `lines_of` whole stays the historians' (`log`, `watch`, `of_task`)."""
    return replay(tailed(path))


def written(conductor, root: Path, path: Path, name: str, judge, undeclared: bool = False) -> list[Event]:
    """The journal's critical section: under its lock the team's declaration is read again -- a team deleted
    meanwhile refuses `team-unknown`, and the directory the lock made, holding no journal, leaves with the
    refusal --, then the events are read, `judge(state, events)` says the events to append -- without `at`,
    `id`, `team` -- or refuses, and they are appended with the next ids. `undeclared` is the writer that speaks of
    a team whose declaration is away while its journal stands (the timer's notice of a failed tick): the journal
    standing is enough for it. -> the events written, each the line written decoded by `Event.of`, as a line read
    from the journal is."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with conductor.record.held(path):
        declaration = team_doc(root, name)
        if not declaration.is_file() and not (undeclared and path.is_file()):
            if not path.is_file():
                shutil.rmtree(path.parent, ignore_errors=True)
            refuse(f"team-unknown -- no {declaration}: the owner declares the team there.")
        events = tailed(path)
        state = replay(events)
        last = max((int(one.get("id") or 0) for one in events), default=0)
        made = []
        for offset, one in enumerate(judge(state, events), 1):
            one = one.json()                           # a typed body: the keys its writer gave, in their order
            made.append({"at": now(), "id": last + offset, "kind": one["kind"], "team": name,
                         **{key: value for key, value in one.items() if key != "kind"}})
        with path.open("a", encoding="utf-8") as handle:
            for one in made:
                handle.write(json.dumps(one, ensure_ascii=False) + "\n")
    return [Event.of(one) for one in made]           # decoded once written: the journal receives what it received


def appended(conductor, root: Path, path: Path, name: str, events: list[dict], undeclared: bool = False) -> list[Event]:
    """Appends the events given, judged already: the tick's writes; `undeclared` as `written` takes it."""
    return written(conductor, root, path, name, lambda state, lines: events, undeclared) if events else []
