"""Scenario `team-delete` -- 5 case(s): `team delete <name> [--yes] [--json]` removes a team and what it made -- its
directory, its journal and the files beside it, its calendar line, its timer, the runs its wake-ups opened -- and
nothing else: the agents stay, a run the team never opened stays. Without `--yes` it says what it would remove and
writes nothing.
- (a) refused, nothing written: a team nobody declared `team-unknown`; a team at work -- a task open -- `team-busy`;
  its directory, its journal and the calendar the same to the byte
- (b) said, nothing written: the team at rest, a ceremony declared (its calendar line laid): without `--yes` the
  verb names the directory, the journal and each run of the team, and writes nothing -- the directory, the records
  and the calendar the same to the byte
- (c) removed: under `--yes` no `teams/<name>/`, no journal (`team status <name>` refuses `team-unknown`), no
  calendar line of the team; the run of each member purged -- its trace gone at its agent --, a run of the same agent
  opened outside the team kept; the agents stand, said; the other team of the house untouched
- (d) two writers, the tick's lock held: the bench holds the team's `tick.lock`; `delete --yes` waits
  `call_lock_wait` (1 s) then refuses `team-busy`, nothing removed -- the directory, the journal and the calendar
  the same to the byte
- (e) two writers at once: `delete --yes` and a `post` of a new task played together on a team at rest, five
  rounds -- each round leaves the team whole and started with its post (the delete refused `team-busy`), or nothing
  of it (no directory, no journal), never a journal without its declaration
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from conductor.state import lock
from tests.harness import cli, race, support

T = support(__file__, "team")


def files_under(root: Path) -> dict[str, bytes]:
    """-> {relative path: bytes} of every file under `root`."""
    return {str(path.relative_to(root)): path.read_bytes() for path in sorted(root.rglob("*")) if path.is_file()} \
        if root.is_dir() else {}


def traces_of(h, path: str, key: str) -> list[str]:
    """-> the files the agent's engine keeps of the run `key`."""
    state = h.meta_of(path) / ".sys" / "state"
    return sorted(one.name for one in state.glob(f"*{key}*")) if state.is_dir() else []


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "m": [{"sleep": 0.1, "body": {"done": "merged"}}],
        "w": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which branch?"}}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    h.declare("gone", "---\nagents: |\n  m agents/m\n  g agents/g\nreports: |\n  g -> m\nroot: m\n"
                      "ceremonies: |\n  daily every weekday 09:30 with g -> m\nschedule: 1\n---\nMerge what is asked.\n")
    h.declare("busy", "---\nagents: |\n  w agents/w\nroot: w\nschedule: off\n---\nAsk first.\n")
    started = h.call("team", "start", "gone", "--message", "merge PR 11", *h.harnessed, now="08:00")
    busy = h.call("team", "start", "busy", "--message", "merge PR 12", *h.harnessed)
    done = h.settled("gone", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    asked = h.settled("busy", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), 60)
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
    mark = f"# pp-team {h.house} gone"
    laid = mark in (h.crontab.read_text(encoding="utf-8") if h.crontab.is_file() else "")
    before = kept()
    said = h.call("team", "delete", "gone", "--json")
    try:
        told = json.loads(said.stdout)
    except ValueError:
        told = {}
    if (started.returncode == 0 and done and key and laid and said.returncode == 0 and told.get("dry") is True
            and told.get("team") == "gone" and [one.get("run") for one in told.get("runs") or []] == [key]
            and told.get("calendar") is True and kept() == before):
        held("(b) said, nothing written", f"gone at rest, its daily's line laid: the dry delete names run {key} and "
             "the calendar line; the directory, the records and the calendar the same to the byte")
    else:
        failures.append(f"  ✗ (b) said                   rc={started.returncode}/{said.returncode} done={done} key={key!r} "
                        f"laid={laid} told={told} same={kept() == before} {said.stderr.strip()[-200:]!r}")

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
            and not (h.teams / "gone").exists() and not (records / "gone").exists() and mark not in table
            and after.returncode == 2 and "team-unknown" in after.stderr
            and h.agent_stands("agents/m") and result.get("agents") == ["agents/g", "agents/m"]
            and (files_under(h.teams / "busy"), files_under(records / "busy")) == busy_before):
        held("(c) removed", f"no teams/gone, no journal (status refuses team-unknown), no calendar line; run {key} "
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
        h.declare(name, f"---\nagents: |\n  r{n} agents/r{n}\nroot: r{n}\nschedule: off\n---\nRace.\n")
        h.call("team", "start", name, "--no-tick")
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
    return 0
