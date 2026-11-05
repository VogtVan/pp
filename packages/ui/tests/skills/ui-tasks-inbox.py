"""Scenario `ui-tasks-inbox` -- the owner's inbox opened from the Tasks tab (batch l-inbox-et-les-taches), on the bench's
`pp-team` witness:
- `b` on the Tasks tab reads `team inbox <team> --json` of the team of the task under the cursor and shows it in an
  overlay titled by the team; `enter` on its question opens the overlay that writes on the question's task, the reply
  chosen -- the command shown names `--task` and `--reply`; nothing played
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
    staged = house.render("--render", "tasks", "--size", "150x40", "--press", "b,enter,o,k")
    preview = T.preview_in(staged, "./pp team post")
    if (done.returncode == 0 and rows and "core-review" in rows[0] and any(f"#{QUESTION['id']}" in row for row in rows[1:])
            and T.preview_in(done, "./pp team inbox") == f"./pp {SEEN}" and "inbox core-review" in house.journal_lines()
            and staged.returncode == 0 and preview == f"./pp {REPLY}" and house.gestures() == []):
        held("b opens the inbox of the task's team", f"{rows[0]!r}, #{QUESTION['id']} in it; enter: {preview!r} shown; "
             "nothing played")
    else:
        failures.append(f"  ✗ b on tasks                  rc={done.returncode}/{staged.returncode} {rows!r} {preview!r} "
                        f"{house.journal_lines()} {done.stdout[-1200:]!r} {done.stderr[-300:]!r}")

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
