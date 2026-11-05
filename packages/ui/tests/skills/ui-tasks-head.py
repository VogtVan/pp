"""Scenario `ui-tasks-head` -- the HEAD of a sequence stays in sight (batch la-sequence-vivante), on the bench's `pp-team`
witness: T3's thread holds sixty posts among six participants, taller and wider than the band at 120x40:
- the head stays: `tab,home` and `tab,end` both show the names of the columns and the last row is in sight at `end`
- the head follows the scroll: `right` ten times moves the names by the same cells as the rows
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

MEMBERS = ["lead", "reviewer", "dev1", "dev2", "dev3", "dev4"]
SIZE = ("--size", "120x40")


def big_log() -> list[dict]:
    """-> T3's thread: its birth, then sixty posts of `lead` to each member in turn."""
    found = [T.T3_LOG[0]]
    for n in range(60):
        found.append(T.event(f"09:{(n + 2) // 60:02d}:{(n + 2) % 60:02d}", "post", 42 + n, task="T3", **{"from": "lead"},
                             to=MEMBERS[1 + n % 5], verb="do", text=f"part {n + 1} of the review"))
    return found


def names_row(text: str, names: tuple = tuple(MEMBERS[:4])) -> str:
    """-> the row of the capture that names the columns of the sequence -- those of `names` in sight: the first four
    at 120 columns, the last ones past the view --, '' without one."""
    return next((one for one in text.split("\n") if all(name in one for name in names)), "")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    log = big_log()
    script = T.script(log={"core-review": T.TEAM_LOG, "core-review/T3": log, "core-review/T2": T.T2_LOG})
    house = T.Teams(bench, "ui-tasks-head", script)

    # --- the head stays --------------------------------------------------------------------------------------
    top = house.render("--render", "tasks", *SIZE, "--press", "tab,home")
    bottom = house.render("--render", "tasks", *SIZE, "--press", "tab,end")
    first, last = f"#{log[1]['id']} ", f"#{log[-1]['id']} "
    if (top.returncode == 0 and bottom.returncode == 0 and names_row(top.stdout) and names_row(bottom.stdout)
            and first in top.stdout and last not in top.stdout and last in bottom.stdout and first not in bottom.stdout):
        held("the head stays", f"the names in sight at home ({first.strip()} shown) and at end ({last.strip()} shown)")
    else:
        failures.append(f"  ✗ head stays                  rc={top.returncode}/{bottom.returncode} "
                        f"top={names_row(top.stdout)!r} bottom={names_row(bottom.stdout)!r} "
                        f"{bottom.stdout[-1800:]!r} {bottom.stderr[-300:]!r}")

    # --- the head follows the scroll --------------------------------------------------------------------------
    moved = house.render("--render", "tasks", *SIZE, "--press", "tab,end," + ",".join(["right"] * 10))
    before, after = names_row(bottom.stdout), names_row(moved.stdout, tuple(MEMBERS[2:]))
    name = MEMBERS[3]                                              # dev2 in sight before and after
    shift = before.index(name) - after.index(name) if name in before and name in after else None
    texts = [sum(1 for one in text.split("\n") if "part " in one) for text in (bottom.stdout, moved.stdout)]
    if (moved.returncode == 0 and shift and shift > 0 and MEMBERS[0] in before and MEMBERS[0] not in after
            and MEMBERS[-1] not in before and MEMBERS[-1] in after and texts[0] < texts[1]):
        held("the head follows the scroll", f"ten `right`: the names moved {shift} cells -- {MEMBERS[0]} out, "
             f"{MEMBERS[-1]} in -- and the rows' texts came into sight ({texts[0]} row(s) before, {texts[1]} after)")
    else:
        failures.append(f"  ✗ head follows                rc={moved.returncode} shift={shift} before={before!r} "
                        f"after={after!r} {moved.stdout[-1500:]!r}")
    return 0
