"""The `wake` domain, layer `rules`: what the team's state says of its wake-ups, and what a wake-up writes.

A definition belongs here when it computes its answer from the state and the values it is given: the run that
carries a task, the intents still open, whether a member is busy, the flags a launch takes, what a member was told
since its last wake-up, a quota and when it lifts, the runs of a member. It also holds the DECISIONS of the wake-ups,
which compose by `made` and `but` the bodies an act writes: what a launch's words write, routed or refused; the end,
the failure, the halt, the refused vector or the renewed run of a wake-up; which launches `stop --kill` ends, and
the `wake-killed` of those it ended; the provider's limit lifted, judged in two steps around the hour; a launch the
journal did not know, a launch that answered on a task stopped, a launcher ended with its process space; a run
reset. A decision that refuses DECLINES by a code, and the act or the verb says the sentence. It also holds a question
a wake-up's rule asks of a later domain's matter -- whether a member is suspected --, because a rule reads no domain
that follows its own. It reads no disk, no clock and no environment and prints nothing: the time and what an effect
gave come to it as values, never as a function to call -- the act reads between two decisions --, and what needs the
system belongs to `store` or to an act.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta

from declaration.model import DEFAULT_SCHEDULE
from house.model import Declined
from task.model import Post, Refused
from wake.model import (DEFAULT_RETRIES, DEFAULT_SUSPECT_MAX, HALT_AFTER, HARNESS_SPARED, RUN_NAME_CHARS, QuotaLifted,
                        QuotaReached, RunRenewed, RunReset, WakeEnded, WakeFailed, WakeHalted, WakeKilled, WakeLaunched,
                        WakeRefused, WakeRouted)
from season.rules import is_member, launch_kept, path_of, schedule_seconds
from task.rules import (act_formed, is_root, opening_of, owed_by, owes, principal_of, routed,
                        told_of)


def path_of_intent(state: dict, intent: dict) -> str:
    """-> the path of the agent a wake-up woke: the `path` its intent carries, else its
    member's path."""
    return str((intent.body.path if intent is not None else None)            # no intent: its member's path, none
               or path_of(state, intent.body.agent if intent is not None else None))


def carrier_of(state: dict, task: str | None) -> str | None:
    """-> the CARRIER of a task, what a member's run is kept by: an occurrence's recurrence, a ring's
    ceremony, any other task itself."""
    held = state.task.tasks.get(task)
    return task if held is None else held.recurrence or held.ceremony or task


def run_held(state: dict, member: str, task: str | None) -> str | None:
    """-> the run the member holds for the task's carrier, None before its first wake-up there."""
    return (state.wake.runs.get(member) or {}).get(carrier_of(state, task))


def carrier_name(state: dict, team: str, carrier: str) -> str:
    """-> the name a run of the carrier carries: a recurrence's name, else `<team> R<n>`; a task's name, else
    `<team> T<n>`; a ceremony's; cut at the run name's bound."""
    recurrence = state.rhythm.recurrences.get(carrier)
    task = state.task.tasks.get(carrier)
    if recurrence is not None:
        text = recurrence.name or f"{team} {carrier}"
    elif task is not None:
        text = task.name or f"{team} {carrier}"
    else:
        text = carrier
    return " ".join(str(text).split())[:RUN_NAME_CHARS].strip()


def open_intents(state: dict) -> list[dict]:
    """-> the intents without an end: the wake-ups under way, in the journal's order."""
    return [one for tag, one in state.wake.intents.items() if tag not in state.wake.ended]


def played(state: dict) -> list[dict]:
    """-> the wake-ups a face says are under way: the intents without an end, less the ones `faced` proved gone."""
    gone = state.wake.gone or ()
    return [one for one in open_intents(state) if str(one.body.tag) not in gone]


def busy(state: dict, member: str) -> bool:
    """-> whether a wake-up of the member is under way: an intent of its without an end, whatever
    its task -- a member plays one wake-up at a time, in its one run."""
    return any(one.body.agent == member and tag not in state.wake.ended for tag, one in state.wake.intents.items())


