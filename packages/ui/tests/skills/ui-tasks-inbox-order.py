"""Scenario `ui-tasks-inbox-order` -- the owner's inbox opened from the Tasks tab (`b`), on the bench's `pp-team` witness,
as `team inbox --json` says it after team's s.1587 (an ask of a task no longer open among the infos, `closed: true`):
- the order (s.1585): the questions first, then the notices that wait for the owner's answer, then the other notices,
  the infos, the tasks done -- each sort the latest first, whatever order `team inbox --json` says them in
- an info `closed`: its row says `(closed)`, `enter` on it opens no reply and plays nothing; `x` on it plays
  `team inbox <team> --seen --id <its id>` and its row leaves, the inbox open; when the team refuses it
  (`team-unknown`, as from an agent's console, s.1613), the refusal is said under the list and the row kept (s.1704)
- a reply the team refuses (`task-closed`): the inbox stays on top and says the refusal under its list
- under the pilot: the refusal said under the list leaves when the cursor moves, and when a reply then passes and the
  inbox is read again (s.1585, relecture #9586)
- under the pilot: each row of the inbox carries the moment of its message, `at` as `team inbox --json` says it, in
  the post's own rendering of a moment (`palette.moment_of`, s.1706)
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")

QUESTION = {"id": 45, "verb": "ask", "from": "reviewer", "task": "T3", "text": "tests green?", "at": "2026-11-10T09:15:00+00:00"}
INBOX = {"core-review": {"team": "core-review", "questions": [QUESTION],
                         "done": [{"task": "T2", "id": 40, "at": "2026-11-12T16:40:00+00:00"}], "returned": []}}
REPLY = f"team post core-review --task {QUESTION['task']} --reply {QUESTION['id']} --message ok --no-tick"
ORDERED = {"core-review": {"team": "core-review",
                           "questions": [QUESTION, {"id": 46, "verb": "ask", "from": "lead", "task": "T3", "text": "and?"}],
                           "notices": [{"id": 41, "from": "core-review", "about": "lead", "task": "T3", "text": "slow",
                                        "awaits": False},
                                       {"id": 43, "from": "core-review", "about": "reviewer", "task": "T3", "text": "fell",
                                        "awaits": True}],
                           "infos": [{"id": 47, "from": "lead", "task": "T3", "text": "older"},
                                     {"id": 49, "from": "lead", "task": "T3", "text": "newer"}],
                           "done": [{"task": "T1", "id": 38}, {"task": "T2", "id": 40}], "returned": []}}
LATEST_FIRST = [46, 45, 43, 41, 49, 47, 40, 38]
CLOSED = {"core-review": {**INBOX["core-review"],
                          "infos": [{"id": 50, "from": "reviewer", "task": "T1", "text": "scope?", "closed": True}]}}
READ_CLOSED = "team inbox core-review --seen --id 50"
UNKNOWN = "pp-team: team-unknown -- no agents/lead/teams/core-review/TEAM.md: the owner declares the team there."
TASK_CLOSED = "pp-team: task-closed -- T3 is resolved: a post opens a new task instead."


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-inbox-order", T.script(inbox=ORDERED))
    # --- the order: the questions first, then each sort the latest first -- s.1585 ------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "150x60", "--press", "b")
    listed = [one for one in P.overlay_rows(done.stdout) if one.startswith("▊")]
    order = [int(found.group(1)) for found in (re.search(r"#(\d+)", one) for one in listed) if found]
    if done.returncode == 0 and order == LATEST_FIRST and house.gestures() == []:
        held("the questions first, the latest first", f"rows {order}: the questions, the notice that waits, the other, "
             "the infos, the tasks done -- each sort from the latest")
    else:
        failures.append(f"  ✗ the order                   rc={done.returncode} order={order} {done.stdout[-1500:]!r}")

    # --- an info closed: said so, no reply ----------------------------------------------------------------------
    house.use(T.script(inbox=CLOSED))
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "150x40", "--press", "b,down,enter")
    inside = P.overlay_rows(done.stdout)
    closed = [one for one in inside if "#50" in one and one.startswith("▊")]
    if (done.returncode == 0 and len(closed) == 1 and "(closed)" in closed[0] and house.gestures() == []
            and any("inbox of core-review" in one for one in inside)):
        held("an info closed, no reply", f"{closed[0][:60]!r}: enter on it opens no reply, plays nothing, the inbox kept")
    else:
        failures.append(f"  ✗ an info closed              rc={done.returncode} closed={closed} {house.gestures()} {inside}")

    # --- x on an info closed: read, its row gone; refused, the refusal under the list -- s.1704 ------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "150x40", "--press", "b,down,x")
    played, inside = house.gestures(), P.overlay_rows(done.stdout)
    house.use(T.script(inbox=CLOSED, answers={"inbox": {"rc": 2, "err": UNKNOWN + "\n"}}))
    house.clear_journal()
    refused = house.render("--render", "tasks", "--size", "150x40", "--press", "b,down,x")
    again, kept = house.gestures(), P.overlay_rows(refused.stdout)
    gap = [one for one in kept if "team-unknown" in one and not one.startswith("▊")]
    if (done.returncode == 0 and played == [READ_CLOSED] and any("inbox of core-review" in one for one in inside)
            and not any("#50" in one for one in inside if one.startswith("▊"))
            and refused.returncode == 0 and again == [READ_CLOSED] and gap
            and any("#50" in one for one in kept if one.startswith("▊"))):
        held("x on an info closed", f"{played[0]}: #50 gone, the inbox open; refused team-unknown: said under the "
             "list, #50 kept")
    else:
        failures.append(f"  ✗ x on an info closed         rc={done.returncode}/{refused.returncode} {played} {again} "
                        f"gap={gap} {inside} {kept}")

    # --- a reply the team refuses: said on the inbox, which stays ------------------------------------------------
    house.use(T.script(inbox=INBOX, answers={"post": {"rc": 2, "err": TASK_CLOSED + "\n"}}))
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "150x40", "--press", "b,enter,o,k,ctrl+enter")
    inside = P.overlay_rows(done.stdout)
    if (done.returncode == 0 and house.gestures() == [REPLY] and any("inbox of core-review" in one for one in inside)
            and any("task-closed" in one for one in inside)):
        held("a reply refused, said on the inbox", f"{REPLY!r} refused task-closed: the inbox on top says it")
    else:
        failures.append(f"  ✗ a reply refused             rc={done.returncode} {house.gestures()} {inside} "
                        f"remedy={P.remedy_of(done.stdout)!r}")

    # --- the refusal said goes: the cursor moves, a reply then passes -------------------------------------------
    house.clear_journal()
    [(rc, said, err)] = T.piloted(bench, house, "ui-tasks-inbox-order", PROBE, "tasks", size="150x40")
    gaps = (said.get("refused"), said.get("moved"), said.get("again"), said.get("passed"))
    dated = said.get("dated") or {}
    if rc == 0 and said.get("opened") and sorted(dated) == ["40", "45"] and all(dated.values()):
        held("each row carries the moment of its message", f"#45 and T2 done (#40): palette.moment_of of their at on "
             "their rows")
    else:
        failures.append(f"  ✗ the moment of each row      rc={rc} dated={dated}")
    if (rc == 0 and said.get("opened") and "task-closed" in (said.get("refused") or "")
            and "task-closed" in (said.get("again") or "") and said.get("moved") == "" and said.get("passed") == ""
            and said.get("posts") == 3 and said.get("top") == "InboxScreen"):
        held("the refusal said goes", "task-closed said under the list; gone once the cursor moves; said again, gone "
             "once a reply passes and the inbox is read again")
    else:
        failures.append(f"  ✗ the refusal said goes       rc={rc} gaps={gaps} {said} {err[-1200:]!r}")
    return 0


PROBE = """
import os
from panes.overlays import GestureScreen, InboxScreen
from textual.widgets import OptionList


