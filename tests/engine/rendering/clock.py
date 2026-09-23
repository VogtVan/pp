"""Scenario `clock` -- 3 case(s):
- the output's own heading ends on the hour and the time since -new, once per output
- a later output says a later hour and a longer elapsed; a -peek says it too
- the keyless console shows the pending block: its hour rides, once
"""
from __future__ import annotations

import re
from datetime import timedelta

from conductor.execution import blocks
from conductor import render

MARK = re.compile(r" · (\d\d):(\d\d):(\d\d) · \+(\d+):(\d\d):(\d\d)$")


def _marks(text: str) -> list[re.Match]:
    return [m for line in text.splitlines() if (m := MARK.search(line))]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("clockws")
    real = blocks.clock
    conductor = env.conductor()
    frozen = {"after": timedelta(seconds=65)}
    # the hour is read at the render, relative to the trace's stamp (the run's -new)
    blocks.clock = lambda: ((blocks._opened_at(conductor._log or "") or real()) + frozen["after"])
    try:
        text = render(conductor.resume(conductor.boot("BOOT.md")))
        opened = blocks._opened_at(conductor._log)
        first = text.splitlines()[0]
        marks = _marks(text)
        local = (opened + frozen["after"]).astimezone().strftime("%H:%M:%S")
        # --- once per output, on the output's heading, hour and elapsed ------------------
        if (first.startswith("▌ pp · ") and len(marks) == 1 and MARK.search(first)
                and first.endswith(f" · {local} · +0:01:05")):
            held("the output's heading says the hour once", f"`{first[-24:]}` on the boot -- "
                 "the local hour and +0:01:05 since -new, the mark once")
        else:
            failures.append(f"  ✗ clock once                 {first!r} marks={len(marks)}")

        # --- a later output, a later hour; the peek says it too ---------------------------
        frozen["after"] = timedelta(hours=1, minutes=2, seconds=3)
        later = render(conductor.forward(""))
        later_first = later.splitlines()[0]
        peeked = conductor.peek()
        peek_text = render(peeked) if peeked else ""
        if (later_first.endswith(" · +1:02:03") and len(_marks(later)) == 1
                and peek_text.splitlines()[0].endswith(" · +1:02:03")):
            held("a later output says a later hour", "`+1:02:03` on the advance and on the peek")
        else:
            failures.append(f"  ✗ clock later                {later_first!r} {peek_text.splitlines()[:1]!r}")
    finally:
        blocks.clock = real

    # --- the keyless console shows the pending block: its hour rides, once ---------------
    shelf = env.cli()
    if shelf.returncode == 0 and len(_marks(shelf.stdout)) == 1:
        held("the keyless console shows the hour once", "it shows the pending block, the mark with it")
    else:
        failures.append(f"  ✗ keyless clock              rc={shelf.returncode} {shelf.stdout[:160]!r}")
    return 0
