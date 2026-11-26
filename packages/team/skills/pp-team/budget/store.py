"""The `budget` domain, layer `store`: where the budget meets the system.

A definition belongs here when it reaches the system for a budget and gives back what it read: it asks the engine
whether the provider's adapter reads a cost it can bound. What a season spent and launched, read from the house's
records and judged, is an act (`budget/acts.py`); a judgement that needs no system belongs to a rule.
"""
from __future__ import annotations

from pathlib import Path



def measured(root: Path, conductor, started: dict) -> bool:
    """-> whether the adapter of the launches' grammar declares a scope for the cost it reads (`COST`):
    the provider `team start` kept, else the one the house is wired with -- what `agent start` holds a
    run's cap by. False when none is known or the adapter refuses."""
    grammar = (started.body.launch or {}).get("provider")
    if grammar is None:
        wired = conductor.install.wired_providers(root.parent)
        grammar = wired[0] if len(wired) == 1 else None
    if grammar is None:
        return False
    try:
        return getattr(conductor.adapters.load(str(grammar), root), "COST", None) in ("session", "launch")
    except conductor.Refusal:
        return False
