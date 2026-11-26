"""The `budget` domain, layer `rules`: what the team may still spend, and what raising its budget writes.

A definition belongs here when it computes its answer from the state and the values it is given: what the launches
under way hold back, the share of the rest a launch may spend, the allowance a season gives. It also holds the
decision of `team budget`, in two steps around the reading of the disk: who raises and the amount (`budget_asked`),
then, given what the season launched, the bound of the launches and the `budget-raised` it composes
(`budget_raised`). A decision DECLINES by a code, and the verb says the sentence. It reads no disk, no clock and no
environment and prints nothing: what needs the system belongs to `store`.
"""
from __future__ import annotations

import math

from house.model import Declined
from budget.model import BudgetRaised
from wake.rules import open_intents
from task.rules import principal_of


def reserved_of(state: dict) -> float:
    """-> the money the wake-ups under way may still spend: the allowances of the intents without an
    end since the last `team-started`."""
    started = state.season.started
    since = int((started.id if started is not None else None) or 0)
    return round(sum(float(one.body.allowance or 0) for one in open_intents(state)
                     if int(one.id or 0) > since), 6)


def share_of(state: dict) -> dict | None:
    """-> the team's budget as the faces say it, `{cap, spent, reserved, left}`: `left` the rest no wake-up
    holds, below 0 when the last ones went past; None without `budget:`."""
    cap = state.season.limits.get("budget")
    if cap is None:
        return None
    reserved = reserved_of(state)
    return {"cap": float(cap), "spent": round(state.budget.cost, 6), "reserved": reserved,
            "left": round(float(cap) - state.budget.cost - reserved, 6)}


def allowance_of(state: dict, started: dict) -> float | None:
    """-> the money a wake-up launched now may spend: its PART of the team's rest, min((budget - the cost
    kept) / k, the rest no wake-up under way holds) -- k the wake-ups that may play together, min(`parallel`,
    the members), the members without `parallel:` --, down to the micro-dollar; None without `budget:`."""
    share = share_of(state)
    if share is None:
        return None
    members = max(1, len(started.body.agents or {}))
    parallel = state.season.limits.get("parallel")
    k = members if parallel is None else max(1, min(int(parallel), members))
    part = min((share["cap"] - share["spent"]) / k, share["left"])
    return math.floor(part * 1e6) / 1e6



def budget_asked(state: dict, owner: str, principal: str | None, money: float | None) -> str:
    """-> who raises the bounds: `team budget` judged before the disk is read -- the principal `--as` names
    (`principal_of`), the dollars asked above the cost of the season; else `Declined`: `team-not-started`,
    `budget-invalid` (`usd`, the dollars, the cost)."""
    if state.season.started is None:
        raise Declined("team-not-started")
    sender = principal_of(state, owner, principal)
    if money is not None and not money > state.budget.cost:
        raise Declined("budget-invalid", "usd", money, state.budget.cost)
    return sender


def budget_raised(sender: str, money: float | None, wakes: int | None, launched: int) -> list:
    """-> `budget-raised {by, budget?, launches?}`: the bounds asked, the launches above the `launched` since the
    start (what the disk said); else `Declined("budget-invalid", "launches", wakes, launched)`."""
    if wakes is not None and not wakes > launched:
        raise Declined("budget-invalid", "launches", wakes, launched)
    return [BudgetRaised.made(by=sender, **({"budget": money} if money is not None else {}),
                              **({"launches": wakes} if wakes is not None else {}))]
