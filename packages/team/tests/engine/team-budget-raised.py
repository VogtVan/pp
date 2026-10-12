"""Scenario `team-budget-raised` -- 2 case(s) (batch le-budget-de-l-equipe, 2026-10-11: row 76 of the study
§ 18, team 0.22.0): `team budget` raises the team's bounds without a start -- `budget-raised`, the replay's
limits raised and `budget-spent` lifted, the members' runs kept. Each case names the invariant of
`team-sim-reframe.py` it replays; a wake-up's share of the budget is `team-budget`'s, the
bound in wake-ups `team-budget-raised-wakes`'s.
- (c) the budget raised in money (I10, I18): `budget: 0.015`, two wake-ups paid (0.02), `budget-spent`;
  `team budget` at or below what is spent refuses `budget-invalid`, `team budget 1` writes `budget-raised`
  and the member due is launched; a team never started refuses `team-not-started`
- (e) two writers (KC33): two `team budget --wakes` played together, five times -- every `budget-raised`
  kept, the journal's ids consecutive
"""
from __future__ import annotations

import subprocess
import sys

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "b": [{"sleep": 0.2, "body": {"do": ["b1", "b2"]}}, {"sleep": 0.1, "body": {"done": "paid"}}],
        "b1": [{"sleep": 0.2, "body": {"done": True}}],
        "b2": [{"sleep": 0.1, "body": {"done": True}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    # --- (c) the budget raised in money -- I10, I18 -------------------------------------------------------
    h.declare("paid", "---\nagents: |\n  b agents/b\n  b1 agents/b1\n  b2 agents/b2\nreports: |\n  b1 b2 -> b\n"
                      "root: b\nparallel: 1\nbudget: 0.015\nschedule: off\n---\nSpend little.\n")
    h.declare("never", "---\nagents: |\n  n agents/n\nroot: n\n---\nNever started.\n")
    paid = h.call("team", "start", "paid", "--message", "review cheaply", *h.harnessed)
    spent = h.settled("paid", lambda found: bool(by_kind(found, "budget-spent")) and all_ended(found), 60)
    low = h.call("team", "budget", "paid", "0.02")
    unstarted = h.call("team", "budget", "never", "1")
    raised = h.call("team", "budget", "paid", "1")
    done_c = h.settled("paid", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    found = h.events("paid")
    raises = by_kind(found, "budget-raised")
    after = [one["agent"] for one in by_kind(found, "wake-intent") if raises and one["id"] > raises[0]["id"]]
    if (paid.returncode == 0 and spent and low.returncode == 2 and "budget-invalid" in low.stderr
            and unstarted.returncode == 2 and "team-not-started" in unstarted.stderr
            and raised.returncode == 0 and len(raises) == 1 and raises[0].get("budget") == 1.0 and done_c
            and "b2" in after and len(by_kind(found, "budget-spent")) == 1):
        held("(c) the budget raised in money", f"0.02 spent of 0.015: budget-spent; 0.02 refuses budget-invalid, a "
             f"team never started team-not-started; budget 1 raised #{raises[0]['id']}, then {' '.join(after)} "
             "woken, T1 done -- I10, I18")
    else:
        failures.append(f"  ✗ (c) raised in money        rc={paid.returncode}/{low.returncode}/{unstarted.returncode}/"
                        f"{raised.returncode} spent={spent} raises={raises} after={after} done={done_c} "
                        f"{low.stderr.strip()[-160:]!r} {unstarted.stderr.strip()[-160:]!r} {raised.stderr.strip()[-200:]!r}")

    # --- (e) two writers: two `team budget` at once, five times -- KC33 -----------------------------------
    h.declare("count", "---\nagents: |\n  w agents/w\nroot: w\nbudget-wakes: 1\nschedule: off\n---\nOne wake-up.\n")
    h.call("team", "start", "count", "--message", "date the release", *h.harnessed, "--no-tick")
    before = len(h.events("count"))
    for n in range(5):
        pair = [subprocess.Popen([sys.executable, str(h.engine), "--instance", str(h.house), "team", "budget", "count",
                                  "--wakes", str(wakes), "--no-tick"],
                                 cwd=str(h.ws), env={**h.env}, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                for wakes in (3 + 2 * n, 4 + 2 * n)]
        for one in pair:
            one.communicate(timeout=60)
    found = h.events("count")
    ids = [one["id"] for one in found]
    raised_n = sorted(one.get("wakes") for one in by_kind(found[before:], "budget-raised"))
    if ids == list(range(ids[0], ids[0] + len(ids))) and raised_n == list(range(3, 13)):
        held("(e) two writers", f"two team budget at once, five times: 10 budget-raised kept, "
             f"{len(ids)} ids consecutive -- KC33")
    else:
        failures.append(f"  ✗ (e) two writers           ids={ids[-12:]} raised={raised_n}")
    return 0
