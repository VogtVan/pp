"""Scenario `team-reset` -- 4 case(s) (batch le-tick, rework of 2026-10-09: decision 64 of the phase,
team 0.16.0): `team reset <name> [--member <m>]` forgets a member's run by its agent's console; each
case names the invariant of `team-sim-reframe.py` or `team-sim-members.py` it replays.
- (a) the refusals before any forgetting (I19): `team-unknown`, `team-not-started`, `participant-unknown`;
  `member-running` on a member whose intent has no end, then on a member whose run's wake lock the bench
  holds -- no slot removed, nothing written
- (b) the tick lock held (KC33): the bench holds `tick.lock`, `team reset` waits `call_lock_wait` (1 s)
  then refuses `team-busy`, nothing forgotten
- (c) the reset (I7, I18): u holds T1 and T2 in its one run K; `team reset --member u`: `run-reset
  {member: u, run: K}`, K's slot gone at the agent, `status` says `run — · reset` and no longer K; the
  owner's reply wakes u on a NEW run whose head carries `[history of T1 for u]`, `[history of T2 for
  u]`, then the inbox, the intention served by pp in its output; T1 merged
- (d) a member without a run: `team reset` without `--member` says `no run to forget`, nothing written
"""
from __future__ import annotations

import json
import re
import time

