"""The `budget` domain, layer `acts`: what a season spent and launched, read then judged.

A definition belongs here when it chains the reading of the house's records and a judgement for the budget: what the
team has spent past its own bound since its last start (`spent`), and the wake-ups it launched since then
(`launched_since_start`), read from the journal's `wake-launched` or from the house's record of the launches and judged
by `went` (`wake/rules.py`). Only verbs and other acts call it. It may use the lower layers of any domain.
"""
from __future__ import annotations

from pathlib import Path

from house.rules import record_of
from house.store import lines_of
from documents.model import MESSAGES
from wake.rules import went


def spent(root: Path, state: dict) -> str:
    """-> what the team has spent past its own bound since its last start, '' when nothing: the money
    (`budget`), the wake-ups launched (`budget-launches`), or a `budget-spent` already written -- the
    bounds of step 5, which a resume never resets."""
    limits = state.season.limits
    if state.budget.budget_spent:
        return "budget-spent is written since the last start"
    if limits.get("budget") is not None and state.budget.cost >= limits["budget"]:
        return f"{state.budget.cost:g} of {limits['budget']:g} USD spent"
    if limits.get("budget-launches") is not None:
        launched = launched_since_start(root, state)
        if launched >= limits["budget-launches"]:
            return f"{launched} of {limits['budget-launches']} launches"
    return ""


def launched_since_start(root: Path, state: dict) -> int:
    """-> the team's wake-ups LAUNCHED since its last `team-started` -- the `wake-launched` event,
    else the tag at the house's `messages.jsonl`: what `budget-launches` counts."""
    started = state.season.started
    since = int((started.id if started is not None else None) or 0)
    tagged = {str(one.get("tag")) for one in lines_of(record_of(root, MESSAGES)) if one.get("tag")}
    return sum(1 for tag, one in state.wake.intents.items()
               if int(one.id or 0) > since and went(state, tagged, tag))
