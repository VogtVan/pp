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
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from . import instance, record, settings
from ..core.errors import Refusal

CLAIMS = "claims.jsonl"     # the record of who plays what is due once: {at, cadence, period, run}


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


def boundary_of(meta: Path, anchor: str) -> date | None:
    """-> the PERIOD a cadence stands in now: the most recent passage of its anchored
    weekday, today included -- the date every run computes alike from the calendar;
    None under `never`."""
    day = anchored_day(meta, anchor)
    if day == "never":
        return None
    today = datetime.now(timezone.utc).date()
    return today - timedelta(days=(today.weekday() - settings.WEEKDAYS.index(day)) % 7)


def _claims(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    found = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            found.append(json.loads(line))
        except ValueError:
            continue                 # a torn line is no claim
    return found


def holder_of(meta: Path, cadence: str, period: str) -> str | None:
    """-> the run that holds the claim of `cadence` for `period`, or None."""
    for one in reversed(_claims(meta / instance.RECORDS / CLAIMS)):
        if one.get("cadence") == cadence and one.get("period") == period:
            return str(one.get("run", ""))
    return None


def claim(meta: Path, cadence: str, period: str, run: str, alive) -> bool:
    """CLAIMS `cadence` for `period` on behalf of `run`, under the claims record's lock:
    True when the period was free, already this run's, or held by a run `alive(run)`
    says is dead -- the line written or replaced --; False when another living run
    holds it. What is due once per period is thus played by ONE run, the first that
    boots into it. Dates, records and the runs' saved states decide -- no clock."""
    path = meta / instance.RECORDS / CLAIMS
    with record.held(path):
        held = _claims(path)
        standing = [one for one in held if one.get("cadence") == cadence and one.get("period") == period]
        if standing:
            holder = str(standing[-1].get("run", ""))
            if holder == run:
                return True
            if alive(holder):
                return False
        kept = [one for one in held if not (one.get("cadence") == cadence and one.get("period") == period)]
        kept.append({"at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                     "cadence": cadence, "period": period, "run": run})
        record.replace(path, "".join(json.dumps(one, ensure_ascii=False) + "\n" for one in kept))
    return True


def crossing_due(meta: Path, anchor: str, record: str, since: str | None = None) -> bool:
    """-> whether the anchored weekday was crossed since the record's last entry:
    the boundary is the most recent passage of that day (today included); an
    absent or empty record reads as never played, so the due stands from the
    first crossing on. `since` names a record that must carry an entry NEWER
    than the last stamp -- nothing new, nothing due. `never` never."""
    boundary = boundary_of(meta, anchor)
    if boundary is None:
        return False
    last = max(record_stamps(meta, record), default=None)
    if last is not None and last.date() >= boundary:
        return False
    if since:
        return any(last is None or one > last for one in record_stamps(meta, since))
    return True
