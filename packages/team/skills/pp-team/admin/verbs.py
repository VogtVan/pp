"""The `admin` domain, layer `verbs`: the command line of the verbs that delete or rename a team.

A definition belongs here when it plays such a verb or reads its arguments: it removes a team and what it made, or moves
it to a new name, and refuses with the usage. What a delete writes first is decided by `admin/rules.py`, and the verb
says the sentence of its refusal. A verb is where the skill meets its caller: it may print, end the call and use every
other layer.
"""
from __future__ import annotations

import json
import os
import shutil

from house.model import BORDER, HOUSE, TEAMS, TEAM_DOC, USAGE, Declined
from house.rules import agent_meta, journal_of, team_doc, team_root
from house.store import house, lines_of, locks, named_team, placed, refuse
from house.verbs import flags
from declaration.model import TICK_LOCK
from admin.model import DELETE_FLAGS, RENAME_FLAGS
from admin.rules import deleting_of
from declaration.acts import declared_paths, team_name
from documents.rules import document_name
from wake.rules import open_intents, purged_already, team_runs
from wake.acts import agent_removed, purged
from net.store import call_wait
from net.acts import disarmed, relaunch_removed, relaunch_standing, timer_standing
from journal.store import state_of, written


def agents_asked(rest: list[str]) -> tuple[list[str], list[str]]:
    """-> (the paths `--agent <path>` names, in their order, each once; the rest of the flags)."""
    paths, kept, index = [], [], 0
    while index < len(rest):
        if rest[index] == "--agent":
            if index + 1 >= len(rest) or rest[index + 1].startswith("--"):
                refuse(USAGE)
            paths.append(rest[index + 1])
            index += 2
            continue
        kept.append(rest[index])
        index += 1
    return list(dict.fromkeys(paths)), kept


