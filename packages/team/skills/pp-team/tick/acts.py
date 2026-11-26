"""The `tick` domain, layer `acts`: one advance of the team -- the effects played, the events written.

A definition belongs here when it plays the tick or one of its steps: it takes the tick's lock without waiting, reads
what the members said, rings what is due, launches each member that has something to receive, arms the timer on the
next deadline, and writes what happened to the journal through its writer. It decides none of the events it writes:
for each, it plays the effect first -- the budget measured, the launcher run, the run named, the hour read --, then
hands what the effect gave to a decision of `tick/rules.py`, and writes the bodies that decision composes, in the
order the tick has always written them. It may use the lower layers of any domain.

A TICK takes `tick.lock` beside the journal WITHOUT waiting: held by another tick, it posts the
mark `tick.pending`, tries once more and exits 0 having written nothing. The holder clears the
mark, plays its steps, releases the lock, THEN reads the mark: set, it takes the lock again
and plays once more. A wake-up is ONE LAUNCH of the harness (`agent start … --launches 1`), and what
the member says in it is read AS IT COMES: each `words` of the launch (a block of text between two
calls of the tool, kept at the run's flow by the house) is read by `agent flow --from` -- by the
launch's FOLLOWER while it plays, by the reap after --, and each ACT a `words` carries (`candidates_of`:
a JSON object, or a list of them, with the key of a form -- `do`, `ask`, `re`, `info` -- alone or
written among other text) is routed once by its rank (`wake-routed {run, launch, words, line}`), or refused
and said to the member when its form or its sense is wrong (`wake-refused`, an `info`); a `words` without
an act is SAID: nothing written, nothing fails. The steps: 1. REAP -- each `wake-intent` without an end: its launch by
its `wake-launched` event, else by its tag at the house's `messages.jsonl` (read from the cursor
`tick.cursor`: a late `wake-launched`), else none: `wake-failed launch-missing`, never final and costing
no retry -- nothing was launched; launched, its wake lock is judged FIRST: held within `timeout:`, the
launch plays and its follower reads it; free, or held past the bound, its flow is read from the rank the
journal reached and the launch ENDED as the flow says: `wake-ended {run, launch, state, cost, flow, tokens}` -- or
`wake-failed harness-error` when the response was kept on an error of the harness and the launch routed no act,
`quota-reached` on the provider's usage limit (the member launched on no task before its `until`, or before
`team resume --task` without one, or a season that gives it another provider) --; `state` what the house said of the run at `--on-end`, `standing` (the run
waits for a production:
relaunched as soon as its lock is free) or `parked` (it waits for a message), `tokens` what the launch's
calls sent the model, added up (`null` when the harness does not measure it) --, or `wake-failed
wake-dead` when no response stands (the harness died: one retry, its messages back in the inbox;
spent: `final`, and the tick ANSWERS in the member's place every message of the launch that owes --
never the opening a principal posted: the team tells that principal with a `notice` about the root),
`wake-timeout` when held past the bound (killed) -- a launch born in ANOTHER process space than the tick's
(`wake-launched.space`: a sandbox's) is never killed by its pid, and, its lock free without an end, ended with that
space: `launch-failed … house: true`, never final, nobody suspected (team 1.14.3); 2. ROUTE -- an act's elements become posts in their
order: `do` to a member that reports to the acting one (on a ceremony task its participants report to
its facilitator), `ask` to any member of the team or to a principal,
the answer `{"re": <id>}` to the author of the message it cites; a `do` off the edges, an `ask` to a name
nobody declared, a `re` citing a message never delivered to the member are
REFUSED (`wake-refused {…, why}`, an `info` to the member): nothing posted, the launch goes on. Each `do`
or `ask` delivered to a member opens ONE debt: the
first answer that cites it settles it, a later one is
posted `info`; the ROOT's answer to the task's opening writes `done` with its text, settles every
debt of the task, `returned` for every post to an agent left undelivered on it, and `schedule-off`
when no task stays open and no ceremony is declared; a post to a principal is delivered at its
writing and never returned; step 3 is gone (team 1.14.0): nothing holds a member, every message for it
launches it, and it answers a task once the answers it wants are in; 4. RING -- each ceremony whose period is due (`every`: the day conforms and the
hour is past, by `PP_NOW` or the local clock; `after`: the followed ceremony's task resolved)
and not yet rung (`ceremony-due` names the period: the journal is the judge) becomes ONE
ceremony task from the team to its facilitator, its OPENING `do` to the facilitator and a `do` per
participant -- each answer reaches the facilitator as a message, and its answer to the opening resolves it;
5. WAKE -- each MEMBER, in the declaration's order, with messages due, no launch of its under way
and the wake lock of its run free, is LAUNCHED ONCE -- on the first task, in the tasks' order, that has a
message for it:
`wake-intent` WRITTEN FIRST, then `agent start … --launches 1 --tag <tag> --on-end "<engine> --instance
<house> team tick <name>"` (`--run <key>`, the member's run for the task's CARRIER, while its slot stands --
a renewal mark an upgrade left included; none yet, an OPENING, named after the carrier by `agent name`; an
OPENING too when the run is renewed, `run-renewed` written before the intent: parked past its context
limit, or opened under another model or provider than the season gives the member now), then
`wake-launched` with the launch's RANK in the run, then its follower spawned; its other tasks wait for its
next launch, each in the run of its carrier. A member whose run STANDS (its last
launch left it waiting for a production) is RELAUNCHED on the task it stands on as soon as its lock is
free, `[nothing new]` at its head: nothing but a stop is delivered to a run that stands and is still continued
-- what is due waits for its park and opens the launch after, a turn of its own; a run whose task has spent its
`launches:` is continued no more and takes its messages. A member
holds ONE run, ONE key and ONE session per CARRIER of its tasks -- a task alone, the recurrence of its
occurrences, the ceremony of its rings --: the run that first answered there, the carrier's later tasks
arriving in it; it plays one launch at a time. The members play in parallel; `parallel:` bounds the team. The HEAD
of a launch -- what the tick writes before pp's output in the prompt -- opens on the inbox of that task
-- each message its head line, `#<id> DO from <member> on <task> -- you owe an answer`, its text
indented under it; under an answer the tick wrote in a member's place (`by: tick`), a line that says the team
wrote it, why, and that the message it answers is closed, then that message whole, with its vector when it
carries one --, or `[nothing new]`, then the messages it still owes from earlier launches;
nothing else -- what the others answered is read on demand, `team responses <name> --since <id>` --:
what an act is and what it owes is said by the team's fragment of the standing orders (`SYSTEM.md`); a NEW
run of a member whose run `-reset` or `team reset` forgot opens on `[history of <task> for <member>]` for the
open tasks of its carrier -- what it was told there and what it answered --, then its inbox. The head never carries
the team's intention -- the body of `TEAM-<name>.md` -- nor the owner's word -- the body of `TEAM.md`: pp serves
both to the team's runs, the team's document naming them in its `serve:` row at the kit's `turn.begin`, each
served again at the next exchange when it changes. An
OPENING carries the season's material (`work:` of SEASON.md -- passed as `--work`, a clone per run, kept with
its run); a resume never does. No wake-up carries a door: the trigger's ENTRY (`entries:` of
TEAM.md -- a ceremony task: its entry; else `do`'s) is a successor the agent's DAG elects at
EVERY exchange, opening or resume -- the team's document at the kit's `turn.begin`, in the team's
directory, decides by `pp-team entry <name>`. Every wake-up gets `--documents teams/<name>`: the
run opens under the team's root of documents. On a STOPPED task an answer is routed
nowhere, a dead wake-up is never retried, and nobody is woken: the stop is delivered at once -- a run STANDING on the task gets it at the head of one more launch.
The bounds count from the last `team-started`: the cost of every wake-up that answered (ended
or failed), and the wake-ups LAUNCHED under `launches` and `budget-launches`. A wake-up gets its SHARE of
the money: under `budget:`, where the adapter of the launch's grammar declares a cost scope (`COST`),
its intent carries an `allowance` -- min((`budget` - the cost kept) / k, `budget` - the cost kept -
the allowances of the wake-ups under way), k the wake-ups that may play together, min(`parallel`, the
members) -- reserved until its end, and `agent start --max-budget-usd` is the member's RUN cap: what
the run spent (its responses' `cost_usd`) plus the allowance; a member due whose rest is all reserved
is `deferred {reserved}`. Elsewhere no cap goes to `agent start`, and nothing is reserved: no per-wake
cap exists, and a `launch.max_budget_usd` an older journal kept is never passed. A wake-up being one
launch, the cap never falls between two launches: the share is the cap the harness plays under, and
what the launch reports is charged whole at its end.
"""
from __future__ import annotations

