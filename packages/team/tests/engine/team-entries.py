"""Scenario `team-entries` -- 1 case(s) (batch le-rythme-et-les-entrees, rework, team 0.13.3; split
out of `team-review` by les-scenarios-par-maison, 2026-10-07): an entry is a successor of the
agent's DAG -- `procs/TEAM-<team>.md` at the kit's `turn.begin`, its `next:` the entries then
`TEAM-IDLE.md`, decided by the instance's skill `team-entry`, which asks `team entry` -- at every
exchange of a member's run.
- (t) the entry of a member already opened (I22): pb opened on T1, resumed on T2, resumed again when the
  daily rings at a frozen 09:31 -- one run; its trace elects `TEAM-IDLE.md`, `TEAM-IDLE.md`, then
  `DAILY.md`; fb concludes the daily on `DAILY.md`; no `door` line anywhere
"""
from __future__ import annotations

import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "fb": {"T1": [{"sleep": 0.1, "body": {"do": ["pb"]}},
                      {"sleep": 0.1, "body": {"done": "first"}}],
               "T2": [{"sleep": 0.1, "body": {"do": ["pb"]}},
                      {"sleep": 0.1, "body": {"done": "second"}}],
               "T3": [{"sleep": 0.1, "body": {"done": "standup"}}]}})
    by_kind, all_ended, intents_on, result_of, runs_launched = (
        T.by_kind, T.all_ended, T.intents_on, T.result_of, T.runs_launched)

    # --- (t) the entry of a member already opened [55] -- I22 --------------------------------------------
    for one in ("agents/fb", "agents/pb"):
        h.entry_laid(one, "DAILY.md", T.DAILY_DOC)
    h.declare("beat", "---\nagents: |\n  fb agents/fb\n  pb agents/pb\nreports: |\n  pb -> fb\nroot: fb\n"
                      "ceremonies: |\n  daily every weekday 09:30 with pb -> fb\n"
                      "entries: |\n  daily -> DAILY.md\nschedule: off\n---\nKeep the beat, member by member.\n")
    beat = h.call("team", "start", "beat", "--message", "first task", *h.harnessed, now="09:10")
    first_t = h.settled("beat", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=60)
    time.sleep(0.5)
    beat2 = h.call("team", "post", "beat", "--message", "second task", now="09:20")
    second_t = h.settled("beat", lambda found: bool(by_kind(found, "done", task="T2")) and all_ended(found), timeout=60)
    time.sleep(0.5)
    rung_t = h.call("team", "tick", "beat", now="09:31")
    daily_t = h.settled("beat", lambda found: bool(by_kind(found, "done", task="T3")) and all_ended(found), timeout=60)
    time.sleep(0.5)
    found_t = h.events("beat")
    key_pb = next((one.get("run") for one in by_kind(found_t, "wake-ended", agent="pb")), "")
    key_fb = next((one.get("run") for one in by_kind(found_t, "wake-ended", agent="fb")), "")
    pb_on_daily = intents_on(found_t, "pb", "T3")
    pb_elected, fb_elected = h.elected("agents/pb", key_pb), h.elected("agents/fb", key_fb)
    if (beat.returncode == 0 and first_t and beat2.returncode == 0 and second_t and rung_t.returncode == 0
            and daily_t and key_pb and runs_launched(found_t, "pb") == {key_pb}
            and len(pb_on_daily) == 1 and pb_on_daily[0].get("run") == key_pb
            and pb_elected == ["TEAM-IDLE.md", "TEAM-IDLE.md", "DAILY.md"]
            and fb_elected[-1:] == ["DAILY.md"] and fb_elected.count("DAILY.md") == 1
            and set(fb_elected[:-1]) == {"TEAM-IDLE.md"}
            and h.doors_in("agents/pb", key_pb) == [] and h.doors_in("agents/fb", key_fb) == []
            and result_of(found_t, "T3") == "standup"):
        held("(t) the entry of a member already opened", f"pb opened on T1 and resumed on T2 then on the daily, "
             f"one run {key_pb}: its team document elects {pb_elected}; fb concludes the daily on DAILY.md "
             f"({fb_elected}); no door -- I22")
    else:
        failures.append(f"  ✗ (t) entry on a resume       {beat.returncode}/{beat2.returncode}/{rung_t.returncode} "
                        f"first={first_t} second={second_t} daily={daily_t} key={key_pb} "
                        f"runs={runs_launched(found_t, 'pb')} on_daily={[(one['id'], one.get('run')) for one in pb_on_daily]} "
                        f"elected={pb_elected}/{fb_elected} doors={h.doors_in('agents/pb', key_pb)} "
                        f"{beat.stderr[-200:]!r} {rung_t.stderr[-200:]!r}")
    return 0
