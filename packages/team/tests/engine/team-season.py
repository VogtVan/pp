"""Scenario `team-season` -- 3 case(s) (batch la-saison, 2026-10-12: row 82 of the study § 18, team 0.31.0): a
`team start` is a SEASON -- on a team at work too: TEAM.md read again, the cost and the counts afresh, the members'
runs kept. Each case names the invariant of `team-sim-reframe.py` it replays; the profiles are
`team-season-profiles`'s.
- (a) a season on a team at work (I18): w asks the owner on T1; `team start` without `--message` opens season 2,
  T1 still open, the season's cost 0; the reply wakes w in the SAME run, and T1 ends done
- (b) the season's budget (I10): `--budget 2 --budget-wakes 5` over a TEAM.md at `budget: 1` -- the face says the
  cap 2, `budget-wakes` 5 and the season's own; `team declaration` says no gap of `limits`; `--budget 0` refuses
  `budget-invalid`
- (c) a task's `wakes:` counted afresh (I10): under `wakes: 1`, k asks the owner, the reply finds the task
  `wakes-spent`; a season, and k is woken again and ends the task
"""
from __future__ import annotations

import json

from tests.harness import cli, support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "r": [{"sleep": 0.1, "body": {"do": ["w"]}}, {"sleep": 0.1, "body": {"done": "merged"}}],
        "w": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which branch?"}}},
              {"sleep": 0.1, "body": {"done": "main"}}],
        "k": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which day?"}}},
              {"sleep": 0.1, "body": {"done": "monday"}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    def face(name: str) -> dict:
        played = cli(h.engine, "--instance", str(h.house), "team", "status", name, "--json", cwd=h.ws, env=h.env)
        try:
            return json.loads(played.stdout)
        except ValueError:
            return {}

    def reply(name: str) -> None:
        ask = [one["id"] for one in by_kind(h.events(name), "post", verb="ask")][-1]
        h.call("team", "post", name, "--task", "T1", "--reply", str(ask), "--message", "main")

    # --- (a) a season on a team at work: the member keeps its run -- I18 ---------------------------------
    h.declare("work", "---\nagents: |\n  r agents/r\n  w agents/w\nreports: |\n  w -> r\nroot: r\nschedule: off\n"
                      "---\nMerge together.\n")
    started = h.call("team", "start", "work", "--message", "merge PR 14", *h.harnessed)
    asked = h.settled("work", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), 60)
    season = h.call("team", "start", "work", *h.harnessed)
    opened = [one.get("task") for one in by_kind(h.events("work"), "task")]
    seasoned = face("work")
    reply("work")
    done = h.settled("work", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    found = h.events("work")
    w_runs = [one.get("run") for one in by_kind(found, "wake-launched", agent="w")]
    w_intents = [one.get("run") for one in by_kind(found, "wake-intent", agent="w")]
    if (started.returncode == 0 and asked and season.returncode == 0 and opened == ["T1"]
            and (seasoned.get("season") or {}).get("n") == 2 and seasoned.get("cost") == 0
            and [t.get("state") for t in seasoned.get("tasks") or []] == ["open"]
            and done and len(set(w_runs)) == 1 and w_intents == [None, w_runs[0]]):
        held("(a) a season on a team at work", f"season 2 on T1 open, cost 0; w woken in its run {w_runs[0]}, T1 done "
             "-- I18")
    else:
        failures.append(f"  ✗ (a) a season at work       rc={started.returncode}/{season.returncode} asked={asked} "
                        f"done={done} season={seasoned.get('season')} cost={seasoned.get('cost')} w={w_intents}/{w_runs} opened={opened} "
                        f"{season.stdout.strip()[-120:]!r} {season.stderr.strip()[-200:]!r}")

    # --- (b) the season's budget -- I10 --------------------------------------------------------------------------
    h.declare("funds", "---\nagents: |\n  f agents/f\nroot: f\nbudget: 1\nschedule: off\n---\nSpend within.\n")
    invalid = h.call("team", "start", "funds", "--message", "x", "--budget", "0", *h.harnessed, "--no-tick")
    funded = h.call("team", "start", "funds", "--message", "price it", "--budget", "2", "--budget-wakes", "5",
                    *h.harnessed, "--no-tick")
    funds = face("funds")
    declared = cli(h.engine, "--instance", str(h.house), "team", "declaration", "funds", "--json", cwd=h.ws, env=h.env)
    try:
        pending = json.loads(declared.stdout).get("pending")
    except ValueError:
        pending = "unreadable"
    if (invalid.returncode == 2 and "budget-invalid" in invalid.stderr and funded.returncode == 0
            and (funds.get("budget") or {}).get("cap") == 2.0 and (funds.get("limits") or {}).get("budget-wakes") == 5
            and funds.get("season") == {"n": 1, "at": (funds.get("started") or {}).get("at"), "budget": 2.0,
                                        "budget-wakes": 5}
            and pending == []):
        held("(b) the season's budget", "--budget 0 refuses budget-invalid; --budget 2 --budget-wakes 5 over TEAM.md's "
             "1: cap 2, budget-wakes 5, the season's own said; declaration: no gap -- I10")
    else:
        failures.append(f"  ✗ (b) the season's budget    rc={invalid.returncode}/{funded.returncode} "
                        f"budget={funds.get('budget')} limits={funds.get('limits')} season={funds.get('season')} "
                        f"pending={pending} {invalid.stderr.strip()[-120:]!r} {funded.stderr.strip()[-160:]!r}")

    # --- (c) a task's wakes: counted afresh -- I10 -----------------------------------------------------------
    h.declare("count", "---\nagents: |\n  k agents/k\nroot: k\nwakes: 1\nschedule: off\n---\nOne wake-up.\n")
    h.call("team", "start", "count", "--message", "date the release", *h.harnessed)
    h.settled("count", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), 60)
    reply("count")
    spent = h.settled("count", lambda found: bool(by_kind(found, "wakes-spent")) and all_ended(found), 30)
    again = h.call("team", "start", "count", *h.harnessed)
    done_c = h.settled("count", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    found = h.events("count")
    starts = by_kind(found, "team-started")
    after = [one for one in by_kind(found, "wake-intent", agent="k") if len(starts) > 1 and one["id"] > starts[-1]["id"]]
    if spent and again.returncode == 0 and done_c and len(after) == 1:
        held("(c) a task's wakes: counted afresh", "wakes 1 spent at the reply; a season, then k woken once more, T1 "
             "done -- I10")
    else:
        failures.append(f"  ✗ (c) wakes afresh           spent={spent} rc={again.returncode} done={done_c} "
                        f"after={len(after)} {again.stderr.strip()[-200:]!r}")
    return 0
