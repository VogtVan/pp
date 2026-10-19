"""Scenario `team-rhythm` -- 3 case(s) (batch le-rythme-et-les-entrees, 2026-10-01; split out of
`team-review` by les-scenarios-par-maison, 2026-10-07): a team `rhythm` (f manager, p1 p2
reviewers; `daily every weekday 09:30 with p1 p2 -> f`, `retro after daily with p1 -> f`,
`entries: | daily -> DAILY.md`), the clock frozen by `PP_NOW`.
- a tick before the hour rings nothing; at 09:31 it writes `ceremony-due {daily, period}` once,
  ONE ceremony task from the team to f, a `do` and a `delegation` f -> p1 and p2; a second tick
  at the same hour rings nothing more
- the participants answer, the facilitator concludes: their `done` rise to f, woken at
  completeness, and f's `done` resolves the ceremony task (`result` says it)
- `after` follows the resolution: the retro rings at the tick after the daily resolves, same
  period, once; p2 (not a retro participant) is never woken for it
- the ceremony wake-up plays its entry (reworked team 0.13.3): DAILY.md laid in the agents'
  instances before the start; p1's run elects `DAILY.md` at its daily exchange, then the neutral
  `TEAM-IDLE.md` at the retro's (`next` lines of its trace, `by: skill`); f's run elects the neutral
  on the root task, `DAILY.md` when it concludes the daily; no `door` line in any trace
- the when is judged at the declaration: `every 2 weeks`, a `with` without `->`, a missing
  hour, an entry naming no ceremony refuse `team-invalid`
"""
from __future__ import annotations