def suspicion_of(state: dict, member: str) -> dict | None:
    """-> the member's SUSPICION (the failure detector ◇P, Chandra and Toueg 1996), read from the journal alone:
    `{falls, until}` while a final failure of its stands -- its INTERVAL runs from the hour of the last one for the
    base of the team's net in seconds (`schedule:`, DEFAULT_SCHEDULE without it or under `off`) doubled at each
    final failure in a row and never above `suspect-max:` (DEFAULT_SUSPECT_MAX without it), `until` the local hour
    it ends --, None for a member not suspected."""
    health = state.health.health.get(member) or {}
    falls = int(health.get("falls") or 0)
    if not falls or not health.get("at"):
        return None
    base = schedule_seconds(state.season.started) or DEFAULT_SCHEDULE
    bound = int(state.season.limits.get("suspect-max") or DEFAULT_SUSPECT_MAX)
    at = datetime.fromisoformat(str(health["at"])).astimezone().replace(tzinfo=None)
    return {"falls": falls, "until": at + timedelta(seconds=min(base * 2 ** (falls - 1), bound))}


# --- the tick: one advance of the team ------------------------------------------------------

def launch_flags(launch: dict) -> list[str]:
    """-> the flags `agent start` gets from what `team start` kept: the harness or the
    provider, the model, the budget, the permission regime, the model's effort. A wake-up is ONE
    launch: `--launches 1` rides every call, never a flag of the start."""
    found: list[str] = []
    for key, flag in (("harness", "--harness"), ("provider", "--provider"), ("model", "--model"),
                      ("max_budget_usd", "--max-budget-usd"), ("permissions", "--permissions"),
                      ("effort", "--effort")):
        if launch.get(key) is not None:
            found += [flag, str(launch[key])]
    return found + ["--launches", "1"]


def cursor_of(state: dict, agent: str, run: str | None, before: int) -> int:
    """-> the RUN's cursor in the team: the id of the last `wake-intent` of that run before the
    one being written (`before`) -- an intent that resumed it, or the one that opened it --, or
    the `team-started` for a new run: a new session knows nothing. The cursor is the journal's:
    nothing is written to share."""
    mine = [int(one.id or 0) for tag, one in state.wake.intents.items()
            if run is not None and one.body.agent == agent and int(one.id or 0) < before
            and (one.body.run == run or launched_run(state, tag) == run)]
    started = state.season.started
    return max(mine or [int((started.id if started is not None else None) or 0)])


def shared(state: dict, agent: str, cursor: int) -> list[dict]:
    """-> the `wake-ended` events of OTHER agents after the cursor: the responses new to the
    agent, in the journal's order."""
    return [one for one in state.wake.ends if int(one.id or 0) > cursor and one.body.agent != agent]


def spent_on(state: dict, run: str) -> float:
    """-> what the run spent in the team's wake-ups, as the journal charged them: the sum of the costs
    of its ends and failures -- what `agent start --max-budget-usd` gets added to a wake-up's share."""
    return round(sum(float(one.body.cost or 0) for one in state.wake.ends + state.wake.fails
                     if one.body.run == run), 6)


def opened_by(one: dict, tag: str) -> bool:
    """-> whether a line of a flow OPENS the launch's own exchange: an `opened` carrying the tag the tick handed
    `agent start` (agent 0.31.1) -- what the reader starts at, never a kept rank alone; an `opened` of another
    exchange (a chat, a launch of before) closes what is read."""
    return one.get("kind") == "opened" and str(one.get("tag") or "") == tag


def measured_of(one: dict) -> dict:
    """-> a flow's `context` object as the journal keeps it, `{tokens, used, window}` as the house said them."""
    return {key: one.get(key) for key in ("tokens", "used", "window")}


