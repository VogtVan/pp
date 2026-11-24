#!/usr/bin/env python3
"""DETERMINISTIC keeper of the session's two records, kept in the instance's store
(`conductor.store`): `operations` (one operation per entry, `{"entry": <text>}`) and `history`
(one weekly digest per entry, `{"synthesis": <text>}`).

  pp-continuity.py recall               -> the latest RECALL_PAGE operations of the last
                                           `continuity_recall_days` days, oldest first, then how
                                           many older ones are left and the call that reads them
                                           -- NOTHING at 0 or on an empty period: the boot's
                                           payload renders no section
  pp-continuity.py recall last <days> [--skip <k>]
                                        -> the latest RECALL_PAGE operations of the last <days>
                                           days past the <k> latest (0 by default), oldest first,
                                           then how many older ones are left and the call that
                                           reads them
  pp-continuity.py register <text ...>  -> adds {"entry": <text>}, dated by the store
  pp-continuity.py history add <text|-> -> adds {"synthesis": <text>}, dated by the store
                                           (`-` reads the paragraph on stdin)
  pp-continuity.py history last [n]     -> the n latest digests (default 1, at most the store's
                                           bound), newest first

Guards: an empty entry or synthesis refuses; an operation over `continuity_entry_budget`
characters (500 by default) and a digest over `continuity_digest_budget` (1500) refuse --
exit 2, nothing written; `0` lifts either limit. Both records are APPEND-ONLY: this script
is their only writer and never rewrites an entry. Every read is a bounded query of the store:
no verb reads a whole record. A record not written yet reads as empty. They are data of the
INSTANCE, so the script finds its home by walking up from its own vendored location to the
directory whose `.sys/` carries `instance.yaml`, and refuses to run anywhere else.

Direct invocation is the operator's own call, unconducted; an agent reaches this skill
through the conductor (`./pp <key> -s pp-continuity ...`).

documentary: one script holds the three gestures of continuity because they share one
walk to the instance, one settings reader and one appender -- a verb differs only by the
record it addresses, the field it carries and the budget that guards it.
"""
from __future__ import annotations

import sys
from pathlib import Path

OPERATIONS = "operations"     # the records of the store this script keeps
HISTORY = "history"
RECALL_KEY = "continuity_recall_days"       # the instance decides; the package says the default
ENTRY_KEY = "continuity_entry_budget"
DIGEST_KEY = "continuity_digest_budget"
RECALL_PAGE = 40      # the operations one recall prints: at the entry budget (500) a page stays
                      # near 21 000 characters, under a host's tool output (25 000), so no page is cut


def refuse(said: str) -> None:
    sys.stderr.write(f"pp-continuity: {said}\n")
    raise SystemExit(2)


def home() -> Path:
    """-> the instance this vendored copy belongs to -- the bootstrap's one walk."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from _core import home as walk                       # noqa: E402 -- the bootstrap
    found = walk(__file__)
    if found is None:
        refuse("not inside an installed instance -- no record to reach.")
    return found


def engine():
    """-> the conductor module this vendored copy runs beside -- the bootstrap's one walk."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from _core import core                                # noqa: E402 -- the bootstrap
    return core(__file__)


def whole(root: Path, key: str) -> int:
    """-> the instance's EFFECTIVE value for `key` -- the operator's line, the effort's
    preset over it, the fragment's default under it. A value that is not a whole number
    refuses."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from _core import core                                # noqa: E402 -- the bootstrap
    face = core(__file__).settings
    try:
        found = face.of(root).of_package(key, face.default_of(root, key))
    except Exception as raised:            # the face refuses a TYPED value by its own name
        if type(raised).__name__ != "Refusal":
            raise
        refuse(str(raised))                # the face names the code, we say it
    try:
        return int(found)
    except (TypeError, ValueError):
        refuse(f"`{key}: {found}` is not a whole number.")


def store(root: Path):
    """-> the store of the instance at `root`."""
    return engine().store.of(root)


def stamp(at: str) -> str:
    """-> an entry's time as the recall prints it: to the second, UTC."""
    return at[:19] + "Z"


def period(days: int) -> str:
    """-> the `since` of the last `days` days, a duration the store reads back from now."""
    if days < 1:
        refuse("a period is at least 1 day.")
    return f"{days}d"


def append(root: Path, record: str, field: str, text: str, limit: int, said: str) -> str:
    """Adds ONE entry -- refuses empty or over-budget, nothing written. -> the value written."""
    value = " ".join(text.split())
    if not value:
        refuse(f"an empty {said} records nothing -- refused.")
    if limit and len(value) > limit:
        refuse(f"{len(value)} chars -- the budget is {limit}, "
               f"{'one line is a record' if field == 'entry' else 'a digest'}, not a report. "
               "Nothing written.")
    store(root).append(record, {field: value})       # the store serializes the writers
    return value