import secrets
from pathlib import Path

from house.rules import agent_meta, journal_of
from house.store import locks, now, space_now, tick_now
from declaration.model import TICK_LOCK
from wake.model import TICK_MARK
from tick.model import EMPTIED, VECTOR_REFUSED
from season.rules import is_principal, path_of
from documents.store import member_vector
from task.rules import dues, loud, owed_by, principal_opening, quiet
from rhythm.acts import rung, sounded
from wake.rules import (busy, carrier_name, carrier_of, halted_of, house_failed,
                        open_intents, owed_free, quota_of, renewal_of, run_held, suspicion_of, vector_refused,
                        vectors_of, went)
from wake.faces import histories_of
from wake.store import held_run, messages_cursor
from wake.acts import following, launched, reaped, run_named
from budget.rules import allowance_of, reserved_of
from budget.store import measured
from health.rules import (beat_of, continued_run, relance_of, silences, standing_of, stood,
                          suspected_answers, tried_of, within)
from net.acts import armed, disarmed, relaunch_removed
from journal.store import appended, state_of, written
from tick.rules import (budget_spent_of, deferred_of, launches_bound_of, launches_spent_of, netless,
                        wake_intent_of, wake_launched_of)
from tick.faces import headed


def woken(root: Path, conductor, name: str, journal: Path) -> int:
    """Step 5: each member, in the declaration's order, with messages due on its tasks, no launch of its
    under way and its run not held, is LAUNCHED once -- on the first task, in the tasks' order, that has a
    message for it: the intent WRITTEN FIRST, then the launch, then
    `wake-launched` -- or `wake-failed` when the console launched nothing. Its other tasks wait for
    its next launch, each in the run of its carrier. A run STANDS per (member, task) (its last launch there left it
    waiting for a production: `wake-ended {state: standing}`); each run a member holds standing is RELAUNCHED on its
    task in its turn (`standing_of`: the tasks' order, one launch at a time) as soon as its wake lock is free, while
    it does not park -- on a resolved task ONE launch more, under `CLOSED_HEAD`, then held as parked (s.1409) --, with `[nothing new]` at its head
    when nothing is due -- a CONTINUATION, judged BEFORE any relance: a standing debtor continues, its debts under
    `[you still owe an answer to]`, never with the head of a relance. Before them, the SILENCES (`silences`): each
    member whose silent PASSAGES in a row -- a wake-up and its continuations, parked without one act of its -- on a
    task it owes on reached `silence:` falls -- `silence` written, the member suspected; a continuation counts for
    nothing: a standing run is continued while it does not park, `launches:` and `budget:` its only bounds. A
    member at the bottom of the deadlocked set that OWES an answer and whose continuation launched nothing (no run
    standing) is RELANCED (`relance_of`), without a count: launched on the first task where it owes, its debts for
    messages, under every guard of a launch. Each intent says whether it CONTINUES a standing run (`continued`); a
    WAKE-UP of a member that owes keeps its BEAT (`beat_of`).
    Before all, the failure detector: each SUSPECTED member within its interval is answered for on the messages
    of members (`suspected_answers`) and launched on what a PRINCIPAL says to it alone -- that launch is its try;
    its interval passed, its next message is its try, and a member owing a principal's opening alone is tried by a
    relance on it (`tried_of`). The members play
    in parallel, one run each; `parallel:` bounds the team. `launches:` bounds the launches of one task
    and `budget-launches:` those of the season. A stopped task launches nobody -- but a run STANDING on it,
    launched ONE more time with the stop at its head (`dues`); under `work:` a run RELAUNCHABLE on its standing
    task takes no other task's head (one clone, one task at a time: T7) -- held by that task's
    `launches:` spent, it does, as a run without `work:`: a member's other tasks never starve. A member whose share of the budget is all held by
    the launches under way is deferred; a paused team, or one off season, launches nobody. -> the events written."""
    count = 0
    state = state_of(journal)
    if state.season.paused or state.season.stopped:
        return 0
    started = state.season.started                       # None before the first start: nobody to wake (LA4)
    tagged = set(messages_cursor(root, name, state))
    clock = tick_now()
    count += len(written(conductor, root, journal, name, lambda now_state, events: suspected_answers(now_state, clock)))
    fallen = False
    for agent in list((started.body.agents if started is not None else None) or {}):
        if quota_of(state_of(journal), agent, clock) is not None:
            continue                                             # its provider's limit holds it: launched on no task
        fell = written(conductor, root, journal, name, lambda now_state, events: silences(now_state, name, clock, agent))
        if fell:                                                 # its silence fell: answered for at this very tick
            count += len(fell)
            count += len(written(conductor, root, journal, name, lambda now_state, events: suspected_answers(now_state, clock)))
            fallen = True
        now_state = state_of(journal)
        suspected = within(now_state, agent, clock)              # within its interval: what a principal says to it
        launched_now = 0                                         # launches it -- its try --, nothing else does
        for task, box in dues(now_state, agent):
            if not loud(now_state, box):                         # members' infos alone: they ride the head of its
                continue                                         # next launch, whatever its cause [114]
            if suspected and not any(is_principal(now_state, one.body.sender) for one in box):
                continue
            launched_now += woken_on(root, conductor, name, journal, started, tagged, agent, task)
        count += launched_now
        if suspected:
            continue
        if not launched_now:                                     # nothing received: its try, its continuation, else a relance
            now_state = state_of(journal)
            tried = tried_of(now_state, agent, clock) if suspicion_of(now_state, agent) is not None else None
            continued = 0                                        # each run that stands: relaunched in its turn
            for standing_on in (standing_of(now_state, agent) if tried is None else []):
                continued = woken_on(root, conductor, name, journal, started, tagged, agent, standing_on, standing=True)
                if continued:                                    # one launch at a time
                    break
            count += continued
            if continued:                                        # a standing debtor CONTINUES: never the head of a relance
                continue
            now_state = state_of(journal)
            why = tried or relance_of(now_state, agent)          # a suspect past its interval: its TRY first; then a
            if why is not None:                                  # debtor whose continuation launched nothing (no run stands)
                debts = owed_free(now_state, agent)              # its first debt on a task that does not halt it
                key = next((one for one in debts if principal_opening(now_state, one)), debts[0]) if why[0] == "tried" else debts[0]
                task = now_state.task.messages[key].body.task
                count += woken_on(root, conductor, name, journal, started, tagged, agent, task, relance=why)
    if fallen:                                                   # a fall answered for a member judged already: once more
        count += woken(root, conductor, name, journal)
    return count


