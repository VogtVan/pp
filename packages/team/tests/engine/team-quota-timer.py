"""Scenario `team-quota-timer` -- 4 case(s): the TIMER of a team whose member a provider's limit holds is due at the
limit's `until`, never at the step (batch le-minuteur-a-until, s.1586) -- the sibling of `team-quota`, its team under the
modelled LLM's `quota` variant, the hour a limit ends moved in the journal while the team rests (`until_set`);
`deadline_of` read on the team's state by the pp-team script vendored at the house, under a step of 300 s.
- (a) qa held until six hours from now, nothing else due: `deadline_of` gives that `until`, not the step
- (b) a recurrence `--every 1h` posted, its first occurrence opened by the post's tick (qa held, nobody launched): its
  next period, an hour from now and before the `until`, is the deadline
- (c) the timer knows its hour by the wall clock (l-heure-murale-du-minuteur): a timer whose `--due` has passed already
  and whose `--sleep` is an hour -- what a sleep of the machine leaves, its monotonic clock stopped -- ticks at once:
  it ends, its mark taken, the member woken
- (d) the tick arms its timer at the until: a team under `schedule: 5m`, its member held by the limit until two minutes
  from now, nothing else due -- `team tick` replaces the step's timer by one due at that `until` (its mark), the member
  not launched again; the stop takes the timer
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
from datetime import datetime, timedelta, timezone

from tests.harness import support

T = support(__file__, "team")
STEP = 300


def until_set(h, name: str, until: str) -> None:
    """The `until` of the team's last `quota-reached` written as given, while the team rests, every other field kept."""
    journal = h.journal_of(name)
    lines = [json.loads(line) for line in journal.read_text(encoding="utf-8").splitlines() if line.strip()]
    last = max((each["id"] for each in lines if each.get("kind") == "quota-reached"), default=None)
    for each in lines:
        if each.get("id") == last:
            each["until"] = until
    journal.write_text("".join(json.dumps(each, ensure_ascii=False) + "\n" for each in lines), encoding="utf-8")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})
    by_kind, all_ended = T.by_kind, T.all_ended
    module = h.module()
    h.declare("q", "---\nagents: |\n  qa agents/qa\nroot: qa\nschedule: off\n---\nWork while the provider lets you.\n")
    started = h.call("team", "start", "q", "--message", "work T1", "--provider", "model", "--model", "quota")
    reached = h.settled("q", lambda found: bool(by_kind(found, "quota-reached")) and all_ended(found), 30)
    until = (datetime.now(timezone.utc) + timedelta(hours=6)).replace(microsecond=0)
    until_set(h, "q", until.isoformat())
    local = until.astimezone().replace(tzinfo=None)

    def deadline() -> tuple[datetime, datetime | None]:
        clock = datetime.now().replace(microsecond=0)
        return clock, module.deadline_of(module.state_of(h.journal_of("q")), clock, STEP)

    # --- (a) the limit's until, not the step ----------------------------------------------------------------------------
    clock, due = deadline()
    if started.returncode == 0 and reached and due == local:
        held("(a) the timer due at the limit's until", f"deadline {due} = until, {clock} + {STEP} s not taken")
    else:
        failures.append(f"  ✗ (a) due at until             rc={started.returncode} reached={reached} clock={clock} "
                        f"due={due} until={local}")

    # --- (b) a nearer hour wins ---------------------------------------------------------------------------------------
    posted = h.call("team", "post", "q", "--every", "1h", "--message", "each hour")    # its tick opens the first
    clock, due = deadline()
    near = due is not None and clock + timedelta(minutes=55) <= due <= clock + timedelta(minutes=61) and due < local
    if posted.returncode == 0 and near:
        held("(b) a recurrence an hour away wins over the until", f"deadline {due}, until {local}")
    else:
        failures.append(f"  ✗ (b) the nearer hour          rc={posted.returncode} clock={clock} due={due} until={local} "
                        f"{posted.stderr.strip()[-200:]!r}")

    # --- (c) the wall clock ends the sleep ----------------------------------------------------------------------------
    h.declare("late", "---\nagents: |\n  lm agents/lm\nroot: lm\nschedule: off\n---\nOne task.\n")
    h.call("team", "start", "late", "--message", "tick me", *h.harnessed, "--no-tick")
    due = (datetime.now() - timedelta(minutes=1)).replace(microsecond=0).isoformat()
    token = "0123456789abcdef"
    timer = subprocess.Popen([sys.executable, str(h.engine), "--instance", str(h.house), "team", "timer", "late",
                              "--sleep", "3600", "--due", due, "--token", token],
                             cwd=h.ws, env={**os.environ, **h.env}, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=True)
    mark = h.records / "teams" / "late" / "tick.timer"
    mark.write_text(json.dumps({"pid": timer.pid, "due": due, "token": token}), encoding="utf-8")
    try:
        ended = timer.wait(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(timer.pid, signal.SIGKILL)
        timer.wait()
        ended = None
    woken = bool(by_kind(h.events("late"), "wake-intent"))
    if ended == 0 and not mark.exists() and woken:
        held("(c) a due already passed ticks at once", f"--due {due}, --sleep 3600: ended, mark taken, lm woken")
    else:
        failures.append(f"  ✗ (c) the wall clock          due={due} ended={ended} mark={mark.exists()} woken={woken}")

    # --- (d) the tick arms its timer at the until -----------------------------------------------------------------------
    h.declare("qn", "---\nagents: |\n  qb agents/qb\nroot: qb\nschedule: 5m\n---\nWork while the provider lets you.\n")
    net_started = h.call("team", "start", "qn", "--message", "work T1", "--provider", "model", "--model", "quota")
    net_reached = h.settled("qn", lambda found: bool(by_kind(found, "quota-reached")) and all_ended(found), 30)
    near_until = (datetime.now(timezone.utc) + timedelta(minutes=2)).replace(microsecond=0)
    until_set(h, "qn", near_until.isoformat())
    net_tick = h.call("team", "tick", "qn")
    net_mark = h.records / "teams" / "qn" / "tick.timer"
    armed_due = json.loads(net_mark.read_text(encoding="utf-8")).get("due") if net_mark.is_file() else None
    net_found = h.events("qn")
    wanted = near_until.astimezone().replace(tzinfo=None).isoformat(timespec="seconds")
    h.off_season("qn")
    net_gone = h.timer_gone("qn")
    if (net_started.returncode == 0 and net_reached and net_tick.returncode == 0 and armed_due == wanted
            and len(T.intents_of(net_found, "qb")) == 1 and len(by_kind(net_found, "quota-reached")) == 1 and net_gone):
        held("(d) the tick arms its timer at the until", f"schedule 5m, qb held until {wanted}: the tick's timer due "
             f"{armed_due}, the step's timer replaced, qb not launched again; the stop takes the timer")
    else:
        failures.append(f"  ✗ (d) the timer at the until   rc={net_started.returncode}/{net_tick.returncode} "
                        f"reached={net_reached} due={armed_due} wanted={wanted} "
                        f"intents={len(T.intents_of(net_found, 'qb'))} gone={net_gone} {net_tick.stderr.strip()[-200:]!r}")
    return 0
