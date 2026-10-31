"""Scenario `ui-tasks-result` -- the band of a task resolved on the Tasks tab, on the bench's `pp-team` witness:
- its result in markdown, whole, and no sequence -- `team result` read once though the cursor comes back to it
- `tab` goes into its frame and `pagedown` scrolls it: the result is taller than the band
- `v` shows its sequence, `v` again its result
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

RESOLVED = "shift+tab,shift+tab,down,down,down,down,tab,tab,down"   # SHOW `resolved`, the cursor on ops' T2


def inner_of(text: str) -> set[str]:
    """-> the parts of the band a `--regions` capture says shown."""
    return {one.split()[1] for one in text.split("\n") if one.startswith("inner ")}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-result")

    # --- a task resolved: its result whole, its frame scrolled, `v` its sequence and back ------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "150x40", "--press", RESOLVED + ",up,down")
    reads = [one for one in house.journal_lines() if one == "result ops T2"]
    regions = inner_of(house.render("--render", "tasks", "--size", "150x40", "--press", RESOLVED, "--regions").stdout)
    if (done.returncode == 0 and "Weekly report" in done.stdout and len(reads) == 1 and "tasks-result" in regions
            and "tasks-sequence" not in regions):
        held("a task resolved shows its result in markdown, no sequence", f"`result ops T2` read {len(reads)} time; "
             f"the band shows {sorted(regions)}")
    else:
        failures.append(f"  ✗ result                      rc={done.returncode} reads={reads} {sorted(regions)} "
                        f"{done.stdout[-1800:]!r} {done.stderr[-400:]!r}")
    scrolled = house.render("--render", "tasks", "--size", "150x40", "--press", RESOLVED + ",tab,pagedown")
    if scrolled.returncode == 0 and "Weekly report" not in scrolled.stdout and "check " in scrolled.stdout:
        held("the result scrolls in its frame", "tab, pagedown: its title out of sight, its rows below in view")
    else:
        failures.append(f"  ✗ result scrolled             rc={scrolled.returncode} {scrolled.stdout[-1800:]!r}")
    toggled = [inner_of(house.render("--render", "tasks", "--size", "150x40", "--press", RESOLVED + keys,
                                     "--regions").stdout) for keys in (",v", ",v,v")]
    if ("tasks-sequence" in toggled[0] and "tasks-result" not in toggled[0] and "tasks-result" in toggled[1]
            and "tasks-sequence" not in toggled[1]):
        held("v changes the result for the sequence, and back", f"v: {sorted(toggled[0])}; v, v: {sorted(toggled[1])}")
    else:
        failures.append(f"  ✗ v                           {toggled}")
    return 0
