"""What the readings show of an agent's runs: each run with its state, its context reduced, the weights summed,
each message with its response."""
from __future__ import annotations

from model.cost import Budget, Context, Cumuls
from model.exchange import Message, Response
from model.policy import Policy
from model.run import Session


def context_seen(full: Context | None) -> dict | None:
    """-> the run's context as `status --json` says it, reduced to what a table shows: `tokens` (the
    context now), `used`, `pp` (pp's share of the context), `over` (pp's part past the context: then no share),
    `estimated`; None without a flow."""
    if full is None:
        return None
    return {"tokens": full.tokens, "used": full.used, "pp": full.pp.share, "over": full.pp.over,
            "estimated": full.estimated}


def no_run(name: str) -> str:
    """-> what `status` says of an agent without a run."""
    return f"pp-agent: {name} -- no run yet."


def run_object(name: str, key: str, named: str, exchanges: int, state: str, awaits: str, stack: str,
               spaces: dict | None, known: Session | None, cumuls: Cumuls, policy: Policy, budget: Budget | None,
               context: Context | None, packages: list[dict] | None, weight: dict, documents: str | None) -> dict:
    """-> one run as `status --json` says it: the state that prevails, what its stack AWAITS (`message`: the
    passage is over; `production`: a step pends -- said whatever prevails, running or dead), the name, the records
    summed, its policy, its budget under a cap, its context reduced, its packages as it plays them (None without a
    slot), its root of documents -- the absolute path its slot keeps, None for a run opened with none or no slot."""
    return {"agent": name, "run": key, "name": named, "exchanges": exchanges,
            "state": state, "awaits": awaits, "stack": stack, "spaces": spaces,
            "session": known.session if known is not None else None,
            "provider": (known.provider or "harness") if known is not None else None,
            **cumuls.json(), "policy": policy.json(),
            "budget": budget.json() if budget is not None else None, "context": context_seen(context),
            "packages": packages, "weight": weight, "documents": documents}


def run_line(key: str, exchanges: int, state: str, resting: str, stack: str, known: Session | None) -> str:
    """-> one run as `status` says it: its exchanges, where it rests -- parked, or standing on its `stack` --
    under the `state` that prevails, a wake-up that plays or one that ended without its response, and the
    session it lives in."""
    where = "parked" if resting == "parked" else f"standing on {stack or 'its block'}"
    if state == "running":
        where = f"running (a wake-up plays) -- {where}"
    elif state == "dead":
        where = f"dead (a wake-up ended without its response) -- {where}"
    held = (f"session {known.session} ({known.provider or 'harness'})" if known is not None else "no session")
    return f"run {key} · {exchanges} exchange(s) · {where} · {held}"


def unopened_line(key: str, state: str) -> str:
    """-> a launch whose agent opened no run, as `status` says it: a wake-up that plays, or one that ended
    without its response."""
    said = ("running (a wake-up plays, no run opened yet)" if state == "running"
            else "dead (a wake-up ended without its response)")
    return f"run {key} · 0 exchange(s) · {said} · no session"


def status_object(name: str, wired: list[str], last: tuple[str | None, Policy] | None, weight: dict,
                  packages: list[dict]) -> dict:
    """-> the agent as the last object of `status --json` says it: the providers the house is wired with, what
    its `last` run played -- `{provider, policy}`, null when no message was ever sent to it --, the weight of its
    runs summed, the packages its instance pins."""
    return {"agent": name, "providers": list(wired),
            "last": {"provider": last[0], "policy": last[1].json()} if last is not None else None,
            "weight": weight, "packages": packages}


def status_lines(responses: int, wired: list[str]) -> list[str]:
    """-> the two lines `status` ends on: the agent's responses, the providers the house is wired with."""
    return [f"{responses} response(s)", f"providers: {', '.join(wired) if wired else '—'}"]


def weight_sum(weights: list[dict]) -> dict:
    """-> the sum of runs' weights; `flow` null when none of them keeps a flow."""
    flows = [one["flow"] for one in weights if one["flow"] is not None]
    return {"lines": sum(one["lines"] for one in weights), "files": sum(one["files"] for one in weights),
            "bytes": sum(one["bytes"] for one in weights), "flow": sum(flows) if flows else None}


def paired(sent: list[Message], answered: list[Response]) -> dict[int, Response]:
    """-> {the rank of a message (from 1): the response that answers it}. A response answers the LAST
    message of the run sent at its hour or before; two responses never take one message and both
    records keep their order -- a response that shares the second of the next message stays at its own
    message when the response after it would otherwise have none. An exchange that kept nothing leaves
    its message unanswered. Records the hour cannot order (a response older than every message) pair by
    rank."""
    hours = [str(one.at or "") for one in sent]
    ranks: list[int] = []
    rank = len(sent)                               # from the last response back: below the next one's message
    for one in reversed(answered):
        hour = str(one.at or "")
        rank -= 1
        while rank >= 0 and hours[rank] > hour:
            rank -= 1
        if rank < 0:
            return {number: one for number, one in enumerate(answered[:len(sent)], 1)}
        ranks.append(rank)
    return {rank + 1: one for rank, one in zip(reversed(ranks), answered)}
