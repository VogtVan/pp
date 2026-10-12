"""Scenario `ui-team-guarded` -- what destroys plays only on the name typed (plan ui, batch
les-gestes-du-pilote), on the bench's `pp-team` witness:
- `k` kills the wake-ups of the task under the cursor: a wrong name and `enter` play nothing, `escape`
  nothing, `T3` typed plays `stop core-review --task T3 --kill`
- `X` stops every task of the team on `core-review` typed, its overlay titled `stop all tasks of core-review` and
  saying what it stops as the face counts it (plan ui, batch l-etat-et-les-gestes); `R` forgets the run of the member under the
  Members cursor on its name typed; `member-running` goes to the remedy line as the verb said it
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-guarded")

    wrong = house.render("--render", "tasks", "--size", "130x40", "--press", "k,T,4,enter")
    after_wrong = house.gestures()
    house.clear_journal()
    house.render("--render", "tasks", "--size", "130x40", "--press", "k,escape")
    after_escape = house.gestures()
    shown = house.render("--render", "tasks", "--size", "130x40", "--press", "k")
    preview = T.preview_in(shown, "./pp team stop")
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "130x40", "--press", "k,T,3,enter")
    if (wrong.returncode == 0 and after_wrong == [] and after_escape == [] and "T3" in wrong.stdout
            and preview == "./pp team stop core-review --task T3 --kill"
            and house.gestures() == ["team stop core-review --task T3 --kill"]):
        held("k plays on the task's name alone", "T4 and enter: nothing; escape: nothing; T3: the kill as shown")
    else:
        failures.append(f"  ✗ kill                        {after_wrong} {after_escape} {preview!r} {house.gestures()} "
                        f"{wrong.stdout[-900:]!r}")

    house.use(T.script(states={"core-review": [T.LIVE_CORE], "ops": [T.OPS]}))
    shown = house.render("--render", "teams", "--size", "130x40", "--press", "X")
    flat = " ".join(shown.stdout.replace("┃", " ").replace("│", " ").split())
    said = "stops 1 open task; 1 wake-up under way ends on its own, its answer routed nowhere"
    if shown.returncode == 0 and "stop all tasks of core-review" in flat and said in flat:
        held("X says what it stops", f"stop all tasks of core-review: {said!r}, counted on the face")
    else:
        failures.append(f"  ✗ stop all said               {flat[-900:]!r}")
    house.use(T.script())
    house.clear_journal()
    house.render("--render", "teams", "--size", "130x40", "--press", "X,v,e,i,l,l,e,enter")
    wrong_team = house.gestures()
    done = house.render("--render", "teams", "--size", "130x40", "--press",
                        "X,c,o,r,e,minus,r,e,v,i,e,w,enter")
    if done.returncode == 0 and wrong_team == [] and house.gestures() == ["team stop core-review"]:
        held("X plays on the team's name alone", "veille: nothing; core-review: stop core-review")
    else:
        failures.append(f"  ✗ stop all                    {wrong_team} {house.gestures()} {done.stdout[-900:]!r}")

    house.clear_journal()
    house.use(T.script(answers={"reset": {"rc": 2, "err": "pp-team: member-running -- reviewer plays a wake-up: "
                                                        "its run cannot be forgotten now.\n"}}))
    done = house.render("--render", "teams", "--size", "130x40", "--press", "tab,down,R,r,e,v,i,e,w,e,r,enter")
    remedy = T.remedy_of(done)
    if (done.returncode == 0 and house.gestures() == ["team reset core-review --member reviewer"]
            and "member-running -- reviewer plays a wake-up" in remedy):
        held("R plays on the member's name, its refusal said", f"reset core-review --member reviewer; {remedy[:70]!r}")
    else:
        failures.append(f"  ✗ reset                       {house.gestures()} {remedy!r} {done.stdout[-900:]!r}")
    return 0
