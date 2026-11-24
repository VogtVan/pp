"""What the readings show of a run's flow: one event of it, as a line."""
from __future__ import annotations

from faces.text import harmless
from model.text import first_line


def event_line(event: dict, current: int | None) -> str:
    """-> one event of a run's flow as `flow` says it: its hour, the exchange it belongs to (`current`, a dash
    before the first), its kind -- a step by its event --, the first line of its text, harmless."""
    kind = event.get("event") if event.get("kind") == "step" else event.get("kind")
    text = event.get("text") or event.get("response") or event.get("title") or event.get("reason") or ""
    return f"{str(event.get('at', ''))[11:19]}  #{current or '-'}  {kind}  {harmless(first_line(str(text)))}".rstrip()
