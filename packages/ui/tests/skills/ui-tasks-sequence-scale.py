"""Scenario `ui-tasks-sequence-scale` -- the TIME SCALE of a task's sequence (batch l-echelle-de-temps, s.1516): each
dated row says, beside its head, the local hour of its event `hh:mm`, then in parentheses the delay since the task was
born `(hh:mm:ss)`, the hours cumulated past a day; on ONE house of the bench's `pp-team` witness (`_tasks_sequence`):
- the band of T3 on the Tasks tab: #42, #44 and #45 say the scale `palette.scale_of` gives their dates, the delay read
  by its fields 0, 60 and 240 seconds after the task's birth
- four rows dated start+42s, start+4m30, start+1h05 and start+26h03, drawn by `palette.sequence_text` in a Textual
  subprocess, say in their gutter what `palette.scale_of` says of their dates -- the column read under the frame
  (`sequence_frame`), never a text copied: each opens on its event's local hour, its delay read by its fields
"""
from __future__ import annotations

from datetime import datetime, timedelta

from tests.harness import support

S = support(__file__, "tasks_sequence")
T = S.T

DELAYS = (42, 270, 3900, 93780)    # start+42s, start+4m30, start+1h05, start+26h03: the hours cumulated past a day
START = "2026-11-07T10:00:00+00:00"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = S.house(bench, "ui-tasks-sequence-scale")
    posts = [one for one in T.T3_LOG if one["event"] == "post"]
    born = datetime.fromisoformat(T.T3_LOG[0]["at"])
    dates = [(datetime.fromisoformat(START) + timedelta(seconds=one)).isoformat() for one in DELAYS]
    drawn, played = S.probe(bench, [[START, dates], [T.T3_LOG[0]["at"], [one["at"] for one in posts]]])
    column, hours, expected = drawn.get("column"), drawn.get("hours") or [], drawn.get("expected") or [None, None]

    # --- the band of T3: each row says its scale ---------------------------------------------------------------
    done = house.render("--render", "tasks", *S.SIZE)
    scales = S.scales_of(done.stdout)
    band = [scales.get(one["id"]) for one in posts]
    delays = [int((datetime.fromisoformat(one["at"]) - born).total_seconds()) for one in posts]
    if done.returncode == 0 and expected[1] and band == expected[1] and [S.delay_of(one) for one in band] == delays:
        held("each row of the band says its hour then its delay", f"{dict(zip([one['id'] for one in posts], band))}")
    else:
        failures.append(f"  ✗ band scale                  band={band} expected={expected[1]} {done.stdout[-1600:]!r}")

    # --- the scale drawn: the column as the function says it, the hour then the delay ---------------------------
    if (played.returncode == 0 and expected[0] and column == expected[0] and len(set(column)) == len(DELAYS)
            and all(one.startswith(hour) for one, hour in zip(column, hours))
            and [S.delay_of(one) for one in column] == list(DELAYS)):
        held("the scale: the event's hour, then the delay since the birth", f"start+{DELAYS}s: the gutter says "
             f"{column}, as scale_of does")
    else:
        failures.append(f"  ✗ scale column                column={column} expected={expected[0]} hours={hours} "
                        f"rc={played.returncode} {played.stderr[-400:]!r}")

    return 0
