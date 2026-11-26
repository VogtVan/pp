"""The `health` domain, layer `rules`: what the team's state says of its health, and what the tick writes of it.

A definition belongs here when it computes its answer from the state and the values it is given: who waits for whom
and the deadlocks that follow, a member's silence on a task, its passages, when it is reminded, the answers the team
gives in place of a member suspected, when it is tried again. The silences and the answers in a member's place are
DECISIONS: they compose by `made` the bodies the tick writes, and the words for a member that does not answer
(`not_answering`) are composed here, where they are written. It reads no disk, no clock and no environment and
prints nothing: the time comes to it as an argument, and what needs the system belongs to `store`.

It reads the typed state by its parts -- `state.task.messages`, `state.season.started`, `state.wake.intents` -- and an
event by `one.id` and `one.body`; a start that may be missing is tested by `None`. What it reads by key is a
dictionary kept in a part: `limits`, and a member's entry in `health`.
"""
from __future__ import annotations

from datetime import datetime

from task.model import Post
from health.model import DEFAULT_SILENCE, Silence
from season.rules import is_member, is_principal, profile_of
from task.rules import (cited_of, inbox, is_notice, is_open, is_root, notice_about, opening_of, owed_by,
                        owes, principal_answered, principal_opening, receives, told_of)
from wake.rules import busy, carrier_of, closed_before, owed_free, run_held, suspicion_of


def waits_for(state: dict) -> dict[str, set[str]]:
    """-> the WAIT-FOR graph of the team, on every open task: a -> b while a `do` or an `ask` of the member a
    to the member b still owes its answer, and a -> p while an `ask` of a to the principal p, or a notice of the team to p
    about a, has no answer of p that cites it -- a notice of a silence holds no wait: the try waits for no answer
    (row 115). A principal waits on nobody."""
    answered = principal_answered(state)
    edges: dict[str, set[str]] = {}
    for key, one in state.task.messages.items():
        to = one.body.to
        notice = is_notice(state, one) and one.body.cause != "silence"   # a silence notice holds no wait (row 115)
        frm = notice_about(state, one) if notice else one.body.sender
        if not is_member(state, frm) or not is_open(state, one.body.task):
            continue
        if (owes(state, key) and is_member(state, to)) or (
                (one.body.verb == "ask" or notice) and is_principal(state, to) and key not in answered):
            edges.setdefault(str(frm), set()).add(str(to))
    return edges


def deadlocked(state: dict) -> set[str]:
    """-> the DEADLOCKED set of the team (Chandy, Misra, Haas 1983, the communication model): the greatest set of
    IDLE members -- no wake-up under way, nothing to receive -- whose every wait stays in the set; a principal is
    in none, since it may always post. Computed from the idle members, dropping any whose wait leaves the set,
    until nothing moves."""
    edges = waits_for(state)
    started = state.season.started
    members = list((started.body.agents if started is not None else None) or {})
    found = {one for one in members if not busy(state, one) and not receives(state, one)}
    moved = True
    while moved:
        moved = False
        for one in list(found):
            if any(other not in found for other in edges.get(one, ())):
                found.discard(one)
                moved = True
    return found


def reached(edges: dict[str, set[str]], member: str) -> set[str]:
    """-> every member and principal the member reaches by its waits."""
    seen, stack = set(), list(edges.get(member, ()))
    while stack:
        one = stack.pop()
        if one not in seen:
            seen.add(one)
            stack.extend(edges.get(one, ()))
    return seen


def at_bottom(state: dict, member: str) -> bool:
    """-> whether the member stands at the BOTTOM of the deadlocked set: in it, and every member it reaches by its
    waits reaches it back -- a sink (it waits for nobody) or a knot. Its answer unblocks those that wait on it."""
    if member not in deadlocked(state):
        return False
    edges = waits_for(state)
    return all(member in reached(edges, one) for one in reached(edges, member))


def silence_since(state: dict, member: str, task: str) -> int:
    """-> the journal id the member's SILENCE on the task counts from: the latest of its last routed act on the task
    (a post of its, `info` included, never one the tick wrote in its place), the task's `resumed`, the season's
    `team-started`, and its last `silence` fall there."""
    acts = [key for key, one in state.task.messages.items()
            if one.body.sender == member and one.body.task == task and one.body.by != "tick"]
    falls = [int(one.id or 0) for one in state.health.silences if one.body.agent == member and one.body.task == task]
    started = state.season.started
    return max(acts + falls + [state.task.resumed.get(task, 0), int((started.id if started is not None else None) or 0)])


