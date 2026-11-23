"""What an exchange's prompt and response are made of: the heads, what pp asks, the words kept."""
from __future__ import annotations

import re
import shlex

from model.exchange import Response, Said
from model.material import Workdir
from model.run import Traced
from model.words import HEAD

INTERRUPTED = "[interrupted by your principal]"   # before HEAD, in the wake-up after an interrupted one


def composed(words: tuple[Said, ...]) -> str | None:
    """-> the RESPONSE of an exchange: the texts of its `words` -- the productions pp took, and they alone --, in
    their order, joined by a blank line; a blank one dropped -- nothing added, nothing folded: a text the model
    handed twice stays twice. None when pp took nothing."""
    texts = [str(one.text or "").strip() for one in words]
    return "\n\n".join(one for one in texts if one) or None


def spoke(kept: Response) -> bool:
    """-> whether the model said something in an exchange: a production pp took, or a last message of a launch
    with characters -- the hand-back mark alone says nothing."""
    return kept.response is not None or any(one is not None and one.chars for one in kept.finals or ())


def pp_called(shell: str | None, console: str) -> bool:
    """-> whether a command calls the agent's console: its first word `./pp`, or the console by its
    absolute path."""
    try:
        words = shlex.split(shell or "")
    except ValueError:
        words = (shell or "").split()
    return bool(words) and words[0] in ("./pp", console)


def packages_line(waiting: dict) -> str | None:
    """-> what an opening carries as `PP_PACKAGES`: every switch of the waiting list, `<name>=on|off` joined by
    commas, in the order they came; None when nothing waits."""
    if not waiting:
        return None
    return ",".join(f"{name}={'on' if on else 'off'}" for name, (on, _) in waiting.items())


def message_head(after: bool) -> str:
    """-> the head the message opens under in the first prompt of a wake-up: the principal's,
    preceded by the interruption's when the run's last wake-up was interrupted."""
    return f"{INTERRUPTED}\n{HEAD}" if after else HEAD


def served_of(kept: list[Traced] | None, output: str) -> dict:
    """-> what a `conduction` says of the output it carries: `chars`, its length; with the trace's
    events since the conduction before (`kept`, None when no trace is followed), `blocks` --
    `{stack, command, wait}` of each block the engine rendered, the outputs held for this launch
    or the one it advanced to -- and `left` when the output is a piece of a cut one, the characters
    still to come."""
    if kept is None:
        return {"chars": len(output)}
    pieces = [one for one in kept if one.kind in ("cut", "chunk")]
    return {"chars": len(output),
            "blocks": [{"stack": one.stack, "command": one.command, "wait": one.wait}
                       for one in kept if one.kind == "block"],
            **({"left": int(pieces[-1].left or 0)} if pieces else {})}


ASKING = re.compile(r"^(WORK|INFER|PICK)\b.* => ", re.M)   # an instruction line: a step the agent plays


def asks(output: str) -> bool:
    """-> whether pp's output ASKS the agent something: an instruction line stands in it -- a step
    to play, whatever its channel. An order block alone (a bare AWAIT, a CONTINUE closing a reading)
    carries none."""
    return ASKING.search(output) is not None


def headed(prompt: str, neighbours: list[tuple[str, str, str]]) -> str:
    """-> the prompt with the neighbours line at its head -- `[runs under way: <key> since
    HH:MM « head » · …]`, a blank line, the message -- or the prompt alone when no other
    run of the agent plays."""
    if not neighbours:
        return prompt
    line = " · ".join(f"{key} since {since} « {head} »" for key, since, head in neighbours)
    return f"[runs under way: {line}]\n\n{prompt}"


def material_of(entry: Workdir) -> dict:
    """-> what the face takes: the path under the workspace, the branch, the base."""
    return {"path": entry.path, "branch": entry.branch, "base": entry.base}


def identity_of(name: str, slug: str) -> dict:
    """-> the git identity of the exchange, in the harness's environment: the agent's path,
    its address at the house (`rep1/ag1` -> `rep1.ag1@<slug>`)."""
    email = f"{name.replace('/', '.')}@{slug or 'house'}"
    return {"GIT_AUTHOR_NAME": name, "GIT_AUTHOR_EMAIL": email,
            "GIT_COMMITTER_NAME": name, "GIT_COMMITTER_EMAIL": email}
