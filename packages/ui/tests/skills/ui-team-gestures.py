"""Scenario `ui-team-gestures` -- writing on a task and giving a team a new task, each in its overlay (plan ui,
batches les-gestes-du-pilote, les-deux-onglets and les-overlays-des-gestes), on the bench's `pp-team` witness:
- `m` on T3 (the first task running): an overlay, `to` / `as` / `reply to` read from `team status --json` (the
  members, the owner and the principals, the questions of the task), then the text; the command under the fields
  is what `enter` plays, word for word -- `post core-review --task T3 --to reviewer --reply 45 --as pm --message ok`
- the owner writes no `--as`; a text on two lines (`shift+enter`) leaves whole
- `n` on the Teams tab: a new task to the root, `post` without `--task` (on the Tasks tab: `ui-team-new-task`)
- after a gesture the tasks are read again
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

TYPED = "m,o,k,shift+tab,space,down,enter,shift+tab,space,down,enter,shift+tab,space,down,down,enter"
POST = "./pp team post core-review --task T3 --to reviewer --reply 45 --as pm --message ok"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-gestures")

    # --- the line, its lists, its preview -------------------------------------------------------------
    shown = house.render("--render", "tasks", "--size", "200x50", "--press", TYPED)
    preview = T.preview_in(shown, "./pp team post")
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "200x50", "--press", TYPED + ",tab,tab,tab,enter")
    played = house.gestures()
    journal = house.journal_lines()
    reread = played and journal.index(played[0]) < len(journal) - 1 and \
        "status core-review" in journal[journal.index(played[0]) + 1:]
    if (shown.returncode == 0 and done.returncode == 0 and preview == POST and played == [POST[len("./pp "):]]
            and reread and "write on T3 of core-review" in " ".join(shown.stdout.split())):
        held("m plays what its overlay shows", f"{preview!r}; the tasks read again after it")
    else:
        failures.append(f"  ✗ the line                    rc={shown.returncode},{done.returncode} {preview!r} {played} "
                        f"{journal} {shown.stdout[-1600:]!r} {done.stderr[-400:]!r}")

    # --- the owner writes no --as ---------------------------------------------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "130x40", "--press", "m,h,i,enter")
    played = house.gestures()
    if done.returncode == 0 and played == ["team post core-review --task T3 --message hi"]:
        held("the owner writes no --as", played[0])
    else:
        failures.append(f"  ✗ owner                       rc={done.returncode} {played} {done.stdout[-900:]!r}")

    # --- n: a new task -------------------------------------------------------------------------------
    shown = house.render("--render", "teams", "--size", "130x40", "--press", "n,g,o")
    preview = T.preview_in(shown, "./pp team post")
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "130x40", "--press", "n,g,o,enter")
    played = house.gestures()
    if (shown.returncode == 0 and done.returncode == 0 and preview == "./pp team post core-review --message go"
            and played == [preview[len("./pp "):]]):
        held("n posts a new task", f"{preview!r} shown, then played")
    else:
        failures.append(f"  ✗ new task                    rc={shown.returncode},{done.returncode} {preview!r} {played} "
                        f"{shown.stdout[-900:]!r}")

    # --- m: a text on two lines -----------------------------------------------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "130x40", "--press", "m,o,k,shift+enter,g,o,enter")
    raw = house.journal.read_text(encoding="utf-8") if house.journal.is_file() else ""
    if done.returncode == 0 and "team post core-review --task T3 --message 'ok\ngo'" in raw:
        held("a text on two lines leaves whole", "--message 'ok\\ngo'")
    else:
        failures.append(f"  ✗ two lines                   rc={done.returncode} {raw!r} {done.stdout[-900:]!r}")

    return 0
