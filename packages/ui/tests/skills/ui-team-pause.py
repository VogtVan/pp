"""Scenario `ui-team-pause` -- `P` pauses the team chosen, or resumes it when the face says it paused, and `r` resumes
the task under the cursor, on the bench's `pp-team` witness:
- `P` on `core-review` (working): its overlay, titled by the team, shows `./pp team pause core-review` under its field
  `as`; `enter` plays it as shown, `escape` plays nothing; `as` on `pm` plays `--as pm`
- `P` on a team the face says paused: `./pp team resume core-review`, never a `--task`
- `r` on the Tasks tab resumes the task under the cursor, the command under its message: a message empty, none; typed,
  `--message`
- a refusal of either verb (`team-paused`, `task-not-blocked`) goes to the remedy line
- the footer of the Teams tab offers `P` and `X`
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the readers of the footer and of an overlay

SIZE = ("--size", "130x40")
PAUSED = {**T.CORE, "state": "paused", "paused": T.PAUSED_AT}
PAUSE = "team pause core-review"
RESUME = "team resume core-review"
TAKEN = f"{RESUME} --task T3"
SAID = f"{TAKEN} --message again"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-pause")

    # --- P: the pause shown, played, escaped; as a principal; the footer ---------------------------------------
    shown = house.render("--render", "teams", *SIZE, "--press", "P,enter,P,escape,P")
    paused = house.gestures()
    preview = T.preview_in(shown, "./pp team pause")
    rows = [one for one in P.overlay_rows(shown.stdout) if one]
    house.clear_journal()
    principal = house.render("--render", "teams", *SIZE, "--press", "P,space,down,enter,enter")
    if (shown.returncode == 0 and preview == f"./pp {PAUSE}" and rows and "core-review" in rows[0].split()
            and paused == [PAUSE]):
        held("P pauses the team as shown", f"{preview!r} under its field; enter: the pause; escape: nothing")
    else:
        failures.append(f"  ✗ pause                       {preview!r} {paused} {rows[:3]!r} {shown.stdout[-1500:]!r} "
                        f"{shown.stderr[-300:]!r}")
    if principal.returncode == 0 and house.gestures() == [f"{PAUSE} --as pm"]:
        held("P as a principal", f"as pm: {PAUSE} --as pm")
    else:
        failures.append(f"  ✗ as                          {house.gestures()} {principal.stdout[-1500:]!r}")
    keys = {key: P.entry_of(shown.stdout, key) for key in ("P", "X")}
    if all(keys.values()):
        held("the footer says P and X", " · ".join(keys.values()))
    else:
        failures.append(f"  ✗ footer                      {keys} {P.keys_of(shown.stdout)!r}")

    # --- r: the task taken back, without a message, then with one ----------------------------------------------
    house.clear_journal()
    written = house.render("--render", "tasks", *SIZE, "--press", "r,enter,r,a,g,a,i,n")
    bare = house.gestures()
    preview = T.preview_in(written, "./pp team resume")
    house.clear_journal()
    said = house.render("--render", "tasks", *SIZE, "--press", "r,a,g,a,i,n,enter")
    if (written.returncode == 0 and said.returncode == 0 and bare == [TAKEN] and preview == f"./pp {SAID}"
            and house.gestures() == [SAID]):
        held("r resumes the task", f"without a message, then with one -- {preview!r} shown")
    else:
        failures.append(f"  ✗ resume task                 {bare} {preview!r} {house.gestures()} {written.stdout[-900:]!r}")

    # --- a team the face says paused: resume -------------------------------------------------------------------
    house.use(T.script(states={"core-review": [PAUSED], "ops": [T.OPS]}))
    house.clear_journal()
    shown = house.render("--render", "teams", *SIZE, "--press", "P,enter,P")
    preview = T.preview_in(shown, "./pp team resume")
    if shown.returncode == 0 and preview == f"./pp {RESUME}" and house.gestures() == [RESUME]:
        held("P resumes a team paused", f"{preview!r}, no --task")
    else:
        failures.append(f"  ✗ resume                      {preview!r} {house.gestures()} {shown.stdout[-1500:]!r}")

    # --- the refusals on the remedy line -----------------------------------------------------------------------
    house.use(T.script(answers={
        "pause": {"rc": 2, "err": "pp-team: team-paused -- core-review is paused since 09:20 by house: "
                                  "team resume core-review takes it back.\n"},
        "resume": {"rc": 2, "err": "pp-team: task-not-blocked -- T3 has a member due: nothing to take back.\n"}}))
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", "P,enter")
    remedy = T.remedy_of(done)
    if done.returncode == 0 and house.gestures() == [PAUSE] and "team-paused" in remedy.split():
        held("a refusal said as the verb said it", f"{remedy[:70]!r}")
    else:
        failures.append(f"  ✗ pause refused               {house.gestures()} {remedy!r} {done.stdout[-900:]!r}")
    house.clear_journal()
    done = house.render("--render", "tasks", *SIZE, "--press", "r,enter")
    remedy = T.remedy_of(done)
    if done.returncode == 0 and house.gestures() == [TAKEN] and "task-not-blocked" in remedy.split():
        held("a refusal goes to the remedy line as said", f"{remedy[:70]!r}")
    else:
        failures.append(f"  ✗ resume refused              {house.gestures()} {remedy!r} {done.stdout[-700:]!r}")
    return 0