def woken_on(root: Path, conductor, name: str, journal: Path, started: dict, tagged: set[str],
             agent: str, task: str, relance: tuple[str, str | None] | None = None, standing: bool = False) -> int:
    """One (member, task) of step 5, judged on the state read again; the house is addressed by
    the member's path. The member's run for the task's CARRIER (`carrier_of`: the task, an occurrence's
    recurrence, a ring's ceremony) is resumed while its slot stands -- a renewal mark an upgrade left
    included --; none yet, its slot gone (`-reset`) or its run dropped (`team reset`), a new run OPENS, told
    the history of the carrier's open tasks, and is NAMED after the carrier (`run_named`) -- as it does when its parked
    run is renewed (`renewal_of`: its context limit reached, or opened under another model or provider than the
    season's; `run-renewed` written with the intent): `wake-launched` keeps the model and the provider of the launch
    (`launch_kept`). A name the house
    refuses is said at `wake-launched` (`name-refused`), the launch plays on. A RELANCE (`relance`: its reason) carries
    the member's debts on the task as its messages and, as its inbox, the members' infos waiting there alone. A STANDING run (`standing`) is
    relaunched on the task it stands on, `[nothing new]` at its head. The intent says `continued` when it resumes a
    run that stood (`stood`) -- its head then carries what varies alone --, and a WAKE-UP of a member that owes
    keeps its `beat` (`beat_of`), said at its head. EVERY launch on a run that stands
    (`continued_run`) is a continuation whatever is due: the stop alone at its head, the messages due waiting for
    its park -- never delivered to a run in the middle of its passage, which would park without a turn on them
    (s.1377) --, and opening the launch after; the TRY of a suspected member alone delivers whatever its run
    (row 108). The launch is ONE launch of the harness (`--launches 1`); its
    `wake-launched` carries the launch's RANK in the run, and its FOLLOWER is spawned to read its flow
    while it plays. A launch the house refuses before any harness is no fall (`house_failed`), and so is one whose
    preparation RAISES once its intent is written: the exception's type and message its cause, the tick goes on to
    its net; a naming that raises is a name refused. -> the events written."""
    count = 0
    state = state_of(journal)
    path = path_of(state, agent)
    if halted_of(state, agent, task) is not None or quota_of(state, agent, tick_now()) is not None:
        return 0                                                 # held by its failures in a row, or by its provider
    if relance is None:
        box, carried = dict(dues(state, agent)).get(task) or [], []
        if continued_run(state, agent, task) and suspicion_of(state, agent) is None:   # its run stands: a
            box = [one for one in box if one.body.verb == "stop"]   # continuation, the stop alone at its head -- the
            #                                                          rest waits for its park and opens the launch after
        if not standing and not loud(state, box):
            return 0                                             # members' infos alone launch nobody [114]
    else:
        box = [one for one in dict(dues(state, agent)).get(task) or [] if quiet(state, one)]   # the infos ride its head
        carried = [key for key in owed_by(state, agent) if state.task.messages[key].body.task == task]
        judged = tried_of(state, agent, tick_now()) if relance[0] == "tried" else relance_of(state, agent)
        if judged != relance or not carried:
            return 0
    if standing and ((agent, task) not in state.wake.standing or run_held(state, agent, task) is None):
        return 0
    if started.body.work and relance is None and any(
            other != task and other not in state.budget.launches_spent for other in standing_of(state, agent)):
        return 0                                                 # under work: a run relaunchable on its standing task takes no
        #                                                          other task's head; held by the task's bound, it does
        #                                                          (no starvation)
    if not (box or carried or standing) or busy(state, agent):
        return 0
    kept = run_held(state, agent, task)                         # the run of the task's carrier
    if kept is not None and held_run(root, conductor, path, kept):
        return 0
    limits = state.season.limits
    per_task = limits.get("launches")
    opened = state.season.started
    since = max(state.task.resumed.get(task, 0),                # a resume, or a season, counts afresh
                int((opened.id if opened is not None else None) or 0))
    task_wakes = sum(1 for tag, one in state.wake.intents.items()
                     if one.body.task == task and int(one.id or 0) > since and went(state, tagged, tag))
    if per_task is not None and task_wakes >= per_task:     # the task's launches are spent
        count += len(appended(conductor, root, journal, name,
                              launches_spent_of(state, started, name, agent, task, task_wakes, per_task)))
        return count
    budget = limits.get("budget")
    if budget is not None and state.budget.cost >= budget:    # the team has spent what it may
        count += len(appended(conductor, root, journal, name, budget_spent_of(state, started, name, agent, task, budget)))
        return count
    total_bound = limits.get("budget-launches")
    since_start = sum(1 for tag, one in state.wake.intents.items()
                      if int(one.id or 0) > int(started.id or 0) and went(state, tagged, tag))
    if total_bound is not None and since_start >= total_bound:   # the costless bound, since the start
        count += len(appended(conductor, root, journal, name,
                              launches_bound_of(state, started, name, agent, task, since_start, total_bound)))
        return count
    parallel = limits.get("parallel")
    if parallel is not None and len(open_intents(state)) >= parallel:
        return len(appended(conductor, root, journal, name, deferred_of(agent, task)))
    allowance = allowance_of(state, started) if measured(root, conductor, started) else None
    if allowance is not None and allowance <= 0:                 # the rest all held by the wake-ups under way
        return len(appended(conductor, root, journal, name, deferred_of(agent, task, reserved_of(state))))
    run = kept
    if run is not None and not conductor.persistence.slot_of(agent_meta(root, path), run).is_file():
        run = None                                               # forgotten (`-reset`): a new run
    renewal = renewal_of(state, agent, task, run)
    if renewal is not None:
        run = None                                               # past its limit, or another model: a new run
    history = histories_of(state, agent, task) if run is None else ""   # an opening is told its carrier's past
    continued = run is not None and stood(state, agent, task)    # it resumes a run that stands: its passage goes on
    beat = None if continued else beat_of(state, agent, task, box)   # a WAKE-UP alone carries the beat
    tag = f"{agent}-{task}-{secrets.token_hex(3)}"
    made = written(conductor, root, journal, name, lambda now_state, events: wake_intent_of(
        now_state, renewal, tag, agent, path, task, run, box, carried, continued, beat, relance, allowance))
    if not made:
        return count                                             # paused meanwhile: nobody woken
    intent = made[-1]
    count += len(made)
    own = member_vector(root, conductor, name, started, agent)
    vectors, code = vectors_of(state, agent, task) + ([own] if own else []), ""
    try:                                                         # the intent written: what raises before the launch
        fresh = state_of(journal)                                # is the house's refusal, never the tick's death
        report, why, code = launched(root, conductor, name, started, path, run, tag,
                                   headed(name, agent, box, history, fresh, relance, task, continued, beat), allowance,
                                   member=agent, vectors=vectors or [EMPTIED])
    except Exception as error:                                   # noqa: BLE001 -- any cause, said whole
        report, why = None, f"{type(error).__name__}: {error}"
    if report is None and vectors and code == VECTOR_REFUSED:    # the launcher refused the run its node: said, final
        return count + len(appended(conductor, root, journal, name, vector_refused(state_of(journal), intent, why, vectors)))
    if report is None:                                           # the house refused, before any harness: no fall
        return count + len(appended(conductor, root, journal, name, house_failed(state_of(journal), name, intent, why)))
    born = space_now()
    try:                                                         # launched: a naming that raises is a name refused
        refused = "" if run else run_named(root, conductor, path, str(report.get("key")), carrier_name(fresh, name, carrier_of(fresh, task)))
    except Exception as error:                                   # noqa: BLE001 -- the launch plays on unnamed
        refused = f"{type(error).__name__}: {error}"
    made = written(conductor, root, journal, name, lambda now_state, events: wake_launched_of(
        now_state, started, tag, agent, report, born, refused))   # `born`: the launcher's process space, this tick's own
    following(root, conductor, name, tag)
    return count + len(made)


