"""Scenario `team-resume` -- 2 case(s) (batch la-reprise-d-une-tache, 2026-10-10: decisions 67-68 of the
phase, team 0.18.0): `team resume <name> --task <id>` takes a STOPPED task back; each case names the
invariant of `team-sim-reframe.py` it replays.
- (a) the refusals before any writing (I23's guard): `team-unknown`, `team-not-started`, `task-unknown`,
  `task-resolved`, `task-not-blocked` (an open task nobody failed on), `principal-unknown`, and without `--task`
  `team-not-paused` (team 0.32.0: `team resume <name>` resumes a paused team) -- rc 2 each, every journal
  byte-identical
- (b) a stopped task taken back (I23, I18): h delegates to h1, a note posted while h waits, `team stop`;
  h1's running wake-up ends routed nowhere, the note RETURNED; `team resume --message "go on"` writes
  `resumed {task, by, from: [stopped]}`, then a `note` to h and to h1 -- the holders at the stop --; h1 is
  woken under its SAME run key with the note at its head, answers `done`, h is woken under its own key and
  resolves T1; the returned note reaches no head and stays returned; `status` and `log` say the resume
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "h": [{"sleep": 0.2, "body": {"do": ["h1"]}}, {"sleep": 0.1, "body": {"done": "resumed"}}],
        "h1": [{"sleep": 3.0, "body": {"done": True}}, {"sleep": 0.1, "body": {"done": True}}],
        "d": [{"sleep": 0.1, "body": {"done": "finished"}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    # --- (a) judged before anything is written -------------------------------------------------------
    h.declare("never", "---\nagents: |\n  n agents/n\nroot: n\nschedule: off\n---\nNever started.\n")
    h.declare("idle", "---\nagents: |\n  i agents/i\nroot: i\nschedule: off\n---\nOne task, still due.\n")
    h.declare("over", "---\nagents: |\n  d agents/d\nroot: d\nschedule: off\n---\nDone at once.\n")
    idle = h.call("team", "start", "idle", "--message", "later", *h.harnessed, "--no-tick")
    over = h.call("team", "start", "over", "--message", "finish", *h.harnessed)
    finished = h.settled("over", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 45)
    journals = {name: h.journal_of(name) for name in ("idle", "over")}
    before = {name: path.read_bytes() for name, path in journals.items()}
    refusals = {
        "team-unknown": h.call("team", "resume", "nope", "--task", "T1"),
        "team-not-started": h.call("team", "resume", "never", "--task", "T1"),
        "task-unknown": h.call("team", "resume", "idle", "--task", "T9"),
        "task-resolved": h.call("team", "resume", "over", "--task", "T1"),
        "task-not-blocked": h.call("team", "resume", "idle", "--task", "T1"),
        "principal-unknown": h.call("team", "resume", "idle", "--task", "T1", "--as", "zz"),
        "team-not-paused": h.call("team", "resume", "idle")}
    untouched = all(path.read_bytes() == before[name] for name, path in journals.items())
    if (idle.returncode == 0 and over.returncode == 0 and finished and untouched
            and all(one.returncode == 2 and code in one.stderr for code, one in refusals.items())):
        held("(a) judged before writing", "team-unknown, team-not-started, task-unknown, task-resolved, "
             "task-not-blocked, principal-unknown, team-not-paused: rc 2 each, both journals byte-identical")
    else:
        failures.append(f"  ✗ (a) judged before writing    rc={idle.returncode}/{over.returncode} finished={finished} "
                        f"untouched={untouched} "
                        f"{[(code, one.returncode, one.stderr.strip()[-120:]) for code, one in refusals.items()]}")

    # --- (b) a stopped task taken back: the holders noted, each in its run -- I23, I18 -----------------
    h.declare("halt", "---\nagents: |\n  h agents/h\n  h1 agents/h1\nreports: |\n  h1 -> h\nroot: h\n"
                      "schedule: off\n---\nHalt, then go on.\n")
    started = h.call("team", "start", "halt", "--message", "review slowly", *h.harnessed)
    running = h.settled("halt", lambda found: bool(by_kind(found, "wake-launched", agent="h1")), 60)
    noted = h.call("team", "post", "halt", "--task", "T1", "--message", "while you wait")
    stopped = h.call("team", "stop", "halt", "--task", "T1")
    quiet = h.settled("halt", lambda found: len(by_kind(found, "wake-ended", agent="h1")) >= 1 and all_ended(found), 60)
    found = h.events("halt")
    runs = {member: T.runs_launched(found, member) for member in ("h", "h1")}
    returned = [one.get("message") for one in by_kind(found, "returned")]
    resumed = h.call("team", "resume", "halt", "--task", "T1", "--message", "go on")
    done = h.settled("halt", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    found = h.events("halt")
    resumes = by_kind(found, "resumed")
    mark = resumes[0]["id"] if resumes else 10 ** 9
    notes = [(one.get("from"), one.get("to"), one.get("text")) for one in by_kind(found, "post", verb="note")
             if one["id"] > mark]
    after = {member: {one.get("run") for one in by_kind(found, "wake-launched", agent=member) if one["id"] > mark}
             for member in ("h", "h1")}
    prompts = {member: h.prompts_of(member) for member in ("h", "h1")}
    revived = prompts["h1"][-1] if len(prompts["h1"]) >= 2 else ""
    status = h.call("team", "status", "halt").stdout
    log = h.call("team", "log", "halt").stdout
    if (started.returncode == 0 and running and noted.returncode == 0 and stopped.returncode == 0 and quiet
            and resumed.returncode == 0 and done and len(returned) == 1
            and [(one.get("task"), one.get("by"), one.get("from")) for one in resumes] == [("T1", "house", ["stopped"])]
            and sorted(notes) == [("house", "h", "go on"), ("house", "h1", "go on")]
            and after["h1"] and after["h1"] <= runs["h1"] and after["h"] and after["h"] <= runs["h"]
            and "note from house on T1: go on" in revived
            and not any("while you wait" in one for one in prompts["h"] + prompts["h1"])
            and [one.get("message") for one in by_kind(found, "returned")] == returned
            and T.result_of(found, "T1") == "resumed"
            and f"T1 · resolved" in status and f"resumed T1 by house · from stopped" in log):
        held("(b) a stopped task taken back", f"resumed #{mark} from [stopped], a note to h and h1; h1 woken in run "
             f"{sorted(after['h1'])[0]} (its own), h in {sorted(after['h'])[0]}; T1 resolved 'resumed'; the returned "
             "note in no head -- I23, I18")
    else:
        failures.append(f"  ✗ (b) a stopped task taken back rc={started.returncode}/{noted.returncode}/{stopped.returncode}/"
                        f"{resumed.returncode} running={running} quiet={quiet} done={done} {resumed.stderr.strip()[-200:]!r} "
                        f"resumes={resumes} notes={notes} runs={runs} after={after} returned={returned} "
                        f"result={T.result_of(found, 'T1')!r} {revived[:300]!r}")
    return 0
