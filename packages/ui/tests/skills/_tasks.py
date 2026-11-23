"""_tasks -- what the scenarios of the Tasks tab's table share (rule 10, cut out of `ui-tasks`): the faces of the
bench's `pp-team` witness they read -- `core-review` and `ops` started --, the names of their tasks and the reading of
a capture's rows (`rows_of`) and band (`band_of`), the tasks the owner has to see (`for_you`), what `team stats` says of
T3 over its two seasons (`STATS`, `SAID`, `BASED`), the task with a long name and four holders (`LONG`), and the probe
that reads the table's cells by Textual's pilot and chooses the base of the costs in the settings (`PROBE`)."""
from __future__ import annotations

import asyncio
import importlib.util
import re
import sys
from datetime import datetime

from tests.harness import SOURCE, support

T = support(__file__, "teams")
P = support(__file__, "dialogue")
FACES = SOURCE / "packages" / "ui" / "skills" / "pp-ui" / "faces" / "__init__.py"
MODEL = SOURCE / "packages" / "ui" / "skills" / "pp-ui" / "model" / "teams.py"
TEAMS = {"core-review": T.CORE, "ops": T.OPS}
TASKS = [(team, task) for team, face in TEAMS.items() for task in face["tasks"]]
T3 = next(task for task in T.CORE["tasks"] if task["id"] == "T3")
NEW = "team post core-review --message go --no-tick"


def _constant(name: str):
    """-> the constant `name` of `palette.py`, None when the palette names none."""
    try:
        return P.palette_constant(name)
    except KeyError:
        return None


CELL = _constant("TASK_CELL")                       # the cells a task's name and its holders hold at most
CUT = P.palette_constant("PENDING")                 # the end of a cell cut
LONG = {**T3, "id": "T9", "name": "triage the flaky scenarios of the night", "cost": None, "resumed": None,
        "holders": ["lead", "reviewer", "alice", "bob-the-builder"], "dos": []}   # a long name and four holders
COLUMNS = ("id", "task", "team", "state", "holder", "at", "elapsed", "effort", "USD", "lnch", "do", "re", "fail", "ctx")


def task_line(usd: float, launches: int, tokens: int, do: int, re_: int, failures: int, elapsed: int, active: int,
              effort: int, first: str, last: str, context: float, season: int | None = None) -> dict:
    """-> T3's line of `team stats`, in a season's `by_task` under `season`, over all its seasons without."""
    return {"task": "T3", "name": T3["name"], **({"season": season} if season else {}), "state": "open",
            "cost": {"usd": usd, "launches": launches, "tokens": tokens, "tokens_estimated": False}, "do": do,
            "re": re_, "failures": failures, "time": {"elapsed": elapsed, "active": active, "effort": effort},
            "first": first, "last": last, "context_max": context}


# T3 worked in two seasons: each season's line, and the total the verb says over both -- the one the table shows
# -- its elapsed time the wall from the first event of its first season to the last of its second (24 h 41 min), its
# active time and its effort summed
DAY_1, DAY_2 = "2026-10-10T", "2026-10-11T"
STATS = {"median": {}, "seasons": [
    {"season": 1, "by_task": [task_line(0.5, 1, 3000, 1, 1, 0, 1200, 1200, 1800, DAY_1 + "09:01:00+00:00",
                                        DAY_1 + "09:21:00+00:00", 0.3, 1)]},
    {"season": 2, "by_task": [task_line(1.0, 3, 6000, 2, 1, 1, 2520, 2520, 3600, DAY_2 + "09:00:00+00:00",
                                        DAY_2 + "09:42:00+00:00", 0.54, 2)]}],
    "by_task": [task_line(1.5, 4, 9000, 3, 2, 1, 88860, 3720, 5400, DAY_1 + "09:01:00+00:00", DAY_2 + "09:42:00+00:00",
                          0.54)]}
SAID = ["1d", "1h30", "1.50", "4", "3", "2", "1", "54%"]        # T3's total, as the table says it in USD
BASED = {"launches": ("cost", "4"), "tokens": ("tok", "9k")}     # each base chosen: the cost's own title, T3's cost


def ended_at_its_bound(house: str) -> tuple[object, str]:
    """-> the face `play_verb` gives for `team status --json` when the verb ends as its bound passes, and what it
    raised instead, if anything -- the post's own seam, loaded from the source, `asyncio.wait_for` made to say
    the bound passed once the verb is over."""
    spec = importlib.util.spec_from_file_location("pp_ui_faces", FACES)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module          # a dataclass reads its module there
    spec.loader.exec_module(module)
    bounded = asyncio.wait_for

    async def late(awaited, timeout):
        await awaited                          # the verb ends...
        raise asyncio.TimeoutError             # ...as its bound passes
    asyncio.wait_for = late
    try:
        return asyncio.run(module.play_verb(["team", "status", "--json"], house)), ""
    except Exception as error:                 # noqa: BLE001 -- what the seam let out is the finding
        return None, f"{type(error).__name__} {error}".rstrip()
    finally:
        asyncio.wait_for = bounded