def ticked(root: Path, conductor, name: str, hint: tuple[str, str] | None = None) -> int:
    """ONE advance of the team under `tick.lock`, taken without waiting: held, the mark is
    posted and the tick leaves; the holder clears the mark, ARMS the timer on the deadline the state read now
    gives (`armed`) -- a tick killed at any point after it, in a launch above all, leaves its net standing --, plays
    reap, ring, wake and the net again (the relaunch entry removed and the timer disarmed at `schedule-off`,
    the timer armed again when a deadline stands: an earlier hour replaces the standing one, a later one keeps it),
    releases, then reads the mark and plays again when it is set. Off season it reaps alone and the net leaves.
    `hint` is what an on-end tick carries of the
    launch that fired it: `(run, state)`. -> the events written."""
    journal = journal_of(root, name)
    if state_of(journal).season.started is None:
        print(f"pp-team: {name} · not started: nothing to advance")
        return 0
    lock = locks(conductor)
    home = journal.parent
    home.mkdir(parents=True, exist_ok=True)
    path, mark = home / TICK_LOCK, home / TICK_MARK
    lease = lock.try_(path)
    if lease is None:
        try:
            with open(mark, "x", encoding="utf-8") as handle:
                handle.write(now() + "\n")
        except FileExistsError:
            pass
        lease = lock.try_(path)
        if lease is None:
            print(f"pp-team: {name} · a tick plays: marked pending")
            return 0
    count, rounds = 0, 0
    while True:
        mark.unlink(missing_ok=True)
        rounds += 1
        count += armed(root, conductor, name, journal)   # 0. the net first: a tick killed past here leaves its timer
        count += reaped(root, conductor, name, journal, hint)
        hint = None
        if not state_of(journal).season.stopped:   # off season: the ends reaped, nothing rung, sounded or woken
            count += rung(conductor, root, name, journal)
            count += sounded(conductor, root, name, journal)
            count += woken(root, conductor, name, journal)
        if netless(state_of(journal)):             # 7. the net, under the lock: a tick that arms and one that
            relaunch_removed(root, conductor, name)   # disarms never cross -- the condition of schedule-off: the
            disarmed(root, name)                   # net leaves with it
        else:
            count += armed(root, conductor, name, journal)   # the timer, when a deadline stands
        lock.release(lease)
        if not mark.exists():
            break
        lease = lock.try_(path)
        if lease is None:
            break                                              # the tick that marked plays now
    print(f"pp-team: {name} · tick · {count} event(s) written in {rounds} round(s)")
    if state_of(journal).season.paused:
        print(f"pp-team: {name} · paused: nobody woken until team resume")
    return count