def failed(state: dict, intent: dict, reason: str, cost=None, run: str | None = None,
           extra: dict | None = None, forced: bool = False) -> list[dict]:
    """-> the events a dead wake-up writes: `wake-failed` -- a retry left: its messages go back
    to the inbox (the replay discards them from the delivered); spent: `final`, and the tick ANSWERS
    in the member's place each message of the wake-up whose debt stands (`re`, `by: tick`, neither `suspected` nor
    `returned`, « the launch of <member> failed: <reason> »), which wakes their authors: a member's head
    shows the message whole (`message_of`), a principal reads the `re` in its box, without the message --
    never the opening a principal posted:
    the root's debt stays owed and the team tells its principal (a `notice` about the root). On a stopped task it is
    `final` at once and goes nowhere.
    A `launch-missing` -- a tick died between the intent and the spawn -- is never final and
    spends no retry: nothing was launched. A wake-up that answered before it failed carries the
    `cost` its answer reported, and the `run` that answered when the answer was conducted -- or the run the
    face knows the state of (`state`, read at agent's face: `standing` or `parked`): that run
    stays the member's, and the retry resumes it. `extra` joins the event's fields (the rank of the flow
    read). A member that repented is
    tolerated one silent retry more per repentance; a SUSPECTED member's failure -- its try -- is final at once;
    `forced` makes it final at once whatever the retries (a launch the launcher refused its vectors). The same failure
    HALT_AFTER times in a row on the task halts the member there (`halting`)."""
    agent, task = intent.body.agent, intent.body.task
    held = state.task.tasks.get(task)
    stopped = held is not None and held.state == "stopped"
    retries = (state.season.limits.get("retries", DEFAULT_RETRIES)
               + int((state.health.health.get(agent) or {}).get("repents") or 0))
    final = stopped or forced or (reason != "launch-missing" and (suspicion_of(state, agent) is not None
                                                        or state.wake.failures.get((agent, task), 0) >= retries))
    first = WakeFailed.made(tag=intent.body.tag, agent=agent, task=task, final=final, reason=reason)
    if isinstance(cost, (int, float)) and not isinstance(cost, bool):
        first = first.but(cost=cost)
    if run:
        first = first.but(run=run)
    events: list = [first.but(**{key: value for key, value in (extra or {}).items() if value is not None})]
    if not stopped:
        events += halting(state, intent, reason)
    if final and not stopped:
        said = f"the launch of {agent} failed: {reason}"
        for key in intent.body.messages or []:
            message = state.task.messages.get(key)
            on = message.body.task if message is not None else None
            author = message.body.sender if message is not None else None
            if not owes(state, key) or (key == opening_of(state, on) and not is_member(state, author)):
                continue
            events.append(Post.made(task=on, sender=agent, to=author, verb="re", re=key, text=said,
                                    by="tick"))
        if is_root(state, agent, task):
            started = state.season.started
            events.append(Post.made(task=task, sender=started.team if started is not None else None,
                                    to=told_of(state, agent, task), verb="notice", about=agent, text=said))
    return events


def vectors_of(state: dict, agent: str, task: str) -> list[str]:
    """-> the VECTORS a run of the member carries on the task, each once in its order: the task's own (`post
    --vector`), then the one of the LAST `do` to the member on that task that carries one -- a later `do`'s vector
    replaces an earlier one's: a corrected node. What each launch of that run passes to the launcher, `--vector
    <v>`. Opaque: the team reads no family, no id."""
    held = state.task.tasks.get(task)
    found = list((held.vectors if held is not None else None) or [])
    last = None
    for one in state.task.messages.values():
        if one.body.task == task and one.body.verb == "do" and one.body.to == agent and one.body.vector:
            last = str(one.body.vector)
    return list(dict.fromkeys(found + ([last] if last else [])))


def vector_refused(state: dict, intent: dict, why: str, vectors: list[str]) -> list[dict]:
    """-> the events a launch carrying VECTORS writes when the launcher refuses a vector -- rc 2 under the code
    `vector-refused` (`VECTOR_REFUSED`); any other refusal is the house's (`house_failed`) --: the node cannot be
    played, a retry would meet the same refusal -- the failure is FINAL at once and said to the task as a
    failed wake-up says it (`failed`: each `do` of the launch answered by the tick, the root's principal told),
    `house: true` (the member did nothing: no suspicion), the vectors on the event; never launched again on it."""
    said = " ".join(why.split())
    return failed(state, intent, f"launch-refused: {said}", forced=True, extra={"house": True, "vectors": vectors})


def house_failed(state: dict, name: str, intent: dict, why: str) -> list[dict]:
    """-> the events a launch the HOUSE refused writes: `agent start` ended before any harness, without its report
    (a package the agent does not pin, a run held, a session missing, a provider unwired). `wake-failed {reason:
    launch-failed: <why>, house: true}`, never final: no retry spent, no fall, no suspicion -- the member did
    nothing --, its messages back in its inbox, so that the next tick launches it again; and ONE notice of the
    team to the owner per (member, cause) since the season began (`house: true`, no `about`: it holds no wait); the
    same refusal HALT_AFTER times in a row on the task halts the member there (`halting`)."""
    said = " ".join(why.split())
    events: list = [WakeFailed.made(tag=intent.body.tag, agent=intent.body.agent, task=intent.body.task, final=False,
                                    reason=f"launch-failed: {said}", house=True)]
    told = f"the house could not launch {intent.body.agent}: {said}"
    started = state.season.started
    since = int((started.id if started is not None else None) or 0)
    if not any(one.body.house and one.body.verb == "notice" and one.body.text == told and one.id > since
               for one in state.task.messages.values()):
        events.append(Post.made(task=intent.body.task, sender=name,
                                to=str(started.body.owner if started is not None else None),
                                verb="notice", house=True, text=told))
    return events + halting(state, intent, events[0].reason)