def page(root: Path, days: int, skip: int):
    """-> (the page of the RECALL_PAGE latest operations of the last `days` days past the `skip`
    latest, the total of the period). The `skip` latest are walked by cursor, a bounded page at
    a time -- the store has no offset and no read takes the whole period."""
    kept, since, cursor, left = store(root), period(days), None, skip
    while left > 0:
        step = kept.read(OPERATIONS, last=min(left, kept.limit()), since=since,
                         **({} if cursor is None else {"before": cursor}))
        if not step.rows:
            return step, step.total
        cursor, left = step.rows[0].seq, left - len(step.rows)
    found = kept.read(OPERATIONS, last=RECALL_PAGE, since=since,
                      **({} if cursor is None else {"before": cursor}))
    return found, found.total


def recalled(root: Path, days: int, skip: int) -> int:
    """Prints the page past `skip`, then the older ones left and the call that reads them.
    -> how many operations the period holds."""
    found, total = page(root, days, skip)
    for one in found.rows:
        print(f"{stamp(one.at)}  {one.body.get('entry', '')}")
    older = max(total - skip - len(found.rows), 0)
    if found.rows and older:
        print(f"pp-continuity: {older} older operation(s) of the last {days} day(s) left -- "
              f"read them with `recall last {days} --skip {skip + len(found.rows)}`.")
    return total


def main(argv: list[str]) -> int:
    verb, rest = (argv[0], argv[1:]) if argv else ("", [])

    if verb == "recall" and not rest:                    # the boot's payload
        root = home()
        days = whole(root, RECALL_KEY)
        if days < 1:
            return 0                     # nothing recalled: no output, no section
        recalled(root, days, 0)
        return 0                         # an empty period prints nothing, on purpose

    if verb == "recall" and len(rest) in (2, 4) and rest[0] == "last" and rest[2:3] in ([], ["--skip"]):
        try:
            days = int(rest[1])
        except ValueError:
            refuse(f"`{rest[1]}` is not a number of days.")
        skip = 0
        if len(rest) == 4:
            if not rest[3].isdigit():
                refuse(f"`{rest[3]}` is not a number of operations to skip.")
            skip = int(rest[3])
        root = home()
        total = store(root).count(OPERATIONS, since=period(days))
        if not total:
            print(f"pp-continuity: nothing recorded in the last {days} day(s).")
            return 0
        if skip >= total:
            print(f"pp-continuity: {total} operation(s) in the last {days} day(s), none past the {skip} latest.")
            return 0
        recalled(root, days, skip)
        return 0

    if verb == "register" and rest:
        root = home()
        value = append(root, OPERATIONS, "entry", " ".join(rest), whole(root, ENTRY_KEY), "entry")
        print(f"pp-continuity: consigned -- {value}")
        return 0

    if verb == "history" and len(rest) >= 2 and rest[0] == "add":
        root = home()
        text = engine().reading.piped() if rest[1:] == ["-"] else " ".join(rest[1:])
        value = append(root, HISTORY, "synthesis", text, whole(root, DIGEST_KEY), "synthesis")
        print(f"pp-continuity: consigned -- {value[:60]}...")
        return 0

    if verb == "history" and rest and rest[0] == "last":
        try:
            count = int(rest[1]) if len(rest) > 1 else 1
        except ValueError:
            refuse(f"`{rest[1]}` is not a number.")
        if count < 1:
            refuse("`last` wants at least 1.")
        found = store(home()).read(HISTORY, last=count)
        if not found.rows:
            print("pp-continuity: nothing recorded yet.")
            return 0
        for one in reversed(found.rows):
            print(f"{stamp(one.at)}  {one.body.get('synthesis', '')}")
        if count > found.bound and found.total > len(found.rows):
            print(f"pp-continuity: {len(found.rows)} of {found.total} digest(s) -- the bound of a read "
                  f"is {found.bound}.")
        return 0

    sys.stderr.write(__doc__)
    return 2


def guarded(argv: list[str]) -> int:
    """-> `main`'s code; a refusal of the store (busy, corrupt, unbounded) said by its name, exit 2."""
    try:
        return main(argv)
    except Exception as raised:            # the engine refuses by its own name
        if type(raised).__name__ != "Refusal":
            raise
        refuse(str(raised))


if __name__ == "__main__":
    raise SystemExit(guarded(sys.argv[1:]))
