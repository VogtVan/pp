"""Scenario `ui-purge-before` -- the runs of an agent purged before a date (plan ui, batch le-poids-et-la-purge), on the
bench's `pp-chat` witness:
- `B` asks the date, the command under the line; `enter` plays the purge without `--yes`, shows what it would remove,
  and plays `--yes` once the date is typed again
- a date written otherwise: the verb's `purge-invalid` on the remedy line, nothing more
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")
DATE = ",".join("2026-10-09").replace("-", "minus")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-purge-before")

    def purges() -> list[str]:
        return [one for one in post.journal_lines() if one.startswith("purge ")]

    post.clear_journal()
    played = post.render("--render", "dialogue", "--size", "140x40", "--press", f"2,enter,B,{DATE},enter,{DATE},enter",
                         "--wait", "none:1.5")
    if (played.returncode == 0
            and purges() == ["purge ag1 --before 2026-10-09 --json", "purge ag1 --before 2026-10-09 --yes --json"]):
        held("B purges the runs before a date", f"the journal says {purges()}")
    else:
        failures.append(f"  ✗ before                      {purges()} {played.stdout[-1500:]!r} {played.stderr[-300:]!r}")

    post.clear_journal()
    bad = post.render("--render", "dialogue", "--size", "140x40", "--press",
                      f"2,enter,B,{','.join('2026').replace('-', 'minus')},minus,1,3,minus,4,5,enter", "--wait", "none:1")
    remedy = bad.stdout.rstrip("\n").split("\n")[-2]
    if bad.returncode == 0 and "purge-invalid" in remedy and purges() == ["purge ag1 --before 2026-13-45 --json"]:
        held("a date written otherwise is refused by the verb", remedy.strip()[:100])
    else:
        failures.append(f"  ✗ purge-invalid               {purges()} {remedy!r} {bad.stderr[-300:]!r}")
    return 0
