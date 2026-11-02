"""Scenario `ui-tasks` -- the Tasks tab says what the teams do, on the bench's `pp-team` witness replaying the faces of
`team` for three declared teams -- `core-review` and `ops` started, `veille` never:
- the tasks of every team started in ONE table, the most recently born first, `recent` by default: the id before the
  name, else the start of the text cut at 30 characters; the team, the state, the holders, the progress counted on
  the face's delegations, the cost, the moment the task was born; the menu counting what each filter keeps; the tasks
  shown over every task on the status line
- the filters: the tasks with a question or an end not seen, every task -- the teams mingled by birth --, a team alone
- `recent`, on faces dated at the reading: an open task of three days stays, a task resolved two days ago leaves, one
  resolved ten hours ago stays
- the task launched follows: `n` played under `resolved`, the new task -- the id the face did not say before -- under
  the cursor, the filter turned to `recent` on the status line; the task resolved by the team, the cursor still on it
- the band: the task under the cursor -- its id, its state, its team, its holders, its text whole --, then its
  sequence, its thread read once at `log`; `enter` opens its thread, its history read at `log` again
- the readings: `status --json`, then one `status <name> --json` per team started, `veille` never read; `u` reads again
- the guards: a verb found ended as its bound passes gives a face `verb-timeout`, never an exception; a reading of the
  tab that raises leaves the post standing -- `2` shows the agents -- and says the exception on the remedy line
"""
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
TEAMS = {"core-review": T.CORE, "ops": T.OPS}
TASKS = [(team, task) for team, face in TEAMS.items() for task in face["tasks"]]
T3 = next(task for task in T.CORE["tasks"] if task["id"] == "T3")
NEW = "team post core-review --message go"


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


NAMES = ("review PR 88", "review PR 87", "daily 2026-10-10", "rotate the certificates", "weekly report")
ROW = re.compile(r"(" + "|".join(re.escape(one) for one in NAMES) + r")\S*(?: \S+)*?\s+(core-review|ops)\s+"
                 r"(open|stopped|resolved)\b")


def moment(iso: str) -> str:
    """The moment a task was born as the post says it of another day (`palette.moment_of`): `DD/MM HH:MM` in local
    time -- the bench's own copy."""
    return f"{datetime.fromisoformat(iso).astimezone():%d/%m %H:%M}"


def _rows(text: str) -> list[str]:
    """-> the rows of the table of the tasks: a task's name, its team, its state."""
    return [found.group(0) for found in map(ROW.search, text.split("\n")) if found]






def _band(text: str) -> list[str]:
    """-> the rows of the band under the table: the centre's rows below its first edge, those with text."""
    centre = T.sides_of(text)[1]
    edge = next((n for n, one in enumerate(centre) if one.strip().startswith("─")), len(centre))
    return [one.strip() for one in centre[edge + 1:] if one.strip()]


def _progress(task: dict) -> str:
    """-> a task's delegations answered over its delegations, as the face carries them."""
    return f"{sum(1 for one in task['dos'] if one['answered'])}/{len(task['dos'])}"


