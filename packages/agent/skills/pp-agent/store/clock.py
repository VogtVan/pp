"""The hour a record's line, a mark or an event is written at."""
from __future__ import annotations

from datetime import datetime, timezone


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
