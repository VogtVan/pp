"""What the context of a run is judged with: the window of its model, the adapter's constants, its marble."""
from __future__ import annotations

from pathlib import Path

from model.context import Scale
from model.policy import Policy
from rules.context import window_of
from store.adapters import declared_of, marble_of
from store.records import session_of_run, sent_to


def model_of(conductor, root: Path, name: str, key: str, cache: dict | None = None) -> Scale:
    """-> what the run's context is judged with: the `window` of its MODEL -- the model of its last message --
    as the adapter of its session's provider declares it, its default window for an undeclared model or no model
    named (`window_of`; None for a caller's command), that adapter's `base`, `ratio` and `kept` (`declared_of`),
    and the `marble` its launches carry (`marble_of`)."""
    known = session_of_run(root, name, key)
    provider = known.provider if known is not None else None
    sent = sent_to(root, name, key)
    model = sent[-1].policy.model if sent else None
    declared = declared_of(conductor, root, provider, cache)
    return Scale(window=window_of(declared, model), base=declared.base, ratio=declared.ratio, kept=declared.kept,
                 marble=marble_of(conductor, root, name, provider, cache))


def windowed(conductor, root: Path, provider: str | None, policy: Policy | None) -> int | None:
    """-> the window of the model a launch's `policy` names, as the adapter of `provider` declares it, its default
    window for an undeclared model or none named (`window_of`); None for a caller's command."""
    return window_of(declared_of(conductor, root, provider), policy.model if policy is not None else None)
