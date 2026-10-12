"""Scenario `ui-purge` -- the weight of the runs and the purge shown first (plan ui, batch le-poids-et-la-purge), on
the bench's `pp-chat` witness replaying the faces of `agent`:
- the Agents tab says each agent's `weight` (`1.2 MB` for ag1, `812 B` for ag2), the overlay of the runs each run's
- `P` on a run plays the purge WITHOUT `--yes` first and shows what it would remove -- the lines by record, the files,
  the bytes -- with the exact `--yes` command under it; a key typed wrong, or `escape`, plays nothing more
The purge played is `ui-purge-yes`'s.
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")
KEY = ",".join("w00001")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-purge")
    render = post.render

    def purges() -> list[str]:
        return [one for one in post.journal_lines() if one.startswith("purge ")]

    def row_of(text: str, name: str) -> str:
        return next((line for line in text.split("\n") if f" {name} " in f" {line} "), "")

    # --- the weight, per agent and per run --------------------------------------------------------------
    table = render("--render", "agents", "--size", "140x30")
    runs = render("--render", "dialogue", "--size", "140x30", "--press", "2,enter")
    if (table.returncode == 0 and "weight" in table.stdout and "1.2 MB" in row_of(table.stdout, "ag1")
            and "812 B" in row_of(table.stdout, "ag2") and runs.returncode == 0 and " weight " in runs.stdout
            and "1.2 MB" in row_of(runs.stdout, "w00001")):
        held("the weight is said", "ag1 1.2 MB and ag2 812 B in the Agents tab; w00001 1.2 MB in the overlay of its runs")
    else:
        failures.append(f"  ✗ weight                      rc={table.returncode}/{runs.returncode} {table.stdout!r} "
                        f"{runs.stdout[-1500:]!r} {runs.stderr[-300:]!r}")

    # --- P: the purge without --yes, shown -----------------------------------------------------------
    post.clear_journal()
    shown = render("--render", "dialogue", "--size", "140x40", "--press", "2,enter,P")
    text = shown.stdout
    if (shown.returncode == 0 and purges() == ["purge ag1 w00001 --json"] and "responses 2" in text
            and "2 file(s)" in text and "./pp agent purge ag1 w00001 --yes --json" in text and "type w00001" in text):
        held("P shows the purge first", f"the journal says {purges()}; the overlay says the lines by record, the files, "
             "the bytes and the --yes command")
    else:
        failures.append(f"  ✗ shown first                 rc={shown.returncode} {purges()} {text[-2000:]!r} {shown.stderr[-300:]!r}")

    # --- a key typed wrong, escape: nothing more --------------------------------------------------------
    post.clear_journal()
    wrong = render("--render", "dialogue", "--size", "140x40", "--press", f"2,enter,P,{KEY[:-1]}2,enter")
    wrong_said = purges()
    post.clear_journal()
    left = render("--render", "dialogue", "--size", "140x40", "--press", "2,enter,P,escape", "--wait", "none:1")
    if (wrong.returncode == 0 and wrong_said == ["purge ag1 w00001 --json"] and "nothing played" in wrong.stdout
            and left.returncode == 0 and purges() == ["purge ag1 w00001 --json"]):
        held("a wrong key or escape plays nothing", "w00002 typed: `nothing played`, no --yes; escape: no --yes")
    else:
        failures.append(f"  ✗ wrong key, escape           {wrong_said} {purges()} {wrong.stdout[-1200:]!r}")
    return 0
