"""The `wake` domain, layer `acts`: what the team does to its agents and their runs -- the effects played, the
events written.

A definition belongs here when it plays an effect of several steps through the house's console or the system: it creates
the agents a team lacks, launches a wake-up, starts its follower, reads a run's flow and routes what a launch said,
reaps the launches that ended, finds the launches nobody holds (`unproven`), names, forgets or purges a run, removes an
agent, or ends a launcher with everything it runs. The follower of one launch and a provider's limit lifted, which play
a tick and which only verbs call, are verbs (`followed`, `quota_lifted`, `wake/verbs.py`). It decides none of the events
it writes: it reads or plays the effect, hands what it found to a decision of `wake/rules.py`, and writes -- through the
journal's writer -- the bodies the decision composes; when a decision needs something read after its first judgement,
such as the hour, the act reads it between two decisions. It may use the lower layers of any domain.
"""
from __future__ import annotations

import json
import os
import shlex
import signal
import subprocess
import sys
from pathlib import Path

from house.model import HOUSE
from house.rules import agent_meta, journal_of, team_root
from house.store import engine_of, foreign, launch_of, locks, refuse
from season.model import PROFILE_KEYS
from wake.model import FOLLOW_LOG, MEMBER_TYPE, REFUSAL_CODE
from season.rules import profile_of
from season.acts import season_played
from task.rules import candidates_of
from wake.rules import (act_judged, ended_from_flow, ended_stopped, failed, foreign_ended, kill_verdict,
                        kills_written, launch_flags, launch_found, measured_of, open_intents, opened_by, path_of_intent,
                        spent_on)
from wake.store import aged, material_of, messages_cursor
from net.store import apart
from journal.store import appended, state_of, written


# --- the agents, by the house's console ----------------------------------------------------

def born(root: Path, conductor, paths: list[str]) -> list[str]:
    """Creates the agents the house lacks by the house's own console, `agent add <path> --type member`: an
    instance at each path under the house that BORROWS the house's machine, no door, its
    SETTINGS at the cap and the member's profile `add` writes (its boot without the catalog of skills nor
    the threads' pass) -- each path once, however many members it plays -- never
    by an import of another package's script; the house (`HOUSE`) is never added. `add` plays
    under the house's BIRTH lock for the path (`born-busy` past `call_lock_wait`): two starts that
    name one new path give it birth once, the other reads `agent-exists`. -> the paths born."""
    engine = engine_of(root, conductor)
    made = []
    for name in dict.fromkeys(paths):
        if name == HOUSE or conductor.instance.is_instance(agent_meta(root, name)):
            continue
        added = subprocess.run([sys.executable, str(engine), "--instance", str(root), "agent", "add", name,
                                "--type", MEMBER_TYPE],
                               capture_output=True, text=True, cwd=str(root.parent), env=dict(os.environ))
        if added.returncode == 0:
            made.append(name)
        elif "agent-exists" not in added.stderr:
            refuse(f"agent-add-failed -- `{name}` could not be born under the house: "
                   f"{(added.stderr or added.stdout).strip()[-300:]}")
    return made


# --- the flow of a launch: read by agent's face, routed as it comes ------------------------------

def flow_lines(root: Path, conductor, path: str, run: str, start: int) -> list[tuple[int, dict]]:
    """-> the lines of the run's flow from the rank `start` on (the first line is 1), each with its rank,
    read by the house's own console: `agent flow <path> <run> --json --from <start>` -- the one way the
    tick reads what a launch says, never the file. A console that refuses (a run the agent forgot)
    reads as nothing."""
    engine = engine_of(root, conductor)
    played = subprocess.run([sys.executable, str(engine), "--instance", str(root), "agent", "flow", path, run,
                             "--json", "--from", str(max(1, start))], capture_output=True, text=True,
                            cwd=str(root.parent), env=dict(os.environ))
    if played.returncode != 0:
        return []
    found = []
    for offset, line in enumerate(played.stdout.splitlines()):
        if not line.strip():
            continue
        try:
            found.append((max(1, start) + offset, json.loads(line)))
        except ValueError:
            continue
    return found


