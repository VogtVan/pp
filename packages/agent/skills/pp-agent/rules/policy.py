"""What the flags of a launch ask: its policy, its provider, its grammar, its bounds."""
from __future__ import annotations

import shlex

from model.policy import Asked, Policy
from model.refusal import Refusal

HEARTBEAT = 60                  # seconds without a step before a line says so

LAUNCHES = 24                   # launches of the harness one wake-up may play, unless `--launches` says


def asked_policy(asked: Asked) -> Policy:
    """-> the policy the flags give, as typed: the model, the budget, the regime, the effort."""
    return Policy(asked.model, asked.max_budget_usd, asked.permissions, asked.effort)


def provider_of(asked: Asked, wired: list[str]) -> tuple[list[str], str | None]:
    """-> (the harness command's head, or the provider's name): the caller's command,
    else the caller's provider, else the ONE the house is `wired` with. A caller's command
    owes the grammar its output is read in, `--provider` beside it (`grammar-missing`)."""
    if asked.harness is not None:
        if asked.provider is None:
            raise Refusal("grammar-missing -- `--harness` runs a caller's command: name the grammar its output is "
                          "read in with `--provider <name>` beside it -- the provider whose adapter reads it.")
        return shlex.split(asked.harness), None
    if asked.provider is not None:
        return [], str(asked.provider)
    if not wired:
        raise Refusal("provider-missing -- no --harness, no --provider, and the house is wired with no adapter.")
    if len(wired) > 1:
        raise Refusal(f"provider-ambiguous -- the house is wired with {', '.join(wired)}: name one with --provider.")
    return [], wired[0]


def provider_named(asked: Asked, wired: list[str]) -> str:
    """-> the name of the harness a launch plays: the provider, or `harness` for a caller's command."""
    return provider_of(asked, wired)[1] or "harness"


def grammar_of(asked: Asked, provider: str | None) -> str:
    """-> the provider whose adapter READS what the harness prints: the provider launched, or under a
    caller's command the one `--provider` names beside it (`provider_of` refuses a command without it)."""
    return provider or str(asked.provider)


def launches_of(asked: Asked) -> int:
    """-> the launches one wake-up may play: `--launches`, a whole number at least 1
    (`launches-invalid` otherwise, a `Refusal` raised), 24 without it."""
    if asked.launches is None:
        return LAUNCHES
    try:
        count = int(asked.launches)
    except ValueError:
        count = 0
    if count < 1:
        raise Refusal(f"launches-invalid -- `--launches {asked.launches}`: a whole number of launches, at least 1.")
    return count


def heartbeat_of(asked: Asked) -> int:
    """-> the seconds without a step before a line says so: `--heartbeat`, a whole number
    at least 1 (`heartbeat-invalid` otherwise, a `Refusal` raised), 60 without it."""
    if asked.heartbeat is None:
        return HEARTBEAT
    try:
        seconds = int(asked.heartbeat)
    except ValueError:
        seconds = 0
    if seconds < 1:
        raise Refusal(f"heartbeat-invalid -- `--heartbeat {asked.heartbeat}`: a whole number of seconds, at least 1.")
    return seconds
