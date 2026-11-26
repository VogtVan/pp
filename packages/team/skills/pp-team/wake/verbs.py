"""The `wake` domain, layer `verbs`: the command line of the verbs that follow, read and guard the wake-ups.

A definition belongs here when it plays such a verb: it follows one launch to its end and ticks (`followed`), lifts a
provider's limit that holds a member (`quota_lifted`, which `team resume --quota` calls: judged before and after the
hour is read, the event written, a tick played), prints the answers the members gave as lines or as JSON, forgets every
run of a member and writes the `run-reset` a rule composes, answers whether a run may be purged, and refuses with the
usage. A verb is where the skill meets its caller: it may print, end the call and use every other layer.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

from pathlib import Path

from house.model import TEAMS, TEAM_DOC, USAGE, Declined
from house.rules import journal_of, team_doc
from house.store import engine_of, house, locks, machine_house, named_team, owner_of, refuse, tick_now
from house.verbs import flags
from declaration.model import TICK_LOCK
from wake.model import RESET_FLAGS, RESPONSES_FLAGS, TICK_MARK
from season.rules import is_member, path_of
from season.faces import off_season
from task.faces import principal_unknown
from wake.rules import (busy, ended_from_flow, measured_of, opened_by, path_of_intent, quota_lift_asked,
                        quota_lift_of, reset_of)
from wake.store import held_run
from wake.acts import act_routed, awaits_of, ending, forgotten, words_of
from net.store import call_wait
from net.acts import netted
from journal.faces import deleting_said, harmless
from journal.store import appended, state_of, written
from tick.rules import netless
from tick.acts import ticked


def follow(rest: list[str]) -> int:
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    if len(rest) != 1 or rest[0].startswith("--"):
        refuse(USAGE)
    journal = journal_of(root, name)
    if not journal.is_file():
        refuse(f"team-not-started -- {name} was never started.")
    count = followed(root, conductor, name, journal, rest[0])
    print(f"pp-team: {name} · follow {rest[0]} · {count} act(s) routed")
    return 0


def responses_verb(rest: list[str]) -> int:
    """`team responses`: what the team's members said, one per `wake-ended`, the words of its launch read
    at the run's flow by the house's console; `--since`, `--agent`, `--task` filter, `--last` cuts; under
    `--json` one object per end, its text whole or `null`. Nothing written."""
    root, conductor = machine_house()                      # the house's team, whatever instance reads it
    name, rest = named_team(conductor, rest)
    asked = flags(rest, RESPONSES_FLAGS)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    state = state_of(journal_of(root, name))
    if state.season.started is None:
        refuse(f"team-not-started -- {name} was never started.")
    numbers: dict[str, int] = {}
    for flag in ("since", "last"):
        if asked[flag] is not None:
            try:
                numbers[flag] = int(asked[flag])
            except ValueError:
                numbers[flag] = -1
            if numbers[flag] < 0:
                refuse(f"{flag}-invalid -- `--{flag} {asked[flag]}`: a whole number of 0 or more.")
    chosen = []
    for one in state.wake.ends:
        task = intent.body.task if (intent := state.wake.intents.get(one.body.tag)) is not None else None
        if "since" in numbers and one.id <= numbers["since"]:
            continue
        if asked["agent"] is not None and one.body.agent != asked["agent"]:
            continue
        if asked["task"] is not None and task != asked["task"]:
            continue
        chosen.append((one, task))
    if "last" in numbers:
        chosen = chosen[-numbers["last"]:] if numbers["last"] else []
    for one, task in chosen:
        intent = state.wake.intents.get(one.body.tag)
        at = path_of_intent(state, intent) if intent is not None else path_of(state, str(one.body.agent))
        text = words_of(root, conductor, at, str(one.body.run or ""), one.body.launch)
        if asked["json"]:
            print(json.dumps({"id": one.id, "member": one.body.agent, "path": at, "task": task,
                              "run": one.body.run, "launch": one.body.launch, "at": one.at,
                              "cost_usd": one.body.cost, "response": text}, ensure_ascii=False))
            continue
        print(f"#{one.id} {one.body.agent} on {task} · run {one.body.run}")
        print(harmless(text) if text is not None else "(response missing at the record)")
        print()
    return 0


def reset_verb(rest: list[str]) -> int:
    """`team reset <name> [--member <m>]`: every run of each member named -- every member without
    `--member` -- forgotten by its agent's console, one `run-reset {member, run}` per run; the next
    wake-up of the member on a task opens a new run, a new session, told the history of that task's carrier.
    Judged before anything is forgotten, under `tick.lock` waited within `call_lock_wait`
    (`team-busy` beyond) and held to the last write: no tick launches on a key being forgotten.
    A member without a run is said, nothing written for it; an agent's console that refuses stops
    the verb, the members forgotten before it written."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    asked = flags(rest, RESET_FLAGS)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    journal = journal_of(root, name)
    journal.parent.mkdir(parents=True, exist_ok=True)
    lock = locks(conductor)
    lease = lock.acquire(journal.parent / TICK_LOCK, wait=call_wait(root, conductor))
    if lease is None:
        refuse(f"team-busy -- a tick of {name} holds {TICK_LOCK} past call_lock_wait: nothing forgotten, "
               "replay once it has played.")
    said: list[str] = []
    try:
        state = state_of(journal)
        if state.season.started is None:
            refuse(f"team-not-started -- {name} was never started: nothing to forget.")
        members = list((state.season.started.body.agents or {}))
        if asked["member"] is not None:
            if not is_member(state, asked["member"]):
                refuse(f"participant-unknown -- `{asked['member']}` is no member of {name}.")
            members = [asked["member"]]
        for member in members:
            runs = list(dict.fromkeys((state.wake.runs.get(member) or {}).values()))
            held = next((run for run in runs if held_run(root, conductor, path_of(state, member), run)), None)
            if busy(state, member) or held is not None:
                refuse(f"member-running -- a wake-up of {member} plays" + (f" in run {held}" if held else "")
                       + ": nothing forgotten, replay once it has ended.")
        for member in members:
            runs = list(dict.fromkeys((state.wake.runs.get(member) or {}).values()))
            if not runs:
                said.append(f"{member} · no run to forget")
            for run in runs:                                     # every run of the member, one per carrier
                why = forgotten(root, conductor, path_of(state, member), run)
                if why:
                    for line in said:
                        print(f"pp-team: {name} · {line}")
                    refuse(f"reset-failed -- the console of {path_of(state, member)} kept run {run}: {why}")
                made = appended(conductor, root, journal, name, reset_of(member, run))
                said.append(f"{member} · run {run} forgotten (run-reset #{made[0].id})")
    finally:
        lock.release(lease)
    for line in said:
        print(f"pp-team: {name} · {line}")
    if (journal.parent / TICK_MARK).exists():
        ticked(root, conductor, name)              # a tick asked while the reset held the lock plays now
    return 0


