"""Scenario `due` -- the pattern `control-flow/due`, played from its demonstration:
- a cadence n plays the guarded step every n completed exchanges, never in the first: 1 opens it
  from the second exchange on, 3 at the fourth and the seventh, none other
- a switch `true` plays it from the first exchange, `false` never; a field left out means never
- a value that is no whole number, or below 0, refuses `guard-invalid` before anything plays
"""
from __future__ import annotations

from tests.harness import demonstrated, demos, plant

DEMOS = ("DIARY.md", "NOTE.md", "PACE.md")
FIELD = "every: "                                     # the field the guard of DIARY.md reads


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("due", bare=True)
    found = demonstrated("control-flow", "due")
    if found != sorted(DEMOS):
        failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    plant(env, "control-flow", "due", DEMOS)
    pace = (demos("control-flow", "due") / "PACE.md").read_text(encoding="utf-8")
    declared = next(line for line in pace.splitlines() if line.startswith(FIELD))

    def paced(value: str | None) -> None:
        """PACE.md planted with its field set to `value`, or without the field."""
        line = "" if value is None else f"{FIELD}{value}\n"
        env.write("procs/PACE.md", pace.replace(f"{declared}\n", line))

    returns: list[str] = []

    def walk(exchanges: int) -> list[str]:
        """-> the document each exchange opens on, the guarded NOTE answered when it plays and
        the document it returns to recorded in `returns`."""
        conductor = env.conductor()
        conductor.forget()
        opened = [conductor.start(conductor.boot("DIARY.md"))]
        key = conductor.run_id
        for _ in range(exchanges - 1):
            if opened[-1].document == "NOTE":
                back = env.conductor(key).submit("")
                returns.append(back.document if back is not None and back.wait else "")
            opened.append(env.conductor(key).submit("the next message"))
        env.conductor(key).forget()
        return [one.document for one in opened]

    # --- a cadence ----------------------------------------------------------------------------
    paced("1")
    every_one = walk(3)
    paced("3")
    every_three = walk(7)
    if (every_one == ["DIARY", "NOTE", "NOTE"] and returns == ["DIARY"] * 2
            and every_three == ["DIARY", "DIARY", "DIARY", "NOTE", "DIARY", "DIARY", "NOTE"]):
        held("a cadence paces the step", f"every 1: {every_one}; every 3: the fourth and the seventh "
             "exchange open on NOTE, none other; each NOTE returns to DIARY's last step")
    else:
        failures.append(f"  ✗ the cadence                 {every_one} {every_three} {returns}")

    # --- a switch, and a field left out --------------------------------------------------------
    paced("true")
    on = walk(2)
    paced("false")
    off = walk(3)
    paced(None)
    absent = walk(3)
    if on == ["NOTE", "NOTE"] and off == ["DIARY"] * 3 and absent == ["DIARY"] * 3:
        held("a switch plays it or never", "`true` from the first exchange, `false` never, the field "
             "left out never -- nothing refuses")
    else:
        failures.append(f"  ✗ the switch                  {on} {off} {absent}")

    # --- a value the guard cannot read refuses ------------------------------------------------
    for wrong in ("banana", "-1"):
        paced(wrong)
        conductor = env.conductor()
        conductor.forget()
        expect("guard-invalid", lambda c=conductor: c.start(c.boot("DIARY.md")))
    return 0
