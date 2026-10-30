"""Scenario `ui-team-guarded` -- the gestures of a team and of a task shown then played, and what destroys played
only on the name typed, on the bench's `pp-team` witness:
- `s` on the Tasks tab (stop the task) shows `./pp team stop core-review --task T3`, `enter` plays it as shown,
  `escape` plays nothing
- `k` kills the wake-ups of the task under the cursor: a wrong name and `enter` play nothing, `escape` nothing, `T3`
  typed plays `stop core-review --task T3 --kill`, the command it showed
- `T` (tick) on the Teams tab shows `./pp team tick core-review`, `enter` plays it as shown, `escape` plays nothing
- `X` stops every task of the team on `core-review` typed, a wrong name plays nothing; its overlay, titled by the team,
  counts the open tasks and the wake-ups under way on them as the face holds them
- `R` forgets the run of the member under the Members cursor on its name typed; the verb's refusal, `member-running`,
  goes to the remedy line
- `D` deletes the team chosen: the dry run of `team delete ops --json` shown, the command under it; `enter` plays
  nothing until `ops` is typed; typed, `team delete ops --yes` plays once and the team leaves the menu; `team-busy`
  goes to the remedy line, nothing shown, nothing played
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the readers of an overlay

SIZE = ("--size", "130x40")
STOP = "team stop core-review --task T3"
KILL = f"{STOP} --kill"
TICK = "team tick core-review"
STOP_ALL = "team stop core-review"
RESET = "team reset core-review --member reviewer"
DRY = "team delete ops --json"
DELETE = "./pp team delete ops --yes"
# core-review with two open tasks and three wake-ups under way on them: T3 woke `reviewer`, T4 `lead` and `scribe`
STOPPING = {**T.LIVE_CORE, "tasks": T.LIVE_CORE["tasks"] + [
    T.running(T.T4, ("lead", "a77f10", "09:12:30"), ("scribe", "c33333", "09:12:40"))]}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-guarded")

    # --- the Tasks tab: s shown then played, k on the task's name alone, escape nothing -----------------------
    wrong = house.render("--render", "tasks", *SIZE, "--press", "s,escape,k,T,4,enter")
    after_wrong = house.gestures()
    killing = T.preview_in(wrong, "./pp team stop")
    house.clear_journal()
    shown = house.render("--render", "tasks", *SIZE, "--press", "k,escape,s")
    after_escape = house.gestures()
    stopping = T.preview_in(shown, "./pp team stop")
    house.clear_journal()
    killed = house.render("--render", "tasks", *SIZE, "--press", "k,T,3,enter")
    after_kill = house.gestures()
    house.clear_journal()
    stopped = house.render("--render", "tasks", *SIZE, "--press", "s,enter")
    if (shown.returncode == 0 and stopped.returncode == 0 and stopping == f"./pp {STOP}" and after_wrong == []
            and after_escape == [] and house.gestures() == [STOP]):
        held("s shows, then plays", f"{stopping!r}; escape plays nothing")
    else:
        failures.append(f"  ✗ s                           rc={shown.returncode},{stopped.returncode} {stopping!r} "
                        f"{after_wrong} {after_escape} {house.gestures()} {shown.stdout[-900:]!r}")
    if (wrong.returncode == 0 and killed.returncode == 0 and after_wrong == [] and after_escape == []
            and killing == f"./pp {KILL}" and after_kill == [KILL]):
        held("k plays on the task's name alone", "T4 and enter: nothing; escape: nothing; T3: the kill as shown")
    else:
        failures.append(f"  ✗ kill                        {after_wrong} {after_escape} {killing!r} {after_kill} "
                        f"{wrong.stdout[-900:]!r}")

    # --- the Teams tab: T shown then played, X counted on the face and played on the team's name alone ---------
    house.use(T.script(states={"core-review": [STOPPING], "ops": [T.OPS]}))
    house.clear_journal()
    refused = house.render("--render", "teams", *SIZE, "--press", "T,escape,X,v,e,i,l,l,e,enter")
    after_refused = house.gestures()
    rows = [one for one in P.overlay_rows(refused.stdout) if one]
    title = rows[0] if rows else ""                     # the overlay's first row: its title
    opened = [one for one in STOPPING["tasks"] if one["state"] == "open"]
    counted = [str(len(opened)), str(sum(len(one.get("running") or []) for one in opened))]
    figures = re.findall(r"(?<![\w.:-])\d+(?![\w.:-])", " ".join(rows[1:]))
    house.clear_journal()
    ticking = house.render("--render", "teams", *SIZE, "--press", "X,c,o,r,e,minus,r,e,v,i,e,w,enter,T")
    after_stop = house.gestures()
    tick = T.preview_in(ticking, "./pp team tick")
    house.clear_journal()
    ticked = house.render("--render", "teams", *SIZE, "--press", "T,enter")
    if (ticking.returncode == 0 and ticked.returncode == 0 and tick == f"./pp {TICK}" and after_refused == []
            and house.gestures() == [TICK]):
        held("T shows, then plays", f"{tick!r}; escape plays nothing")
    else:
        failures.append(f"  ✗ T                           rc={ticking.returncode},{ticked.returncode} {tick!r} "
                        f"{after_refused} {house.gestures()} {ticking.stdout[-900:]!r}")
    if refused.returncode == 0 and "core-review" in title.split() and figures == counted:
        held("X counts what it stops on the face", f"titled by core-review; {counted[0]} open task(s), {counted[1]} "
             "wake-up(s) under way, as the face holds them")
    else:
        failures.append(f"  ✗ stop all counted            {title!r} {figures} {counted} {rows!r}")
    if (refused.returncode == 0 and ticking.returncode == 0 and after_refused == []
            and T.preview_in(refused, "./pp team stop") == f"./pp {STOP_ALL}" and after_stop == [STOP_ALL]):
        held("X plays on the team's name alone", f"veille: nothing; core-review: {STOP_ALL}, as shown")
    else:
        failures.append(f"  ✗ stop all                    {after_refused} {after_stop} {refused.stdout[-900:]!r}")

    # --- R on the member's name, its refusal on the remedy line ------------------------------------------------
    house.use(T.script(answers={"reset": {"rc": 2, "err": "pp-team: member-running -- reviewer plays a wake-up: "
                                                        "its run cannot be forgotten now.\n"}}))
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", "tab,down,R,r,e,v,i,e,w,e,r,enter")
    remedy = T.remedy_of(done)
    if done.returncode == 0 and house.gestures() == [RESET] and "member-running" in remedy.split():
        held("R plays on the member's name, its refusal said", f"{RESET}; {remedy[:70]!r}")
    else:
        failures.append(f"  ✗ reset                       {house.gestures()} {remedy!r} {done.stdout[-900:]!r}")
    # --- D: the dry run, the name typed, --yes once; team-busy to the remedy ---------------------------------
    house.clear_journal()
    shown = house.render("--render", "teams", "--size", "160x40", "--press", "down,D,enter")
    preview = T.preview_in(shown, "./pp team delete")
    dry = house.gestures()
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "160x40", "--press", "down,D,o,p,s,enter")
    menu = [one.split()[0] for one in T.sides_of(done.stdout)[0] if one.split()]
    if (shown.returncode == 0 and done.returncode == 0 and preview == DELETE and dry == [DRY]
            and "teams/ops" in shown.stdout and "b11111" in shown.stdout
            and house.gestures() == [DRY, DELETE[len("./pp "):]] and "ops" not in menu and "core-review" in menu):
        held("D deletes a team on its name typed", f"{preview!r} under the dry run; enter alone played {dry}; typed: "
             f"{house.gestures()}, the menu {menu}")
    else:
        failures.append(f"  ✗ delete                      rc={shown.returncode},{done.returncode} {preview!r} {dry} "
                        f"{house.gestures()} {menu} {shown.stdout[-1600:]!r} {done.stderr[-400:]!r}")
    house.use(T.script(answers={"delete": {"rc": 2, "err": "pp-team: team-busy -- ops is at work (T1): stop it "
                                                           "first (`team stop ops --kill`), then delete it.\n"}}))
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "160x40", "--press", "down,D,o,p,s,enter")
    remedy = T.remedy_of(done)
    if done.returncode == 0 and house.gestures() == [DRY] and "team-busy" in remedy and "./pp team delete" not in done.stdout:
        held("D on a team at work: team-busy on the remedy line", f"{remedy[:60]!r}; nothing shown, nothing played")
    else:
        failures.append(f"  ✗ delete busy                 rc={done.returncode} {house.gestures()} {remedy!r} "
                        f"{done.stdout[-1200:]!r}")
    return 0
