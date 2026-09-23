#!/usr/bin/env python3
"""DETERMINISTIC keeper of the session's two records, under the instance's `.sys/records/`:
`operations.jsonl` (one operation per line) and `history.jsonl` (one weekly digest per line).

  pp-continuity.py recall               -> the operations of the last `continuity_recall_days`
                                           days, oldest first -- NOTHING at 0 or on an empty
                                           period: the boot's payload renders no section
  pp-continuity.py recall last <days>   -> every operation of the last <days> days, oldest first
  pp-continuity.py register <text ...>  -> appends {"at": <UTC>, "entry": <text>}
  pp-continuity.py history add <text|-> -> appends {"at": <UTC>, "synthesis": <text>}
                                           (`-` reads the paragraph on stdin)
  pp-continuity.py history last [n]     -> the n latest digests (default 1), newest first

Guards: an empty entry or synthesis refuses; an operation over `continuity_entry_budget`
characters (500 by default) and a digest over `continuity_digest_budget` (1500) refuse --
exit 2, nothing written; `0` lifts either limit. Both records are APPEND-ONLY: this script
is their only writer and never rewrites a line. They are data of the INSTANCE, so the
script finds its home by walking up from its own vendored location to the directory whose
`.sys/` carries `instance.yaml`, and refuses to run anywhere else.

Direct invocation is the operator's own call, unconducted; an agent reaches this skill
through the conductor (`./pp <key> -s pp-continuity ...`).

documentary: one script holds the three gestures of continuity because they share one
walk to the instance, one settings reader and one appender -- a verb differs only by the
record it addresses, the field it carries and the budget that guards it.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

OPERATIONS = "operations.jsonl"
HISTORY = "history.jsonl"
RECALL_KEY = "continuity_recall_days"       # the instance decides; the package says the default
ENTRY_KEY = "continuity_entry_budget"
DIGEST_KEY = "continuity_digest_budget"


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


def lines(path: Path, field: str) -> list[dict]:
    """-> every record of `path`, oldest first -- a line that does not parse refuses."""
    if not path.is_file():
        refuse(f"{path} is missing -- the package seeds it at install; run `./pp doctor`.")
    found = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            one = json.loads(line)
            datetime.fromisoformat(one["at"]), one[field]
        except (ValueError, KeyError, TypeError):
            refuse(f"line {number} of {path.name} is not a record -- this script is the "
                   "only writer, the file is not for hand edits.")
        found.append(one)
    return found


def since(path: Path, days: int) -> list[dict]:
    """-> the operations of the last `days` days, oldest first."""
    if days < 1:
        refuse("a period is at least 1 day.")
    horizon = datetime.now(timezone.utc) - timedelta(days=days)
    return [one for one in lines(path, "entry")
            if datetime.fromisoformat(one["at"]) >= horizon]


def append(path: Path, field: str, text: str, limit: int, said: str) -> dict:
    """Appends ONE record -- refuses empty or over-budget, nothing written."""
    value = " ".join(text.split())
    if not value:
        refuse(f"an empty {said} records nothing -- refused.")
    if limit and len(value) > limit:
        refuse(f"{len(value)} chars -- the budget is {limit}, "
               f"{'one line is a record' if field == 'entry' else 'a digest'}, not a report. "
               "Nothing written.")
    record = {"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), field: value}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def records(root: Path, name: str) -> Path:
    return root / ".sys" / "records" / name


def main(argv: list[str]) -> int:
    verb, rest = (argv[0], argv[1:]) if argv else ("", [])

    if verb == "recall" and not rest:                    # the boot's payload
        root = home()
        days = whole(root, RECALL_KEY)
        if days < 1:
            return 0                     # nothing recalled: no output, no section
        for one in since(records(root, OPERATIONS), days):
            print(f"{one['at']}  {one['entry']}")
        return 0                         # an empty period prints nothing, on purpose

    if verb == "recall" and len(rest) == 2 and rest[0] == "last":
        try:
            days = int(rest[1])
        except ValueError:
            refuse(f"`{rest[1]}` is not a number of days.")
        found = since(records(home(), OPERATIONS), days)
        if not found:
            print(f"pp-continuity: nothing recorded in the last {days} day(s).")
            return 0
        for one in found:
            print(f"{one['at']}  {one['entry']}")
        return 0

    if verb == "register" and rest:
        root = home()
        record = append(records(root, OPERATIONS), "entry", " ".join(rest),
                        whole(root, ENTRY_KEY), "entry")
        print(f"pp-continuity: consigned -- {record['entry']}")
        return 0

    if verb == "history" and len(rest) >= 2 and rest[0] == "add":
        root = home()
        text = sys.stdin.read() if rest[1:] == ["-"] else " ".join(rest[1:])
        record = append(records(root, HISTORY), "synthesis", text,
                        whole(root, DIGEST_KEY), "synthesis")
        print(f"pp-continuity: consigned -- {record['synthesis'][:60]}...")
        return 0

    if verb == "history" and rest and rest[0] == "last":
        try:
            count = int(rest[1]) if len(rest) > 1 else 1
        except ValueError:
            refuse(f"`{rest[1]}` is not a number.")
        if count < 1:
            refuse("`last` wants at least 1.")
        found = list(reversed(lines(records(home(), HISTORY), "synthesis")))[:count]
        if not found:
            print("pp-continuity: nothing recorded yet.")
            return 0
        for one in found:
            print(f"{one['at']}  {one['synthesis']}")
        return 0

    sys.stderr.write(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