import re
import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "f": [{"sleep": 0.1, "body": {"done": "root done"}},
              {"sleep": 0.1, "body": {"done": "standup summary"}},
              {"sleep": 0.1, "body": {"done": "retro summary"}}],
        "p1": [{"sleep": 0.1, "body": {"done": True}},
               {"sleep": 0.1, "body": {"done": True}}],
        "p2": [{"sleep": 0.1, "body": {"done": True}}]})
    by_kind, all_ended = T.by_kind, T.all_ended
    h.declare("rhythm", "---\nagents: |\n  f f\n  p1 p1\n  p2 p2\n"
                        "reports: |\n  p1 p2 -> f\nroot: f\n"
                        "ceremonies: |\n  daily every weekday 09:30 with p1 p2 -> f\n"
                        "  retro after daily with p1 -> f\n"
                        "entries: |\n  daily -> DAILY.md\n---\nKeep the beat.\n")

    # --- a tick at the daily's hour rings once -------------------------------------------------
    for one in ("f", "p1", "p2"):                  # f's daily wake-up plays the same entry
        h.entry_laid(one, "DAILY.md", T.DAILY_DOC)
    rhythm = h.call("team", "start", "rhythm", "--message", "open the day", *h.harnessed, "--no-tick", now="09:10")
    early = h.call("team", "tick", "rhythm", now="09:15")
    root_done = h.settled("rhythm", lambda found: bool(by_kind(found, "done", task="T1")), timeout=60)
    none_yet = by_kind(h.events("rhythm"), "ceremony-due")
    rung = h.call("team", "tick", "rhythm", now="09:31")
    found = h.events("rhythm")
    due_daily = by_kind(found, "ceremony-due", ceremony="daily")
    ceremony_task = next((one for one in found if one.get("kind") == "task" and one.get("ceremony") == "daily"), {})
    dos = [one for one in by_kind(found, "post", verb="do") if one.get("task") == ceremony_task.get("task")
           and one.get("from") == "f"]
    opening = [one for one in by_kind(found, "post", verb="do") if one.get("task") == ceremony_task.get("task")
               and one.get("from") == "rhythm"]
    delegs = T.delegated(found, task=ceremony_task.get("task"))
    again_rung = h.call("team", "tick", "rhythm", now="09:31")
    once = len(by_kind(h.events("rhythm"), "ceremony-due", ceremony="daily"))
    if (rhythm.returncode == 0 and early.returncode == 0 and root_done and none_yet == []
            and rung.returncode == 0 and len(due_daily) == 1 and due_daily[0].get("period") == "2026-10-01"
            and ceremony_task.get("to") == "f" and ceremony_task.get("from") == "rhythm"
            and ceremony_task.get("period") == "2026-10-01"
            and sorted(one.get("to") for one in dos) == ["p1", "p2"]
            and sorted(one.get("to") for one in delegs) == ["p1", "p2"]
            and [one.get("to") for one in opening] == ["f"]
            and all(one.get("from") == "f" for one in dos + delegs)
            and again_rung.returncode == 0 and once == 1):
        held("a tick at the daily's hour rings once", f"09:15 rings nothing; 09:31 writes ceremony-due "
             f"(period 2026-10-01), the task {ceremony_task.get('task')} from the team to f, its opening to f, a "
             "do to p1 and p2; a second tick at 09:31 rings nothing more")
    else:
        failures.append(f"  ✗ ring once                   {rhythm.returncode}/{early.returncode}/{rung.returncode} "
                        f"root={root_done} none={none_yet} due={due_daily} task={ceremony_task} dos={len(dos)} "
                        f"delegs={len(delegs)} once={once} {rung.stderr[-200:]!r}")

    # --- the participants answer, the facilitator concludes; after follows; the entry opens -----
    settled_r = h.settled("rhythm", lambda found: len(by_kind(found, "done")) >= 3 and all_ended(found), timeout=90)
    time.sleep(1.0)
    found = h.events("rhythm")
    due_retro = by_kind(found, "ceremony-due", ceremony="retro")
    retro_task = next((one for one in found if one.get("kind") == "task" and one.get("ceremony") == "retro"), {})
    retro_delegs = T.delegated(found, task=retro_task.get("task"))
    daily_result = h.call("team", "result", "rhythm", str(ceremony_task.get("task")))
    retro_result = h.call("team", "result", "rhythm", str(retro_task.get("task")))
    p2_intents = by_kind(found, "wake-intent", agent="p2")
    f2_prompt = h.prompt_of("f-2")
    p1_run = next((one.get("run") for one in by_kind(found, "wake-launched", agent="p1")), None)
    f_run = next((one.get("run") for one in by_kind(found, "wake-launched", agent="f")), None)
    p1_elected, f_elected = h.elected("p1", p1_run), h.elected("f", f_run)
    if (settled_r and len(due_retro) == 1 and due_retro[0].get("period") == "2026-10-01"
            and retro_task.get("to") == "f" and [one.get("to") for one in retro_delegs] == ["p1"]
            and daily_result.returncode == 0 and daily_result.stdout == '"standup summary"\n'
            and retro_result.returncode == 0 and retro_result.stdout == '"retro summary"\n'
            and len(p2_intents) == 1
            and re.search(r"^#\d+ RE #\d+ from p1 on ", f2_prompt, re.M)
            and re.search(r"^#\d+ RE #\d+ from p2 on ", f2_prompt, re.M)
            and p1_elected == ["DAILY.md", "TEAM-IDLE.md"]
            and f_elected == ["TEAM-IDLE.md", "DAILY.md", "TEAM-IDLE.md"]
            and h.doors_in("p1", p1_run) == [] and h.doors_in("f", f_run) == []):
        held("the ceremony runs and plays its entry", "p1 and p2 answer, f concludes (standup summary); "
             "the retro rings after the resolution, p1 alone, f concludes (retro summary); p2 woken once; "
             f"p1's run elects {p1_elected}, f's {f_elected} -- no door")
    else:
        failures.append(f"  ✗ ceremony flow               settled={settled_r} retro={due_retro} rt={retro_task} "
                        f"rdelegs={[one.get('to') for one in retro_delegs]} results={daily_result.stdout!r}/"
                        f"{retro_result.stdout!r} p2={len(p2_intents)} elected={p1_elected}/{f_elected} "
                        f"doors={h.doors_in('p1', p1_run)}/{h.doors_in('f', f_run)} f2={f2_prompt[-200:]!r}")

    # --- the when and the entries are judged at the declaration ---------------------------------
    h.declare("badw1", "---\nagents: |\n  s s\nroot: s\nceremonies: |\n  biweekly every 2 weeks fri 15:00 with s -> s\n---\n")
    h.declare("badw2", "---\nagents: |\n  s s\nroot: s\nceremonies: |\n  daily every weekday 09:30 with s\n---\n")
    h.declare("badw3", "---\nagents: |\n  s s\nroot: s\nceremonies: |\n  daily every weekday with s -> s\n---\n")
    h.declare("bade", "---\nagents: |\n  s s\nroot: s\nentries: |\n  sprint -> SPRINT.md\n---\n")
    bad_when = {name: h.call("team", "start", name, "--message", "x", "--no-tick")
                for name in ("badw1", "badw2", "badw3", "bade")}
    if (all(one.returncode == 2 and "team-invalid" in one.stderr and one.stdout == ""
            for one in bad_when.values())
            and not any(h.journal_of(name).exists() for name in bad_when)):
        held("the when and the entries are judged", "every 2 weeks, a with without ->, a missing hour, "
             "an entry naming no ceremony: team-invalid, nothing written")
    else:
        failures.append("  ✗ when judged                 "
                        + " ".join(f"{name}={one.returncode}:{one.stderr[-90:]!r}" for name, one in bad_when.items()))
    return 0