def guard_verb(rest: list[str]) -> int:
    """`pp-team guard` (the vector on stdin): the GUARDIAN of the family `agent-run:<path>/<key>` -- the
    engine's call when `agent purge` asks before removing a run. A run a member of a LIVING team holds (the
    team started, a task open or a ceremony declared, and no `deleting` written) refuses, the team, the member and `team reset` named:
    purged, the member's next wake-up would find no run. Reads only, no lock."""
    if rest:
        refuse(USAGE)
    root, conductor = house()
    prefix, _, ident = conductor.reading.piped().strip().partition(":")
    if prefix != "agent-run":
        refuse(f"family-foreign -- `{prefix}:` is not a family this package guards (agent-run)")
    path, _, key = ident.rpartition("/")
    home = root.parent / TEAMS
    for name in sorted(one.name for one in home.iterdir() if (one / TEAM_DOC).is_file()) if home.is_dir() else []:
        journal = journal_of(root, name)
        if not journal.is_file():
            continue
        state = state_of(journal)
        if state.season.started is None or netless(state) or state.season.deleting:
            continue
        for member, run in ((member, run) for member, held in state.wake.runs.items() for run in held.values()):
            if run == key and path_of(state, member) == path:
                refuse(f"member-run -- run {key} of {path} is the run of member {member} of team {name}, "
                       f"which lives: `team reset {name} --member {member}` first, or wait for the team's end")
    return 0