def calls():
    log = os.environ.get("PP_UI_TEAM_LOG", "")
    return open(log, encoding="utf-8").read().splitlines() if log and os.path.isfile(log) else []


def posts():
    return len([line for line in calls() if line.startswith("team post")])


def gap(app):
    return str(app.screen.query_one("#inbox-gap").render()) if isinstance(app.screen, InboxScreen) else None


async def replied(app, pilot, count):
    await pilot.press("enter")
    if not await until(pilot, lambda: isinstance(app.screen, GestureScreen), 5):
        return False
    await pilot.press("o", "k", "ctrl+enter")
    return await until(pilot, lambda: posts() >= count and isinstance(app.screen, InboxScreen), 8)


async def probe(app, pilot, view, out):
    await pilot.press("b")
    out["opened"] = await until(pilot, lambda: isinstance(app.screen, InboxScreen) and bool(app.screen.query("#inbox")))
    if not out["opened"]:
        return
    import palette
    found = json.loads(open(os.environ["PP_UI_TEAM_SCRIPT"], encoding="utf-8").read())["inbox"]["core-review"]
    moments = {str(one["id"]): one["at"] for sort in ("questions", "done") for one in found.get(sort) or []}
    listed = app.screen.query_one("#inbox", OptionList)
    rows = {str(app.screen.lines[n][2]): str(listed.get_option_at_index(n).prompt) for n in range(listed.option_count)}
    out["dated"] = {mid: palette.moment_of(at) in rows.get(mid, "") for mid, at in moments.items()}
    app.screen.query_one("#inbox", OptionList).highlighted = 0
    await pilot.pause()
    await replied(app, pilot, 1)
    await until(pilot, lambda: "task-closed" in (gap(app) or ""), 5)
    out["refused"] = gap(app)
    await pilot.press("down")
    await pilot.pause()
    await pilot.pause()
    out["moved"] = gap(app)
    await pilot.press("up")
    await pilot.pause()
    await replied(app, pilot, 2)
    await until(pilot, lambda: "task-closed" in (gap(app) or ""), 5)
    out["again"] = gap(app)
    path = os.environ["PP_UI_TEAM_SCRIPT"]
    script = json.loads(open(path, encoding="utf-8").read())
    script.get("answers", {}).pop("post", None)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(script))
    await replied(app, pilot, 3)

    def reread():
        found = calls()
        last = [n for n, line in enumerate(found) if line.startswith("team post")][-1:]
        return bool(last) and "inbox core-review" in found[last[0] + 1:]
    await until(pilot, reread, 8)
    await pilot.pause()
    await pilot.pause()
    out["passed"], out["posts"], out["top"] = gap(app), posts(), type(app.screen).__name__
"""
