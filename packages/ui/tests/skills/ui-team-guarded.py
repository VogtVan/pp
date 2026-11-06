"""Scenario `ui-team-guarded` -- the gestures of a team and of a task asked in an overlay then played, and what
destroys played only on the name typed, on the bench's `pp-team` witness -- what plays read from its journal, no
command on screen:
- `s` on the Tasks tab (stop the task): `enter` plays `team stop core-review --task T3`, `escape` plays nothing
- `k` kills the wake-ups of the task under the cursor: a wrong name and `enter` play nothing, `escape` nothing, `T3`
  typed plays `stop core-review --task T3 --kill`
- `T` (tick) on the Teams tab: `enter` plays `team tick core-review`, `escape` plays nothing
- `X` stops every task of the team on `core-review` typed, a wrong name plays nothing; its overlay, titled by the team,
  counts the open tasks and the wake-ups under way on them as the face holds them
- `R` forgets the run of the member under the Members cursor on its name typed; the verb's refusal, `member-running`,
  goes to the remedy line
- `D` deletes the team chosen: what the dry run of `team delete ops --json` would remove shown, the agents it lists as
  checks; `enter` plays nothing until `ops` is typed -- `tab` goes from the checks to the name --; typed,
  `team delete ops --yes` plays once and the team leaves the menu; `team-busy`
  goes to the remedy line, nothing played
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
DELETE = "team delete ops --yes"
# core-review with two open tasks and three wake-ups under way on them: T3 woke `reviewer`, T4 `lead` and `scribe`
STOPPING = {**T.LIVE_CORE, "tasks": T.LIVE_CORE["tasks"] + [
    T.running(T.T4, ("lead", "a77f10", "09:12:30"), ("scribe", "c33333", "09:12:40"))]}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-guarded")

    # --- the Tasks tab: s shown then played, k on the task's name alone, escape nothing -----------------------
    wrong = house.render("--render", "tasks", *SIZE, "--press", "s,escape,k,T,4,enter")
    after_wrong = house.gestures()
    house.clear_journal()
    shown = house.render("--render", "tasks", *SIZE, "--press", "k,escape,s")
    after_escape = house.gestures()
    house.clear_journal()
    killed = house.render("--render", "tasks", *SIZE, "--press", "k,T,3,enter")
    after_kill = house.gestures()
    house.clear_journal()
    stopped = house.render("--render", "tasks", *SIZE, "--press", "s,enter")
    if (shown.returncode == 0 and stopped.returncode == 0 and "./pp" not in shown.stdout and after_wrong == []
            and after_escape == [] and house.gestures() == [STOP]):
        held("s asks, then plays", f"{STOP!r}, no command on screen; escape plays nothing")
    else:
        failures.append(f"  ✗ s                           rc={shown.returncode},{stopped.returncode} "
                        f"{after_wrong} {after_escape} {house.gestures()} {shown.stdout[-900:]!r}")
    if (wrong.returncode == 0 and killed.returncode == 0 and after_wrong == [] and after_escape == []
            and "./pp" not in wrong.stdout and after_kill == [KILL]):
        held("k plays on the task's name alone", f"T4 and enter: nothing; escape: nothing; T3: {KILL}")
    else:
        failures.append(f"  ✗ kill                        {after_wrong} {after_escape} {after_kill} "
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
    house.clear_journal()
    ticked = house.render("--render", "teams", *SIZE, "--press", "T,enter")
    if (ticking.returncode == 0 and ticked.returncode == 0 and "./pp" not in ticking.stdout and after_refused == []
            and house.gestures() == [TICK]):
        held("T asks, then plays", f"{TICK!r}, no command on screen; escape plays nothing")
    else:
        failures.append(f"  ✗ T                           rc={ticking.returncode},{ticked.returncode} "
                        f"{after_refused} {house.gestures()} {ticking.stdout[-900:]!r}")
    if refused.returncode == 0 and "core-review" in title.split() and figures == counted:
        held("X counts what it stops on the face", f"titled by core-review; {counted[0]} open task(s), {counted[1]} "
             "wake-up(s) under way, as the face holds them")
    else:
        failures.append(f"  ✗ stop all counted            {title!r} {figures} {counted} {rows!r}")
    if (refused.returncode == 0 and ticking.returncode == 0 and after_refused == [] and "./pp" not in refused.stdout
            and after_stop == [STOP_ALL]):
        held("X plays on the team's name alone", f"veille: nothing; core-review: {STOP_ALL}")
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
    dry = house.gestures()
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "160x40", "--press", "down,D,tab,o,p,s,enter")
    menu = [one.split()[0] for one in T.sides_of(done.stdout)[0] if one.split()]
    if (shown.returncode == 0 and done.returncode == 0 and "./pp" not in shown.stdout and dry == [DRY]
            and "teams/ops" in shown.stdout and "b11111" in shown.stdout
            and house.gestures() == [DRY, DELETE] and "ops" not in menu and "core-review" in menu):
        held("D deletes a team on its name typed", f"the dry run shown, no command; enter alone played {dry}; typed: "
             f"{house.gestures()}, the menu {menu}")
    else:
        failures.append(f"  ✗ delete                      rc={shown.returncode},{done.returncode} {dry} "
                        f"{house.gestures()} {menu} {shown.stdout[-1600:]!r} {done.stderr[-400:]!r}")
    house.use(T.script(answers={"delete": {"rc": 2, "err": "pp-team: team-busy -- ops is at work (T1): stop it "
                                                           "first (`team stop ops --kill`), then delete it.\n"}}))
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "160x40", "--press", "down,D,o,p,s,enter")
    remedy = T.remedy_of(done)
    if done.returncode == 0 and house.gestures() == [DRY] and "team-busy" in remedy and "./pp" not in done.stdout:
        held("D on a team at work: team-busy on the remedy line", f"{remedy[:60]!r}; nothing played")
    else:
        failures.append(f"  ✗ delete busy                 rc={done.returncode} {house.gestures()} {remedy!r} "
                        f"{done.stdout[-1200:]!r}")
    return 0
