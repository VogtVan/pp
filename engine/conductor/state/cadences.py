"""state.cadences -- the ONE predicate of a work that is DUE: a record crossed by an
anchored day.

A package declares a cadence (a document to play at a socket) or a check (a
signal to push at the boot) against an ANCHOR -- a SETTINGS key holding a weekday
or `never` -- and a RECORD -- a jsonl of dated entries. The work is due when the
record's last entry stands BEFORE the last passage of the anchored weekday; a
`since` record narrows it to "and something happened since". Dates and records
alone decide -- never the agent's judgment, never a counter, never a clock of
its own: the bench writes the stamps it wants and the verdict follows.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import instance, settings
from ..core.errors import Refusal


def record_stamps(meta: Path, record: str) -> list[datetime]:
    """-> every `at` a jsonl record under the instance's records carries, as
    datetimes; an absent record or a torn line reads as nothing."""
    path = meta / instance.RECORDS / record
    if not path.is_file():
        return []
    found = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            found.append(datetime.fromisoformat(json.loads(line)["at"]))
        except (ValueError, KeyError):
            continue
    return found


def anchored_day(meta: Path, anchor: str) -> str:
    """-> the weekday an anchor names: `@SETTINGS.<key>` resolved at the instance
    (its own value, else the owner's default), or `never`; a literal weekday is
    accepted as it is. Anything else refuses `anchor-invalid`."""
    declared = settings.referenced(meta, anchor) if anchor.startswith("@") else anchor
    declared = str(declared or "").strip().lower()
    if declared in settings.WEEKDAYS or declared == "never":
        return declared
    raise Refusal("anchor-invalid",
                  f"`{anchor}` -- an anchor is a weekday or `never`, got `{declared or '(nothing)'}`")


def crossing_due(meta: Path, anchor: str, record: str, since: str | None = None) -> bool:
    """-> whether the anchored weekday was crossed since the record's last entry:
    the boundary is the most recent passage of that day (today included); an
    absent or empty record reads as never played, so the due stands from the
    first crossing on. `since` names a record that must carry an entry NEWER
    than the last stamp -- nothing new, nothing due. `never` never."""
    day = anchored_day(meta, anchor)
    if day == "never":
        return False
    last = max(record_stamps(meta, record), default=None)
    today = datetime.now(timezone.utc).date()
    boundary = today - timedelta(days=(today.weekday() - settings.WEEKDAYS.index(day)) % 7)
    if last is not None and last.date() >= boundary:
        return False
    if since:
        return any(last is None or one > last for one in record_stamps(meta, since))
    return True