def failure_identity(reason) -> str:
    """-> a failure's reason as the guard compares it: its CODED prefix alone, never what a harness or a house said --
    `harness-error: <error>`, the error cut at its first colon (`harness rc <n>` for an exit without an error of its
    own); `launch-failed: <code>` and `launch-refused: <code>`, the refusal's code; `wake-dead`, `wake-timeout` and
    any reason without a colon as they are."""
    said = " ".join(str(reason or "").split())
    head, colon, rest = said.partition(": ")
    if not colon:
        return head
    if head == "harness-error":
        return f"{head}: {rest.split(':', 1)[0].strip()}"
    coded = re.match(r"(?:[\w.-]+: )?([A-Za-z]\w*(?:-[a-z0-9]+)*)", rest)
    return f"{head}: {coded.group(1) if coded else ''}"


def owed_free(state: dict, member: str) -> list[int]:
    """-> the debts of the member (`owed_by`) on the tasks that do not halt it (`halted_of`): what a relance or a try
    carries."""
    return [key for key in owed_by(state, member)
            if halted_of(state, member, state.task.messages[key].body.task) is None]


def halted_of(state: dict, agent: str, task: str | None) -> dict | None:
    """-> the `wake-halted` that holds the member on the task, None when nothing holds it there."""
    return next((one for one in state.wake.halts if one.body.agent == agent and one.body.task == task), None)


def wake_of(state: dict, tag) -> tuple | None:
    """-> (member, task) of the intent of the tag, None for a tag no intent holds."""
    intent = state.wake.intents.get(tag)
    return (intent.body.agent, intent.body.task) if intent is not None else None


def halting(state: dict, intent: dict, reason: str) -> list[dict]:
    """-> `wake-halted {agent, task, reason, count}` and ONE notice of the team to the owner (`halted: true`, no
    `about`: it holds no wait) when the failure of `intent` is the HALT_AFTER-th one in a row of its member on its task
    with the same identity (`failure_identity`) since the task's last resume or the season's start -- an end of the
    member there breaks the row, a `launch-missing` launched nothing and is never counted --; [] otherwise. The member
    is launched on that task no more until `team resume --task`."""
    agent, task = intent.body.agent, intent.body.task
    if reason == "launch-missing" or halted_of(state, agent, task) is not None:
        return []
    started = state.season.started
    since = max(int(state.task.resumed.get(task, 0) or 0), int((started.id if started is not None else None) or 0))
    mine = sorted((one for one in [*state.wake.ends, *state.wake.fails] if int(one.id or 0) > since
                   and wake_of(state, one.body.tag) == (agent, task)),
                  key=lambda one: int(one.id or 0))
    same, identity = 1, failure_identity(reason)
    for one in reversed(mine):
        said = one.body.reason if one.kind == "wake-failed" else None   # an end carries no reason
        if said == "launch-missing":
            continue
        if one.kind != "wake-failed" or failure_identity(said) != identity:
            break
        same += 1
    if same < HALT_AFTER:
        return []
    team = started.team if started is not None else None
    return [WakeHalted.made(agent=agent, task=task, reason=reason, count=same),
            Post.made(task=task, sender=team, to=str(started.body.owner if started is not None else None),
                      verb="notice", halted=True,
                      text=f"{agent} failed {same} times in a row on {task} ({reason}): the team no longer "
                           f"launches it on {task} until `team resume {team} --task {task}`")]


def quota_of(state: dict, member: str, clock: datetime) -> dict | None:
    """-> the provider's limit that holds the member at `clock`, `{until, said, at, task, tag}` -- its `until` still to
    come, or none said --, None when no limit holds it."""
    held = state.wake.quotas.get(member)
    if not held:
        return None
    if held.get("until") is None:
        return held
    try:
        until = datetime.fromisoformat(str(held["until"])).astimezone().replace(tzinfo=None)
    except ValueError:
        return held
    return held if clock < until else None


