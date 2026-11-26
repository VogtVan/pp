"""Scenario `ui-tasks-thread` -- the thread of a task draws before its history returns (batch la-sequence-vivante), on
the bench's `pp-team` witness whose `log` tarries two seconds:
- the band draws what the watch said of the task before `team log` returned: a post #46 relayed at 0.5 s is a row of the
  sequence before the history (the render's word `rows`), and the whole thread once it returned
- the overlay of the thread closing while its workers still draw (batch le-result-et-le-fil, s.1507): its children
  gone, the screen still attached, the watch says a post of the task -- the history read again and the post added
  draw nothing and raise nothing, the post stays up; in a Textual app played in a subprocess, the team's faces stood
  in for
"""
from __future__ import annotations

import json
import subprocess

from tests.harness import SOURCE, support

T = support(__file__, "teams")
SKILL = SOURCE / "packages" / "ui" / "skills" / "pp-ui"
TEXTUAL = ("uv", "run", "--quiet", "--no-project", "--with", "textual==8.2.8", "--with", "pyyaml>=6", "python3")
PROBE = """
import asyncio, json, sys
sys.path.insert(0, sys.argv[1])
from textual.app import App
from faces import Face
import panes.tasks as tasks

POST = json.loads(sys.argv[2])
queue = asyncio.Queue()
reads = []


class Watch:
    async def events(self):
        while True:
            found = await queue.get()
            if found is None:
                return
            yield found

    async def close(self):
        queue.put_nowait(None)


async def follow(house, team):
    return Watch()


async def log(house, team, task=None):
    reads.append(task)
    return [], Face(("team", "log"), 0, "", "")


class Pane:
    house = "house"

    def open_ids(self, team):
        return set()


tasks.faces.follow, tasks.faces.log = follow, log


async def main():
    app = App()
    said = {"failed": None}
    try:
        async with app.run_test(size=(120, 40)) as pilot:
            screen = tasks.ThreadScreen(Pane(), "core-review", "T3", "T3")
            await app.push_screen(screen)
            while screen.reading:
                await pilot.pause()
            await screen.query_one("#box").remove()       # the children gone, the screen still attached: its closing
            queue.put_nowait(POST)
            for _ in range(10):
                await pilot.pause()
            said.update(attached=screen.is_attached, running=app.is_running, reads=len(reads))
    except Exception as failed:
        said["failed"] = f"{type(failed).__name__}: {failed}"[:300]
    print(json.dumps(said))


asyncio.run(main())
"""


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    script = T.script(log={"core-review": T.TEAM_LOG, "core-review/T3": [{"sleep": 2.0}] + T.T3_LOG,
                           "core-review/T2": T.T2_LOG},
                      watch={"core-review": [{"sleep": 0.5}, T.WRITTEN, {"sleep": 0.2}, T.STEP]})
    house = T.Teams(bench, "ui-tasks-thread", script)
    done = house.render("--render", "tasks", "--size", "150x42", "--press", "rows")   # the render waits for the history: the post came before it;
    # every row in sight under a head of five lines, the principal's part under its name
    noted = next((one[5:] for one in reversed(done.stdout.split("\n")) if one.startswith("rows ")), "")
    ids = [one["id"] for one in T.T3_LOG if one["event"] == "post"] + [T.WRITTEN["id"]]
    if (done.returncode == 0 and noted == "1" and all(f"#{one} " in done.stdout for one in ids)):
        held("the thread draws before the log returns", f"{noted} row drawn before the history, {len(ids)} after it")
    else:
        failures.append(f"  ✗ before the log              rc={done.returncode} rows={noted!r} "
                        f"{done.stdout[-1500:]!r} {done.stderr[-300:]!r}")

    # --- the overlay closing while a worker draws: nothing drawn, nothing raised ------------------------------------
    probe = bench.temp() / "thread-closing-probe.py"
    probe.write_text(PROBE, encoding="utf-8")
    played = subprocess.run([*TEXTUAL, str(probe), str(SKILL), json.dumps(T.WRITTEN)], capture_output=True, text=True,
                            cwd=bench.temp(), timeout=120)
    try:
        said = json.loads(played.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        said = {}
    if played.returncode == 0 and said.get("failed") is None and said.get("attached") and said.get("reads", 0) >= 2:
        held("the thread closing draws nothing and raises nothing",
             f"children gone, still attached; history read {said['reads']} times, the post up")
    else:
        failures.append(f"  ✗ closing                     rc={played.returncode} {said} {played.stderr[-1200:]!r}")
    return 0