def _for_you() -> set[tuple[str, str]]:
    """-> the tasks the owner has to see: a question waits on it, or its end is not seen yet."""
    return {(team, one["task"]) for team, face in TEAMS.items() for one in face["waiting"]["questions"]} | \
        {(team, task) for team, face in TEAMS.items() for task in face["waiting"]["done"]}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks")

    # --- the tasks of every team, the open ones by default; `u` reads again ----------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "150x40", "--press", "u")
    journal = house.journal_lines()
    text = done.stdout
    menu, centre = T.sides_of(text)
    rows = _rows(text)
    by_state = {state: sum(1 for _, one in TASKS if one["state"] == state) for state in ("open", "stopped", "resolved")}
    counts = [by_state["open"], by_state["open"], len(_for_you()), by_state["stopped"], by_state["resolved"], len(TASKS)]
    born = [name for _, one in sorted(TASKS, key=lambda pair: pair[1]["at"], reverse=True) if one["state"] == "open"
            for name in NAMES if name in (one.get("name") or one["text"])]
    menu_counts = [int(found.group(1)) for found in (re.search(r"(\d+)\s*$", one) for one in menu) if found]
    core = T.cells_of(next((one for one in centre if re.match(r"\s*T3\s", one)), ""))
    ops_task = T.OPS["tasks"][0]
    ops = T.cells_of(next((one for one in centre if re.match(rf"\s*{ops_task['id']}\s", one) and "ops" in one), ""))
    status, band = P.status_of(text), _band(text)
    if (done.returncode == 0 and len(rows) == by_state["open"] and menu_counts[:6] == counts
            and [name for row in rows for name in NAMES if name in row] == born
            and core[7:8] == [moment(T3["at"])] and ops[7:8] == [moment(ops_task["at"])]
            and core[:4] == ["T3", T3["name"], "core-review", T3["state"]]
            and set(re.findall(r"[\w-]+", core[4])) == set(T3["holders"]) and core[5] == _progress(T3)
            and len(ops) > 5 and ops[0] == ops_task["id"] and ops[1].startswith(ops_task["text"][:29])
            and len(ops[1]) == 30 and ops[1] != ops_task["text"] and ops[2:4] == ["ops", ops_task["state"]]
            and set(re.findall(r"[\w-]+", ops[4])) == set(ops_task["holders"]) and ops[5] == _progress(ops_task)
            and "veille" not in text and f"{by_state['open']}/{len(TASKS)}" in status):
        held("the tasks of every team, recent by default, the newest first", f"{len(rows)} of {len(TASKS)} rows "
             f"{born}: {core[:2]} born {core[7]}, {ops[:2]} cut at 30, progress {core[5]} and {ops[5]}; the menu counts "
             f"{counts}")
    else:
        failures.append(f"  ✗ every team                  rc={done.returncode} rows={rows} menu={menu_counts} {core} "
                        f"{ops} {status!r} {text[-2500:]!r} {done.stderr[-400:]!r}")

    # --- the readings: the teams started alone, `u` again (the first render) -----------------------------
    readings = [one for one in journal if one.startswith("status")]
    if (set(readings) == {"status", "status core-review", "status ops"} and readings.count("status") == 2
            and all(readings.count(f"status {team}") == 2 for team in TEAMS)):
        held("the readings: the teams started alone, u again", f"{sorted(set(readings))}; after u {len(readings)} "
             "readings")
    else:
        failures.append(f"  ✗ readings                    {journal}")

    # --- the cost of each task, a named task's text whole in the band (the first render) ------------------
    if (core[6:7] == [f"{T3['cost']:.2f}"] and not re.search(r"\d\.\d\d", ops[6] if len(ops) > 6 else "0.00")
            and any(T3["text"] in row for row in band) and any(f"{T3['cost']:.2f}" in row for row in band)):
        held("the cost of a task, a named task's text whole", f"T3 at {core[6]}, {ops_task['id']} of ops without one; "
             "the band says T3's text whole")
    else:
        failures.append(f"  ✗ cost and text               t3={core} ops={ops} {band}")

    # --- the band: the task whole, then its sequence (the first render); `enter` its thread ----------
    house.clear_journal()
    thread = house.render("--render", "tasks", "--size", "150x40", "--press", "enter")
    title, rows = P.title_of(thread.stdout), P.overlay_rows(thread.stdout)
    asked = next(one for one in T.T3_LOG if one.get("verb") == "ask")
    first = next(one for one in T.T3_LOG if one["event"] == "post")
    if (band and all(one in band[0] for one in ("T3", T3["state"], "core-review"))
            and any(all(one in row for one in T3["holders"]) for row in band[1:])
            and any(row.startswith(f"#{first['id']} {first['verb']} ") for row in band)
            and journal.count("log core-review T3") == 1 and house.journal_lines().count("log core-review T3") == 2
            and title and all(one in title[0] for one in ("core-review", "T3", T3["name"]))
            and any(f"#{asked['id']}" in row and asked["text"] in row for row in rows)
            and all(any(f"#{one['id']}" in row for row in rows) for one in T.T3_LOG)):
        held("the band: the task whole, then its sequence", f"{band[0]!r}, its holders; the row #{first['id']}; enter: "
             f"{title[0]!r}, #{T.T3_LOG[0]['id']} to #{T.T3_LOG[-1]['id']}, the question #{asked['id']} with its text")
    else:
        failures.append(f"  ✗ band                        {band} {house.journal_lines()} {title} {rows} "
                        f"{thread.stderr[-400:]!r}")

    # --- the filters -------------------------------------------------------------------------------
    every = [name for _, one in sorted(TASKS, key=lambda pair: pair[1]["at"], reverse=True)
             for name in NAMES if name in (one.get("name") or one["text"])]
    for keys, expected, what in (("shift+tab,shift+tab,down,down", {"review PR 88", "daily 2026-10-10", "weekly report"},
                                  "for you"),
                                 ("shift+tab,shift+tab,down,down,down,down,down", set(NAMES), "all"),
                                 ("shift+tab,down", {"review PR 88"}, "a team alone")):
        done = house.render("--render", "tasks", "--size", "150x36", "--press", keys)
        rows = _rows(done.stdout)
        found = {name for name in NAMES if any(name in one for one in rows)}
        ordered = what != "all" or [name for row in rows for name in NAMES if name in row] == every
        if done.returncode == 0 and found == expected and len(rows) == len(expected) and ordered:
            held(f"the filter {what}", f"--press {keys}: {sorted(found)}")
        else:
            failures.append(f"  ✗ filter {what:<20} rc={done.returncode} {sorted(found)} {rows} "
                            f"{done.stdout[-1500:]!r} {done.stderr[-300:]!r}")

    # --- recent: the open tasks, and those ended within the day ------------------------------------------
    day = 86400
    core = {**T.CORE, "tasks": [{**one, **dated} for one, dated in zip(T.CORE["tasks"], (
        {"at": T.ago(3 * day + 60), "ended": T.ago(3 * day)},              # T1 stopped three days ago
        {"at": T.ago(2 * day + 3600), "ended": T.ago(2 * day)},            # T2 resolved two days ago
        {"at": T.ago(3 * day), "ended": None}))]}                         # T3 open for three days
    ops = {**T.OPS, "tasks": [{**T.OPS["tasks"][0], "at": T.ago(3600), "ended": None},
                              {**T.OPS["tasks"][1], "at": T.ago(11 * 3600), "ended": T.ago(10 * 3600)}]}
    house.use(T.script(states={"core-review": [core], "ops": [ops]}))
    done = house.render("--render", "tasks", "--size", "150x36")
    rows = [name for row in _rows(done.stdout) for name in NAMES if name in row]
    kept = ["rotate the certificates", "weekly report", "review PR 88"]
    if done.returncode == 0 and rows == kept:
        held("recent keeps the open tasks and those ended within the day", f"{rows}: T3 open for three days, ops' T2 "
             "resolved ten hours ago; T2 resolved two days ago and T1 stopped three days ago left out")
    else:
        failures.append(f"  ✗ recent                      rc={done.returncode} {rows} {done.stdout[-1500:]!r} "
                        f"{done.stderr[-300:]!r}")
    house.use(T.script())

    # --- the task launched follows ---------------------------------------------------------------------------
    born = {**T.T4, "at": T.ago(30), "ended": None}
    after = {**T.CORE, "tasks": T.CORE["tasks"] + [born]}
    resolved = {**T.CORE, "tasks": T.CORE["tasks"] + [{**born, "state": "resolved", "holders": [], "ended": T.ago(5)}]}
    house.use(T.script(states={"core-review": [T.CORE, after, resolved], "ops": [T.OPS]},
                       watch={"core-review": [{"sleep": 5.0}, T.event("09:14:00", "done", 49, task="T4")]}))
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "150x40", "--press",
                        "shift+tab,shift+tab,down,down,down,down,n,g,o,enter", "--wait", "team:done")
    lines = [one.strip() for one in T.sides_of(done.stdout)[1] if one.strip()]
    first = next((one for one in lines if re.match(r"T\d\s", one)), "")
    band = next((one for one in lines if one.startswith(f"T4{P.palette_constant('SEP')}")), "")
    status = P.status_of(done.stdout)
    if (done.returncode == 0 and house.gestures() == [NEW] and first.startswith("T4")
            and "resolved" in band and "show recent" in status):
        held("the task launched follows", f"{'./pp ' + NEW!r} under resolved: T4 first and under the cursor, "
             f"{band[:30]!r} once the team resolved it; the status says {status.split(' · ')[1:3]}")
    else:
        failures.append(f"  ✗ launched follows            rc={done.returncode} {house.gestures()} {first!r} {band!r} "
                        f"{status!r} {done.stdout[-1800:]!r} {done.stderr[-400:]!r}")
    house.use(T.script())

    # --- the guards: a verb ended at its bound, a reading that raises ------------------------------------
    face, raised = ended_at_its_bound(str(house.ws))
    if face is not None and face.rc == -1 and "verb-timeout" in face.err and not raised:
        held("a verb ended at its bound gives a face", f"rc {face.rc}, `verb-timeout` on its err, nothing raised")
    else:
        failures.append(f"  ✗ verb at its bound           {face!r} raised={raised!r}")
    (house.faces / "team").chmod(0o644)        # the console of `team` cannot be played: the reading raises
    broken = house.render("--render", "tasks", "--size", "150x40", "--press", "2")
    remedy = P.remedy_of(broken.stdout)
    if broken.returncode == 0 and "PermissionError" in remedy and "agents/reviewer" in broken.stdout:
        held("a reading that raises leaves the post standing", f"the remedy says {remedy.split(' [')[0]!r}; `2` shows "
             "the agents")
    else:
        failures.append(f"  ✗ reading guarded             rc={broken.returncode} {remedy!r} {broken.stdout[-1200:]!r} "
                        f"{broken.stderr[-600:]!r}")
    (house.faces / "team").chmod(0o755)
    return 0
