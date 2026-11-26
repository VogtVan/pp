"""The resume of a run: what it was, the session it reopens, its material, its root of documents."""
from __future__ import annotations

from dataclasses import replace

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
