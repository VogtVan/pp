"""Scenario `team-delete` -- 9 case(s): `team delete <name> [--yes] [--json]` removes a team and what it made -- its
directory, its journal and the files beside it, its relaunch entry, its timer, the runs its wake-ups opened -- and
nothing else: the agents stay, a run the team never opened stays. Without `--yes` it says what it would remove and
writes nothing.
- (a) refused, nothing written: a team nobody declared `team-unknown`; a team at work -- a task open -- `team-busy`;
  its directory, its journal and the calendar the same to the byte
- (b) said, nothing written: the team at rest, a ceremony declared (the house's relaunch entry laid): without `--yes` the
  verb names the directory, the journal and each run of the team, and writes nothing -- the directory, the records
  and the calendar the same to the byte
- (c) removed: under `--yes` no `teams/<name>/`, no journal (`team status <name>` refuses `team-unknown`), no
  relaunch entry -- the other team, under `schedule: off`, needs none; the run of each member purged -- its trace gone at its agent --, a run of the same agent
  opened outside the team kept; the agents stand, said; the other team of the house untouched
- (d) two writers, the tick's lock held: the bench holds the team's `tick.lock`; `delete --yes` waits
  `call_lock_wait` (1 s) then refuses `team-busy`, nothing removed -- the directory, the journal and the calendar
  the same to the byte
- (e) two writers at once: `delete --yes` and a `post` of a new task played together on a team at rest, five
  rounds -- each round leaves the team whole and started with its post (the delete refused `team-busy`), or nothing
  of it (no directory, no journal), never a journal without its declaration
- (f) the journal's lock orders the two writers, whatever the load: the bench holds the journal's lock as a writer
  does -- `delete --yes` waits for it, the declaration and the journal standing while it waits, then removes the
  team; a `post` waiting for it while the declaration goes refuses `team-unknown` and writes nothing; a write on a
  team nobody declares refuses `team-unknown` and leaves no directory behind
- (g) a delete refused leaves the team whole: a task a post wrote while `delete --yes` waited for the journal's lock
  -- the bench writes it, holding the lock -- makes the delete refuse `team-busy` with nothing removed: no
  `deleting`, the relaunch entry, the timer's mark and the run in place
- (h) a team deleting opens nothing: on a team whose `deleting` stands, `post`, `start`, `resume --task`, `resume`
  and `ring` refuse `team-deleting`, nothing written, and a tick past the hour of its ceremony and of its recurrence
  opens no task; a timer whose tick failed there (`timer_relayed`, on a team under a step that keeps its net) arms no
  timer and tells nobody, its declaration standing or gone -- the journal the same to the byte
- (i) a delete taken up after a refused purge goes on: the purge of the second agent's run refused while its wake
  lock is held (`delete-failed`), `delete --yes` again holds the first agent's run, purged already, as purged and
  removes the team
(f) and (g) see a writer wait for the journal's lock at /proc/locks: unseen within the bound, the case is red;
without /proc/locks it prints NOT PLAYED, outside the held cases.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from conductor.state import lock, record
from tests.harness import cli, holding, race, support

T = support(__file__, "team")


def files_under(root: Path) -> dict[str, bytes]:
    """-> {relative path: bytes} of every file under `root`."""
    return {str(path.relative_to(root)): path.read_bytes() for path in sorted(root.rglob("*")) if path.is_file()} \
        if root.is_dir() else {}


def traces_of(h, path: str, key: str) -> list[str]:
    """-> the files the agent's engine keeps of the run `key`."""
    state = h.meta_of(path) / ".sys" / "state"
    return sorted(one.name for one in state.glob(f"*{key}*")) if state.is_dir() else []


LOCKS = Path("/proc/locks")         # the waiters of a lock, listed by Linux alone


def waited_on(path: Path) -> bool:
    """-> whether a process waits for the lock on `path` -- a waiter's line of /proc/locks (`->`) names its inode."""
    try:
        inode, text = os.stat(path).st_ino, LOCKS.read_text(encoding="utf-8")
    except OSError:
        return False
    return any(len(fields) > 6 and fields[1] == "->" and fields[6].endswith(f":{inode}")
               for fields in (line.split() for line in text.splitlines()))


def reached(process: subprocess.Popen, journal: Path) -> bool:
    """-> whether `process` was seen waiting for the journal's lock, read at /proc/locks, before it ended and within
    the bound -- never seen, the case that needs it is red."""
    gate = journal.with_name(journal.name + ".lock")
    until(lambda: process.poll() is not None or waited_on(gate))
    return process.poll() is None and waited_on(gate)


