"""The `tick` domain, layer `faces`: how a tick speaks to the member it wakes.

A definition belongs here when it composes the head of the message a woken member reads -- who it is, what it owes, what
came for it, what it may still do -- and gives it back without printing it.
"""
from __future__ import annotations

from tick.model import BEAT, CLOSED_HEAD, CYCLED, IDENTITY, NOTHING_NEW, RELANCED, STOPPED_HEAD
from task.rules import is_open, owes
from wake.faces import message_of
from health.faces import health_lines


def headed(team: str, agent: str, box: list[dict], history: str = "", state: dict | None = None,
           relance: tuple[str, str | None] | None = None, task: str | None = None, continued: bool = False,
           beat: int | None = None) -> str:
    """-> the HEAD of a launch, what the tick writes before pp's output in the prompt. A WAKE-UP alone says what
    holds for its whole passage: its first line, who is launched (`IDENTITY`); for a NEW run of a member that had
    one, the history of its open tasks; for a RELANCE, the line that says why the member is launched -- `RELANCED`,
    or, in a cycle of waits, `CYCLED` naming the member it waits on: an answer or an info asked --; and the BEAT
    (`BEAT`: the exchanges left to say an act on the task, this one counted) of a member that owes there. EVERY
    head, a CONTINUATION's (`continued`) included, says what varies: the HEALTH VIEW while another member is
    suspected, one line each (`[not answering at the moment: <member> -- tried again at HH:MM]`); then the inbox --
    what arrived for the member since its last launch, each message its head line and its text under it
    (`message_of`), a relance's the members' infos that waited --, or `[nothing new]` when a standing run is
    relaunched with nothing to deliver -- `CLOSED_HEAD` when its task is resolved: no act is awaited, one said
    reaches its author as a second answer does --; a `stop` at the head of a run standing on the stopped task opens
    on `STOPPED_HEAD`: the run says no act and parks; then the messages delivered at an earlier launch that the
    member still owes an answer on the TASK of the launch (every open task when none is named), under `[you still
    owe an answer to]`. Nothing else -- what the others answered is read on demand (`team responses`) --: the
    contract of the acts is the body of the team's document, served by pp at the start of the member's exchange,
    and the team's intention is never in the message: pp serves it from `TEAM.md` (`team_document`)."""
    typed = state                                  # the state read, or None: the empty state below stands for it
    state = state if state is not None else {"messages": {}, "debts": {}, "tasks": {}, "started": None}
    messages, delivered, tasks = ((typed.task.messages, typed.task.delivered, typed.task.tasks) if typed is not None
                                  else ({}, (), {}))
    health = health_lines(typed, agent) if typed is not None else ""
    shown = {one.id for one in box}
    lines = [message_of(state, agent, one) for one in box]
    still = [message_of(state, agent, one) for key, one in sorted(messages.items())
             if key not in shown and one.body.to == agent and owes(state, key) and key in delivered
             and is_open(state, one.body.task) and (task is None or one.body.task == task)]
    first = "" if continued else IDENTITY.format(team=team, member=agent) + "\n\n"
    told = history + "\n\n" if history and not continued else ""
    left = BEAT.format(left=beat, task=task) + "\n\n" if beat is not None and not continued else ""
    if relance is not None and not continued:
        why = RELANCED if relance[1] is None else CYCLED.format(member=relance[1])
        inboxed = why + "\n\n" + left + ("[inbox]\n" + "\n".join(lines) + "\n\n" if lines else "")
    elif lines:
        inboxed = left + "[inbox]\n" + "\n".join(lines) + "\n\n"
        if any(one.body.verb == "stop" for one in box):        # a run standing on a stopped task: its last launch
            inboxed = STOPPED_HEAD + "\n\n" + inboxed
    elif tasks.get(task) is not None and tasks[task].state == "resolved":   # a run standing on a closed task, continued
        inboxed = CLOSED_HEAD + "\n\n"
    else:
        inboxed = left + NOTHING_NEW + "\n\n"
    return (first + (health + "\n\n" if health else "") + told + inboxed
            + ("[you still owe an answer to]\n" + "\n".join(still) + "\n\n" if still else "")).rstrip("\n") + "\n"
