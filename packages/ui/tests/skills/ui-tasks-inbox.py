"""Scenario `ui-tasks-inbox` -- the owner's inbox opened from the Tasks tab (batch l-inbox-et-les-taches), on the bench's
`pp-team` witness:
- `b` on the Tasks tab reads `team inbox <team> --json` of the team of the task under the cursor and shows it in an
  overlay titled by the team; `enter` on its question opens the overlay that writes on the question's task, the reply
  chosen -- `enter` there plays a post naming `--task` and `--reply`, as the witness's journal says it; `b` alone
  plays nothing, no command shown
- `x` there plays `team inbox <team> --seen`
- on the Dialogue tab `b` reads nothing of team
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")

QUESTION = {"id": 45, "verb": "ask", "from": "reviewer", "task": "T3", "text": "tests green?"}
INBOX = {"core-review": {"team": "core-review", "questions": [QUESTION], "done": [{"task": "T2", "id": 40}], "returned": []}}
REPLY = f"team post core-review --task {QUESTION['task']} --reply {QUESTION['id']} --message ok"
SEEN = "team inbox core-review --seen"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-inbox", T.script(inbox=INBOX))

    # --- b: the inbox of the task's team; enter replies on the question's task ---------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "150x40", "--press", "b")
    rows = [one for one in P.overlay_rows(done.stdout) if one]
    read, unplayed = "inbox core-review" in house.journal_lines(), house.gestures()
    house.clear_journal()
    replied = house.render("--render", "tasks", "--size", "150x40", "--press", "b,enter,o,k,enter")
    if (done.returncode == 0 and rows and "core-review" in rows[0] and any(f"#{QUESTION['id']}" in row for row in rows[1:])
            and "./pp" not in done.stdout and read and unplayed == []
            and replied.returncode == 0 and house.gestures() == [REPLY]):
        held("b opens the inbox of the task's team", f"{rows[0]!r}, #{QUESTION['id']} in it, no command, nothing played; "
             f"enter, ok, enter: {REPLY!r}")
    else:
        failures.append(f"  ✗ b on tasks                  rc={done.returncode}/{replied.returncode} "
                        f"{rows!r} {unplayed} {house.gestures()} {done.stdout[-1200:]!r} {done.stderr[-300:]!r}")

    # --- x marks it seen; b elsewhere reads nothing ------------------------------------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "150x40", "--press", "b,x")
    played = house.gestures()
    house.clear_journal()
    other = house.render("--render", "dialogue", "--size", "150x40", "--press", "b")
    if done.returncode == 0 and played == [SEEN] and other.returncode == 0 and house.journal_lines() == []:
        held("x marks the inbox seen; b elsewhere reads nothing", f"{played[0]}; no call of team from the dialogue")
    else:
        failures.append(f"  ✗ seen                        rc={done.returncode}/{other.returncode} {played} "
                        f"{house.journal_lines()} {done.stdout[-600:]!r}")
    return 0