from conductor import persistence
from conductor.state import lock
from tests.harness import holding, support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "u": {"T1": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which branch?"}}},
                     {"sleep": 0.1, "body": {"done": "merged"}}],
              "T2": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which tag?"}}},
                     {"sleep": 0.1, "body": {"done": "tagged"}}]}})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of
    settings = h.house / "SETTINGS.md"                      # the owner's edit: a short wait for the house's locks
    settings.write_text(re.sub(r"^call_lock_wait: \d+$", "call_lock_wait: 1", settings.read_text(encoding="utf-8"),
                               count=1, flags=re.M), encoding="utf-8")

    h.declare("up", "---\nagents: |\n  u agents/u\nroot: u\nschedule: off\n---\nMerge what is asked.\n")
    up = h.call("team", "start", "up", "--message", "merge PR 11", *h.harnessed)
    asked1 = h.settled("up", lambda found: bool(by_kind(found, "wake-ended", agent="u")) and all_ended(found), 60)
    up2 = h.call("team", "post", "up", "--to", "u", "--message", "tag release 2")
    asked = asked1 and h.settled("up", lambda found: len(by_kind(found, "wake-ended", agent="u")) == 2
                                 and all_ended(found), 60)
    found = h.events("up")
    kept = next((one.get("run") for one in reversed(by_kind(found, "wake-ended", agent="u"))), "")
    slot = persistence.slot_of(h.meta_of("agents/u"), kept) if kept else h.ws
    stands = bool(kept) and slot.is_file()

    # --- (a) judged before anything is forgotten -- I19 -----------------------------------------------
    unknown = h.call("team", "reset", "nope")
    h.declare("never", "---\nagents: |\n  n agents/n\nroot: n\nschedule: off\n---\nNever started.\n")
    never = h.call("team", "reset", "never")
    nobody = h.call("team", "reset", "up", "--member", "zz")
    h.declare("busy", "---\nagents: |\n  b agents/b\nroot: b\nschedule: off\n---\nBusy.\n")
    started_b = h.call("team", "start", "busy", "--message", "work", *h.harnessed, "--no-tick")
    found_b = h.events("busy")
    do_b = next(one["id"] for one in by_kind(found_b, "post", verb="do"))
    last_b = max(one["id"] for one in found_b)
    with h.journal_of("busy").open("a", encoding="utf-8") as handle:   # an intent of b without an end
        handle.write(json.dumps({"at": "2026-10-09T12:00:00+00:00", "id": last_b + 1, "team": "busy",
                                 "kind": "wake-intent", "tag": "busy-b", "agent": "b", "path": "agents/b",
                                 "task": "T1", "run": None, "index": 1, "messages": [do_b]}) + "\n")
    running_b = h.call("team", "reset", "busy")
    lock_u = h.meta_of("agents/u") / ".sys" / "state" / f"session-{kept}.wake.lock"
    deadline = time.monotonic() + 30                  # the last wake-up may still be releasing its lock
    while lock.held(lock_u) and time.monotonic() < deadline:
        time.sleep(0.2)
    with holding(lock_u):                                    # u's run still releasing its wake lock
        running_u = h.call("team", "reset", "up", "--member", "u")
    refusals = {"team-unknown": unknown, "team-not-started": never, "participant-unknown": nobody,
                "member-running": running_b}
    untouched = slot.is_file() and not by_kind(h.events("up"), "run-reset") and not by_kind(h.events("busy"), "run-reset")
    if (up.returncode == 0 and up2.returncode == 0 and asked and stands and started_b.returncode == 0
            and all(one.returncode == 2 and code in one.stderr for code, one in refusals.items())
            and running_u.returncode == 2 and "member-running" in running_u.stderr and untouched):
        held("(a) judged before forgetting", "team-unknown, team-not-started, participant-unknown, member-running "
             f"(an intent without an end; u's wake lock held): rc 2 each, {kept}'s slot standing, no run-reset -- I19")
    else:
        failures.append(f"  ✗ (a) judged before forgetting  rc={up.returncode}/{up2.returncode} asked={asked} "
                        f"stands={stands} {[(code, one.returncode, one.stderr.strip()[-120:]) for code, one in refusals.items()]} "
                        f"u={running_u.returncode} {running_u.stderr.strip()[-160:]!r} untouched={untouched}")

    # --- (b) the tick lock held: team-busy past call_lock_wait -- KC33 --------------------------------
    with holding(h.journal_of("up").parent / "tick.lock"):
        waited = h.call("team", "reset", "up", "--member", "u")
    if waited.returncode == 2 and "team-busy" in waited.stderr and slot.is_file() and not by_kind(h.events("up"), "run-reset"):
        held("(b) the tick lock held", "team reset waits call_lock_wait (1 s), then team-busy: nothing forgotten -- KC33")
    else:
        failures.append(f"  ✗ (b) the tick lock held        rc={waited.returncode} {waited.stderr.strip()[-200:]!r} "
                        f"slot={slot.is_file()}")

    # --- (c) the reset: a new run told every open task -- I7, I18 --------------------------------------
    reset = h.call("team", "reset", "up", "--member", "u")
    found = h.events("up")
    resets = [(one.get("member"), one.get("run")) for one in by_kind(found, "run-reset")]
    line = h.status_line("up", "u · ")
    ask_u = next((one["id"] for one in by_kind(found, "post", verb="ask") if one.get("task") == "T1"), -1)
    replied = h.call("team", "post", "up", "--task", "T1", "--reply", str(ask_u), "--message", "main")
    done = h.settled("up", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 45)
    found = h.events("up")
    reopened = next((one for one in h.prompts_of("u") if "[history of T1 for u]" in one), "")
    intention_at, history_at = reopened.find("Merge what is asked."), reopened.find("[history of T1 for u]")
    output_at = reopened.find("▌ pp · run")
    second_at, inbox_at = reopened.find("[history of T2 for u]"), reopened.find("[inbox]")
    new_runs = {one.get("run") for one in by_kind(found, "wake-launched", agent="u")} - {kept}
    if (reset.returncode == 0 and resets == [("u", kept)] and not slot.is_file()
            and "run — · reset" in line and kept not in line and replied.returncode == 0 and done
            and len(new_runs) == 1 and 0 <= history_at < second_at < inbox_at < output_at < intention_at
            and reopened.count("Merge what is asked.") == 1
            and "INFORMATION — TEAM.md" in reopened[output_at:intention_at]
            and "reply from house on T1: main" in reopened[inbox_at:]
            and not any("run-unknown" in str(one.get("reason")) for one in by_kind(found, "wake-failed"))
            and result_of(found, "T1") == "merged"):
        held("(c) the reset", f"run-reset {{u, {kept}}}, the slot gone, status {line.strip()!r}; the reply opens "
             f"run {sorted(new_runs)[0]} told T1's then T2's history, then the inbox, the intention served in its "
             "output; T1 merged -- I7, I18")
    else:
        failures.append(f"  ✗ (c) the reset                 rc={reset.returncode}/{replied.returncode} "
                        f"{reset.stderr.strip()[-200:]!r} resets={resets} slot={slot.is_file()} line={line!r} "
                        f"done={done} runs={new_runs} at={history_at}/{second_at}/{inbox_at}/{output_at}/{intention_at} "
                        f"{reopened[:400]!r}")

    # --- (d) a member without a run -------------------------------------------------------------------
    h.declare("fresh", "---\nagents: |\n  v agents/v\nroot: v\nschedule: off\n---\nNot woken yet.\n")
    fresh = h.call("team", "start", "fresh", "--message", "later", *h.harnessed, "--no-tick")
    before = len(h.events("fresh"))
    none = h.call("team", "reset", "fresh")
    if (fresh.returncode == 0 and none.returncode == 0 and "no run to forget" in none.stdout
            and len(h.events("fresh")) == before):
        held("(d) a member without a run", f"{none.stdout.strip()!r}; nothing written")
    else:
        failures.append(f"  ✗ (d) a member without a run    rc={fresh.returncode}/{none.returncode} "
                        f"{(none.stdout + none.stderr).strip()[-200:]!r} events={before}->{len(h.events('fresh'))}")
    return 0