def ended_from_flow(state: dict, intent: dict, launch: dict, told: dict, hint: str | None,
                    awaits: tuple[str | None, bool] = (None, False)) -> list[dict]:
    """-> the events that END a launch whose flow said its end: `wake-ended {tag, agent, run, launch, state,
    cost, flow, context, tokens}` when a response was kept -- `state` what the house said of the run at `--on-end` (the
    `response` line's, else `hint`, the `PP_AGENT_STATE` the on-end tick carries): `standing`, the run
    waits for a production and is relaunched; `parked`, it waits for a message --; `wake-failed wake-dead
    {state}` when the launch ended without a response (the harness died): `state` what the run awaits, read at
    agent's face (`awaits`); no run on it, the member keeps the run that answered before or opens a new one.
    `flow` is the rank of the flow the journal reached: the next launch of the run reads from there; `context` the
    last context the exchange measured, None when it measured none; `tokens` what its calls sent the model (`sent_of`).
    A response kept on an ERROR of the harness -- its
    `error` set or its `harness_rc` not 0, but for the errors that are no fault of it (`HARNESS_SPARED`) -- whose launch
    routed no act is no answer: `wake-failed {reason: harness-error: <error>}`, the run kept (`failed`); one on the
    provider's usage limit (`error: quota`) is `quota-reached {agent, task, until, said}`: no failure, no retry, no
    fall -- the member is launched on no task before `until`, or before `team resume --task` without one."""
    response = told.get("response") or {}
    cost = told.get("cost") if told.get("cost") else response.get("cost_usd")
    run, rank = launch.body.run if launch is not None else None, told.get("rank")
    if not told.get("response"):
        said, resumable = awaits
        return failed(state, intent, "wake-dead", None, run if resumable else None, {"flow": rank, "state": said})
    said = str(response.get("state") or hint or "parked")
    error, rc = response.get("error"), response.get("harness_rc")
    if error == "quota":                                         # the provider's limit: a stop, never a failure
        quota = response.get("quota") or {}
        return [QuotaReached.made(tag=intent.body.tag, agent=intent.body.agent, task=intent.body.task, run=run,
                                  launch=launch.body.launch if launch is not None else None, state=said, cost=cost,
                                  flow=rank,
                                  until=quota.get("until"), said=quota.get("said"))]
    if (error not in HARNESS_SPARED and (error is not None or rc not in (0, None))
            and not state.wake.routed.get(intent.body.tag)):
        return failed(state, intent, f"harness-error: {error or f'harness rc {rc}'}", cost, run,
                      {"flow": rank, "state": said, "harness_rc": rc})
    return [WakeEnded.made(tag=intent.body.tag, agent=intent.body.agent, run=run,
                           launch=launch.body.launch if launch is not None else None, state=said,
                           cost=cost, flow=rank, context=told.get("context"), tokens=sent_of(response))]


def sent_of(response: dict) -> int | None:
    """-> the tokens the calls of a wake-up sent the model, as its response's record says them (`tokens_sent`);
    None when the adapter measured none."""
    sent = response.get("tokens_sent")
    return sent if isinstance(sent, int) and not isinstance(sent, bool) else None


def launches_of_run(state: dict, run: str) -> int:
    """-> the launches the journal knows of the run: its `wake-launched` events -- the rank the next one
    takes, and the rank of the exchange in the run's flow (`agent flow --exchange`)."""
    return sum(1 for one in state.wake.launched.values() if one.body.run == run)


def went(state: dict, tagged: set[str], tag: str) -> bool:
    """-> whether the intent was LAUNCHED: its `wake-launched` event, or its tag at the house's
    `messages.jsonl` (`tagged`: what the cursor read of it) -- the reap's own test. The bounds count
    these alone."""
    return tag in state.wake.launched or tag in tagged


def launched_run(state: dict, tag: str) -> str | None:
    """-> the run the `wake-launched` of the tag names, None while nothing launched it."""
    launched = state.wake.launched.get(tag)
    return launched.body.run if launched is not None else None