def delete_verb(rest: list[str]) -> int:
    """`team delete <name> [--agent <path>]... [--yes] [--json]`: removes the team and what it made -- its timer, its
    relaunch entry, every run its wake-ups opened (by `agent purge`, at each agent), its journal and the files beside
    it, then its directory, the owner's declaration and documents with it -- and, under `--agent`, the agents named
    (by `agent remove`, after the purge of the runs and before the directory goes). An agent named must be one the
    dry face lists under `agents` -- declared by this team and by no other, and one `agent remove` takes away: never
    `HOUSE` -- else `agent-kept` for `HOUSE`, `agent-shared` for the others, judged before any write; the purge of
    the team's runs plays at every agent, `HOUSE` too. Without `--yes` it says what it would remove and writes
    nothing. Judged under `tick.lock` waited within `call_lock_wait` (`team-busy` beyond) and held to the end:
    `team-unknown`, `team-busy` while a task is open or a wake-up plays. Under `--yes`, the tasks are judged again
    and `deleting` written in ONE section of the journal's lock, before anything is removed: a task a post wrote meanwhile -- a post takes the journal's lock alone --
    refuses `team-busy`, nothing written, the timer, the relaunch entry and the runs in place; once `deleting` stands,
    every writer that opens work -- a post, a start, a resume, a ring -- refuses `team-deleting`, the tick rings and
    sounds nothing, and the team's guard lets its runs go. A purge or a removal refused stops the verb, said --
    `delete` played again goes on: a run its agent no longer knows (`run-unknown`) was purged the first time. The
    journal's directory and the team's directory leave last, under `tick.lock`; a write that comes after finds no
    declaration (`written`). The agents not named stay: the ones no other team declares are said."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    wanted, rest = agents_asked(rest)
    asked = flags(rest, DELETE_FLAGS)
    directory = team_root(root, name)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    journal = journal_of(root, name)
    lock = locks(conductor)
    lease = None
    if journal.parent.is_dir():
        lease = lock.acquire(journal.parent / TICK_LOCK, wait=call_wait(root, conductor))
        if lease is None:
            refuse(f"team-busy -- a tick of {name} holds {TICK_LOCK} past call_lock_wait: nothing removed, "
                   "replay once it has played.")
    try:
        state = state_of(journal)
        events = lines_of(journal) if journal.is_file() else []
        opened = [one.id for one in state.task.tasks.values() if one.state == "open"]
        if opened or open_intents(state):
            refuse(f"team-busy -- {name} is at work ({', '.join(opened) or 'a wake-up plays'}): stop it first "
                   f"(`team stop {name} --kill`), then delete it.")
        runs = team_runs(state, events)
        relaunch = relaunch_standing(root)
        timer = bool(timer_standing(root, name))
        started = state.season.started
        mine = set((started.body.agents or {}).values()) if started is not None else set()
        mine |= declared_paths(root, conductor, name)
        home = root.parent / TEAMS
        others: set[str] = set()
        for other in (sorted(one.name for one in home.iterdir() if (one / TEAM_DOC).is_file()) if home.is_dir() else []):
            if other != name:
                others |= declared_paths(root, conductor, other)
        agents = sorted(one for one in mine - others if one != HOUSE)
        kept = [one for one in wanted if one == HOUSE]
        if kept:
            refuse(f"agent-kept -- {', '.join(kept)}: `agent remove` never removes this agent: leave it out of `--agent`; "
                   f"the agents the team can remove are {', '.join(agents) or 'none'}; nothing removed.")
        shared = [one for one in wanted if one not in agents]
        if shared:
            refuse(f"agent-shared -- {', '.join(shared)}: not an agent {name} alone declares (another team declares it, "
                   f"or none does); the agents the team may take away are {', '.join(agents) or 'none'}; nothing removed.")
        told = {"team": name, "name": team_name(root, conductor, name), "dry": not asked["yes"],
                "directory": str(directory.relative_to(root.parent)),
                "journal": str(journal.parent.relative_to(root.parent)) if journal.parent.is_dir() else None,
                "relaunch": relaunch, "timer": timer, "runs": runs, "agents": agents, "removed": []}
        if asked["yes"]:
            def judge(now: dict, lines: list[dict]) -> list[dict]:
                try:
                    return deleting_of(now)
                except Declined as declined:
                    at_work, = declined.args[1:]
                    refuse(f"team-busy -- {name} is at work ({', '.join(at_work) or 'a wake-up plays'}): stop it "
                           f"first (`team stop {name} --kill`), then delete it.")

            if journal.is_file():
                written(conductor, root, journal, name, judge)
            disarmed(root, name)
            if relaunch:
                relaunch_removed(root, conductor, name, but=name)
            by_path: dict[str, list[str]] = {}
            for one in runs:
                by_path.setdefault(one["path"], []).append(one["run"])
            for path, keys in by_path.items():
                if not agent_meta(root, path).is_dir():
                    continue
                why = purged(root, conductor, path, keys)
                gone = purged_already(why)
                if gone and set(keys) - gone:              # a delete taken up: what an earlier one purged is gone
                    why = purged(root, conductor, path, [one for one in keys if one not in gone])
                elif gone:
                    why = ""
                if why:
                    refuse(f"delete-failed -- the purge of {', '.join(keys)} at {path} refused: {why} -- nothing more "
                           f"removed; `team delete {name} --yes` again goes on")
            for path in wanted:
                if not agent_meta(root, path).is_dir():
                    continue
                why = agent_removed(root, conductor, path)
                if why:
                    refuse(f"delete-failed -- the removal of {path} refused: {why} -- nothing more removed; "
                           f"`team delete {name} --yes` again goes on")
                told["removed"].append(path)
            shutil.rmtree(journal.parent, ignore_errors=True)
            shutil.rmtree(directory, ignore_errors=True)
    finally:
        if lease is not None:
            lock.release(lease)
    if asked["json"]:
        print(json.dumps(told, ensure_ascii=False))
        return 0
    verb = "removed" if asked["yes"] else "would remove"
    print(f"pp-team: {name} · {verb}: {told['directory']}" + (f", {told['journal']}" if told["journal"] else "")
          + (", the relaunch entry" if relaunch else "") + (", the timer" if timer else "")
          + (f", {len(runs)} run(s): " + ", ".join(f"{one['path']} {one['run']}" for one in runs) if runs else ""))
    if told["removed"]:
        print(f"pp-team: {name} · the agents removed: {', '.join(told['removed'])}")
    staying = [one for one in agents if one not in told["removed"]]
    if staying:
        print(f"pp-team: {name} · the agents stay: {', '.join(staying)} -- no other team declares them"
              + ("" if asked["yes"] else f" (`--agent <path>` takes one away)"))
    if not asked["yes"]:
        print(f"pp-team: {name} · nothing written -- `team delete {name} --yes` removes it")
    return 0


def rename_verb(rest: list[str]) -> int:
    """`team rename <name> <new> [--json]`: moves the team to a new directory name -- its identity. Judged before any
    write: `new` as a team's name (`team-invalid`), `team-unknown`, `team-exists` when `teams/<new>/` or the records of
    `<new>` stand, `team-busy` under `tick.lock` past `call_lock_wait` or while a task is open or a wake-up plays.
    Then, the lock held: the timer disarmed (the next tick arms it again), `teams/<name>/` moved to `teams/<new>/`
    with the intention `TEAM-<name>.md` renamed `TEAM-<new>.md` inside it, the records of the team (its journal and
    the files beside it) moved, and `name:` of `TEAM.md` rewritten when it was the old directory's name -- a name of
    the owner's own stays. The house's relaunch entry does not change; the members' entries are laid again at the
    next start. Under `--json` ONE object `{from, to, name}`."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    new, rest = named_team(conductor, rest)
    asked = flags(rest, RENAME_FLAGS)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    directory, target = team_root(root, name), team_root(root, new)
    journal, moved = journal_of(root, name), journal_of(root, new)
    if new == name or target.exists() or moved.parent.exists():
        refuse(f"team-exists -- {target} or its records stand already: another name.")
    lock = locks(conductor)
    lease = None
    if journal.parent.is_dir():
        lease = lock.acquire(journal.parent / TICK_LOCK, wait=call_wait(root, conductor))
        if lease is None:
            refuse(f"team-busy -- a tick of {name} holds {TICK_LOCK} past call_lock_wait: nothing moved, "
                   "replay once it has played.")
    try:
        state = state_of(journal)
        opened = [one.id for one in state.task.tasks.values() if one.state == "open"]
        if opened or open_intents(state):
            refuse(f"team-busy -- {name} is at work ({', '.join(opened) or 'a wake-up plays'}): stop it first "
                   f"(`team stop {name} --kill`), then rename it.")
        shown = team_name(root, conductor, name)
        disarmed(root, name)
        own = directory / document_name(name)
        if own.is_file() and not (directory / document_name(new)).exists():
            os.replace(own, directory / document_name(new))
        if journal.parent.is_dir():
            moved.parent.parent.mkdir(parents=True, exist_ok=True)
            os.replace(journal.parent, moved.parent)
        os.replace(directory, target)
    finally:
        if lease is not None:
            lock.release(lease)
    if shown == name:
        doc = team_doc(root, new)
        text = doc.read_text(encoding="utf-8")
        lines = text.split("\n")
        end = lines.index(BORDER, 1) if BORDER in lines[1:] else 0
        for index in range(1, end):
            if lines[index].rstrip() == f"name: {name}":
                lines[index] = f"name: {new}"
                placed(doc, "\n".join(lines).encode("utf-8"))
                break
        shown = new
    if asked["json"]:
        print(json.dumps({"from": name, "to": new, "name": shown}, ensure_ascii=False))
        return 0
    print(f"pp-team: {name} · renamed {new} · {TEAMS}/{new}/ and its records moved"
          + (f" · name: {shown}" if shown == new else f" · shown as {shown}"))
    return 0