def flow_read(root: Path, conductor, name: str, journal: Path, tag: str) -> dict:
    """Reads the flow of the launch `tag` from the rank the journal last kept of the run (from 1 when it kept
    none), finds the exchange the launch OPENED by its tag (`opened_by`) and routes every `words` of that
    exchange that reads as an act, in order (`act_routed`); nothing before that `opened` is routed. -> what the
    flow said of the launch's END: `{"ended", "response", "verdict", "cost", "context", "rank"}` -- `ended` once its
    `verdict` line stands (the house wrote the end of the exchange before it gave the wake lock back), `response`
    the `response` line's fields when one was kept, `cost` the sum of the `agent` events' costs, `context` the last
    `context` the exchange said (`measured_of`), `rank` the last line read. Nothing written beyond the routing."""
    state = state_of(journal)
    intent, launch = state.wake.intents.get(tag), state.wake.launched.get(tag)
    run = str((launch.body.run if launch is not None else None) or "")
    path = path_of_intent(state, intent)                    # None when no intent holds the tag: its member's path
    told = {"ended": False, "response": None, "verdict": None, "cost": 0.0, "context": None,
            "rank": int(state.wake.flow.get(run) or 0)}
    if not run:
        return told
    ordinal, opened = 0, False
    for rank, one in flow_lines(root, conductor, path, run, told["rank"] + 1):
        kind = one.get("kind")
        told["rank"] = rank
        if kind == "opened":                       # the launch's own exchange opens here, by its tag: what
            ordinal, opened = 0, opened_by(one, tag)   # stands before it is an earlier one's, never routed
        if not opened:
            continue
        if kind == "words":
            ordinal += 1
            act_routed(conductor, root, journal, name, tag, rank, ordinal, str(one.get("text") or ""))
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
    return told


def following(root: Path, conductor, name: str, tag: str) -> None:
    """Spawns the follower of the launch `tag`, detached -- its own session, its output appended to
    `follow.log` beside the journal --: the tick that launched it goes on."""
    engine = engine_of(root, conductor)
    log = journal_of(root, name).parent / FOLLOW_LOG
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("ab") as handle:
        subprocess.Popen([sys.executable, str(engine), "--instance", str(root), "team", "follow", name, tag],
                         stdin=subprocess.DEVNULL, stdout=handle, stderr=handle, cwd=str(root.parent),
                         env=dict(os.environ), **apart())


def answered_in_flow(root: Path, conductor, state: dict, intent: dict, launch: dict) -> bool:
    """-> whether the launch's flow carries the END of its exchange (a `response` line after the `opened` that
    carries the launch's tag): a wake-up that answered -- the kill spares it, the reap ends it with its cost."""
    run = launch.get("run")
    if not run:
        return False
    start = int(state.wake.flow.get(str(run)) or 0) + 1
    opened = False
    for _, one in flow_lines(root, conductor, path_of_intent(state, intent), str(run), start):
        if one.get("kind") == "opened":
            opened = opened_by(one, str(intent.body.tag))
        if opened and one.get("kind") == "response":
            return True
    return False


def awaits_of(root: Path, conductor, path: str, run: str) -> tuple[str | None, bool]:
    """-> (what the run's stack awaits, whether its harness session stands), read at agent's FACE (`agent
    status <path> --json`: `awaits`, `session`): `standing` (a production: the run is relaunched) or `parked`
    (a message); (None, False) when the face says nothing of that run. The one reading of a run's state a
    launch without a response leaves -- never deduced from the failure; the run is resumed only with its
    session (a launch killed before its harness said anything left none: `session-missing` otherwise)."""
    engine = engine_of(root, conductor)
    played = subprocess.run([sys.executable, str(engine), "--instance", str(root), "agent", "status", path, "--json"],
                            capture_output=True, text=True, cwd=str(root.parent), env=dict(os.environ))
    for line in played.stdout.splitlines():
        try:
            one = json.loads(line)
        except ValueError:
            continue
        if one.get("run") == run and one.get("awaits") in ("message", "production"):
            return ("parked" if one["awaits"] == "message" else "standing"), bool(one.get("session"))
    return None, False


def act_routed(conductor, root: Path, journal: Path, name: str, tag: str, rank: int, ordinal: int, text: str) -> list[dict]:
    """ONE `words` of a launch, routed under the journal's lock -- once: a `wake-routed` of the tag at
    that rank standing, nothing is written again (the follower and the tick read the same flow). Its CANDIDATES
    (`candidates_of`) are judged by `act_judged`; a `words` without a candidate writes nothing. -> the events
    written."""
    found = candidates_of(text)
    if not found:
        return []
    return written(conductor, root, journal, name,
                   lambda state, events: act_judged(state, name, tag, rank, ordinal, found))


def ending(conductor, root: Path, journal: Path, name: str, tag: str, events: list[dict]) -> list[dict]:
    """Appends the events that END the intent `tag`, judged under the journal's lock: nothing
    when another writer ended it meanwhile (a `stop --kill`, another tick)."""
    return written(conductor, root, journal, name, lambda state, lines: [] if tag in state.wake.ended else events)


