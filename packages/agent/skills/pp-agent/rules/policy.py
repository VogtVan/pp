"""What the flags of a launch ask: its policy, its grammar, its bounds, the switches it waits to play."""
from __future__ import annotations

import shlex

from model.policy import Asked, Policy
from model.refusal import Refusal
from model.words import HOUSE

HEARTBEAT = 60                  # seconds without a step before a line says so

LAUNCHES = 24                   # launches of the harness one wake-up may play, unless `--launches` says


def asked_policy(asked: Asked) -> Policy:
    """-> the policy the flags give, as typed: the model, the budget, the regime, the effort."""
    return Policy(asked.model, asked.max_budget_usd, asked.permissions, asked.effort)


def house_judged(name: str, key: str | None, asked: Asked) -> None:
    """The house's own refusal, before any provider is judged or any message read: its material would
    be a clone in its own tree (`work-on-house`). Any other agent passes."""
    if name != HOUSE:
        return
    if asked.work is not None:
        raise Refusal("work-on-house -- the house works in its own tree: `--work` gives an AGENT its clone.")


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


def asked_switches(asked: Asked, where: str, base: str, pinned: set[str]) -> list[tuple[str, bool, str]]:
    """-> the `--package <name>=on|off` of a launch as (name, on, value), judged before anything is opened
    or written, against the packages the agent's instance at `where` pins (`pinned`, beyond its `base`):
    `package-invalid` (not the form), `package-base` (the instance's base), `package-unpinned` (a name it does
    not pin, switched on). A name it does not pin, switched off, asks nothing -- it plays nowhere already --
    and is left out."""
    found = []
    for value in asked.package or []:
        name, _, state = str(value).partition("=")
        if not name or state not in ("on", "off"):
            raise Refusal(f"package-invalid -- `--package {value}`: the form is <name>=on or <name>=off.")
        if name == base:
            raise Refusal(f"package-base -- `{name}` is the instance's base: it always plays.")
        if name not in pinned:
            if state == "off":
                continue
            raise Refusal(f"package-unpinned -- `{name}` is not pinned by {where}: the packages it pins are "
                          f"{', '.join(sorted(pinned)) or 'none'}.")
        found.append((name, state == "on", str(value)))
    return found


def seeded(switches: list, held: dict) -> dict:
    """-> the waiting list a launch's `--package` starts with, `{name: (on, value)}`: each switch the run's own
    switches (`held`) do not hold already -- at an opening, every one --, in the order given, the last word on
    a name winning. At an opening the list rides `PP_PACKAGES` on the `-new` (`packages_line`); at a resume
    `replayer` plays it: either way the word is WRITTEN at the run, over the agent's SETTINGS."""
    waiting: dict = {}
    for name, on, value in switches:
        waiting.pop(name, None)
        if held.get(name) != ("on" if on else "off"):
            waiting[name] = (on, value)
    return waiting