def renewal_of(state: dict, agent: str, task: str, run: str | None) -> dict | None:
    """-> the `run-renewed {member, task, run, why, ...}` the member's wake-up on `task` writes before its intent, None
    when it resumes `run` -- the ONE decision of a renewal, read at a wake-up, never in the middle of a passage: a run
    STANDING on the task is continued until it parks, unless its PROVIDER changed -- a session lives under its provider
    alone, and `agent start` refuses to resume it under another (`provider-mismatch`). Two causes, the first that holds:
    - `why: model` -- the run was opened under another model or provider than the season's profile gives the member
      now (`opened_under`, `launch_kept`), with `was` and `now`; a run whose opening kept no trace is not renewed so;
    - `why: context` -- the last measure of `run` (the last `wake-ended` of that run that carries a context, read from
      the journal alone) reached the limit, with `used` and `limit`: on an OCCURRENCE, its recurrence's `context`, at
      the member's FIRST wake-up on it (an occurrence is never cut between two runs), `recurrence` said; on a task of
      its own carrier, the task's `context` (its `post --context`), else the season's (`context:` of SEASON.md).
    Without a limit, without a measure, or under it, the run is resumed."""
    if run is None:
        return None
    started = state.season.started
    was = opened_under(state, run)
    now = launch_kept(started, agent) if started is not None else {"model": None, "provider": None}   # no start
    if (agent, task) in state.wake.standing and (was is None or was["provider"] == now["provider"]):
        return None
    held = state.task.tasks.get(task)
    recurrence = state.rhythm.recurrences.get(held.recurrence if held is not None else None)
    head = RunRenewed.made(member=agent, **({"recurrence": recurrence.id} if recurrence is not None else {}), task=task,
                           run=run)
    if was is not None and was != now:
        return head.but(why="model", was=was, now=now)
    if recurrence is not None:
        limit = recurrence.context
        if any(one.body.agent == agent and one.body.task == task for one in state.wake.intents.values()):
            return None
    elif carrier_of(state, task) == task:
        context = held.context if held is not None else None
        limit = context if context is not None else state.season.limits.get("context")
    else:
        return None
    measure = next((one.body.context for one in reversed(state.wake.ends)
                    if one.body.run == run and isinstance(one.body.context, dict)), None)
    used = (measure or {}).get("used")
    if limit is None or not isinstance(used, (int, float)) or used * 100 < limit:
        return None
    return head.but(why="context", used=used, limit=limit)


def opened_under(state: dict, run: str) -> dict | None:
    """-> `{model, provider}` the run was OPENED under: what its first `wake-launched` kept; None when that launch kept
    neither (a journal of before team 1.24.0)."""
    first = next((one for one in state.wake.launched.values() if one.body.run == run), None)
    if first is None or not ("model" in first.line or "provider" in first.line):   # kept, even at null: the line says
        return None
    return {"model": first.body.model, "provider": first.body.provider}


def running_on(state: dict, task: str) -> list[dict]:
    """-> the wake-ups under way on the task, in the journal's order: each intent without an end that
    carries it -- its member, tag, run and hour once launched (`null` before), its allowance. A launch nobody
    holds (`faced`: its wake lock free) is not under way: what a post turns a spinner on is a launch PROVEN."""
    found = []
    gone = state.wake.gone or ()
    for tag, one in state.wake.intents.items():
        if tag in state.wake.ended or one.body.task != task or str(tag) in gone:
            continue
        launched = state.wake.launched.get(tag)
        found.append({"member": one.body.agent, "tag": tag, "run": launched.body.run if launched is not None else None,
                      "since": launched.at if launched is not None else None, "allowance": one.body.allowance,
                      "relance": one.body.relance})
    return found


def last_launch(state: dict, member: str) -> dict | None:
    """-> the `wake-launched` of the member's last intent, None while that intent stands launched
    by nobody yet."""
    latest = None
    for one in sorted(state.wake.intents.values(), key=lambda entry: int(entry.id or 0)):
        if one.body.agent == member:
            latest = state.wake.launched.get(one.body.tag)
    return latest


def launched_at(state: dict, member: str) -> str:
    """-> `HH:MM` (UTC) of the member's last launch -- `?` while its intent stands launched by
    nobody yet."""
    launch = last_launch(state, member)
    return str(launch.at)[11:16] if launch is not None and launch.at else "?"


def run_of(state: dict, member: str) -> tuple[str, str, list[str]] | None:
    """-> (run, state, tasks) of the member, or None before its first wake-up: the run
    its last launch carried (`?` when none was launched); `running` while its last intent has no
    end -- `gone` when nobody holds that launch (`faced`: its end is not read yet, or it died with its process
    space) --, `killed` when a `stop --kill` ended it, `refused` when the house refused its launch, `dead` when it
    failed, `ended` otherwise -- and `kept` when that last intent and its end are of a season BEFORE the one that
    plays: a season starts nobody suspected (`team-started`), and what a launch of the season before said is no
    state of this one; the run is kept, nothing was launched since; the
    tasks its wake-ups carried, on EVERY run it holds -- one per carrier, each said by `run_face` --, in the
    order of their first intent. After a `team reset`
    the intents before it are the forgotten runs': none since, the run is `—` and its state `reset`."""
    since = int(state.wake.reset.get(member) or 0)
    intents = [one for one in sorted(state.wake.intents.values(), key=lambda entry: int(entry.id or 0))
               if one.body.agent == member and int(one.id or 0) > since]
    if not intents:
        return ("—", "reset", []) if member in state.wake.reset else None
    runs = {str(one.body.tag): launched_run(state, one.body.tag) for one in intents}
    run = next((key for key in reversed(list(runs.values())) if key), None)
    tasks = list(dict.fromkeys(str(one.body.task) for one in intents))
    last_tag = str(intents[-1].body.tag)
    answered = {str(one.body.tag) for one in state.wake.ends}
    started = state.season.started
    season = int((started.id if started is not None else None) or 0)
    ended_at = max((int(one.id or 0) for one in [*state.wake.ends, *state.wake.fails]
                    if str(one.body.tag) == last_tag), default=0)
    if last_tag not in state.wake.ended:
        how = "gone" if last_tag in (state.wake.gone or ()) else "running"
    elif max(int(intents[-1].id or 0), ended_at) < season:
        how = "kept"
    elif last_tag in state.wake.killed:
        how = "killed"
    elif last_tag in answered:
        how = "ended"
    elif last_tag in state.wake.house:
        how = "refused"
    elif (state.wake.quotas.get(member) or {}).get("tag") == last_tag:
        how = "quota"
    else:
        how = "dead"
    return run or "?", how, tasks