def reaped(root: Path, conductor, name: str, journal: Path, hint: tuple[str, str] | None = None) -> int:
    """Step 1 and 2 (and 6 on a root's `done`): each intent without an end is matched to its launch,
    its flow is READ from the rank the journal reached -- every `words` that reads as an act routed, once
    (`flow_read`; the follower reads the same flow while the launch plays, and a launch under way within
    `timeout:` is left to it) --, and the launch is ended when its flow says so (`ended_from_flow`):
    `wake-ended` with the run's state and its cost, or `wake-failed`. A launch whose flow has no end:
    its wake lock held past `timeout:`, it is killed and fails `wake-timeout`; its lock free, it died
    without saying so -- `wake-failed wake-dead`; born in another process space than this tick's (`foreign`), it
    ended with that space: the house's failure (`house_failed`), and its pid is never killed. A launch that fails
    carries the run's `state`, read at
    agent's face (`awaits_of`): standing, the run is relaunched while its retries last. `hint` is what the on-end tick carries, `(run, state)`
    from `PP_AGENT_RUN` and `PP_AGENT_STATE`. -> the events written."""
    lock = locks(conductor)
    count = 0
    state = state_of(journal)
    for tag in list(state.wake.intents):
        intent = state.wake.intents[tag]
        if tag in state.wake.ended:
            continue
        launch = state.wake.launched.get(tag)
        if launch is None:
            found = messages_cursor(root, name, state).get(tag)
            if found is None or not found.get("run"):
                count += len(ending(conductor, root, journal, name, tag, failed(state, intent, "launch-missing")))
                state = state_of(journal)
                continue
            launch = appended(conductor, root, journal, name, launch_found(state, tag, intent, found))[0]
            count += 1
            state = state_of(journal)
        run = str(launch.body.run or "")
        path = path_of_intent(state, intent)
        held = lock.held(launch_of(conductor, agent_meta(root, path), run))   # judged BEFORE the flow is read: a
        bound = state.season.limits.get("timeout")                            # launch over wrote its end first
        if held and (bound is None or aged(launch) <= float(bound)):
            continue                                           # the launch plays: its follower reads its flow
        told = flow_read(root, conductor, name, journal, tag)
        state = state_of(journal)
        if not told["ended"]:
            if held:
                # a stuck launch: past the bound it is ended by the kill gesture and
                # FAILS -- the retries apply; `wake-killed` stays the principal's word
                pid = launch.body.pid
                if isinstance(pid, int) and not foreign(launch.body.space):   # another space's pid names nobody here
                    ended_now(pid)
                said, resumable = awaits_of(root, conductor, path, run)
                count += len(ending(conductor, root, journal, name, tag,
                                    failed(state, intent, "wake-timeout", None, run if resumable else None,
                                           {"flow": told["rank"], "state": said})))
            elif foreign(launch.body.space):
                # its launcher was born in another process space -- a sandbox's -- and ended with it: the
                # house's failure, never final; a fresh run at the next launch (this one never had a session)
                count += len(ending(conductor, root, journal, name, tag,
                                    foreign_ended(state, name, intent, told["rank"], launch.body.space)))
            else:
                said, resumable = awaits_of(root, conductor, path, run)
                count += len(ending(conductor, root, journal, name, tag,
                                    failed(state, intent, "wake-dead", None, run if resumable else None,
                                           {"flow": told["rank"], "state": said})))
            state = state_of(journal)
            continue
        said = hint[1] if hint is not None and hint[0] == run else None
        held_task = state.task.tasks.get(intent.body.task)
        if (held_task.state if held_task is not None else None) == "stopped" and told.get("response"):
            events = ended_stopped(tag, intent, launch, run, told, said)
        else:
            events = ended_from_flow(state, intent, launch, told, said,
                                     (None, False) if told.get("response") else awaits_of(root, conductor, path, run))
        count += len(ending(conductor, root, journal, name, tag, events))
        state = state_of(journal)
    return count


