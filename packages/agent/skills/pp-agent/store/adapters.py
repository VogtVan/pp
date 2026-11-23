"""What the adapter of a provider declares and reads: the cost, the caps, the windows, the marble, the stop."""
from __future__ import annotations

import subprocess
from pathlib import Path

from model.cost import Declared
from model.exchange import Launch, Stop
from model.policy import Policy
from model.words import ESTIMATE
from store.houses import agent_at
from store.refusal import refuse


def cost_scope(conductor, root: Path, grammar: str) -> str | None:
    """-> the scope of the cost the adapter of `grammar` reads, as its `wire.py` declares it (`COST`):
    `session` (the session's cumul at that launch), `launch` (that launch alone), or None (no cost read,
    or no declaration)."""
    scope = getattr(conductor.adapters.load(grammar, root), "COST", None)
    return scope if scope in ("session", "launch") else None


def launcher_cap(conductor, root: Path, grammar: str, policy: Policy) -> int | None:
    """-> the CAP this script puts on the outputs it serves at the prompt, in characters, read from what the
    adapter of `grammar` declares: `CAPS[model]` when the policy's model is named there -- the name as
    `--model` gives it --, else its `CAP` (the client's own bound, whatever the model), else None: no
    variable on the principal's call, the engine's floor holds. The engine names no model; the launcher knows it."""
    wire = conductor.adapters.load(grammar, root)
    model = policy.model
    found = (dict(getattr(wire, "CAPS", {}) or {})).get(model) if isinstance(model, str) else None
    if found is None:
        found = getattr(wire, "CAP", None)
    return int(found) if isinstance(found, int) and not isinstance(found, bool) and found > 0 else None


def spells_of(conductor, root: Path, provider: str | None) -> tuple[str, ...]:
    """-> the keys of a policy the adapter of `provider` spells on the line it composes (its `SPELLS`); none
    for a caller's command."""
    if provider is None:
        return ()
    return tuple(getattr(conductor.adapters.load(provider, root), "SPELLS", ()))


def declared_of(conductor, root: Path, provider: str | None, cache: dict | None = None) -> Declared:
    """-> what the adapter of `provider` declares for a run's context: `windows` (`CONTEXT_WINDOWS`, its models
    verified alone), `default` (`DEFAULT_WINDOW`, the window of a model it does not declare, None without one) and
    the estimate's `base`, `ratio` and `kept` (`ESTIMATE`, their defaults when it declares none); no window and the
    defaults alone for a caller's command or an adapter that does not load."""
    cache = {} if cache is None else cache
    if provider not in cache:
        module = None
        if provider:
            try:
                module = conductor.adapters.load(provider, root)
            except conductor.Refusal:
                module = None
        windows = getattr(module, "CONTEXT_WINDOWS", {}) or {}
        cache[provider] = Declared(
            windows=tuple(dict(windows).items()), default=getattr(module, "DEFAULT_WINDOW", None),
            **{key: getattr(module, name, default) for key, (name, default) in ESTIMATE.items()})
    return cache[provider]


def marble_of(conductor, root: Path, name: str, provider: str | None, cache: dict | None = None) -> int:
    """-> the tokens of the standing orders the agent's launches carry under `provider`, as the engine counts them
    (`conductor.metrics.tokens`): its marble `.sys/system.md` when the provider's adapter receipts it
    (`receipted`), 0 for a caller's command, an adapter that carries none or a marble not compiled yet."""
    cache = {} if cache is None else cache
    if ("marble", name, provider) not in cache:
        meta = agent_at(root, name)
        marble = meta / ".sys" / "system.md"
        carried = marble.is_file() and receipted(conductor, root, meta, [], provider, Policy())
        cache[("marble", name, provider)] = conductor.metrics.tokens(marble.read_text(encoding="utf-8")) if carried else 0
    return cache[("marble", name, provider)]


def receipted(conductor, root: Path, meta: Path, head: list[str], provider: str | None, policy: Policy) -> bool:
    """-> whether the harness's launch carries the MARBLE: the receipt `PP_MARBLE` the provider's
    adapter declares in the env of the line it composes (claude, gemini and codex do; cursor,
    whose host carries no marble, does not). A caller's command (`--harness`) composes nothing
    and carries none. Read on the composition alone, nothing launched."""
    if head or not provider:
        return False
    try:
        _, env, _ = conductor.adapters.launch(provider, meta.parent, meta, "", marble=meta / ".sys" / "system.md",
                                              wiring=root.parent, policy=policy.json() or None)
    except conductor.Refusal:
        return False                               # the launch's own refusal is said where it is composed
    return str(env.get("PP_MARBLE", "")) == "1"


def read_answer(conductor, meta: Path, grammar: str, played: subprocess.CompletedProcess) -> Launch:
    """-> what the harness answered, its session identity owed: read by the adapter of `grammar`
    (`conductor.adapters.answer`), a caller's command as a provider's, and its `stop` beside when the
    adapter reads one (`stop_of`). No identity refuses `session-missing`: nothing is kept."""
    try:
        read = conductor.adapters.answer(grammar, meta, played.stdout, played.stderr)
    except conductor.Refusal as refusal:
        refuse(f"{refusal} -- nothing recorded")
    return Launch.of(read, stop_of(conductor, meta, grammar, played))


def stop_of(conductor, meta: Path, grammar: str, played: subprocess.CompletedProcess) -> Stop | None:
    """-> the provider's stop the adapter of `grammar` reads in the launch's output -- a usage limit, its kind
    `quota`, recognised by the adapter alone --, None when it reads none or says it in another shape. Read at
    the adapter's own `answer`: the engine's face keeps its four keys."""
    try:
        said = conductor.adapters.load(grammar, meta).answer(str(played.stdout), str(played.stderr))
    except conductor.Refusal:
        return None
    return Stop.of(said)
