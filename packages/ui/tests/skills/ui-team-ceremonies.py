"""Scenario `ui-team-ceremonies` -- the ceremonies of a team read in their overlay, `c` on the Teams tab (plan
ui, batches les-ceremonies-au-poste and les-deux-onglets), on the bench's `pp-team` witness replaying `CEREMONIAL`: `daily` rung and closed,
`retro` after it under `any 2` rung and open (one participant of three has answered, its task T5 carries the
facilitator's wait), `review` never rung:
- the table of the ceremonies says the progress of each last ring, counted on the face's `progress`: `1/1`,
  `1/3 any 2`, `—` before any ring -- at 200x50, and the frame holds at 80x24
- the detail of a ceremony says its chain (`then retro` on `daily`, `after daily` on `retro`), its progress
  with the participants still waited for, and the wait the task of its last ring carries, as `waits` says it
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")


def _flat(text: str) -> str:
    return " ".join(text.split())


def _row(text: str, name: str) -> str:
    """-> the line of the Ceremonies table that names the ceremony."""
    return next((line for line in text.split("\n") if f" {name} " in line and ("/" in line or "—" in line)), "")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    script = T.script(states={"core-review": [T.CEREMONIAL], "veille": [{"team": "veille", "started": None}]})
    house = T.Teams(bench, "ui-team-ceremonies", script)

    # --- the progress column ------------------------------------------------------------------------
    done = house.render("--render", "teams", "--size", "200x50", "--press", "c")
    rows = {name: _row(done.stdout, name) for name in ("daily", "retro", "review")}
    if (done.returncode == 0 and "progress" in done.stdout and "1/1" in rows["daily"]
            and "1/3 any 2" in rows["retro"] and "—" in rows["review"] and "/" not in rows["review"].split("review", 1)[1][:12]):
        held("the progress of each last ring", f"daily {'1/1'}, retro {'1/3 any 2'}, review — (never rung)")
    else:
        failures.append(f"  ✗ progress column             rc={done.returncode} {rows} {done.stdout[-2400:]!r} "
                        f"{done.stderr[-300:]!r}")
    small = house.render("--render", "teams", "--size", "80x24", "--press", "c")
    lines = small.stdout.rstrip("\n").split("\n")
    if (small.returncode == 0 and len(lines) == 24 and max(len(one) for one in lines) <= 80
            and "ceremonies of core-review" in small.stdout):
        held("the frame holds at 80x24", "24 lines of 80 columns at most, the overlay of the ceremonies titled")
    else:
        failures.append(f"  ✗ frame 80x24                 rc={small.returncode} lines={len(lines)} {small.stdout!r}")

    # --- the detail: the chain, the progress, the wait ----------------------------------------------
    for keys, said, absent, what in (
            ("c", ("daily · every weekday 09:30", "chain then retro", "progress 1/1",
                             "wait lead any 1 · met"), (), "daily"),
            ("c,down", ("retro · after daily", "chain after daily", "quorum any 2",
                                  "progress 1/3 any 2 · waits scribe, dev2", "wait lead any 2 · open",
                                  "2026-10-10 · T5 · open"), (), "retro"),
            ("c,down,down", ("review · every mon 10:00", "chain —", "progress —"), ("wait lead",), "review")):
        done = house.render("--render", "teams", "--size", "160x44", "--press", keys)
        flat = _flat(done.stdout)
        if done.returncode == 0 and all(one in flat for one in said) and not any(one in flat for one in absent):
            held(f"the detail of {what}", "; ".join(said))
        else:
            failures.append(f"  ✗ detail {what:<20} rc={done.returncode} {said} {[one for one in said if one not in flat]} "
                            f"{done.stdout[-1800:]!r} {done.stderr[-300:]!r}")
    return 0
