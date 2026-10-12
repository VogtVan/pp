"""Scenario `team-budget-raised-wakes` -- 1 case(s) (batch le-budget-de-l-equipe, 2026-10-11: row 76 of the
study § 18, team 0.22.0): `team budget --wakes` raises `budget-wakes` without a start, and the member is woken
in its SAME run; the bound in dollars is `team-budget-raised`'s. The case names the invariant of
`team-sim-reframe.py` it replays.
- (d) the budget raised in wake-ups (I18, KBE10): `budget-wakes: 1`, w asks the owner, the reply finds the
  bound spent; `team budget --wakes 2` and w is woken in its SAME run; status and `status --json` say the
  budget
"""
from __future__ import annotations

import json
import subprocess

from tests.harness import cli, support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "w": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which date?"}}},
              {"sleep": 0.1, "body": {"done": "dated"}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    def reply(name: str) -> subprocess.CompletedProcess:
        ask = next((one["id"] for one in by_kind(h.events(name), "post", verb="ask")), -1)
        return h.call("team", "post", name, "--task", "T1", "--reply", str(ask), "--message", "main")

    # --- (d) the budget raised in wake-ups: the member woken in its SAME run -- I18, KBE10 ----------------
    h.declare("count", "---\nagents: |\n  w agents/w\nroot: w\nbudget-wakes: 1\nbudget: 3\nschedule: off\n---\n"
                       "One wake-up.\n")
    counted = h.call("team", "start", "count", "--message", "date the release", *h.harnessed)
    asked_w = h.settled("count", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), 60)
    replied_w = reply("count")
    spent_w = by_kind(h.events("count"), "budget-spent")
    raised_w = h.call("team", "budget", "count", "--wakes", "2")
    done_w = h.settled("count", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    found = h.events("count")
    first_run = next((one.get("run") for one in by_kind(found, "wake-ended", agent="w")), None)
    runs = [one.get("run") for one in by_kind(found, "wake-intent", agent="w")]
    text = h.status_line("count", "budget ")
    played = cli(h.engine, "--instance", str(h.house), "team", "status", "count", "--json", cwd=h.ws, env=h.env)
    try:
        face = json.loads(played.stdout.splitlines()[0]).get("budget")
    except (ValueError, IndexError, AttributeError):
        face = None
    if (counted.returncode == 0 and asked_w and replied_w.returncode == 0 and len(spent_w) == 1
            and spent_w[0].get("unit") == "wakes" and raised_w.returncode == 0 and done_w
            and runs == [None, first_run] and first_run
            and text.startswith("budget 0.02/3 USD") and "left 2.98" in text
            and face == {"cap": 3.0, "spent": 0.02, "reserved": 0.0, "left": 2.98}):
        held("(d) the budget raised in wake-ups", f"budget-wakes 1 spent; --wakes 2 raised; w woken in its run "
             f"{first_run}, T1 done; status `{text}`, --json {face} -- I18, KBE10")
    else:
        failures.append(f"  ✗ (d) raised in wake-ups     rc={counted.returncode}/{replied_w.returncode}/"
                        f"{raised_w.returncode} asked={asked_w} spent={spent_w} done={done_w} runs={runs} "
                        f"first={first_run} text={text!r} face={face} {raised_w.stderr.strip()[-200:]!r}")
    return 0