def team_runs(state: dict, events: list[dict]) -> list[dict]:
    """-> every run a wake-up of the team opened, `{member, path, run}` in the order the journal met them: the
    runs its `wake-launched` and `wake-ended` name, a member's path read at its intent or at the start."""
    paths: dict[str, str] = {}
    by_tag: dict[str, str] = {}
    found: dict[tuple[str, str], dict] = {}
    for one in events:
        kind = one.get("kind")
        if kind == "team-started":
            paths.update({str(member): str(path) for member, path in (one.get("agents") or {}).items()})
        elif kind == "wake-intent" and one.get("path"):
            by_tag[str(one.get("tag"))] = str(one["path"])
        elif kind in ("wake-launched", "wake-ended") and one.get("run"):
            member = str(one.get("agent"))
            path = by_tag.get(str(one.get("tag"))) or paths.get(member)
            if path:
                found.setdefault((path, str(one["run"])), {"member": member, "path": path, "run": str(one["run"])})
    for member, run in ((member, run) for member, held in state.wake.runs.items() for run in held.values()):
        if run and paths.get(member):
            found.setdefault((paths[member], run), {"member": member, "path": paths[member], "run": run})
    return list(found.values())


def purged_already(said: str) -> set[str]:
    """-> the run keys `agent purge` refused as `run-unknown` -- runs no longer at the agent: a delete taken up after
    a `delete-failed` purged them the first time, nothing of them is left."""
    found = re.search(r"run-unknown -- `([^`]*)`", said or "")
    return set(found.group(1).split()) if found else set()


def closed_before(state: dict, intent: dict) -> bool:
    """-> whether a launch was a CONTINUATION ON A CLOSED TASK: its intent written after the `done` of its task. A
    run that stands on a task its root closed gets ONE such launch, under `CLOSED_HEAD`, to end its passage; when
    it stands after it, the replay holds it as parked -- nothing continues it any more, a message alone launches
    it again (s.1409: twelve old runs continued without end on 2026-11-08, an open task starved). Nothing is
    written for it: the journal's `wake-ended {state: standing}` stays what the house said of the run."""
    done = state.task.done.get(intent.body.task)
    return done is not None and int(intent.id or 0) > int(done.id or 0)



def act_judged(state: dict, name: str, tag: str, rank: int, ordinal: int, found: list) -> list:
    """-> what ONE `words` of a launch writes, its CANDIDATES (`candidates_of`) judged in their order, whole or not at
    all -- [] when the intent is unknown or a `wake-routed` of the tag at that rank stands: `wake-routed {tag, agent,
    run, launch, words, line}` then the posts of a candidate whose form and sense are right (`routed`); `wake-refused
    {..., why}` and an `info` to the member for one whose form is broken (`act_formed`) or whose sense is wrong; on a
    stopped task, each goes nowhere (`wake-routed` with `nowhere`)."""
    intent = state.wake.intents.get(tag)
    launch = state.wake.launched.get(tag)
    if intent is None or rank <= int(state.wake.routed.get(tag) or 0):
        return []
    read = {"tag": tag, "agent": intent.body.agent, "run": launch.body.run if launch is not None else None,
            "launch": launch.body.launch if launch is not None else None, "words": ordinal, "line": rank}
    marked = WakeRouted.made(**read)
    held = state.task.tasks.get(intent.body.task)
    if held is not None and held.state == "stopped":
        return [marked.but(nowhere=True) for _ in found]
    decided: list = []
    settled: set = set()
    closed: set = set()
    for elements, broken in found:
        try:
            if elements is None:
                raise Refused(broken)
            act_formed(elements)
            decided += [marked, *routed(state, intent, elements, settled, closed)]
        except Refused as why:
            decided += [WakeRefused.made(**read, why=str(why)),
                        Post.made(task=intent.body.task, sender=name, to=intent.body.agent, verb="info",
                                  text=f"your act was refused: {why}")]
    return decided


