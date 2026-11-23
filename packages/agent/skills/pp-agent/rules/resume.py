"""The resume of a run -- what it was, the session it reopens, its material, its root of documents -- and the
verdict of an exchange: why it did not end well, its line and its fields."""
from __future__ import annotations

from dataclasses import replace

from model.exchange import Issue
from model.policy import Asked, Policy
from model.material import Workdir
from model.refusal import Refusal, WorkFailure
from model.run import Session
from model.words import SESSIONS


def resumable(key: str, where: str, stands: bool, known: Session | None, provider: str | None) -> str:
    """-> the session a resume reopens: the run `stands` at the agent `where` (`run-unknown` otherwise), its
    session is recorded (`session-missing` otherwise -- nothing is launched), under the provider it was opened
    with (`provider-mismatch`; None is a caller's command)."""
    if not stands:
        raise Refusal(f"run-unknown -- no run `{key}` at {where}.")
    if known is None:
        raise Refusal(f"session-missing -- run {key} has no session recorded at {SESSIONS}: it is never "
                      "launched without one; `--new` opens another run.")
    if known.provider != provider:
        raise Refusal(f"provider-mismatch -- run {key} lives in a session of "
                      f"{known.provider or 'a caller command'}, not of {provider or 'a caller command'}.")
    return str(known.session)


def resumed_of(key: str | None, asked: Asked, known: Session | None, wired: list[str], policy: Policy) -> Asked:
    """-> the call's flags, completed on a resume by what the RUN was: the provider of its session (`known`)
    when neither `--provider` nor `--harness` is given, and each key of its last `policy` (the
    `policy` of its last line at `messages.jsonl`) the call does not give (`Asked.resumed`). A flag of the call
    always prevails. A run opened under a caller's command cannot be relaunched without it
    (`harness-required`); a provider the house is no longer `wired` with refuses
    (`provider-unwired`). No session recorded: the flags as given (`resumable` says
    `session-missing`)."""
    if known is None:
        return asked
    if asked.harness is None and asked.provider is None:
        recorded = known.provider
        if not recorded:
            raise Refusal(f"harness-required -- run {key} lives in the session of a caller's command: "
                          "resume it with that command, `--harness <command>`.")
        if recorded not in wired:
            raise Refusal(f"provider-unwired -- run {key} lives in a session of {recorded}, and the house is wired "
                          f"with {', '.join(wired) or 'no adapter'}.")
        asked = replace(asked, provider=recorded)
    return asked.resumed(policy)


def documents_judged(key: str | None, held: str, other: bool) -> None:
    """Refuses `documents-fixed` before anything is launched when a resume names a root `other` than the
    one its run was opened with (`held`): a run keeps the composition it opened."""
    if other:
        raise Refusal(f"documents-fixed -- run {key} keeps the root of documents it opened with "
                      f"({held or 'none'}): another root opens another run.")


def standing_material(name: str, key: str, entry: Workdir | None, stands: bool) -> Workdir | None:
    """-> the run's material as recorded (`entry`), None when it has none; `workdir-missing` when the
    clone is gone (it `stands` no more) or was pruned: a run is never resumed without its material."""
    if entry is None:
        return None
    if entry.state == "pruned":
        raise WorkFailure(f"workdir-missing -- the material of run {key} ({entry.path}) was pruned: a run is "
                          "never resumed without its material; a new run clones again.")
    if not stands:
        raise WorkFailure(f"workdir-missing -- the material of run {key} ({entry.path}) is gone: "
                          f"`agent prune {name} {key} --force` forgets it, a new run clones again.")
    return entry


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
