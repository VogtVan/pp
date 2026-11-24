"""Scenario `ui-tasks-sequence-live` -- the SEQUENCE of the task under the cursor on the Tasks tab, followed live, on
ONE house of the bench's `pp-team` witness (`_tasks_sequence`) whose script changes by `use()`:
- the sequence followed live: `core-review`'s watch saying a post, a step of `lead`, a step of `reviewer`, then the end
  of `lead`'s wake-up -- the post's row added after the others, the pile of procs of `reviewer` under its name, `lead`'s
  gone with its wake-up; `tab` goes into the sequence, its cursor on the last row, `up` one row above
- the band keeps its place: the detail and the sequence where they stood before a post came, as `--regions` says
- the footer says the keys of where the focus stands: the sequence's (`w`) once it is focused (none of them before:
  `ui-tasks-sequence`)
"""
from __future__ import annotations

from tests.harness import support

S = support(__file__, "tasks_sequence")
T, P = S.T, S.P
SIZE = ("--size", "170x41")   # every row in sight under a head of five lines, the table of the tasks without a scroll bar


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = S.house(bench, "ui-tasks-sequence-live")
    posts = [one for one in T.T3_LOG if one["event"] == "post"]
    at_rest = house.render("--render", "tasks", *SIZE, "--regions").stdout

    # --- the sequence followed live: a post added, the piles of the members, the cursor -------------------------
    watched = [{"sleep": 0.8}, T.WRITTEN] + T.TWO_WATCH    # #46 once the thread is read: added live
    script = T.script(watch={"core-review": watched})
    script["states"]["core-review"] = [T.LIVE_CORE]
    house.use(script)
    done = moved = house.render("--render", "tasks", *SIZE, "--wait", "team:wake-ended:3", "--press", "tab,up")
    heads = S.heads_of(done.stdout)
    edge = T.edge_of(moved.stdout) or 0
    cursor = next((one[edge:].lstrip(" ") for one in moved.stdout.split("\n")
                   if one[edge:].lstrip(" ").startswith(S.CURSOR)), "")
    ids = sorted(one["id"] for one in posts + [T.WRITTEN])
    frame = {one["agent"]: one["stack"].split("▸")[-1].strip() for one in (T.STEP, T.LEAD_STEP)}
    if (done.returncode == 0 and heads == ids and frame["reviewer"] in done.stdout
            and frame["lead"] not in done.stdout and cursor.startswith(f"{S.CURSOR}#{T.WRITTEN['id']} ")):
        held("the sequence followed live", f"rows {heads}: #{T.WRITTEN['id']} in its place; reviewer's pile drawn, "
             f"lead's gone with its wake-up; tab, up: the cursor on {cursor.split()[0]!r}")
    else:
        failures.append(f"  ✗ live sequence               rc={done.returncode} {heads} {cursor!r} "
                        f"{done.stdout[-2400:]!r} {moved.stdout[-1200:]!r} {done.stderr[-400:]!r}")
    grown = house.render("--render", "tasks", *SIZE, "--wait", "team:wake-ended:3", "--regions").stdout
    before, after = S.placed(at_rest, "tasks-detail", "tasks-sequence"), S.placed(grown, "tasks-detail", "tasks-sequence")
    if before and len(before) == 2 and before == after:
        held("the band keeps its place as the sequence grows", f"{after} before and after #{T.WRITTEN['id']} came")
    else:
        failures.append(f"  ✗ band in place               {before} {after}")
    keys = P.keys_of(moved.stdout)
    if "[w]" in keys:
        held("the footer says the keys of the sequence once it is focused", "`w` there in the sequence")
    else:
        failures.append(f"  ✗ keys of the sequence        {keys!r}")

    return 0