def every_task() -> str | None:
    """-> the `SHOW` filter that keeps every task, as the post's typed state names it (`model.teams.EVERY_TASK`),
    loaded from the source; None when the model names none."""
    spec = importlib.util.spec_from_file_location("pp_ui_model_teams", MODEL)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module          # a dataclass reads its module there
    spec.loader.exec_module(module)
    return getattr(module, "EVERY_TASK", None)


NAMES = ("review PR 88", "review PR 87", "daily 2026-10-10", "rotate the certificates", "weekly report")
ROW = re.compile(r"(" + "|".join(re.escape(one) for one in NAMES) + r")\S*(?: \S+)*?\s+(core-review|ops)\s+"
                 r"(open|stopped|resolved)\b")


def moment(iso: str) -> str:
    """The moment a task was born as the post says it of another day (`palette.moment_of`): `DD/MM HH:MM` in local
    time -- the bench's own copy."""
    return f"{datetime.fromisoformat(iso).astimezone():%d/%m %H:%M}"


def rows_of(text: str) -> list[str]:
    """-> the rows of the table of the tasks: a task's name, its team, its state."""
    return [found.group(0) for found in map(ROW.search, text.split("\n")) if found]






def band_of(text: str) -> list[str]:
    """-> the rows of the band under the table of the tasks (`band_rows`)."""
    return T.band_rows(T.sides_of(text)[1])


def for_you() -> set[tuple[str, str]]:
    """-> the tasks the owner has to see: a question waits on it, or its end is not seen yet."""
    return {(team, one["task"]) for team, face in TEAMS.items() for one in face["waiting"]["questions"]} | \
        {(team, task) for team, face in TEAMS.items() for task in face["waiting"]["done"]}



# the columns of the Tasks table and the cells of each of its rows, once the tasks are read; then, for `launches` then
# `tokens`, the settings opened by the footer's key `SETTINGS_KEY` and the base chosen in their list: the overlay that
# opened, the one `escape` opens over the choice changed and the one a second `escape` gives back, the base sent by
# `ctrl+enter` as each pane holds it (the Teams tab's summary and dashboard, the Tasks table), whether the titles of the
# summary and of the dashboard say it, the base once its word in the summary's title is clicked, the table read again
SETTINGS_KEY = "O"
PROBE = """
from render import screen_text
from panes import season


def read(table):
    return ([str(one.label) for one in table.columns.values()],
            [[str(cell) for cell in table.get_row_at(index)] for index in range(table.row_count)])


def says(frame, base):
    return season.BASE_WORDS[base] in season.plain_of(frame.border_title or "")


async def probe(app, pilot, view, out):
    table = app.query_one("#tasks-list")
    if not await until(pilot, lambda: table.row_count > 0, 8):
        return
    out["columns"], out["rows"] = read(table)
    out["first"] = [app.teams._base, app.tasks.base]
    app.show_pane("teams")
    await app.pane_settled()
    await pilot.pause()
    for base in ("launches", "tokens"):
        await pilot.press("%s")
        await pilot.pause()
        opened = type(app.screen).__name__
        for key in ("down", "down", "enter"):   # unrolled on the base in force, the next one chosen
            await pilot.press(key)
            await pilot.pause()
        await pilot.press("escape")
        await pilot.pause()
        asked = type(app.screen).__name__
        await pilot.press("escape")
        await pilot.pause()
        back = type(app.screen).__name__
        await pilot.press("ctrl+enter")
        await pilot.pause()
        stats, board = app.query_one("#teams-stats"), app.query_one("#teams-board")
        app.teams.open_board(True)
        await pilot.pause()
        titled = says(stats, base) and says(board, base)
        app.teams.open_board(False)
        await pilot.pause()
        region = stats.region
        at = screen_text(app).split("\\n")[region.y].find(season.BASE_WORDS[base], region.x)
        if at >= 0:
            await pilot.click("#teams-stats", offset=(at - region.x + 1, 0))
            await pilot.pause()
        out[base + "-said"] = [opened, asked, back, app.teams._base, app.tasks.base, titled, at >= 0, app.teams._base]
        app.show_pane("tasks")
        await app.pane_settled()
        await pilot.pause()
        out[base] = read(table)
        app.show_pane("teams")
        await app.pane_settled()
        await pilot.pause()
""" % SETTINGS_KEY
