"""Scenario `ui-tasks-activity` -- the ACTIVITY of a member in the sequence of its task (batch la-sequence-vivante), on
the bench's `pp-team` witness replaying the team's watch, no task running so that the post rests between two objects:
- the live line of a member moves between two blocks: the watch saying a block, a call of a tool, its result, a thought,
  then a block makes the line under `reviewer`'s name change five times (the render's word `live`): the block's frame,
  then the gesture on it, then the next block alone
- the context is beside the member: a `context` object of the watch puts `ctx 17%` beside `reviewer`'s name
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "teams")


def line_of(text: str, mark: str) -> str:
    return next((one for one in text.split("\n") if mark in one), "")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-activity", T.script(watch={"core-review": T.LIVE_WATCH}))

    # --- the live line moves between two blocks -------------------------------------------------------
    done = house.render("--render", "tasks", "--size", "150x40", "--press",
                        "wait:team:block,live,wait:team:activity,live,wait:team:activity,live,wait:team:activity,live,"
                        "wait:team:block,live")
    noted = next((one[5:] for one in reversed(done.stdout.split("\n")) if one.startswith("live ")), "")
    lines = [one.strip() for one in noted.split(" | ")]
    frames = [T.STEP["stack"].split("▸")[-1].strip(), T.STEP_LAST["stack"].split("▸")[-1].strip()]
    if (done.returncode == 0 and len(lines) == 5 and len(set(lines)) == 5
            and all(one.startswith("reviewer=") for one in lines)
            and frames[0] in lines[0] and T.ACT_TOOL["name"] in lines[1] and T.ACT_TOOL["title"] in lines[1]
            and "chars" in lines[2] and T.ACT_THOUGHT["text"].split()[0] in lines[3] and frames[1] in lines[4]
            and frames[0] not in lines[4] and T.ACT_TOOL["name"] not in lines[4]):
        held("the live line moves between two blocks", f"five distinct lines: {lines}")
    else:
        failures.append(f"  ✗ live line                   rc={done.returncode} {lines!r} {done.stdout[-1500:]!r} "
                        f"{done.stderr[-400:]!r}")

    # --- the context beside the member --------------------------------------------------------------
    house.use(T.script(watch={"core-review": [{"sleep": 0.3}, T.ACT_CONTEXT, T.STEP]}))
    done = house.render("--render", "tasks", "--size", "160x40", "--wait", "team:block")
    head = line_of(done.stdout, "reviewer ctx")
    if done.returncode == 0 and re.search(r"reviewer ctx 17%", head):
        held("the context is beside the member", f"{head.strip()[:60]!r}")
    else:
        failures.append(f"  ✗ context beside the member   rc={done.returncode} {head!r} {done.stdout[-1500:]!r}")
    return 0
