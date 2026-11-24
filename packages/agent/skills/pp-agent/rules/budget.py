"""The budget of a run: what a cap leaves, what a launch cost."""
from __future__ import annotations

from dataclasses import replace

from model.cost import Budget
from model.policy import Policy


def budget_of(policy: Policy, spent: float) -> Budget | None:
    """-> the run's budget, from the policy's cap and what the run spent; None without a cap. `left` goes
    below 0 when the last launch went past the cap."""
    cap = policy.max_budget_usd
    if not isinstance(cap, (int, float)):
        return None
    return Budget(cap=float(cap), spent=round(spent, 6), left=round(float(cap) - spent, 6))


def limiter(policy: Policy, spent: float, spells: tuple[str, ...]):
    """-> `limit(spent_now)`: the policy of the NEXT launch, given what the exchange spent so far
    (`spent_now`, None for nothing) on top of what the run spent before it (`spent`) -- the run's
    remainder as `max_budget_usd` where the adapter of the provider spells the key (`spells`), the
    key dropped where it does not; None when the cap leaves nothing. Without a cap, the policy as is."""
    cap = policy.max_budget_usd
    if not isinstance(cap, (int, float)):
        return lambda spent_now: policy

    def limit(spent_now: float | None) -> Policy | None:
        left = round(float(cap) - spent - float(spent_now or 0.0), 6)
        if left <= 0:
            return None
        return replace(policy, max_budget_usd=left if "max_budget_usd" in spells else None)
    return limit


def costed(scope: str | None, read, cumul: float | None) -> tuple[float | None, float | None]:
    """-> (the launch's cost, the session's cumul after it) from the cost the adapter read, in its scope;
    (None, the cumul as it was) when it read none or declares no scope."""
    if scope is None or not isinstance(read, (int, float)):
        return None, cumul
    if scope == "session":
        return round(float(read) - float(cumul or 0.0), 6), float(read)
    return round(float(read), 6), round(float(cumul or 0.0) + float(read), 6)
