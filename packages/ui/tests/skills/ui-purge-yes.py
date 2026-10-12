"""Scenario `ui-purge-yes` -- the purge played (plan ui, batch le-poids-et-la-purge; cut from `ui-purge`, rule 10), on
the bench's `pp-chat` witness:
- `P`, the run's key typed, `enter`: the `--yes` command plays word for word as shown, after the purge without
  `--yes`; the overlay of the runs is read again, the run gone
- a conversation the post kept open on the purged run leaves its memory
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")
KEY = ",".join("w00001")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-purge-yes")

    def purges() -> list[str]:
        return [one for one in post.journal_lines() if one.startswith("purge ")]

    kept = post.render("ag1", "--render", "dialogue", "--size", "140x40")
    before = [one.get("run") for one in post.remembered()]
    post.clear_journal()
    played = post.render("--render", "dialogue", "--size", "140x40", "--press", f"escape,2,enter,P,{KEY},enter",   # escape: the line of the tab the memory opens
                         "--wait", "none:1.5", keep=True)
    rows = [line for line in played.stdout.split("\n") if "w00001" in line and "w00009" not in line]
    after = [one.get("run") for one in post.remembered()]
    if (kept.returncode == 0 and before == ["w00001"] and played.returncode == 0
            and purges() == ["purge ag1 w00001 --json", "purge ag1 w00001 --yes --json"]
            and any("w00009" in line for line in played.stdout.split("\n")) and after == []):
        held("the purge plays as shown", f"the journal says {purges()}; the overlay read again without w00001; the "
             f"memory {before} -> {after}")
    else:
        failures.append(f"  ✗ played                      {purges()} memory {before} -> {after} rows={rows[:3]} "
                        f"{played.stdout[-1500:]!r} {played.stderr[-300:]!r}")
    return 0
