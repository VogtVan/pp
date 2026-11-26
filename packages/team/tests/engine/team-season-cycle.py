"""Scenario `team-season-cycle` -- 7 case(s): a SEASON has an end -- `team stop <team>` stops it, the team is OFF
SEASON until the next `team start`, and only then is it changed -- under a frozen clock (`PP_NOW`, Thursday). No
wake-up plays: every call is `--no-tick` but the ticks the cases play off season and at the restart.
- (a) the stop: a team at 08:00 with two open tasks, a recurrence `day 09:00` and a ceremony `daily every day 09:00`
  -- `team stop c --json` writes the tasks' `stopped`, then `season-stopped {by, tasks, recurrences}` naming T1, T2
  and R1, its face `{team, stopped: {id, tasks, recurrences}}` the same; the relaunch entry removed; a second stop
  refuses `season-stopped`, the journal byte for byte
- (b) nothing works off season: a tick at 09:01, the hour of the recurrence and of the ceremony, writes no task, no
  ring, no wake-up, arms no timer; `post`, `ring` and `pause` refuse `season-stopped` -- the journal, `TEAM.md` and
  `SEASON.md` byte for byte
- (c) written off season alone: on a team in season, `team declare` of `TEAM.md` and of `SEASON.md` and `team start`
  refuse `season-running`, naming `team stop`, the journal and both files byte for byte; off season, `team declare`
  writes `TEAM.md`; `status --json` says `season.state` `stopped` and `season.stopped {at, by, id}` before the
  restart, `running` and no `stopped` after it; `declaration --json` says `started.state`
- (d) the restart catches nothing up: `team start` at 10:00 opens the season; a tick at 10:01 opens no occurrence of
  the 09:00 period passed off season and rings no daily; `status --json` says the recurrence `due` false, its
  `next_due` Friday 09:00
- (e) the flags a form needs, off season: `team declare --body-file -` writes the body read on standard input, under
  `--season` that of `SEASON.md`; `--report "w x -> m"` writes the line of `reports:` whose target is m in place of
  `w -> m`, `--no-report m` takes it out, the block with it; `--report "ghost -> m"` refuses `participant-unknown` and
  `--report "w"` `team-invalid`, nothing written
- (f) `status` says the season's state by the event that made it: under a pause, the pause's number beside the
  start's; off season, the stop's; once a second season opens, its line says the rank 2
- (g) the start judged again under the journal's lock: the bench holds the lock of a team never started while its
  `team start` waits for it (seen at /proc/locks), and writes there what a writer of the meantime would have -- a
  `deleting`: the start refuses `team-deleting`; a `team-started`: it refuses `season-running` -- no event of the
  start written either time. Without /proc/locks the case is not played
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from conductor.state import record
from tests.harness import cli, support

T = support(__file__, "team")
TEAM = ("---\nagents: |\n  m agents/m\n  w agents/w\nreports: |\n  w -> m\nroot: m\nschedule: 5m\nceremonies: |\n"
        "  daily every day 09:00 with w -> m\n---\nHold the season.\n")
LOCKS = Path("/proc/locks")         # the waiters of a lock, listed by Linux alone


def waited_on(path: Path) -> bool:
    """-> whether a process waits for the lock on `path` -- a waiter's line of /proc/locks (`->`) names its inode."""
    try:
        inode, text = os.stat(path).st_ino, LOCKS.read_text(encoding="utf-8")
    except OSError:
        return False
    return any(len(fields) > 6 and fields[1] == "->" and fields[6].endswith(f":{inode}")
               for fields in (line.split() for line in text.splitlines()))


