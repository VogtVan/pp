"""The launch of a harness: its provider and its policy, the line composed, the environments,
the house's calls to the agent's conductor."""
from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

from acts.refusal import ruled
from model.policy import Asked, Policy
from rules.policy import asked_policy, grammar_of, launches_of, heartbeat_of, provider_of
from store.adapters import cost_scope
from store.houses import wired_of, engine_of
from store.locks import wake_log_of
from store.refusal import refuse

HOLD = "PP_HOLD_OUTPUT"                  # on this script's calls of an exchange that mounts vectors: the
                                         # message opens the exchange, the mounts are posed, the engine renders
                                         # nothing -- one bare call plays the exchange and renders it once
PROMPT_CAP = "PP_PROMPT_CAP"             # the cap of the outputs this script serves at the prompt, in characters, on its
                                         # own calls: what the adapter declares of the run's model (`launcher_cap`)
CONDUCTED_RUN = "PP_CONDUCTED_RUN"       # the run this launch conducts: on the CLI's environment, never this script's calls --
                                         # the engine tells the agent's calls from this script's by it


CREATE_NEW_PROCESS_GROUP = 0x00000200   # Windows' process creation flags, read on any system
CREATE_NO_WINDOW = 0x08000000


def unmeasured(conductor, root: Path, asked: Asked, policy: Policy) -> str | None:
    """-> the refusal of a cap the run cannot hold: `budget-unmeasured` when the policy carries a cap and
    the adapter of the run's grammar declares no scope of cost; None otherwise."""
    if policy.max_budget_usd is None:
        return None
    grammar = grammar_of(asked, ruled(provider_of, asked, wired_of(conductor, root))[1])
    try:
        if cost_scope(conductor, root, grammar) is not None:
            return None
    except conductor.Refusal as refusal:
        return str(refusal)
    return (f"budget-unmeasured -- the adapter of `{grammar}` declares no scope for the cost it reads (`COST` None): "
            "no cap can be held on its runs -- drop `--max-budget-usd`.")


def policy_of(conductor, asked: Asked) -> Policy:
    """-> the policy as the face judged it (`conductor.adapters.judged`): the flags given,
    typed and checked -- the policy that composes the line is the one the record keeps."""
    try:
        judged = conductor.adapters.judged(asked_policy(asked).json())
    except conductor.Refusal as refusal:
        refuse(str(refusal))
    return Policy.of(judged)


def bounds_of(asked: Asked) -> tuple[int, int]:
    """-> (the seconds without a step before a line says so, the launches one wake-up may play), as
    `--heartbeat` and `--launches` ask; a value neither reads is refused, the heartbeat's first."""
    return ruled(heartbeat_of, asked), ruled(launches_of, asked)


def set_policy(conductor, root: Path, asked: Asked, fields: dict) -> tuple[Asked, str | None]:
    """A `set` of a conversation's flow: the model, the budget, the permission regime or the effort
    of the NEXT launches, judged by the face with the rest of the policy before `asked` takes them.
    -> (what is asked from now on, None) when it holds, else (`asked` as it was, the code of its refusal):
    `provider-fixed` (a
    session belongs to its provider), `policy-unknown` or `policy-invalid` (the face's own),
    `budget-unmeasured` for a cap under an adapter whose cost has no scope (its `COST`), and
    `policy-unsupported` for a regime the run's provider does not spell (its adapter's `SPELLS`;
    a caller's command spells what it is given)."""
    if "provider" in fields:
        return asked, "provider-fixed"
    try:
        conductor.adapters.judged({**asked_policy(asked).json(), **fields})
    except conductor.Refusal as refusal:
        return asked, refusal.code
    if "max_budget_usd" in fields:
        refused = unmeasured(conductor, root, asked, Policy(max_budget_usd=fields["max_budget_usd"]))
        if refused is not None:
            return asked, refused.split(" ", 1)[0]
    if "permissions" in fields:
        provider = ruled(provider_of, asked, wired_of(conductor, root))[1]
        if provider is not None:
            try:
                spelled = getattr(conductor.adapters.load(provider, root), "SPELLS", ())
            except conductor.Refusal as refusal:
                return asked, refusal.code
            if "permissions" not in spelled:
                return asked, "policy-unsupported"
    return replace(asked, **fields), None


