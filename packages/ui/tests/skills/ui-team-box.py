"""Scenario `ui-team-box` -- `b`, the owner's inbox of the team chosen (plan ui, batch les-overlays-des-gestes), on
the bench's `pp-team` witness:
- `b` reads `team inbox <team> --json` and shows, in an overlay, the questions waiting for the owner, the tasks
  done and the posts returned, with the command of `x` under them
- `enter` on a question opens the overlay that writes on its task, `reply to` on the question: `enter` there plays
  `team post <team> --task <task> --reply <id> --message <text>`
- `x` in the overlay plays `team inbox <team> --seen`, as shown; `escape` plays nothing
- a team where nothing waits says so
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

INBOX = {"core-review": {"team": "core-review",
                         "questions": [{"id": 45, "verb": "ask", "from": "reviewer", "task": "T3", "text": "tests green?"}],
                         "done": [{"task": "T2", "id": 40}],
                         "returned": [{"id": 33, "verb": "note", "from": "house", "task": "T1",
                                       "text": "the deadline moved"}]}}
SEEN = "./pp team inbox core-review --seen"
REPLY = "./pp team post core-review --task T3 --reply 45 --message ok"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-box", T.script(inbox=INBOX))

    # --- b: the three lists, the command of x ---------------------------------------------------------
    shown = house.render("--render", "teams", "--size", "130x40", "--press", "b")
    flat = " ".join(shown.stdout.split())
    lines = ("#45 ask from reviewer on T3", "tests green?", "T2 done", "#33 note from house on T1 returned")
    if (shown.returncode == 0 and all(one in flat for one in lines) and T.preview_in(shown, "./pp team inbox") == SEEN
            and "inbox core-review" in house.journal_lines() and house.gestures() == []):
        held("b shows the owner's inbox", f"{', '.join(lines)}; {SEEN!r} under them; nothing played")
    else:
        failures.append(f"  ✗ the box                     rc={shown.returncode} {house.journal_lines()} "
                        f"{shown.stdout[-1500:]!r} {shown.stderr[-400:]!r}")

    # --- x: the inbox seen, as shown; escape nothing --------------------------------------------------
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "130x40", "--press", "b,x")
    played = house.gestures()
    house.clear_journal()
    none = house.render("--render", "teams", "--size", "130x40", "--press", "b,escape")
    if done.returncode == 0 and played == [SEEN[len("./pp "):]] and none.returncode == 0 and house.gestures() == []:
        held("x marks the inbox seen", f"{played[0]}; escape plays nothing")
    else:
        failures.append(f"  ✗ seen                        rc={done.returncode} {played} {house.gestures()} "
                        f"{done.stdout[-900:]!r}")

    # --- enter on a question: the reply written on its task -------------------------------------------
    shown = house.render("--render", "teams", "--size", "130x40", "--press", "b,enter,o,k")
    preview = T.preview_in(shown, "./pp team post")
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "130x40", "--press", "b,enter,o,k,enter")
    played = house.gestures()
    if shown.returncode == 0 and done.returncode == 0 and preview == REPLY and played == [REPLY[len("./pp "):]]:
        held("enter on a question replies to it", f"{preview!r} shown, then played")
    else:
        failures.append(f"  ✗ reply                       rc={shown.returncode},{done.returncode} {preview!r} {played} "
                        f"{shown.stdout[-1500:]!r} {shown.stderr[-400:]!r}")

    # --- nothing waits ---------------------------------------------------------------------------------
    house.use(T.script())
    empty = house.render("--render", "teams", "--size", "130x40", "--press", "b")
    if empty.returncode == 0 and "nothing waits for you" in " ".join(empty.stdout.split()):
        held("an empty inbox says so", "nothing waits for you")
    else:
        failures.append(f"  ✗ empty                       rc={empty.returncode} {empty.stdout[-900:]!r}")
    return 0