def reached(process: subprocess.Popen, journal: Path, timeout: float = 60.0) -> bool:
    """-> whether `process` was seen waiting for the journal's lock before it ended and within the bound."""
    gate = journal.with_name(journal.name + ".lock")
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline and process.poll() is None and not waited_on(gate):
        time.sleep(0.05)
    return process.poll() is None and waited_on(gate)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})
    code = T.refusal_code

    def kept(name: str) -> tuple:
        """-> the journal, TEAM.md and SEASON.md of a team, byte for byte (None for a file that stands not)."""
        read = lambda path: path.read_bytes() if path.is_file() else None
        return (read(h.journal_of(name)), read(h.teams / name / "TEAM.md"), read(h.teams / name / "SEASON.md"))

    def faced(played) -> dict:
        try:
            return json.loads(played.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            return {}

    # --- (a) the stop -------------------------------------------------------------------------------------------
    h.declare("c", TEAM)
    (h.teams / "c" / "SEASON.md").write_text("---\nmodel: m-1\n---\nThe season's word.\n", encoding="utf-8")
    begun = h.call("team", "start", "c", "--no-tick", now="08:00")
    for text in ("first", "second"):
        h.call("team", "post", "c", "--message", text, "--no-tick", now="08:01")
    h.call("team", "post", "c", "--every", "day 09:00", "--message", "each day", "--no-tick", now="08:02")
    entry_before = h.crontab.read_text(encoding="utf-8") if h.crontab.is_file() else ""
    stopped = h.call("team", "stop", "c", "--json", "--no-tick", now="08:10")
    face = faced(stopped)
    found = h.events("c")
    closing = (T.by_kind(found, "season-stopped") or [{}])[-1]
    entry_after = h.crontab.read_text(encoding="utf-8") if h.crontab.is_file() else ""
    before_again = kept("c")
    again = h.call("team", "stop", "c", "--no-tick", now="08:11")
    if (begun.returncode == 0 and stopped.returncode == 0
            and sorted(one.get("task") for one in T.by_kind(found, "stopped")) == ["T1", "T2"]
            and found[-1].get("kind") == "season-stopped"
            and (closing.get("tasks"), closing.get("recurrences")) == (["T1", "T2"], ["R1"]) and closing.get("by")
            and face == {"team": "c", "stopped": {"id": closing.get("id"), "tasks": ["T1", "T2"],
                                                   "recurrences": ["R1"]}}
            and "tick" in entry_before and "tick" not in entry_after
            and again.returncode == 2 and code(again.stderr) == "season-stopped" and kept("c") == before_again):
        bench.refusals += 1
        held("(a) the stop", "T1 and T2 stopped, then season-stopped {by, tasks [T1, T2], recurrences [R1]}, the face "
             "the same; the relaunch entry removed; a second stop: season-stopped, the journal byte for byte")
    else:
        failures.append(f"  ✗ (a) the stop               rc={begun.returncode}/{stopped.returncode}/{again.returncode} "
                        f"closing={closing} face={face} entry={'tick' in entry_before}/{'tick' in entry_after} "
                        f"{(stopped.stderr or again.stderr).strip()[-200:]!r}")

    # --- (b) nothing works off season -------------------------------------------------------------------------------
    count = len(h.events("c"))
    ticked = h.call("team", "tick", "c", now="09:01")
    after = h.events("c")[count:]
    timer = h.records / "teams" / "c" / "tick.timer"
    stood = kept("c")
    refused = {"post": h.call("team", "post", "c", "--message", "more", "--no-tick", now="09:02"),
               "ring": h.call("team", "ring", "c", "daily", "--no-tick", now="09:02"),
               "pause": h.call("team", "pause", "c", now="09:02")}
    codes = {verb: (one.returncode, code(one.stderr)) for verb, one in refused.items()}
    if (ticked.returncode == 0 and not [one for one in after if one.get("kind") in
                                         ("task", "ceremony-due", "wake-intent", "recurrence-skipped")]
            and not timer.exists() and codes == {verb: (2, "season-stopped") for verb in refused}
            and kept("c") == stood):
        bench.refusals += len(refused)
        held("(b) nothing works off season", f"a tick at 09:01 writes {len(after)} event(s): no task, no ring, no "
             "wake-up, no timer; post, ring and pause: season-stopped, the journal, TEAM.md and SEASON.md byte for byte")
    else:
        failures.append(f"  ✗ (b) off season             rc={ticked.returncode} after={[one.get('kind') for one in after]} "
                        f"timer={timer.exists()} codes={codes} same={kept('c') == stood}")

    # --- (c) written off season alone --------------------------------------------------------------------------
    h.declare("d", TEAM)
    h.call("team", "start", "d", "--no-tick", now="08:00")
    word = bench.temp() / "word.md"
    word.write_text("Another word.\n", encoding="utf-8")
    stood_d = kept("d")
    running = {"declare": h.call("team", "declare", "d", "--budget", "3"),
               "declare --season": h.call("team", "declare", "d", "--season", "--body-file", str(word)),
               "start": h.call("team", "start", "d", "--no-tick", now="08:30")}
    said = {verb: (one.returncode, code(one.stderr), "team stop" in one.stderr) for verb, one in running.items()}
    off = h.face("c", now="09:30")
    written = h.call("team", "declare", "c", "--budget", "3", "--json")
    declaration = T.declaration_read(h, "c")
    if (said == {verb: (2, "season-running", True) for verb in running} and kept("d") == stood_d
            and (off.get("season") or {}).get("state") == "stopped"
            and ((off.get("season") or {}).get("stopped") or {}).get("id") == closing.get("id")
            and {"at", "by", "id"} <= set((off.get("season") or {}).get("stopped") or {})
            and written.returncode == 0 and faced(written).get("written") == ["budget"]
            and ((declaration.get("started") or {}).get("state")) == "stopped"):
        bench.refusals += len(running)
        held("(c) written off season alone", "in season: declare, declare --season and start refuse season-running "
             "naming team stop, nothing written; off season: declare writes budget; status season.state stopped with "
             "season.stopped {at, by, id}; declaration started.state stopped")
    else:
        failures.append(f"  ✗ (c) written off season     said={said} same={kept('d') == stood_d} "
                        f"season={off.get('season')} written={written.returncode}/{faced(written)} "
                        f"declaration={declaration.get('started')} {written.stderr.strip()[-200:]!r}")

    # --- (d) the restart catches nothing up ---------------------------------------------------------------------
    restarted = h.call("team", "start", "c", "--no-tick", now="10:00")
    count = len(h.events("c"))
    h.call("team", "tick", "c", now="10:01")
    after = h.events("c")[count:]
    on = h.face("c", now="10:02")
    recurrence = next(iter(on.get("recurrences") or []), {})
    if (restarted.returncode == 0 and not [one for one in after if one.get("kind") in ("task", "ceremony-due")]
            and (on.get("season") or {}).get("state") == "running" and "stopped" not in (on.get("season") or {})
            and recurrence.get("due") is False and recurrence.get("next_due") == "2026-10-02T09:00"):
        held("(d) the restart catches nothing up", "started at 10:00: the tick of 10:01 opens no occurrence and rings "
             "no daily; season.state running; R1 due false, next_due Friday 09:00")
    else:
        failures.append(f"  ✗ (d) the restart            rc={restarted.returncode} after={[one.get('kind') for one in after]} "
                        f"season={on.get('season')} recurrence={recurrence} {restarted.stderr.strip()[-200:]!r}")

    # --- (e) the flags a form needs, off season ---------------------------------------------------------------
    h.off_season("c")
    piped = lambda *args, text: cli(h.engine, "--instance", str(h.house), "team", "declare", "c", *args, "--json",
                                    cwd=h.ws, env=h.env, stdin=text)
    body_t = piped("--body-file", "-", text="The word from the post.\n")
    body_s = piped("--season", "--body-file", "-", text="The season's word from the post.\n")
    team_md = (h.teams / "c" / "TEAM.md").read_text(encoding="utf-8")
    season_md = (h.teams / "c" / "SEASON.md").read_text(encoding="utf-8")
    joined = h.call("team", "declare", "c", "--member", "x", "agents/x", "--report", "w x -> m", "--json")
    joined_md = (h.teams / "c" / "TEAM.md").read_text(encoding="utf-8")
    parted = h.call("team", "declare", "c", "--no-report", "m", "--json")
    parted_md = (h.teams / "c" / "TEAM.md").read_text(encoding="utf-8")
    stood_e = kept("c")
    bad = {"participant-unknown": h.call("team", "declare", "c", "--report", "ghost -> m"),
           "team-invalid": h.call("team", "declare", "c", "--report", "w")}
    codes_e = {wanted: (one.returncode, code(one.stderr)) for wanted, one in bad.items()}
    if (body_t.returncode == 0 and faced(body_t).get("written") == ["body"]
            and team_md.endswith("---\nThe word from the post.\n")
            and body_s.returncode == 0 and faced(body_s).get("written") == ["body"]
            and season_md.endswith("---\nThe season's word from the post.\n")
            and joined.returncode == 0 and faced(joined).get("written") == ["agents", "reports"]
            and "reports: |\n  w x -> m\n" in joined_md and "  w -> m\n" not in joined_md
            and parted.returncode == 0 and faced(parted).get("written") == ["reports"] and "reports:" not in parted_md
            and codes_e == {wanted: (2, wanted) for wanted in bad} and kept("c") == stood_e):
        bench.refusals += len(bad)
        held("(e) the flags a form needs", "--body-file - writes TEAM.md's body, and SEASON.md's under --season; "
             "--report 'w x -> m' replaces the line of m, --no-report m takes the block out; ghost: "
             "participant-unknown, no arrow: team-invalid, nothing written")
    else:
        failures.append(f"  ✗ (e) the form's flags       rc={body_t.returncode}/{body_s.returncode}/{joined.returncode}/"
                        f"{parted.returncode} faces={faced(body_t)}/{faced(joined)}/{faced(parted)} codes={codes_e} "
                        f"team={joined_md!r} {(body_t.stderr or joined.stderr or parted.stderr).strip()[-200:]!r}")

    # --- (f) status says the season's state by the event that made it -------------------------------------------
    def marks(said: str) -> list[int]:
        return [int(one) for one in re.findall(r"\(#(\d+)\)", said)]
    h.declare("s", TEAM)
    h.call("team", "start", "s", "--message", "do it", "--no-tick", now="08:00")
    opened = marks(h.call("team", "status", "s", now="08:01").stdout)
    paused = h.call("team", "pause", "s", now="08:02")
    pause_id = h.events("s")[-1]["id"]
    under_pause = marks(h.call("team", "status", "s", now="08:03").stdout)
    h.call("team", "resume", "s", "--no-tick", now="08:04")
    h.call("team", "stop", "s", "--no-tick", now="08:05")
    stop_id = next((one["id"] for one in reversed(h.events("s")) if one.get("kind") == "season-stopped"), None)
    off = marks(h.call("team", "status", "s", now="08:06").stdout)
    again = h.call("team", "start", "s", "--message", "a second season", "--no-tick", now="08:07")
    second = h.call("team", "status", "s", now="08:08").stdout
    ranks = [line.split()[1] for line in second.splitlines() if line.split()[:1] == ["season"]]
    if (paused.returncode == 0 and under_pause == opened + [pause_id] and off == opened + [stop_id]
            and again.returncode == 0 and ranks == ["2"]):
        held("(f) status says the season's state", f"under the pause, status names (#{pause_id}) beside the start's "
             f"{opened}; off season, (#{stop_id}); a second season opened, its line says the rank 2")
    else:
        failures.append(f"  ✗ (f) the season at status    paused={paused.returncode} {under_pause} off={off} "
                        f"opened={opened} ids={pause_id}/{stop_id} again={again.returncode} ranks={ranks}")

    # --- (g) the start judged again under the journal's lock -------------------------------------------------------
    # the start is seen waiting at /proc/locks; without it the case is not played: nothing shows the wait
    if LOCKS.is_file():
        opening = {key: value for key, value in T.by_kind(h.events("d"), "team-started")[-1].items()
                   if key not in ("at", "id", "team")}
        meantime = {"g-deleting": {"kind": "deleting"}, "g-running": {**opening, "kind": "team-started"}}
        refused_g, waited_g, kinds_g = {}, {}, {}
        for name, event in meantime.items():
            h.declare(name, TEAM)                             # m and w stand already: nothing is born
            journal = h.journal_of(name)
            with record.held(journal):                        # a writer of the journal, as a post holds it
                starting = subprocess.Popen([sys.executable, str(h.engine), "--instance", str(h.house), "team",
                                             "start", name, "--no-tick"], cwd=h.ws,
                                            env={**os.environ, **h.env, "PP_NOW": T.THURSDAY + "11:00"},
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                waited_g[name] = reached(starting, journal)
                journal.write_text(json.dumps({"at": "2026-10-01T09:00:00+00:00", "id": 1, "team": name, **event})
                                   + "\n", encoding="utf-8")
            _, said_g = starting.communicate(timeout=120)
            refused_g[name] = (starting.returncode, code(said_g))
            kinds_g[name] = [one.get("kind") for one in h.events(name)]
        if (all(waited_g.values())
                and refused_g == {"g-deleting": (2, "team-deleting"), "g-running": (2, "season-running")}
                and kinds_g == {"g-deleting": ["deleting"], "g-running": ["team-started"]}):
            bench.refusals += len(meantime)
            held("(g) the start judged again under the lock", "a start waiting for the journal's lock: a deleting "
                 "written meanwhile refuses team-deleting, a team-started season-running; the journal holds the "
                 "meantime's event alone")
        else:
            failures.append(f"  ✗ (g) the start under the lock waited={waited_g} refused={refused_g} kinds={kinds_g}")
    else:
        print("  · (g) NOT PLAYED -- no /proc/locks here to see the start wait for the journal's lock")
    return 0
