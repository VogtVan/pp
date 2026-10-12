"""Scenario `ui-team-declaration` -- `e`, the declaration of the team chosen (plan ui, batch
les-overlays-des-gestes), on the bench's `pp-team` witness:
- `e` reads `team declaration <team> --json` and shows, in an overlay, its path, the verdict of `start`'s judge
  (`ok`, or the refusal `start` would write), the keys a new start would change, then `TEAM.md` whole as text
- a team never started says `not started`
- nothing is played: after `e` the witness's journal holds readings alone
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

TEXT = "---\nname: core-review\nagents: |\n  lead agents/lead\n  reviewer agents/reviewer\nroot: lead\n---\nReview the PRs.\n"
CORE = {"team": "core-review", "path": "teams/core-review/TEAM.md", "text": TEXT, "digest": "abc123abc123",
        "verdict": {"ok": True, "refusal": None}, "started": {"at": "2026-10-10T09:00:00+00:00", "id": 1,
                                                              "digest": "abc123abc123"},
        "changed": False, "pending": []}
OPS = {"team": "ops", "path": "teams/ops/TEAM.md", "text": "---\nname: ops\nparallel: 0\n---\n", "digest": "def456def456",
       "verdict": {"ok": False, "refusal": "team-invalid -- parallel: 0 is not a whole number of 1 or more"},
       "started": {"at": "2026-10-10T09:00:00+00:00", "id": 1, "digest": "000000000000"}, "changed": True,
       "pending": None}
VEILLE = {"team": "veille", "path": "teams/veille/TEAM.md", "text": "---\nname: veille\n---\n", "digest": "aaa",
          "verdict": {"ok": True, "refusal": None}, "started": None, "changed": False, "pending": []}
PENDING = {**CORE, "changed": True, "pending": [{"key": "root", "started": "lead", "declared": "reviewer"},
                                                {"key": "limits", "started": {"budget": 2.0}, "declared": {"budget": 5.0}}]}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-declaration",
                    T.script(declarations={"core-review": CORE, "ops": OPS, "veille": VEILLE}))

    def shown(keys: str):
        house.clear_journal()
        done = house.render("--render", "teams", "--size", "130x40", "--press", keys)
        return done, " ".join(done.stdout.split())

    done, flat = shown("e")
    if (done.returncode == 0 and "teams/core-review/TEAM.md" in flat and "verdict ok" in flat
            and "Review the PRs." in flat and "root: lead" in flat and "nothing pending" in flat
            and "declaration core-review" in house.journal_lines() and house.gestures() == []):
        held("e shows the declaration", "its path, verdict ok, nothing pending, TEAM.md whole; nothing played")
    else:
        failures.append(f"  ✗ declaration                 rc={done.returncode} {house.journal_lines()} "
                        f"{done.stdout[-1500:]!r} {done.stderr[-400:]!r}")

    done, flat = shown("down,e")
    if done.returncode == 0 and "verdict refused: team-invalid -- parallel: 0" in flat and house.gestures() == []:
        held("a declaration start would refuse says its refusal", "verdict refused: team-invalid -- parallel: 0 …")
    else:
        failures.append(f"  ✗ refused                     rc={done.returncode} {done.stdout[-1200:]!r}")

    done, flat = shown("down,down,e")
    if done.returncode == 0 and "not started" in flat and "teams/veille/TEAM.md" in flat:
        held("a team never started says so", "not started")
    else:
        failures.append(f"  ✗ never started               rc={done.returncode} {done.stdout[-1200:]!r}")

    house.use(T.script(declarations={"core-review": PENDING}))
    done, flat = shown("e")
    if (done.returncode == 0 and "root · lead → reviewer" in flat and "limits · " in flat
            and "2 key(s) wait a start" in flat and house.gestures() == []):
        held("the keys a start would change are said", "root · lead → reviewer, limits; 2 key(s) wait a start")
    else:
        failures.append(f"  ✗ pending                     rc={done.returncode} {done.stdout[-1500:]!r}")
    lines = house.journal_lines()
    if lines and all(not one.startswith("team ") for one in lines):
        held("e plays nothing", f"{len(lines)} reading(s) in the journal, no gesture")
    else:
        failures.append(f"  ✗ readings alone              {lines}")
    return 0