def stood(state: dict, member: str, task: str) -> bool:
    """-> whether the member's run for the task's CARRIER stands: its last launch there left it waiting for a
    production, and nothing parked it since."""
    carrier = carrier_of(state, task)
    return any(one == member and carrier_of(state, other) == carrier for one, other in state.wake.standing)


def passages_of(state: dict, member: str, task: str) -> list[dict]:
    """-> the member's PASSAGES on the task, in the journal's order (row 115): each WAKE-UP of its there and its
    CONTINUATIONS, until the run parks -- `{id, end}`, the id of the wake-up's intent and the id of the `wake-ended`
    that parked the run, None while it stands, plays, or died. A launch is a continuation when it resumes a run
    that stood at its intent: read on the earlier end of the member's launches on the task's carrier, as the replay
    holds it -- a `wake-ended {state: standing}`, or a `wake-failed` that left the run standing with a retry; the
    one continuation on a closed task (`closed_before`) parks the run whatever its end says: the first launch on
    the carrier's next task is a wake-up --, never on a field of the intent, so that a journal of before reads the
    same."""
    carrier = carrier_of(state, task)
    ends = {one.body.tag: one for one in state.wake.ends}
    fails = {one.body.tag: one for one in state.wake.fails}
    found: list[dict] = []
    standing = False
    for tag, intent in state.wake.intents.items():
        if intent.body.agent != member or carrier_of(state, intent.body.task) != carrier:
            continue
        if not (standing and intent.body.run and found):       # a WAKE-UP: it opens a passage
            found.append({"id": int(intent.id or 0), "task": intent.body.task, "end": None})
        if tag in ends:
            standing = ends[tag].body.state == "standing" and not closed_before(state, intent)
            found[-1]["end"] = None if standing else int(ends[tag].id or 0)
        elif tag in fails:
            standing = (fails[tag].body.state == "standing" and not fails[tag].body.final
                        and not closed_before(state, intent))
    return [one for one in found if one["task"] == task]


def owed_at(state: dict, member: str, task: str, at: int) -> bool:
    """-> whether the member owed an answer on the task at the journal id `at`: a `do` or an `ask` a launch of its
    had carried by then, that no answer settled before."""
    carried = {key for one in state.wake.intents.values()
               if one.body.agent == member and int(one.id or 0) <= at for key in one.body.messages or []}
    for key in carried:
        message = state.task.messages.get(key)
        settled = state.task.debts.get(key, "x")
        if (message is not None and message.body.to == member and message.body.task == task and settled != "x"
                and (settled is None or not isinstance(settled, int) or settled > at)):
            return True
    return False


def awaited_principal(state: dict, member: str, task: str, at: int) -> bool:
    """-> whether the member waited for a PRINCIPAL's answer on the task at the journal id `at`: a question of its
    own to a principal, asked before, that no answer of a principal cited by then."""
    answered: dict = {}
    for key, one in state.task.messages.items():
        cited = cited_of(state, one) if one.body.verb in ("re", "reply") and is_principal(state, one.body.sender) else None
        if cited is not None:
            answered[cited] = min(answered.get(cited, key), key)
    return any(one.body.verb == "ask" and one.body.sender == member and one.body.task == task
               and is_principal(state, one.body.to) and key < at and answered.get(key, at) >= at
               for key, one in state.task.messages.items())


def silence_of(state: dict, member: str, task: str, after: int = 0) -> int:
    """-> the member's SILENCE on the task (row 115): its silent PASSAGES there since `silence_since` -- and since
    `after`, the fall a suspect's passages count from. A passage is silent when its run PARKED, the member owed an
    answer on the task at its wake-up, said no routed act since -- an act moves `silence_since` -- and waited for no
    principal's answer at the park. A CONTINUATION counts for nothing: a run that stands is continued while it does
    not park. Read from the journal alone: nothing is written to count."""
    since = max(silence_since(state, member, task), after)
    return sum(1 for one in passages_of(state, member, task)
               if one["id"] > since and one["end"] is not None and owed_at(state, member, task, one["id"])
               and not awaited_principal(state, member, task, one["end"]))


