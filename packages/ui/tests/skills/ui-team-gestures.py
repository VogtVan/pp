"""Scenario `ui-team-gestures` -- writing on a task in its overlay, the command
under the fields what `enter` plays word for word, on the bench's `pp-team` witness:
- `m` on T3 (the first task running): an overlay titled by the task and its team, `to` / `as` / `reply to` read from
  `team status --json` (the members, the owner and the principals, the questions of the task), then the text --
  `post core-review --task T3 --to reviewer --reply 45 --as pm --message ok`; the tasks read again after it
- the owner writes no `--as`; a text on two lines (`ctrl+enter`) leaves whole
(a new task, `n`: `ui-tasks-new-task`)
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the readers of a capture

TYPED = "m,o,k,shift+tab,space,down,enter,shift+tab,space,down,enter,shift+tab,space,down,down,enter"
POST = "./pp team post core-review --task T3 --to reviewer --reply 45 --as pm --message ok"
TWO_LINES = "team post core-review --task T3 --message 'ok\ngo'"
TASK = next(one for one in T.CORE["tasks"] if one["id"] == "T3")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-gestures")

    # --- m: the line, its lists, its preview ----------------------------------------------------------
    shown = house.render("--render", "tasks", "--size", "200x50", "--press", TYPED)
    preview = T.preview_in(shown, "./pp team post")
    title = " ".join(P.title_of(shown.stdout))
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "200x50", "--press", TYPED + ",tab,tab,tab,enter")
    played = house.gestures()
    journal = house.journal_lines()
    reread = played and journal.index(played[0]) < len(journal) - 1 and \
        "status core-review" in journal[journal.index(played[0]) + 1:]
    if (shown.returncode == 0 and done.returncode == 0 and preview == POST and played == [POST[len("./pp "):]]
            and reread and T.in_order(title, TASK["id"], TASK["name"], T.CORE["team"])):
        held("m plays what its overlay shows", f"{preview!r}; the tasks read again after it")
    else:
        failures.append(f"  ✗ the line                    rc={shown.returncode},{done.returncode} {preview!r} {played} "
                        f"{title!r} {journal} {shown.stdout[-1600:]!r} {done.stderr[-400:]!r}")

    # --- m by the owner: no --as, a text on two lines -------------------------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "130x40", "--press", "m,o,k,ctrl+enter,g,o,enter")
    raw = house.journal.read_text(encoding="utf-8") if house.journal.is_file() else ""
    if done.returncode == 0 and TWO_LINES in raw and "--as" not in raw:
        held("the owner writes no --as", TWO_LINES.split(" --message")[0])
        held("a text on two lines leaves whole", "--message 'ok\\ngo'")
    else:
        failures.append(f"  ✗ owner, two lines            rc={done.returncode} {raw!r} {done.stdout[-900:]!r}")

    return 0
