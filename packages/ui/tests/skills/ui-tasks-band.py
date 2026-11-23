"""Scenario `ui-tasks-band` -- the band of a task on the Tasks tab in three zones under the table (batch
la-zone-tache-en-sous-zones), on the bench's `pp-team` witness:
- the table shows ten tasks at most: thirty-two tasks under `all` at 130x60, ten rows of tasks in sight
- the summary, unframed, holds five lines at most; its `dos` line counts the `do`s answered over every `do` (`10/12`),
  then names the two left, on ONE line -- cut by `…` on a narrow screen, never wrapped
- the text of the task in its own frame `text`, its markdown drawn -- no `**`, no `#` --, six rows inside the frame at
  130x40, four at 130x28 (the screen's `-short`); a task without a text has no such frame
- the frame below says what it shows: `sequence` on a task open, `result` on a task resolved, `sequence` after `v`
The frames that expand have their own scenarios, `ui-tasks-band-sequence`, `-text` and `-list` (`_tasks_band`).
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
B = support(__file__, "tasks_band")
WIDE, SHORT, NARROW, TALL, EVERY, RESOLVED = B.WIDE, B.SHORT, B.NARROW, B.TALL, B.EVERY, B.RESOLVED
ID_ROW, regions_of, rows_in, titles_of = B.ID_ROW, B.regions_of, B.rows_in, B.titles_of


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-band", T.script(states={"core-review": [T.crowded(30)], "ops": [T.OPS]}))

    # --- the table shows ten tasks at most ----------------------------------------------------------------------
    done = house.render("--render", "tasks", *TALL, "--press", EVERY)
    rows = [one for one in T.sides_of(done.stdout)[1] if ID_ROW.match(one.strip(" │"))]
    if done.returncode == 0 and len(rows) == 10:
        held("the table shows ten tasks at most", f"32 tasks under all at 130x60: {len(rows)} rows in sight")
    else:
        failures.append(f"  ✗ ten rows                    rc={done.returncode} {len(rows)} rows {done.stdout[-2400:]!r} "
                        f"{done.stderr[-400:]!r}")

    # --- the summary: five lines at most, `dos` on one line, cut by `…` --------------------------------------------
    house.use(T.script(states={"core-review": [T.CORE_BAND], "ops": [T.OPS]}))
    wide, shapes = (house.render("--render", "tasks", *WIDE, *extra) for extra in ((), ("--regions",)))
    places = regions_of(shapes.stdout)
    summary = rows_in(wide.stdout, places["tasks-detail"]) if "tasks-detail" in places else []
    dos = [one for one in summary if "10/12" in one]
    narrow = [one.strip(" │") for one in T.sides_of(house.render("--render", "tasks", *NARROW).stdout)[1]]
    at = next((n for n, one in enumerate(narrow) if "10/12" in one), None)
    cut_dos = narrow[at:at + 1] if at is not None else []         # the line of the dos
    if (wide.returncode == 0 and 0 < places.get("tasks-detail", (0, 0, 0, 99))[3] <= 5
            and len(dos) == 1 and all(one in dos[0] for one in T.LATE) and not any("dev3" in one for one in dos)
            and len(cut_dos) == 1 and cut_dos[0].endswith("…")):
        held("the summary in five lines, dos on one line", f"{places['tasks-detail'][3]} lines; "
             f"{dos[0].strip()!r}; at 80 columns {cut_dos[0].strip()!r}")
    else:
        failures.append(f"  ✗ summary                     rc={wide.returncode} {places.get('tasks-detail')} {summary} "
                        f"{cut_dos} {wide.stdout[-2400:]!r} {wide.stderr[-400:]!r}")

    # --- the text in its own frame: its markdown drawn, six rows -- four under 30 --, none without a text ----------
    low = regions_of(house.render("--render", "tasks", *SHORT, "--regions").stdout)
    text = rows_in(wide.stdout, places["tasks-text"]) if "tasks-text" in places else []
    house.use(T.script(states={"core-review": [T.CORE_NEXT], "ops": [T.OPS]}))      # T4, born last, says no text
    bare = regions_of(house.render("--render", "tasks", *WIDE, "--regions").stdout)
    inside = (places.get("tasks-text", (0, 0, 0, 0))[3] - 2, low.get("tasks-text", (0, 0, 0, 0))[3] - 1)  # round, top
    if (inside == (6, 4) and any("Release 2.4" in one for one in text) and not any("**" in one for one in text)
            and not any(one.strip(" │╭╮").startswith("#") for one in text) and "text" in titles_of(wide.stdout)
            and "tasks-text" not in bare and "tasks-sequence" in bare):
        held("the text in its frame, its markdown drawn", f"{inside[0]} rows at 130x40, {inside[1]} at 130x28; "
             f"T4 without a text: no frame, the band {sorted(one for one in bare if one.startswith('tasks-'))}")
    else:
        failures.append(f"  ✗ text frame                  {inside} {text} {titles_of(wide.stdout)} {sorted(bare)}")

    # --- the frame below says what it shows ---------------------------------------------------------------------
    house.use(T.script())
    opened = titles_of(wide.stdout)
    resolved, toggled = (titles_of(house.render("--render", "tasks", *WIDE, "--press", keys).stdout)
                         for keys in (RESOLVED, RESOLVED + ",v"))
    if opened[-1:] == ["sequence"] and resolved[-1:] == ["result"] and toggled[-1:] == ["sequence"]:
        held("the frame below says what it shows", f"T7 open: {opened}; ops' T2 resolved: {resolved}; v: {toggled}")
    else:
        failures.append(f"  ✗ bottom title                {opened} {resolved} {toggled}")

    return 0
