"""Scenario `ui-team-gestures` -- writing on a task and giving a team a new task, each in its overlay, the command
under the fields what `enter` plays word for word, on the bench's `pp-team` witness:
- `m` on T3 (the first task running): an overlay titled by the task and its team, `to` / `as` / `reply to` read from
  `team status --json` (the members, the owner and the principals, the questions of the task), then the text --
  `post core-review --task T3 --to reviewer --reply 45 --as pm --message ok`; the tasks read again after it
- `n` on the Teams tab: a new task to the root, `post` without `--task`
- the owner writes no `--as`; a text on two lines (`ctrl+enter`) leaves whole
- `n` on the Tasks tab: its team the one of the task under the cursor, its name as typed, accents kept --
  `post core-review --name 'Réunion fournisseurs' --message go`
- `n` on the Tasks tab, its team chosen in the overlay: `post ops --message go`, its `to` and `as` following the team
  chosen
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the readers of a capture

TYPED = "m,o,k,shift+tab,space,down,enter,shift+tab,space,down,enter,shift+tab,space,down,down,enter"
POST = "./pp team post core-review --task T3 --to reviewer --reply 45 --as pm --message ok"
NEW = "./pp team post core-review --message go"
TWO_LINES = "team post core-review --task T3 --message 'ok\ngo'"
NAME = "Réunion fournisseurs"
NAMED = f"./pp team post core-review --name '{NAME}' --message go"
CHOSEN = "team post ops --message go"
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

    # --- n on the Teams tab: a new task ---------------------------------------------------------------
    shown = house.render("--render", "teams", "--size", "130x40", "--press", "n,g,o")
    preview = T.preview_in(shown, "./pp team post")
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "130x40", "--press", "n,g,o,enter")
    played = house.gestures()
    if shown.returncode == 0 and done.returncode == 0 and preview == NEW and played == [preview[len("./pp "):]]:
        held("n posts a new task", f"{preview!r} shown, then played")
    else:
        failures.append(f"  ✗ new task                    rc={shown.returncode},{done.returncode} {preview!r} {played} "
                        f"{shown.stdout[-900:]!r}")

    # --- m by the owner: no --as, a text on two lines -------------------------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "130x40", "--press", "m,o,k,ctrl+enter,g,o,enter")
    raw = house.journal.read_text(encoding="utf-8") if house.journal.is_file() else ""
    if done.returncode == 0 and TWO_LINES in raw and "--as" not in raw:
        held("the owner writes no --as", TWO_LINES.split(" --message")[0])
        held("a text on two lines leaves whole", "--message 'ok\\ngo'")
    else:
        failures.append(f"  ✗ owner, two lines            rc={done.returncode} {raw!r} {done.stdout[-900:]!r}")

    # --- n on the Tasks tab: a name, accents kept -----------------------------------------------------
    keys = "n,g,o,shift+tab,shift+tab,shift+tab," + ",".join("space" if one == " " else one for one in NAME)
    shown = house.render("--render", "tasks", "--size", "200x50", "--press", keys)
    preview = T.preview_in(shown, "./pp team post")
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "130x40", "--press", keys + ",enter")
    if shown.returncode == 0 and done.returncode == 0 and preview == NAMED and house.gestures() == [NAMED[len("./pp "):]]:
        held("n names its task as typed", f"{preview!r} shown, then played")
    else:
        failures.append(f"  ✗ named                       rc={shown.returncode},{done.returncode} {preview!r} "
                        f"{house.gestures()} {shown.stdout[-1200:]!r} {shown.stderr[-300:]!r}")

    # --- n on the Tasks tab: the team chosen in the overlay -------------------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "130x40", "--press",
                        "n,g,o,shift+tab,shift+tab,shift+tab,shift+tab,space,down,enter,enter")
    if done.returncode == 0 and house.gestures() == [CHOSEN]:
        held("n gives the team chosen its task", house.gestures()[0])
    else:
        failures.append(f"  ✗ team chosen                 rc={done.returncode} {house.gestures()} {done.stdout[-1200:]!r}")

    return 0