def beat_of(state: dict, member: str, task: str, box: list[dict]) -> int | None:
    """-> the BEAT a WAKE-UP keeps on its intent and says at its head: the exchanges left to the member to say an act
    on the task, this one counted -- `silence:` less its silent passages in a row there, never under 1; 1 for a
    suspected member, whose silent try is one more fall; None for a member that owes nothing on the task once its
    box is delivered: nothing is asked of it."""
    owing = (any(state.task.messages[key].body.task == task for key in owed_by(state, member))
             or any(owes(state, one.id) and one.body.to == member for one in box))
    if not owing:
        return None
    if suspicion_of(state, member) is not None:
        return 1
    return max(1, silence_limit(state, member) - silence_of(state, member, task))


def standing_of(state: dict, member: str) -> list[str]:
    """-> the tasks the member's runs STAND on and are continued on, one (member, task) each: open or resolved -- a
    run standing on a closed task is continued ONCE (`closed_before`); a stopped one is launched once more by its
    stop (`dues`) --, in the tasks' order, from the one after the task of its last launch: each in its turn."""
    order = list(state.task.tasks)
    tasks = [task for task in order if (member, task) in state.wake.standing
             and state.task.tasks[task].state in ("open", "resolved")]
    last = next((one.body.task for one in reversed(state.wake.intents.values()) if one.body.agent == member), None)
    after = order.index(last) if last in order else -1
    return [task for task in tasks if order.index(task) > after] + [task for task in tasks if order.index(task) <= after]


def continued_run(state: dict, member: str, task: str) -> bool:
    """-> whether the member's run for the task's CARRIER stands and is still continued: a pair (member, task') of
    that carrier stands, its run held, its task open or resolved, its launches not spent -- what `woken_on` asks of
    a continuation. ONE run is one passage: nothing but a stop is delivered to it until it parks -- the messages
    due wait, and open the launch after its park, a turn of their own (s.1377). A run that is continued no more
    -- its task's `launches:` spent, or a first launch dead before any run was kept -- takes its messages, so that
    nothing starves."""
    carrier = carrier_of(state, task)
    return any(one == member and carrier_of(state, other) == carrier and other not in state.budget.launches_spent
               and (state.task.tasks[other].state if other in state.task.tasks else None) in ("open", "resolved")
               and run_held(state, member, other) is not None
               for one, other in state.wake.standing)


def silent_tasks(state: dict, member: str) -> list[str]:
    """-> the tasks the member's silence is judged on: each task it owes an answer on. A run that stands is not
    judged for itself: it is continued while it does not park; a closed task has no silence."""
    return list(dict.fromkeys(str(state.task.messages[key].body.task) for key in owed_by(state, member)))


def silence_limit(state: dict, member: str) -> int:
    """-> the silent passages in a row that make the member suspected: its profile's `--silence`, else the season's
    or `TEAM.md`'s `silence:` (`state["limits"]`), else DEFAULT_SILENCE."""
    started = state.season.started
    profile = profile_of(started, member) if started is not None else {}
    if profile.get("silence") is not None:
        return int(profile["silence"])
    return int(state.season.limits.get("silence") or DEFAULT_SILENCE)


def relance_of(state: dict, member: str) -> tuple[str, str | None] | None:
    """-> why the tick RELANCES the member: it owes an answer on a task that does not halt it (`owed_free`) and stands
    at the bottom of the deadlocked set --
    `("owed", None)` a sink, `("cycle", <member>)` a knot, naming a member it waits on --; None otherwise. Every
    relance asks an answer or an info, whatever the member's silence. No count bounds the relances: its silence
    makes the member suspected, and `launches:`, `budget:` and `budget-launches:` bound a long task."""
    debts = owed_free(state, member)
    if not debts or not at_bottom(state, member):
        return None
    waits = sorted(waits_for(state).get(member, ()))
    return ("owed", None) if not waits else ("cycle", waits[0])


