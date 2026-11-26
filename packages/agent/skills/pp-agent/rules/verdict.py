"""The verdict of an exchange: why it did not end well, its line and its fields."""
from __future__ import annotations

from model.exchange import Issue


def reason_of(key: str, issue: Issue, refusal: str | None) -> str | None:
    """-> why an exchange that kept a response did not end well -- the first that applies: the
    interruption, the harness's exit code, the run's cap reached, the launches spent, the passage not over
    (said with the last `refusal` the run's trace holds), the push that failed --; None when it ended well."""
    done, sent_back, stack = issue.account, issue.sent_back, issue.stack
    if issue.interrupted:
        return f"interrupted -- run {key} stands on `{stack}`: the next message, or `--run {key}`, takes it up"
    if done.harness_rc != 0:
        return f"harness rc {done.harness_rc}: {done.harness_stderr or 'nothing on stderr'}"
    if done.budget_spent:
        said = issue.budget
        return (f"budget-spent -- run {key} spent {said.spent:g} USD of its {said.cap:g} USD cap; the last response "
                f"is kept, the run stands on `{stack}`: raise the cap (`--max-budget-usd`, a `set`) and `--run {key}` "
                "takes it up")
    if done.spent:
        return (f"launches-spent -- run {key} played {issue.bound} launch(es) without its passage ending; the last "
                f"response is kept, the run stands on `{stack}`: `--run {key}` takes it up, `--launches` raises the bound")
    if not issue.arrived:
        why = f"; last refusal: {refusal}" if refusal is not None else ""
        return f"the passage is not over -- the run stands on `{stack}` (a step pends), the response recorded{why}"
    if sent_back is not None and not sent_back.pushed:
        return (f"push failed -- {sent_back.reason} -- the response is kept, the branch "
                f"{sent_back.branch} stays in {sent_back.path}: replay a wake-up once the repository answers.")
    return None


def verdict(name: str, key: str, issue: Issue) -> str:
    """-> the verdict line of an exchange, as stderr says it: the agent, the run, the exchange, its
    state, the harness's exit code, the cost, the launches, the strays, a standing run taken up, a
    wake-up after an interruption, the material's push; under a cap, what the run spent of it."""
    done, sent_back = issue.account, issue.sent_back
    cost, said = done.cost_usd, issue.budget
    branch = ""
    if sent_back is not None:
        branch = (f" · {sent_back.branch} {'pushed' if sent_back.pushed else 'push failed'}"
                  f" ({sent_back.commits} commit(s){', dirty' if sent_back.dirty else ''})")
    return (f"pp-agent: {name} · run {key} · exchange {issue.exchanges} · {issue.said} · harness rc {done.harness_rc}"
            + (f" · {cost:g} USD" if isinstance(cost, float) else "")
            + (f" · {said.spent:g}/{said.cap:g} USD cap" if said is not None else "") + f" · {done.launches} launch(es)"
            + (f" · {len(done.strays)} stray run(s)" if done.strays else "")
            + (" · standing resumed" if issue.standing else "")
            + (" · after an interruption" if issue.after else "") + branch)


def verdict_of(issue: Issue, reason: str | None) -> dict:
    """-> the fields of a `verdict` event: what the verdict line says, as data -- the state, the
    harness's exit code, the cost, the launches, the strays, a standing run taken up, whether a
    response was kept, the run's budget under a cap, and the reason when the exchange did not end well."""
    done = issue.account
    kept = issue.kept is not None
    state = issue.said if kept else ("interrupted" if issue.interrupted else "stopped")
    return {"exchange": issue.exchanges, "state": state, "harness_rc": done.harness_rc,
            "cost_usd": done.cost_usd, "launches": done.launches, "strays": len(done.strays),
            "standing_resumed": issue.standing, "kept": kept,
            "budget": issue.budget.json() if issue.budget is not None else None,
            **({"reason": reason} if reason else {})}