def kill_verdict(launch: dict, answered: bool, apart: bool) -> str:
    """-> what `stop --kill` does to ONE launch under way on its task, from what the act read of it -- `answered`, its
    flow holds its response; `apart`, it was born in another process space (`foreign`): `answered` (spared, the reap
    ends it), `unlaunched` (no pid yet: it ends on its own), `foreign` (its pid names nobody here), `kill` (its
    launcher is ended by its process group)."""
    if launch.get("run") and answered:
        return "answered"
    if not isinstance(launch.get("pid"), int):
        return "unlaunched"
    if apart:
        return "foreign"
    return "kill"


def kills_written(task: str, killed: list) -> list:
    """-> `wake-killed {tag, agent, task, run, pid}` for each (intent, launch) whose launcher the kill ended, in order."""
    return [WakeKilled.made(tag=one.body.tag, agent=one.body.agent, task=task, run=launch.get("run"),
                            pid=launch.get("pid"))
            for one, launch in killed]


def quota_lift_asked(state: dict, owner: str, member: str | None, principal: str | None) -> tuple:
    """-> (who lifts, the members named): what `team resume --quota` asks, judged before the hour is read -- the
    principal `--as` names (`principal_of`, the owner without it), the member `--member` names, else every member of
    the season; else `Declined` by its code: `team-not-started`, `team-deleting`, `season-stopped`, `member-unknown`
    (the member, the members the season knows)."""
    if state.season.started is None:
        raise Declined("team-not-started")
    if state.season.deleting:
        raise Declined("team-deleting")
    if state.season.stopped:
        raise Declined("season-stopped")
    sender = principal_of(state, owner, principal)
    agents = state.season.started.body.agents or {}
    if member is not None and member not in agents:
        raise Declined("member-unknown", member, list(agents))
    return sender, ([member] if member is not None else list(agents))


def quota_lift_of(state: dict, sender: str, member: str | None, named: list, now) -> list:
    """-> `quota-lifted {by, members}`: the members named a provider's limit holds at `now`, lifted by `sender`; else
    `Declined("quota-not-held", member)` -- the member asked, or None for every member."""
    lifted = [one for one in named if quota_of(state, one, now) is not None]
    if not lifted:
        raise Declined("quota-not-held", member)
    return [QuotaLifted.made(by=sender, members=lifted)]


def launch_found(state: dict, tag: str, intent: dict, found: dict) -> list:
    """-> the `wake-launched` of an intent the journal does not know launched, from what the house's record says of it
    (`found`: its run and pid); its rank is the run's next."""
    return [WakeLaunched.made(tag=tag, agent=intent.body.agent, run=found["run"], pid=found.get("pid"),
                              launch=launches_of_run(state, str(found["run"])) + 1)]


def ended_stopped(tag: str, intent: dict, launch: dict, run: str, told: dict, said: str | None) -> list:
    """-> the `wake-ended` of a launch that answered on a task stopped meanwhile: no failure is judged, its state the
    response's, else `said`, else parked; its cost, its flow, its context and its tokens."""
    response = told["response"] or {}
    return [WakeEnded.made(tag=tag, agent=intent.body.agent, run=run, launch=launch.body.launch,
                           state=str(response.get("state") or said or "parked"),
                           cost=told.get("cost") or response.get("cost_usd"), flow=told["rank"],
                           context=told.get("context"), tokens=sent_of(response))]


def foreign_ended(state: dict, name: str, intent: dict, rank, space) -> list:
    """-> the events of a launch whose launcher was born in another process space and ended with it: the house's
    failure (`house_failed`), its flow read and that space said on the failure."""
    events = house_failed(state, name, intent, "its launcher played in another process space, which ended before "
                          "the exchange did -- tick the team from the house's own")
    return [events[0].but(flow=rank, space=space), *events[1:]]


def reset_of(member: str, run: str) -> list:
    """-> `run-reset {member, run}`: `team reset` forgot one run of the member."""
    return [RunReset.made(member=member, run=run)]