def compose(conductor, root: Path, meta: Path, head: list[str], provider: str | None,
            prompt: str, policy: Policy, session: str | None,
            workdir: dict | None = None) -> tuple[list[str], dict, str]:
    """-> (argv, env, stdin): the caller's command with the session in `PP_AGENT_SESSION`,
    or the line the provider's adapter composes -- the agent's marble, the house's wiring,
    the policy, the session opened (None) or resumed, the material --; `stdin` the prompt
    the process reads on its standard input, the material's head before it. A caller's
    command gets the material as the face composes it for a provider: the same head, the
    same `PP_WORKDIR` and `PP_CONSOLE` (`conductor.adapters.material`, `headed`,
    `console_of`)."""
    adapters = conductor.adapters
    try:
        if head:
            held = adapters.material(workdir)
            console = adapters.console_of(meta.parent)
            env = {"PP_AGENT_SESSION": session} if session else {}
            if held:
                env.update({"PP_WORKDIR": held["path"], "PP_CONSOLE": str(console)})
            return list(head), env, adapters.headed(prompt, held, console)
        return adapters.launch(provider, meta.parent, meta, prompt, marble=meta / ".sys" / "system.md",
                               wiring=root.parent, policy=policy.json() or None, session=session, workdir=workdir)
    except conductor.Refusal as refusal:
        refuse(str(refusal))
    return [], {}, ""


def principal_environment(door: str | None = None, documents: str | None = None,
                          marble: bool = False, cap: int | None = None, packages: str | None = None,
                          hold: bool = False) -> dict:
    """-> the environment of this script's OWN calls to the agent's conductor: the launcher's,
    without what a run of the house would name to it (`PP_RUN`, `PP_HOME`, a session, a root of
    documents, a composition) and the run a launch conducts (`PP_CONDUCTED_RUN`: this script's calls
    are the principal's) -- and, at an opening alone, the entry `--door` names, carried by `PP_DOOR`, the root `--documents` names,
    carried by `PP_DOCUMENTS`, and the composition the `--package` switches give, carried by
    `PP_PACKAGES` (`<name>=on|off`, joined by commas: the run's own switches before its first block
    is composed). `marble` is the RECEIPT the harness's launch declares (`PP_MARBLE`
    in the adapter's env): the standing orders ride the harness's own channel, so the conductor
    serves none in the block -- a caller's command (`--harness`) carries no marble and gets none. `cap`
    is the cap of the outputs served at the prompt (`launcher_cap`), carried by `PP_PROMPT_CAP`; None
    carries nothing and the engine's floor holds. `hold` asks the engine to render nothing at this call
    (`PP_HOLD_OUTPUT`): the message and the mounts of an exchange that mounts vectors, which the bare call
    that follows them renders once."""
    environment = {one: value for one, value in os.environ.items()
                   if one not in ("PP_RUN", "PP_HOME", "PP_AGENT_SESSION", "PP_DOOR", "PP_DOCUMENTS", "PP_PACKAGES",
                                  "PP_MARBLE", PROMPT_CAP, HOLD, CONDUCTED_RUN)}
    if hold:
        environment[HOLD] = "true"
    if cap:
        environment[PROMPT_CAP] = str(cap)
    if marble:
        environment["PP_MARBLE"] = "1"
    if door is not None:
        environment["PP_DOOR"] = door
    if documents is not None:
        environment["PP_DOCUMENTS"] = documents
    if packages is not None:
        environment["PP_PACKAGES"] = packages
    return environment