def launched(root: Path, conductor, name: str, started: dict, path: str, run: str | None,
             tag: str, message: str, allowance: float | None = None, member: str | None = None,
             vectors: list[str] | None = None) -> tuple[dict | None, str, int]:
    """`agent start <path>` by the house's own console -- the agent that plays the member: the
    message, the tag, the on-end tick, the run to resume -- or, at an opening, the team's material
    (`work:`: a clone per member, `pp-agent`'s; a resume reopens its own) --, the launch flags kept
    at `team-started`, and the team's directory as the run's root of documents (`--documents`). No
    door: the entry is a successor the agent's DAG elects at every exchange (`documents_written`). Under an
    `allowance`, `--max-budget-usd` is the member's RUN cap: what the run spent plus the allowance; without
    one no cap is passed. The member's PROFILE at `team-started.profiles` replaces the team's provider, model,
    effort or permissions it names; the switches of the season -- the team's `--package`, covered name by name
    by the member's -- go as `--package <name>=on|off`, which the run's opening composes its first block with and
    a resume plays before its first launch. The `vectors` the member's run carries on its task (`vectors_of`), then
    the member's own (`member_vector`), go as `--vector <v>` each, at every launch -- the whole set, `--vector -` when
    it is empty, so that a run never keeps the vector of a season gone: opaque strings, the launcher alone resolves
    them. -> ({key, pid}, '', '') or
    (None, why, the code at the head of the launcher's refusal when it ended rc 2, '' otherwise)."""
    engine = engine_of(root, conductor)
    on_end = f"{shlex.quote(sys.executable)} {shlex.quote(str(engine))} --instance {shlex.quote(str(root))} team tick {name}"
    argv = [sys.executable, str(engine), "--instance", str(root), "agent", "start", path,
            "--message", message, "--tag", tag, "--on-end", on_end, "--documents", str(team_root(root, name))]
    if run:
        argv += ["--run", run]
    elif started.body.work:
        argv += ["--work", str(material_of(root, str(started.body.work)))]
    launch = dict(started.body.launch or {})
    launch.pop("max_budget_usd", None)                   # an older journal's per-wake cap is never passed
    profile = profile_of(started, member)
    launch.update({key: profile[key] for key in PROFILE_KEYS if profile.get(key) is not None})
    if allowance is not None:
        spent = spent_on(state_of(journal_of(root, name)), run) if run else 0.0
        launch["max_budget_usd"] = round(spent + allowance, 6)
    argv += launch_flags(launch)
    for value in season_played(root, conductor, started, member):   # the season's set: one switch per pin
        argv += ["--package", value]
    for vector in vectors or []:                                      # the nodes the run carries, opaque
        argv += ["--vector", vector]
    played = subprocess.run(argv, capture_output=True, text=True, cwd=str(root.parent), env=dict(os.environ))
    if played.returncode != 0:
        head = REFUSAL_CODE.search(played.stderr or "") if played.returncode == 2 else None
        return (None, (played.stderr or played.stdout).strip()[-300:] or f"agent start rc {played.returncode}",
                head.group(1) if head else "")
    try:
        report = json.loads(played.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return None, f"agent start reported `{played.stdout.strip()[:80]}`", ""
    return report, "", ""


def ended_now(pid: int) -> bool:
    """Ends a detached launcher by its process group -- the launcher, the harness it runs and
    what that runs. -> False when the group was gone already. Windows: `taskkill /T`."""
    if os.name == "nt":
        return subprocess.run(["taskkill", "/T", "/F", "/PID", str(pid)], capture_output=True).returncode == 0
    try:
        os.killpg(pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        return False
    return True


def kills(root: Path, conductor, name: str, state: dict, task: str, said: list[str]) -> list[dict]:
    """-> `wake-killed` for every launch under way on the task whose flow says no end, its launcher
    ended by its process group; a launch that answered (its `response` at the flow) is spared -- the reap
    ends it, its cost counted --; a launcher gone already, not launched yet, or born in another process space
    (`foreign`: its pid names nobody here), is said and left to the reap."""
    killed = []
    for one in open_intents(state):
        if one.body.task != task:
            continue
        held = state.wake.launched.get(one.body.tag)    # the launch, a dictionary at its two sources (LA2)
        launch = ((held.line if held is not None else None) or messages_cursor(root, name, state).get(one.body.tag)
                  or {})
        pid = launch.get("pid")
        answered = bool(launch.get("run")) and answered_in_flow(root, conductor, state, one, launch)
        verdict = kill_verdict(launch, answered,
                               isinstance(pid, int) and not answered and foreign(launch.get("space")))
        agent = one.body.agent
        if verdict == "answered":
            said.append(f"{task} · {agent} has answered: spared -- the reap ends it")
        elif verdict == "unlaunched":
            said.append(f"{task} · {agent} not launched yet: it ends on its own")
        elif verdict == "foreign":
            said.append(f"{task} · {agent}'s launcher plays in another process space ({launch.get('space')}): "
                        f"its pid {pid} names nobody here, left to the reap")
        elif ended_now(pid):
            said.append(f"{task} · killed {agent} (pid {pid}, run {launch.get('run')})")
            killed.append((one, launch))
        else:
            said.append(f"{task} · {agent}'s pid {pid} is gone already")
    if not any(line.startswith(f"{task} · killed") for line in said):
        said.append(f"{task} · nothing to kill")
    return kills_written(task, killed)


def words_of(root: Path, conductor, path: str, run: str, launch) -> str | None:
    """-> what a launch SAID, its `words` joined by a blank line, read at the run's flow by the house's
    console (`agent flow --exchange <launch> --json`); None when the launch is unknown or its flow
    carries no words."""
    if not run or not isinstance(launch, int):
        return None
    engine = engine_of(root, conductor)
    played = subprocess.run([sys.executable, str(engine), "--instance", str(root), "agent", "flow", path, run,
                             "--json", "--exchange", str(launch)], capture_output=True, text=True,
                            cwd=str(root.parent), env=dict(os.environ))
    if played.returncode != 0:
        return None
    texts = []
    for line in played.stdout.splitlines():
        try:
            one = json.loads(line)
        except ValueError:
            continue
        if isinstance(one, dict) and one.get("kind") == "words" and str(one.get("text") or "").strip():
            texts.append(str(one["text"]).strip())
    return "\n\n".join(texts) if texts else None


def run_named(root: Path, conductor, path: str, run: str, text: str) -> str:
    """`agent name <path> <run> <text>` by the house's console: an opening carries its carrier's name. -> ''
    once named, else what the house said -- the wake-up plays on unnamed."""
    played = subprocess.run([sys.executable, str(engine_of(root, conductor)), "--instance", str(root), "agent", "name",
                             path, run, text], capture_output=True, text=True, cwd=str(root.parent), env=dict(os.environ))
    return "" if played.returncode == 0 else (played.stderr or played.stdout).strip()[-200:] or f"rc {played.returncode}"


def forgotten(root: Path, conductor, path: str, run: str) -> str:
    """`-reset <run>` by the console of the agent at `path` -- the house's engine addressing the
    agent's instance, the gesture an owner plays by hand. -> '' once forgotten, else what the
    engine said (`call-busy`: a call holds the run)."""
    meta = agent_meta(root, path)
    played = subprocess.run([sys.executable, str(engine_of(root, conductor)), "--instance", str(meta), "-reset", run],
                            capture_output=True, text=True, cwd=str(meta.parent), env=dict(os.environ))
    return "" if played.returncode == 0 else (played.stderr or played.stdout).strip()[-300:] or f"rc {played.returncode}"


def purged(root: Path, conductor, path: str, runs: list[str]) -> str:
    """`agent purge <path> <run> ... --yes` by the house's console -> '' once removed, else what it said."""
    played = subprocess.run([sys.executable, str(engine_of(root, conductor)), "--instance", str(root), "agent",
                             "purge", path, *runs, "--yes"], capture_output=True, text=True, cwd=str(root.parent),
                            env=dict(os.environ))
    return "" if played.returncode == 0 else (played.stderr or played.stdout).strip()[-300:] or f"rc {played.returncode}"


def agent_removed(root: Path, conductor, path: str) -> str:
    """`agent remove <path> --yes` by the house's console -> '' once removed, else what it said."""
    played = subprocess.run([sys.executable, str(engine_of(root, conductor)), "--instance", str(root), "agent",
                             "remove", path, "--yes"], capture_output=True, text=True, cwd=str(root.parent),
                            env=dict(os.environ))
    return "" if played.returncode == 0 else (played.stderr or played.stdout).strip()[-300:] or f"rc {played.returncode}"


def unproven(root: Path, conductor, state: dict) -> set[str]:
    """-> the tags of the intents without an end whose launch NOBODY holds: launched (`wake-launched`) and its wake
    lock free -- its launcher ended and the next tick reads its end, or it died with its process space and no tick
    came since. A wake lock is what the house SEES of a launch, from any process space; a pid is not. An intent not
    launched yet is the tick's that writes it: never in."""
    lock = locks(conductor)
    gone = set()
    for one in open_intents(state):
        launch = state.wake.launched.get(one.body.tag)
        if (launch is not None and launch.body.run
                and not lock.held(launch_of(conductor, agent_meta(root, path_of_intent(state, one)),
                                            str(launch.body.run)))):
            gone.add(str(one.body.tag))
    return gone