def silences(state: dict, name: str, clock: datetime, member: str | None = None) -> list:
    """-> what the tick writes for each member whose SILENCE fell (row 115): `silence {agent, task, passages}` for a
    member, no wake-up of its under way, whose silent passages in a row on a task it owes on (`silent_tasks`)
    reach `silence:`; for a member suspected already, once its interval passed, ONE silent passage begun since its
    last fall -- of a launch or of its silence: its try said nothing -- is one more fall. The replay makes each a
    fall of the detector (`health.falls + 1`,
    `cause: silence`). A root's principal gets the team's notice about it, once per opening. Judged for ONE member
    (`member`) right before its own wake, on the journal as it stands then -- a launch of its may have ended
    since the tick began --, or for every member."""
    events: list = []
    started = state.season.started
    for member in ([member] if member else list((started.body.agents if started is not None else None) or {})):
        if busy(state, member):
            continue
        suspicion = suspicion_of(state, member)
        fallen_at = int((state.health.health.get(member) or {}).get("id") or 0) if suspicion is not None else 0
        for task in silent_tasks(state, member):
            n = silence_of(state, member, task, fallen_at)
            fell = (n >= 1 and clock >= suspicion["until"]) if suspicion is not None else (
                n >= silence_limit(state, member))
            if not fell:
                continue
            events.append(Silence.made(agent=member, task=task, passages=n))
            opening = opening_of(state, task)
            told = any(is_notice(state, one) and one.body.about == member and one.body.task == task
                       and one.id > int(opening or 0) for one in state.task.messages.values())
            if is_root(state, member, task) and not told:
                events.append(Post.made(task=task, sender=name, to=told_of(state, member, task), verb="notice",
                                        about=member, cause="silence",
                                        text=f"{member} owes an answer on {task} and ended {n} exchange(s) in a row "
                                             "without a message to the team: it is suspected, and the team tries it "
                                             "again after a pause"))
            break                                                # one fall per tick and member
    return events


def within(state: dict, member: str, clock: datetime) -> bool:
    """-> whether the member is suspected and its interval still runs: nobody wakes it."""
    suspicion = suspicion_of(state, member)
    return suspicion is not None and clock < suspicion["until"]


def suspected_answers(state: dict, clock: datetime) -> list:
    """-> what the tick writes for each SUSPECTED member within its interval, no wake-up of its under way: every
    debt it owes to a MEMBER and every `do` or `ask` of a member that reaches it answered in its place (`re`, `by:
    tick`, its text the hour from which a message reaches the member again), which takes the message out of the
    member's inbox and wakes its author: `suspected` on a message a `wake-intent` of the member carried -- a debt
    delivered, or a message a dead launch gave back to the inbox for its retry --, `returned` on a message no
    `wake-intent` of the member ever carried -- the replay holds that one for returned to its author. Either way the
    author's head shows the message whole (`message_of`). What a PRINCIPAL
    says to the member is never answered for: a launch of the member delivers it at this very tick (`woken`), and
    that launch is its try; a principal's opening delivered before the fall stays owed, tried once the interval
    passed (`tried_of`). A member's message that owes nothing waits for the try."""
    events: list = []
    started = state.season.started
    for member in list((started.body.agents if started is not None else None) or {}):
        suspicion = suspicion_of(state, member)
        if suspicion is None or clock >= suspicion["until"] or busy(state, member):
            continue
        said = not_answering(member, suspicion)
        carried = {key for one in state.wake.intents.values() if one.body.agent == member
                   for key in one.body.messages or []}       # what a launch of the member carried, whatever its end
        reaching = [one.id for one in inbox(state, member) if owes(state, one.id) and is_open(state, one.body.task)]
        for key in dict.fromkeys(owed_by(state, member) + reaching):
            message = state.task.messages[key]
            if is_member(state, message.body.sender):
                how = "suspected" if key in carried or key in state.task.delivered else "returned"
                events.append(Post.made(task=message.body.task, sender=member, to=message.body.sender, verb="re",
                                        re=key, by="tick", **{how: True}, text=said))
    return events


def tried_of(state: dict, member: str, clock: datetime) -> tuple[str, None] | None:
    """-> `("tried", None)` when the tick TRIES the suspected member by a relance: its interval passed, no wake-up
    of its under way, and a principal's opening among its debts -- what nothing else would deliver it again. A
    member with another message to receive is tried by that message, as any wake-up."""
    suspicion = suspicion_of(state, member)
    if suspicion is None or clock < suspicion["until"] or busy(state, member):
        return None
    return ("tried", None) if any(principal_opening(state, key) for key in owed_free(state, member)) else None


def not_answering(member: str, suspicion: dict) -> str:
    return (f"no answer: {member} is not answering at the moment. A message sent to {member} from "
            f"{suspicion['until']:%H:%M:%S} on reaches it again")