def appended_by_hand(h, name: str, events: list[dict]) -> None:
    """Events appended to the team's journal by the bench itself, numbered after its last -- what a writer that holds
    the journal's lock writes."""
    last = max((int(one.get("id") or 0) for one in h.events(name)), default=0)
    with h.journal_of(name).open("a", encoding="utf-8") as handle:
        for offset, one in enumerate(events, 1):
            handle.write(json.dumps({"at": "2026-11-15T12:00:00+00:00", "id": last + offset, "team": name, **one}) + "\n")


def until(predicate, timeout: float = 60.0) -> bool:
    """Polls `predicate` until it holds; False past the bound."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.05)
    return bool(predicate())


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "m": [{"sleep": 0.1, "body": {"done": "merged"}}],
        "w": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which branch?"}}}],
        # (i) two members on two agents, each with its run
        "p": [{"sleep": 0.1, "body": {"do": ["q"]}}, {"sleep": 0.1, "body": {"done": "both"}}],
        "q": [{"sleep": 0.1, "body": {"done": True}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    h.declare("gone", "---\nagents: |\n  m agents/m\n  g agents/g\nreports: |\n  g -> m\nroot: m\n"
                      "ceremonies: |\n  daily every weekday 09:30 with g -> m\nschedule: 1\n---\nMerge what is asked.\n")
    h.declare("busy", "---\nagents: |\n  w agents/w\nroot: w\nschedule: off\n---\nAsk first.\n")
    started = h.call("team", "start", "gone", "--message", "merge PR 11", *h.harnessed, now="08:00")
    busy = h.call("team", "start", "busy", "--message", "merge PR 12", *h.harnessed)
    h.declare("twice", "---\nagents: |\n  p agents/p\n  q agents/q\nreports: |\n  q -> p\nroot: p\nschedule: off\n"
                       "---\nTwo runs, two agents.\n")
    twice = h.call("team", "start", "twice", "--message", "review PR 13", *h.harnessed)
    # (h): a team with a ceremony and a recurrence, at rest at 08:00 of the frozen day
    h.declare("half", "---\nagents: |\n  hf agents/hf\nroot: hf\nceremonies: |\n  daily every weekday 09:30 with hf -> hf\n"
                      "schedule: off\n---\nBeing deleted.\n")
    h.call("team", "start", "half", "--no-tick", now="08:00")
    every_h = h.call("team", "post", "half", "--every", "day 09:00", "--message", "the morning", "--no-tick", now="08:00")
    # (h) too: a team under a step, its ceremony keeping its net; never ticked -- the case alone relays its timer
    h.declare("halt", "---\nagents: |\n  ht agents/ht\nroot: ht\nceremonies: |\n  daily every weekday 09:30 with ht -> ht\n"
                      "schedule: 1s\n---\nStopped on its way out.\n")
    h.call("team", "start", "halt", "--no-tick", now="08:00")
    # the teams of (e) and (f), declared and started at once while gone and busy work: none ticks
    quiet = {f"race{n}": f"---\nagents: |\n  r{n} agents/r{n}\nroot: r{n}\nschedule: off\n---\nRace.\n" for n in range(5)}
    quiet.update({"lockd": "---\nagents: |\n  ld agents/ld\nroot: ld\nschedule: off\n---\nDeleted behind a writer.\n",
                  "lockp": "---\nagents: |\n  lp agents/lp\nroot: lp\nschedule: off\n---\nPosted behind a delete.\n"})
    for name, text in quiet.items():
        h.declare(name, text)
    race(h.engine, [["--instance", str(h.house), "team", "start", name, "--no-tick"] for name in quiet],
         cwd=h.ws, env=h.env)
    done = h.settled("gone", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    asked = h.settled("busy", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), 60)
    done_i = h.settled("twice", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    key = next((one.get("run") for one in by_kind(h.events("gone"), "wake-ended", agent="m")), "") or ""
    outside = cli(h.engine, "--instance", str(h.meta_of("agents/m")), "-new", cwd=h.meta_of("agents/m").parent,
                  env=h.env)
    other = (re.search(r"run ([0-9a-f]{6})", outside.stdout) or [None, ""])[1]
    records = h.records / "teams"

    def kept() -> tuple:
        return (files_under(h.teams), files_under(records),
                h.crontab.read_bytes() if h.crontab.is_file() else b"")

    # --- (a) refused, nothing written ------------------------------------------------------------------------
    before = kept()
    unknown = h.call("team", "delete", "ghost", "--yes")
    working = h.call("team", "delete", "busy", "--yes")
    if (busy.returncode == 0 and asked and unknown.returncode == 2 and "team-unknown" in unknown.stderr
            and working.returncode == 2 and "team-busy" in working.stderr and kept() == before):
        bench.refusals += 2
        held("(a) refused, nothing written", "ghost refuses team-unknown, busy (T1 open) team-busy; the teams' "
             "directories, journals and the calendar the same to the byte")
    else:
        failures.append(f"  ✗ (a) refused                rc={unknown.returncode}/{working.returncode} asked={asked} "
                        f"same={kept() == before} {unknown.stderr.strip()[-160:]!r} {working.stderr.strip()[-160:]!r}")

    # --- (b) said, nothing written ---------------------------------------------------------------------------
    mark = f"# pp-team {h.house}"                       # the house's one line, its teams in need behind it
    laid = any(one.endswith(mark) for one in (h.crontab.read_text(encoding="utf-8") if h.crontab.is_file() else "").splitlines())
    before = kept()
    said = h.call("team", "delete", "gone", "--json")
    try:
        told = json.loads(said.stdout)
    except ValueError:
        told = {}
    if (started.returncode == 0 and done and key and laid and said.returncode == 0 and told.get("dry") is True
            and told.get("team") == "gone" and [one.get("run") for one in told.get("runs") or []] == [key]
            and told.get("relaunch") is True and kept() == before):
        held("(b) said, nothing written", f"gone at rest, its daily's relaunch entry laid: the dry delete names run {key} and "
             "the entry; the directory, the records and the calendar the same to the byte")
    else:
        failures.append(f"  ✗ (b) said                   rc={started.returncode}/{said.returncode} done={done} key={key!r} "
                        f"laid={laid} told={told} same={kept() == before} {said.stderr.strip()[-200:]!r}")

    # --- (g) a delete refused leaves the team whole --------------------------------------------------------------
    # the delete is seen waiting at /proc/locks; without it the case is not played: nothing shows the wait
    if LOCKS.is_file():
        journal_g = h.journal_of("gone")
        timer_g = records / "gone" / "tick.timer"
        before_g = (laid, timer_g.is_file(), traces_of(h, "agents/m", key))
        with record.held(journal_g):                     # a post's write, held while the delete comes
            refusing = subprocess.Popen([sys.executable, str(h.engine), "--instance", str(h.house), "team", "delete",
                                         "gone", "--yes"], cwd=h.ws, env={**os.environ, **h.env},
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            waited_g = reached(refusing, journal_g)
            appended_by_hand(h, "gone", [{"kind": "task", "task": "T2", "from": "house", "to": "m", "text": "one more"},
                                         {"kind": "post", "task": "T2", "from": "house", "to": "m", "verb": "do",
                                          "text": "one more"}])
        _, said_g = refusing.communicate(timeout=120)
        table_g = h.crontab.read_text(encoding="utf-8") if h.crontab.is_file() else ""
        after_g = (any(one.endswith(mark) for one in table_g.splitlines()), timer_g.is_file(),
                   traces_of(h, "agents/m", key))
        deleting_g = [one for one in h.events("gone") if one.get("kind") == "deleting"]
        stopped_g = h.call("team", "stop", "gone", "--task", "T2", "--no-tick")   # T2 closed: (c) deletes it at rest
        if (waited_g and refusing.returncode == 2 and "team-busy" in said_g and deleting_g == []
                and after_g == before_g and before_g[2] and stopped_g.returncode == 0):
            held("(g) a delete refused leaves the team whole", "T2 written while the delete waited for the journal's "
                 "lock: team-busy, no deleting, the relaunch entry, the timer's mark and the run in place")
        else:
            failures.append(f"  ✗ (g) a delete refused        waited={waited_g} rc={refusing.returncode} "
                            f"{said_g.strip()[-120:]!r} deleting={len(deleting_g)} before={before_g[:2]}/"
                            f"{len(before_g[2])} after={after_g[:2]}/{len(after_g[2])} stop={stopped_g.returncode}")
    else:
        print("  · (g) NOT PLAYED -- no /proc/locks here to see the delete wait for the journal's lock")

    # --- (h) a team deleting opens nothing ----------------------------------------------------------------------
    appended_by_hand(h, "half", [{"kind": "deleting"}])  # a delete stopped once `deleting` stood
    mark_h = max(int(one.get("id") or 0) for one in h.events("half"))
    half_before = h.journal_of("half").read_bytes()
    verbs_h = {"post": ["post", "half", "--message", "x"], "start": ["start", "half", "--message", "again"],
               "resume --task": ["resume", "half", "--task", "T1"], "resume": ["resume", "half"],
               "ring": ["ring", "half", "daily"]}                 # each refused: they play at once, at 09:00
    refused_h = dict(zip(verbs_h, race(h.engine, [["--instance", str(h.house), "team", *argv, "--no-tick"]
                                                  for argv in verbs_h.values()],
                                       cwd=h.ws, env={**h.env, "PP_NOW": T.THURSDAY + "09:00"})))
    unchanged_h = h.journal_of("half").read_bytes() == half_before
    ticked_h = h.call("team", "tick", "half", now="10:00")   # the ceremony and the recurrence due: nothing opens
    opened_h = [one.get("task") for one in h.events("half") if one.get("kind") == "task" and one["id"] > mark_h]
    # the delete stopped on its way, the timer's tick failed: relayed, it arms nothing and tells nobody
    appended_by_hand(h, "halt", [{"kind": "deleting"}])
    halt_before = h.journal_of("halt").read_bytes()
    relay = T.probe_script(h, "root, conductor = mod.house()\ntry:\n"
                              "    mod.timer_relayed(root, conductor, 'halt', 'the tick failed')\n    code = 0\n"
                              "except SystemExit as stop:\n    code = stop.code\n"
                              "armed = bool(mod.timer_standing(root, 'halt'))\nmod.disarmed(root, 'halt')\n"
                              "print(json.dumps({'rc': code, 'timer': armed}))\n")

    def relayed() -> dict:
        played = subprocess.run([sys.executable, str(relay)], capture_output=True, text=True, cwd=h.ws,
                                env={**os.environ, **h.env})
        try:
            return json.loads(played.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            return {"rc": played.returncode, "said": played.stderr.strip()[-160:]}

    declared_h = relayed()                                # `deleting` written, TEAM.md still there
    (h.teams / "halt" / "TEAM.md").rename(h.teams / "halt" / "TEAM.md.away")
    undeclared_h = relayed()                              # the declaration removed, the journal left
    silent_h = (h.journal_of("halt").read_bytes() == halt_before
                and not [one for one in h.events("halt") if one.get("timer")])
    quiet_h = {"rc": 0, "timer": False}
    if (every_h.returncode == 0 and all(one.returncode == 2 and "team-deleting" in one.stderr for one in refused_h.values())
            and unchanged_h and ticked_h.returncode == 0 and opened_h == []
            and declared_h == quiet_h and undeclared_h == quiet_h and silent_h):
        held("(h) a team deleting opens nothing", "deleting stands: post, start, resume --task, resume and ring refuse "
             "team-deleting, the journal the same to the byte; a tick past the ceremony's and the recurrence's hours "
             "opens no task; a failed timer relayed there arms no timer and writes no notice, TEAM.md standing or gone")
    else:
        failures.append(f"  ✗ (h) a team deleting         every={every_h.returncode} "
                        f"{ {verb: (one.returncode, one.stderr.strip()[-70:]) for verb, one in refused_h.items()} } "
                        f"unchanged={unchanged_h} tick={ticked_h.returncode} opened={opened_h} "
                        f"relayed={declared_h}/{undeclared_h} silent={silent_h}")

    # --- (i) a delete taken up after a refused purge goes on --------------------------------------------------------
    try:
        runs_i = [(one["path"], one["run"]) for one in json.loads(h.call("team", "delete", "twice", "--json").stdout)["runs"]]
    except (ValueError, KeyError, TypeError):
        runs_i = []
    paths_i = list(dict.fromkeys(path for path, _ in runs_i))
    last_i = next((run for path, run in runs_i if paths_i and path == paths_i[-1]), "")
    if len(paths_i) == 2 and last_i:
        with holding(h.meta_of(paths_i[-1]) / ".sys" / "state" / f"session-{last_i}.wake.lock"):   # a run still playing
            failed_i = h.call("team", "delete", "twice", "--yes")
        purged_first = not traces_of(h, paths_i[0], dict(runs_i)[paths_i[0]])
        again_i = h.call("team", "delete", "twice", "--yes")
    else:
        failed_i = again_i = None
        purged_first = False
    gone_i = not (h.teams / "twice").exists() and not (records / "twice").exists()
    if (twice.returncode == 0 and done_i and failed_i is not None and failed_i.returncode == 2
            and "delete-failed" in failed_i.stderr and purged_first
            and again_i.returncode == 0 and gone_i and not traces_of(h, paths_i[-1], last_i)):
        held("(i) a delete taken up goes on", f"{paths_i[0]}'s run purged, {paths_i[-1]}'s refused while its wake lock "
             "was held: delete-failed; delete --yes again holds the run gone at the first agent as purged and removes "
             "the team")
    else:
        failures.append(f"  ✗ (i) a delete taken up       done={done_i} runs={runs_i} "
                        f"failed={failed_i and (failed_i.returncode, failed_i.stderr.strip()[-120:])} "
                        f"first={purged_first} again={again_i and (again_i.returncode, again_i.stderr.strip()[-160:])} "
                        f"gone={gone_i}")

    # --- (c) removed ------------------------------------------------------------------------------------------
    busy_before = (files_under(h.teams / "busy"), files_under(records / "busy"))
    traced = traces_of(h, "agents/m", key)
    removed = h.call("team", "delete", "gone", "--yes", "--json")
    try:
        result = json.loads(removed.stdout)
    except ValueError:
        result = {}
    after = h.call("team", "status", "gone")
    table = h.crontab.read_text(encoding="utf-8") if h.crontab.is_file() else ""
    if (removed.returncode == 0 and result.get("dry") is False and traced and not traces_of(h, "agents/m", key)
            and other and traces_of(h, "agents/m", other)
            and not (h.teams / "gone").exists() and not (records / "gone").exists()
            and not any(one.endswith(mark) for one in table.splitlines())
            and after.returncode == 2 and "team-unknown" in after.stderr
            and h.agent_stands("agents/m") and result.get("agents") == ["agents/g", "agents/m"]
            and (files_under(h.teams / "busy"), files_under(records / "busy")) == busy_before):
        held("(c) removed", f"no teams/gone, no journal (status refuses team-unknown), no relaunch entry -- busy, under schedule: off, needs none; run {key} "
             f"purged at agents/m, run {other} opened outside kept; agents/m and agents/g stand and are said; busy untouched")
    else:
        failures.append(f"  ✗ (c) removed                rc={removed.returncode}/{after.returncode} result={result} "
                        f"traced={traced} left={traces_of(h, 'agents/m', key)} other={other!r}/{traces_of(h, 'agents/m', other)} "
                        f"dir={(h.teams / 'gone').exists()} journal={(records / 'gone').exists()} line={mark in table} "
                        f"{removed.stderr.strip()[-200:]!r}")
    # --- (d) two writers, the tick's lock held ----------------------------------------------------------------
    settings = h.house / "SETTINGS.md"                      # the owner's edit: a short wait for the house's locks
    settings.write_text(re.sub(r"^call_lock_wait: \d+$", "call_lock_wait: 1", settings.read_text(encoding="utf-8"),
                               count=1, flags=re.M), encoding="utf-8")
    h.declare("held", "---\nagents: |\n  hd agents/hd\nroot: hd\nschedule: off\n---\nHeld.\n")
    h.journal_of("held").parent.mkdir(parents=True, exist_ok=True)
    lease = lock.acquire(records / "held" / "tick.lock", wait=5)
    before = (files_under(h.teams / "held"), files_under(records / "held"),
              h.crontab.read_bytes() if h.crontab.is_file() else b"")    # the lock's own file laid first
    try:
        waited = h.call("team", "delete", "held", "--yes")
    finally:
        if lease is not None:
            lock.release(lease)
    after = (files_under(h.teams / "held"), files_under(records / "held"),
             h.crontab.read_bytes() if h.crontab.is_file() else b"")
    if lease is not None and waited.returncode == 2 and "team-busy" in waited.stderr and after == before:
        bench.refusals += 1
        held("(d) the tick's lock held", "delete --yes waits call_lock_wait (1 s), then team-busy; the directory, "
             "the journal and the calendar the same to the byte")
    else:
        failures.append(f"  ✗ (d) lock held              lease={lease is not None} rc={waited.returncode} "
                        f"same={after == before} {waited.stderr.strip()[-200:]!r}")

    # --- (e) two writers at once: a delete and a post ----------------------------------------------------------
    rounds = []
    for n in range(5):
        name = f"race{n}"
        both = race(h.engine, [["--instance", str(h.house), "team", "delete", name, "--yes"],
                               ["--instance", str(h.house), "team", "post", name, "--message", "x", "--no-tick"]],
                    cwd=h.ws, env=h.env)
        whole = (h.teams / name / "TEAM.md").is_file() and h.journal_of(name).is_file()
        gone = not (h.teams / name).exists() and not (records / name).exists()
        posted = whole and any(one.get("kind") == "task" for one in h.events(name))
        rounds.append((n, [one.returncode for one in both], whole, gone, posted,
                       both[0].stderr.strip()[-120:], both[1].stderr.strip()[-120:]))
    if all((whole and posted) or gone for _, _, whole, gone, posted, _, _ in rounds):
        held("(e) a delete and a post at once", "five rounds: "
             + ", ".join("posted, kept" if whole else "deleted" for _, _, whole, _, _, _, _ in rounds)
             + " -- never a journal without its declaration")
    else:
        failures.append(f"  ✗ (e) delete and post        {rounds}")

    # --- (f) the journal's lock orders the two writers -------------------------------------------------------
    # the writers are seen waiting at /proc/locks; without it the case is not played: nothing shows the wait
    if LOCKS.is_file():
        def console(*words: str) -> subprocess.Popen:
            return subprocess.Popen([sys.executable, str(h.engine), "--instance", str(h.house), *words], cwd=h.ws,
                                    env={**os.environ, **h.env}, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True)

        journal_d = h.journal_of("lockd")
        with record.held(journal_d):                         # a writer of the journal, as a post holds it
            deleting = console("team", "delete", "lockd", "--yes")
            waited_d = reached(deleting, journal_d)
            standing_d = (h.teams / "lockd" / "TEAM.md").is_file() and journal_d.is_file()
        _, said_d = deleting.communicate(timeout=120)
        gone_d = not (h.teams / "lockd").exists() and not (records / "lockd").exists()

        journal_p = h.journal_of("lockp")
        with record.held(journal_p):
            posting = console("team", "post", "lockp", "--message", "x", "--no-tick")
            waited_p = reached(posting, journal_p)
            (h.teams / "lockp" / "TEAM.md").unlink()         # the declaration goes while the post waits
        _, said_p = posting.communicate(timeout=120)
        tasks_p = [one for one in h.events("lockp") if one.get("kind") == "task"]

        probe = T.probe_script(h, "root, conductor = mod.house()\njournal = mod.journal_of(root, 'nowhere')\n"
                                  "try:\n    mod.written(conductor, root, journal, 'nowhere', lambda state, events: [])\n"
                                  "    code = 0\nexcept SystemExit as stop:\n    code = stop.code\n"
                                  "print(json.dumps({'rc': code, 'folder': journal.parent.exists()}))\n")
        probed = subprocess.run([sys.executable, str(probe)], capture_output=True, text=True, cwd=h.ws,
                                env={**os.environ, **h.env})
        try:
            nowhere = json.loads(probed.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            nowhere = {}
        if (waited_d and standing_d and deleting.returncode == 0 and gone_d
                and waited_p and posting.returncode == 2 and "team-unknown" in said_p and tasks_p == []
                and nowhere == {"rc": 2, "folder": False} and "team-unknown" in probed.stderr):
            held("(f) the journal's lock orders the two writers", "delete --yes waited for the journal's lock, the "
                 "declaration and the journal standing, then removed the team; a post waiting for it while the declaration "
                 "went refused team-unknown, no task written; a write on a team nobody declares refused team-unknown, no "
                 "directory left")
        else:
            failures.append(f"  ✗ (f) the journal's lock      delete: waited={waited_d} standing={standing_d} "
                            f"rc={deleting.returncode} gone={gone_d} {said_d.strip()[-120:]!r} -- post: waited={waited_p} "
                            f"rc={posting.returncode} tasks={len(tasks_p)} {said_p.strip()[-120:]!r} -- nowhere={nowhere} "
                            f"{probed.stderr.strip()[-160:]!r}")
    else:
        print("  · (f) NOT PLAYED -- no /proc/locks here to see a writer wait for the journal's lock")
    return 0