def followed(root: Path, conductor, name: str, journal: Path, tag: str) -> int:
    """`team follow <name> <tag>`: the FOLLOWER of one launch -- keeps ONE `agent flow <path> <run> --json
    --from <rank> --follow` open on the launch's flow, from the rank the journal last kept of the run (from 1
    when it kept none), finds the exchange the launch OPENED by its tag (`opened_by`) and reads what it
    streams line by line: each `words` of that exchange that is an act routed as it comes (`act_routed`, once
    by its rank), the team ticked after it (an act may wake another member); at the exchange's `verdict` the
    launch's END is written (`ended_from_flow`) and the team ticked, and the follower leaves -- as it does when
    the stream ends (no launch plays and nothing comes), or when the intent is ended in the journal. A stream
    that ends at the `verdict` of an EARLIER exchange, before the launch's `opened`, is opened again from the
    rank reached while the launch's wake lock is held. Spawned detached by the tick at every launch, outside
    the tick's lock. -> the acts it routed."""
    state = state_of(journal)
    intent, launch = state.wake.intents.get(tag), state.wake.launched.get(tag)
    run = str((launch.body.run if launch is not None else None) or "")
    if intent is None or not run or tag in state.wake.ended:
        return 0
    path = path_of_intent(state, intent)
    engine = engine_of(root, conductor)
    told = {"ended": False, "response": None, "verdict": None, "cost": 0.0, "context": None,
            "rank": int(state.wake.flow.get(run) or 0)}
    routed_count, ordinal, opened = 0, 0, False
    while True:
        start = told["rank"] + 1
        stream = subprocess.Popen([sys.executable, str(engine), "--instance", str(root), "agent", "flow", path, run,
                                   "--json", "--from", str(start), "--follow"],
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, cwd=str(root.parent),
                                  env=dict(os.environ))
        assert stream.stdout is not None
        for rank, line in enumerate(stream.stdout, start):
            if not line.strip():
                continue
            try:
                one = json.loads(line)
            except ValueError:
                continue
            kind = one.get("kind")
            told["rank"] = rank
            if kind == "opened":                   # the launch's own exchange opens here, by its tag: what
                ordinal, opened = 0, opened_by(one, tag)   # stands before it is an earlier one's, never routed
            if not opened:
                continue
            if kind == "words":
                ordinal += 1
                if act_routed(conductor, root, journal, name, tag, rank, ordinal, str(one.get("text") or "")):
                    routed_count += 1
                    ticked(root, conductor, name)
            elif kind == "agent":
                cost = one.get("cost_usd")
                if isinstance(cost, (int, float)) and not isinstance(cost, bool):
                    told["cost"] = round(told["cost"] + float(cost), 6)
            elif kind == "context":
                told["context"] = measured_of(one)
            elif kind == "response":
                told["response"] = one
            elif kind == "verdict":
                told["verdict"], told["ended"] = one, True
                break
        stream.stdout.close()
        stream.wait()
        if told["ended"] or opened or not held_run(root, conductor, path, run):
            break                                  # over; or the launch's exchange seen or gone: the reap reads on
    if told["ended"]:                               # the launch is over: its end written here, the tick after
        state = state_of(journal)
        if tag not in state.wake.ended and tag in state.wake.intents:
            ending(conductor, root, journal, name, tag,
                   ended_from_flow(state, state.wake.intents[tag], state.wake.launched.get(tag), told, None,
                                   (None, False) if told.get("response") else awaits_of(root, conductor, path, run)))
        ticked(root, conductor, name)
    return routed_count


def quota_lifted(root: Path, conductor, name: str, asked: dict) -> int:
    """`team resume <name> --quota [--member <member>] [--as <principal>] [--no-tick]`: the provider's limit lifted by
    the owner -- the member's, or every member's a limit holds now, dated or not --, judged under the journal's lock:
    `team-unknown`, `team-not-started`, `team-deleting`, `season-stopped`, `principal-unknown`, `member-unknown` (a
    member the season under way does not know), `quota-not-held` (no limit holds the member, or nobody); then ONE
    `quota-lifted {by, members}`, the relaunch entry laid again, and a tick unless `--no-tick`: each member lifted is
    launched on what waits for it (s.1811, team 1.35.11)."""
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    journal = journal_of(root, name)

    def judge(state: dict, events: list[dict]) -> list[dict]:
        try:
            sender, named = quota_lift_asked(state, owner, asked["member"], asked["as"])
            return quota_lift_of(state, sender, asked["member"], named, tick_now())
        except Declined as declined:
            code, *data = declined.args
            if code == "team-not-started":
                refuse(f"team-not-started -- {name} was never started.")
            if code == "team-deleting":
                refuse(deleting_said(name))
            if code == "season-stopped":
                refuse(off_season(name, state))
            if code == "principal-unknown":
                refuse(principal_unknown(*data))
            if code == "member-unknown":
                member, agents = data
                refuse(f"member-unknown -- `{member}`: the season of `{name}` knows {', '.join(agents) or 'nobody'}.")
            if code == "quota-not-held":
                member, = data
                refuse(f"quota-not-held -- no provider's limit holds {member or 'a member of ' + name} now: "
                       "nothing to lift.")
            raise ValueError(f"no sentence for the refusal `{code}`")

    made = written(conductor, root, journal, name, judge)[0]
    print(f"pp-team: {name} · quota-lifted #{made.id} {', '.join(made.body.members)} by {made.body.by}")
    netted(root, conductor, name, state_of(journal))   # the members free again: the net laid again when gone
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0
