"""What the verbs that talk to an agent say: the response a wake-up kept, a space opened or closed on a run, what a
conversation says of an exchange that did not end well, the outcome of a wake-up read after it, the
report of a wake-up launched apart."""
from __future__ import annotations

from model.exchange import Response


def kept_object(kept: Response, session: str, state: str) -> dict:
    """-> the response a wake-up kept as `run --json` says it: its record's line, then its `session` and the
    `state` the exchange ended in."""
    return {**kept.json(), "session": session, "state": state}


def spaced_object(key: str, spaces: dict | None, state: str, launches: int, cost: float | None) -> dict:
    """-> a space opened or closed as `open --json` and `close --json` say it: the run under `key` and `run`, the
    `spaces` its last block said -- none open and none openable without one --, its `state`, the launches and the
    cost of the wake-up -- `run` and `launches` as a response's record says them: a reader of records counts this
    wake-up as one of `run`'s."""
    return {"key": key, "run": key, "spaces": spaces or {"open": [], "openable": []}, "state": state,
            "launches": launches, "cost_usd": cost}


def spaced_line(name: str, key: str, space: str | None, spaces: dict | None, state: str) -> str:
    """-> a space opened or closed as `open` and `close` say it: the run, the `space` opened (None: closed), the
    spaces open after it, the run's `state`."""
    found = spaces or {"open": [], "openable": []}
    return (f"pp-agent: {name} · run {key} · {'opened ' + str(space) if space is not None else 'closed'} · open: "
            f"{', '.join(found['open']) or '—'} · {state}")


def told_line(reason: str) -> str:
    """-> what a conversation says on stderr of an exchange that kept nothing, or did not end well: its reason."""
    return f"pp-agent: {reason}"


def started_object(key, pid) -> dict:
    """-> what `start` says once its child reported: the `key` of the run and the `pid` of the wake-up."""
    return {"key": key, "pid": pid}


def logged_lines(tail: list[str]) -> list[str]:
    """-> the last lines of a wake-up's log as `wait` and `result` say them on stderr before `wake-dead`."""
    return [f"  {one}" for one in tail]


def outcome_line(name: str, key: str, exchanges: int, said: str, kept: Response) -> str:
    """-> the outcome of a wake-up as `wait` and `result` say it on stderr: the agent, the run, its exchanges,
    how the last one ended (`said`), the harness's exit code, the cost and the launches of the response `kept`."""
    cost, launches = kept.cost_usd, kept.launches
    return (f"pp-agent: {name} · run {key} · exchange {exchanges} · {said} · harness rc {kept.harness_rc}"
            + (f" · {cost:g} USD" if isinstance(cost, float) else "")
            + (f" · {launches} launch(es)" if isinstance(launches, int) else ""))
