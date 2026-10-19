"""Scenario `ui-team-ceremonies` -- the ceremonies of a team read in their overlay, rung at hand from it, and a
ceremony leading to its task, on the bench's `pp-team` witness replaying `CEREMONIAL`: `daily` rung and closed (T2),
`retro` after it under `any 2` rung and open (one participant of three has answered, its task T5 carries the
facilitator's wait), `review` never rung:
- `c` on the Teams tab: the table of the ceremonies counts the progress of each last ring on the face's `progress`,
  the quorum beside it, nothing before any ring
- the detail of `retro` says what it follows, who takes part and who facilitates, its last ring, its progress with
  the participants still waited for, and the wait the task of its last ring carries
- `g` opens the ceremonies, the command of the ring of the one under the cursor shown under them; `g` again plays it
  word for word, the team read again after it; `escape` closes them and plays nothing
- the `as` chosen in the overlay rides the ring: `--as pm`; the owner writes none
- `enter` on a ceremony: the Tasks tab shown, every task of the team, the band of the task of its last ring and that
  task's last event; on a ceremony never rung the overlay stays, one row more naming it
- a refusal of the verb -- `ceremony-open` -- goes to the remedy line as the verb said it
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the readers of a capture and of the palette's source

SIZE = ("--size", "130x40")
TEAM = T.CEREMONIAL["team"]
DAILY, RETRO, REVIEW = T.CEREMONIAL["ceremonies"]
RING = f"./pp team ring {TEAM} "
AS_PM = "c,tab,space,down,enter"
PM = T.CEREMONIAL["principals"][0]
OPEN = ("pp-team: ceremony-open -- T5 of `retro` is open: one ring at a time, ring again once it is resolved "
        "or stopped.\n")


def _rows(done) -> list[str]:
    """-> the rows inside the overlay of a render, blank ones kept."""
    return P.overlay_rows(done.stdout)


def _table(rows: list[str]) -> dict[str, list[str]]:
    """-> the cells of the table of the ceremonies, by the ceremony each row names first."""
    names = {one["name"] for one in T.CEREMONIAL["ceremonies"]}
    return {cells[0]: cells for cells in map(T.cells_of, rows) if cells and cells[0] in names}


def _detail(rows: list[str]) -> list[str]:
    """-> the block of rows under the table: from the first row of text after its last row to the next blank one."""
    last = max((n for n, row in enumerate(rows) if T.cells_of(row)[:1] == [REVIEW["name"]]), default=None)
    if last is None:
        return []
    block: list[str] = []
    for row in rows[last + 1:]:
        if not row and block:
            break
        if row:
            block.append(row)
    return block


def _active(done) -> str:
    """-> the tab the bar under the tabs marks: the word of the tabs' row over the bar's `╸…╺` segment."""
    lines = done.stdout.split("\n")
    if len(lines) < 3 or "╸" not in lines[2] or "╺" not in lines[2]:
        return ""
    return lines[1][lines[2].index("╸") + 1:lines[2].index("╺")].strip()


def _tabs(done) -> list[str]:
    lines = done.stdout.split("\n")
    return lines[1].split() if len(lines) > 1 else []


def _progress(ceremony: dict) -> list[str]:
    """-> what the face's `progress` counts of a ring: the participants answered of all of them, the quorum."""
    said = ceremony["progress"]
    return [f"{sum(1 for one in said if one['answered'])}/{len(said)}"] + \
        ([str(ceremony["quorum"])] if ceremony["quorum"] is not None else [])


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    states = {"core-review": [T.CEREMONIAL], "veille": [{"team": "veille", "started": None}]}
    house = T.Teams(bench, "ui-team-ceremonies", T.script(states=states))
    none = P.palette_constant("NONE")

    # --- the progress column ------------------------------------------------------------------------
    done = house.render("--render", "teams", "--size", "200x50", "--press", "c")
    table = _table(_rows(done))
    counted = {one["name"]: T.in_order(" ".join(table.get(one["name"], [])[1:2]), *_progress(one))
               for one in (DAILY, RETRO)}
    if (done.returncode == 0 and all(counted.values()) and table.get(REVIEW["name"], [])[1:2] == [none]
            and TEAM in " ".join(P.title_of(done.stdout))):
        held("the progress of each last ring", "; ".join(f"{name} {' any '.join(_progress(one))}" for name, one in
                                                         ((DAILY["name"], DAILY), (RETRO["name"], RETRO)))
             + f"; {REVIEW['name']} {none}")
    else:
        failures.append(f"  ✗ progress column             rc={done.returncode} {counted} {table} {done.stdout[-2400:]!r} "
                        f"{done.stderr[-300:]!r}")

    # --- the detail of retro: what it follows, its ring, its progress, the wait of its task ---------
    done = house.render("--render", "teams", "--size", "160x44", "--press", "c,down")
    detail = _detail(_rows(done))
    task = next(one for one in T.CEREMONIAL["tasks"] if one["id"] == RETRO["last"]["task"])
    wait = task["waits"][0]
    waited = [one["member"] for one in RETRO["progress"] if not one["answered"]]
    found = {
        "head": bool(detail) and T.in_order(detail[0], RETRO["name"], RETRO["after"]),
        "after": any(T.in_order(row, RETRO["after"]) for row in detail[1:]),
        "with": any(T.in_order(row, *RETRO["participants"], RETRO["facilitator"]) for row in detail),
        "last": any(T.in_order(row, *(RETRO["last"][key] for key in ("period", "task", "state"))) for row in detail),
        "progress": any(T.in_order(row, *_progress(RETRO), *waited) for row in detail),
        "wait": any(T.in_order(row, wait["member"], str(wait["any"])) for row in detail)}
    if done.returncode == 0 and all(found.values()):
        held("the detail of retro", f"after {RETRO['after']}; {', '.join(RETRO['participants'])} → "
             f"{RETRO['facilitator']}; last ring {RETRO['last']['task']}; waits {', '.join(waited)}; "
             f"{wait['member']} any {wait['any']} on {task['id']}")
    else:
        failures.append(f"  ✗ detail retro                rc={done.returncode} {found} {detail!r} {done.stdout[-1800:]!r} "
                        f"{done.stderr[-300:]!r}")

    # --- g: shown, then played; escape plays nothing ------------------------------------------------
    shown = house.render("--render", "teams", *SIZE, "--press", "g,down")
    preview = T.preview_in(shown, "./pp team ring")
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", "g,escape,g,down,g")
    played, journal = house.gestures(), house.journal_lines()
    reread = bool(played) and f"status {TEAM}" in journal[journal.index(played[0]) + 1:]
    if (shown.returncode == 0 and done.returncode == 0 and preview == RING + RETRO["name"]
            and played == [preview[len("./pp "):]] and reread):
        held("g rings the ceremony under the cursor", f"{preview!r} shown, played as shown, the team read again; "
             "escape before it played nothing")
    else:
        failures.append(f"  ✗ ring                        rc={shown.returncode},{done.returncode} {preview!r} {played} "
                        f"{journal} {shown.stdout[-1200:]!r} {done.stderr[-300:]!r}")

    # --- the as of the line ---------------------------------------------------------------------------
    shown = house.render("--render", "teams", *SIZE, "--press", AS_PM)
    preview = T.preview_in(shown, "./pp team ring")
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", AS_PM + ",g")
    played = house.gestures()
    if (shown.returncode == 0 and done.returncode == 0 and preview == f"{RING}{DAILY['name']} --as {PM}"
            and played == [preview[len("./pp "):]]):
        held("the as chosen rides the ring", preview)
    else:
        failures.append(f"  ✗ as pm                       rc={shown.returncode},{done.returncode} {preview!r} {played} "
                        f"{shown.stdout[-1200:]!r}")

    # --- enter: from a ceremony to its task ----------------------------------------------------------
    done = house.render("--render", "teams", *SIZE, "--press", "c,enter")
    _, centre = T.sides_of(done.stdout)
    task = next(one for one in T.CEREMONIAL["tasks"] if one["id"] == DAILY["last"]["task"])
    listed = [one["id"] for one in T.CEREMONIAL["tasks"]
              if any(T.cells_of(row)[:1] == [one["id"]] and TEAM in T.cells_of(row) for row in centre)]
    # the band's head says the task, its state, then its team -- the table's row says the team before the state
    band = any(T.in_order(row, task["id"], task["state"], TEAM) for row in centre)
    last = any(T.in_order(row, f"#{task['last']['id']}", task["last"]["kind"]) for row in centre)
    tabs = _tabs(done)
    if (done.returncode == 0 and len(tabs) > 3 and _active(done) == tabs[3]
            and listed == [one["id"] for one in T.CEREMONIAL["tasks"]] and band and last and not house.alive()):
        held("enter leads a ceremony to its task", f"{DAILY['name']}: the Tasks tab, {', '.join(listed)} listed, the band "
             f"of {task['id']} and its last event (#{task['last']['id']} {task['last']['kind']})")
    else:
        failures.append(f"  ✗ enter daily                 rc={done.returncode} active={_active(done)!r} {listed} "
                        f"band={band} last={last} {done.stdout[-1400:]!r} {done.stderr[-300:]!r}")

    before = house.render("--render", "teams", *SIZE, "--press", "c,down,down")
    done = house.render("--render", "teams", *SIZE, "--press", "c,down,down,enter")
    rows, kept = [one for one in _rows(done) if one], [one for one in _rows(before) if one]
    more = [one for one in rows if one not in kept]
    tabs = _tabs(done)
    if (before.returncode == 0 and done.returncode == 0 and all(one in rows for one in kept) and len(more) == 1
            and REVIEW["name"] in more[0].split() and len(tabs) > 2 and _active(done) == tabs[2]):
        held("a ceremony never rung says so", f"the overlay kept, one row more naming {REVIEW['name']}")
    else:
        failures.append(f"  ✗ enter review                rc={before.returncode},{done.returncode} {more!r} "
                        f"active={_active(done)!r} {done.stdout[-900:]!r}")

    # --- a refusal on the remedy line ----------------------------------------------------------------
    house.use(T.script(states=states, answers={"ring": {"rc": 2, "err": OPEN}}))
    done = house.render("--render", "teams", *SIZE, "--press", "c,down,g")
    remedy = T.remedy_of(done)
    code, said = OPEN.split(": ", 1)[1].split(" -- ", 1)
    if done.returncode == 0 and code in remedy.split() and " ".join(said.split()[:5]) in remedy:
        held("a refusal goes to the remedy line as said", remedy[:100])
    else:
        failures.append(f"  ✗ refused                     rc={done.returncode} {remedy!r} {done.stdout[-900:]!r}")
    return 0
