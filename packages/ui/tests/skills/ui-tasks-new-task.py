"""Scenario `ui-tasks-new-task` -- giving a team a new task in its overlay, what `enter` plays read from the journal
of the bench's `pp-team` witness, no command shown on screen:
- `n` on the Teams tab: a new task to the root, `post` without `--task`, played from a 130x40 screen where its fields
  scroll
- `n` on the Tasks tab: its team the one of the task under the cursor, its name as typed, accents kept --
  `post core-review --name 'Réunion fournisseurs' --message go`
- `n` on the Tasks tab, its team chosen in the overlay: `post ops --message go`, its `to` and `as` following the team
  chosen
- `n` with a period and a context limit: `post core-review --every 4h --context 70% --message go`; the limit typed
  without a period is not passed
- `n` on the Tasks tab, its team off season: the `post` refused `season-stopped` keeps the overlay on top, each field as
  typed, the refusal's code under the fields; `enter` again, the post accepted, closes it -- read by Textual's pilot
  (a long message, no command shown: `ui-tasks-long-message`)
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

NEW = "team post core-review --message go --no-tick"
NAME = "Réunion fournisseurs"
NAMED = f"team post core-review --name '{NAME}' --message go --no-tick"
CHOSEN = "team post ops --message go --no-tick"
LIMITED = "team post core-review --every 4h --context 70% --message go --no-tick"
OFF_SEASON = "pp-team: season-stopped -- core-review is off season: `team start core-review`\n"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-new-task")

    # --- n on the Teams tab: a new task ---------------------------------------------------------------
    done = house.render("--render", "teams", "--size", "130x40", "--press", "n,g,o,ctrl+enter")   # the fields scrolled
    played = house.gestures()
    if done.returncode == 0 and played == [NEW] and "./pp" not in done.stdout:
        held("n posts a new task", f"{played[0]!r} played, no command on screen")
    else:
        failures.append(f"  ✗ new task                    rc={done.returncode} {played} {done.stdout[-900:]!r}")

    # --- n on the Tasks tab: a name, accents kept -----------------------------------------------------
    keys = "n,g,o,shift+tab,shift+tab,shift+tab," + ",".join("space" if one == " " else one for one in NAME)
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "130x40", "--press", keys + ",ctrl+enter")
    if done.returncode == 0 and house.gestures() == [NAMED]:
        held("n names its task as typed", f"{NAMED!r} played")
    else:
        failures.append(f"  ✗ named                       rc={done.returncode} {house.gestures()} "
                        f"{done.stdout[-1200:]!r} {done.stderr[-300:]!r}")

    # --- n on the Tasks tab: the team chosen in the overlay -------------------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "130x40", "--press",
                        "n,g,o,shift+tab,shift+tab,shift+tab,shift+tab,space,down,enter,ctrl+enter")
    if done.returncode == 0 and house.gestures() == [CHOSEN]:
        held("n gives the team chosen its task", house.gestures()[0])
    else:
        failures.append(f"  ✗ team chosen                 rc={done.returncode} {house.gestures()} {done.stdout[-1200:]!r}")

    # --- n with a period and a context limit; a limit without a period ----------------------------------
    said, codes = [], []
    for keys in ("n,g,o,tab,4,h,tab,7,0,%,ctrl+enter", "n,g,o,tab,tab,7,0,%,ctrl+enter"):
        house.clear_journal()
        limited = house.render("--render", "teams", "--size", "130x60", "--press", keys)
        codes.append(limited.returncode)
        said += house.gestures()
    if codes == [0, 0] and said == [LIMITED, NEW]:
        held("n passes a context limit with a period alone", f"{said}")
    else:
        failures.append(f"  ✗ context limit               {said} {limited.stdout[-1500:]!r}")

    # --- n off season: the post refused keeps the form, then sent again ------------------------------------
    house.use({**T.script(), "answers": {"post": {"rc": 2, "err": OFF_SEASON}}})
    house.clear_journal()
    [(rc, seen, err)] = T.piloted(bench, house, "ui-tasks-new-task", PROBE, "tasks", size="130x40")
    posts = [one for one in house.journal_lines() if one.startswith("team post")]
    refused, again = seen.get("refused") or {}, seen.get("again") or {}
    if (rc == 0 and refused.get("top") == "GestureScreen" and refused.get("code") == "season-stopped"
            and (refused.get("values") or {}).get("message") == "go"
            and (refused.get("values") or {}).get("team") == "core-review"
            and again.get("top") != "GestureScreen" and posts == [NEW, NEW]):
        held("a post refused keeps its form", f"season-stopped under the fields, {refused['values']} kept; sent again "
             f"and accepted, the form closed: {posts}")
    else:
        failures.append(f"  ✗ refused keeps the form      rc={rc} {seen} {posts} {err[-1500:]!r}")

    return 0


# `n` on the Tasks tab, `go` typed, `enter` refused off season; the post then accepted, `enter` again
PROBE = """
import os
from panes.overlays import GestureScreen


def top(app):
    screen = app.screen
    shown = isinstance(screen, GestureScreen)
    refused = getattr(screen, "refused", None) if shown else None
    return {"top": type(screen).__name__, "values": screen.values() if shown else None,
            "code": refused[0] if refused else None}


async def probe(app, pilot, view, out):
    await pilot.press("n")
    if not await until(pilot, lambda: isinstance(app.screen, GestureScreen), 5):
        return
    await pilot.press("g", "o", "ctrl+enter")
    await until(pilot, lambda: not isinstance(app.screen, GestureScreen) or getattr(app.screen, "refused", None), 8)
    out["refused"] = top(app)
    if not isinstance(app.screen, GestureScreen):
        return
    script = Path(os.environ["PP_UI_TEAM_SCRIPT"])
    found = json.loads(script.read_text(encoding="utf-8"))
    found.pop("answers", None)
    script.write_text(json.dumps(found), encoding="utf-8")
    await pilot.press("ctrl+enter")
    await until(pilot, lambda: not isinstance(app.screen, GestureScreen), 8)
    await app.pane_settled()
    out["again"] = top(app)
"""