def harness_environment(env: dict, run: str = "") -> dict:
    """-> the environment of the CLI: the launcher's without `PP_RUN`, `PP_HOME`,
    `PP_AGENT_SESSION`, `PP_DOOR`, `PP_DOCUMENTS`, `PP_PACKAGES`; plus what the adapter adds (`PP_MARBLE`, the
    session, the material), and the KEY of the run this launch conducts (`PP_CONDUCTED_RUN`) --
    the one site that sets it: the agent's calls on that run are never the principal's, a `-new`
    the model plays inside it opens nothing, a `-new` of another conversation of the instance opens."""
    environment = {one: value for one, value in os.environ.items()
                   if one not in ("PP_RUN", "PP_HOME", "PP_AGENT_SESSION", "PP_DOOR", "PP_DOCUMENTS",
                                  "PP_PACKAGES", CONDUCTED_RUN)}
    if run:
        environment[CONDUCTED_RUN] = run
    environment.update(env)
    return environment


def conducted(conductor, root: Path, meta: Path, *args: str, door: str | None = None,
              documents: str | None = None, marble: bool = False, cap: int | None = None,
              packages: str | None = None, hold: bool = False) -> subprocess.CompletedProcess:
    """ONE call of this script to the agent's conductor, the principal's -- the house's
    engine on the agent's instance: `-new "<message>"` at an opening, `<key> "<message>"` at a
    passage's end, the bare `<key>` that serves what the run holds or makes it advance, `-peek` for the
    block that stands. The engine judges; this script reads what it printed. The engine reads no input on
    these calls: it gets none -- a Python child that inherits a pipe its parent reads freezes under Windows
    (CPython gh-78961), and a conversation reads its commands on that pipe."""
    return subprocess.run([sys.executable, str(engine_of(conductor, root)), "--instance", str(meta), *args],
                          stdin=subprocess.DEVNULL, capture_output=True, text=True,
                          env=principal_environment(door, documents, marble, cap, packages, hold))


def principal_line(conductor, root: Path, meta: Path, *args: str, door: str | None = None,
                   documents: str | None = None, marble: bool = False, cap: int | None = None,
                   packages: str | None = None, hold: bool = False) -> str:
    """-> the principal's call as `--dry-run` says it: the receipt, the cap, the door, the root and
    the composition when carried, the line."""
    return (("PP_MARBLE=1 " if marble else "") + (f"{PROMPT_CAP}={cap} " if cap else "")
            + (f"PP_DOOR={door} " if door is not None else "")
            + (f"PP_DOCUMENTS={shlex.quote(documents)} " if documents is not None else "")
            + (f"PP_PACKAGES={packages} " if packages is not None else "")
            + (f"{HOLD}=true " if hold else "")
            + shlex.join([sys.executable, str(engine_of(conductor, root)), "--instance", str(meta), *args]))


def apart(system: str = os.name) -> dict:
    """-> the arguments that start a process detached from the caller: under Windows a console of its own that
    no window shows, in a process group of its own -- closing the operator's window ends nothing; elsewhere a
    session of its own."""
    if system == "nt":
        return {"creationflags": CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP}
    return {"start_new_session": True}


def reported(lock, meta: Path, key: str) -> None:
    """The detached child's REPORT: one JSON line `{key, pid}` on stdout, the parent's
    answer; then stdout goes to nowhere and stderr to the wake log -- the parent is gone."""
    print(json.dumps({"key": key, "pid": os.getpid()}), flush=True)
    sys.stdout.flush()
    sys.stderr.flush()
    quiet = os.open(os.devnull, os.O_WRONLY)
    log = os.open(wake_log_of(lock, meta, key), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    os.dup2(quiet, 1)
    os.dup2(log, 2)
    os.close(quiet)
    os.close(log)


def on_end(command: str, root: Path, name: str, key: str | None, state: str) -> None:
    """Plays the caller's `--on-end` command by the shell, once the wake lock is released and
    the records written: `PP_AGENT_NAME`, `PP_AGENT_RUN` and `PP_AGENT_STATE` in its
    environment, its exit code said on stderr -- never the wake-up's own. The shell is the system's: `sh`
    under POSIX, `cmd.exe` under Windows. The command is the caller's, and so is its input: it inherits it."""
    environment = {**os.environ, "PP_AGENT_NAME": name, "PP_AGENT_RUN": key or "", "PP_AGENT_STATE": state}
    played = subprocess.run(command, shell=True, cwd=str(root.parent), env=environment, stdin=None)
    print(f"pp-agent: on-end rc {played.returncode}", file=sys.stderr)
