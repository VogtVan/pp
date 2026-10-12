"""Scenario `ui-context` -- the GAUGE of a run's context beside the message line (plan ui, batch la-zone-du-chat),
on the bench's `pp-chat` witness, read from `context` of `agent stats --json` alone:
- before any verdict, `ctx —`, and no `stats` played
- after the verdict of `ag1`'s first turn, `stats ag1 w00001 --json` played and the gauge says `17% · pp 33%`
  after a bar of ten cells: pp's part and the rest of the used part in two looks, the empty cells in a third
  (`--styles`)
- a run without `context` (`w00009`) says `ctx —` after its verdict
- a run taken up says its gauge before any message: `stats` played at its opening
"""
from __future__ import annotations

import re

from tests.harness import support

P = support(__file__, "dialogue")

SIZE = ("--size", "120x30")
GAUGE = re.compile(r"ctx [▰▱]{10} 17% · pp 33%")
SEGMENT = re.compile(r"\x1b\[([0-9;]*)m([^\x1b]*)")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-context")
    render = post.render

    def stats() -> list[str]:
        return [one for one in post.journal_lines() if one.startswith("stats ")]

    # --- before any verdict: ctx —, nothing played -------------------------------------------------------------
    post.clear_journal()
    rest = render("ag1", "--render", "dialogue", *SIZE)
    if rest.returncode == 0 and "ctx —" in rest.stdout and stats() == []:
        held("before any verdict the gauge says ctx —", "no stats played")
    else:
        failures.append(f"  ✗ rest                        {stats()} {rest.stdout[-600:]!r} {rest.stderr[-300:]!r}")

    # --- after the verdict: stats played, 17% · pp 33%, the bar in two looks and its empty cells -----------------
    post.clear_journal()
    turned = render("ag1", "--render", "dialogue", *SIZE, "--styles", "--press", "h,i,enter,wait:waiting")
    plain = P.ANSI.sub("", turned.stdout)
    row = next((one for one in turned.stdout.split("\n") if GAUGE.search(P.ANSI.sub("", one))), "")
    full = {style for style, text in SEGMENT.findall(row) if "▰" in text}
    empty = {style for style, text in SEGMENT.findall(row) if "▱" in text}
    if (turned.returncode == 0 and GAUGE.search(plain) and stats() == ["stats ag1 w00001 --json"]
            and len(full) >= 2 and empty and not empty & full):
        held("after the verdict the gauge reads the face", f"{GAUGE.search(plain).group(0)!r}; {stats()}; the used "
             f"cells in {len(full)} looks, the empty ones in another")
    else:
        failures.append(f"  ✗ gauge                       {stats()} full={full} empty={empty} {plain[-900:]!r} "
                        f"{turned.stderr[-300:]!r}")

    # --- a run without context: ctx — after its verdict ----------------------------------------------------------
    post.clear_journal()
    flowless = render("ag1", "--run", "w00009", "--render", "dialogue", *SIZE, "--press", "h,i,enter,wait:waiting")
    if flowless.returncode == 0 and "ctx —" in flowless.stdout and "stats ag1 w00009 --json" in stats():
        held("a run without context says ctx —", f"{stats()}")
    else:
        failures.append(f"  ✗ flowless                    {stats()} {flowless.stdout[-600:]!r} {flowless.stderr[-300:]!r}")

    # --- a run taken up: its gauge before any message ------------------------------------------------------------
    post.clear_journal()
    taken = render("ag1", "--run", "w00001", "--render", "dialogue", *SIZE)
    if taken.returncode == 0 and GAUGE.search(taken.stdout) and stats() == ["stats ag1 w00001 --json"]:
        held("a run taken up says its gauge at once", f"{GAUGE.search(taken.stdout).group(0)!r} before any message")
    else:
        failures.append(f"  ✗ taken up                    {stats()} {taken.stdout[-600:]!r} {taken.stderr[-300:]!r}")
    return 0
